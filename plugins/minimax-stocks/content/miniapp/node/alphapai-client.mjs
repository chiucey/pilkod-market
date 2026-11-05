// @ts-check
// Alpha派（OpenPai）投研知识检索：用户在「数据源」页填入 API Key、校验通过后启用；没有 Key 时整个来源静默跳过。
// 只调用只读接口：健康检查 sync/auth/hello；公司打标列表（点评、社媒、纪要、研报、公告按股票代码过滤）和对应详情；投研知识检索 paipai/recall-data。
// 以公司为主体时用 Alpha派 自己的公司打标，不用别名检索；环节、话题、自由文本才用语义召回。
// Key 只保存在 Mini App 数据目录的 alphapai.json（权限 600）：不回传给页面，不写进日志和错误信息。
import { createHash } from 'node:crypto';
import { chmod, readFile, rename, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

export const ALPHAPAI_SOURCE = 'Alpha派';
const DEFAULT_BASE_URL = 'https://open-api.rabyte.cn';
const API_PREFIX = '/alpha/open-api/v1';
const OK_CODE = 200000;
const RATE_LIMITED_CODE = 42900;
const UNAUTHORIZED_CODE = 401000;
const DEFAULT_TIMEOUT_MS = 20_000;
const CONFIG_FILE = 'alphapai.json';
const DAY_MS = 86_400_000;

/** 召回类型（recallType）→ 显示名。 */
export const ALPHAPAI_TYPES = Object.freeze({
  comment: '点评', social_media: '社媒', roadShow: '纪要', roadShow_ir: '官方路演', roadShow_us: '美股业绩会',
  report: '研报', foreign_report: '外资研报', third_report: '三方研报', ann: '公告', edb: '指标', vps: '基金报告',
});
/** 语义召回的默认类型：点评、社媒、纪要、官方路演、研报。公告、指标等在统一检索里按需指定。 */
export const SENTIMENT_TYPES = Object.freeze(['comment', 'social_media', 'roadShow', 'roadShow_ir', 'report']);
/** 有公司打标（按股票代码过滤）的类型；官方路演、美股业绩会、指标、基金报告没有，只能语义召回。 */
export const TAGGED_TYPES = Object.freeze(['comment', 'social_media', 'roadShow', 'report', 'foreign_report', 'third_report', 'ann']);
/** 行情页舆情默认按公司打标取：点评、社媒、纪要、研报、外资研报。 */
export const FEED_TAGGED_TYPES = Object.freeze(['comment', 'social_media', 'roadShow', 'report', 'foreign_report']);
const PAGE_SIZE = 20;
const REPORT_PAGE_SIZE = 10;
/** 详情接口有额度（点评详情每天 100 条）：列表只给摘要的资料不自动取全文，用户或 Agent 要看时再取（detail）。 */
const QUOTA_PATTERN = /上限|额度|次数/;

/** 页面上显示的 Key：只露尾号。 */
export function maskKey(key) {
  const text = typeof key === 'string' ? key : '';
  if (!text) return '';
  return text.length <= 8 ? '•'.repeat(text.length) : '••••' + text.slice(-4);
}

/** 用户粘贴的 Key：去掉首尾空白后 8–256 个字符，中间不能有空白或控制字符。 */
export function normalizeKey(value) {
  const key = typeof value === 'string' ? value.trim() : '';
  if (key.length < 8 || key.length > 256 || /[\s\u0000-\u001f\u007f]/.test(key)) return null;
  return key;
}

/** 北京时间的日期 yyyy-MM-dd。 */
export function beijingDate(date) {
  return new Date(date.getTime() + 8 * 3_600_000).toISOString().slice(0, 10);
}

/** "2026-09-28 23:13:28" / "2026-09-28" → "2026-09-28T23:13:28+08:00"；解析不了返回 ''。 */
export function toBeijingIso(value) {
  const match = String(value ?? '').trim().match(/^(\d{4}-\d{2}-\d{2})(?:[ T](\d{2}:\d{2})(:\d{2})?)?/);
  if (!match) return '';
  const iso = match[1] + 'T' + (match[2] ? match[2] + (match[3] ?? ':00') : '00:00:00') + '+08:00';
  return Number.isFinite(Date.parse(iso)) ? iso : '';
}

/** 召回类型的显示名；接口偶尔返回枚举外的细分类型（如 us_announcement）。 */
export function typeLabel(type) {
  const key = String(type ?? '');
  if (Object.hasOwn(ALPHAPAI_TYPES, key)) return ALPHAPAI_TYPES[/** @type {keyof typeof ALPHAPAI_TYPES} */ (key)];
  if (/announce|^ann/i.test(key)) return '公告';
  if (/report/i.test(key)) return '研报';
  if (/roadshow/i.test(key)) return '纪要';
  return '资料';
}

const clean = (value) => (typeof value === 'string' ? value.replace(/\s+/g, ' ').trim() : '');
/** 网页正文转纯文本（社媒正文可能带 HTML）。 */
const stripHtml = (html) => String(html ?? '')
  .replace(/<(script|style|noscript)[\s\S]*?<\/\1>/gi, ' ')
  .replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|div|li|h[1-6]|tr|section|article)>/gi, '\n')
  .replace(/<[^>]+>/g, ' ')
  .replace(/&nbsp;/g, ' ').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&')
  .replace(/[ \t]{2,}/g, ' ');
