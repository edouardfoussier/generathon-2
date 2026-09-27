#!/usr/bin/env python3
"""Package existing realistic inserts for CapCut. No generation or transcoding.

Reads manifest.json without modifying it. Only assets inside this folder can be
included; source films, credentials, caches and provider URLs are never copied.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit
import zipfile

HERE = Path(__file__).resolve().parent
MEDIA_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.mp4', '.webm'}
INCOMPLETE = {'rejected', 'failed', 'pending', 'queued', 'running', 'generating', 'submission_unknown'}


def local_asset(value, root):
    if not isinstance(value, str) or not value.strip() or '\\' in value:
        raise ValueError('file must name an existing local asset')
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('remote URLs and URL parameters are not package assets')
    value = unquote(parsed.path)
    prefix = '/creative/realistic-refinement-v1/'
    if value.startswith(prefix):
        value = value[len(prefix):]
    elif value.startswith('creative/realistic-refinement-v1/'):
        value = value[len('creative/realistic-refinement-v1/'):]
    if value.startswith('/') or any(part.startswith('.') for part in Path(value).parts):
        raise ValueError('hidden, absolute and parent paths cannot be packaged')
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or path.suffix.lower() not in MEDIA_EXTENSIONS:
        raise ValueError('only new image/video files inside this folder can be packaged')
    if not path.is_file() or path.stat().st_size == 0:
        raise FileNotFoundError('asset is not yet available')
    return path


def label(value, default=''):
    if isinstance(value, dict):
        value = value.get('fr') or value.get('en')
    return value if isinstance(value, str) else default


def slug(value):
    plain = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', plain).strip('-')[:65] or 'asset'


def atomic_json(path, data):
    temporary = path.with_suffix('.pending.json')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(path)


def build(root=HERE):
    root = root.resolve()
    manifest = json.loads((root / 'manifest.json').read_text())
    assets = manifest.get('assets')
    if not isinstance(assets, list):
        raise ValueError('manifest.json needs an assets list')
    audit_path = root / 'audit.md'
    audit = audit_path.read_text() if audit_path.is_file() else 'Audit non encore disponible.'
    selected, missing, skipped = [], [], []
    used_ids = set()
    for index, asset in enumerate(assets, 1):
        if not isinstance(asset, dict):
            skipped.append({'id': str(index), 'reason': 'Invalid manifest entry'})
            continue
        ident = str(asset.get('id', index))
        if ident in used_ids:
            raise ValueError('Asset IDs must be unique: ' + ident)
        used_ids.add(ident)
        if asset.get('usable') is False or asset.get('status') in INCOMPLETE:
            skipped.append({'id': ident, 'reason': 'Not marked as a usable completed asset'})
            continue
        if asset.get('kind') not in {'image', 'video'}:
            skipped.append({'id': ident, 'reason': 'Not an image or video'})
            continue
        try:
            path = local_asset(asset.get('file'), root)
        except FileNotFoundError:
            missing.append({'id': ident, 'reason': 'File not yet available'})
            continue
        except ValueError as error:
            skipped.append({'id': ident, 'reason': str(error)})
            continue
        title = label(asset.get('title'), ident)
        filename = f'{index:02}_{slug(ident)}_{slug(title)}{path.suffix.lower()}'
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        public = {'id': ident, 'title': title, 'kind': asset['kind'], 'filename': filename,
                  'sourceFile': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                  'sha256': digest, 'placement': label(asset.get('placement')),
                  'note': label(asset.get('note')), 'recommendation': label(asset.get('recommendation'))}
        # Store only useful human-authored text, never blindly dump provider jobs.
        for field in ('prompt', 'imagePrompt', 'videoPrompt', 'model'):
            if isinstance(asset.get(field), str):
                public[field] = asset[field]
        selected.append((path, public))
    metadata = {'version': 1, 'generatedAt': dt.datetime.now(dt.timezone.utc).isoformat(),
                'ready': bool(selected), 'assetCount': len(selected),
                'assets': [record for _, record in selected], 'missing': missing,
                'skipped': skipped, 'auditText': audit}
    if not selected:
        atomic_json(root / 'package.json', metadata)
        return metadata
    downloads = root / 'downloads'
    downloads.mkdir(exist_ok=True)
    archive = downloads / 'luna-rafa-realistic-inserts.zip'
    temporary = downloads / '.luna-rafa-realistic-inserts.pending.zip'
    lines = ['# Luna & Rafa — Inserts réalistes pour CapCut', '',
             'Ce dossier contient uniquement les nouveaux médias disponibles. Le montage CapCut et les prises originales restent inchangés.', '',
             '## Importer', '',
             '1. Décompresser cette archive, puis importer les fichiers du dossier assets dans CapCut.',
             '2. Les numéros suivent le manifeste : ils servent au repérage, pas à imposer une durée ou un ordre de montage.',
             '3. Lire le placement conseillé ci-dessous, choisir les portions utiles et conserver une copie du montage existant.',
             '4. Les clips générés contiennent des pistes audio qui n’ont pas été écoutées et validées créativement. Les couper dans CapCut avant le travail intentionnel sur la bande-son.', '',
             '## Avant de rallonger le film', '',
             'L’export audité dure 91,63 s à l’image, dont environ 33,43 s de noir après 58,20 s. Retirer cette queue noire ; elle ne représente pas des scènes manquantes.',
             'Cible indicative après inserts : 65–75 s, à ajuster selon le rythme sans chercher à remplir le noir. Les nouveaux fichiers sont des candidats à visionner, pas un nouveau montage final.', '',
             '## Fichiers', '']
    for _, item in selected:
        lines += [f"### {item['filename']}", '', item['title']]
        for field, heading in [('placement', 'Placement'), ('recommendation', 'Conseil'), ('note', 'Note')]:
            if item[field]:
                lines += [f'{heading} : {item[field]}']
        lines.append('')
    lines += ['## Provenance', '', 'Aucun fichier média n’a été transcodé : les empreintes SHA-256 sont dans assets.json.',
              'prompts.json reprend les textes de production disponibles. reference-pack.json conserve les prompts exacts des anciennes prises choisies, ainsi que les recettes de raccord proposées.',
              'Pub non officielle — exercice de hackathon. Converse n’est pas partenaire. Aucun des personnages fictifs ne représente une célébrité.', '']
    prompts = [{k: v for k, v in record.items() if k in {'id', 'title', 'prompt', 'imagePrompt', 'videoPrompt', 'model', 'recommendation'}}
               for _, record in selected]
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as output:
            for path, item in selected:
                output.write(path, 'assets/' + item['filename'])
            output.writestr('README.md', '\n'.join(lines))
            output.writestr('audit.md', audit)
            output.writestr('assets.json', json.dumps(metadata['assets'], ensure_ascii=False, indent=2) + '\n')
            output.writestr('prompts.json', json.dumps(prompts, ensure_ascii=False, indent=2) + '\n')
            for name in ('reference-pack.json', 'transition-plan.json', 'qa-review.md'):
                path = root / name
                if path.is_file():
                    output.write(path, name)
        with zipfile.ZipFile(temporary) as check:
            bad = check.testzip()
            if bad:
                raise ValueError('ZIP checksum verification failed: ' + bad)
        temporary.replace(archive)
    finally:
        temporary.unlink(missing_ok=True)
    metadata.update(zipFile=archive.relative_to(root).as_posix(), zipBytes=archive.stat().st_size)
    atomic_json(root / 'package.json', metadata)
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=HERE, help='Override for a local fixture or copied project.')
    args = parser.parse_args()
    try:
        result = build(args.root)
    except (OSError, ValueError, TypeError) as error:
        parser.exit(2, 'Package not created: ' + str(error) + '\n')
    print(json.dumps({key: result.get(key) for key in ('ready', 'assetCount', 'zipFile', 'zipBytes', 'missing', 'skipped')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
