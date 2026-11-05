import { t, tt, localeTag, localizeShell, languagePreference, saveLanguagePreference } from './i18n.js';
import { createMessageReader, createMessagePreloader } from './message-reader.js';
import { createPageState } from './page-state.js';
import { errorMessages as errors } from './error-contract.js';
import { createPageClient } from './page-client.js';
import { createUiContextBridge } from './ui-context.js';
import { createAttachmentUploads } from './uploads.js';
import { loadSignature } from './signatures.js';
import { createMailOrganizer } from './organize.js';
import { createRichEditor } from './editor-controls.js';
import { createAttachmentAccess } from './attachments.js';
import { prepareQuotedMessage } from './quoted-message.js';
import { renderDraftBody } from './mail-content.js';
import { createStorageWorkspace, confirmDraftRemoval } from './storage.js';
import { formatProductTime } from './product-time.js';
import { createBatchWorkspace } from './batches.js';
import { readWorkbenchTarget } from './workbench-target.js';
import { createAccountWorkspace, readAccountScope, rememberAccountScope } from './accounts.js';
import { createAccountConnection, vaultErrors } from './account-connection.js';
import { createLocalDataClear } from './local-data-clear.js';
import { createMailMergeWorkspace } from './mail-merge.js';
import { renderIsolatedMessage } from './message-format.js';
import { icon, decorateAction, avatar, envelope, deliveryView, attachmentIdentity } from './mail-view.js';
import { installWorkbenchPopups } from './popups.js';

localizeShell(document);
const pageState = createPageState();
installWorkbenchPopups();
const pendingReadFlags = new Map();
const $ = (id) => document.getElementById(id);
let refreshOperation;
let accountsGeneration = 0;
let accountsSyncedAt = 0;
let focusSyncPending = false;
for (const [id, name] of Object.entries({
  'inbox-tab': 'inbox',
  'work-tab': 'work',
  'drafts-tab': 'draft',
  'sent-tab': 'sent',
  'batches-tab': 'batch',
  compose: 'plus',
  settings: 'settings',
  preferences: 'settings',
  refresh: 'refresh',
  'close-compose': 'close',
}))
  $(id).prepend(icon(name));
$('settings').setAttribute('aria-label', t('邮箱设置'));
document.querySelector('#list-options > summary').replaceChildren(icon('more'));
$('settings').title = t('邮箱设置');
$('preferences').title = t('账号偏好');
$('preferences').setAttribute('aria-label', t('账号偏好'));
document.querySelector('.brand-mark').replaceChildren(icon('mail'));
document.querySelector('#search > button').replaceChildren(icon('search'));
const filterSummary = document.querySelector('.search-advanced > summary');
decorateAction(filterSummary, 'filter', true);
document.querySelector('.folder-control').after(document.querySelector('.search-advanced'));
for (const control of document.querySelectorAll('.search-advanced input, .search-advanced button')) control.setAttribute('form', 'search');
decorateAction($('close-compose'), 'close', true);
document.querySelector('.detail-empty')?.prepend(icon('mail'));
const CHUNK = 96 * 1024;
const MAX_ATTACHMENT = 10 * 1024 * 1024;
const states = {
  draft: t('草稿'),
  pending_confirmation: t('等待工作台确认'),
  queued: t('已确认，等待投递'),
  sending: t('投递中'),
  sent: t('已提交邮件服务器'),
  unknown: t('投递结果不确定，禁止自动重发'),
};

const pageClient = createPageClient((...args) => fetch(...args));
const messageReader = createMessageReader((input, signal) => api('messages/read', input, signal));
const messagePreloader = createMessagePreloader(messageReader, () =>
  !pageState.lifecycle.busy && !pageState.lifecycle.disposed && !pageState.composer.editor &&
  pageState.navigation.view === 'inbox' && document.body.dataset.workspace !== 'settings' &&
  !$('compose-dialog').open && document.visibilityState !== 'hidden' && !refreshOperation);
let prefetchTimer;

const attachmentAccess = createAttachmentAccess({ api, sha256, el, notice });

function disposeReader() { pageState.releaseReader(); }

const searchFields = [
  'subject-search',
  'from-search',
  'to-search',
  'text-search',
  'since-search',
  'until-search',
  'flagged-search',
  'attachments-search',
  'unread',
];

const viewNames = {
  inbox: t('收件箱'),
  work: t('待处理'),
  drafts: t('草稿'),
  sent: t('发送记录'),
  batches: t('批量任务'),
};
const draftImageUrl = (source) =>
  attachmentAccess.imageUrl(source.replace(/^cid:/u, '').replace(/@email-workbench$/u, ''));
const batchWorkspace = createBatchWorkspace({
  imageUrl: draftImageUrl,
  $,
  el,
  button,
  api,
  notice,
  run,
  date,
  bytes,
  showDetail,
  leaveEditor,
  openDraft,
  accounts: () => pageState.account.accounts,
  accountId: () => pageState.account.accountId,
  resetEditor: () => {
    mailMergeWorkspace.dispose();
    accountWorkspace.dispose();
    pageState.requests.invalidate('reader');
    pageState.composer.editor?.uploads?.dispose();
    pageState.composer.editor?.rich?.destroy();
    pageState.composer.editor = undefined;
    pageState.composer.dirty = false;
  },
  refresh: () => loadList(),
  prepareMailing: () => mailMergeWorkspace.open(),
});
const mailMergeWorkspace = createMailMergeWorkspace({
  imageUrl: attachmentAccess.imageUrl,
  canPreview: attachmentAccess.canPreview,
  previewAttachment: attachmentAccess.preview,
  error: (code) => errors[code] ?? t('操作未完成，请检查当前状态。'),
  $,
  el,
  button,
  api,
  notice,
  run,
  leaveEditor,
  showDetail,
  openDraft,
  accounts: () => pageState.account.accounts,
  defaultSender: () => pageState.account.preferences.defaultAccountId ?? '',
  dirty: (value) => {
    pageState.composer.dirty = value;
  },
  resetEditor: () => {
    mailMergeWorkspace.dispose();
    accountWorkspace.dispose();
    pageState.requests.invalidate('reader');
    pageState.composer.editor?.uploads?.dispose();
    pageState.composer.editor?.rich?.destroy();
    pageState.composer.editor = undefined;
    pageState.composer.dirty = false;
    clearTimeout(pageState.composer.autosaveTimer);
  },
  review: (refs) => batchWorkspace.review(refs),
});
const accountWorkspace = createAccountWorkspace({
  imageUrl: attachmentAccess.imageUrl,
  $,
  el,
  button,
  api,
  notice,
  leaveEditor,
  openSettings,
  showDetail: showSettings,
  accountId: () => pageState.account.accountId,
  returnToMailbox,
  maintenance: () => storageWorkspace.open(),
  accounts: () => pageState.account.accounts,
  dirty: (value) => {
    pageState.composer.dirty = value;
  },
  resetEditor: () => {
    mailMergeWorkspace.dispose();
    accountWorkspace.dispose();
    pageState.requests.invalidate('reader');
    pageState.composer.editor?.uploads?.dispose();
    pageState.composer.editor?.rich?.destroy();
    pageState.composer.editor = undefined;
    pageState.composer.dirty = false;
    clearTimeout(pageState.composer.autosaveTimer);
  },
  refresh: () => loadAccounts(),
});
const accountPreference = (id) => pageState.account.preferences.accounts.find((item) => item.accountId === id);
const localDataClear = createLocalDataClear({ el, api, cleared: finishLocalDataClear });
const accountConnection = createAccountConnection({
  el, api, notice, accounts: () => pageState.account.accounts,
  error: (code) => errors[code],
  connected: refreshAfterSetup,
  select: changeAccount,
  clearLocalData: () => localDataClear.open(),
});
const storageWorkspace = createStorageWorkspace({
  $,
  el,
  button,
  api,
  bytes,
  notice,
  leaveEditor,
  resetEditor: blankDetail,
  showDetail: showSettings,
  returnToSettings: () => accountWorkspace.open(),
  clearLocalData: () => localDataClear.open(),
});
const organizer = createMailOrganizer({
  $,
  el,
  button,
  api,
  notice,
  messages: () => pageState.inbox.loadedMessages,
  render: renderInboxRows,
  error: (code) => errors[code] ?? t('未能完成，请刷新核对。'),
  refresh: async () => {
    blankDetail();
    await loadList();
  },
});

function releaseEditLease() {
  if (!pageState.composer.editLease) return;
  clearTimeout(pageState.composer.editLease.timer); pageState.composer.editLease.node.remove(); pageState.composer.editLease = undefined;
  $('compose-detail').inert = false;
}
function holdEditLease(operation) {
  releaseEditLease();
  if (!pageState.composer.editor?.draft.id) return;
  $('compose-detail').inert = true;
  const node = el('div', undefined, 'editor-lease');
  node.append(el('span', t('当前版本已保存，正在等待助手更新。')));
  const resume = el('button', t('继续手动编辑')); resume.type = 'button';
  resume.addEventListener('click', async () => {
    resume.disabled = true; pageState.composer.editSequence += 1;
    try { await uiBridge.invalidate(); releaseEditLease(); }
    catch { resume.disabled = false; notice(t('尚未撤回协作许可，连接恢复后可继续，或等待本次许可到期。'), true); }
  });
  node.append(resume); $('compose-dialog').append(node);
  pageState.composer.editLease = { node, timer: setTimeout(releaseEditLease, Math.max(0, operation.expiresAt - Date.now() + 100)) };
}
const uiBridge = createUiContextBridge({
  api, notice, available: () => !!pageState.lifecycle.csrf && !pageState.lifecycle.disposed && !pageState.lifecycle.localDataCleared,
  capture: () => ({
    ...(pageState.account.accountId && pageState.account.accountId !== '*' ? { accountId: pageState.account.accountId } : {}),
    view: accountConnection.active() ? 'connect' : $('compose-dialog').open ? 'compose' : document.body.dataset.workspace === 'settings' ? 'settings' : pageState.navigation.view,
    ...(pageState.navigation.view === 'inbox' ? { folder: $('folder').value || 'INBOX' } : {}),
    ...(pageState.reader.selectedMessageKey ? { selectedMessageRef: JSON.parse(pageState.reader.selectedMessageKey) } : {}),
    selectedMessageRefs: organizer.selectedRefs(),
    ...(pageState.composer.editor?.draft.id ? { selectedDraftId: pageState.composer.editor.draft.id, draftRevision: pageState.composer.editor.draft.revision } : {}),
    filters: { query: $('subject-search').value, unreadOnly: $('unread').checked, flaggedOnly: $('flagged-search').checked },
    editSequence: pageState.composer.editSequence, dirty: pageState.composer.dirty, saving: !!pageState.composer.saving, uploading: !!pageState.composer.pendingTransfer || hasUploads(),
  }),
  execute: async (operation) => {
    if (pageState.lifecycle.busy) return { status: 'blocked', result: { reason: 'busy' } };
    let ack = { status: 'failed', result: { reason: 'unavailable' } };
    await run(async () => {
      if (operation.kind === 'refresh') {
        if (pageState.composer.dirty || pageState.composer.saving || pageState.composer.pendingTransfer || hasUploads()) {
          notice(t('助手已更新草稿；当前输入已保留，请保存恢复副本后核对最新版本。'), true);
          ack = { status: 'blocked', result: { reason: 'changed' } };
          return;
        }
        if (operation.target.draftId) {
          if (operation.target.draftId === pageState.composer.editor?.draft.id) await openDraft(operation.target.draftId);
        } else {
          const wasSettings = document.body.dataset.workspace === 'settings';
          const previousAccount = pageState.account.accountId;
          await loadAccounts();
          if (pageState.account.accountId !== previousAccount && !pageState.composer.editor && !wasSettings) blankDetail();
          if (wasSettings) await accountWorkspace.open();
          else { await loadList(); if (!pageState.composer.editor && pageState.reader.selectedMessageKey) await openMessage(JSON.parse(pageState.reader.selectedMessageKey)); }
        }
        ack = { status: 'done', result: {} };
        return;
      }
      if (pageState.composer.saving) await pageState.composer.saving;
      if (pageState.composer.pendingTransfer || hasUploads()) {
        if (pageState.composer.editor && pageState.composer.dirty && !pageState.composer.pendingTransfer) await persistEditing('recovery', true);
        ack = { status: 'blocked', result: { reason: 'uploading' } };
        return;
      }
      if (pageState.composer.dirty && !pageState.composer.editor) {
        ack = { status: 'blocked', result: { reason: 'changed' } };
        return;
      }
      if (pageState.composer.editor) {
        const raw = editingContent();
        const valid = ['to', 'cc', 'bcc'].flatMap((key) => splitAddresses(raw[key]))
          .every((address) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(address));
        if (!valid) {
          if (pageState.composer.dirty || !hasRecovery()) await persistEditing('recovery', true);
          ack = { status: 'blocked', result: { reason: 'invalid_input', recoveryId: pageState.composer.editor.recovery.id } };
          return;
        }
        if (pageState.composer.dirty || !pageState.composer.editor.draft.id) await persistEditing('draft', true);
      }
      if (pageState.composer.dirty) { ack = { status: 'blocked', result: { reason: 'changed' } }; return; }
      const saved = pageState.composer.editor?.draft.id ? { draftId: pageState.composer.editor.draft.id, revision: pageState.composer.editor.draft.revision } : {};
      if (operation.kind === 'navigate') {
        const target = operation.target;
        const navigationAccount = target.accountId ?? target.messageRef?.accountId;
        if (navigationAccount && navigationAccount !== pageState.account.accountId) {
          // Agent navigation is local to this page; changing the default is a separate explicit tool.
          if (!pageState.account.accounts.some((account) => account.id === navigationAccount)) failure('ACCOUNT_NOT_FOUND');
          pageState.account.accountId = navigationAccount;
          $('account').value = pageState.account.accountId;
          pageState.inbox.folderScope = undefined;
          pageState.inbox.cursor = undefined;
          pageState.inbox.query = undefined;
          for (const id of searchFields) { if ($(id).type === 'checkbox') $(id).checked = false; else $(id).value = ''; }
          updateAccountLabel();
        }
        if (target.draftId) await openDraft(target.draftId);
        else if (target.batchId) await batchWorkspace.open(target.batchId);
        else if (target.messageRef) await openMessage(target.messageRef);
        else if (target.view === 'settings') await accountWorkspace.open();
        else if (target.view === 'maintenance') await storageWorkspace.open();
        else if (target.view === 'connect') await openSettings();
        else if (target.view === 'compose') await newComposer();
        else {
          selectView(target.view ?? 'inbox'); blankDetail();
          if (target.folder) { await loadFolderOptions(); $('folder').value = target.folder; }
          await loadList();
        }
      }
      if (operation.kind === 'flush') holdEditLease(operation);
      ack = { status: 'done', result: saved };
    });
    return ack;
  },
});
document.addEventListener('input', () => { pageState.composer.editSequence += 1; void uiBridge.publish(); });

