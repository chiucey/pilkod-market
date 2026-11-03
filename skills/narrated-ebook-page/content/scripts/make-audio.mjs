#!/usr/bin/env node
/**
 * make-audio.mjs —— 把页面里带 data-tts-* 的段落合成成 mp3，并写回 AUDIO_MANIFEST
 *
 * 用法：
 *   node scripts/make-audio.mjs <index.html> [选项]
 *
 * 选项：
 *   --voice-id "<id>"      音色 id，默认 Chinese (Mandarin)_Radio_Host（电台男主播）
 *   --voice-name "<名>"    音色显示名，默认 电台男主播
 *   --speed <0.5–2>        语速，默认 0.95
 *   --emotion <名字>       情感，默认 neutral
 *   --out <目录>           mp3 输出目录，默认 <html 所在目录>/assets/audio
 *   --dry-run              只抽取朗读文本并打印，不合成、不改文件
 *   --force                已存在的音频也重新生成
 *
 * 依赖：mcode-tools CLI（在 PATH 上），以及已连接的 matrix TTS。
 * 一次最多合成 10 段，脚本自动分批；上游限流（429）会自动退避重试并缩批。
 *
 * 文件命名：<章id>_<章内序号>.mp3，例如 ch1_000.mp3。
 * 用「章 + 序号」而不是全局流水号，是为了让「插入一段」不会让后面的音频集体错位。
 * 复用旧音频的依据是**文本比对**：HTML 里这段文字没变，就不重新合成。
 */

import { execFileSync } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, existsSync, statSync, renameSync } from 'node:fs';
import { dirname, join, resolve, relative } from 'node:path';

/* ── 参数 ───────────────────────────────────────────────── */
const argv = process.argv.slice(2);
const opts = {
  file: null, voiceId: 'Chinese (Mandarin)_Radio_Host', voiceName: '电台男主播',
  speed: 0.95, emotion: 'neutral', out: null, dryRun: false, force: false,
};
for (let k = 0; k < argv.length; k++) {
  const a = argv[k];
  if (a === '--voice-id') opts.voiceId = argv[++k];
  else if (a === '--voice-name') opts.voiceName = argv[++k];
  else if (a === '--speed') opts.speed = parseFloat(argv[++k]);
  else if (a === '--emotion') opts.emotion = argv[++k];
  else if (a === '--out') opts.out = argv[++k];
  else if (a === '--dry-run') opts.dryRun = true;
  else if (a === '--force') opts.force = true;
  else if (!a.startsWith('--') && !opts.file) opts.file = a;
}
if (!opts.file) {
  console.error('用法：node scripts/make-audio.mjs <index.html> [选项]');
  process.exit(2);
}
const htmlPath = resolve(opts.file);
if (!existsSync(htmlPath)) {
  console.error(`找不到文件：${htmlPath}`);
  process.exit(2);
}
const htmlDir = dirname(htmlPath);

/* ── HTML 里的对象字面量定位（字符串与注释要跳过） ────────── */
function findLiteralEnd(src, start) {
  let depth = 0;
  for (let k = start; k < src.length; k++) {
    const ch = src[k];
    if (ch === '"' || ch === "'" || ch === '`') {
      const q = ch; k++;
      while (k < src.length) { if (src[k] === '\\') { k += 2; continue; } if (src[k] === q) break; k++; }
      continue;
    }
    if (ch === '/' && src[k + 1] === '/') { while (k < src.length && src[k] !== '\n') k++; continue; }
    if (ch === '/' && src[k + 1] === '*') { k += 2; while (k < src.length && !(src[k] === '*' && src[k + 1] === '/')) k++; k++; continue; }
    if (ch === '{') depth++;
    else if (ch === '}') { depth--; if (depth === 0) return k + 1; }
  }
  return -1;
}

/* 找出 var AUDIO_MANIFEST = ... 的值区间 */
function manifestRange(src) {
  const decl = /var\s+AUDIO_MANIFEST\s*=\s*/.exec(src);
  if (!decl) return null;
  let vStart = decl.index + decl[0].length;
  while (vStart < src.length && /\s/.test(src[vStart])) vStart++;
  let vEnd;
  if (src.startsWith('null', vStart)) vEnd = vStart + 4;
  else if (src[vStart] === '{') { vEnd = findLiteralEnd(src, vStart); if (vEnd < 0) return null; }
  else vEnd = vStart;
  return { start: vStart, end: vEnd, text: src.slice(vStart, vEnd) };
}

