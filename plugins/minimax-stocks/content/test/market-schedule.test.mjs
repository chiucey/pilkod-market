import assert from 'node:assert/strict';
import test from 'node:test';
import { marketClock, marketDataDates, marketRefreshPlan, provisionalDailyBar, sessionInProgress } from '../miniapp/node/market-schedule.mjs';

const at = (iso) => new Date(iso);

test('market data dates: lunch break and 15:00–15:05 belong to today, preopen and weekends to the last settled day', () => {
  // 周二 2026-10-27
  assert.deepEqual(marketDataDates(at('2026-10-27T10:00:00+08:00')), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' }, 'morning session');
  assert.deepEqual(marketDataDates(at('2026-10-27T11:40:00+08:00')), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' }, 'lunch break shows this morning, not yesterday');
  assert.deepEqual(marketDataDates(at('2026-10-27T14:00:00+08:00')), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' }, 'afternoon session');
  assert.deepEqual(marketDataDates(at('2026-10-27T15:02:00+08:00')), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' }, 'closed but before the final refresh');
  assert.deepEqual(marketDataDates(at('2026-10-27T15:10:00+08:00')), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' }, 'after close');
  assert.deepEqual(marketDataDates(at('2026-10-27T09:00:00+08:00')), { dailyEndDate: '2026-10-26', intradayDate: '2026-10-26' }, 'before the open');
  assert.deepEqual(marketDataDates(at('2026-10-31T10:00:00+08:00')), { dailyEndDate: '2026-10-30', intradayDate: '2026-10-30' }, 'Saturday');
  assert.deepEqual(marketDataDates(at('2026-11-02T09:00:00+08:00')), { dailyEndDate: '2026-10-30', intradayDate: '2026-10-30' }, 'Monday before the open');
  // 计划里带了终刷日期时，分时取终刷那天
  const now = at('2026-10-28T08:00:00+08:00');
  const plan = marketRefreshPlan(now, { lastMarketRefreshDate: '2026-10-27', finalRefreshDate: '2026-10-26', dataDate: '2026-10-27' });
  assert.equal(plan.reason, 'closing-catchup');
  assert.deepEqual(marketDataDates(now, plan), { dailyEndDate: '2026-10-27', intradayDate: '2026-10-27' });
  assert.equal(sessionInProgress(marketClock(at('2026-10-27T12:30:00+08:00'))), true);
  assert.equal(sessionInProgress(marketClock(at('2026-10-27T15:06:00+08:00'))), false);
});

test('lunch break: catch up today once, and again while the cached intraday is still not today', () => {
  const now = at('2026-10-27T11:40:00+08:00');
  assert.equal(marketRefreshPlan(now, { lastMarketRefreshDate: '2026-10-26', intradayDate: '2026-10-26', dataDate: '2026-10-26' }).reason, 'lunch-catchup', 'app started during lunch, morning was missed');
  assert.equal(marketRefreshPlan(now, { lastMarketRefreshDate: '2026-10-27', intradayDate: '2026-10-26', dataDate: '2026-10-26' }).reason, 'lunch-catchup', 'refreshed today but intraday is still yesterday');
  const idle = marketRefreshPlan(now, { lastMarketRefreshDate: '2026-10-27', intradayDate: '2026-10-27', dataDate: '2026-10-27' });
  assert.equal(idle.fetch, false, 'morning already complete: no polling during lunch');
  assert.equal(marketRefreshPlan(at('2026-10-27T10:31:00+08:00'), null).reason, 'trading');
});

test('provisional daily bar from today\'s quote while the provider has no daily bar for today yet', () => {
  const lastBar = { date: '2026-10-26', open: 597.01, high: 601.8, low: 572.01, close: 594.5 };
  const latestQuote = { quote: { tradingDate: '2026-10-27', price: 603.3, previousClose: 594.5, open: 611, high: 617.19, low: 595.5, volume: 14490000, amount: 8776000000 } };
  assert.deepEqual(provisionalDailyBar(lastBar, latestQuote), {
    date: '2026-10-27', open: 611, high: 617.19, low: 595.5, close: 603.3, previousClose: 594.5,
    volume: 14490000, amount: 8776000000, isFinal: false, source: 'latest_quote',
  });
  assert.equal(provisionalDailyBar({ ...lastBar, date: '2026-10-27' }, latestQuote), null, 'provider already has today');
  assert.equal(provisionalDailyBar(lastBar, { quote: { ...latestQuote.quote, price: 0 } }), null, 'no usable price');
  assert.equal(provisionalDailyBar(lastBar, null), null);
  // 报价的最高 / 最低没跟上现价时，K 线仍然包住现价
  const bar = provisionalDailyBar(lastBar, { quote: { ...latestQuote.quote, high: 600, low: 605, price: 610 } });
  assert.equal(bar.high, 611);
  assert.equal(bar.low, 605);
});
