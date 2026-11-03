import { t, tt } from './i18n.js';
import { renderDraftBody } from './mail-content.js';

export async function confirmDraftSend(draft, attachments, { el, bytes, imageUrl, sender }) {
  const dialog = el('dialog', undefined, 'confirmation-dialog');
  const form = el('form');
  form.method = 'dialog';
  form.append(el('h2', t('确认发送这封邮件？')));
  for (const [label, value] of [
    [t('发件人'), sender],
    [t('收件人'), draft.content.to.join('、')],
    [t('抄送'), (draft.content.cc ?? []).join('、')],
    [t('密送'), (draft.content.bcc ?? []).join('、')],
    [t('主题'), draft.content.subject || t('（未填写主题）')],
  ])
    if (value) form.append(el('p', `${label}：${value}`));
  form.append(renderDraftBody(draft.content, { imageUrl }));
  form.append(el('h3', tt`附件（${attachments.length}）`));
  for (const attachment of attachments)
    form.append(el('p', `${attachment.filename} · ${bytes(attachment.size)}`));
  const actions = el('div', undefined, 'actions');
  const cancel = el('button', t('返回编辑'));
  cancel.value = 'cancel';
  cancel.autofocus = true;
  const send = el('button', t('确认发送'), 'primary');
  send.value = 'send';
  actions.append(cancel, send);
  form.append(actions);
  dialog.append(form);
  document.body.append(dialog);
  try {
    const result = new Promise((resolve) =>
      dialog.addEventListener('close', () => resolve(dialog.returnValue === 'send'), {
        once: true,
      }),
    );
    dialog.showModal();
    return await result;
  } finally {
    dialog.remove();
  }
}
