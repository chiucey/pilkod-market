#!/usr/bin/env node
/**
 * build.mjs — content.json → index.html
 *
 * 读 references/template.html，注入 meta / nav / chapters / style-kit，产出：
 *   <work>/index.html    单文件电子版（CSS/JS 内联）
 *   <work>/content.md    同内容的纯文字稿，便于逐字校对
 *
 * 用法：
 *   node build.mjs <content.json> [--work <输出目录>] [--no-md]
 *
 * 内容错误尽量不中断：未知 block 类型、缺图只告警，最后统一打印。
 * 硬错误（模板缺失、JSON 解析失败）直接退出非 0。
 */
import { readFileSync, writeFileSync, existsSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REFS = join(HERE, '..', 'references');
const TEMPLATE_FILE = join(REFS, 'template.html');
const STYLEKIT_FILE = join(REFS, 'style-kit.html');

const warnings = [];
const warn = (m) => { warnings.push(m); console.error('[WARN] ' + m); };

const esc = (v) => String(v ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/** 取字段：默认转义；同名 +Html 后缀表示原样插入（允许行内标签） */
function f(obj, name, fallback = '') {
  if (!obj || typeof obj !== 'object') return fallback;
  if (obj[name] != null) return esc(obj[name]);
  if (obj[name + 'Html'] != null) return String(obj[name + 'Html']);
  return fallback;
}

/** block 文本：块上写了 html:true 就原样插入，否则走 f() */
function bt(b, name) {
  if (b && b.html === true) return String(b[name] ?? b[name + 'Html'] ?? '');
  return f(b, name);
}

/* ── block 渲染 ──────────────────────────────────── */

function renderBlock(b, ctx) {
  switch (b.type) {
    case 'h3':
      return `        <h3 class="h h--3">${bt(b, 'text')}</h3>`;

    case 'h4':
      return `        <h4 class="h h--4">${bt(b, 'text')}</h4>`;

    case 'pull': {
      const cite = f(b, 'cite');
      return `        <blockquote class="pull">\n          ${bt(b, 'text')}\n${cite ? `          <cite>${cite}</cite>\n` : ''}        </blockquote>`;
    }

    case 'cards': {
      const items = (b.items || []).map((it, i) => `          <div class="card">
            <div class="card__n">${esc(it.n ?? it.label ?? String(i + 1).padStart(2, '0'))}</div>
            <p class="card__t">${f(it, 't')}</p>
            <p class="card__d">${f(it, 'd')}</p>
          </div>`).join('\n');
      return `        <div class="cards">\n${items}\n        </div>`;
    }

    case 'list': {
      const variant = b.variant || 'ordered';
      const cls = variant === 'dot' ? 'list list--dot' : variant === 'check' ? 'list list--check' : 'list';
      const tag = variant === 'ordered' ? 'ol' : 'ul';
      const items = (b.items || []).map((it) => {
        const text = (it && typeof it === 'object') ? bt(it, 'text') : esc(it);
        return `          <li>${text}</li>`;
      }).join('\n');
      return `        <${tag} class="${cls}">\n${items}\n        </${tag}>`;
    }

    case 'callout': {
      const tone = b.tone === 'note' ? ' callout--note' : '';
      return `        <div class="callout${tone}">\n          <b>${f(b, 'label')}</b>\n          <p>${bt(b, 'text')}</p>\n        </div>`;
    }

    case 'figure': {
      const src = b.src || '';
      if (!src) { warn('figure 缺 src'); return ''; }
      if (!existsSync(join(ctx.work, src))) warn(`figure 图片不存在：${src}`);
      const alt = b.alt ? esc(b.alt) : '';
      if (!alt) warn(`figure 缺 alt：${src}`);
      const cap = f(b, 'caption');
      return `        <figure class="figure">
          <img src="${esc(src)}" alt="${alt}" loading="lazy" decoding="async">
${cap ? `          <figcaption>${cap}</figcaption>\n` : ''}        </figure>`;
    }

    case 'slot':
      return `        <figure class="figure">
          <div class="slot"><b>${f(b, 'label', '图位')}</b>${f(b, 'hint')}</div>
        </figure>`;

    case 'bars': {
      const rows = (b.items || []).map((it) => {
        const v = Math.max(0, Math.min(100, Number(it.value) || 0));
        return `          <div class="bar__row"><span class="bar__label">${f(it, 'label')}</span><span class="bar__track"><span class="bar__fill" style="--w:${v}"></span></span><span class="bar__val">${esc(it.display ?? it.value ?? '')}</span></div>`;
      }).join('\n');
      return `        <div class="bars">\n${rows}\n        </div>`;
    }

    case 'timeline': {
      const items = (b.items || []).map((it) =>
        `          <li><time>${esc(it.time || '')}</time><b>${esc(it.title || '')}</b>${it.text ? `<br>${esc(it.text)}` : ''}</li>`
      ).join('\n');
      return `        <ol class="timeline">\n${items}\n        </ol>`;
    }

    case 'table': {
      const head = (b.head || []).map((h) => `<th>${esc(h)}</th>`).join('');
      const rows = (b.rows || []).map((r) =>
        `            <tr>${(r || []).map((c) => `<td>${esc(c)}</td>`).join('')}</tr>`
      ).join('\n');
      return `        <div class="tablewrap">
          <table>
            <thead><tr>${head}</tr></thead>
            <tbody>
${rows}
            </tbody>
          </table>
        </div>`;
    }

    case 'tags': {
      const items = (b.items || []).map((it) => {
        const obj = (it && typeof it === 'object') ? it : { t: it };
        return `        <span class="tag${obj.accent ? ' tag--amber' : ''}">${esc(obj.t)}</span>`;
      }).join('\n');
      return `        <div class="tags">\n${items}\n        </div>`;
    }

    case 'divider':
      return `        <div class="divider">◆ ◆ ◆</div>`;

    default: {
      warn(`未知 block type "${b.type}"，已按正文渲染；请回 content.json 改成受支持的 type`);
      return bt(b, 'text') ? `        <p class="prose">${bt(b, 'text')}</p>` : '';
    }
  }
}

function renderBlocks(blocks, ctx) {
  const out = [];
  let proseBuf = [];
  const flush = () => { if (proseBuf.length) { out.push(proseBuf.join('\n')); proseBuf = []; } };

  for (const b of blocks || []) {
    if (!b || typeof b !== 'object') { warn('blocks 里有非对象项，已跳过'); continue; }
    if (b.type === 'prose') {
      proseBuf.push(`        <p class="prose${b.noIndent ? ' no-indent' : ''}">${bt(b, 'text')}</p>`);
      continue;
    }
    flush();
    const html = renderBlock(b, ctx);
    if (html) out.push(html);
  }
  flush();
  return out.join('\n');
}

/* ── 章节 / 导航 / 封面 ───────────────────────────── */

function renderChapter(ch, i, ctx) {
  const id = ch.id || ('ch' + (i + 1));
  const no = ch.no || ('Chapter ' + String(i + 1).padStart(2, '0'));
  const lead = f(ch, 'lead');
  if (!ch.title) warn(`第 ${i + 1} 章缺 title`);
  return `  <section class="chapter" id="${esc(id)}">
    <header class="chapter__head">
      <span class="chapter__no">${esc(no)}</span>
      <h2 class="chapter__title">${esc(ch.title || '（未命名章节）')}</h2>
${lead ? `      <p class="chapter__lead">${lead}</p>\n` : ''}    </header>

${renderBlocks(ch.blocks, ctx)}
  </section>`;
}

function renderNav(chapters, labels, styleKit) {
  const items = [`    <a href="#cover"><small>Cover</small>${esc(labels.cover)}</a>`];
  chapters.forEach((ch, i) => {
    const id = ch.id || ('ch' + (i + 1));
    const no = ch.no || ('Chapter ' + String(i + 1).padStart(2, '0'));
    items.push(`    <a href="#${esc(id)}"><small>${esc(no)}</small>${esc(ch.title || '（未命名章节）')}</a>`);
  });
  if (styleKit) items.push(`    <a href="#sandbox"><small>Library</small>${esc(labels.styleKit)}</a>`);
  return items.join('\n');
}

function renderFacts(facts) {
  return (facts || []).slice(0, 5).map((x) => {
    const k = Array.isArray(x) ? x[0] : x.k;
    const v = Array.isArray(x) ? x[1] : x.v;
    return `          <li><span>${esc(k)}</span><span>${esc(v)}</span></li>`;
  }).join('\n');
}

function renderCover(meta, ctx) {
  const src = meta.cover;
  if (!src) {
    warn('meta.cover 为空，封面区输出占位框');
    return `      <figure class="cover__frame cover__ph">
        <span class="cover__phlabel">Cover Placeholder</span>
        <b class="cover__phmark">${esc(meta.title || '书名待定')}</b>
        <span class="cover__phhint">待替换 · assets/cover.jpg</span>
      </figure>`;
  }
  if (!existsSync(join(ctx.work, src))) warn(`封面图不存在：${src}`);
  const alt = meta.coverAlt ? esc(meta.coverAlt) : '';
  if (!alt) warn('meta.coverAlt 为空');
  return `      <figure class="cover__frame">
        <img src="${esc(src)}" alt="${alt}">
      </figure>${meta.coverCaption ? `\n      <div class="cover__caption">${esc(meta.coverCaption)}</div>` : ''}`;
}

/* ── 纯文字稿 ────────────────────────────────────── */

function plainBlock(b) {
  if (!b || typeof b !== 'object') return [];
  switch (b.type) {
    case 'prose': return ['', String(b.text ?? '')];
    case 'h3': return ['', `### ${b.text ?? ''}`];
    case 'h4': return ['', `#### ${b.text ?? ''}`];
    case 'pull': {
      const cite = String(b.cite ?? '');
      const tail = cite ? (cite.startsWith('——') ? `　${cite}` : `　—— ${cite}`) : '';
      return ['', `> ${b.text ?? ''}${tail}`];
    }
    case 'cards': return ['', ...(b.items || []).map((it) => `- **${it.t ?? ''}**：${it.d ?? ''}`)];
    case 'list': return ['', ...(b.items || []).map((it) => `- ${typeof it === 'object' ? (it.text ?? '') : it}`)];
    case 'callout': return ['', `【${b.label ?? '注'}】${b.text ?? ''}`];
    case 'figure': return ['', `[图] ${b.caption || b.alt || b.src || ''}`];
    case 'slot': return ['', `[图位] ${b.label || ''} ${b.hint || ''}`];
    case 'bars': return ['', ...(b.items || []).map((it) => `- ${it.label ?? ''}：${it.display ?? it.value ?? ''}`)];
    case 'timeline': return ['', ...(b.items || []).map((it) => `- ${it.time ?? ''} ${it.title ?? ''}　${it.text ?? ''}`)];
    case 'table': return ['', ...(b.rows || []).map((r) => `| ${(r || []).join(' | ')} |`)];
    case 'tags': return ['', (b.items || []).map((it) => (typeof it === 'object' ? it.t : it)).join(' / ')];
    case 'divider': return ['', '---'];
    default: return b.text ? ['', String(b.text)] : [];
  }
}

function renderPlain(content, meta) {
  const L = [`# ${meta.title || '书名'}`];
  if (meta.subtitle) L.push('', meta.subtitle);
  if (meta.author) L.push('', `著　${meta.author}`);
  if (meta.intro) L.push('', String(meta.intro));
  for (const ch of content.chapters || []) {
    const no = ch.no ? ch.no + ' · ' : '';
    L.push('', `## ${no}${ch.title || '（未命名章节）'}`);
    if (ch.lead) L.push('', String(ch.lead));
    for (const b of ch.blocks || []) L.push(...plainBlock(b));
  }
  return L.join('\n') + '\n';
}

/* ── 主流程 ──────────────────────────────────────── */

function main() {
  const argv = process.argv.slice(2);
  const input = argv.find((a) => !a.startsWith('--'));
  if (!input) {
    console.error('用法: node build.mjs <content.json> [--work <输出目录>] [--no-md]');
    process.exit(2);
  }
  const workFlag = argv.includes('--work') ? argv[argv.indexOf('--work') + 1] : null;
  const withMd = !argv.includes('--no-md');

  if (!existsSync(TEMPLATE_FILE)) {
    console.error(`找不到模板：${TEMPLATE_FILE}`);
    process.exit(1);
  }

  const contentPath = resolve(input);
  if (!existsSync(contentPath)) {
    console.error(`找不到 content.json：${contentPath}`);
    process.exit(1);
  }

  let content;
  try {
    content = JSON.parse(readFileSync(contentPath, 'utf-8'));
  } catch (e) {
    console.error(`content.json 解析失败：${e.message}`);
    process.exit(1);
  }

  const meta = content.meta || {};
  const chapters = Array.isArray(content.chapters) ? content.chapters : [];
  const styleKit = meta.styleKit === true;
  const work = resolve(workFlag || dirname(contentPath));
  const ctx = { work };

  const DEFAULT_LABELS = {
    cover: '封面', styleKit: '组件样式库', toggle: '目录', progress: '阅读进度',
    footer: '© 电子可视化版', print: '打印', printTitle: '打印 / 导出 PDF',
    fsDown: '缩小字号', fsUp: '放大字号', fsKey: 'ebook.fs'
  };
  const labels = { ...DEFAULT_LABELS, ...(meta.labels || {}) };

  const intro = meta.intro ? f(meta, 'intro') : '';
  let styleKitHtml = '';
  if (styleKit) {
    if (existsSync(STYLEKIT_FILE)) styleKitHtml = readFileSync(STYLEKIT_FILE, 'utf-8');
    else warn('styleKit=true 但找不到 style-kit.html');
  }

  const chaptersHtml = chapters.map((ch, i) => renderChapter(ch, i, ctx)).join('\n\n');
  const colophon = (content.colophon || [])
    .map((s) => `    <span>${esc(s)}</span>`).join('\n');

  const map = {
    LANG: esc(meta.lang || 'zh-CN'),
    HEAD_TITLE: esc(meta.title ? `${meta.title}${meta.subtitle ? ' · ' + meta.subtitle : ''}` : '电子版'),
    META_DESCRIPTION: esc(meta.description || meta.intro || meta.title || ''),
    KICKER: esc(meta.kicker || 'Electronic Edition'),
    TITLE: esc(meta.title || '书名待定'),
    SUBTITLE: esc(meta.subtitle || ''),
    BYLINE: meta.byline ? esc(meta.byline) : (meta.author ? `著 <b>${esc(meta.author)}</b>` : ''),
    FACTS: renderFacts(meta.facts),
    INTRO: intro,
    COVER_BLOCK: renderCover(meta, ctx),
    NAV: renderNav(chapters, labels, styleKit),
    CHAPTERS: chaptersHtml,
    STYLEKIT: styleKitHtml,
    COLOPHON: colophon,
    NAV_TOGGLE_LABEL: esc(labels.toggle),
    PROGRESS_LABEL: esc(labels.progress),
    FOOTER: esc(labels.footer),
    PRINT_LABEL: esc(labels.print),
    PRINT_TITLE: esc(labels.printTitle),
    FS_DOWN_TITLE: esc(labels.fsDown),
    FS_UP_TITLE: esc(labels.fsUp),
    FS_KEY: esc(labels.fsKey)
  };

  let html = readFileSync(TEMPLATE_FILE, 'utf-8');
  const missing = [];
  html = html.replace(/\{\{([A-Z0-9_]+)\}\}/g, (m, k) => {
    if (k in map) return map[k];
    missing.push(k);
    return m;
  });
  missing.forEach((k) => warn(`模板占位符 {{${k}}} 没有对应内容`));

  const outHtml = join(work, 'index.html');
  writeFileSync(outHtml, html, 'utf-8');

  let outMd = null;
  if (withMd) {
    outMd = join(work, 'content.md');
    writeFileSync(outMd, renderPlain(content, meta), 'utf-8');
  }

  const kb = (p) => (existsSync(p) ? (statSync(p).size / 1024).toFixed(1) + ' KB' : '—');
  const blocks = chapters.reduce((n, ch) => n + ((ch.blocks || []).length), 0);

  console.log('');
  console.log('生成完成');
  console.log(`  ${outHtml}  (${kb(outHtml)})`);
  if (outMd) console.log(`  ${outMd}  (${kb(outMd)})`);
  console.log(`  章节 ${chapters.length} · 内容块 ${blocks}`);
  if (warnings.length) console.log(`  警告 ${warnings.length} 条（见上）`);
  console.log('');
}

main();
