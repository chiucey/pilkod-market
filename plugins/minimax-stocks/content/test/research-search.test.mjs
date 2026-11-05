import assert from 'node:assert/strict';
import test from 'node:test';
import { alphapaiPlan, excerptAround, neighborMap, pickNeighbors, planResearch, researchHints, runResearch, topicTokens } from '../miniapp/node/research-search.mjs';
import { assembleFeed } from '../miniapp/node/search-terms.mjs';

const PROFILE = {
  subject: { id: '新易盛', title: '新易盛', type: 'company', tickers: ['300502.SZ'] },
  core: [
    { term: '新易盛', kind: 'name', label: '公司名' },
    { term: 'Eoptolink', kind: 'alias', label: '别名' },
    { term: '新易盛通信', kind: 'alias', label: '别名' },
    { term: '300502', kind: 'code', label: '代码' },
  ],
  related: [
    { term: '光模块', node: '光模块', relation: '所属环节', label: '光模块（所属环节）' },
    { term: '800G 光模块', node: '800G 光模块', relation: '产品', label: '800G 光模块（产品）' },
    { term: '中际旭创', node: '中际旭创', relation: '竞争对手', label: '中际旭创（竞争对手）' },
    { term: '英伟达', node: '英伟达', relation: '客户', label: '英伟达（客户）' },
    { term: 'NVIDIA', node: '英伟达', relation: '客户', label: '英伟达（客户）' },
    { term: '光芯片', node: '光芯片', relation: '上游', label: '光芯片（上游）' },
  ],
};

test('plan: subject names and aliases are searched together; the rest of the query is the topic', () => {
  const plan = planResearch({ query: 'eoptolink 1.6T 出货', profile: PROFILE });
  assert.equal(plan.topic, '1.6T 出货');
  assert.deepEqual(plan.tokens, ['1.6T', '出货']);
  assert.deepEqual(plan.phrases.map((phrase) => phrase.text), ['新易盛 1.6T 出货', 'Eoptolink 1.6T 出货']);
  assert.deepEqual(plan.keywords, ['新易盛', 'Eoptolink'], '关键词来源不拼话题；包含公司名的别名不单独检索');
  assert.deepEqual(plan.related, []);
  assert.deepEqual(plan.map, { 所属环节: ['光模块'], 产品: ['800G 光模块'], 竞争对手: ['中际旭创'], 客户: ['英伟达'], 上游: ['光芯片'] });

  const wide = planResearch({ query: '', profile: PROFILE, neighbors: true });
  assert.equal(wide.topic, '');
  assert.deepEqual(wide.phrases.map((phrase) => phrase.text), ['新易盛', 'Eoptolink', '光模块', '光芯片', '英伟达', '中际旭创']);
  assert.equal(wide.related.length, PROFILE.related.length);

  const narrow = planResearch({ query: '新易盛', profile: PROFILE, expand: false });
  assert.deepEqual(narrow.phrases.map((phrase) => phrase.text), ['新易盛']);
  assert.equal(narrow.matchCore.length, 4, '不检索别名时也用别名判断直接提及');

  const free = planResearch({ query: '北美云厂商 资本开支', profile: { subject: null, core: [], related: [] } });
  assert.equal(free.subject, null);
  assert.deepEqual(free.phrases.map((phrase) => phrase.text), ['北美云厂商 资本开支']);
  assert.deepEqual(free.tokens, ['北美云厂商', '资本开支']);
});

test('neighbor picks rotate across directions; tokens drop generic words', () => {
  const picks = pickNeighbors([
    { term: 'A', node: 'A', relation: '所属环节' }, { term: 'B', node: 'B', relation: '产品' },
    { term: 'C', node: 'C', relation: '供应商' }, { term: 'D', node: 'D', relation: '客户' }, { term: 'd', node: 'D', relation: '客户' },
  ], 3);
  assert.deepEqual(picks.map((item) => item.term), ['A', 'C', 'D']);
  assert.deepEqual(neighborMap([{ term: 'x', node: 'X', relation: '客户' }]), {}, '别名不进地图');
  assert.deepEqual(topicTokens('光模块 需求 与 AI、DSP'), ['光模块', 'AI', 'DSP']);
});

