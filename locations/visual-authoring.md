# Location visual authoring

The existing manifest schema is preserved. `visualAuthoring` and each location's
`visualSpec` are additive, opt-in authoring metadata for the external image
operator/narrator. No application runtime, asset selection or renderer is wired
up by this change.

## Generate a reusable normal scene

`locations/generation-plan.json` already folds each archetype's spec into its job
prompts (`scripts/plan-location-scenes.py`): normal jobs get the required
features, spatial relationships, environment, setting and exclusions; YOLO jobs
keep the required features and spatial relationships so the place stays
recognizable. For a one-off normal scene outside the plan:

Read `visualSpec.imageSafePrompt` for the selected location. It includes the
shared normal art direction and the location's authored essentials, spatial
relationships, environmental conditions, setting limits and exclusions. It
intentionally omits optional landmarks and does not assert a campaign identity.
`optionalFeatures` lists compatible proposals; choose them deliberately rather
than silently adding everything. Required features describe the normal catalog
default, not every possible depiction in every campaign.

Before generating a campaign-specific scene, resolve the public setting, visible
geography, door counts/connections, era/culture/materials, season/time/weather
and any requested visible inhabitants. Public campaign facts take precedence;
choose another archetype if its defining features are incompatible. Freeze an
approved public layout and visual palette for future views. Do not fill unknowns
with a named castle, river, faction or secret passage. Keep GM-only notes, trap
solutions and future outcomes out of image-model input.

## Existing variants and YOLO

Existing variant records and image files are not rewritten. Their full
description, tags, lighting and mood describe those particular assets, including
incidental landmarks. `provenance.prompt` remains the historical request, not an
editable current description. A forest image containing a river and a ruined
castle cannot be assumed to match every forest scene.

New visual constraints are prospective. Previous `review.visual: passed` results
do not certify that those assets meet the newly added constraints. Inspect the
actual image and reconcile its complete content with the intended scene before
selecting it; retain fallback if no compatible image exists.

For YOLO, require explicit tone selection and a visible original comic twist.
Use `artDirection.yolo`, the recognizable location structure and the chosen
variant's description (or an explicitly authored new twist). Reconcile deliberate
departures from normal exclusions one by one. Do not merely reuse the normal
prompt and label its result YOLO. Do not use a private story fact as the joke.

## Validation

Run `python3 scripts/validate-location-visual-specs.py --self-test` for all entries,
feature types, uniqueness, assembled prompt completeness and malformed-fixture
rejections. Optional `--baseline /path/to/previous-manifest.json` verifies that
removing only the new fields recovers the previous manifest exactly, including
all variants, hashes and provenance. Use a fresh baseline when generation has
added assets concurrently.

The visual-spec validator does not inspect pixels or prove campaign correctness.
Run the existing `python3 scripts/validate-location-resources.py` in a full checkout
to verify WebP hashes, sizes, dimensions and coverage. Neither script replaces
human/image review of visible content.
