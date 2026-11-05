import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, realpath, writeFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { createWikiService } from '../miniapp/node/wiki-service.mjs';
import {
  clipFileName, clipMarkdown, createFileIndex, dateFromText, excerptFromText, looksLikeMinutes, mergeRecords, normalizeDate, normalizeRecord, parseSource,
} from '../miniapp/node/wiki-records.mjs';
import { createOpener } from '../miniapp/node/open-external.mjs';
import { folderId } from '../miniapp/node/asset-folders.mjs';
import { assembleFeed } from '../miniapp/node/search-terms.mjs';

function serve(service) {
  const readJson = async (request) => { const chunks = []; for await (const chunk of request) chunks.push(chunk); const text = Buffer.concat(chunks).toString('utf8'); return text ? JSON.parse(text) : {}; };
  const json = (response, status, value) => { response.writeHead(status, { 'content-type': 'application/json' }); response.end(JSON.stringify(value)); };
  const server = createServer((request, response) => {
    service.handle(request, response, new URL(request.url, 'http://t'), { readJson, json }).then((handled) => { if (!handled) json(response, 404, {}); });
  });
  return new Promise((resolve) => server.listen(0, '127.0.0.1', () => resolve(server)));
}
async function waitFor(check, timeout = 5000) {
  const started = Date.now();
  for (;;) { const value = await check(); if (value) return value; if (Date.now() - started > timeout) throw new Error('timeout'); await new Promise((resolve) => setTimeout(resolve, 25)); }
}

test('records: dates, minutes detection, source parsing, validation and merging', () => {
  assert.equal(dateFromText('2026年10月12日 中际旭创调研纪要'), '2026-10-12');
  assert.equal(dateFromText('20261012 纪要'), '2026-10-12');
  assert.equal(dateFromText('2026-13-01 纪要'), null);
  assert.equal(normalizeDate('2026-10'), '2026-10');
  assert.equal(normalizeDate('最近'), null);
  assert.ok(looksLikeMinutes('调研/新易盛交流纪要.docx'));
  assert.ok(!looksLikeMinutes('光模块深度报告.pdf'));
  const index = createFileIndex([{ key: 'f1:研报/光模块深度.pdf', display: '资料库/研报/光模块深度.pdf', path: '/x/研报/光模块深度.pdf', base: '光模块深度.pdf', baseNoExt: '光模块深度' }]);
  assert.deepEqual(parseSource('资料库/研报/光模块深度.pdf p12', index), { label: '资料库/研报/光模块深度.pdf p12', file: 'f1:研报/光模块深度.pdf', locator: 'p12' });
  assert.equal(parseSource('光模块深度.pdf「供需」节', index).file, 'f1:研报/光模块深度.pdf');
  assert.equal(parseSource('见 https://wx.zsxq.com/topic/1 原文', index).url, 'https://wx.zsxq.com/topic/1');
  assert.equal(parseSource({ url: 'javascript:alert(1)' }, index), null);
  assert.deepEqual(parseSource('某券商口头交流', index), { label: '某券商口头交流' });

  const ctx = { resolveEntity: (name) => (name === '新易盛' ? { title: '新易盛' } : null), resolveSource: (src) => parseSource(src, index) };
  assert.throws(() => normalizeRecord({ kind: 'change', entity: '不存在', date: '2026-10-01', text: '订单增加', sources: ['x'] }, ctx), /还没有页面/);
  assert.throws(() => normalizeRecord({ kind: 'change', entity: '新易盛', date: '最近', text: '订单增加', sources: ['x'] }, ctx), /date/);
  assert.throws(() => normalizeRecord({ kind: 'change', entity: '新易盛', date: '2026-10-01', text: '订单增加', sources: [] }, ctx), /sources/);
  const first = normalizeRecord({ kind: 'change', entity: '新易盛', date: '2026-10-01', text: '800G 订单环比增加', dimension: '订单', direction: 'improve', from: '10 万只', to: '15 万只', sources: ['资料库/研报/光模块深度.pdf p3'] }, ctx);
  assert.equal(first.direction, 'improve');
  assert.equal(first.sources[0].file, 'f1:研报/光模块深度.pdf');
  const second = normalizeRecord({ kind: 'change', entity: '新易盛', date: '2026-10-01', text: '800G 订单环比增加', sources: ['https://wx.zsxq.com/topic/9'] }, ctx);
  assert.equal(second.direction, 'unclear');
  assert.equal(second.dimension, '其他');
  assert.equal(first.id, second.id, 'same entity, date and text is one record');
  const once = mergeRecords([], [first]);
  const twice = mergeRecords(once.records, [second]);
  assert.equal(twice.records.length, 1);
  assert.equal(twice.merged.length, 1);
  assert.equal(twice.records[0].sources.length, 2);
  assert.equal(twice.records[0].direction, 'improve');

  assert.equal(clipFileName({ title: 'a/b:c', publishedAt: '2026-10-20T10:00:00+08:00' }), '2026-10-20 a b c.md');
  const md = clipMarkdown({ id: 'zsxq-1', source: '知识星球', title: '标题', content: '正文', url: 'https://wx.zsxq.com/topic/1', publishedAt: '2026-10-20T10:00:00+08:00' }, { symbol: '300502.SZ', name: '新易盛', importedAt: '2026-10-25T00:00:00Z' });
  assert.match(md, /sentimentId: "zsxq-1"/);
  assert.match(md, /原文：https:\/\/wx\.zsxq\.com\/topic\/1/);
  assert.ok(excerptFromText(md, 40).startsWith('标题'));
});

