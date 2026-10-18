"""Deterministic public synthetic examples. No customer SVGs or dependencies."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'fixtures' / 'normalization'
NS = 'http://www.w3.org/2000/svg'


def cases():
    def svg(body, attrs=''):
        return f'<svg xmlns="{NS}" width="240" height="120" {attrs}>{body}</svg>'
    styles = '<style>rect {fill: red} .paint {fill: blue} #box {fill: green} .paint {fill: yellow}</style>'
    return [
        dict(id='rounded-diagram-arrows', input=svg('<title id="t">Public diagram</title><desc id="d">Synthetic arrows</desc><defs><marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="#363636"/></marker><style>.box {fill: white; stroke: black; stroke-width: 2; rx: 10} .arrow {fill: none; stroke: black; stroke-width: 2; marker-end: url(#arrow)}</style></defs><rect class="box" x="10" y="10" width="60" height="40"/><path class="arrow" d="M70 30 H130"/><path class="arrow" d="M200 50 V90 H40 V70"/>', 'role="img" aria-labelledby="t d"'), expect='accept'),
        dict(id='cascade', input=svg(styles + '<g fill="purple" opacity="0.5"><rect id="box" class="paint" width="20" height="20" fill="white"/><rect class="paint" x="30" width="20" height="20" style="fill: teal; fill: navy"/><circle cx="90" cy="10" r="10"/></g>'), expect='accept'),
        dict(id='source-order', input=svg('<style>.paint {fill: blue} .paint {fill: red}</style><rect class="paint" width="20" height="20"/>'), expect='accept'),
        dict(id='selector-list', input=svg('<style>rect, .paint {fill: blue}</style><rect width="20" height="20"/><circle class="paint" cx="60" cy="10" r="10"/>'), expect='accept'),
        dict(id='accessibility', input=svg('<title id="t">Example</title><desc id="d">Description</desc><rect width="20" height="20"/>', 'role="img" aria-labelledby="t" aria-label="fallback" aria-describedby="d" aria-live="polite"'), expect='accept'),
        dict(id='important-conflict', input=svg('<style>.a {fill: red !important} #x {fill: blue}</style><rect id="x" class="a"/>'), expect='unsupported-css'),
        dict(id='unsupported-unmatched', input=svg('<style>.unused {filter: blur(2px)}</style>'), expect='unsupported-css'),
        dict(id='unclosed-rule', input=svg('<style>.paint {fill: red</style>'), expect='unsupported-css'),
        dict(id='unclosed-comment', input=svg('<style>/* unfinished</style>'), expect='unsupported-css'),
        dict(id='external-css', input=svg('<style>@import "https://example.invalid/style.css";</style>'), expect='unsupported-css'),
        dict(id='external-paint', input=svg('<rect fill="url(https://example.invalid/paint.svg#p)"/>'), expect='unsupported-css'),
        dict(id='pseudo-selector', input=svg('<style>rect:hover {fill: red}</style>'), expect='unsupported-css'),
        dict(id='relative-font', input=svg('<text style="font-size: 2em">Example</text>'), expect='unsupported-css'),
        dict(id='escaped-css', input=svg('<style>.a {f\\69ll: red}</style>'), expect='unsupported-css'),
        dict(id='unsafe-xml', input=f'<!DOCTYPE svg [<!ENTITY example "inert">]><svg xmlns="{NS}"/>', expect='unsafe-input'),
        dict(id='processing-instruction', input=f'<?example inert?><svg xmlns="{NS}"/>', expect='unsafe-input'),
        dict(id='script-element', input=svg('<script/>'), expect='unsafe-input'),
        dict(id='event-attribute', input=svg('<rect onclick="inert"/>'), expect='unsafe-input'),
        dict(id='duplicate-xml-attribute', input=svg('<rect fill="red" fill="blue"/>'), expect='invalid-xml'),
        dict(id='missing-aria-target', input=svg('', 'aria-labelledby="missing"'), expect='invalid-reference'),
        dict(id='missing-paint-target', input=svg('<rect fill="url(#missing)"/>'), expect='invalid-reference'),
        dict(id='wrong-paint-target', input=svg('<rect id="paint" fill="url(#paint)"/>'), expect='invalid-reference'),
        dict(id='recursive-definition', input=svg('<defs><clipPath id="c"><rect clip-path="url(#c)"/></clipPath></defs>'), expect='invalid-reference'),
        dict(id='unsupported-marker-host', input=svg('<defs><marker id="a" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 Z" fill="black"/></marker></defs><path d="M0 0 C1 2 3 4 5 6" fill="none" marker-end="url(#a)"/>'), expect='unsupported-css'),
    ]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = (json.dumps(cases(), indent=2, ensure_ascii=False) + '\n').encode()
    path = ROOT / 'cases.json'
    if args.check:
        if path.read_bytes() != data:
            raise SystemExit('Normalization cases are not reproducible')
    else:
        ROOT.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


if __name__ == '__main__':
    main()
