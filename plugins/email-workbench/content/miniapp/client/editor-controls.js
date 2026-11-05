import { t } from './i18n.js';
import { createRichEditor as createCoreRichEditor } from './rich-editor.js';
import { icon, decorateAction } from './mail-view.js';

/** Presentation wrapper; the existing editor, schema and commands stay unchanged. */
export function createRichEditor(textarea, options) {
  const editor = createCoreRichEditor(textarea, options);
  const toolbar = textarea.nextElementSibling?.querySelector('.rich-toolbar');
  if (!toolbar) return editor;
  const more = document.createElement('details'); more.className = 'editor-more';
  const summary = document.createElement('summary'); summary.textContent = t('更多格式');
  summary.title = t('更多格式'); summary.setAttribute('aria-label', t('更多格式')); summary.replaceChildren(icon('more'));
  const controls = document.createElement('div'); controls.className = 'editor-more-controls';
  more.append(summary, controls);
  for (const control of [...toolbar.children]) {
    if (![t('加粗'), t('斜体'), t('链接'), t('图片')].includes(control.title)) controls.append(control);
    const names = { [t('加粗')]:'bold', [t('斜体')]:'italic', [t('链接')]:'link', [t('图片')]:'image', [t('撤销')]:'undo', [t('重做')]:'redo' };
    const name = names[control.textContent];
    if (name) decorateAction(control, name, control.parentElement === toolbar);
  }
  const groups = [[t('文字与段落'), [t('下划线'), t('列表'), t('编号'), t('引用')]], [t('表格'), [t('表格'), t('加行'), t('加列'), t('删行'), t('删列')]], [t('编辑'), [t('撤销'), t('重做'), t('纯文本')]]];
  const remaining = [...controls.children];
  for (const [title, names] of groups) {
    const group = document.createElement('div'); group.className = 'editor-menu-group';
    const heading = document.createElement('span'); heading.textContent = title; group.append(heading);
    for (const control of remaining) if (names.includes(control.title)) group.append(control);
    if (group.childElementCount > 1) controls.append(group);
  }
  if (controls.childElementCount) toolbar.append(more);
  more.addEventListener('toggle', () => { if (more.open) { const link = textarea.nextElementSibling?.querySelector('.rich-link-form'); if (link) link.hidden = true; } });
  more.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopPropagation(); more.open = false; summary.focus();
    } else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
      event.preventDefault();
      const choices = [...controls.querySelectorAll('button:not(:disabled), select:not(:disabled)')].filter(node => !node.hidden);
      const current = choices.indexOf(document.activeElement);
      const next = current < 0 ? (event.key === 'ArrowDown' ? 0 : choices.length - 1) : (current + (event.key === 'ArrowDown' ? 1 : choices.length - 1)) % choices.length;
      if (more.open && (!controls.hasAttribute('popover') || controls.matches(':popover-open'))) choices[next]?.focus();
      else {
        more.addEventListener('toggle', () => { if (more.open) choices[next]?.focus(); }, { once: true });
        more.open = true;
      }
    }
  });
  controls.addEventListener('click', (event) => {
    if (event.target.closest('button')) more.open = false;
  });
  return editor;
}
