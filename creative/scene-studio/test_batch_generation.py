"""Background batch lifecycle and HTTP checks with a fake local bridge only."""
import http.client
import json
from pathlib import Path
import tempfile
import threading
import time
import unittest
import uuid

import server
from batch_generation import BatchManager, BridgeRejected, KNOWN_MODELS
from test_server import png


class FakeBridge:
    def __init__(self, creative):
        self.creative = creative
        self.submissions = []
        self.gets = []
        self.outputs = {}
        self.rejected = set()
        self.ambiguous = False
        self.reject_output_path = False
        self.final_status = 'completed'
        self.gate = None
        self.refreshed = 0

    def config(self):
        return {'configured': True, 'models': list(KNOWN_MODELS.values()), 'secret': 'must-not-leak'}

    def library(self, refresh=False):
        self.refreshed += bool(refresh)
        assets = [{'id': str(p.relative_to(self.creative)), 'kind': 'image',
                   'relativePath': str(p.relative_to(self.creative.parent))}
                  for p in self.creative.rglob('*.png') if not any(part.startswith('.') for part in p.relative_to(self.creative).parts)]
        for job_id, path in self.outputs.items():
            assets.append({'id': 'output_' + job_id, 'kind': 'video',
                           'relativePath': 'creative/assets/ref.png' if self.reject_output_path else str(path.relative_to(self.creative.parent))})
        return {'assets': assets}

    def submit(self, payload):
        self.submissions.append(payload)
        if len(self.submissions) in self.rejected:
            raise BridgeRejected('Fake local queue limit reached.')
        if self.ambiguous:
            raise TimeoutError('Response lost after server accepted the request.')
        job_id = uuid.uuid4().hex
        directory = self.creative / 'editor' / 'generated' / job_id
        directory.mkdir(parents=True)
        path = directory / ('media.png' if payload['model'] == 'nano-banana2' else 'media.mp4')
        path.write_bytes(png() if path.suffix == '.png' else b'\x00\x00\x00\x18ftypmp42' + bytes(30))
        self.outputs[job_id] = path
        return {'id': job_id, 'status': 'queued'}

    def get(self, job_id):
        self.gets.append(job_id)
        if self.gate:
            self.gate.wait(4)
        return {'id': job_id, 'status': self.final_status, 'outputId': 'output_' + job_id,
                'url': 'https://unused-and-never-forwarded.example/result'}


class BatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.creative = Path(self.temp.name) / 'creative'
        (self.creative / 'assets').mkdir(parents=True)
        (self.creative / 'assets' / 'ref.png').write_bytes(png())
        self.store = server.JobStore(Path(self.temp.name) / '.state', self.creative)
        self.bridge = FakeBridge(self.creative)
        self.managers = []
        self.manager = self.make_manager()

    def tearDown(self):
        if self.bridge.gate:
            self.bridge.gate.set()
        for manager in self.managers:
            manager.close()
        self.temp.cleanup()

    def make_manager(self, autostart=False):
        manager = BatchManager(self.store, server.validate_payload, server.atomic_json,
                               server.canonical_json, server.Conflict, bridge=self.bridge,
                               autostart=autostart, poll_seconds=.01)
        self.managers.append(manager)
        return manager

    def payload(self, count=2, **changes):
        return {'idempotencyKey': str(uuid.uuid4()), 'engine': 'fal', 'model': 'seedance25',
                'requests': [{'sceneId': f's{i:02}', 'type': 'video', 'duration': 4,
                              'prompt': f'Painted scene {i}, one restrained movement.',
                              'modification': 'Preserve the drawn faces.',
                              'startingImage': '/creative/assets/ref.png'} for i in range(count)], **changes}

    def test_batch_is_idempotent_and_result_imports_without_replacing_original(self):
        payload = self.payload()
        batch, created = self.manager.submit(payload)
        self.assertTrue(created)
        duplicate, created = self.manager.submit(payload)
        self.assertFalse(created)
        self.assertEqual([j['id'] for j in batch['jobs']], [j['id'] for j in duplicate['jobs']])
        self.assertEqual(len(self.bridge.submissions), 0)
        for job in batch['jobs']:
            self.manager.run_job(job['id'])
            done = self.store.get(job['id'])
            self.assertEqual(done['status'], 'completed')
            self.assertTrue(done['result']['url'].endswith('/artifact'))
            self.assertTrue((self.store._dir(job['id']) / done['result']['filename']).is_file())
            self.assertNotIn('https://', json.dumps(done))
        self.assertEqual(len(self.bridge.submissions), 2)
        self.assertEqual((self.creative / 'assets' / 'ref.png').read_bytes(), png())
        self.assertIn('Requested change:', self.bridge.submissions[0]['prompt'])
        payload['requests'][0]['prompt'] += ' Changed.'
        with self.assertRaises(server.Conflict):
            self.manager.submit(payload)

    def test_partial_failure_does_not_stop_other_scene(self):
        self.bridge.rejected = {1}
        batch, _ = self.manager.submit(self.payload())
        for job in batch['jobs']:
            self.manager.run_job(job['id'])
        self.assertEqual([self.store.get(j['id'])['status'] for j in batch['jobs']], ['failed', 'completed'])

    def test_ambiguous_submission_is_not_retried_after_restart(self):
        self.bridge.ambiguous = True
        batch, _ = self.manager.submit(self.payload(1))
        ident = batch['jobs'][0]['id']
        self.manager.run_job(ident)
        self.assertEqual(self.store.get(ident)['status'], 'submission_unknown')
        restarted = self.make_manager()
        restarted.run_job(ident)
        self.assertEqual(len(self.bridge.submissions), 1)

    def test_interrupted_submit_is_flagged_but_accepted_job_resumes_polling(self):
        batch, _ = self.manager.submit(self.payload())
        first, second = [j['id'] for j in batch['jobs']]
        self.store.update_generation(first, status='submitting')
        response = self.bridge.submit({'sourceId': 'assets/ref.png', 'model': 'seedance25', 'prompt': 'Previously accepted.', 'duration': 4})
        self.store.update_generation(second, status='running', bridgeJobId=response['id'])
        restarted = self.make_manager()
        self.assertEqual(self.store.get(first)['status'], 'submission_unknown')
        restarted.run_job(second)
        self.assertEqual(self.store.get(second)['status'], 'completed')
        self.assertEqual(len(self.bridge.submissions), 1)

    def test_invalid_batch_rejected_before_any_job_or_paid_submission(self):
        cases = [self.payload(7), self.payload(0), self.payload(model='invented'), self.payload(engine='remote')]
        for field, value in [('duration', 7), ('prompt', 'x' * 12001), ('startingImage', '/creative/../secret.png')]:
            data = self.payload(); data['requests'][1][field] = value; cases.append(data)
        duplicate = self.payload(); duplicate['requests'][1]['sceneId'] = duplicate['requests'][0]['sceneId']; cases.append(duplicate)
        for data in cases:
            with self.subTest(data=str(data)[:120]), self.assertRaises(ValueError):
                self.manager.submit(data)
        self.assertEqual(self.store.list(), [])
        self.assertEqual(self.bridge.submissions, [])

    def test_mcp_batch_remains_awaiting_operator(self):
        batch, _ = self.manager.submit(self.payload(engine='mcp', model=None))
        self.assertTrue(all(j['status'] == 'awaiting_mcp' and not j['autonomous'] for j in batch['jobs']))
        self.assertEqual(self.bridge.submissions, [])

    def test_registry_cannot_import_an_unrelated_local_file(self):
        self.bridge.reject_output_path = True
        batch, _ = self.manager.submit(self.payload(1))
        ident = batch['jobs'][0]['id']
        self.manager.run_job(ident)
        self.assertEqual(self.store.get(ident)['status'], 'failed')
        self.assertIsNone(self.store.get(ident)['result'])

    def test_provider_interruption_is_terminal_and_never_automatically_resubmitted(self):
        self.bridge.final_status = 'interrupted'
        batch, _ = self.manager.submit(self.payload(1))
        ident = batch['jobs'][0]['id']
        self.manager.run_job(ident)
        self.assertEqual(self.store.get(ident)['status'], 'failed')
        self.assertEqual(self.store.get(ident)['bridgeStatus'], 'interrupted')
        restarted = self.make_manager()
        restarted.run_job(ident)
        self.assertEqual(len(self.bridge.submissions), 1)

    def test_completed_hidden_image_is_copied_only_when_selected(self):
        previous, _ = self.store.submit({'sceneId': 'hero', 'type': 'image', 'prompt': 'Original reference.'})
        self.store.complete(previous['id'], self.creative / 'assets' / 'ref.png')
        data = self.payload(1)
        data['requests'][0]['startingImage'] = f"/api/studio/jobs/{previous['id']}/artifact"
        batch, _ = self.manager.submit(data)
        self.manager.run_job(batch['jobs'][0]['id'])
        self.assertEqual(self.store.get(batch['jobs'][0]['id'])['status'], 'completed')
        self.assertIn('generation-references/', self.bridge.submissions[0]['sourceId'])

    def test_two_workers_execute_in_parallel_and_duplicate_submit_preserves_running(self):
        self.bridge.gate = threading.Event()
        active = self.make_manager(autostart=True)
        data = self.payload(3)
        batch, _ = active.submit(data)
        deadline = time.monotonic() + 3
        while len(self.bridge.submissions) < 2 and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertEqual(len(self.bridge.submissions), 2)
        duplicate, created = active.submit(data)
        self.assertFalse(created)
        self.assertNotIn('submission_unknown', [j['status'] for j in duplicate['jobs']])
        self.bridge.gate.set()
        deadline = time.monotonic() + 3
        while any(self.store.get(j['id'])['status'] != 'completed' for j in batch['jobs']) and time.monotonic() < deadline:
            time.sleep(.01)
        self.assertEqual(len(self.bridge.submissions), 3)
        self.assertTrue(all(self.store.get(j['id'])['status'] == 'completed' for j in batch['jobs']))

    def test_generation_config_exposes_no_credentials_or_provider_urls(self):
        config = self.manager.config()
        self.assertTrue(config['configured'])
        self.assertEqual(config['concurrency'], 2)
        self.assertEqual(config['maxBatchSize'], 6)
        self.assertNotIn('secret', json.dumps(config))
        self.assertNotIn('endpoint', json.dumps(config))

    def test_http_config_and_batch_contract_without_network_provider(self):
        web = server.StudioServer(('127.0.0.1', 0), self.store, bridge=self.bridge, batch_autostart=False)
        thread = threading.Thread(target=web.serve_forever, daemon=True); thread.start()
        try:
            def call(method, path, payload=None):
                connection = http.client.HTTPConnection('127.0.0.1', web.server_port, timeout=4)
                body = json.dumps(payload) if payload else None
                connection.request(method, path, body, {'Content-Type': 'application/json'} if body else {})
                response = connection.getresponse(); data = json.loads(response.read()); status = response.status
                connection.close(); return status, data
            status, config = call('GET', '/api/studio/generation-config')
            self.assertEqual(status, 200); self.assertTrue(config['configured'])
            payload = self.payload()
            status, batch = call('POST', '/api/studio/batch', payload)
            self.assertEqual(status, 202); self.assertEqual(len(batch['jobs']), 2)
            self.assertEqual(call('POST', '/api/studio/batch', payload)[0], 200)
            self.assertEqual(len(call('GET', '/api/studio/jobs')[1]['jobs']), 2)
            self.assertEqual(self.bridge.submissions, [])
        finally:
            web.shutdown(); web.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
