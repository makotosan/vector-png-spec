"""Fixture sanity checker, NOT a general PNG decoder or full conformance oracle."""
import re
import struct
import xml.etree.ElementTree as ET
import zlib


class NoActiveXML(ET.TreeBuilder):
    def doctype(self, *args):
        raise ValueError('DTD forbidden')

    def pi(self, *args):
        raise ValueError('Processing instructions forbidden')


def extract_source(data):
    if len(data) > 32_000_000 or data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Invalid PNG signature or file size')
    pos, chunks, sources = 8, [], []
    while pos + 12 <= len(data):
        size, = struct.unpack_from('>I', data, pos)
        kind = data[pos + 4:pos + 8]
        end = pos + 8 + size
        if end + 4 > len(data):
            raise ValueError('Truncated chunk')
        raw = data[pos + 8:end]
        crc, = struct.unpack_from('>I', data, end)
        if zlib.crc32(kind + raw) & 0xffffffff != crc:
            raise ValueError('Bad CRC')
        chunks.append((kind, raw))
        if kind in {b'acTL', b'fcTL', b'fdAT'}:
            raise ValueError('APNG forbidden')
        if kind in {b'iTXt', b'tEXt', b'zTXt'} and raw.split(b'\0', 1)[0] == b'vector-png.svg':
            if kind != b'iTXt':
                raise ValueError('Source must use iTXt')
            rest = raw[len(b'vector-png.svg') + 1:]
            if rest[:2] != b'\1\0':
                raise ValueError('Wrong compression fields')
            language, translated, compressed = rest[2:].split(b'\0', 2)
            if language and not re.fullmatch(rb'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', language):
                raise ValueError('Invalid fixture language tag')
            translated.decode('utf-8')
            dec = zlib.decompressobj()
            source = dec.decompress(compressed, 1_000_001)
            if len(source) > 1_000_000 or not dec.eof or dec.unused_data:
                raise ValueError('Invalid or excessive compressed source')
            sources.append(source)
        pos = end + 4
        if kind == b'IEND':
            if size or pos != len(data):
                raise ValueError('Invalid PNG ending')
            break
    kinds = [kind for kind, _ in chunks]
    if not kinds or kinds[0] != b'IHDR' or kinds[-1] != b'IEND' or kinds.count(b'IHDR') != 1 or b'IDAT' not in kinds:
        raise ValueError('Missing or duplicate structural chunks')
    # Deliberately limited to this catalog's 1x1 RGBA8, filter-0 fixture raster.
    if chunks[0][1] != struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0):
        raise ValueError('Not the supported fixture raster')
    raster_dec = zlib.decompressobj()
    raster = raster_dec.decompress(b''.join(raw for kind, raw in chunks if kind == b'IDAT'), 6)
    if len(raster) != 5 or raster[0] != 0 or not raster_dec.eof or raster_dec.unused_data:
        raise ValueError('Invalid fixture raster')
    if len(sources) != 1:
        raise ValueError('Expected one source')
    source = sources[0]
    text = source.decode('utf-8-sig')
    if '\0' in text:
        raise ValueError('NUL forbidden')
    declaration = re.match(r'^<\?xml\s+([^?]*)\?>', text)
    if declaration:
        encoding = re.search(r'encoding\s*=\s*[\'"]([^\'"]+)', declaration[1])
        if encoding and encoding[1].lower() != 'utf-8':
            raise ValueError('Conflicting XML encoding')
    root = ET.fromstring(text, parser=ET.XMLParser(target=NoActiveXML()))
    if root.tag != '{http://www.w3.org/2000/svg}svg':
        raise ValueError('Wrong root')
    return source