$('storage').addEventListener('click', () => {
  void run(storageWorkspace.open);
});

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function button(text, action, className) {
  const node = el('button', text, className);
  node.type = 'button';
  node.addEventListener('click', () => {
    void run(action);
  });
  return node;
}
function localButton(text, action, className) {
  const node = el('button', text, className);
  node.type = 'button';
  node.dataset.localOperation = 'true';
  node.addEventListener('click', async () => {
    if (node.disabled) return;
    node.disabled = true;
    node.setAttribute('aria-busy', 'true');
    const idleContent = [...node.childNodes];
    node.textContent = tt`${text}中…`;
    try {
      await action();
    } catch (error) {
      notice(errors[error?.code] ?? t('此项操作未完成，可以重试。'), true);
    } finally {
      node.disabled = false;
      node.removeAttribute('aria-busy');
      node.replaceChildren(...idleContent);
    }
  });
  return node;
}
function hasUploads() {
  return Boolean(pageState.composer.editor?.uploads?.pending());
}
function notice(text, error = false) {
  if (pageState.lifecycle.localDataCleared) return;
  $('notice').textContent = text;
  $('notice').className = error ? 'error' : '';
  $('notice').setAttribute('role', error ? 'alert' : 'status');
  $('compose-notice').textContent = $('compose-dialog').open ? text : '';
  $('compose-notice').className = error ? 'error' : '';
  $('compose-notice').setAttribute('role', error ? 'alert' : 'status');
}
function date(value) {
  return formatProductTime(value, { preset: 'common-precise', locale: localeTag() }) || t('时间未知');
}
function bytes(value) {
  return value < 1024
    ? `${value} B`
    : value < 1024 * 1024
      ? `${(value / 1024).toFixed(1)} KiB`
      : `${(value / 1024 / 1024).toFixed(1)} MiB`;
}
function failure(code) {
  const error = new Error(code);
  error.code = code;
  throw error;
}
async function api(route, value = {}, signal) {
  if (pageState.lifecycle.localDataCleared) failure('SERVICE_CLOSED');
  let result;
  try { result = await pageClient.call(route, value, signal); }
  catch (error) {
    if (['EMAIL_SYNC_AUTH_REQUIRED', 'EMAIL_SYNC_ACCOUNT_CHANGED', 'EMAIL_SYNC_CONFLICT', 'EMAIL_SYNC_CORRUPT',
      'ACCOUNT_REQUIRED', 'ACCOUNT_NOT_FOUND', 'SERVICE_CLOSED', 'SERVICE_RESTARTED', 'SESSION_STALE',
      'MAILBOX_AUTH_FAILED', 'STALE_MESSAGE', 'MESSAGE_NOT_FOUND'].includes(error.code)) { messagePreloader.stop(); messageReader.clear(); }
    throw error;
  }
  if (['messages/move', 'work/set'].includes(route)) messageReader.clear();
  if (route === 'messages/flag') messageReader.update(value.ref, value.flag === 'seen' ? { unread: !value.value } : { flagged: value.value });
  if (pageState.lifecycle.localDataCleared) failure('SERVICE_CLOSED');
  return result;
}
function navigate(action) {
  if (pageState.lifecycle.busy) { pageState.navigation.pendingNavigation = action; return; }
  return run(action);
}
async function run(action) {
  messagePreloader.stop();
  if (pageState.lifecycle.busy || pageState.lifecycle.localDataCleared) return;
  let invalidField;
  pageState.lifecycle.busy = true;
  activity(t('正在处理…'));
  document.body.setAttribute('aria-busy', 'true');
  updateEditorLock();
  try {
    await action();
  } catch (error) {
    if (error?.code === 'FORM_INVALID') invalidField = error.fieldId;
    if (vaultErrors.has(error?.code)) accountConnection.unlock(error, async () => {
      await loadAccounts();
      if (!pageState.composer.dirty && !pageState.composer.pendingTransfer) await loadList();
      await openDraftTarget();
    });
    notice(
      (error?.code === 'FORM_INVALID' ? error.message : errors[error?.code] ?? t('操作未完成。请核对连接和当前状态；未保存的编辑仍保留在页面中。')) +
        (pageState.composer.pendingTransfer ? t(' 可核对保存状态，或取消本次保存并保留当前编辑。') : ''),
      true,
    );
  } finally {
    pageState.lifecycle.busy = false;
    if ($('activity')) $('activity').hidden = true;
    document.body.removeAttribute('aria-busy');
    updateEditorLock();
    if (invalidField) {
      $(invalidField)?.focus();
      $(invalidField)?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
    }
    if (pageState.navigation.pendingNavigation && !pageState.lifecycle.disposed) {
      const next = pageState.navigation.pendingNavigation; pageState.navigation.pendingNavigation = undefined;
      void run(next);
    } else if (pageState.navigation.pendingWorkbenchTarget && pageState.lifecycle.csrf && !pageState.lifecycle.disposed) {
      pageState.navigation.pendingWorkbenchTarget = false;
      void run(openDraftTarget);
    }
  }
}
// Refresh feedback outlives run()'s short interaction lock. Only the current
// operation may finish it; navigation and page disposal retire older feedback.
function beginRefresh() {
  const operation = {};
  refreshOperation = operation;
  $('refresh').disabled = true;
  $('refresh').setAttribute('aria-busy', 'true');
  $('refresh').setAttribute('aria-label', t('刷新中…'));
  $('refresh-label').textContent = t('刷新中…');
  $('refresh-status').textContent = t('正在刷新…');
  $('refresh-status').removeAttribute('title');
  $('refresh-status').classList.remove('error');
  return operation;
}
function resetRefresh() {
  refreshOperation = undefined;
  $('refresh').disabled = pageState.lifecycle.localDataCleared;
  $('refresh').removeAttribute('aria-busy');
  $('refresh').setAttribute('aria-label', t('刷新'));
  $('refresh-label').textContent = t('刷新');
  $('refresh-status').textContent = '';
  $('refresh-status').removeAttribute('title');
  $('refresh-status').classList.remove('error');
}
function finishRefresh(operation, failed = false) {
  if (refreshOperation !== operation || pageState.lifecycle.disposed || pageState.lifecycle.localDataCleared) return;
  resetRefresh();
  $('refresh-status').textContent = failed ? t('刷新未完成，可重试') : t('刷新完成');
  $('refresh-status').classList.toggle('error', failed);
  if (!failed) $('refresh-status').title = tt`最近刷新：${date(Date.now())}`;
}
async function waitForInbox(jobs, generation, operation) {
  const completed = Promise.allSettled(jobs).then(() => {
    if (!pageState.requests.current('inbox', generation)) return;
    finishRefresh(operation, [...pageState.inbox.mailboxPages.values()].some((page) => page.error));
  });
  // Release the global interaction lock, not the refresh operation itself.
  await Promise.race([completed, new Promise((resolve) => setTimeout(resolve, 250))]);
}
function inboxScope() {
  return JSON.stringify([pageState.account.accountId, pageState.inbox.query]);
}
function activity(text) {
  $('activity-label').textContent = text;
  $('activity').hidden = false;
}
async function leaveEditor() {
  if (pageState.composer.saving) await pageState.composer.saving.catch(() => {});
  if ((!pageState.composer.dirty || hasRecovery()) && !pageState.composer.pendingTransfer && !hasUploads()) {
    $('compose-dialog').close();
    return true;
  }
  const dialog = $('discard-dialog');
  dialog.returnValue = 'stay';
  const canSaveDraft = Boolean(pageState.composer.editor && $('editor'));
  $('discard-save').hidden = !canSaveDraft;
  $('discard-title').textContent = canSaveDraft ? t('保存这封邮件？') : t('离开未保存的编辑？');
  $('discard-subject').textContent = $('draft-subject')?.value || $('merge-title')?.value || t('未保存的编辑');
  $('discard-recipient').hidden = !canSaveDraft;
  $('discard-recipient').textContent = $('draft-to')?.value || t('尚未填写收件人');
  $('discard-save').disabled = Boolean(pageState.composer.pendingTransfer || hasUploads());
  $('discard-description').textContent = $('discard-save').disabled
    ? t('附件尚未完成上传，请继续编辑并处理上传后再保存。')
    : t('还有未保存的修改。保存后可在草稿中继续编辑。');
  if (!canSaveDraft) $('discard-description').textContent = t('当前修改尚未保存，离开后不会保留。');
  dialog.showModal();
  const choice = await new Promise((resolve) =>
    dialog.addEventListener('close', () => resolve(dialog.returnValue), { once: true }),
  );
  if (choice === 'save') {
    if (!canSaveDraft) return false;
    const owner = pageState.composer.editor;
    await saveDraft();
    // A failed/uncertain save or a newer edit must never dismiss the content.
    if (pageState.composer.editor !== owner || pageState.composer.dirty || pageState.composer.pendingTransfer || hasUploads()) return false;
    $('compose-dialog').close();
    return true;
  }
  if (choice !== 'discard') return false;
  if (pageState.composer.editor?.recovery?.revision)
    await api('recoveries/discard', { id: pageState.composer.editor.recovery.id, revision: pageState.composer.editor.recovery.revision });
  pageState.composer.dirty = false;
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.pendingTransfer = undefined;
  $('compose-dialog').close();
  return true;
}
function blankDetail() {
  releaseEditLease();
  disposeReader();
  delete $('detail').dataset.accountManagement;
  mailMergeWorkspace.dispose();
  accountWorkspace.dispose();
  pageState.requests.invalidate('reader');
  pageState.reader.selectedMessageKey = undefined;
  $('compose-dialog').close();
  $('compose-detail').replaceChildren();
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.editor?.rich?.destroy();
  pageState.composer.editor = undefined;
  delete $('detail').dataset.batch;
  clearTimeout(pageState.composer.autosaveTimer);
  document.body.dataset.screen = 'list';
  renderEmptyDetail();
}
function renderEmptyDetail(state) {
  const content = {
    inbox: [t('选择一封邮件'), t('在列表中选择邮件，查看正文或起草回复。')],
    work: [t('选择一项待办'), t('打开待处理邮件，阅读内容或继续回复。')],
    workEmpty: [t('暂无工作项'), t('在收件箱打开邮件，可加入待处理或标记为已检查。')],
    draftsEmpty: [t('暂无草稿'), t('写一封邮件，或让助手为你准备。')],
    sentEmpty: [t('暂无发送记录'), t('确认发送后，可在这里查看结果。')],
    drafts: [t('选择一份草稿'), t('打开草稿继续编辑，或点击“写邮件”开始。')],
    sent: [t('选择一条发送记录'), t('查看发送结果与对应邮件。')],
    batches: [t('选择一项批量任务'), t('查看收件人清单、发送进度和结果。')],
    loading: [t('正在读取邮箱'), t('邮件加载后会出现在左侧列表。')],
    empty: [t('没有匹配邮件'), t('调整搜索条件，或切换邮箱与文件夹。')],
    failed: [t('邮件暂未加载'), t('请在列表中重试。')],
  };
  const [title, description] = content[state ?? pageState.navigation.view] ?? content.inbox;
  const empty = el('div', undefined, 'empty detail-empty');
  empty.append(icon('mail'), el('h2', title), el('p', description));
  if (!state && ['inbox', 'work'].includes(pageState.navigation.view)) empty.append(el('p', t('打开正文后自动标为已读。'), 'privacy-note'));
  if (state === 'workEmpty') empty.append(button(t('去收件箱'), () => navigate(async () => { selectView('inbox'); blankDetail(); await loadList(); }), 'primary'));
  if (state === 'draftsEmpty') empty.append(button(t('写邮件'), () => $('compose').click(), 'primary'));
  $('detail').replaceChildren(empty);
}

