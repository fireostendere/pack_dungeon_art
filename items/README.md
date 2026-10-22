# Item icons

270 inventory icons cover 90 base items: every SRD weapon (37), every SRD armour and the shield (13), ten potions and alchemical flasks, and the thirty pieces of adventuring gear a party carries most. Each item has three designs:

| Design | Style | What it is |
| --- | --- | --- |
| `01` | common | the plain, issue make |
| `02` | ornate | the better or parade make: gilding, gems, bright cloth |
| `03` | dark | the blackened, rugged or worn make |

Previews per group: [weapons](../previews/items/weapon.png), [armour](../previews/items/armor.png), [elixirs](../previews/items/elixir.png), [gear](../previews/items/gear.png).

## Files

Everything is in [public/assets/item-icons/](../public/assets/item-icons/):

- `<id>/01.svg` … `03.svg`: the source artwork. A 64 × 64 viewBox, flat cel tones under one dark outline, no gradients, filters, images or external references. Scales to any size.
- `<id>/01.webp` … `03.webp`: the same design rendered at 512 × 512 on a transparent background (Chromium, WebP lossless), for clients that need a raster.
- `records/<id>.json`: English and Russian names, group, the category plate colour the game draws it on, and each design's description, sizes, hashes and provenance.
- `manifest.json`: the item list by group, design policy, formats, coverage and the source commit.

The common [art-index.json](../art-index.json) lists every WebP with `category: "item"`, its `vectorPath`/`vectorSha256` for the SVG, `nameRu`, `group`, `style` and `description`. Use record paths rather than constructing them.

## How the game uses them

In `fireostendere/dungeon_master` an inventory line is read as a base item by its own words, by the SRD weapon or armour the rules engine resolves, or by its item kind, in English or Russian («Длинный меч», «Кольчуга», «Зелье лечения»). Which of the three designs a line wears is fixed by its inventory row, so two daggers in one pack usually look different. Plain gear, a `+1` copy of a base item and potions show the drawing on their category plate; named magic items keep their own glyph.

## Provenance and regeneration

The artwork is original procedural vector art authored for this project, not AI-generated and not derived from third-party illustrations. Its source of truth is `fireostendere/dungeon_master`:

- catalog, names and design descriptions: `src/lib/item-art/base-items.ts`;
- the drawings: `src/lib/item-art/drawings/` (`weapons.ts`, `armor.ts`, `elixirs.ts`, `gear.ts`, brushes in `kit.ts`);
- `node scripts/build-item-art.mjs` writes the SVGs, `node scripts/test-base-item-art.mjs` checks them.

To add an item, add its row and its three drawings there, rebuild, then copy the SVGs here, render the WebPs at 512 × 512 and refresh the records, manifest and index entries. The source commit of this export is in `manifest.json`.

Validate with `python scripts/validate-item-icons.py` (Python 3 and Pillow; run without `-O`).
