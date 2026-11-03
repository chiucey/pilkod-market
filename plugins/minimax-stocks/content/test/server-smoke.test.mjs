import assert from 'node:assert/strict';
import { mkdtemp, rm, stat } from 'node:fs/promises';
import { createServer } from 'node:net';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

// 冒烟：不带 Connector / Agent 启动完整的 Node 入口，检查页面、静态资源、wiki 路由和 MCP 工具清单。
test('server serves the assets page, wiki routes and wiki MCP tools', async () => {
  process.env.PATH = '/usr/bin:/bin';
  const { start } = await import('../miniapp/node/server.mjs');
  const port = await new Promise((resolve) => { const probe = createServer(); probe.listen(0, '127.0.0.1', () => { const { port: free } = probe.address(); probe.close(() => resolve(free)); }); });
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-smoke-'));
  const controller = new AbortController();
  const lifecycle = await start({
    pluginId: 'minimax-stocks',
    pluginRoot: join(dirname(fileURLToPath(import.meta.url)), '..'),
    dataDir,
    listen: { host: '127.0.0.1', port },
    signal: controller.signal,
    logger: { debug() {}, info() {}, warn() {}, error() {} },
  });
  const base = 'http://127.0.0.1:' + port;
  try {
    const html = await (await fetch(base + '/dashboard')).text();
    assert.match(html, /id="assets-main"/);
    assert.match(html, /data-app-page="assets"/);
    assert.match(html, /\/client\/wiki\.js/);
    const js = await fetch(base + '/client/wiki.js');
    assert.equal(js.status, 200);
    assert.match(js.headers.get('content-type'), /javascript/);
    assert.equal((await fetch(base + '/client/wiki.css')).status, 200);
    assert.equal((await fetch(base + '/client/sources.js')).status, 200);
    assert.match(html, /data-app-page="sources"/);
    const sources = await (await fetch(base + '/api/sources')).json();
    assert.deepEqual(sources.thirdParty.map((source) => source.id), ['hengsheng_market', 'comein', 'tencentdocs', 'zsxq', 'alphapai']);
    assert.equal(sources.thirdParty[0].status, 'unavailable');
    // Alpha派：没填 Key 时未连接；Key 格式不对直接拒绝（不发请求、不落盘）。
    const alpha = sources.thirdParty[4];
    assert.equal(alpha.status, 'unavailable');
    assert.deepEqual(alpha.apiKey, { configured: false, masked: '', savedAt: null });
    const badKey = await fetch(base + '/api/sources/alphapai', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ apiKey: 'short' }) });
    assert.equal(badKey.status, 400);
    assert.equal((await badKey.json()).error, 'alphapai_key_format');
    await assert.rejects(stat(join(dataDir, 'alphapai.json')), { code: 'ENOENT' });
    assert.ok(sources.local.some((source) => source.id === 'picker'));
    const tested = await (await fetch(base + '/api/sources/test', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ id: 'all' }) })).json();
    assert.equal(tested.thirdParty[0].test.ok, false);
    assert.match(tested.thirdParty[0].test.message, /Connector 授权/);
    assert.equal(tested.thirdParty[3].test.ok, false);
    assert.equal(tested.thirdParty[4].test.ok, false);
    assert.match(tested.thirdParty[4].test.message, /API Key/);
    assert.match(tested.local.find((source) => source.id === 'agent').test.message, /Agent 权限/);
    assert.equal((await fetch(base + '/client/../server.mjs')).status, 404);
    const status = await (await fetch(base + '/api/wiki/status')).json();
    assert.equal(status.agentAvailable, false);
    assert.equal(status.lenses.length, 3);
    const rpc = async (method, params) => (await (await fetch(base + '/mcp/minimax-stocks', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }) })).json()).result;
    const names = (await rpc('tools/list', {})).tools.map((tool) => tool.name);
    for (const name of ['watchlist_list', 'get_view_brief', 'data_sources', 'wiki_search', 'wiki_get_page', 'wiki_neighbors', 'wiki_pages_for_stock', 'wiki_upsert_page', 'wiki_job_brief', 'wiki_mark_source', 'wiki_status', 'wiki_resolve_company', 'wiki_stock_materials', 'wiki_link_stock_file', 'wiki_find_duplicates', 'wiki_merge_pages', 'wiki_tag_material', 'wiki_add_records', 'wiki_list_changes', 'research_search', 'research_read']) {
      assert.ok(names.includes(name), name);
    }
    const postView = (body) => fetch(base + '/api/view-state', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
    const viewBrief = async () => JSON.parse((await rpc('tools/call', { name: 'get_view_brief', arguments: {} })).content[0].text);
    await postView({ page: 'assets', assetsTab: 'graph', wikiView: 'chain', wikiIndustry: '光模块', wikiPage: 'ghost:英伟达' });
    const brief = await viewBrief();
    assert.equal(brief.viewing.page, '资产');
    assert.equal(brief.viewing.assetsTab, '知识图谱');
    assert.equal(brief.viewing.wikiView, '产业链');
    assert.equal(brief.viewing.wikiIndustry, '光模块');
    assert.equal(brief.viewing.wikiSelectedPage, '英伟达');
    assert.equal(brief.wiki.pages, 0);
    // 资料库页签上不报告图谱视图（用户看不到它），但保留上次选中的节点。
    await postView({ page: 'assets', assetsTab: 'files', wikiView: 'graph', wikiPage: 'ghost:英伟达' });
    const filesBrief = await viewBrief();
    assert.equal(filesBrief.viewing.assetsTab, '资料库');
    assert.equal(filesBrief.viewing.wikiView, undefined);
    assert.equal(filesBrief.viewing.wikiSelectedPage, '英伟达');
    // 缺省值：未知页签按资料库处理，未知视图按知识图谱处理。
    await postView({ page: 'assets', assetsTab: 'nope', wikiView: 'nope' });
    assert.equal((await viewBrief()).viewing.assetsTab, '资料库');
    await postView({ page: 'assets', assetsTab: 'graph', wikiView: 'nope' });
    assert.equal((await viewBrief()).viewing.wikiView, '知识图谱');
    await postView({ page: 'assets', assetsTab: 'changes' });
    assert.equal((await viewBrief()).viewing.assetsTab, '边际变化');
    await postView({ page: 'market', marketFeed: 'minutes' });
    assert.equal((await viewBrief()).viewing.feedTab, '纪要');
    // SSE：资料库变更后推送 wiki.updated（页面据此刷新个股资料与资产页）。
    const controller2 = new AbortController();
    const stream = await fetch(base + '/api/events', { signal: controller2.signal });
    const reader = stream.body.getReader();
    const lenses = await (await fetch(base + '/api/wiki/lenses')).json();
    await fetch(base + '/api/wiki/lenses', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ purpose: 'SSE', lenses: lenses.lenses }) });
    let received = '';
    const deadline = Date.now() + 3000;
    while (!received.includes('event: wiki.updated') && Date.now() < deadline) {
      const chunk = await Promise.race([reader.read(), new Promise((resolve) => setTimeout(() => resolve({ value: null }), 500))]);
      if (chunk.value) received += Buffer.from(chunk.value).toString('utf8');
    }
    controller2.abort();
    assert.match(received, /event: wiki\.updated\ndata: \{"kind":"lenses"/);
    // 知识库固定在数据目录里：不关联任何文件夹也能写页面；pages 一次写多个。
    const upsert = await rpc('tools/call', { name: 'wiki_upsert_page', arguments: { title: '光模块', type: 'segment' } });
    assert.notEqual(upsert.isError, true);
    assert.equal(JSON.parse(upsert.content[0].text).page.title, '光模块');
    assert.ok(await stat(join(dataDir, 'wiki', 'pages', '光模块.md')));
    const batch = await rpc('tools/call', { name: 'wiki_upsert_page', arguments: { pages: [{ title: '800G 光模块', type: 'product', relations: [{ type: 'belongs_to', target: '光模块' }] }, { title: '1.6T 光模块', type: 'product' }, { title: '没有类型的新页面' }] } });
    const written = JSON.parse(batch.content[0].text);
    assert.equal(written.written, 2);
    assert.equal(written.failed, 1);
    // 统一检索：什么来源都没接入时静默返回空结果，不报错；主体按知识图谱节点识别，产业链地图带上挂在下面的细分。
    const call = async (name, args) => { const reply = await rpc('tools/call', { name, arguments: args }); return { isError: reply.isError === true, value: JSON.parse(reply.content[0].text) }; };
    const search = await call('research_search', { query: '光模块 价格' });
    assert.equal(search.isError, false);
    assert.equal(search.value.subject.title, '光模块');
    assert.equal(search.value.topic, '价格');
    assert.deepEqual(search.value.items, []);
    assert.deepEqual(search.value.failed, []);
    assert.deepEqual(search.value.searched.map((entry) => entry.source), ['行情页已抓取的舆情']);
    assert.deepEqual(search.value.chain, { 细分: ['800G 光模块'] });
    assert.ok(search.value.wiki_pages.some((page) => page.title === '光模块'));
    assert.ok(search.value.hints.length > 0);
    assert.equal((await call('research_search', {})).isError, true);
    const read = await call('research_read', { ids: ['nope', 'file:missing:x.md'] });
    const full = await fetch(base + '/api/sentiment/full', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ id: 'alphapai-nope' }) });
    assert.equal(full.status, 404);
    assert.equal((await full.json()).loaded, false);
    assert.deepEqual(read.value.items.map((item) => item.found), [false, false]);
    const statusAfter = await (await fetch(base + '/api/wiki/status')).json();
    assert.equal(statusAfter.pages, 3);
    assert.equal(statusAfter.wiki.path, join(dataDir, 'wiki'));
    assert.equal((await fetch(base + '/api/wiki/home', { method: 'PUT', headers: { 'content-type': 'application/json' }, body: '{}' })).status, 404);
  } finally {
    await lifecycle.dispose();
    controller.abort();
    await rm(dataDir, { recursive: true, force: true });
  }
});
