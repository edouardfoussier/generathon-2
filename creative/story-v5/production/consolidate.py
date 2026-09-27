"""Rebuild the v5 review manifest from completed, locally available generation slices."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ORDER = ['K01', 'T01A', 'K03', 'K04', 'K05', 'K06', 'K07', 'K08', 'T01B', 'VK01', 'VT01', 'VT01-CUT']

def main():
    destination = ROOT / 'manifest.json'
    manifest = json.loads(destination.read_text()) if destination.exists() else {'version': 1}
    assets = []
    for part in ['luna', 'memories', 'transitions']:
        for name in ['result.json', 'motion-result.json']:
            path = ROOT / part / name
            if not path.exists():
                continue
            for asset in json.loads(path.read_text()).get('assets', []):
                if asset.get('status') == 'generated' and (ROOT / asset['file']).is_file():
                    asset.setdefault('kind', 'image')
                    asset['teamApproved'] = False
                    assets.append(asset)
    assert len({a['code'] for a in assets}) == len(assets), 'Duplicate asset codes'
    assets.sort(key=lambda a: ORDER.index(a['code']) if a['code'] in ORDER else len(ORDER))
    manifest.update(assets=assets, updatedAt=datetime.now(timezone.utc).isoformat(),
                    status='review-ready' if sum(a['kind'] == 'video' for a in assets) >= 2 else 'images-ready-motion-tests-pending')
    destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f"{sum(a['kind'] == 'image' for a in assets)} images and {sum(a['kind'] == 'video' for a in assets)} videos on the board.")

if __name__ == '__main__':
    main()
