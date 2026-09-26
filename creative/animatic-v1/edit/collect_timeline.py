"""Merge each production unit's shot map; run from the repository root."""
import csv
import json
from pathlib import Path
import subprocess

shots, jobs, durations = {}, {}, {}
for unit in ['opening', 'family', 'memories']:
    base = Path('creative/animatic-v1') / unit
    for job in json.loads((base / 'generation-log.json').read_text())['jobs']:
        filename = job.get('file', job.get('localFile'))
        if filename:
            if not filename.startswith('creative/'):
                filename = str(base / filename)
        else:
            kind = job.get('media', job.get('type', job.get('media_type', job.get('mediaType'))))
            filename = str(base / ('stills' if kind == 'image' else 'videos') / (job['code'] + ('.png' if kind == 'image' else '.mp4')))
        jobs[filename] = job
    for shot in json.loads((base / 'shot-map.json').read_text())['shots']:
        filename = shot.get('file', shot.get('relativefile'))
        if not filename.startswith('creative/'):
            filename = str(base / filename)
        assert Path(filename).exists(), filename
        shot['file'] = filename
        job = jobs.get(filename, {})
        asset_id = shot.get('asset_id', job.get('assetId'))
        if shot['shot_id'] == 'S07':
            asset_id = '4d8776ad-f103-4575-b5a3-2066d4ea19c6'
        assert asset_id, (shot['shot_id'], filename)
        shot['asset_id'] = asset_id
        shot['source_in_seconds'] = round(shot.get('source_in_seconds', 0) * 24) / 24
        if shot['media_type'] == 'video':
            if filename not in durations:
                durations[filename] = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', filename]))
            shot['available_duration'] = durations[filename]
        shots[shot['shot_id']] = shot

output = []
for row in csv.DictReader(open('creative/converse-shot-list-v2.csv')):
    shot = shots[row['shot_id']]
    for key in ['start_seconds', 'end_seconds', 'duration_seconds']:
        shot[key] = float(row[key])
    for key in ['title_en', 'title_fr']:
        shot[key] = row[key]
    assert shot['media_type'] == 'image' or shot['source_in_seconds'] + shot['duration_seconds'] <= shot['available_duration'] + 1/48, shot['shot_id']
    output.append(shot)
assert len(output) == 26 and sum(s['duration_seconds'] for s in output) == 76
for previous, following in zip(output, output[1:]):
    assert previous['end_seconds'] == following['start_seconds']
timeline = {'fps':24, 'width':1920, 'height':1080, 'duration_seconds':76, 'shots':output}
Path('creative/animatic-v1/edit/timeline.json').write_text(json.dumps(timeline, indent=2, ensure_ascii=False) + '\n')
print(json.dumps([{'file':s['file'], 'id':s['asset_id']} for s in output]))
