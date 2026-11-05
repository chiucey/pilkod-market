// Daily history completeness rules shared by startup repair and full-fetch handling.

// A three-year A-share daily history should contain substantially more than one
// trading year. This catches quote-only and short-tail responses without
// requiring the provider to expose an exact expected trading-day count.
export const MIN_FULL_HISTORY_BARS = 250;

/**
 * Whether a provider response is sufficient to be treated as a full history.
 * coverageComplete may be false when endDate is today and today's session is
 * not available yet; the historical range is still acceptable when it reaches
 * the provider's latest available date and starts no later than the request.
 *
 * @param {any} bundle
 * @param {string} expectedStartDate
 */
export function hasSufficientFullHistory(bundle, expectedStartDate) {
  const items = Array.isArray(bundle?.items) ? bundle.items : [];
  if (items.length < MIN_FULL_HISTORY_BARS || typeof expectedStartDate !== 'string') return false;

  const firstItemDate = items[0]?.date;
  const lastItemDate = items.at(-1)?.date;
  const effectiveStartDate = typeof bundle?.effectiveRange?.startDate === 'string'
    ? bundle.effectiveRange.startDate
    : firstItemDate;
  const effectiveEndDate = typeof bundle?.effectiveRange?.endDate === 'string'
    ? bundle.effectiveRange.endDate
    : lastItemDate;
  const latestAvailableDate = bundle?.latestAvailableDate ?? bundle?.dataDate ?? lastItemDate;

  return typeof effectiveStartDate === 'string'
    && effectiveStartDate <= expectedStartDate
    && typeof effectiveEndDate === 'string'
    && typeof latestAvailableDate === 'string'
    && effectiveEndDate >= latestAvailableDate
    && lastItemDate >= latestAvailableDate;
}

/**
 * Whether a persisted entry must be repaired with a full history request.
 * @param {any|null} entry
 */
export function needsFullHistoryRepair(entry) {
  return !entry?.full
    || !Array.isArray(entry.bars)
    || entry.bars.length < MIN_FULL_HISTORY_BARS;
}
