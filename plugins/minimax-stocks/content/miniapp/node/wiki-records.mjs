// @ts-check
// 资料元数据与「带日期、带出处的记录」：资料类型 / 日期识别、节点的最新动态与边际变化、出处解析、收录舆情的文件格式。
// 只有纯函数，状态和落盘在 wiki-service.mjs。
import { createHash } from 'node:crypto';
import { nameKey } from './wiki-format.mjs';

export const DOC_TYPES = Object.freeze(['纪要', '研报', '公告', '新闻', '笔记', '舆情', '其他']);
export const CHANGE_DIMENSIONS = Object.freeze(['订单', '价格', '产能', '业绩', '客户', '技术', '政策', '竞争', '供需', '其他']);
/** 方向是 Agent 依据资料做的判断，界面上会注明。 */
export const CHANGE_DIRECTIONS = Object.freeze({ improve: '改善', weaken: '走弱', unclear: '待判断' });
export const RECORD_KINDS = Object.freeze({ update: '最新动态', change: '边际变化' });
export const MAX_RECORDS = 5000;

const MINUTES_PATTERN = /纪要|调研|交流|电话会|路演|专家|访谈|业绩会|说明会|minutes|transcript/i;

/** 文件名或路径看起来像会议 / 调研纪要（Agent 打过类型时以 Agent 为准）。 */
export function looksLikeMinutes(rel) {
  return MINUTES_PATTERN.test(String(rel ?? ''));
}

const clean = (value, max) => (typeof value === 'string' ? value.replace(/\s+/g, ' ').trim().slice(0, max) : '');

function validDate(y, m, d) {
  const year = Number(y), month = Number(m), day = Number(d);
  if (!(month >= 1 && month <= 12 && day >= 1 && day <= 31)) return null;
  const date = new Date(Date.UTC(year, month - 1, day));
  if (date.getUTCMonth() !== month - 1) return null;
  return year + '-' + String(month).padStart(2, '0') + '-' + String(day).padStart(2, '0');
}

/** 从文件名、标题或时间字符串里找日期：2026-10-12、2026.10.12、2026年10月12日、20261012。 */
export function dateFromText(text) {
  const s = String(text ?? '');
  const sep = s.match(/(20\d{2})\s*[-_./年]\s*(\d{1,2})\s*[-_./月]\s*(\d{1,2})/);
  if (sep) { const value = validDate(sep[1], sep[2], sep[3]); if (value) return value; }
  const compact = s.match(/(?<!\d)(20\d{2})(\d{2})(\d{2})(?!\d)/);
  if (compact) return validDate(compact[1], compact[2], compact[3]);
  return null;
}

/** Agent 给出的日期：YYYY-MM-DD，或只知道月份时 YYYY-MM。 */
export function normalizeDate(value) {
  if (typeof value !== 'string') return null;
  const s = value.trim();
  const full = dateFromText(s);
  if (full) return full;
  const month = s.match(/^(20\d{2}|19\d{2})\s*[-/.年]\s*(\d{1,2})\s*月?$/);
  if (month && Number(month[2]) >= 1 && Number(month[2]) <= 12) return month[1] + '-' + String(Number(month[2])).padStart(2, '0');
  return null;
}

export function safeUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return null;
  try {
    const url = new URL(value.trim());
    return url.protocol === 'http:' || url.protocol === 'https:' ? url.href : null;
  } catch {
    return null;
  }
}

/**
 * 资料文件索引，用来把出处文字对应到可打开的文件。
 * @param {{ key: string, display: string, path: string, base: string, baseNoExt: string }[]} entries
 */
export function createFileIndex(entries) {
  const byKey = new Map(), byDisplay = new Map(), byPath = new Map(), byBase = new Map();
  for (const entry of entries) {
    byKey.set(entry.key, entry);
    byDisplay.set(nameKey(entry.display), entry);
    byPath.set(entry.path, entry);
    for (const base of new Set([entry.base, entry.baseNoExt])) {
      if (!base || base.length < 4) continue;
      const key = nameKey(base);
      if (!byBase.has(key)) byBase.set(key, []);
      byBase.get(key).push(entry);
    }
  }
  const displays = [...entries].sort((a, b) => b.display.length - a.display.length);
  return { entries, byKey, byDisplay, byPath, byBase, displays };
}

/** 按 key、路径、「文件夹/文件名」或唯一的文件名找文件。 */
export function lookupFile(ref, index) {
  if (typeof ref !== 'string' || !ref.trim()) return null;
  const value = ref.trim();
  const byBase = index.byBase.get(nameKey(value));
  return index.byKey.get(value) ?? index.byPath.get(value) ?? index.byDisplay.get(nameKey(value)) ?? (byBase?.length === 1 ? byBase[0] : null);
}

