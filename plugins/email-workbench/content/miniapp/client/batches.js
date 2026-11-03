import { t, tt } from './i18n.js';
import { renderDraftBody } from './mail-content.js';

const batchStates = {
  pending_confirmation: t('等待工作台确认'),
  sending: t('正在投递'),
  paused: t('已暂停'),
  completed: t('清单已处理'),
  cancelled: t('已取消'),
  invalidated: t('内容已变更，需重新检查'),
};
const itemStates = {
  pending: t('等待确认'),
  queued: t('等待投递'),
  sending: t('正在投递'),
  sent: t('已提交邮件服务器'),
  unknown: t('结果不确定'),
  skipped: t('未发送'),
};

/** The page prepares and observes; only a deliberate page click requests approval. */
export function createBatchWorkspace(ctx) {
  const { $, el, button, api, notice, date, bytes } = ctx;
  let activeId;
  let timer;
  let disposed = false;
  let generation = 0;
  let request;
  const active = () =>
    !disposed && activeId && $('detail').dataset.batch === activeId && $('batch-status');
  function frame(title) {
    generation += 1;
    ctx.resetEditor();
    delete $('detail').dataset.batch;
    delete $('detail').dataset.accountManagement;
    $('detail').replaceChildren(el('h2', title));
    clearTimeout(timer);
    $('items').querySelectorAll('[data-batch-id]').forEach((row) => row.removeAttribute('aria-current'));
    activeId = undefined;
  }
  function summary(messages) {
    const unique = new Set(
      messages.flatMap(({ draft }) => [
        ...draft.content.to,
        ...draft.content.cc,
        ...draft.content.bcc,
      ]),
    );
    const accounts = new Set(messages.map(({ draft }) => draft.content.accountId));
    return tt`${messages.length} 封邮件 · ${unique.size} 个地址 · ${accounts.size} 个发件邮箱`;
  }
  function contentCard(message, expanded = false, flat = false) {
    const { draft, account, attachments = [] } = message;
    const card = el(flat ? 'article' : 'details', undefined, 'review-card');
    if (!flat) card.open = expanded;
    card.append(
      el(
        flat ? 'h3' : 'summary',
        flat
          ? draft.content.subject || t('无主题')
          : `${draft.content.to.join(', ') || draft.content.bcc.join(', ')} · ${draft.content.subject || t('无主题')}`,
      ),
    );
    const meta = el('dl', undefined, 'review-envelope');
    for (const [label, text] of [
      [t('发件邮箱'), account?.address ?? t('已断开')],
      ['To', draft.content.to.join(', ')],
      ['Cc', draft.content.cc.join(', ')],
      ['Bcc', draft.content.bcc.join(', ')],
    ]) {
      meta.append(el('dt', label), el('dd', text || t('无')));
    }
    card.append(meta, renderDraftBody(draft.content, { imageUrl: ctx.imageUrl }));
    if (draft.content.to.length + draft.content.cc.length > 1)
      card.append(el('p', t('这封邮件的 To / Cc 收件人彼此可见。'), 'review-note'));
    for (const attachment of attachments)
      card.append(el('p', `${attachment.filename} · ${bytes(attachment.bytes)}`, 'attachment'));
    return card;
  }
  async function readPreviews(references) {
    const messages = [];
    for (const ref of references) {
      const draft = await api('drafts/read', { id: ref.id });
      if (draft.revision !== ref.revision || draft.status !== 'draft')
        throw Object.assign(new Error('REVISION_CONFLICT'), { code: 'REVISION_CONFLICT' });
      const attachments = [];
      for (const id of draft.content.attachmentIds) {
        const value = await api('attachments/read', { id, offset: 0 });
        attachments.push({
          id: value.id,
          filename: value.filename,
          bytes: value.bytes,
          sha256: value.sha256,
        });
      }
      messages.push({
        draft,
        account: ctx.accounts().find((a) => a.id === draft.content.accountId),
        attachments,
      });
    }
    return messages;
  }
  async function review(references, pendingBatch) {
    if (!references.length || references.length > 100) {
      notice(t('每份清单请选择 1 至 100 封已保存草稿。'), true);
      return;
    }
    const messages = pendingBatch ? pendingBatch.preview.messages : await readPreviews(references);
    frame(t('检查发送清单'));
    const titleRow = el('header', undefined, 'subject-line batch-review-heading');
    const state = el('span', t('待确认'), 'inline-state');
    state.dataset.status = 'pending';
    titleRow.append($('detail').querySelector('h2'), state);
    $('detail').prepend(titleRow);
    $('detail').append(el('p', summary(messages), 'review-summary'));
    const titleLabel = el('label', t('任务名称'), 'batch-name');
    const title = el('input');
    title.id = 'batch-title';
    title.maxLength = 120;
    title.value =
      messages.length === 1 ? messages[0].draft.content.subject || t('邮件发送') : t('批量邮件');
    if (pendingBatch) {
      title.value = pendingBatch.request.title;
      title.readOnly = true;
    }
    titleLabel.append(title);
    $('detail').append(titleLabel);
    const groups = new Map();
    messages.forEach((message) => {
      const key = JSON.stringify([
        message.draft.content.subject,
        message.draft.content.text,
        message.draft.content.html,
        message.attachments.map((a) => [a.filename, a.sha256]),
      ]);
      const group = groups.get(key) ?? [];
      group.push(message);
      groups.set(key, group);
    });
    const shared = groups.size === 1 && messages.length > 1;
    const occurrences = new Map();
    messages.forEach(({ draft }, index) => {
      for (const field of ['to', 'cc', 'bcc'])
        for (const address of draft.content[field]) {
          const key = address.toLowerCase();
          const entries = occurrences.get(key) ?? [];
          entries.push({ index, field });
          occurrences.set(key, entries);
        }
    });
    const duplicates = [...occurrences].filter(([, entries]) => entries.length > 1);
    const layout = el('div', undefined, 'review-layout');
    const recipients = el('nav', undefined, 'review-recipients');
    recipients.setAttribute('aria-label', t('固定清单中的邮件'));
    recipients.append(el('h3', tt`待发送 · ${messages.length} 封`));
    const preview = el('section', undefined, 'review-content');
    preview.tabIndex = 0;
    preview.id = 'review-preview';
    preview.setAttribute('aria-label', t('所选邮件的完整内容'));
    const choices = [];
    const choose = (index) => {
      choices.forEach((row, at) => row.setAttribute('aria-current', String(at === index)));
      preview.replaceChildren(
        el('p', tt`第 ${index + 1} / ${messages.length} 封 · 最终内容`, 'eyebrow'),
      );
      if (shared)
        preview.append(
          el(
            'p',
            t('共同内容：所有邮件的主题、正文和附件相同。每封独立投递，收件人以各封信封信息为准。'),
            'common-content',
          ),
        );
      else if (messages.length > 1)
        preview.append(el('p', t('逐人内容存在差异，请检查姓名、时间、链接与附件。'), 'review-note'));
      if (duplicates.length) {
        const warning = el('details', undefined, 'review-note');
        warning.append(
          el('summary', tt`${duplicates.length} 个地址重复出现，请核对是否有意发送多封`),
        );
        for (const [address, entries] of duplicates)
          warning.append(
            el(
              'p',
              `${address}：${entries.map(({ index: messageIndex, field }) => tt`第 ${messageIndex + 1} 封 ${field.toUpperCase()}`).join('、')}`,
            ),
          );
        preview.append(warning);
      }
      preview.append(contentCard(messages[index], true, true));
      preview.scrollTop = 0;
    };
    messages.forEach((message, index) => {
      const content = message.draft.content;
      const row = button('', () => choose(index), 'review-recipient');
      const copy = el('span');
      copy.append(
        el('strong', content.to.join(', ') || content.bcc.join(', ') || content.cc.join(', ')),
        el('small', content.subject || t('无主题')),
      );
      row.append(el('span', String(index + 1), 'review-number'), copy);
      row.setAttribute('aria-controls', preview.id);
      choices.push(row);
      recipients.append(row);
    });
    choose(0);
    layout.append(recipients, preview);
    $('detail').append(layout);
    const actions = el('div', undefined, 'actions review-foot');
    request = undefined;
    const submit = button(
      tt`确认发送这 ${messages.length} 封`,
      async () => {
        if (!title.value.trim()) {
          notice(t('请填写任务名称。'), true);
          title.focus();
          return;
        }
        request ??= {
          requestId: crypto.randomUUID(),
          title: title.value.trim(),
          drafts: references,
        };
        const frozen = pendingBatch ?? await api('batches/confirm', request);
        const result = await api('batches/approve', { id: frozen.id });
        await open(result.id);
        notice(t('已在工作台确认并提交批量发送。SMTP 接受不代表收件人已收到。'));
      },
      'primary',
    );
    actions.append(el('span', t('核对这份固定清单后，在工作台中一次确认。'), 'muted'), submit);
    if (pendingBatch)
      actions.append(
        button(t('取消此发送清单'), async () => {
          await api('batches/stop', { id: pendingBatch.id, action: 'cancel' });
          await open(pendingBatch.id);
          notice(t('发送清单已取消，尚未投递的邮件不会发送。'));
        }),
      );
    $('detail').append(actions);
    ctx.showDetail();
  }
  function renderListRow(row, batch) {
    const sent = batch.items.filter((item) => item.status === 'sent').length;
    const title = el('span', undefined, 'subject-line');
    const state = el('span', batch.status === 'pending_confirmation' ? t('待确认') : batchStates[batch.status], 'inline-state');
    state.dataset.status = batch.status;
    title.append(el('strong', batch.title ?? batch.request.title), state);
    row.replaceChildren(
      title,
      el('span', tt`${batch.items.length} 封邮件 · ${sent} 封已接受`, 'muted'),
      el('time', date(batch.updatedAt), 'muted'),
    );
    row.setAttribute('aria-current', String(batch.id === activeId));
  }
  async function list(current = () => true, signal) {
    const batches = await api('batches/list', undefined, signal);
    if (!current()) return;
    const scope = ctx.accountId();
    const rows = batches.filter(
      (batch) => scope === '*' || !batch.accountIds || batch.accountIds.includes(scope),
    );
    $('items').replaceChildren();
    $('selection-bar').hidden = true;
    const intro = el('section', undefined, 'batch-intro');
    intro.append(
      el('h3', t('一份清单，一次确认')),
      el('p', t('导入收件人名单，填写邮件内容，逐人预览后确认发送。')),
      button(t('从名单准备草稿'), () => ctx.prepareMailing(), 'primary'),
    );
    $('items').append(intro);
    for (const batch of rows) {
      const row = button(
        '',
        async () => {
          if (await ctx.leaveEditor()) await open(batch.id);
        },
        'item',
      );
      row.dataset.batchId = batch.id;
      renderListRow(row, batch);
      $('items').append(row);
    }
    if (!rows.length)
      $('items').append(el('p', t('还没有批量任务。从名单准备第一批邮件；也可以在草稿中勾选已有邮件，集中确认发送。'), 'empty'));
    if (!rows.length && $('detail').querySelector('.detail-empty')) {
      const empty = el('div', undefined, 'empty detail-empty');
      empty.append(el('h2', t('从名单准备草稿')), el('p', t('导入收件人名单，填写邮件内容，逐人预览后确认发送。')));
      $('detail').replaceChildren(empty);
    }
    $('scope').textContent = tt`${rows.length} 个发送任务`;
    $('more').hidden = true;
    notice(t('每封的完整内容先固定；修改或追加邮件需要新的确认。'));
  }
  async function open(id) {
    const batch = await api('batches/read', { id });
    if (batch.status === 'pending_confirmation') {
      await review(batch.request.drafts, batch);
      return;
    }
    frame(batch.request.title);
    activeId = id;
    $('detail').dataset.batch = id;
    $('detail').append(el('p', summary(batch.preview.messages), 'review-summary'));
    const status = el('p', undefined, 'task-status');
    status.id = 'batch-status';
    status.setAttribute('role', 'status');
    $('detail').append(status);
    const progress = el('progress');
    progress.id = 'batch-progress';
    progress.max = batch.items.length;
    progress.setAttribute('aria-label', t('已处理邮件'));
    $('detail').append(progress);
    const items = el('div');
    items.id = 'batch-results';
    $('detail').append(items);
    const actions = el('div', undefined, 'actions');
    actions.id = 'batch-actions';
    $('detail').append(actions);
    const originals = el('details');
    originals.append(el('summary', t('查看这次确认的完整清单')));
    batch.preview.messages.forEach((message) => originals.append(contentCard(message)));
    $('detail').append(originals);
    await updateProgress(batch);
    ctx.showDetail();
    if (needsPolling(batch)) schedule();
  }
  const needsPolling = (batch) =>
    ['pending_confirmation', 'sending'].includes(batch.status) ||
    batch.items.some((item) => item.status === 'sending');
  async function updateProgress(batch) {
    if (!active() || batch.id !== activeId) return;
    renderProgress(batch);
    const row = [...$('items').querySelectorAll('[data-batch-id]')]
      .find((item) => item.dataset.batchId === batch.id);
    if (row) renderListRow(row, batch);
    if (!['pending_confirmation', 'sending'].includes(batch.status)) await ctx.refresh();
  }
  function renderProgress(batch) {
    if (!active() || batch.id !== activeId) return;
    const sent = batch.items.filter((item) => item.status === 'sent').length;
    const unknown = batch.items.filter((item) => item.status === 'unknown').length;
    $('batch-status').textContent =
      tt`${batchStates[batch.status]} · ${sent}/${batch.items.length} 封已提交邮件服务器${unknown ? tt` · ${unknown} 封结果不确定` : ''}`;
    $('batch-progress').value = batch.items.filter((item) =>
      ['sent', 'unknown', 'skipped'].includes(item.status),
    ).length;
    $('batch-results').replaceChildren(
      ...batch.items.map((item) => {
        const preview = batch.preview.messages.find((message) => message.draft.id === item.draftId);
        const row = el('div', undefined, 'result-row');
        const identity = el('div', undefined, 'result-identity');
        identity.append(
          button(
            preview?.draft.content.subject || t('（无主题）'),
            async () => {
              if (await ctx.leaveEditor()) await ctx.openDraft(item.draftId);
            },
            'result-subject',
          ),
          el(
            'span',
            preview?.draft.content.to.join(', ') || preview?.draft.content.bcc.join(', ') || t('邮件'),
          ),
        );
        const status = el('strong', itemStates[item.status], 'item-state');
        status.dataset.status = item.status;
        row.append(identity, status);
        if (item.accepted?.length && item.rejected?.length)
          row.append(el('small', tt`已接受：${item.accepted.join(', ')}`));
        if (item.rejected?.length) row.append(el('small', tt`未接受：${item.rejected.join(', ')}`));
        return row;
      }),
    );
    const actions = $('batch-actions');
    actions.replaceChildren();
    if (['pending_confirmation', 'sending'].includes(batch.status)) {
      actions.append(
        button(t('暂停未发送邮件'), async () => {
          generation += 1;
          const stopped = await api('batches/stop', { id: batch.id, action: 'pause' });
          await updateProgress(stopped);
          if (needsPolling(stopped)) schedule();
          notice(t('已停止后续投递。正在投递的邮件仍可能完成，继续发送需要重新确认。'));
        }),
      );
      actions.append(
        button(t('取消剩余清单'), async () => {
          generation += 1;
          const stopped = await api('batches/stop', { id: batch.id, action: 'cancel' });
          await updateProgress(stopped);
          if (needsPolling(stopped)) schedule();
        }),
      );
    } else {
      clearTimeout(timer);
      const remaining = batch.items.filter((item) =>
        ['skipped', 'pending', 'queued'].includes(item.status),
      );
      if (remaining.length)
        actions.append(
          button(t('检查未发送草稿'), async () => {
            const refs = [];
            for (const item of remaining) {
              const draft = await api('drafts/read', { id: item.draftId });
              if (draft.status === 'draft') refs.push({ id: draft.id, revision: draft.revision });
            }
            if (refs.length) await review(refs);
            else notice(t('没有可重新检查的未发送草稿。'));
          }),
        );
    }
    actions.append(
      button(t('刷新状态'), async () => {
        generation += 1;
        const updated = await api('batches/read', { id: batch.id });
        await updateProgress(updated);
        if (active() && needsPolling(updated)) schedule();
      }),
    );
    if (unknown)
      actions.append(
        el('p', t('结果不确定的项不能自动重发。请通过服务商发送记录或收件端核对。'), 'review-note'),
      );
  }
  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(async () => {
      if (!active()) return;
      const expectedGeneration = generation;
      try {
        const batch = await api('batches/read', { id: activeId });
        if (expectedGeneration !== generation) return;
        let updated = false;
        await ctx.run(async () => {
          if (!active() || expectedGeneration !== generation) return;
          await updateProgress(batch);
          updated = true;
        });
        if (active() && expectedGeneration === generation && (!updated || needsPolling(batch))) schedule();
      } catch {
        if (active() && expectedGeneration === generation)
          notice(t('任务状态暂未更新，可点“刷新状态”重新核对。'), true);
      }
    }, 2000);
  }
  return {
    list,
    review,
    open,
    dispose: () => {
      generation += 1;
      disposed = true;
      clearTimeout(timer);
    },
    resume: () => {
      disposed = false;
      if (active()) schedule();
    },
  };
}
