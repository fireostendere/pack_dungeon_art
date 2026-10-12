import test from 'node:test';
import assert from 'node:assert/strict';
import { validateTemplate, createSceneState, projectScene, discoverFromRoll, shareDiscovery,
  setPhysicalState } from '../runtime/location-scenes.mjs';

// Synthetic TEST FIXTURE ONLY. Overlay paths here are not shipped art.
const template = () => ({ schemaVersion: 1, id: 'sample-room',
  base: { asset: 'public/assets/location-scenes/dungeon-chamber/normal-01.webp', width: 1536, height: 864 },
  features: [{ id: 'concealed-panel', kind: 'secret-passage', label: 'Stone panel',
    destinationLocationId: 'private-room-b', bounds: { x: 0.4, y: 0.3, width: 0.1, height: 0.4 },
    discovery: { skills: ['perception', 'investigation'], dc: 15, allowPassive: false },
    art: { discovered: 'public/assets/location-layers/test/panel-seam.webp',
      open: 'public/assets/location-layers/test/panel-open.webp' } }] });
const context = (actorId = 'alice', extra = {}) => ({ authorized: true, role: 'player', actorId,
  campaignId: 'campaign-a', locationId: 'room-a', timelineEpoch: 'epoch-1', ...extra });
const dm = () => context('dm', { role: 'dm' });
const stateFor = (t) => createSceneState(t, context());
const proof = (extra = {}) => ({ id: 'roll-1', actorId: 'alice', campaignId: 'campaign-a', locationId: 'room-a',
  timelineEpoch: 'epoch-1', featureId: 'concealed-panel', purpose: 'discover', skill: 'perception',
  dc: 15, kind: 'ability-check', status: 'resolved', total: 18, ...extra });
const discover = (t, s, p = proof(), c = context()) => discoverFromRoll(t, s,
  { featureId: 'concealed-panel', rollId: p.id }, c, async () => p);

test('unrevealed player DTO contains no secret material, even nested extra base metadata', () => {
  const t = template(); t.base.debug = { secret: 'leak' };
  const view = projectScene(t, stateFor(t), context());
  assert.deepEqual(view.features, []);
  for (const value of ['concealed-panel', 'Stone panel', 'private-room-b', 'seam', 'roll-', 'dc', 'debug', 'leak', 'revision']) {
    assert.ok(!JSON.stringify(view).includes(value), value);
  }
});

test('successful stored check reveals only to its actor and only the discovered asset', async () => {
  const t = template(); const s = stateFor(t); const snapshot = JSON.stringify(s);
  const result = await discover(t, s);
  assert.equal(result.outcome, 'discovered');
  assert.equal(JSON.stringify(s), snapshot);
  assert.deepEqual(projectScene(t, result.state, context('bob')), projectScene(t, s, context('bob')));
  const alice = projectScene(t, result.state, context());
  assert.equal(alice.features[0].phase, 'discovered');
  assert.ok(alice.features[0].asset.endsWith('panel-seam.webp'));
  assert.ok(!JSON.stringify(alice).includes('panel-open'));
  assert.equal(result.state.features['concealed-panel'].phase, 'closed');
});

test('failed check does not reveal and is consumed, not rerolled by this library', async () => {
  const t = template(); const s = stateFor(t);
  const result = await discover(t, s, proof({ total: 14 }));
  assert.equal(result.outcome, 'failed');
  assert.deepEqual(projectScene(t, s, context()), projectScene(t, result.state, context()));
  assert.deepEqual(result.state.consumedRollIds, ['roll-1']);
});

test('unresolved checks stay pending and can resolve later with the same ID', async () => {
  const t = template(); const s = stateFor(t);
  const pending = await discover(t, s, proof({ status: 'pending', total: undefined }));
  assert.equal(pending.outcome, 'pending'); assert.deepEqual(pending.state, s);
  assert.equal((await discover(t, pending.state)).outcome, 'discovered');
});

test('replaying an applied roll is idempotent and never re-reads/rerolls', async () => {
  const t = template(); const first = await discover(t, stateFor(t));
  const replay = await discoverFromRoll(t, first.state, { featureId: 'concealed-panel', rollId: 'roll-1' },
    context(), () => { throw Error('must not load again'); });
  assert.equal(replay.outcome, 'duplicate'); assert.deepEqual(replay.state, first.state);
});

for (const [field, value] of Object.entries({ id: 'other', campaignId: 'campaign-b', locationId: 'room-b',
  actorId: 'bob', timelineEpoch: 'epoch-0', featureId: 'another-panel', purpose: 'attack', skill: 'athletics', dc: 1 })) {
  test(`rejects a roll with mismatched ${field}`, async () => {
    const t = template(); const p = proof({ [field]: value });
    await assert.rejects(discoverFromRoll(t, stateFor(t), { featureId: 'concealed-panel', rollId: 'roll-1' },
      context(), async () => p), /not applicable/);
  });
}

test('a forged request success flag cannot replace a persisted roll', async () => {
  const t = template();
  await assert.rejects(discoverFromRoll(t, stateFor(t), { featureId: 'concealed-panel', rollId: 'x', success: true, total: 999 },
    context(), async () => null), /not applicable/);
});

