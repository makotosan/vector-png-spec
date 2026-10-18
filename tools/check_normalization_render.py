"""Verify independently rendered public fixtures; optional Pillow dependency."""
import json
import hashlib
from pathlib import Path
from PIL import Image
from normalization_fixture import normalize_structure

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.normalization-render'


def main():
    manifest = json.loads((WORK/'manifest.json').read_text(encoding='utf-8'))
    environment = json.loads((WORK/'manifest.json.results.json').read_text(encoding='utf-8'))
    results = []
    for case, env in zip(manifest, environment, strict=True):
        assert case['id'] == env['id']
        with Image.open(case['before']+'.png') as before, Image.open(case['after']+'.png') as after:
            a, b = before.convert('RGBA'), after.convert('RGBA')
            assert a.size == b.size == (case['width'], case['height'])
            assert a.tobytes() == b.tobytes(), 'RGBA mismatch: '+case['id']
            if case['id'] == 'nameplate':
                qr = json.loads((ROOT/'fixtures'/'normalization'/'qr-matrix.json').read_text())
                # Validate each complete module rectangle, including four-module
                # quiet zone. No interpolation or absent/merged modules permitted.
                matrix = qr['matrix']
                for y in range(29):
                    for x in range(29):
                        dark = 4 <= x < 25 and 4 <= y < 25 and matrix[y-4][x-4]
                        expected = (0,0,0,255) if dark else (255,255,255,255)
                        tile = b.crop((450+x*6,40+y*6,456+x*6,46+y*6))
                        assert tile.tobytes() == bytes(expected) * 36, ('QR module',x,y)
                # The named text region must contain non-background ink.
                assert b.crop((25,40,400,120)).convert('RGB').tobytes() != bytes((255,255,255)) * (375*80)
            results.append(dict(id=case['id'], exact_rgba=True, render=env))
            raw = Path(case['before']).read_bytes()
            normalized = Path(case['after']).read_bytes()
            expected, report = normalize_structure(raw)
            assert normalized == expected
            report.update(status='success', output_sha256=hashlib.sha256(normalized).hexdigest(), render=env)
            report['checks']['render'] = 'pass'
            (WORK/(case['id']+'.report.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (WORK/'verification.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([dict(id=r['id'],exact_rgba=r['exact_rgba']) for r in results]))


if __name__ == '__main__':
    main()