test('run: parallel sources, dedupe, match labels, time window, failures noted, silent when absent', async () => {
  const now = Date.parse('2026-10-27T12:00:00+08:00');
  const plan = planResearch({ query: '1.6T', profile: PROFILE, neighbors: true });
  const calls = [];
  const item = (id, source, title, content, date) => ({ id, source, title, summary: content.slice(0, 50), content, publishedAt: date + 'T10:00:00+08:00', tags: [] });
  const adapters = [
    {
      id: 'alphapai', name: 'Alpha派', mode: 'semantic',
      search: async (phrase) => {
        calls.push(['alphapai', phrase]);
        if (phrase === '新易盛 1.6T') return [item('a1', 'Alpha派', '新易盛 1.6T 订单', '新易盛 1.6T 订单落地', '2026-10-25'), item('a-old', 'Alpha派', '旧闻', '新易盛 去年', '2026-06-01')];
        if (phrase === 'Eoptolink 1.6T') return [item('a1', 'Alpha派', '新易盛 1.6T 订单', '新易盛 1.6T 订单落地', '2026-10-25'), item('a2', 'Alpha派', 'Eoptolink 1.6T ramp', 'Eoptolink 1.6T shipments', '2026-10-24')];
        if (phrase === '光芯片') return [item('a3', 'Alpha派', 'EML 涨价', '光芯片 EML 供不应求', '2026-10-23')];
        return [];
      },
    },
    { id: 'zsxq', name: '知识星球', mode: 'keyword', search: async (term) => { calls.push(['zsxq', term]); return term === '新易盛' ? [item('z1', '知识星球', '新易盛 调研', '新易盛 1.6T 良率', '2026-10-22'), item('z2', '知识星球', '不相关', '别的公司', '2026-10-22')] : []; } },
    { id: 'comein', name: '进门财经', mode: 'semantic', search: async () => { throw Object.assign(new Error('x'), { code: 'TIMEOUT' }); } },
    { id: 'feed', name: '行情页已抓取的舆情', mode: 'pool', search: () => [item('z1', '知识星球', '新易盛 调研', '新易盛 1.6T 良率', '2026-10-22'), item('p1', '进门财经', '中际旭创 点评', '中际旭创 扩产', '2026-10-21'), item('p2', '进门财经', '无关', '银行 息差', '2026-10-21')] },
    { id: 'library', name: '本地资料库', mode: 'local', search: async () => ({ items: [{ id: 'file:f:1', source: '本地资料库', title: '光模块深度', summary: '', content: '', publishedAt: '2025-01-01T00:00:00+08:00', tags: [], display: '研报/光模块深度.pdf', termHits: ['Eoptolink'], readWithTool: true }] }) },
  ];
  const result = await runResearch({ plan, adapters, days: 30, limit: 20, now });
  const byId = Object.fromEntries(result.items.map((entry) => [entry.id, entry]));
  assert.deepEqual(Object.keys(byId).sort(), ['a1', 'a2', 'a3', 'file:f:1', 'p1', 'z1']);
  assert.equal(byId.a1.match, '直接提及');
  assert.equal(byId.a2.match, '别名 Eoptolink');
  assert.equal(byId.a3.match, '关联 · 光芯片（上游）');
  assert.equal(byId.p1.match, '关联 · 中际旭创（竞争对手）');
  assert.equal(byId['file:f:1'].match, '别名 Eoptolink', '本地资料按正文命中的词判断');
  assert.equal(byId['file:f:1'].file, '研报/光模块深度.pdf');
  assert.equal(byId['file:f:1'].more, true);
  assert.equal(byId.z1.source, '知识星球');
  assert.equal(byId.z1.type, '星球帖子');
  assert.equal(byId.a1.date, '2026-10-25');
  assert.equal(result.items[0].id, 'a1', '按相关度：标题直接提及、命中话题、两个检索词都找到的排第一');
  assert.deepEqual(byId.a1.topic, ['1.6T']);
  assert.equal(byId.a3.topic, undefined);
  const alpha = result.searched.find((entry) => entry.source === 'Alpha派');
  assert.equal(alpha.older, 1, '早于时间窗的不列出，但计数');
  assert.equal(alpha.kept, 3);
  assert.equal(result.searched.find((entry) => entry.source === '知识星球').kept, 1);
  assert.match(researchHints(plan, result).join(' '), /早于时间窗没有列出（Alpha派 1 条）/);
  assert.deepEqual(result.failed, [{ source: '进门财经', reason: '超时', failed: 6, of: 6 }]);
  assert.deepEqual(result.searched.map((entry) => entry.source), ['Alpha派', '知识星球', '行情页已抓取的舆情', '本地资料库']);
  assert.equal(result.full.length, result.items.length);
  assert.ok(calls.some(([source, input]) => source === 'zsxq' && input === '光芯片'), '发散时关键词来源也查相邻节点');

  const narrow = await runResearch({ plan, adapters: adapters.slice(0, 1), limit: 2, now });
  assert.equal(narrow.items.length, 2);
  assert.equal(narrow.total, 3);

  const empty = await runResearch({ plan: planResearch({ query: '没有的东西', profile: null }), adapters: [], now });
  assert.deepEqual(empty, { searched: [], failed: [], total: 0, by_source: {}, items: [], full: [] });
  assert.match(researchHints(planResearch({ query: '没有的东西', profile: null }), empty).join(' '), /没有召回不等于没有发生/);
});