test('opener picks the platform command and rejects option-like targets', async () => {
  const calls = [];
  const run = async (file, args, options) => { calls.push([file, args, options.ignoreExitCode]); };
  await createOpener({ platform: 'darwin', run }).open('/Users/a/b.pdf');
  await createOpener({ platform: 'win32', run }).open('C:\\a\\b.pdf');
  await createOpener({ platform: 'linux', run }).open('https://example.com/');
  assert.deepEqual(calls, [['open', ['/Users/a/b.pdf'], false], ['explorer.exe', ['C:\\a\\b.pdf'], true], ['xdg-open', ['https://example.com/'], false]]);
  await assert.rejects(createOpener({ platform: 'darwin', run }).open('-a Calculator'), /无效/);
  assert.equal(createOpener({ platform: 'test', run }).supported, false);
});

test('minutes tagging, records, clips, scan job and open-with-default-app', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-v3-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-v3-data-'));
  const folder = join(home, '资料');
  await mkdir(join(folder, '纪要'), { recursive: true });
  await writeFile(join(folder, '纪要', '2026-10-12 光模块龙头交流纪要.md'), '# 交流纪要\n公司 800G 出货环比增长三成，1.6T 已送样。');
  await writeFile(join(folder, '纪要', '新易盛调研纪要.md'), '新易盛：海外云厂商订单饱满。');
  await writeFile(join(folder, '光模块深度报告.md'), '新易盛与中际旭创竞争。');
  const names = { '300502.SZ': '新易盛', '300308.SZ': '中际旭创' };
  const sentimentRows = [{ symbol: '300502.SZ', shortName: '新易盛', items: [
    { id: 'zsxq-1', source: '知识星球', title: '新易盛 1.6T 订单落地', summary: '1.6T 订单', content: '据渠道，新易盛 1.6T 订单落地，单价约 1200 美元。', publishedAt: '2026-10-20T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/1', tags: [] },
    { id: 'zsxq-2', source: '知识星球', title: '光模块行业周报', summary: '周报', content: '行业周报：价格平稳。', publishedAt: '2026-10-18T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/2', tags: [] },
  ] }];
  const opened = [];
  const opener = { supported: true, open: async (target) => { opened.push(target); } };
  let clipsChanged = 0;
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const agent = {
    async run({ text }, { onEvent } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      if (brief.task === 'scan') {
        assert.equal(brief.entities[0].page.title, '新易盛');
        for (const item of brief.items) {
          if (item.title.includes('订单')) {
            await tool('wiki_add_records', { job_id: jobId, records: [{ kind: 'change', entity: '新易盛', date: '2026-10-20', text: '1.6T 订单落地', dimension: '订单', direction: 'improve', to: '单价约 1200 美元', sources: [item.file] }] });
          }
          await tool('wiki_mark_source', { job_id: jobId, file: item.file, status: 'ingested', note: item.title.includes('订单') ? '记 1 条变化' : '无边际变化' });
        }
      } else {
        for (const file of brief.batch) {
          if (file.name.includes('交流纪要')) {
            await tool('wiki_upsert_page', { job_id: jobId, title: '光模块龙头交流纪要', type: 'source', sources: [file.name], body: '摘要' });
            await tool('wiki_add_records', { job_id: jobId, records: [{ kind: 'update', entity: '新易盛', date: '2026-10-12', text: '800G 出货环比增长三成', sources: [file.file + ' 第 1 段'] }] });
            const marked = await tool('wiki_mark_source', {
              job_id: jobId, file: file.file, status: 'ingested', summary_page: '光模块龙头交流纪要', doc_type: '纪要', doc_date: '2026-10-12', doc_title: '光模块龙头交流纪要',
              stocks: [{ name: '新易盛', relevance: 'core', note: '800G 出货环比 +30%' }, { name: '某未上市公司', relevance: 'mentioned' }],
            });
            assert.deepEqual(marked.tagged.unresolved, ['某未上市公司']);
          } else {
            await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'skipped', note: '测试跳过' });
          }
        }
      }
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE' };
    },
    async reply() {},
  };
  service = createWikiService({
    context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test',
    lookupName: (symbol) => names[symbol] ?? null,
    resolveCompany: async (query) => (query.includes('新易盛') ? { symbol: '300502.SZ', shortName: '新易盛' } : null),
    sentiments: () => sentimentRows, watchlist: () => ['300502.SZ'], currentSymbol: () => '300502.SZ', opener, onClipsChanged: () => { clipsChanged += 1; },
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const enc = encodeURIComponent;
  const call = async (path, body) => { const response = await fetch(base + path, body === undefined ? undefined : { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }); return { status: response.status, body: await response.json() }; };
  const finished = (kind) => waitFor(async () => { const s = (await call('/status')).body; return s.job?.kind === kind && ['done', 'error'].includes(s.job?.status) ? s.job : null; });
  try {
    assert.equal((await call('/folders', { path: folder })).status, 200);
    await tool('wiki_upsert_page', { title: '新易盛', type: 'company', tickers: ['300502.SZ'], industry: '光通信', sources: ['资料/光模块深度报告.md'], body: '见 光模块深度报告.md' });

    let minutes = (await call('/minutes?symbol=300502.SZ&name=' + enc('新易盛'))).body;
    assert.deepEqual(minutes.items.map((item) => item.rel), ['纪要/新易盛调研纪要.md'], 'only the filename match before tagging');

    assert.equal((await call('/jobs', {})).status, 200);
    const ingest = await finished('ingest');
    assert.equal(ingest.status, 'done', ingest.error);
    assert.equal(ingest.records, 1);
    minutes = (await call('/minutes?symbol=300502.SZ&name=' + enc('新易盛'))).body;
    const tagged = minutes.items.find((item) => item.rel.includes('交流纪要'));
    assert.ok(tagged, 'agent-tagged minutes show up without a string match');
    assert.equal(tagged.date, '2026-10-12');
    assert.equal(tagged.dateSource, 'agent');
    assert.equal(tagged.tagged, true);
    assert.equal(tagged.relevance, 'core');
    assert.equal(tagged.summaryPage.title, '光模块龙头交流纪要');
    const files = (await call('/files')).body.folders[0].files;
    const minutesFile = files.find((item) => item.rel.includes('交流纪要'));
    assert.equal(minutesFile.docType, '纪要');
    assert.equal(minutesFile.docTypeBy, 'agent');
    assert.ok(minutesFile.stocks.some((stock) => stock.symbol === '300502.SZ' && stock.by === 'agent'));
    assert.equal(files.find((item) => item.rel === '光模块深度报告.md').docType, undefined);

    const detail = (await call('/page?title=' + enc('新易盛'))).body.page;
    assert.equal(detail.records[0].text, '800G 出货环比增长三成');
    assert.equal(detail.records[0].sources[0].kind, 'file');
    assert.equal(detail.records[0].sources[0].locator, '第 1 段');
    assert.equal(detail.sourceRefs[0].kind, 'file');
    assert.ok(detail.linkables.some((item) => item.text === '光模块深度报告.md'));

    assert.equal((await call('/open', { key: detail.sourceRefs[0].key })).status, 200);
    assert.equal(opened[0], join(folder, '光模块深度报告.md'));
    assert.equal((await call('/open', { url: 'https://wx.zsxq.com/topic/1' })).status, 200);
    assert.equal(opened[1], 'https://wx.zsxq.com/topic/1');
    assert.equal((await call('/open', { url: 'javascript:alert(1)' })).status, 400);
    assert.equal((await call('/open', { key: 'nope:x.md' })).status, 404);

    const clip = await call('/clips', { symbol: '300502.SZ', ids: ['zsxq-1'] });
    assert.equal(clip.body.imported, 1);
    assert.equal(clipsChanged, 1);
    assert.equal((await call('/clips', { symbol: '300502.SZ', ids: ['zsxq-1'] })).body.skipped, 1);
    assert.ok(service.clippedIds().has('zsxq-1'));
    const clips = (await call('/files')).body.folders.find((item) => item.id === 'clips');
    assert.equal(clips.label, '收录的舆情');
    assert.equal(clips.virtual, true);
    assert.equal(clips.files[0].status, 'new');
    assert.equal(clips.files[0].docType, '舆情');
    assert.match(clips.files[0].rel, /^知识星球\/2026-10-20 /);
    assert.match(await readFile(join(clips.path, clips.files[0].rel), 'utf8'), /1\.6T 订单落地/);
    assert.equal((await call('/status')).body.files.pending, 1, 'clipped sentiment waits to be ingested');

    assert.equal((await call('/jobs', { kind: 'scan', scope: 'current' })).body.kind, 'scan');
    const scan = await finished('scan');
    assert.equal(scan.status, 'done', scan.error);
    assert.equal(scan.records, 1);
    const changes = (await call('/changes')).body;
    assert.equal(changes.changes.length, 1);
    assert.equal(changes.changes[0].direction, 'improve');
    assert.equal(changes.changes[0].entityId, '新易盛');
    assert.equal(changes.changes[0].sources[0].kind, 'url');
    assert.equal(changes.changes[0].sources[0].url, 'https://wx.zsxq.com/topic/1');
    assert.deepEqual(changes.changes[0].sourceKinds, ['知识星球']);
    assert.equal((await call('/jobs', { kind: 'scan', scope: 'current' })).status, 409, 'scanned items are not scanned again');
    const listed = await tool('wiki_list_changes', { symbol: '300502.SZ' });
    assert.equal(listed.total, 1);
    assert.match(listed.items[0].direction, /改善/);
    const related = (await call('/related?symbol=300502.SZ&name=' + enc('新易盛'))).body;
    assert.equal(related.changes.length, 1);
    assert.equal(related.updates[0].text, '800G 出货环比增长三成');

    const tagResult = await tool('wiki_tag_material', { file: '资料/光模块深度报告.md', doc_type: '研报', stocks: [{ name: '中际旭创', symbol: '300308.SZ', relevance: 'mentioned' }] });
    assert.equal(tagResult.doc_type, '研报');
    assert.equal(tagResult.stocks[0].symbol, '300308.SZ');
    await assert.rejects(tool('wiki_tag_material', { file: '不存在.md', doc_type: '纪要' }), /不在关联的资料文件夹里/);

    await tool('wiki_upsert_page', { title: 'Eoptolink', type: 'company', body: 'x' });
    await tool('wiki_add_records', { records: [{ kind: 'update', entity: 'Eoptolink', date: '2026-09', text: '海外产能扩张', sources: ['https://example.com/a'] }] });
    assert.equal((await call('/merge', { into: '新易盛', from: ['Eoptolink'] })).status, 200);
    const merged = (await call('/page?title=' + enc('新易盛'))).body.page;
    assert.ok(merged.records.some((record) => record.text === '海外产能扩张'), 'records follow merged nodes');
  } finally {
    server.close();
    await service.dispose();
  }
});


