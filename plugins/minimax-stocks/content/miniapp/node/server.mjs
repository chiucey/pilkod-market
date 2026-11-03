// @ts-check
import { createServer } from 'node:http';
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';
import { join } from 'node:path';
import { createConnectorGateway } from './market-connector.mjs';
import { createBarsStore } from './bars-store.mjs';
import { createZsxqBridge } from './zsxq-cli.mjs';
import { createMcpDispatcher } from './mcp-server.mjs';
import { marketClock, lastSettledTradingDate, marketDataDates, marketRefreshPlan, provisionalDailyBar } from './market-schedule.mjs';
import { hasSufficientFullHistory, needsFullHistoryRepair } from './history-policy.mjs';
import { createWikiService } from './wiki-service.mjs';
import { assembleFeed } from './search-terms.mjs';
import { createFolderPicker } from './folder-picker.mjs';
import {
  ALPHAPAI_SOURCE, ALPHAPAI_TYPES, FEED_TAGGED_TYPES as ALPHAPAI_FEED_TYPES, SENTIMENT_TYPES as ALPHAPAI_SENTIMENT_TYPES, TAGGED_TYPES as ALPHAPAI_TAGGED_TYPES, createAlphaPai,
} from './alphapai-client.mjs';
import { alphapaiPlan, dayOf, itemFacts, planResearch, researchHints, runResearch } from './research-search.mjs';

const MAX_BODY_BYTES = 2_000_000;
const PROVENANCE = 'hengsheng-market-connector';
const REFRESH_INTERVAL_MS = 60_000;
const SENTIMENT_TTL_MS = 60_000;
// 用知识图谱扩展检索时，额外的检索词（别名、所属环节、产品）刷新得慢一些，避免频繁调用来源。
const TERM_TTL_MS = 15 * 60_000;
const MAX_TERM_QUERIES = 4;
const MAX_FEED_ITEMS = 120;
const DEFAULT_SYMBOL = '600519.SH';
const ZSXQ_SOURCE = '知识星球';
const COMEIN_SOURCE = '进门财经';
const TDOCS_SOURCE = '腾讯文档';
// Alpha派 每次召回约 4–5 秒、有限流：行情页舆情 10 分钟刷新一次，在后台跑，不拖慢切换股票。
const ALPHAPAI_TTL_MS = 10 * 60_000;
const ALPHAPAI_DAYS = 30;
/** 研报、纪要更新慢：行情页按打标取最近 90 天。 */
const ALPHAPAI_LONG_DAYS = 90;
/** 行情页 Alpha派 舆情的取法版本：改为按公司打标后，旧的（按名称语义召回的）缓存要重新取。 */
const ALPHAPAI_FEED_VERSION = 'tagged-1';
/** 行情页每种 Alpha派 资料最多留几条（按时间取最新的），避免点评把研报、纪要挤掉。 */
const ALPHAPAI_FEED_CAPS = { 点评: 15, 社媒: 10, 纪要: 6, 研报: 6, 外资研报: 5 };
/** 发给页面的舆情不带 ref（Alpha派 列表里的时效 ID，只在服务端按需取全文时用）。 */
const stripRef = (item) => {
  if (!item || !item.ref) return item;
  const { ref: _ref, ...rest } = item;
  return rest;
};
/** 统一检索（research_search）可以指定的来源。 */
const RESEARCH_SOURCE_IDS = ['alphapai', 'comein', 'zsxq', 'tdocs', 'library', 'feed'];

/** @typedef {import('./miniapp-api.js').MiniAppContext} MiniAppContext */

