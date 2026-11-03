import { t } from './i18n.js';
import { createSignatureEditor } from './signatures.js';

const SCOPE_KEY = 'email-workbench-account-scope';
const validScope = (value) =>
  /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/u.test(value ?? '');
// Only an opaque mailbox selection is stored in Browser storage, never mail or account details.
export function readAccountScope() {
  try {
    const value = localStorage.getItem(SCOPE_KEY);
    return validScope(value) ? value : '';
  } catch {
    return '';
  }
}
export function rememberAccountScope(value) {
  try {
    if (validScope(value)) localStorage.setItem(SCOPE_KEY, value);
    else localStorage.removeItem(SCOPE_KEY);
  } catch {
    /* A blocked storage policy must not prevent mailbox use. */
  }
}

/** Account preferences contain no authentication material and never modify saved drafts. */
export function createAccountWorkspace(ctx) {
  const { $, el, button, api, notice } = ctx;
  let signatureEditors = [];
  function dispose() {
    for (const editor of signatureEditors) editor.dispose();
    signatureEditors = [];
  }
  async function open() {
    if (!(await ctx.leaveEditor())) return;
    const value = await api('accounts/preferences');
    dispose();
    ctx.resetEditor();
    const detail = $('detail');
    delete detail.dataset.batch;
    delete detail.dataset.accountManagement;
    detail.dataset.settingsPage = 'preferences';
    const header = el('div', undefined, 'settings-heading');
    header.append(el('h2', t('邮箱设置')), button(t('本机空间与维护'), async () => { if (await ctx.leaveEditor()) await ctx.maintenance(); }, 'quiet'));
    detail.replaceChildren(header);
    if (!ctx.accounts().some((item) => item.id === ctx.accountId())) {
      detail.append(el('p', t('当前没有已连接的邮箱。连接后可设置名称和签名。'), 'muted'),
        button(t('连接邮箱'), () => ctx.openSettings(), 'primary'));
      notice('');
      ctx.showDetail();
      return;
    }
    let activeTab = 'general';
    const tabs = el('div', undefined, 'settings-tabs');
    tabs.setAttribute('role', 'group'); tabs.setAttribute('aria-label', t('邮箱设置分类'));
    const description = el('p', undefined, 'muted settings-description');
    const descriptions = { general: t('设置此邮箱的显示名称与已发送副本。'), signature: t('签名用于之后创建的新邮件，已有草稿保持不变。'), connection: t('管理此邮箱的授权与连接。') };
    const actions = el('div', undefined, 'actions settings-actions');
    const updateTab = (id) => { activeTab = id; description.textContent = descriptions[id]; actions.hidden = id === 'connection'; if (actions.firstElementChild) actions.firstElementChild.textContent = id === 'signature' ? t('保存签名') : t('保存设置'); };
    updateTab('general');
    const sections = new Map();
    for (const [id, label] of [['general', t('常用')], ['signature', t('签名')], ['connection', t('连接')]]) {
      const section = el('section', undefined, 'settings-section'); section.id = `settings-${id}`; section.hidden = id !== 'general'; sections.set(id, section);
      const tab = button(label, () => { updateTab(id); for (const [key, node] of sections) node.hidden = key !== id; for (const button of tabs.children) button.setAttribute('aria-pressed', String(button === tab)); });
      tab.setAttribute('aria-pressed', String(id === 'general')); tabs.append(tab);
    }
    detail.append(tabs, description);
    const form = el('form', undefined, 'editor');
    form.id = 'account-preferences';
    form.addEventListener('submit', (event) => event.preventDefault());
    form.addEventListener('input', () => ctx.dirty(true));
    const rows = [];
    for (const account of ctx.accounts().filter((item) => item.id === ctx.accountId())) {
      const preference = value.accounts.find((item) => item.accountId === account.id);
      const card = el('fieldset', undefined, 'account-card');
      card.append(el('legend', t('邮箱资料')));
      const identity = el('div', undefined, 'settings-identity');
      identity.append(el('strong', account.address), el('span', t('已连接'), 'connection-badge'));
      detail.insertBefore(identity, tabs);
      const fields = {};
      for (const [key, text, max, multiline] of [
        ['label', t('显示名称'), 100, false],
        ['group', t('分组（可选）'), 60, false],
        ['signature', t('此邮箱的签名'), 5000, true],
      ]) {
        const label = el('label', text);
        const input = el(multiline ? 'textarea' : 'input');
        input.id = `account-${key}-${account.id}`;
        input.maxLength = max;
        input.value = preference?.[key] ?? (key === 'label' ? account.label : '');
        label.append(input);
        card.append(label);
        fields[key] = input;
      }
      const signatureEditor = createSignatureEditor(fields.signature, preference, {
        api,
        el,
        imageUrl: ctx.imageUrl,
        changed: () => ctx.dirty(true),
      });
      signatureEditors.push(signatureEditor);
      sections.get('signature').append(fields.signature.parentElement);
      const delivery = el('fieldset', undefined, 'account-card');
      delivery.append(el('legend', t('已发送副本')));
      const copyLabel = el('label', t('保存方式'));
      const copyMode = el('select');
      copyMode.id = `account-sentCopyMode-${account.id}`;
      for (const [key, text] of [
        ['provider', t('由服务商保存（默认）')],
        ['workbench', t('由工作台保存一份副本')],
      ]) {
        const option = el('option', text);
        option.value = key;
        copyMode.append(option);
      }
      copyMode.value = preference?.sentCopyMode ?? 'provider';
      fields.sentCopyMode = copyMode;
      copyLabel.append(copyMode);
      delivery.append(copyLabel);
      delivery.append(
        el(
          'p',
          t('服务商已自动保存时，无需再保存一份。副本状态不明时只核对，不自动追加。'),
          'muted',
        ),
      );
      const folderLabel = el('label', t('已发送文件夹'));
      const sentFolder = el('select');
      const automatic = el('option', t('自动识别服务商标记'));
      automatic.value = '';
      sentFolder.append(automatic);
      fields.sentFolder = sentFolder;
      if (preference?.sentFolder) {
        const saved = el('option', preference.sentFolder);
        saved.value = preference.sentFolder;
        sentFolder.append(saved);
        sentFolder.value = preference.sentFolder;
      }
      const folderRow = el('span', undefined, 'settings-inline-field');
      folderRow.append(
        sentFolder,
        button(t('获取文件夹'), async () => {
          const folders = await api('messages/folders', { accountId: account.id });
          const current = sentFolder.value;
          sentFolder.replaceChildren(automatic);
          for (const folder of folders) {
            const option = el('option', folder.path);
            option.value = folder.path;
            sentFolder.append(option);
          }
          sentFolder.value = current;
        }),
      );
      folderLabel.append(folderRow);
      delivery.append(folderLabel);
      const updateCopyFields = () => { folderLabel.hidden = copyMode.value !== 'workbench'; };
      copyMode.addEventListener('change', updateCopyFields);
      updateCopyFields();
      const connection = sections.get('connection');
      const credentials = el('div', undefined, 'settings-option');
      const credentialText = el('div');
      credentialText.append(el('h3', t('邮箱授权')), el('p', t('授权码失效或更换后，在这里更新。'), 'muted'));
      credentials.append(credentialText, button(t('更新授权码'), async () => { if (await ctx.leaveEditor()) await ctx.openSettings({ address: account.address }); }));
      const disconnectRow = el('div', undefined, 'settings-option');
      const disconnectText = el('div');
      disconnectText.append(el('h3', t('断开邮箱')), el('p', t('移除账号中的连接；已保存的本机草稿和记录保留。'), 'muted'));
      disconnectRow.append(disconnectText, button(t('断开邮箱'), async () => { if (await ctx.leaveEditor()) await disconnect(account, value); }, 'danger'));
      connection.append(credentials, disconnectRow, el('p', t('连接跟随 MCode 账号同步，草稿与附件保存在本机。'), 'muted'));
      rows.push({ accountId: account.id, fields, signatureEditor });
      sections.get('general').append(card, delivery);
    }
    form.append(...sections.values());

    actions.append(
      button(
        t('保存设置'),
        async () => {
          const readInput = () => ({
            revision: value.revision,
            ...(value.defaultAccountId ? { defaultAccountId: value.defaultAccountId } : {}),
            accounts: [...value.accounts.filter((item) => !rows.some((row) => row.accountId === item.accountId)), ...rows.map(({ accountId, fields, signatureEditor }) => ({
              accountId,
              ...signatureEditor.value(),
              ...Object.fromEntries(
                Object.entries(fields)
                  .filter(
                    ([key, input]) => key !== 'signature' && (key !== 'sentFolder' || input.value),
                  )
                  .map(([key, input]) => [key, input.value]),
              ),
            }))],
          });
          const snapshot = readInput();
          const result = await api('accounts/preferences/save', snapshot);
          // Rich text can still be edited while a previous preference version is saving.
          let changed = true;
          try {
            changed = JSON.stringify(readInput()) !== JSON.stringify(snapshot);
          } catch {
            /* upload in progress */
          }
          Object.assign(value, result);
          ctx.dirty(changed);
          await ctx.refresh();
          notice(
            changed
              ? t('上一版账号偏好已保存，新输入的内容尚未保存。')
              : activeTab === 'signature' ? t('签名已保存，将用于之后创建的新邮件。') : t('邮箱设置已保存。'),
          );
        },
        'primary',
      ),
    );
    form.append(actions);
    detail.append(form);
    ctx.showDetail();
    notice('');
  }
  async function disconnect(account, preferences) {
    const remaining = ctx.accounts().filter((item) => item.id !== account.id);
    const dialog = el('dialog', undefined, 'account-connection');
    dialog.setAttribute('aria-labelledby', 'disconnect-title');
    const heading = el('h2', t('断开此邮箱？'));
    heading.id = 'disconnect-title';
    dialog.append(heading, el('p', account.address), el('p', t('从当前 MCode 账号的云端配置移除此邮箱，其他设备刷新后也会断开。已保存草稿、附件和发送记录仍保留在本机。'), 'muted'));
    const form = el('form');
    form.method = 'dialog';
    let next;
    if (preferences.defaultAccountId === account.id && remaining.length) {
      const label = el('label', t('改用以下邮箱作为当前和默认发件邮箱'));
      next = el('select');
      next.id = 'disconnect-next-account';
      for (const item of remaining) {
        const option = el('option', item.address);
        option.value = item.id;
        next.append(option);
      }
      label.append(next); form.append(label);
    }
    const actions = el('div', undefined, 'actions');
    for (const [value, text] of [['cancel', t('保留连接')], ['disconnect', t('确认断开')]]) {
      const node = el('button', text);
      node.value = value;
      if (value === 'disconnect') node.className = 'danger';
      else node.autofocus = true;
      actions.append(node);
    }
    form.append(actions); dialog.append(form); document.body.append(dialog);
    const approved = await new Promise((resolve) => {
      dialog.addEventListener('close', () => resolve(dialog.returnValue === 'disconnect'), { once: true });
      dialog.showModal();
    });
    const nextAccountId = next?.value;
    dialog.remove();
    if (!approved) return;
    await api('accounts/disconnect', { accountId: account.id, ...(nextAccountId ? { nextAccountId } : {}) });
    await ctx.refresh();
    await open();
    notice(t('邮箱已断开，已保存草稿和发送记录仍保留。'));
  }
  async function manage() { return open(); }
  return { open, manage, dispose };
}
