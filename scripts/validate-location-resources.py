#!/usr/bin/env python3
"""Validate actual files and catalog/queue agreement. Requires Pillow for decoding."""
from __future__ import annotations
import hashlib
import json
from collections import Counter
from pathlib import Path, PurePosixPath
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def asset_path(raw: str) -> Path:
    path = PurePosixPath(raw)
    require(not path.is_absolute() and '..' not in path.parts and '\\' not in raw, f'Unsafe path: {raw}')
    resolved = (ROOT / raw).resolve()
    require(resolved.is_relative_to(ROOT), f'Escaping path: {raw}')
    return resolved


def main() -> None:
    index = load('art-index.json')
    manifest = load('public/assets/location-scenes/manifest.json')
    plan = load('locations/generation-plan.json')
    images = {entry['path']: entry for entry in index['images']}
    require(len(images) == len(index['images']) == index['imageCount'], 'Duplicate/mismatched global image count')
    totals = Counter(entry['category'] for entry in images.values())
    for category, count in totals.items():
        require(index.get(category + 'ImageCount') == count, f'{category} count mismatch')
    byte_total = 0
    for name, entry in images.items():
        path = asset_path(name)
        require(path.is_file(), f'Missing artwork: {name}')
        data = path.read_bytes()
        require(len(data) == entry['bytes'], f'Byte length mismatch: {name}')
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], f'SHA256 mismatch: {name}')
        if 'gitBlobSha' in entry:
            blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\x00' + data).hexdigest()
            require(blob == entry['gitBlobSha'], f'Git blob mismatch: {name}')
        with Image.open(path) as image:
            image.load()
            require(image.size == (entry['width'], entry['height']), f'Dimensions mismatch: {name}')
            require(Image.MIME.get(image.format) == entry['mime'], f'Format mismatch: {name}')
        byte_total += len(data)
    require(byte_total == index['imageBytes'], 'Global byte count mismatch')
    expected, ready = set(), set()
    statuses = Counter()
    target_by_style = Counter()
    for key, location in manifest['locations'].items():
        total = sum(location['targetVariants'].values())
        for style, count in location['targetVariants'].items():
            target_by_style[style] += count
            expected.update(f'{key}/{style}-{number:02d}' for number in range(1, count + 1))
        actual = len(location['variants'])
        status = 'pending' if not actual else 'complete' if actual == total else 'partial'
        require(location['status'] == status, f'Wrong coverage status for {key}')
        statuses[status] += 1
        for variant in location['variants']:
            item_id = f'{key}/{variant["id"]}'
            require(item_id in expected and item_id not in ready, f'Invalid or duplicate variant {item_id}')
            ready.add(item_id)
            name = f'public/assets/location-scenes/{variant["path"]}'
            require(name in images and images[name]['category'] == 'location', f'Unindexed scene: {name}')
            require(images[name]['sha256'] == variant['sha256'], f'Catalog hash mismatch: {name}')
    coverage = manifest['coverage']
    require(len(manifest['locations']) == coverage['locationTypes'], 'Location-type count mismatch')
    require(len(ready) == coverage['verifiedAssets'] == totals['location'], 'Ready scene count mismatch')
    require(len(expected) == coverage['targetAssets'], 'Target scene count mismatch')
    require(dict(target_by_style) == coverage['targetByStyle'], 'Style targets mismatch')
    for key, count in statuses.items():
        require(coverage[key] == count, f'Coverage {key} mismatch')
    pending = {job['id'] for job in plan['jobs']}
    require(len(pending) == len(plan['jobs']) == plan['pendingBaseImageCount'], 'Duplicate or mismatched queue count')
    require(pending == expected - ready, 'Queue does not exactly cover missing base images')
    require(plan['readyBaseImageCount'] == len(ready) and plan['targetBaseImageCount'] == len(expected), 'Stale queue header')
    for job in plan['jobs']:
        require(job['status'] == 'pending' and not asset_path(job['output']['path']).exists(), f'Phantom pending job: {job["id"]}')
    templates = load('locations/scene-templates.json')
    require(len(templates['templates']) == len(ready), 'Ready template count mismatch')
    require(templates['integrationStatus'] == 'resource-library-only', 'Do not claim gameplay integration')
    for template in templates['templates']:
        require(template['base']['asset'] in images, f'Missing template base {template["id"]}')
        for feature in template['features']:
            for value in feature['art'].values():
                require(asset_path(value).is_file(), f'Missing feature artwork: {value}')
    print(json.dumps({'verifiedImages': len(images), 'categoryCounts': dict(totals), 'verifiedBytes': byte_total,
                      'locationTypes': len(manifest['locations']), 'pendingBaseImages': len(pending),
                      'authoredSecretFeatures': sum(len(t['features']) for t in templates['templates']),
                      'gameplayIntegrated': False}))


if __name__ == '__main__':
    main()