test('passive checks require explicit policy and the same stored scope binding', async () => {
  const t = template(); const p = proof({ kind: 'passive-check' });
  await assert.rejects(discover(t, stateFor(t), p), /not applicable/);
  t.features[0].discovery.allowPassive = true;
  assert.equal((await discover(t, stateFor(t), p)).outcome, 'discovered');
});

test('invalid totals and cancelled rolls do not change state', async () => {
  const t = template();
  for (const p of [proof({ total: NaN }), proof({ total: Infinity }), proof({ total: '30' }), proof({ status: 'cancelled' })]) {
    await assert.rejects(discover(t, stateFor(t), p), /not resolved/);
  }
});

test('explicit knowledge sharing affects only authorized present allies', async () => {
  const t = template(); const { state } = await discover(t, stateFor(t));
  const shared = shareDiscovery(t, state, 'concealed-panel', ['bob'], context('alice', { presentAllyIds: ['bob'] }));
  assert.equal(projectScene(t, shared, context('bob')).features.length, 1);
  assert.equal(projectScene(t, shared, context('eve')).features.length, 0);
  assert.throws(() => shareDiscovery(t, state, 'concealed-panel', ['eve'], context('alice', { presentAllyIds: ['bob'] })));
  assert.throws(() => shareDiscovery(t, state, 'concealed-panel', ['eve'], context('bob', { presentAllyIds: ['eve'] })));
});

test('discovery does not grant physical open permissions', async () => {
  const t = template(); const { state } = await discover(t, stateFor(t));
  assert.throws(() => setPhysicalState(t, state, 'concealed-panel', 'open', context()), /Forbidden/);
  const open = setPhysicalState(t, state, 'concealed-panel', 'open', dm());
  assert.equal(projectScene(t, open, context()).features[0].phase, 'open');
  assert.deepEqual(projectScene(t, open, context('bob')).features, []);
  const observer = projectScene(t, open, context('bob', { observedFeatureIds: ['concealed-panel'] }));
  assert.equal(observer.features[0].phase, 'open');
  assert.ok(!JSON.stringify(observer).includes('panel-seam'));
});

test('location, campaign, epoch and membership boundaries fail closed', async () => {
  const t = template(); const s = stateFor(t);
  for (const invalid of [{ authorized: false }, { campaignId: 'other' }, { locationId: 'other' },
    { timelineEpoch: 'other' }, { role: 'administrator' }, { actorId: '' }]) {
    const c = context('alice', invalid);
    assert.equal(projectScene(t, s, c), null);
    await assert.rejects(discover(t, s, proof(), c), /Forbidden/);
  }
});

test('serialization retains personal discoveries and consumed-roll protection', async () => {
  const t = template(); const { state } = await discover(t, stateFor(t));
  const restored = JSON.parse(JSON.stringify(state));
  assert.deepEqual(projectScene(t, restored, context()), projectScene(t, state, context()));
  assert.equal((await discover(t, restored)).outcome, 'duplicate');
});

test('multiple secrets are independent; finding one exposes no data for another', async () => {
  const t = template(); const second = structuredClone(t.features[0]);
  second.id = 'another-panel'; second.label = 'Second secret'; t.features.push(second);
  const { state } = await discover(t, stateFor(t));
  assert.equal(projectScene(t, state, context()).features.length, 1);
  assert.ok(!JSON.stringify(projectScene(t, state, context())).includes('another-panel'));
});

test('DM sees secret positions but player DTO still excludes destinations and difficulty', () => {
  const t = template(); assert.equal(projectScene(t, stateFor(t), dm()).features.length, 1);
});

test('template validation rejects unsafe URLs, bad geometry, duplicate IDs and numeric IDs', () => {
  for (const asset of ['https://evil/door.webp', 'public/assets/location-layers/../secret.webp',
    'public/assets/location-layers/%2e%2e/secret.webp', 'javascript:alert(1)', '/tmp/secret.webp']) {
    const t = template(); t.features[0].art.open = asset;
    assert.throws(() => validateTemplate(t), /Invalid overlay/);
  }
  const duplicate = template(); duplicate.features.push(structuredClone(duplicate.features[0]));
  assert.throws(() => validateTemplate(duplicate), /Duplicate/);
  const malformed = template(); malformed.features[0].bounds.width = 2;
  assert.throws(() => validateTemplate(malformed), /bounds/);
  const numeric = template(); numeric.features[0].id = 1;
  assert.throws(() => validateTemplate(numeric), /invalid feature/);
});

test('template/state identity mismatch cannot silently reveal a different room', () => {
  const t = template(); const s = stateFor(t); t.id = 'different-template';
  assert.throws(() => projectScene(t, s, context()), /identity/);
});

test('unfinished overlays are not silently substituted with another phase image', async () => {
  const t = template(); delete t.features[0].art.discovered;
  const { state } = await discover(t, stateFor(t));
  assert.equal(projectScene(t, state, context()).features[0].asset, null);
});

test('disarming is restricted to traps and repeated physical state is idempotent', () => {
  const t = template(); const s = stateFor(t);
  assert.throws(() => setPhysicalState(t, s, 'concealed-panel', 'disarmed', dm()), /traps/);
  assert.deepEqual(setPhysicalState(t, s, 'concealed-panel', 'closed', dm()), s);
});
