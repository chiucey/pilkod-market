import { t, tt } from './i18n.js';
/** Per-file uploads are independent of draft persistence and never lock text editing. */
export function createAttachmentUploads({ api, el, count, committed, changed, beforeUpload }) {
  const element = el('div', undefined, 'attachment-uploads');
  element.setAttribute('aria-live', 'polite');
  const jobs = [];
  let processing = false;
  let disposed = false;
  const pending = () => jobs.some((job) => job.state !== 'done');
  const notify = () => {
    if (!disposed) {
      draw();
      changed();
    }
  };
  function draw() {
    element.replaceChildren();
    for (const job of jobs.filter((item) => item.state !== 'done')) {
      const row = el('div', undefined, 'attachment-upload');
      row.append(
        el('span', job.file.name),
        el(
          'span',
          job.state === 'failed'
            ? job.error
            : job.state === 'uploading'
              ? tt`上传中 ${job.percent ?? 0}%`
              : t('等待上传'),
          'muted',
        ),
      );
      if (job.state === 'failed') {
        const retry = el('button', t('重试此附件'));
        retry.type = 'button';
        retry.addEventListener('click', () => {
          job.state = 'waiting';
          notify();
          void drain();
        });
        row.append(retry);
      }
      if (job.state !== 'uploading') {
        const remove = el('button', t('移除此项'));
        remove.type = 'button';
        remove.addEventListener('click', () => {
          jobs.splice(jobs.indexOf(job), 1);
          // Removing an unreferenced attachment never changes a draft or sends mail.
          void api('uploads/cancel', { id: job.id }).catch(() => {});
          notify();
        });
        row.append(remove);
      }
      element.append(row);
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
        notify();
        try {
          await beforeUpload();
          if (disposed) return;
          if (job.file.size > 10 * 1024 * 1024) throw new Error(t('单个附件不能超过 10 MiB'));
          if (count() >= 10) throw new Error(t('一封邮件最多 10 个附件，请先移除不需要的附件'));
          const content = new Uint8Array(await job.file.arrayBuffer());
          try {
            const sha256 = [...new Uint8Array(await crypto.subtle.digest('SHA-256', content))]
              .map((byte) => byte.toString(16).padStart(2, '0'))
              .join('');
            let state = await api('uploads/begin', {
              id: job.id,
              kind: 'attachment',
              filename: job.file.name,
              contentType: /^[\w.+-]+\/[\w.+-]+$/u.test(job.file.type)
                ? job.file.type
                : 'application/octet-stream',
              bytes: content.length,
              sha256,
            });
            if (state.status === 'cancelled') throw new Error(t('上传已取消，请重新选择文件'));
            if (state.status === 'committing') throw new Error(t('正在持久化，请稍后核对此附件'));
            if (state.status !== 'committed') {
              if (
                !Number.isInteger(state.offset) ||
                state.offset < 0 ||
                state.offset > content.length
              )
                throw new Error(t('上传进度不一致，请重试核对原请求'));
              while (state.offset < content.length) {
                const end = Math.min(state.offset + 96 * 1024, content.length);
                let chunk = '';
                for (const byte of content.subarray(state.offset, end))
                  chunk += String.fromCharCode(byte);
                state = await api('uploads/append', {
                  id: job.id,
                  offset: state.offset,
                  contentBase64: btoa(chunk),
                });
                if (state.offset !== end) throw new Error(t('上传进度不一致，请重试核对原请求'));
                job.percent = Math.floor((end / content.length) * 100);
                notify();
                if (disposed) return;
              }
              state = { result: await api('uploads/commit', { id: job.id }) };
            }
            if (!disposed) committed(state.result, job.inline);
            job.state = 'done';
          } finally {
            content.fill(0);
          }
        } catch (error) {
          job.state = 'failed';
          job.error = error.code ? t('上传未完成，重试将核对原请求') : error.message;
        }
        notify();
      }
    } finally {
      processing = false;
      notify();
    }
  }
  return {
    element,
    pending,
    enqueue(files, inline = false) {
      if (disposed) return;
      for (const file of files)
        jobs.push({ id: crypto.randomUUID(), file, inline, state: 'waiting' });
      notify();
      void drain();
    },
    dispose() {
      disposed = true;
      jobs.length = 0;
    },
  };
}
