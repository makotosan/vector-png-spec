import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
try:
    from normalization_fixture import Rejected, normalize_structure, publish_pair, validate_output
except ModuleNotFoundError as exc:
    if exc.name != 'tinycss2':
        raise
    raise unittest.SkipTest('Optional normalization tests require requirements-normalization.txt')
from build_normalization_fixtures import cases

def case_named(name):
    return next(c for c in cases() if c['id'] == name)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'fixtures' / 'normalization'


class NormalizationTests(unittest.TestCase):
    def test_catalog_and_rejections(self):
        catalog = json.loads((FIXTURES / 'cases.json').read_text(encoding='utf-8'))
        self.assertEqual(catalog, cases())
        for case in catalog:
            with self.subTest(case=case['id']):
                if case['expect'] == 'accept':
                    result, report = normalize_structure(case['input'].encode())
                    validate_output(result)
                    self.assertEqual(report['checks']['render'], 'not-checked')
                    self.assertEqual(report['checks']['authenticity'], 'not-verified')
                    self.assertEqual(report['status'], 'failure')
                else:
                    with self.assertRaises(Rejected) as caught:
                        normalize_structure(case['input'].encode())
                    self.assertEqual(caught.exception.code, case['expect'])

    def test_cascade_inheritance_and_group_opacity(self):
        output, _ = normalize_structure(case_named('cascade')['input'].encode())
        root = validate_output(output)
        group = list(root)[0]
        self.assertEqual(group.get('opacity'), '0.5')
        a, b, circle = list(group)
        self.assertEqual(a.get('fill'), 'green')
        self.assertEqual(b.get('fill'), 'navy')
        self.assertIsNone(circle.get('fill'))  # inherits purple, not root default
        self.assertTrue(all(n.get('opacity') is None for n in group))
        self.assertNotIn(b'class=', output)
        out, _ = normalize_structure(case_named('source-order')['input'].encode())
        self.assertEqual(list(validate_output(out))[0].get('fill'), 'red')

    def test_accessibility_reports_loss_and_targets(self):
        output, report = normalize_structure(case_named('accessibility')['input'].encode())
        root = validate_output(output)
        self.assertEqual(root.find('{http://www.w3.org/2000/svg}title').text, 'Example')
        records = {r['attribute']: r for r in report['accessibility']}
        self.assertEqual(records['aria-labelledby']['target'], 'title')
        self.assertEqual(records['aria-describedby']['target'], 'desc')
        self.assertEqual(records['aria-label']['loss'], 'lower-priority-label')
        self.assertEqual(records['role']['loss'], 'unsupported-semantics')
        self.assertNotIn(b'aria-', output)

    def test_synthetic_nameplate_expected_files(self):
        source = (FIXTURES / 'nameplate.input.svg').read_bytes()
        output, report = normalize_structure(source)
        self.assertEqual(output, (FIXTURES / 'nameplate.expected.svg').read_bytes())
        self.assertEqual(report, json.loads((FIXTURES / 'nameplate.expected-report.json').read_text(encoding='utf-8')))
        self.assertEqual(report['changes']['class_attributes'], 26)
        self.assertEqual(report['changes']['style_elements'], 1)
        root = validate_output(output)
        self.assertTrue(any('EXAMPLE' in (n.text or '') for n in root.iter()))
        # QR path geometry and quiet zone survive the structural transformation.
        ns = '{http://www.w3.org/2000/svg}'
        import xml.etree.ElementTree as ET
        before = ET.fromstring(source).find('.//' + ns + 'path[@id="qr"]')
        after = root.find('.//' + ns + 'path[@id="qr"]')
        self.assertEqual(before.get('d'), after.get('d'))

    def test_resource_bounds(self):
        samples = [b' ' * 1_000_001,
                   ('<svg xmlns="http://www.w3.org/2000/svg">' + '<g>' * 33 + '</g>' * 33 + '</svg>').encode(),
                   ('<svg xmlns="http://www.w3.org/2000/svg">' + '<rect/>' * 5000 + '</svg>').encode(),
                   ('<svg xmlns="http://www.w3.org/2000/svg"><style>' + ' ' * 100001 + '</style></svg>').encode(),
                   ('<svg xmlns="http://www.w3.org/2000/svg"><style>' + ','.join('.c'+str(i) for i in range(1001)) + '{fill:red}</style></svg>').encode()]
        for data in samples:
            with self.subTest(length=len(data)), self.assertRaises(Rejected) as caught:
                normalize_structure(data)
            self.assertEqual(caught.exception.code, 'resource-limit')

    def test_transaction_and_input_immutability(self):
        # Stub checks the file transaction only; real rendering is an independent test.
        verified = lambda a, b: (True, {'test_stub': True})
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output, report = [root / n for n in ['input.svg', 'output.svg', 'report.json']]
            data = case_named('cascade')['input'].encode()
            source.write_bytes(data)
            publish_pair(source, output, report, verified)
            self.assertEqual(source.read_bytes(), data)
            self.assertEqual(json.loads(report.read_text())['checks']['render'], 'pass')
            for dst, rep in [(source, root/'other.json'), (output, report), (root/'new.svg', root/'new.svg')]:
                with self.assertRaises(Rejected):
                    publish_pair(source, dst, rep, verified)
            output.unlink()
            report.unlink()
            with self.assertRaises(Rejected):
                publish_pair(source, output, report, lambda a, b: (False, {}))
            self.assertFalse(output.exists())
            self.assertFalse(report.exists())
            import os
            link = os.link
            def fail_second(src, dst):
                if Path(dst) == report:
                    raise OSError('simulated second publication failure')
                link(src, dst)
            with patch('normalization_fixture.os.link', side_effect=fail_second), self.assertRaises(OSError):
                publish_pair(source, output, report, verified)
            self.assertEqual(source.read_bytes(), data)
            self.assertEqual(sorted(p.name for p in root.iterdir()), ['input.svg'])
            alias = root/'alias.svg'
            os.link(source, alias)
            with self.assertRaises(Rejected) as caught:
                publish_pair(source, alias, report, verified)
            self.assertEqual(caught.exception.code, 'output-alias')


if __name__ == '__main__':
    unittest.main()
