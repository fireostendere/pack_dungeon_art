# NPC portraits and resource packs

This collection contains **120 NPC portraits** (384×384 JPEG) in two styles (80 normal, 40 YOLO). Images are stored individually in [public/assets/npc-portraits/](../public/assets/npc-portraits/) and indexed with the other artwork in [art-index.json](../art-index.json).

- [portrait-index.json](portrait-index.json) maps IDs to direct portrait paths and their archive membership.
- [npc-roster.json](npc-roster.json) contains original NPC names and game metadata.
- [packs/npc/](../packs/npc/) has the 6 original ZIP resource packs (20 portraits each).
- [previews/npc/](../previews/npc/) has the six contact-sheet previews.

All image, archive, and preview bytes are preserved. Original source: [fireostendere/pack_npc](https://github.com/fireostendere/pack_npc) at 71340a0b3cc37bebb35f623da500bddaa6b8cd5d.

## Expansion request: 2026-11-08 (planning only)

Target **50 normal portraits and 5 YOLO portraits per canonical visual race or
visually distinct subrace group**. These are target TOTALS, not 55 additional
portraits on top of the existing collection. Credit
each existing accepted portrait once to a matching quota; preserve all current
images, NPC records, packs and provenance. This update generates no art and
does not publish, merge or deploy anything.

### Verified scope and limits

The app consumes `fireostendere/pack_dungeon_art`, as verified in
`fireostendere/dungeon_master/src/lib/art/library.ts`. This section extends the
existing NPC document; the existing location queue remains
[locations/generation-plan.json](../locations/generation-plan.json).

Local app snapshot: commit `c01c978aac5b6378d87e27de86e6423664e855cb`.
`src/lib/srd/races.json` contains 32 bundled race/subrace entries. Installed
`data/content/open5e.sqlite` contains 81 race rows from wotc-srd, odm-expanded,
srd-2024, o5e and toh. Reproducing the parent-choice filtering from
`src/lib/content/race-options.ts` and `mechanics.ts` gives 74 pack options;
`src/app/characters/builder/useBuilderOptions.ts` adds missing Loxodon.
The resulting 75 rows include four duplicate bundled aliases. Normalizing these
with `src/lib/srd/race-id.ts`, while retaining separate Tome of Heroes sources,
gives **71 source-aware race/subrace entries**, listed below. Verification was
a read-only database/source audit, not a live production UI check.

The 71 entries are a source-aware inventory, NOT 71 verified distinct visual
races and NOT 71 independent portrait quotas. The **number of canonical visual
groups and the grand portrait target remain unresolved** pending appearance
deduplication. No aggregate generation budget is approved by this inventory.

Quota rule: 50 normal + 5 YOLO target totals per canonical visual race/subrace
group. Source-book, edition and mechanics aliases share the same art pool unless
a documented visual distinction justifies a separate group. In particular:

- `human` and `variant_human` share a Human visual group; mechanical variation
  alone creates no extra quota.
- Bundled `drow` and `toh:drow` remain separate rules records but must not receive
  separate quotas solely because their books differ. Reconcile their appearances
  and share the visual group unless a material distinction is documented.
- Chassis and heritage rows are components, not automatically standalone visual
  races. Group them by resulting appearance before assigning any quota.
- Other subraces may justify separate visual groups, but document recognizable
  visual differences rather than assuming every selectable option needs one.

Before generation, map every inventory ID to a stable canonicalVisualGroupId,
record the evidence and aliases, and mark unresolved mappings explicitly. Store
quota once per visual group, not once per alias. Existing portraits are credited
once to their accepted visual group; all aliases may reuse that group's pool.
User homebrew, campaign book filters and other live-server packs are outside
this local snapshot and must be reconciled without multiplying duplicate groups.

### Source-aware inventory (not a quota table)

All 71 entries and their source distinctions are retained below for traceability.
Visual grouping is a separate review; a row in this table is not a new art job.

| Inventory ID | App name |
|---|---|
| `aasimar` | Aasimar |
| `air_genasi` | Genasi (Air) |
| `bugbear` | Bugbear |
| `changeling` | Changeling |
| `deep_gnome` | Gnome (Deep) |
| `dragonborn` | Dragonborn |
| `drow` | Elf (Drow) |
| `earth_genasi` | Genasi (Earth) |
| `firbolg` | Firbolg |
| `fire_genasi` | Genasi (Fire) |
| `forest_gnome` | Gnome (Forest) |
| `goblin` | Goblin |
| `goliath` | Goliath |
| `half_elf` | Half-Elf |
| `half_orc` | Half-Orc |
| `high_elf` | Elf (High) |
| `hill_dwarf` | Dwarf (Hill) |
| `human` | Human |
| `kenku` | Kenku |
| `lightfoot_halfling` | Halfling (Lightfoot) |
| `lizardfolk` | Lizardfolk |
| `loxodon` | Loxodon |
| `mountain_dwarf` | Dwarf (Mountain) |
| `orc` | Orc |
| `rock_gnome` | Gnome (Rock) |
| `stoor_halfling` | Stoor Halfling |
| `stout_halfling` | Halfling (Stout) |
| `tabaxi` | Tabaxi |
| `tiefling` | Tiefling |
| `toh:acid_cap` | Acid Cap |
| `toh:alseid` | Alseid |
| `toh:bhain_kwai` | Bhain Kwai |
| `toh:boghaid` | Boghaid |
| `toh:catfolk` | Catfolk |
| `toh:delver` | Delver |
| `toh:derro` | Derro |
| `toh:derro_heritage` | Derro Heritage |
| `toh:dragonborn_heritage` | Dragonborn Heritage |
| `toh:drow` | Drow |
| `toh:drow_heritage` | Drow Heritage |
| `toh:dwarf_chassis` | Dwarf Chassis |
| `toh:dwarf_heritage` | Dwarf Heritage |
| `toh:elfshadow_fey_heritage` | Elf/Shadow Fey Heritage |
| `toh:erina` | Erina |
| `toh:far_touched` | Far-Touched |
| `toh:favored` | Favored |
| `toh:fever_bit` | Fever-Bit |
| `toh:gnome_chassis` | Gnome Chassis |
| `toh:gnome_heritage` | Gnome Heritage |
| `toh:halfling_heritage` | Halfling Heritage |
| `toh:human_chassis` | Human Chassis |
| `toh:humanhalf_elf_heritage` | Human/Half-Elf Heritage |
| `toh:kobold_chassis` | Kobold Chassis |
| `toh:kobold_heritage` | Kobold Heritage |
| `toh:malkin` | Malkin |
| `toh:minotaur` | Minotaur |
| `toh:morel` | Morel |
| `toh:mutated` | Mutated |
| `toh:pantheran` | Pantheran |
| `toh:purified` | Purified |
| `toh:ravenfolk` | Ravenfolk |
| `toh:satarre` | Satarre |
| `toh:shade` | Shade |
| `toh:tiefling_heritage` | Tiefling Heritage |
| `toh:trollkin_heritage` | Trollkin Heritage |
| `toh:uncorrupted` | Uncorrupted |
| `tortle` | Tortle |
| `variant_human` | Human (Variant) |
| `warforged` | Warforged |
| `water_genasi` | Genasi (Water) |
| `wood_elf` | Elf (Wood) |

### Existing portraits: separate baseline, not new jobs

At art-pack commit `2529669268c15d402bdb44a437f874ee0b701be4`, all 120 roster IDs
have NPC entries in `art-index.json`: 80 normal and 40 YOLO across 43 raw
species labels. This verifies index membership, not image hashes or visual
quality. Narrator art and generic creature portraits are not silently credited
to these NPC quotas.

| Existing species label | Normal | YOLO |
|---|---:|---:|
| aasimar | 1 | 0 |
| animated coat | 0 | 1 |
| animated skeleton | 0 | 2 |
| awakened goat | 0 | 1 |
| awakened pigeon | 0 | 1 |
| awakened spider | 0 | 1 |
| birdfolk | 1 | 0 |
| changeling | 0 | 1 |
| dragonborn | 2 | 0 |
| drow | 1 | 0 |
| dryad | 1 | 0 |
| duergar | 1 | 0 |
| dwarf | 9 | 3 |
| elf | 7 | 0 |
| fairy | 0 | 1 |
| fey | 1 | 0 |
| fiend | 0 | 1 |
| firbolg | 1 | 0 |
| genie | 0 | 1 |
| ghost | 1 | 1 |
| gnome | 6 | 2 |
| goblin | 3 | 3 |
| hag | 1 | 0 |
| half-elf | 5 | 0 |
| half-orc | 2 | 0 |
| halfling | 6 | 4 |
| hobgoblin | 2 | 0 |
| human | 16 | 7 |
| kobold | 1 | 1 |
| lich | 1 | 0 |
| lizardfolk | 1 | 0 |
| minotaur | 1 | 0 |
| orc | 2 | 2 |
| revenant | 1 | 0 |
| satyr | 0 | 1 |
| sentient cake | 0 | 1 |
| sentient puddle | 0 | 1 |
| sphinx | 1 | 0 |
| tiefling | 3 | 2 |
| tortle | 0 | 1 |
| treant | 0 | 1 |
| vampire | 1 | 0 |
| wood elf | 1 | 0 |

Before creating jobs, map each existing portrait to one justified canonical
visual group and visually review it. Generic elf/dwarf/gnome/halfling labels do
not prove a visually distinct subrace. A drow portrait need not identify a rules
source book to be shared by compatible aliases. Keep uncertain visual mappings
unresolved instead of counting them several times or assuming zero existing art.
Nonmatching
undead, awakened objects and other species remain preserved bonus NPCs.
No definitive remaining-generation count is asserted until mapping is reviewed.
Compute deficits separately: `max(0, 50 - acceptedNormal)` and
`max(0, 5 - acceptedYolo)`. Keep portraits exceeding the target.

Vary adult age, gender presentation, facial features, build, occupation, clothing,
expression, pose and lighting while retaining race-appropriate anatomy. Avoid
near-identical faces with changed accessories. YOLO keeps readable species
identity and coherent motives. Preserve originals, prompts, provenance and IDs;
review decoded images, dimensions, composition, similarity and hashes before
updating ready-art indices. Prompts, placeholders and crops are not new portraits.