/* 宽松解析清单（键可以不加引号），失败返回 null */
function parseManifestLiteral(text) {
  if (!text || text.trim() === 'null') return null;
  try { return JSON.parse(text); } catch { /* 继续尝试宽松解析 */ }
  try {
    /* eslint-disable no-new-func */
    return new Function(`return (${text});`)();
  } catch { return null; }
}

/* ── 1. 抽出要朗读的段落 ─────────────────────────────────── */
const html = readFileSync(htmlPath, 'utf8');

function attr(attrs, name) {
  const m = attrs.match(new RegExp(`\\b${name}\\s*=\\s*"([^"]*)"`));
  return m ? m[1] : null;
}

function extractInner(src, tag, start) {
  const scan = /<(\/?)([a-zA-Z][a-zA-Z0-9]*)\b[^>]*?(\/?)>/g;
  scan.lastIndex = start;
  let depth = 1, s;
  const want = tag.toLowerCase();
  while ((s = scan.exec(src))) {
    if (s[3] === '/') continue;
    if (s[2].toLowerCase() !== want) continue;
    if (s[1] === '/') { depth--; if (depth === 0) return { html: src.slice(start, s.index), end: s.index + s[0].length }; }
    else depth++;
  }
  return { html: src.slice(start), end: src.length };
}

function toText(inner) {
  return inner
    .replace(/<br\s*\/?>/gi, ' ')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ').replace(/&amp;/g, '&').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;|&apos;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function kindOf(tag, cls) {
  const t = tag.toLowerCase();
  if (/^h[1-6]$/.test(t)) return t;
  if (/\bprose\b/.test(cls)) return 'prose';
  if (t === 'li') return 'list';
  if (/\bcard/.test(cls)) return 'card';
  if (/\bpull\b/.test(cls)) return 'pull';
  if (/\bcallout\b/.test(cls)) return 'callout';
  if (/\btimeline\b/.test(cls)) return 'timeline';
  if (/\bbars\b/.test(cls)) return 'bars';
  if (/\btablewrap\b/.test(cls)) return 'table';
  return t;
}

const blocks = [];
const tagRe = /<([a-zA-Z][a-zA-Z0-9]*)\b([^>]*?)>/g;
let tm;
while ((tm = tagRe.exec(html))) {
  const tag = tm[1];
  const attrs = tm[2];
  if (!/\bdata-tts-c\s*=/.test(attrs)) continue;
  const c = attr(attrs, 'data-tts-c');
  const i = attr(attrs, 'data-tts-i');
  if (c === null || i === null) continue;
  const cls = attr(attrs, 'class') || '';
  const ttsText = attr(attrs, 'data-tts-text');
  const got = extractInner(html, tag, tagRe.lastIndex);
  const text = (ttsText !== null ? ttsText : toText(got.html)).trim();
  blocks.push({
    chapter: c, i: parseInt(i, 10), kind: kindOf(tag, cls), text,
    elEnd: got.end,
  });
  tagRe.lastIndex = got.end;
}

if (!blocks.length) {
  console.error('这个文件里没有带 data-tts-c / data-tts-i 的段落，先按 authoring.md 加标记。');
  process.exit(1);
}

/* 按「章首次出现的顺序 + 章内序号」排序，并编全局号 */
const chapOrder = [];
for (const b of blocks) if (!chapOrder.includes(b.chapter)) chapOrder.push(b.chapter);
blocks.sort((a, b) => (chapOrder.indexOf(a.chapter) - chapOrder.indexOf(b.chapter)) || (a.i - b.i));
blocks.forEach((b, n) => { b.n = n; });

const seen = new Set();
for (const b of blocks) {
  const key = `${b.chapter}#${b.i}`;
  if (seen.has(key)) { console.error(`朗读序号重复：${key}`); process.exit(1); }
  seen.add(key);
}

