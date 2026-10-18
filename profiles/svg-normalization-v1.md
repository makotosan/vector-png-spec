# SVG Normalization Profile v1 — draft 0.1

[日本語全文参考訳](svg-normalization-v1.ja.md)

Status: experimental input-processing profile, 2026-10-18. This English text is
normative; MUST, MUST NOT, SHOULD and MAY have the meanings in SPEC.md. This is
not a general CSS sanitizer or an extension of safe-svg-v1.

## 1. Purpose and compatibility

A normalizer transforms a restricted CSS-styled SVG into an SVG satisfying
[safe-svg-v1](safe-svg-v1.md) before a writer embeds it. It MUST NOT relax that
output profile. PNG wire v1, `vector-png.svg`, compression and extraction rules
are unchanged. Normalization is an explicit import operation, not extraction:
the original bytes MUST remain unchanged; only the normalized SVG is embedded.
No profile identifier or conversion report is added to the wire format.

## 2. Validate before transforming or rendering

Input MUST be strict UTF-8 XML (optional BOM and UTF-8 declaration), with one SVG
namespace `svg` root. Before rendering, a normalizer MUST reject DTDs, entity
declarations, external entities, non-declaration processing instructions, scripts,
event handlers, animation, foreign namespaces, images, use, foreignObject,
external resources and unknown elements/attributes. It MUST disable all file and
network fetching, including during before/after rendering. No browser DOM import
of unchecked source is permitted. Every declaration MUST be validated even if
overridden, unmatched or inside an otherwise unused definition.

The input vocabulary is safe-svg-v1 plus `style` and restricted `marker` elements,
unqualified `class`, `style`, `marker-end`, and `role` / `aria-*` attributes, and
the marker definition attributes in section 3.1. A style element MUST be a direct
child of the root or of a root-level defs, contain only CSS text, and have no
attributes except optional `type="text/css"`. Nested SVG roots are unsupported.
IDs and local resources MUST follow safe-svg-v1, including reference target
types, unique IDs and the ban on references within resource definitions, except
for the explicitly supported marker-end targets in section 3.1.
Accessibility attributes are inert metadata, never executable instructions.

Baseline limits MUST be enforced before allocation and while parsing: input and
output each at most 1,000,000 UTF-8 bytes; at most 5000 elements, depth 32 (root
0), 100,000 code points per attribute, 100,000 UTF-8 CSS bytes across style
elements and attributes, 1000 selectors and 10,000 declarations. Viewport limits
are 4096 pixels per side and 4,000,000 pixels. Implementations MUST document
stricter limits or explicitly increased local limits and report `resource-limit`
separately from malformed input. Parsing, matching and rendering MUST have finite
time and memory policies; a subprocess timeout alone is not an OS sandbox.

## 3. Closed CSS subset

The baseline accepts rule lists and inline declaration lists. Whitespace and
CSS comments are allowed. Each selector MUST be exactly one case-sensitive SVG
element name, `.CLASS`, or `#ID`; CLASS and ID in selectors and class tokens MUST
match `[A-Za-z_][A-Za-z0-9_-]*`. A comma-separated list of these selectors is
allowed. Combinators, compound selectors, universal/attribute/pseudo selectors,
namespaced selectors, escapes, nesting, all at-rules (including @import,
@font-face and @media), custom properties, shorthands and `!important` MUST be
rejected. A trailing declaration semicolon is allowed; malformed syntax MUST NOT
be recovered by silently ignoring declarations. Duplicate XML attributes are
invalid XML; duplicate valid CSS declarations are resolved by section 4.

Allowed properties and values (property names are ASCII case-insensitive):

| Properties | Accepted value grammar |
| --- | --- |
| fill, stroke | `none`, the 16 CSS basic color names, `#RGB`, `#RRGGBB`, or exact `url(#ID)` to a local gradient |
| stop-color | The same colors, without `none` or URL |
| opacity, fill-opacity, stroke-opacity, stop-opacity | Decimal number in [0,1] |
| stroke-width, font-size | Nonnegative decimal, optionally `px` |
| stroke-miterlimit | Decimal number at least 1 |
| stroke-dashoffset | Signed decimal, optionally `px` |
| stroke-dasharray | `none`, or a nonempty comma/whitespace list of nonnegative decimals optionally `px`; not all zero |
| fill-rule | `nonzero`, `evenodd` |
| stroke-linecap | `butt`, `round`, `square` |
| stroke-linejoin | `miter`, `round`, `bevel` |
| font-family | One or more comma-separated ASCII names, unquoted words separated by spaces or quoted names; no escapes |
| font-weight | `normal`, `bold`, or 100, 200, …, 900 |
| font-style | `normal`, `italic`, `oblique` |
| text-anchor | `start`, `middle`, `end` |
| dominant-baseline | `auto`, `alphabetic`, `middle`, `central`, `hanging`, `text-before-edge`, `text-after-edge` |
| clip-path | `none` or exact `url(#ID)` to a local clipPath |
| rx, ry | Nonnegative decimal, optionally `px`, applied only to rect |
| marker-end | `none` or exact `url(#ID)` to a restricted local marker |

