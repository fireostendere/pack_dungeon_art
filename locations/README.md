# Location art and dynamic resource packs

## Delivery status

The original catalog is preserved: **288 location archetypes**, a target of
**1,367 base illustrations**, and **20 existing images** imported from
`fireostendere/dungeon_master` without re-encoding. The remaining **1,347 images**
are pending. No new AI images or finished secret overlays were generated in this
change. The first 282 pending jobs give currently uncovered archetypes one normal
illustration each before extra variants and YOLO versions.

This repository now contains a **resource-library implementation**, not a deployed
ODM gameplay feature. The scene helpers and DOM adapter are implemented and
unit-tested. Campaign persistence, authentication, authoritative roll binding,
MCP/API wiring, spatial observations and the live game UI still need integration
in `dungeon_master`. No live campaign, server or gameplay code was modified.

## Files

- [Ready illustrations](../public/assets/location-scenes/) and their
  [full catalog](../public/assets/location-scenes/manifest.json).
- [Generation plan](generation-plan.json): all remaining base jobs, English prompts,
  priority order, delivery metadata and required review. These are tasks, NOT art.
- [Scene templates](scene-templates.json): one static template per existing image.
  Their feature arrays are empty until matching overlays are actually authored.
- [Layer authoring contract](layer-authoring.json): production requirements for
  discovered/open/disarmed patches. No missing layer is advertised as ready.
- [Server scene helpers](../runtime/location-scenes.mjs) and
  [player DOM renderer](../runtime/location-scene-client.mjs).

`art-index.json` remains the index of actual, verified files only. Generic image
paths are repository-relative; when serving the repository's `public/` directory,
remove the `public/` prefix in your approved asset URL resolver.

## What “a secret appears after a check” means

A **clean base image** depicts the normal room or landscape. It must not already
show the secret passage, a suspicious outline, a trap mechanism, hidden loot or
a marker telling players where to search. Ordinary, non-secret exits may remain.

A secret is an independent, explicitly authored feature with normalized bounds.
Its states are separate from the base and from every other secret:

1. **Undiscovered:** no feature ID, position, label, hitbox, difficulty, destination
   or overlay URL is sent to that player. The renderer receives only the base.
2. **Discovered:** a completed, applicable stored check has succeeded; the matching
   closed-panel/seam or clue layer appears only for the discovering character.
   Finding a door does NOT open it, unlock it or grant movement through it.
3. **Open / disarmed:** after the game engine resolves the relevant interaction,
   a separate localized patch depicts the changed physical state. Knowledge and
   the physical state are separate. An open passage can be visible to another
   character only when the server confirms that they actually observe it.

Individual knowledge can be explicitly shared with present allies. Another
player's successful check does not silently reveal the feature to the whole
party. Failure, a pending physical-dice entry, another actor's roll, another room,
an old timeline or a check for a different feature must not trigger a reveal.
The helpers roll no dice and never infer success from narration or a client flag.

## Artwork workflow

Generate clean base plates first. Review them before selecting overlay positions.
For each selected feature, edit the SAME composition/reference into a discovered
state and an open state. Export registered, localized RGBA patches (PNG or
alpha-preserving WebP). They must have matching perspective, material, light and
scale and cover only their authored bounds. Pixels outside the patch remain
unchanged; do not rerender the entire room during a reveal.

The feature's `bounds` use fractions of the base image:
`{ "x": 0.25, "y": 0.3, "width": 0.1, "height": 0.4 }`.
Coordinates above are illustrative, not a real secret placement. Array order is
paint order. Avoid overlapping secret patches unless their composition has been
reviewed together. Separate features avoid generating all combinations of secrets.
Do not apply one generic doorway patch across unrelated camera angles.

Template shape (authoring draft, not ready art):

```json
{
  "schemaVersion": 1,
  "id": "example-scene",
  "base": {
    "asset": "public/assets/location-scenes/dungeon-chamber/normal-01.webp",
    "width": 1536,
    "height": 864
  },
  "features": [{
    "id": "stone-panel",
    "kind": "secret-passage",
    "label": "Stone panel",
    "bounds": { "x": 0.25, "y": 0.3, "width": 0.1, "height": 0.4 },
    "discovery": {
      "skills": ["perception", "investigation"],
      "dc": 15,
      "allowPassive": false
    },
    "art": {}
  }]
}
```

