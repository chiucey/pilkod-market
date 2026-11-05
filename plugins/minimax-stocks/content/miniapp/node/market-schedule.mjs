// @ts-check
// Pure A-share refresh scheduling rules (Asia/Shanghai), kept separate for deterministic tests.

const FINAL_REFRESH_MINUTE = 15 * 60 + 5; // 15:05，给收盘数据五分钟落库时间。

/**
 * @param {Date} [now]
 * @returns {{ date: string, minutes: number, isWeekday: boolean,
 *             phase: 'weekend'|'preopen'|'morning'|'lunch'|'afternoon'|'closing_wait'|'after_close',
 *             trading: boolean }}
 */
export function marketClock(now = new Date()) {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Shanghai', hourCycle: 'h23',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', weekday: 'short',
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(now)
      .filter((part) => part.type !== 'literal')
      .map((part) => [part.type, part.value]),
  );
  const minutes = Number(parts.hour) * 60 + Number(parts.minute);
  const isWeekday = !['Sat', 'Sun'].includes(parts.weekday);
  let phase;
  if (!isWeekday) phase = 'weekend';
  else if (minutes < 570) phase = 'preopen';
  else if (minutes < 690) phase = 'morning';
  else if (minutes < 780) phase = 'lunch';
  else if (minutes < 900) phase = 'afternoon';
  else if (minutes < FINAL_REFRESH_MINUTE) phase = 'closing_wait';
  else phase = 'after_close';
  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    minutes,
    isWeekday,
    phase,
    trading: phase === 'morning' || phase === 'afternoon',
  };
}

/** 最近一个已完成交易日（不接交易日历，周末跳过）。 */
export function lastSettledTradingDate(now = new Date()) {
  for (let back = 0; back < 10; back += 1) {
    const candidate = new Date(now.getTime() - back * 86_400_000);
    const clock = marketClock(candidate);
    if (!clock.isWeekday) continue;
    if (back === 0 && clock.minutes < FINAL_REFRESH_MINUTE) continue;
    return clock.date;
  }
  return marketClock(now).date;
}

/**
 * Decide whether one symbol may perform a scheduled network refresh now.
 *
 * - morning / afternoon: every timer tick;
 * - lunch: exactly one catch-up when the App missed the morning session;
 * - >=15:05: one closing refresh per symbol;
 * - preopen / weekend: only catch up a previously missed closing refresh.
 *
 * @param {Date} now
 * @param {any|null} entry
 */
export function marketRefreshPlan(now, entry) {
  const clock = marketClock(now);
  const settledDate = lastSettledTradingDate(now);
  const lastRefreshDate = typeof entry?.lastMarketRefreshDate === 'string'
    ? entry.lastMarketRefreshDate
    : null;
  const finalRefreshDate = typeof entry?.finalRefreshDate === 'string'
    ? entry.finalRefreshDate
    : null;
  const dataDate = typeof entry?.dataDate === 'string' ? entry.dataDate : null;

  if (clock.trading) {
    return { fetch: true, reason: 'trading', clock, settledDate, markFinalDate: null };
  }
  // 自愈：终刷标记声称完成，但本地数据日期仍落后于最近已结算交易日（例如
  // 数据源当时未提供当日数据、或升级前的旧标记），强制补拉直到数据跟上。
  if (dataDate !== null && dataDate < settledDate) {
    return { fetch: true, reason: 'stale-catchup', clock, settledDate, markFinalDate: settledDate };
  }
  // 午休：上午盘已经完整。没跑过上午盘（午休才启动）、或者手里的分时还不是今天的，就补拉一次今天的数据。
  const intradayStale = typeof entry?.intradayDate === 'string' && entry.intradayDate !== clock.date;
  if (clock.phase === 'lunch' && (lastRefreshDate !== clock.date || intradayStale)) {
    return { fetch: true, reason: 'lunch-catchup', clock, settledDate, markFinalDate: null };
  }
  if (clock.phase === 'after_close' && finalRefreshDate !== clock.date) {
    return { fetch: true, reason: 'closing-final', clock, settledDate, markFinalDate: clock.date };
  }
  const missedPreviousClose = ['preopen', 'weekend'].includes(clock.phase)
    && finalRefreshDate !== settledDate;
  if (missedPreviousClose) {
    return { fetch: true, reason: 'closing-catchup', clock, settledDate, markFinalDate: settledDate };
  }
  return { fetch: false, reason: 'idle', clock, settledDate, markFinalDate: null };
}

/**
 * 今天的交易是否已经开始、还没到收盘终刷：上午盘、午休、下午盘和 15:00–15:05。
 * 这段时间里「当前交易日」是今天——午休时上午盘已经完整，不能退回去展示昨天。
 * @param {{ phase: string }} clock
 */
export function sessionInProgress(clock) {
  return ['morning', 'lunch', 'afternoon', 'closing_wait'].includes(clock.phase);
}

/**
 * 这次刷新要取哪一天的日K（查询截止日）和分时。
 * - 盘中、午休、15:00–15:05：今天（午休启动时补拉的是今天上午盘，而不是昨天）；
 * - 收盘终刷 / 收盘后：今天（此时最近已收盘交易日就是今天）；
 * - 开盘前、周末：上一个已收盘交易日。
 * @param {Date} now
 * @param {{ clock?: any, settledDate?: string | null, markFinalDate?: string | null } | null} [plan]
 */
export function marketDataDates(now, plan = null) {
  const clock = plan?.clock ?? marketClock(now);
  const settledDate = plan?.settledDate ?? lastSettledTradingDate(now);
  if (sessionInProgress(clock)) return { dailyEndDate: clock.date, intradayDate: clock.date };
  return { dailyEndDate: settledDate, intradayDate: plan?.markFinalDate ?? settledDate };
}

/**
 * 行情源还没给出当天日K时（盘中常见），用当天的最新报价补一根临时 K 线，只用于展示：
 * 开盘、最高、最低、现价、成交量、成交额都是报价里的真实值；行情源给出当天日K后自然被替换。
 * @param {{ date: string } | undefined} lastBar
 * @param {any} latestQuote barsStore 里的 latestQuote（{ quote: { tradingDate, open, high, low, price, volume, amount } }）
 */
export function provisionalDailyBar(lastBar, latestQuote) {
  const q = latestQuote?.quote;
  if (!q || typeof q.tradingDate !== 'string' || !lastBar || q.tradingDate <= lastBar.date) return null;
  if (![q.open, q.high, q.low, q.price].every((value) => Number.isFinite(value) && value > 0)) return null;
  return {
    date: q.tradingDate,
    open: q.open,
    high: Math.max(q.high, q.price, q.open),
    low: Math.min(q.low, q.price, q.open),
    close: q.price,
    previousClose: Number.isFinite(q.previousClose) ? q.previousClose : undefined,
    volume: Number.isFinite(q.volume) ? q.volume : 0,
    amount: Number.isFinite(q.amount) ? q.amount : 0,
    isFinal: false,
    source: 'latest_quote',
  };
}

export const MARKET_FINAL_REFRESH_MINUTE = FINAL_REFRESH_MINUTE;
