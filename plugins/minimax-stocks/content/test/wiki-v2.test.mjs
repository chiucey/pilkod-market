import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdtemp, mkdir, readFile, readdir, realpath, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import { deflateRawSync } from 'node:zlib';
import { buildNameIndex, findDuplicateGroups, mergeInto, mergePage, normalizeCompanyName, tickerFromText, validateUpsert } from '../miniapp/node/wiki-format.mjs';
import { officeTextFromBuffer } from '../miniapp/node/office-text.mjs';
import { createFolderPicker } from '../miniapp/node/folder-picker.mjs';
import { createWikiService } from '../miniapp/node/wiki-service.mjs';

const NOW = '2026-10-25T12:00:00.000Z';
const page = (input) => mergePage(null, validateUpsert(input), NOW);

function zip(entries) {
  const locals = [], centrals = [];
  let offset = 0;
  for (const entry of entries) {
    const data = Buffer.from(entry.data, 'utf8');
    const compressed = deflateRawSync(data);
    const name = Buffer.from(entry.name);
    const local = Buffer.alloc(30);
    local.writeUInt32LE(0x04034b50, 0); local.writeUInt16LE(20, 4); local.writeUInt16LE(8, 8);
    local.writeUInt32LE(compressed.length, 18); local.writeUInt32LE(data.length, 22); local.writeUInt16LE(name.length, 26);
    locals.push(local, name, compressed);
    const central = Buffer.alloc(46);
    central.writeUInt32LE(0x02014b50, 0); central.writeUInt16LE(20, 4); central.writeUInt16LE(20, 6); central.writeUInt16LE(8, 10);
    central.writeUInt32LE(compressed.length, 20); central.writeUInt32LE(data.length, 24); central.writeUInt16LE(name.length, 28); central.writeUInt32LE(offset, 42);
    centrals.push(central, name);
    offset += 30 + name.length + compressed.length;
  }
  const directory = Buffer.concat(centrals);
  const end = Buffer.alloc(22);
  end.writeUInt32LE(0x06054b50, 0); end.writeUInt16LE(entries.length, 8); end.writeUInt16LE(entries.length, 10);
  end.writeUInt32LE(directory.length, 12); end.writeUInt32LE(offset, 16);
  return Buffer.concat([...locals, directory, end]);
}
const docx = (text) => zip([{ name: '[Content_Types].xml', data: '<Types/>' }, { name: 'word/document.xml', data: '<w:document><w:body><w:p><w:r><w:t>' + text + '</w:t></w:r></w:p></w:body></w:document>' }]);

test('ticker detection, name index and company-name normalization', () => {
  assert.equal(tickerFromText('600519'), '600519.SH');
  assert.equal(tickerFromText('sz300308'), '300308.SZ');
  assert.equal(tickerFromText('0700.HK'), '0700.HK');
  assert.equal(tickerFromText('贵州茅台'), null);
  assert.equal(tickerFromText('800G'), null);
  const pages = [page({ title: '贵州茅台', type: 'company', tickers: ['600519.SH'], aliases: ['茅台'] })];
  const index = buildNameIndex(pages);
  for (const key of ['贵州茅台', '茅台', '600519.sh', '600519']) assert.equal(index.get(key), '贵州茅台', key);
  assert.equal(normalizeCompanyName('贵州茅台酒股份有限公司'), '贵州茅台酒');
  assert.equal(normalizeCompanyName('中际旭创（300308）'), '中际旭创');
  assert.equal(normalizeCompanyName('NVIDIA Corp.'), 'nvidia');
});

