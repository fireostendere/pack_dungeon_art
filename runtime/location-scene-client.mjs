/** Render ONLY the server's projectScene DTO. Never import a campaign template,
 * secret state, rolls, DCs or the entire resource-pack manifest in a player view.
 * assetUrl resolves an approved asset ID to your authenticated serving endpoint.
 */
export function renderLocationScene(element, view, { assetUrl, onFeature } = {}) {
  if (!element?.ownerDocument || typeof assetUrl !== 'function') throw new TypeError('DOM element and assetUrl required');
  element.replaceChildren(); // Revoke old location/layers immediately, including after leaving a room.
  if (!view) return;
  if (view.schemaVersion !== 1 || !Number.isInteger(view.base?.width) || view.base.width <= 0
    || !Number.isInteger(view.base?.height) || view.base.height <= 0 || !Array.isArray(view.features)) {
    throw new TypeError('Invalid projected scene');
  }
  const document = element.ownerDocument;
  const frame = document.createElement('div');
  frame.style.position = 'relative';
  frame.style.width = '100%';
  frame.style.aspectRatio = `${view.base.width} / ${view.base.height}`;
  const image = (asset, alt) => {
    const node = document.createElement('img');
    node.src = assetUrl(asset);
    node.alt = alt;
    node.draggable = false;
    node.style.width = '100%';
    node.style.height = '100%';
    node.style.display = 'block';
    return node;
  };
  frame.append(image(view.base.asset, 'Location'));
  for (const feature of view.features) {
    const { x, y, width, height } = feature.bounds ?? {};
    if (![x, y, width, height].every(Number.isFinite) || x < 0 || y < 0 || width <= 0 || height <= 0
      || x + width > 1 || y + height > 1) throw new TypeError('Invalid bounds');
    const layer = document.createElement('div');
    Object.assign(layer.style, { position: 'absolute', left: `${x * 100}%`, top: `${y * 100}%`,
      width: `${width * 100}%`, height: `${height * 100}%`, pointerEvents: 'none' });
    if (feature.asset) layer.append(image(feature.asset, ''));
    if (typeof onFeature === 'function') {
      const button = document.createElement('button');
      button.type = 'button';
      button.textContent = feature.label;
      button.style.pointerEvents = 'auto';
      button.addEventListener('click', () => onFeature(feature.id));
      layer.append(button);
    }
    frame.append(layer);
  }
  element.append(frame);
}
