# Dungeon art library

## Google Drive location import

120 ready location images are now indexed; 100 scenes were added by this import. The full 288-archetype catalog and all previously published images are preserved. 1,247 base images remain pending. Source bytes were not re-encoded. Earlier delivery descriptions below describe the original import. This update adds static art resources only, not live gameplay integration.

## Imported collection

**5,900 ready images are available: 5,660 creature portraits, 120 NPC portraits and 120 location scenes.**
The existing-art migration is complete. The larger generation catalog still contains pending entries; these are not ready artwork.

The files are stored individually under `public/assets/`, using their original
paths. `art-index.json` lists only images that are present in this commit, with
names, variants, styles, dimensions, byte lengths and hashes.

## Artwork and source attribution

This collection contains original AI-generated artwork. Available per-image
provenance and source citation URLs are included in the index. Bestiary references
identify creatures; they do not imply a license to publisher artwork. No new
copyright or third-party artwork license is asserted by this migration.

Image bytes are unchanged from the validated source collection. The imported
delivery contains 5,660 creature portraits, 120 location scenes, and 120 NPC portraits. Original
source material and backups are preserved separately.

Source repository: `fireostendere/dungeon_master`.
- Creature source branch: `assets/creature-avatars-2026-09-30`, commit `5e1285d213c4ab91bae8fc2e6f835fe27371ff20`.
- Location source branch: `assets/location-scenes-2026-10-02`, commit `5df5771ff6f7013b77efb1835587a6b2f359608b`.

The complete imported collection is indexed in `art-index.json`. Pending catalog entries are excluded.

## NPC portraits and resource packs

120 extracted NPC portraits (80 normal, 40 YOLO) are now available individually in [public/assets/npc-portraits/](public/assets/npc-portraits/). The [NPC collection](npc/README.md) contains the character roster, mapping index, six original [ZIP resource packs](packs/npc/) and [previews](previews/npc/). Their files are cataloged in art-index.json alongside creature and location art.

## Location scenes

20 existing location illustrations have been imported without changing their bytes. The [location catalog](public/assets/location-scenes/manifest.json) preserves 288 archetypes and a target of 1,367 illustrations. This import created no new AI-generated artwork. New generation tasks and layered scene authoring are documented in [locations/](locations/README.md). Each archetype carries an authored `visualSpec` (required, optional and forbidden features, spatial layout, environment and setting), and the pending queue in `locations/generation-plan.json` builds its prompts from it; see [locations/visual-authoring.md](locations/visual-authoring.md).

## Creature portraits

5,660 individual [creature portraits](public/assets/creature-avatars/) cover 1,415 creatures, with 3 normal variants and 1 YOLO variant each. The [catalog](public/assets/creature-avatars/manifest.json) preserves all 2,308 canonical IDs; 893 remain pending. Names, variants, metadata and provenance are linked from the common index. See the [Drive import report](creatures/imports/google-drive-2026-10-12.json). How to generate the pending ones is in [creatures/README.md](creatures/README.md#generating-the-pending-creatures).