function showDetail() {
  document.body.dataset.screen = 'detail';
  const heading = $('detail').querySelector('h2');
  if (!heading) return;
  heading.tabIndex = -1;
  document.querySelector('.reader').scrollTop = 0;
  heading.focus({ preventScroll: true });
}
function showSettings() {
  pageState.navigation.settingsReturn ??= { view: pageState.navigation.view, messageRef: pageState.reader.selectedMessageKey ? JSON.parse(pageState.reader.selectedMessageKey) : undefined };
  if (document.body.dataset.workspace !== 'settings') resetRefresh();
  document.body.dataset.workspace = 'settings';
  document.querySelector('.reader').hidden = false;
  pageState.requests.invalidate('inbox');
  pageState.requests.invalidate('list');
  newMail.hidden = true;
  organizer.clear(); organizer.hide();
  for (const name of Object.keys(viewNames)) $(`${name}-tab`).setAttribute('aria-pressed', 'false');
  $('settings').setAttribute('aria-pressed', 'true');
  showDetail();
}
async function returnToMailbox() {
  if (!(await leaveEditor())) return;
  const target = pageState.navigation.settingsReturn ?? { view: 'inbox' };
  pageState.navigation.settingsReturn = undefined;
  selectView(target.view);
  blankDetail();
  await loadList();
  if (target.messageRef && target.messageRef.accountId === pageState.account.accountId) await openMessage(target.messageRef);
}
function updateAccountLabel() {
  $('account-address').textContent =
    pageState.account.accountId === '*'
      ? tt`${pageState.account.accounts.length} 个已连接邮箱`
      : (pageState.account.accounts.find((item) => item.id === pageState.account.accountId)?.address ?? '');
  document.querySelector('.account-label').hidden = !pageState.account.accounts.length && !pageState.account.historyAccounts.length;
  const trigger = $('account-trigger');
  const menu = $('account-menu');
  const accounts = [...pageState.account.accounts, ...pageState.account.historyAccounts];
  const current = accounts.find((item) => item.id === pageState.account.accountId);
  const name = accountPreference(current?.id)?.label || current?.label || t('邮箱');
  trigger.replaceChildren(icon('mail'));
  if (name !== current?.address) trigger.append(el('strong', name, 'account-name'));
  trigger.append(el('span', current?.address ?? t('选择邮箱'), 'account-trigger-address'), icon('chevronDown'));
  trigger.title = tt`切换邮箱：${current?.address ?? ''}`;
  menu.replaceChildren(el('p', t('切换邮箱'), 'account-menu-heading'));
  for (const account of accounts) {
    const historical = !pageState.account.accounts.some((item) => item.id === account.id);
    const label = accountPreference(account.id)?.label || account.label;
    const option = el('button', undefined, 'account-option'); option.type = 'button';
    option.addEventListener('click', () => {
      $('account-picker').open = false;
      void navigate(() => changeAccount(account.id));
    });
    option.setAttribute('aria-label', `${label === account.address ? '' : `${label} `}${account.address}${historical ? t(' · 本地历史') : ''}`);
    option.setAttribute('aria-pressed', String(account.id === pageState.account.accountId));
    const identity = el('span', undefined, 'account-option-identity');
    identity.append(el('strong', label), el('small', historical ? tt`${account.address} · 本地历史` : account.address));
    option.append(icon('mail'), identity);
    if (account.id === pageState.account.accountId) option.append(icon('check'));
    menu.append(option);
  }
  const add = el('button', t('添加邮箱'), 'account-add'); add.type = 'button';
  add.addEventListener('click', () => {
    $('account-picker').open = false;
    void navigate(() => changeAccount('__add'));
  });
  decorateAction(add, 'plus'); menu.append(add);
  $('account-summary').hidden = true;
  $('account-links').hidden = true;
  $('account-links').replaceChildren();
  $('account-list-label').hidden = true;
}
function selectView(next) {
  resetRefresh();
  delete document.body.dataset.workspace;
  pageState.navigation.settingsReturn = undefined;
  $('settings').setAttribute('aria-pressed', 'false');
  document.querySelectorAll('.search-advanced, #list-options, #account-picker').forEach((node) => { node.open = false; });
  newMail.hidden = true;
  pageState.requests.invalidate('inbox');
  pageState.requests.invalidate('list');
  pageState.requests.invalidate('reader');
  organizer.clear();
  organizer.hide();
  pageState.navigation.view = next;
  pageState.inbox.cursor = undefined;
  pageState.composer.draftSelection.clear();
  updateSelection();
  for (const name of Object.keys(viewNames))
    $(`${name}-tab`).setAttribute('aria-pressed', String(pageState.navigation.view === name));
  $('list-title').textContent = viewNames[pageState.navigation.view];
  $('search').hidden = pageState.navigation.view !== 'inbox' || !pageState.account.accountId;
  $('mail-filters').hidden = pageState.navigation.view !== 'inbox' || !pageState.account.accountId;
  $('work-filter-label').hidden = pageState.navigation.view !== 'work' || !pageState.account.accountId;
  $('more').hidden = true;
}
function updateSelection() {
  $('selection-bar').hidden = !pageState.composer.draftSelection.size || pageState.navigation.view !== 'drafts';
  $('selection-count').textContent = tt`已选择 ${pageState.composer.draftSelection.size} 封`;
}
async function loadAccounts(current = () => true) {
  const generation = ++accountsGeneration;
  const previousAccount = pageState.account.accountId;
  const [result, savedPreferences, draftsResult] = await Promise.all([
    api('accounts/list'), api('accounts/preferences'),
    api('drafts/list').then(value => ({ value }), error => ({ error })),
  ]);
  if (!current() || generation !== accountsGeneration || pageState.lifecycle.disposed) return false;
  if (!Array.isArray(result)) failure('INVALID_RESPONSE');
  if (draftsResult.error && (result.length || draftsResult.error.code !== 'ACCOUNT_REQUIRED')) throw draftsResult.error;
  const historicalDrafts = draftsResult.value ?? [];
  if (JSON.stringify(result) !== JSON.stringify(pageState.account.accounts)) messageReader.clear();
  accountsSyncedAt = Date.now();
  if (!Array.isArray(savedPreferences.accounts)) failure('INVALID_RESPONSE');
  const previousDefault = pageState.account.preferences.defaultAccountId;
  pageState.account.preferences = savedPreferences;
  pageState.account.accounts = result;
  if (pageState.account.accountId !== '*' && (!pageState.account.accountsLoaded || !pageState.account.accountId || pageState.account.accountId === previousDefault))
    pageState.account.accountId = savedPreferences.defaultAccountId ?? pageState.account.accounts[0]?.id ?? '';
  pageState.account.accountsLoaded = true;
  pageState.account.historyAccounts = [
    ...new Map(
      historicalDrafts
        .filter((draft) => !pageState.account.accounts.some((account) => account.id === draft.accountId))
        .map((draft) => [
          draft.accountId,
          {
            id: draft.accountId,
            address: draft.senderSnapshot?.address ?? t('已移除账号'),
            label: draft.senderSnapshot?.label ?? t('本地历史'),
          },
        ]),
    ).values(),
  ];
  const scopes = [...pageState.account.accounts, ...pageState.account.historyAccounts];
  if (!(pageState.account.accountId === '*' && scopes.length > 1) && !scopes.some((item) => item.id === pageState.account.accountId))
    pageState.account.accountId = scopes[0]?.id ?? '';
  if (previousAccount !== pageState.account.accountId) {
    pageState.requests.invalidate('inbox'); pageState.inbox.folderScope = undefined; pageState.inbox.cursor = undefined; pageState.inbox.query = undefined;
    for (const id of searchFields) { if ($(id).type === 'checkbox') $(id).checked = false; else $(id).value = ''; }
  }
  rememberAccountScope(pageState.account.accountId);
  $('account').replaceChildren(
    ...pageState.account.accounts.map((item) => {
      const preference = accountPreference(item.id);
      const label = preference?.label || item.label;
      const option = el(
        'option',
        `${preference?.group ? `${preference.group} / ` : ''}${label === item.address ? item.address : `${label} · ${item.address}`}`,
      );
      option.value = item.id;
      return option;
    }),
  );
  if (pageState.account.historyAccounts.length) {
    const group = el('optgroup');
    group.label = t('已移除邮箱的本地历史');
    for (const mailbox of pageState.account.historyAccounts) {
      const option = el('option', tt`${mailbox.address} · 本地历史`);
      option.value = mailbox.id;
      group.append(option);
    }
    $('account').append(group);
  }
  if (!scopes.length) {
    const option = el('option', t('尚未连接邮箱'));
    option.value = '';
    $('account').append(option);
  }
  const addAccount = el('option', t('＋ 添加邮箱…'));
  addAccount.value = '__add';
  $('account').append(addAccount);
  $('account').value = pageState.account.accountId;
  const connectedScope =
    pageState.account.accounts.some((item) => item.id === pageState.account.accountId) || (pageState.account.accountId === '*' && pageState.account.accounts.length > 0);
  if (!connectedScope && ['inbox', 'work'].includes(pageState.navigation.view) && pageState.account.historyAccounts.length)
    selectView('sent');
  updateAccountLabel();
  document.body.dataset.accounts = pageState.account.accountId ? 'connected' : 'empty';
  $('search').hidden = pageState.navigation.view !== 'inbox' || !pageState.account.accountId;
  $('mail-filters').hidden = pageState.navigation.view !== 'inbox' || !pageState.account.accountId;
  $('work-filter-label').hidden = pageState.navigation.view !== 'work' || !pageState.account.accountId;
  $('compose').hidden = !connectedScope;
  $('preferences').hidden = true;
  $('inbox-tab').hidden = !pageState.account.accounts.length;
  $('work-tab').hidden = !connectedScope;
  for (const name of ['drafts', 'sent', 'batches']) $(`${name}-tab`).hidden = !pageState.account.accountId;
  document.querySelector('.reader').hidden = !pageState.account.accountId;
  $('list-title').textContent = !pageState.account.accountId ? t('连接邮箱') : viewNames[pageState.navigation.view];
  return true;
}
function renderActiveFilters() {
  const unread = $('unread').checked;
  const starred = $('flagged-search').checked;
  for (const tab of document.querySelectorAll('[data-mail-filter]')) {
    const selected = tab.dataset.mailFilter === 'all' ? !unread && !starred : tab.dataset.mailFilter === 'unread' ? unread : starred;
    tab.setAttribute('aria-pressed', String(selected));
  }
  const labels = { 'from-search':t('发件人'), 'to-search':t('收件人'), 'text-search':t('仅主题'), 'since-search':t('开始'), 'until-search':t('截止'), 'flagged-search':t('仅星标'), 'attachments-search':t('含附件或图片') };
  let chips = $('active-filters');
  if (!chips) { chips = el('div', undefined, 'active-filters'); chips.id = 'active-filters'; document.querySelector('.search-fields').append(chips); }
  chips.replaceChildren();
  for (const [id, label] of Object.entries(labels)) {
    const input = $(id); const value = input.type === 'checkbox' ? input.checked : input.value;
    if (!value) continue;
    const chip = button(`${label}${input.type === 'checkbox' ? '' : `：${value}`} ×`, async () => {
      if (input.type === 'checkbox') input.checked = false; else input.value = '';
      organizer.clear(); pageState.inbox.cursor = undefined; pageState.inbox.query = undefined; await loadList();
    });
    chip.setAttribute('aria-label', tt`移除筛选：${label}`); chips.append(chip);
  }
  chips.hidden = !chips.childElementCount || pageState.navigation.view !== 'inbox';
  const summary = document.querySelector('.search-advanced > summary');
  const filterName = tt`筛选${chips.childElementCount ? ` (${chips.childElementCount})` : ''}`;
  summary.setAttribute('aria-label', filterName); summary.title = filterName;
  summary.replaceChildren(icon('filter'));
  if (chips.childElementCount) summary.append(el('span', String(chips.childElementCount), 'filter-count'));
}
async function loadList(more = false) {
  messagePreloader.stop();
  messageReader.cancelPrefetch();
  const generation = pageState.requests.invalidate('list');
  const current = () => pageState.requests.current('list', generation);
  const operation = beginRefresh();
  renderActiveFilters();
  if (!more) newMail.hidden = true;
  const label = more ? t('正在加载更多邮件…') : tt`正在加载${viewNames[pageState.navigation.view]}…`;
  activity(label);
  $('items').setAttribute('aria-busy', 'true');
  $('items').inert = true;
  if (!more) { pageState.requests.invalidate('inbox'); $('more').hidden = true; }
  try {
    const pending = await readList(more, current);
    if (!current()) return;
    if (pending) await waitForInbox(pending.jobs, pending.generation, operation);
    else finishRefresh(operation);
  } catch (error) {
    if (!current()) return;
    finishRefresh(operation, true);
    if (!more) {
      const failed = el('div', undefined, 'empty load-failure');
      failed.append(
        el('h3', tt`${viewNames[pageState.navigation.view]}加载失败`),
        el('p', errors[error?.code] ?? t('暂时无法完成读取，请稍后重试。')),
        button(t('重试加载'), () => loadList()),
      );
      $('items').replaceChildren(failed);
      $('scope').textContent = t('未能完成加载');
    }
    throw error;
  } finally {
    if (current() && (pageState.navigation.view !== 'inbox' || ![...pageState.inbox.mailboxPages.values()].some((page) => page.loading))) {
      $('items').removeAttribute('aria-busy');
      $('items').inert = false;
    }
  }
}
async function readList(more = false, current = () => true) {
  if (!pageState.account.accountId) {
    const empty = el('div', undefined, 'empty onboarding');
    const brand = el('div', undefined, 'onboarding-brand');
    brand.append(icon('mail'), el('strong', t('邮箱助手')));
    const mark = el('div', undefined, 'onboarding-symbol'); mark.append(icon('mail'));
    const connect = button(t('连接邮箱'), () => openSettings(), 'primary');
    decorateAction(connect, 'plus');
    const preparation = el('section', undefined, 'onboarding-preparation');
    const steps = el('ol', undefined, 'onboarding-steps');
    steps.append(el('li', t('在服务商设置中开启 IMAP / SMTP')), el('li', t('准备邮箱授权码或应用密码')));
    preparation.append(el('p', t('连接前准备'), 'muted'), steps);
    const help = button(t('查看连接方式'), () => openSettings(), 'quiet');
    empty.append(brand, mark, el('h2', t('连接你的第一个邮箱')),
      el('p', t('阅读邮件、起草回复和批量通知，都在一个工作台。')), connect, preparation, help);
    $('items').replaceChildren(empty);
    $('scope').textContent = '';
    $('more').hidden = true;
    notice(t('尚未连接邮箱。支持范围取决于服务商的 IMAP/SMTP 和登录策略。'));
    return;
  }
  notice(t('正在读取…'));
  if (pageState.navigation.view === 'work') {
    if (!more) {
      pageState.inbox.workCursor = undefined;
    }
    const page = await api('work/list', {
      ...(pageState.account.accountId === '*' ? {} : { accountId: pageState.account.accountId }),
      status: $('work-filter').value,
      ...(more && pageState.inbox.workCursor ? { before: pageState.inbox.workCursor } : {}),
    }, pageState.requests.signal('list'));
    if (!current()) return;
    if (!Array.isArray(page.items)) failure('INVALID_RESPONSE');
    if (!more) $('items').replaceChildren();
    for (const item of page.items) {
      const row = button(
        '',
        async () => {
          if (await leaveEditor()) await openMessage(item.ref, row);
        },
        'item',
      );
      const subject = el('span', undefined, 'subject-line');
      const state = el('span', $('work-filter').value === 'pending' ? t('待处理') : t('已检查'), 'inline-state');
      state.dataset.status = $('work-filter').value;
      subject.append(el('strong', item.subject || t('（无主题）')), state);
      row.append(
        subject,
        el('span', item.from.join(', '), 'muted'),
        el('time', date(item.timestampMs)),
      );
      row.append(
        el(
          'span',
          pageState.account.accounts.find((account) => account.id === item.ref.accountId)?.address,
          'account-badge',
        ),
      );
      $('items').append(row);
    }
    pageState.inbox.workCursor = page.nextBefore;
    $('more').hidden = !pageState.inbox.workCursor;
    $('more').textContent = t('继续读取工作项');
    if (!$('items').childElementCount)
      $('items').append(
        el(
          'div',
          $('work-filter').value === 'pending'
            ? t('没有待处理项。打开邮件后加入待处理，或让助手按你的要求整理。')
            : t('还没有标记为已检查的邮件。'),
          'empty',
        ),
      );
    if (!pageState.reader.selectedMessageKey && $('detail').querySelector('.detail-empty'))
      renderEmptyDetail($('items').querySelector('button.item') ? 'work' : 'workEmpty');
    $('scope').textContent = tt`${$('items').querySelectorAll('button.item').length} 条已载入工作项`;
    notice(t('工作状态保存在本机，独立于邮箱未读状态。这里只列出已标记的邮件。'));
    return;
  }
  $('more').textContent = t('继续查询更早邮件');
  if (pageState.navigation.view === 'batches') {
    await batchWorkspace.list(current, pageState.requests.signal('list'));
    return;
  }
  if (pageState.navigation.view === 'drafts' || pageState.navigation.view === 'sent') {
    const [drafts, recoveries] = await Promise.all([
      api('drafts/list', undefined, pageState.requests.signal('list')),
      pageState.navigation.view === 'drafts' ? api('recoveries/list', undefined, pageState.requests.signal('list')) : [],
    ]);
    if (!current()) return;
    if (!Array.isArray(drafts)) failure('INVALID_RESPONSE');
    const visibleRecoveries = recoveries.filter(
      (item) => pageState.account.accountId === '*' || item.accountId === pageState.account.accountId,
    );
    const selected = drafts.filter(
      (item) =>
        !visibleRecoveries.some((backup) => backup.basedOn?.id === item.id) &&
        (pageState.account.accountId === '*' || item.accountId === pageState.account.accountId) &&
        (pageState.navigation.view === 'sent'
          ? ['sending', 'sent', 'unknown'].includes(item.status)
          : !['sending', 'sent', 'unknown'].includes(item.status)),
    );
    for (const id of pageState.composer.draftSelection.keys())
      if (
        !selected.some(
          (item) =>
            item.id === id && item.revision === pageState.composer.draftSelection.get(id) && item.status === 'draft',
        )
      )
        pageState.composer.draftSelection.delete(id);
    $('items').replaceChildren(
      ...selected.map((item) => {
        const wrapper = el('div', undefined, 'draft-row');
        if (item.status === 'draft') {
          wrapper.dataset.selectable = 'true';
          const check = el('input');
          check.type = 'checkbox';
          check.checked = pageState.composer.draftSelection.has(item.id);
          check.setAttribute('aria-label', tt`选择草稿：${item.subject || t('无主题')}`);
          check.addEventListener('change', () => {
            if (check.checked) pageState.composer.draftSelection.set(item.id, item.revision);
            else pageState.composer.draftSelection.delete(item.id);
            updateSelection();
          });
          wrapper.append(check);
        }
        const row = button(
          '',
          async () => {
            if (await leaveEditor()) {
              await openDraft(item.id);
              selectRow(row);
            }
          },
          'item',
        );
        const meta = el('span', undefined, 'item-heading');
        const shortState = { sent: t('已提交邮件服务器'), sending: t('投递中'), unknown: t('结果不确定'), pending_confirmation: t('待确认') };
        const status = el('span', shortState[item.status] ?? states[item.status], 'item-state');
        status.title = states[item.status];
        status.dataset.status = item.status;
        const recipients = el('span', item.to?.join(', ') || t('未填写收件人'), 'draft-recipients');
        recipients.title = recipients.textContent;
        meta.append(recipients, el('time', date(item.updatedAt)));
        // Preparation origin remains available in the opened draft, not the list's identity row.
        row.title = item.subject || t('（无主题）');
        prepareMessageIntent(row, item);
        const subjectLine = el('span', undefined, 'subject-line');
        subjectLine.append(el('strong', item.subject || t('（无主题）')), status);
        row.append(meta, subjectLine);
        if (pageState.account.accountId === '*')
          row.append(
            el(
              'span',
              pageState.account.accounts.find((a) => a.id === item.accountId)?.address ??
                item.senderSnapshot?.address ??
                t('已移除账号'),
              'account-badge',
            ),
          );
        wrapper.append(row);
        return wrapper;
      }),
    );
    if (visibleRecoveries.length) {
      const section = el('section', undefined, 'recovery-list');
      section.append(el('h3', t('可恢复的编辑')));
      for (const recovery of visibleRecoveries) {
        const row = button(
          '',
          async () => {
            if (await leaveEditor()) await openRecovery(recovery.id);
          },
          'item',
        );
        row.append(
          el('span', t('已自动备份 · 待补全'), 'item-state'),
          el('strong', recovery.subject || t('（未填写主题）')),
          el('time', date(recovery.updatedAt)),
        );
        section.append(row);
      }
      $('items').prepend(section);
    }
    if (!selected.length && !visibleRecoveries.length)
      $('items').append(
        el(
          'div',
          pageState.navigation.view === 'drafts'
            ? t('还没有草稿。写一封邮件，或让助手为你准备。')
            : t('还没有发送记录。确认后的投递状态会保存在这里。'),
          'empty',
        ),
      );
    $('scope').textContent =
      tt`${selected.length} 条${pageState.navigation.view === 'drafts' ? t('本地草稿') : t('本地投递记录')}${visibleRecoveries.length ? tt` · ${visibleRecoveries.length} 份可恢复编辑` : ''}`;
    $('more').hidden = true;
    updateSelection();
    if (!selected.length && !visibleRecoveries.length && $('detail').querySelector('.detail-empty')) renderEmptyDetail(pageState.navigation.view === 'drafts' ? 'draftsEmpty' : 'sentEmpty');
    notice(
      pageState.navigation.view === 'drafts'
        ? t('可以选择多封已保存草稿，集中预览并在工作台确认。')
        : t('SMTP 接受不等于收件人已收到；结果不明的邮件不会自动重发。'),
    );
    return;
  }
  if (!more) {
    await loadFolderOptions(current);
    if (!current()) return;
    pageState.inbox.query = {
      folder: $('folder').value.trim() || 'INBOX',
      query: $('subject-search').value,
      from: $('from-search').value,
      to: $('to-search').value,
      subject: $('text-search').value,
      flaggedOnly: $('flagged-search').checked,
      hasAttachments: $('attachments-search').checked,
      ...dateFilters(),
      unreadOnly: $('unread').checked,
      limit: 20,
    };
    pageState.inbox.mailboxPages.clear();
    pageState.inbox.loadedMessages = pageState.inbox.loadedMessages.filter((item) => item.ref.accountId === pageState.account.accountId && item.ref.folder === pageState.inbox.query.folder);
    pageState.inbox.mailboxPages.set(pageState.account.accountId, { replacePending: true });
  }
  const targets = pageState.account.accounts
    .filter((a) => pageState.account.accountId === '*' || a.id === pageState.account.accountId)
    .filter((a) => !more || pageState.inbox.mailboxPages.get(a.id)?.cursor || pageState.inbox.mailboxPages.get(a.id)?.error);
  const generation = pageState.requests.invalidate('inbox');
  const jobs = targets.map((account) => fetchInboxPage(account, generation, more));
  if (pageState.inbox.loadedMessages.length && !$('items').querySelector('.inline-error')) updateInboxLoading();
  else renderInboxRows();
  return { jobs, generation };
}
async function fetchInboxPage(account, generation, more) {
  const id = account.id;
  const previous = pageState.inbox.mailboxPages.get(id);
  const replace = !more || previous?.replacePending;
  const capturedQuery = { ...pageState.inbox.query };
  pageState.inbox.mailboxPages.set(id, { ...previous, loading: true, error: undefined });
  try {
    const page = await api('messages/list', {
      ...capturedQuery,
      accountId: id,
      ...(!replace && more ? previous?.cursor : {}),
    }, pageState.requests.signal('inbox'));
    if (!pageState.requests.current('inbox', generation) || pageState.navigation.view !== 'inbox') return;
    if (!Array.isArray(page.messages) || typeof page.uidValidity !== 'string')
      failure('INVALID_RESPONSE');
    pageState.inbox.mailboxPages.set(id, {
      cursor: page.nextBeforeUid
        ? { beforeUid: page.nextBeforeUid, uidValidity: page.uidValidity }
        : undefined,
      uidValidity: page.uidValidity,
      unreadCount: page.unreadCount,
      totalMessages: page.totalMessages,
    });
    pageState.inbox.resultScope = inboxScope();
    if (replace) pageState.inbox.loadedMessages = pageState.inbox.loadedMessages.filter((item) => item.ref.accountId !== id);
    for (const item of page.messages) {
      const existing = pageState.inbox.loadedMessages.findIndex(
        (old) => JSON.stringify(old.ref) === JSON.stringify(item.ref),
      );
      if (existing < 0) pageState.inbox.loadedMessages.push(item);
      else pageState.inbox.loadedMessages[existing] = item;
    }
  } catch (error) {
    if (!pageState.requests.current('inbox', generation) || pageState.navigation.view !== 'inbox') return;
    if (error?.code === 'STALE_MESSAGE' && more && !replace) {
      pageState.inbox.mailboxPages.set(id, { replacePending: true });
      await fetchInboxPage(account, generation, false);
      return;
    }
    pageState.inbox.mailboxPages.set(id, { ...previous, replacePending: replace, error: error?.code ?? 'MAILBOX_UNAVAILABLE' });
  } finally {
    if (pageState.requests.current('inbox', generation) && pageState.navigation.view === 'inbox') renderInboxRows();
  }
}
function renderInboxRows() {
  pageState.inbox.loadedMessages.sort(
    (a, b) => (b.timestampMs ?? 0) - (a.timestampMs ?? 0) || b.ref.uid - a.ref.uid,
  );
  $('items').replaceChildren();
  for (const [id, state] of pageState.inbox.mailboxPages)
    if (state.error) {
      const error = el('div', undefined, 'inline-error');
      error.append(
        el('strong', pageState.account.accounts.find((a) => a.id === id)?.address),
        el('p', errors[state.error] ?? t('此邮箱未能完成查询。')),
        ...(state.replacePending && pageState.inbox.loadedMessages.length ? [el('p', t('以下为上次载入的邮件，当前查询尚未完成。'))] : []),
        button(t('重试此邮箱'), async () => {
          const account = pageState.account.accounts.find((item) => item.id === id);
          if (!account || refreshOperation) return;
          const operation = beginRefresh();
          const generation = pageState.requests.generation('inbox');
          const job = fetchInboxPage(account, generation, true);
          renderInboxRows();
          await waitForInbox([job], generation, operation);
        }),
      );
      $('items').append(error);
    }
  for (const item of pageState.inbox.loadedMessages) {
    const row = button(
      '',
      async () => {
        if (await leaveEditor()) await openMessage(item.ref, row);
      },
      'item',
    );
    const heading = el('span', undefined, 'item-heading');
    heading.append(el('span', item.from.join(', '), 'sender'), el('time', date(item.timestampMs)));
    const subjectLine = el('span', undefined, 'subject-line');
    subjectLine.append(el('strong', item.subject || t('（无主题）')));
    row.append(heading, subjectLine);
    row.dataset.messageKey = JSON.stringify(item.ref);
    if (row.dataset.messageKey === pageState.reader.selectedMessageKey) row.setAttribute('aria-current', 'true');
    row.title = item.subject || t('（无主题）');
    prepareMessageIntent(row, item);
    updateMessageRow(row, item);
    if (pageState.account.accountId === '*')
      row.append(
        el('span', pageState.account.accounts.find((a) => a.id === item.ref.accountId)?.address, 'account-badge'),
      );
    $('items').append(organizer.row(item, row));
  }
  const loading = updateInboxLoading();
  pageState.inbox.cursor = [...pageState.inbox.mailboxPages.values()].some((page) => page.cursor && !page.error);
  $('more').hidden = !pageState.inbox.cursor;
  const failed = [...pageState.inbox.mailboxPages.values()].filter((page) => page.error).length;
  if (!$('items').children.length) {
    const empty = el('div', undefined, 'list-empty');
    empty.append(el('h3', loading ? t('正在加载邮件…') : t('没有匹配邮件')), el('p', loading ? t('首次读取可能需要一点时间。') : pageState.inbox.cursor ? t('可继续查询更早邮件，或调整筛选条件。') : t('试试其他关键词或清除筛选。')));
    if (!loading) empty.append(button(t('清除筛选'), () => $('reset-search').click()));
    $('items').append(empty);
  }
  if ($('detail').querySelector('.detail-empty') && !pageState.reader.selectedMessageKey)
    renderEmptyDetail(pageState.inbox.loadedMessages.length ? undefined : loading ? 'loading' : failed ? 'failed' : 'empty');
  updateInboxScope();
  if (!loading && !failed) prepareReadingWindow();
  if ($('compose-dialog').open) return;
  notice(
    loading
      ? ($('items').inert ? t('正在查询当前范围…') : t('正在查询当前邮箱，已加载邮件可以打开。'))
      : failed
        ? t('查询未完成，已加载结果可能不完整，可重试。')
        : pageState.inbox.cursor
          ? t('已读取当前范围，可以继续查询更早邮件。')
          : t('本次查询已到末尾。'),
    Boolean(failed),
  );
}

