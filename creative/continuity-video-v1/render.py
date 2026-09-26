#!/usr/bin/env python3
"""Assemble reviewed native Seedance 30 s clips with exact editorial phone inserts."""
from pathlib import Path
import argparse
import json
import subprocess
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent


def call(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def render(suffix, ending_fix=None):
    source = ROOT / 'videos' / ('opening-' + suffix + '.mp4')
    if not source.exists():
        raise SystemExit(f'Missing actual generated source: {source}. No stand-in is allowed.')
    meta = probe(source)
    if float(meta['format']['duration']) < 29.9:
        raise SystemExit('Source is too short for the timed opening; inspect and revise the edit explicitly.')
    output = ROOT / 'renders' / ('converse-continuity-' + suffix + '-seedance25-30s.mp4')
    inputs = ['ffmpeg', '-y', '-v', 'warning', '-i', str(source), '-i', str(ROOT/'common'/('phone-'+suffix+'.mp4')),
              '-i', str(ROOT/'common/opening-audio.wav')]
    normalized = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24'
    ending_duration = 26 if ending_fix else 30
    filters = ('[0:v]'+normalized+',split=2[a][b];'
               '[a]trim=start=0:end=15,setpts=PTS-STARTPTS[before];'
               f'[b]trim=start=22:end={ending_duration},setpts=PTS-STARTPTS[after];'
               '[1:v]fps=24,setsar=1,trim=duration=7,setpts=PTS-STARTPTS[phone];')
    if ending_fix:
        if suffix != 'n':raise SystemExit('Only the explicitly reviewed Nano ending correction is authorized.')
        ending_fix = ROOT / ending_fix
        if not ending_fix.is_file() or float(probe(ending_fix)['format']['duration']) < 4:
            raise SystemExit('Missing or short native ending correction.')
        inputs += ['-i', str(ending_fix)]
        filters += '[3:v]'+normalized+',trim=duration=4,setpts=PTS-STARTPTS[ending];[before][phone][after][ending]concat=n=4:v=1:a=0[v]'
    else:
        filters += '[before][phone][after]concat=n=3:v=1:a=0[v]'
    call(inputs + ['-filter_complex', filters,
          '-map', '[v]', '-map', '2:a', '-t', '30', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
          '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(output)])
    call(['ffmpeg', '-v', 'error', '-i', str(output), '-f', 'null', '-'])
    shots = [2, 7, 11, 14, 18, 23, 25, 27.5, 29.5]
    sheet = Image.new('RGB', (1280, 786), '#25271e')
    draw = ImageDraw.Draw(sheet)
    for index, t in enumerate(shots):
        frame = ROOT/'qa'/f'{suffix}-{index:02}.jpg'
        call(['ffmpeg','-y','-v','error','-ss',str(t),'-i',str(output),'-frames:v','1','-vf','scale=426:240',str(frame)])
        x, y = (index%3)*426, (index//3)*262
        sheet.paste(Image.open(frame), (x,y));draw.text((x+10,y+242),f'{suffix.upper()} · {t:.1f}s',fill='white')
    sheet.save(ROOT/'qa'/f'{suffix}-contact-sheet.jpg',quality=92)
    call(['ffmpeg','-y','-v','error','-ss','7','-i',str(output),'-frames:v','1',str(ROOT/'renders'/f'{suffix}-poster.jpg')])
    result = {'source':str(source.relative_to(ROOT)),'output':str(output.relative_to(ROOT)),
              'metadata':probe(output),'qa':'Decode verified; contact sheet created. Visual review must still be recorded.',
              'nativeRangeReplaced':{'start':15,'end':22,'reason':'Exact readable editorial phone interface'},
              'audio':'Common score and two English voices reused from approved v3 comparison.',
              'endingCorrection':{'range':[26,30], 'source':str(ending_fix.relative_to(ROOT))} if ending_fix else None}
    (ROOT/'qa'/f'{suffix}-probe.json').write_text(json.dumps(result,indent=2))
    print(output)


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('variant', choices=['n','s','g','all']);parser.add_argument('--ending-fix');args=parser.parse_args()
    if args.variant=='all' and args.ending_fix:raise SystemExit('Render Nano separately with its explicit ending correction.')
    for suffix in ('nsg' if args.variant=='all' else args.variant):render(suffix,args.ending_fix)