/** 列表里的 ID 大多是有时效的加密串：用标题、时间、机构生成稳定 id，刷新后同一份资料还是同一条。 */
const stableId = (key) => createHash('sha1').update(key).digest('hex').slice(0, 16);
const tagList = (tags) => (Array.isArray(tags) ? tags : [])
  .filter((tag) => tag && typeof tag.name === 'string' && tag.name.trim())
  .slice(0, 8)
  .map((tag) => ({ code: typeof tag.code === 'string' ? tag.code : '', name: tag.name.trim() }));
const firstTag = (tags) => tagList(tags)[0]?.name ?? '';
const tagNames = (tags, max = 3) => tagList(tags).slice(0, max).map((tag) => tag.name).join('、');
const pageRows = (page) => (Array.isArray(page?.data) ? page.data : Array.isArray(page) ? page : []);
const safeHttp = (url) => {
  try {
    const parsed = new URL(String(url));
    return ['http:', 'https:'].includes(parsed.protocol) ? parsed.href : '';
  } catch {
    return '';
  }
};

/** 公司打标结果 → 舆情条目（与语义召回的条目同一形状，另带 stocks：Alpha派 打的股票标签）。 */
function makeItem({ id, key, title, content, fallback = '', publishedAt, docType, institution = '', industry = '', stocks = [], url = '', preview = false, ref = null }) {
  const body = content || fallback;
  return {
    id: 'alphapai-' + (id || stableId(key)),
    source: ALPHAPAI_SOURCE,
    title: title.slice(0, 120),
    summary: body.slice(0, 180),
    content: body,
    publishedAt,
    tags: [docType, institution, industry].filter(Boolean).slice(0, 3),
    docType,
    ...(institution ? { institution } : {}),
    ...(stocks.length ? { stocks } : {}),
    ...(url ? { url } : {}),
    // preview：列表里只有摘要（点评前 100 字，研报、纪要只有标题和机构），全文要按 ref 另取。
    ...(preview && ref ? { preview: true, ref } : {}),
  };
}

/** 同类型、同一天、同标题的视为同一份资料（点评常有修订版），留正文长的；按发布时间从新到旧。 */
export function dedupeItems(items) {
  /** @type {Map<string, any>} */
  const out = new Map();
  for (const item of items) {
    const key = item.docType + '|' + clean(item.title).toLowerCase() + '|' + String(item.publishedAt).slice(0, 10);
    const prior = out.get(key);
    if (!prior || String(item.content).length > String(prior.content).length) out.set(key, item);
  }
  return [...out.values()].sort((a, b) => (Date.parse(b.publishedAt) || 0) - (Date.parse(a.publishedAt) || 0));
}
const cleanChunk = (value) => (typeof value === 'string' ? value.replace(/\r\n?/g, '\n').replace(/[ \t]+\n/g, '\n').replace(/\n[ \t]+/g, '\n').replace(/\n{3,}/g, '\n\n').trim() : '');