function updateInboxLoading() {
  const loading = [...pageState.inbox.mailboxPages.values()].some((page) => page.loading);
  // Old rows remain readable only while refreshing the same mailbox/query.
  $('items').inert = loading && pageState.inbox.resultScope !== inboxScope();
  if (loading) $('items').setAttribute('aria-busy', 'true');
  else $('items').removeAttribute('aria-busy');
  $('more').disabled = loading;
  return loading;
}

function updateInboxScope() {
  if (pageState.navigation.view !== 'inbox' || !pageState.inbox.query) return;
  if (
    !pageState.inbox.loadedMessages.length &&
    [...pageState.inbox.mailboxPages.values()].some((page) => page.loading) &&
    [...pageState.inbox.mailboxPages.values()].every((page) => page.loading)
  ) {
    $('scope').textContent = t('正在加载收件箱…');
    return;
  }
  const failed = [...pageState.inbox.mailboxPages.values()].filter((page) => page.error).length;
  const unread = pageState.inbox.loadedMessages.filter((message) => message.unread).length;
  const folder = $('folder').selectedOptions[0]?.textContent || pageState.inbox.query.folder;
  const completed = [...pageState.inbox.mailboxPages.values()].filter((page) => !page.loading && !page.error);
  const totalUnread =
    completed.length && completed.every((page) => Number.isInteger(page.unreadCount))
      ? completed.reduce((total, page) => total + page.unreadCount, 0)
      : undefined;
  $('scope').title =
    tt`${pageState.account.accountId === '*' ? tt`全部 ${pageState.account.accounts.length} 个邮箱` : folder} · 已加载 ${pageState.inbox.loadedMessages.length} 封 · ${unread} 封未读${totalUnread === undefined ? '' : tt` · ${completed.length < pageState.inbox.mailboxPages.size ? t('已连接部分') : t('当前文件夹')}共 ${totalUnread} 封未读`}${failed ? tt` · ${failed} 个账号未完成` : ''}`;
  $('scope').textContent = tt`已加载 ${pageState.inbox.loadedMessages.length} 封 · ${unread} 封未读${failed ? tt` · ${failed} 个邮箱未完成` : ''}`;
}

function updateMessageRow(initialRow, message) {
  let row = initialRow;
  if (!row?.isConnected && row?.dataset.messageKey)
    row =
      [...$('items').querySelectorAll('[data-message-key]')].find(
        (node) => node.dataset.messageKey === JSON.stringify(message.ref),
      ) ?? row;
  if (!row) return;
  row.dataset.unread = String(message.unread);
  row.querySelector('.unread-badge')?.remove();
  row.querySelector('.star-badge')?.remove();
  // Preserve sender, time, and account in the accessible name as flags change.
  row.removeAttribute('aria-label');
  if (message.unread) {
    const marker = el('span', undefined, 'unread-badge');
    marker.append(el('span', t('未读'), 'sr-only'));
    marker.title = t('未读');
    row.prepend(marker);
  }
  row.querySelector('.message-meta')?.remove();
  row.querySelector('.work-badge')?.remove();
  if (message.flagged) { const marker = el('span', undefined, 'star-badge'); marker.append(icon('starred'), el('span', t('星标'), 'sr-only')); row.append(marker); }
  if (message.workStatus === 'pending' || (message.workStatus === 'done' && pageState.navigation.view === 'work')) {
    const meta = el('span', undefined, 'message-meta');
    const state = el('span', undefined, 'work-badge');
    state.dataset.status = message.workStatus;
    state.append(icon(message.workStatus === 'pending' ? 'work' : 'check'),
      el('span', message.workStatus === 'pending' ? t('待处理') : t('已检查')));
    meta.append(state); row.append(meta);
  }
  const cached = pageState.inbox.loadedMessages.find(
    (item) => JSON.stringify(item.ref) === JSON.stringify(message.ref),
  );
  if (cached) {
    const page = pageState.inbox.mailboxPages.get(message.ref.accountId);
    if (cached.unread !== message.unread && Number.isInteger(page?.unreadCount))
      page.unreadCount = Math.max(0, page.unreadCount + (message.unread ? 1 : -1));
    Object.assign(cached, { unread: message.unread, flagged: message.flagged, workStatus: message.workStatus });
  }
}

async function loadFolderOptions(current = () => true) {
  const account = pageState.account.accounts.find((item) => item.id === pageState.account.accountId);
  const scope = pageState.account.accountId === '*' ? '*' : `${pageState.account.accountId}:${account?.connectionRevision ?? 1}`;
  if (pageState.inbox.folderScope === scope) return;
  if (pageState.inbox.folderScope) pageState.inbox.folderChoices.set(pageState.inbox.folderScope, $('folder').value);
  // loadList keeps previous rows inert until this account's folder is resolved.
  const folders =
    pageState.account.accountId === '*'
      ? [{ path: 'INBOX', role: 'inbox' }]
      : (pageState.inbox.folderCache.get(scope) ?? (await api('messages/folders', { accountId: pageState.account.accountId }, pageState.requests.signal('list'))));
  if (!current()) return;
  if (
    !Array.isArray(folders) ||
    !folders.length ||
    folders.some((item) => typeof item.path !== 'string')
  )
    failure('INVALID_RESPONSE');
  const names = {
    inbox: t('收件箱'),
    sent: t('服务商已发送'),
    drafts: t('服务商草稿'),
    trash: t('已删除'),
    junk: t('垃圾邮件'),
    archive: t('归档'),
    all: t('所有邮件'),
  };
  $('folder').replaceChildren(
    ...folders.map((folder) => {
      const option = el(
        'option',
        names[folder.role] ? `${names[folder.role]} · ${folder.path}` : folder.path,
      );
      option.value = folder.path;
      return option;
    }),
  );
  const previous = pageState.inbox.folderChoices.get(scope);
  $('folder').value = folders.some((item) => item.path === previous)
    ? previous
    : (folders.find((item) => item.role === 'inbox') ?? folders[0]).path;
  pageState.inbox.folderCache.set(scope, folders);
  pageState.inbox.folderScope = scope;
}

