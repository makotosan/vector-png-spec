# vector-png specification

[日本語](README.ja.md)

An application-independent **draft** for PNG files containing editable SVG source
in compressed iTXt. This repository defines the format and interoperability
expectations; it is not a Codex skill or an Illustrator/Inkscape plugin.

- [Normative specification: wire v1, draft 0.1](SPEC.md)
- [日本語仕様ガイド](SPEC.ja.md) (informative translation)
- [Safe SVG profile](profiles/safe-svg-v1.md)
- [Interoperability and implementation guidance](IMPLEMENTATIONS.md)
- [Fixture catalog and test instructions](fixtures/README.md)

The [Python CLI / Codex skill](https://github.com/makotosan/vector-png) is a
separate reference implementation. Future Illustrator, Inkscape and other
integrations can implement the container without depending on Python or CairoSVG.
No Adobe or Inkscape integration is implemented or certified here.

Three distinct claims must not be confused: **container validity**, **safe SVG
profile support**, and **renderer-specific pixel comparison**. A successful
container check does not establish that pixels match the SVG or that SVG is safe
to execute. Exact CairoSVG pixel equality is not a universal format requirement.

Run the dependency-free fixture checks with Python 3.10+:

```sh
python -m unittest discover -s tests -v
python tools/build_fixtures.py --check
```

Changes are proposed through issues or pull requests. The English SPEC.md is
normative; draft revisions must identify wire-format impact. Wire v1 has no
embedded version field; an incompatible successor needs a new documented keyword.
See [CONTRIBUTING.md](CONTRIBUTING.md). All original documents, tools and fixtures
in this repository are MIT licensed; upstream standards retain their own licenses.
