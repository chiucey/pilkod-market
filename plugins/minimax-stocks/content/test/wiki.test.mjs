import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, mkdir, readFile, rm, stat, writeFile, realpath } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import {
  buildGraph, mergePage, pagesForStock, parsePage, searchPages, serializePage, slugify, validateUpsert,
} from '../miniapp/node/wiki-format.mjs';
import { resolveFolder, scanFolder } from '../miniapp/node/asset-folders.mjs';
import { normalizeLensState, validateLensUpdate } from '../miniapp/node/wiki-lenses.mjs';
import { createWikiService } from '../miniapp/node/wiki-service.mjs';

const NOW = '2026-10-25T12:00:00.000Z';

test('validateUpsert normalizes fields and marks unsourced relations pending', () => {
  const input = validateUpsert({
    title: ' 中际旭创 ', type: 'company', chain: 'midstream', tickers: ['300308', 'sz:300308'], aliases: ['旭创', '中际旭创'],
    relations: [{ type: 'supplies', target: '英伟达', note: '800G' }, { type: 'belongs_to', target: '光模块', source: 'a.pdf p3' }],
  });
  assert.equal(input.title, '中际旭创');
  assert.deepEqual(input.tickers, ['300308.SZ']);
  assert.deepEqual(input.aliases, ['旭创']);
  assert.equal(input.relations[0].status, 'pending');
  assert.equal(input.relations[1].status, 'confirmed');
  assert.throws(() => validateUpsert({ title: 'x', type: 'nope' }), /type 只能是/);
  assert.throws(() => validateUpsert({ title: 'x', chain: 'side' }), /chain 只能是/);
  assert.throws(() => validateUpsert({ title: 'A', relations: [{ type: 'supplies', target: 'a' }] }), /不能指向页面自己/);
  assert.equal(slugify('a/b:c*?'), 'a-b-c');
});

test('mergePage unions lists and merges relations by type+target', () => {
  const first = mergePage(null, validateUpsert({ title: '光模块', type: 'segment', sources: ['a.pdf'], relations: [{ type: 'belongs_to', target: '光通信', source: 'a.pdf' }] }), NOW);
  const second = mergePage(first, validateUpsert({ title: '光模块', sources: ['b.pdf'], relations: [{ type: 'belongs_to', target: '光通信', note: '核心环节' }, { type: 'upstream_of', target: '服务器', source: 'b.pdf' }] }), NOW);
  assert.equal(second.type, 'segment');
  assert.deepEqual(second.sources, ['a.pdf', 'b.pdf']);
  assert.equal(second.relations.length, 2);
  const belongs = second.relations.find((rel) => rel.type === 'belongs_to');
  assert.equal(belongs.note, '核心环节');
  assert.equal(belongs.source, 'a.pdf');
  assert.equal(belongs.status, 'confirmed');
});

test('page files round-trip and tolerate hand-written YAML', () => {
  const page = mergePage(null, validateUpsert({ title: '光芯片', type: 'segment', chain: 'upstream', industry: '光通信', body: '# 概述\n见 [[光模块]]', relations: [{ type: 'upstream_of', target: '光模块', source: 'x' }] }), NOW);
  const parsed = parsePage(serializePage(page), page.id);
  assert.equal(parsed.title, '光芯片');
  assert.equal(parsed.chain, 'upstream');
  assert.equal(parsed.relations[0].target, '光模块');
  assert.match(parsed.body, /\[\[光模块\]\]/);
  const hand = parsePage('---\ntitle: 英伟达\ntype: company\ntickers: [NVDA, "AAPL"]\n---\n正文', '英伟达');
  assert.deepEqual(hand.tickers, ['NVDA', 'AAPL']);
  assert.equal(hand.body, '正文');
});