test('a slow source stops at the time budget instead of blowing the MCP timeout', async () => {
  const plan = planResearch({ query: '', profile: PROFILE, neighbors: true });
  const slow = { id: 'slow', name: '慢来源', mode: 'semantic', concurrency: 1, search: () => new Promise((resolve) => setTimeout(() => resolve([]), 300)) };
  const result = await runResearch({ plan, adapters: [slow], budgetMs: 1700 });
  assert.deepEqual(result.searched.map((entry) => [entry.source, entry.queries]), [['慢来源', plan.phrases.length]]);
  assert.equal(result.failed.length, 1);
  assert.match(result.failed[0].reason, /时间预算/);
  assert.equal(result.failed[0].failed, plan.phrases.length - 1);
});

test('selection keeps a few from every source, then fills by relevance', async () => {
  const plan = planResearch({ query: '', profile: PROFILE });
  const make = (source, count) => Array.from({ length: count }, (_, index) => ({ id: source + index, source, title: '新易盛 ' + source + index, summary: '', content: '新易盛', publishedAt: '2026-10-2' + (index % 7) + 'T10:00:00+08:00', tags: [] }));
  const adapters = [
    { id: 'a', name: 'Alpha派', mode: 'semantic', search: async () => make('Alpha派', 30) },
    { id: 'z', name: '知识星球', mode: 'keyword', search: async () => make('知识星球', 3) },
  ];
  const result = await runResearch({ plan, adapters, limit: 10, now: Date.parse('2026-10-27T12:00:00+08:00') });
  assert.equal(result.items.length, 10);
  assert.equal(result.items.filter((item) => item.source === '知识星球').length, 2, '少的来源保底 2 条');
  assert.equal(result.by_source['Alpha派'], 30);
});

test('excerpts start near the first hit', () => {
  const text = 'a'.repeat(500) + '新易盛 1.6T 订单' + 'b'.repeat(500);
  const excerpt = excerptAround(text, ['新易盛'], 100);
  assert.ok(excerpt.startsWith('…'));
  assert.ok(excerpt.includes('新易盛'));
  assert.equal(excerptAround('短文本', ['x'], 100), '短文本');
});