test('auto organize: new files and new sentiments are picked up without clicks; stopping pauses it', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-auto-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-auto-data-'));
  const folder = join(home, '资料');
  await mkdir(folder, { recursive: true });
  await writeFile(join(folder, '新易盛调研纪要.md'), '新易盛：海外订单饱满。');
  const rows = [{ symbol: '300502.SZ', shortName: '新易盛', items: [
    { id: 'zsxq-a', source: '知识星球', title: '新易盛 1.6T 放量', summary: 'x', content: '1.6T 放量', publishedAt: '2026-10-20T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/a', tags: [] },
  ] }];
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  let hang = false;
  const kinds = [];
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const agent = {
    async run({ text }, { onEvent, signal } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      if (hang) {
        await new Promise((resolve) => signal?.addEventListener('abort', resolve, { once: true }));
        return { sessionId: 's', turnId: 't', status: 'aborted', text: '' };
      }
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      kinds.push(brief.task);
      if (brief.task === 'scan') {
        for (const item of brief.items) await tool('wiki_mark_source', { job_id: jobId, file: item.file, status: 'ingested', note: '无边际变化' });
      } else {
        for (const file of brief.batch) {
          await tool('wiki_upsert_page', { job_id: jobId, title: '新易盛', type: 'company', tickers: ['300502.SZ'], sources: [file.name] });
          await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'ingested', doc_type: '纪要', stocks: [{ name: '新易盛', relevance: 'core' }] });
        }
      }
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE' };
    },
    async reply() {},
  };
  service = createWikiService({
    context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test',
    lookupName: (symbol) => (symbol === '300502.SZ' ? '新易盛' : null),
    sentiments: () => rows, watchlist: () => [], currentSymbol: () => '300502.SZ',
    autoOrganize: true, autoDelayMs: 20, autoScanGapMs: 0, autoRescanMs: 60_000,
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const call = async (path, body, method = 'POST') => { const response = await fetch(base + path, body === undefined ? undefined : { method, headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }); return { status: response.status, body: await response.json() }; };
  try {
    assert.equal((await call('/folders', { path: folder })).status, 200);
    await waitFor(async () => kinds.includes('ingest') && kinds.includes('scan') && !(await call('/status')).body.job?.status?.match(/queued|running/), 8000);
    assert.deepEqual(kinds, ['ingest', 'scan'], 'files first, then new sentiments, no clicks');
    const status = (await call('/status')).body;
    assert.equal(status.auto.enabled, true);
    assert.equal(status.auto.unscanned, 0);
    assert.equal(status.job.auto, true);
    const latest = (await call('/latest?symbol=300502.SZ&name=' + encodeURIComponent('新易盛'))).body;
    assert.equal(latest.company.title, '新易盛');
    assert.equal(latest.auto.available, true);

    // 用户手动停止正在跑的自动任务：自动整理暂停，不会立刻又启动
    hang = true;
    rows[0].items.push({ id: 'zsxq-b', source: '知识星球', title: '新的一条', summary: 'y', content: 'y', publishedAt: '2026-10-21T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/b', tags: [] });
    service.onSentimentsUpdated();
    const running = await waitFor(async () => { const s = (await call('/status')).body; return s.job?.kind === 'scan' && s.job.status === 'running' && s.job.files.some((file) => file.key === 'sentiment:zsxq-b') ? s.job : null; }, 8000);
    assert.equal((await call('/jobs/' + running.id + '/cancel', {})).status, 200);
    const paused = await waitFor(async () => { const s = (await call('/status')).body; return s.auto.enabled === false ? s : null; }, 5000);
    assert.equal(paused.job.status, 'cancelled');
    assert.ok(paused.auto.pausedAt);
    hang = false;
    const resumed = await call('/auto', { enabled: true }, 'PUT');
    assert.equal(resumed.body.enabled, true);
    await waitFor(async () => { const s = (await call('/status')).body; return s.job?.status === 'done' && s.auto.unscanned === 0; }, 8000);
  } finally {
    server.close();
    await service.dispose();
  }
});

