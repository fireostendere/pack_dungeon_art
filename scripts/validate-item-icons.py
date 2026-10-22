#!/usr/bin/env python3
"""Validate the item icon collection: manifest, records, files and index.

Every base item has three designs (01 common, 02 ornate, 03 dark), each as a
flat self-contained SVG and its 512 x 512 WebP render. Hashes and sizes in the
records and in art-index.json must match the files on disk.
"""
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

if not __debug__:
    raise RuntimeError('Run this validator without Python -O; its checks use assertions.')

ROOT = Path(__file__).resolve().parents[1]
REL = 'public/assets/item-icons'
ASSETS = ROOT / REL
STYLES = {'01': 'common', '02': 'ornate', '03': 'dark'}
GROUPS = {'weapon', 'armor', 'elixir', 'gear'}
FORBIDDEN = re.compile(r'gradient|<filter|<image|<script|<foreignObject|href=', re.I)

m = json.loads((ASSETS / 'manifest.json').read_text(encoding='utf-8'))
assert m['schemaVersion'] == 1
assert m['designsPerItem'] == 3
assert set(m['groups']) == GROUPS
assert sum(len(ids) for ids in m['groups'].values()) == len(m['items']) == m['coverage']['items']
assert m['coverage']['pending'] == 0 and m['coverage']['complete'] == len(m['items'])
assert m['coverage']['verifiedAssets'] == m['coverage']['targetAssets'] == 3 * len(m['items'])

seen = set()
by_path = {}
for item_id, entry in m['items'].items():
    assert re.fullmatch(r'[a-z]+(?:-[a-z]+)*', item_id), item_id
    assert item_id in m['groups'][entry['group']]
    assert re.search(r'[а-яё]', entry['nameRu'], re.I), f'{item_id}: Russian name'
    assert entry['record'] == f'records/{item_id}.json'
    record = json.loads((ASSETS / entry['record']).read_text(encoding='utf-8'))
    assert record['id'] == item_id and record['status'] == 'complete'
    assert record['name'] == entry['name'] and record['nameRu'] == entry['nameRu']
    assert [v['id'] for v in record['variants']] == list(STYLES)
    descriptions = set()
    for v in record['variants']:
        assert v['style'] == STYLES[v['id']]
        descriptions.add(v['description'])
        assert v['path'] == f"{item_id}/{v['id']}.webp"
        raster = (ASSETS / v['path']).read_bytes()
        assert hashlib.sha256(raster).hexdigest() == v['sha256'] and len(raster) == v['bytes'], v['path']
        assert v['sha256'] not in seen, f"{v['path']}: duplicate image"
        seen.add(v['sha256'])
        with Image.open(ASSETS / v['path']) as im:
            assert im.format == 'WEBP' and im.size == (512, 512) and im.mode == 'RGBA', v['path']
            assert im.getpixel((0, 0))[3] == 0, f"{v['path']}: transparent background"
        vec = v['vector']
        assert vec['path'] == f"{item_id}/{v['id']}.svg" and vec['viewBox'] == '0 0 64 64'
        svg = (ASSETS / vec['path']).read_bytes()
        assert hashlib.sha256(svg).hexdigest() == vec['sha256'] and len(svg) == vec['bytes'], vec['path']
        text = svg.decode('utf-8')
        assert text.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"'), vec['path']
        assert not FORBIDDEN.search(text), f"{vec['path']}: flat and self-contained"
        clips = set(re.findall(r'<clipPath id="([^"]+)"', text))
        assert set(re.findall(r'url\(#([^)]+)\)', text)) <= clips, f"{vec['path']}: undefined clip"
        by_path[f"{REL}/{v['path']}"] = (item_id, v)
    assert len(descriptions) == 3, f'{item_id}: three different designs'

on_disk = {p.relative_to(ASSETS).as_posix() for p in ASSETS.rglob('*') if p.is_file()}
expected = {'manifest.json'} | {f'records/{i}.json' for i in m['items']}
expected |= {f"{i}/{n}.{ext}" for i in m['items'] for n in STYLES for ext in ('svg', 'webp')}
assert on_disk == expected, f'unexpected or missing files: {sorted(on_disk ^ expected)[:10]}'

index = json.loads((ROOT / 'art-index.json').read_text(encoding='utf-8'))
items = [image for image in index['images'] if image['category'] == 'item']
assert len(items) == len(by_path) == index['itemImageCount'] == index['collections']['items']['verifiedAssets']
assert index['imageCount'] == len(index['images'])
assert index['imageBytes'] == sum(image['bytes'] for image in index['images'])
for image in items:
    item_id, v = by_path[image['path']]
    assert image['subjectId'] == item_id and image['variantId'] == v['id'] and image['style'] == v['style']
    assert image['sha256'] == v['sha256'] and image['bytes'] == v['bytes']
    assert image['vectorPath'] == f"{REL}/{v['vector']['path']}" and image['vectorSha256'] == v['vector']['sha256']
    assert image['metadata'] == f'{REL}/records/{item_id}.json'
    raster = (ROOT / image['path']).read_bytes()
    assert hashlib.sha1(b'blob %d\0' % len(raster) + raster).hexdigest() == image['gitBlobSha']

print(f"item icons: {len(m['items'])} items, {len(by_path)} designs, SVG and WebP verified")
