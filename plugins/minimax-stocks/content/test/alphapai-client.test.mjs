import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { ALPHAPAI_SOURCE, createAlphaPai, maskKey, normalizeKey, recallToItems, toBeijingIso } from '../miniapp/node/alphapai-client.mjs';

const KEY = 'test-key-0123456789abcd';

/** 假的 Alpha派 服务：按路径返回预设响应，记下每次请求（含请求头）。 */
function fakeFetch(handlers) {
  const calls = [];
  const fetchImpl = async (url, init) => {
    const path = new URL(url).pathname;
    calls.push({ path, headers: init.headers, body: JSON.parse(init.body) });
    const handler = handlers[path];
    const reply = typeof handler === 'function' ? handler(calls.length) : handler;
    const { status = 200, body } = reply ?? { status: 404, body: {} };
    return new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });
  };
  return { fetchImpl, calls };
}

test('recall rows map to sentiment items: Beijing time, type labels, merged chunks', () => {
  const items = recallToItems([
    { id: 'C1', type: 'comment', contextInfo: '发布时间为: 2026-09-28 23:13:28,行业: 通信,电子,机构: ,标题: 光模块法案影响有限, 政策仍有变数', chunks: ['第一段', '第二段'], title: '', time: '', industry: '通信,电子', institution: '' },
    { id: 'C1', chunks: ['第三段', '第一段'] },
    { id: 'R1', type: 'report', chunks: ['研报正文'], title: '新易盛深度', time: '2026-10-01', industry: '通信', institution: '广发证券' },
    { id: 'U1', type: 'us_announcement', chunks: ['公告正文'], title: '美股公告', time: '2026-10-02 08:00:00' },
    { id: 'X1', type: 'report', chunks: [], title: '没有正文', time: '2026-10-01' },
    { id: '', chunks: ['没有 id'], title: 't', time: '2026-10-01' },
  ]);
  assert.equal(items.length, 3);
  const [comment, report, ann] = items;
  assert.equal(comment.id, 'alphapai-C1');
  assert.equal(comment.source, ALPHAPAI_SOURCE);
  assert.equal(comment.title, '光模块法案影响有限, 政策仍有变数');
  assert.equal(comment.publishedAt, '2026-09-28T23:13:28+08:00');
  assert.equal(comment.content, '第一段\n\n第二段\n\n第三段');
  assert.deepEqual(comment.tags, ['点评', '通信']);
  assert.equal(report.docType, '研报');
  assert.equal(report.institution, '广发证券');
  assert.deepEqual(report.tags, ['研报', '广发证券', '通信']);
  assert.equal(report.publishedAt, '2026-10-01T00:00:00+08:00');
  assert.equal(ann.docType, '公告');
  assert.equal(toBeijingIso('not a date'), '');
  assert.equal(maskKey(KEY), '••••abcd');
  assert.equal(normalizeKey(' short '), null);
  assert.equal(normalizeKey('has space inside'), null);
  assert.equal(normalizeKey('  ' + KEY + '\n'), KEY);
});

test('API key: validated before saving, stored with mode 600, never echoed; cleared on demand', async () => {
  const dataDir = await mkdtemp(join(tmpdir(), 'alphapai-'));
  try {
    const rejected = fakeFetch({ '/alpha/open-api/v1/sync/auth/hello': { status: 401, body: { msg: '无权访问', code: 401000 } } });
    const first = await createAlphaPai({ dataDir, fetchImpl: rejected.fetchImpl });
    assert.equal(first.configured, false);
    await assert.rejects(first.saveKey('bad key'), (error) => error.code === 'ALPHAPAI_KEY_FORMAT');
    assert.equal(rejected.calls.length, 0, '格式不对时不发请求');
    await assert.rejects(first.saveKey(KEY), (error) => error.code === 'ALPHAPAI_UNAUTHORIZED' && !String(error.message).includes(KEY));
    assert.equal(first.configured, false);
    await assert.rejects(stat(join(dataDir, 'alphapai.json')), { code: 'ENOENT' });

    const ok = fakeFetch({ '/alpha/open-api/v1/sync/auth/hello': { body: { code: 200000, message: 'success', data: 'success' } } });
    const second = await createAlphaPai({ dataDir, fetchImpl: ok.fetchImpl });
    const status = await second.saveKey('  ' + KEY + '  ');
    assert.equal(ok.calls[0].headers['app-agent'], KEY);
    assert.deepEqual(status, { configured: true, masked: '••••abcd', length: KEY.length, savedAt: status.savedAt });
    assert.equal(JSON.stringify(second.status()).includes(KEY), false);
    const info = await stat(join(dataDir, 'alphapai.json'));
    assert.equal(info.mode & 0o777, 0o600);
    const reloaded = await createAlphaPai({ dataDir, fetchImpl: ok.fetchImpl });
    assert.equal(reloaded.configured, true);
    assert.equal(await reloaded.hello(), true);

    await reloaded.clearKey();
    assert.equal(reloaded.configured, false);
    assert.equal(JSON.parse(await readFile(join(dataDir, 'alphapai.json'), 'utf8')).apiKey, null);
    assert.equal((await createAlphaPai({ dataDir, fetchImpl: ok.fetchImpl })).configured, false);
    await assert.rejects(reloaded.recall({ query: '新易盛' }), (error) => error.code === 'ALPHAPAI_NOT_CONFIGURED');
  } finally {
    await rm(dataDir, { recursive: true, force: true });
  }
});

