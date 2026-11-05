import assert from 'node:assert/strict';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import test from 'node:test';
import {
  MIN_FULL_HISTORY_BARS,
  hasSufficientFullHistory,
  needsFullHistoryRepair,
} from '../miniapp/node/history-policy.mjs';
import { createBarsStore } from '../miniapp/node/bars-store.mjs';

function rows(count, startDate = '2023-08-21') {
  const start = new Date(`${startDate}T00:00:00Z`);
  return Array.from({ length: count }, (_, index) => {
    const date = new Date(start);
    date.setUTCDate(date.getUTCDate() + index);
    return {
      date: date.toISOString().slice(0, 10),
      open: 1,
      high: 1,
      low: 1,
      close: 1,
      previousClose: 1,
      volume: 1,
      amount: 1,
      isFinal: true,
    };
  });
}

test('rejects quote-only and short-tail full-history responses', () => {
  const short = rows(1, '2026-09-18');
  assert.equal(hasSufficientFullHistory({
    items: short,
    effectiveRange: { startDate: '2026-09-18', endDate: '2026-09-18' },
    latestAvailableDate: '2026-09-18',
  }, '2023-08-21'), false);
  assert.equal(needsFullHistoryRepair({ full: true, bars: rows(14, '2026-09-01') }), true);
});

test('accepts complete historical range even when today is unavailable', () => {
  const history = rows(MIN_FULL_HISTORY_BARS, '2023-08-21');
  assert.equal(hasSufficientFullHistory({
    items: history,
    effectiveRange: { startDate: '2022-08-11', endDate: history.at(-1).date },
    latestAvailableDate: history.at(-1).date,
    coverageComplete: false,
  }, '2023-08-21'), true);
  assert.equal(needsFullHistoryRepair({ full: true, bars: history }), false);
});

test('allows a poisoned full cache to be downgraded', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'minimax-stocks-'));
  try {
    const store = await createBarsStore(directory);
    await store.setBars('600100.SH', rows(MIN_FULL_HISTORY_BARS), { full: true });
    const repaired = await store.setBars('600100.SH', rows(1, '2026-09-18'), {
      full: false,
      coverageComplete: false,
    });
    assert.equal(repaired.full, false);
    assert.equal(repaired.dailyCoverageComplete, false);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