test('graph exposes ghosts, typed edges and wikilink mentions; search handles CJK', () => {
  const pages = [
    mergePage(null, validateUpsert({ title: '中际旭创', type: 'company', tickers: ['300308.SZ'], aliases: ['旭创'], body: '主营 [[光模块]]', relations: [{ type: 'supplies', target: '英伟达', source: 's' }] }), NOW),
    mergePage(null, validateUpsert({ title: '光模块', type: 'segment', body: '高速光模块是 AI 集群的核心器件' }), NOW),
  ];
  const graph = buildGraph(pages);
  assert.equal(graph.ghosts.length, 1);
  assert.equal(graph.ghosts[0].title, '英伟达');
  assert.ok(graph.edges.some((edge) => edge.type === 'mention' && edge.to === '光模块'));
  assert.equal(searchPages(pages, '旭创')[0].title, '中际旭创');
  assert.equal(searchPages(pages, '300308')[0].title, '中际旭创');
  assert.equal(searchPages(pages, '集群')[0].title, '光模块');
  assert.equal(pagesForStock(pages, '300308.SZ', '').length, 1);
  assert.equal(pagesForStock(pages, '000001.SZ', '旭创').length, 1);
});

test('lens state keeps builtins and validates user prompts', () => {
  const state = normalizeLensState({ lenses: [{ id: 'chain', prompt: '我的产业链 Prompt', enabled: false }, { id: 'custom-a1', name: '技术路线', prompt: '看技术' }] });
  assert.equal(state.lenses.find((lens) => lens.id === 'chain').prompt, '我的产业链 Prompt');
  assert.equal(state.lenses.find((lens) => lens.id === 'chain').modified, true);
  assert.ok(state.lenses.some((lens) => lens.id === 'custom-a1'));
  assert.ok(state.lenses.some((lens) => lens.id === 'policy'));
  assert.throws(() => validateLensUpdate({ lenses: [{ id: 'evil', name: 'x', prompt: 'y' }] }), /id 不合法/);
  assert.throws(() => validateLensUpdate({ lenses: [{ id: 'chain', name: '', prompt: 'y' }] }), /名称/);
});

test('folder rules and scanning stay inside the resource folder', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-home-')));
  try {
    const folder = join(home, 'research');
    await mkdir(join(folder, 'sub'), { recursive: true });
    await mkdir(join(folder, '_wiki', 'pages'), { recursive: true });
    await mkdir(join(folder, 'node_modules'), { recursive: true });
    await mkdir(join(home, '.hidden'), { recursive: true });
    await writeFile(join(folder, 'a.md'), '# A');
    await writeFile(join(folder, 'sub', 'b.pdf'), '%PDF-1.4');
    await writeFile(join(folder, '.secret.md'), 'x');
    await writeFile(join(folder, '~$lock.docx'), 'x');
    await writeFile(join(folder, 'img.png'), 'x');
    await writeFile(join(folder, '_wiki', 'pages', 'p.md'), 'x');
    await writeFile(join(folder, 'node_modules', 'n.md'), 'x');
    assert.equal(await resolveFolder('~/research', { home }), folder);
    await assert.rejects(resolveFolder(home, { home }), /用户目录/);
    await assert.rejects(resolveFolder('~/.hidden', { home }), /隐藏目录/);
    assert.equal(await resolveFolder('~/.hidden', { home, fromSession: true }), join(home, '.hidden'));
    await assert.rejects(resolveFolder(tmpdir(), { home }), /用户目录下/);
    await assert.rejects(resolveFolder('relative/path', { home }), /绝对路径/);
    const scan = await scanFolder(folder);
    assert.deepEqual(scan.files.map((file) => file.rel).sort(), ['a.md', 'sub/b.pdf']);
  } finally {
    await rm(home, { recursive: true, force: true });
  }
});

