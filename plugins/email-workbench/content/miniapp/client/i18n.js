import english from './messages.en.js';

const preferenceKey = 'email-workbench-language';
export const supportedLanguages = ['auto', 'zh', 'en'];
export function languagePreference() {
  try { const saved = globalThis.localStorage?.getItem(preferenceKey); return supportedLanguages.includes(saved) ? saved : 'auto'; }
  catch { return 'auto'; }
}
export function locale() {
  // This module also serves Node validation code: keep wire/protocol copy stable.
  if (typeof document === 'undefined') return 'zh';
  const preference = languagePreference();
  if (preference !== 'auto') return preference;
  const languages = globalThis.navigator?.languages ?? [globalThis.navigator?.language];
  for (const language of languages) {
    if (/^zh(?:-|$)/iu.test(language)) return 'zh';
    if (/^en(?:-|$)/iu.test(language)) return 'en';
  }
  return 'en';
}
export function localeTag() { return locale() === 'zh' ? 'zh-CN' : 'en-US'; }
export function saveLanguagePreference(value) {
  if (!supportedLanguages.includes(value)) throw new TypeError('Unsupported language');
  // A storage failure must not falsely report a persisted language choice.
  globalThis.localStorage.setItem(preferenceKey, value);
}
export function t(source) { return locale() === 'en' ? (english[source] ?? source) : source; }
export function tt(parts, ...values) {
  const source = parts.join('{}');
  let index = 0;
  // Substitute values once; braces and markup in user content are never parsed.
  return t(source).replace(/\{\}/gu, () => String(values[index++]));
}
/** Only called on our static HTML shell, before inserting any user mail/data.
 * No observer, DOM-wide runtime replacement, or translation of message frames. */
export function localizeShell(document) {
  document.documentElement.lang = localeTag();
  const walker = document.createTreeWalker(document.documentElement, 4);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    if (['SCRIPT', 'STYLE'].includes(node.parentElement?.tagName)) continue;
    const text = node.textContent.trim();
    if (text && Object.hasOwn(english, text)) node.textContent = node.textContent.replace(text, t(text));
  }
  for (const node of document.querySelectorAll('[aria-label], [title], [placeholder]'))
    for (const attr of ['aria-label', 'title', 'placeholder'])
      if (node.hasAttribute(attr)) node.setAttribute(attr, t(node.getAttribute(attr)));
}
