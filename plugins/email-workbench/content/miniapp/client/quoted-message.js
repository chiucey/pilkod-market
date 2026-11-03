import { t, tt } from './i18n.js';
import { safeLink } from './mail-content.js';

const escape = (value) =>
  String(value ?? '').replace(
    /[&<>"']/gu,
    (char) =>
      ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      })[char],
  );
const plainHtml = (text) => `<p>${escape(text).replace(/\n/gu, '<br>')}</p>`;
const TAGS = new Set(
  'a p div span strong b em i u s h1 h2 h3 h4 ul ol li blockquote pre code br hr table thead tbody tfoot tr td th'.split(
    ' ',
  ),
);
const failure = (code) => {
  throw Object.assign(new Error(code), { code });
};

/** Prepare a complete quote before opening the composer. Never truncate or silently omit an attachment. */
export async function prepareQuotedMessage(
  message,
  kind,
  { api, date, signature = '', signatureHtml, signatureAttachments = [] },
) {
  const heading = tt`${kind === 'forward' ? t('转发邮件') : t('原邮件')}\n发件人：${message.from.join(', ')}\n收件人：${message.to.join(', ')}\n时间：${date(message.timestampMs)}\n主题：${message.subject}`;
  if (`${signature}\n\n${heading}\n\n${message.text}`.length > 200000) failure('QUOTE_TOO_LARGE');
  const formatted =
    message.formattedBody && !message.formattedBody.limited ? message.formattedBody : undefined;
  const required = new Set(
    (formatted?.tokens ?? [])
      .filter((token) => token.type === 'image' && token.source.startsWith('cid:'))
      .map((token) => decodeURIComponent(token.source.slice(4))),
  );
  for (const id of required)
    if (message.attachments.filter((asset) => asset.contentId === id).length !== 1)
      failure('QUOTE_IMAGE_MISSING');
  const originals = message.attachments.filter(
    (asset) => kind === 'forward' || required.has(asset.contentId),
  );
  if (
    originals.length + signatureAttachments.length > 10 ||
    originals.some((asset) => asset.bytes > 10 * 1024 * 1024)
  )
    failure('QUOTE_ATTACHMENTS_TOO_LARGE');
  const attachments = [...signatureAttachments];
  const inline = new Map();
  for (const asset of originals) {
    const saved = await api('attachments/import', { ref: message.ref, index: asset.index });
    attachments.push(saved);
    if (asset.contentId) inline.set(asset.contentId, saved.id);
  }
  let remoteImages = 0;
  let original = plainHtml(message.text);
  if (formatted)
    original = formatted.tokens
      .map((token) => {
        if (token.type === 'text') return escape(token.text);
        if (token.type === 'image') {
          if (token.source.startsWith('cid:')) {
            const id = inline.get(decodeURIComponent(token.source.slice(4)));
            if (!id) failure('QUOTE_IMAGE_MISSING');
            return `<img src="cid:${id}@email-workbench" alt="${escape(token.alt)}">`;
          }
          const href = safeLink(token.source);
          remoteImages += 1;
          return href
            ? `<p><a href="${escape(href)}">${escape(token.alt || t('原邮件外部图片'))}</a></p>`
            : '';
        }
        if (!TAGS.has(token.tag)) return '';
        if (token.type === 'close')
          return ['br', 'hr'].includes(token.tag) ? '' : `</${token.tag}>`;
        let attrs =
          token.tag === 'a' && safeLink(token.href)
            ? ` href="${escape(safeLink(token.href))}"`
            : '';
        if (['td', 'th'].includes(token.tag))
          for (const name of ['colspan', 'rowspan'])
            if (Number.isInteger(token[name]) && token[name] > 0 && token[name] <= 20)
              attrs += ` ${name}="${token[name]}"`;
        return `<${token.tag}${attrs}>`;
      })
      .join('');
  const html = `${signatureHtml ?? plainHtml(signature || '')}<p><br></p><blockquote>${plainHtml(heading)}${original}</blockquote>`;
  if (html.length > 512 * 1024) failure('QUOTE_TOO_LARGE');
  return { html, text: `${signature}\n\n${heading}\n\n${message.text}`, attachments, remoteImages };
}