function selectRow(initialRow) {
  let row = initialRow;
  if (row?.dataset.messageKey) {
    pageState.reader.selectedMessageKey = row.dataset.messageKey;
    row =
      [...$('items').querySelectorAll('[data-message-key]')].find(
        (node) => node.dataset.messageKey === pageState.reader.selectedMessageKey,
      ) ?? row;
  }
  for (const node of $('items').querySelectorAll('[aria-current]'))
    node.removeAttribute('aria-current');
  row?.setAttribute('aria-current', 'true');
}
function prepareReadingWindow(ref) {
  const items = pageState.inbox.loadedMessages;
  const index = ref ? items.findIndex(item => JSON.stringify(item.ref) === JSON.stringify(ref)) : -1;
  const candidates = index < 0 ? items.slice(0, 3) : [...items.slice(index + 1, index + 3), ...items.slice(Math.max(0, index - 1), index)];
  messagePreloader.schedule(candidates);
}
function prepareMessageIntent(row, item) {
  // Intent-only, at most one small message. Never fetch an entire mailbox or remote images.
  const cancel = () => clearTimeout(prefetchTimer);
  const prepare = () => {
    cancel();
    if (!Number.isFinite(item.size) || item.size > 256 * 1024) return;
    prefetchTimer = setTimeout(() => {
      if (!row.isConnected || pageState.lifecycle.busy || pageState.lifecycle.disposed ||
          pageState.composer.editor || document.visibilityState === 'hidden') return;
      messagePreloader.stop();
      void messageReader.prefetch(item.ref);
    }, 300);
  };
  row.addEventListener('pointerenter', prepare);
  row.addEventListener('focus', prepare);
  row.addEventListener('pointerleave', cancel);
  row.addEventListener('blur', cancel);
}
async function openMessage(ref, row) {
  clearTimeout(prefetchTimer);
  disposeReader();
  const generation = pageState.requests.invalidate('reader');
  const signal = pageState.requests.signal('reader');
  const current = () => pageState.requests.current('reader', generation);
  selectRow(row);
  pageState.reader.selectedMessageKey = JSON.stringify(ref);
  const loading = el('div', undefined, 'reader-loading');
  loading.setAttribute('role', 'status');
  loading.append(
    el('span', undefined, 'loading-spinner'),
    el('h2', t('正在读取邮件正文…')),
    el('p', t('可以继续选择其他邮件。')),
  );
  if (!messageReader.peek(ref)) $('detail').replaceChildren(loading);
  showDetail();
  const job = readMessage(ref, row, current, signal)
    .catch((error) => {
      if (!current()) return;
      const failed = el('div', undefined, 'empty load-failure');
      failed.append(
        el('h2', t('正文未能加载')),
        el('p', errors[error.code] ?? t('请检查连接后重试。')),
        button(t('重新读取正文'), () => openMessage(ref, row)),
      );
      $('detail').replaceChildren(failed);
      notice(t('正文未能加载，邮件仍保留原来的未读状态。'), true);
    });
  await Promise.race([job, new Promise((resolve) => setTimeout(resolve, 50))]);
}
async function readMessage(ref, row, current, signal) {
  const cached = messageReader.peek(ref);
  const message = await messageReader.load(ref);
  if (!current()) return;
  // Flags come from the latest loaded list; cached content must not restore old unread badges.
  const summary = pageState.inbox.loadedMessages.find(item => JSON.stringify(item.ref) === JSON.stringify(ref));
  if (cached && summary) Object.assign(message, { unread: summary.unread, flagged: summary.flagged, ...(summary.workStatus === undefined ? {} : { workStatus: summary.workStatus }) });
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.editor?.rich?.destroy();
  pageState.composer.editor = undefined;
  delete $('detail').dataset.batch;
  pageState.composer.dirty = false;
  updateMessageRow(row, message);
  updateInboxScope();
  selectRow(row);
  const detail = $('detail');
  const header = el('header', undefined, 'mail-heading');
  const readState = el('p', message.unread ? t('未读邮件') : t('已读邮件'), 'eyebrow read-state');
  readState.dataset.unread = String(message.unread);
  const subjectLine = el('div', undefined, 'subject-line');
  const workLabel = el('span', undefined, 'inline-state');
  subjectLine.append(el('h2', message.subject || t('（无主题）')), workLabel);
  header.append(readState, subjectLine);
  const senderCard = el('div', undefined, 'sender-card');
  senderCard.append(
    avatar(el, message.from[0]),
    envelope(el, [
      [t('发件人'), message.from.join(', ')],
      [t('收件人'), message.to.join(', ')],
      [t('抄送'), message.cc.join(', ')],
      [t('时间'), date(message.timestampMs)],
    ]),
  );
  detail.replaceChildren(header, senderCard);
  const plainBody = el('pre', message.text || t('（无纯文本正文）'), 'message-body');
  const formatted = renderIsolatedMessage(message.formattedBody, {
    text: message.text,
    onUnavailable: () => { if (current()) { plainBody.hidden = false; if (formatted) formatted.hidden = true; notice(t('排版阅读器暂未加载，已显示完整纯文本。'), true); } },
    imageUrl: async (source) => {
      if (!current()) failure('SERVICE_CLOSED');
      if (!source.startsWith('cid:')) {
        const image = await api('images/remote', { ref: message.ref, source }, signal);
        if (!attachmentAccess.isImage(image)) failure('INVALID_RESPONSE');
        const imageBytes = Uint8Array.from(atob(image.contentBase64), (char) => char.charCodeAt(0));
        if (!current()) failure('SERVICE_CLOSED');
        const url = URL.createObjectURL(new Blob([imageBytes], { type: image.contentType }));
        pageState.reader.images.add(url);
        return url;
      }
      const contentId = decodeURIComponent(source.slice(4));
      const matching = message.attachments.filter((asset) => asset.contentId === contentId);
      if (matching.length !== 1) failure('ATTACHMENT_NOT_FOUND');
      const saved = await api('attachments/import', { ref: message.ref, index: matching[0].index }, signal);
      const readerAccess = createAttachmentAccess({ api: (route, value) => api(route, value, signal), sha256, el, notice });
      pageState.reader.assets.add(readerAccess);
      if (!current()) { readerAccess.dispose(); failure('SERVICE_CLOSED'); }
      return readerAccess.imageUrl(saved.id);
    },
  });
  pageState.reader.frame = formatted;
  if (formatted) {
    const controls = el('div', undefined, 'format-controls');
    const toggle = button(t('查看纯文本'), async () => {
      formatted.hidden = !formatted.hidden;
      plainBody.hidden = !formatted.hidden;
      toggle.textContent = formatted.hidden ? t('查看保留排版') : t('查看纯文本');
    });
    controls.append(toggle, el('span', t('保留邮件原有排版；图片自动加载，失败可单独重试。'), 'muted'));
    plainBody.hidden = true;
    detail.append(controls, formatted, plainBody);
  } else {
    if (message.formattedBody?.limited)
      detail.append(el('p', t('原邮件排版较复杂，已使用完整纯文本显示。'), 'muted'));
    detail.append(plainBody);
  }
  const attachmentsSection = el('section', undefined, 'mail-attachments');
  if (message.attachments.length) attachmentsSection.append(el('h3', tt`附件 ${message.attachments.length}`));
  for (const attachment of message.attachments) {
    const item = el('div', undefined, 'attachment');
    item.append(...attachmentIdentity(attachment, el, bytes));
    const download = localButton(t('下载附件'), async () => {
      const saved = await api('attachments/import', { ref: message.ref, index: attachment.index });
      await downloadAttachment(saved.id);
    });
    if (attachmentAccess.canPreview(attachment))
      item.append(
        localButton(t('预览'), async () => {
          const saved = await api('attachments/import', {
            ref: message.ref,
            index: attachment.index,
          });
          if (!current()) return;
          await attachmentAccess.preview(saved);
        }),
      );
    decorateAction(download, 'download', true);
    download.setAttribute('aria-label', tt`下载附件：${attachment.filename}`);
    download.title = attachment.bytes > MAX_ATTACHMENT ? t('附件超过 10 MiB，请在服务商邮箱下载') : tt`下载 ${attachment.filename}`;
    download.disabled = attachment.bytes > MAX_ATTACHMENT;
    item.append(download);
    attachmentsSection.append(item);
  }
  if (message.attachments.length) detail.append(attachmentsSection);
  const actions = el('div', undefined, 'actions');
  const prepareQuote = async (kind) => {
    const signature = await loadSignature(accountPreference(message.ref.accountId), api);
    return prepareQuotedMessage(message, kind, {
      api,
      date,
      signature: signature.text,
      signatureHtml: signature.html,
      signatureAttachments: signature.attachments,
    });
  };
  const quoteNotice = (quote, text) =>
    notice(
      `${text}${quote.remoteImages ? t(' 原邮件外部图片保留为链接，可核对后自行插入图片。') : ''}`,
    );
  actions.append(
    button(t('回复'), async () => {
      const quote = await prepareQuote('reply');
      const to = (message.replyTo?.length ? message.replyTo : message.from).filter(
        (address) => !/[<>]/u.test(address),
      );
      await renderEditor(
        {
          content: {
            accountId: message.ref.accountId,
            to,
            cc: [],
            bcc: [],
            subject: /^Re:/iu.test(message.subject) ? message.subject : `Re: ${message.subject}`,
            text: quote.text,
            html: quote.html,
            attachmentIds: quote.attachments.map((asset) => asset.id),
            replyToMessage: message.ref,
          },
        },
        quote.attachments,
      );
      pageState.composer.dirty = true;
      quoteNotice(quote, t('已保留原邮件上下文，请在引用上方回复并核对收件人。'));
    }),
  );
  actions.append(
    button(t('回复全部'), async () => {
      const quote = await prepareQuote('reply');
      const own = new Set(pageState.account.accounts.map((account) => account.address.toLowerCase()));
      const unique = (values) => [
        ...new Map(
          values
            .filter((address) => !/[<>]/u.test(address) && !own.has(address.toLowerCase()))
            .map((address) => [address.toLowerCase(), address]),
        ).values(),
      ];
      const to = unique([
        ...(message.replyTo?.length ? message.replyTo : message.from),
        ...message.to,
      ]);
      const cc = unique(message.cc).filter(
        (address) => !to.some((value) => value.toLowerCase() === address.toLowerCase()),
      );
      await renderEditor(
        {
          content: {
            accountId: message.ref.accountId,
            to,
            cc,
            bcc: [],
            subject: /^Re:/iu.test(message.subject) ? message.subject : `Re: ${message.subject}`,
            text: quote.text,
            html: quote.html,
            attachmentIds: quote.attachments.map((asset) => asset.id),
            replyToMessage: message.ref,
          },
        },
        quote.attachments,
      );
      pageState.composer.dirty = true;
      quoteNotice(quote, t('已保留原邮件上下文，请核对回复全部的收件人和抄送。'));
    }),
    button(t('转发'), async () => {
      const quote = await prepareQuote('forward');
      await renderEditor(
        {
          content: {
            accountId: message.ref.accountId,
            to: [],
            cc: [],
            bcc: [],
            subject: /^Fwd:/iu.test(message.subject) ? message.subject : `Fwd: ${message.subject}`,
            text: quote.text,
            html: quote.html,
            attachmentIds: quote.attachments.map((asset) => asset.id),
          },
        },
        quote.attachments,
      );
      pageState.composer.dirty = true;
      quoteNotice(
        quote,
        tt`已保留转发正文与 ${quote.attachments.length} 个附件，请填写收件人并核对内容。`,
      );
    }),
  );
  const flags = el('div', undefined, 'actions');
  const applyReadState = (unread) => {
    message.unread = unread;
    messageReader.update(message.ref, { unread });
    updateMessageRow(row, message);
    updateInboxScope();
    // A completed background sync must not update another open message.
    if (!current()) return;
    markRead.textContent = unread ? t('标为已读') : t('标为未读');
    readState.textContent = unread ? t('未读邮件') : t('已读邮件');
    readState.dataset.unread = String(unread);
    header.querySelector('.read-sync-error')?.remove();
  };
  const setRead = async (seen) => {
    const key = JSON.stringify(message.ref);
    // Reopening shares a matching mutation; opposite explicit changes stay ordered.
    let pending = pendingReadFlags.get(key);
    if (!pending || pending.seen !== seen) {
      const previous = pending;
      if (previous) previous.superseded = true;
      pending = { seen, confirmedUnread: previous?.confirmedUnread ?? message.unread };
      const operation = pending;
      operation.promise = (previous ? previous.promise.catch(() => {}) : Promise.resolve())
        .then(() => api('messages/flag', { ref: message.ref, flag: 'seen', value: seen }))
        .then(() => {
          operation.confirmedUnread = !seen;
          const latest = pendingReadFlags.get(key);
          if (latest) latest.confirmedUnread = !seen;
        });
      pendingReadFlags.set(key, operation);
    }
    markRead.disabled = true;
    applyReadState(!seen);
    try { await pending.promise; }
    catch (error) {
      if (!pending.superseded) applyReadState(pending.confirmedUnread);
      throw error;
    } finally {
      if (pendingReadFlags.get(key) === pending) pendingReadFlags.delete(key);
      markRead.disabled = false;
    }
    // A later explicit change owns the displayed state now.
    if (pending.superseded || !current()) return;
    if (pageState.navigation.view === 'inbox' && $('unread').checked && seen) {
      pageState.inbox.loadedMessages = pageState.inbox.loadedMessages.filter(item => JSON.stringify(item.ref) !== key);
      organizer.clear();
      renderInboxRows();
    }
  };
  const markRead = button(message.unread ? t('标为已读') : t('标为未读'), async () => {
    const seen = message.unread;
    await setRead(seen);
    notice(seen ? t('已同步为已读。') : t('已同步为未读。'));
  });
  const star = button(message.flagged ? t('取消星标') : t('加星标'), async () => {
    const value = !message.flagged;
    await api('messages/flag', { ref: message.ref, flag: 'flagged', value });
    message.flagged = value;
    messageReader.update(message.ref, { flagged: value });
    updateMessageRow(row, message);
    star.textContent = value ? t('取消星标') : t('加星标');
    notice(value ? t('已同步星标。') : t('已取消星标。'));
  });
  actions.append(markRead);
  flags.append(star);
  const updateWorkLabel = () => {
    workLabel.hidden = !['pending', 'done'].includes(message.workStatus);
    workLabel.dataset.status = message.workStatus;
    workLabel.textContent = message.workStatus === 'pending' ? t('待处理') : t('已检查');
  };
  updateWorkLabel();
  const setWork = async (status) => {
    await api('work/set', { ref: message.ref, status });
    message.workStatus = status;
    updateWorkLabel();
    updateMessageRow(row, message);
    workAction.textContent = message.workStatus === 'pending' ? t('标记已检查') : t('加入待处理');
    decorateAction(workAction, 'work');
    if (pageState.navigation.view === 'work') await loadList();
    notice(t('工作状态已保存，没有改变邮箱未读状态。'));
  };
  const workAction = button(message.workStatus === 'pending' ? t('标记已检查') : t('加入待处理'), () => setWork(message.workStatus === 'pending' ? 'done' : 'pending'));
  const replyAction = actions.firstElementChild;
  replyAction.classList.add('primary');
  const extra = el('details', undefined, 'message-more');
  const extraActions = el('div', undefined, 'actions');
  extra.append(el('summary', t('更多操作')), extraActions);
  // Reply-all and forward remain available beside the common organization controls.
  for (const action of [...actions.children]) if (action !== markRead && action !== replyAction) extraActions.append(action);
  extraActions.append(markRead, star);
  extraActions.append(button(t('清除工作标记'), () => setWork('none')));
  setupActionMenu(extra);
  const organization = organizer.controls(message);
  const [move, archive, trash] = organization.children;
  decorateAction(move, 'folder', true); decorateAction(archive, 'archive', true); decorateAction(trash, 'delete', true);
  decorateAction(workAction, 'work');
  actions.replaceChildren(replyAction, archive, move, trash, workAction, extra);
  actions.classList.add('message-actions');
  detail.insertBefore(actions, header);
  showDetail();
  await formatted?.bodyReady;
  if (!current()) return;
  if (message.unread || pendingReadFlags.get(JSON.stringify(ref))?.seen === true) {
    try { await setRead(true); if (current()) notice(t('已打开邮件并同步为已读。')); }
    catch {
      if (!current()) return;
      const warning = el('div', undefined, 'read-sync-error'); warning.setAttribute('role', 'status');
      warning.append(el('span', t('正文已打开，已读状态同步失败。')), button(t('重试标为已读'), async () => { await setRead(true); notice(t('已同步为已读。')); }));
      header.append(warning);
      notice(t('已读状态尚未同步，未读标记保留，可重试。'), true);
    }
  } else notice(t('已打开邮件。'));
  if (current()) prepareReadingWindow(ref);
}
async function openDraft(id) {
  pageState.requests.invalidate('reader');
  const draft = await api('drafts/read', { id });
  const attachments = [];
  for (const attachmentId of draft.content.attachmentIds) {
    const {
      id: attachmentIdValue,
      filename,
      contentType,
      bytes: attachmentBytes,
      sha256: digest,
    } = await api('attachments/read', {
      id: attachmentId,
      offset: 0,
    });
    attachments.push({
      id: attachmentIdValue,
      filename,
      contentType,
      bytes: attachmentBytes,
      sha256: digest,
    });
  }
  pageState.composer.pendingTransfer = undefined;
  pageState.composer.dirty = false;
  if (['sending', 'sent', 'unknown'].includes(draft.status)) {
    renderDelivery(draft, attachments);
    notice(t('正在查看本机发送记录。正文和附件为投递时的固定内容。'));
  } else if (!pageState.account.accounts.some((account) => account.id === draft.content.accountId)) {
    blankDetail();
    const detail = $('detail');
    detail.replaceChildren(
      el('h2', draft.content.subject || t('（无主题）')),
      el(
        'p',
        tt`此草稿属于已移除的邮箱：${draft.senderSnapshot?.address ?? t('历史账号')}。原始内容保留在本机。`,
        'review-note',
      ),
      renderDraftBody(draft.content, { imageUrl: draftImageUrl }),
    );
    if (draft.senderSnapshot?.address)
      detail.append(
        button(t('重新连接此邮箱'), () => openSettings({ address: draft.senderSnapshot.address })),
      );
    if (pageState.account.accounts.length) {
      const label = el('label', t('使用其他邮箱另存为新邮件'));
      const select = el('select');
      select.append(el('option', t('请选择发件邮箱')));
      select.firstElementChild.value = '';
      for (const account of pageState.account.accounts) {
        const option = el('option', account.address);
        option.value = account.id;
        select.append(option);
      }
      label.append(select);
      detail.append(
        label,
        button(t('另存为新草稿'), async () => {
          if (!pageState.account.accounts.some((account) => account.id === select.value)) failure('INVALID_INPUT');
          const content = { ...draft.content };
          delete content.replyToMessage;
          await renderEditor({ content: { ...content, accountId: select.value } }, attachments);
          pageState.composer.dirty = true;
          updateDraftStatus();
          notice(t('已复制为新草稿，请核对新的发件邮箱、签名与收件人。原草稿保留在历史中。'));
        }),
      );
    }
    showDetail();
  } else {
    await renderEditor(draft, attachments);
    notice(t('已读取最新草稿。编辑后会自动保存，发送前仍需核对确认。'));
  }
}
async function openRecovery(id, asNew = false) {
  const backup = await api('recoveries/read', { id });
  let draft;
  if (backup.basedOn && !asNew) {
    try {
      draft = await api('drafts/read', { id: backup.basedOn.id });
    } catch (error) {
      if (error.code !== 'DRAFT_NOT_FOUND') throw error;
    }
    if (
      !draft ||
      draft.revision !== backup.basedOn.revision ||
      ['queued', 'sending', 'sent', 'unknown'].includes(draft.status)
    ) {
      blankDetail();
      const detail = $('detail');
      detail.replaceChildren(
        el('h2', t('核对恢复内容')),
        el(
          'p',
          t('原草稿已变化或已进入发送流程。恢复内容不会覆盖原记录；另存前请核对，避免重复发送。'),
          'readonly-warning',
        ),
        renderDraftBody(backup.content, { imageUrl: draftImageUrl }),
        button(t('恢复为新草稿'), () => openRecovery(id, true)),
        button(t('删除这份恢复内容'), async () => {
          await api('recoveries/discard', { id, revision: backup.revision });
          blankDetail();
          await loadList();
        }),
      );
      showDetail();
      return;
    }
  }
  const attachments = await Promise.all(
    backup.content.attachmentIds.map(async (assetId) => {
      const asset = await api('attachments/read', { id: assetId, offset: 0 });
      delete asset.contentBase64;
      return asset;
    }),
  );
  const content = {
    ...backup.content,
    ...Object.fromEntries(
      ['to', 'cc', 'bcc'].map((key) => [key, splitAddresses(backup.content[key])]),
    ),
  };
  await renderEditor({ ...(draft ?? {}), content }, attachments);
  for (const key of ['to', 'cc', 'bcc']) $(`draft-${key}`).value = backup.content[key];
  pageState.composer.editor.recovery = {
    id: backup.id,
    revision: backup.revision,
    snapshot: JSON.stringify(editingContent()),
  };
  pageState.composer.dirty = true;
  updateDraftStatus();
  updateEditorLock();
  notice(t('已恢复完整编辑内容，请补全并核对收件人。保存为草稿后才能预览发送。'));
}
function renderDelivery(draft, attachments) {
  $('compose-dialog').close();
  $('compose-detail').replaceChildren();
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.editor?.rich?.destroy();
  pageState.composer.editor = undefined;
  clearTimeout(pageState.composer.autosaveTimer);
  clearTimeout(pageState.composer.draftPoll);
  delete $('detail').dataset.batch;
  $('detail').replaceChildren(
    deliveryView(draft, attachments, {
      el,
      button,
      localButton,
      canPreview: attachmentAccess.canPreview,
      previewAttachment: attachmentAccess.preview,
      date,
      bytes,
      imageUrl: draftImageUrl,
      sender:
        draft.senderSnapshot?.address ??
        pageState.account.accounts.find((item) => item.id === draft.content.accountId)?.address,
      checkCopy: pageState.account.accounts.some((account) => account.id === draft.content.accountId)
        ? async () => {
            await api('drafts/sent-copy', { id: draft.id });
            await openDraft(draft.id);
          }
        : undefined,
      download: downloadAttachment,
      refresh: () => openDraft(draft.id),
    }),
  );
  showDetail();
}
function setupActionMenu(menu, decorate = true) {
  menu.classList.add('action-menu');
  const summary = menu.querySelector('summary');
  let pendingFocus;
  menu.addEventListener('toggle', () => {
    const focus = pendingFocus;
    pendingFocus = undefined;
    if (menu.open) focus?.();
  });
  if (decorate) summary.prepend(icon('more'));
  const symbols = { [t('插入此邮箱签名')]: 'edit', [t('重新读取')]: 'refresh', [t('查询发送状态')]: 'info', [t('删除草稿')]: 'delete', [t('查看原邮件')]: 'mail', [t('回复全部')]: 'reply', [t('转发')]: 'sent', [t('清除工作标记')]: 'check' };
  for (const action of menu.querySelectorAll('button')) {
    if (action.textContent === t('删除草稿')) action.classList.add('destructive');
    if (symbols[action.textContent]) decorateAction(action, symbols[action.textContent]);
  }
  menu.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopPropagation(); pendingFocus = undefined; menu.open = false; summary.focus();
    } else if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
      event.preventDefault();
      const choices = [...menu.querySelectorAll('button:not(:disabled)')].filter((node) => !node.hidden);
      const origin = document.activeElement;
      const index = choices.indexOf(origin);
      const next = index < 0 ? (event.key === 'ArrowDown' ? 0 : choices.length - 1) : (index + (event.key === 'ArrowDown' ? 1 : choices.length - 1)) % choices.length;
      const focus = () => {
        if (menu.isConnected && menu.open && (document.activeElement === origin || menu.contains(document.activeElement))) choices[next]?.focus();
      };
      const panel = menu.querySelector(':scope > :not(summary)');
      if (menu.open && (!panel?.hasAttribute('popover') || panel.matches(':popover-open'))) focus();
      else {
        // The document's toggle listener puts the panel in the top layer first.
        // Until then its buttons are hidden and the browser ignores focus().
        pendingFocus = focus;
        menu.open = true;
      }
    }
  });
  menu.addEventListener('click', (event) => {
    if (event.target.closest('button')) { menu.open = false; summary.focus({ preventScroll: true }); }
  });
}
function field(labelText, id, value, tag = 'input') {
  const label = el('label', labelText);
  const input = el(tag);
  input.id = id;
  input.value = value;
  label.append(input);
  return label;
}
function senderOptions() {
  return pageState.account.accounts.map((account) => {
    const option = el('option', account.address);
    option.value = account.id;
    return option;
  });
}
function createSenderFields(selectedId) {
  const fromLabel = el('label', t('发件邮箱'));
  const selector = el('select');
  selector.id = 'draft-from';
  selector.append(...senderOptions());
  selector.value = selectedId;
  selector.addEventListener('change', () => {
    pageState.composer.editor.draft.content.accountId = selector.value;
    notice(
      tt`已切换发件邮箱，请检查正文中的签名。${pageState.composer.editor.draft.content.replyToMessage ? t('回复仍保留原邮件会话，请核对新的发件身份。') : ''}`,
    );
    pageState.composer.dirty = true;
    updateDraftStatus();
    updateEditorLock();
    scheduleAutosave();
  });
  selector.setAttribute('aria-describedby', 'sender-help');
  fromLabel.append(selector);
  fromLabel.className = 'compose-line';
  const senderHelp = el('details', undefined, 'sender-help');
  const helpToggle = el('summary', t('发件说明'));
  const helpContent = el('p', t('仅用于此邮件，不改变默认邮箱。切换顶部邮箱不会改变已有草稿的发件人。'));
  helpContent.id = 'sender-help';
  senderHelp.append(helpToggle, helpContent);
  return [fromLabel, senderHelp];
}
function refreshEditorSenders() {
  if (!pageState.composer.editor || !$('editor')) return;
  const selector = $('draft-from');
  if (selector) {
    selector.replaceChildren(...senderOptions());
    selector.value = pageState.composer.editor.draft.content.accountId;
  } else if (pageState.account.accounts.length > 1) {
    $('editor').querySelector('.composer-from')?.replaceWith(...createSenderFields(pageState.composer.editor.draft.content.accountId));
  }
  updateEditorLock();
}
async function renderEditor(draft, attachments) {
  releaseEditLease();
  // Load optional signature resources before replacing an existing editor.
  const initialSignature =
    !draft.id && !draft.content.text && !draft.content.html
      ? await loadSignature(accountPreference(draft.content.accountId), api)
      : undefined;
  mailMergeWorkspace.dispose();
  accountWorkspace.dispose();
  pageState.requests.invalidate('reader');
  delete $('detail').dataset.batch;
  clearTimeout(pageState.composer.autosaveTimer);
  pageState.composer.autosaveBlocked = false;
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.editor?.rich?.destroy();
  pageState.composer.editor = { draft, attachments, recovery: { id: crypto.randomUUID(), revision: 0 } };
  if (initialSignature) {
    Object.assign(draft.content, {
      text: initialSignature.text,
      ...(initialSignature.html ? { html: initialSignature.html } : {}),
    });
    for (const asset of initialSignature.attachments)
      if (!attachments.some((item) => item.id === asset.id)) attachments.push(asset);
    draft.content.attachmentIds = attachments.map((asset) => asset.id);
  }
  const locked = ['sending', 'sent', 'unknown'].includes(draft.status);
  const detail = $('compose-detail');
  $('draft-status')?.remove();
  detail.replaceChildren();
  $('compose-title').textContent = draft.id ? t('编辑草稿') : t('写邮件');
  const form = el('form', undefined, 'editor');
  form.id = 'editor';
  if (draft.preparedBy === 'assistant')
    form.append(
      el(
        'p',
        tt`助手起草${draft.editedBy === 'user' ? t(' · 你已修改') : ''}。请核对收件人、事实和附件后再发送。`,
        'draft-origin',
      ),
    );
  const originalMessage = draft.content.replyToMessage ? button(t('查看原邮件'), async () => {
    if (!(await leaveEditor())) return;
    await openMessage(draft.content.replyToMessage);
  }) : undefined;
  const from = pageState.account.accounts.find((item) => item.id === draft.content.accountId);
  const senderLine = el('div', undefined, 'compose-sender');
  form.append(senderLine);
  if (pageState.account.accounts.length > 1) senderLine.append(...createSenderFields(draft.content.accountId));
  else senderLine.append(el('p', tt`发件人：${from?.address ?? t('账号已断开')}`, 'composer-from'));
  senderLine.append(button(t('添加邮箱'), () => openSettings(), 'quiet'));
  const status = el(
    'p',
    draft.id ? tt`${states[draft.status]} · 版本 ${draft.revision}` : t('新草稿 · 尚未保存'),
    'status',
  );
  status.id = 'draft-status';
  $('compose-title').after(status);
  status.setAttribute('role', 'status');
  if (locked)
    form.append(
      el(
        'p',
        draft.status === 'unknown'
          ? t('存在重复投递风险。先核对服务商邮箱和本地发送记录，不要重新发送。')
          : t('该记录已进入投递流程，不能再编辑。'),
        'readonly-warning',
      ),
    );
  const recipients = el('div', undefined, 'recipient-fields');
  const recipientOptions = el('div', undefined, 'recipient-options');
  for (const [key, label] of [
    ['to', t('收件人 To')],
    ['cc', t('抄送 Cc')],
    ['bcc', t('密送 Bcc')],
  ]) {
    const recipient = field(label, `draft-${key}`, draft.content[key].join(', '));
    recipient.className = 'compose-line';
    recipient.id = `recipient-${key}`;
    const addressInput = recipient.querySelector('input');
    addressInput.placeholder =
      key === 'to' ? t('填写邮箱地址，多个地址用逗号分隔') : t('多个地址用逗号分隔');
    addressInput.autocomplete = 'off';
    addressInput.spellcheck = false;
    if (key !== 'to') {
      recipient.hidden = !draft.content[key].length;
      // Collapse preserves addresses and keeps a populated field visible when reopened.
      const toggle = el('button', label, 'quiet');
      toggle.type = 'button';
      toggle.setAttribute('aria-controls', recipient.id);
      toggle.setAttribute('aria-expanded', String(!recipient.hidden));
      toggle.addEventListener('click', () => {
        recipient.hidden = !recipient.hidden;
        toggle.setAttribute('aria-expanded', String(!recipient.hidden));
        if (!recipient.hidden) addressInput.focus({ preventScroll: true });
      });
      recipientOptions.append(toggle);
    }
    recipients.append(recipient);
  }
  const toRow = recipients.querySelector('#recipient-to');
  const recipientPrimary = el('div', undefined, 'recipient-primary');
  toRow.before(recipientPrimary);
  recipientPrimary.append(toRow, recipientOptions);
  form.append(recipients);
  const subject = field(t('主题'), 'draft-subject', draft.content.subject);
  subject.className = 'compose-line compose-subject';
  subject.querySelector('input').placeholder = t('邮件主题');
  const body = field('', 'draft-text', draft.content.text, 'textarea');
  body.querySelector('textarea').setAttribute('aria-label', t('邮件正文（纯文本）'));
  body.className = 'compose-body';
  body.querySelector('textarea').placeholder = t('在这里撰写邮件…');
  form.append(subject, body);
  pageState.composer.editor.rich = createRichEditor(body.querySelector('textarea'), {
    html: draft.content.html,
    collapseQuotes: true,
    quoteIcon: () => icon('more'),
    imageUrl: attachmentAccess.imageUrl,
    files: (files, inline) => {
      pageState.composer.editor.uploads.enqueue(files, inline);
    },
  });
  form.querySelector('#draft-subject').maxLength = 998;
  form.querySelector('#draft-text').maxLength = 200000;
  const attachmentList = el('div');
  attachmentList.id = 'draft-attachments';
  const owner = pageState.composer.editor;
  pageState.composer.editor.uploads = createAttachmentUploads({
    api,
    el,
    count: () => owner.attachments.length,
    beforeUpload: async () => {
      if (pageState.composer.saving) await pageState.composer.saving;
      if (pageState.composer.pendingTransfer) failure('OUTCOME_UNKNOWN');
    },
    committed: (asset, inline) => {
      if (pageState.composer.editor !== owner) return;
      if (!owner.attachments.some((item) => item.id === asset.id)) owner.attachments.push(asset);
      if (inline && attachmentAccess.isImage(asset)) owner.rich.insertImage(asset);
    },
    changed: () => {
      if (pageState.composer.editor !== owner) return;
      pageState.composer.dirty = true;
      pageState.composer.autosaveBlocked = false;
      updateDraftStatus();
      updateEditorLock();
      if (!hasUploads()) scheduleAutosave();
    },
  });
  const attachmentSection = el('section', undefined, 'compose-attachments');
  attachmentSection.setAttribute('aria-label', t('邮件附件'));
  const attachmentHeading = el('div', undefined, 'attachment-heading');
  const attachmentCount = el('span', t('附件 0'));
  attachmentCount.id = 'attachment-count';
  const limits = el('details', undefined, 'attachment-help');
  limits.append(el('summary', t('大小限制')), el('p', t('单个文件不超过 10 MiB，每封邮件最多 10 个附件。正文图片也计入。')));
  attachmentHeading.append(icon('attachment'), attachmentCount, limits);
  attachmentSection.append(attachmentHeading, attachmentList, pageState.composer.editor.uploads.element);
  form.append(attachmentSection);
  const picker = field(t('添加附件'), 'attachment-picker', '', 'input');
  picker.className = 'attachment-picker';
  const input = picker.querySelector('input');
  input.type = 'file';
  input.multiple = true;
  input.addEventListener('change', () => {
    const files = [...input.files];
    pageState.composer.editor.uploads.enqueue(files);
    input.value = '';
  });
  const attachmentTools = el('div', undefined, 'attachment-tools');
  attachmentTools.append(picker);
  attachmentHeading.append(attachmentTools);
  const actions = el('div', undefined, 'actions compose-actions');
  const more = el('details', undefined, 'compose-more');
  const secondary = el('div', undefined, 'secondary-actions');
  more.append(el('summary', t('更多操作')), secondary);
  secondary.append(
    button(t('插入此邮箱签名'), async () => {
      if (['sending', 'sent', 'unknown'].includes(pageState.composer.editor.draft.status) || pageState.composer.pendingTransfer) return;
      const signature = await loadSignature(accountPreference(pageState.composer.editor.draft.content.accountId), api);
      if (!signature.text && !signature.attachments.length) {
        notice(t('此邮箱尚未设置签名，可在账号偏好中添加。'));
        return;
      }
      const ids = new Set(pageState.composer.editor.attachments.map((asset) => asset.id));
      if (
        signature.text &&
        $('draft-text').value.endsWith(signature.text) &&
        signature.attachments.every((asset) => ids.has(asset.id))
      ) {
        notice(t('正文末尾已包含此邮箱签名。'));
        return;
      }
      if (
        $('draft-text').value.length + signature.text.length + 2 > 200000 ||
        new Set([...ids, ...signature.attachments.map((asset) => asset.id)]).size > 10
      )
        failure('INVALID_INPUT');
      for (const asset of signature.attachments)
        if (!ids.has(asset.id)) pageState.composer.editor.attachments.push(asset);
      if (signature.html) pageState.composer.editor.rich.appendHtml(`<p><br></p>${signature.html}`);
      else pageState.composer.editor.rich.appendText(`\n\n${signature.text}`);
      renderAttachments();
      pageState.composer.dirty = true;
      updateDraftStatus();
      scheduleAutosave();
    }),
  );
  const reconcile = button(t('核对保存状态'), async () => {
    await reconcileTransfer();
    applyTransferResult();
  });
  reconcile.id = 'reconcile';
  reconcile.hidden = !pageState.composer.pendingTransfer;
  const cancelTransfer = button(t('取消本次保存并继续编辑'), cancelPendingTransfer);
  cancelTransfer.id = 'cancel-transfer';
  cancelTransfer.hidden = !pageState.composer.pendingTransfer;
  const reload = button(t('重新读取'), async () => {
    if (pageState.composer.editor.draft.id && (await leaveEditor())) await openDraft(pageState.composer.editor.draft.id);
  });
  reload.id = 'draft-reload';
  reload.disabled = !draft.id;
  const save = button(t('保存草稿'), saveDraft);
  save.id = 'draft-save';
  save.disabled = locked;
  const confirm = button(
    t('发送'),
    async () => {
      const owner = pageState.composer.editor;
      if (owner.sendSubmitted) return;
      if (pageState.composer.saving) await pageState.composer.saving;
      if (hasUploads() || pageState.composer.pendingTransfer) {
        notice(t('请先完成附件上传，正文和附件仍保留。'), true);
        return;
      }
      validateRecipients(true);
      if (pageState.composer.dirty || !pageState.composer.editor.draft.id) await persistEditing('draft', false);
      if (pageState.composer.editor !== owner || pageState.composer.dirty || !pageState.composer.editor.draft.id) return;
      const reviewed = pageState.composer.editor.draft;
      const pending = await api('drafts/confirm', { id: reviewed.id, revision: reviewed.revision });
      const { reviewId, revision, digest } = pending.review;
      const result = await api('drafts/approve', { reviewId, revision, digest, confirmed: true });
      pageState.composer.editor.draft = result;
      pageState.composer.editor.sendSubmitted = ['pending_confirmation', 'queued'].includes(result.status);
      updateDraftStatus();
      notice(t('已在工作台确认并提交发送。SMTP 接受不代表收件人已收到。'));
      watchDraftStatus(result.id);
    },
    'primary',
  );
  confirm.id = 'draft-confirm';
  confirm.disabled = locked;
  const check = button(t('查询发送状态'), async () => {
    if (!pageState.composer.editor.draft.id) return;
    const result = await api('drafts/status', { id: pageState.composer.editor.draft.id });
    if (result.revision !== pageState.composer.editor.draft.revision) {
      notice(t('草稿版本已变化；当前编辑未被覆盖，请重新读取并核对。'), true);
      return;
    }
    Object.assign(pageState.composer.editor.draft, result);
    if (!['pending_confirmation', 'queued'].includes(result.status)) pageState.composer.editor.sendSubmitted = false;
    updateDraftStatus();
    const finalStatus = ['sending', 'sent', 'unknown'].includes(result.status);
    if (finalStatus && !pageState.composer.dirty && !pageState.composer.pendingTransfer) await openDraft(pageState.composer.editor.draft.id);
    if (['sent', 'unknown'].includes(result.status) && ['drafts', 'sent'].includes(pageState.navigation.view))
      await loadList();
    const preserved =
      finalStatus && (pageState.composer.dirty || pageState.composer.pendingTransfer)
        ? t('未保存的正文与附件仍保留在页面中，未包含在本次投递中；请复制保留后再重新读取记录。')
        : '';
    notice(
      tt`当前状态：${states[result.status]}。${result.status === 'sent' ? t('表示 SMTP 已接受，不代表已送达。') : ''}${preserved}`,
    );
  });
  check.id = 'draft-check';
  check.disabled = !draft.id;
  if (originalMessage) secondary.append(originalMessage);
  secondary.append(reload, check);
  if (draft.id && draft.status === 'draft')
    secondary.append(
      button(t('删除草稿'), async () => {
        if (await confirmDraftRemoval(pageState.composer.editor.draft, { el })) {
          if (pageState.composer.saving) await pageState.composer.saving;
          await api('drafts/delete', { id: pageState.composer.editor.draft.id, revision: pageState.composer.editor.draft.revision });
          if (pageState.composer.editor.recovery?.revision)
            await api('recoveries/discard', {
              id: pageState.composer.editor.recovery.id,
              revision: pageState.composer.editor.recovery.revision,
            });
          pageState.composer.dirty = false;
          blankDetail();
          await loadList();
          notice(t('草稿已删除。'));
        }
      }),
    );
  const uploadRecovery = el('div', undefined, 'upload-recovery');
  uploadRecovery.append(reconcile, cancelTransfer);
  attachmentSection.append(uploadRecovery);
  setupActionMenu(more);
  const localNote = el('span', t('草稿保留在本机'), 'compose-local-note');
  actions.append(more, localNote, save, confirm);
  const scroll = el('div', undefined, 'compose-scroll');
  scroll.append(...form.children);
  form.append(scroll, actions);
  for (const control of form.querySelectorAll('input, textarea')) control.disabled = locked;
  form.addEventListener('input', (event) => {
    clearFieldError(event.target);
    if (event.target.id !== 'attachment-picker') {
      pageState.composer.dirty = true;
      pageState.composer.autosaveBlocked = false;
      updateDraftStatus();
      scheduleAutosave();
    }
  });
  form.addEventListener('submit', (event) => event.preventDefault());
  detail.append(form);
  updateDraftStatus();
  // Opening a native picker must stay in the user gesture. run() locks the
  // file input before its action executes, which makes input.click() a no-op.
  const attachAction = el('button', t('添加附件'), 'editor-attach');
  attachAction.type = 'button';
  attachAction.disabled = locked;
  attachAction.addEventListener('click', () => {
    if (!input.disabled) input.click();
  });
  decorateAction(attachAction, 'attachment');
  form.querySelector('.rich-toolbar')?.append(attachAction);
  renderAttachments(locked);
  if (!$('compose-dialog').open) $('compose-dialog').showModal();
  $('compose-title').tabIndex = -1;
  $('compose-title').focus({ preventScroll: true });
  detail.scrollTop = 0;
}
function renderAttachments(locked = false) {
  const list = $('draft-attachments');
  list.replaceChildren();
  $('attachment-count').textContent = tt`附件 ${pageState.composer.editor.attachments.length}`;
  for (const attachment of pageState.composer.editor.attachments) {
    const item = el('div', undefined, 'attachment');
    const identity = el('span', undefined, 'attachment-identity');
    identity.append(el('span', attachment.filename), el('small', bytes(attachment.bytes), 'muted'));
    item.append(icon('file'), identity);
    if (attachmentAccess.canPreview(attachment))
      item.append(localButton(t('预览'), () => attachmentAccess.preview(attachment)));
    item.append(localButton(t('下载'), () => downloadAttachment(attachment.id)));
    if (!locked) item.append(button(t('移除'), async () => removeAttachment(attachment.id)));
    list.append(item);
  }
}
function removeAttachment(id) {
  if (pageState.composer.pendingTransfer) failure('OUTCOME_UNKNOWN');
  if (pageState.composer.saving || hasUploads()) failure('BUSY');
  if (pageState.composer.editor.sendSubmitted || ['queued', 'sending', 'sent', 'unknown'].includes(pageState.composer.editor.draft.status)) failure('DRAFT_LOCKED');
  pageState.composer.editor.rich?.removeImage(id);
  pageState.composer.editor.attachments = pageState.composer.editor.attachments.filter((entry) => entry.id !== id);
  pageState.composer.dirty = true;
  pageState.composer.autosaveBlocked = false;
  renderAttachments();
  updateDraftStatus();
  scheduleAutosave();
}
function updateDraftStatus() {
  const draft = pageState.composer.editor.draft;
  if ($('draft-check')) $('draft-check').hidden = !(pageState.composer.editor.sendSubmitted || ['pending_confirmation', 'queued', 'sending', 'sent', 'unknown'].includes(draft.status));
  $('draft-status').textContent =
    `${pageState.composer.editor.sendSubmitted ? t('已确认 · 等待投递') : states[pageState.composer.editor.draft.status] ?? t('新草稿')}${pageState.composer.editor.draft.revision ? tt` · 版本 ${pageState.composer.editor.draft.revision}` : ''}${pageState.composer.dirty ? (hasRecovery() ? t(' · 编辑内容已自动备份') : t(' · 有未保存修改')) : ''}${pageState.composer.saving ? t(' · 正在保存…') : ''}`;
}

