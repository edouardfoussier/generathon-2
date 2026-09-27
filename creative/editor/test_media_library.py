#!/usr/bin/env python3
"""Catalog security/provenance, source-specific validation, and mixed-media export."""
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace

from media_library import MediaLibrary
import server


class LibraryTests(unittest.TestCase):
    def test_manifest_metadata_reference_mapping_stability_and_hidden_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            collection = repo / 'creative' / 'story-v5'
            collection.mkdir(parents=True)
            (collection / 'luna.png').write_bytes(b'image fixture')
            (collection / 'next.png').write_bytes(b'image fixture')
            (collection / 'qa').mkdir()
            (collection / 'qa' / 'frame.png').write_bytes(b'ignored')
            (collection / '.state').mkdir()
            (collection / '.state' / 'secret.png').write_bytes(b'ignored')
            outside = repo / 'private.png'
            outside.write_bytes(b'outside')
            (collection / 'escape.png').symlink_to(outside)
            (collection / 'manifest.json').write_text(json.dumps({'assets': [
                {'code': 'L01', 'file': 'luna.png', 'title': {'fr': 'Luna', 'en': 'Luna'}, 'model': 'test'},
                {'code': 'K01', 'file': 'next.png', 'prompt': 'Turn toward the light.', 'referenceCodes': ['L01']},
                {'file': '../private.png', 'prompt': 'Do not expose this path'},
            ]}))
            library = MediaLibrary(repo)
            first = library.snapshot()
            self.assertEqual(len(first['assets']), 2)
            luna = next(a for a in first['assets'] if a['code'] == 'L01')
            shot = next(a for a in first['assets'] if a['code'] == 'K01')
            self.assertEqual(shot['referenceIds'], [luna['id']])
            self.assertEqual(shot['prompt'], 'Turn toward the light.')
            self.assertEqual(library.path_for(luna['id']), (collection / 'luna.png').resolve())
            self.assertIsNone(library.path_for('../../private.png'))
            self.assertEqual(library.refresh()['assets'], first['assets'])
            self.assertNotIn(str(repo), json.dumps(first))
            # Regeneration manifests refer directly to stable catalog IDs.
            (collection / 'generated.png').write_bytes(b'image variant')
            (collection / 'variant-manifest.json').write_text(json.dumps({'assets': [{
                'file': 'generated.png', 'referenceIds': [luna['id']], 'sourceId': shot['id']}]}))
            variant = next(a for a in library.refresh()['assets'] if a['name'] == 'generated')
            self.assertEqual(variant['sourceId'], shot['id'])
            self.assertEqual(variant['referenceIds'], [luna['id'], shot['id']])
            # A registered path replaced by an escaping symlink is denied too.
            (collection / 'luna.png').unlink()
            (collection / 'luna.png').symlink_to(outside)
            self.assertIsNone(library.path_for(luna['id']))

    def test_source_specific_bounds_and_audio_options(self):
        recipe = {'version': 1, 'fps': 24, 'audioMode': 'source', 'segments': [
            {'id': 'first', 'sourceId': 'short', 'inFrame': 0, 'outFrame': 48}]}
        self.assertEqual(server.validate_recipe(recipe, {'short'}, source_durations={'short': 48}), recipe)
        recipe['segments'][0]['outFrame'] = 49
        with self.assertRaises(server.ValidationError):
            server.validate_recipe(recipe, {'short'}, source_durations={'short': 48})
        recipe['segments'][0]['outFrame'] = 24
        recipe['soundtrackId'] = 'song'
        with self.assertRaises(server.ValidationError):
            server.validate_recipe(recipe, {'short'}, audio_ids={'different-song'})
        result = server.validate_recipe(recipe, {'short'}, audio_ids={'song'})
        self.assertEqual(result['soundtrackId'], 'song')
        recipe['audioMode'] = 'unknown'
        with self.assertRaises(server.ValidationError):
            server.validate_recipe(recipe, {'short'}, audio_ids={'song'})