function locatorAfter(text, needle) {
  const at = text.indexOf(needle);
  if (at < 0) return '';
  return clean((text.slice(0, at) + ' ' + text.slice(at + needle.length)).replace(/^[\s·:：,，、-]+/, ''), 120);
}

/** 在一段出处文字里找最长的已知文件（「文件夹/文件名」优先，其次唯一的文件名）。 */
function findFileInText(text, index) {
  const folded = nameKey(text);
  for (const entry of index.displays) {
    const display = nameKey(entry.display);
    if (display.length >= 4 && folded.includes(display)) return { entry, locator: locatorAfter(text, entry.display) };
  }
  let best = null;
  for (const [base, list] of index.byBase) {
    if (list.length !== 1 || base.length < 6 || !folded.includes(base)) continue;
    if (!best || base.length > best.base.length) best = { base, entry: list[0] };
  }
  if (!best) return null;
  const needle = [best.entry.base, best.entry.baseNoExt].find((item) => item && text.includes(item)) ?? '';
  return { entry: best.entry, locator: needle ? locatorAfter(text, needle) : '' };
}

/**
 * 一条出处（字符串，或 { file, url, locator, label }）→ { label, file?, url?, locator? }。
 * file 存资料文件的 key，界面据此用默认应用打开；找不到文件时只保留文字。
 */