test('duplicate groups and merge keep one canonical company node', () => {
  const pages = [
    page({ title: '贵州茅台', type: 'company', tickers: ['600519.SH'], body: '主页面', relations: [{ type: 'competes', target: '五粮液', source: 'a' }] }),
    page({ title: '600519', type: 'company', body: '代码页', relations: [{ type: 'related', target: '贵州茅台', source: 'b' }] }),
    page({ title: '茅台', type: 'company', tickers: ['600519.SH'], relations: [{ type: 'competes', target: '五粮液', source: 'c' }] }),
    page({ title: '贵州茅台股份', type: 'company' }),
    page({ title: '五粮液', type: 'company', tickers: ['000858.SZ'] }),
    page({ title: '光模块', type: 'segment' }),
  ];
  pages[1].tickers = [];
  const groups = findDuplicateGroups(pages);
  assert.equal(groups.length, 1);
  assert.equal(groups[0].primary, '贵州茅台');
  assert.deepEqual(groups[0].pages.map((item) => item.id).sort(), ['600519', '茅台', '贵州茅台', '贵州茅台股份'].sort());
  assert.equal(groups[0].confidence, 'medium');
  assert.ok(groups[0].reasons.includes('同一股票代码 600519.SH'));
  const merged = mergeInto(pages[0], [pages[1], pages[2]], NOW);
  assert.deepEqual(merged.aliases.sort(), ['600519', '茅台'].sort());
  assert.equal(merged.relations.length, 1);
  assert.match(merged.body, /合并自「600519」/);
  assert.equal(findDuplicateGroups([pages[0], pages[4]]).length, 0, 'different tickers never merge');
});

test('office text extraction reads docx without dependencies', () => {
  const text = officeTextFromBuffer(docx('公司拜访：贵州茅台 &amp; 直销渠道'), /^word\/document\.xml$/);
  assert.match(text, /贵州茅台 & 直销渠道/);
});

test('folder picker drives the native dialog per platform', async () => {
  const calls = [];
  const run = (result) => async (command, args) => { calls.push([command, args]); return typeof result === 'function' ? result(command) : result; };
  const mac = createFolderPicker({ platform: 'darwin', home: tmpdir(), run: run({ code: 0, stdout: '/Users/x/研报/\n', stderr: '' }) });
  assert.equal(mac.kind, 'finder');
  assert.deepEqual(await mac.pick(), { path: '/Users/x/研报' });
  assert.equal(calls[0][0], 'osascript');
  assert.ok(calls[0][1].includes('activate'));
  const cancel = createFolderPicker({ platform: 'darwin', home: tmpdir(), run: run({ code: 1, stdout: '', stderr: 'execution error: User canceled. (-128)' }) });
  assert.deepEqual(await cancel.pick(), { cancelled: true });
  const win = createFolderPicker({ platform: 'win32', home: tmpdir(), run: run({ code: 3, stdout: '', stderr: '' }) });
  assert.deepEqual(await win.pick(), { cancelled: true });
  const linux = createFolderPicker({ platform: 'linux', home: tmpdir(), run: run((command) => (command === 'zenity' ? { code: 'ENOENT', stdout: '', stderr: '' } : { code: 0, stdout: '/home/x/docs\n', stderr: '' })) });
  assert.deepEqual(await linux.pick(), { path: '/home/x/docs' });
  assert.equal(createFolderPicker({ platform: 'aix' }).kind, null);
});

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