test('Alpha派 plan: company by its own stock tags, no aliases; recall only for topics, untagged types, nodes and neighbours', () => {
  const options = { types: null, taggedTypes: ['comment', 'social_media', 'roadShow', 'report', 'foreign_report', 'third_report', 'ann'], defaultTagged: ['comment', 'social_media', 'roadShow', 'report', 'foreign_report'], defaultRecall: ['comment', 'social_media', 'roadShow', 'roadShow_ir', 'report'] };
  const steps = (plan, extra = {}) => alphapaiPlan(plan, { ...options, ...extra }).map((step) => [step.kind, step.label, step.types.join(',')]);
  assert.deepEqual(steps(planResearch({ query: '', profile: PROFILE })), [['tagged', '公司打标 300502.SZ', 'comment,social_media,roadShow,report,foreign_report']]);
  assert.deepEqual(steps(planResearch({ query: 'Eoptolink 1.6T 出货', profile: PROFILE })), [
    ['tagged', '公司打标 300502.SZ', 'comment,social_media,roadShow,report,foreign_report'],
    ['recall', '新易盛 1.6T 出货', 'comment,social_media,roadShow,roadShow_ir,report'],
  ]);
  assert.deepEqual(steps(planResearch({ query: '', profile: PROFILE }), { types: ['ann', 'edb'] }), [['tagged', '公司打标 300502.SZ', 'ann'], ['recall', '新易盛', 'edb']]);
  const segment = { subject: { id: '光模块', title: '光模块', type: 'segment', tickers: [] }, core: [{ term: '光模块', kind: 'name', label: '公司名' }, { term: '光收发模块', kind: 'alias', label: '别名' }], related: [{ term: '光芯片', node: '光芯片', relation: '上游', label: '光芯片（上游）' }] };
  assert.deepEqual(steps(planResearch({ query: '光模块 价格', profile: segment, neighbors: true })), [['recall', '光模块 价格', 'comment,social_media,roadShow,roadShow_ir,report'], ['recall', '光芯片', 'comment,social_media,roadShow,roadShow_ir,report']]);
  assert.deepEqual(steps(planResearch({ query: '北美云厂商 资本开支', profile: null })), [['recall', '北美云厂商 资本开支', 'comment,social_media,roadShow,roadShow_ir,report']]);
  const all = JSON.stringify(alphapaiPlan(planResearch({ query: '1.6T', profile: PROFILE, neighbors: true }), options));
  assert.ok(!all.includes('Eoptolink') && !all.includes('新易盛通信'), 'Alpha派 不发别名');
});

test('tagged items count as direct mentions; same title on the same day is merged; step labels become found_by', async () => {
  const plan = planResearch({ query: '', profile: PROFILE });
  const item = (id, title, content, stocks) => ({ id, source: 'Alpha派', title, summary: '', content, publishedAt: '2026-10-26T10:00:00+08:00', tags: [], docType: '点评', ...(stocks ? { stocks } : {}) });
  const adapter = {
    id: 'alphapai', name: 'Alpha派', mode: 'keyword',
    inputs: [{ label: '公司打标 300502.SZ' }],
    search: async () => [item('t1', '易中天集体下跌', '光模块板块回调', [{ code: '300502.SZ', name: '新易盛' }]), item('t2', '易中天集体下跌', '光模块板块回调，更长的正文'), item('t3', '银行息差', '无关')],
  };
  const result = await runResearch({ plan, adapters: [adapter], now: Date.parse('2026-10-27T12:00:00+08:00') });
  assert.equal(result.items.length, 1);
  assert.equal(result.items[0].match, '公司打标');
  assert.equal(result.items[0].found_by, '公司打标 300502.SZ');
  assert.match(result.items[0].excerpt, /更长的正文/, '合并时留正文长的，标签保留');
  assert.equal(result.total, 1);
});

test('market feed: an item Alpha派 tagged with this stock is a direct mention even without the name in the text', () => {
  const profile = { symbol: '300502.SZ', core: [{ term: '新易盛', kind: 'name', label: '公司名' }], related: [] };
  const feed = assembleFeed({
    pool: [
      { id: 'p1', source: 'Alpha派', title: '易中天集体下跌', summary: '', content: '光模块板块回调', publishedAt: '2026-10-22T14:00:00+08:00', tags: [], stocks: [{ code: '300502.SZ', name: '新易盛' }] },
      { id: 'p2', source: 'Alpha派', title: '别的公司', summary: '', content: '与本公司无关', publishedAt: '2026-10-22T14:00:00+08:00', tags: [], stocks: [{ code: '600519.SH', name: '贵州茅台' }] },
    ],
    profile,
  });
  assert.deepEqual(feed.map((entry) => [entry.id, entry.match.direct, entry.match.via]), [['p1', true, 'tag']]);
});
