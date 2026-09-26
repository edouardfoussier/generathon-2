#!/usr/bin/env python3
"""Merge reviewed batch records and verify local media before board publication."""
import json
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parent
PARTS = ['luna-results.json', 'character-results.json', 'places-shoes-results.json']


def main():
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    assets = []
    missing = []
    for name in PARTS:
        path = ROOT / name
        if not path.exists():
            missing.append(name)
            continue
        data = json.loads(path.read_text())
        assets.extend(data if isinstance(data, list) else data.get('assets', data.get('items', [])))
    codes = set()
    subjects = defaultdict(list)
    for record in assets:
        assert record['code'] not in codes, record['code']
        codes.add(record['code'])
        path = (ROOT / record['localFile']).resolve()
        assert path.is_relative_to(ROOT), path
        with Image.open(path) as im:
            im.load()
            record['width'], record['height'] = im.size
            record['fileFormat'] = im.format
            if im.format == 'JPEG' and path.suffix.lower() != '.jpg':
                target = path.with_suffix('.jpg')
                path.rename(target)
                record['localFile'] = target.relative_to(ROOT).as_posix()
        assert record['status'] in {'generated', 'completed', 'ready'}, record['code']
        assert isinstance(record.get('qa'), dict) and record['qa'].get('fr') and record['qa'].get('en'), f"Missing bilingual review: {record['code']}"
        record['teamApproved'] = False
        subjects[record['subjectId']].append(record)
    order = {m['id']: index for index, m in enumerate(manifest['models'])}
    assets.sort(key=lambda r: (['characters', 'locations', 'shoes'].index(r['group']), r['code'][:4], order[r['model']]))
    qa = ROOT / 'qa'
    qa.mkdir(exist_ok=True)
    for subject, records in subjects.items():
        records.sort(key=lambda r: order[r['model']])
        assert len({r['model'] for r in records}) == len(records), subject
        sheet = Image.new('RGB', (1800, 420), '#eee9df')
        draw = ImageDraw.Draw(sheet)
        for index, record in enumerate(records):
            with Image.open(ROOT / record['localFile']) as im:
                thumb = ImageOps.contain(im.convert('RGB'), (590, 355))
                sheet.paste(thumb, (index * 600 + (600-thumb.width)//2, 50+(355-thumb.height)//2))
            draw.text((index*600+12, 12), record['code'] + ' | ' + record.get('modelLabel', record['model']), fill='#161914')
        filename = f"qa/{records[0]['code'][:4]}-comparison.jpg"
        sheet.save(ROOT / filename, quality=91)
        for record in records:
            record['comparisonSheet'] = filename
    manifest['assets'] = assets
    manifest['publishedCounts'] = dict(Counter(r['group'] for r in assets))
    manifest['publishedCounts']['total'] = len(assets)
    manifest['missingBatchFiles'] = missing
    manifest['complete'] = not missing and len(assets) == manifest['intendedCounts']['total'] and all(len(rs)==3 for rs in subjects.values())
    manifest['creditsFromRetainedRecords'] = sum(r.get('totalCreditsCharged', r.get('creditsCharged', 0)) or 0 for r in assets)
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'images':len(assets), 'subjects':len(subjects), 'complete':manifest['complete'], 'missing':missing}))


if __name__ == '__main__':
    main()