if (opts.dryRun) {
  console.log(`\n共 ${blocks.length} 段待朗读（音色：${opts.voiceName}）\n`);
  for (const b of blocks) {
    console.log(`[${String(b.n).padStart(3, '0')}] ${b.chapter}#${b.i}  ${b.kind}  ${b.text.length} 字`);
    console.log(`      ${b.text}`);
  }
  console.log(`\n总字数 ${blocks.reduce((s, b) => s + b.text.length, 0)}`);
  process.exit(0);
}

/* ── 2. 输出路径与旧清单 ─────────────────────────────────── */
const outDir = opts.out ? resolve(opts.out) : join(htmlDir, 'assets', 'audio');
const voiceDir = opts.voiceId.replace(/[^A-Za-z0-9_]+/g, '_');
/* "Chinese (Mandarin)_Radio_Host" → "Chinese_Mandarin__Radio_Host"
   规则：非字母数字、非下划线的连续片段折叠成一个下划线；已有的下划线原样保留。
   与已上线项目的目录名保持一致。 */
const voicePath = join(outDir, voiceDir);
mkdirSync(voicePath, { recursive: true });

const fileOf = (b) => `${b.chapter}_${String(b.i).padStart(3, '0')}.mp3`;
const pathOf = (b) => join(voicePath, fileOf(b));

/* 旧清单：用来判断哪些段落可以复用已有音频 */
const oldRange = manifestRange(html);
const oldManifest = oldRange ? parseManifestLiteral(oldRange.text) : null;
const oldByKey = new Map();
if (oldManifest && Array.isArray(oldManifest.blocks)) {
  for (const b of oldManifest.blocks) {
    const paths = Object.values(b.audio || {});
    if (paths[0]) oldByKey.set(`${b.chapter}#${b.i}`, { text: b.text, path: paths[0] });
  }
}

/* ── 3. 判定哪些要合成 ───────────────────────────────────── */
const reusable = new Map();      /* key → 最终绝对路径 */
const todo = [];

for (const b of blocks) {
  const key = `${b.chapter}#${b.i}`;
  const old = oldByKey.get(key);
  if (!opts.force && old && old.text === b.text) {
    const oldAbs = resolve(htmlDir, old.path);
    if (existsSync(oldAbs)) {
      const newAbs = pathOf(b);
      if (oldAbs !== newAbs) {
        try { renameSync(oldAbs, newAbs); } catch { /* 重命名失败就沿用旧路径 */ }
      }
      reusable.set(key, existsSync(newAbs) ? newAbs : oldAbs);
      continue;
    }
  }
  todo.push(b);
}

console.log(`\n音色：${opts.voiceName}  (${opts.voiceId})`);
console.log(`段落：${blocks.length} 段 —— 复用 ${reusable.size} 段，需合成 ${todo.length} 段\n`);

/* ── 4. 合成（带 429 退避重试与缩批） ────────────────────── */
function sleep(ms) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, ms);
}

function callTTS(requests) {
  const raw = execFileSync(
    'mcode-tools',
    ['connector', 'call', 'connector__matrix__batch_text_to_audio', '--args', JSON.stringify({ requests })],
    { encoding: 'utf8', maxBuffer: 32 * 1024 * 1024 }
  );
  return JSON.parse(raw);
}

function synthBatch(requests) {
  const results = new Map();      /* file_name → node_id */
  const errors = [];              /* {req, msg} */
  let queue = requests.slice();
  let limit = 10;
  let delayMs = 3000;

  for (let round = 0; round < 8 && queue.length; round++) {
    const groups = [];
    for (let i = 0; i < queue.length; i += limit) groups.push(queue.slice(i, i + limit));

    const retry = [];
    for (const g of groups) {
      let res;
      try { res = callTTS(g); }
      catch (e) {
        const msg = String(e.stderr || e.message).slice(0, 200);
        errors.push(...g.map((r) => ({ req: r, msg })));
        continue;
      }
      for (const it of res.success_items || []) results.set(it.file_name, it.node_id);

      for (const f of res.failed_items || []) {
        const req = g[f.index];
        const msg = f.error_msg || `err_code ${f.err_code}`;
        if (f.err_code === 429 || /rate.?limit|too many|busy/i.test(msg)) retry.push({ req, msg });
        else errors.push({ req, msg });
      }
    }

    if (!retry.length) break;

    limit = Math.max(1, Math.min(limit, 3));
    queue = retry.map((x) => x.req);
    console.log(`      ↻ ${queue.length} 段被上游限流，${delayMs / 1000}s 后以每批 ${limit} 段重试`);
    sleep(delayMs);
    delayMs = Math.min(delayMs * 2, 45000);
  }

  for (const req of queue) {
    if (!results.has(req.output_file)) errors.push({ req, msg: '重试 8 轮仍未成功（上游持续限流）' });
  }
  return { results, errors };
}