function serve(service) {
  const readJson = async (request) => {
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    const text = Buffer.concat(chunks).toString('utf8');
    return text ? JSON.parse(text) : {};
  };
  const json = (response, status, value) => { response.writeHead(status, { 'content-type': 'application/json' }); response.end(JSON.stringify(value)); };
  const server = createServer((request, response) => {
    const url = new URL(request.url, 'http://test.local');
    service.handle(request, response, url, { readJson, json }).then((handled) => { if (!handled) json(response, 404, { error: 'not_found' }); });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}

async function waitFor(check, timeout = 5000) {
  const started = Date.now();
  for (;;) {
    const value = await check();
    if (value) return value;
    if (Date.now() - started > timeout) throw new Error('timeout');
    await new Promise((resolve) => setTimeout(resolve, 25));
  }
}

test('end to end: link folder, background agent builds the wiki, graph and stock links', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-data-'));
  const folder = join(home, '研报');
  await mkdir(folder, { recursive: true });
  await writeFile(join(folder, '光模块深度.md'), '# 光模块深度\n中际旭创是 800G 光模块龙头，主要客户英伟达。');
  await writeFile(join(folder, '扫描件.pdf'), '%PDF-1.4 binary');
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  const events = [];
  const prompts = [];
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const agent = {
    async run({ text, sessionId }, { onEvent } = {}) {
      prompts.push({ text, sessionId });
      onEvent?.({ type: 'turn.started', sessionId: 'sess-1', turnId: 't1', model: {} });
      onEvent?.({ type: 'tool.started', sessionId: 'sess-1', turnId: 't1', name: 'mcp__minimax-stocks__wiki_job_brief' });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      assert.ok(brief.lenses.some((lens) => lens.name === '产业链视角'));
      for (const file of brief.batch) {
        if (file.name.endsWith('.pdf')) { await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'skipped', note: '扫描件无法识别' }); continue; }
        const content = await readFile(file.path, 'utf8');
        assert.match(content, /中际旭创/);
        await tool('wiki_upsert_page', { job_id: jobId, title: '光通信', type: 'industry', body: '光通信产业链' });
        await tool('wiki_upsert_page', { job_id: jobId, title: '光芯片', type: 'segment', chain: 'upstream', industry: '光通信', relations: [{ type: 'upstream_of', target: '光模块', source: file.name }] });
        await tool('wiki_upsert_page', { job_id: jobId, title: '光模块', type: 'segment', chain: 'midstream', industry: '光通信', relations: [{ type: 'belongs_to', target: '光通信', source: file.name }] });
        const result = await tool('wiki_upsert_page', {
          job_id: jobId, title: '中际旭创', type: 'company', chain: 'midstream', industry: '光通信', tickers: ['300308'], aliases: ['旭创'],
          body: '## 概述\n800G 光模块龙头，见 [[光模块]]。\n\n| 指标 | 数值 |\n| --- | --- |\n| 份额 | 高 |',
          relations: [{ type: 'belongs_to', target: '光模块', source: file.name }, { type: 'supplies', target: '英伟达', note: '800G 光模块' }],
        });
        assert.deepEqual(result.targets_without_page, ['英伟达']);
        await tool('wiki_upsert_page', { job_id: jobId, title: '光模块深度', type: 'source', sources: [file.name], body: '摘要' });
        await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'ingested', summary_page: '光模块深度' });
      }
      return { sessionId: 'sess-1', turnId: 't1', status: 'finished', text: 'WIKI_BATCH_DONE 2' };
    },
    async reply() {},
  };
  service = createWikiService({ context: { agent }, dataDir, mutate, broadcast: (_event, data) => events.push(data.kind), log: () => {}, home, lookupName: () => null });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const call = async (path, init) => { const response = await fetch(base + path, init && { ...init, headers: { 'content-type': 'application/json' } }); return { status: response.status, body: await response.json() }; };
  try {
    assert.equal((await call('/status')).body.folders.length, 0);
    assert.equal((await call('/folders', { method: 'POST', body: JSON.stringify({ path: tmpdir() }) })).status, 400);
    const added = await call('/folders', { method: 'POST', body: JSON.stringify({ path: '~/研报' }) });
    assert.equal(added.status, 200);
    assert.equal(added.body.folder.isHome, undefined, 'no save-location concept any more');
    assert.equal((await call('/folders', { method: 'POST', body: JSON.stringify({ path: folder }) })).body.added, false);
    const files = await call('/files');
    assert.equal(files.body.counts.new, 2);

    const badLens = await call('/lenses', { method: 'PUT', body: JSON.stringify({ lenses: [{ id: 'x', name: 'n', prompt: 'p' }] }) });
    assert.equal(badLens.status, 400);
    const lenses = (await call('/lenses')).body;
    const saved = await call('/lenses', { method: 'PUT', body: JSON.stringify({ purpose: '跟踪光通信', lenses: lenses.lenses.map((lens) => ({ ...lens, enabled: lens.id !== 'competition' })) }) });
    assert.equal(saved.status, 200);
    assert.equal(saved.body.purpose, '跟踪光通信');

    const job = await call('/jobs', { method: 'POST', body: '{}' });
    assert.equal(job.status, 200);
    assert.equal(job.body.total, 2);
    assert.equal((await call('/jobs', { method: 'POST', body: '{}' })).status, 409);
    const done = await waitFor(async () => { const s = (await call('/status')).body; return ['done', 'error'].includes(s.job?.status) ? s : null; });
    assert.equal(done.job.status, 'done', done.job.error);
    assert.equal(done.job.ingested, 1);
    assert.equal(done.job.skipped, 1);
    assert.ok(done.job.lensNames.includes('产业链视角'));
    assert.ok(!done.job.lensNames.includes('竞争格局视角'));
    assert.equal(prompts.length, 1);
    assert.match(prompts[0].text, /minimax-stocks:llm-wiki/);
    assert.equal(done.pages, 5);

    const after = await call('/files');
    assert.equal(after.body.counts.ingested, 1);
    assert.equal(after.body.counts.skipped, 1);
    assert.equal(after.body.counts.pending, 0);

    const graph = (await call('/graph')).body;
    assert.equal(graph.pages.length, 5);
    assert.deepEqual(graph.ghosts.map((ghost) => ghost.title), ['英伟达']);
    assert.ok(graph.edges.some((edge) => edge.type === 'upstream_of' && edge.from === '光芯片' && edge.to === '光模块'));
    const company = graph.pages.find((page) => page.title === '中际旭创');
    assert.deepEqual(company.tickers, ['300308.SZ']);

    const detail = (await call('/page?id=' + encodeURIComponent('光模块'))).body.page;
    assert.ok(detail.backlinks.some((link) => link.title === '中际旭创' && link.relation === 'belongs_to'));
    assert.ok(detail.backlinks.some((link) => link.title === '光芯片' && link.relation === 'upstream_of'));
    const ghost = (await call('/page?title=' + encodeURIComponent('英伟达'))).body;
    assert.equal(ghost.ghost, true);

    const related = (await call('/related?symbol=300308.SZ&name=' + encodeURIComponent('中际旭创'))).body;
    assert.equal(related.matches[0].title, '中际旭创');
    assert.ok(related.groups.find((group) => group.key === 'segment').items.some((item) => item.title === '光模块'));
    assert.ok(related.groups.find((group) => group.key === 'customer').items.some((item) => item.title === '英伟达' && item.ghost));
    assert.equal((await call('/related?symbol=600519.SH&name=' + encodeURIComponent('贵州茅台'))).body.matches.length, 0);

    const neighbors = await tool('wiki_neighbors', { title: '旭创' });
    assert.equal(neighbors.center, '中际旭创');
    assert.ok(neighbors.edges.some((edge) => edge.to === '英伟达'));
    assert.equal((await tool('wiki_search', { query: '800G' })).results[0].title, '中际旭创');
    assert.equal((await tool('wiki_status', {})).files.ingested, 1);
    await assert.rejects(tool('wiki_mark_source', { job_id: done.job.id, file: 'x', status: 'ingested' }), /已经结束/);

    // 知识库固定在 dataDir/wiki/，资料文件夹里不写任何东西。
    const wikiDir = join(dataDir, 'wiki');
    const pageFile = await readFile(join(wikiDir, 'pages', '中际旭创.md'), 'utf8');
    assert.match(pageFile, /tickers: \["300308.SZ"\]/);
    assert.ok(await stat(join(wikiDir, 'manifest.json')));
    assert.match(await readFile(join(wikiDir, 'log.md'), 'utf8'), /已整理 · 研报\/光模块深度.md/);
    await waitFor(async () => Boolean(await stat(join(wikiDir, 'index.md')).catch(() => null)), 4000);
    assert.match(await readFile(join(wikiDir, 'index.md'), 'utf8'), /\[\[中际旭创\]\]/);
    assert.equal(await stat(join(folder, '_wiki')).catch(() => null), null, 'nothing is written into the material folder');

    await writeFile(join(folder, '光模块深度.md'), '# 光模块深度（更新）\n新增 1.6T 内容。');
    const changed = await call('/files?refresh=1');
    assert.equal(changed.body.counts.changed, 1);
    assert.ok(events.includes('pages') && events.includes('job') && events.includes('files'));

    const second = join(home, '纪要');
    await mkdir(second);
    assert.equal((await call('/folders', { method: 'POST', body: JSON.stringify({ path: join(folder, 'sub') }) })).status, 400);
    const secondAdded = await call('/folders', { method: 'POST', body: JSON.stringify({ path: second }) });
    assert.equal(secondAdded.status, 200);
    assert.equal((await call('/home', { method: 'PUT', body: JSON.stringify({ folderId: secondAdded.body.folder.id }) })).status, 404, 'the save location cannot be chosen');
    assert.equal((await call('/folders/' + added.body.folder.id, { method: 'DELETE' })).status, 200, 'any folder can be unlinked: the knowledge base is not inside it');
    assert.equal((await call('/graph')).body.pages.length, 5, 'pages stay after unlinking the folder');
  } finally {
    await service.dispose();
    await new Promise((resolve) => server.close(resolve));
    await rm(home, { recursive: true, force: true });
    await rm(dataDir, { recursive: true, force: true });
  }
});

