"""Prepare only the committed public normalization examples for render tests."""
import json
from pathlib import Path
from normalization_fixture import normalize_structure, validate_output

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'fixtures' / 'normalization'
WORK = ROOT / '.normalization-render'


def main():
    WORK.mkdir(exist_ok=True)
    cases = [('nameplate', (FIXTURES / 'nameplate.input.svg').read_bytes())]
    cases.extend((c['id'], c['input'].encode()) for c in json.loads((FIXTURES/'cases.json').read_text(encoding='utf-8')) if c['expect'] == 'accept')
    manifest = []
    for name, raw in cases:
        output, _ = normalize_structure(raw)
        root = validate_output(output)
        before, after = WORK/(name+'.before.svg'), WORK/(name+'.after.svg')
        before.write_bytes(raw)
        after.write_bytes(output)
        manifest.append(dict(id=name, before=str(before), after=str(after), width=int(root.get('width')), height=int(root.get('height'))))
    (WORK/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(WORK/'manifest.json')


if __name__ == '__main__':
    main()
