import { t } from './i18n.js';
const MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024;
const IMAGE_TYPES = new Set(['image/png', 'image/jpeg', 'image/gif', 'image/webp']);

export function createAttachmentAccess({ api, sha256, el, notice }) {
  const urls = new Map();
  const transientUrls = new Set();
  let disposed = false;
  async function read(id) {
    const chunks = [];
    let offset = 0;
    let metadata;
    do {
      const part = await api('attachments/read', { id, offset });
      metadata ??= part;
      if (
        part.id !== id ||
        part.sha256 !== metadata.sha256 ||
        part.bytes !== metadata.bytes ||
        part.bytes > MAX_ATTACHMENT_BYTES ||
        part.offset !== offset
      )
        throw Object.assign(new Error('Invalid attachment'), { code: 'INVALID_RESPONSE' });
      const chunk = Uint8Array.from(atob(part.contentBase64), (char) => char.charCodeAt(0));
      if (
        chunk.length !== part.nextOffset - offset ||
        part.nextOffset > part.bytes ||
        (part.nextOffset === offset && offset < part.bytes)
      )
        throw Object.assign(new Error('Invalid attachment'), { code: 'INVALID_RESPONSE' });
      chunks.push(chunk);
      offset = part.nextOffset;
    } while (offset < metadata.bytes);
    const content = new Uint8Array(metadata.bytes);
    let position = 0;
    for (const chunk of chunks) {
      content.set(chunk, position);
      position += chunk.length;
      chunk.fill(0);
    }
    try {
      if ((await sha256(content)) !== metadata.sha256)
        throw Object.assign(new Error('Invalid attachment'), { code: 'INVALID_RESPONSE' });
      return {
        ...metadata,
        blob: new Blob([content], {
          type: IMAGE_TYPES.has(metadata.contentType)
            ? metadata.contentType
            : 'application/octet-stream',
        }),
      };
    } finally {
      content.fill(0);
    }
  }
  async function imageUrl(id) {
    if (!urls.has(id))
      urls.set(
        id,
        (async () => {
          const value = await read(id);
          if (!IMAGE_TYPES.has(value.contentType)) throw new Error('Not an image');
          const url = URL.createObjectURL(value.blob);
          if (disposed) {
            URL.revokeObjectURL(url);
            throw new Error('Closed');
          }
          return url;
        })().catch((error) => {
          urls.delete(id);
          throw error;
        }),
      );
    return urls.get(id);
  }
  async function download(id) {
    const { blob, filename } = await read(id);
    const url = URL.createObjectURL(blob);
    const link = el('a');
    link.href = url;
    link.download = filename.replace(/[/\\]/gu, '_');
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    notice(t('附件已校验并交给浏览器下载。'));
  }
  async function preview(attachment) {
    const dialog = el('dialog', undefined, 'attachment-preview');
    const header = el('header');
    const title = el('h2', attachment.filename);
    title.id = `attachment-title-${crypto.randomUUID()}`;
    dialog.setAttribute('aria-labelledby', title.id);
    const close = el('button', t('关闭'));
    close.type = 'button';
    header.append(title, close);
    dialog.append(header);
    let disposePreview;
    let cancelImage;
    const content = el('div', undefined, 'attachment-preview-content');
    dialog.append(content);
    const opener = document.activeElement;
    const finish = () => {
      dialog.close();
      cancelImage?.();
      disposePreview?.();
      dialog.remove();
      opener?.focus();
    };
    close.addEventListener('click', finish);
    dialog.addEventListener('cancel', (event) => {
      event.preventDefault();
      finish();
    });
    document.body.append(dialog);
    dialog.showModal();
    close.focus();
    const load = async () => {
      content.replaceChildren();
      const loading = el('p', attachment.contentType === 'application/pdf' ? t('正在加载 PDF…') : t('正在加载图片…'), 'attachment-preview-state');
      loading.setAttribute('role', 'status');
      content.append(loading);
      try {
      if (attachment.contentType === 'application/pdf') {
        const [{ blob }, { createPdfPreview }] = await Promise.all([
          read(attachment.id),
          import('./pdf-preview.js'),
        ]);
        if (!dialog.isConnected) return;
        content.replaceChildren();
        disposePreview = await createPdfPreview(blob, content);
        if (!dialog.isConnected) disposePreview();
      } else {
        const image = el('img');
        image.alt = attachment.filename;
        const source = await imageUrl(attachment.id);
        if (!dialog.isConnected) return;
        const loaded = await new Promise((resolve, reject) => {
          const cleanup = () => { image.onload = null; image.onerror = null; cancelImage = undefined; };
          image.onload = () => { cleanup(); resolve(true); };
          image.onerror = () => { cleanup(); reject(Object.assign(new Error('Image decode failed'), { code: 'IMAGE_DECODE_FAILED' })); };
          cancelImage = () => { cleanup(); image.removeAttribute('src'); resolve(false); };
          image.src = source;
        });
        if (loaded && dialog.isConnected) content.replaceChildren(image);
      }
      } catch (error) {
        if (!dialog.isConnected) return;
        const state = el('div', undefined, 'attachment-preview-state');
        const message = el('p', error?.code === 'IMAGE_DECODE_FAILED'
          ? t('无法显示这张图片，文件可能已损坏或格式不受支持。')
          : t('预览暂不可用，可重试或下载原附件查看。'));
        message.setAttribute('role', 'alert');
        const actions = el('div', undefined, 'actions');
        if (error?.code !== 'IMAGE_DECODE_FAILED') {
          const retry = el('button', t('重试预览'));
          retry.type = 'button';
          retry.addEventListener('click', () => { retry.disabled = true; void load(); });
          actions.append(retry);
        }
        const save = el('button', t('下载原附件'));
        save.type = 'button';
        save.addEventListener('click', async () => {
          save.disabled = true;
          try { await download(attachment.id); }
          catch { message.textContent = t('下载未完成，请检查连接后重试。'); }
          finally { save.disabled = false; }
        });
        actions.append(save);
        state.append(message, actions);
        content.replaceChildren(state);
      }
    };
    await load();
  }
  return {
    read,
    objectUrl(blob) {
      const url = URL.createObjectURL(blob);
      transientUrls.add(url);
      return url;
    },
    imageUrl,
    download,
    preview,
    isImage: (value) => IMAGE_TYPES.has(value.contentType),
    canPreview: (value) =>
      IMAGE_TYPES.has(value.contentType) || value.contentType === 'application/pdf',
    dispose: () => {
      disposed = true;
      for (const pending of urls.values())
        void pending.then((url) => URL.revokeObjectURL(url)).catch(() => {});
      urls.clear();
      for (const url of transientUrls) URL.revokeObjectURL(url);
      transientUrls.clear();
    },
  };
}
