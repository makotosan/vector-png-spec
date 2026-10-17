# safe-svg-v1 — restricted SVG profile, draft 0.1

This optional processing profile is distinct from container validity. It describes
the initial Python implementation's feature subset; it is not all of SVG.
No on-wire profile marker exists. An implementation MUST validate actual content.

Allowed SVG-namespace elements:

```text
svg g defs title desc path rect circle ellipse line polyline polygon text tspan
linearGradient radialGradient stop clipPath
```

Allowed unqualified attributes:

```text
id x y x1 y1 x2 y2 cx cy r rx ry width height viewBox preserveAspectRatio d points
transform fill fill-opacity fill-rule stroke stroke-width stroke-opacity
stroke-linecap stroke-linejoin stroke-miterlimit stroke-dasharray stroke-dashoffset
opacity font-family font-size font-weight font-style text-anchor dominant-baseline
dx dy rotate offset stop-color stop-opacity gradientUnits gradientTransform
spreadMethod fx fy fr clip-path clipPathUnits
```

Namespace declarations are XML namespace syntax, not presentation attributes.
Unknown or namespace-qualified attributes/elements MUST be rejected. DTDs,
entity declarations and non-declaration processing instructions are prohibited.
Comments and an optional UTF-8 XML declaration are allowed.

Reject event handlers, scripting, CSS/style, hyperlinks, image/data URLs, use,
foreignObject, animation, external references and resource fetching. Attribute
values MUST NOT contain backslash, @, braces, semicolon, angle brackets, NUL,
or controls below U+0020 other than TAB/LF/CR. Maximum attribute length is
100,000 Unicode code points. IDs MUST match `[A-Za-z_][A-Za-z0-9_.-]*` and be unique.

The only resource URL syntax is exactly `url(#ID)` for fill/stroke references
to a local linearGradient/radialGradient, or clip-path references to a local
clipPath. An attribute containing `url` (case insensitive) outside that exact
form MUST be rejected, matching the intentionally restrictive initial policy.
References inside resource definitions and their descendants MUST be rejected,
preventing recursive clips/paint servers. No file/network fallback is permitted.

At most 5000 elements and depth 32 (root depth 0) are allowed. Container byte
and pixel limits also apply. Validate numeric/path syntax through a bounded
renderer; allowlisting alone does not prove valid SVG or eliminate native-library
risks. Rendering SHOULD run with a timeout; the Python implementation uses 20
seconds. This is not an OS sandbox or hard memory quota.

Wider SVG support requires a separately documented profile/security policy.
Adapters MUST NOT silently remove unsupported artwork and claim lossless editing.
