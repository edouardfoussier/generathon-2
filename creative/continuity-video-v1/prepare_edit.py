#!/usr/bin/env python3
"""Prepare exact phone graphics and common opening audio; never fabricates video jobs."""
from pathlib import Path
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
STUDY = ROOT.parent / 'continuity-study'
COMMON = ROOT / 'common'
COMMON.mkdir(exist_ok=True)
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
LOOKUP = {x['code']: x for x in json.loads((STUDY / 'manifest.json').read_text())['assets']}


def text(draw, xy, words, size=26, bold=False, color='#292d26', spacing=8):
    draw.multiline_text(xy, words, font=ImageFont.truetype(BOLD if bold else FONT, size), fill=color, spacing=spacing)


def phone(suffix, answer):
    # Editorial UI composition, not a newly generated picture. The attached
    # portrait is cropped from the corresponding model's Rafa continuity sheet.
    image = Image.new('RGB', (1280, 720), '#292820')
    d = ImageDraw.Draw(image)
    d.rounded_rectangle((383, 9, 897, 711), radius=36, fill='#141712')
    d.rounded_rectangle((395, 22, 885, 698), radius=29, fill='#f2eee3')
    d.rounded_rectangle((571, 33, 709, 47), radius=7, fill='#141712')
    text(d, (431, 72), 'Conversation', 26, True)
    d.line((429, 116, 850, 116), fill='#d2ccbe', width=1)
    d.rounded_rectangle((425, 139, 856, 397), radius=16, fill='#e4dece')
    asset = LOOKUP['CC02' + suffix]
    ref = Image.open(STUDY / asset['localFile']).convert('RGB')
    # Third panel is the close portrait in all three reference sheets. Retain
    # exactly that generated identity, without a new face synthesis.
    w, h = ref.size
    portrait = ref.crop((round(w * .677), 0, w, h))
    portrait.thumbnail((137, 175), Image.Resampling.LANCZOS)
    image.paste(portrait, (447 + (137-portrait.width)//2, 157))
    d = ImageDraw.Draw(image)
    text(d, (612, 202), 'Rafa', 26, True)
    text(d, (612, 240), '1970', 21, color='#6f735f')
    text(d, (447, 324), 'What was my\ngrandfather like?', 26, True, spacing=5)
    if answer:
        text(d, (445, 447), 'AI', 19, True, '#717765')
        text(d, (445, 486), "I don't have enough\ninformation about him.", 26, spacing=8)
    else:
        text(d, (445, 481), 'Thinking…', 25, color='#7f826f')
    d.rounded_rectangle((426, 629, 855, 672), radius=14, outline='#d8d2c4', width=1)
    text(d, (446, 640), 'Message', 19, color='#8a8b7d')
    d.rounded_rectangle((572, 684, 707, 688), radius=2, fill='#63685a')
    output = COMMON / ('phone-' + suffix.lower() + ('-answer' if answer else '-loading') + '.png')
    image.save(output)
    return output


def run(args):
    subprocess.run(args, check=True)


def main():
    for suffix in 'NSG':
        loading, answer = phone(suffix, False), phone(suffix, True)
        output = COMMON / ('phone-' + suffix.lower() + '.mp4')
        run(['ffmpeg', '-y', '-v', 'warning', '-loop', '1', '-framerate', '24', '-t', '1.6', '-i', str(loading),
             '-loop', '1', '-framerate', '24', '-t', '5.4', '-i', str(answer), '-filter_complex',
             '[0:v]setsar=1[a];[1:v]setsar=1[b];[a][b]concat=n=2:v=1:a=0[v]',
             '-map', '[v]', '-t', '7', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)])
    source = ROOT.parent / 'model-comparison-v3/shared/audio'
    run(['ffmpeg', '-y', '-v', 'warning', '-i', str(source/'score.wav'), '-i', str(source/'mom-opening.wav'),
         '-i', str(source/'luna-annoyed.wav'), '-filter_complex',
         "[0:a]atrim=0:30,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=2,afade=t=out:st=29.5:d=0.5,volume='if(lt(t,10),0.19,if(lt(t,22),0.35,0.6))':eval=frame[m];"
         '[1:a]atempo=0.70,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.45,adelay=250|250[v1];'
         '[2:a]atempo=0.72,volume=1.35,adelay=6120|6120[v2];'
         '[m][v1][v2]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=11,aresample=48000[out]',
         '-map', '[out]', '-t', '30', '-c:a', 'pcm_s16le', str(COMMON/'opening-audio.wav')])
    print('Prepared three 7-second phone inserts and one common 30-second audio mix. Native opening videos are still pending.')


if __name__ == '__main__':
    main()
