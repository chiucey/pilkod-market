#!/usr/bin/env node
/**
 * verify.mjs — 校验生成的 index.html
 *
 * 查那些「不会报错、只会安静坏掉」的问题：图片路径、alt、目录锚点、章节数、
 * 残留占位符、标签闭合、版式 token 是否在位。
 *
 * 用法：
 *   node verify.mjs <index.html> [--json]
 *
 * 退出码：0 = 无错误（可能有警告）；1 = 有错误。
 */
import { readFileSync, existsSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';

const VOID = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
  'link', 'meta', 'param', 'source', 'track', 'wbr']);

const RESIDUE = ['章节标题写在这里', '内容简介占位', '占位段落', '待填写', '示例文字', '待补充'];

const args = process.argv.slice(2);
const file = args.find((a) => !a.startsWith('--'));
const asJson = args.includes('--json');

const errors = [];
const warns = [];
const oks = [];
const err = (m) => errors.push(m);
const warn = (m) => warns.push(m);
const ok = (m) => oks.push(m);

function tagBalance(html) {
  const clean = html
    .replace(/<script[\s\S]*?<\/script>/gi, '')
    .replace(/<style[\s\S]*?<\/style>/gi, '')
    .replace(/<!--[\s\S]*?-->/g, '');
  const stack = [];
  const problems = [];
  const re = /<(\/?)([a-zA-Z][a-zA-Z0-9-]*)([^>]*?)(\/?)>/g;
  let m;
  while ((m = re.exec(clean)) !== null) {
    const closing = m[1];
    const t = m[2].toLowerCase();
    const selfClose = m[4];
    if (VOID.has(t) || selfClose === '/') continue;
    if (!closing) {
      stack.push({ t, at: m.index });
    } else {
      const top = stack.pop();
      if (!top) problems.push(`多余的 </${t}>`);
      else if (top.t !== t) problems.push(`<${top.t}> 被 </${t}> 关闭`);
    }
  }
  stack.forEach((s) => problems.push(`未闭合 <${s.t}>`));
  return problems;
}

function main() {
  if (!file) {
    console.error('用法: node verify.mjs <index.html> [--json]');
    process.exit(2);
  }
  const path = resolve(file);
  if (!existsSync(path)) {
    console.error(`文件不存在：${path}`);
    process.exit(1);
  }
  const html = readFileSync(path, 'utf-8');
  const dir = dirname(path);

  /* 1. 骨架 */
  if (/^<!DOCTYPE html>/i.test(html.trim())) ok('doctype');
  else err('缺少 <!DOCTYPE html>');
  if (/<title>[^<]{1,120}<\/title>/i.test(html)) ok('title 非空');
  else err('缺少 title 或为空');
  if (/name="viewport"/i.test(html)) ok('viewport meta');
  else warn('没有 viewport meta，手机上会按桌面宽度渲染');

  /* 2. 标签闭合 */
  const bad = tagBalance(html);
  if (bad.length) bad.forEach((p) => err('标签问题：' + p));
  else ok('标签全部闭合');

  /* 3. 残留占位（组件样式库区块内不算） */
  const noSandbox = html.replace(/<section class="sandbox"[\s\S]*?<\/section>/g, '');
  const residues = RESIDUE.filter((w) => noSandbox.includes(w));
  const leftTokens = [...new Set((noSandbox.match(/\{\{[A-Z0-9_]+\}\}/g) || []))];
  if (residues.length) err('残留占位文案：' + residues.join('、'));
  if (leftTokens.length) err('未替换的模板占位符：' + leftTokens.join(' '));
  if (!residues.length && !leftTokens.length) ok('无残留占位');

  /* 4. 资源引用 */
  const refs = [...new Set([...html.matchAll(/(?:src|href)="([^"#][^"]*)"/g)].map((m) => m[1]))]
    .filter((u) => !/^(https?:)?\/\//i.test(u));
  let missing = 0;
  refs.forEach((r) => {
    const p = join(dir, decodeURIComponent(r));
    if (!existsSync(p)) { err(`资源不存在：${r}`); missing++; }
  });
  if (!missing) ok(`${refs.length} 个本地资源引用全部存在`);

  /* 5. 图片 alt */
  const imgs = [...html.matchAll(/<img\b[^>]*>/gi)].map((m) => m[0]);
  let noAlt = 0;
  imgs.forEach((tag) => {
    const m = tag.match(/alt="([^"]*)"/i);
    if (!m || !m[1].trim()) { err(`图片缺 alt：${tag.slice(0, 80)}`); noAlt++; }
  });
  if (imgs.length && !noAlt) ok(`${imgs.length} 张图片都有 alt`);
  if (!imgs.length) warn('页面里没有 <img>，检查封面图是不是没生成');

  /* 6. 目录锚点 */
  const ids = [...new Set([...html.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]))];
  const navMatch = html.match(/<nav[^>]*id="nav"[\s\S]*?<\/nav>/i);
  if (!navMatch) err('找不到 <nav id="nav">，目录不会高亮');
  else {
    const hrefs = [...navMatch[0].matchAll(/href="#([^"]+)"/g)].map((m) => m[1]);
    if (!hrefs.length) warn('目录里没有条目');
    const dead = hrefs.filter((h) => !ids.includes(h));
    if (dead.length) err('目录指向不存在的锚点：' + dead.join(' '));
    else ok(`${hrefs.length} 条目录锚点全部命中`);
  }

  /* 7. 章节数与 id 唯一性 */
  const sections = (html.match(/<section class="chapter"/g) || []).length;
  if (sections === 0) warn('没有 <section class="chapter">，页面只有封面');
  const dupIds = ids.filter((id, i) => ids.indexOf(id) !== i);
  if (dupIds.length) err('重复的 id：' + [...new Set(dupIds)].join(' '));
  else ok(`${sections} 个章节，id 无重复`);

  /* 8. 版式 token */
  ['--paper', '--ink', '--amber', '--deep'].forEach((t) => {
    if (!html.includes(t + ':')) err(`缺少版式变量 ${t}`);
  });
  ok('白底 / 黑字 / 橙黄 / 深色 token 齐备');
  if (/prefers-color-scheme\s*:\s*dark/i.test(html)) warn('有深色模式分支，会破坏白底黑字的固定视觉');

  /* 9. 打印样式 */
  if (!/@media print/i.test(html)) warn('没有 @media print，导出 PDF 会带上侧栏和按钮');
  else ok('打印样式存在');

  /* 10. 体积 */
  const kb = (statSync(path).size / 1024).toFixed(0);
  if (kb > 800) warn(`单页 ${kb}KB，偏大（考虑把正文图再压一档）`);
  else ok(`单页 ${kb}KB`);

  if (asJson) {
    console.log(JSON.stringify({ file: path, ok: oks, warn: warns, error: errors }, null, 2));
  } else {
    console.log('');
    oks.forEach((m) => console.log('[OK]   ' + m));
    warns.forEach((m) => console.log('[WARN] ' + m));
    errors.forEach((m) => console.log('[FAIL] ' + m));
    console.log('');
    if (errors.length) console.log(`✗ ${errors.length} 个错误 / ${warns.length} 个警告`);
    else console.log(`✓ 通过${warns.length ? '（' + warns.length + ' 个警告）' : ''}`);
    console.log('');
  }

  process.exit(errors.length ? 1 : 0);
}

main();
