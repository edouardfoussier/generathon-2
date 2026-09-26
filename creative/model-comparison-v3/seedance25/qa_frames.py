"""Probe downloaded clips and create five-frame contact sheets for visual QA."""
import json
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
reports = []
for movie in sorted((ROOT / 'videos').glob('*.mp4')):
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(movie)]))
    stream = next(x for x in info['streams'] if x['codec_type'] == 'video')
    duration = float(info['format']['duration'])
    times = [min(duration - .1, t) for t in [0, duration * .25, duration * .5, duration * .75, duration - .1]]
    out = ROOT / 'qa' / movie.stem
    out.mkdir(parents=True, exist_ok=True)
    sheet = Image.new('RGB', (1200, 496), '#181a18')
    draw = ImageDraw.Draw(sheet)
    for i, t in enumerate(times):
        frame = out / f'{i}.jpg'
        if not frame.exists():
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-ss', str(t), '-i', str(movie), '-frames:v', '1', '-q:v', '2', '-y', str(frame)], check=True)
        im = Image.open(frame).convert('RGB')
        im.thumbnail((396, 223))
        x, y = (i % 3) * 400, (i // 3) * 248
        sheet.paste(im, (x, y + 23))
        draw.text((x + 6, y + 4), f'{movie.stem} | {t:.2f}s', fill='white')
    sheet.save(ROOT / 'qa' / f'{movie.stem}-contact.jpg', quality=90)
    reports.append({'shotId': movie.stem, 'file': str(movie.relative_to(ROOT.parent.parent.parent)), 'duration': duration, 'width': stream['width'], 'height': stream['height'], 'fps': stream['avg_frame_rate'], 'sizeBytes': movie.stat().st_size, 'audio': any(x['codec_type'] == 'audio' for x in info['streams'])})
(ROOT / 'qa' / 'probe-report.json').write_text(json.dumps(reports, indent=2))
print(json.dumps(reports, indent=2))
