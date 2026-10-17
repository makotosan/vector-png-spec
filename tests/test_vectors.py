import base64
import json
from pathlib import Path
import sys
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_fixtures import extract_source
from build_fixtures import vectors


class FixtureTests(unittest.TestCase):
    def test_catalog(self):
        catalog = json.loads((ROOT / 'fixtures/vectors.json').read_text(encoding='utf-8'))
        self.assertGreaterEqual(len(catalog['fixtures']), 20)
        for item in catalog['fixtures']:
            with self.subTest(name=item['name']):
                data = base64.b64decode(item['png_base64'], validate=True)
                if item['container_valid']:
                    self.assertEqual(extract_source(data), base64.b64decode(item['source_base64']))
                else:
                    with self.assertRaises((ValueError, UnicodeError, zlib.error)):
                        extract_source(data)

    def test_reproducible(self):
        actual = json.loads((ROOT / 'fixtures/vectors.json').read_text(encoding='utf-8'))
        self.assertEqual(actual, vectors())

    def test_document_links(self):
        self.assertIn('(SPEC.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))
        self.assertIn('(README.ja.md)', (ROOT / 'README.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
