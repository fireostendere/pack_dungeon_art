# Creature artwork

5,660 byte-preserved WebP portraits at 512 x 512 pixels cover 1,415 creatures: 4,245 normal images and 1,415 YOLO images. The 2,308-ID roster retains 893 pending entries with no available pictures.

Images, catalog shards, records, provenance, and the schema-2 resolver are in [public/assets/creature-avatars/](../public/assets/creature-avatars/). Canonical IDs and existing portable `roster-<UTF-8-hex>` filenames are unchanged. Use record paths rather than constructing paths from creature IDs.

The common [art-index.json](../art-index.json) contains only ready artwork. `metadata` points to the creature record; `provenancePath` points to the original provenance JSON, while `provenance` remains an inline object for compatibility.

The five source ZIPs remain on Drive, not duplicated in Git. 705 existing creature images and 20 location scenes matched exactly and were reused. NPC resources, location metadata and secret-layer helpers were preserved. No image was generated or re-encoded.

Validate with `python scripts/validate-creature-avatars.py` and `python scripts/validate-location-resources.py` (Python 3 and Pillow required; run without -O). Original source attribution is retained; creature references do not grant a license to publisher artwork.
