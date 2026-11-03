// @ts-check
// Local per-symbol market data store with incremental merge.
// Files live under <dataDir>/bars/<SYMBOL>.json:
//   { symbol, full, bars: [{date,open,high,low,close,previousClose,volume,amount}],
//     updatedAt, intradayDate, intraday, intradayFetchedAt }
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';
import { join } from 'node:path';

const MAX_BARS = 1300;

export async function createBarsStore(dataDir) {
  const root = join(dataDir, 'bars');
  await mkdir(root, { recursive: true });
  /** @type {Map<string, any>} */
  const cache = new Map();

  function fileFor(symbol) {
    return join(root, `${symbol.replace(/[^0-9A-Z.]/gi, '')}.json`);
  }

  async function load(symbol) {
    if (cache.has(symbol)) return cache.get(symbol);
    try {
      const entry = JSON.parse(await readFile(fileFor(symbol), 'utf8'));
      if (entry && Array.isArray(entry.bars)) {
        cache.set(symbol, entry);
        return entry;
      }
    } catch (error) {
      if (error?.code !== 'ENOENT' && !(error instanceof SyntaxError)) throw error;
    }
    return null;
  }

  async function persist(symbol) {
    const entry = cache.get(symbol);
    if (!entry) return;
    const pending = `${fileFor(symbol)}.pending`;
    await writeFile(pending, JSON.stringify(entry), 'utf8');
    await rename(pending, fileFor(symbol));
  }

  return {
    /** Cached entry or null. */
    get: load,

    /** Replace the whole bar history (initial or upgraded fetch). */
    async setBars(symbol, bars, {
      full = undefined,
      basisVersion = undefined,
      revision = undefined,
      coverageComplete = undefined,
    }) {
      const previous = cache.get(symbol) ?? {};
      cache.set(symbol, {
        ...previous,
        symbol,
        // An explicit false must be able to downgrade a poisoned full=true cache.
        full: full === undefined ? Boolean(previous.full) : Boolean(full),
        bars: dedupeSorted(bars).slice(-MAX_BARS),
        ...(basisVersion !== undefined ? { basisVersion } : {}),
        ...(revision !== undefined ? { dailyRevision: revision } : {}),
        ...(coverageComplete !== undefined ? { dailyCoverageComplete: coverageComplete === true } : {}),
        updatedAt: new Date().toISOString(),
      });
      await persist(symbol);
      return cache.get(symbol);
    },

    /** Merge an incremental delta: overlapping dates are replaced, new dates appended. */
    async mergeBars(symbol, delta, {
      full = undefined,
      basisVersion = undefined,
      revision = undefined,
      coverageComplete = undefined,
    } = {}) {
      const entry = (await load(symbol)) ?? { symbol, full: false, bars: [] };
      const byDate = new Map(entry.bars.map((row) => [row.date, row]));
      for (const row of delta) byDate.set(row.date, row);
      entry.bars = dedupeSorted([...byDate.values()]).slice(-MAX_BARS);
      if (full !== undefined) entry.full = Boolean(full);
      if (basisVersion !== undefined) entry.basisVersion = basisVersion;
      if (revision !== undefined) entry.dailyRevision = revision;
      if (coverageComplete !== undefined) entry.dailyCoverageComplete = coverageComplete === true;
      entry.updatedAt = new Date().toISOString();
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },

    /**
     * updateMode=replace semantics: a complete provider response replaces every
     * local bar inside the requested range, so in-range supplier revisions
     * (including removed rows) are accepted. Rows outside the range are kept.
     */
    async replaceBarsRange(symbol, rows, {
      startDate,
      endDate,
      full = undefined,
      basisVersion = undefined,
      revision = undefined,
      coverageComplete = undefined,
    }) {
      const entry = (await load(symbol)) ?? { symbol, full: false, bars: [] };
      const kept = entry.bars.filter((row) => row.date < startDate || row.date > endDate);
      entry.bars = dedupeSorted([...kept, ...rows]).slice(-MAX_BARS);
      if (full !== undefined) entry.full = Boolean(full);
      if (basisVersion !== undefined) entry.basisVersion = basisVersion;
      if (revision !== undefined) entry.dailyRevision = revision;
      if (coverageComplete !== undefined) entry.dailyCoverageComplete = coverageComplete === true;
      entry.updatedAt = new Date().toISOString();
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },

    /** Store the latest quote payload (provider truth; kept when a later poll returns quote=null). */
    async setQuote(symbol, quotePayload) {
      const entry = (await load(symbol)) ?? { symbol, full: false, bars: [] };
      entry.latestQuote = quotePayload;
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },

    /**
     * Replace the intraday series for one trading date (the provider returns a
     * complete daily replacement). Empty rows never overwrite an existing day.
     */
    async setIntraday(symbol, date, rows, {
      isFinal = false, asOf = null, revision = null, coverageComplete = true,
    } = {}) {
      const entry = (await load(symbol)) ?? { symbol, full: false, bars: [] };
      if (coverageComplete || entry.intradayDate !== date || !Array.isArray(entry.intraday)) {
        entry.intraday = dedupeIntraday(rows);
      } else {
        entry.intraday = dedupeIntraday([...entry.intraday, ...rows]);
      }
      entry.intradayDate = date;
      entry.intradayFinal = isFinal === true;
      entry.intradayAsOf = asOf;
      entry.intradayRevision = revision;
      entry.intradayFetchedAt = new Date().toISOString();
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },

    /** Record one successful network refresh for scheduling and diagnostics. */
    async markRefresh(symbol, { date, reason, providerFetchedAt, dataDate }) {
      const entry = await load(symbol);
      if (!entry) return null;
      entry.lastMarketRefreshDate = date;
      entry.lastMarketRefreshAt = new Date().toISOString();
      entry.lastMarketRefreshReason = reason;
      entry.providerFetchedAt = providerFetchedAt ?? null;
      entry.dataDate = dataDate ?? entry.bars.at(-1)?.date ?? null;
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },

    /** Record that the closing "final refresh" for the given trading date is done. */
    async markFinal(symbol, date) {
      const entry = await load(symbol);
      if (!entry) return null;
      entry.finalRefreshDate = date;
      entry.finalRefreshAt = new Date().toISOString();
      cache.set(symbol, entry);
      await persist(symbol);
      return entry;
    },
  };
}

function dedupeSorted(bars) {
  const byDate = new Map();
  for (const row of bars) byDate.set(row.date, row);
  return [...byDate.values()].sort((a, b) => a.date.localeCompare(b.date));
}

function dedupeIntraday(rows) {
  const byTimestamp = new Map();
  for (const row of rows) byTimestamp.set(row.timestamp, row);
  return [...byTimestamp.values()].sort((a, b) => a.timestamp.localeCompare(b.timestamp));
}