const requests = todo.map((b) => ({
  text: b.text,
  voice_id: opts.voiceId,
  speed: opts.speed,
  emotion: opts.emotion,
  output_file: fileOf(b),
}));

const { results, errors } = requests.length ? synthBatch(requests) : { results: new Map(), errors: [] };
for (const e of errors) console.error(`  ✗ ${e.req.output_file} 合成失败：${e.msg}`);

let done = 0;
const failed = errors.map((e) => e.req.output_file);
for (const b of todo) {
  const fname = fileOf(b);
  const nodeId = results.get(fname);
  if (!nodeId) continue;
  try {
    const au = JSON.parse(execFileSync('mcode-tools', ['get-asset-url', nodeId], { encoding: 'utf8' }));
    const resp = await fetch(au.download_url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const buf = Buffer.from(await resp.arrayBuffer());
    if (buf.length < 1024) throw new Error(`文件过小（${buf.length} 字节），可能不是有效音频`);
    writeFileSync(pathOf(b), buf);
    done++;
    process.stdout.write(`\r  已下载 ${done}/${todo.length} 段`);
  } catch (e) {
    failed.push(fname);
    console.error(`\n  ✗ ${fname} 下载失败：${String(e.message).slice(0, 160)}`);
  }
}
if (todo.length) process.stdout.write('\n');

/* ── 5. 写 AUDIO_MANIFEST ───────────────────────────────── */
const finalPath = new Map();      /* key → 绝对路径 */
for (const b of blocks) {
  const key = `${b.chapter}#${b.i}`;
  const p = pathOf(b);
  if (existsSync(p)) finalPath.set(key, p);
  else if (reusable.has(key)) finalPath.set(key, reusable.get(key));
}
const have = blocks.filter((b) => finalPath.has(`${b.chapter}#${b.i}`));

if (!have.length) {
  console.error('\n没有生成任何音频，页面保持原来的音源设置。');
  process.exit(1);
}

const relPath = (abs) => {
  const r = relative(htmlDir, abs).split(/[\\/]/).join('/');
  return r.startsWith('.') ? r : r;
};

const manifest = {
  generatedFrom: 'make-audio.mjs',
  speed: opts.speed,
  emotion: opts.emotion,
  voices: [{ id: opts.voiceId, name: opts.voiceName }],
  blocks: have.map((b) => ({
    i: b.i, n: b.n, chapter: b.chapter, kind: b.kind, text: b.text,
    audio: { [opts.voiceId]: relPath(finalPath.get(`${b.chapter}#${b.i}`)) },
  })),
};

const json = JSON.stringify(manifest, null, 2).replace(/</g, '\\u003c');
const range = manifestRange(html);
if (!range) {
  console.error('脚本里没有 var AUDIO_MANIFEST 声明，写不进去。');
  process.exit(1);
}
writeFileSync(htmlPath, html.slice(0, range.start) + json + html.slice(range.end), 'utf8');

/* ── 6. 收尾 ────────────────────────────────────────────── */
const total = have.reduce((s, b) => s + statSync(finalPath.get(`${b.chapter}#${b.i}`)).size, 0);
const missList = failed.map((f) => String(f).replace(/\.mp3$/, '')).join(',');
console.log(`\n✅ 清单已写回 ${htmlPath}`);
console.log(`   音色：${opts.voiceName}（${opts.voiceId}）`);
console.log(`   段落：${have.length}/${blocks.length} 段配了音频${failed.length ? `，${failed.length} 段没配上（${missList}）` : ''}`);
console.log(`   文件：${voicePath}`);
console.log(`   体积：${(total / 1024 / 1024).toFixed(2)} MB`);
if (failed.length) {
  console.log('\n⚠️  失败的段落不会出现在清单里，引擎会自动走浏览器合成兜底。');
  console.log('   过一会儿重跑同一条命令即可，已生成的文件不会重做。');
}