test('company uniqueness, stock materials, stock collection job and merges', async () => {
  const home = await realpath(await mkdtemp(join(tmpdir(), 'stocks-home-')));
  const dataDir = await mkdtemp(join(tmpdir(), 'stocks-data-'));
  const folder = join(home, '资料库');
  await mkdir(join(folder, '周报'), { recursive: true });
  await writeFile(join(folder, '贵州茅台2025三季报点评.md'), '# 点评\n贵州茅台 Q3 收入增长，直销占比提升。贵州茅台批价企稳。');
  await writeFile(join(folder, '周报', '白酒行业周报.txt'), '本周茅台批价企稳，五粮液动销平稳。');
  await writeFile(join(folder, '调研纪要.docx'), docx('公司拜访：贵州茅台直销渠道'));
  await writeFile(join(folder, '持仓表.csv'), '代码,名称\n600519,示例\n300750,示例');
  await writeFile(join(folder, '新能源.md'), '宁德时代电池出货。');
  const names = { '600519.SH': '贵州茅台', '000858.SZ': '五粮液' };
  let queue = Promise.resolve();
  const mutate = (operation) => { const run = queue.then(operation); queue = run.catch(() => {}); return run; };
  let service;
  const tool = (name, args) => service.mcpTools.find((item) => item.name === name).handler(args);
  const agent = {
    async run({ text }, { onEvent } = {}) {
      onEvent?.({ type: 'turn.started', sessionId: 's', turnId: 't', model: {} });
      const jobId = /"job_id":"([a-z0-9]+)"/.exec(text)[1];
      const brief = await tool('wiki_job_brief', { job_id: jobId });
      assert.equal(brief.task, 'stock');
      assert.equal(brief.stock.symbol, '600519.SH');
      assert.equal(brief.stock.existing_page.title, '贵州茅台');
      for (const file of brief.batch) {
        assert.ok(file.match_reasons.length > 0);
        if (file.name.includes('持仓表')) { await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'skipped', relevance: 'irrelevant', stock_note: '只是持仓列表' }); continue; }
        const merged = await tool('wiki_upsert_page', { job_id: jobId, title: '贵州茅台酒股份有限公司', type: 'company', tickers: ['600519'], body: '## 概况\n高端白酒龙头。', relations: [{ type: 'competes', target: '000858', source: file.name }] });
        assert.equal(merged.merged_into, '贵州茅台');
        if (file.name.includes('点评')) {
          await tool('wiki_upsert_page', { job_id: jobId, title: '贵州茅台2025三季报点评', type: 'source', sources: [file.name], body: '摘要：[[贵州茅台]]' });
          await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'ingested', relevance: 'core', stock_note: 'Q3 点评：直销占比提升', summary_page: '贵州茅台2025三季报点评' });
        } else {
          await tool('wiki_mark_source', { job_id: jobId, file: file.file, status: 'skipped', relevance: 'mentioned', stock_note: '提到批价企稳' });
        }
      }
      return { sessionId: 's', turnId: 't', status: 'finished', text: 'WIKI_BATCH_DONE' };
    },
    async reply() {},
  };
  const picker = { kind: 'finder', pick: async () => ({ path: folder }), dispose() {} };
  service = createWikiService({
    context: { agent }, dataDir, mutate, broadcast: () => {}, log: () => {}, home, platform: 'test', picker,
    lookupName: (symbol) => names[symbol] ?? null,
    resolveCompany: async (query) => (query.includes('茅台') || query.startsWith('600519') ? { symbol: '600519.SH', shortName: '贵州茅台' } : null),
  });
  const server = await serve(service);
  const base = 'http://127.0.0.1:' + server.address().port + '/api/wiki';
  const call = async (path, body) => { const response = await fetch(base + path, body === undefined ? undefined : { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) }); return { status: response.status, body: await response.json() }; };
  try {
    const picked = await call('/folders/pick', {});
    assert.equal(picked.body.picked, true);
    assert.equal((await call('/status')).body.picker, 'finder');

    const created = await tool('wiki_upsert_page', { title: '600519', type: 'company', aliases: ['茅台'], body: '白酒' });
    assert.equal(created.page.title, '贵州茅台', 'code title is canonicalized to the short name');
    const again = await tool('wiki_upsert_page', { title: '茅台', type: 'company' });
    assert.equal(again.merged_into, '贵州茅台');
    await tool('wiki_upsert_page', { title: '五粮液', type: 'company', tickers: ['000858.SZ'], relations: [{ type: 'competes', target: '600519.SH', source: 'x' }] });
    const wuliangye = (await call('/page?title=' + encodeURIComponent('五粮液'))).body.page;
    assert.equal(wuliangye.relations[0].target, '贵州茅台');
    const resolved = await tool('wiki_resolve_company', { query: '贵州茅台酒股份有限公司' });
    assert.equal(resolved.canonical_title, '贵州茅台');
    assert.equal(resolved.existing_page.title, '贵州茅台');

    const materials = (await call('/stock?symbol=600519.SH&name=' + encodeURIComponent('贵州茅台'))).body;
    const byName = Object.fromEntries(materials.materials.map((item) => [item.rel, item]));
    assert.ok(materials.keys.includes('茅台'));
    assert.equal(materials.materials[0].rel, '贵州茅台2025三季报点评.md');
    assert.ok(byName['周报/白酒行业周报.txt'].reasons.some((reason) => reason.kind === 'content' && reason.key === '茅台'));
    assert.ok(byName['调研纪要.docx'].reasons.some((reason) => reason.kind === 'content'));
    assert.ok(byName['持仓表.csv'].reasons.some((reason) => reason.key === '600519'));
    assert.equal(byName['新能源.md'], undefined);
    assert.equal(materials.pending, 4);
    assert.equal('path' in materials.materials[0], false);

    const job = await call('/jobs', { kind: 'stock', symbol: '600519.SH', name: '贵州茅台' });
    assert.equal(job.status, 200);
    assert.equal(job.body.kind, 'stock');
    const done = await waitFor(async () => { const s = (await call('/status')).body; return ['done', 'error'].includes(s.job?.status) ? s : null; });
    assert.equal(done.job.status, 'done', done.job.error);
    assert.deepEqual(done.job.relevance, { core: 1, mentioned: 2, irrelevant: 1 });

    const graph = (await call('/graph')).body;
    const maotai = graph.pages.filter((item) => item.tickers.includes('600519.SH'));
    assert.equal(maotai.length, 1, 'one company node for 600519');
    assert.ok(maotai[0].aliases.includes('贵州茅台酒股份有限公司'));
    assert.ok(maotai[0].relations.some((rel) => rel.type === 'competes' && rel.target === '五粮液'));
    assert.equal(graph.ghosts.length, 0);

    const detail = (await call('/page?id=' + encodeURIComponent('贵州茅台'))).body.page;
    assert.equal(detail.stockFiles.length, 3);
    assert.equal(detail.stockFiles[0].relevance, 'core');
    const files = (await call('/files')).body.folders[0].files;
    const report = files.find((file) => file.rel === '贵州茅台2025三季报点评.md');
    assert.equal(report.status, 'ingested');
    assert.equal(report.stocks[0].name, '贵州茅台');
    assert.equal(files.find((file) => file.rel === '持仓表.csv').status, 'new', 'irrelevant to one stock is not skipped globally');
    assert.equal(files.find((file) => file.rel === '调研纪要.docx').status, 'new');

    assert.equal((await call('/jobs', { kind: 'stock', symbol: '600519.SH' })).status, 409);
    await writeFile(join(folder, '周报', '白酒行业周报.txt'), '本周茅台批价继续企稳。');
    const refreshed = (await call('/stock?symbol=600519.SH&refresh=1')).body;
    assert.equal(refreshed.pending, 1);
    assert.equal(refreshed.materials.find((item) => item.rel === '周报/白酒行业周报.txt').linkStale, true);
    await tool('wiki_link_stock_file', { symbol: '600519.SH', file: refreshed.materials.find((item) => item.rel === '新能源.md')?.key ?? files.find((file) => file.rel === '新能源.md').key, relevance: 'irrelevant' });

    const root = join(dataDir, 'wiki', 'pages');
    await writeFile(join(root, '600519.md'), '---\ntitle: "600519"\ntype: "company"\n---\n\n旧的代码页\n');
    await writeFile(join(root, '贵州茅台股份.md'), '---\ntitle: "贵州茅台股份"\ntype: "company"\n---\n\n名称相近\n');
    await writeFile(join(root, '某基金.md'), '---\ntitle: "某基金"\ntype: "concept"\nrelations: [{"type":"related","target":"贵州茅台股份","source":"s","status":"confirmed"}]\n---\n\n持仓\n');
    await call('/reload', {});
    const dups = (await call('/duplicates')).body.groups;
    assert.equal(dups.length, 1);
    assert.equal(dups[0].primary, '贵州茅台');
    assert.equal((await call('/status')).body.duplicates, 1);
    const merged = await call('/merge', { into: '贵州茅台', from: ['600519', '贵州茅台股份'] });
    assert.equal(merged.body.archived, 2);
    assert.equal((await call('/duplicates')).body.groups.length, 0);
    const fund = (await call('/page?title=' + encodeURIComponent('某基金'))).body.page;
    assert.equal(fund.relations[0].target, '贵州茅台');
    assert.equal((await readdir(join(dataDir, 'wiki', 'archive'))).length, 2);
    assert.match(await readFile(join(dataDir, 'wiki', 'log.md'), 'utf8'), /合并节点/);
  } finally {
    await service.dispose();
    await new Promise((resolve) => server.close(resolve));
    await rm(home, { recursive: true, force: true });
    await rm(dataDir, { recursive: true, force: true });
  }
});
