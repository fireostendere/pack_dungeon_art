/** Server-side scene projection helpers. This is NOT an HTTP authorization layer.
 * Templates, state, identity, membership, observation and rolls must be loaded
 * by the trusted game server. Never pass a player-supplied template/context/roll.
 */
const SLUG = /^[a-z0-9][a-z0-9-]{0,95}$/;
const ASSET = /^public\/assets\/location-(?:scenes|layers)\/(?:[a-z0-9][a-z0-9-]*\/)*[a-z0-9][a-z0-9-]*\.(?:webp|png|jpg)$/;
const PHASES = ['closed', 'open', 'disarmed'];
const KINDS = ['secret-passage', 'trap', 'cache', 'clue', 'illusion'];
const copy = (value) => structuredClone(value);
const requireValue = (condition, message) => { if (!condition) throw new Error(message); };
const key = (value) => typeof value === 'string' && value.length > 0 && value.length <= 200;
const owns = (object, name) => Object.hasOwn(object, name);

export function validateTemplate(template) {
  requireValue(template?.schemaVersion === 1 && typeof template.id === 'string' && SLUG.test(template.id), 'Invalid template');
  requireValue(ASSET.test(template.base?.asset ?? ''), 'Invalid base asset');
  requireValue(Number.isInteger(template.base.width) && template.base.width > 0 && template.base.width <= 8192,
    'Invalid image width');
  requireValue(Number.isInteger(template.base.height) && template.base.height > 0 && template.base.height <= 8192,
    'Invalid image height');
  requireValue(Array.isArray(template.features) && template.features.length <= 64, 'Invalid features');
  const seen = new Set();
  for (const feature of template.features) {
    requireValue(typeof feature?.id === 'string' && SLUG.test(feature.id) && !seen.has(feature.id), 'Duplicate or invalid feature');
    seen.add(feature.id);
    requireValue(KINDS.includes(feature.kind), 'Invalid feature kind');
    requireValue(typeof feature.label === 'string' && feature.label.length > 0 && feature.label.length <= 100,
      'Invalid feature label');
    const { x, y, width, height } = feature.bounds ?? {};
    requireValue([x, y, width, height].every(Number.isFinite) && x >= 0 && y >= 0 && width > 0 && height > 0
      && x + width <= 1 && y + height <= 1, 'Invalid normalized bounds');
    const rule = feature.discovery;
    requireValue(Number.isInteger(rule?.dc) && rule.dc >= 0 && rule.dc <= 100, 'Invalid discovery DC');
    requireValue(Array.isArray(rule.skills) && rule.skills.length > 0
      && rule.skills.every((skill) => ['perception', 'investigation', 'arcana'].includes(skill)), 'Invalid discovery skills');
    requireValue(typeof rule.allowPassive === 'boolean', 'Explicit passive-check policy required');
    requireValue(feature.art && typeof feature.art === 'object' && !Array.isArray(feature.art), 'Missing feature art');
    for (const [phase, asset] of Object.entries(feature.art)) {
      requireValue(['discovered', 'open', 'disarmed'].includes(phase) && ASSET.test(asset), 'Invalid overlay asset');
    }
    // A hotspot without art is a supported authoring draft, not a finished overlay.
    if (feature.destinationLocationId !== undefined) requireValue(key(feature.destinationLocationId), 'Invalid destination');
  }
  return template;
}

export function createSceneState(template, { campaignId, locationId, timelineEpoch }) {
  validateTemplate(template);
  requireValue(key(campaignId) && key(locationId) && key(timelineEpoch), 'Invalid scene identity');
  return { schemaVersion: 1, templateId: template.id, campaignId, locationId, timelineEpoch,
    revision: 0, consumedRollIds: [], features: Object.fromEntries(template.features.map((feature) =>
      [feature.id, { phase: 'closed', discoveredBy: [] }])) };
}

function validateState(template, state) {
  validateTemplate(template);
  requireValue(state?.schemaVersion === 1 && state.templateId === template.id && key(state.campaignId)
    && key(state.locationId) && key(state.timelineEpoch), 'Invalid state identity');
  requireValue(Number.isSafeInteger(state.revision) && state.revision >= 0, 'Invalid revision');
  requireValue(Array.isArray(state.consumedRollIds) && state.consumedRollIds.every(key), 'Invalid roll ledger');
  requireValue(state.features && Object.keys(state.features).length === template.features.length, 'Invalid state features');
  for (const feature of template.features) {
    const value = owns(state.features, feature.id) ? state.features[feature.id] : null;
    requireValue(value && PHASES.includes(value.phase) && Array.isArray(value.discoveredBy)
      && value.discoveredBy.every(key), 'Invalid feature state');
  }
}