export function parseSource(src, index) {
  if (src && typeof src === 'object') {
    const locator = clean(src.locator, 120);
    const url = safeUrl(src.url);
    if (url) return { label: clean(src.label, 200) || url, url, ...(locator ? { locator } : {}) };
    const entry = typeof src.file === 'string' ? lookupFile(src.file, index) : null;
    if (entry) return { label: entry.display + (locator ? ' ' + locator : ''), file: entry.key, ...(locator ? { locator } : {}) };
    const label = clean(src.label ?? src.file ?? '', 200);
    return label ? { label: label + (locator ? ' ' + locator : '') } : null;
  }
  const text = clean(src, 300);
  if (!text) return null;
  const urlMatch = text.match(/https?:\/\/[^\s)）」』"'<>，。]+/);
  const url = urlMatch ? safeUrl(urlMatch[0]) : null;
  if (url) return { label: text, url };
  const found = findFileInText(text, index);
  if (found) return { label: text, file: found.entry.key, ...(found.locator ? { locator: found.locator } : {}) };
  return { label: text };
}

export function recordId(record) {
  const basis = [record.kind, nameKey(record.entity), record.date, nameKey(record.text)].join('|');
  return 'r' + createHash('sha1').update(basis).digest('hex').slice(0, 12);
}

/**
 * 校验并规范一条记录。entity 必须是已有页面；date 和 sources 必填。
 * @param {any} input
 * @param {{ resolveEntity: (name: string) => { title: string } | null, resolveSource: (src: any) => any }} ctx
 */
export function normalizeRecord(input, ctx) {
  const fail = (message) => { throw Object.assign(new Error(message), { code: 'INVALID_ARGUMENTS' }); };
  if (!input || typeof input !== 'object') fail('每条记录需要是对象');
  const kind = input.kind === 'change' ? 'change' : input.kind === 'update' ? 'update' : null;
  if (!kind) fail('kind 只能是 update（最新动态）或 change（边际变化）');
  const entityName = clean(input.entity, 120);
  if (!entityName) fail('entity 必填：记录属于哪个节点（页面标题）');
  const entity = ctx.resolveEntity(entityName);
  if (!entity) fail('「' + entityName + '」还没有页面：先用 wiki_upsert_page 建页面，或改用已有页面的标题');
  const date = normalizeDate(input.date);
  if (!date) fail('date 必填，格式 YYYY-MM-DD（只知道月份时 YYYY-MM）；用资料或事件本身的日期，不要用今天');
  const text = clean(input.text, 400);
  if (text.length < 4) fail('text 必填：一句话写清楚事实或变化');
  const sources = (Array.isArray(input.sources) ? input.sources.slice(0, 8) : []).map((src) => ctx.resolveSource(src)).filter(Boolean);
  if (!sources.length) fail('sources 至少一条：资料文件（wiki_job_brief 的 file 字段，可加 locator 写页码 / 小节）或网页链接');
  /** @type {any} */
  const record = { kind, entity: entity.title, date, text, sources };
  if (kind === 'change') {
    record.dimension = CHANGE_DIMENSIONS.includes(input.dimension) ? input.dimension : '其他';
    record.direction = typeof input.direction === 'string' && input.direction in CHANGE_DIRECTIONS ? input.direction : 'unclear';
    const from = clean(input.from, 160), to = clean(input.to, 160);
    if (from) record.from = from;
    if (to) record.to = to;
  }
  record.id = recordId(record);
  return record;
}

const sourceIdentity = (src) => (src.url ? 'u:' + src.url : src.file ? 'f:' + src.file + '|' + (src.locator ?? '') : 't:' + nameKey(src.label));

/** 按日期倒序，同一天按写入时间倒序。 */
export function sortRecords(list) {
  return [...list].sort((a, b) => String(b.date).localeCompare(String(a.date)) || String(b.createdAt ?? '').localeCompare(String(a.createdAt ?? '')));
}

/** 同一节点、同一天、同一句话视为同一条记录：合并出处，补全维度和方向。 */
export function mergeRecords(existing, incoming, { origin = 'chat', jobId = null, now = new Date().toISOString(), max = MAX_RECORDS } = {}) {
  const byId = new Map(existing.map((record) => [record.id, record]));
  const added = [], merged = [];
  for (const record of incoming) {
    const prior = byId.get(record.id);
    if (prior) {
      const seen = new Set(prior.sources.map(sourceIdentity));
      const next = { ...prior, sources: [...prior.sources, ...record.sources.filter((src) => !seen.has(sourceIdentity(src)))].slice(0, 12), updatedAt: now };
      if (record.kind === 'change') {
        if (record.dimension && (!prior.dimension || prior.dimension === '其他')) next.dimension = record.dimension;
        if (record.direction && (!prior.direction || prior.direction === 'unclear')) next.direction = record.direction;
        if (record.from && !prior.from) next.from = record.from;
        if (record.to && !prior.to) next.to = record.to;
      }
      byId.set(record.id, next);
      merged.push(record.id);
    } else {
      byId.set(record.id, { ...record, origin, ...(jobId ? { jobId } : {}), createdAt: now });
      added.push(record.id);
    }
  }
  let records = [...byId.values()];
  if (records.length > max) records = sortRecords(records).slice(0, max);
  return { records, added, merged };
}

/** 读回磁盘上的记录：丢掉结构不对的条目。 */
export function normalizeStoredRecords(value) {
  if (!Array.isArray(value)) return [];
  return value.filter((record) => record && typeof record.id === 'string' && (record.kind === 'update' || record.kind === 'change')
    && typeof record.entity === 'string' && typeof record.date === 'string' && typeof record.text === 'string' && Array.isArray(record.sources)).slice(0, MAX_RECORDS);
}

/** 去掉 frontmatter、标题符号和表格分隔线后的正文摘录。 */
export function excerptFromText(text, max = 200) {
  const body = String(text ?? '').replace(/^\uFEFF?---\n[\s\S]*?\n---\n/, '').split('\n')
    .map((line) => line.replace(/^#{1,6}\s+/, '').replace(/^>\s?/, '').replace(/[*_]/g, '').trim())
    .filter((line) => line && !/^[-|:\s]+$/.test(line))
    .join(' ');
  return body.replace(/\s+/g, ' ').trim().slice(0, max);
}

export function sanitizeFileName(text, max = 60) {
  const cleaned = String(text ?? '').replace(/[\\/:*?"<>|\u0000-\u001f]/g, ' ').replace(/\s+/g, ' ').trim().replace(/^\.+/, '');
  return cleaned.slice(0, max).trim() || '未命名';
}

/** 收录的舆情按来源分子目录：知识星球 / 进门财经 / 腾讯文档。 */
export function clipSourceDir(source) {
  return sanitizeFileName(source || '舆情', 20);
}

export function clipFileName(item, today = new Date().toISOString().slice(0, 10)) {
  return (dateFromText(String(item?.publishedAt ?? '')) ?? today) + ' ' + sanitizeFileName(item?.title) + '.md';
}

/** 收录的舆情存成 Markdown：frontmatter 记来源、链接、时间和股票，正文是原文。 */
export function clipMarkdown(item, stock) {
  const field = (key, value) => key + ': ' + JSON.stringify(value ?? '');
  const lines = [
    '---',
    field('source', item.source), field('title', item.title),
    ...(safeUrl(item.url) ? [field('url', safeUrl(item.url))] : []),
    field('publishedAt', item.publishedAt ?? ''), field('symbol', stock.symbol), field('stock', stock.name ?? ''),
    field('sentimentId', item.id), field('importedAt', stock.importedAt),
    '---',
    '',
    '# ' + String(item.title ?? '').trim(),
    '',
    '> ' + [item.source, String(item.publishedAt ?? '').slice(0, 10), stock.name ? stock.name + '（' + stock.symbol + '）' : stock.symbol].filter(Boolean).join(' · '),
    '',
    String(item.content || item.summary || '').trim(),
    '',
  ];
  if (Array.isArray(item.tags) && item.tags.length) lines.push('标签：' + item.tags.join('、'), '');
  if (safeUrl(item.url)) lines.push('原文：' + safeUrl(item.url), '');
  return lines.join('\n');
}
