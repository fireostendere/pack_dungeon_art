# Item icons

2,124 inventory icons, each a flat SVG with a 512 × 512 WebP render:

- **882 designs of 376 base items.** 253 kinds have three designs each, and 123 potions have one picture each.
- **1,242 named magic items**, one picture each.
- **112 aura layers**: the magic items' enchantment alone, to lay over any base design.

## Base items

| Group | Kinds | Designs | What is in it |
| --- | ---: | ---: | --- |
| `weapon` | 49 | 147 | every SRD weapon, industrial melee weapons (monoblade, chainblade, shock baton), sword-cane and the common firearms |
| `armor` | 29 | 87 | every SRD armour and the shield, modern vests and plating, helmets, great helms, coifs, gauntlets, bracers, greaves, pauldrons, gorgets, bucklers and tower shields |
| `attire` | 13 | 39 | clothes and fine clothes, cloaks, hats, hoods, gloves, boots, shoes, belts, masks, goggles, scarves, costumes |
| `jewelry` | 14 | 42 | rings and signet rings, necklaces, amulets, circlets, crowns, earrings, bracelets, brooches, gems, coins, ingots, medals, beads |
| `arcana` | 12 | 36 | staves, wands, rods, robes, wizard hats, druidic focuses, rune stones, spell scrolls, hourglasses, figurines, wings, crystal balls |
| `elixir` | 123 | 123 | every potion, elixir, oil and alchemical flask in the game, and ten custom bottles |
| `gear` | 46 | 138 | the adventuring gear a party carries most, from rope and torches to tents, saddles and banners |
| `tool` | 20 | 60 | artisan's and adventurer's kits, spyglass, compass, locks and keys, traps, pickaxe |
| `container` | 15 | 45 | sacks, barrels, buckets, jars, jugs, mugs, bowls, books, journals, letters, documents, cards, dice, chess |
| `instrument` | 10 | 30 | lute, flute, drum, horn, lyre, violin, bagpipes, tambourine, bell, gong |
| `food` | 11 | 33 | bread, cheese, fruit, berries, mushrooms, sweets, meat, sausage, ale, wine, drink |
| `nature` | 8 | 24 | herbs, flowers, incense, perfume, soap, pelts, trophies, feathers |
| `zeitgeist` | 26 | 78 | ZEITGEIST pistols, carbines, muskets, shotgun, launcher, gun mods, ammunition, firedust, grenades, and the gadgets of the age (pocket watch, camera, clockwork bird, gremlin, typewriter, newspaper) |

A kind with three designs has:

| Design | Style | What it is |
| --- | --- | --- |
| `01` | common | the plain, issue make |
| `02` | ornate | the better or parade make: gilding, gems, bright cloth |
| `03` | dark | the blackened, rugged or worn make |

A potion has a single design, `01`, style `single`: one picture for one potion, so no two potions look alike. The bottle, liquid, stopper and mark show what the potion does: red and round heals, a shield resists, a skull is poison. `custom-potion-1` … `custom-potion-10` are for potions a table invents.

## Named magic items

Every printed magic item the game knows is drawn as its base kind under an enchantment. Artifacts and one-per-world relics such as Excalibur and Mjölnir are left out.

- **Base:** the kind its name reads as; a Flame Tongue is a longsword and a Ring of Protection a ring. Cursed and dark items wear the dark design, and very rare and legendary items the ornate one.
- **Theme:** read from the name. It sets the aura's colour and its motes. There are 14 themes:

  | Theme | Motes |
  | --- | --- |
  | fire | flames |
  | frost | snowflakes |
  | storm | bolts |
  | poison | drops |
  | radiant | suns |
  | necrotic | skulls |
  | psychic | spirals |
  | arcane | sparkles |
  | nature | leaves |
  | water | bubbles |
  | air | wind |
  | earth | stones |
  | luck | clovers |
  | blood | drops |

- **Tier:** set by rarity. A higher tier adds more motes.

  | Tier | Rarity | Aura |
  | --- | --- | --- |
  | 1 | common or uncommon | a plain aura disc |
  | 2 | rare | adds a rune ring |
  | 3 | very rare | stronger again |
  | 4 | legendary | adds a second ring |

Items of one kind, theme and rarity step through mote placements and arcane hues. As a result, 1,241 of the 1,242 pictures are distinct.

## Files

Everything is in [public/assets/item-icons/](../public/assets/item-icons/).

Base items:

- `<id>/01.svg` … `03.svg`: the source artwork. A 64 × 64 viewBox, flat cel tones under one dark outline, and no gradients, filters, images or external references, so it scales to any size.
- `<id>/01.webp` … `03.webp`: the same designs rendered at 512 × 512 on a transparent background (Chromium, WebP lossless).
- `records/<id>.json`: the English and Russian names, group, category plate colour, and each design's description, sizes, hashes and provenance.

Magic items:

- `magic/<slug>.svg` and `magic/<slug>.webp`: the pictures.
- `magic/manifest.json`: each item's English and Russian names, rarity, base kind and design, theme, tier, sizes and hashes.

Aura layers:

- `aura/<theme>-<tier>-back.svg`: goes under a base design.
- `aura/<theme>-<tier>-front.svg`: goes over it.

`manifest.json` lists the base items by group, the design policy, formats, coverage and the source commit.

The common [art-index.json](../art-index.json) lists every WebP:

- base designs have `category: "item"`;
- magic items have `category: "magicItem"`;
- each entry has `vectorPath`/`vectorSha256` for its SVG, and `nameRu`.

Use the record and manifest paths rather than constructing them.

Previews are in [previews/items/](../previews/items/):

- one sheet per base group: `weapon.png`, `elixir.png`, …;
- the magic items: `magic-01.png` … `magic-08.png`.

## How the game uses them

In `fireostendere/dungeon_master`, an inventory line is read as a base item by the longest name that matches it. That name can be the line's own words, the SRD weapon or armour the rules engine resolves, or its item kind, in English or Russian: «Длинный меч», «Кольчужная рубаха», «Зелье лечения».

- **Plain gear and potions** show their drawing on the category plate. Which of the three designs a line wears is fixed by its inventory row, so two daggers in one pack usually look different.
- **A printed magic item** shows its own picture.
- **Other magic**, such as a `+1` sword or a homebrew «Пылающий топор», shows its base design between the aura layers of its theme and rarity.
- **Artifacts** keep their glyph.

## Provenance and regeneration

The artwork is original procedural vector art authored for this project. It is not AI-generated and not derived from third-party illustrations. Its source of truth is `fireostendere/dungeon_master`:

- catalog, names and design descriptions: `src/lib/item-art/base-items.ts` and `src/lib/item-art/catalog/`;
- the drawings: `src/lib/item-art/drawings/` (brushes in `kit.ts`, potions in `potions.ts`, the enchantment in `magic.ts`);
- `node scripts/build-item-art.mjs` writes the SVGs, and `node scripts/test-base-item-art.mjs` checks them.

To add an item:

1. Add its row and drawings in `fireostendere/dungeon_master` and rebuild.
2. Copy the SVGs here and render the WebPs at 512 × 512.
3. Refresh the records, manifests and index entries.

The source commit of this export is in `manifest.json`.

Validate with `python scripts/validate-item-icons.py` (Python 3 and Pillow; run without `-O`).
