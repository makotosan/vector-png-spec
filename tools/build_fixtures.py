"""Deterministic tiny PNG fixtures; no renderer or third-party dependency."""
import argparse
import base64
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
KEY = b'vector-png.svg'
SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1"><rect width="1" height="1" fill="red"/></svg>'


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)


def zpack(data):
    # One stored DEFLATE block: stable bytes across operating systems/zlib versions.
    if len(data) > 65535:
        raise ValueError('Fixture is too large for one stored block')
    return b'\x78\x01\x01' + struct.pack('<HH', len(data), len(data) ^ 65535) + data + struct.pack('>I', zlib.adler32(data) & 0xffffffff)


def source_chunk(raw, flag=1, method=0, language=b'', translated=b''):
    prefix = KEY + b'\0' + bytes([flag, method]) + language + b'\0' + translated + b'\0'
    return chunk(b'iTXt', prefix + (zpack(raw) if flag else raw))


def png(metadata, pixel=b'\xff\0\0\xff', after=False):
    head = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0))
    raster = chunk(b'IDAT', zpack(b'\0' + pixel))
    return head + (raster + metadata if after else metadata + raster) + chunk(b'IEND', b'')


def vectors():
    raw = SVG.encode()
    good = source_chunk(raw)
    cases = []

    def add(name, data, valid, reason, source=None):
        item = dict(name=name, png_base64=base64.b64encode(data).decode(),
                    container_valid=valid, reason=reason)
        if valid:
            item['source_base64'] = base64.b64encode(raw if source is None else source).decode()
        cases.append(item)

    add('basic', png(good), True, 'One red pixel and its SVG source')
    add('source-after-idat', png(good, after=True), True, 'iTXt may follow IDAT')
    add('language-fields', png(source_chunk(raw, language=b'ja', translated='SVG ソース'.encode())), True, 'Valid non-empty text fields')
    bom = b'\xef\xbb\xbf' + raw
    add('utf8-bom', png(source_chunk(bom)), True, 'Preserve BOM bytes on extraction', bom)
    escaped = raw.replace(b'<rect', b'<title>A &amp; B</title><!-- <?inert?> --><rect')
    add('escaped-and-comment', png(source_chunk(escaped)), True, 'XML escaping and inert comments are allowed', escaped)
    add('different-preview', png(good, pixel=b'\0\0\xff\xff'), True, 'Container-valid; red SVG versus blue raster. Preview NOT verified')
    inert = raw.replace(b'<rect', b'<script>/* inert test data */</script><rect')
    add('unsafe-svg', png(source_chunk(inert)), True, 'Container-valid but MUST be rejected by safe-svg-v1 before rendering', inert)
    add('missing-source', png(b''), False, 'No source')
    add('duplicate-source', png(good + good), False, 'Ambiguous source')
    add('wrong-chunk-type', png(chunk(b'tEXt', KEY + b'\0' + raw)), False, 'iTXt required')
    add('uncompressed', png(source_chunk(raw, flag=0)), False, 'Compression flag must be 1')
    add('wrong-method', png(source_chunk(raw, method=1)), False, 'Compression method must be 0')
    add('trailing-zlib', png(chunk(b'iTXt', KEY + b'\0\1\0\0\0' + zpack(raw) + b'junk')), False, 'Trailing compressed data')
    add('invalid-utf8', png(source_chunk(b'\xff')), False, 'UTF-8 required')
    add('wrong-root', png(source_chunk(b'<svg/>')), False, 'SVG namespace required')
    add('dtd', png(source_chunk(b'<!DOCTYPE svg><svg xmlns="http://www.w3.org/2000/svg"/>')), False, 'DTD forbidden')
    add('processing-instruction', png(source_chunk(b'<?test inert?>' + raw)), False, 'PI forbidden')
    add('wrong-xml-encoding', png(source_chunk(b'<?xml version="1.0" encoding="ISO-8859-1"?>' + raw)), False, 'Conflicting declared encoding')
    add('apng-marker', png(good + chunk(b'acTL', struct.pack('>II', 1, 0))), False, 'Animation marker forbidden')
    add('trailing-file-data', png(good) + b'junk', False, 'Trailing file data')
    bad = bytearray(png(good)); bad[-1] ^= 1
    add('bad-crc', bytes(bad), False, 'Invalid CRC')
    return dict(spec='wire-v1-draft-0.1', fixtures=cases)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    text = json.dumps(vectors(), ensure_ascii=False, indent=2) + '\n'
    target = ROOT / 'fixtures/vectors.json'
    if args.check:
        if target.read_text(encoding='utf-8') != text:
            raise SystemExit('Fixture catalog differs; regenerate and review changes')
        print('Fixture catalog is reproducible')
    else:
        target.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
