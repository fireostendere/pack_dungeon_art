#!/usr/bin/env python3
"""Build a deterministic pending-art queue. No generation, network calls or git pushes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / 'public/assets/location-scenes/manifest.json'
OUTPUT = ROOT / 'locations/generation-plan.json'
NORMAL_BRIEFS = [
    'Classic, grounded version of this location; balanced establishing composition and clear functional layout.',
    'A visibly well-kept version with refined craftsmanship; asymmetrical wide composition and soft directional light.',
    'A timeworn but still usable version, with repairs and local material textures; quiet, subdued atmosphere.',
    'An austere, practical version with spare details; use depth and contrasting foreground silhouettes.',
    'A grander interpretation with imposing scale appropriate to the archetype; layered atmospheric depth.',
    'A modest, intimate interpretation appropriate to the archetype; rich surfaces and restrained details.',
    'An old version shaped by generations of use; material patina and accumulated ordinary objects tell its history.',
    'An isolated or quiet version; unusual but believable wide viewpoint and a strong readable central focal area.',
    'A carefully restored or renewed version; convincing construction, subtle ornament and clear sightlines.',
    'A dramatic version with stronger light-and-shadow contrast; retain the same recognizable fantasy archetype.',
]
YOLO_BRIEFS = [
    'One tiny, ordinary location-appropriate object has its own absurdly grand throne or pedestal; everything else stays believable.',
    'An unnecessary miniature copy of this very location is carefully maintained inside the scene as though it were important.',
    'A large location-appropriate statue solemnly performs a mundane chore using an absurdly small tool.',
    'An ordinary inanimate location-appropriate object has been given a lavish ceremonial waiting area and velvet ropes.',
]
COMMON = (
    'One cohesive cinematic hand-painted fantasy environment illustration, wide establishing view, 16:9. '
    'Believable materials, perspective, scale and lighting; readable large forms with atmospheric depth. '
    'No prominent party, named characters, text, labels, grids, UI, collage, borders, logos or watermark. '
    'The location is the subject. Match its description; do not replace it with a generic room. '
    'Produce a clean initial-state base plate: no indicated concealed door, suspicious seam, visible trap mechanism, '
    'treasure hint, marked hiding place, revealed secret corridor or unexplained glowing clue. '
    'Ordinary doors and exits explicitly appropriate to the archetype may remain visible. '
    'Where the environment permits, retain some unobstructed ordinary surface for later authored localized overlays, '
    'without highlighting that surface or implying a secret. Do not bake any actual campaign secrets into the image.'
)
NEGATIVE = ('readable writing, labels, watermark, logo, UI, grid, collage, panels, split view, '
            'obvious concealed door, outlined secret panel, exposed trap, treasure marker, inconsistent perspective')


def build(catalog: dict) -> dict:
    jobs = []
    ready = []
    frequency_rank = {'very_common': 0, 'common': 1, 'regular': 2, 'uncommon': 3, 'rare': 4}
    for location_id, location in catalog['locations'].items():
        generated = {variant['id'] for variant in location['variants']}
        ready.extend(f'{location_id}/{variant}' for variant in generated)
        for style in ('normal', 'yolo'):
            for number in range(1, location['targetVariants'][style] + 1):
                variant_id = f'{style}-{number:02d}'
                if variant_id in generated:
                    continue
                brief = (NORMAL_BRIEFS if style == 'normal' else YOLO_BRIEFS)[number - 1]
                phase = 'coverage-first' if style == 'normal' and number == 1 else 'normal-variety' if style == 'normal' else 'yolo-variety'
                art_direction = catalog['artDirection'][style]
                prompt = (f'{COMMON}\nLocation: {location["name"]}.\n'
                          f'Environment: {location["description"]}\n'
                          f'Art direction: {art_direction}\nVariant direction: {brief}\n'
                          'Adapt the variation to this location; do not add indoor furniture to an outdoor landscape '
                          'unless the location description explicitly calls for it.\n'
                          'Delivery target: 1536 by 864 pixels. Keep the original output before WebP encoding.')
                jobs.append({'id': f'{location_id}/{variant_id}', 'status': 'pending',
                             'stage': phase, 'locationId': location_id, 'locationName': location['name'],
                             'category': location['category'], 'frequency': location['frequency'],
                             'variantId': variant_id, 'style': style, 'variantBrief': brief,
                             'prompt': prompt, 'negativePrompt': NEGATIVE,
                             'output': {'path': f'public/assets/location-scenes/{location_id}/{variant_id}.webp',
                                        'width': 1536, 'height': 864, 'mime': 'image/webp', 'quality': 88},
                             'requiredReview': ['file-decodes', 'dimensions', 'sha256', 'visual-quality',
                                                'location-match', 'no-secret-spoilers']})
    stages = {'coverage-first': 0, 'normal-variety': 1, 'yolo-variety': 2}
    jobs.sort(key=lambda job: (stages[job['stage']], frequency_rank[job['frequency']], job['locationId'], job['variantId']))
    return {'schemaVersion': 1, 'language': 'en', 'catalogPath': CATALOG.relative_to(ROOT).as_posix(),
            'status': 'planned-not-generated', 'batchSize': 20,
            'readyBaseImageCount': len(ready), 'targetBaseImageCount': catalog['coverage']['targetAssets'],
            'pendingBaseImageCount': len(jobs), 'coverageFirstJobCount': sum(job['stage'] == 'coverage-first' for job in jobs),
            'generationPolicy': 'Never count a prompt, placeholder, crop or imported image as a new AI generation. '
                                'Publish only decoded and visually approved images; update the catalog atomically with each batch.',
            'layerPolicy': 'Author feature layers only after selecting and reviewing a base. Match camera, materials, '
                           'light and exact normalized bounds. Keep all campaign-specific secret state server-side. '
                           'Layer tasks are not part of the base-image counts.',
            'jobs': jobs}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the checked-in queue is stale; do not write files')
    args = parser.parse_args()
    plan = build(json.loads(CATALOG.read_text(encoding='utf-8')))
    serialized = json.dumps(plan, ensure_ascii=False, indent=2) + '\n'
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8') != serialized:
            raise SystemExit('Generation plan is stale. Run scripts/plan-location-scenes.py.')
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(serialized, encoding='utf-8')
    print(json.dumps({key: value for key, value in plan.items() if key.endswith('Count')}))


if __name__ == '__main__':
    main()
