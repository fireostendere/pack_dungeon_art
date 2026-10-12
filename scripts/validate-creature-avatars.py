#!/usr/bin/env python3
"""Validate actual files and honest coverage of the creature avatar registry."""
import hashlib
import json
from pathlib import Path
from PIL import Image

# Generated from avatar_identity.py; this public validator stays standalone.
"""Exact roster identities and portable path keys for the fixed 2,308-ID scope.

Canonical IDs (JSON keys and source primary keys) never change.
Only the 16 reviewed exceptions get ASCII UTF-8-hex storage names.
"""
import hashlib
import json
import re

SPECIAL_IDS = (
    "monkey's-bane-vine",
    'npc:-apostle', 'npc:-atavist', 'npc:-breathstealer',
    'npc:-cultist-psychophant', 'npc:-field-commander', 'npc:-first-servant',
    'npc:-fixer', 'npc:-frost-afflicted', 'npc:-infested-duelist',
    'npc:-infiltrator', 'npc:-merchant-captain', 'npc:-warlock-of-the-genie-lord',
    'npc:-wind-acolyte', 'púca', 'vættir-tob1-2023',
)
ROSTER_IDS_SHA256 = '1c0cdaa91c5288dbcbc9688e7a80a1a829f63bb1a803613eb538014a35282aa4'
ROSTER_IDS_SORTED_SHA256 = '09a6eefa1dad4eddd50cd0f352bc7edf30f4d87ddecf9b9cce64633d2f69bb88'


def storage_key(slug):
    if not isinstance(slug, str):
        raise ValueError('Creature ID must be a string')
    if slug in SPECIAL_IDS:
        return 'roster-' + slug.encode('utf-8').hex()
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', slug):
        raise ValueError(f'Invalid or unreviewed creature ID: {slug!r}')
    return slug


def validate_roster_ids(ids, ordered=True):
    """Pin scope and order, then reject collisions on case-insensitive filesystems."""
    if (not isinstance(ids, list) or len(ids) != 2308 or
            any(not isinstance(s, str) for s in ids) or len(set(ids)) != len(ids)):
        raise ValueError('Expected the unique 2,308-ID roster')
    values = ids if ordered else sorted(ids)
    digest = hashlib.sha256(json.dumps(values, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    if digest != (ROSTER_IDS_SHA256 if ordered else ROSTER_IDS_SORTED_SHA256):
        raise ValueError('Roster ID scope/order changed; separate identity review required')
    keys = [storage_key(s) for s in ids]
    if len({k.casefold() for k in keys}) != len(ids):
        raise ValueError('Storage-key collision')
    reserved = {'con', 'prn', 'aux', 'nul'} | {p + str(i) for p in ('com', 'lpt') for i in range(1, 10)}
    if any(k in reserved or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', k) for k in keys):
        raise ValueError('Nonportable storage key')
    return dict(zip(ids, keys))



if not __debug__:
    raise RuntimeError('Run this validator without Python -O; its checks use assertions.')

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'public/assets/creature-avatars'
m = json.loads((ASSETS / 'manifest.json').read_text(encoding='utf-8'))
assert m['schemaVersion'] == 2
assert m['variantPolicy'] == {'normal': 3, 'yolo': 1}
assert len(m['creatures']) == m['sourceRoster']['creatureCount'] == 2308
storage = validate_roster_ids(list(m['creatures']), ordered=False)
seen = set()
counts = {'complete': 0, 'partial': 0, 'pending': 0}
assets = 0
catalogs = {key: json.loads((ASSETS / path).read_text(encoding='utf-8')) for key, path in m['catalogShards'].items()}
assert set().union(*(set(c) for c in catalogs.values())) == set(m['creatures'])
assert sum(map(len, catalogs.values())) == len(m['creatures'])
assert set(m['variantRecords']).issubset(m['creatures'])
for slug, shard in m['creatures'].items():
    creature = dict(catalogs[str(shard)][slug])
    if slug in m['variantRecords']:
        assert m['variantRecords'][slug] == f'records/{storage[slug]}.json'
        creature.update(json.loads((ASSETS / m['variantRecords'][slug]).read_text(encoding='utf-8')))
    else:
        creature.update(status='pending', variants=[], modes={'normal': [], 'yolo': []})
    assert slug == creature['id']
    ids = set()
    for v in creature['variants']:
        assert v['id'] not in ids
        ids.add(v['id'])
        assert v['style'] in ('normal', 'yolo')
        assert v['path'] == f"{storage[slug]}/{v['id']}.webp"
        assert v['provenance']['promptRef'] == f"provenance/{storage[slug]}-{v['id']}.json"
        p = (ASSETS / v['path']).resolve()
        assert p.is_relative_to(ASSETS.resolve())
        b = p.read_bytes()
        h = hashlib.sha256(b).hexdigest()
        assert h == v['sha256'] and len(b) == v['bytes']
        assert h not in seen, 'Duplicate image is not a distinct variant'
        seen.add(h)
        with Image.open(p) as im:
            assert im.format == 'WEBP' and im.size == (512, 512)
            im.verify()
        assert v['mime'] == 'image/webp'
        assert (v['width'], v['height']) == (512, 512)
        provenance = (ASSETS / v['provenance']['promptRef']).resolve()
        assert provenance.is_relative_to(ASSETS.resolve())
        info = json.loads(provenance.read_text(encoding='utf-8'))
        assert info['creatureId'] == slug and info['variantId'] == v['id']
        assert info['style'] == v['style'] and info['promptStatus']
        assert 'prompt' not in info
        assert all(set(ref) == {'url'} for ref in info.get('designReferences', []))
        assets += 1
    expected_modes = {s: [v['id'] for v in creature['variants'] if v['style'] == s]
                      for s in ('normal', 'yolo')}
    assert creature['modes'] == expected_modes
    complete = all(len(expected_modes[s]) == n for s, n in m['variantPolicy'].items())
    status = 'complete' if complete else ('partial' if ids else 'pending')
    assert creature['status'] == status
    counts[status] += 1
assert m['coverage'] == dict(creatures=2308, **counts, verifiedAssets=assets, targetAssets=9232)
print(json.dumps(dict(**counts, verifiedAssets=assets, targetAssets=9232)))