/** contextInfo 形如「发布时间为: 2026-09-28 23:13:28,行业: 通信,电子,机构: ,标题: …」；标题在最后，可能含逗号。 */
function contextField(context, field) {
  if (field === 'title') return clean(context.match(/标题[:：]\s*([\s\S]*)$/)?.[1] ?? '');
  return clean(context.match(/发布时间为?[:：]\s*(\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}(?::\d{2})?)?)/)?.[1] ?? '');
}

/**
 * 召回结果 → 舆情条目（与进门财经、知识星球的条目同一形状，另带 docType、institution）。同一份资料的多个片段合并成一条。
 * @param {any[]} rows
 */
export function recallToItems(rows) {
  /** @type {Map<string, any>} */
  const out = new Map();
  for (const row of Array.isArray(rows) ? rows : []) {
    if (!row || typeof row !== 'object') continue;
    const rawId = clean(String(row.id ?? ''));
    if (!rawId) continue;
    const chunks = (Array.isArray(row.chunks) ? row.chunks : []).map(cleanChunk).filter(Boolean);
    const prior = out.get(rawId);
    if (prior) {
      const extra = chunks.filter((chunk) => !prior.content.includes(chunk));
      if (extra.length) prior.content = [prior.content, ...extra].join('\n\n');
      continue;
    }
    const context = typeof row.contextInfo === 'string' ? row.contextInfo : '';
    const content = chunks.join('\n\n');
    const title = (clean(row.title) || contextField(context, 'title') || clean(content.split('\n')[0])).slice(0, 120);
    const publishedAt = toBeijingIso(row.time) || toBeijingIso(contextField(context, 'time'));
    if (!content || !title || !publishedAt) continue;
    const label = typeLabel(row.type);
    const institution = clean(row.institution);
    const industry = clean(row.industry).split(/[,，、]/)[0]?.trim() ?? '';
    out.set(rawId, {
      id: 'alphapai-' + rawId,
      source: ALPHAPAI_SOURCE,
      title,
      summary: '',
      content,
      publishedAt,
      tags: [label, institution, industry].filter(Boolean).slice(0, 3),
      docType: label,
      ...(institution ? { institution } : {}),
    });
  }
  return [...out.values()].map((item) => ({ ...item, summary: item.content.slice(0, 180) }));
}

function codeError(code, message) {
  return Object.assign(new Error(message), { code });
}

/**
 * @param {{ dataDir: string, fetchImpl?: typeof fetch, baseUrl?: string, timeoutMs?: number, sleep?: (ms: number) => Promise<void>, log?: (code: string, fields: Record<string, unknown>) => void }} options
 */