function updateEditorLock() {
  if (!pageState.composer.editor || !$('editor')) return;
  const final = Boolean(pageState.composer.editor.sendSubmitted) || ['sending', 'sent', 'unknown'].includes(pageState.composer.editor.draft.status);
  const disabled = pageState.lifecycle.busy || Boolean(pageState.composer.pendingTransfer) || Boolean(pageState.composer.saving) || hasUploads() || final;
  const textLocked = pageState.lifecycle.busy || (pageState.composer.pendingTransfer && !pageState.composer.pendingTransfer.background) || final;
  pageState.composer.editor.rich?.setEditable(!textLocked);
  for (const node of document.querySelectorAll('#editor input, #editor textarea')) {
    // Unsaved text remains focusable and selectable for copying, but cannot edit a sent record.
    node.disabled =
      Boolean(textLocked && (!final || !pageState.composer.dirty || node.type === 'file')) ||
      (node.type === 'file' && disabled);
    node.readOnly = final;
  }
  $('draft-save').disabled = disabled;
  if ($('draft-from')) $('draft-from').disabled = disabled;
  $('draft-reload').disabled = pageState.lifecycle.busy || Boolean(pageState.composer.saving) || !pageState.composer.editor.draft.id;
  $('draft-check').disabled = pageState.lifecycle.busy || Boolean(pageState.composer.saving) || !pageState.composer.editor.draft.id;
  $('draft-confirm').disabled = disabled;
  const attach = $('editor').querySelector('.editor-attach');
  if (attach) attach.disabled = disabled;
  $('reconcile').hidden = !pageState.composer.pendingTransfer;
  $('cancel-transfer').hidden = !pageState.composer.pendingTransfer;
  renderAttachments(disabled);
}
function editingContent() {
  if (!pageState.composer.editor || !$('editor')) return undefined;
  return {
    accountId: pageState.composer.editor.draft.content.accountId,
    to: $('draft-to').value,
    cc: $('draft-cc').value,
    bcc: $('draft-bcc').value,
    subject: $('draft-subject').value,
    text: $('draft-text').value,
    html: pageState.composer.editor.rich.html(),
    attachmentIds: pageState.composer.editor.attachments.map((item) => item.id),
    ...(pageState.composer.editor.draft.content.replyToMessage
      ? { replyToMessage: pageState.composer.editor.draft.content.replyToMessage }
      : {}),
  };
}
const splitAddresses = (value) =>
  value
    .split(/[,;，；\n]/u)
    .map((part) => part.trim())
    .filter(Boolean);
