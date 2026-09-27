#!/usr/bin/env python3
"""Package the user's screenshot selection without trimming or re-encoding."""
import csv
import hashlib
import html
import io
import json
from pathlib import Path
import zipfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def digest(stream):
    value = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
        value.update(chunk)
    return value.hexdigest()


def main():
    selection = json.loads((HERE / 'selection.json').read_text())
    clips = selection['clips']
    assert [c['order'] for c in clips] == list(range(1, len(clips) + 1))
    assert len({c['filename'] for c in clips}) == len(clips)
    for clip in clips:
        source = (REPO / clip['source']).resolve()
        assert source.is_relative_to(REPO / 'creative') and source.is_file()
        assert source.suffix == '.mp4' and Path(clip['filename']).name == clip['filename']
        with source.open('rb') as stream:
            clip['sha256'] = digest(stream)
    total_seconds = sum(c['durationSeconds'] for c in clips)
    csv_text = io.StringIO(newline='')
    writer = csv.writer(csv_text)
    writer.writerow(['Order', 'Filename', 'Scene', 'Model', 'Seconds', 'Original source', 'SHA256'])
    for c in clips:
        writer.writerow([c['order'], 'clips/' + c['filename'], c['title'], c['model'],
                         f"{c['durationSeconds']:.6f}", c['source'], c['sha256']])
    instructions = f'''LUNA & RAFA — SELECTION CAPCUT / CAPCUT SELECTION
{len(clips)} clips · {total_seconds:.3f} seconds of original footage

FRANCAIS
1. Dezipper cette archive.
2. Importer les 20 fichiers MP4 du dossier clips dans CapCut.
3. Trier par nom (ordre croissant 01 a 20), puis placer dans cet ordre sur la piste.
4. Ajuster les coupes, la musique et le son dans CapCut.

L'ordre reproduit exactement les captures fournies, sans reorganisation narrative.
La capture contenant S13 et S15 fournit deux fichiers consecutifs (11 et 12).
Les deux B07B, Seedance et Veo, restent deux prises distinctes (05 et 07).
Le dernier fichier est V25, pas V25R1.
Ce sont les prises ENTIERES, sans decoupe, recompression ni modification du son.
Le total de rushes depasse 80 secondes ; le montage final reste a raccourcir.
L'audio natif est conserve quand il existe ; les prises Seedance sont muettes.
L'archive ne contient pas de musique ajoutee et n'est pas un projet CapCut.

ENGLISH
Unzip, import the MP4 files from clips, sort filenames ascending (01 to 20),
then place them on the timeline in that order and trim to your final edit.
The order follows the supplied screenshots, including S13 then S15 in one image.
Both B07B alternatives are included; the final clip is V25, not V25R1.
These are complete original takes, unchanged and without re-encoding.
Native audio is retained where present; the Seedance takes are silent.
The combined rushes exceed the final 80-second limit and still need editing.
No added soundtrack or native CapCut project is included.

ORDRE / ORDER
''' + '\n'.join(f"{c['order']:02d}. {c['filename']} — {c['title']} — {c['durationSeconds']:.3f} s" for c in clips) + '\n'
    archive = HERE / selection['archive']
    assert archive.parent == HERE and archive.suffix == '.zip'
    temporary = archive.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as bundle:
        # Insertion order and zero-padded filenames both preserve the requested order.
        for c in clips:
            bundle.write(REPO / c['source'], 'clips/' + c['filename'])
        bundle.writestr('README.txt', instructions)
        bundle.writestr('ORDER.csv', csv_text.getvalue().encode('utf-8-sig'))
        bundle.writestr('selection.json', json.dumps(selection, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(temporary) as bundle:
        assert bundle.testzip() is None
        assert [n for n in bundle.namelist() if n.endswith('.mp4')] == ['clips/' + c['filename'] for c in clips]
        for c in clips:
            with bundle.open('clips/' + c['filename']) as stream:
                assert digest(stream) == c['sha256'], f"Archive mismatch: {c['filename']}"
    temporary.replace(archive)
    (HERE / 'selection.json').write_text(json.dumps(selection, ensure_ascii=False, indent=2) + '\n')
    (HERE / 'README.txt').write_text(instructions)
    (HERE / 'ORDER.csv').write_text(csv_text.getvalue(), encoding='utf-8-sig')
    mb = archive.stat().st_size / 1_000_000
    rows = ''.join(f'<li><span class="number">{c["order"]:02d}</span><div><strong>{html.escape(c["title"])}</strong><small>{html.escape(c["filename"])}</small></div><span class="length">{c["durationSeconds"]:.1f} s</span><a href="/{html.escape(c["source"])}" target="_blank" rel="noopener">Voir ↗</a></li>' for c in clips)
    page = '''<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Luna & Rafa — Sélection CapCut</title>
<style>
:root{color-scheme:dark;font:16px/1.5 system-ui,sans-serif;background:#11150f;color:#edf0e5}*{box-sizing:border-box}body{margin:0}main{max-width:900px;margin:auto;padding:44px 24px 72px}a{color:#d9e9a7;text-underline-offset:4px}.eyebrow{font-size:11px;letter-spacing:.23em;text-transform:uppercase;color:#b3c18f}h1{font:clamp(32px,6vw,58px)/1.06 Georgia,serif;margin:22px 0}header p{max-width:660px;color:#bdc5b5}.download{display:inline-block;padding:17px 24px;background:#dceaaf;color:#16200d;border-radius:8px;text-decoration:none;font-weight:700;margin:16px 0}.meta{font-size:13px;color:#bac6a6}.note{padding:18px 22px;background:#222b1b;border:1px solid #445136;border-radius:10px;margin:28px 0}.note p{margin:0}.note p+p{margin-top:10px;color:#bdc5b5}.instructions{color:#ccd1c3;font-size:14px}ol{padding:0;list-style:none;border-top:1px solid #3a4431;margin-top:32px}li{display:flex;gap:18px;align-items:center;padding:16px 0;border-bottom:1px solid #303a28}li div{flex:1;min-width:0}small{display:block;color:#9ca78f;overflow-wrap:anywhere}.number{font:22px Georgia,serif;color:#a7bc7b;min-width:26px}.length{font-size:13px;white-space:nowrap;color:#bcc7ac}li a{font-size:13px;white-space:nowrap}.foot{font-size:12px;color:#a0ac94;margin-top:28px}@media(max-width:520px){main{padding:24px 18px}li{gap:10px}li strong{font-size:14px}.length{display:none}}
</style><main><a href="/studio">← Retour à l’atelier</a><header><p class="eyebrow">Luna & Rafa / CapCut handoff</p><h1>Votre sélection.<br>Prête pour le montage.</h1><p>20 prises originales, numérotées dans l’ordre de vos captures. La boîte, les souvenirs de Rafa, la transmission, puis le retour à Luna.</p>'''
    page += f'<a class="download" href="{html.escape(archive.name)}" download="{html.escape(archive.name)}">↓ Télécharger les 20 clips · {mb:.1f} Mo</a><div class="meta">ZIP · MP4 originaux · sans recompression · {total_seconds:.1f} secondes de rushes</div></header>'
    page += '<div class="note"><p><strong>Dézippez → importez le dossier clips → triez par nom, de 01 à 20.</strong></p><p>Gardez ensuite les passages voulus dans CapCut. Les prises complètes donnent environ 1 min 55 de rushes ; le film final reste à ramener à 1 min 20 maximum.</p></div><p class="instructions">S13 et S15 sont inclus séparément, en positions 11 et 12. Les deux B07B restent présents. Le ZIP contient aussi un récapitulatif FR/EN et la liste des sources.</p><ol>'
    page += rows + '</ol><p class="foot">Originals preserved. Unzip, import the clips and sort by filename ascending (01–20). Full takes with native audio where present; no added soundtrack. <a href="ORDER.csv" download>Liste CSV ↓</a></p></main></html>'
    (HERE / 'index.html').write_text(page)
    print(json.dumps({'archive': str(archive), 'clips': len(clips), 'bytes': archive.stat().st_size,
                      'seconds': total_seconds, 'verified': 'ZIP CRC and all 20 SHA-256 hashes match originals'}))


if __name__ == '__main__':
    main()
