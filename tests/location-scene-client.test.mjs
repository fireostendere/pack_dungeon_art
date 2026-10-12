import test from 'node:test';
import assert from 'node:assert/strict';
import { renderLocationScene } from '../runtime/location-scene-client.mjs';
// DOM contract tests, not browser E2E/visual tests.
function dom() {
  const document = { createElement(tag) { return { tag, ownerDocument: document, style: {}, children: [],
    append(...nodes) { this.children.push(...nodes); },
    replaceChildren(...nodes) { this.children = nodes; },
    addEventListener(event, handler) { this[event] = handler; } }; } };
  return document.createElement('section');
}
const view = () => ({ schemaVersion: 1, locationId: 'room',
  base: { asset: 'base.webp', width: 1536, height: 864 }, features: [] });
test('renderer requests only the projected assets, never hidden or future phases', () => {
  const root = dom(); const requests = [];
  renderLocationScene(root, view(), { assetUrl(path) { requests.push(path); return `/authorized/${path}`; } });
  assert.deepEqual(requests, ['base.webp']);
  assert.equal(root.children[0].style.aspectRatio, '1536 / 864');
  assert.equal(root.children[0].children.length, 1);
});
test('revoking the view removes stale layers immediately', () => {
  const root = dom(); renderLocationScene(root, view(), { assetUrl: (p) => p });
  renderLocationScene(root, null, { assetUrl: (p) => p });
  assert.deepEqual(root.children, []);
});
test('discovered layer stays aligned and labels are text rather than HTML', () => {
  const root = dom(); const input = view();
  input.features.push({ id: 'panel', label: '<img src=x onerror=alert(1)>', phase: 'discovered',
    asset: 'seam.webp', bounds: { x: .2, y: .3, width: .1, height: .4 } });
  let clicked = null;
  renderLocationScene(root, input, { assetUrl: (p) => p, onFeature: (id) => clicked = id });
  const overlay = root.children[0].children[1];
  assert.equal(overlay.style.left, '20%'); assert.equal(overlay.style.width, '10%');
  const button = overlay.children[1]; assert.equal(button.textContent, input.features[0].label);
  assert.equal(button.innerHTML, undefined); button.click(); assert.equal(clicked, 'panel');
});
test('malformed new state does not leave the old room on screen', () => {
  const root = dom(); renderLocationScene(root, view(), { assetUrl: (p) => p });
  assert.throws(() => renderLocationScene(root, {}, { assetUrl: (p) => p }));
  assert.deepEqual(root.children, []);
});
