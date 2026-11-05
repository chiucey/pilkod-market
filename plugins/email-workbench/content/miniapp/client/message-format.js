import { t, tt } from './i18n.js';
import { safeMailStyle, safeMailStylesheet } from './mail-style.js';
import { applyLink, imagePlaceholder } from './mail-content.js';

const tags = new Set([
  'center', 'font',
  'a',
  'p',
  'div',
  'span',
  'strong',
  'b',
  'em',
  'i',
  'u',
  's',
  'h1',
  'h2',
  'h3',
  'h4',
  'ul',
  'ol',
  'li',
  'blockquote',
  'pre',
  'code',
  'br',
  'hr',
  'table',
  'thead',
  'tbody',
  'tfoot',
  'tr',
  'td',
  'th',
]);

function appendText(parent, text) {
  const document = parent.ownerDocument;
  // Hidden preheader padding loses its provider styles during sanitization.
  // Collapse only entire invisible runs; never remove characters within content.
  if (text.length > 32 && !text.replace(/[\s\u034f\u200b-\u200d\u2060\u2800\ufeff]/gu, '')) {
    parent.append(document.createTextNode(' '));
    return;
  }
  // Host replaces links with inert annotations. Long tracking URLs stay available
  // in full without overwhelming the reading view or creating navigable links.
  let offset = 0;
  for (const match of text.matchAll(/ \[链接：(https?:\/\/[^\s]+?)\]/gu)) {
    if (match[1].length <= 120) continue;
    let url;
    try {
      url = new URL(match[1]);
    } catch {
      continue;
    }
    parent.append(document.createTextNode(text.slice(offset, match.index)));
    const wrapper = document.createElement('span');
    wrapper.className = 'mail-link';
    const toggle = document.createElement('button');
    toggle.type = 'button';
    toggle.className = 'mail-link-toggle';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.textContent = tt`${url.hostname} · 展开完整链接`;
    const full = document.createElement('span');
    full.className = 'mail-link-full';
    full.textContent = match[1];
    full.hidden = true;
    toggle.addEventListener('click', () => {
      full.hidden = !full.hidden;
      toggle.setAttribute('aria-expanded', String(!full.hidden));
      toggle.textContent = `${url.hostname} · ${full.hidden ? t('展开完整链接') : t('收起链接')}`;
    });
    wrapper.append(t(' [链接：'), toggle, full, ']');
    parent.append(wrapper);
    offset = match.index + match[0].length;
  }
  parent.append(document.createTextNode(text.slice(offset)));
}

/** Construct only inert presentation nodes, even if a provider returns unexpected tokens. */
export function renderFormattedBody(formatted, options = {}) {
  const document = options.document ?? globalThis.document;
  if (
    !formatted ||
    formatted.limited ||
    !Array.isArray(formatted.tokens) ||
    formatted.tokens.length > 4000
  )
    return undefined;
  const root = document.createElement('div');
  root.className = 'formatted-message';
  const stack = [root];
  const pending = [];
  let characters = 0;
  for (const token of formatted.tokens) {
    if (!token || typeof token !== 'object') return undefined;
    if (token.type === 'text' && typeof token.text === 'string') {
      characters += token.text.length;
      if (characters > 32_000) return undefined;
      appendText(stack.at(-1), token.text);
    } else if (
      token.type === 'image' &&
      typeof token.source === 'string' &&
      typeof token.alt === 'string' &&
      token.source.length <= 2048 &&
      token.alt.length <= 500
    ) {
      const picture = imagePlaceholder(token.source, token.alt, { ...options, autoRemote: true, mailStyle: safeMailStyle(token.style), width: token.width, height: token.height }, pending);
      stack.at(-1).append(picture);
    } else if (token.type === 'open' && tags.has(token.tag)) {
      if (stack.length >= 41) return undefined;
      const node = document.createElement(token.tag);
      const style = safeMailStyle(token.style);
      if (style) node.setAttribute('style', style);
      if (typeof token.className === 'string' && /^[a-zA-Z0-9_ -]{1,300}$/u.test(token.className)) node.className = token.className;
      if (typeof token.id === 'string' && /^[a-zA-Z][a-zA-Z0-9_-]{0,99}$/u.test(token.id)) node.id = token.id;
      for (const key of ['width', 'height']) if (/^\d{1,4}%?$/u.test(token[key] ?? '')) node.setAttribute(key, token[key]);
      for (const key of ['cellPadding', 'cellSpacing', 'border']) if (Number.isInteger(token[key]) && token[key] >= 0 && token[key] <= 99) node.setAttribute(key.toLowerCase(), String(token[key]));
      if (token.tag === 'a') applyLink(node, token.href);
      if (['td', 'th'].includes(token.tag))
        for (const [key, attr] of [
          ['colspan', 'colSpan'],
          ['rowspan', 'rowSpan'],
        ]) {
          if (Number.isInteger(token[key]) && token[key] >= 1 && token[key] <= 20)
            node[attr] = token[key];
        }
      stack.at(-1).append(node);
      stack.push(node);
    } else if (
      token.type === 'close' &&
      stack.length > 1 &&
      stack.at(-1).tagName.toLowerCase() === token.tag
    )
      stack.pop();
    else return undefined;
  }
  if (stack.length !== 1 || (!root.textContent.trim() && !root.querySelector('figure'))) return undefined;
  root.ready = Promise.all(pending);
  return root;
}

