# Validation record

2026-10-18, local Windows x64 / Python 3.13.

- `python -m unittest discover -s tests -v`: 3 tests passed, including all
  21 positive/negative fixture cases, extracted source byte comparison and
  deterministic catalog regeneration.
- `python tools/build_fixtures.py --check`: fixture catalog is reproducible.
- CI runs the same checks on Windows, macOS and Linux with Python 3.13.

These checks validate this limited test catalog. They are not certification of
all PNG/SVG features, a production security validator, or proof of preview/source
equivalence. Native Illustrator/Inkscape integrations have not been tested here.
