#!/usr/bin/env python3
"""Merge completed production records into the review page's editorial order."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
plan = json.loads((ROOT / 'transition-plan.json').read_text())
luna = json.loads((ROOT / 'luna/manifest.json').read_text())
assets = []

placements = {
    'RL01': ('Après la boîte et avant les lacets · vers 00:10 dans votre export.',
             'Garder environ 2 s pour établir le regard de Luna avant le souvenir.'),
    'RL02': ('Après le retour au présent · vers 00:50, avant le départ.',
             'Le trait est plus large que prévu et colore une partie de la réparation. Option de personnalisation à choisir avec l’équipe.'),
    'RL03': ('Après le geste personnel et le départ du grenier, avant la signature.',
             'Une seule poussée puis une glisse. Le détail orange est très peu visible à cette échelle ; éviter de raccorder ensuite sur une réparation vierge en gros plan.'),
    'RT01-P': ('Entre les lacets de Luna et le terrain de Rafa · autour de 00:14.',
               'Source présent pour construire le raccord ; utiliser le montage RT01-CUT pour un premier essai.'),
    'RT01-M': ('À la suite du pied de Luna, avant de révéler Rafa.',
               'Privilégier 0–1,5 s : la fin comporte un pivot et un déplacement, pas un appui vertical.'),
    'RT01-C': ('Alternative au raccord coupé · ne pas cumuler les deux versions.',
               'La bascule se cache sous une lumière très forte vers 2,7–3,7 s. Variante plus lente ; comparer au raccord franc.'),
    'RT01-CUT': ('Remplace le passage lacets → pieds de Rafa, autour de 00:14.',
                 'Premier choix proposé : coupe courte entre deux cadrages alignés. Aucun fondu de silhouettes.'),
    'RT01-FLASH': ('Alternative au raccord franc, au même endroit.',
                  'Même coupe, masquée par un éclat de six images. Plus marqué, sans transformation anatomique.'),
}

def decorate(record, ident, kind, file, title, poster=None):
    item = dict(record)
    item.update(id=ident, kind=kind, file=file, title=title)
    item.setdefault('model', 'Kling 3 Pro' if kind == 'video' else 'Nano Banana 2')
    if poster:
        item['poster'] = poster
    placement, recommendation = placements.get(ident.replace('-still', ''), ('Image de référence pour le plan associé.', ''))
    item.update(placement=placement, recommendation=recommendation)
    item['usable'] = item.get('status') == 'generated' and (ROOT / file).is_file()
    if kind == 'video':
        item['note'] = ('Raccord local de 1,54 s, sans piste audio. Sources complètes également fournies.'
                        if ident in {'RT01-CUT', 'RT01-FLASH'} else
                        'Prise candidate à choisir en équipe. Son généré à couper au prémontage ; le travail sonore viendra ensuite.')
    return item

for code in ['RL01', 'RT01-CUT', 'RT01-FLASH', 'RT01-P', 'RT01-M', 'RT01-C', 'RL02', 'RL03']:
    if code.startswith('RL'):
        found = next((a for a in luna['assets'] if a['code'] in {code, code + 'V'} and a['kind'] == 'video'), None)
        if found:
            assets.append(decorate(found, code, 'video', 'luna/' + found['file'], found['title'], 'luna/images/' + code + '.png'))
    else:
        found = next((a for a in plan['videos'] if a['id'] == code), None)
        if found:
            poster = 'images/RT01-M-rafa-court.png' if code == 'RT01-M' else 'images/RT01-P2-luna-match.png'
            assets.append(decorate(found, code, 'video', found['file'], found['title'], poster))

for code in ['RL01', 'RT01-P2', 'RT01-M', 'RL02', 'RL03']:
    if code.startswith('RL'):
        found = next(a for a in luna['assets'] if a['code'] == code and a['kind'] == 'image')
        assets.append(decorate(found, code + '-still', 'image', 'luna/' + found['file'], found['title'] + ' · image clé'))
    else:
        found = next(a for a in plan['images'] if a['code'] == code)
        assets.append(decorate(found, code + '-still', 'image', found['file'], found['title'] + ' · image clé'))

result = {'version': 1, 'title': 'Luna & Rafa · Reprises réalistes',
          'sourceEdit': '0927(1).mov', 'style': 'Photoreal live-action',
          'teamApproved': False, 'assets': assets}
(ROOT / 'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(f'{len(assets)} assets; {sum(a["usable"] for a in assets)} available')
