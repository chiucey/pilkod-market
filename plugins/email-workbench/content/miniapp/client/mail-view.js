import { t, tt } from './i18n.js';
import { renderDraftBody } from './mail-content.js';
import { icon } from './icon.js';
export { icon } from './icon.js';

/** Keep visible and accessible labels when replacing text controls with official icons. */
export function decorateAction(node, name, compact = false) {
  const text = node.textContent;
  const label = document.createElement('span'); label.textContent = text;
  if (compact) label.className = 'sr-only';
  node.replaceChildren(icon(name), label);
  node.classList.toggle('icon-action', compact);
  node.title = text;
  return node;
}

export function avatar(el, value = '') {
  const label =
    value
      .replace(/^[\s"']+/u, '')
      .slice(0, 1)
      .toUpperCase() || '@';
  const node = el('span', label, 'mail-avatar');
  node.dataset.tone = String(label.charCodeAt(0) % 3);
  node.setAttribute('aria-hidden', 'true');
  return node;
}

export function envelope(el, entries) {
  const list = el('dl', undefined, 'mail-envelope');
  for (const [label, value] of entries) {
    if (value) list.append(el('dt', label), el('dd', value));
  }
  return list;
}

export function attachmentIdentity(attachment, el, bytes) {
  const type = attachment.contentType?.split(';')[0] ?? '';
  const extension = attachment.filename?.split('.').pop()?.toUpperCase();
  const kind = type.startsWith('image/') ? tt`${extension || t('图片')} 图片`
    : type === 'text/plain' ? t('文本文件') : type === 'application/pdf' ? t('PDF 文档')
    : extension && extension.length <= 8 && extension !== attachment.filename?.toUpperCase() ? tt`${extension} 文件` : t('文件');
  const symbol = el('span', undefined, 'attachment-symbol');
  symbol.append(icon(type.startsWith('image/') ? 'image' : 'file'));
  const identity = el('span', undefined, 'attachment-identity');
  const name = el('span', attachment.filename); name.title = attachment.filename;
  identity.append(name, el('small', `${kind} · ${bytes(attachment.bytes)}`, 'muted'));
  return [symbol, identity];
}

export function deliveryView(draft, attachments, ctx) {
  const { el, button, date, bytes, sender, download, refresh } = ctx;
  const attachmentButton = ctx.localButton ?? button;
  const article = el('article', undefined, 'delivery-view');
  const banner = el('div', undefined, 'delivery-banner');
  banner.dataset.status = draft.status;
  banner.setAttribute('role', 'status');
  const copy = el('div');
  const labels = {
    sent: [t('已提交邮件服务器'), t('服务器已接受这封邮件，尚不能确认收件人已收到或已阅读。')],
    sending: [t('正在投递'), t('正在等待发件服务器回执，请勿重复发送。')],
    unknown: [t('投递结果不确定'), t('请核对服务商记录或收件端；此记录不能自动重发。')],
  };
  const [title, description] = labels[draft.status];
  copy.append(el('strong', title), el('p', description));
  banner.append(icon(draft.status === 'sent' ? 'check' : 'sent'), copy);
  banner.append(button(t('刷新状态'), refresh, 'quiet'));
  const header = el('header', undefined, 'mail-heading');
  const subject = el('div', undefined, 'subject-line');
  const state = el('span', title, 'inline-state');
  state.dataset.status = draft.status;
  subject.append(el('h2', draft.content.subject || t('（无主题）')), state);
  header.append(el('p', t('发送记录'), 'eyebrow'), subject);
  if (draft.status === 'sent') {
    state.setAttribute('role', 'status');
    const hint = el('p', description, 'delivery-hint');
    header.append(hint, button(t('刷新状态'), refresh, 'quiet'));
  }
  const senderCard = el('div', undefined, 'sender-card');
  senderCard.append(
    avatar(el, sender),
    envelope(el, [
      [t('发件人'), sender ?? t('账号已断开')],
      [t('收件人'), draft.content.to.join(', ')],
      [t('抄送'), draft.content.cc.join(', ')],
      [t('密送'), draft.content.bcc.join(', ')],
      [t('更新时间'), date(draft.updatedAt)],
    ]),
  );
  if (draft.status !== 'sent') article.append(banner);
  article.append(header, senderCard);
  article.append(renderDraftBody(draft.content, { imageUrl: ctx.imageUrl }));
  if (attachments.length) {
    const section = el('section', undefined, 'mail-attachments');
    section.setAttribute('aria-label', t('邮件附件'));
    section.append(el('h3', tt`附件 · ${attachments.length}`));
    for (const attachment of attachments) {
      const row = el('div', undefined, 'attachment');
      row.append(...attachmentIdentity(attachment, el, bytes));
      if (ctx.canPreview?.(attachment))
        row.append(attachmentButton(t('预览'), () => ctx.previewAttachment(attachment)));
      const save = attachmentButton(t('下载附件'), () => download(attachment.id));
      decorateAction(save, 'download', true);
      save.setAttribute('aria-label', tt`下载附件：${attachment.filename}`);
      save.title = tt`下载 ${attachment.filename}`;
      row.append(save);
      section.append(row);
    }
    article.append(section);
  }
  const receipt = el('details', undefined, 'delivery-receipt');
  receipt.append(
    el('summary', t('发送技术详情')),
    el('p', t('这是发件服务器返回的处理结果，不是收件或已读回执。'), 'receipt-explanation'),
    envelope(el, [
      [t('已接受的地址'), draft.accepted?.join(', ')],
      [t('未接受的地址'), draft.rejected?.join(', ')],
    ]),
  );
  if (draft.messageId) {
    receipt.append(envelope(el, [[t('邮件编号'), draft.messageId]]));
  }
  const copyStatus = {
    found: t('已在服务商文件夹中找到副本'),
    saved: t('工作台已保存副本'),
    not_found: t('暂未找到服务商副本；可稍后核对'),
    folder_unknown: t('未识别已发送文件夹，可在账号偏好中选择'),
    unknown: t('副本状态暂未确认；不会自动重复保存'),
  };
  const copySection = el('section', undefined, 'sent-copy-status');
  copySection.append(
    el('h3', t('服务商已发送副本')),
    el('p', copyStatus[draft.sentCopy?.status] ?? t('此历史记录尚未核对服务商副本')),
  );
  if (draft.sentCopy?.folder)
    copySection.append(el('p', tt`文件夹：${draft.sentCopy.folder}`, 'muted'));
  if (ctx.checkCopy && ['sent', 'unknown'].includes(draft.status))
    copySection.append(button(t('核对服务商副本'), ctx.checkCopy));
  receipt.append(copySection);
  article.append(receipt);
  return article;
}
