# Implementation and migration notes

The [vector-png Python project](https://github.com/makotosan/vector-png) predates
this draft and implements the same compressed iTXt keyword convention. Its
CLI/skill is an implementation, not the authority for interpreting this spec.

The initial CLI is stricter in some areas (exact CairoSVG preview matching),
and is not yet audited against every new requirement here (including all PNG
ordering, single-frame APNG rejection, byte-preserving BOM handling and declared
XML encoding checks). It MUST NOT be advertised as fully conforming merely
because this repository was created. No existing implementation was changed
automatically by extracting this specification.

For Illustrator/Inkscape adapters:

1. Parse and bound the PNG/source without executing SVG or fetching resources.
2. Apply the adapter's SVG security/feature policy before import.
3. Import source into the editor; preserve dimensions/viewBox and explain losses.
4. Export updated SVG and generate a preview from that exported source in one
   consistent pipeline. Do not export unrelated raster/SVG representations.
5. Write one compressed iTXt source and publish a validated complete PNG.
6. Report container, profile and preview checks separately.

Do not compare Illustrator pixels with CairoSVG and call a difference corruption.
An adapter can compare with its own pinned renderer, or explicitly report preview
verification as not checked. Font outlining helps portability but changes editing
semantics and should be a deliberate user/export choice.

Conformance claims should identify the exact spec commit, raster support, SVG
profile, limits, renderer and known deviations. The fixture checker here is a
test-data sanity check, not a production SVG sanitizer, full PNG decoder, or
complete certification suite. Rendering/native-app integration tests belong in
the implementing repositories.

## Optional normalized import

[日本語全文参考訳](IMPLEMENTATIONS.ja.md)

[SVG Normalization Profile v1](profiles/svg-normalization-v1.md) is an input-only
profile. Implementations may adopt it without changing wire v1 or widening the
safe-svg-v1 allowlist. Validate the original, resolve the restricted CSS cascade,
materialize rect rx/ry, expand the restricted triangle arrow markers, migrate
accessible names/descriptions, validate the output, compare controlled renders,
and publish a separate SVG/report pair without modifying input. Keep extraction
byte-preserving; never normalize automatically on extract.

CSS rx/ry requires an SVG2-capable before-renderer. A renderer silently ignoring
these declarations cannot validate appearance preservation. Marker expansion is
deliberately limited to the profile's explicit triangle and open linear path
forms. Other markers, curves or unsupported styling must fail rather than lose
artwork. Metadata migration can report semantic losses; it does not promise full
native editing or accessibility fidelity.

Future CLI proposals are `normalize input.svg normalized.svg --report report.json`
and `convert input.svg output.png --report report.json`. They are not implemented
here or automatically added to the Python CLI. The latter would normalize first,
then use the writer/container checks and report container, profile, rendering and
authenticity separately. Support claims must pin and audit the new profile.

The test-only transformer and render adapter in tools exercise fixtures, not
arbitrary uploads. They are not a production security boundary or a shipped
normalization CLI. No implementation compatibility reference is automatically
advanced by this specification change. Compatibility impact: optional input
processing only; existing PNG fixtures, keyword and stored SVG profile unchanged.