test('recall sends types and a Beijing-date window, retries once when rate limited, maps business errors', async () => {
  const dataDir = await mkdtemp(join(tmpdir(), 'alphapai-'));
  try {
    const row = { id: 'S1', type: 'social_media', chunks: ['新易盛 1.6T 放量'], title: '社媒观点', time: '2026-10-20 10:00:00', industry: '', institution: '' };
    const server = fakeFetch({
      '/alpha/open-api/v1/sync/auth/hello': { body: { code: 200000, data: 'success' } },
      '/alpha/open-api/v1/paipai/recall-data': (count) => (count === 2 ? { body: { code: 42900, msg: '限流' } } : { body: { code: 200000, message: 'success', data: [row] } }),
    });
    const slept = [];
    const client = await createAlphaPai({ dataDir, fetchImpl: server.fetchImpl, sleep: async (ms) => { slept.push(ms); } });
    await client.saveKey(KEY);
    const items = await client.recall({ query: ' 新易盛 ', types: ['comment', 'ann', 'nope'], days: 7, now: new Date('2026-10-27T17:00:00Z') });
    assert.deepEqual(slept, [1500]);
    assert.equal(items.length, 1);
    assert.equal(items[0].docType, '社媒');
    const body = server.calls[1].body;
    assert.deepEqual(body, { query: '新易盛', recallType: ['comment', 'ann'], isCutOff: true, startTime: '2026-10-21', endTime: '2026-10-28' });
    assert.equal(server.calls.length, 3);

    const failing = fakeFetch({
      '/alpha/open-api/v1/sync/auth/hello': { body: { code: 200000, data: 'success' } },
      '/alpha/open-api/v1/paipai/recall-data': { body: { code: 500303, message: '参数错误' } },
    });
    const other = await createAlphaPai({ dataDir, fetchImpl: failing.fetchImpl });
    await assert.rejects(other.recall({ query: 'x' }), (error) => error.code === 'ALPHAPAI_500303' && /参数错误/.test(error.message));
    assert.deepEqual(await other.recall({ query: '   ' }), []);
  } finally {
    await rm(dataDir, { recursive: true, force: true });
  }
});

