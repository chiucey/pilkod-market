---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 6b853baedfd03a95b146fd209e67fbb2
    PropagateID: 6b853baedfd03a95b146fd209e67fbb2
    ReservedCode1: 304502204acd14f5e7902d33edc46530e86f5779e5f98ba7bd49267156b7c75485485e6a0221009bd313cfc80f6518507b881f9e197f595cc7b24c45dfde60036f60f29fed9dc1
    ReservedCode2: 304402204f10630ef4caa085d2c0c9989713db807094d7d585f71f1616d390a4e52edbb302202aadc5d07756ad1d91462de57dfc6f928c681d6970ce89ea8a8e238b7e7a81d6
---

# Reference

## Project mapping

- Portable snapshot:
  - `.cursor/skills/supplier-pricing-core/vendor/scripts/main.py`
  - `.cursor/skills/supplier-pricing-core/vendor/scripts/api_server.py`
- Backend logic: `extracted_project/skills/taobao/scripts/main.py`
- Backend API: `extracted_project/skills/taobao/scripts/api_server.py`
- Data store: `extracted_project/skills/taobao/data/suppliers.json`
- Upstream skill doc snapshot: `extracted_project/skills/taobao/SKILL.md`

## What to edit for common requests

- "Adjust matching quality":
  - `NLPMatcher.check_brand_match`
  - `NLPMatcher.match_score`
  - `NLPMatcher.match` thresholds
- "Adjust outlier handling / average":
  - `_trimmed_mean_prices`
  - `_filter_matches_by_price_band`
  - `analyze_price`
- "Adjust listing thresholds":
  - `THRESHOLD_AVG_AUTO_LIST`
  - `THRESHOLD_AVG_REVIEW`
  - `should_list`
- "Adjust API output fields":
  - `/api/analyze/<id>`
  - `/api/batch-analyze`

## Batch analyze consistency checklist

- Uses same market data retrieval path as single analyze
- Uses same matcher threshold and `should_list`
- Writes back `status` and `updated_at`
- Returns `deviation_from_avg` in payload
- Handles `pending` request filter with `review` inclusion when expected by product UX

## Persistence checklist

- DataStore write uses flush + fsync
- Product status updates save to `suppliers.json`
- `updated_at` changes on each status write

## Notes

- Search-based market results can vary over time for same keyword.
- `goods_id` identifies a matched listing from a given search result; it is not currently a lock-price flow by itself.

