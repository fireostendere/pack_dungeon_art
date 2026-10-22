#!/usr/bin/env python3
"""Validate the item icon collection: manifest, records, files and index.

Every base kind has three designs (01 common, 02 ornate, 03 dark) and every
potion one, each as a flat self-contained SVG and its 512 x 512 WebP render.
Named magic items (magic/) have one picture each; the aura layers (aura/) are
SVG only. Hashes and sizes in the records, manifests and art-index.json must
match the files on disk.
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
GROUPS = {'weapon', 'armor', 'attire', 'jewelry', 'arcana', 'elixir', 'gear', 'tool', 'container', 'instrument', 'food', 'nature', 'zeitgeist'}
THEMES = {'fire', 'frost', 'storm', 'poison', 'radiant', 'necrotic', 'psychic', 'arcane', 'nature', 'water', 'air', 'earth', 'luck', 'blood'}
FORBIDDEN = re.compile(r'gradient|<filter|<image|<script|<foreignObject|href=', re.I)

m = json.loads((ASSETS / 'manifest.json').read_text(encoding='utf-8'))
assert m['schemaVersion'] == 1
assert m['designsPerItem'] == {'kinds': 3, 'potions': 1}
assert set(m['groups']) == GROUPS
assert sum(len(ids) for ids in m['groups'].values()) == len(m['items']) == m['coverage']['items']
assert m['coverage']['pending'] == 0 and m['coverage']['complete'] == len(m['items'])
assert m['coverage']['verifiedAssets'] == m['coverage']['targetAssets']

seen = set()
by_path = {}


def check_svg(vec, path=None):
    svg = (ASSETS / vec['path']).read_bytes()
    assert hashlib.sha256(svg).hexdigest() == vec['sha256'] and len(svg) == vec['bytes'], vec['path']
    check_svg_text(svg, vec['path'])


def check_svg_text(svg, name):
    text = svg.decode('utf-8')
    assert text.startswith('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"'), name
    assert not FORBIDDEN.search(text), f"{name}: flat and self-contained"
    clips = set(re.findall(r'<clipPath id="([^"]+)"', text))
    assert set(re.findall(r'url\(#([^)]+)\)', text)) <= clips, f"{name}: undefined clip"


def check_raster(rel, sha, size, unique=True):
    raster = (ASSETS / rel).read_bytes()
    assert hashlib.sha256(raster).hexdigest() == sha and len(raster) == size, rel
    if unique:
        assert sha not in seen, f"{rel}: duplicate image"
        seen.add(sha)
    with Image.open(ASSETS / rel) as im:
        assert im.format == 'WEBP' and im.size == (512, 512) and im.mode == 'RGBA', rel
        assert im.getpixel((0, 0))[3] == 0, f"{rel}: transparent background"
for item_id, entry in m['items'].items():
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', item_id), item_id
    assert item_id in m['groups'][entry['group']]
    assert re.search(r'[а-яё]', entry['nameRu'], re.I), f'{item_id}: Russian name'
    assert entry['record'] == f'records/{item_id}.json'
    record = json.loads((ASSETS / entry['record']).read_text(encoding='utf-8'))
    assert record['id'] == item_id and record['status'] == 'complete'
    assert record['name'] == entry['name'] and record['nameRu'] == entry['nameRu']
    single = entry['group'] == 'elixir'
    assert [v['id'] for v in record['variants']] == (['01'] if single else list(STYLES)), item_id
    descriptions = set()
    for v in record['variants']:
        assert v['style'] == ('single' if single else STYLES[v['id']])
        descriptions.add(v['description'])
        assert v['path'] == f"{item_id}/{v['id']}.webp"
        check_raster(v['path'], v['sha256'], v['bytes'])
        vec = v['vector']
        assert vec['path'] == f"{item_id}/{v['id']}.svg" and vec['viewBox'] == '0 0 64 64'
        check_svg(vec)
        by_path[f"{REL}/{v['path']}"] = (item_id, v)
    assert len(descriptions) == len(record['variants']), f'{item_id}: different designs'

# Named magic items: one picture each over a base kind, no artifacts.
mm = json.loads((ASSETS / m['magic']['manifest']).read_text(encoding='utf-8'))
assert mm['schemaVersion'] == 1 and set(mm['themes']) == THEMES
assert mm['count'] == len(mm['items']) == m['magic']['items']
magic_paths = {}
for slug, record in mm['items'].items():
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) and record['id'] == slug, slug
    assert record['rarity'] in {'common', 'uncommon', 'rare', 'very-rare', 'legendary'}, f'{slug}: no artifacts'
    assert record['base'] in m['items'] and record['theme'] in THEMES and record['tier'] in {1, 2, 3, 4}, slug
    assert re.search(r'[а-яё]', record['nameRu'], re.I), f'{slug}: Russian name'
    assert record['path'] == f'magic/{slug}.webp' and record['vector']['path'] == f'magic/{slug}.svg'
    # Two items of one kind, theme and rarity share their picture.
    check_raster(record['path'], record['sha256'], record['bytes'], unique=False)
    check_svg(record['vector'])
    magic_paths[f"{REL}/{record['path']}"] = record

aura = {f"aura/{t}-{n}-{layer}.svg" for t in THEMES for n in range(1, 5) for layer in ('back', 'front')}
assert m['aura']['layers'] == len(aura)
for rel in aura:
    check_svg_text((ASSETS / rel).read_bytes(), rel)

on_disk = {p.relative_to(ASSETS).as_posix() for p in ASSETS.rglob('*') if p.is_file()}
expected = {'manifest.json', m['magic']['manifest']} | {f'records/{i}.json' for i in m['items']} | aura
expected |= {f"{i}/{n}.{ext}" for i in m['items'] for n in (['01'] if m['items'][i]['group'] == 'elixir' else STYLES) for ext in ('svg', 'webp')}
expected |= {f"magic/{slug}.{ext}" for slug in mm['items'] for ext in ('svg', 'webp')}
assert on_disk == expected, f'unexpected or missing files: {sorted(on_disk ^ expected)[:10]}'

index = json.loads((ROOT / 'art-index.json').read_text(encoding='utf-8'))
magic = [image for image in index['images'] if image['category'] == 'magicItem']
assert len(magic) == len(magic_paths) == index['magicItemImageCount'] == index['collections']['magicItems']['verifiedAssets']
for image in magic:
    record = magic_paths[image['path']]
    assert image['subjectId'] == record['id'] and image['sha256'] == record['sha256'] and image['bytes'] == record['bytes']
    assert image['vectorPath'] == f"{REL}/{record['vector']['path']}" and image['vectorSha256'] == record['vector']['sha256']
    raster = (ROOT / image['path']).read_bytes()
    assert hashlib.sha1(b'blob %d\0' % len(raster) + raster).hexdigest() == image['gitBlobSha']
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

print(f"item icons: {len(m['items'])} items, {len(by_path)} designs, {len(magic_paths)} magic items, {len(aura)} aura layers; SVG and WebP verified")
