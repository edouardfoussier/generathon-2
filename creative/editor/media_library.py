"""Read-only, path-safe inventory of the project's existing creative media."""
from __future__ import annotations
import copy
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import math
import re
import tempfile
from pathlib import Path
import shutil
import subprocess
import threading
from urllib.parse import quote

KINDS = {'.mp4': 'video', '.webm': 'video', '.mov': 'video', '.m4v': 'video',
         '.png': 'image', '.jpg': 'image', '.jpeg': 'image', '.webp': 'image',
         '.mp3': 'audio', '.wav': 'audio', '.m4a': 'audio', '.aac': 'audio', '.ogg': 'audio', '.flac': 'audio'}
SKIP = {'node_modules', 'vendor', 'exports', '__pycache__', 'qa', 'frames', 'posters', 'thumbnails', 'contact-sheets'}
PATH_KEYS = ('localFile', 'file', 'filename', 'localPath', 'video', 'outputFile', 'output')


def localized(value, fallback=''):
    if isinstance(value, dict):
        return str(value.get('fr') or value.get('en') or fallback)
    return str(value) if isinstance(value, (str, int)) else fallback


class MediaLibrary:
    def __init__(self, repo, legacy_sources=None):
        self.repo = Path(repo).resolve()
        self.creative = self.repo / 'creative'
        self.legacy = {Path(p).resolve(): key for key, p in (legacy_sources or {}).items()}
        self.lock = threading.RLock()
        self.refresh_lock = threading.Lock()
        self.poster_slots = threading.BoundedSemaphore(3)
        self.poster_locks = {}
        self._records, self._paths, self._cache = {}, {}, {}
        self.cache_file = self.creative / 'editor' / '.state' / 'catalog-cache.json'
        try:
            self._cache = json.loads(self.cache_file.read_text())
        except (OSError, ValueError):
            pass
        self.refresh()

    def _safe(self, candidate):
        path = Path(candidate).resolve()
        if not path.is_relative_to(self.creative) or not path.is_file():
            return None
        relative = path.relative_to(self.creative)
        if any(part.startswith('.') or part in {'node_modules', 'vendor', 'exports', '__pycache__'} for part in relative.parts):
            return None
        return path if path.suffix.lower() in KINDS else None

    def _resolve(self, value, source):
        if not isinstance(value, str) or '://' in value or '\x00' in value:
            return None
        path = Path(value)
        candidates = [path] if path.is_absolute() else [source.parent / path, self.repo / path]
        # Some nested provenance files use paths relative to the collection root.
        candidates += [parent / path for parent in source.parents if parent.is_relative_to(self.creative)] if not path.is_absolute() else []
        for candidate in candidates:
            try:
                found = self._safe(candidate)
                if found:
                    return found
            except (OSError, ValueError):
                continue
        return None

    def _probe(self, path):
        relative = str(path.relative_to(self.repo))
        stat = path.stat()
        fingerprint = [stat.st_mtime_ns, stat.st_size]
        cached = self._cache.get(relative, {})
        if cached.get('fingerprint') == fingerprint:
            return cached['data']
        result = {'durationFrames': 0, 'durationSeconds': 0, 'hasAudio': False}
        ffprobe = shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe'
        try:
            data = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-show_entries',
                'stream=codec_type,width,height,duration,avg_frame_rate:format=duration', '-of', 'json', str(path)],
                stderr=subprocess.DEVNULL, timeout=15))
            streams = data.get('streams', [])
            video = next((s for s in streams if s.get('codec_type') == 'video'), {})
            duration = float(video.get('duration') or data.get('format', {}).get('duration') or 0)
            if not math.isfinite(duration) or duration < 0:
                duration = 0
            result = {'durationFrames': math.floor(duration * 24 + 0.001), 'durationSeconds': duration,
                      'hasAudio': any(s.get('codec_type') == 'audio' for s in streams)}
            if video:
                result.update(width=video.get('width'), height=video.get('height'), nativeFrameRate=video.get('avg_frame_rate'))
        except (OSError, ValueError, subprocess.SubprocessError):
            result['probeError'] = 'Media metadata could not be read.'
        self._cache[relative] = {'fingerprint': fingerprint, 'data': result}
        return result

    def refresh(self):
        with self.refresh_lock:
            return self._refresh()

    def _refresh(self):
        metadata = {}
        all_files = list(self.creative.rglob('*')) if self.creative.exists() else []
        json_files = [p for p in all_files if p.suffix == '.json' and p.is_file()
                      and not any(part.startswith('.') or part in SKIP for part in p.relative_to(self.creative).parts)]
        # Prefer rich manifests over incidental job/QA metadata.
        json_files.sort(key=lambda p: ('manifest' in p.name, len(p.parts)))
        def walk(value, source, inherited=None):
            if isinstance(value, list):
                for child in value:
                    walk(child, source, inherited)
            elif isinstance(value, dict):
                context = {**(inherited or {})}
                if isinstance(value.get('model'), str):
                    context['model'] = value['model']
                found = next((self._resolve(value.get(key), source) for key in PATH_KEYS if self._resolve(value.get(key), source)), None)
                if found:
                    previous = metadata.get(found, {})
                    item = {**previous, **context}
                    for key in ('code', 'id', 'title', 'name', 'model', 'imageModel', 'videoModel', 'prompt', 'status', 'description', 'scene', 'group', 'referenceCodes', 'references', 'referenceImages', 'referenceAssets', 'referenceIds', 'referenceId', 'sourceId', 'assetId', 'arcadsPath', 'reviewStatus'):
                        if value.get(key) is not None:
                            item[key] = value[key]
                    poster = self._resolve(value.get('poster'), source)
                    if poster:
                        item['_poster'] = poster
                    item['_manifest'] = str(source.relative_to(self.repo))
                    metadata[found] = item
                for key, child in value.items():
                    if isinstance(child, (dict, list)):
                        walk(child, source, context)
        for source in json_files:
            try:
                if source.stat().st_size <= 8 * 1024 * 1024:
                    walk(json.loads(source.read_text()), source)
            except (OSError, ValueError):
                continue
        paths = set(metadata)
        for path in all_files:
            if path.suffix.lower() not in KINDS:
                continue
            relative = path.relative_to(self.creative)
            if any(part.startswith('.') or part.lower() in SKIP or part.lower().startswith('qa-') for part in relative.parts):
                continue
            if any(word in path.stem.lower() for word in ('contact-sheet', 'contact_sheet', 'poster', 'thumbnail')):
                continue
            found = self._safe(path)
            if found:
                paths.add(found)
        records, by_id = {}, {}
        def make_record(path):
            relative = path.relative_to(self.repo)
            item = metadata.get(path, {})
            media_id = self.legacy.get(path) or 'm_' + hashlib.sha256(str(relative).encode()).hexdigest()[:20]
            kind = KINDS[path.suffix.lower()]
            title = item.get('title') or item.get('name') or path.stem.replace('_', ' ').replace('-', ' ')
            collection = path.relative_to(self.creative).parts[0] if len(path.relative_to(self.creative).parts) > 1 else 'references'
            model = item.get('videoModel') if kind == 'video' else item.get('imageModel')
            record = {'id': media_id, 'kind': kind, 'name': localized(title, path.stem), 'title': title,
                      'url': '/library/' + media_id, 'collection': collection, 'model': model or item.get('model', ''),
                      'prompt': item.get('prompt', '') if isinstance(item.get('prompt', ''), str) else '',
                      'relativePath': str(relative), 'code': str(item.get('code', '')), 'referenceIds': [],
                      'bytes': path.stat().st_size, 'modifiedAt': path.stat().st_mtime,
                      'provenance': item.get('_manifest', ''), 'reviewStatus': item.get('reviewStatus', '')}
            if item.get('_poster'):
                record['posterUrl'] = '/' + quote(str(item['_poster'].relative_to(self.repo)))
            elif kind == 'video':
                record['posterUrl'] = '/library-poster/' + media_id + '.jpg'
            if kind in {'video', 'audio'}:
                record.update(self._probe(path))
            else:
                record.update(durationFrames=0, durationSeconds=0, hasAudio=False)
            return media_id, record, path
        with ThreadPoolExecutor(max_workers=6) as pool:
            for media_id, record, path in pool.map(make_record, sorted(paths)):
                records[media_id], by_id[media_id] = record, path
        lookups = {media_id: media_id for media_id in records}
        for media_id, path in by_id.items():
            item = metadata.get(path, {})
            for alias in (item.get('code'), item.get('assetId'), item.get('arcadsPath'), item.get('id')):
                if isinstance(alias, str):
                    lookups[alias] = media_id
        for media_id, path in by_id.items():
            item = metadata.get(path, {})
            references = []
            for key in ('referenceCodes', 'references', 'referenceImages', 'referenceAssets', 'referenceIds'):
                value = item.get(key, [])
                if isinstance(value, list):
                    for ref in value:
                        candidates = [ref] if isinstance(ref, str) else [ref.get(k) for k in ('code', 'assetId', 'durablePath')] if isinstance(ref, dict) else []
                        for candidate in candidates:
                            target = lookups.get(candidate) if isinstance(candidate, str) else None
                            if target and target != media_id and records[target]['kind'] == 'image' and target not in references:
                                references.append(target)
            for field in ('referenceId', 'sourceId'):
                candidate = item.get(field)
                target = lookups.get(candidate) if isinstance(candidate, str) else None
                if target and target != media_id:
                    if field == 'sourceId':
                        records[media_id]['sourceId'] = target
                    if records[target]['kind'] == 'image' and target not in references:
                        references.append(target)
            records[media_id]['referenceIds'] = references
        with self.lock:
            self._records, self._paths = records, by_id
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.cache_file.with_suffix('.tmp')
            temporary.write_text(json.dumps(self._cache))
            temporary.replace(self.cache_file)
        except OSError:
            pass
        return self.snapshot()

    def snapshot(self):
        with self.lock:
            assets = sorted(self._records.values(), key=lambda a: (-a['modifiedAt'], a['name']))
            counts = {}
            for asset in assets:
                counts[asset['collection']] = counts.get(asset['collection'], 0) + 1
            return copy.deepcopy({'assets': assets, 'collections': [{'id': key, 'name': key, 'count': value} for key, value in sorted(counts.items())]})

    def get(self, media_id):
        with self.lock:
            return copy.deepcopy(self._records.get(media_id))

    def path_for(self, media_id):
        with self.lock:
            path = self._paths.get(media_id)
        return self._safe(path) if path else None

    def poster_path(self, media_id):
        """Lazily make one safe JPEG per video; cap encoder concurrency at three."""
        if not isinstance(media_id, str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,80}', media_id):
            return None
        record = self.get(media_id)
        if not record or record['kind'] != 'video':
            return None
        with self.lock:
            lock = self.poster_locks.setdefault(media_id, threading.Lock())
        with lock:
            source = self.path_for(media_id)
            if source is None:
                return None
            folder = (self.cache_file.parent / 'thumbnails').resolve()
            if not folder.is_relative_to(self.repo):
                return None
            path = folder / (media_id + '.jpg')
            metadata = folder / (media_id + '.json')
            if not path.resolve().is_relative_to(folder) or not metadata.resolve().is_relative_to(folder):
                return None
            temporary = None
            try:
                stat = source.stat()
                fingerprint = [stat.st_mtime_ns, stat.st_size, 480]
                if path.is_file() and path.stat().st_size > 0:
                    try:
                        if json.loads(metadata.read_text()) == fingerprint:
                            return path
                    except (OSError, ValueError):
                        pass
                folder.mkdir(parents=True, exist_ok=True)
                if not folder.resolve().is_relative_to(self.repo):
                    return None
                ffmpeg = shutil.which('ffmpeg') or '/opt/homebrew/bin/ffmpeg'
                at = min(.2, max(0, record.get('durationSeconds', 0) / 2))
                with self.poster_slots:
                    with tempfile.NamedTemporaryFile(prefix='.poster-', suffix='.jpg', dir=folder, delete=False) as target:
                        temporary = Path(target.name)
                    result = subprocess.run([ffmpeg, '-v', 'error', '-nostdin', '-y', '-ss', str(at),
                        '-i', str(source), '-frames:v', '1', '-an', '-vf', 'scale=480:-2',
                        '-q:v', '4', '-threads', '1', str(temporary)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
                    if result.returncode or not temporary.is_file() or temporary.stat().st_size == 0:
                        return None
                    temporary.replace(path)
                    metadata.write_text(json.dumps(fingerprint))
                return path
            except (OSError, ValueError, subprocess.SubprocessError):
                return None
            finally:
                if temporary:
                    temporary.unlink(missing_ok=True)

    def sources(self):
        with self.lock:
            return {key: self._paths[key] for key, asset in self._records.items() if asset['kind'] == 'video' and asset['durationFrames'] > 0}

    def duration_for(self, media_id):
        return (self.get(media_id) or {}).get('durationFrames', 0)
