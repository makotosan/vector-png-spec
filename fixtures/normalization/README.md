# Normalization fixtures

[日本語](README.ja.md)

These original synthetic examples exercise the experimental
[normalization profile](../../profiles/svg-normalization-v1.md). No customer SVG
or business content is included. nameplate.input.svg has one style element and
26 class attributes. It includes text and a version-1-L QR encoding the inert
text VECTOR-PNG, with a four-module quiet zone and six pixels per module.
The matrix was generated using ReportLab's QR encoder; no encoder code is copied
or required at test time. qr-matrix.json records the expected module grid.

nameplate.expected.svg and nameplate.expected-report.json are reviewed golden
structural results, not a claim of verified conversion. The report deliberately
says failure/render not-checked and has no output digest: analysis alone cannot
pass the rendering gate. The public cases.json also includes cascade, source
order, selector lists, inheritance, group opacity, metadata migration, and a
rounded diagram with horizontal and returning triangle arrows, plus inert
rejections for unsupported CSS, external references, XML hazards and conflicts.
No rejected case is rendered. Size/depth/count limits and transactional output
protection are tested dynamically rather than storing oversized files.

The Python tool in tools/normalization_fixture.py is an executable fixture
example, not a production sanitizer, fully audited normalizer or shipped CLI.
It uses tinycss2 tokenization and an independent restricted-output checker.
Transaction tests use an explicitly labeled renderer stub solely to test file
publication; actual appearance is checked by the separate Chromium adapter.
The finite suite is not certification of arbitrary SVG or accessibility behavior.

## Structural checks

The original PNG fixture tests remain dependency-free. Additional normalization
tests are skipped with an explicit reason if tinycss2 is absent. For all tests:

```sh
python -m pip install -r requirements-normalization.txt
python -m unittest discover -s tests -v
python tools/build_fixtures.py --check
python tools/build_normalization_fixtures.py --check
```

build_normalization_fixtures.py regenerates only cases.json, without external
dependencies. Golden SVG/report and QR changes must be reviewed deliberately;
they must not be regenerated automatically to make a failed test pass.

## Independent optional SVG2 rendering

Use a controlled host with fonts installed. Install Pillow in the test Python
environment and Playwright in a local Node environment, then install Chromium.
Alternatively set NORMALIZATION_CHROME to an existing Chrome executable.

```sh
python -m pip install Pillow
npm install --no-save playwright@1.58.2
npx playwright install chromium
python tools/prepare_normalization_render.py
node tools/render_normalization.cjs .normalization-render/manifest.json
python tools/check_normalization_render.py
```

The adapter renders checked sources as isolated SVG image documents, disables
script and external network access, and captures same-host RGBA previews at the
declared dimensions. The checker demands exact equality, checks every QR module
and quiet-zone pixel, and checks that the text region has ink. Review text and
arrows visually as well. This is not an OCR, physical print or phone-camera scan
test. Font choice is host-dependent and recorded; cross-host equality is not
asserted. A renderer that ignores CSS geometry, such as CSS rx/ry, is unsuitable
for those before/after checks. Results stay in ignored .normalization-render/.

Compatibility: no changes to PNG wire v1, the source keyword, safe-svg-v1 output
allowlists, or the original 21 PNG cases. See VALIDATION.md for actual results;
configured tests are not evidence of execution.
