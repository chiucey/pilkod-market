// @ts-check
// 统一检索：一次查遍已经接入的数据源——Alpha派、进门财经、知识星球、腾讯文档、本地资料库，以及行情页已经抓到的舆情。
// 检索词来自知识图谱：主体（公司 / 环节 / 产品节点）的名称、别名、代码同步检索，算「直接提及」；
// 打开 neighbors 时再带上相邻节点（所属环节、产品、上下游、客户、供应商、竞争对手）一起检索，算「关联」，用于先发散、再收敛的研究。
// 没接入的来源由调用方直接不传进来，结果里不出现；接入了但这次调用失败的记进 failed，用来说明覆盖面。
import { fold, matchProfile, usableTerm } from './search-terms.mjs';

const DAY_MS = 86_400_000;
const CALL_TIMEOUT_MS = 20_000;
/** 一次统一检索的总时间预算（MCP 调用整体超时 30 秒，留出余量）。 */
const BUDGET_MS = 22_000;
export const MAX_ALIAS_QUERIES = 2;
export const MAX_NEIGHBOR_QUERIES = 4;

/** 相邻节点按方向分组：发散检索时每个方向轮流取，避免全是同一类。 */
export const NEIGHBOR_GROUPS = /** @type {const} */ ([
  ['所属', ['所属环节', '产品', '细分', '相关公司', '生产方']],
  ['上游', ['上游', '供应商']],
  ['下游', ['下游环节', '客户']],
  ['竞争', ['竞争对手', '替代']],
  ['其他', ['驱动因素', '影响', '相关']],
]);
const GROUP_OF = new Map(NEIGHBOR_GROUPS.flatMap(([group, labels]) => labels.map((label) => [label, group])));
const DEFAULT_TYPE = { 进门财经: '点评', 知识星球: '星球帖子', 腾讯文档: '在线文档', 本地资料库: '本地资料' };
const MODE_RANK = { semantic: 3, keyword: 2, local: 1, pool: 0 };
const REASONS = {
  TIMEOUT: '超时', ALPHAPAI_UNAUTHORIZED: 'API Key 失效或没有权限', ALPHAPAI_RATE_LIMITED: '调用太频繁（被限流）', ALPHAPAI_NETWORK: '网络不通',
  CONNECTOR_TOOL_MISSING: 'Connector 工具不在清单里', CONNECTOR_UNAVAILABLE: 'Connector 暂不可用', CONNECTOR_PARSE_ERROR: '返回格式无法识别',
  BUDGET: '超出本次检索的时间预算，少查了几个词',
};

const squash = (text) => String(text ?? '').replace(/\s+/g, ' ').trim();
const escapeRegExp = (text) => text.replace(/[.*+?^$(){}|[\]\\]/g, '\\$&');

