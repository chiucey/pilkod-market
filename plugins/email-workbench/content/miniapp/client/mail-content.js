import { t } from './i18n.js';
import { icon } from './icon.js';

const TAGS = new Set([
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
  'a',
]);
export function safeLink(value) {
  if (typeof value !== 'string' || value.length > 2048 || /[\u0000-\u0020\u007f]/u.test(value))
    return undefined;
  try {
    const url = new URL(value);
    if (['http:', 'https:', 'mailto:'].includes(url.protocol) && !url.username && !url.password)
      return url.href;
  } catch {
    /* Invalid links remain text. */
  }
}
export function applyLink(node, href) {
  const url = safeLink(href);
  if (url) {
    node.href = url;
    node.target = '_blank';
    node.rel = 'noopener noreferrer';
    node.title = url;
  }
}
export function imagePlaceholder(source, alt, options, pending) {
  const document = options.document ?? globalThis.document;
  const figure = document.createElement('figure');
  figure.className = 'mail-image';
  figure.dataset.workbenchImage = 'true';
  figure.dataset.state = 'idle';
  const controls = document.createElement('figcaption'); controls.className = 'mail-image-controls';
  const identity = document.createElement('span'); identity.className = 'mail-image-identity';
  const status = document.createElement('strong'); status.setAttribute('role', 'status');
  const description = document.createElement('span'); description.textContent = alt || t('邮件图片');
  identity.append(status, description);
  const load = document.createElement('button'); load.type = 'button';
  load.className = 'mail-image-retry'; load.append(icon('refresh', document));
  const label = document.createElement('span'); load.append(label);
  const inline = source.startsWith('cid:');
  const setState = (state, text, action) => {
    figure.dataset.state = state; status.textContent = text; label.textContent = action;
    load.setAttribute('aria-label', `${action}：${alt || t('邮件图片')}`);
  };
  setState('idle', inline ? t('内嵌图片尚未加载') : t('外部图片尚未加载'), t('加载图片'));
  controls.append(icon('image', document), identity, load); figure.append(controls);
  const show = async () => {
    load.disabled = true;
    controls.hidden = false;
    setState('loading', inline ? t('正在加载内嵌图片…') : t('正在加载邮件图片…'), t('加载中…'));
    try {
      const url = await options.imageUrl?.(source);
      if (!url?.startsWith('blob:')) throw new Error('Unavailable');
      const img = document.createElement('img');
      img.alt = alt || t('邮件图片');
      img.src = url;
      if (options.mailStyle) img.setAttribute('style', options.mailStyle);
      for (const key of ['width', 'height']) if (/^\d{1,4}%?$/u.test(options[key] ?? '')) img.setAttribute(key, options[key]);
      img.addEventListener(
        'error',
        () => {
          img.remove();
          controls.hidden = false;
          load.disabled = false;
          setState('failed', t('图片未能显示'), t('重试'));
        },
        { once: true },
      );
      figure.querySelector('img')?.remove();
      figure.prepend(img);
      // A resolved download is not a painted image. Keep the reader pending until decoding succeeds.
      if (img.decode) {
        let timeout;
        try {
          await Promise.race([
            img.decode(),
            new Promise((_, reject) => {
              timeout = setTimeout(() => reject(new Error('Image timeout')), 15000);
            }),
          ]);
        } finally {
          clearTimeout(timeout);
        }
      }
      controls.hidden = true;
      figure.dataset.state = 'ready';
      return true;
    } catch {
      figure.querySelector('img')?.remove();
      controls.hidden = false;
      setState('failed', t('图片未能加载'), t('重试'));
      return false;
    } finally {
      load.disabled = false;
    }
  };
  load.addEventListener('click', () => {
    void show();
  });
  if ((inline || options.autoRemote) && options.imageUrl) pending.push(show());
  else if (!inline) {
    const url = safeLink(source);
    if (url) {
      const host = document.createElement('small');
      host.textContent = new URL(url).hostname;
      identity.append(host);
    }
  }
  return figure;
}

/** Rebuild the bounded canonical draft as allowlisted DOM; never insert source HTML into the page. */
export function renderDraftBody(content, options = {}) {
  if (!content.html || content.html.length > 512 * 1024) {
    const plain = document.createElement('pre');
    plain.className = 'message-body';
    plain.textContent = content.text || t('（空正文）');
    return plain;
  }
  const parsed = new DOMParser().parseFromString(content.html, 'text/html');
  const root = document.createElement('div');
  root.className = 'formatted-message';
  const pending = [];
  let count = 0;
  const copy = (from, to, depth) => {
    if (++count > 20000 || depth > 40) throw new Error('Body limit');
    if (from.nodeType === 3) {
      to.append(document.createTextNode(from.textContent));
      return;
    }
    if (from.nodeType !== 1) return;
    const tag = from.tagName.toLowerCase();
    if (tag === 'img') {
      const source = from.getAttribute('src') ?? '';
      if (/^cid:[0-9a-f-]{36}@email-workbench$/u.test(source))
        to.append(imagePlaceholder(source, from.getAttribute('alt') ?? '', options, pending));
      return;
    }
    if (!TAGS.has(tag)) return;
    const node = document.createElement(tag);
    if (tag === 'a') applyLink(node, from.getAttribute('href'));
    if (['left', 'center', 'right'].includes(from.getAttribute('align')))
      node.setAttribute('align', from.getAttribute('align'));
    if (tag === 'td' || tag === 'th')
      for (const name of ['colspan', 'rowspan']) {
        const value = Number(from.getAttribute(name));
        if (Number.isInteger(value) && value > 0 && value <= 20)
          node.setAttribute(name, String(value));
      }
    to.append(node);
    for (const child of from.childNodes) copy(child, node, depth + 1);
  };
  try {
    for (const child of parsed.body.childNodes) copy(child, root, 0);
  } catch {
    root.replaceChildren();
    const plain = document.createElement('pre');
    plain.className = 'message-body';
    plain.textContent = content.text;
    root.append(plain);
  }
  root.ready = Promise.all(pending);
  return root;
}