test('latest feed brings in segment and product records; scan scope all covers current stock and watchlist', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-latest-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-latest-data-'));
  const folder = join(home, '资料');
  await mkdir(folder, { recursive: true });
  await writeFile(join(folder, '笔记.md'), '光模块笔记');
  const rows = [
    { symbol: '300502.SZ', shortName: '新易盛', items: [{ id: 's-a', source: '知识星球', title: 'a', summary: 'a', content: 'a', publishedAt: '2026-10-20T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/a', tags: [] }] },
    { symbol: '300308.SZ', shortName: '中际旭创', items: [{ id: 's-b', source: '知识星球', title: 'b', summary: 'b', content: 'b', publishedAt: '2026-10-21T10:00:00+08:00', url: 'https://wx.zsxq.com/topic/b', tags: [] }] },
  ];
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const scanned = [];
  const agent = {
    async run({ text }, { onEvent } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      for (const item of brief.items ?? []) { scanned.push(item.file); await tool('wiki_mark_source', { job_id: jobId, file: item.file, status: 'ingested', note: '无边际变化' }); }
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE' };
    },
    async reply() {},
  };
  service = createWikiService({
    context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test',
    lookupName: (symbol) => ({ '300502.SZ': '新易盛', '300308.SZ': '中际旭创' })[symbol] ?? null,
    sentiments: () => rows, watchlist: () => ['300308.SZ'], currentSymbol: () => '300502.SZ',
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const call = async (path, body, method = 'POST') => { const response = await fetch(base + path, body === undefined ? undefined : { method, headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }); return { status: response.status, body: await response.json() }; };
  try {
    assert.equal((await call('/folders', { path: folder })).status, 200);
    await tool('wiki_upsert_page', { title: '光模块', type: 'segment', chain: 'midstream', industry: '光通信' });
    await tool('wiki_upsert_page', { title: '1.6T 光模块', type: 'product', industry: '光通信' });
    await tool('wiki_upsert_page', { title: '新易盛', type: 'company', tickers: ['300502.SZ'], relations: [{ type: 'belongs_to', target: '光模块', source: 'https://example.com/r' }, { type: 'produces', target: '1.6T 光模块', source: 'https://example.com/r' }] });
    await tool('wiki_upsert_page', { title: '中际旭创', type: 'company', tickers: ['300308.SZ'] });
    await tool('wiki_add_records', { records: [
      { kind: 'change', entity: '新易盛', date: '2026-10-20', text: '海外订单上调', dimension: '订单', direction: 'improve', sources: ['https://example.com/1'] },
      { kind: 'change', entity: '光模块', date: '2026-10-22', text: '800G 价格企稳', dimension: '价格', direction: 'unclear', sources: ['https://example.com/2'] },
      { kind: 'update', entity: '1.6T 光模块', date: '2026-10-18', text: '开始小批量出货', sources: ['https://example.com/3'] },
      { kind: 'change', entity: '中际旭创', date: '2026-10-23', text: '别的公司的变化', dimension: '订单', direction: 'improve', sources: ['https://example.com/4'] },
    ] });
    const latest = (await call('/latest?symbol=300502.SZ&name=' + encodeURIComponent('新易盛'))).body;
    assert.equal(latest.company.title, '新易盛');
    assert.deepEqual(latest.records.map((record) => [record.entity, record.related]), [['光模块', true], ['新易盛', false], ['1.6T 光模块', true]], 'own records plus its segment and product, newest first, other companies excluded');
    assert.ok(latest.records.every((record) => record.entityId), 'every record can open its node');
    assert.deepEqual([...latest.related].sort(), ['1.6T 光模块', '光模块'].sort());
    assert.equal(latest.auto.available, false, 'auto organize is off in this service');
    const unknown = (await call('/latest?symbol=600000.SH&name=' + encodeURIComponent('浦发银行'))).body;
    assert.equal(unknown.company, null);
    assert.deepEqual(unknown.records, []);

    // 资产页「立即扫描」：scope=all 覆盖当前股票和自选股，和 auto.unscanned 的口径一致
    assert.equal((await call('/status')).body.auto.unscanned, 2);
    const job = (await call('/jobs', { kind: 'scan', scope: 'all', symbol: '300502.SZ' })).body;
    assert.equal(job.total, 2);
    await waitFor(async () => (await call('/status')).body.job?.status === 'done', 5000);
    assert.equal(scanned.length, 2);
    assert.equal((await call('/status')).body.auto.unscanned, 0);
    assert.equal((await call('/jobs', { kind: 'scan', scope: 'all' })).status, 409);
  } finally {
    server.close();
    await service.dispose();
  }
});

test('auto organize: a sentiment refresh does not postpone a run that is already scheduled', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-auto2-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-auto2-data-'));
  const folder = join(home, '资料');
  await mkdir(folder, { recursive: true });
  await writeFile(join(folder, '新易盛调研纪要.md'), '新易盛：海外订单饱满。');
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  let startedAt = 0;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const agent = {
    async run({ text }, { onEvent } = {}) {
      if (!startedAt) startedAt = Date.now();
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      for (const file of brief.batch ?? []) await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'skipped', note: '测试' });
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE' };
    },
    async reply() {},
  };
  service = createWikiService({
    context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test',
    lookupName: () => null, sentiments: () => [], watchlist: () => [], currentSymbol: () => null,
    autoOrganize: true, autoDelayMs: 300, autoScanGapMs: 0, autoRescanMs: 60_000,
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  try {
    // 启动时排的那一次先跑掉（还没有文件夹，什么都不做）
    await new Promise((resolve) => setTimeout(resolve, 450));
    const linkedAt = Date.now();
    const response = await fetch(base + '/folders', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ path: folder }) });
    assert.equal(response.status, 200);
    service.onSentimentsUpdated(); // 舆情刷新排的是 3 倍延迟，不能把关联文件夹触发的整理往后推
    await waitFor(async () => startedAt, 5000);
    assert.ok(startedAt - linkedAt < 750, 'run started ' + (startedAt - linkedAt) + 'ms after linking');
  } finally {
    server.close();
    await service.dispose();
  }
});