test('jobs fail fast without agent access and stop when an agent makes no progress', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-data-'));
  await mkdir(join(home, 'docs'));
  await writeFile(join(home, 'docs', 'a.txt'), 'hello');
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  const permissions = [];
  const lazyAgent = {
    async run(_input, { onEvent } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      onEvent?.({ type: 'permission.requested', sessionId: 's', turnId: 't', requestId: 'r1', toolName: 'read', reason: '读取用户文件' });
      await new Promise((resolve) => setTimeout(resolve, 50));
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_FAILED 读不到' };
    },
    async reply(input) { permissions.push(input); },
  };
  for (const agent of [undefined, lazyAgent]) {
    const service = createWikiService({ context: agent ? { agent } : {}, dataDir, mutate, broadcast: () => {}, log: () => {}, home });
    const server = await serve(service);
    const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
    const post = async (path, body) => { const response = await fetch(base + path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }); return { status: response.status, body: await response.json() }; };
    try {
      await post('/folders', { path: join(home, 'docs') });
      const started = await post('/jobs', {});
      if (!agent) { assert.equal(started.status, 503); continue; }
      assert.equal(started.status, 200);
      const pending = await waitFor(async () => { const s = await (await fetch(base + '/status')).json(); return s.job?.permission ? s : null; });
      assert.equal(pending.job.status, 'approval');
      assert.equal((await post('/jobs/' + pending.job.id + '/permission', { decision: 'allowOnce' })).status, 200);
      assert.deepEqual(permissions, [{ sessionId: 's', requestId: 'r1', decision: 'allowOnce' }]);
      const final = await waitFor(async () => { const s = await (await fetch(base + '/status')).json(); return s.job?.status === 'error' ? s : null; });
      assert.match(final.job.error, /读不到/);
      assert.equal(final.files.pending, 1);
    } finally {
      await service.dispose();
      await new Promise((resolve) => server.close(resolve));
    }
  }
  await rm(home, { recursive: true, force: true });
  await rm(dataDir, { recursive: true, force: true });
});