// Context is constructed from server authentication and spatial membership,
// NOT deserialized from a client body or trusted because it says "dm".
function authorized(state, context) {
  return context?.authorized === true && key(context.actorId)
    && ['player', 'dm'].includes(context.role)
    && context.campaignId === state.campaignId && context.locationId === state.locationId
    && context.timelineEpoch === state.timelineEpoch;
}

/** Apply only a completed, persisted check that was requested for this feature.
 * loadRoll resolves a roll ID through the authoritative dice store. Pending and
 * failed checks do not reveal art; completed failures are consumed too. Persist
 * result.state with a compare-and-swap on the ORIGINAL revision in one DB txn.
 */
export async function discoverFromRoll(template, state, { featureId, rollId }, context, loadRoll) {
  validateState(template, state);
  requireValue(authorized(state, context), 'Forbidden');
  requireValue(typeof loadRoll === 'function' && key(rollId), 'A stored roll is required');
  const feature = template.features.find((entry) => entry.id === featureId);
  requireValue(feature, 'Check is not applicable');
  if (state.consumedRollIds.includes(rollId)) return { outcome: 'duplicate', state: copy(state) };
  const roll = await loadRoll(rollId);
  const rule = feature.discovery;
  requireValue(roll?.id === rollId && roll.campaignId === state.campaignId && roll.locationId === state.locationId
    && roll.timelineEpoch === state.timelineEpoch && roll.actorId === context.actorId
    && roll.featureId === featureId && roll.purpose === 'discover' && rule.skills.includes(roll.skill)
    && roll.dc === rule.dc, 'Check is not applicable');
  requireValue(roll.kind === 'ability-check' || (roll.kind === 'passive-check' && rule.allowPassive), 'Check is not applicable');
  if (roll.status === 'pending') return { outcome: 'pending', state: copy(state) };
  requireValue(roll.status === 'resolved' && Number.isFinite(roll.total), 'Check is not resolved');
  const next = copy(state);
  next.revision += 1;
  next.consumedRollIds.push(rollId);
  const passed = roll.total >= rule.dc;
  if (passed && !next.features[featureId].discoveredBy.includes(context.actorId)) {
    next.features[featureId].discoveredBy.push(context.actorId);
  }
  return { outcome: passed ? 'discovered' : 'failed', state: next };
}

/** Explicit sharing; recipients are validated by the server as present allies. */
export function shareDiscovery(template, state, featureId, recipients, context) {
  validateState(template, state);
  requireValue(authorized(state, context), 'Forbidden');
  const current = owns(state.features, featureId) ? state.features[featureId] : null;
  requireValue(current?.discoveredBy.includes(context.actorId), 'Feature is not known');
  requireValue(Array.isArray(recipients) && recipients.length > 0 && recipients.length <= 100
    && recipients.every((id) => key(id) && context.presentAllyIds?.includes(id)), 'Invalid sharing recipients');
  const next = copy(state);
  next.features[featureId].discoveredBy = [...new Set([...current.discoveredBy, ...recipients])];
  if (next.features[featureId].discoveredBy.length !== current.discoveredBy.length) next.revision += 1;
  return next;
}

/** World state, separate from knowledge. Call only AFTER interaction/lock/trap
 * adjudication by the game server. Discovery alone never opens a passage.
 * This resource helper does NOT authorize movement or alter battle-map terrain.
 */
export function setPhysicalState(template, state, featureId, phase, context) {
  validateState(template, state);
  requireValue(authorized(state, context) && context.role === 'dm', 'Forbidden');
  requireValue(owns(state.features, featureId) && PHASES.includes(phase), 'Invalid feature transition');
  const feature = template.features.find((entry) => entry.id === featureId);
  requireValue(phase !== 'disarmed' || feature.kind === 'trap', 'Only traps can be disarmed');
  const next = copy(state);
  if (next.features[featureId].phase !== phase) next.revision += 1;
  next.features[featureId].phase = phase;
  return next;
}

/** A player-safe DTO: no unrevealed IDs, bounds, labels, DCs, destinations, full
 * art maps, discovery ledgers or global revisions. Do not transmit the template.
 * Observed features come from server visibility/line-of-sight, never the client.
 */
export function projectScene(template, state, context) {
  validateState(template, state);
  if (!authorized(state, context)) return null;
  const features = [];
  for (const feature of template.features) {
    const current = state.features[feature.id];
    const observed = current.phase !== 'closed' && context.observedFeatureIds?.includes(feature.id);
    if (context.role !== 'dm' && !current.discoveredBy.includes(context.actorId) && !observed) continue;
    const phase = current.phase === 'closed' ? 'discovered' : current.phase;
    features.push({ id: feature.id, label: feature.label, phase, bounds: copy(feature.bounds),
      // Never send another state's asset as a preload hint. Missing art stays null.
      asset: feature.art[phase] ?? null });
  }
  return { schemaVersion: 1, locationId: state.locationId, base: { asset: template.base.asset, width: template.base.width, height: template.base.height }, features };
}
