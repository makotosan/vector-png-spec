# Validation record

[日本語](VALIDATION.ja.md)

2026-10-18, local Windows x64 / Python 3.13.

- `python -m unittest discover -s tests -v`: 3 tests passed, including all
  21 positive/negative fixture cases, extracted source byte comparison and
  deterministic catalog regeneration.
- `python tools/build_fixtures.py --check`: fixture catalog is reproducible.
- CI runs the same checks on Windows, macOS and Linux with Python 3.13.

These checks validate this limited test catalog. They are not certification of
all PNG/SVG features, a production security validator, or proof of preview/source
equivalence. Native Illustrator/Inkscape integrations have not been tested here.

## SVG normalization proposal (Issue #1)

2026-10-18, Windows x64, Python 3.13.5, tinycss2 1.5.1, Chrome 155.0.8059.80.

- 9 unittest tests passed: the original 21 PNG cases, 24 normalization catalog
  cases (5 accepted, 19 rejected), the synthetic 26-class/one-style nameplate,
  dynamic size/depth/count limits, cascade/inheritance, accessibility records,
  input immutability, hard-link alias detection, no-clobber publication,
  mismatch refusal and rollback after a second-output publication failure.
- Both fixture generators passed --check; the original PNG catalog is unchanged.
- Six public positive examples (nameplate and five catalog cases) were rendered
  before/after in the same offline, script-disabled Chromium image environment.
  All had exact decoded RGBA equality at their declared sizes. Every QR module
  and quiet-zone pixel matched the recorded matrix; the text region contained ink.
  Nameplate text and diagram arrows were also visually inspected. No phone-camera,
  physical-print, OCR or cross-OS equality test is claimed.
- Two user-supplied private diagrams, 1200x470 and 1200x500, also had exact
  same-host RGBA equality after CSS rx/ry materialization and restricted arrow
  expansion. Japanese text and arrows were visually inspected. Their original
  files were read only; neither sources nor their generated previews/reports are
  published in this repository. Synthetic fixtures cover the same feature forms.
- The existing installed reference helper's safe SVG validator accepted all six
  public and three local private-check outputs (one duplicated public nameplate).
  This is additional evidence, not a claim of full reference-implementation audit.

The font environment was this Windows host's system fonts with the SVG font-family
preserved. Fonts are not a portable pinned bundle; these results only compare
each before/after pair on this host. A renderer ignoring SVG2 CSS geometry cannot
serve as the before-render oracle. Normalization render checks are an optional
separate toolchain; the CI matrix installs tinycss2 and runs structural tests,
not these browser checks. CI results must be inspected separately after publication.

Documentation parity was reviewed for SPEC, README, IMPLEMENTATIONS, VALIDATION,
the normalization profile and its fixture README, including requirements, limits,
tables, examples and references. No wire-format, safe-svg-v1 allowlist or existing
PNG-fixture acceptance change is introduced. The test transformer is not a
production normalization CLI or a security certification.