A decimal is `[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)` without exponent or
nonfinite values. Keywords and color names are ASCII case-insensitive; fragment
IDs are case-sensitive. A parser MUST tokenize CSS; it MUST NOT implement this
by blindly splitting at semicolons or removing style nodes before inspection.
Other functions, units, percentage values, currentColor, inherit, initial,
unset, revert and var/calc MUST be rejected. These restrictions also apply to
input presentation attributes for the listed properties. Other safe-svg-v1
attributes, including geometry and transforms, remain subject to that profile
and bounded rendering. Other CSS geometry properties and CSS transforms are
not accepted. rx/ry MUST be resolved using SVG2 CSS geometry semantics and
materialized on rect as attributes; a renderer that ignores CSS rx/ry is not a
valid before-render oracle for such input.

### 3.1 Restricted arrow-marker expansion

This input-only subset supports the arrow forms commonly used in diagrams.
Markers MUST be direct children of a root-level defs. The only marker attributes
are id, markerWidth, markerHeight, refX, refY, orient and markerUnits. Width/height
MUST be positive unitless decimals; refX/refY MUST be within that viewport and
default to 0. orient MUST be `auto`. markerUnits is `strokeWidth` (default) or
`userSpaceOnUse`. No viewBox, transform, overflow, marker-start/mid, context paint,
or recursive resource references are supported. Each marker MUST contain exactly
one path, with no attributes except d and an optional solid fill. Its geometry
MUST be the viewport-contained triangle `M0,0 Lw,h/2 L0,h Z`, where w/h are the
marker viewport dimensions. Paint MUST be a solid color, not none or a resource.

marker-end MUST apply only to an open, single-subpath path with fill none, using
absolute M/L/H/V segments (implicit repeated coordinates allowed), with a nonzero
last segment. A host transform, opacity or clip-path declaration is unsupported
in this baseline and MUST fail. A normalizer MUST compute the last tangent,
orient the triangle to it, scale by the computed stroke-width for strokeWidth
units (default 1), offset by refX/refY, and insert an ordinary path/group immediately
after the host. It MUST preserve parent compositing, local geometry and paint
order, explicitly set the marker paint and stroke none, and remove marker
definitions/attributes only after all uses have been expanded. Other marker or
host geometry MUST be rejected, not approximated. Expansion counts MUST be
reported in changes.expanded_markers. Output still uses only safe-svg-v1 elements.

## 4. Cascade, inheritance and output

Implementations MUST follow the author cascade for the supported subset:
presentation attributes have specificity zero and precede all author rules;
element, class and ID selectors have specificity (0,0,1), (0,1,0) and (1,0,0).
Inline declarations outrank all supported selectors. Higher specificity wins;
ties use later style-element/rule/declaration order. Selector lists use the
highest specificity among matching selectors. Legal conflicts MUST resolve
deterministically, not fail merely because colors differ. Unsupported conflict
mechanisms, such as `!important`, MUST fail even when they would lose.

Winning declarations MUST be written as unqualified presentation attributes on
the same element. For inherited properties the nearest ancestor's computed value
is inherited only when the element has no own winning declaration. The output
MUST preserve that behavior by retaining the element hierarchy and attribute
placement; it MAY materialize equivalent inherited values. In particular group
opacity and clip-path MUST NOT be flattened into children: they are not inherited
paint values. stop-color/stop-opacity likewise MUST NOT be inherited. SVG initial
values apply where there is no declaration or applicable inheritance.

The normalizer MUST remove style elements, class and inline style attributes
only after resolution, preserve retained artwork's geometry, text, IDs, order and
local references (apart from expanded marker bookkeeping and reported metadata migration),
and revalidate the complete serialized output against safe-svg-v1. It MUST NOT
silently strip unsupported artwork or claim byte-preserving extraction. It MUST
reject an output exceeding limits or containing any unsupported remaining data.

## 5. Accessibility migration

For each element, accessible name precedence is aria-labelledby, aria-label,
then its existing direct title. aria-labelledby and aria-describedby MUST resolve
space-separated unique IDs in order to text-only title, desc, text or tspan
content (no other descendants); missing, cyclic/self, or nontext targets MUST
fail. Join referenced text with spaces and collapse XML whitespace. The name
MUST be represented by a direct title; aria-describedby content by a direct desc.
Existing direct title/desc MUST be retained if not replaced. If replacement is
needed, the old text MUST be recorded as loss; multiple existing direct title or
desc children are unsupported. New metadata nodes MUST NOT duplicate IDs.