export async function createAlphaPai({
  dataDir,
  fetchImpl = globalThis.fetch,
  baseUrl = DEFAULT_BASE_URL,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms)),
  log = () => {},
}) {
  const file = join(dataDir, CONFIG_FILE);
  /** @type {string | null} */
  let apiKey = null;
  /** @type {string | null} */
  let savedAt = null;
  try {
    const stored = JSON.parse(await readFile(file, 'utf8'));
    apiKey = normalizeKey(stored?.apiKey);
    savedAt = apiKey && typeof stored?.savedAt === 'string' ? stored.savedAt : null;
  } catch {
    apiKey = null;
  }

  /** 业务成功是 code === 200000；HTTP 200 不代表成功。错误里只带错误码和服务端的简短说明，不带 Key。 */
  async function post(path, body, key) {
    if (!key) throw codeError('ALPHAPAI_NOT_CONFIGURED', '还没有填写 Alpha派 API Key');
    let response;
    try {
      response = await fetchImpl(baseUrl + API_PREFIX + path, {
        method: 'POST',
        headers: { 'app-agent': key, 'content-type': 'application/json; charset=utf-8' },
        body: JSON.stringify(body ?? {}),
        signal: AbortSignal.timeout(timeoutMs),
      });
    } catch (error) {
      const timedOut = error?.name === 'TimeoutError' || error?.name === 'AbortError';
      throw codeError(timedOut ? 'TIMEOUT' : 'ALPHAPAI_NETWORK', timedOut ? 'Alpha派 超时没有响应' : 'Alpha派 网络不通');
    }
    const payload = await response.json().catch(() => null);
    const code = Number(payload?.code);
    if (response.status === 401 || response.status === 403 || code === UNAUTHORIZED_CODE) throw codeError('ALPHAPAI_UNAUTHORIZED', 'API Key 无效或没有权限');
    if (response.status === 429 || code === RATE_LIMITED_CODE) throw codeError('ALPHAPAI_RATE_LIMITED', 'Alpha派 调用太频繁，稍后再试');
    if (!response.ok) throw codeError('ALPHAPAI_HTTP_' + response.status, 'Alpha派 服务返回 HTTP ' + response.status);
    if (code !== OK_CODE) {
      const message = clean(String(payload?.message ?? payload?.msg ?? '')).slice(0, 120);
      if (QUOTA_PATTERN.test(message)) throw codeError('ALPHAPAI_QUOTA', 'Alpha派：' + message);
      if (/权限/.test(message)) throw codeError('ALPHAPAI_FORBIDDEN', 'Alpha派：' + message);
      throw codeError('ALPHAPAI_' + (Number.isFinite(code) ? code : 'BAD_RESPONSE'), message ? 'Alpha派：' + message : 'Alpha派 返回了无法识别的结果');
    }
    return payload.data;
  }

  async function persist(value) {
    const pending = file + '.pending';
    await writeFile(pending, JSON.stringify(value), { encoding: 'utf8', mode: 0o600 });
    await chmod(pending, 0o600);
    await rename(pending, file);
  }

  /** 业务调用：被限流（42900）时等 1.5 秒重试一次。 */
  async function call(path, body) {
    try {
      return await post(path, body, apiKey);
    } catch (error) {
      if (error?.code !== 'ALPHAPAI_RATE_LIMITED') throw error;
      await sleep(1500);
      return post(path, body, apiKey);
    }
  }

  // 研报、纪要、点评的列表 ID 是有时效的加密串：存在 ref 里，按需取全文时用；过期了就按标题重新列一次找回来。
  async function taggedComments(code, from, to) {
    const rows = pageRows(await call('/comments/list', { page: 1, pageSize: PAGE_SIZE, commentScope: 'all', startDate: from, endDate: to, stockCombSymbol: [code] }));
    return rows.map((row) => {
      const title = clean(row?.title);
      const publishedAt = toBeijingIso(row?.commentTime) || toBeijingIso(row?.updateTime);
      if (!title || !publishedAt) return null;
      const institution = firstTag(row.institutionTag);
      // 列表里的正文只有前 100 字；全文要调详情，而点评详情每天有额度（100 条），只在明确要看时取。
      return makeItem({
        key: 'comment|' + title + '|' + row.commentTime + '|' + institution, title, content: cleanChunk(stripHtml(row.content)), publishedAt,
        docType: ALPHAPAI_TYPES.comment, institution, industry: firstTag(row.industryTag), stocks: tagList(row.stockTag),
        preview: true, ref: typeof row.commentId === 'string' ? { kind: 'comment', id: row.commentId, symbol: code, title, time: clean(row.commentTime) } : null,
      });
    }).filter(Boolean);
  }

  async function taggedSocial(code, from, to) {
    const rows = pageRows(await call('/social/media/article/list', { pageNum: 1, pageSize: PAGE_SIZE, excludeContent: false, stock: [code], startDate: from, endDate: to }));
    return rows.map((row) => {
      const title = clean(row?.title);
      const publishedAt = toBeijingIso(row?.publishDate);
      if (!title || !publishedAt) return null;
      return makeItem({
        id: clean(String(row.id ?? '')), key: 'social|' + title + '|' + row.publishDate, title, content: cleanChunk(stripHtml(row.content)), publishedAt,
        docType: ALPHAPAI_TYPES.social_media, institution: clean(row.accountName), industry: firstTag(row.industry), stocks: tagList(row.stock), url: safeHttp(row.url),
      });
    }).filter(Boolean);
  }

  const REPORT_SCOPES = { report: ['domestic', ALPHAPAI_TYPES.report], foreign_report: ['foreign', ALPHAPAI_TYPES.foreign_report], third_report: ['independent', ALPHAPAI_TYPES.third_report] };
  async function taggedReports(code, type, from, to) {
    const [scope, docType] = REPORT_SCOPES[type];
    const rows = pageRows(await call('/report/list', { page: 1, pageSize: REPORT_PAGE_SIZE, reportScope: scope, stockCombSymbol: [code], startDate: from, endDate: to }));
    return rows.map((row) => {
      const original = clean(row?.title);
      const title = clean(row?.titleCn) || original;
      const publishedAt = toBeijingIso(row?.reportTime);
      if (!title || !publishedAt) return null;
      const institution = firstTag(row.institutionTag);
      const authors = tagNames(row.analystTag) || tagNames(row.authorTag);
      const fallback = [original && original !== title ? original : '', [clean(row.reportTypeLabel), institution, authors].filter(Boolean).join(' · ')].filter(Boolean).join('\n');
      return makeItem({
        key: 'report|' + scope + '|' + original + '|' + row.reportTime + '|' + institution, title, content: '', fallback, publishedAt,
        docType, institution, industry: firstTag(row.industryTag), stocks: tagList(row.stockTag),
        preview: true, ref: typeof row.reportId === 'string' ? { kind: 'report', id: row.reportId, symbol: code, scope, title: original, time: clean(row.reportTime) } : null,
      });
    }).filter(Boolean);
  }

  async function taggedMinutes(code, from, to) {
    const rows = pageRows(await call('/summary/list', { meetingMarketType: 'A', pageNum: 1, pageSize: REPORT_PAGE_SIZE, stockCombSymbol: [code], beginTime: from + ' 00:00:00', endTime: to + ' 23:59:59' }));
    return rows.map((row) => {
      const title = clean(row?.title);
      const publishedAt = toBeijingIso(row?.publishTime) || toBeijingIso(row?.meetingTime);
      if (!title || !publishedAt) return null;
      const institution = firstTag(row.institutionTag);
      const guests = tagNames(row.guestTag);
      const fallback = [tagNames(row.meetingContentType), institution, guests ? '嘉宾：' + guests : ''].filter(Boolean).join(' · ');
      const readable = typeof row.roadshowId === 'string' && Array.isArray(row.availableNoteTypes) && row.availableNoteTypes.includes('ai_note');
      return makeItem({
        key: 'minutes|' + title + '|' + (row.publishTime ?? row.meetingTime), title, content: '', fallback, publishedAt,
        docType: ALPHAPAI_TYPES.roadShow, institution, industry: firstTag(row.industryTag), stocks: tagList(row.stockTag),
        preview: true, ref: readable ? { kind: 'minutes', id: row.roadshowId, symbol: code, title, time: clean(row.publishTime ?? row.meetingTime) } : null,
      });
    }).filter(Boolean);
  }

  async function taggedAnnouncements(code, from, to) {
    const rows = pageRows(await call('/announcement/list', { pageNum: 1, pageSize: PAGE_SIZE, stockCode: [code], publishFrom: from, publishTo: to, sortBy: 'actual_publish_time', sortOrder: 'desc' }));
    return rows.map((row) => {
      const title = clean(row?.title);
      const publishedAt = toBeijingIso(row?.actualPublishTime) || toBeijingIso(row?.publishTime);
      if (!title || !publishedAt) return null;
      return makeItem({
        key: 'ann|' + title + '|' + (row.publishTime ?? ''), title, content: '', fallback: clean(row.announcementType) ? '公告类型：' + clean(row.announcementType) : '', publishedAt,
        docType: ALPHAPAI_TYPES.ann, industry: firstTag(row.industryTag), stocks: tagList(row.stockTag),
      });
    }).filter(Boolean);
  }

  /** 按 ref 取一次全文。 */
  async function detailOnce(ref, id) {
    if (ref.kind === 'comment') {
      const row = pageRows(await call('/comments/detail', { commentId: [id] }))[0];
      return cleanChunk(stripHtml(row?.content ?? ''));
    }
    if (ref.kind === 'report') {
      const data = await call('/report/detail', { reportId: id });
      return cleanChunk(stripHtml(data?.contentCn || data?.content || data?.summary || data?.fullContentCn || data?.fullContent || ''));
    }
    if (ref.kind === 'minutes') {
      const data = await call('/summary/detail', { roadshowId: id, noteType: 'ai_note' });
      return cleanChunk(stripHtml(data?.content || data?.markdownContent || data?.aiContent || ''));
    }
    return '';
  }

  /** 列表 ID 过期时：重新列出同一天、同一只股票的资料，按标题（和时间）找回同一条的新 ID。 */
  async function relist(ref) {
    const date = String(ref.time ?? '').slice(0, 10);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date) || !ref.symbol) return null;
    if (ref.kind === 'comment') {
      const rows = pageRows(await call('/comments/list', { page: 1, pageSize: 50, commentScope: 'all', startDate: date, endDate: date, stockCombSymbol: [ref.symbol] }));
      return rows.find((row) => clean(row?.title) === ref.title && clean(row?.commentTime) === ref.time)?.commentId ?? null;
    }
    if (ref.kind === 'report') {
      const rows = pageRows(await call('/report/list', { page: 1, pageSize: 20, reportScope: ref.scope ?? 'domestic', stockCombSymbol: [ref.symbol], startDate: date, endDate: date }));
      return rows.find((row) => clean(row?.title) === ref.title)?.reportId ?? null;
    }
    if (ref.kind === 'minutes') {
      const rows = pageRows(await call('/summary/list', { meetingMarketType: 'A', pageNum: 1, pageSize: 20, stockCombSymbol: [ref.symbol], beginTime: date + ' 00:00:00', endTime: date + ' 23:59:59' }));
      return rows.find((row) => clean(row?.title) === ref.title)?.roadshowId ?? null;
    }
    return null;
  }

  const status = () => ({ configured: apiKey !== null, masked: maskKey(apiKey), length: apiKey?.length ?? 0, savedAt });

  return {
    get configured() { return apiKey !== null; },
    status,
    /** 健康检查：验证连通性与鉴权。 */
    async hello() {
      await post('/sync/auth/hello', {}, apiKey);
      return true;
    },
    /** 先用这个 Key 调一次健康检查，通过了才保存（替换旧 Key）。 */
    async saveKey(value) {
      const key = normalizeKey(value);
      if (!key) throw codeError('ALPHAPAI_KEY_FORMAT', 'API Key 格式不对：应为 8–256 个字符，不含空格');
      await post('/sync/auth/hello', {}, key);
      const at = new Date().toISOString();
      await persist({ apiKey: key, savedAt: at });
      apiKey = key;
      savedAt = at;
      return status();
    },
    /** 清除 Key：配置文件改写成空，不删除文件。 */
    async clearKey() {
      apiKey = null;
      savedAt = null;
      await persist({ apiKey: null, clearedAt: new Date().toISOString() });
    },
    /**
     * 投研知识检索（语义召回）。时间按资料发布时间，默认最近 30 天；被限流（42900）时等 1.5 秒重试一次。
     * @param {{ query: string, types?: readonly string[], days?: number, now?: Date }} input
     */
    async recall({ query, types = SENTIMENT_TYPES, days = 30, now = new Date() }) {
      const q = clean(String(query ?? '')).slice(0, 200);
      if (!q) return [];
      const wanted = [...new Set((Array.isArray(types) ? types : []).filter((type) => typeof type === 'string' && Object.hasOwn(ALPHAPAI_TYPES, type)))];
      const span = Math.max(1, Math.min(3650, Math.round(Number(days) || 30)));
      const body = {
        query: q,
        recallType: wanted.length ? wanted : [...SENTIMENT_TYPES],
        isCutOff: true,
        startTime: beijingDate(new Date(now.getTime() - span * DAY_MS)),
        endTime: beijingDate(now),
      };
      let data;
      try {
        data = await post('/paipai/recall-data', body, apiKey);
      } catch (error) {
        if (error?.code !== 'ALPHAPAI_RATE_LIMITED') throw error;
        await sleep(1500);
        data = await post('/paipai/recall-data', body, apiKey);
      }
      return recallToItems(Array.isArray(data) ? data : []);
    },
    /**
     * 按 Alpha派 的公司打标取资料（按股票代码过滤，不用别名）：点评、社媒、纪要、研报、外资 / 三方研报、公告。
     * 只调列表接口：社媒有全文；点评只有前 100 字，研报、纪要只有标题和机构（preview，全文用 detail 按需取）。部分接口失败时返回其余的，全部失败才报错。
     * days 用于点评、社媒、公告；longDays 用于研报、纪要（更新慢，默认同 days）。
     * @param {{ symbol: string, types?: readonly string[], days?: number, longDays?: number, now?: Date }} input
     */
    async tagged({ symbol, types = FEED_TAGGED_TYPES, days = 30, longDays = days, now = new Date() }) {
      const code = String(symbol ?? '').trim().toUpperCase();
      if (!/^\d{6}\.(SH|SZ|BJ)$/.test(code)) return [];
      const span = (value) => Math.max(1, Math.min(3650, Math.round(Number(value) || 30)));
      const to = beijingDate(now);
      const from = beijingDate(new Date(now.getTime() - span(days) * DAY_MS));
      const longFrom = beijingDate(new Date(now.getTime() - Math.max(span(days), span(longDays)) * DAY_MS));
      const wanted = new Set((Array.isArray(types) ? types : []).filter((type) => TAGGED_TYPES.includes(type)));
      const jobs = [];
      if (wanted.has('comment')) jobs.push(taggedComments(code, from, to));
      if (wanted.has('social_media')) jobs.push(taggedSocial(code, from, to));
      if (wanted.has('roadShow')) jobs.push(taggedMinutes(code, longFrom, to));
      for (const type of ['report', 'foreign_report', 'third_report']) if (wanted.has(type)) jobs.push(taggedReports(code, type, longFrom, to));
      if (wanted.has('ann')) jobs.push(taggedAnnouncements(code, from, to));
      if (!jobs.length) return [];
      const settled = await Promise.allSettled(jobs);
      const failed = settled.filter((result) => result.status === 'rejected');
      if (failed.length === settled.length) throw /** @type {PromiseRejectedResult} */ (failed[0]).reason;
      return dedupeItems(settled.flatMap((result) => (result.status === 'fulfilled' ? result.value : [])));
    },
    /**
     * 按需取全文（item.preview 且带 ref 的点评、研报、纪要）。列表 ID 过期时按标题重新列一次再取。
     * 额度用完（ALPHAPAI_QUOTA）、没有权限（ALPHAPAI_FORBIDDEN）、Key 失效、限流、网络问题直接报错，不重找。
     * @param {{ ref?: { kind: string, id: string, symbol?: string, scope?: string, title?: string, time?: string } | null }} item
     */
    async detail(item) {
      const ref = item?.ref;
      if (!ref || typeof ref.id !== 'string' || !['comment', 'report', 'minutes'].includes(ref.kind)) throw codeError('ALPHAPAI_NO_DETAIL', '这条资料没有可以另取的全文');
      const final = new Set(['ALPHAPAI_QUOTA', 'ALPHAPAI_FORBIDDEN', 'ALPHAPAI_UNAUTHORIZED', 'ALPHAPAI_NOT_CONFIGURED', 'ALPHAPAI_RATE_LIMITED', 'ALPHAPAI_NETWORK', 'TIMEOUT']);
      let text = '';
      try {
        text = await detailOnce(ref, ref.id);
      } catch (error) {
        if (final.has(error?.code)) throw error;
        log('alphapai_detail_retry', { kind: ref.kind, code: String(error?.code ?? 'UNKNOWN') });
      }
      if (!text) {
        const fresh = await relist(ref);
        if (fresh && fresh !== ref.id) text = await detailOnce(ref, fresh);
      }
      if (!text) throw codeError('ALPHAPAI_EMPTY', 'Alpha派 没有返回这份资料的全文');
      return text;
    },
  };
}
