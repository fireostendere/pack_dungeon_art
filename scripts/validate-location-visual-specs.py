#!/usr/bin/env python3
"""Validate authored location visual specs; optionally verify original data preservation.

This does not inspect image pixels. Run validate-location-resources.py separately
in a checkout containing the WebP assets to validate their bytes and dimensions.
"""
import argparse
import copy
import json
import re
from pathlib import Path


def load_unique(path):
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, f'Duplicate JSON key: {key}'
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs)


def validate(manifest, baseline=None):
    contract = manifest['visualAuthoring']
    assert contract['schemaVersion'] == 1
    assert contract['scope'] == 'reusable-archetypes-not-campaign-canon'
    assert contract['campaignAdaptation']['binding'] is None
    assert 'does not integrate' in contract['consumerStatus']
    assert 'do not certify' in contract['existingArtwork']
    assert len(manifest['locations']) == manifest['sourceRoster']['locationCount']
    prompts, layouts, paths = set(), set(), set()
    for slug, location in manifest['locations'].items():
        assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug), slug
        spec = location['visualSpec']
        assert spec['scope'] == 'authored-normal-archetype-default', slug
        for field, minimum, maximum in [('requiredFeatures', 2, 4), ('optionalFeatures', 1, 3), ('forbiddenFeatures', 2, 4)]:
            values = spec[field]
            assert isinstance(values, list) and minimum <= len(values) <= maximum, (slug, field)
            assert all(isinstance(x, str) and x.strip() for x in values), (slug, field)
            assert len(values) == len(set(values)), (slug, field)
        assert not set(spec['requiredFeatures']) & set(spec['forbiddenFeatures']), slug
        for field in ['spatialLayout', 'environmentalConstraints', 'settingConstraints', 'imageSafePrompt']:
            assert isinstance(spec[field], str) and len(spec[field]) >= 20, (slug, field)
        prompt = spec['imageSafePrompt']
        assert location['name'] in prompt and manifest['artDirection']['normal'] in prompt, slug
        for feature in spec['requiredFeatures'] + spec['forbiddenFeatures']:
            assert feature in prompt, (slug, feature)
        for field in ['spatialLayout', 'environmentalConstraints', 'settingConstraints']:
            assert spec[field] in prompt, (slug, field)
        assert '16:9' in prompt and 'hidden features' in prompt, slug
        assert not re.search(r'\{\{|\}\}|\b(?:TODO|TBD|INSERT_HERE)\b', prompt), slug
        assert prompt not in prompts and spec['spatialLayout'] not in layouts, slug
        prompts.add(prompt)
        layouts.add(spec['spatialLayout'])
        for variant in location['variants']:
            path = variant['path']
            assert path not in paths and path.startswith(slug + '/'), (slug, path)
            assert '..' not in Path(path).parts and not Path(path).is_absolute(), path
            # Drive-imported variants carry a description but no original prompt.
            assert variant['description'], path
            paths.add(path)
    if baseline is not None:
        # Preserve every pre-existing field, including concurrent variants and metadata.
        stripped = copy.deepcopy(manifest)
        del stripped['visualAuthoring']
        for location in stripped['locations'].values():
            del location['visualSpec']
        assert stripped == baseline, 'Existing manifest data changed'
    return {'locations': len(prompts), 'uniqueLayouts': len(layouts), 'variantReferences': len(paths), 'baselinePreserved': baseline is not None}


def self_test(manifest):
    slug = next(iter(manifest['locations']))
    mutations = [
        lambda m: m['locations'][slug]['visualSpec'].update(requiredFeatures=[]),
        lambda m: m['locations'][slug]['visualSpec'].update(imageSafePrompt='TODO'),
        lambda m: m['locations'][slug]['visualSpec'].update(scope='campaign-canon'),
        lambda m: m['visualAuthoring']['campaignAdaptation'].update(binding='invented-campaign'),
    ]
    for mutate in mutations:
        broken = copy.deepcopy(manifest)
        mutate(broken)
        try:
            validate(broken)
        except (AssertionError, KeyError, TypeError):
            continue
        raise AssertionError('Validator accepted a malformed fixture')
    return len(mutations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', nargs='?', type=Path, default=Path(__file__).resolve().parents[1] / 'public/assets/location-scenes/manifest.json')
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    manifest = load_unique(args.manifest)
    result = validate(manifest, load_unique(args.baseline) if args.baseline else None)
    if args.self_test:
        result['rejectedMalformedFixtures'] = self_test(manifest)
    print(json.dumps(result))