All role and aria-* attributes MUST be removed from output. The report MUST
record every removed attribute, its element location, value, migration target
or explicit loss reason, including a lower-priority aria-label and semantic
roles, states or relationships not representable in title/desc. Unknown aria-*
attributes MUST be reported as unsupported semantics, not silently dropped.
Conversion MAY succeed with these reported semantic losses, but MUST NOT claim
full accessibility equivalence. A caller SHOULD offer review of these losses.

## 6. Rendering gate and safe publication

Before and after normalization MUST be rendered only after input checks, in the
same controlled renderer/version, font environment, viewport, background,
color/alpha policy and resource-denial policy. The default comparison MUST use
exact decoded RGBA equality. Another explicit local comparison policy MAY use
documented tolerances, but MUST report them and MUST NOT hide a mismatch as a pass.
Cross-OS exact equality is not a universal requirement. Normalization failure,
render failure, timeout or mismatch MUST fail by default and MUST NOT publish a
successful normalized SVG or PNG. An explicit analysis-only mode MAY skip
rendering, but MUST report `not-checked`, MUST NOT claim verified success and
MUST NOT publish conversion output. Fixture-only tests of cascade rules are not
a substitute for the rendering gate in a user-facing implementation.

The original file MUST NOT be modified, even by explicit overwrite. The normalized
SVG and JSON report MUST be distinct output paths, neither aliasing input nor
each other (including symlinks/hard links). Existing outputs MUST be preserved by
default. Implementations MUST stage and validate complete data before publication,
use no-clobber publication, and roll back any newly created output if publishing
its pair fails. A failure diagnostic MAY be returned separately; it MUST NOT
overwrite an existing output/report or leave a partial successful pair. A future
explicit overwrite option MUST still protect input and disclose its policy.

## 7. Conversion report

The report MUST be UTF-8 JSON and include the following independent results.
Field names below define the baseline report schema; additional fields MAY exist.

| Field | Meaning |
| --- | --- |
| profile | `svg-normalization-v1` |
| status | `success` or `failure` |
| input_sha256, output_sha256 | Byte digests; output is null on failure |
| changes | Counts of removed style elements, class attributes, inline styles, applied declarations and expanded_markers |
| accessibility | Ordered records with element path, attribute, original value, target or loss reason |
| checks.input, checks.safe_svg | `pass`, `fail` or `not-checked` |
| checks.render | `pass`, `mismatch`, `error` or `not-checked` |
| checks.container | `not-applicable` for SVG-only normalization; separately checked for PNG conversion |
| checks.authenticity | `not-verified`; hashes and pixels do not authenticate origin |
| render | Renderer/version, fonts, viewport, background, color/alpha policy, resource policy, exact/tolerant mode and tolerances; null if not checked |
| errors, warnings | Structured records with code, stage and explanation; empty arrays when none |

Failure codes SHOULD distinguish invalid-xml, unsafe-input, unsupported-css,
invalid-reference, resource-limit, output-exists, output-alias, render-error and
render-mismatch. Digests MUST NOT be described as signatures. Reports containing
source metadata MUST be treated as untrusted data. A successful report MUST have
passed input, safe-svg and render checks; a structurally valid PNG alone does not
establish these claims. File paths in accessibility records use root `/svg[1]`
and same-name sibling indices, e.g. `/svg[1]/g[1]/text[2]`.

## 8. Fixtures, migration and future CLI (informative)

[fixtures/normalization](../fixtures/normalization/README.md) contains synthetic,
original test data, expected outputs/reports and rejection cases. It does not
publish the user's nameplate. Structural tests and optional controlled-render
tests have different dependencies; finite fixtures are not full certification.

Proposed future reference CLI: `normalize input.svg normalized.svg --report report.json`
and `convert input.svg output.png --report report.json`. These commands are not
implemented by this specification repository. A future convert MUST run the
normalization gate, then the existing writer and container checks, and record
the results separately. No automatic extraction-time normalization is proposed.

This profile adds an optional input path and does not change existing fixture
acceptance, the safe-svg-v1 allowlist, or wire v1. Existing readers need no change.
Implementations must review and pin this profile before claiming support.

References: [CSS cascade](https://www.w3.org/TR/css-cascade-3/),
[SVG styling](https://www.w3.org/TR/SVG/styling.html),
[SVG title/desc and accessibility](https://www.w3.org/TR/SVG/struct.html).
The subset above is deliberately narrower; those standards do not imply support
for omitted CSS features.
