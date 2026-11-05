import { t, tt } from './i18n.js';
export function createStorageWorkspace(ctx) {
  const { $, el, button, api, bytes, notice } = ctx;
  async function open() {
    if (!(await ctx.leaveEditor())) return;
    ctx.resetEditor();
    const value = await api('storage/status');
    const detail = $('detail');
    detail.dataset.settingsPage = 'storage';
    const header = el('div', undefined, 'settings-heading');
    header.append(el('h2', t('本地邮箱空间')), button(t('返回设置'), ctx.returnToSettings));
    detail.replaceChildren(
      header,
      el('p', t('草稿与附件保存在本机加密空间。以下为工作台用量上限，不代表电脑磁盘容量。'), 'muted'),
    );
    const meters = el('div', undefined, 'storage-meters');
    detail.append(meters);
    for (const [label, used, total] of [
      [t('附件'), value.attachmentBytes, value.attachmentLimitBytes],
      [t('草稿与记录'), value.stateBytes, value.stateLimitBytes],
    ]) {
      const section = el('section', undefined, 'storage-card');
      const progress = el('progress');
      progress.max = total;
      progress.value = used;
      progress.setAttribute('aria-label', tt`${label}空间`);
      section.append(el('h3', label), el('p', `${bytes(used)} / ${bytes(total)}`), progress);
      if (used / total >= 0.8)
        section.append(
          el('p', t('空间即将用满，可清理未使用附件或删除不再需要的草稿。'), 'review-note'),
        );
      meters.append(section);
    }
    detail.append(
      el(
        'p',
        tt`${value.draftCount} 条草稿与投递记录 · ${value.recoveryCount} 份可恢复编辑 · ${value.attachmentCount} 个附件`,
      ),
    );
    const clean = button(tt`清理未使用附件（${bytes(value.unusedBytes)}）`, async () => {
      const result = await api('storage/clean');
      await open();
      notice(tt`已清理 ${bytes(result.removedBytes)}。草稿、恢复内容和发送清单使用的附件均保留。`);
    });
    clean.disabled = !value.unusedIds.length;
    const cleanup = el('section', undefined, 'storage-cleanup');
    cleanup.append(
      el('h3', t('附件清理')),
      ...(value.unusedIds.length ? [] : [el('p', t('暂无可清理附件'), 'muted')]),
      clean,
      el(
        'p',
        t('只清理超过 24 小时且未被草稿、恢复内容或发送清单使用的附件。近期上传的文件会保留，便于继续编辑。'),
        'muted',
      ),
    );
    detail.append(cleanup);
    const danger = el('details', undefined, 'storage-card');
    danger.append(el('summary', t('重置与清除')));
    danger.append(
      el('h3', t('清除本机邮箱数据')),
      el('p', t('永久删除当前登录账号的本机草稿、发送记录、附件和本机加密密钥。云端连接、远端邮件及其他设备的数据不受影响。'), 'muted'),
      button(t('清除本机邮箱数据'), ctx.clearLocalData, 'danger'),
    );
    detail.append(danger);
    ctx.showDetail();
    notice('');
  }
  return { open };
}

export async function confirmDraftRemoval(draft, { el }) {
  const dialog = el('dialog', undefined, 'confirmation-dialog');
  const opener = document.activeElement;
  const title = el('h2', t('删除这份草稿？'));
  title.id = `delete-draft-title-${crypto.randomUUID()}`;
  dialog.setAttribute('aria-labelledby', title.id);
  const form = el('form');
  form.method = 'dialog';
  form.append(
    title,
    el('p', draft.content.subject || t('（未填写主题）')),
    el('p', t('删除后无法从草稿列表恢复。已发送邮件与其他草稿不受影响。')),
  );
  const actions = el('div', undefined, 'actions');
  const keep = el('button', t('保留草稿'));
  keep.value = 'keep';
  keep.autofocus = true;
  const remove = el('button', t('删除草稿'));
  remove.value = 'delete';
  remove.className = 'danger';
  actions.append(keep, remove);
  form.append(actions);
  dialog.append(form);
  document.body.append(dialog);
  dialog.showModal();
  const result = await new Promise((resolve) =>
    dialog.addEventListener('close', () => resolve(dialog.returnValue === 'delete'), {
      once: true,
    }),
  );
  dialog.remove();
  opener?.focus();
  return result;
}