export async function start(context) {
  const dataDir = context.dataDir;
  // 官方包 pluginId 为 minimax-stocks；本地开发副本（如 minimax-stocks-dev）的 MCP 服务名与路径随 pluginId 变化。
  const pluginId = typeof context.pluginId === 'string' && context.pluginId ? context.pluginId : 'minimax-stocks';
  const mcpPath = '/mcp/' + pluginId;
  await mkdir(dataDir, { recursive: true });
  const indexHtml = await readFile(join(context.pluginRoot, 'miniapp/client/index.html'), 'utf8');
  const clientAssets = new Map([
    ['/client/wiki.js', { type: 'text/javascript; charset=utf-8', body: await readFile(join(context.pluginRoot, 'miniapp/client/wiki.js'), 'utf8') }],
    ['/client/wiki.css', { type: 'text/css; charset=utf-8', body: await readFile(join(context.pluginRoot, 'miniapp/client/wiki.css'), 'utf8') }],
    ['/client/sources.js', { type: 'text/javascript; charset=utf-8', body: await readFile(join(context.pluginRoot, 'miniapp/client/sources.js'), 'utf8') }],
  ]);
  const gateway = createConnectorGateway(context);
  const barsStore = await createBarsStore(dataDir);
  const zsxq = createZsxqBridge();
  // Alpha派：用户在数据源页填的 API Key（dataDir/alphapai.json，权限 600）；没填时整个来源静默跳过。
  const alphapai = await createAlphaPai({ dataDir, log: (code, fields) => log(context, 'miniapp.runtime.' + code, fields) });

  let marketState = await loadJson(join(dataDir, 'market-data.json'), null);
  if (marketState && marketState.provenance !== PROVENANCE) marketState = null;
  /** @type {Record<string, Record<string, { updatedAt: string, items: any[] }>>} */
  const sentimentStore = await loadJson(join(dataDir, 'sentiments.json'), {});
  /** 扩展检索词的结果：{ [来源]: { [检索词]: { updatedAt, items } } }，多只股票共用（同一个环节只搜一次）。 */
  const termStore = await loadJson(join(dataDir, 'sentiment-terms.json'), {});
  let sentimentVersion = 0;
  /** @type {any[]} */
  let watchlist = normalizeWatchlist(await loadJson(join(dataDir, 'watchlist.json'), []));
  /** @type {Record<string, string>} */
  const nameCache = await loadJson(join(dataDir, 'names.json'), {});
  let currentSymbol = marketState?.symbol ?? DEFAULT_SYMBOL;

  // 舆情/行情能力校验：每个来源必须有对应的 Connector 工具或 CLI 才会被调用和刷新。
  let capabilities = {
    market: false,
    comein: false,
    search: false,
    tdocs: false,
    zsxq: { available: false, reason: 'unchecked', groupId: null },
    checkedAt: 0,
  };
  /** 正在进行的能力校验（启动时多处会同时触发，只跑一次）。 */
  let capabilityCheck = null;
  const connectionStatus = { market: 'pending', comein: 'pending', zsxq: 'pending', tdocs: 'pending', alphapai: 'pending' };
  /** Alpha派 正在刷新的股票（召回慢，避免同一只股票重复发起）。 */
  const alphapaiInflight = new Set();
  /** research_search 返回过的条目全文，供 research_read 读取（最多 400 条）。 */
  /** @type {Map<string, any>} */
  const researchCache = new Map();
  // 数据源页：每个来源最近一次成功 / 失败的时间与错误码，以及手动检测的结果（只在内存里）。
  /** @type {Record<string, { lastOkAt?: string, lastErrorAt?: string, lastError?: string }>} */
  const sourceHealth = { market: {}, comein: {}, tdocs: {}, zsxq: {}, alphapai: {} };
  /** @type {Record<string, { at: string, ok: boolean, ms: number, message: string }>} */
  const sourceTests = {};
  const noteSource = (key, ok, error) => {
    const entry = sourceHealth[key];
    if (!entry) return;
    if (ok) entry.lastOkAt = new Date().toISOString();
    else { entry.lastErrorAt = new Date().toISOString(); entry.lastError = String(error?.code ?? 'UNKNOWN').slice(0, 60); }
  };
  const picker = createFolderPicker();

  // Client 上报的浏览上下文（内存态，供 MCP get_view_brief 使用）。
  let viewState = null;

  let mutationQueue = Promise.resolve();
  const sseClients = new Set();
  const heartbeat = setInterval(() => {
    for (const response of sseClients) response.write(': heartbeat\n\n');
  }, 20_000);

  let refreshInFlight = null;
  const initialRefresh = refreshAll().catch(() => {});
  const refreshTimer = setInterval(() => { void refreshAll().catch(() => {}); }, REFRESH_INTERVAL_MS);

  // 资产页（资料库 + 知识图谱）：关联文件夹、后台 Agent 整理、MCP 查询工具；与行情共用 mutate 队列和 SSE。
  const wiki = createWikiService({
    context,
    pluginId,
    dataDir,
    mutate,
    broadcast: broadcastEvent,
    log: (code, fields) => log(context, code, fields),
    lookupName: (symbol) => nameCache[normalizeSymbol(symbol)] ?? (marketState && normalizeSymbol(marketState.symbol) === normalizeSymbol(symbol) ? marketState.shortName : null),
    resolveCompany: resolveCompanyIdentity,
    picker,
    // 行情页已经抓到的舆情：收入资产、扫描边际变化都从这里取原文，不信任页面传来的内容。
    // 和行情页同一份列表：直接检索到的 + 知识图谱扩展检索到的（别名、相邻节点），每条带命中原因。
    sentiments: () => [...new Set([...Object.keys(sentimentStore), ...watchlist.map((item) => item.symbol), ...(marketState ? [marketState.symbol] : [])].map((symbol) => normalizeSymbol(symbol)))]
      .map((symbol) => ({ symbol, shortName: nameFor(symbol), items: sentimentsFor(symbol) })),
    watchlist: () => watchlist.map((item) => item.symbol),
    currentSymbol: () => marketState?.symbol ?? currentSymbol,
    onClipsChanged: () => broadcast(),
    autoOrganize: true,
  });
  void wiki.brief();

  // Mini App-managed Streamable HTTP MCP：发布后 Host 将 minimax-stocks 指向本进程。
  const mcpDispatch = createMcpDispatcher({
    serverInfo: { name: pluginId, version: '1.4.0' },
    tools: [
      {
        name: 'watchlist_list',
        description: '查询自选股列表（含最新价、涨跌额、涨跌幅、更新时间）。',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        handler: async () => ({ items: watchlist }),
      },
      {
        name: 'watchlist_add',
        description: '添加自选股。query 可以是股票代码（600519 / 600519.SH / SH:600519）或中文简称、关键词；命中多个候选时返回 candidates 列表，请让用户选择后用精确代码重试。',
        inputSchema: { type: 'object', properties: { query: { type: 'string', description: '股票代码或中文简称/关键词' } }, required: ['query'], additionalProperties: false },
        handler: mcpWatchlistAdd,
      },
      {
        name: 'watchlist_remove',
        description: '从自选股移除一个标的。',
        inputSchema: { type: 'object', properties: { symbol: { type: 'string', description: '股票代码，如 600519.SH' } }, required: ['symbol'], additionalProperties: false },
        handler: async (args) => {
          const symbol = normalizeSymbol(String(args?.symbol ?? ''));
          const existed = watchlist.some((row) => row.symbol === symbol);
          if (existed) {
            await mutate(async () => {
              watchlist = watchlist.filter((item) => item.symbol !== symbol);
              await persistJson('watchlist.json', watchlist);
            });
            broadcast();
          }
          return { removed: existed, symbol };
        },
      },
      {
        name: 'watchlist_refresh',
        description: '立即刷新全部自选股报价（从行情 Connector 增量拉取），返回刷新后的列表。',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        handler: async () => {
          await refreshWatchlist({ scheduled: false });
          return { items: watchlist };
        },
      },
      {
        name: 'get_view_brief',
        description: '返回用户当前在股市页面上正在查看的内容摘要：所在页面（行情 / 资产 / 数据源）、当前股票与实时报价、图表视图（日K/分时/成交额、时间范围、均线开关）、最新 / 舆情 / 纪要板块（feedTab）、舆情筛选状态、最近点开阅读的舆情条目、自选股列表、资产页的页签（资料库 / 知识图谱 / 边际变化）、知识图谱的视图（图谱 / 产业链）与选中的节点。当用户提到"这只股票""这条消息/舆情""这个节点""刚才看的"等指代时，先调用本工具了解上下文。',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        handler: async () => ({ ...assembleBrief(), wiki: await wiki.brief() }),
      },
      {
        name: 'data_sources',
        description: '列出股市使用的数据源及连接状态：恒生行情、进门财经、腾讯文档、知识星球、Alpha派，以及后台 Agent、资料库、Spotlight 等本地能力。用户问「接了哪些数据」「知识星球连上没有」「Alpha派 的 Key 填了没有」时使用。',
        inputSchema: { type: 'object', properties: {}, additionalProperties: false },
        handler: async () => sourcesPayload(),
      },
      {
        name: 'research_search',
        description: '统一检索（舆情 / 投研资料）：一次查遍已经接入的数据源——Alpha派（点评、社媒、纪要、研报、外资研报，可加公告、指标、官方路演）、进门财经、知识星球、腾讯文档、本地资料库，以及行情页已经抓到的舆情；没接入的来源自动跳过，不报错。以公司或知识图谱节点为主体时（给 symbol，或 query 里有公司 / 环节 / 产品名），用它的名称、别名、代码同步检索，query 里其余的词当话题；Alpha派 不用别名：公司按 Alpha派 自己的公司打标（股票代码）取，话题再按「公司名 + 话题」语义召回，环节、产品、自由文本只用本名召回；neighbors=true 时再把相邻节点（所属环节、产品、上游、下游、客户、竞争对手）一起检索，用于发散研究。返回去重后的条目（来源、类型、日期、机构、命中原因 match、摘录）、各来源检索情况（searched / failed）、产业链地图 chain 和相关知识图谱节点；全文用 research_read。研究方法（先发散、再收敛）见 skill sentiment-search。',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: '检索词或问题：公司名、环节 / 产品名、话题，如「新易盛 1.6T 出货」「光芯片 涨价」「北美云厂商 资本开支」' },
            symbol: { type: 'string', description: '股票代码，如 300502.SZ。给了就以这家公司为主体：名称、别名、代码同步检索，query 当话题' },
            expand: { type: 'boolean', description: '是否用知识图谱里的别名同步检索，默认 true' },
            neighbors: { type: 'boolean', description: '是否把相邻节点（所属环节、产品、上下游、客户、竞争对手）一起检索，默认 false；发散研究时打开' },
            sources: { type: 'array', items: { type: 'string', enum: RESEARCH_SOURCE_IDS }, description: '只查这些来源：alphapai / comein（进门财经）/ zsxq（知识星球）/ tdocs（腾讯文档）/ library（本地资料库）/ feed（行情页已抓取的舆情）；默认全部已接入的' },
            alphapai_types: { type: 'array', items: { type: 'string', enum: Object.keys(ALPHAPAI_TYPES) }, description: 'Alpha派 召回的资料类型，默认 comment、social_media、roadShow、roadShow_ir、report。核对事实加 ann（公告）、edb（指标）；外资观点 foreign_report；美股业绩会 roadShow_us；基金经理观点 vps' },
            days: { type: 'integer', minimum: 1, maximum: 365, description: '外部来源按发布时间回看的天数，默认 30；本地资料库不按时间过滤' },
            limit: { type: 'integer', minimum: 1, maximum: 80, description: '最多返回多少条，默认 20（每个来源先保底几条，其余按相关度取）' },
            excerpt_chars: { type: 'integer', minimum: 80, maximum: 2000, description: '每条摘录的字数，默认 240' },
          },
          additionalProperties: false,
        },
        handler: researchSearch,
      },
      {
        name: 'research_read',
        description: '读取 research_search 结果的全文：传结果里的 id，一次最多 8 条。舆情返回正文；本地资料库的文件（id 以 file: 开头）返回正文，PDF 等读不了的格式返回 read_with_tool 路径，用读取工具打开；腾讯文档只能拿到标题和链接。',
        inputSchema: {
          type: 'object',
          properties: {
            ids: { type: 'array', items: { type: 'string' }, minItems: 1, maxItems: 8, description: 'research_search 结果里的 id' },
            max_chars: { type: 'integer', minimum: 500, maximum: 20000, description: '每条最多返回的字数，默认 8000' },
          },
          required: ['ids'],
          additionalProperties: false,
        },
        handler: researchRead,
      },
      ...wiki.mcpTools,
    ],
  });

  const server = createServer((request, response) => {
    void handleRequest(request, response).catch((error) => {
      log(context, 'miniapp.runtime.request_error', { code: error?.code ?? 'REQUEST_FAILED' });
      if (!response.headersSent && ['INVALID_SNAPSHOT', 'INVALID_WATCHLIST', 'INVALID_SENTIMENTS', 'BODY_TOO_LARGE', 'INVALID_JSON'].includes(error?.code)) {
        json(response, 400, { error: error.code.toLowerCase(), message: error.message });
      } else if (!response.headersSent) json(response, 500, { error: 'request_failed' });
      else response.end();
    });
  });

  async function handleRequest(request, response) {
    const url = new URL(request.url ?? '/', 'http://miniapp.local');
    if (url.pathname === mcpPath) {
      if (request.method !== 'POST') {
        response.writeHead(405, { allow: 'POST' });
        response.end();
        return;
      }
      const { payload } = await mcpDispatch(await readJson(request));
      if (payload === null) {
        response.writeHead(202);
        response.end();
      } else {
        json(response, 200, payload);
      }
      return;
    }
    if (await wiki.handle(request, response, url, { readJson, json })) return;
    if (request.method === 'GET' && clientAssets.has(url.pathname)) {
      const asset = clientAssets.get(url.pathname);
      response.writeHead(200, { 'content-type': asset.type, 'cache-control': 'no-store' });
      response.end(asset.body);
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/sources') {
      json(response, 200, await sourcesPayload());
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/sources/test') {
      const payload = await readJson(request);
      const id = typeof payload?.id === 'string' ? payload.id : 'all';
      const ids = id === 'all' ? SOURCE_TEST_IDS : SOURCE_TEST_IDS.filter((item) => item === id);
      if (!ids.length) return json(response, 404, { error: 'source_not_found' });
      await Promise.all(ids.map((item) => testSource(item)));
      json(response, 200, await sourcesPayload());
      return;
    }
    // Alpha派 API Key：保存前先校验（健康检查），Key 不回传给页面；清除时一并清掉已抓到的 Alpha派 舆情。
    if (url.pathname === '/api/sources/alphapai' && request.method === 'PUT') {
      const payload = await readJson(request);
      try {
        await saveAlphaPaiKey(payload?.apiKey);
      } catch (error) {
        log(context, 'miniapp.runtime.alphapai_key_rejected', { code: error?.code ?? 'UNKNOWN' });
        const status = error?.code === 'ALPHAPAI_KEY_FORMAT' || error?.code === 'ALPHAPAI_UNAUTHORIZED' ? 400 : 502;
        json(response, status, { error: String(error?.code ?? 'ALPHAPAI_FAILED').toLowerCase(), message: String(error?.message ?? '保存失败') });
        return;
      }
      json(response, 200, await sourcesPayload());
      return;
    }
    if (url.pathname === '/api/sources/alphapai' && request.method === 'DELETE') {
      await clearAlphaPaiKey();
      json(response, 200, await sourcesPayload());
      return;
    }
    // 舆情详情里的「加载全文」：Alpha派 列表里只有摘要的点评、研报、纪要，按需取全文（点评详情每天有额度）。
    if (request.method === 'POST' && url.pathname === '/api/sentiment/full') {
      const payload = await readJson(request);
      const id = typeof payload?.id === 'string' ? payload.id.slice(0, 200) : '';
      if (!id) return json(response, 400, { error: 'id_required' });
      const result = await loadAlphaPaiFull(id);
      if (result.loaded) broadcast();
      json(response, result.found ? 200 : 404, {
        loaded: result.loaded === true,
        ...(result.item ? { item: { id: result.item.id, content: result.item.content, summary: result.item.summary, preview: result.item.preview === true } } : {}),
        ...(result.message ? { message: result.message } : {}),
        ...(result.code ? { code: result.code } : {}),
      });
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/view-state') {
      viewState = sanitizeViewState(await readJson(request));
      json(response, 200, { ok: true });
      return;
    }
    if (request.method === 'GET' && url.pathname === '/dashboard') {
      response.writeHead(200, { 'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store' });
      response.end(indexHtml);
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/health') {
      json(response, 200, {
        ok: true,
        service: 'minimax-stocks',
        provenance: PROVENANCE,
        connector: gateway ? 'available' : 'unavailable',
        capabilities: {
          market: capabilities.market,
          comein: capabilities.comein,
          tdocs: capabilities.tdocs,
          zsxq: { available: capabilities.zsxq.available, reason: capabilities.zsxq.reason },
          alphapai: alphapai.configured,
        },
        symbol: currentSymbol,
        marketUpdatedAt: marketState?.fetchedAt ?? null,
        marketDataDate: marketState?.dataDate ?? null,
        marketSchedule: marketScheduleBrief(),
      });
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/search') {
      const query = (url.searchParams.get('q') ?? '').trim();
      if (query === '') return json(response, 400, { error: 'query_required' });
      if (gateway && capabilities.checkedAt === 0) await checkCapabilities();
      // 能力校验：search_instruments 在 Connector 清单中才调用，否则降级为本地代码/名称解析。
      if (gateway && capabilities.search) {
        try {
          const result = await gateway.searchInstruments(query, 8);
          let cacheDirty = false;
          for (const item of result.items) {
            if (!nameCache[item.symbol]) {
              nameCache[item.symbol] = item.shortName;
              cacheDirty = true;
            }
          }
          if (cacheDirty) await persistJson('names.json', nameCache);
          json(response, 200, { ok: true, source: 'connector', matchStatus: result.matchStatus, items: result.items });
          return;
        } catch (error) {
          log(context, 'miniapp.runtime.search_failed', { code: error?.code ?? 'UNKNOWN' });
        }
      }
      const local = resolveSymbol(query);
      json(response, 200, {
        ok: true,
        source: 'local',
        matchStatus: local ? 'exact' : 'not_found',
        items: local ? [{ symbol: local, shortName: nameCache[local] ?? local, exchangeName: exchangeForSymbol(local) }] : [],
      });
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/refresh') {
      const requested = url.searchParams.get('symbol');
      const target = requested ? resolveSymbol(requested) : currentSymbol;
      if (!target) {
        json(response, 404, { error: 'snapshot_unavailable', symbol: normalizeSymbol(requested) });
        return;
      }
      if (!gateway) {
        json(response, 503, { error: 'connector_unavailable' });
        return;
      }
      try {
        // Wait for the startup/timer refresh before issuing the user-requested forced refresh.
        if (refreshInFlight) await refreshInFlight;
        currentSymbol = target;
        await refreshMarket(target, { scheduled: false, force: true, awaitSentiments: true });
        if (!marketState) {
          json(response, 503, { error: 'market_unavailable' });
          return;
        }
        json(response, 200, assembleSnapshot());
      } catch (error) {
        log(context, 'miniapp.runtime.manual_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
        const status = error?.code === 'CONNECTOR_UNAVAILABLE' || error?.code === 'CONNECTOR_TOOL_MISSING' ? 503 : 502;
        json(response, status, { error: status === 503 ? 'connector_unavailable' : 'connector_error' });
      }
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/snapshot') {
      const requested = url.searchParams.get('symbol');
      if (!requested || (marketState && matchesSymbol(requested, marketState.symbol, marketState.shortName))) {
        if (!marketState) await initialRefresh;
        if (!marketState) {
          json(response, 503, { error: gateway ? 'market_unavailable' : 'connector_unavailable' });
          return;
        }
        json(response, 200, assembleSnapshot());
        return;
      }
      const target = resolveSymbol(requested);
      if (!target) {
        json(response, 404, { error: 'snapshot_unavailable', symbol: normalizeSymbol(requested) });
        return;
      }
      if (!gateway) {
        json(response, 503, { error: 'connector_unavailable' });
        return;
      }
      try {
        // 秒开路径：本地缓存命中时立即返回，连接器/CLI 刷新放到后台，完成后 SSE 通知页面。
        if (await serveFromCache(target)) {
          currentSymbol = target;
          json(response, 200, assembleSnapshot());
          void backgroundRefresh(target).catch((error) => {
            log(context, 'miniapp.runtime.background_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
          });
          return;
        }
        // 首次访问：只同步等全量K线，报价/分时/简称/舆情由后台补齐后 SSE 通知。
        const initialNow = new Date();
        const initialClock = marketClock(initialNow);
        const fullStartDate = fullHistoryStartDate(initialNow);
        const bundle = await gateway.fetchDailyBars(target, {
          startDate: fullStartDate,
          endDate: dailyQueryEndDate(initialNow, initialClock, lastSettledTradingDate(initialNow)),
          warmupBars: 249,
        });
        if (bundle.items.length === 0) fail('CONNECTOR_EMPTY_RESULT', `no daily bars for ${target}`);
        await barsStore.setBars(target, bundle.items, {
          full: hasSufficientFullHistory(bundle, fullStartDate),
          basisVersion: bundle.basisVersion,
          revision: bundle.revision,
          coverageComplete: bundle.coverageComplete,
        });
        await serveFromCache(target);
        currentSymbol = target;
        json(response, 200, assembleSnapshot());
        void backgroundRefresh(target).catch((error) => {
          log(context, 'miniapp.runtime.background_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
        });
      } catch (error) {
        log(context, 'miniapp.runtime.symbol_switch_failed', { code: error?.code ?? 'UNKNOWN' });
        if (error?.code === 'CONNECTOR_EMPTY_RESULT' || error?.disposition === 'provider_reported') {
          json(response, 404, { error: 'snapshot_unavailable', symbol: target });
        } else if (error?.code === 'CONNECTOR_UNAVAILABLE') {
          json(response, 503, { error: 'connector_unavailable' });
        } else {
          json(response, 502, { error: 'connector_error' });
        }
      }
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/watchlist') {
      json(response, 200, { items: watchlist });
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/sentiment') {
      json(response, 200, { symbol: currentSymbol, items: sentimentsFor(currentSymbol).map(stripRef) });
      return;
    }
    if (request.method === 'GET' && url.pathname.startsWith('/api/sentiment/')) {
      const id = decodeURIComponent(url.pathname.slice('/api/sentiment/'.length));
      const item = sentimentsFor(currentSymbol).find((entry) => entry.id === id);
      if (!item) return json(response, 404, { error: 'sentiment_not_found' });
      json(response, 200, stripRef(item));
      return;
    }
    if (request.method === 'GET' && url.pathname === '/api/events') {
      response.writeHead(200, {
        'content-type': 'text/event-stream; charset=utf-8',
        'cache-control': 'no-cache',
        connection: 'keep-alive',
      });
      response.write(`event: ready\ndata: ${JSON.stringify({ symbol: currentSymbol })}\n\n`);
      sseClients.add(response);
      request.on('close', () => sseClients.delete(response));
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/ingest/sentiments') {
      const payload = await readJson(request);
      if (!isRecord(payload) || typeof payload.symbol !== 'string' || typeof payload.source !== 'string' || payload.source.trim() === '') {
        fail('INVALID_SENTIMENTS', 'symbol and source are required');
      }
      const symbol = normalizeSymbol(payload.symbol);
      const items = validateSentimentItems(payload.items, payload.source.trim());
      await mutate(async () => {
        sentimentStore[symbol] = sentimentStore[symbol] ?? {};
        sentimentStore[symbol][payload.source.trim()] = { updatedAt: new Date().toISOString(), items };
        sentimentVersion += 1;
        await persistJson('sentiments.json', sentimentStore);
      });
      broadcast();
      wiki.onSentimentsUpdated();
      json(response, 200, { ok: true, symbol, source: payload.source.trim(), count: items.length });
      return;
    }
    if (request.method === 'POST' && url.pathname === '/api/watchlist') {
      const payload = await readJson(request);
      if (!isRecord(payload) || typeof payload.symbol !== 'string' || payload.symbol.trim() === '') fail('INVALID_WATCHLIST', 'symbol is required');
      const symbol = resolveSymbol(payload.symbol);
      if (!symbol) fail('INVALID_WATCHLIST', 'use a stock code such as 600519.SH');
      const item = await addWatchlistSymbol(symbol);
      json(response, 200, { ok: true, item });
      return;
    }
    if (request.method === 'DELETE' && url.pathname.startsWith('/api/watchlist/')) {
      const symbol = normalizeSymbol(decodeURIComponent(url.pathname.slice('/api/watchlist/'.length)));
      await mutate(async () => {
        watchlist = watchlist.filter((item) => normalizeSymbol(item.symbol) !== symbol);
        await persistJson('watchlist.json', watchlist);
      });
      json(response, 200, { ok: true, symbol });
      return;
    }
    json(response, 404, { error: 'not_found' });
  }

  async function addWatchlistSymbol(symbol) {
    if (!watchlist.some((row) => row.symbol === symbol)) {
      const item = {
        symbol,
        shortName: nameCache[symbol] ?? (marketState && marketState.symbol === symbol ? marketState.shortName : symbol),
        exchange: exchangeForSymbol(symbol),
        price: null, change: null, changePercent: null, previousClose: null,
        updatedAt: new Date().toISOString(),
        status: 'pending',
      };
      await mutate(async () => {
        watchlist = [...watchlist, item];
        await persistJson('watchlist.json', watchlist);
      });
      broadcast();
      void refreshWatchlist().catch(() => {});
    }
    return watchlist.find((row) => row.symbol === symbol);
  }

  async function mcpWatchlistAdd(args) {
    const query = String(args?.query ?? '').trim();
    if (query === '') fail('INVALID_ARGUMENTS', 'query is required');
    let symbol = resolveSymbol(query);
    if (!symbol && gateway && capabilities.search) {
      const result = await gateway.searchInstruments(query, 5);
      if (result.matchStatus === 'exact' || result.items.length === 1) {
        symbol = result.items[0]?.symbol ?? null;
      } else if (result.items.length > 1) {
        return { added: false, reason: 'multiple_candidates', candidates: result.items };
      }
    }
    if (!symbol) return { added: false, reason: 'not_found', query };
    const item = await addWatchlistSymbol(symbol);
    return { added: true, item };
  }

  function sanitizeViewState(payload) {
    if (!isRecord(payload)) fail('INVALID_JSON', 'view state must be an object');
    const text = (value, max) => (typeof value === 'string' ? value.slice(0, max) : '');
    return {
      view: ['daily', 'intraday', 'turnover'].includes(payload.view) ? payload.view : 'daily',
      range: ['3m', '1y', '3y'].includes(payload.range) ? payload.range : '3m',
      ma: Array.isArray(payload.ma) ? payload.ma.filter((value) => Number.isFinite(value)).slice(0, 6) : [],
      sentimentSource: text(payload.sentimentSource, 16) || 'all',
      sentimentQuery: text(payload.sentimentQuery, 100),
      theme: ['light', 'dark'].includes(payload.theme) ? payload.theme : 'light',
      watchlistOpen: payload.watchlistOpen === true,
      recentSentimentIds: Array.isArray(payload.recentSentimentIds)
        ? payload.recentSentimentIds.filter((value) => typeof value === 'string').slice(0, 5)
        : [],
      page: ['assets', 'sources'].includes(payload.page) ? payload.page : 'market',
      assetsTab: ['files', 'graph', 'changes'].includes(payload.assetsTab) ? payload.assetsTab : 'files',
      marketFeed: ['latest', 'minutes'].includes(payload.marketFeed) ? payload.marketFeed : 'sentiment',
      wikiView: payload.wikiView === 'chain' ? 'chain' : 'graph',
      wikiPage: text(payload.wikiPage, 120),
      wikiIndustry: text(payload.wikiIndustry, 80),
      updatedAt: new Date().toISOString(),
    };
  }

  function assembleBrief() {
    const viewLabels = { daily: '日K', intraday: '分时', turnover: '成交额' };
    const rangeLabels = { '3m': '近3个月', '1y': '近1年', '3y': '近3年' };
    const sentiments = marketState ? sentimentsFor(marketState.symbol) : [];
    const bySource = {};
    for (const item of sentiments) bySource[item.source] = (bySource[item.source] ?? 0) + 1;
    const recentlyViewedSentiments = (viewState?.recentSentimentIds ?? [])
      .map((id) => sentiments.find((item) => item.id === id))
      .filter((item) => item !== undefined)
      .map((item) => ({
        id: item.id, source: item.source, title: item.title,
        publishedAt: item.publishedAt,
        summary: (item.summary ?? '').slice(0, 120),
        ...(item.url ? { url: item.url } : {}),
      }));
    return {
      currentStock: marketState ? {
        symbol: marketState.symbol,
        shortName: marketState.shortName,
        exchange: marketState.exchange,
        quote: marketState.quote,
        lastTradingDate: marketState.daily.at(-1)?.date ?? null,
        intradayDate: marketState.intradayDate,
        dataRefreshedAt: marketState.fetchedAt,
      } : null,
      viewing: viewState ? {
        page: viewState.page === 'assets' ? '资产' : viewState.page === 'sources' ? '数据源' : '行情',
        ...(viewState.page === 'assets' ? {
          assetsTab: ({ graph: '知识图谱', changes: '边际变化' })[viewState.assetsTab] ?? '资料库',
          // 图谱视图只在用户正看着知识图谱页签时报告；选中的节点一直保留，供「刚才那个节点」这类指代使用。
          ...(viewState.assetsTab === 'graph' ? {
            wikiView: viewState.wikiView === 'chain' ? '产业链' : '知识图谱',
            wikiIndustry: viewState.wikiIndustry || null,
          } : {}),
          wikiSelectedPage: viewState.wikiPage ? (wiki.pageTitle(viewState.wikiPage) ?? viewState.wikiPage.replace(/^ghost:/, '')) : null,
        } : {}),
        ...(viewState.page === 'market' ? { feedTab: ({ latest: '最新', minutes: '纪要' })[viewState.marketFeed] ?? '舆情' } : {}),
        chartTab: viewLabels[viewState.view] ?? viewState.view,
        chartRange: viewState.view === 'daily' ? (rangeLabels[viewState.range] ?? viewState.range) : null,
        maLines: viewState.view === 'daily' ? viewState.ma.map((period) => `MA${period}`) : [],
        sentimentSourceFilter: viewState.sentimentSource,
        sentimentSearch: viewState.sentimentQuery || null,
        theme: viewState.theme,
        watchlistPanelOpen: viewState.watchlistOpen,
        reportedAt: viewState.updatedAt,
      } : null,
      recentlyViewedSentiments,
      sentimentCounts: { total: sentiments.length, bySource },
      watchlist: watchlist.map((item) => ({ symbol: item.symbol, shortName: item.shortName, price: item.price, changePercent: item.changePercent })),
      ...(viewState ? {} : { note: '页面尚未上报浏览状态（可能未打开或仍是旧版本页面）。' }),
    };
  }

  /** 公司身份解析：代码 → 简称（缓存 / 进门财经），名称 → 代码（恒生代码搜索）。结果写入 names.json，供 Wiki 公司唯一化使用。 */
  async function resolveCompanyIdentity(query) {
    const text = String(query ?? '').trim();
    if (!text) return null;
    if (gateway && capabilities.checkedAt === 0) await checkCapabilities().catch(() => {});
    const remember = async (symbol, name) => {
      if (symbol && name && nameCache[symbol] !== name) { nameCache[symbol] = name; await persistJson('names.json', nameCache).catch(() => {}); }
    };
    const direct = resolveSymbol(text);
    if (direct) {
      let shortName = nameCache[direct] ?? watchlist.find((row) => row.symbol === direct && row.shortName !== direct)?.shortName ?? null;
      if (!shortName && gateway && capabilities.comein) shortName = await gateway.fetchShortName(direct).catch(() => null);
      if (!shortName && gateway && capabilities.search) {
        const found = await gateway.searchInstruments(direct.slice(0, 6), 3).catch(() => null);
        shortName = found?.items.find((item) => normalizeSymbol(item.symbol) === direct)?.shortName ?? null;
      }
      await remember(direct, shortName);
      return { symbol: direct, shortName };
    }
    if (gateway && capabilities.search) {
      const found = await gateway.searchInstruments(text, 5).catch(() => null);
      if (found?.items.length) {
        for (const item of found.items) await remember(normalizeSymbol(item.symbol), item.shortName);
        const exact = found.matchStatus === 'exact' || found.items.length === 1 ? found.items[0] : found.items.find((item) => item.shortName === text);
        if (exact) return { symbol: normalizeSymbol(exact.symbol), shortName: exact.shortName };
        return { symbol: null, shortName: null, candidates: found.items.map((item) => ({ symbol: normalizeSymbol(item.symbol), shortName: item.shortName })) };
      }
    }
    return null;
  }

  const SOURCE_DEFS = [
    { id: 'hengsheng_market', key: 'market', name: '恒生行情', type: 'connector', provider: 'hengsheng_market', usage: '实时报价、日K、分时、代码与简称搜索；也用于 Wiki 公司节点的代码 ↔ 简称解析', tools: [['get_latest_quote', true], ['get_daily_bars', true], ['get_intraday_series', true], ['search_instruments', false]] },
    { id: 'comein', key: 'comein', name: '进门财经', type: 'connector', provider: 'comein', usage: '券商点评舆情；股票简称解析', tools: [['searchAnalystComments', true], ['get_stock_details', false]] },
    { id: 'tencentdocs', key: 'tdocs', name: '腾讯文档', type: 'connector', provider: 'tencentdocs', usage: '按股票简称检索你的腾讯文档，作为舆情来源', tools: [['manage.search_file', true]] },
    { id: 'zsxq', key: 'zsxq', name: '知识星球', type: 'cli', usage: '在你加入的星球里检索与当前股票相关的话题（本机 zsxq-cli，只读）' },
    { id: 'alphapai', key: 'alphapai', name: ALPHAPAI_SOURCE, type: 'apikey', usage: '按公司打标取点评、社媒、纪要、研报（含外资）；统一检索还能查公告、指标' },
  ];
  const SOURCE_TEST_IDS = ['hengsheng_market', 'comein', 'tencentdocs', 'zsxq', 'alphapai', 'agent'];
  /** 限时等待；结束后清掉计时器（不然检测完还会把进程多挂 25 秒）。 */
  const withTimeout = (promise, ms) => {
    let timer;
    const timeout = new Promise((_, reject) => { timer = setTimeout(() => reject(Object.assign(new Error('timeout'), { code: 'TIMEOUT' })), ms); });
    return Promise.race([promise, timeout]).finally(() => clearTimeout(timer));
  };

  /** 手动检测：每个来源做一次只读调用，记录耗时和结果。 */
  async function testSource(id) {
    const started = Date.now();
    const sample = marketState?.symbol ?? DEFAULT_SYMBOL;
    const sampleName = marketState?.shortName ?? nameCache[sample] ?? '贵州茅台';
    const record = (ok, message, error) => {
      sourceTests[id] = { at: new Date().toISOString(), ok, ms: Date.now() - started, message: String(message).slice(0, 160) };
      const def = SOURCE_DEFS.find((item) => item.id === id);
      if (def) noteSource(def.key, ok, error);
    };
    try {
      if (id === 'agent') {
        if (!context.agent) return record(false, '未获得后台 Agent 权限（需要 MiniMax Code 3.1.2+）');
        const models = await withTimeout(context.agent.models(), 15_000);
        const current = models?.models?.find((model) => model.providerId === models.default?.providerId && model.modelId === models.default?.modelId);
        return record(true, '可用 · 默认模型 ' + (current?.displayName ?? models?.default?.modelId ?? '未知'));
      }
      if (id === 'zsxq') {
        const result = await withTimeout(zsxq.checkAvailable({ force: true }), 25_000);
        capabilities = { ...capabilities, zsxq: result };
        if (result.available) return record(true, '已登录 · 加入了 ' + (result.groupCount ?? 1) + ' 个星球');
        return record(false, ({ cli_missing: '本机没有安装 zsxq-cli', cli_error: 'zsxq-cli 未登录或运行出错', no_group: '账号下没有加入的星球' })[result.reason] ?? '暂不可用', { code: result.reason });
      }
      if (id === 'alphapai') {
        if (!alphapai.configured) return record(false, '还没有填写 API Key');
        await withTimeout(alphapai.hello(), 25_000);
        return record(true, '鉴权正常 · Key 尾号 ' + alphapai.status().masked.slice(-4));
      }
      if (!gateway) return record(false, 'Mini App 没有获得 Connector 授权');
      await checkCapabilities();
      if (id === 'hengsheng_market') {
        if (capabilities.search) {
          const found = await withTimeout(gateway.searchInstruments(sample.slice(0, 6), 1), 20_000);
          return record(true, '代码搜索正常：' + sample + ' → ' + (found.items[0]?.shortName ?? '无结果'));
        }
        const quote = await withTimeout(gateway.fetchLatestQuote(sample), 20_000);
        return record(true, '报价正常：' + sample + (quote?.quote?.price ? ' ' + quote.quote.price : ''));
      }
      if (id === 'comein') {
        const name = await withTimeout(gateway.fetchShortName(sample), 20_000);
        return record(Boolean(name), name ? '简称解析正常：' + sample + ' → ' + name : '调用成功但没有返回简称');
      }
      if (id === 'tencentdocs') {
        const docs = await withTimeout(gateway.fetchTencentDocs(sampleName), 20_000);
        return record(true, '检索「' + sampleName + '」返回 ' + docs.length + ' 个文档');
      }
    } catch (error) {
      log(context, 'miniapp.runtime.source_test_failed', { id, code: error?.code ?? 'UNKNOWN' });
      const known = ({ TIMEOUT: '超时没有响应', CONNECTOR_TOOL_MISSING: '对应的 Connector 工具不在清单里', CONNECTOR_UNAVAILABLE: 'Connector 暂不可用' })[error?.code];
      return record(false, known ?? (String(error?.code ?? '').startsWith('ALPHAPAI_') ? String(error.message) : '调用失败（' + (error?.code ?? '未知错误') + '）'), error);
    }
    return record(false, '未知数据源');
  }

  async function sourcesPayload() {
    const names = gateway ? await gateway.listToolNames().catch(() => null) : null;
    const statusFor = (def, presentRequired, total) => {
      const health = sourceHealth[def.key] ?? {};
      const test = sourceTests[def.id];
      const lastOk = Date.parse(health.lastOkAt ?? '') || 0;
      const lastErr = Date.parse(health.lastErrorAt ?? '') || 0;
      if (!presentRequired) return 'unavailable';
      if (lastErr > lastOk) return 'error';
      if (lastOk || test?.ok) return presentRequired < total ? 'degraded' : 'connected';
      return presentRequired < total ? 'degraded' : 'ready';
    };
    const third = SOURCE_DEFS.map((def) => {
      const health = sourceHealth[def.key] ?? {};
      const base = { id: def.id, name: def.name, type: def.type, usage: def.usage, lastOkAt: health.lastOkAt ?? null, lastErrorAt: health.lastErrorAt ?? null, lastError: health.lastError ?? null, test: sourceTests[def.id] ?? null };
      if (def.type === 'cli') {
        const z = capabilities.zsxq;
        const status = z.available ? (Date.parse(health.lastErrorAt ?? '') > Date.parse(health.lastOkAt ?? '') ? 'error' : 'connected') : (z.reason === 'unchecked' ? 'checking' : 'unavailable');
        return { ...base, access: '本机 CLI · zsxq-cli', status, detail: z.available ? '已登录，加入了 ' + (z.groupCount ?? 1) + ' 个星球' : ({ cli_missing: '本机没有安装 zsxq-cli', cli_error: 'zsxq-cli 未登录或运行出错', no_group: '账号下没有加入的星球', unchecked: '尚未检测' })[z.reason] ?? '暂不可用', hint: z.available ? null : '安装 zsxq-cli 并登录后点「检测」', tools: [] };
      }
      if (def.type === 'apikey') {
        const key = alphapai.status();
        const test = sourceTests[def.id];
        const lastOk = Date.parse(health.lastOkAt ?? '') || 0;
        const lastErr = Date.parse(health.lastErrorAt ?? '') || 0;
        const status = !key.configured ? 'unavailable' : lastErr > lastOk ? 'error' : lastOk || test?.ok ? 'connected' : 'ready';
        return {
          ...base,
          access: 'API Key · open-api.rabyte.cn',
          status,
          detail: key.configured ? '已保存 Key（' + key.length + ' 位，尾号 ' + key.masked.slice(-4) + '）' : '还没有填写 API Key',
          hint: key.configured ? null : '填入 API Key 即可使用。Key 可在 Alpha派 管理后台获取，或联系客户经理。',
          tools: [],
          apiKey: { configured: key.configured, masked: key.masked, savedAt: key.savedAt },
        };
      }
      const provided = names ? [...names].filter((name) => name.startsWith(def.provider + '.')).map((name) => name.slice(def.provider.length + 1)) : [];
      const tools = def.tools.map(([name, required]) => ({ name, required, present: provided.includes(name) }));
      const required = tools.filter((tool) => tool.required);
      const presentRequired = required.filter((tool) => tool.present).length;
      const status = !gateway ? 'unavailable' : statusFor(def, presentRequired, required.length);
      return {
        ...base,
        access: 'Host Connector · ' + def.provider,
        status,
        detail: !gateway ? 'Mini App 没有获得 Connector 授权' : !provided.length ? '没有连接这个 App' : presentRequired < required.length ? '缺少必需工具：' + required.filter((tool) => !tool.present).map((tool) => tool.name).join('、') : '工具齐全（' + provided.length + ' 个）',
        hint: provided.length ? null : '在 MiniMax Code 里连接「' + def.name + '」App 后点「检测」',
        tools,
        extraTools: provided.filter((name) => !def.tools.some(([tool]) => tool === name)).slice(0, 20),
      };
    });
    const wikiBrief = await wiki.brief();
    const local = [
      { id: 'agent', name: '后台 Agent', status: context.agent ? (sourceTests.agent && !sourceTests.agent.ok ? 'error' : 'connected') : 'unavailable', detail: context.agent ? '可以运行资料整理和个股归集任务' : '需要 MiniMax Code 3.1.2+ 的 Mini App Agent 权限', usage: '整理资料到知识图谱、归集个股资料、扫描舆情中的边际变化', test: sourceTests.agent ?? null },
      { id: 'library', name: '本地资料库', status: wikiBrief?.folders ? 'connected' : 'unavailable', detail: wikiBrief ? (wikiBrief.folders ? wikiBrief.folders + ' 个关联文件夹 · ' + wikiBrief.pages + ' 个知识图谱节点' : '还没有关联资料文件夹') : '读取失败', usage: '研报、纪要、笔记等本地文件（只读）' },
      { id: 'minutes', name: '纪要', status: wikiBrief?.folders ? 'connected' : 'unavailable', detail: wikiBrief?.folders ? '来自资料库：文件名识别 + Agent 打标后按股票匹配' : '还没有关联资料文件夹', usage: '行情页「纪要」板块；也进知识图谱和边际变化' },
      { id: 'picker', name: '文件夹选择框', status: picker.kind ? 'connected' : 'unavailable', detail: ({ finder: 'macOS 访达', windows: 'Windows 文件夹选择框', linux: 'zenity / kdialog' })[picker.kind] ?? '当前系统不支持', usage: '在资产页用系统对话框选择要关联的文件夹' },
      { id: 'spotlight', name: 'Spotlight 全文检索', status: process.platform === 'darwin' ? 'connected' : 'unavailable', detail: process.platform === 'darwin' ? '用于在 PDF 等格式里查找个股相关资料' : '仅 macOS 可用；其他系统只检索文本与 Office 文档', usage: '个股资料自动匹配' },
    ];
    return { checkedAt: new Date().toISOString(), connector: gateway ? 'available' : 'unavailable', thirdParty: third, local };
  }

  function marketScheduleBrief() {
    const clock = marketClock();
    return {
      timezone: 'Asia/Shanghai',
      date: clock.date,
      phase: clock.phase,
      trading: clock.trading,
      rule: '交易时段每60秒；15:05后每个标的一次收盘终刷',
    };
  }

  function assembleSnapshot() {
    const zsxqLabel = capabilities.zsxq.available
      ? 'CLI 已接入'
      : ({ cli_missing: 'CLI 未安装', cli_error: 'CLI 未就绪', no_group: '未加入星球', unchecked: '检测中' }[capabilities.zsxq.reason] ?? '暂不可用');
    return {
      ...marketState,
      sentiments: markClipped(sentimentsFor(marketState.symbol)).map(stripRef),
      searchScope: searchScope(marketState.symbol),
      watchlist,
      sourceConnections: [
        { name: '恒生行情', status: capabilities.market && (connectionStatus.market === 'ok' || Boolean(marketState?.dataDate)) ? 'verified' : 'error', label: connectionStatus.market === 'ok' ? '已接入 · 60秒同步' : (capabilities.market && marketState?.dataDate ? '已接入 · 本地缓存' : '暂不可用') },
        { name: COMEIN_SOURCE, status: capabilities.comein && connectionStatus.comein !== 'error' ? 'verified' : 'error', label: capabilities.comein ? (connectionStatus.comein === 'error' ? '读取失败' : '已接入') : '暂不可用' },
        { name: TDOCS_SOURCE, status: capabilities.tdocs && connectionStatus.tdocs !== 'error' ? 'verified' : 'error', label: capabilities.tdocs ? (connectionStatus.tdocs === 'error' ? '读取失败' : '已接入') : '暂不可用' },
        { name: ZSXQ_SOURCE, status: capabilities.zsxq.available && connectionStatus.zsxq !== 'error' ? 'verified' : 'error', label: zsxqLabel },
        { name: ALPHAPAI_SOURCE, status: alphapai.configured && connectionStatus.alphapai !== 'error' ? 'verified' : 'error', label: alphapai.configured ? (connectionStatus.alphapai === 'error' ? '读取失败' : '已接入') : '未填写 Key' },
      ],
      marketSchedule: marketScheduleBrief(),
      provenance: PROVENANCE,
    };
  }

  /** 已收入资产的舆情带上 clipped，行情页据此显示「已收入」。 */
  function markClipped(items) {
    const ids = wiki.clippedIds();
    return ids.size ? items.map((item) => (ids.has(item.id) ? { ...item, clipped: true } : item)) : items;
  }

  function nameFor(symbol) {
    const key = normalizeSymbol(symbol);
    return nameCache[key] ?? watchlist.find((item) => normalizeSymbol(item.symbol) === key)?.shortName ?? (marketState && normalizeSymbol(marketState.symbol) === key ? marketState.shortName : null);
  }

  /** @type {Map<string, { version: number, profile: any, items: any[] }>} */
  const assembled = new Map();
  /**
   * 一只股票的舆情：按名称直接检索到的，加上用知识图谱扩展检索到的——别名和所属环节 / 产品的额外检索结果，
   * 以及其他股票舆情里提到这家公司或它相邻节点的。每条带 match：直接提及（名称 / 别名 / 代码）还是关联（相邻节点）。
   */
  function sentimentsFor(symbol) {
    const key = normalizeSymbol(symbol);
    const profile = wiki.searchProfile(key, nameFor(key));
    const memo = assembled.get(key);
    if (memo && memo.version === sentimentVersion && memo.profile === profile) return memo.items;
    const items = assembleFeed({
      own: Object.values(sentimentStore[key] ?? {}).flatMap((entry) => entry?.items ?? []),
      // Alpha派 不用别名检索（公司本身按它的公司打标取），旧缓存里按别名召回的结果也不再用。
      expanded: profile.queries.flatMap((query) => Object.entries(termStore).flatMap(([source, bySource]) => (source === ALPHAPAI_SOURCE && query.kind === 'alias' ? [] : bySource?.[query.term]?.items ?? []))),
      pool: Object.entries(sentimentStore).filter(([other]) => other !== key).flatMap(([, bySource]) => Object.values(bySource ?? {}).flatMap((entry) => entry?.items ?? [])),
      profile,
      limit: MAX_FEED_ITEMS,
    });
    assembled.set(key, { version: sentimentVersion, profile, items });
    if (assembled.size > 30) assembled.delete(assembled.keys().next().value);
    return items;
  }

  /** 行情页上说明这次检索用了哪些词。 */
  function searchScope(symbol) {
    const profile = wiki.searchProfile(normalizeSymbol(symbol), nameFor(symbol));
    return {
      company: profile.company?.title ?? null,
      aliases: profile.core.filter((item) => item.kind === 'alias').map((item) => item.term).slice(0, 6),
      related: profile.related.filter((item) => item.term === item.node).map((item) => ({ term: item.term, relation: item.relation })).slice(0, 10),
      queries: profile.queries.map((item) => item.term),
    };
  }

  const termInflight = new Set();
  /** 扩展检索：用别名和最相关的环节 / 产品再去各来源搜一遍（每个词 15 分钟刷新一次，结果多只股票共用）。 */
  async function refreshExpanded(symbolKey, shortName) {
    const profile = wiki.searchProfile(symbolKey, shortName);
    let changed = false;
    for (const query of profile.queries.slice(0, MAX_TERM_QUERIES)) {
      const term = query.term;
      /** @type {[string, () => Promise<any[]>][]} */
      const sources = [];
      if (capabilities.zsxq.available && capabilities.zsxq.groupId) sources.push([ZSXQ_SOURCE, () => zsxq.fetchTopics(capabilities.zsxq.groupId, term)]);
      if (capabilities.comein) sources.push([COMEIN_SOURCE, () => gateway.fetchAnalystComments(term + ' 点评 观点 动态', isoDate(addDays(new Date(), -90)), 10)]);
      if (capabilities.tdocs) sources.push([TDOCS_SOURCE, () => gateway.fetchTencentDocs(term)]);
      // Alpha派 不发别名：公司本身已经按公司打标取过了；所属环节、产品这类相邻节点照常语义召回。
      if (alphapai.configured && query.kind !== 'alias') sources.push([ALPHAPAI_SOURCE, () => fetchAlphaPai(term)]);
      for (const [source, fetcher] of sources) {
        const slot = source + '|' + term;
        const existing = termStore[source]?.[term];
        if (termInflight.has(slot) || (existing && Date.now() - Date.parse(existing.updatedAt) < TERM_TTL_MS)) continue;
        termInflight.add(slot);
        try {
          const items = await fetcher();
          await mutate(async () => {
            termStore[source] = termStore[source] ?? {};
            termStore[source][term] = { updatedAt: new Date().toISOString(), items: (Array.isArray(items) ? items : []).slice(0, 30) };
            const terms = Object.entries(termStore[source]).sort((a, b) => String(b[1]?.updatedAt).localeCompare(String(a[1]?.updatedAt)));
            for (const [old] of terms.slice(40)) delete termStore[source][old];
            sentimentVersion += 1;
            await persistJson('sentiment-terms.json', termStore);
          });
          changed = true;
        } catch (error) {
          log(context, 'miniapp.runtime.sentiment_term_failed', { source, code: error?.code ?? 'UNKNOWN' });
        } finally {
          termInflight.delete(slot);
        }
      }
    }
    if (changed) {
      broadcast();
      wiki.onSentimentsUpdated();
    }
  }

  function resolveSymbol(input) {
    const normalized = normalizeSymbol(input);
    if (/^\d{6}\.(SH|SZ|BJ)$/.test(normalized)) return normalized;
    if (/^\d{6}$/.test(normalized)) {
      const exchange = guessExchange(normalized);
      return exchange ? `${normalized}.${exchange}` : null;
    }
    const upper = normalized.toUpperCase();
    const watched = watchlist.find((row) => String(row.shortName).toUpperCase() === upper);
    if (watched) return watched.symbol;
    const cached = Object.entries(nameCache).find(([, name]) => name.toUpperCase() === upper);
    return cached ? cached[0] : null;
  }

  /** 每个数据来源在调用前必须通过能力校验；结果缓存一个刷新周期。同一时间只跑一次。 */
  function checkCapabilities() {
    if (!capabilityCheck) capabilityCheck = runCapabilityCheck().finally(() => { capabilityCheck = null; });
    return capabilityCheck;
  }

  async function runCapabilityCheck() {
    const next = {
      market: false,
      comein: false,
      search: false,
      tdocs: false,
      zsxq: { available: false, reason: 'cli_missing', groupId: null },
      checkedAt: Date.now(),
    };
    if (gateway) {
      try {
        const names = await gateway.listToolNames();
        next.market = names.has('hengsheng_market.get_latest_quote')
          && names.has('hengsheng_market.get_daily_bars')
          && names.has('hengsheng_market.get_intraday_series');
        next.comein = names.has('comein.searchAnalystComments');
        next.search = names.has('hengsheng_market.search_instruments');
        next.tdocs = names.has('tencentdocs.manage.search_file');
      } catch (error) {
        log(context, 'miniapp.runtime.capability_check_failed', { code: error?.code ?? 'UNKNOWN' });
      }
    }
    next.zsxq = await zsxq.checkAvailable();
    capabilities = next;
    return capabilities;
  }

  async function refreshAll() {
    if (refreshInFlight) return refreshInFlight;
    refreshInFlight = (async () => {
      await checkCapabilities();
      if (!gateway) return;
      // 每分钟 tick 都进入 refreshMarket；它会按交易时钟决定是否真的拉 K 线。
      let marketUsable = true;
      try {
        await refreshMarket(currentSymbol, { scheduled: true, awaitSentiments: true });
      } catch (error) {
        marketUsable = false;
        connectionStatus.market = error?.code === 'CONNECTOR_TOOL_MISSING' ? 'unavailable' : 'error';
        noteSource('market', false, error);
        log(context, 'miniapp.runtime.market_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
        // 行情源不可用时不阻塞舆情：各来源独立过能力校验后照常刷新。
        if (marketState) {
          await refreshSentiments(marketState.symbol, marketState.shortName).catch((sentimentError) => {
            log(context, 'miniapp.runtime.sentiments_refresh_failed', { code: sentimentError?.code ?? 'UNKNOWN' });
          });
        }
      }
      if (marketUsable) {
        await refreshWatchlist().catch((error) => {
          log(context, 'miniapp.runtime.watchlist_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
        });
      }
    })().finally(() => { refreshInFlight = null; });
    return refreshInFlight;
  }

  async function refreshMarket(symbol, {
    awaitSentiments = true,
    force = false,
    scheduled = false,
  } = {}) {
    if (!gateway) fail('CONNECTOR_UNAVAILABLE', 'host connector is not available');
    if (capabilities.checkedAt === 0) await checkCapabilities();
    // 能力清单是提示，不是硬门槛；下面的真实 Connector 调用才决定成败。
    const now = new Date();
    const clock = marketClock(now);
    let entry = await barsStore.get(symbol);
    const historyNeedsRepair = needsFullHistoryRepair(entry);
    let plan = scheduled
      ? marketRefreshPlan(now, entry)
      : { fetch: true, reason: 'manual', clock, settledDate: lastSettledTradingDate(now), markFinalDate: null };
    if (force) {
      plan = { ...plan, fetch: true, reason: 'manual' };
    } else if (historyNeedsRepair) {
      // A poisoned full=true/short-history cache must not be allowed to stay on
      // the incremental path, even after the market has reached a final date.
      plan = { ...plan, fetch: true, reason: 'history-repair' };
    }

    if (plan.fetch) {
      // 报价、日K、分时独立处理成功/失败；任一成功即视为行情源可用。
      let anySuccess = false;
      let changed = false;
      let firstError = null;

      // 1) 最新报价：真实价 + 自身昨收。quote=null 时保留上一份有效值。
      try {
        const quotePayload = await gateway.fetchLatestQuote(symbol);
        anySuccess = true;
        if (quotePayload.quote) {
          if (entry?.latestQuote?.revision !== quotePayload.revision) changed = true;
          entry = (await barsStore.setQuote(symbol, quotePayload)) ?? entry;
        }
      } catch (error) {
        firstError ??= error;
        log(context, 'miniapp.runtime.quote_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
      }

      // 2) 日K：首次全量或历史修复；之后只拉尾部并按日期合并；空结果保留本地历史。
      const fullStartDate = fullHistoryStartDate(now);
      const dailyEndDate = dailyQueryEndDate(now, clock, plan.settledDate);
      let providerFetchedAt = null;
      let providerDataDate = entry?.dataDate ?? entry?.bars?.at(-1)?.date ?? null;
      try {
        if (!entry || historyNeedsRepair || entry.bars.length === 0) {
          const bundle = await gateway.fetchDailyBars(symbol, {
            startDate: fullStartDate, endDate: dailyEndDate, warmupBars: 249,
          });
          anySuccess = true;
          providerFetchedAt = bundle.fetchedAt;
          providerDataDate = bundle.dataDate ?? providerDataDate;
          if (bundle.items.length > 0) {
            const full = hasSufficientFullHistory(bundle, fullStartDate);
            const options = {
              full,
              basisVersion: bundle.basisVersion,
              revision: bundle.revision,
              coverageComplete: bundle.coverageComplete,
            };
            // A short response must not destroy a better local history while it
            // is being retried; it is merged and explicitly remains full=false.
            entry = full
              ? await barsStore.setBars(symbol, bundle.items, options)
              : await barsStore.mergeBars(symbol, bundle.items, options);
            changed = true;
          }
        } else {
          const lastDate = entry.bars.at(-1).date;
          const bundle = await gateway.fetchDailyBars(symbol, {
            startDate: isoDate(addDays(new Date(`${lastDate}T00:00:00Z`), -7)), endDate: dailyEndDate, warmupBars: 0,
            knownBasisVersion: entry.basisVersion ?? null,
          });
          anySuccess = true;
          providerFetchedAt = bundle.fetchedAt;
          providerDataDate = bundle.dataDate ?? providerDataDate;
          const basisChanged = bundle.basisVersion && entry.basisVersion && bundle.basisVersion !== entry.basisVersion;
          if (bundle.reloadRequired || basisChanged) {
            // 历史修订：丢弃该口径旧历史与衍生均线，按原完整范围重查。
            log(context, 'miniapp.runtime.daily_history_reload', { symbol });
            const fullBundle = await gateway.fetchDailyBars(symbol, {
              startDate: fullStartDate, endDate: dailyEndDate, warmupBars: 249,
            });
            providerDataDate = fullBundle.dataDate ?? providerDataDate;
            if (fullBundle.items.length > 0) {
              const full = hasSufficientFullHistory(fullBundle, fullStartDate);
              const options = {
                full,
                basisVersion: fullBundle.basisVersion,
                revision: fullBundle.revision,
                coverageComplete: fullBundle.coverageComplete,
              };
              entry = full
                ? await barsStore.setBars(symbol, fullBundle.items, options)
                : await barsStore.mergeBars(symbol, fullBundle.items, options);
              changed = true;
            }
          } else if (bundle.items.length > 0) {
            const sameRevision = bundle.revision && entry.dailyRevision === bundle.revision;
            if (!sameRevision) {
              const range = bundle.requestedRange;
              entry = bundle.updateMode === 'replace' && bundle.coverageComplete
                ? await barsStore.replaceBarsRange(symbol, bundle.items, {
                  startDate: range.startDate, endDate: range.endDate,
                  basisVersion: bundle.basisVersion ?? undefined,
                  revision: bundle.revision ?? undefined,
                  coverageComplete: bundle.coverageComplete,
                })
                : await barsStore.mergeBars(symbol, bundle.items, {
                  basisVersion: bundle.basisVersion ?? undefined,
                  revision: bundle.revision ?? undefined,
                  coverageComplete: bundle.coverageComplete,
                });
              changed = true;
            } else if (bundle.coverageComplete !== undefined
              && entry.dailyCoverageComplete !== (bundle.coverageComplete === true)) {
              entry = await barsStore.setBars(symbol, entry.bars, { coverageComplete: bundle.coverageComplete });
              changed = true;
            }
          }
        }
        entry = (await barsStore.markRefresh(symbol, {
          date: clock.date,
          reason: plan.reason,
          providerFetchedAt,
          dataDate: providerDataDate,
        })) ?? entry;
      } catch (error) {
        firstError ??= error;
        log(context, 'miniapp.runtime.daily_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
      }

      // 3) 分时：显式 1 分钟；provider 返回整日替换；空结果不清空本地缓存。
      // 盘中、午休和 15:00–15:05 取今天：午休时启动补拉的是今天上午盘，不能退回昨天。
      const intradayDate = marketDataDates(now, plan).intradayDate ?? entry?.bars?.at(-1)?.date ?? null;
      const shouldFetchIntraday = intradayDate
        && (!scheduled || ['trading', 'lunch-catchup', 'closing-final', 'closing-catchup', 'stale-catchup'].includes(plan.reason));
      if (shouldFetchIntraday) {
        try {
          const series = await gateway.fetchIntraday(symbol, intradayDate);
          anySuccess = true;
          if (series.items.length > 0) {
            const effectiveDate = series.dataDate ?? intradayDate;
            const sameRevision = series.revision && entry?.intradayRevision === series.revision
              && entry?.intradayDate === effectiveDate && entry?.intradayFinal === series.isFinal;
            if (!sameRevision) {
              entry = (await barsStore.setIntraday(symbol, effectiveDate, series.items, {
                isFinal: series.isFinal,
                asOf: series.asOf,
                revision: series.revision,
                coverageComplete: series.updateMode === 'replace' && series.coverageComplete,
              })) ?? entry;
              changed = true;
            }
          }
        } catch (error) {
          firstError ??= error;
          log(context, 'miniapp.runtime.intraday_refresh_failed', { code: error?.code ?? 'UNKNOWN' });
        }
      }

      if (anySuccess) {
        connectionStatus.market = 'ok';
        capabilities.market = true;
        noteSource('market', true);
      } else if (firstError) {
        throw firstError; // 三路全部失败才视为行情刷新失败
      }

      // 收盘终刷：coverageComplete=false 时，即使超过 16:05 也不能把缓存打成终刷完成。
      if (plan.markFinalDate && entry) {
        const finalDate = plan.markFinalDate;
        const dailyFinal = entry.bars?.find((row) => row.date === finalDate)?.isFinal === true;
        const historyComplete = entry.full === true;
        const coverageComplete = entry.dailyCoverageComplete === true;
        const intradayFinal = entry.intradayFinal === true && entry.intradayDate === finalDate;
        const quoteFinal = entry.latestQuote?.isFinal === true
          && (entry.latestQuote?.quote?.tradingDate === finalDate || entry.latestQuote?.dataDate === finalDate);
        const confirmed = historyComplete && coverageComplete && dailyFinal && intradayFinal && quoteFinal;
        const overdue = clock.date > finalDate || clock.minutes >= 16 * 60 + 5;
        if (confirmed || (overdue && historyComplete && coverageComplete)) {
          entry = (await barsStore.markFinal(symbol, finalDate)) ?? entry;
          if (!confirmed) log(context, 'miniapp.runtime.final_unconfirmed', { symbol, finalDate });
        }
      }

      if (!changed && !force && marketState?.symbol === symbol) {
        // 无变化时保持页面稳定：不重复提交与广播，但舆情照常。
        const quietSentiments = refreshSentiments(symbol, nameCache[symbol] ?? symbol);
        if (awaitSentiments) await quietSentiments;
        else void quietSentiments.catch(() => {});
        return;
      }
    }

    let shortName = nameCache[symbol] ?? null;
    if (!shortName && capabilities.comein) {
      try {
        shortName = await gateway.fetchShortName(symbol);
        if (shortName) {
          nameCache[symbol] = shortName;
          await persistJson('names.json', nameCache);
        }
      } catch {
        shortName = null;
      }
    }

    // 舆情独立于 K 线时段；每个来源自己按能力和 TTL 决定是否调用。
    const sentimentsRefresh = refreshSentiments(symbol, shortName ?? symbol);
    if (awaitSentiments) await sentimentsRefresh;
    else void sentimentsRefresh.catch(() => {});

    if (!plan.fetch) return;
    if (!force && symbol !== currentSymbol) return; // 后台刷新期间用户已切换标的，跳过提交
    const nextEntry = await barsStore.get(symbol);
    if (!nextEntry?.bars?.length) return;
    const refreshedAt = new Date().toISOString();
    const nextState = stateFromEntry(symbol, nextEntry, refreshedAt, { clock });
    validateMarketState(nextState);
    await mutate(async () => {
      marketState = nextState;
      await persistJson('market-data.json', marketState);
    });
    broadcast();
  }

  /** 切换标的后的后台补数据：乐观尝试完整行情刷新，失败则至少独立刷新舆情。 */
  async function backgroundRefresh(symbol) {
    if (capabilities.checkedAt === 0) await checkCapabilities();
    try {
      return await refreshMarket(symbol, { awaitSentiments: false });
    } catch (error) {
      log(context, 'miniapp.runtime.background_market_failed', { code: error?.code ?? 'UNKNOWN' });
      return refreshSentiments(symbol, nameCache[symbol] ?? symbol);
    }
  }

  /** 秒开路径：本地缓存命中时直接以缓存出快照，不等任何外部调用。 */
  async function serveFromCache(symbol) {
    const entry = await barsStore.get(symbol);
    if (!entry || !Array.isArray(entry.bars) || entry.bars.length === 0) return false;
    const nextState = stateFromEntry(symbol, entry, entry.updatedAt ?? new Date().toISOString());
    validateMarketState(nextState);
    await mutate(async () => {
      marketState = nextState;
      await persistJson('market-data.json', marketState);
    });
    return true;
  }

  function stateFromEntry(symbol, entry, updatedAt, { clock = marketClock() } = {}) {
    const bars = entry.bars;
    const last = bars.at(-1);
    // 行情源还没给出当天日K时（盘中常见），用当天报价补一根临时 K 线，日K和成交额才能看到今天；
    // 只用于展示，不写进缓存，行情源给出当天日K后自然被替换。
    const provisional = provisionalDailyBar(last, entry.latestQuote);
    const shownBars = provisional ? [...bars, provisional] : bars;
    const intraday = Array.isArray(entry.intraday) ? entry.intraday : [];
    const latestQuote = entry.latestQuote ?? null;
    let quote;
    let quoteAsOf = null;
    let quoteTradingDate = null;
    let quoteIsFinal = false;
    let quoteSource = 'daily_close';
    if (latestQuote?.quote) {
      // 报价卡使用 get_latest_quote 的真实价及该报价自己的昨收；changePercent 已是百分数。
      const q = latestQuote.quote;
      quote = {
        price: q.price,
        change: q.change,
        changePercent: q.changePercent,
        open: q.open, high: q.high, low: q.low,
        previousClose: q.previousClose,
        turnover: q.amount,
        updatedAt: latestQuote.asOf ?? updatedAt,
      };
      quoteAsOf = latestQuote.asOf ?? null;
      quoteTradingDate = q.tradingDate;
      quoteIsFinal = latestQuote.isFinal === true;
      quoteSource = 'latest_quote';
    } else {
      // 升级过渡兜底：从未获得报价快照时展示最近日K终值（真实数据，非实时）。
      const previousClose = last.previousClose;
      quote = {
        price: last.close,
        change: round2(last.close - previousClose),
        changePercent: previousClose ? round2((last.close - previousClose) / previousClose * 100) : 0,
        open: last.open, high: last.high, low: last.low,
        previousClose,
        turnover: last.amount,
        updatedAt,
      };
      quoteTradingDate = last.date;
      quoteIsFinal = last.isFinal === true;
    }
    const intradayLast = intraday.at(-1) ?? null;
    return {
      symbol,
      shortName: nameCache[symbol] ?? symbol,
      exchange: exchangeForSymbol(symbol),
      quote,
      quoteAsOf,
      quoteTradingDate,
      quoteIsFinal,
      quoteSource,
      daily: shownBars.map((row) => ({ date: row.date, open: row.open, high: row.high, low: row.low, close: row.close, volume: row.volume })),
      dailyProvisionalDate: provisional ? provisional.date : null,
      intraday,
      intradayDate: typeof entry.intradayDate === 'string' ? entry.intradayDate : null,
      intradayFinal: entry.intradayFinal === true,
      intradayAsOf: typeof entry.intradayAsOf === 'string' ? entry.intradayAsOf : null,
      intradayLastPending: intradayLast ? intradayLast.isFinal !== true : false,
      turnoverSeries: shownBars.slice(-60).map((row) => ({ date: row.date, amount: row.amount })),
      fetchedAt: updatedAt,
      dataDate: entry.dataDate ?? last.date,
      marketPhase: clock.phase,
      lastMarketRefreshDate: entry.lastMarketRefreshDate ?? null,
      finalRefreshDate: entry.finalRefreshDate ?? null,
      provenance: PROVENANCE,
    };
  }

  /** 舆情刷新：每个来源先过能力校验，再按各自的 TTL 并行刷新；失败保留本地缓存。Alpha派 召回慢，在后台刷，到了再推给页面。 */
  async function refreshSentiments(symbol, shortName) {
    const key = normalizeSymbol(symbol);
    const jobs = [];
    if (capabilities.comein) {
      jobs.push(refreshSource(key, COMEIN_SOURCE, async () => {
        const code = key.split('.')[0];
        const startDate = isoDate(addDays(new Date(), -90));
        return gateway.fetchAnalystComments(`${shortName} ${code} 点评 观点 动态`, startDate, 20);
      }, 'comein'));
    } else {
      connectionStatus.comein = 'unavailable';
    }
    if (capabilities.zsxq.available && capabilities.zsxq.groupId) {
      jobs.push(refreshSource(key, ZSXQ_SOURCE, () => zsxq.fetchTopics(capabilities.zsxq.groupId, shortName), 'zsxq'));
    } else {
      connectionStatus.zsxq = 'unavailable';
    }
    if (capabilities.tdocs) {
      jobs.push(refreshSource(key, TDOCS_SOURCE, () => gateway.fetchTencentDocs(shortName), 'tdocs'));
    } else {
      connectionStatus.tdocs = 'unavailable';
    }
    if (alphapai.configured) {
      if (!alphapaiInflight.has(key)) {
        alphapaiInflight.add(key);
        void refreshSource(key, ALPHAPAI_SOURCE, () => fetchAlphaPaiFeed(key, shortName), 'alphapai', ALPHAPAI_TTL_MS, ALPHAPAI_FEED_VERSION).finally(() => alphapaiInflight.delete(key));
      }
    } else {
      connectionStatus.alphapai = 'unavailable';
    }
    await Promise.all(jobs);
    // 知识图谱扩展检索在后台跑，不拖慢切换股票。
    void refreshExpanded(key, shortName).catch(() => {});
  }

  /** Alpha派 语义召回（所属环节、产品等扩展检索词用）：最近 30 天的点评、社媒、纪要、官方路演、研报。调用期间 Key 被清除时丢弃结果。 */
  async function fetchAlphaPai(query) {
    const items = await alphapai.recall({ query, types: ALPHAPAI_SENTIMENT_TYPES, days: ALPHAPAI_DAYS });
    if (!alphapai.configured) throw Object.assign(new Error('Alpha派 Key 已清除'), { code: 'ALPHAPAI_NOT_CONFIGURED' });
    return items.slice(0, 30);
  }

  /**
   * 行情页的 Alpha派 舆情：按 Alpha派 自己的公司打标（股票代码）取，不用名称或别名检索。
   * 点评、社媒取最近 30 天，纪要、研报（含外资）取最近 90 天。调用期间 Key 被清除时丢弃结果。
   */
  async function fetchAlphaPaiFeed(symbol, shortName) {
    const key = normalizeSymbol(symbol);
    const items = /^\d{6}\.(SH|SZ|BJ)$/.test(key)
      ? await alphapai.tagged({ symbol: key, types: ALPHAPAI_FEED_TYPES, days: ALPHAPAI_DAYS, longDays: ALPHAPAI_LONG_DAYS })
      : await alphapai.recall({ query: shortName, types: ALPHAPAI_SENTIMENT_TYPES, days: ALPHAPAI_DAYS });
    if (!alphapai.configured) throw Object.assign(new Error('Alpha派 Key 已清除'), { code: 'ALPHAPAI_NOT_CONFIGURED' });
    /** @type {Record<string, number>} */
    const counts = {};
    const capped = items.filter((item) => {
      counts[item.docType] = (counts[item.docType] ?? 0) + 1;
      return counts[item.docType] <= (ALPHAPAI_FEED_CAPS[item.docType] ?? 5);
    });
    // 已经取过全文的保留全文，刷新列表不会退回摘要。
    const loaded = new Map((sentimentStore[key]?.[ALPHAPAI_SOURCE]?.items ?? []).filter((item) => item && !item.preview).map((item) => [item.id, item]));
    return capped.map((item) => (item.preview && loaded.has(item.id) ? loaded.get(item.id) : item));
  }

  /** 已经抓到的某条舆情（原始对象）。 */
  function findSentimentItem(id) {
    for (const bySource of Object.values(sentimentStore)) for (const entry of Object.values(bySource ?? {})) {
      const hit = entry?.items?.find((item) => item?.id === id);
      if (hit) return hit;
    }
    for (const byTerm of Object.values(termStore)) for (const entry of Object.values(byTerm ?? {})) {
      const hit = entry?.items?.find((item) => item?.id === id);
      if (hit) return hit;
    }
    return null;
  }

  /**
   * 按需取 Alpha派 全文：列表里只有摘要的点评（前 100 字）、研报和纪要（标题、机构）。点评详情每天有额度（100 条），
   * 所以只在用户点「加载全文」或 Agent 调 research_read 时才取；取到后写回缓存，之后不再重复取。
   */
  async function loadAlphaPaiFull(id) {
    const item = researchCache.get(id) ?? findSentimentItem(id);
    if (!item) return { found: false, loaded: false, message: '找不到这条舆情，刷新后再试' };
    if (item.source !== ALPHAPAI_SOURCE || !item.preview || !item.ref) return { found: true, loaded: false, item };
    if (!alphapai.configured) return { found: true, loaded: false, item, message: '还没有填写 Alpha派 API Key' };
    let content;
    try {
      content = await alphapai.detail(item);
    } catch (error) {
      log(context, 'miniapp.runtime.alphapai_full_failed', { code: error?.code ?? 'UNKNOWN' });
      return { found: true, loaded: false, item, code: String(error?.code ?? 'UNKNOWN'), message: String(error?.message ?? '取全文失败') };
    }
    const { ref: _ref, preview: _preview, ...rest } = item;
    const full = { ...rest, content, summary: content.slice(0, 180) };
    await mutate(async () => {
      const swap = (entry) => {
        if (Array.isArray(entry?.items)) entry.items = entry.items.map((other) => (other?.id === id ? { ...full } : other));
      };
      for (const bySource of Object.values(sentimentStore)) if (bySource?.[ALPHAPAI_SOURCE]) swap(bySource[ALPHAPAI_SOURCE]);
      for (const entry of Object.values(termStore[ALPHAPAI_SOURCE] ?? {})) swap(entry);
      sentimentVersion += 1;
      await persistJson('sentiments.json', sentimentStore);
      await persistJson('sentiment-terms.json', termStore);
    });
    if (researchCache.has(id)) researchCache.set(id, full);
    return { found: true, loaded: true, item: full };
  }

  /** version：取法变了的来源（如 Alpha派 改为按公司打标）带上版本号，旧版本的缓存视为过期。 */
  async function refreshSource(symbolKey, source, fetcher, statusKey, ttlMs = SENTIMENT_TTL_MS, version = undefined) {
    const existing = sentimentStore[symbolKey]?.[source];
    if (existing && existing.version === version && Date.now() - Date.parse(existing.updatedAt) < ttlMs) {
      connectionStatus[statusKey] = 'ok';
      return;
    }
    try {
      const items = await fetcher();
      connectionStatus[statusKey] = 'ok';
      noteSource(statusKey, true);
      await mutate(async () => {
        sentimentStore[symbolKey] = sentimentStore[symbolKey] ?? {};
        sentimentStore[symbolKey][source] = { updatedAt: new Date().toISOString(), items, ...(version ? { version } : {}) };
        sentimentVersion += 1;
        await persistJson('sentiments.json', sentimentStore);
      });
      broadcast(); // 后台舆情刷新落地后通知页面
      wiki.onSentimentsUpdated();
    } catch (error) {
      if (error?.code === 'ALPHAPAI_NOT_CONFIGURED') {
        connectionStatus[statusKey] = 'unavailable';
        return;
      }
      connectionStatus[statusKey] = 'error';
      noteSource(statusKey, false, error);
      log(context, 'miniapp.runtime.sentiment_refresh_failed', { source, code: error?.code ?? 'UNKNOWN' });
    }
  }

  // ---------- Alpha派 Key ----------
  /** 保存 Alpha派 Key：先校验，通过后立刻按当前股票拉一次舆情（不等 TTL），扩展检索词随后补上。 */
  async function saveAlphaPaiKey(value) {
    const started = Date.now();
    await alphapai.saveKey(value);
    sourceTests.alphapai = { at: new Date().toISOString(), ok: true, ms: Date.now() - started, message: '鉴权正常，已保存 Key' };
    noteSource('alphapai', true);
    connectionStatus.alphapai = 'ok';
    const symbol = normalizeSymbol(marketState?.symbol ?? currentSymbol);
    const name = nameFor(symbol) ?? symbol;
    if (!alphapaiInflight.has(symbol)) {
      alphapaiInflight.add(symbol);
      void refreshSource(symbol, ALPHAPAI_SOURCE, () => fetchAlphaPaiFeed(symbol, name), 'alphapai', 0, ALPHAPAI_FEED_VERSION)
        .then(() => refreshExpanded(symbol, name))
        .catch(() => {})
        .finally(() => alphapaiInflight.delete(symbol));
    }
  }

  /** 清除 Alpha派 Key：一并清掉已经抓到的 Alpha派 舆情（已存入资料库的保留）。 */
  async function clearAlphaPaiKey() {
    await alphapai.clearKey();
    await mutate(async () => {
      for (const bySource of Object.values(sentimentStore)) if (bySource && ALPHAPAI_SOURCE in bySource) delete bySource[ALPHAPAI_SOURCE];
      delete termStore[ALPHAPAI_SOURCE];
      sentimentVersion += 1;
      await persistJson('sentiments.json', sentimentStore);
      await persistJson('sentiment-terms.json', termStore);
    });
    for (const id of [...researchCache.keys()]) if (id.startsWith('alphapai-')) researchCache.delete(id);
    delete sourceTests.alphapai;
    sourceHealth.alphapai = {};
    connectionStatus.alphapai = 'unavailable';
    broadcast();
  }

  // ---------- 统一检索（MCP research_search / research_read） ----------
  /** 所有已经抓到的舆情（按股票直接检索的 + 扩展检索词的），按 id 去重。 */
  function cachedSentimentItems() {
    /** @type {Map<string, any>} */
    const seen = new Map();
    const add = (entry) => {
      for (const item of entry?.items ?? []) if (item && typeof item.id === 'string' && !seen.has(item.id)) seen.set(item.id, item);
    };
    for (const bySource of Object.values(sentimentStore)) for (const entry of Object.values(bySource ?? {})) add(entry);
    for (const byTerm of Object.values(termStore)) for (const entry of Object.values(byTerm ?? {})) add(entry);
    return [...seen.values()];
  }

  function clampInt(value, min, max, fallback) {
    if (value === undefined || value === null || value === '') return fallback;
    const number = Math.round(Number(value));
    return Number.isFinite(number) ? Math.min(max, Math.max(min, number)) : fallback;
  }

  /**
   * 统一检索：一次查遍已接入的数据源，没接入的静默跳过；主体（公司 / 节点）的名称、别名、代码同步检索，
   * neighbors 时带上相邻节点。接入了但这次失败的来源记进 failed。
   */
  async function researchSearch(args) {
    let query = String(args?.query ?? '').replace(/\s+/g, ' ').trim().slice(0, 120);
    let symbolText = String(args?.symbol ?? '').trim().slice(0, 40);
    if (!symbolText && /^\d{6}(\.(SH|SZ|BJ))?$/i.test(query)) {
      symbolText = query;
      query = '';
    }
    if (!query && !symbolText) throw Object.assign(new Error('query 和 symbol 至少给一个'), { code: 'INVALID_ARGUMENTS' });
    const expand = args?.expand !== false;
    const neighbors = args?.neighbors === true;
    const days = clampInt(args?.days, 1, 365, 30);
    const limit = clampInt(args?.limit, 1, 80, 20);
    const excerptChars = clampInt(args?.excerpt_chars, 80, 2000, 240);
    const wanted = new Set(Array.isArray(args?.sources) ? args.sources.filter((id) => RESEARCH_SOURCE_IDS.includes(id)) : []);
    const use = (id) => wanted.size === 0 || wanted.has(id);
    const types = Array.isArray(args?.alphapai_types) ? args.alphapai_types.filter((type) => typeof type === 'string' && Object.hasOwn(ALPHAPAI_TYPES, type)) : [];
    // 刚启动时能力校验可能还没跑完（知识星球 CLI 要几秒）：等它完成，免得漏查已接入的来源。
    if (capabilities.checkedAt === 0) await checkCapabilities().catch(() => {});
    let symbol = '';
    let name = null;
    if (symbolText) {
      const identity = await resolveCompanyIdentity(symbolText).catch(() => null);
      if (identity?.symbol) {
        symbol = identity.symbol;
        name = identity.shortName ?? null;
      } else if (!query) query = symbolText;
    }
    let profile = await wiki.researchProfile({ symbol, name, query });
    // 单个词、知识图谱里没有对应节点：看看是不是股票简称（代码搜索唯一命中才算）。
    if (!profile.subject && !symbol && query && !/\s/.test(query) && query.length <= 12) {
      const identity = await resolveCompanyIdentity(query).catch(() => null);
      if (identity?.symbol) profile = await wiki.researchProfile({ symbol: identity.symbol, name: identity.shortName ?? query, query });
    }
    const plan = planResearch({ query, profile, expand, neighbors });
    /** @type {any[]} */
    const adapters = [];
    /** @type {ReturnType<typeof alphapaiPlan>} */
    let alphapaiSteps = [];
    if (use('alphapai') && alphapai.configured) {
      // 召回一次 4–5 秒：3 路并发，发散时 5 个检索词两轮查完，留在 MCP 超时之内。
      // Alpha派 不用别名：公司按 Alpha派 的公司打标（股票代码）取，话题和打标覆盖不到的类型再语义召回；环节、自由文本只用本名召回。
      alphapaiSteps = alphapaiPlan(plan, { types: types.length ? types : null, taggedTypes: ALPHAPAI_TAGGED_TYPES, defaultTagged: ALPHAPAI_FEED_TYPES, defaultRecall: ALPHAPAI_SENTIMENT_TYPES });
      adapters.push({
        id: 'alphapai', name: ALPHAPAI_SOURCE, mode: 'semantic', concurrency: 3, inputs: alphapaiSteps,
        search: (step) => (step.kind === 'tagged' ? alphapai.tagged({ symbol: step.symbol, types: step.types, days }) : alphapai.recall({ query: step.query, types: step.types, days })),
      });
    }
    if (use('comein') && gateway && capabilities.comein) {
      adapters.push({ id: 'comein', name: COMEIN_SOURCE, mode: 'semantic', concurrency: 2, search: (phrase) => gateway.fetchAnalystComments(phrase, isoDate(addDays(new Date(), -days)), 20) });
    }
    if (use('zsxq') && capabilities.zsxq.available && capabilities.zsxq.groupId) {
      adapters.push({ id: 'zsxq', name: ZSXQ_SOURCE, mode: 'keyword', concurrency: 2, search: (term) => zsxq.fetchTopics(capabilities.zsxq.groupId, term) });
    }
    if (use('tdocs') && gateway && capabilities.tdocs) {
      adapters.push({ id: 'tdocs', name: TDOCS_SOURCE, mode: 'keyword', concurrency: 2, search: (term) => gateway.fetchTencentDocs(term) });
    }
    const wikiBrief = use('library') ? await wiki.brief() : null;
    if (wikiBrief?.folders) {
      const terms = [...(plan.subject ? plan.matchCore.map((item) => item.term) : [plan.query]), ...plan.tokens, ...plan.related.map((item) => item.term)];
      adapters.push({ id: 'library', name: '本地资料库', mode: 'local', concurrency: 1, search: () => wiki.searchLibrary({ terms, spotlightTerms: terms.slice(0, 4), limit: 20 }) });
    }
    // 指定了 Alpha派 资料类型时，已抓取的 Alpha派 舆情也只要这些类型（行情页抓的是点评、社媒、纪要等，不能混进来充当公告、指标）。
    const typeLabels = new Set(types.map((type) => ALPHAPAI_TYPES[type]));
    if (use('feed')) adapters.push({ id: 'feed', name: '行情页已抓取的舆情', mode: 'pool', concurrency: 1, search: () => cachedSentimentItems().filter((item) => !types.length || item.source !== ALPHAPAI_SOURCE || typeLabels.has(item.docType)) });
    const result = await runResearch({ plan, adapters, days, limit, excerptChars });
    for (const item of result.full) {
      researchCache.delete(item.id);
      researchCache.set(item.id, item);
    }
    while (researchCache.size > 400) researchCache.delete(researchCache.keys().next().value);
    const pages = await wiki.researchPages(plan.subject ? [plan.subject.title] : [plan.query, ...plan.tokens], 5).catch(() => []);
    const { full, ...found } = result;
    const now = Date.now();
    return {
      query: plan.query || null,
      subject: plan.subject ? { title: plan.subject.title, type: plan.subject.type, ...(plan.subject.tickers?.length ? { tickers: plan.subject.tickers } : {}) } : null,
      ...(plan.topic ? { topic: plan.topic } : {}),
      terms: {
        direct: (plan.subject ? plan.matchCore.map((item) => item.term) : [plan.query, ...plan.tokens]).slice(0, 8),
        ...(plan.neighbors ? { related: [...new Set(plan.related.filter((item) => item.term === item.node).map((item) => item.label))].slice(0, 12) } : {}),
      },
      queries: plan.phrases.map((phrase) => phrase.text),
      ...(alphapaiSteps.length ? { alphapai_queries: alphapaiSteps.map((step) => step.label) } : {}),
      ...(adapters.some((adapter) => adapter.mode === 'keyword') ? { keywords: plan.keywords } : {}),
      window: { days, from: dayOf(new Date(now - days * 86_400_000).toISOString()), to: dayOf(new Date(now).toISOString()), note: '外部来源按发布时间过滤；本地资料库不按时间过滤' },
      ...found,
      chain: plan.map,
      wiki_pages: pages,
      hints: researchHints(plan, found),
    };
  }

  /** research_read：按 id 读 research_search 结果的全文（舆情正文 / 本地资料正文或路径）。 */
  async function researchRead(args) {
    const ids = [...new Set((Array.isArray(args?.ids) ? args.ids : []).filter((id) => typeof id === 'string' && id.trim()).map((id) => id.trim()))].slice(0, 8);
    if (!ids.length) throw Object.assign(new Error('ids 至少给一个（research_search 结果里的 id）'), { code: 'INVALID_ARGUMENTS' });
    const maxChars = clampInt(args?.max_chars, 500, 20_000, 8000);
    const pool = ids.some((id) => !id.startsWith('file:') && !researchCache.has(id)) ? new Map(cachedSentimentItems().map((item) => [item.id, item])) : new Map();
    const items = [];
    for (const id of ids) {
      if (id.startsWith('file:')) {
        const material = await wiki.readMaterial(id.slice(5), maxChars).catch(() => null);
        items.push(material ?? { id, found: false, hint: '这个文件已经不在关联的资料文件夹里' });
        continue;
      }
      let item = researchCache.get(id) ?? pool.get(id);
      if (!item) {
        items.push({ id, found: false, hint: '不在最近的检索结果里：重新 research_search 后再读' });
        continue;
      }
      // Alpha派 列表里只有摘要的（点评前 100 字，研报、纪要只有标题）：现在取全文（点评详情每天有额度）。
      let note = '';
      if (item.source === ALPHAPAI_SOURCE && item.preview && item.ref) {
        const loaded = await loadAlphaPaiFull(id);
        if (loaded.loaded) item = loaded.item;
        else note = '只拿到摘要：' + (loaded.message ?? '取全文失败');
      }
      const content = String(item.content || item.summary || '');
      items.push({
        id,
        source: item.source,
        title: item.title,
        ...itemFacts(item),
        ...(Array.isArray(item.tags) && item.tags.length ? { tags: item.tags } : {}),
        content: content.slice(0, maxChars),
        chars: content.length,
        truncated: content.length > maxChars,
        ...(item.source === TDOCS_SOURCE ? { hint: '腾讯文档只能检索到标题，正文请打开链接' } : {}),
        ...(note ? { hint: note } : {}),
      });
    }
    return { items };
  }

  /** 自选股报价：本地缓存 + 最近 7 天增量合并；只有交易时段/收盘终刷才访问行情 Connector。 */
  async function refreshWatchlist({ scheduled = true } = {}) {
    if (!gateway) return;
    const now = new Date();
    const clock = marketClock(now);
    let changed = false;
    const next = [];
    for (const item of watchlist) {
      if (marketState && item.symbol === marketState.symbol && scheduled) {
        const nextItem = {
          ...item,
          shortName: marketState.shortName,
          price: marketState.quote.price,
          change: marketState.quote.change,
          changePercent: marketState.quote.changePercent,
          previousClose: marketState.quote.previousClose,
          updatedAt: marketState.quote.updatedAt,
          status: 'active',
        };
        changed ||= nextItem.price !== item.price || nextItem.updatedAt !== item.updatedAt || nextItem.status !== item.status;
        next.push(nextItem);
        continue;
      }
      try {
        let entry = await barsStore.get(item.symbol);
        const plan = scheduled
          ? marketRefreshPlan(now, entry)
          : { fetch: true, reason: 'manual', clock, settledDate: lastSettledTradingDate(now), markFinalDate: null };
        let providerFetchedAt = null;
        let providerDataDate = entry?.dataDate ?? entry?.bars?.at(-1)?.date ?? null;
        if (plan.fetch) {
          // 自选股：最新报价 + 日K尾部；分时只由当前标的的 refreshMarket 维护。
          try {
            const quotePayload = await gateway.fetchLatestQuote(item.symbol);
            if (quotePayload.quote) entry = (await barsStore.setQuote(item.symbol, quotePayload)) ?? entry;
          } catch {
            // 报价失败不阻塞日K；列表沿用上一份有效值。
          }
          if (!entry || !entry.full || entry.bars.length === 0) {
            const bundle = await gateway.fetchDailyBars(item.symbol, {
              startDate: isoDate(addDays(now, -30)),
              endDate: dailyQueryEndDate(now, clock, plan.settledDate),
              warmupBars: 0,
            });
            providerFetchedAt = bundle.fetchedAt;
            providerDataDate = bundle.dataDate ?? providerDataDate;
            if (bundle.items.length > 0) entry = await barsStore.setBars(item.symbol, bundle.items, {
              basisVersion: bundle.basisVersion,
              revision: bundle.revision,
              coverageComplete: bundle.coverageComplete,
            });
          } else {
            const lastDate = entry.bars.at(-1).date;
            const bundle = await gateway.fetchDailyBars(item.symbol, {
              startDate: isoDate(addDays(new Date(`${lastDate}T00:00:00Z`), -7)),
              endDate: dailyQueryEndDate(now, clock, plan.settledDate),
              warmupBars: 0,
              knownBasisVersion: entry.basisVersion ?? null,
            });
            providerFetchedAt = bundle.fetchedAt;
            providerDataDate = bundle.dataDate ?? providerDataDate;
            if (bundle.items.length > 0) entry = await barsStore.mergeBars(item.symbol, bundle.items, {
              basisVersion: bundle.basisVersion ?? undefined,
              revision: bundle.revision ?? undefined,
              coverageComplete: bundle.coverageComplete,
            });
          }
          entry = (await barsStore.markRefresh(item.symbol, {
            date: clock.date, reason: plan.reason, providerFetchedAt, dataDate: providerDataDate,
          })) ?? entry;
          if (plan.markFinalDate && entry) {
            const finalDate = plan.markFinalDate;
            const dailyFinal = entry.bars?.find((row) => row.date === finalDate)?.isFinal === true;
            const quoteFinal = entry.latestQuote?.isFinal === true
              && (entry.latestQuote?.quote?.tradingDate === finalDate || entry.latestQuote?.dataDate === finalDate);
            const overdue = clock.date > finalDate || clock.minutes >= 16 * 60 + 5;
            if (dailyFinal || quoteFinal || overdue) {
              entry = (await barsStore.markFinal(item.symbol, finalDate)) ?? entry;
            }
          }
        }
        if (!entry || !entry.bars?.length) { next.push(item); continue; }
        let shortName = item.shortName;
        if ((!shortName || shortName === item.symbol) && capabilities.comein) {
          shortName = nameCache[item.symbol] ?? await gateway.fetchShortName(item.symbol).catch(() => null) ?? item.symbol;
          if (shortName !== item.symbol && !nameCache[item.symbol]) {
            nameCache[item.symbol] = shortName;
            await persistJson('names.json', nameCache);
          }
        }
        const derived = stateFromEntry(item.symbol, entry, entry.lastMarketRefreshAt ?? item.updatedAt, { clock });
        const nextItem = {
          ...item,
          shortName,
          price: derived.quote.price,
          change: derived.quote.change,
          changePercent: derived.quote.changePercent,
          previousClose: derived.quote.previousClose,
          updatedAt: derived.quote.updatedAt,
          status: 'active',
        };
        changed ||= nextItem.price !== item.price || nextItem.updatedAt !== item.updatedAt
          || nextItem.status !== item.status || nextItem.shortName !== item.shortName;
        next.push(nextItem);
      } catch {
        next.push(item);
      }
    }
    if (changed) {
      await mutate(async () => {
        // 按 symbol 合并写回：刷新期间被移除的标的不复活，新增的标的保留。
        const updates = new Map(next.map((item) => [item.symbol, item]));
        watchlist = watchlist.map((item) => updates.get(item.symbol) ?? item);
        await persistJson('watchlist.json', watchlist);
      });
      broadcast();
    }
  }

  function mutate(operation) {
    const run = mutationQueue.then(operation);
    mutationQueue = run.catch(() => {});
    return run;
  }

  async function persistJson(fileName, value) {
    const pendingFile = join(dataDir, `${fileName}.pending`);
    await writeFile(pendingFile, JSON.stringify(value, null, 2), 'utf8');
    await rename(pendingFile, join(dataDir, fileName));
  }

  function broadcast() {
    broadcastEvent('snapshot.updated', { symbol: currentSymbol, updatedAt: marketState?.fetchedAt ?? null });
  }

  function broadcastEvent(event, data) {
    const packet = `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
    for (const response of sseClients) response.write(packet);
  }

  await listen(server, context.listen.host, context.listen.port);
  log(context, 'miniapp.runtime.listening', { connector: gateway ? 'available' : 'unavailable' });

  let disposed = false;
  const dispose = async () => {
    if (disposed) return;
    disposed = true;
    clearInterval(heartbeat);
    clearInterval(refreshTimer);
    zsxq.dispose();
    await wiki.dispose();
    picker.dispose();
    await mutationQueue;
    for (const response of sseClients) response.end();
    sseClients.clear();
    await close(server);
  };
  const onAbort = () => void dispose();
  context.signal.addEventListener('abort', onAbort, { once: true });
  if (context.signal.aborted) await dispose();

  return { dispose };
}

async function loadJson(filePath, fallback) {
  try {
    return JSON.parse(await readFile(filePath, 'utf8'));
  } catch (error) {
    if (error?.code !== 'ENOENT' && !(error instanceof SyntaxError)) throw error;
    return fallback;
  }
}

function validateMarketState(value) {
  if (!isRecord(value)) fail('INVALID_SNAPSHOT', 'market state must be an object');
  for (const key of ['symbol', 'shortName', 'exchange']) {
    if (typeof value[key] !== 'string' || value[key].trim() === '') fail('INVALID_SNAPSHOT', `${key} is required`);
  }
  if (!isRecord(value.quote)) fail('INVALID_SNAPSHOT', 'quote is required');
  for (const key of ['price', 'change', 'changePercent', 'open', 'high', 'low', 'previousClose', 'turnover']) {
    if (!Number.isFinite(value.quote[key])) fail('INVALID_SNAPSHOT', `quote.${key} must be a number`);
  }
  if (typeof value.quote.updatedAt !== 'string') fail('INVALID_SNAPSHOT', 'quote.updatedAt is required');
  if (!Array.isArray(value.daily) || value.daily.length === 0) fail('INVALID_SNAPSHOT', 'daily cannot be empty');
  for (const row of value.daily) {
    if (!isRecord(row) || typeof row.date !== 'string' || !['open', 'high', 'low', 'close', 'volume'].every((key) => Number.isFinite(row[key]))) {
      fail('INVALID_SNAPSHOT', 'daily rows must include date, OHLC and volume');
    }
  }
  if (!Array.isArray(value.intraday)) fail('INVALID_SNAPSHOT', 'intraday must be an array');
  for (const row of value.intraday) {
    if (!isRecord(row) || typeof row.time !== 'string' || !Number.isFinite(row.price) || !Number.isFinite(row.volume)) {
      fail('INVALID_SNAPSHOT', 'intraday rows must include time, price and volume');
    }
  }
  if (!Array.isArray(value.turnoverSeries)) fail('INVALID_SNAPSHOT', 'turnoverSeries must be an array');
  for (const row of value.turnoverSeries) {
    if (!isRecord(row) || typeof row.date !== 'string' || !Number.isFinite(row.amount)) {
      fail('INVALID_SNAPSHOT', 'turnoverSeries rows must include date and amount');
    }
  }
}

function validateSentimentItems(items, source) {
  if (!Array.isArray(items)) fail('INVALID_SENTIMENTS', 'items must be an array');
  return items.map((item, index) => {
    if (!isRecord(item) || typeof item.title !== 'string' || item.title.trim() === '' || typeof item.publishedAt !== 'string') {
      fail('INVALID_SENTIMENTS', 'each item needs title and publishedAt');
    }
    const content = typeof item.content === 'string' ? item.content : '';
    const summary = typeof item.summary === 'string' && item.summary.trim() !== '' ? item.summary : content.slice(0, 180);
    let url;
    try {
      const parsed = new URL(String(item.url));
      if (['http:', 'https:'].includes(parsed.protocol)) url = parsed.href;
    } catch { url = undefined; }
    return {
      id: typeof item.id === 'string' && item.id.trim() !== '' ? item.id : `${source}-${index}-${Date.parse(item.publishedAt) || index}`,
      source,
      title: item.title.trim(),
      summary,
      content,
      publishedAt: item.publishedAt,
      tags: Array.isArray(item.tags) ? item.tags.filter((tag) => typeof tag === 'string').slice(0, 6) : [],
      ...(url ? { url } : {}),
    };
  });
}

function normalizeWatchlist(items) {
  if (!Array.isArray(items)) return [];
  return items.filter((item) => isRecord(item) && typeof item.symbol === 'string').map((item) => ({
    symbol: normalizeSymbol(item.symbol),
    shortName: typeof item.shortName === 'string' && item.shortName.trim() !== '' ? item.shortName : item.symbol,
    exchange: typeof item.exchange === 'string' ? item.exchange : exchangeForSymbol(item.symbol),
    price: Number.isFinite(item.price) ? item.price : null,
    change: Number.isFinite(item.change) ? item.change : null,
    changePercent: Number.isFinite(item.changePercent) ? item.changePercent : null,
    previousClose: Number.isFinite(item.previousClose) ? item.previousClose : null,
    updatedAt: typeof item.updatedAt === 'string' ? item.updatedAt : new Date().toISOString(),
    status: item.status === 'active' ? 'active' : 'pending',
  }));
}

async function readBody(request) {
  const chunks = [];
  let size = 0;
  for await (const chunk of request) {
    size += chunk.length;
    if (size > MAX_BODY_BYTES) fail('BODY_TOO_LARGE', 'request body exceeds limit');
    chunks.push(chunk);
  }
  return Buffer.concat(chunks).toString('utf8');
}

async function readJson(request) {
  const body = await readBody(request);
  try {
    return JSON.parse(body);
  } catch {
    fail('INVALID_JSON', 'request body must be valid JSON');
  }
}

function json(response, status, value) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
  response.end(JSON.stringify(value));
}

function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function normalizeSymbol(value) {
  const compact = String(value ?? '').trim().toUpperCase().replace(/\s+/g, '');
  const prefix = compact.match(/^(SH|SZ|BJ)[:._-]?(\d{6})$/);
  if (prefix) return `${prefix[2]}.${prefix[1]}`;
  const suffix = compact.match(/^(\d{6})[:._-]?(SH|SZ|BJ)$/);
  return suffix ? `${suffix[1]}.${suffix[2]}` : compact;
}

function matchesSymbol(input, symbol, shortName) {
  const query = normalizeSymbol(input), canonical = normalizeSymbol(symbol);
  return query === canonical || query === canonical.split('.')[0] || query === String(shortName).toUpperCase();
}

function guessExchange(code) {
  if (/^(60|68)/.test(code)) return 'SH';
  if (/^(00|30)/.test(code)) return 'SZ';
  if (/^(43|8[37]|92)/.test(code)) return 'BJ';
  return null;
}

function exchangeForSymbol(symbol) {
  const exchange = String(symbol).split('.').at(-1);
  return exchange === 'SH' ? '上交所' : exchange === 'SZ' ? '深交所' : exchange === 'BJ' ? '北交所' : '待识别';
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}


function addDays(date, days) {
  const next = new Date(date);
  next.setUTCDate(next.getUTCDate() + days);
  return next;
}

function fullHistoryStartDate(date) {
  return isoDate(addDays(date, -365 * 3 - 30));
}

function dailyQueryEndDate(now, clock, settledDate) {
  // 盘中、午休和 15:00–15:05 查到今天；开盘前、周末查到上一个已收盘交易日。
  return marketDataDates(now, { clock, settledDate: settledDate ?? lastSettledTradingDate(now) }).dailyEndDate;
}

function round2(value) {
  return Math.round(value * 100) / 100;
}

function fail(code, message) {
  const error = new Error(message);
  error.code = code;
  throw error;
}

function log(context, code, fields = {}) {
  if (context.logger?.info) context.logger.info(code, fields);
}

function listen(server, host, port) {
  return new Promise((resolve, reject) => {
    const onError = (error) => reject(error);
    server.once('error', onError);
    server.listen(port, host, () => {
      server.off('error', onError);
      resolve();
    });
  });
}

function close(server) {
  return new Promise((resolve, reject) => {
    server.close((error) => (error ? reject(error) : resolve()));
  });
}
