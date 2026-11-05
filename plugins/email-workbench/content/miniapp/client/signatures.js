import { t, tt } from './i18n.js';
import { createRichEditor } from './editor-controls.js';

const CID = /^cid:([0-9a-f-]{36})@email-workbench$/u;
const invalid = (message) => {
  throw Object.assign(new Error(message), { code: 'INVALID_INPUT' });
};
const imageIds = (html) => {
  const template = document.createElement('template');
  template.innerHTML = html;
  return [
    ...new Set(
      [...template.content.querySelectorAll('img')]
        .map((node) => node.getAttribute('src')?.match(CID)?.[1])
        .filter(Boolean),
    ),
  ];
};

/** Signature assets stay in the encrypted Host store and become explicit draft attachments. */
export async function loadSignature(preference, api) {
  const attachments = await Promise.all(
    (preference?.signatureAttachmentIds ?? []).map(async (id) => {
      const { filename, contentType, bytes, sha256 } = await api('attachments/read', {
        id,
        offset: 0,
      });
      return { id, filename, contentType, bytes, sha256 };
    }),
  );
  return {
    text: preference?.signature ?? '',
    ...(preference?.signatureHtml ? { html: preference.signatureHtml } : {}),
    attachments,
  };
}

export function createSignatureEditor(textarea, preference, { api, el, imageUrl, changed }) {
  let disposed = false;
  let processing = false;
  const jobs = [];
  const status = el('div', undefined, 'signature-uploads');
  status.setAttribute('aria-live', 'polite');
  const rich = createRichEditor(textarea, {
    html: preference?.signatureHtml,
    label: t('邮箱签名'),
    placeholder: t('添加姓名、职位和联系方式…'),
    imageUrl,
    files: (files) => {
      if (disposed) return;
      for (const file of files) jobs.push({ file, id: crypto.randomUUID(), state: 'waiting' });
      changed();
      void drain();
    },
  });
  textarea.parentElement.append(
    status,
    el(
      'p',
      t('支持格式、链接及图片。最多 3 张图片，每张不超过 2 MiB。'),
      'muted',
    ),
  );
  function draw() {
    status.replaceChildren();
    for (const job of jobs.filter((item) => item.state !== 'done')) {
      const row = el('div', undefined, 'signature-upload');
      row.append(
        el(
          'span',
          `${job.file.name} · ${job.state === 'failed' ? job.error : job.state === 'uploading' ? tt`上传中 ${job.percent ?? 0}%` : t('等待上传')}`,
        ),
      );
      if (job.state === 'failed') {
        const retry = el('button', t('重试这张图片'));
        retry.type = 'button';
        retry.addEventListener('click', () => {
          job.state = 'waiting';
          void drain();
        });
        const remove = el('button', t('移除此项'));
        remove.type = 'button';
        remove.addEventListener('click', () => {
          jobs.splice(jobs.indexOf(job), 1);
          draw();
        });
        row.append(retry, remove);
      }
      status.append(row);
    }
  }
  async function drain() {
    if (processing || disposed) return;
    processing = true;
    try {
      while (!disposed) {
        const job = jobs.find((item) => item.state === 'waiting');
        if (!job) break;
        job.state = 'uploading';
        draw();
        try {
          if (job.file.size > 2 * 1024 * 1024) invalid(t('图片超过 2 MiB'));
          if (!/^image\/(png|jpeg|gif|webp)$/u.test(job.file.type))
            invalid(t('请选择 PNG、JPEG、GIF 或 WebP 图片'));
          if (imageIds(rich.html()).length >= 3) invalid(t('签名最多 3 张图片'));
          const content = new Uint8Array(await job.file.arrayBuffer());
          try {
            const sha256 = [...new Uint8Array(await crypto.subtle.digest('SHA-256', content))]
              .map((byte) => byte.toString(16).padStart(2, '0'))
              .join('');
            let receipt = await api('uploads/begin', {
              id: job.id,
              kind: 'attachment',
              filename: job.file.name,
              contentType: job.file.type,
              bytes: content.length,
              sha256,
            });
            if (receipt.status === 'cancelled') invalid(t('上传已取消，请重新选择图片'));
            if (receipt.status !== 'committed') {
              if (
                !Number.isInteger(receipt.offset) ||
                receipt.offset < 0 ||
                receipt.offset > content.length
              )
                invalid(t('上传进度无法核对'));
              while (receipt.offset < content.length) {
                const end = Math.min(receipt.offset + 96 * 1024, content.length);
                let chunk = '';
                for (const byte of content.subarray(receipt.offset, end))
                  chunk += String.fromCharCode(byte);
                receipt = await api('uploads/append', {
                  id: job.id,
                  offset: receipt.offset,
                  contentBase64: btoa(chunk),
                });
                if (receipt.offset !== end) invalid(t('上传进度不一致'));
                job.percent = Math.floor((end / content.length) * 100);
                if (!disposed) draw();
              }
              receipt = {
                status: 'committed',
                result: await api('uploads/commit', { id: job.id }),
              };
            }
            if (!disposed) {
              rich.insertImage(receipt.result);
              changed();
            }
            job.state = 'done';
          } finally {
            content.fill(0);
          }
        } catch (error) {
          job.state = 'failed';
          job.error =
            error.code === 'INVALID_INPUT' ? error.message : t('上传未完成，可核对原请求并重试');
        }
        if (!disposed) draw();
      }
    } finally {
      processing = false;
    }
  }
  return {
    value() {
      if (processing || jobs.some((job) => job.state !== 'done'))
        invalid(t('请先完成或移除未完成的签名图片上传'));
      const html = rich.html();
      const ids = imageIds(html);
      if (textarea.value.length > 5000 || html.length > 32 * 1024 || ids.length > 3)
        invalid(t('签名超出长度或图片数量上限'));
      return { signature: textarea.value, signatureHtml: html, signatureAttachmentIds: ids };
    },
    dispose() {
      disposed = true;
      rich.destroy();
    },
  };
}