The difficulty and skills are illustrative campaign settings, not universal D&D
rules. Fill `art.discovered` and `art.open` only with real, reviewed patch files.
A draft with empty art can expose a known feature label but is NOT a finished
visual reveal. Do not list drafts as completed dynamic scenes.

## ODM integration boundary — still to implement in the game

Keep actual campaign templates and feature placements in **server-private state**.
The public Git repository contains reusable resources, not a campaign's secrets.
Hiding DOM elements with CSS, omitting a tooltip, or naming a file “secret” is not
an access-control mechanism. Public generic assets are browseable; access-controlled
campaign manifests and private feature-to-location bindings are still required.

The host adapter must authenticate the viewer and derive campaign, room, actor,
epoch, ally membership and observed features from authoritative spatial state.
None of `context`, `template`, `state`, role, DC, recipients or visibility may be
trusted merely because it arrived in a client request. A player searches through
normal game actions; they do not supply a hidden feature ID to enumerate secrets.

Before requesting a discovery roll through the existing dice flow, persist its
binding to campaign, location, timeline epoch, actor, feature, purpose, skill and
DC. `discoverFromRoll` loads a stored roll by ID through an injected resolver; it
accepts only resolved, correctly scoped records. Pending results remain pending;
failed results are consumed without revealing. Passive resolution requires an
explicit feature policy and a real server-recorded result. Do not expose the
private resolver response or internal feature failure details to the player.

Store the returned state with **compare-and-swap on the original revision**, in
one transaction with roll consumption. If two requests race, reread and reapply
the SAME roll ID after a CAS failure. Do not request another roll. The pure helper
cannot itself guarantee database durability or concurrency. Timeline restoration
must change the authoritative epoch to invalidate old proofs.

For opening, lock picking, disabling a trap or dispelling an illusion, adjudicate
all needed checks/resources first. Only the trusted game adapter may call
`setPhysicalState`. A DM role string supplied by a browser is not authorization.
Synchronize physical passages with the actual battle map, collision, LOS and
location connectivity; this art helper does not alter movement or map terrain.
Persist witnessed discoveries explicitly if knowledge should survive later LOS
loss or closing the door. This is separate from transient `observedFeatureIds`.

After every state change, compute `projectScene` separately for each authorized
viewer. Apply the same filtering to HTTP, SSE, reconnect/replay, exports, memories,
chat and media URLs; do not broadcast one global secret-bearing payload. Do not
include global revision counters that reveal another player's hidden discoveries.
Use viewer-scoped/no-store caching for private projections. Never preload the
undiscovered or future-state assets into the player DOM. Remove the previous view
immediately when leaving a room, as the renderer does for a null projection.
The `onFeature` callback submits a normal player action, not a local reveal.

## Verification and generation handoff

```sh
python scripts/plan-location-scenes.py
python scripts/plan-location-scenes.py --check
python scripts/validate-location-resources.py
node --test tests/location-scenes.test.mjs tests/location-scene-client.test.mjs
```

Validation requires Pillow; runtime helpers use only standard JavaScript.
The test suite covers private projections, stored-roll scope, passive policy,
pending/failure, replay, separate discoveries, sharing, physical-state separation,
timeline boundaries, serialization, path/geometry validation and DOM replacement.
DOM tests use a minimal contract fixture; they are **not** full-browser E2E or
visual acceptance tests. The finished game still needs multi-user browser tests.

A generation-capable session/backend should consume the pending plan in order,
keep originals, decode and visually review outputs, update byte lengths, dimensions,
SHA-256 and provenance, then publish images and consistent indices in batches of
20. Rebuild the queue after each accepted batch. Preserve existing creature/NPC
assets. Do not use GitHub Actions or automatically charge an external image API.
There is no background image-generation job running as part of this delivery.
