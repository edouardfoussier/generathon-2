#!/usr/bin/env python3
"""Fit the two actual generated cues; keep untouched originals for review.

No new music is synthesized locally. A removes a middle phrase and retains its
natural final cadence. B trims only the provider's 42 ms excess. The requested
tempo and section timings are creative directions, not generation guarantees.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parent


def run(args):
    return subprocess.run([str(x) for x in args], check=True, capture_output=True, text=True)


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]).stdout)


def loudness(path):
    log = run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'loudnorm=I=-20:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-']).stderr
    return json.loads(log[log.rfind('{'):log.rfind('}')+1])


def main():
    items = [
        ('MU01', 'organic-latin-breakbeat',
         '[0:a]asplit=2[x][y];[x]atrim=0:46,asetpts=PTS-STARTPTS[a];'
         '[y]atrim=start=64,asetpts=PTS-STARTPTS[b];'
         '[a][b]acrossfade=d=0.040816:c1=tri:c2=tri,atrim=0:76,aresample=48000[out]',
         {'sourceRangesSeconds': [[0, 46], [64, 94.040816]], 'crossfadeSeconds': 0.040816,
          'note': 'Original pitch/tempo retained; an 18-second middle portion is removed; original final cadence retained. Edit is provisional pending musical audition.'}),
        ('MU02', 'tactile-percussion-piano',
         '[0:a]atrim=0:76,asetpts=PTS-STARTPTS,aresample=48000[out]',
         {'sourceRangesSeconds': [[0, 76]], 'crossfadeSeconds': 0,
          'note': 'Only 42 ms of trailing provider excess removed. Original pitch/tempo and entire arrangement retained.'})
    ]
    reports = []
    for code, name, graph, edit in items:
        source, target = ROOT/f'{name}-original.wav', ROOT/f'{name}-76s.wav'
        run(['ffmpeg', '-y', '-v', 'warning', '-i', source, '-filter_complex', graph,
             '-map', '[out]', '-t', 76, '-ac', 2, '-c:a', 'pcm_s16le', target])
        # Compact listening copy accompanies the exact PCM edit master.
        run(['ffmpeg', '-y', '-v', 'warning', '-i', target, '-c:a', 'libmp3lame', '-b:a', '192k', ROOT/f'{name}-76s.mp3'])
        run(['ffmpeg', '-v', 'error', '-i', target, '-f', 'null', '-'])
        meta = probe(target)
        actual = float(meta['format']['duration'])
        if abs(actual - 76) > .00001:
            raise RuntimeError(f'{code}: expected exact 76 s, got {actual}')
        reports.append({'code': code, 'sourceFile': source.name, 'outputFile': target.name,
                        'sourceSeconds': float(probe(source)['format']['duration']), 'outputSeconds': actual,
                        'outputSha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                        'metadata': meta, 'editing': edit, 'loudnessMeasured': loudness(target),
                        'fullDecodePassed': True})
    (ROOT/'technical-qa.json').write_text(json.dumps({'tracks': reports,
        'method': 'ffprobe metadata, complete ffmpeg decoding and EBU R128 loudness measurement; no claim of human audition.'}, indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k in ('code', 'outputFile', 'sourceSeconds', 'outputSeconds', 'loudnessMeasured')} for r in reports], indent=2))


if __name__ == '__main__':
    main()
