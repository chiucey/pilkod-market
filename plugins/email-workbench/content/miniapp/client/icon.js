import { icons } from './mcode-icons.js';
// Only trusted, bundled design-system assets become DOM nodes; never provider HTML.
export function icon(name, document = globalThis.document) {
  const create = ([tag, attributes, children]) => {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [key, value] of Object.entries(attributes)) node.setAttribute(key, value);
    node.append(...children.map(create));
    return node;
  };
  const svg = create(icons[name] ?? icons.mail);
  svg.setAttribute('aria-hidden', 'true');
  svg.setAttribute('focusable', 'false');
  svg.classList.add('icon');
  return svg;
}
