"""Durable scene batches through a fixed, credential-free local Cut Room bridge.

Only an explicit batch POST authorizes new generations. Known job ids can be
polled after restart; an interrupted/ambiguous POST is never automatically sent
again. Tests inject a fake bridge, so no provider credit is needed.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import copy
import hashlib
import http.client
import json
from pathlib import Path
import re
import shutil
import threading
from urllib.parse import unquote
import uuid


MAX_BATCH = 6
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}
KNOWN_MODELS = {
    'seedance25': {'id': 'seedance25', 'name': 'Seedance 2.5 · 720p', 'kind': 'video',
                   'durations': [4, 5, 6, 8, 10, 12, 15], 'requiresReference': True},
    'kling25': {'id': 'kling25', 'name': 'Kling 2.5 Turbo Pro', 'kind': 'video',
                'durations': [5, 10], 'requiresReference': True},
    'nano-banana2': {'id': 'nano-banana2', 'name': 'Nano Banana 2 · 2K', 'kind': 'image',
                    'durations': [], 'requiresReference': True},
}
ID_RE = re.compile(r'^[a-f0-9]{32}$')


class BridgeRejected(ValueError):
    """An explicit local 4xx rejection: no accepted Cut Room job."""


class CutRoomBridge:
    """No caller-controlled URL, redirect, proxy, cookie or authentication data."""
    def request(self, method, path, payload=None):
        connection = http.client.HTTPConnection('127.0.0.1', 8787, timeout=20)
        body = json.dumps(payload, allow_nan=False).encode() if payload is not None else None
        headers = {'Content-Type': 'application/json'} if body is not None else {}
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(20 * 1024 * 1024 + 1)
            if len(raw) > 20 * 1024 * 1024:
                raise ConnectionError('The local Cut Room response is too large.')
            if not 200 <= response.status < 300:
                if 400 <= response.status < 500:
                    raise BridgeRejected('Cut Room rejected the request. Check its model, reference and pending queue.')
                raise ConnectionError('The local Cut Room service did not confirm the request.')
            data = json.loads(raw)
            if not isinstance(data, dict):
                raise ConnectionError('The local Cut Room response is invalid.')
            return data
        finally:
            connection.close()

    def config(self):
        return self.request('GET', '/api/generation/config')

    def library(self, refresh=False):
        return self.request('POST', '/api/library/refresh', {}) if refresh else self.request('GET', '/api/library')

    def submit(self, payload):
        return self.request('POST', '/api/generation', payload)

    def get(self, job_id):
        if not isinstance(job_id, str) or not ID_RE.fullmatch(job_id):
            raise ValueError('Invalid Cut Room job identifier.')
        return self.request('GET', '/api/generation/jobs/' + job_id)


class BatchManager:
    def __init__(self, store, validate, atomic_json, canonical_json, conflict,
                 bridge=None, autostart=True, poll_seconds=4):
        self.store = store
        self.validate = validate
        self.write = atomic_json
        self.canonical = canonical_json
        self.conflict = conflict
        self.bridge = bridge or CutRoomBridge()
        self.autostart = autostart
        self.poll_seconds = poll_seconds
        self.folder = store.state / 'batches'
        self.folder.mkdir(exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.library_lock = threading.Lock()
        self.stop = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='scene-fal')
        self.scheduled = set()
        self._recover()

    def close(self):
        self.stop.set()
        self.executor.shutdown(wait=False, cancel_futures=True)

    def config(self):
        result = {'engine': 'fal', 'provider': 'fal', 'configured': False, 'concurrency': 2,
                  'maxBatchSize': MAX_BATCH, 'models': list(copy.deepcopy(KNOWN_MODELS).values()),
                  'message': 'Start Cut Room on port 8787 with FAL configured to generate automatically.'}
        try:
            config = self.bridge.config()
            result['configured'] = config.get('configured') is True
            available = {m.get('id') for m in config.get('models', []) if isinstance(m, dict)}
            result['models'] = [m for m in result['models'] if m['id'] in available]
            if result['configured']:
                result['message'] = 'Background FAL generation is ready through local Cut Room; two jobs run at once.'
        except (OSError, ValueError, http.client.HTTPException):
            pass
        return result

    def _response(self, batch, created):
        return {'id': batch['id'], 'engine': batch['engine'], 'model': batch.get('model'),
                'created': created,
                'jobs': [self.store.get(job_id) for job_id in batch.get('jobIds', [])]}

    def submit(self, payload, header_key=None):
        if not isinstance(payload, dict) or not set(payload) <= {'idempotencyKey', 'engine', 'model', 'requests'}:
            raise ValueError('Batch accepts idempotencyKey, engine, model and requests.')
        key = payload.get('idempotencyKey', header_key)
        if header_key and key != header_key:
            raise ValueError('Header and payload idempotency keys differ.')
        try:
            batch_id = uuid.UUID(key).hex
        except (ValueError, TypeError, AttributeError):
            raise ValueError('A batch requires a UUID idempotencyKey.') from None
        engine = payload.get('engine')
        if engine not in {'fal', 'mcp'}:
            raise ValueError('Choose the fal or mcp engine.')
        requests = payload.get('requests')
        if not isinstance(requests, list) or not 1 <= len(requests) <= MAX_BATCH:
            raise ValueError('Choose between one and six scenes per batch.')
        model_id = payload.get('model')
        model = KNOWN_MODELS.get(model_id) if isinstance(model_id, str) else None
        if engine == 'fal' and not model:
            raise ValueError('Choose a supported FAL model.')
        normalized = []
        scenes = set()
        for index, supplied in enumerate(requests):
            request, _, _ = self.validate(supplied, self.store.creative, self.store.state)
            if request['sceneId'] in scenes:
                raise ValueError('Each scene may appear only once in a batch.')
            scenes.add(request['sceneId'])
            if engine == 'fal':
                if request['type'] != model['kind']:
                    raise ValueError('The selected model must match every request type.')
                prompt = self._prompt(request)
                if not 10 <= len(prompt) <= 12000:
                    raise ValueError('Each FAL prompt must contain 10 to 12,000 characters.')
                if request['type'] == 'video' and (type(request['duration']) is not int or request['duration'] not in model['durations']):
                    raise ValueError('Choose an exact duration supported by the selected video model.')
                self._reference_path(request)  # Validate local file before recording any job.
            child = copy.deepcopy(supplied)
            child['idempotencyKey'] = str(uuid.uuid5(uuid.UUID(hex=batch_id), str(index)))
            normalized.append(child)
        fingerprint = hashlib.sha256(self.canonical({'engine': engine, 'model': model_id,
                                                     'requests': normalized}).encode()).hexdigest()
        with self.lock:
            path = self.folder / (batch_id + '.json')
            if path.is_file():
                batch = json.loads(path.read_text())
                if batch['fingerprint'] != fingerprint:
                    raise self.conflict('This batch idempotency key belongs to different requests.')
                self._materialize(batch)
                return self._response(batch, False), False
            if engine == 'fal':
                config = self.config()
                if not config['configured'] or model_id not in {m['id'] for m in config['models']}:
                    raise self.conflict('FAL is unavailable. Start the configured Cut Room on port 8787 or select the MCP queue.')
            if sum(j['status'] in {'awaiting_mcp', 'queued', 'submitting', 'running'} for j in self.store.list()) + len(normalized) > 100:
                raise self.conflict('Too many pending scene requests. Finish some before adding a batch.')
            batch = {'id': batch_id, 'engine': engine, 'model': model_id if engine == 'fal' else None,
                     'fingerprint': fingerprint, 'requests': normalized, 'jobIds': []}
            # A durable batch intent precedes all job creation and provider POSTs.
            self.write(path, batch)
            self._materialize(batch)
            return self._response(batch, True), True

    @staticmethod
    def _prompt(request):
        # UI can apply the common instruction inside the scene prompt. Avoid
        # appending it twice when the editable prompt already contains it.
        prompt = request.get('prompt', '').strip()
        direction = request.get('modification', '').strip()
        if direction and direction not in prompt:
            prompt += '\n\nRequested change:\n' + direction
        return prompt.strip()

    def _materialize(self, batch):
        ids = []
        for payload in batch['requests']:
            execution = {'batchId': batch['id'], 'engine': batch['engine'], 'model': batch.get('model')}
            if batch['engine'] == 'fal':
                execution.update(mode='fal_bridge', autonomous=True, status='queued',
                                 startingImage=payload.get('startingImage'),
                                 message='Queued for background generation through local Cut Room.')
            job, _ = self.store.submit(payload, execution=execution)
            ids.append(job['id'])
        batch['jobIds'] = ids
        self.write(self.folder / (batch['id'] + '.json'), batch)
        for job_id in ids:
            self._schedule(job_id)

    def _recover(self):
        for path in self.folder.glob('*.json'):
            if not ID_RE.fullmatch(path.stem):
                continue
            try:
                batch = json.loads(path.read_text())
                if batch.get('id') != path.stem:
                    continue
                self._materialize(batch)
            except (OSError, ValueError, KeyError, self.conflict):
                # Preserve corrupt intent for inspection; never infer a paid POST.
                continue

    def _schedule(self, job_id):
        if job_id in self.scheduled:
            return
        job = self.store.get(job_id)
        if not job or job.get('engine') != 'fal':
            return
        if job['status'] == 'submitting' and not job.get('bridgeJobId'):
            self.store.update_generation(job_id, status='submission_unknown',
                error='Submission was interrupted before its job id was saved. Check Cut Room before creating another take.',
                message='No automatic resubmission: the earlier request may already have been accepted.')
            return
        if job['status'] not in {'queued', 'running'} or not self.autostart or job_id in self.scheduled:
            return
        self.scheduled.add(job_id)
        self.executor.submit(self.run_job, job_id)

    def _reference_path(self, request):
        url = request.get('startingImage')
        if not url:
            candidates = [r for r in request.get('references', []) if r.get('role') in {'start_frame', 'starting_image'}]
            candidates += request.get('references', [])
            url = next((r['url'] for r in candidates if r.get('source') != 'provider' and
                        (r.get('url', '').startswith('/api/studio/jobs/') or Path(r.get('url', '')).suffix.lower() in IMAGE_SUFFIXES)), None)
        if not isinstance(url, str):
            raise ValueError('FAL requires a local starting image for each scene.')
        generated = re.fullmatch(r'/api/studio/jobs/([a-f0-9]{32})/artifact', url)
        if generated:
            source = self.store.get(generated[1])
            result = (source or {}).get('result') or {}
            filename = result.get('filename', '')
            if not source or source['status'] != 'completed' or source['type'] != 'image' or Path(filename).name != filename:
                raise ValueError('The starting image must be a completed studio image.')
            path = (self.store._dir(source['id']) / filename).resolve()
            if path.parent != self.store._dir(source['id']).resolve():
                raise ValueError('Invalid completed image path.')
        else:
            if not url.startswith('/creative/') or '%' in unquote(url) or '?' in url or '#' in url:
                raise ValueError('FAL only accepts local starting images.')
            relative = Path(unquote(url).removeprefix('/creative/'))
            if any(p.startswith('.') for p in relative.parts):
                raise ValueError('Hidden starting images are not allowed.')
            path = (self.store.creative / relative).resolve()
            if not path.is_relative_to(self.store.creative):
                raise ValueError('Starting image escaped the creative folder.')
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            raise ValueError('A starting image must be an existing PNG, JPEG or WebP file.')
        return path

    def _source_id(self, request, job_id):
        path = self._reference_path(request)
        # Completed studio assets are deliberately hidden from the general
        # library. Copy only the explicitly selected image into a public cache.
        if path.is_relative_to(self.store.state):
            folder = self.store.creative / 'scene-studio' / 'generation-references' / job_id
            folder.mkdir(parents=True, exist_ok=True)
            target = folder / ('reference' + path.suffix.lower())
            if not target.exists():
                temporary = folder / ('.pending-' + target.name)
                shutil.copyfile(path, temporary)
                temporary.replace(target)
            path = target.resolve()
        relative = path.relative_to(self.store.creative.parent).as_posix()
        with self.library_lock:
            for refresh in (False, True):
                catalog = self.bridge.library(refresh=refresh)
                asset = next((a for a in catalog.get('assets', []) if a.get('relativePath') == relative and a.get('kind') == 'image'), None)
                if asset and isinstance(asset.get('id'), str):
                    return asset['id']
        raise ValueError('This starting image could not be found in the Cut Room library. Choose the native scene image instead of a thumbnail.')

    def _import(self, job_id, upstream):
        output_id = upstream.get('outputId')
        if not isinstance(output_id, str):
            raise ValueError('The completed Cut Room job has no registered output.')
        catalog = self.bridge.library()
        asset = next((a for a in catalog.get('assets', []) if a.get('id') == output_id), None)
        if not asset or not isinstance(asset.get('relativePath'), str):
            raise ValueError('The generated result is missing from the Cut Room registry.')
        path = (self.store.creative.parent / asset['relativePath']).resolve()
        expected = (self.store.creative / 'editor' / 'generated' / upstream['id']).resolve()
        if not expected.is_relative_to(self.store.creative) or path.parent != expected or path.name not in {'media.png', 'media.mp4'}:
            raise ValueError('The generated result is outside its registered Cut Room output folder.')
        self.store.complete(job_id, path, provider='fal', provider_job_id=upstream['id'])

    def run_job(self, job_id):
        """Process one job, with at most one submit; public for deterministic tests."""
        job = self.store.get(job_id)
        if not job or job.get('engine') != 'fal' or job['status'] not in {'queued', 'running'}:
            return
        bridge_id = job.get('bridgeJobId')
        if not bridge_id:
            try:
                request = self.store.request(job_id)
                source_id = self._source_id(request, job_id)
                payload = {'sourceId': source_id, 'model': job['model'], 'prompt': self._prompt(request)}
                if job['type'] == 'video':
                    payload['duration'] = job['duration']
                if self.stop.is_set():
                    return
            except (OSError, ValueError, http.client.HTTPException):
                self.store.fail(job_id, 'The starting image or local Cut Room library is unavailable. No generation was submitted.')
                return
            claimed = self.store.update_generation(job_id, expected_status='queued', status='submitting',
                                                   message='Submitting one generation to local Cut Room.')
            if not claimed:
                return
            try:
                upstream = self.bridge.submit(payload)
                bridge_id = upstream.get('id')
                if not isinstance(bridge_id, str) or not ID_RE.fullmatch(bridge_id):
                    raise ConnectionError('Missing accepted job identifier.')
            except BridgeRejected as error:
                self.store.fail(job_id, str(error))
                return
            except (OSError, ValueError, http.client.HTTPException):
                self.store.update_generation(job_id, status='submission_unknown',
                    error='Cut Room did not confirm a job id. Check its generation list before trying again.',
                    message='No automatic resubmission: the request may already have been accepted.')
                return
            self.store.update_generation(job_id, status='running', bridgeJobId=bridge_id,
                provider='fal', providerJobId=bridge_id,
                message='Generation accepted. It continues in the background; you can change scenes or close this tab.')
        while not self.stop.is_set():
            try:
                upstream = self.bridge.get(bridge_id)
                if not isinstance(upstream, dict) or upstream.get('id') != bridge_id:
                    raise ConnectionError('Unexpected generation response.')
                state = upstream.get('status')
                if state == 'completed':
                    self._import(job_id, upstream)
                    return
                if state in {'failed', 'submission_unknown', 'interrupted', 'cancelled', 'canceled'}:
                    message = str(upstream.get('error') or 'The provider could not complete this generation.')[:800]
                    message = re.sub(r'https?://\S+', '[provider link]', message)
                    self.store.update_generation(job_id, status=state if state=='submission_unknown' else 'failed',
                                                 bridgeStatus=state, error=message, message=message)
                    return
                self.store.update_generation(job_id, status='running', bridgeStatus=state,
                    message='Waiting for the provider. The job continues in the background.')
            except BridgeRejected:
                self.store.update_generation(job_id, status='submission_unknown',
                    error='The accepted Cut Room job is no longer available. Verify its saved job id before retrying.',
                    message='Known job id preserved; no generation was resubmitted.')
                return
            except (OSError, http.client.HTTPException):
                self.store.update_generation(job_id, message='Cut Room is unavailable. Reconnecting to the same job without resubmitting.')
            except ValueError as error:
                self.store.fail(job_id, str(error)[:800])
                return
            self.stop.wait(self.poll_seconds)
