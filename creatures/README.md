# Creature artwork

5,660 byte-preserved WebP portraits at 512 x 512 pixels cover 1,415 creatures: 4,245 normal images and 1,415 YOLO images. The 2,308-ID roster retains 893 pending entries with no available pictures.

Images, catalog shards, records, provenance, and the schema-2 resolver are in [public/assets/creature-avatars/](../public/assets/creature-avatars/). Canonical IDs and existing portable `roster-<UTF-8-hex>` filenames are unchanged. Use record paths rather than constructing paths from creature IDs.

The common [art-index.json](../art-index.json) contains only ready artwork. `metadata` points to the creature record; `provenancePath` points to the original provenance JSON, while `provenance` remains an inline object for compatibility.

The five source ZIPs remain on Drive, not duplicated in Git. 705 existing creature images and 20 location scenes matched exactly and were reused. NPC resources, location metadata and secret-layer helpers were preserved. No image was generated or re-encoded.

Validate with `python scripts/validate-creature-avatars.py` and `python scripts/validate-location-resources.py` (Python 3 and Pillow required; run without -O). Original source attribution is retained; creature references do not grant a license to publisher artwork.

## Generating the pending creatures

A creature is pending when `manifest.json` has no `variantRecords` entry for it. Each creature needs four 1:1 images: `01`–`03` normal and `04` YOLO, generated with OpenAI `image_gen` and kept as originals before the 512 × 512 WebP encode (Lanczos, quality 88, method 6). Take identity, size and anatomy from the creature's bestiary entry. Use publisher pages for identity facts only. Never copy their art or prose. Write one prompt per image in this order, like the published 5,660:

1. **Use case and format.** `Use case: stylized-concept. Original square 1:1 dark-fantasy creature avatar, painterly realistic detail, readable at 512 pixels.`
2. **One subject.** Exactly ONE intact creature in ONE continuous scene. No companion, rider, prey, victim, offspring or background creature. Unshown parts are naturally occluded or out of frame, never amputated. No grid, collage, inset, repeated view, detached head or reflection double.
3. **Safe and original.** No blood, injury, severed parts, exposed tissue, feeding or attack impact. Humanoid forms are clearly adult and fully clothed. No copied publisher illustration, readable text, logo, watermark, border or UI.
4. **Identity block.** Size and name in capitals (`ONE LARGE THURSIR ARMORER`), then the anatomy with exact counts in capitals: heads, eyes, arms, legs, wings, tails, fins. Add colours and materials. Equipment is ordinary and removable. End with explicit negatives for what models tend to add (`No horns, extra arms, wings or tail`).
5. **Scene for the variant.**
   - `01` (normal): the whole creature at rest in an empty natural habitat, with every identity feature readable.
   - `02` (normal): a tight portrait of the attached head filling about 85–90 % of the square. The neck continues out of frame, and the rest of the body is out of frame, never cut off.
   - `03` (normal): the whole creature in motion (leaping, climbing, flying, swimming) in an empty habitat, with the same counts visible.
   - `04` (YOLO): absurd wordless fantasy comedy. The creature keeps its true form and a calm natural face, and the joke is one separate harmless inanimate prop. No body transformation, squeezing, text or helper.

Review every result against its prompt (identity, counts, single subject, no gore) before you add it to the catalog. Then run `python scripts/validate-creature-avatars.py`.
