#!/usr/bin/env python3
"""Publish finished continuity candidates on the board without altering earlier cards.

Run from any directory. Defaults to ../continuity-study/manifest.json.
Only completed image records with an existing local file become public cards.
Generation metadata remains in the source manifest; no remote URLs are copied.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

BOARD = Path(__file__).resolve().parent
STUDY = BOARD.parent / 'continuity-study'
READY = {'generated', 'completed', 'complete', 'succeeded', 'success', 'ready'}
GROUPS = {'characters', 'locations', 'shoes'}


def localized(value, language, *, english_label=False):
    if isinstance(value, dict):
        chosen = value.get(language) or value.get('en') or value.get('fr') or ''
        return localized(chosen, language)
    if isinstance(value, list):
        return ' '.join(filter(None, (localized(item, language, english_label=english_label) for item in value)))
    if not isinstance(value, str):
        return ''
    value = value.strip()
    return ('EN · ' + value) if english_label and language == 'fr' and value else value


def read_assets():
    source = (BOARD / 'assets.js').read_text()
    prefix = 'window.CONVERSE_ASSETS = '
    if not source.startswith(prefix):
        raise ValueError('Unexpected assets.js format; refusing to overwrite.')
    return json.loads(source[len(prefix):].strip().removesuffix(';'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', nargs='?', type=Path, default=STUDY / 'manifest.json')
    args = parser.parse_args()
    study = json.loads(args.manifest.read_text())
    models = {item['id']: item['label'] for item in study.get('models', [])}
    model_order = {item['id']: index for index, item in enumerate(study.get('models', []))}
    records = study.get('assets', [])
    existing = read_assets()
    previous = [asset for asset in existing if asset.get('category') != 'continuity']
    used_codes = {asset['code'] for asset in previous}
    subject_order = {}
    cards = []
    skipped = []
    for record in records:
        code = record.get('code', '')
        if record.get('status', '').lower() not in READY or record.get('kind', 'image') != 'image':
            skipped.append(code)
            continue
        local = record.get('localFile')
        image = (STUDY / local).resolve() if isinstance(local, str) and local else None
        if image is None or not image.is_relative_to(STUDY.resolve()) or not image.is_file():
            skipped.append(code)
            continue
        if image.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
            raise ValueError(f'Unsupported image file for {code}: {image.name}')
        if not code or code in used_codes:
            raise ValueError(f'Missing or duplicate asset code: {code!r}')
        if record.get('group') not in GROUPS or not record.get('subjectId'):
            raise ValueError(f'Missing group or subjectId for {code}')
        used_codes.add(code)
        subject_order.setdefault(record['subjectId'], len(subject_order))
        label = record.get('modelLabel') or models.get(record.get('model')) or record.get('model', '')
        title = record.get('title') or record['subjectId']
        subject_title = record.get('subjectTitle') or title
        card = {
            'code': code, 'category': 'continuity', 'group': record['group'],
            'subjectId': record['subjectId'],
            'subjectTitle': localized(subject_title, 'fr'), 'subjectTitleEn': localized(subject_title, 'en'),
            'title': localized(title, 'fr'), 'titleEn': localized(title, 'en'),
            'subtitle': localized(record.get('subtitle'), 'fr') or f'{label} · Proposition à choisir',
            'subtitleEn': localized(record.get('subtitle'), 'en') or f'{label} · Candidate for selection',
            'model': label, 'modelId': record.get('model', ''),
            'filename': '../continuity-study/' + image.relative_to(STUDY.resolve()).as_posix(),
            'status': 'generated', 'aspectRatio': record.get('aspectRatio', '16:9'),
            'teamApproved': False,
        }
        for lang, key in [('fr', 'note'), ('en', 'noteEn')]:
            parts = [localized(record.get('qa'), lang, english_label=True),
                     localized(record.get('referenceNotes'), lang, english_label=True)]
            card[key] = ' '.join(filter(None, parts))
        if record.get('assetId'):
            card['assetId'] = record['assetId']
        cards.append(card)
    cards.sort(key=lambda card: (
        ['characters', 'locations', 'shoes'].index(card['group']),
        subject_order[card['subjectId']], model_order.get(card['modelId'], 99)))
    manifest = json.loads((BOARD / 'manifest.json').read_text())
    manifest['jobs'] = [job for job in manifest['jobs'] if job.get('category') != 'continuity'] + cards
    manifest['continuityExploration'] = {
        'sourceManifest': '../continuity-study/manifest.json',
        'style': study.get('style'),
        'models': study.get('models', []),
        'intendedCounts': study.get('intendedCounts', {}),
        'publishedImageCount': len(cards),
        'pendingOrUnavailableCodes': skipped,
        'teamApproved': False,
        'creditNote': 'See source manifest for the complete generation ledger and credit totals.',
    }
    if cards:
        manifest['phase'] = 'Exploration 11 — Continuity reference comparison'
    serialized = json.dumps(previous + cards, ensure_ascii=False, indent=2) + ';\n'
    (BOARD / 'assets.js').write_text('window.CONVERSE_ASSETS = ' + serialized)
    (BOARD / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    after = read_assets()
    assert [asset for asset in after if asset.get('category') != 'continuity'] == previous
    print(f'Published {len(cards)} continuity images; preserved {len(previous)} earlier cards; skipped {len(skipped)} pending/unavailable records.')


if __name__ == '__main__':
    main()
