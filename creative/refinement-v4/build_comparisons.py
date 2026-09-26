#!/usr/bin/env python3
"""Publish only local, probeable refinement assets; works with file:// and HTTP."""
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = [
    ('luna-original', 'videos/luna-original.mp4'),
    ('luna-prompt', 'videos/luna-prompt.mp4'),
    ('luna-pro', 'videos/luna-pro.mp4'),
    ('salsa-original', 'videos/salsa-original.mp4'),
    ('salsa-prompt', 'videos/salsa-prompt.mp4'),
    ('salsa-pro', 'videos/salsa-pro.mp4'),
    ('phone-original', 'videos/phone-original.mp4'),
    ('phone-attic', 'videos/phone-attic.mp4'),
    ('phone-attic-v2', 'videos/phone-attic-v2.mp4'),
    ('film-original', '../gpt-full-film-v1/renders/converse-gpt-seedance25-full-76s.mp4'),
    ('film-a', 'renders/converse-refinement-v4-music-a-76s.mp4'),
    ('film-b', 'renders/converse-refinement-v4-music-b-76s.mp4'),
    ('music-a', 'music/organic-latin-breakbeat-76s.mp3'),
    ('music-b', 'music/tactile-percussion-piano-76s.mp3'),
]


def probe(path):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, timeout=15, check=True)
        data = json.loads(result.stdout)
        duration = float(data['format']['duration'])
        if duration <= 0 or not data['streams']:
            return None
        return data, duration
    except (OSError, subprocess.SubprocessError, ValueError, KeyError):
        return None


def main():
    (ROOT / 'posters').mkdir(exist_ok=True)
    assets = []
    for code, relative in SOURCES:
        path = ROOT / relative
        if not path.is_file():
            continue
        result = probe(path)
        if not result:
            continue
        metadata, duration = result
        is_video = any(s.get('codec_type') == 'video' for s in metadata['streams'])
        entry = {'id': code, 'file': relative, 'duration': round(duration, 3), 'kind': 'video' if is_video else 'audio'}
        if is_video:
            poster = ROOT / 'posters' / f'{code}.jpg'
            if not poster.exists() or poster.stat().st_mtime < path.stat().st_mtime:
                at = min(2.0 if code.startswith('film-') else 0.5, duration / 2)
                subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(at), '-i', str(path), '-frames:v', '1', '-vf', 'scale=960:-2', '-q:v', '3', str(poster)], check=True, timeout=30)
            entry['poster'] = str(poster.relative_to(ROOT))
        assets.append(entry)
    ref_dir = ROOT / 'faces/references'
    salsa = 'salsa-nano-banana-pro-corrected.png' if (ref_dir / 'salsa-nano-banana-pro-corrected.png').is_file() else 'salsa-nano-banana-pro.png'
    references = [str((ref_dir / name).relative_to(ROOT)) for name in ['luna-nano-banana-pro.png', salsa] if (ref_dir / name).is_file()]
    notes_file = ROOT / 'comparison-notes.json'
    notes = json.loads(notes_file.read_text()) if notes_file.exists() else {}
    data = {'version': 1, 'updatedAt': datetime.now(timezone.utc).isoformat(), 'assets': assets, 'references': references, 'notes': notes}
    encoded = json.dumps(data, ensure_ascii=False, indent=2)
    (ROOT / 'comparison-manifest.json').write_text(encoded + '\n')
    (ROOT / 'comparison-data.js').write_text('window.CONVERSE_REFINEMENTS = ' + encoded + ';\n')
    print(f'Published {len(assets)} probeable media files and {len(references)} reference images.')


if __name__ == '__main__':
    main()
