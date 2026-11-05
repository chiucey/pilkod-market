#!/usr/bin/env node
// check-page.mjs — 电子版页面确定性校验
//
// 用法: node check-page.mjs <index.html>
// 退出码: 0 = 无错误（可能有警告）, 1 = 有错误
//
// 只做「用正则就能判定」的检查：配色契约、朗读标记对齐、表格降级、
// 外链依赖、打印与响应式块、音频文件是否真的存在。
// 视觉问题（栏宽、压字、溢出）静态查不出来，要靠浏览器实测。
//
// 不依赖任何第三方包；只用 Node.js 内置 fs / path。

import { readFileSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const target = process.argv[2];
if (!target) {
  console.error('Usage: node check-page.mjs <index.html>');
  process.exit(2);
}
const file = resolve(target);
if (!existsSync(file)) {
  console.error(`[FAIL] 文件不存在: ${file}`);
  process.exit(1);
}
const html = readFileSync(file, 'utf-8');
const dir = dirname(file);

let errors = 0;
let warns = 0;
const fail = (m) => { console.error(`[FAIL] ${m}`); errors++; };
const warn = (m) => { console.error(`[WARN] ${m}`); warns++; };
const ok = (m) => { console.log(`[OK]   ${m}`); };

console.log(`检查: ${file}`);
console.log('');

/* 结构类检查只能看「渲染出来的那部分」。
   引擎脚本里会出现 '[data-tts-c="…"]' 这类字符串，注释里会出现「占位」二字 ——
   直接扫整份 HTML 会把脚本和注释当成正文，产生误报（朗读段数多算、
   模板自带的说明文字被判成「占位文案没替换」）。 */
const doc = html
  .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '<script></script>')
  .replace(/<style\b[^>]*>[\s\S]*?<\/style>/gi, '<style></style>');