/** Only this same-origin, scriptless sandbox is allowed to display incoming mail styles. */
export function renderIsolatedMessage(formatted, options = {}) {
  if (!formatted || formatted.limited || !Array.isArray(formatted.tokens)) return undefined;
  const frame = document.createElement('iframe');
  frame.className = 'mail-reader-frame';
  frame.title = t('邮件正文（安全隔离）');
  frame.setAttribute('sandbox', 'allow-same-origin');
  frame.referrerPolicy = 'no-referrer';
  frame.src = '/email/reader';
  let resize;
  let finished;
  let bodyVisible;
  let active = true;
  const unavailable = () => { if (active) { options.onUnavailable?.(); bodyVisible(); finished([]); } };
  const loadTimer = setTimeout(unavailable, 10000);
  frame.addEventListener('error', unavailable, { once: true });
  frame.bodyReady = new Promise((resolve) => { bodyVisible = resolve; });
  frame.ready = new Promise((resolve) => { finished = resolve; });
  frame.addEventListener('load', () => {
    clearTimeout(loadTimer);
    if (!active) return;
    const doc = frame.contentDocument;
    if (!doc?.body) { unavailable(); return; }
    const root = renderFormattedBody(formatted, { ...options, document: doc, imageUrl: async (source) => {
      if (!active) throw new Error('Reader closed');
      const url = await options.imageUrl?.(source);
      if (!active) throw new Error('Reader closed');
      return url;
    } });
    if (!root) { doc.body.textContent = options.text ?? t('请使用纯文本查看'); bodyVisible(); finished([]); return; }
    for (const rule of formatted.stylesheet ?? []) {
      const safe = safeMailStylesheet(`${rule.selector}{${rule.style}}`);
      if (!safe.length) continue;
      const style = doc.createElement('style');
      style.textContent = safe.map((item) => `${item.selector}{${item.style}}`).join('');
      doc.head.append(style);
    }
    doc.body.replaceChildren(doc.adoptNode(root));
    doc.addEventListener('click', (event) => {
      const link = event.target.closest?.('a[href]');
      if (!link) return;
      event.preventDefault();
      const external = document.createElement('a'); applyLink(external, link.href);
      if (external.href) { document.body.append(external); external.click(); external.remove(); }
    });
    const measure = () => { if (active) frame.style.height = `${Math.max(160, Math.min(40000, doc.body.scrollHeight + 24))}px`; };
    if (typeof ResizeObserver !== 'undefined') { resize = new ResizeObserver(measure); resize.observe(doc.body); }
    measure();
    // Reading is complete once the body is visible; images settle independently.
    bodyVisible();
    void root.ready.then((value) => { measure(); finished(value); });
  }, { once: true });
  frame.dispose = () => { clearTimeout(loadTimer); active = false; resize?.disconnect(); bodyVisible(); finished([]); };
  return frame;
}
