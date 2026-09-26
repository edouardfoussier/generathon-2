"""Probe generated Veo sources and assemble evenly sampled contact sheets."""
from pathlib import Path
import json, subprocess
from PIL import Image, ImageDraw

UNIT = Path(__file__).resolve().parents[1]
records = []
for video in sorted((UNIT / 'videos').glob('*.mp4')):
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    stream = next(s for s in probe['streams'] if s['codec_type']=='video')
    duration = float(probe['format']['duration'])
    record = {'id':video.stem,'file':str(video.relative_to(UNIT)), 'duration':duration,'width':stream['width'],'height':stream['height'],'frameRate':stream.get('avg_frame_rate'),'bytes':video.stat().st_size}
    records.append(record)
    sheet = UNIT / 'qa' / f'{video.stem}-sheet.jpg'
    if sheet.exists() and sheet.stat().st_mtime >= video.stat().st_mtime:
        continue
    canvas = Image.new('RGB',(1280,810),(25,25,25))
    draw = ImageDraw.Draw(canvas)
    for index, time in enumerate([0.2,1.4,2.8,4.2,5.8,max(0,duration-0.3)]):
        frame = UNIT / 'qa' / f'{video.stem}-{index}.jpg'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(min(time,duration-.1)),'-i',str(video),'-frames:v','1','-vf','scale=640:360',str(frame)],check=True)
        img = Image.open(frame)
        x = index%2*640
        y = index//2*270
        img.thumbnail((640,245))
        canvas.paste(img,(x,y))
        draw.text((x+8,y+246), f'{video.stem} | {time:.1f}s',fill=(255,255,255))
        frame.unlink()
    canvas.save(sheet,quality=88)
(UNIT / 'qa' / 'metadata.json').write_text(json.dumps(records,indent=2))
print(json.dumps(records,indent=2))
