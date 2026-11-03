// Menus remain DOM descendants of their dialog, but paint in the browser's top layer.
// This avoids clipping by the editor's scroll area without relaxing its overflow rules.
export function installWorkbenchPopups(doc = document) {
  const win = doc.defaultView;
  const selector = '.editor-more, .action-menu, .sender-help, .attachment-help, .search-advanced, #list-options';
  const open = new Map();
  const bounds = (details) => {
    const viewport = win.visualViewport;
    const left = viewport?.offsetLeft ?? 0, top = viewport?.offsetTop ?? 0;
    const right = left + (viewport?.width ?? win.innerWidth);
    const bottom = top + (viewport?.height ?? win.innerHeight);
    const dialog = details.closest('dialog[open]')?.getBoundingClientRect();
    return { left: Math.max(left, dialog?.left ?? left) + 8, top: Math.max(top, dialog?.top ?? top) + 8,
      right: Math.min(right, dialog?.right ?? right) - 8, bottom: Math.min(bottom, dialog?.bottom ?? bottom) - 8 };
  };
  const position = (details, panel) => {
    const anchor = details.querySelector('summary').getBoundingClientRect();
    const box = bounds(details);
    panel.style.maxWidth = `${Math.max(0, box.right - box.left)}px`;
    panel.style.maxHeight = `${Math.max(0, box.bottom - box.top)}px`;
    const natural = panel.getBoundingClientRect();
    const below = Math.max(0, box.bottom - anchor.bottom - 6);
    const above = Math.max(0, anchor.top - box.top - 6);
    const preferAbove = details.matches('.compose-more, .attachment-help');
    const upwards = preferAbove ? above >= natural.height || above > below : below < natural.height && above > below;
    panel.style.maxHeight = `${Math.min(box.bottom - box.top, upwards ? above : below)}px`;
    const size = panel.getBoundingClientRect();
    const start = details.matches('.editor-more, .compose-more, .attachment-help, .account-picker, .organize-menu');
    const clamp = (value, min, max) => Math.max(min, Math.min(value, max));
    panel.style.left = `${clamp(start ? anchor.left : anchor.right - size.width, box.left, box.right - size.width)}px`;
    panel.style.top = `${clamp(upwards ? anchor.top - size.height - 6 : anchor.bottom + 6, box.top, box.bottom - size.height)}px`;
  };
  const close = (details, panel) => {
    if (panel.matches(':popover-open')) panel.hidePopover();
    open.delete(details);
  };
  const onToggle = (event) => {
    const details = event.target;
    if (!details.matches?.(selector)) return;
    const panel = details.querySelector(':scope > :not(summary)');
    if (!panel) return;
    if (typeof panel.showPopover !== 'function') { details.classList.add('popup-inline'); return; }
    if (!details.open) { close(details, panel); return; }
    for (const [other, otherPanel] of open) if (other !== details) { other.open = false; close(other, otherPanel); }
    panel.setAttribute('popover', 'manual');
    panel.classList.add('workbench-popup');
    Object.assign(panel.style, { position: 'fixed', margin: '0', right: 'auto', bottom: 'auto' });
    if (!panel.matches(':popover-open')) panel.showPopover();
    open.set(details, panel);
    position(details, panel);
  };
  const reposition = () => {
    for (const [details, panel] of open) {
      if (!details.isConnected || !details.open || details.closest('dialog:not([open])')) close(details, panel);
      else position(details, panel);
    }
  };
  const dismiss = (event) => {
    for (const [details, panel] of open) if (!details.contains(event.target)) { details.open = false; close(details, panel); }
  };
  const escape = (event) => {
    if (event.key !== 'Escape' || !open.size) return;
    event.preventDefault(); event.stopPropagation();
    for (const [details, panel] of open) { details.open = false; close(details, panel); details.querySelector('summary').focus(); }
  };
  doc.addEventListener('toggle', onToggle, true);
  doc.addEventListener('scroll', reposition, true);
  doc.addEventListener('click', dismiss);
  doc.addEventListener('keydown', escape, true);
  win.addEventListener('resize', reposition);
  win.visualViewport?.addEventListener('resize', reposition);
  win.visualViewport?.addEventListener('scroll', reposition);
  const dispose = () => {
    for (const [details, panel] of open) close(details, panel);
    doc.removeEventListener('toggle', onToggle, true);
    doc.removeEventListener('scroll', reposition, true);
    doc.removeEventListener('click', dismiss);
    doc.removeEventListener('keydown', escape, true);
    win.removeEventListener('resize', reposition);
    win.visualViewport?.removeEventListener('resize', reposition);
    win.visualViewport?.removeEventListener('scroll', reposition);
    win.removeEventListener('pagehide', onPageHide);
  };
  const onPageHide = (event) => {
    if (!event.persisted) dispose();
    else for (const [details, panel] of open) { details.open = false; close(details, panel); }
  };
  win.addEventListener('pagehide', onPageHide);
  return dispose;
}
