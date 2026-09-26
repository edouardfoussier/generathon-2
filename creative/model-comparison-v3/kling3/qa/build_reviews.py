"""Probe source clips and make labelled contact sheets for human/model inspection."""
from pathlib import Path
import json, subprocess, hashlib
from PIL import Image, ImageDraw

BASE = Path(__file__).resolve().parents[1]
reports = {}
for path in sorted((BASE / 'videos').glob('*.mp4')):
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    duration = float(probe['format']['duration'])
    reports[path.stem] = {'duration_seconds': duration, 'width': v['width'], 'height': v['height'], 'fps': v['r_frame_rate'], 'audio_present': any(s['codec_type'] == 'audio' for s in probe['streams']), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    sheet_path = BASE / 'qa' / (path.stem + '-review.jpg')
    if sheet_path.exists():
        continue
    times = [0, duration * .2, duration * .4, duration * .6, duration * .8, max(0, duration - .1)]
    canvas = Image.new('RGB', (1200, 516), '#171917')
    draw = ImageDraw.Draw(canvas)
    for i, t in enumerate(times):
        frame = BASE / 'qa' / (path.stem + '-frame-' + str(i) + '.jpg')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(t), '-i', str(path), '-frames:v', '1', '-vf', 'scale=400:225:force_original_aspect_ratio=decrease,pad=400:225:(ow-iw)/2:(oh-ih)/2', '-y', str(frame)], check=True)
        canvas.paste(Image.open(frame), ((i % 3) * 400, (i // 3) * 258 + 28))
        draw.text(((i % 3) * 400 + 8, (i // 3) * 258 + 7), f'{path.stem} | {t:.2f}s', fill='white')
        frame.unlink()
    canvas.save(sheet_path, quality=91)
(BASE / 'qa' / 'metadata.json').write_text(json.dumps(reports, indent=2) + '\n')
print(json.dumps({'clips': len(reports), 'seconds': sum(r['duration_seconds'] for r in reports.values())}))