/** 话题拆词：按空白和标点切开，留下能当检索词的（中文至少 2 个字，英文 / 数字至少 2 个字符）。 */
export function topicTokens(text) {
  const out = [];
  const seen = new Set();
  for (const part of squash(text).split(/[\s,，。;；、\/|·:：()（）【】\[\]"'“”‘’!?！？]+/)) {
    const token = part.trim();
    if (!token || seen.has(fold(token))) continue;
    if (!usableTerm(token) && !(token.length >= 2 && /^[a-z0-9][a-z0-9.+-]*$/i.test(token))) continue;
    seen.add(fold(token));
    out.push(token);
    if (out.length >= 8) break;
  }
  return out;
}

/** 发散检索用的相邻节点：只取节点本名，按「所属 → 上游 → 下游 → 竞争 → 其他」轮流取。 */
export function pickNeighbors(related, max = MAX_NEIGHBOR_QUERIES) {
  const primary = (related ?? []).filter((item) => item && item.term === item.node);
  const buckets = NEIGHBOR_GROUPS.map(([group]) => primary.filter((item) => (GROUP_OF.get(item.relation) ?? '其他') === group));
  const out = [];
  for (let round = 0; out.length < max && buckets.some((bucket) => bucket.length > round); round += 1) {
    for (const bucket of buckets) if (bucket[round] && out.length < max) out.push(bucket[round]);
  }
  return out;
}

/** 给 AI 的产业链地图：关系 → 节点名（每类最多 8 个）。 */
export function neighborMap(related) {
  /** @type {Record<string, string[]>} */
  const out = {};
  for (const item of related ?? []) {
    if (!item || item.term !== item.node || !item.relation) continue;
    const list = (out[item.relation] ??= []);
    if (!list.includes(item.node) && list.length < 8) list.push(item.node);
  }
  return out;
}

/**
 * 规划检索词。profile 是 wiki.researchProfile 的结果：subject 为 null 时按自由文本检索。
 * - 语义来源（Alpha派、进门财经）用 phrases：主体名 + 话题、别名 + 话题，发散时再加相邻节点。
 * - 关键词来源（知识星球、腾讯文档）用 keywords：只搜名称、别名、相邻节点，结果再按话题排序。
 * @param {{ query?: string, profile?: { subject: any, core: any[], related: any[] } | null, expand?: boolean, neighbors?: boolean }} input
 */
export function planResearch({ query = '', profile = null, expand = true, neighbors = false }) {
  const q = squash(query).slice(0, 120);
  const subject = profile?.subject ?? null;
  /** 全部叫法（名称、别名、代码）：用来判断「直接提及」，不受 expand 影响。 */
  const matchCore = [];
  const seen = new Set();
  for (const item of profile?.core ?? []) {
    const term = squash(item?.term);
    if (!term || seen.has(fold(term))) continue;
    seen.add(fold(term));
    matchCore.push({ term, kind: String(item.kind ?? 'name'), label: String(item.label ?? '') });
  }
  const names = matchCore.filter((item) => item.kind === 'name').map((item) => item.term);
  const main = names[0] ?? (subject ? squash(subject.title) : '');
  // 话题：有主体时，是 query 去掉主体各种叫法之后剩下的部分；没有主体时整句就是检索词。
  let topic = q;
  if (subject && q) {
    let rest = q;
    for (const name of [...matchCore.map((item) => item.term), squash(subject.title)].filter(Boolean).sort((a, b) => b.length - a.length)) {
      rest = rest.replace(new RegExp(escapeRegExp(name), 'gi'), ' ');
    }
    topic = squash(rest);
  }
  const tokens = topicTokens(topic);
  const aliases = expand
    ? matchCore.filter((item) => item.kind === 'alias' && !(main && fold(item.term).includes(fold(main)))).slice(0, MAX_ALIAS_QUERIES)
    : [];
  const related = Array.isArray(profile?.related) ? profile.related : [];
  const picks = neighbors ? pickNeighbors(related) : [];
  const ask = (name) => (topic ? name + ' ' + topic : name);
  /** @type {{ text: string, kind: string, label: string }[]} */
  const phrases = [];
  const addPhrase = (text, kind, label) => {
    const value = squash(text).slice(0, 160);
    if (value && !phrases.some((phrase) => fold(phrase.text) === fold(value))) phrases.push({ text: value, kind, label });
  };
  /** @type {string[]} */
  const keywords = [];
  const addKeyword = (text) => {
    const value = squash(text).slice(0, 60);
    if (value && !keywords.some((keyword) => fold(keyword) === fold(value))) keywords.push(value);
  };
  if (subject && main) {
    addPhrase(ask(main), 'name', '名称');
    addKeyword(main);
    for (const alias of aliases) {
      addPhrase(ask(alias.term), 'alias', '别名 ' + alias.term);
      addKeyword(alias.term);
    }
  } else if (q) {
    addPhrase(q, 'query', '检索词');
    addKeyword(q);
  }
  for (const pick of picks) {
    addPhrase(pick.term, 'related', pick.label);
    addKeyword(pick.term);
  }
  return {
    query: q,
    subject,
    topic: subject ? topic : '',
    tokens,
    matchCore,
    related: neighbors ? related : [],
    phrases,
    keywords,
    expand,
    neighbors,
    map: neighborMap(related),
  };
}

/** 一条结果和检索词的关系：直接提及（名称 / 别名 / 代码）、关联（相邻节点）、话题覆盖率。 */
function assess(entry, plan) {
  const item = entry.item;
  const hay = fold([item.title, item.summary, item.content, ...(Array.isArray(item.tags) ? item.tags : []), ...(Array.isArray(item.termHits) ? item.termHits : [])].join(' '));
  const match = matchProfile(hay, { core: plan.subject ? plan.matchCore : [], related: plan.related });
  const tokenHits = plan.tokens.filter((token) => hay.includes(fold(token)));
  const coverage = plan.tokens.length ? tokenHits.length / plan.tokens.length : 0;
  const phraseHit = !plan.subject && Boolean(plan.query) && hay.includes(fold(plan.query));
  // Alpha派 等来源自己给资料打了股票标签：标在主体公司上的就算直接提及（正文里不一定出现公司名）。
  const tickers = Array.isArray(plan.subject?.tickers) ? plan.subject.tickers : [];
  const tagged = tickers.length > 0 && Array.isArray(item.stocks) && item.stocks.some((stock) => tickers.includes(stock?.code));
  const direct = tagged || (plan.subject ? match.direct : phraseHit || (plan.tokens.length > 0 && coverage >= 0.5));
  // 标题里就出现主体（或检索词）的，多半是专门讲它的，比正文顺带提一句的更相关。
  const title = fold(item.title);
  const titleHit = plan.subject ? plan.matchCore.some((core) => title.includes(fold(core.term))) || (tagged && item.stocks.length <= 2) : plan.tokens.some((token) => title.includes(fold(token))) || (Boolean(plan.query) && title.includes(fold(plan.query)));
  const titleRelated = !titleHit && plan.related.some((rel) => title.includes(fold(rel.term)));
  let label;
  if (tagged) {
    label = '公司打标';
  } else if (plan.subject && match.direct) {
    const hit = match.core[0];
    label = hit.kind === 'alias' ? '别名 ' + hit.term : hit.kind === 'code' ? '代码 ' + hit.term : '直接提及';
  } else if (!plan.subject && direct) {
    label = phraseHit ? '直接提及' : '命中 ' + tokenHits.join('、');
  } else if (match.related.length) {
    label = '关联 · ' + match.related[0].label;
  } else {
    label = entry.mode === 'semantic' ? '语义召回' : '命中';
  }
  return { direct, related: match.related.length > 0, coverage, label, titleHit, titleRelated, topicHits: plan.subject ? tokenHits : [] };
}

/** 北京时间的日期。 */
export function dayOf(value) {
  const ts = Date.parse(String(value ?? ''));
  return Number.isFinite(ts) ? new Date(ts + 8 * 3_600_000).toISOString().slice(0, 10) : '';
}

function safeHttp(url) {
  try {
    const parsed = new URL(String(url));
    return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : '';
  } catch {
    return '';
  }
}

/** 条目的类型、日期、机构、链接（各来源字段不一样，在这里统一）。 */
export function itemFacts(item) {
  const tags = Array.isArray(item?.tags) ? item.tags : [];
  const institution = typeof item?.institution === 'string' && item.institution
    ? item.institution
    : item?.source === '进门财经' && typeof tags[1] === 'string' ? tags[1] : '';
  const type = typeof item?.docType === 'string' && item.docType
    ? item.docType
    : item?.source === '进门财经' && typeof tags[0] === 'string' && tags[0] ? tags[0] : DEFAULT_TYPE[item?.source] ?? '资料';
  const url = safeHttp(item?.url);
  return { type, date: dayOf(item?.publishedAt), ...(institution ? { institution } : {}), ...(url ? { url } : {}) };
}

/** 摘录：内容短就整段；长的话从第一个命中的检索词前面一点开始截。 */
export function excerptAround(text, terms, max = 300) {
  const source = squash(text);
  if (source.length <= max) return source;
  const hay = fold(source);
  let at = -1;
  for (const term of terms) {
    const needle = fold(term);
    if (!needle) continue;
    const index = hay.indexOf(needle);
    if (index !== -1 && (at === -1 || index < at)) at = index;
  }
  if (at === -1 || at < max * 0.4) return source.slice(0, max) + '…';
  const start = Math.max(0, Math.min(at - Math.round(max * 0.25), source.length - max));
  return '…' + source.slice(start, start + max) + (start + max < source.length ? '…' : '');
}

async function eachLimit(inputs, limit, worker) {
  let next = 0;
  const run = async () => {
    while (next < inputs.length) {
      const index = next;
      next += 1;
      await worker(inputs[index]);
    }
  };
  await Promise.all(Array.from({ length: Math.max(1, Math.min(limit, inputs.length)) }, run));
}

function withTimeout(promise, ms) {
  let timer;
  const timeout = new Promise((_, reject) => {
    timer = setTimeout(() => reject(Object.assign(new Error('timeout'), { code: 'TIMEOUT' })), ms);
  });
  return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
}

const byScore = (a, b) => b.score - a.score || (Date.parse(b.entry.item.publishedAt) || 0) - (Date.parse(a.entry.item.publishedAt) || 0);

/** 先给每个来源保底几条（覆盖面：一个来源结果再多也挤不掉别的来源），剩下的名额按相关度取。结果按相关度排序。 */
function select(rows, limit) {
  /** @type {Map<string, any[]>} */
  const groups = new Map();
  for (const row of rows) {
    const key = String(row.entry.item.source);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key)?.push(row);
  }
  const lists = [...groups.values()].map((list) => list.sort(byScore)).sort((a, b) => b[0].score - a[0].score);
  const quota = Math.max(2, Math.floor(limit / Math.max(1, lists.length * 2)));
  const picked = new Set();
  for (const list of lists) for (const row of list.slice(0, quota)) if (picked.size < limit) picked.add(row);
  for (const row of [...rows].sort(byScore)) {
    if (picked.size >= limit) break;
    picked.add(row);
  }
  return [...picked].sort(byScore);
}

/**
 * 并发查询各来源，合并去重、标注命中原因、排序、截断成紧凑结果。
 * adapter.mode：semantic 每个 phrase 调一次；keyword 每个 keyword 调一次；local / pool 只调一次（自己按检索词过滤）。
 * semantic 的结果都保留（来源已经按语义判断过相关）；其余只保留直接提及或关联到相邻节点的。
 * @param {{ plan: ReturnType<typeof planResearch>, adapters: { id: string, name: string, mode: 'semantic' | 'keyword' | 'local' | 'pool', concurrency?: number, search: (input: string | null) => any }[], days?: number, limit?: number, excerptChars?: number, now?: number, timeoutMs?: number }} input
 */
export async function runResearch({ plan, adapters, days = 30, limit = 20, excerptChars = 240, now = Date.now(), timeoutMs = CALL_TIMEOUT_MS, budgetMs = BUDGET_MS }) {
  const since = now - days * DAY_MS;
  // 总时间预算：MCP 调用整体有超时，排在后面的调用剩余时间不够就不发了，记进 failed。
  const deadline = Date.now() + budgetMs;
  /** @type {Map<string, { item: any, mode: string, queries: string[], sources: Set<string> }>} */
  const found = new Map();
  /** @type {any[]} */
  const reports = adapters.map(() => null);
  /** @type {any[]} */
  const failures = adapters.map(() => null);
  await Promise.all(adapters.map(async (adapter, index) => {
    // adapter.inputs：来源自己规划的检索步骤（如 Alpha派 的公司打标 + 语义召回），每步带 label；否则按模式用 phrases / keywords。
    const inputs = Array.isArray(adapter.inputs) ? adapter.inputs : adapter.mode === 'semantic' ? plan.phrases.map((phrase) => phrase.text) : adapter.mode === 'keyword' ? plan.keywords : [null];
    if (!inputs.length) return;
    const started = Date.now();
    let ok = 0;
    let hits = 0;
    /** @type {any[]} */
    const errors = [];
    await eachLimit(inputs, adapter.concurrency ?? 2, async (input) => {
      const remaining = deadline - Date.now();
      if (remaining < 1500) {
        errors.push({ code: 'BUDGET' });
        return;
      }
      try {
        const result = await withTimeout(Promise.resolve().then(() => adapter.search(input)), Math.min(timeoutMs, remaining));
        const items = Array.isArray(result) ? result : Array.isArray(result?.items) ? result.items : [];
        ok += 1;
        const label = input && typeof input === 'object' ? String(input.label ?? '') : input;
        for (const item of items) {
          if (!item || typeof item.id !== 'string' || typeof item.title !== 'string') continue;
          hits += 1;
          const prior = found.get(item.id);
          if (!prior) {
            found.set(item.id, { item, mode: adapter.mode, queries: label ? [label] : [], sources: new Set([adapter.name]) });
            continue;
          }
          if (label && !prior.queries.includes(label)) prior.queries.push(label);
          prior.sources.add(adapter.name);
          if (MODE_RANK[adapter.mode] > MODE_RANK[prior.mode]) Object.assign(prior, { item, mode: adapter.mode });
        }
      } catch (error) {
        errors.push(error);
      }
    });
    if (ok) reports[index] = { source: adapter.name, queries: inputs.length, hits, kept: 0, ms: Date.now() - started };
    if (errors.length) {
      const code = errors[0]?.code;
      failures[index] = { source: adapter.name, reason: REASONS[code] ?? '调用失败（' + String(code ?? '未知错误').slice(0, 40) + '）', failed: errors.length, of: inputs.length };
    }
  }));
  // 同一来源、同一天、同标题的视为同一份资料（不同接口各返回一次，或同一条点评的修订版）：合并，留正文长的。
  /** @type {Map<string, any>} */
  const byTitle = new Map();
  for (const entry of [...found.values()]) {
    const key = String(entry.item.source) + '|' + fold(squash(entry.item.title)) + '|' + dayOf(entry.item.publishedAt);
    const prior = byTitle.get(key);
    if (!prior) {
      byTitle.set(key, entry);
      continue;
    }
    for (const query of entry.queries) if (!prior.queries.includes(query)) prior.queries.push(query);
    for (const name of entry.sources) prior.sources.add(name);
    if (String(entry.item.content ?? '').length > String(prior.item.content ?? '').length) prior.item = { ...entry.item, stocks: entry.item.stocks ?? prior.item.stocks };
    else if (!prior.item.stocks && entry.item.stocks) prior.item = { ...prior.item, stocks: entry.item.stocks };
    if (MODE_RANK[entry.mode] > MODE_RANK[prior.mode]) prior.mode = entry.mode;
    found.delete(entry.item.id);
  }
  const rows = [];
  /** @type {Map<string, number>} 按来源统计：早于时间窗、没列出的条数。 */
  const older = new Map();
  for (const entry of found.values()) {
    const verdict = assess(entry, plan);
    if (entry.mode !== 'semantic' && !verdict.direct && !verdict.related) continue;
    const ts = Date.parse(entry.item.publishedAt);
    if (entry.mode !== 'local' && Number.isFinite(ts) && ts < since - DAY_MS) {
      for (const name of entry.sources) older.set(name, (older.get(name) ?? 0) + 1);
      continue;
    }
    const age = Number.isFinite(ts) ? Math.max(0, (now - ts) / DAY_MS) : days;
    const recency = Math.max(0, 1 - age / Math.max(7, days));
    const base = verdict.direct ? 3 : verdict.related ? 1.6 : entry.mode === 'semantic' ? 1.2 : 0.5;
    const focus = verdict.titleHit ? 1 : verdict.titleRelated ? 0.5 : 0;
    const echo = entry.sources.size > 1 || entry.queries.length > 1 ? 0.3 : 0;
    rows.push({ entry, verdict, score: base + focus + (plan.subject ? verdict.coverage * 2 : 0) + recency + echo });
  }
  /** @type {Record<string, number>} */
  const bySource = {};
  for (const row of rows) bySource[row.entry.item.source] = (bySource[row.entry.item.source] ?? 0) + 1;
  const picked = select(rows, limit);
  for (const report of reports) {
    if (!report) continue;
    report.kept = rows.filter((row) => row.entry.sources.has(report.source)).length;
    if (older.get(report.source)) report.older = older.get(report.source);
  }
  const focus = [...plan.tokens, ...plan.matchCore.map((item) => item.term), ...(plan.subject ? [] : [plan.query]), ...plan.related.map((item) => item.term)];
  const items = picked.map((row) => {
    const item = row.entry.item;
    const content = squash(item.content || item.summary || '');
    const excerpt = excerptAround(content, focus, excerptChars);
    return {
      id: item.id,
      source: String(item.source),
      title: squash(item.title).slice(0, 120),
      ...itemFacts(item),
      ...(typeof item.display === 'string' && item.display ? { file: item.display } : {}),
      match: row.verdict.label,
      ...(row.verdict.topicHits.length ? { topic: row.verdict.topicHits } : {}),
      ...(row.entry.queries[0] ? { found_by: row.entry.queries[0] } : {}),
      excerpt,
      ...(content.length > excerpt.length + 40 || item.readWithTool || item.preview ? { more: true } : {}),
      ...(item.preview ? { preview: true } : {}),
    };
  });
  return {
    searched: reports.filter(Boolean),
    failed: failures.filter(Boolean),
    total: rows.length,
    by_source: bySource,
    items,
    /** 选中条目的完整对象：给 research_read 缓存用，不返回给模型。 */
    full: picked.map((row) => row.entry.item),
  };
}

/**
 * Alpha派 怎么查（不用别名）：
 * - 公司主体：用 Alpha派 自己的公司打标，按股票代码取点评、社媒、纪要、研报、公告；打标覆盖不到的类型（官方路演、美股业绩会、指标、基金报告）
 *   或者有话题时，再按「公司名 + 话题」语义召回一次。
 * - 环节 / 产品 / 概念节点、自由文本：只用本名（+ 话题）语义召回。
 * - 发散时，相邻节点各语义召回一次。
 * types 为 null 时用默认：打标用 defaultTagged，召回用 defaultRecall。
 * @param {ReturnType<typeof planResearch>} plan
 * @param {{ types: string[] | null, taggedTypes: readonly string[], defaultTagged: readonly string[], defaultRecall: readonly string[] }} options
 * @returns {{ kind: 'tagged' | 'recall', label: string, symbol?: string, query?: string, types: string[] }[]}
 */
export function alphapaiPlan(plan, { types, taggedTypes, defaultTagged, defaultRecall }) {
  const ticker = plan.subject?.type === 'company' ? (plan.subject.tickers ?? []).map(String).find((code) => /^\d{6}\.(SH|SZ|BJ)$/.test(code)) ?? null : null;
  const main = plan.matchCore.find((item) => item.kind === 'name')?.term ?? squash(plan.subject?.title ?? '');
  const recallTypes = types ?? [...defaultRecall];
  const tagTypes = (types ?? [...defaultTagged]).filter((type) => taggedTypes.includes(type));
  const untagged = (types ?? []).filter((type) => !taggedTypes.includes(type));
  /** @type {{ kind: 'tagged' | 'recall', label: string, symbol?: string, query?: string, types: string[] }[]} */
  const steps = [];
  const recall = (query, stepTypes) => {
    const text = squash(query).slice(0, 160);
    if (text && stepTypes.length) steps.push({ kind: 'recall', label: text, query: text, types: stepTypes });
  };
  if (ticker) {
    if (tagTypes.length) steps.push({ kind: 'tagged', label: '公司打标 ' + ticker, symbol: ticker, types: tagTypes });
    if (plan.topic) recall(main + ' ' + plan.topic, recallTypes);
    else recall(main, untagged);
  } else if (plan.subject && main) {
    recall(plan.topic ? main + ' ' + plan.topic : main, recallTypes);
  } else if (plan.query) {
    recall(plan.query, recallTypes);
  }
  for (const phrase of plan.phrases) if (phrase.kind === 'related') recall(phrase.text, recallTypes);
  return steps.filter((step, index) => steps.findIndex((other) => other.label === step.label) === index);
}

/** 下一步提示：没结果怎么放宽、怎么发散、怎么读全文、覆盖面缺口。 */
export function researchHints(plan, result) {
  const hints = [];
  if (!result.items.length) hints.push('没有检索到：换更宽的词，把 days 放宽到 90 或 365，或者先用 wiki_neighbors 找到上下游节点再分别检索。没有召回不等于没有发生。');
  const chain = Object.entries(plan.map);
  if (!plan.neighbors && chain.length) {
    hints.push('发散：neighbors=true 会把相邻节点一起检索（' + chain.slice(0, 4).map(([relation, nodes]) => relation + ' ' + nodes.slice(0, 2).join('、')).join('；') + '），也可以对单个节点再调本工具。');
  }
  const older = result.searched.filter((entry) => entry.older);
  if (older.length) hints.push('有结果早于时间窗没有列出（' + older.map((entry) => entry.source + ' ' + entry.older + ' 条').join('、') + '）；需要更早的资料就放宽 days。');
  if (result.items.some((item) => item.more)) hints.push('需要全文时用 research_read 传 id（一次最多 8 条）。');
  if (result.failed.length) hints.push('有来源这次没查成（见 failed），回答时说明覆盖面。');
  return hints;
}