test('company feed uses Alpha派 own stock tags, list endpoints only; full text is fetched on demand', async () => {
  const dataDir = await mkdtemp(join(tmpdir(), 'alphapai-'));
  try {
    const P = '/alpha/open-api/v1';
    const tag = [{ code: '300502.SZ', name: '新易盛' }, { code: '300308.SZ', name: '中际旭创' }];
    let socialFails = false;
    let commentDetail = 'ok';
    const server = fakeFetch({
      [P + '/sync/auth/hello']: { body: { code: 200000, data: 'success' } },
      [P + '/comments/list']: (count) => {
        const body = server.calls[count - 1].body;
        const id = body.startDate === body.endDate ? 'enc-9' : 'enc-1';
        return { body: { code: 200000, data: { data: [
          { commentId: id, title: '光模块点评', content: '前100字…', commentTime: '2026-10-26 10:00:00', stockTag: tag, institutionTag: [{ code: 'I1', name: '中泰证券' }], industryTag: [{ code: 'X', name: '通信' }] },
          { commentId: 'enc-2', title: '光模块点评', content: '短', commentTime: '2026-10-26 08:00:00', stockTag: tag, institutionTag: [{ code: 'I1', name: '中泰证券' }] },
        ] } } };
      },
      [P + '/comments/detail']: (count) => {
        const ids = server.calls[count - 1].body.commentId;
        if (commentDetail === 'quota') return { body: { code: 400000, message: '当日查询点评详情已达上限（100条）' } };
        if (commentDetail === 'expired' && ids[0] === 'enc-1') return { body: { code: 400000, message: '参数错误' } };
        return { body: { code: 200000, data: [{ commentId: ids[0], title: '光模块点评', content: '完整点评正文，新易盛 1.6T 放量。', commentTime: '2026-10-26 10:00:00' }] } };
      },
      [P + '/social/media/article/list']: () => (socialFails ? { status: 500, body: {} } : { body: { code: 200000, data: { data: [
        { id: 'RAR1', title: '易中天集体下跌', content: '<p>新易盛跌 12%</p><p>第二段</p>', url: 'https://mp.weixin.qq.com/s/x', publishDate: '2026-10-22 16:19:08', accountName: '中国证券报', stock: tag, industry: [] },
      ] } } }),
      [P + '/summary/list']: { body: { code: 200000, data: { data: [
        { summaryId: 'S1', roadshowId: 'R1', title: '新易盛业绩会', publishTime: '2026-09-01 20:00:00', availableNoteTypes: ['ai_note'], meetingContentType: [{ code: 'performance_meeting', name: '业绩会' }], stockTag: tag.slice(0, 1), institutionTag: [{ code: 'I2', name: '中金公司' }] },
      ] } } },
      [P + '/summary/detail']: { body: { code: 200000, data: { aiContent: '纪要摘要', content: '纪要全文：1.6T 出货超预期。' } } },
      [P + '/report/list']: (count) => {
        const body = server.calls[count - 1].body;
        if (body.reportScope === 'foreign') return { body: { code: 200000, data: { data: [{ reportId: 'F1', title: 'Eoptolink: Strong Growth', titleCn: '新易盛：增长动能强劲', reportTime: '2026-08-24 00:00:00', reportTypeLabel: '公司研究', institutionTag: [{ code: 'I3', name: '摩根士丹利' }], stockTag: tag.slice(0, 1) }] } } };
        return { body: { code: 200000, data: { data: [{ reportId: 'D1', title: '新易盛(300502)业绩加速兑现', reportTime: '2026-10-10 00:00:00', reportTypeLabel: '公司研究', institutionTag: [{ code: 'I4', name: '天风证券' }], analystTag: [{ code: null, name: '张三' }], stockTag: tag.slice(0, 1) }] } } };
      },
      [P + '/report/detail']: { body: { code: 200000, data: { content: '事件：公司发布半年报，营收同比翻倍。' } } },
      [P + '/announcement/list']: { body: { code: 200000, data: { data: [{ announcementId: 'A1', title: '新易盛(300502.SZ):关于回购公司股份方案的公告', publishTime: '2026-10-23 00:00:00', actualPublishTime: '2026-10-23 12:13:18', announcementType: '权益变动', stockTag: tag.slice(0, 1) }] } } },
    });
    const client = await createAlphaPai({ dataDir, fetchImpl: server.fetchImpl });
    await client.saveKey(KEY);
    const now = new Date('2026-10-27T04:00:00Z');
    const items = await client.tagged({ symbol: '300502.sz', types: ['comment', 'social_media', 'roadShow', 'report', 'foreign_report', 'ann', 'edb'], days: 30, longDays: 90, now });
    const byType = Object.fromEntries(items.map((item) => [item.docType, item]));
    assert.deepEqual(Object.keys(byType).sort(), ['公告', '外资研报', '研报', '社媒', '纪要', '点评'].sort());
    assert.equal(server.calls.filter((call) => /detail/.test(call.path)).length, 0, '取列表时不调任何详情接口（点评详情每天只有 100 条额度）');
    assert.equal(items.filter((item) => item.docType === '点评').length, 1, '同一天同标题的点评只留一条（摘要长的）');
    const comment = byType['点评'];
    assert.equal(comment.content, '前100字…');
    assert.equal(comment.preview, true);
    assert.deepEqual(comment.ref, { kind: 'comment', id: 'enc-1', symbol: '300502.SZ', title: '光模块点评', time: '2026-10-26 10:00:00' });
    assert.deepEqual(comment.stocks, tag);
    assert.equal(comment.institution, '中泰证券');
    assert.equal(byType['社媒'].id, 'alphapai-RAR1', '社媒用原 id，和语义召回的结果能去重');
    assert.equal(byType['社媒'].content, '新易盛跌 12%\n第二段', '社媒正文去掉 HTML');
    assert.equal(byType['社媒'].preview, undefined);
    assert.equal(byType['社媒'].url, 'https://mp.weixin.qq.com/s/x');
    assert.equal(byType['纪要'].content, '业绩会 · 中金公司');
    assert.equal(byType['纪要'].ref.kind, 'minutes');
    assert.equal(byType['研报'].content, '公司研究 · 天风证券 · 张三');
    assert.equal(byType['外资研报'].title, '新易盛：增长动能强劲');
    assert.match(byType['外资研报'].content, /Eoptolink: Strong Growth\n公司研究 · 摩根士丹利/);
    assert.equal(byType['公告'].content, '公告类型：权益变动');
    assert.equal(byType['公告'].preview, undefined);
    assert.equal(byType['公告'].publishedAt, '2026-10-23T12:13:18+08:00');
    const body = (path, pick = (b) => b) => server.calls.filter((call) => call.path === P + path).map((call) => pick(call.body));
    assert.deepEqual(body('/comments/list', (b) => [b.stockCombSymbol, b.startDate, b.endDate]), [[['300502.SZ'], '2026-09-27', '2026-10-27']]);
    assert.deepEqual(body('/social/media/article/list', (b) => [b.stock, b.excludeContent]), [[['300502.SZ'], false]]);
    assert.deepEqual(body('/summary/list', (b) => [b.meetingMarketType, b.stockCombSymbol, b.beginTime]), [['A', ['300502.SZ'], '2026-07-29 00:00:00']]);
    assert.deepEqual(body('/report/list', (b) => [b.reportScope, b.startDate]).sort(), [['domestic', '2026-07-29'], ['foreign', '2026-07-29']]);
    assert.deepEqual(body('/announcement/list', (b) => [b.stockCode, b.publishFrom, b.sortBy]), [[['300502.SZ'], '2026-09-27', 'actual_publish_time']]);

    // 按需取全文：点评、研报、纪要各一次。
    assert.equal(await client.detail(comment), '完整点评正文，新易盛 1.6T 放量。');
    assert.equal(await client.detail(byType['研报']), '事件：公司发布半年报，营收同比翻倍。');
    assert.equal(await client.detail(byType['纪要']), '纪要全文：1.6T 出货超预期。');
    await assert.rejects(client.detail(byType['社媒']), (error) => error.code === 'ALPHAPAI_NO_DETAIL');
    // 额度用完：直接报，不重找。
    commentDetail = 'quota';
    const before = server.calls.length;
    await assert.rejects(client.detail(comment), (error) => error.code === 'ALPHAPAI_QUOTA' && /100/.test(error.message));
    assert.equal(server.calls.length - before, 1);
    // 列表 ID 过期：按标题重新列同一天的资料，用新 ID 再取。
    commentDetail = 'expired';
    assert.equal(await client.detail(comment), '完整点评正文，新易盛 1.6T 放量。');
    assert.deepEqual(server.calls.slice(-3).map((call) => [call.path.replace(P, ''), call.body.commentId ?? call.body.startDate]), [['/comments/detail', ['enc-1']], ['/comments/list', '2026-10-26'], ['/comments/detail', ['enc-9']]]);

    // 再取一次列表：id 不变；部分接口失败时返回其余的；全部失败才报错。
    socialFails = true;
    const again = await client.tagged({ symbol: '300502.SZ', types: ['comment', 'social_media'], days: 30, now });
    assert.deepEqual(again.map((item) => item.id), [comment.id]);
    assert.deepEqual(await client.tagged({ symbol: '光模块', types: ['comment'] }), []);
    await assert.rejects(client.tagged({ symbol: '300502.SZ', types: ['social_media'], now }), (error) => error.code === 'ALPHAPAI_HTTP_500');
  } finally {
    await rm(dataDir, { recursive: true, force: true });
  }
});
