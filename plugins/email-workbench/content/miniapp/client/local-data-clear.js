import { t, tt } from './i18n.js';
const CONFIRMATION = t('清除本机邮箱数据');
const SCOPE_KEY = 'email-workbench-account-scope';
const failures = {
  BUSY: t('仍有邮箱操作、投递或其他页面占用。请等待操作结束后手动重试，不会自动再次提交。'),
  CREDENTIAL_DENIED: t('系统未允许删除本插件的凭证。请允许系统凭证访问后手动重试。'),
  CREDENTIAL_LOCKED: t('系统凭证库已锁定。请先解锁系统凭证库，再手动重试。'),
  CREDENTIAL_UNAVAILABLE: t('系统凭证库暂不可用。请检查系统状态后手动重试。'),
  STORAGE_UNAVAILABLE: t('本机文件清理未完成。请检查磁盘空间与访问权限后手动重试。'),
  VAULT_CLEAR_PENDING: t('上次清除尚未完成，邮箱业务已暂停。请手动重试清除，不会自动初始化新的邮箱库。'),
  VAULT_CORRUPT: t('本机邮箱元信息损坏，无法安全确定要清除的数据。未继续清理，请检查本机存储。'),
};

/** Destructive page-only operation. No automatic retries, including after uncertain responses. */
export function createLocalDataClear({ el, api, cleared }) {
  let dialog;
  let pending = false;
  let disposed = false;
  function open() {
    if (disposed || pending) return;
    if (dialog?.open) { dialog.querySelector('input')?.focus(); return; }
    const opener = document.activeElement;
    const node = el('dialog', undefined, 'confirmation-dialog local-data-clear');
    dialog = node;
    node.id = 'local-data-clear';
    node.setAttribute('aria-labelledby', 'local-data-clear-title');
    const title = el('h2', t('清除本机邮箱数据？'));
    title.id = 'local-data-clear-title';
    node.append(title, el('p', t('此操作无法撤销，仅影响当前登录账号在这台电脑上的数据。'), 'review-note'));
    const scope = el('ul', undefined, 'clear-scope');
    scope.append(el('li', t('永久删除：本机草稿、可恢复编辑、发送记录、附件及本机加密密钥。')), el('li', t('继续保留：云端邮箱连接、远端邮件和其他设备上的数据。')));
    node.append(scope);
    const form = el('form', undefined, 'connection-form');
    form.id = 'local-data-clear-form';
    const label = el('label', tt`请输入“${CONFIRMATION}”以确认`);
    const input = el('input');
    input.id = 'local-data-clear-confirmation';
    input.autocomplete = 'off';
    input.spellcheck = false;
    input.setAttribute('aria-describedby', 'local-data-clear-status');
    label.append(input);
    const status = el('p', '', 'connection-status');
    status.id = 'local-data-clear-status';
    status.setAttribute('role', 'status');
    const actions = el('div', undefined, 'actions');
    const cancel = el('button', t('取消'));
    cancel.type = 'button';
    cancel.autofocus = true;
    const submit = el('button', t('永久清除'), 'danger');
    submit.id = 'local-data-clear-submit';
    submit.type = 'submit';
    submit.disabled = true;
    const close = () => {
      if (pending) return;
      input.value = '';
      node.remove();
      if (dialog === node) dialog = undefined;
      if (opener?.isConnected && !opener.disabled) opener.focus({ preventScroll: true });
    };
    input.addEventListener('input', () => { submit.disabled = pending || input.value !== CONFIRMATION; });
    cancel.addEventListener('click', close);
    node.addEventListener('cancel', (event) => { event.preventDefault(); close(); });
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (pending || input.value !== CONFIRMATION) return;
      pending = true;
      input.disabled = true; cancel.disabled = true; submit.disabled = true;
      status.textContent = t('正在清除本插件的本机邮箱数据…');
      status.className = 'connection-status';
      status.setAttribute('role', 'status');
      try {
        const result = await api('vault/clear', { confirmation: '清除本机邮箱数据' });
        if (!result?.cleared || result.status !== 'uninitialized') throw new Error('Invalid clear result');
        if (disposed || dialog !== node) return;
        try { localStorage.removeItem(SCOPE_KEY); } catch { /* A blocked browser store must not undo a completed clear. */ }
        input.value = '';
        status.textContent = t('本机邮箱数据已清除，重新打开后会恢复云端邮箱连接。');
        cleared();
      } catch (error) {
        if (disposed || dialog !== node) return;
        status.textContent = failures[error?.code] ?? t('未能确认清除完成。请核对本机状态，再手动重试；不会自动重新提交。');
        status.className = 'connection-status error';
        status.setAttribute('role', 'alert');
        pending = false;
        input.disabled = false; cancel.disabled = false;
        submit.textContent = t('重试清除');
        submit.disabled = input.value !== CONFIRMATION;
      }
    });
    actions.append(cancel, submit); form.append(label, status, actions); node.append(form);
    document.body.append(node); node.showModal(); cancel.focus();
  }
  return {
    open,
    active: () => Boolean(dialog?.open),
    dispose() { disposed = true; dialog?.remove(); dialog = undefined; },
  };
}