const validAddress = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/u.test(value);
function clearFieldError(input) {
  if (input.getAttribute?.('aria-invalid') !== 'true') return;
  input.removeAttribute('aria-invalid');
  input.removeAttribute('aria-describedby');
  $(`${input.id}-error`)?.remove();
}
function fieldError(id, message) {
  const input = $(id);
  clearFieldError(input);
  const label = input.closest('label');
  label.hidden = false;
  document.querySelector(`[aria-controls="${label.id}"]`)?.setAttribute('aria-expanded', 'true');
  const hint = el('small', message, 'field-error');
  hint.id = `${id}-error`;
  hint.setAttribute('role', 'alert');
  label.append(hint);
  input.setAttribute('aria-invalid', 'true');
  input.setAttribute('aria-describedby', hint.id);
  return Object.assign(new Error(message), { code: 'FORM_INVALID', fieldId: id });
}
function validateRecipients(requireRecipient = false) {
  let count = 0;
  for (const [key, label] of [['to', t('收件人')], ['cc', t('抄送')], ['bcc', t('密送')]]) {
    const input = $(`draft-${key}`);
    clearFieldError(input);
    const values = splitAddresses(input.value);
    if (values.some((value) => !validAddress(value)))
      throw fieldError(input.id, tt`${label}地址格式不正确，请填写完整邮箱地址，多个地址用逗号分隔。`);
    count += values.length;
  }
  if (requireRecipient && count === 0) throw fieldError('draft-to', t('请至少填写一位收件人。'));
  if (count > 100) throw fieldError('draft-to', t('收件人、抄送和密送合计不能超过 100 人。'));
}
function hasRecovery() {
  const content = editingContent();
  return Boolean(content && pageState.composer.editor?.recovery?.snapshot === JSON.stringify(content));
}
async function saveDraft() {
  if (pageState.composer.saving) await pageState.composer.saving;
  return persistEditing('draft', false);
}
function persistEditing(kind, background) {
  clearTimeout(pageState.composer.autosaveTimer);
  if (pageState.composer.saving) return pageState.composer.saving;
  if (pageState.composer.pendingTransfer || (kind === 'draft' && hasUploads())) failure('OUTCOME_UNKNOWN');
  if (kind === 'draft') validateRecipients();
  const owner = pageState.composer.editor;
  const raw = editingContent();
  const snapshot = JSON.stringify(raw);
  const payload =
    kind === 'recovery'
      ? {
          id: owner.recovery.id,
          revision: owner.recovery.revision,
          ...(owner.draft.id
            ? { basedOn: { id: owner.draft.id, revision: owner.draft.revision } }
            : {}),
          content: raw,
        }
      : {
          content: {
            ...raw,
            ...Object.fromEntries(
              ['to', 'cc', 'bcc'].map((key) => [key, splitAddresses(raw[key])]),
            ),
          },
          ...(owner.draft.id
            ? { existing: { id: owner.draft.id, revision: owner.draft.revision } }
            : {}),
        };
  const operation = (async () => {
    try {
      await startTransfer(
        new TextEncoder().encode(JSON.stringify(payload)),
        { kind },
        { owner, snapshot, background },
      );
    } catch (error) {
      // Only definitive validation rejections are eligible for cancellation.
      // The authoritative receipt still decides whether to apply a completed
      // save or release the lock. Unknown outcomes remain locked for review.
      if (pageState.composer.pendingTransfer && ['INVALID_INPUT', 'DRAFT_INCOMPLETE', 'ACCOUNT_NOT_FOUND', 'ATTACHMENT_NOT_FOUND', 'MESSAGE_TOO_LARGE'].includes(error?.code)) {
        await cancelPendingTransfer().catch(() => {});
      }
      throw error;
    }
    applyTransferResult();
  })();
  pageState.composer.saving = operation.finally(() => {
    pageState.composer.saving = undefined;
    if (!pageState.lifecycle.disposed && pageState.composer.editor === owner) {
      updateDraftStatus();
      updateEditorLock();
      if (pageState.composer.dirty && !hasRecovery() && !pageState.composer.pendingTransfer && !pageState.composer.autosaveBlocked) scheduleAutosave();
    }
  });
  updateEditorLock();
  return pageState.composer.saving;
}
function scheduleAutosave() {
  clearTimeout(pageState.composer.autosaveTimer);
  pageState.composer.autosaveTimer = setTimeout(async () => {
    if (
      pageState.lifecycle.disposed ||
      !pageState.composer.editor ||
      !pageState.composer.dirty ||
      pageState.composer.pendingTransfer ||
      pageState.composer.autosaveBlocked ||
      (pageState.composer.editor.draft.status && pageState.composer.editor.draft.status !== 'draft')
    )
      return;
    if (pageState.lifecycle.busy || pageState.composer.saving) {
      scheduleAutosave();
      return;
    }
    const raw = editingContent();
    if (!raw.accountId) return;
    const valid = ['to', 'cc', 'bcc']
      .flatMap((key) => splitAddresses(raw[key]))
      .every(validAddress);
    if (hasRecovery() && (!valid || hasUploads())) return;
    try {
      await persistEditing(valid && !hasUploads() ? 'draft' : 'recovery', true);
    } catch (error) {
      pageState.composer.autosaveBlocked = true;
      notice(
        `${
          errors[error?.code] ?? t('自动保存暂未完成，当前编辑仍保留。')
        }${pageState.composer.pendingTransfer ? t(' 可核对保存状态；请先保留内容再关闭。') : t(' 当前编辑仍保留，可修正后继续保存。')}`,
        true,
      );
    }
  }, 2500);
}
function watchDraftStatus(id, deadline = Date.now() + 16 * 60_000) {
  clearTimeout(pageState.composer.draftPoll);
  pageState.composer.draftPoll = setTimeout(async () => {
    if (pageState.lifecycle.disposed || pageState.composer.editor?.draft.id !== id || Date.now() > deadline) return;
    if (pageState.lifecycle.busy) {
      watchDraftStatus(id, deadline);
      return;
    }
    try {
      const result = await api('drafts/status', { id });
      if (pageState.lifecycle.disposed || pageState.composer.editor?.draft.id !== id) return;
      // Saving may have started while this request was in flight, including digest computation
      // before pendingTransfer exists. Do not apply an older receipt or release its edit lock.
      if (pageState.lifecycle.busy || pageState.composer.saving) {
        watchDraftStatus(id, deadline);
        return;
      }
      if (result.revision !== pageState.composer.editor.draft.revision) {
        notice(t('草稿已变化，当前编辑保留，请重新读取核对。'), true);
        return;
      }
      Object.assign(pageState.composer.editor.draft, result);
      if (!['pending_confirmation', 'queued'].includes(result.status)) pageState.composer.editor.sendSubmitted = false;
      updateDraftStatus();
      updateEditorLock();
      if (['sent', 'unknown'].includes(result.status)) {
        // Refresh list membership/counts without navigating away from the current receipt.
        // Use the normal UI operation lock so a view switch cannot race the list response.
        await run(async () => {
          const preserveEditing = pageState.composer.dirty || pageState.composer.pendingTransfer;
          if (!preserveEditing) renderDelivery(pageState.composer.editor.draft, pageState.composer.editor.attachments);
          if (['drafts', 'sent'].includes(pageState.navigation.view)) await loadList();
          notice(preserveEditing
            ? tt`当前状态：${states[result.status]}。当前未保存修改仍保留在页面，未包含在本次投递中。`
            : t('投递状态已更新。正文和附件为投递时的固定内容。'));
        });
        return;
      }
      if (['pending_confirmation', 'queued', 'sending'].includes(result.status))
        watchDraftStatus(id, deadline);
      else
        notice(
          tt`当前状态：${states[result.status]}。${result.status === 'sent' ? t('表示 SMTP 接受，收件端送达需另行核验。') : ''}${pageState.composer.dirty && ['sending', 'sent', 'unknown'].includes(result.status) ? t('当前未保存修改仍保留在页面，未包含在本次投递中。') : ''}`,
        );
    } catch {
      if (!pageState.lifecycle.disposed) notice(t('发送状态暂未更新，可手动查询；请勿重复发送。'), true);
    }
  }, 2000);
}
async function sha256(content) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', content))]
    .map((byte) => byte.toString(16).padStart(2, '0'))
    .join('');
}
function base64(content) {
  let result = '';
  for (const byte of content) result += String.fromCharCode(byte);
  return btoa(result);
}
async function startTransfer(content, metadata, editing) {
  const digest = await sha256(content);
  if (pageState.lifecycle.localDataCleared) { content.fill(0); failure('SERVICE_CLOSED'); }
  pageState.composer.pendingTransfer = {
    ...editing,
    content,
    metadata: {
      ...metadata,
      id: crypto.randomUUID(),
      bytes: content.length,
      sha256: digest,
    },
  };
  $('reconcile').hidden = false;
  const state = await api('uploads/begin', pageState.composer.pendingTransfer.metadata);
  await resumeTransfer(state);
}
async function resumeTransfer(state) {
  const transfer = pageState.composer.pendingTransfer;
  if (state.status === 'cancelled') {
    releaseCancelledTransfer();
    return;
  }
  if (state.status === 'committed') {
    transfer.result = state.result;
    return;
  }
  if (state.status === 'committing') {
    notice(t('正在持久化，请稍后再次检查状态。'));
    return;
  }
  if (state.offset < 0 || state.offset > transfer.content.length || !Number.isInteger(state.offset))
    failure('INVALID_RESPONSE');
  for (let offset = state.offset; offset < transfer.content.length; ) {
    const end = Math.min(offset + CHUNK, transfer.content.length);
    const result = await api('uploads/append', {
      id: transfer.metadata.id,
      offset,
      contentBase64: base64(transfer.content.subarray(offset, end)),
    });
    if (result.offset !== end) failure('TRANSFER_CONFLICT');
    offset = end;
    notice(
      tt`正在保存${transfer.metadata.kind === 'draft' ? t('草稿') : t('附件')}：${Math.round((offset / transfer.content.length) * 100)}%`,
    );
  }
  transfer.commitAttempted = true;
  transfer.result = await api('uploads/commit', { id: transfer.metadata.id });
}
async function reconcileTransfer() {
  if (!pageState.composer.pendingTransfer) return;
  // Repeating begin is idempotent, but after any unknown outcome first read the receipt.
  const status = await api('uploads/status', { id: pageState.composer.pendingTransfer.metadata.id });
  await resumeTransfer(status);
}
async function cancelPendingTransfer() {
  const transfer = pageState.composer.pendingTransfer;
  if (!transfer) return;
  let status;
  try {
    status = await api('uploads/status', { id: transfer.metadata.id });
  } catch (error) {
    // No domain commit was dispatched, so an absent temporary upload is safe to release.
    if (error?.code !== 'TRANSFER_EXPIRED' || transfer.commitAttempted) throw error;
  }
  if (status?.status === 'committing') {
    notice(t('正在持久化，不能取消；请稍后检查上传结果。'));
    return;
  }
  if (status?.status === 'cancelled') {
    releaseCancelledTransfer();
    return;
  }
  const result =
    !status || status.status === 'committed'
      ? status
      : await api('uploads/cancel', { id: transfer.metadata.id });
  // Cancellation races with completion: preserve and apply the committed receipt, never erase it.
  if (result?.status === 'committed') {
    transfer.result = result.result;
    applyTransferResult();
    return;
  }
  if (result && result.cancelled !== true) failure('INVALID_RESPONSE');
  releaseCancelledTransfer();
}
function releaseCancelledTransfer() {
  pageState.composer.pendingTransfer.content.fill(0);
  pageState.composer.pendingTransfer = undefined;
  notice(t('本次保存已取消，表单内容和已选附件仍保留。请修正输入后重新保存。'));
}
function applyTransferResult() {
  const transfer = pageState.composer.pendingTransfer;
  if (!transfer?.result) return;
  if (transfer.metadata.kind === 'attachment') {
    pageState.composer.editor.attachments.push(transfer.result);
    pageState.composer.dirty = true;
    renderAttachments();
    updateDraftStatus();
    notice(t('附件已保存到加密邮箱空间；请保存草稿以关联附件。'));
  } else {
    if (transfer.owner && transfer.owner !== pageState.composer.editor) {
      transfer.content.fill(0);
      pageState.composer.pendingTransfer = undefined;
      return;
    }
    const currentContent = editingContent();
    const unchanged = !transfer.snapshot || JSON.stringify(currentContent) === transfer.snapshot;
    if (transfer.metadata.kind === 'recovery') {
      pageState.composer.editor.recovery = {
        id: transfer.result.id,
        revision: transfer.result.revision,
        snapshot: transfer.snapshot,
      };
    } else {
      pageState.composer.editor.draft = transfer.result;
      if (!unchanged && currentContent) pageState.composer.editor.draft.content.accountId = currentContent.accountId;
      pageState.composer.dirty = !unchanged;
      const backup = pageState.composer.editor.recovery;
      if (backup?.revision)
        void api('recoveries/discard', { id: backup.id, revision: backup.revision }).catch(
          () => {},
        );
      pageState.composer.editor.recovery = { id: crypto.randomUUID(), revision: 0 };
    }
    pageState.composer.pendingTransfer = undefined;
    updateDraftStatus();
    const from = $('draft-from');
    if (from) from.value = pageState.composer.editor.draft.content.accountId;
    $('draft-reload').disabled = false;
    $('draft-check').disabled = false;
    updateEditorLock();
    notice(
      transfer.metadata.kind === 'recovery'
        ? hasUploads()
          ? t('编辑内容已自动备份，附件上传完成后会保存完整草稿。')
          : t('编辑内容已自动保存在本机，收件地址可稍后补全。在草稿中可以恢复。')
        : pageState.composer.dirty
          ? t('上一版已保存，继续保存你新输入的内容。')
          : t('草稿已保存。请核对完整内容，点击“发送”即确认发送。'),
    );
  }
  transfer.content.fill(0);
  pageState.composer.pendingTransfer = undefined;
  $('reconcile').hidden = true;
}
async function downloadAttachment(id) {
  return attachmentAccess.download(id);
}

