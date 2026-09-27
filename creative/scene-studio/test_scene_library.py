"""Catalog and assignment tests with local fixtures only; no generation requests."""
import copy
import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

import server
from scene_library import SceneLibrary


class Inventory:
    def __init__(self, creative):
        self.creative = creative
        self.refreshes = 0
        self.records = []
        for i, (name, kind) in enumerate([('court.mp4', 'video'), ('film.mp4', 'video'),
                                        ('unknown.mp4', 'video'), ('still.png', 'image')]):
            path = creative / name
            path.write_bytes(b'local fixture')
            self.records.append({'id': 'm_' + str(i) * 20, 'kind': kind, 'name': name,
                'relativePath': 'creative/' + name, 'durationSeconds': 76 if name == 'film.mp4' else 8,
                'url': '/library/wrong-port', 'posterUrl': '/library-poster/old.jpg'})

    def snapshot(self):
        return {'assets': copy.deepcopy(self.records)}

    def path_for(self, key):
        item = next((r for r in self.records if r['id'] == key), None)
        return self.creative / Path(item['relativePath']).name if item else None

    def refresh(self):
        self.refreshes += 1

    def poster_path(self, key):
        return None


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.creative = root / 'creative'
        self.folder = self.creative / 'scene-studio'
        self.folder.mkdir(parents=True)
        self.store = server.JobStore(root / 'state', self.creative)
        self.media = Inventory(self.creative)
        self.catalog = self.folder / 'scene-catalog.json'
        self.catalog.write_text(json.dumps({'entries': [
            {'relativePath': 'creative/court.mp4', 'group': 'scenes', 'sceneIds': ['s08-basketball'],
             'note': 'Verified shot plan.', 'ranges': [
                 {'sceneId': 's08-basketball', 'inSeconds': 1, 'outSeconds': 7},
                 {'sceneId': 's99', 'inSeconds': 0, 'outSeconds': 2},
                 {'sceneId': 's08-basketball', 'inSeconds': 1, 'outSeconds': 20}]},
            {'relativePath': 'creative/film.mp4', 'group': 'films', 'sceneIds': [], 'note': 'Full edit.'}]}))
        (self.folder / 'project.json').write_text(json.dumps({'scenes': [{'id': 's08-basketball', 'title': 'Le tir'}]}))
        self.library = SceneLibrary(self.store, server.atomic_json, self.media)

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_video_inventory_and_verified_ranges(self):
        data = self.library.snapshot()
        self.assertEqual(data['counts'], {'total': 3, 'scenes': 1, 'films': 1, 'other': 0, 'unassigned': 1})
        court = data['assets'][0]
        self.assertEqual(court['url'], '/creative/court.mp4')
        self.assertEqual(court['ranges'], [{'sceneId': 's08-basketball', 'inSeconds': 1, 'outSeconds': 7}])
        self.assertEqual(court['posterUrl'], '/api/studio/library/' + court['id'] + '/poster')
        self.assertEqual(data['assets'][2]['sceneIds'], [])
        self.library.snapshot(refresh=True)
        self.assertEqual(self.media.refreshes, 1)

    def test_assignment_survives_restart_without_rewriting_sources_or_curated_catalog(self):
        before = self.catalog.read_bytes()
        key = self.media.records[0]['id']
        changed = self.library.assign({'id': key, 'sceneIds': ['custom-shot'], 'group': 'scenes'})['asset']
        self.assertEqual(changed['ranges'], [])
        self.assertTrue(changed['manuallyAssigned'])
        restarted = SceneLibrary(self.store, server.atomic_json, self.media)
        self.assertEqual(restarted.snapshot()['assets'][0]['sceneIds'], ['custom-shot'])
        self.assertEqual(self.catalog.read_bytes(), before)
        self.assertEqual((self.creative / 'court.mp4').read_bytes(), b'local fixture')

    def test_invalid_or_unknown_assignments_are_not_saved(self):
        for change in [
            {'id': 'm_' + '0' * 20, 'sceneIds': [], 'group': 'scenes'},
            {'id': 'm_' + '0' * 20, 'sceneIds': ['../escape'], 'group': 'scenes'},
            {'id': 'm_' + '0' * 20, 'sceneIds': ['s01'], 'group': 'other'},
            {'id': 'm_' + 'f' * 20, 'sceneIds': ['s01'], 'group': 'scenes'},
            {'id': 'http://evil/clip', 'sceneIds': [], 'group': 'other'},
        ]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.library.assign(change)
        self.assertFalse(self.library.overrides_path.exists())

    def test_completed_jobs_use_generation_scene_and_do_not_expose_private_file_paths(self):
        job, _ = self.store.submit({'sceneId': 's08-basketball', 'type': 'video', 'prompt': 'A jump shot.'})
        self.assertEqual(self.library.snapshot()['counts']['total'], 3)
        video = self.creative / 'tiny.mp4'
        video.write_bytes(b'\x00\x00\x00\x18ftypisom000000000000')
        self.store.complete(job['id'], video)
        with patch.object(self.library, '_job_duration', return_value=4):
            asset = self.library.snapshot()['assets'][-1]
        self.assertEqual(asset['sceneIds'], ['s08-basketball'])
        self.assertEqual(asset['url'], f"/api/studio/jobs/{job['id']}/artifact")
        self.assertNotIn('.state', json.dumps(asset))
        self.assertEqual(asset['durationSeconds'], 4)

    def test_missing_mapping_keeps_unknown_clips_visible(self):
        self.catalog.unlink()
        data = self.library.snapshot()
        self.assertEqual(data['counts']['unassigned'], 3)
        self.assertEqual(data['counts']['total'], 3)

    def test_corrupt_assignment_file_is_preserved_on_write(self):
        self.library.overrides_path.write_text('{unreadable')
        with self.assertRaisesRegex(ValueError, 'no data was overwritten'):
            self.library.assign({'id': self.media.records[0]['id'], 'sceneIds': ['s08-basketball'], 'group': 'scenes'})
        self.assertEqual(self.library.overrides_path.read_text(), '{unreadable')

    def test_http_read_refresh_and_assignment_boundaries(self):
        web = server.StudioServer(('127.0.0.1', 0), self.store, batch_autostart=False)
        web.scene_library = self.library
        thread = threading.Thread(target=web.serve_forever, daemon=True)
        thread.start()
        def request(method, suffix='', data=None, headers=None):
            connection = http.client.HTTPConnection('127.0.0.1', web.server_port, timeout=5)
            connection.request(method, '/api/studio/library' + suffix,
                body=json.dumps(data) if data is not None else None,
                headers=headers or {'Content-Type': 'application/json'})
            response = connection.getresponse()
            result = response.status, json.loads(response.read())
            connection.close()
            return result
        try:
            self.assertEqual(request('GET')[1]['counts']['total'], 3)
            self.assertEqual(request('POST', '/refresh', {})[0], 200)
            self.assertEqual(request('POST', '/assignment', {
                'id': self.media.records[2]['id'], 'sceneIds': ['s08-basketball'], 'group': 'scenes'})[0], 200)
            self.assertEqual(request('GET')[1]['counts']['scenes'], 2)
            self.assertEqual(request('POST', '/assignment', {}, {'Content-Type': 'application/json',
                'Origin': 'https://other.invalid'})[0], 403)
            self.assertEqual(request('POST', '/assignment', {})[0], 400)
        finally:
            web.shutdown()
            web.server_close()


if __name__ == '__main__':
    unittest.main()