class MixedExportTests(unittest.TestCase):
    def test_short_clips_native_audio_silent_video_and_music_override(self):
        ffmpeg, ffprobe = server.find_program('ffmpeg'), server.find_program('ffprobe')
        with tempfile.TemporaryDirectory() as folder:
            repo = Path(folder)
            collection = repo / 'creative' / 'fixtures'
            collection.mkdir(parents=True)
            silent, sound, song = [collection / name for name in ('silent.mp4', 'sound.mp4', 'music.wav')]
            common = [ffmpeg, '-v', 'error', '-nostdin', '-y']
            subprocess.run(common + ['-f', 'lavfi', '-i', 'color=c=red:s=160x90:r=30:d=2',
                                    '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(silent)], check=True)
            subprocess.run(common + ['-f', 'lavfi', '-i', 'color=c=blue:s=160x90:r=24:d=2',
                                    '-f', 'lavfi', '-i', 'sine=frequency=440:duration=2',
                                    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest', str(sound)], check=True)
            subprocess.run(common + ['-f', 'lavfi', '-i', 'sine=frequency=880:duration=1', str(song)], check=True)
            library = MediaLibrary(repo)
            assets = {a['name']: a for a in library.snapshot()['assets']}
            self.assertEqual(assets['silent']['durationFrames'], 48)
            self.assertFalse(assets['silent']['hasAudio'])
            self.assertTrue(assets['sound']['hasAudio'])
            self.assertEqual(assets['silent']['posterUrl'], '/library-poster/' + assets['silent']['id'] + '.jpg')
            with patch('media_library.subprocess.run', wraps=subprocess.run) as encoder:
                with ThreadPoolExecutor(max_workers=4) as pool:
                    posters = list(pool.map(library.poster_path, [assets['silent']['id']] * 4))
                self.assertEqual(encoder.call_count, 1)
            self.assertTrue(all(p == posters[0] for p in posters))
            self.assertEqual(posters[0].read_bytes()[:2], b'\xff\xd8')
            # Reopening the library uses the disk cache without re-encoding.
            reopened = MediaLibrary(repo)
            with patch('media_library.subprocess.run', side_effect=AssertionError('Unexpected encode')):
                self.assertEqual(reopened.poster_path(assets['silent']['id']), posters[0])
            self.assertIsNone(library.poster_path('../../private'))
            self.assertIsNone(library.poster_path(assets['music']['id']))
            handler = object.__new__(server.EditorHandler)
            handler.server = SimpleNamespace(library=library, manager=None)
            self.assertEqual(handler._resolve_file(assets['silent']['posterUrl']), (posters[0], False))
            self.assertEqual(handler._resolve_file('/library-poster/unknown.jpg'), (None, False))
            self.assertEqual(handler._resolve_file('/library-poster/../../private.jpg'), (None, False))
            # A changed source invalidates its thumbnail; extraction failure has no stale result.
            silent.write_bytes(b'not a video')
            self.assertIsNone(library.poster_path(assets['silent']['id']))
            subprocess.run(common + ['-f', 'lavfi', '-i', 'color=c=red:s=160x90:r=30:d=2',
                                    '-an', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(silent)], check=True)
            library.refresh()
            manager = server.ExportManager(output_dir=repo / 'exports', library=library)
            recipe = {'version': 1, 'fps': 24, 'audioMode': 'source', 'segments': [
                {'id': 'silent', 'sourceId': assets['silent']['id'], 'inFrame': 24, 'outFrame': 48},
                {'id': 'sound', 'sourceId': assets['sound']['id'], 'inFrame': 0, 'outFrame': 24}]}
            def render(payload):
                job = manager.submit(payload)
                deadline = time.monotonic() + 60
                while job['status'] not in {'completed', 'failed'} and time.monotonic() < deadline:
                    time.sleep(.05)
                    job = manager.get(job['id'])
                self.assertEqual(job['status'], 'completed', job)
                path = manager.output_dir / (job['id'] + '.mp4')
                data = json.loads(subprocess.check_output([ffprobe, '-v', 'error', '-count_frames', '-show_entries',
                    'stream=codec_type,nb_read_frames,avg_frame_rate:format=duration', '-of', 'json', str(path)]))
                video = next(s for s in data['streams'] if s['codec_type'] == 'video')
                self.assertEqual(int(video['nb_read_frames']), 48)
                self.assertEqual(video['avg_frame_rate'], '24/1')
                return path
            path = render(recipe)
            import array
            pcm = array.array('f')
            pcm.frombytes(subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(path), '-vn', '-ac', '1',
                                                  '-ar', '48000', '-f', 'f32le', 'pipe:1']))
            self.assertLess(max(abs(v) for v in pcm[:47000]), .001)
            self.assertGreater(max(abs(v) for v in pcm[50000:94000]), .05)
            recipe['soundtrackId'] = assets['music']['id']
            replacement = render(recipe)
            pcm = array.array('f')
            pcm.frombytes(subprocess.check_output([ffmpeg, '-v', 'error', '-i', str(replacement), '-vn', '-ac', '1',
                                                  '-ar', '48000', '-f', 'f32le', 'pipe:1']))
            self.assertGreater(max(abs(v) for v in pcm[:47000]), .05)
            self.assertLess(max(abs(v) for v in pcm[50000:94000]), .001)


if __name__ == '__main__':
    unittest.main(verbosity=2)