async function openSettings(setup = {}) {
  const result = await api('accounts/settings', setup);
  if (result.status === 'unsupported') {
    notice(result.reason === 'oauth' ? t('此邮箱需要 OAuth，本期暂不支持。') : t('此邮箱需要 Bridge，本期暂不支持。'), true);
    return;
  }
  await accountConnection.open(result, setup);
}
function finishLocalDataClear() {
  // Only a successful explicit clear can discard local work and retire this page.
  pageState.lifecycle.localDataCleared = true;
  pageState.composer.dirty = false;
  pageState.composer.autosaveBlocked = true;
  pageState.navigation.pendingWorkbenchTarget = false;
  autoCheck.checked = false;
  disposePage(false, { preserveClearResult: true });
  pageState.composer.editor = undefined;
  pageState.composer.pendingTransfer?.content.fill(0);
  pageState.composer.pendingTransfer = undefined;
  $('compose-dialog').close();
  $('compose-detail').replaceChildren();
  location.replace(location.pathname);
}
async function refreshAfterSetup(result) {
  const accountManagement = $('detail').dataset.accountManagement === 'true';
  await loadAccounts();
  refreshEditorSenders();
  if (accountManagement && !pageState.composer.dirty && !pageState.composer.pendingTransfer) {
    await accountWorkspace.manage();
  } else if (!pageState.composer.editor && !pageState.composer.dirty && !pageState.composer.pendingTransfer) {
    if (document.body.dataset.workspace === 'settings') await accountWorkspace.open();
    else { blankDetail(); await loadList(); }
  }
  notice(result.status === 'connected'
    ? t('邮箱已连接，可以继续处理邮件。')
    : t('邮箱已断开，已保存草稿和发送记录仍保留。'));
}
$('review-selected').addEventListener('click', () => {
  void run(async () => {
    if (await leaveEditor())
      await batchWorkspace.review([...pageState.composer.draftSelection].map(([id, revision]) => ({ id, revision })));
  });
});
$('clear-selection').addEventListener('click', () => {
  pageState.composer.draftSelection.clear();
  updateSelection();
  for (const node of $('items').querySelectorAll('input[type=checkbox]')) node.checked = false;
});
function disposePage(persisted = false, { preserveClearResult = false } = {}) {
  if (!pageState.suspend({ permanent: !persisted })) return;
  clearTimeout(prefetchTimer); messagePreloader.stop(); messageReader.clear();
  resetRefresh();
  uiBridge.stop();
  releaseEditLease();
  batchWorkspace.dispose();
  if (!persisted) {
    accountWorkspace.dispose();
    // Keep the successful clear receipt visible until native navigation finishes.
    if (!preserveClearResult) {
      accountConnection.dispose();
      localDataClear.dispose();
    }
    mailMergeWorkspace.dispose();
    pageState.composer.editor?.uploads?.dispose();
    pageState.composer.editor?.rich?.destroy();
    attachmentAccess.dispose();
  }
}
window.addEventListener('pagehide', (event) => disposePage(event.persisted));
window.addEventListener('pageshow', (event) => {
  if (!event.persisted || !pageState.resume()) return;
  uiBridge.start();
  batchWorkspace.resume();
  if (
    pageState.composer.editor?.draft.id &&
    ['pending_confirmation', 'queued', 'sending'].includes(pageState.composer.editor.draft.status)
  )
    watchDraftStatus(pageState.composer.editor.draft.id);
  if (pageState.composer.editor && pageState.composer.dirty) scheduleAutosave();
  if (
    !pageState.lifecycle.busy && !pageState.composer.editor && !pageState.composer.dirty &&
    !pageState.composer.pendingTransfer && pageState.navigation.view === 'inbox' &&
    document.body.dataset.workspace !== 'settings' &&
    [...pageState.inbox.mailboxPages.values()].some((mailbox) => mailbox.loading)
  ) void run(() => loadList());
  if (autoCheck.checked) void checkNewMail();
});
$('language').value = languagePreference();
const languageTrigger = $('language-trigger');
languageTrigger.textContent = localeTag().startsWith('zh') ? '中文' : 'EN';
languageTrigger.title = t('界面语言');
// The full native language selector lives in a viewport-clamped popup at every width.

$('language').addEventListener('change', () => {
  const requested = $('language').value;
  void navigate(async () => {
    if (accountConnection.active() || localDataClear.active() || !(await leaveEditor())) {
      $('language').value = languagePreference(); return;
    }
    try { saveLanguagePreference(requested); }
    catch { $('language').value = languagePreference(); notice(t('无法保存语言设置，请检查浏览器存储权限。'), true); return; }
    window.location.reload();
  });
});
$('settings').addEventListener('click', () => {
  void navigate(() => accountWorkspace.open());
});
$('preferences').addEventListener('click', () => {
  void navigate(() => accountWorkspace.open());
});
window.addEventListener('focus', () => {
  if (focusSyncPending || Date.now() - accountsSyncedAt < 30_000 || !pageState.lifecycle.csrf || pageState.lifecycle.busy || pageState.composer.editor || accountConnection.active() || localDataClear.active()) return;
  const view = pageState.navigation.view, scope = pageState.account.accountId;
  const workspace = document.body.dataset.workspace;
  const previous = JSON.stringify(pageState.account.accounts);
  const current = () => !pageState.lifecycle.busy && !pageState.composer.editor && !pageState.composer.dirty && !accountConnection.active() && !localDataClear.active() && workspace === document.body.dataset.workspace && view === pageState.navigation.view && scope === pageState.account.accountId;
  focusSyncPending = true;
  void loadAccounts(current).then(async applied => {
    if (!applied) return;
    if (previous !== JSON.stringify(pageState.account.accounts) || scope !== pageState.account.accountId) {
      await run(async () => {
        if (document.body.dataset.workspace === 'settings') await accountWorkspace.open();
        else { blankDetail(); await loadList(); }
      });
    }
  }).catch(error => {
    if (current() && !pageState.lifecycle.disposed) notice(errors[error?.code] ?? t('暂时无法完成读取，请稍后重试。'), true);
  }).finally(() => { focusSyncPending = false; });
});
$('back-to-list').addEventListener('click', () => {
  void run(async () => {
    if (!(await leaveEditor())) return;
    blankDetail();
    $('list-title').focus();
  });
});
$('refresh').addEventListener('click', () => {
  if (refreshOperation) return;
  void run(async () => {
    messageReader.clear();
    const operation = beginRefresh();
    try {
      if (pageState.inbox.folderScope) pageState.inbox.folderChoices.set(pageState.inbox.folderScope, $('folder').value);
      pageState.inbox.folderScope = undefined;
      pageState.inbox.folderCache.clear();
      await loadAccounts();
      if (document.body.dataset.workspace === 'settings') {
        await accountWorkspace.open();
        finishRefresh(operation);
      } else await loadList();
    } catch (error) {
      finishRefresh(operation, true);
      throw error;
    }
  });
});
$('folder').addEventListener('change', () => {
  organizer.clear();
  pageState.inbox.cursor = undefined; pageState.inbox.query = undefined;
  for (const id of searchFields) { if ($(id).type === 'checkbox') $(id).checked = false; else $(id).value = ''; }
  void navigate(() => loadList());
});
$('work-filter').addEventListener('change', () => {
  void navigate(() => loadList());
});
async function newComposer() {
    if (!pageState.account.accountId) {
      notice(t('请先连接邮箱。'), true);
      return;
    }
    if (!(await leaveEditor())) return;
    await renderEditor(
      {
        content: {
          accountId: pageState.account.preferences.defaultAccountId ?? '',
          to: [],
          cc: [],
          bcc: [],
          subject: '',
          text: '',
          attachmentIds: [],
        },
      },
      [],
    );
    pageState.composer.dirty = false;
    notice(t('新邮件会自动保存。核对完整内容后，点击“发送”即确认发送。'));
}
$('compose').addEventListener('click', () => { void run(newComposer); });
async function changeAccount(next) {
  if (next !== '__add' && ![...pageState.account.accounts, ...pageState.account.historyAccounts].some((item) => item.id === next)) return;
  if (next === '__add') {
    $('account').value = pageState.account.accountId;
    await openSettings();
    return;
  }
  if (!(await leaveEditor())) {
    $('account').value = pageState.account.accountId;
    return;
  }
  const wasSettings = document.body.dataset.workspace === 'settings';
  // A view is switched only after the shared backend has persisted the new default.
  // Opening a particular draft never uses this explicit-switch operation.
  if (pageState.account.accounts.some((item) => item.id === next)) {
    try {
      const result = await api('accounts/select', { accountId: next });
      pageState.account.preferences = result.preferences ?? result;
    } catch (error) {
      $('account').value = pageState.account.accountId;
      throw error;
    }
  }
  pageState.inbox.scopeFilters.set(
    pageState.account.accountId,
    Object.fromEntries(
      searchFields.map((id) => [id, $(id).type === 'checkbox' ? $(id).checked : $(id).value]),
    ),
  );
  pageState.requests.invalidate('inbox');
  organizer.clear();
  pageState.account.accountId = next;
  rememberAccountScope(next);
  const filters = {};
  pageState.inbox.cursor = undefined; pageState.inbox.query = undefined;
  for (const id of searchFields) {
    if ($(id).type === 'checkbox') $(id).checked = filters[id] ?? false;
    else $(id).value = filters[id] ?? '';
  }
  const connectedScope =
    pageState.account.accounts.some((item) => item.id === next) || (next === '*' && pageState.account.accounts.length > 0);
  if (!connectedScope && ['inbox', 'work'].includes(pageState.navigation.view)) selectView('sent');
  $('compose').hidden = !connectedScope;
  $('work-tab').hidden = !connectedScope;
  $('account').value = next;
  updateAccountLabel();
  if (wasSettings) { await accountWorkspace.open(); return; }
  blankDetail();
  await loadList();
}
$('account').addEventListener('change', () => {
  const next = $('account').value;
  void navigate(() => changeAccount(next));
});
async function closeComposer() {
  releaseEditLease();
  if (!(await leaveEditor())) return;
  pageState.composer.editor?.uploads?.dispose();
  pageState.composer.editor?.rich?.destroy();
  pageState.composer.editor = undefined;
  pageState.composer.dirty = false;
  clearTimeout(pageState.composer.autosaveTimer);
  clearTimeout(pageState.composer.draftPoll);
  $('compose-detail').replaceChildren();
  if (pageState.navigation.view === 'drafts') await loadList();
  notice(t('已关闭写信窗口。已保存的内容可在草稿中继续编辑。'));
}
function requestCloseComposer() {
  const focused = document.activeElement;
  void run(closeComposer).then(() => {
    if (!$('compose-dialog').open) $('compose').focus({ preventScroll: true });
    else if (focused?.isConnected && !focused.disabled) focused.focus({ preventScroll: true });
  });
}
$('close-compose').addEventListener('click', requestCloseComposer);
$('compose-dialog').addEventListener('cancel', (event) => {
  event.preventDefault();
  requestCloseComposer();
});
for (const tab of document.querySelectorAll('[data-mail-filter]')) {
  tab.addEventListener('click', () => {
    $('unread').checked = tab.dataset.mailFilter === 'unread';
    $('flagged-search').checked = tab.dataset.mailFilter === 'starred';
    organizer.clear();
    void navigate(() => loadList());
  });
}
$('unread').addEventListener('change', () => {
  organizer.clear();
  void navigate(() => loadList());
});
for (const next of Object.keys(viewNames))
  $(`${next}-tab`).addEventListener('click', () => {
    void navigate(async () => {
      if (!(await leaveEditor())) return;
      if (
        next === 'inbox' &&
        pageState.account.accountId !== '*' &&
        !pageState.account.accounts.some((account) => account.id === pageState.account.accountId)
      ) {
        pageState.account.accountId = pageState.account.preferences.defaultAccountId ?? pageState.account.accounts[0]?.id ?? '';
        $('account').value = pageState.account.accountId;
        updateAccountLabel();
        $('compose').hidden = !pageState.account.accountId;
      }
      selectView(next);
      blankDetail();
      $('items').replaceChildren(el('p', tt`正在加载${viewNames[next]}…`, 'empty'));
      $('scope').textContent = '';
      // Keep fast local reads in the same interaction, but never make navigation
      // wait for a slow server. loadList owns cancellation and stale-result guards.
      const pending = loadList().catch(error => {
        if (!pageState.lifecycle.disposed) notice(errors[error?.code] ?? t('暂时无法完成读取，请稍后重试。'), true);
      });
      await Promise.race([pending, new Promise(resolve => setTimeout(resolve, 50))]);
    });
  });
setupActionMenu($('account-picker'), false);
for (const popup of document.querySelectorAll('.search-advanced, #list-options, #account-picker')) {
  popup.addEventListener('toggle', () => {
    if (popup.open) for (const other of document.querySelectorAll('.search-advanced, #list-options, #account-picker')) if (other !== popup) other.open = false;
  });
  popup.addEventListener('keydown', (event) => { if (event.key === 'Escape') { event.preventDefault(); popup.open = false; popup.querySelector('summary').focus(); } });
}
document.addEventListener('click', (event) => {
  for (const popup of document.querySelectorAll('.search-advanced, #list-options, .action-menu, .editor-more, .sender-help, .attachment-help')) if (popup.open && !popup.contains(event.target)) popup.open = false;
});
$('search').addEventListener('submit', (event) => {
  event.preventDefault();
  clearFieldError($('until-search'));
  if ($('since-search').value && $('until-search').value && $('until-search').value < $('since-search').value) {
    document.querySelector('.search-advanced').open = true;
    const error = fieldError('until-search', t('截止日期不能早于开始日期。'));
    $('until-search').focus();
    notice(error.message, true);
    return;
  }
  organizer.clear();
  document.querySelector('.search-advanced').open = false;
  void navigate(() => loadList());
});
$('reset-search').addEventListener('click', () => {
  clearFieldError($('until-search'));
  organizer.clear();
  for (const id of searchFields) {
    if ($(id).type === 'checkbox') $(id).checked = false;
    else $(id).value = '';
  }
  document.querySelector('.search-advanced').open = false;
  void navigate(() => loadList());
});
for (const id of ['since-search', 'until-search']) $(id).addEventListener('input', () => clearFieldError($('until-search')));
function dateFilters() {
  const values = {};
  if ($('since-search').value) values.sinceDate = $('since-search').value;
  if ($('until-search').value) {
    const end = new Date(`${$('until-search').value}T00:00:00Z`);
    end.setUTCDate(end.getUTCDate() + 1);
    if (!Number.isFinite(end.getTime())) failure('INVALID_INPUT');
    values.untilDate = end.toISOString().slice(0, 10);
  }
  if (values.sinceDate && values.untilDate && values.untilDate <= values.sinceDate) failure('INVALID_INPUT');
  return values;
}
// Explicit per-open-page refresh preference. No background Agent task or persisted mailbox mirror.
const autoCheckLabel = el('label', undefined, 'check');
const autoCheck = el('input');
autoCheck.type = 'checkbox';
autoCheck.id = 'auto-check-mail';
autoCheckLabel.append(autoCheck, el('span', t('自动检查新邮件')));
document.querySelector('.list-options-panel').append(autoCheckLabel);
const newMail = button(t('有新邮件，刷新列表'), async () => {
  newMail.hidden = true;
  await loadList();
});
newMail.hidden = true;
newMail.className = 'new-mail';
$('scope').after(newMail);

async function checkNewMail() {
  clearTimeout(pageState.lifecycle.mailCheckTimer);
  if (pageState.lifecycle.disposed || !autoCheck.checked) return;
  if (!pageState.lifecycle.busy && pageState.navigation.view === 'inbox' && document.body.dataset.workspace !== 'settings' && pageState.inbox.query && document.visibilityState === 'visible') {
    const generation = pageState.requests.generation('inbox');
    const captured = { ...pageState.inbox.query };
    const scope = pageState.account.accountId;
    await Promise.allSettled(
      pageState.account.accounts
        .filter((account) => scope === '*' || account.id === scope)
        .map(async (account) => {
          const previous = pageState.inbox.loadedMessages
            .filter((item) => item.ref.accountId === account.id)
            .map((item) => item.ref.uid);
          const state = pageState.inbox.mailboxPages.get(account.id);
          if (!state || state.loading || state.error) return;
          const page = await api('messages/list', { ...captured, accountId: account.id, limit: 1 });
          if (!pageState.requests.current('inbox', generation) || !autoCheck.checked) return;
          if (page.uidValidity !== state.uidValidity) {
            newMail.textContent = t('邮箱内容已更新，刷新列表');
            newMail.hidden = false;
          } else if (page.messages.some((item) => item.ref.uid > Math.max(0, ...previous))) {
            newMail.textContent = t('有新邮件，刷新列表');
            newMail.hidden = false;
          }
        }),
    );
  }
  if (!pageState.lifecycle.disposed && autoCheck.checked)
    pageState.lifecycle.mailCheckTimer = setTimeout(() => {
      void checkNewMail();
    }, 60000);
}
autoCheck.addEventListener('change', () => {
  if (autoCheck.checked) void checkNewMail();
  else {
    clearTimeout(pageState.lifecycle.mailCheckTimer);
    newMail.hidden = true;
  }
});
$('more').addEventListener('click', () => {
  void run(() => loadList(true));
});
window.addEventListener('beforeunload', (event) => {
  if ((pageState.composer.dirty && !hasRecovery()) || pageState.composer.pendingTransfer || hasUploads()) {
    event.preventDefault();
    event.returnValue = '';
  }
});
async function openDraftTarget() {
  const target = readWorkbenchTarget(location.search || location.hash);
  if (!target) return;
  // Consume the one-shot route. The host observes this in-page URL change, so opening
  // the same draft again still navigates even after the user moved to another view.
  history.replaceState(null, '', location.pathname);
  if (target.kind === 'setup') {
    const result = await api('accounts/setup', { id: target.id });
    if (result.status === 'connected') {
      await refreshAfterSetup(result);
      return;
    }
    if (['cancelled', 'expired'].includes(result.status)) {
      notice(t('这次连接操作已结束。已保存的邮箱仍可使用；需要添加邮箱时请重新打开连接表单。'), true);
      return;
    }
    await accountConnection.open(result, { fromTask: true });
    return;
  }
  if (!(await leaveEditor())) return;
  if (target.kind === 'batch') {
    await loadAccounts();
    selectView('batches');
    blankDetail();
    await loadList();
    await batchWorkspace.open(target.id);
    return;
  }
  const draft = await api('drafts/read', { id: target.id });
  await loadAccounts();
  selectView(['sending', 'sent', 'unknown'].includes(draft.status) ? 'sent' : 'drafts');
  blankDetail();
  await loadList();
  await openDraft(draft.id);
  if (draft.status === 'pending_confirmation') {
    notice(t('助手已准备好这封邮件。请核对发件邮箱和完整内容，再点击“发送”。'));
    $('draft-confirm')?.focus();
  }
}
window.addEventListener('hashchange', () => {
  if (!pageState.lifecycle.csrf || pageState.lifecycle.busy) pageState.navigation.pendingWorkbenchTarget = true;
  else void run(openDraftTarget);
});
void run(async () => {
  pageState.lifecycle.csrf = await pageClient.bootstrap();
  uiBridge.start();
  await loadAccounts();
  await loadList();
  await openDraftTarget();
});