/* ── 1. 配色契约 ────────────────────────────────────────── */
function cssBlocks() {
  return [...html.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map((m) => m[1]);
}
const css = cssBlocks().join('\n');

function token(name) {
  const m = css.match(new RegExp(`--${name}\\s*:\\s*([^;]+);`));
  return m ? m[1].trim() : null;
}
function hex(v) {
  const m = v && v.match(/^#([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (!m) return null;
  let h = m[1];
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
function lum(rgb) {
  const a = rgb.map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * a[0] + 0.7152 * a[1] + 0.0722 * a[2];
}

const paper = token('paper'), ink = token('ink'), amber = token('amber'), deep = token('deep');
if (!paper || !ink || !amber || !deep) {
  fail('缺少配色 token：需要 --paper / --ink / --amber / --deep');
} else {
  const P = hex(paper), I = hex(ink), A = hex(amber), D = hex(deep);
  if (!P || !I || !A || !D) {
    fail('配色 token 不是十六进制色值，无法校验');
  } else {
    if (lum(P) < 0.9) fail(`--paper 应为白底（当前 ${paper}）`);
    else ok('--paper 是白底');

    if (lum(I) > 0.18) fail(`--ink 应为近黑正文（当前 ${ink}）`);
    else ok('--ink 是近黑正文');

    /* 橙黄：红高、绿中、蓝低 */
    if (!(A[0] > 190 && A[1] > 110 && A[1] < 210 && A[2] < 90)) {
      fail(`--amber 应为橙黄（当前 ${amber}）`);
    } else ok('--amber 是橙黄');

    /* 深色小标题：亮度低且偏冷 */
    if (!(lum(D) < 0.22 && D[2] >= D[0])) {
      fail(`--deep 应为深色（当前 ${deep}）`);
    } else ok('--deep 是深色');
  }
}

/* ── 2. 字号两层 ────────────────────────────────────────── */
if (!/--fs-base\s*:/.test(css)) fail('缺少 --fs-base（断点基准字号）');
else if (!/--fs-scale\s*:/.test(css)) fail('缺少 --fs-scale（读者偏好倍率）');
else if (!/--fs\s*:\s*calc\(\s*var\(--fs-base\)\s*\*\s*var\(--fs-scale\)\s*\)/.test(css)) {
  fail('--fs 必须由 calc(var(--fs-base) * var(--fs-scale)) 组成，否则移动端降档会被内联样式压住');
} else ok('字号是「基准 × 倍率」两层');

/* ── 3. 响应式与打印 ────────────────────────────────────── */
const brs = [...css.matchAll(/@media\s*\(max-width:\s*(\d+)px\)/g)].map((m) => parseInt(m[1], 10));
if (!brs.includes(860)) fail('缺少 860px 断点（移动端外壳：顶栏 + 底部朗读条）');
else ok('有 860px 移动端断点');
if (!brs.includes(560)) fail('缺少 560px 断点（手机档：宽表卡片化）');
else ok('有 560px 手机档断点');
if (!brs.some((b) => b <= 400)) fail('缺少 ≤400px 断点（小屏收窄）');
else ok('有小屏收窄断点');

if (!/@media\s*print/.test(css)) fail('缺少 @media print，导出 PDF 会带上目录、朗读条这些交互层');
else {
  const printBlock = css.slice(css.indexOf('@media print'));
  if (!/\.rail[^{]*\{[^}]*display\s*:\s*none/.test(printBlock)) {
    fail('打印样式没有隐藏左侧目录 .rail');
  } else if (!/\.ttsbar[^{]*\{[^}]*display\s*:\s*none/.test(printBlock)) {
    fail('打印样式没有隐藏朗读竖条 .ttsbar');
  } else if (!/(page-break-before|break-before)/.test(printBlock)) {
    warn('打印样式没有章节分页规则（page-break-before）');
  } else ok('打印样式隐藏了交互层并做了分页');
}

/* ── 4. 朗读系统挂钩 ────────────────────────────────────── */
const scriptText = [...html.matchAll(/<script(?![^>]*src=)[^>]*>([\s\S]*?)<\/script>/gi)]
  .map((m) => m[1]).join('\n');
for (const hook of ['btnStartRead', 'ttsBar', 'ttsPanel']) {
  if (!doc.includes(hook)) fail(`缺少朗读挂钩：${hook}`);
}
if (!/var\s+AUDIO_MANIFEST\s*=/.test(scriptText)) fail('脚本里没有 AUDIO_MANIFEST 声明');
if (!doc.includes('data-tts-c') || !doc.includes('data-tts-i')) {
  fail('正文里没有 data-tts-c / data-tts-i 标记，朗读无法定位段落');
}
if (!/id="ch1"/.test(doc)) fail('缺少第一章 id="ch1"（封面「开始阅读」与章间跳转都靠它）');
if (!/id="btnStartRead"[^>]*href="#ch1"/.test(doc) && !/href="#ch1"[^>]*id="btnStartRead"/.test(doc)) {
  fail('「开始阅读」按钮的 href 必须指向 #ch1（禁用 JS 时也要能跳转）');
}
/* 朗读开关必须在播放时切换成暂停键。
   少了这行，按钮永远长一个样（永远显示播放键），
   播放中也看不出还能不能暂停——不报错，只是悄悄地废掉。 */
if (!/barToggle[^;{}]*classList\.\s*(?:toggle|add|remove)\(\s*['"]is-on/.test(scriptText)) {
  fail('朗读开关没有播放/暂停图标切换（播放中不显示暂停键）');
}
if (!errors) ok('朗读挂钩齐全');

/* ── 5. 朗读序号连续性 ──────────────────────────────────── */
const tags = [...doc.matchAll(/<[^>]*data-tts-c[^>]*>/g)].map((m) => m[0]);
if (!tags.length) {
  fail('没有任何带 data-tts-c 的元素，朗读无从定位段落');
} else {
  const byChapter = new Map();
  let missingIdx = 0;
  for (const t of tags) {
    const c = t.match(/data-tts-c="([^"]*)"/);
    const i = t.match(/data-tts-i="([^"]*)"/);
    if (!c) continue;
    if (!i) { missingIdx++; continue; }
    const arr = byChapter.get(c[1]) || [];
    arr.push(parseInt(i[1], 10));
    byChapter.set(c[1], arr);
  }
  if (missingIdx) fail(`${missingIdx} 个元素有 data-tts-c 却没有 data-tts-i，顺序无法确定`);
  let seqOk = true;
  for (const [ch, arr] of byChapter) {
    arr.sort((a, b) => a - b);
    for (let k = 0; k < arr.length; k++) {
      if (arr[k] !== k) {
        fail(`章节 ${ch} 的朗读序号不连续：期望 ${k}，实际 ${arr[k]}（会导致跳段或重复念）`);
        seqOk = false;
        break;
      }
    }
  }
  if (seqOk) {
    /* 把「哪几章会被朗读」显式说出来。目录章 id="toc" 出现在这里，
       就表示它带着朗读段、连续朗读时会被念出来——这本身不是错，但要看得见。 */
    ok(`${byChapter.size} 章会被朗读（共 ${tags.length} 段）：${[...byChapter.keys()].join('、')}`);
  }
}

/* ── 6. 目录与章节一致 ──────────────────────────────────── */
const chapterIds = [...doc.matchAll(/<section[^>]*class="[^"]*chapter[^"]*"[^>]*id="([^"]+)"/g)].map((m) => m[1]);
const navIds = [...doc.matchAll(/<a[^>]*data-ch="([^"]+)"/g)].map((m) => m[1]);
for (const id of chapterIds) {
  if (!navIds.includes(id)) fail(`章节 ${id} 没有出现在左侧目录里（data-ch）`);
}
const tocCount = (doc.match(/<section[^>]*class="[^"]*chapter[^"]*"[^>]*id="toc"/g) || []).length;
if (tocCount !== 1) warn('没有找到唯一的目录章 id="toc"');
if (chapterIds.length !== navIds.length) {
  warn(`章节数（${chapterIds.length}）与目录条目数（${navIds.length}）不一致`);
} else ok(`${chapterIds.length} 个章节与目录条目一一对应`);

/* ── 7. 表格降级：每个 td 要有 data-l ───────────────────── */
const tableBlocks = [...doc.matchAll(/<div class="tablewrap">([\s\S]*?)<\/div>/g)].map((m) => m[1]);
let tdTotal = 0, tdMissing = 0;
for (const blk of tableBlocks) {
  for (const td of blk.matchAll(/<td([^>]*)>/g)) {
    tdTotal++;
    if (!/data-l\s*=/.test(td[1])) tdMissing++;
  }
}
if (!tableBlocks.length) {
  warn('页面里没有 .tablewrap 表格；如果内容有表格，确认是否需要补一张');
} else if (tdMissing) {
  fail(`${tdMissing}/${tdTotal} 个 <td> 缺 data-l，手机档宽表摊成卡片后看不到列名`);
} else ok(`${tableBlocks.length} 张表格的 td 全部带 data-l`);

/* ── 8. SVG 图表 ────────────────────────────────────────── */
const svgs = [...doc.matchAll(/<svg[^>]*class="[^"]*svgfig__svg[^"]*"[^>]*>/g)].map((m) => m[0]);
if (!svgs.length) {
  warn('页面里没有内联 SVG 图表（figure--svg）');
} else {
  let bad = 0;
  for (const s of svgs) {
    if (!/role="img"/.test(s) || !/aria-label="[^"]+"/.test(s)) bad++;
  }
  if (bad) fail(`${bad}/${svgs.length} 张 SVG 缺 role="img" 或 aria-label（读屏软件会念不出来）`);
  else ok(`${svgs.length} 张 SVG 都有 role="img" 与 aria-label`);
}

/* ── 9. id 唯一性 ───────────────────────────────────────── */
const ids = [...doc.matchAll(/\sid="([^"]+)"/g)].map((m) => m[1]);
const dupes = [...new Set(ids.filter((v, i) => ids.indexOf(v) !== i))];
if (dupes.length) fail(`id 重复：${dupes.join(', ')}（SVG 内样式按 id 选择，重复会串样式）`);
else ok(`${ids.length} 个 id 无重复`);

/* ── 10. 外链依赖 ───────────────────────────────────────── */
const externals = [];
for (const m of doc.matchAll(/(?:src|href)="(https?:\/\/[^"]+)"/g)) {
  if (!/w3\.org\/2000\/svg/.test(m[1])) externals.push(m[1]);
}
if (/@import\s+url\(\s*['"]?https?:/.test(css)) externals.push('@import 远程样式表');
if (externals.length) {
  fail(`存在外链依赖（会破坏离线与单文件交付）：${[...new Set(externals)].slice(0, 5).join(', ')}`);
} else ok('无外链依赖');

/* ── 11. 音频文件是否真的存在 ───────────────────────────── */

/* 极简 JS 对象字面量解析器：对象 / 数组 / 字符串 / 数字 / 布尔 / null / 无引号键。
   引擎在运行时把清单当 JS 对象字面量直接用，所以键加不加引号都能跑，
   这里就不能用 JSON.parse 一刀切。刻意不用 eval —— 校验脚本不执行页面里的代码。 */
function parseLiteral(text) {
  let p = 0;
  const ws = () => { while (p < text.length && /\s/.test(text[p])) p++; };
  function parseString() {
    const q = text[p++];
    let out = '';
    while (p < text.length) {
      const c = text[p++];
      if (c === '\\') { out += text[p++]; continue; }
      if (c === q) return out;
      out += c;
    }
    throw new Error('字符串没有闭合');
  }
  function parseKey() {
    ws();
    if (text[p] === '"' || text[p] === "'") return parseString();
    const id = /[A-Za-z_$][A-Za-z0-9_$]*/.exec(text.slice(p));
    if (!id) throw new Error(`键名不合法 @${p}`);
    p += id[0].length;
    return id[0];
  }
  function parseValue() {
    ws();
    const ch = text[p];
    if (ch === '{') return parseObject();
    if (ch === '[') return parseArray();
    if (ch === '"' || ch === "'") return parseString();
    if (text.startsWith('true', p)) { p += 4; return true; }
    if (text.startsWith('false', p)) { p += 5; return false; }
    if (text.startsWith('null', p)) { p += 4; return null; }
    const num = /^-?\d+(\.\d+)?([eE][+-]?\d+)?/.exec(text.slice(p));
    if (num) { p += num[0].length; return Number(num[0]); }
    throw new Error(`意外的字符 ${JSON.stringify(ch)} @${p}`);
  }
  function parseObject() {
    p++; const obj = {};
    ws();
    if (text[p] === '}') { p++; return obj; }
    for (;;) {
      const key = parseKey();
      ws();
      if (text[p] !== ':') throw new Error(`键 ${key} 后缺冒号`);
      p++;
      obj[key] = parseValue();
      ws();
      if (text[p] === ',') {
        p++; ws();
        if (text[p] === '}') { p++; return obj; }
        continue;
      }
      if (text[p] === '}') { p++; return obj; }
      throw new Error('对象里缺 , 或 }');
    }
  }
  function parseArray() {
    p++; const arr = [];
    ws();
    if (text[p] === ']') { p++; return arr; }
    for (;;) {
      arr.push(parseValue());
      ws();
      if (text[p] === ',') {
        p++; ws();
        if (text[p] === ']') { p++; return arr; }
        continue;
      }
      if (text[p] === ']') { p++; return arr; }
      throw new Error('数组里缺 , 或 ]');
    }
  }
  return parseValue();
}

/* 找出对象字面量的结束位置。跳过字符串与注释 —— 否则正文里的 { } 会把深度算错。 */
function findLiteralEnd(src, start) {
  let depth = 0;
  for (let k = start; k < src.length; k++) {
    const ch = src[k];
    if (ch === '"' || ch === "'" || ch === '`') {
      const q = ch; k++;
      while (k < src.length) {
        if (src[k] === '\\') { k += 2; continue; }
        if (src[k] === q) break;
        k++;
      }
      continue;
    }
    if (ch === '/' && src[k + 1] === '/') { while (k < src.length && src[k] !== '\n') k++; continue; }
    if (ch === '/' && src[k + 1] === '*') {
      k += 2;
      while (k < src.length && !(src[k] === '*' && src[k + 1] === '/')) k++;
      k++; continue;
    }
    if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) return k + 1; }
  }
  return -1;
}

function extractManifest(src) {
  const m = src.match(/var\s+AUDIO_MANIFEST\s*=/);
  if (!m) return { found: false, value: null };
  let i = m.index + m[0].length;
  while (i < src.length && /\s/.test(src[i])) i++;
  if (src.startsWith('null', i)) return { found: true, value: null };
  if (src[i] !== '{') return { found: true, value: null, opaque: true };
  const end = findLiteralEnd(src, i);
  if (end < 0) return { found: true, value: null, broken: true };
  const literal = src.slice(i, end);
  try { return { found: true, value: parseLiteral(literal) }; }
  catch (e) {
    try { return { found: true, value: JSON.parse(literal) }; }
    catch { return { found: true, value: null, broken: true, why: e.message }; }
  }
}
const mf = extractManifest(scriptText);
if (mf.broken) {
  fail(`AUDIO_MANIFEST 解析失败，引擎会拿到 undefined${mf.why ? `（${mf.why}）` : ''}`);
} else if (mf.opaque) {
  warn('AUDIO_MANIFEST 不是对象字面量，无法校验音频文件是否存在');
} else if (!mf.value) {
  ok('未配置音频清单，走浏览器语音合成');
} else {
  const paths = [];
  for (const b of mf.value.blocks || []) {
    for (const p of Object.values(b.audio || {})) paths.push(p);
  }
  if (!paths.length) {
    warn('AUDIO_MANIFEST 里没有任何音频路径，朗读会一直走合成分支');
  } else {
    const missing = paths.filter((p) => !existsSync(join(dir, p)));
    if (missing.length) {
      fail(`${missing.length}/${paths.length} 个音频文件不存在（这些段落会没声音）：${missing.slice(0, 3).join(', ')}`);
    } else ok(`${paths.length} 个音频文件全部存在`);
  }
  const vo = (mf.value.voices || []).map((v) => v.id).filter(Boolean);
  if (!vo.length) fail('AUDIO_MANIFEST.voices 为空，音色切换与默认音色都取不到');
  else {
    const names = (mf.value.voices || []).map((v) => v.name);
    if (!names.includes('电台男主播')) {
      warn('音频清单里没有「电台男主播」，引擎会退回清单里的第一个音色');
    } else {
      ok('默认音色「电台男主播」在清单里');
    }
  }

  /* 清单要覆盖所有朗读段落。
     段落加了却没重新生成音频，是最安静的一种错配——页面上看不出来，
     只有读者点播放时才发现某段没声音，或者念的是上一段的内容。 */
  const manifestKeys = new Set(
    (mf.value.blocks || []).map((b) => `${b.chapter}#${b.i}`)
  );
  const htmlKeys = new Set();
  for (const t of tags) {
    const c = t.match(/data-tts-c="([^"]*)"/);
    const i = t.match(/data-tts-i="([^"]*)"/);
    if (c && i) htmlKeys.add(`${c[1]}#${i[1]}`);
  }
  const uncovered = [...htmlKeys].filter((k) => !manifestKeys.has(k));
  const orphan = [...manifestKeys].filter((k) => !htmlKeys.has(k));
  if (uncovered.length) {
    fail(`${uncovered.length} 个朗读段落在清单里没有对应音频：${uncovered.slice(0, 5).join('、')}（重跑 make-audio.mjs）`);
  } else if (orphan.length) {
    warn(`清单里有 ${orphan.length} 条音频在页面上找不到对应段落：${orphan.slice(0, 5).join('、')}（多半是段落删了但音频还在）`);
  } else {
    ok(`清单覆盖全部 ${htmlKeys.size} 个朗读段落`);
  }
}

/* ── 12. 页面元信息 ─────────────────────────────────────── */
const title = doc.match(/<title>([\s\S]*?)<\/title>/);
if (!title || !title[1].trim()) fail('缺少 <title>');
else if (/书名占位|占位/.test(title[1])) warn('<title> 还是占位文案，交付前替换');
const desc = doc.match(/<meta[^>]*name="description"[^>]*content="([^"]*)"/i);
if (!desc || !desc[1].trim()) warn('缺少 meta description');
if (!/<html[^>]*lang="zh/i.test(doc)) warn('<html> 缺 lang="zh-CN"，读屏软件会用错发音规则');

/* ── 13. 封面只做文字卡片（不要封面图）───────────────────────
   封面模板是纯文字卡片：书名 + 关键数字 + 两个入口。
   一旦在里面放 <img> 或外链图，就同时破坏两个前提——
   单文件自包含（离线可读、不下载外部文件）与打印不失真。
   这一条只查封面区，不查正文：正文里的 .slot 占位与内联 SVG 都是允许的。 */
const coverBlk = doc.match(/<section[^>]*class="[^"]*cover[^"]*"[^>]*>([\s\S]*?)<\/section>/i);
if (coverBlk) {
  const imgs = [...coverBlk[1].matchAll(/<img\b[^>]*>/gi)].map((m) => m[0]);
  const bgImg = [...coverBlk[1].matchAll(/url\(\s*['"]?[^)]+\.(?:jpe?g|png|webp|gif|avif)/gi)].map((m) => m[0]);
  if (imgs.length || bgImg.length) {
    fail(`封面区有图片（${imgs.length} 个 <img>、${bgImg.length} 处背景图）——封面只做文字卡片，改用文字版式`);
  } else {
    ok('封面是文字卡片，没有图片');
  }
} else {
  warn('页面里没有封面区 section.cover（不是每份文档都需要封面，确认是否有意去掉）');
}

/* ── 14. 残留占位文案 ───────────────────────────────────── */
const placeholders = ['书名占位', '副标题占位', '作者姓名', '章节标题', '待替换', '占位'];
const left = placeholders.filter((p) => doc.includes(p));
if (left.length) warn(`仍有模板占位文案未替换：${left.join('、')}`);
/* 「待定」是允许的占位（SKILL.md：没有作者就写「待定」并在交付时说明），
   但它会原样留在成品里，所以单独提醒一句，区别于「必须改掉的占位」。 */
if (doc.includes('待定')) {
  warn('文里还有「待定」（通常是作者、版本等未确认字段）：交付前补齐，或在交付说明里写明哪几处待定');
}
console.log('');
if (errors) {
  console.error(`✗ ${errors} 个错误，${warns} 个警告`);
  process.exit(1);
}
console.log(`✓ 无错误${warns ? `（${warns} 个警告）` : ''}`);
process.exit(0);
