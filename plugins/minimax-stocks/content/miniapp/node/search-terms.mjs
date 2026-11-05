// @ts-check
// 用知识图谱扩大检索：公司的名称、别名、代码算「直接提及」，相邻节点（所属环节、产品、客户、供应商、竞争对手……）
// 的名称和别名算「关联」。行情页的舆情、纪要和搜索框都用这里的字符串匹配；只做包含匹配，不做语义判断。

/** 太泛、会误匹配一大片的词，不当检索词。 */
const GENERIC = new Set([
  '公司', '行业', '市场', '产品', '技术', '业务', '客户', '供应商', '其他', '国内', '海外', '中国', '全球', '美国',
  'a股', '港股', '美股', '龙头', '厂商', '企业', '集团', '上游', '中游', '下游', '产业链', '概念', '板块', '政策', '需求', '供给',
]);

export const fold = (text) => String(text ?? '').normalize('NFKC').toLowerCase();
const isCjk = (text) => /[\u3400-\u9fff]/.test(text);

/** 能不能当检索词：中文至少 2 个字，英文 / 数字至少 3 个字符；纯股票代码另算，泛词不要。 */
export function usableTerm(term) {
  const text = String(term ?? '').trim();
  if (!text || text.length > 40) return false;
  if (/^\d{6}(\.(sh|sz|bj))?$/i.test(text)) return false;
  if (GENERIC.has(fold(text))) return false;
  return isCjk(text) ? text.length >= 2 : text.replace(/[^a-z0-9]/gi, '').length >= 3;
}

/** 从公司这一侧看关系：out 是公司页上的关系，in 是别的页面指向公司的关系。 */
export const RELATION_LABELS = {
  out: { belongs_to: '所属环节', produces: '产品', supplies: '客户', upstream_of: '下游环节', competes: '竞争对手', substitutes: '替代', drives: '影响', related: '相关' },
  in: { supplies: '供应商', upstream_of: '上游', competes: '竞争对手', substitutes: '替代', drives: '驱动因素', related: '相关', produces: '生产方' },
};
/** 相邻节点的排序：越靠前越重要。待核关系排在同类确认关系之后。 */
export const RELATION_PRIORITY = { 所属环节: 1, 产品: 2, 竞争对手: 3, 客户: 4, 供应商: 5, 上游: 6, 下游环节: 6, 替代: 7, 驱动因素: 8, 影响: 8, 生产方: 8, 相关: 9 };

/**
 * 在一段文字里找检索词。core 命中算直接提及；只命中 related 算关联。
 * @param {string} text
 * @param {{ core: { term: string, kind: string, label: string }[], related: { term: string, label: string, node?: string }[] }} profile
 */
export function matchProfile(text, profile) {
  const hay = fold(text);
  const core = profile.core.filter((item) => hay.includes(fold(item.term)));
  const related = profile.related.filter((item) => hay.includes(fold(item.term)));
  return { direct: core.length > 0, core, related };
}

/** 页面上显示的一句话：直接提及显示命中的叫法，关联显示节点和关系。 */
export function matchLabels(match, limit = 3) {
  if (match.core.length) return match.core.slice(0, limit).map((item) => (item.kind === 'name' ? item.term : item.label + ' ' + item.term));
  const seen = new Set();
  const out = [];
  for (const item of match.related) {
    if (seen.has(item.label)) continue;
    seen.add(item.label);
    out.push(item.label);
    if (out.length >= limit) break;
  }
  return out;
}

/**
 * 组装一只股票的舆情列表。own：按名称直接检索到的（一律保留）；expanded：用别名 / 相邻节点额外检索到的；
 * pool：其他股票的舆情。后两类只保留文字里确实出现了检索词的，按命中情况标 match。
 * @param {{ own?: any[], expanded?: any[], pool?: any[], profile: any, limit?: number }} input
 */
export function assembleFeed({ own = [], expanded = [], pool = [], profile, limit = 120 }) {
  /** @type {Map<string, any>} */
  const out = new Map();
  const take = (item, origin) => {
    if (!item || typeof item.id !== 'string' || out.has(item.id)) return;
    const match = matchProfile([item.title, item.summary, item.content, ...(Array.isArray(item.tags) ? item.tags : [])].join(' '), profile);
    // 来源自己打了股票标签（Alpha派）：标在这只股票上的算直接提及，正文里不一定出现公司名。
    const tagged = Boolean(profile.symbol) && Array.isArray(item.stocks) && item.stocks.some((stock) => stock && stock.code === profile.symbol);
    if (origin !== 'own' && !tagged && !match.direct && !match.related.length) return;
    const via = tagged ? 'tag' : match.direct ? match.core[0].kind : origin === 'own' ? 'search' : 'related';
    out.set(item.id, { ...item, match: { direct: tagged || match.direct || origin === 'own', via, terms: via === 'search' || via === 'tag' ? [] : matchLabels(match) } });
  };
  for (const item of own) take(item, 'own');
  for (const item of expanded) take(item, 'term');
  for (const item of pool) take(item, 'pool');
  return [...out.values()].sort((a, b) => String(b.publishedAt).localeCompare(String(a.publishedAt))).slice(0, limit);
}
