#!/usr/bin/env python3
"""Publish reviewed motion exports and current generation statuses to the board.

Only ready/completed records with a real, probeable local video become cards.
Manifests are read from ../continuity-video-v1/manifest.json and
../motion-design-v1/manifest.json, or positional arguments. All paths in a source
manifest are relative to its directory. Signed media URLs are never copied.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess

BOARD = Path(__file__).resolve().parent
CREATIVE = BOARD.parent
READY = {'ready', 'completed', 'complete', 'reviewed'}
MODELS = [('opening-n', 'Nano Banana 2'), ('opening-s', 'Seedream 5 Pro'),
          ('opening-g', 'GPT Image 2.5 Sunburst')]


def load(path):
    return json.loads(path.read_text())


def localized(value, language):
    if isinstance(value, dict):
        return str(value.get(language) or value.get('en') or value.get('fr') or '')
    return value if isinstance(value, str) else ''


def local_media(source, value, extensions):
    if not isinstance(value, str) or not value or '://' in value:
        return None
    path = (source.parent / value).resolve()
    if not path.is_relative_to(CREATIVE.resolve()) or not path.is_file() or path.suffix.lower() not in extensions:
        return None
    return path


def probe(path):
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration:stream=codec_type', '-of', 'json', str(path)],
        capture_output=True, text=True, check=True, timeout=30)
    metadata = json.loads(result.stdout)
    duration = float(metadata.get('format', {}).get('duration', 0))
    if duration <= 0 or not any(stream.get('codec_type') == 'video' for stream in metadata.get('streams', [])):
        raise ValueError(f'No playable video found: {path}')
    return round(duration, 3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifests', nargs='*', type=Path)
    args = parser.parse_args()
    sources = args.manifests or [CREATIVE / 'continuity-video-v1/manifest.json',
                                 CREATIVE / 'motion-design-v1/manifest.json']
    prefix = 'window.CONVERSE_ASSETS = '
    raw = (BOARD / 'assets.js').read_text()
    if not raw.startswith(prefix):
        raise ValueError('Unexpected assets.js format; refusing to overwrite.')
    before = json.loads(raw[len(prefix):].strip().removesuffix(';'))
    preserved = [item for item in before if item.get('category') != 'motionlab']
    codes = {item['code'] for item in preserved}
    cards, skipped = [], []
    for source in sources:
        if not source.is_file():
            continue
        for record in load(source).get('assets', []):
            code = record.get('code')
            video = local_media(source, record.get('localFile'), {'.mp4', '.webm', '.mov'})
            if record.get('status', '').lower() not in READY or not video:
                skipped.append(code)
                continue
            group = record.get('group')
            if group not in {'openings', 'full-film'} or not code or code in codes:
                raise ValueError(f'Missing group or duplicate code: {code}')
            if group == 'openings' and record.get('treatmentId') not in dict(MODELS):
                raise ValueError(f'Opening requires treatmentId opening-n/s/g: {code}')
            duration = probe(video)
            if record.get('durationSeconds') and abs(duration - float(record['durationSeconds'])) > 0.3:
                raise ValueError(f'Duration differs from source manifest: {code}')
            codes.add(code)
            card = {'code': code, 'category': 'motionlab', 'group': group,
                'mediaType': 'video', 'status': 'reviewed', 'filename': os.path.relpath(video, BOARD),
                'durationSeconds': duration, 'imageModel': record.get('imageModel', ''),
                'videoModel': record.get('videoModel', ''), 'model': record.get('videoModel', ''),
                'referenceCodes': record.get('referenceCodes', []), 'aspectRatio': '16:9'}
            if record.get('treatmentId'):
                card['treatmentId'] = record['treatmentId']
            for name in ['title', 'subtitle', 'note']:
                card[name] = localized(record.get(name), 'fr')
                card[name + 'En'] = localized(record.get(name), 'en')
            poster = local_media(source, record.get('poster'), {'.jpg', '.jpeg', '.png', '.webp'})
            if poster:
                card['poster'] = os.path.relpath(poster, BOARD)
            cards.append(card)
    cards.sort(key=lambda item: (['openings', 'full-film'].index(item['group']),
        [key for key, _ in MODELS].index(item['treatmentId']) if item.get('treatmentId') else 9))
    plan_path = CREATIVE / 'continuity-video-v1/plan.json'
    plan = load(plan_path) if plan_path.is_file() else {}
    variants = {item['id']: item for item in plan.get('variants', [])}
    status = {'treatments': []}
    for key, label in MODELS:
        variant = variants.get(key, {})
        ready = next((card for card in cards if card.get('treatmentId') == key), None)
        status['treatments'].append({'id': key, 'assetModel': label,
            'status': 'ready' if ready else variant.get('status', 'not-submitted'),
            'referenceCodes': variant.get('codes', [])})
    status['fullFilmReady'] = any(card['group'] == 'full-film' for card in cards)
    (BOARD / 'motion-status.js').write_text('window.CONVERSE_MOTION_STATUS = ' +
        json.dumps(status, ensure_ascii=False, indent=2) + ';\n')
    (BOARD / 'assets.js').write_text(prefix + json.dumps(preserved + cards, ensure_ascii=False, indent=2) + ';\n')
    manifest = load(BOARD / 'manifest.json')
    manifest['jobs'] = [job for job in manifest['jobs'] if job.get('category') != 'motionlab'] + cards
    manifest['motionExploration'] = {'publishedVideoCount': len(cards), 'status': status,
        'pendingOrUnavailableCodes': skipped,
        'sourceManifests': [os.path.relpath(source.resolve(), BOARD) for source in sources]}
    if cards:
        manifest['phase'] = 'Exploration 12 — Continuity in motion'
    (BOARD / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    after = json.loads((BOARD / 'assets.js').read_text()[len(prefix):].strip().removesuffix(';'))
    assert [item for item in after if item.get('category') != 'motionlab'] == preserved
    print(f'Published {len(cards)} motion videos; preserved {len(preserved)} existing cards; skipped {len(skipped)} unavailable records.')


if __name__ == '__main__':
    main()
