// @ts-check
// 产业链 Wiki 的纯逻辑：页面 schema、frontmatter 读写、合并、图谱、检索。
// 方法论参考 Karpathy 的 LLM-Wiki 模式（原始资料 → LLM 维护的 Wiki → 规则），实现为本插件自写。

export const PAGE_TYPES = Object.freeze({
  industry: '行业',
  segment: '产业链环节',
  company: '公司',
  product: '产品/技术',
  concept: '概念/指标',
  event: '事件/政策',
  source: '资料摘要',
});

export const CHAIN_POSITIONS = Object.freeze({
  upstream: '上游',
  midstream: '中游',
  downstream: '下游',
});

/** 有向关系：from（页面本身）→ target。 */
export const RELATION_TYPES = Object.freeze({
  upstream_of: '上游供给',
  supplies: '供货给',
  belongs_to: '属于',
  produces: '生产 / 布局',
  competes: '竞争',
  substitutes: '替代',
  drives: '驱动 / 影响',
  related: '相关',
});

export const LIMITS = Object.freeze({
  title: 80,
  body: 40_000,
  listItem: 120,
  listLength: 40,
  relations: 120,
  relationNote: 400,
  relationSource: 300,
});

const FORBIDDEN_FILE_CHARS = /[\\/:*?"<>|#^[\]\u0000-\u001f]+/g;

/** 页面 id = 文件名主干；保留中文，去掉文件系统和 wikilink 不允许的字符。 */
export function slugify(title) {
  const cleaned = String(title ?? '')
    .normalize('NFKC')
    .replace(FORBIDDEN_FILE_CHARS, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/^[.\-\s]+|[.\-\s]+$/g, '')
    .slice(0, LIMITS.title);
  return cleaned;
}

export function nameKey(value) {
  return String(value ?? '').normalize('NFKC').trim().toLowerCase().replace(/\s+/g, ' ');
}

export function normalizeTicker(value) {
  const compact = String(value ?? '').trim().toUpperCase().replace(/\s+/g, '');
  const prefix = compact.match(/^(SH|SZ|BJ)[:._-]?(\d{6})$/);
  if (prefix) return `${prefix[2]}.${prefix[1]}`;
  const suffix = compact.match(/^(\d{6})[:._-]?(SH|SZ|BJ)$/);
  if (suffix) return `${suffix[1]}.${suffix[2]}`;
  if (/^\d{6}$/.test(compact)) {
    if (/^(60|68)/.test(compact)) return `${compact}.SH`;
    if (/^(00|30)/.test(compact)) return `${compact}.SZ`;
    if (/^(43|8[37]|92)/.test(compact)) return `${compact}.BJ`;
  }
  return compact;
}

function invalid(message) {
  const error = new Error(message);
  /** @type {any} */ (error).code = 'INVALID_ARGUMENTS';
  return error;
}

function cleanText(value, max) {
  return typeof value === 'string' ? value.normalize('NFKC').replace(/\s+/g, ' ').trim().slice(0, max) : '';
}

function cleanList(value, { max = LIMITS.listItem, length = LIMITS.listLength, map = (v) => v } = {}) {
  if (value === undefined || value === null) return [];
  const items = Array.isArray(value) ? value : [value];
  const out = [];
  const seen = new Set();
  for (const item of items) {
    const text = map(cleanText(item, max));
    if (!text) continue;
    const key = nameKey(text);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push(text);
    if (out.length >= length) break;
  }
  return out;
}

/**
 * 校验并规范化一次写入请求（MCP wiki_upsert_page）。错误信息面向 Agent，说明如何修正。
 * @param {any} input
 */
export function validateUpsert(input) {
  if (!input || typeof input !== 'object') throw invalid('参数必须是对象');
  const title = cleanText(input.title, LIMITS.title + 1);
  if (!title) throw invalid('title 必填：页面标题，例如「光模块」「中际旭创」');
  if (title.length > LIMITS.title) throw invalid(`title 不能超过 ${LIMITS.title} 个字符`);
  if (!slugify(title)) throw invalid('title 不能只包含符号');
  const type = input.type === undefined ? undefined : String(input.type);
  if (type !== undefined && !(type in PAGE_TYPES)) {
    throw invalid(`type 只能是 ${Object.keys(PAGE_TYPES).join(' / ')}`);
  }
  let chain;
  if (input.chain !== undefined && input.chain !== null && input.chain !== '') {
    chain = String(input.chain);
    if (!(chain in CHAIN_POSITIONS)) throw invalid('chain 只能是 upstream / midstream / downstream，或留空');
  } else if (input.chain === null || input.chain === '') chain = null;
  const body = input.body === undefined ? undefined : String(input.body);
  if (body !== undefined && body.length > LIMITS.body) throw invalid(`body 不能超过 ${LIMITS.body} 个字符，请精简或拆成多个页面`);
  const relationsInput = input.relations === undefined ? [] : input.relations;
  if (!Array.isArray(relationsInput)) throw invalid('relations 必须是数组');
  if (relationsInput.length > LIMITS.relations) throw invalid(`一次最多写入 ${LIMITS.relations} 条关系`);
  const relations = relationsInput.map((rel, index) => validateRelation(rel, index, title));
  return {
    title,
    ...(type !== undefined ? { type } : {}),
    ...(chain !== undefined ? { chain } : {}),
    ...(input.industry !== undefined ? { industry: cleanText(input.industry, LIMITS.title) || null } : {}),
    tickers: cleanList(input.tickers, { max: 16, map: normalizeTicker }),
    aliases: cleanList(input.aliases, { max: LIMITS.title }).filter((alias) => nameKey(alias) !== nameKey(title)),
    tags: cleanList(input.tags, { max: 30, length: 20 }),
    sources: cleanList(input.sources, { max: LIMITS.relationSource, length: 60 }),
    ...(body !== undefined ? { body: body.replace(/\r\n?/g, '\n').trim() } : {}),
    relations,
    replaceRelations: input.replace_relations === true,
  };
}

function validateRelation(rel, index, title) {
  if (!rel || typeof rel !== 'object') throw invalid(`relations[${index}] 必须是对象`);
  const type = String(rel.type ?? '');
  if (!(type in RELATION_TYPES)) throw invalid(`relations[${index}].type 只能是 ${Object.keys(RELATION_TYPES).join(' / ')}`);
  const target = cleanText(rel.target, LIMITS.title + 1);
  if (!target || !slugify(target)) throw invalid(`relations[${index}].target 必填：目标页面标题`);
  if (target.length > LIMITS.title) throw invalid(`relations[${index}].target 不能超过 ${LIMITS.title} 个字符`);
  if (nameKey(target) === nameKey(title)) throw invalid(`relations[${index}] 不能指向页面自己`);
  const note = cleanText(rel.note, LIMITS.relationNote);
  const source = cleanText(rel.source, LIMITS.relationSource);
  const status = rel.status === 'pending' || !source ? 'pending' : 'confirmed';
  return { type, target, ...(note ? { note } : {}), ...(source ? { source } : {}), status };
}

/**
 * 合并到已有页面：标量字段覆盖、列表并集、关系按 (type,target) 去重覆盖；body 提供时整体替换。
 * @param {any | null} existing
 * @param {ReturnType<typeof validateUpsert>} input
 * @param {string} now
 */
export function mergePage(existing, input, now) {
  const base = existing ?? {
    id: slugify(input.title),
    title: input.title,
    type: input.type ?? 'concept',
    chain: null,
    industry: null,
    tickers: [], aliases: [], tags: [], sources: [], relations: [],
    created: now,
    updated: now,
    body: '',
  };
  const union = (a, b, length = LIMITS.listLength) => cleanList([...(a ?? []), ...(b ?? [])], { max: LIMITS.relationSource, length });
  const relations = input.replaceRelations ? [] : [...(base.relations ?? [])];
  for (const rel of input.relations) {
    const at = relations.findIndex((item) => item.type === rel.type && nameKey(item.target) === nameKey(rel.target));
    if (at === -1) relations.push(rel);
    else {
      const prev = relations[at];
      relations[at] = {
        ...prev,
        ...rel,
        note: rel.note ?? prev.note,
        source: rel.source ?? prev.source,
        status: rel.source || prev.source ? (rel.status === 'pending' && !rel.source && prev.status === 'confirmed' ? 'confirmed' : rel.status) : 'pending',
      };
      if (!relations[at].note) delete relations[at].note;
      if (!relations[at].source) delete relations[at].source;
    }
  }
  return {
    ...base,
    type: input.type ?? base.type,
    chain: input.chain !== undefined ? input.chain : base.chain,
    industry: input.industry !== undefined ? input.industry : base.industry,
    tickers: union(base.tickers, input.tickers, 12),
    aliases: union(base.aliases, input.aliases).filter((alias) => nameKey(alias) !== nameKey(base.title)),
    tags: union(base.tags, input.tags, 20),
    sources: union(base.sources, input.sources, 80),
    relations: relations.slice(0, 400),
    body: input.body !== undefined ? input.body : base.body,
    updated: now,
  };
}

const FRONT_KEYS = ['title', 'type', 'chain', 'industry', 'tickers', 'aliases', 'tags', 'sources', 'relations', 'created', 'updated'];

/** 每个 frontmatter 字段一行 `key: <JSON>`（JSON 也是合法的 YAML flow 值）。 */
export function serializePage(page) {
  const lines = ['---'];
  for (const key of FRONT_KEYS) {
    const value = page[key];
    if (value === undefined || value === null || (Array.isArray(value) && value.length === 0)) continue;
    lines.push(`${key}: ${JSON.stringify(value)}`);
  }
  lines.push('---', '', page.body ?? '', '');
  return lines.join('\n');
}

/**
 * 解析页面文件。兼容用户手改的简单 YAML 标量和 `[a, b]` 列表。
 * @param {string} text @param {string} id
 */
export function parsePage(text, id) {
  const normalized = String(text).replace(/\r\n?/g, '\n');
  /** @type {Record<string, any>} */
  const meta = {};
  let body = normalized;
  if (normalized.startsWith('---\n')) {
    const end = normalized.indexOf('\n---', 4);
    if (end !== -1) {
      const header = normalized.slice(4, end);
      body = normalized.slice(end + 4).replace(/^[^\n]*\n/, '');
      for (const line of header.split('\n')) {
        const match = line.match(/^([a-z_]+):\s*(.*)$/);
        if (!match) continue;
        meta[match[1]] = parseValue(match[2]);
      }
    }
  }
  const list = (value) => (Array.isArray(value) ? value.filter((item) => typeof item === 'string') : typeof value === 'string' && value ? [value] : []);
  const relations = Array.isArray(meta.relations)
    ? meta.relations.filter((rel) => rel && typeof rel === 'object' && typeof rel.target === 'string' && rel.type in RELATION_TYPES)
      .map((rel) => ({
        type: rel.type,
        target: String(rel.target).slice(0, LIMITS.title),
        ...(typeof rel.note === 'string' && rel.note ? { note: rel.note.slice(0, LIMITS.relationNote) } : {}),
        ...(typeof rel.source === 'string' && rel.source ? { source: rel.source.slice(0, LIMITS.relationSource) } : {}),
        status: rel.status === 'confirmed' && rel.source ? 'confirmed' : 'pending',
      }))
    : [];
  return {
    id,
    title: typeof meta.title === 'string' && meta.title.trim() ? meta.title.trim().slice(0, LIMITS.title) : id,
    type: typeof meta.type === 'string' && meta.type in PAGE_TYPES ? meta.type : 'concept',
    chain: typeof meta.chain === 'string' && meta.chain in CHAIN_POSITIONS ? meta.chain : null,
    industry: typeof meta.industry === 'string' && meta.industry.trim() ? meta.industry.trim().slice(0, LIMITS.title) : null,
    tickers: list(meta.tickers).map(normalizeTicker),
    aliases: list(meta.aliases),
    tags: list(meta.tags),
    sources: list(meta.sources),
    relations,
    created: typeof meta.created === 'string' ? meta.created : null,
    updated: typeof meta.updated === 'string' ? meta.updated : null,
    body: body.trim(),
  };
}

function parseValue(raw) {
  const value = raw.trim();
  if (value === '') return '';
  try {
    return JSON.parse(value);
  } catch {
    if (value.startsWith('[') && value.endsWith(']')) {
      return value.slice(1, -1).split(',').map((item) => item.trim().replace(/^["']|["']$/g, '')).filter(Boolean);
    }
    return value.replace(/^["']|["']$/g, '');
  }
}

/** 文本本身是不是一个股票代码（600519 / 600519.SH / SH600519 / 0700.HK）；是则返回规范代码。 */
export function tickerFromText(text) {
  const raw = String(text ?? '').normalize('NFKC').trim();
  if (!raw || raw.length > 12) return null;
  const ticker = normalizeTicker(raw);
  if (/^\d{6}\.(SH|SZ|BJ)$/.test(ticker)) return ticker;
  if (/^\d{4,5}\.HK$/.test(ticker)) return ticker;
  return null;
}

/** A 股代码去掉交易所后缀，用于「600519」这种裸代码的匹配。 */
export function bareCode(ticker) {
  const match = String(ticker ?? '').match(/^(\d{6})\.(SH|SZ|BJ)$/);
  return match ? match[1] : null;
}

const COMPANY_SUFFIX = /(股份有限公司|有限责任公司|有限公司|集团股份|控股股份|股份公司|（集团）|\(集团\)|集团|控股|公司|inc\.?|corp\.?|corporation|co\.,?\s*ltd\.?|ltd\.?|limited|holdings?)$/i;

/** 公司名归一：去掉括号里的代码、常见公司后缀和空白，用于识别「同一家公司的不同写法」。 */
export function normalizeCompanyName(name) {
  let value = String(name ?? '').normalize('NFKC').toLowerCase().replace(/[（(]\s*[a-z]{0,2}\d{4,6}(\.[a-z]{2})?\s*[)）]/g, '').replace(/\s+/g, '');
  for (let i = 0; i < 3; i += 1) {
    const next = value.replace(COMPANY_SUFFIX, '');
    if (next === value || next.length < 2) break;
    value = next;
  }
  return value;
}

/** 名称（标题、别名、股票代码和裸代码，忽略大小写）→ 页面 id。标题优先于别名，别名优先于代码。 */
export function buildNameIndex(pages) {
  const index = new Map();
  for (const page of pages) index.set(nameKey(page.title), page.id);
  for (const page of pages) {
    for (const alias of page.aliases ?? []) {
      const key = nameKey(alias);
      if (!index.has(key)) index.set(key, page.id);
    }
  }
  for (const page of pages) {
    for (const ticker of page.tickers ?? []) {
      for (const key of [nameKey(ticker), bareCode(ticker)]) if (key && !index.has(key)) index.set(key, page.id);
    }
  }
  return index;
}

/** 按股票代码找页面（代码规范化后比较）。 */
export function pageByTicker(pages, tickers) {
  const wanted = new Set((tickers ?? []).map(normalizeTicker).filter(Boolean));
  if (!wanted.size) return null;
  return pages.find((page) => (page.tickers ?? []).some((ticker) => wanted.has(normalizeTicker(ticker)))) ?? null;
}

/**
 * 找出疑似重复的节点组：同一股票代码、以代码为标题的页面、别名互指、公司名归一后相同或包含。
 * 只看公司（及以代码为标题的页面）；代码互相冲突的两页永远不算重复。
 * @param {any[]} pages
 */
export function findDuplicateGroups(pages) {
  const parent = new Map(pages.map((page) => [page.id, page.id]));
  const find = (id) => { while (parent.get(id) !== id) id = parent.get(id); return id; };
  /** @type {Map<string, { reasons: Set<string>, confidence: 'high' | 'medium' }>} */
  const links = new Map();
  const conflict = (a, b) => a.tickers.length && b.tickers.length && !a.tickers.some((ticker) => b.tickers.includes(ticker));
  const link = (a, b, reason, confidence) => {
    if (a.id === b.id || conflict(a, b)) return;
    parent.set(find(a.id), find(b.id));
    const key = [a.id, b.id].sort().join('\u0000');
    const entry = links.get(key) ?? { reasons: new Set(), confidence: 'medium' };
    entry.reasons.add(reason);
    if (confidence === 'high') entry.confidence = 'high';
    links.set(key, entry);
  };
  const companies = pages.filter((page) => page.type === 'company' || (page.tickers ?? []).length || tickerFromText(page.title));
  for (let i = 0; i < companies.length; i += 1) {
    for (let j = i + 1; j < companies.length; j += 1) {
      const a = companies[i], b = companies[j];
      const shared = a.tickers.find((ticker) => b.tickers.includes(ticker));
      if (shared) { link(a, b, '同一股票代码 ' + shared, 'high'); continue; }
      const ta = tickerFromText(a.title), tb = tickerFromText(b.title);
      if ((ta && b.tickers.includes(ta)) || (tb && a.tickers.includes(tb))) { link(a, b, '以股票代码命名的页面', 'high'); continue; }
      const namesA = [a.title, ...a.aliases].map(nameKey), namesB = [b.title, ...b.aliases].map(nameKey);
      if (namesA.some((name) => namesB.includes(name))) { link(a, b, '名称或别名相同', 'high'); continue; }
      if (a.type !== 'company' || b.type !== 'company') continue;
      const na = normalizeCompanyName(a.title), nb = normalizeCompanyName(b.title);
      if (na.length < 2 || nb.length < 2) continue;
      if (na === nb) link(a, b, '公司全称与简称', 'high');
      else if (na.includes(nb) || nb.includes(na)) link(a, b, '名称相近', 'medium');
    }
  }
  const groups = new Map();
  for (const page of companies) {
    const root = find(page.id);
    if (!groups.has(root)) groups.set(root, []);
    groups.get(root).push(page);
  }
  const result = [];
  for (const members of groups.values()) {
    if (members.length < 2) continue;
    const ids = new Set(members.map((page) => page.id));
    const reasons = new Set();
    let confidence = 'high';
    for (const [key, entry] of links) {
      const [a, b] = key.split('\u0000');
      if (!ids.has(a) || !ids.has(b)) continue;
      entry.reasons.forEach((reason) => reasons.add(reason));
      if (entry.confidence === 'medium') confidence = 'medium';
    }
    const primary = [...members].sort((a, b) => score(b) - score(a))[0];
    result.push({ confidence, reasons: [...reasons], primary: primary.id, pages: members.map((page) => ({ id: page.id, title: page.title, type: page.type, tickers: page.tickers, aliases: page.aliases, relations: page.relations.length, bodyLength: (page.body ?? '').length })) });
  }
  return result.sort((a, b) => (a.confidence === b.confidence ? 0 : a.confidence === 'high' ? -1 : 1));

  function score(page) {
    return (page.tickers.length ? 100 : 0) - (tickerFromText(page.title) ? 200 : 0) + page.relations.length * 2 + Math.min(50, (page.body ?? '').length / 200) + (page.type === 'company' ? 10 : 0);
  }
}

/**
 * 把若干页面合并进主页面（纯函数）：别名并入旧标题与别名，代码/标签/来源取并集，关系合并去掉指向自身的，
 * 正文保留主页面，其余页面的正文以「合并自」小节附在后面。
 */
export function mergeInto(into, froms, now) {
  const all = [into, ...froms];
  const selfKeys = new Set(all.flatMap((page) => [page.title, ...(page.aliases ?? []), ...(page.tickers ?? []), ...(page.tickers ?? []).map(bareCode)]).filter(Boolean).map(nameKey));
  const relations = [];
  for (const rel of all.flatMap((page) => page.relations ?? [])) {
    if (selfKeys.has(nameKey(rel.target))) continue;
    const at = relations.findIndex((item) => item.type === rel.type && nameKey(item.target) === nameKey(rel.target));
    if (at === -1) relations.push({ ...rel });
    else if (rel.status === 'confirmed' && relations[at].status !== 'confirmed') relations[at] = { ...rel };
  }
  let body = into.body ?? '';
  for (const page of froms) {
    const extra = String(page.body ?? '').trim();
    if (extra && !body.includes(extra.slice(0, 80))) body = (body ? body + '\n\n' : '') + '## 合并自「' + page.title + '」\n\n' + extra;
  }
  const union = (key, length) => cleanList(all.flatMap((page) => page[key] ?? []), { max: LIMITS.relationSource, length });
  return {
    ...into,
    type: into.type === 'concept' && froms.some((page) => page.type === 'company') ? 'company' : into.type,
    chain: into.chain ?? froms.find((page) => page.chain)?.chain ?? null,
    industry: into.industry ?? froms.find((page) => page.industry)?.industry ?? null,
    tickers: union('tickers', 12),
    aliases: cleanList([...(into.aliases ?? []), ...froms.flatMap((page) => [page.title, ...(page.aliases ?? [])])], { max: LIMITS.title, length: LIMITS.listLength }).filter((alias) => nameKey(alias) !== nameKey(into.title)),
    tags: union('tags', 20),
    sources: union('sources', 80),
    relations: relations.slice(0, 400),
    body,
    created: [into.created, ...froms.map((page) => page.created)].filter(Boolean).sort()[0] ?? now,
    updated: now,
  };
}

const WIKILINK = /\[\[([^\]|\n]{1,80})(?:\|[^\]\n]{0,80})?\]\]/g;

export function extractWikilinks(body) {
  const out = new Set();
  for (const match of String(body ?? '').matchAll(WIKILINK)) {
    const target = match[1].trim();
    if (target) out.add(target);
  }
  return [...out];
}

export function excerpt(body, length = 140) {
  return String(body ?? '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/^\s*\|.*$/gm, ' ')
    .replace(/^#+\s.*$/gm, ' ')
    .replace(/\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g, (_, target, label) => label || target)
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/[*_`>|#-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, length);
}

export function pageSummary(page) {
  return {
    id: page.id,
    title: page.title,
    type: page.type,
    chain: page.chain,
    industry: page.industry,
    tickers: page.tickers,
    aliases: page.aliases,
    tags: page.tags,
    sources: page.sources,
    relations: page.relations,
    updated: page.updated,
    excerpt: excerpt(page.body),
  };
}

/**
 * 图谱：节点为页面 + 尚无页面的关系目标（ghost），边为结构化关系 + 正文 wikilink（mention）。
 * @param {any[]} pages
 */
export function buildGraph(pages) {
  const names = buildNameIndex(pages);
  const ghosts = new Map();
  const edges = [];
  const typedPairs = new Set();
  const resolve = (name) => {
    const id = names.get(nameKey(name));
    if (id) return id;
    const ghostId = `ghost:${nameKey(name)}`;
    if (!ghosts.has(ghostId)) ghosts.set(ghostId, { id: ghostId, title: String(name).trim(), ghost: true, mentions: 0 });
    ghosts.get(ghostId).mentions += 1;
    return ghostId;
  };
  for (const page of pages) {
    for (const rel of page.relations ?? []) {
      const target = resolve(rel.target);
      if (target === page.id) continue;
      typedPairs.add(`${page.id}\u0000${target}`);
      typedPairs.add(`${target}\u0000${page.id}`);
      edges.push({ from: page.id, to: target, type: rel.type, status: rel.status, ...(rel.note ? { note: rel.note } : {}), ...(rel.source ? { source: rel.source } : {}) });
    }
  }
  for (const page of pages) {
    for (const link of extractWikilinks(page.body)) {
      const target = names.get(nameKey(link));
      if (!target || target === page.id || typedPairs.has(`${page.id}\u0000${target}`)) continue;
      typedPairs.add(`${page.id}\u0000${target}`);
      typedPairs.add(`${target}\u0000${page.id}`);
      edges.push({ from: page.id, to: target, type: 'mention', status: 'confirmed' });
    }
  }
  return { ghosts: [...ghosts.values()], edges };
}

/** 中文按二元组、其他按词切分。 */
export function tokenize(text) {
  const tokens = new Set();
  const lower = String(text ?? '').normalize('NFKC').toLowerCase();
  for (const word of lower.match(/[a-z0-9.]+/g) ?? []) if (word.length >= 2 || /\d/.test(word)) tokens.add(word);
  for (const run of lower.match(/[\u3400-\u9fff]+/g) ?? []) {
    if (run.length === 1) tokens.add(run);
    for (let i = 0; i < run.length - 1; i += 1) tokens.add(run.slice(i, i + 2));
  }
  return [...tokens];
}

/**
 * @param {any[]} pages @param {string} query @param {number} limit
 */
export function searchPages(pages, query, limit = 10) {
  const q = nameKey(query);
  if (!q) return [];
  const tokens = tokenize(q);
  const ticker = normalizeTicker(query);
  const results = [];
  for (const page of pages) {
    const title = nameKey(page.title);
    let score = 0;
    if (title === q) score += 40;
    else if (title.includes(q)) score += 18;
    if ((page.aliases ?? []).some((alias) => nameKey(alias) === q)) score += 30;
    else if ((page.aliases ?? []).some((alias) => nameKey(alias).includes(q))) score += 10;
    if ((page.tickers ?? []).includes(ticker)) score += 35;
    const tags = (page.tags ?? []).map(nameKey);
    if (tags.includes(q)) score += 8;
    if (page.industry && nameKey(page.industry) === q) score += 6;
    const haystack = `${title} ${(page.aliases ?? []).join(' ')} ${tags.join(' ')} ${String(page.body ?? '').toLowerCase()}`;
    let hits = 0;
    for (const token of tokens) if (haystack.includes(token)) hits += 1;
    if (tokens.length) score += Math.round((hits / tokens.length) * 12);
    if (score <= 0 || (tokens.length > 1 && hits / tokens.length < 0.5 && score < 10)) continue;
    results.push({ page, score });
  }
  results.sort((a, b) => b.score - a.score || a.page.title.localeCompare(b.page.title, 'zh-CN'));
  return results.slice(0, Math.max(1, Math.min(50, limit))).map(({ page, score }) => ({
    ...pageSummary(page),
    score,
    snippet: snippetFor(page.body, tokens),
  }));
}

function snippetFor(body, tokens) {
  const text = excerpt(body, 4000);
  const lower = text.toLowerCase();
  let at = -1;
  for (const token of tokens) {
    at = lower.indexOf(token);
    if (at !== -1) break;
  }
  if (at === -1) return text.slice(0, 160);
  const start = Math.max(0, at - 50);
  return `${start > 0 ? '…' : ''}${text.slice(start, start + 160)}`;
}

/** 一只股票相关的页面：tickers 命中，或标题/别名等于简称。 */
export function pagesForStock(pages, symbol, shortName) {
  const ticker = normalizeTicker(symbol);
  const name = nameKey(shortName);
  return pages.filter((page) => (ticker && (page.tickers ?? []).includes(ticker))
    || (name && (nameKey(page.title) === name || (page.aliases ?? []).some((alias) => nameKey(alias) === name))));
}

/** 生成人类可读的 index.md。 */
export function renderIndex(pages, now) {
  const lines = ['# 产业链 Wiki 索引', '', `> 由「股市」Mini App 维护，更新于 ${now}。共 ${pages.length} 个页面。`, ''];
  for (const [type, label] of Object.entries(PAGE_TYPES)) {
    const group = pages.filter((page) => page.type === type).sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'));
    if (!group.length) continue;
    lines.push(`## ${label}（${group.length}）`, '');
    for (const page of group) {
      const meta = [page.chain ? CHAIN_POSITIONS[page.chain] : '', page.industry ?? '', (page.tickers ?? []).join(' ')].filter(Boolean).join(' · ');
      const text = excerpt(page.body, 60);
      lines.push(`- [[${page.title}]]${meta ? ` — ${meta}` : ''}${text ? `：${text}` : ''}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}
