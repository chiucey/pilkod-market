// Incoming-mail presentation only. Outgoing rich-content canonicalization is independent.
const properties = new Set([
  'color', 'background-color', 'font', 'font-family', 'font-size', 'font-weight', 'font-style',
  'line-height', 'letter-spacing', 'word-spacing', 'text-align', 'text-decoration', 'text-transform',
  'white-space', 'word-break', 'overflow-wrap', 'vertical-align', 'direction',
  'width', 'height', 'min-width', 'max-width', 'min-height', 'max-height',
  'margin', 'margin-top', 'margin-right', 'margin-bottom', 'margin-left',
  'padding', 'padding-top', 'padding-right', 'padding-bottom', 'padding-left',
  'border', 'border-width', 'border-style', 'border-color', 'border-radius',
  'border-top', 'border-right', 'border-bottom', 'border-left', 'border-collapse', 'border-spacing',
  'table-layout', 'display', 'float', 'clear', 'list-style-type', 'list-style-position',
]);
export function safeMailStyle(source) {
  if (typeof source !== 'string' || source.length > 4096) return '';
  const declarations = [];
  for (const declaration of source.split(';')) {
    const colon = declaration.indexOf(':');
    if (colon < 1) continue;
    let property = declaration.slice(0, colon).trim().toLowerCase();
    const value = declaration.slice(colon + 1).trim();
    if (property === 'background') property = 'background-color';
    if (!properties.has(property) || !value || value.length > 300) continue;
    if (/url|expression|javascript|data:|var\(|attr\(|image|paint|behavior|binding|[\\{}<>@\u0000-\u001f]/iu.test(value)) continue;
    const plain = value.replace(/(?:rgb|rgba|hsl|hsla)\([\d.,%\s+-]+\)/giu, 'color').replace(/\s*!important\s*$/iu, '');
    if (!/^[\w\s#.,%'"/+\-]+$/u.test(plain)) continue;
    declarations.push(`${property}:${value}`);
  }
  return declarations.join(';');
}
export function safeMailStylesheet(source) {
  if (typeof source !== 'string' || source.length > 32768) return [];
  const result = [];
  for (const match of source.matchAll(/([^{}]+)\{([^{}]*)\}/gu)) {
    const selector = match[1].trim();
    // Simple type/class/id selectors and combinators only; no at-rules, escapes or attributes.
    if (!selector || selector.length > 300 || !/^[a-zA-Z0-9_.#\s,*>+~-]+$/u.test(selector)) continue;
    const style = safeMailStyle(match[2]);
    if (style) result.push({ selector, style });
    if (result.length === 100) break;
  }
  return result;
}
