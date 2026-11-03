// @ts-check
// Host Connector gateway for the 股市 runtime.
// Providers and tool shapes below were probe-verified on 2026-09-11 (hengsheng_market 1.3.0):
//   hengsheng_market.get_latest_quote    {symbol} → { quote|null, dataDate, latestAvailableDate, asOf, isFinal, revision }
//   hengsheng_market.get_daily_bars      {symbol,startDate,endDate,warmupBars,adjustment,knownBasisVersion}
//   hengsheng_market.get_intraday_series {symbol,tradingDate,intervalMinutes(必须显式传 1)}
//   comein.searchAnalystComments         {query,start_time,topK}
//   comein.get_stock_details             {queries[],include[]}
import { decodeHostConnectorValue } from './host-connector-value.mjs';

const HENGSHENG = 'hengsheng_market';
const COMEIN = 'comein';
const TENCENTDOCS = 'tencentdocs';

export function createConnectorGateway(context) {
  const connector = /** @type {any} */ (context.hostConnector);
  if (!connector) return null;

  /** @type {Map<string, string>} */
  const toolRefs = new Map();
  /** @type {Set<string>} */
  let lastToolNames = new Set();
  let inventoryFetchedAt = 0;
  let inventoryInFlight = null;

  async function refreshInventory(force = false) {
    if (!force && Date.now() - inventoryFetchedAt < 5_000 && lastToolNames.size > 0) {
      return lastToolNames;
    }
    if (inventoryInFlight) return inventoryInFlight;
    inventoryInFlight = (async () => {
      const inventory = await connector.list();
      const tools = Array.isArray(inventory?.tools) ? inventory.tools : [];
      const names = new Set();
      for (const entry of tools) {
        if (typeof entry?.provider !== 'string' || typeof entry?.name !== 'string') continue;
        const key = `${entry.provider}.${entry.name}`;
        names.add(key);
        if (typeof entry.toolRef === 'string') toolRefs.set(key, entry.toolRef);
      }
      // 短暂空清单不清掉上一轮可用引用；真实 call 仍会验证其是否有效。
      if (names.size > 0) lastToolNames = names;
      inventoryFetchedAt = Date.now();
      return new Set([...lastToolNames, ...names]);
    })().finally(() => { inventoryInFlight = null; });
    return inventoryInFlight;
  }

  async function resolveToolRef(provider, name) {
    const key = `${provider}.${name}`;
    if (toolRefs.has(key)) return toolRefs.get(key);
    const delays = [0, 150, 600];
    for (const delay of delays) {
      if (delay > 0) await wait(delay);
      await refreshInventory(true);
      if (toolRefs.has(key)) return toolRefs.get(key);
    }
    fail('CONNECTOR_TOOL_MISSING', `${key} is not in the Host Connector inventory`);
  }

  async function call(provider, name, args) {
    const key = `${provider}.${name}`;
    let toolRef = await resolveToolRef(provider, name);
    try {
      const result = await connector.call(toolRef, args);
      return decodeHostConnectorValue(result?.value);
    } catch (error) {
      // 工具引用可能因 Host 重连而失效；强制重取一次后只重试这一回。
      toolRefs.delete(key);
      await refreshInventory(true);
      const refreshed = toolRefs.get(key);
      if (!refreshed || refreshed === toolRef) throw error;
      toolRef = refreshed;
      const result = await connector.call(toolRef, args);
      return decodeHostConnectorValue(result?.value);
    }
  }

  return {
    /** Capability probe: returns a Set of "provider.name" currently in the inventory. */
    async listToolNames() {
      return refreshInventory(false);
    },

    /**
     * Latest quote (hengsheng_market 1.3.0). `quote` may be null when no valid
     * quote exists; callers must keep their last good value in that case.
     */
    async fetchLatestQuote(symbol) {
      const decoded = await call(HENGSHENG, 'get_latest_quote', { symbol });
      if (!isRecord(decoded)) {
        fail('CONNECTOR_PARSE_ERROR', 'get_latest_quote returned an unexpected shape');
      }
      let quote = null;
      if (isRecord(decoded.quote)) {
        const q = decoded.quote;
        const numeric = ['price', 'previousClose', 'open', 'high', 'low', 'change', 'changePercent'];
        if (numeric.every((key) => Number.isFinite(q[key])) && typeof q.tradingDate === 'string') {
          quote = {
            tradingDate: q.tradingDate,
            price: q.price,
            previousClose: q.previousClose,
            open: q.open,
            high: q.high,
            low: q.low,
            change: q.change,
            changePercent: q.changePercent, // 已是百分数，不再乘 100
            volume: Number.isFinite(q.volume) ? q.volume : 0,
            amount: Number.isFinite(q.amount) ? q.amount : 0,
          };
        }
      }
      return {
        quote,
        status: String(decoded.status ?? ''),
        reason: typeof decoded.reason === 'string' ? decoded.reason : null,
        dataDate: typeof decoded.dataDate === 'string' ? decoded.dataDate : null,
        latestAvailableDate: typeof decoded.latestAvailableDate === 'string' ? decoded.latestAvailableDate : null,
        asOf: typeof decoded.asOf === 'string' ? decoded.asOf : null,
        fetchedAt: typeof decoded.fetchedAt === 'string' ? decoded.fetchedAt : new Date().toISOString(),
        isFinal: decoded.isFinal === true,
        revision: typeof decoded.revision === 'string' ? decoded.revision : null,
        cacheStatus: typeof decoded.cacheStatus === 'string' ? decoded.cacheStatus : null,
      };
    },

    /**
     * Daily K bars. Returns { items, fetchedAt, dataDate, status, basisVersion, reloadRequired }.
     * An explicitly empty provider result returns items: [] instead of throwing,
     * so callers can keep local history untouched.
     */
    async fetchDailyBars(symbol, { startDate, endDate, warmupBars = 0, knownBasisVersion = null }) {
      const args = { symbol, startDate, endDate, warmupBars, adjustment: 'none' };
      if (typeof knownBasisVersion === 'string' && knownBasisVersion !== '') args.knownBasisVersion = knownBasisVersion;
      const decoded = await call(HENGSHENG, 'get_daily_bars', args);
      if (!isRecord(decoded) || !Array.isArray(decoded.items)) {
        fail('CONNECTOR_PARSE_ERROR', 'get_daily_bars returned an unexpected shape');
      }
      const items = decoded.items
        .filter((row) => isRecord(row)
          && typeof row.date === 'string'
          && ['open', 'high', 'low', 'close', 'previousClose'].every((key) => Number.isFinite(row[key])))
        .map((row) => ({
          date: row.date,
          open: row.open, high: row.high, low: row.low, close: row.close,
          previousClose: row.previousClose,
          volume: Number.isFinite(row.volume) ? row.volume : 0,
          amount: Number.isFinite(row.amount) ? row.amount : 0,
          isFinal: row.isFinal === true,
          ...(typeof row.source === 'string' ? { source: row.source } : {}),
        }));
      const errorCodes = Array.isArray(decoded.errors)
        ? decoded.errors.map((entry) => (isRecord(entry) ? String(entry.code ?? '') : '')).filter((code) => code !== '')
        : [];
      return {
        items,
        status: String(decoded.status ?? ''),
        reason: typeof decoded.reason === 'string' ? decoded.reason : null,
        fetchedAt: typeof decoded.fetchedAt === 'string' ? decoded.fetchedAt : new Date().toISOString(),
        dataDate: typeof decoded.dataDate === 'string' ? decoded.dataDate : (items.at(-1)?.date ?? null),
        latestAvailableDate: typeof decoded.latestAvailableDate === 'string' ? decoded.latestAvailableDate : null,
        basisVersion: typeof decoded.basisVersion === 'string' ? decoded.basisVersion : null,
        revision: typeof decoded.revision === 'string' ? decoded.revision : null,
        updateMode: typeof decoded.updateMode === 'string' ? decoded.updateMode : 'replace',
        requestedRange: isRecord(decoded.requestedRange) ? decoded.requestedRange : { startDate, endDate },
        effectiveRange: isRecord(decoded.effectiveRange) ? decoded.effectiveRange : null,
        coverageComplete: decoded.coverageComplete !== false,
        reloadRequired: decoded.reloadRequired === true || errorCodes.includes('HISTORY_REVISION_CHANGED'),
        errorCodes,
      };
    },

    /**
     * One-minute intraday series for one explicit trading date (intervalMinutes
     * must be sent as 1: the provider keeps a legacy 5-minute default).
     * The provider returns a complete daily replacement; an explicitly empty
     * result keeps items: [] with reason so callers preserve local caches.
     */
    async fetchIntraday(symbol, tradingDate) {
      const decoded = await call(HENGSHENG, 'get_intraday_series', {
        symbol, tradingDate, intervalMinutes: 1,
      });
      if (!isRecord(decoded) || !Array.isArray(decoded.items)) {
        fail('CONNECTOR_PARSE_ERROR', 'get_intraday_series returned an unexpected shape');
      }
      const items = decoded.items
        .filter((row) => isRecord(row) && typeof row.timestamp === 'string' && Number.isFinite(row.price))
        .map((row) => ({
          timestamp: String(row.timestamp),
          time: String(row.timestamp).slice(11, 16),
          price: row.price,
          volume: Number.isFinite(row.volume) ? row.volume : 0,
          amount: Number.isFinite(row.amount) ? row.amount : 0,
          isFinal: row.isFinal === true,
        }));
      return {
        items,
        status: String(decoded.status ?? ''),
        reason: typeof decoded.reason === 'string' ? decoded.reason : null,
        dataDate: typeof decoded.dataDate === 'string' ? decoded.dataDate : null,
        latestAvailableDate: typeof decoded.latestAvailableDate === 'string' ? decoded.latestAvailableDate : null,
        asOf: typeof decoded.asOf === 'string' ? decoded.asOf : null,
        fetchedAt: typeof decoded.fetchedAt === 'string' ? decoded.fetchedAt : new Date().toISOString(),
        isFinal: decoded.isFinal === true,
        revision: typeof decoded.revision === 'string' ? decoded.revision : null,
        updateMode: typeof decoded.updateMode === 'string' ? decoded.updateMode : 'replace',
        coverageComplete: decoded.coverageComplete !== false,
      };
    },

    /** Analyst comment feed from 进门财经. Returns normalized sentiment items. */
    async fetchAnalystComments(query, startDate, topK = 20) {
      const decoded = await call(COMEIN, 'searchAnalystComments', {
        query, start_time: startDate, topK,
      });
      if (!Array.isArray(decoded)) {
        fail('CONNECTOR_PARSE_ERROR', 'searchAnalystComments returned an unexpected shape');
      }
      return decoded
        .filter((row) => isRecord(row) && typeof row.title === 'string' && row.title.trim() !== '')
        .map((row) => {
          const body = typeof row.viewpoint === 'string' && row.viewpoint.trim() !== ''
            ? row.viewpoint.trim()
            : (typeof row.chunkText === 'string' ? row.chunkText.trim() : '');
          const publishedAt = Number.isFinite(row.businessTime)
            ? new Date(row.businessTime).toISOString()
            : '';
          const tags = [row.docType, row.institutionName]
            .filter((tag) => typeof tag === 'string' && tag.trim() !== '')
            .map((tag) => String(tag));
          const id = typeof row.docId === 'string' && row.docId !== ''
            ? `comein-${row.docId}`
            : `comein-${typeof row.chunkId === 'string' ? row.chunkId : Math.random().toString(36).slice(2)}`;
          return {
            id,
            source: '进门财经',
            title: row.title.trim(),
            summary: body.slice(0, 180),
            content: body,
            publishedAt,
            tags,
          };
        })
        .filter((item) => item.publishedAt !== '' && item.content !== '');
    },

    /**
     * Instrument search (code / exchange-prefixed code / Chinese name / keyword).
     * Returns { matchStatus: 'exact'|'candidates'|'not_found', items: [{symbol, shortName, exchangeName}] }.
     */
    async searchInstruments(query, limit = 8) {
      const decoded = await call(HENGSHENG, 'search_instruments', { query, limit });
      if (!isRecord(decoded) || !Array.isArray(decoded.items) || typeof decoded.matchStatus !== 'string') {
        fail('CONNECTOR_PARSE_ERROR', 'search_instruments returned an unexpected shape');
      }
      return {
        matchStatus: decoded.matchStatus,
        items: decoded.items
          .filter((row) => isRecord(row) && typeof row.symbol === 'string' && typeof row.shortName === 'string')
          .map((row) => ({
            symbol: row.symbol,
            shortName: row.shortName,
            exchangeName: typeof row.exchangeName === 'string' ? row.exchangeName : '',
          })),
      };
    },

    /** 腾讯文档全局搜索，映射为舆情条目（文档标题命中即收录，点击跳原文）。 */
    async fetchTencentDocs(query) {
      const decoded = await call(TENCENTDOCS, 'manage.search_file', { search_key: query });
      if (!isRecord(decoded) || !Array.isArray(decoded.list)) {
        fail('CONNECTOR_PARSE_ERROR', 'manage.search_file returned an unexpected shape');
      }
      const extLabels = {
        tencentdoc: '文档', tencentsheet: '表格', tencentslide: '幻灯片',
        smartcanvas: '智能文档', tencentform: '收集表', tencentmind: '思维导图',
      };
      return decoded.list
        .filter((row) => isRecord(row)
          && typeof row.title === 'string' && row.title.trim() !== ''
          && typeof row.file_id === 'string' && row.file_id !== '')
        .map((row) => {
          const millis = Number(row.modify_time);
          const publishedAt = Number.isFinite(millis) && millis > 0 ? new Date(millis).toISOString() : '';
          const extLabel = extLabels[String(row.ext ?? '')] ?? '文档';
          const modifier = typeof row.modifier_nick === 'string' ? row.modifier_nick.trim() : '';
          const summary = `腾讯文档${extLabel}${modifier ? ` · ${modifier} 最后编辑` : ''}`;
          let url;
          try {
            const parsed = new URL(String(row.url));
            if (['http:', 'https:'].includes(parsed.protocol)) url = parsed.href;
          } catch { url = undefined; }
          return {
            id: `tdoc-${row.file_id}`,
            source: '腾讯文档',
            title: row.title.trim(),
            summary,
            content: summary,
            publishedAt,
            tags: [extLabel, ...(modifier ? [modifier] : [])],
            ...(url ? { url } : {}),
          };
        })
        .filter((item) => item.publishedAt !== '');
    },

    /** Resolve a stock short name via 进门财经. Returns null when unresolved. */
    async fetchShortName(symbol) {
      const compact = comeinCode(symbol);
      if (!compact) return null;
      const decoded = await call(COMEIN, 'get_stock_details', {
        queries: [compact], include: ['standardized_info'],
      });
      if (!isRecord(decoded) || !Array.isArray(decoded.data)) return null;
      const info = decoded.data.find((row) => isRecord(row) && isRecord(row.standardized_info))?.standardized_info;
      const name = info && typeof info.stock_short_name === 'string' ? info.stock_short_name.trim() : '';
      return name === '' ? null : name;
    },
  };
}

/** '600519.SH' → 'sh600519' (进门财经 code format). */
function comeinCode(symbol) {
  const match = String(symbol).toUpperCase().match(/^(\d{6})\.(SH|SZ|BJ)$/);
  return match ? `${match[2].toLowerCase()}${match[1]}` : null;
}

function isRecord(value) {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function wait(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

function fail(code, message) {
  const error = new Error(message);
  error.code = code;
  throw error;
}
