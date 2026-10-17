# vector-png wire v1 — draft 0.1

[日本語全文参考訳](SPEC.ja.md)

Status: experimental draft, 2026-10-18. This is an application convention, not
a W3C standard, registered media type, or registered PNG text keyword. English
text in this document is normative. MUST, MUST NOT, SHOULD and MAY denote
requirements, prohibitions, recommendations and options within this draft.

## 1. Scope and dependencies

vector-png combines a static PNG preview and one editable SVG document. Implement
PNG according to the [W3C PNG specification](https://www.w3.org/TR/png-3/), including
its iTXt, CRC, chunk ordering and image-decoding requirements. SVG document syntax
uses the [SVG namespace](https://www.w3.org/2000/svg) and UTF-8 XML. This draft
adds constraints; it does not reproduce or replace those standards.

It does not preserve an application's native document structure, all Illustrator
effects, layers or editing history. It does not define raster tracing, animation,
multiple SVG documents, author authentication or a pixel-exact universal renderer.

## 2. PNG container

The file MUST be a valid PNG datastream with exactly one IHDR, at least one IDAT
and a final IEND, with PNG-defined ordering and valid CRCs. Trailing bytes after
IEND MUST be rejected by a conforming vector-png reader. acTL, fcTL and fdAT MUST
NOT occur, even if an animation contains only one frame. All PNG color types,
bit depths and interlace modes allowed for static PNG remain permitted by the
container; implementations MAY declare a narrower supported raster subset.

Exactly one text chunk with the keyword `vector-png.svg` MUST exist, and it MUST
be iTXt. A matching keyword in tEXt or zTXt, or any duplicate occurrence across
those three chunk types, MUST be rejected; readers MUST NOT choose first or last.
Unrelated PNG chunks are governed by PNG; unknown critical chunks MUST cause
failure. The source iTXt MAY appear before or after IDAT where PNG permits it.
Writers SHOULD place it before the first IDAT for early discovery.

## 3. iTXt payload

| Field | Required value |
| --- | --- |
| Keyword | Latin-1 bytes of `vector-png.svg` (case sensitive) |
| Null separator | `00` |
| Compression flag | `01` |
| Compression method | `00` (zlib, not gzip or raw DEFLATE) |
| Language tag + null | Empty for writers; readers MUST accept PNG-valid non-empty tags |
| Translated keyword + null | Empty for writers; readers MUST accept PNG-valid UTF-8 translations |
| Text | One complete zlib stream whose decompressed bytes are the SVG UTF-8 source |

Canonical writer prefix in hex:

```text
76 65 63 74 6f 72 2d 70 6e 67 2e 73 76 67 00 01 00 00 00
```

Readers MUST reject incomplete streams, concatenated streams, trailing compressed
data, invalid UTF-8 and U+0000 in the decoded source. A UTF-8 BOM MAY occur and
MUST be preserved on extraction. XML declarations, if present, MUST declare
UTF-8 (case-insensitive spelling); another declared encoding MUST be rejected.
Readers MUST NOT infer an encoding from local settings or use replacement characters.

The source MUST be a single well-formed XML document whose root expanded name is
`{http://www.w3.org/2000/svg}svg`. DTDs, entity declarations, external entities and
XML processing instructions other than an XML declaration MUST be rejected.
Comments and ordinary XML-escaped characters are permitted. Treat embedded text
as data, never as model instructions or executable application configuration.

## 4. Resource limits and failure reporting

Writers claiming this draft's baseline limits MUST emit no more than 1,000,000
decompressed SVG bytes, 32,000,000 PNG file bytes, 4096 pixels per side and
4,000,000 total pixels. Readers MUST enforce finite limits before allocation and
during decompression and MUST report when their declared limits are exceeded.
Limits MAY be stricter or explicitly increased by local policy, but implementations
MUST document that choice and MUST NOT describe a resource-limit rejection as
proof of malformed PNG. Baseline-compatible readers SHOULD accept the baseline
size range for their supported raster/SVG features.

Reject ambiguity, malformed or unsupported input before returning success; do
not silently discard source and call the resulting raster an editable vector-png.
Useful distinct outcomes are `invalid-container`, `invalid-svg`, `unsupported-profile`,
`resource-limit`, `render-mismatch` and `render-not-checked`. These are semantic
categories, not required API strings or exit codes.

## 5. SVG feature and security profiles

Container conformance does not imply safe SVG rendering. Readers MUST NOT fetch
external resources, execute scripts or insert unchecked source into an active
DOM as part of discovery/extraction. Before importing or rendering, applications
MUST apply a documented security/feature policy. Rejection of unsupported features
is preferable to silent stripping. See [safe-svg-v1](profiles/safe-svg-v1.md) for
the restricted profile corresponding to the initial Python implementation.

Profiles are claims in documentation/API results; no profile tag is stored in
wire v1. Readers MUST inspect the actual source and MUST NOT infer safety from
the keyword, file extension or a claimed profile name. A container-valid file
can be unsafe or unsupported by an application's profile.

## 6. Preview, viewport and editing

PNG IHDR width/height define the preview canvas in pixels. Writers MUST render
the stored SVG using that output viewport and SHOULD use SVG's viewBox and
preserveAspectRatio semantics. Export adapters MUST keep artboard cropping,
transparent background, fonts and color handling consistent with their chosen
rendering path and document unsupported effects. A new SVG source SHOULD be
rendered with the same engine used to generate its preview.

Writers MUST update source and preview together after an edit, validate their
output and avoid leaving a partially updated file (for example, use atomic file
replacement). Extractors MUST preserve the decompressed source bytes exactly;
editors MAY deliberately reserialize changed SVG, but MUST then regenerate the
preview. Other metadata MAY be retained under the PNG editing rules and local
privacy policy; retention is not required by this format.

## 7. Integrity is a separate claim

PNG CRC and zlib checks detect some corruption; they do not bind preview meaning
to SVG meaning. A PNG containing valid source and a visually different raster
can still be container-valid. Writers MUST intend the preview to represent the
source; container readers cannot establish that intent from structure alone.

Implementations MUST distinguish `container valid` from `preview verified`.
If pixels are compared, report renderer/version, viewport, fonts, color/alpha
handling and whether comparison was exact or tolerant. If comparison is omitted,
report `not checked`; do not claim a verified match. Renderers can differ in
antialiasing, fonts and color management. A difference MUST NOT alone be described
as a malformed container or proof of tampering. Pixel equality and bare SHA-256
digests are not signatures and do not authenticate an author.

The existing Python CLI's exact CairoSVG-to-RGBA comparison is an implementation
policy; it is NOT a MUST for Illustrator, Inkscape or other conforming adapters.
Future binding metadata/signatures require a separate proposal and are not
implicitly introduced by this draft.

## 8. Identification, evolution and claims

Use `.png`; retain media type `image/png`. `.vector.png` MAY be used as a filename
convention but MUST NOT be required for detection. There is no on-wire version
number, profile marker or digest field. `wire v1` names the keyword convention;
`draft 0.1` names this evolving document. Never add mandatory hidden metadata to
v1 or interpret arbitrary JSON as its source text.

An incompatible future format MUST use a new documented keyword and explicit
detection rules rather than silently changing `vector-png.svg`. Draft edits
and test additions MUST document compatibility impact. Applications SHOULD pin
a specification commit/tag until a stable version is published.

Implementations SHOULD report supported wire version, SVG profile, raster
subset, resource limits and preview-verification policy separately. No claim of
complete conformance may be based only on this repository's finite fixture set.