test('the knowledge base lives in one fixed place: the legacy _wiki of the old save folder is migrated once', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-mig-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-mig-data-'));
  const folder = join(home, '资料');
  const legacy = join(folder, '_wiki');
  await mkdir(join(legacy, 'pages'), { recursive: true });
  await mkdir(join(legacy, 'clips', '知识星球'), { recursive: true });
  await writeFile(join(folder, '2026-10-20 新易盛调研纪要.md'), '新易盛：海外订单饱满。');
  await writeFile(join(legacy, 'pages', '新易盛.md'), '---\ntitle: "新易盛"\ntype: "company"\ntickers: ["300502.SZ"]\n---\n\n旧版知识库里的公司页\n');
  await writeFile(join(legacy, 'records.json'), JSON.stringify([{ id: 'r1', kind: 'update', entity: '新易盛', date: '2026-10-01', text: '旧版记录', sources: [{ label: '旧资料.md' }] }]));
  await writeFile(join(legacy, 'manifest.json'), JSON.stringify({ version: 1, sources: {}, stockLinks: {}, files: {}, clips: { 'zsxq-1': { symbol: '300502.SZ' } }, scanned: { 'zsxq-1': { at: '2026-10-01T00:00:00Z' } } }));
  await writeFile(join(legacy, 'clips', '知识星球', '2026-10-01 一条舆情.md'), '---\nsource: "知识星球"\n---\n\n新易盛 1.6T 放量');
  await writeFile(join(legacy, 'README.md'), '# 产业链 Wiki\n');
  const id = folderId(folder);
  await writeFile(join(dataDir, 'wiki-settings.json'), JSON.stringify({ folders: [{ id, path: folder, label: '资料', addedAt: '2026-10-01T00:00:00Z' }], homeId: id }));
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  const make = () => createWikiService({ context: {}, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test', lookupName: (symbol) => (symbol === '300502.SZ' ? '新易盛' : null) });
  let service = make();
  let server = await serve(service);
  const get = async (path) => (await fetch('http://127.0.0.1:' + server.address().port + '/api/wiki' + path)).json();
  try {
    const status = await get('/status');
    assert.equal(status.pages, 1);
    assert.equal(status.wiki.path, join(dataDir, 'wiki'));
    assert.equal(status.wiki.migratedFrom, legacy);
    assert.equal(status.home, undefined);
    assert.equal(status.folders[0].isHome, undefined);
    assert.match(await readFile(join(dataDir, 'wiki', 'pages', '新易盛.md'), 'utf8'), /旧版知识库里的公司页/);
    assert.match(await readFile(join(dataDir, 'wiki', 'README.md'), 'utf8'), /全局只有这一份/);
    assert.equal((await get('/latest?symbol=300502.SZ&name=' + encodeURIComponent('新易盛'))).records.length, 1, 'records come along');
    const files = await get('/files');
    assert.equal(files.folders.find((item) => item.virtual)?.files.length, 1, 'stored sentiments come along as the virtual folder');
    assert.equal(files.folders.find((item) => !item.virtual).files.length, 1, 'the old _wiki is still not scanned as material');
    assert.match(await readFile(join(legacy, 'README.md'), 'utf8'), /^> 已迁移/);
    const settings = JSON.parse(await readFile(join(dataDir, 'wiki-settings.json'), 'utf8'));
    assert.equal(settings.migration.done, true);
    assert.equal(settings.homeId, undefined);
    // 第二次启动不再复制：旧目录后来改了也不覆盖知识库
    await writeFile(join(legacy, 'pages', '新易盛.md'), '---\ntitle: "新易盛"\ntype: "company"\n---\n\n旧目录后来又改了\n');
    server.close();
    await service.dispose();
    service = make();
    server = await serve(service);
    assert.equal((await get('/status')).pages, 1);
    assert.match(await readFile(join(dataDir, 'wiki', 'pages', '新易盛.md'), 'utf8'), /旧版知识库里的公司页/);
  } finally {
    server.close();
    await service.dispose();
  }
});

test('organizing works in batches: small text files go together with their text inline, pages and marks are written in bulk', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-batch-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-batch-data-'));
  const folder = join(home, '资料');
  await mkdir(folder, { recursive: true });
  for (let i = 1; i <= 12; i += 1) await writeFile(join(folder, '笔记' + String(i).padStart(2, '0') + '.md'), '# 笔记 ' + i + '\n光模块 800G 出货跟踪第 ' + i + ' 条。');
  await writeFile(join(folder, '深度报告.pdf'), '%PDF-1.4 fake');
  await writeFile(join(folder, '长文.md'), '# 长文\n' + '光模块供需。'.repeat(3000));
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const batches = [];
  const agent = {
    async run({ text }, { onEvent } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      batches.push(brief.batch);
      const pages = await tool('wiki_upsert_page', { job_id: jobId, pages: brief.batch.map((file) => ({ title: file.name.split('/').pop().replace(/\.[a-z]+$/, '') + ' 摘要', type: 'source', sources: [file.name] })) });
      assert.equal(pages.written, brief.batch.length);
      const marked = await tool('wiki_mark_source', { job_id: jobId, items: brief.batch.map((file) => ({ file: file.file, status: 'ingested', doc_type: '笔记' })) });
      assert.equal(marked.marked, brief.batch.length);
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE ' + brief.batch.length };
    },
    async reply() {},
  };
  service = createWikiService({ context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test' });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const post = async (path, body) => (await fetch(base + path, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) })).json();
  try {
    await post('/folders', { path: folder });
    const job = await post('/jobs', {});
    assert.equal(job.total, 14);
    const done = await waitFor(async () => { const s = await (await fetch(base + '/status')).json(); return s.job?.status === 'done' ? s : null; }, 8000);
    assert.equal(done.job.turns, 2, '14 files in 2 rounds instead of 4 files per round');
    assert.deepEqual(batches.map((batch) => batch.length), [10, 4]);
    const all = batches.flat();
    const pdf = all.find((file) => file.name.endsWith('.pdf'));
    assert.equal(pdf.read_with_tool, true);
    assert.equal(pdf.text, undefined);
    const small = all.find((file) => file.name.endsWith('笔记01.md'));
    assert.match(small.text, /800G 出货跟踪第 1 条/);
    const long = all.find((file) => file.name.endsWith('长文.md'));
    assert.equal(long.text_truncated, true);
    assert.ok(long.text.length <= 8000 && long.text_chars > 8000);
    assert.equal(done.files.ingested, 14);
    await assert.rejects(tool('wiki_upsert_page', { job_id: job.id }), /title|pages/);
  } finally {
    server.close();
    await service.dispose();
  }
});

test('search terms come from the knowledge graph: aliases count as direct mentions, neighbours widen sentiment and minutes retrieval', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-terms-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-terms-data-'));
  const folder = join(home, '资料');
  await mkdir(join(folder, '纪要'), { recursive: true });
  await writeFile(join(folder, '纪要', '2026-10-21 行业交流纪要.md'), '# 交流\n光模块 800G 报价持平，1.6T 送样加速。');
  await writeFile(join(folder, '纪要', '2026-10-20 新易盛调研纪要.md'), '# 调研\n新易盛海外订单饱满。');
  await writeFile(join(folder, '纪要', '2026-10-19 白酒调研纪要.md'), '# 调研\n茅台批价企稳。');
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  service = createWikiService({
    context: {}, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test',
    lookupName: (symbol) => ({ '300502.SZ': '新易盛', '300308.SZ': '中际旭创', '688498.SH': '源杰科技' })[symbol] ?? null,
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const get = async (path) => (await fetch(base + path)).json();
  try {
    await fetch(base + '/folders', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ path: folder }) });
    await tool('wiki_upsert_page', { pages: [
      { title: '光模块', type: 'segment', aliases: ['光模组'] },
      { title: '800G 光模块', type: 'product', relations: [{ type: 'belongs_to', target: '光模块', source: 's' }] },
      { title: '中际旭创', type: 'company', tickers: ['300308.SZ'] },
      { title: '源杰科技', type: 'company', tickers: ['688498.SH'] },
      { title: '新易盛', type: 'company', tickers: ['300502.SZ'], aliases: ['Eoptolink', '新易盛科技'], relations: [
        { type: 'belongs_to', target: '光模块', source: 's' }, { type: 'produces', target: '800G 光模块', source: 's' }, { type: 'competes', target: '中际旭创', source: 's' },
      ] },
    ] });
    await tool('wiki_upsert_page', { title: '源杰科技', relations: [{ type: 'supplies', target: '新易盛', note: '光芯片', source: 's' }] });
    const profile = service.searchProfile('300502.SZ', '新易盛');
    assert.deepEqual(profile.core.map((item) => item.term), ['新易盛', 'Eoptolink', '新易盛科技', '300502']);
    const labels = profile.related.map((item) => item.term + '|' + item.relation);
    for (const expected of ['光模块|所属环节', '光模组|所属环节', '800G 光模块|产品', '中际旭创|竞争对手', '源杰科技|供应商']) assert.ok(labels.includes(expected), expected);
    assert.ok(labels.indexOf('光模块|所属环节') < labels.indexOf('中际旭创|竞争对手'), 'segments and products rank before competitors');
    assert.deepEqual(profile.queries.map((item) => item.term), ['Eoptolink', '光模块', '800G 光模块'], 'source queries: aliases not containing the name, then segment and product');

    const segment = await get('/expand?q=' + encodeURIComponent('光模块'));
    assert.deepEqual(segment.terms, ['光模块', '光模组', '800G 光模块']);
    const company = await get('/expand?q=' + encodeURIComponent('新易盛'));
    assert.deepEqual(company.terms, ['新易盛', 'Eoptolink', '新易盛科技', '300502'], 'companies expand to their own names only');
    assert.deepEqual((await get('/expand?q=xyz')).terms, ['xyz']);

    const minutes = await get('/minutes?symbol=300502.SZ&name=' + encodeURIComponent('新易盛'));
    const titles = minutes.items.map((item) => item.title);
    assert.ok(titles.includes('2026-10-21 行业交流纪要'), 'industry minutes found through the segment');
    assert.ok(!titles.includes('2026-10-19 白酒调研纪要'));
    const industry = minutes.items.find((item) => item.title === '2026-10-21 行业交流纪要');
    assert.equal(industry.related, true);
    assert.ok(industry.reasons.some((reason) => reason.includes('光模块（所属环节）')));
    assert.equal(minutes.items.find((item) => item.title === '2026-10-20 新易盛调研纪要').related, false);

    const feed = assembleFeed({
      profile,
      own: [{ id: 'own-1', title: '新易盛 1.6T', summary: '', content: '新易盛 1.6T 放量', publishedAt: '2026-10-22' }, { id: 'own-2', title: '搜索返回的模糊结果', summary: '', content: '与名称无关', publishedAt: '2026-10-21' }],
      expanded: [{ id: 'term-1', title: '光模组价格', summary: '', content: '光模组报价下调', publishedAt: '2026-10-23' }, { id: 'term-2', title: '无关', summary: '', content: '白酒', publishedAt: '2026-10-24' }],
      pool: [{ id: 'pool-1', title: '海外', summary: '', content: 'Eoptolink 扩产', publishedAt: '2026-10-20' }, { id: 'own-1', title: '重复', content: '新易盛', publishedAt: '2026-10-25' }],
    });
    assert.deepEqual(feed.map((item) => [item.id, item.match.direct, item.match.via, item.match.terms.join(',')]), [
      ['term-1', false, 'related', '光模块（所属环节）'],
      ['own-1', true, 'name', '新易盛'],
      ['own-2', true, 'search', ''],
      ['pool-1', true, 'alias', '别名 Eoptolink'],
    ]);
  } finally {
    server.close();
    await service.dispose();
  }
});
