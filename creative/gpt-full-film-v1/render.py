#!/usr/bin/env python3
"""Finish CV01G without regenerating or re-encoding its first 720 picture frames.

Only actual generated clips are accepted. All picture sources use the GPT Image
2.5 continuity family. The end card is an editorial crop and original typesetting,
not another generative image. Run --prepare while the six clips are still pending.
"""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tempfile
import wave
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
CREATIVE = ROOT.parent
OPENING = CREATIVE / 'continuity-video-v1/renders/converse-continuity-g-seedance25-30s.mp4'
SHARED_AUDIO = CREATIVE / 'model-comparison-v3/shared/audio'
SCHEDULE = [('basketball', 30, 7), ('salsa', 37, 8), ('wedding', 45, 4),
            ('newborn', 49, 4), ('handover', 53, 8), ('return', 61, 11)]
OUTPUT = ROOT / 'renders/converse-gpt-seedance25-full-76s.mp4'
NORMALIZE = 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=24'
FONT_DIR = Path('/System/Library/Fonts/Supplemental')


def call(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)]))


def frame_hashes(path, seconds=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:v:0']
    if seconds is not None:
        cmd += ['-t', str(seconds)]
    cmd += ['-f', 'framemd5', '-']
    result = subprocess.check_output(cmd, text=True)
    return [line.rsplit(',', 1)[-1].strip() for line in result.splitlines() if line and not line.startswith('#')]


def sha256(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def prepare_endcard():
    source = CREATIVE / 'continuity-study/images/CS02G.png'
    ref = Image.open(source).convert('RGB')
    w, h = ref.size
    # Preserve the actual complete side profile from the middle/lower panel.
    shoe = ref.crop((round(.342*w), round(.405*h), round(.665*w), round(.775*h)))
    shoe.thumbnail((602, 400), Image.Resampling.LANCZOS)
    # Warm paper is sampled from an empty part of that same approved reference.
    paper = ref.crop((round(.005*w), round(.91*h), round(.325*w), round(.995*h)))
    image = paper.resize((1280, 720), Image.Resampling.LANCZOS)
    image.paste(shoe, (48 + (602-shoe.width)//2, 177 + (400-shoe.height)//2))
    d = ImageDraw.Draw(image)
    d.text((696, 230), 'CONVERSE', font=ImageFont.truetype(str(FONT_DIR/'Arial Narrow Bold.ttf'), 104), fill='#222520')
    d.text((702, 365), 'CONSERVE', font=ImageFont.truetype(str(FONT_DIR/'Arial Bold.ttf'), 40), fill='#222520')
    d.text((702, 418), 'WHAT MATTERS.', font=ImageFont.truetype(str(FONT_DIR/'Arial Bold.ttf'), 40), fill='#222520')
    output = ROOT / 'graphics/endcard.png'
    image.save(output)
    (ROOT/'graphics/provenance.json').write_text(json.dumps({
        'source': '../continuity-study/images/CS02G.png',
        'referenceCode': 'CS02G', 'sourceSha256': sha256(source),
        'treatment': 'Complete shoe profile crop on sampled paper; original typographic arrangement, no generated or altered shoe details.',
        'brandText': 'CONVERSE', 'tagline': 'CONSERVE WHAT MATTERS.',
        'fonts': ['Arial Narrow Bold', 'Arial Bold'],
        'note': 'Editorial typesetting, not a claim to use the official Converse wordmark font.'
    }, indent=2))


def prepare_audio():
    # Decode the original approved AAC opening. No new mix, normalisation, speed
    # change, or fades are applied to those first 30 seconds of PCM.
    call(['ffmpeg', '-y', '-v', 'warning', '-i', OPENING, '-map', '0:a:0', '-t', '30',
          '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', ROOT/'audio/opening-preserved.wav'])
    call(['ffmpeg', '-y', '-v', 'warning', '-i', SHARED_AUDIO/'score.wav',
          '-i', SHARED_AUDIO/'mom-return.wav', '-i', SHARED_AUDIO/'luna-ending.wav',
          '-filter_complex',
          "[0:a]atrim=start=30:end=76,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.25,afade=t=out:st=44.6:d=1.4,volume='if(lt(t,32),0.72,if(lt(t,41),0.19,0.6))':eval=frame[m];"
          '[1:a]atempo=0.72,highpass=f=130,lowpass=f=6600,aecho=0.8:0.8:45:0.1,volume=1.45,adelay=32900|32900[v1];'
          '[2:a]atempo=0.78,volume=1.35,adelay=37100|37100[v2];'
          '[m][v1][v2]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-18:TP=-1.5:LRA=11,aresample=48000[out]',
          '-map', '[out]', '-t', '46', '-ac', '2', '-c:a', 'pcm_s16le', ROOT/'audio/continuation.wav'])
    call(['ffmpeg', '-y', '-v', 'warning', '-i', ROOT/'audio/opening-preserved.wav',
          '-i', ROOT/'audio/continuation.wav', '-filter_complex',
          '[0:a][1:a]concat=n=2:v=0:a=1[out]', '-map', '[out]', '-t', '76',
          '-c:a', 'pcm_s16le', ROOT/'audio/full-mix.wav'])
    with wave.open(str(ROOT/'audio/opening-preserved.wav')) as opening, wave.open(str(ROOT/'audio/full-mix.wav')) as final:
        count = opening.getnframes()
        if count != 30*48000 or opening.readframes(count) != final.readframes(count):
            raise SystemExit('Opening PCM preservation failed before the final AAC encode.')


def prepare():
    for folder in ('graphics', 'audio', 'renders', 'qa', 'videos'):
        (ROOT/folder).mkdir(exist_ok=True)
    if not OPENING.is_file():
        raise SystemExit('The approved CV01G opening is missing; cannot fabricate a replacement.')
    prepare_endcard()
    prepare_audio()


def contact_sheet():
    times = [2, 11, 18, 25, 29.9, 31, 34, 36.7, 38, 42, 44.7, 46.5,
             48.7, 50.5, 52.7, 54, 57.5, 60.7, 62, 65, 68, 71.5, 73, 75.5]
    sheet = Image.new('RGB', (1600, 1040), '#222520')
    draw = ImageDraw.Draw(sheet)
    for i, t in enumerate(times):
        dest = ROOT/'qa'/f'frame-{i:02}.jpg'
        call(['ffmpeg','-y','-v','error','-ss',str(t),'-i',OUTPUT,'-frames:v','1','-vf','scale=320:180',dest])
        x, y = (i%5)*320, (i//5)*208
        sheet.paste(Image.open(dest), (x,y))
        draw.text((x+8,y+184), f'{t:.1f} s', fill='#f7f0df')
    sheet.save(ROOT/'qa/contact-sheet.jpg', quality=92)
    call(['ffmpeg','-y','-v','error','-ss','11','-i',OUTPUT,'-frames:v','1',ROOT/'renders/poster.jpg'])


def render():
    prepare()
    sources = []
    for name, start, duration in SCHEDULE:
        path = ROOT/'videos'/f'{name}.mp4'
        if not path.is_file():
            raise SystemExit(f'Missing actual generated video {path}; no still-image stand-ins are permitted.')
        meta = probe(path)
        stream = next((s for s in meta['streams'] if s['codec_type']=='video'), None)
        if not stream or float(stream.get('duration', meta['format']['duration'])) < duration-.05:
            raise SystemExit(f'{name} is shorter than the planned {duration} s; inspect it before revising the edit.')
        sources.append({'file':str(path.relative_to(ROOT)), 'sha256':sha256(path), 'start':start,
                        'duration':duration, 'sourceMetadata':meta})
    with tempfile.TemporaryDirectory(prefix='converse-gpt-assembly-') as temp:
        work = Path(temp)
        cmd = ['ffmpeg', '-y', '-v', 'warning']
        for source in sources:
            cmd += ['-i', ROOT/source['file']]
        cmd += ['-loop', '1', '-framerate', '24', '-i', ROOT/'graphics/endcard.png']
        filters = []
        for i, source in enumerate(sources):
            filters.append(f'[{i}:v]{NORMALIZE},trim=duration={source["duration"]},setpts=PTS-STARTPTS[v{i}]')
        filters.append(f'[6:v]{NORMALIZE},trim=duration=4,setpts=PTS-STARTPTS[v6]')
        filters.append(''.join(f'[v{i}]' for i in range(7))+'concat=n=7:v=1:a=0[tail]')
        call(cmd + ['-filter_complex', ';'.join(filters), '-map', '[tail]', '-an', '-t', '46',
                    '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-video_track_timescale','12288',
                    '-movflags','+faststart',work/'tail.mp4'])
        call(['ffmpeg','-y','-v','warning','-i',OPENING,'-map','0:v:0','-an','-c:v','copy',work/'opening.mp4'])
        concat = work/'concat.txt'
        concat.write_text(f"file '{work/'opening.mp4'}'\nfile '{work/'tail.mp4'}'\n")
        call(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',concat,'-map','0:v:0',
              '-an','-c:v','copy','-movflags','+faststart',work/'picture.mp4'])
        call(['ffmpeg','-y','-v','warning','-i',work/'picture.mp4','-i',ROOT/'audio/full-mix.wav',
              '-map','0:v:0','-map','1:a:0','-t','76','-c:v','copy','-c:a','aac','-b:a','192k',
              '-movflags','+faststart',OUTPUT])
    call(['ffmpeg','-v','error','-i',OUTPUT,'-f','null','-'])
    original_hashes, final_hashes = frame_hashes(OPENING), frame_hashes(OUTPUT,30)
    unchanged = len(original_hashes)==720 and original_hashes==final_hashes
    if not unchanged:
        raise SystemExit('Picture preservation failed: first 720 decoded frames differ from CV01G.')
    meta = probe(OUTPUT)
    video = next(s for s in meta['streams'] if s['codec_type']=='video')
    if int(video['nb_frames']) != 1824 or abs(float(video['duration'])-76)>.01:
        raise SystemExit('Unexpected frame count or duration; do not mark this render ready.')
    contact_sheet()
    volume = subprocess.run(['ffmpeg','-hide_banner','-i',str(OUTPUT),'-af','volumedetect','-vn','-sn','-dn','-f','null','-'],
                            check=True,capture_output=True,text=True).stderr
    volume_lines=[line for line in volume.splitlines() if 'mean_volume:' in line or 'max_volume:' in line]
    (ROOT/'qa/render-report.json').write_text(json.dumps({
        'output':str(OUTPUT.relative_to(ROOT)), 'sha256':sha256(OUTPUT), 'metadata':meta,
        'fullDecodePassed':True, 'openingPictureExactlyPreserved':unchanged,
        'openingDecodedFramesCompared':len(original_hashes),
        'openingSource':str(OPENING.relative_to(CREATIVE)), 'openingSha256':sha256(OPENING),
        'audio':{'opening':'Original approved AAC decoded to PCM without changes, then final programme encoded to AAC.',
                 'openingPCMBeforeFinalAACVerifiedIdentical':True,
                 'continuation':'Existing v3 score and English Mom/Luna voices, no new paid audio.',
                 'momReturnAt':62.9,'lunaEndingAt':67.1,'volumeChecks':volume_lines},
        'sources':sources,
        'endcard':{'start':72,'duration':4,'source':'graphics/endcard.png'},
        'visualQA':'Contact sheet generated; a human/agent visual review is still required.'
    },indent=2))
    print(OUTPUT)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--prepare',action='store_true',help='Prepare only the end card and audio while generations are pending.')
    args=parser.parse_args()
    prepare() if args.prepare else render()
