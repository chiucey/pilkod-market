import { t, tt } from './i18n.js';
import { icon } from './icon.js';

/** Selection is local; every result refers to the exact account/folder/UID selected. */
export function createMailOrganizer(ctx) {
  const { $, el, button, api, notice } = ctx;
  const selected = new Map();
  let selecting = false;
  const bar = el('div', undefined, 'organize-bar');
  bar.hidden = true;
  const toggle = button(t('选择邮件'), () => {
    selecting = !selecting;
    if (!selecting) selected.clear();
    render();
    ctx.render();
  });
  toggle.classList.add('selection-toggle');
  $('list-options').before(toggle);
  $('mail-filters').after(bar);
  const key = (ref) => JSON.stringify(ref);
  const messages = () => [...selected.values()];
  function render() {
    toggle.textContent = selecting ? t('完成选择') : t('选择邮件');
    toggle.setAttribute('aria-pressed', String(selecting));
    bar.hidden = !selecting;
    bar.replaceChildren();
    if (!selecting) return;
    const loaded = ctx.messages();
    const allSelected = loaded.length > 0 && loaded.every((item) => selected.has(key(item.ref)));
    const firstLine = el('div', undefined, 'organize-line');
    const all = el('input'); all.type = 'checkbox';
    all.checked = allSelected; all.indeterminate = selected.size > 0 && !allSelected;
    all.disabled = !loaded.length;
    all.setAttribute('aria-label', t('选择已加载邮件'));
    all.addEventListener('change', () => {
      if (allSelected || selected.size === 100) selected.clear();
      else {
        for (const item of loaded) if (selected.size < 100) selected.set(key(item.ref), item);
      }
      render(); ctx.render();
      if (loaded.length > 100 && selected.size === 100) notice(t('每次最多处理 100 封，已选择前 100 封。'));
    });
    const cancel = button(t('取消'), () => { selected.clear(); selecting = false; render(); ctx.render(); }, 'quiet');
    firstLine.append(all, el('strong', tt`已选 ${selected.size} 封`), cancel);
    const secondLine = el('div', undefined, 'organize-line');
    const menu = el('details', undefined, 'action-menu organize-menu');
    const summary = el('summary'); summary.append(el('span', t('标记')), icon('chevronDown'));
    summary.setAttribute('aria-disabled', String(!selected.size));
    summary.addEventListener('click', (event) => { if (!selected.size) event.preventDefault(); });
    const panel = el('div', undefined, 'action-menu-panel');
    for (const [label, flag, value] of [[t('标为已读'), 'seen', true], [t('标为未读'), 'seen', false], [t('加星标'), 'flagged', true], [t('取消星标'), 'flagged', false]]) {
      const action = button(label, () => { menu.open = false; return apply(messages(), flag, value); }, 'quiet');
      action.disabled = !selected.size; panel.append(action);
    }
    menu.append(summary, panel);
    const move = button(t('移动…'), () => chooseMove(messages())); move.prepend(icon('folder')); move.disabled = !selected.size;
    secondLine.append(menu, move, el('span', tt`当前已加载 ${loaded.length} 封`, 'organize-scope'));
    bar.append(firstLine, secondLine);
  }
  function row(item, content) {
    if (!selecting) return content;
    const wrap = el('div', undefined, 'message-selection-row');
    const box = el('input');
    box.type = 'checkbox';
    box.checked = selected.has(key(item.ref));
    box.setAttribute('aria-label', tt`选择邮件：${item.subject || t('无主题')}`);
    box.addEventListener('change', () => {
      if (box.checked && selected.size >= 100) {
        box.checked = false;
        notice(t('每次最多处理 100 封。'), true);
        return;
      }
      if (box.checked) selected.set(key(item.ref), item);
      else selected.delete(key(item.ref));
      wrap.dataset.selected = String(box.checked);
      render();
    });
    wrap.dataset.selected = String(box.checked);
    wrap.append(box, content);
    return wrap;
  }
  async function apply(items, flag, value, destination) {
    const results = [];
    for (const item of items) {
      try {
        if (destination) await api('messages/move', { ref: item.ref, destination });
        else await api('messages/flag', { ref: item.ref, flag, value });
        results.push({ item, ok: true });
        selected.delete(key(item.ref));
      } catch (error) {
        results.push({ item, error: error.code });
      }
    }
    await ctx.refresh();
    render();
    const failed = results.filter((result) => !result.ok);
    if (failed.length) {
      const panel = el('section', undefined, 'inline-error');
      panel.append(
        el('strong', tt`${results.length - failed.length} 封已处理，${failed.length} 封未确认完成`),
      );
      for (const result of failed)
        panel.append(el('p', `${result.item.subject || t('无主题')}：${ctx.error(result.error)}`));
      panel.append(
        el('p', t('失败项仍保留选择。移动结果不明时先检查原文件夹和目标文件夹，再决定下一步。')),
      );
      $('items').prepend(panel);
    }
    notice(
      tt`${results.length - failed.length} / ${results.length} 封已处理。${failed.length ? t('请查看列表顶部逐封结果。') : ''}`,
      !!failed.length,
    );
  }
  async function chooseMove(items, role) {
    if (new Set(items.map((item) => item.ref.accountId)).size !== 1) {
      notice(t('移动邮件时请先选择同一个邮箱的邮件；读写状态可以跨邮箱批量处理。'), true);
      return;
    }
    const folders = await api('messages/folders', { accountId: items[0].ref.accountId });
    const candidates = folders.filter(
      (folder) => !items.some((item) => item.ref.folder === folder.path),
    );
    if (!candidates.length) {
      notice(t('没有可移动到的其他文件夹。'), true);
      return;
    }
    const dialog = el('dialog', undefined, 'confirmation-dialog move-dialog');
    const opener = document.activeElement;
    const form = el('form');
    form.method = 'dialog';
    const title = el('h2', tt`移动 ${items.length} 封邮件`);
    title.id = `move-title-${crypto.randomUUID()}`;
    dialog.setAttribute('aria-labelledby', title.id);
    form.append(title);
    const label = el('label', t('目标文件夹'));
    const select = el('select');
    for (const folder of candidates) {
      const option = el(
        'option',
        `${folder.path}${folder.role === 'trash' ? t('（垃圾箱）') : folder.role === 'archive' ? t('（归档）') : ''}`,
      );
      option.value = folder.path;
      select.append(option);
    }
    const preferred = candidates.find((folder) => folder.role === role);
    if (preferred) select.value = preferred.path;
    label.append(select);
    form.append(label);
    if (role && !preferred) form.append(el('p', t('服务商没有标记对应文件夹，请选择正确目标。')));
    form.append(
      el(
        'p',
        items.length === 1
          ? items[0].subject || t('无主题')
          : t('所选邮件会移出原文件夹。此操作不会清空垃圾箱。'),
      ),
    );
    const cancel = el('button', t('取消'));
    cancel.value = 'cancel';
    const move = el('button', t('确认移动'));
    move.value = 'move';
    move.className = 'primary';
    const actions = el('div', undefined, 'actions');
    actions.append(cancel, move);
    form.append(actions);
    dialog.append(form);
    document.body.append(dialog);
    dialog.showModal();
    const choice = await new Promise((resolve) =>
      dialog.addEventListener('close', () => resolve(dialog.returnValue), { once: true }),
    );
    const destination = select.value;
    dialog.remove();
    opener?.focus();
    if (choice === 'move') await apply(items, undefined, undefined, destination);
  }
  return {
    row,
    selectedRefs: () => [...selected.values()].map((item) => item.ref),
    clear() {
      selected.clear();
      selecting = false;
      render();
    },
    hide() {
      bar.hidden = true;
    },
    controls(item) {
      const group = el('div', undefined, 'actions');
      group.append(
        button(t('移动到…'), () => chooseMove([item])),
        button(t('归档'), () => chooseMove([item], 'archive')),
        button(t('移到垃圾箱'), () => chooseMove([item], 'trash')),
      );
      return group;
    },
  };
}
