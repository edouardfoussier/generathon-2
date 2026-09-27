"""Scene labels layered over the existing media inventory; never moves source files."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import threading
import time
from urllib.parse import quote

from media_library import MediaLibrary

GROUPS = {'scenes', 'films', 'other', 'unassigned'}
SCENE_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_.-]{0,79}$')
MEDIA_ID = re.compile(r'^(?:m_[a-f0-9]{20}|studio_[a-f0-9]{32})$')


class SceneLibrary:
    def __init__(self, store, write, media=None):
        self.store, self.write = store, write
        self.folder = store.creative / 'scene-studio'
        self.overrides_path = store.state / 'scene-assignments.json'
        self.lock = threading.RLock()
        self._media = media
        self._refreshed = time.monotonic() if media else 0
        self._job_probes = {}

    @property
    def media(self):
        if self._media is None:
            self._media = MediaLibrary(self.store.creative.parent)
            # Studio has its own write cache; Cut Room can stay running with its key.
            self._media.cache_file = self.store.state / 'library-cache.json'
            self._refreshed = time.monotonic()
        return self._media

    @staticmethod
    def _json(path, default):
        try:
            return json.loads(path.read_text())
        except (OSError, ValueError):
            return default

    def _assignment(self, value):
        if not isinstance(value, dict) or value.get('group') not in GROUPS:
            raise ValueError('Choose scenes, films, other or unassigned.')
        ids = value.get('sceneIds', [])
        if (not isinstance(ids, list) or len(ids) > 20 or
                any(not isinstance(s, str) or not SCENE_ID.fullmatch(s) for s in ids)):
            raise ValueError('Provide up to 20 valid scene identifiers.')
        ids = list(dict.fromkeys(ids))
        if value['group'] == 'scenes' and not ids:
            raise ValueError('Choose at least one scene for this clip.')
        if value['group'] in {'other', 'unassigned'} and ids:
            raise ValueError('Only scene clips and multi-scene films can have scene labels.')
        return {'group': value['group'], 'sceneIds': ids}

    def _labels(self, asset, entry, overrides):
        override = overrides.get(asset['relativePath'])
        chosen = override if override is not None else entry
        try:
            labels = self._assignment(chosen)
        except ValueError:
            labels = {'sceneIds': [], 'group': 'unassigned'}
        asset.update(labels)
        asset['classificationNote'] = ('Classement modifié dans l’atelier.' if override is not None else
            str((entry or {}).get('note') or 'Aucun rattachement certain : à classer après visionnage.'))
        asset['manuallyAssigned'] = override is not None
        # Only editorially verified ranges are suggested. A manual reassignment
        # cannot accidentally retain ranges from another story scene.
        asset['ranges'] = []
        if override is None:
            for item in (entry or {}).get('ranges', []):
                if not isinstance(item, dict):
                    continue
                first, last = item.get('inSeconds'), item.get('outSeconds')
                if (item.get('sceneId') in labels['sceneIds'] and
                        type(first) in (int, float) and type(last) in (int, float) and
                        math.isfinite(first) and math.isfinite(last) and 0 <= first < last and
                        0 < asset.get('durationSeconds', 0) >= last - .05):
                    asset['ranges'].append({'sceneId': item['sceneId'], 'inSeconds': first,
                                            'outSeconds': min(last, asset['durationSeconds'])})
        return asset

    def _job_duration(self, path):
        fingerprint = (path.stat().st_mtime_ns, path.stat().st_size)
        cached = self._job_probes.get(str(path))
        if cached and cached[0] == fingerprint:
            return cached[1]
        duration = 0
        try:
            data = json.loads(subprocess.check_output([
                shutil.which('ffprobe') or '/opt/homebrew/bin/ffprobe', '-v', 'error',
                '-show_entries', 'format=duration', '-of', 'json', str(path)],
                timeout=15, stderr=subprocess.DEVNULL))
            duration = float(data.get('format', {}).get('duration', 0))
            if not math.isfinite(duration) or duration < 0:
                duration = 0
        except (OSError, ValueError, subprocess.SubprocessError):
            pass
        self._job_probes[str(path)] = fingerprint, duration
        return duration

    def snapshot(self, refresh=False):
        with self.lock:
            media = self.media
            if refresh or time.monotonic() - self._refreshed > 60:
                media.refresh()
                self._refreshed = time.monotonic()
            document = self._json(self.folder / 'scene-catalog.json', {})
            entries = {e['relativePath']: e for e in document.get('entries', [])
                       if isinstance(e, dict) and isinstance(e.get('relativePath'), str)}
            overrides = self._json(self.overrides_path, {})
            if not isinstance(overrides, dict):
                overrides = {}
            project = self._json(self.folder / 'project.json', {})
            scenes = [{'id': s['id'], 'title': s['title']} for s in project.get('scenes', [])]
            titles = {s['id']: s['title'] for s in scenes}
            assets = []
            for asset in media.snapshot()['assets']:
                if asset['kind'] != 'video' or not media.path_for(asset['id']):
                    continue
                asset['url'] = '/' + quote(asset['relativePath'], safe='/')
                if not asset.get('posterUrl', '').startswith('/creative/'):
                    asset['posterUrl'] = f"/api/studio/library/{asset['id']}/poster"
                entry = entries.get(asset['relativePath'])
                self._labels(asset, entry, overrides)
                if asset['relativePath'].startswith('creative/scene-studio/assets/clips/'):
                    scene_id = Path(asset['relativePath']).stem
                    asset['name'] = titles.get(scene_id, asset['name']) + ' · montage V4'
                assets.append(asset)
            for job in self.store.list():
                if job.get('status') != 'completed' or job.get('type') != 'video':
                    continue
                result = job.get('result') or {}
                name = result.get('filename', '')
                if name not in {'result.mp4', 'result.webm'}:
                    continue
                folder = self.store._dir(job['id']).resolve()
                path = (folder / name).resolve()
                if path.parent != folder or not path.is_file():
                    continue
                sid = job['sceneId']
                asset = {'id': 'studio_' + job['id'], 'kind': 'video', 'jobId': job['id'],
                         'name': titles.get(sid, sid) + ' · nouvelle prise',
                         'url': f"/api/studio/jobs/{job['id']}/artifact",
                         'posterUrl': None, 'relativePath': 'studio:' + job['id'],
                         'collection': 'scene-studio-generations', 'model': job.get('model', job.get('provider', '')),
                         'durationSeconds': self._job_duration(path), 'modifiedAt': path.stat().st_mtime,
                         'prompt': job.get('prompt', ''), 'provenance': 'Génération de l’atelier · ' + job['id']}
                self._labels(asset, {'group': 'scenes', 'sceneIds': [sid],
                                    'note': 'Scène enregistrée lors de la génération.'}, overrides)
                assets.append(asset)
            counts = {'total': len(assets), **{group: 0 for group in GROUPS}}
            for asset in assets:
                counts[asset['group']] += 1
            return {'assets': assets, 'scenes': scenes, 'counts': counts}

    def assign(self, payload):
        if not isinstance(payload, dict) or set(payload) != {'id', 'sceneIds', 'group'}:
            raise ValueError('Provide id, sceneIds and group.')
        if not isinstance(payload['id'], str) or not MEDIA_ID.fullmatch(payload['id']):
            raise ValueError('Unknown media identifier.')
        labels = self._assignment(payload)
        with self.lock:
            asset = next((a for a in self.snapshot()['assets'] if a['id'] == payload['id']), None)
            if asset is None:
                raise ValueError('Clip not found in this local library.')
            try:
                overrides = json.loads(self.overrides_path.read_text())
            except FileNotFoundError:
                overrides = {}
            except (OSError, ValueError):
                raise ValueError('Saved assignments are unreadable; no data was overwritten.')
            if not isinstance(overrides, dict):
                raise ValueError('Saved assignments are unreadable; no data was overwritten.')
            overrides[asset['relativePath']] = labels
            self.write(self.overrides_path, overrides)
            return {'asset': self._labels(copy.deepcopy(asset), None, overrides)}

    def poster(self, media_id):
        if not MEDIA_ID.fullmatch(media_id):
            return None
        with self.lock:
            media = self.media
        return media.poster_path(media_id)
