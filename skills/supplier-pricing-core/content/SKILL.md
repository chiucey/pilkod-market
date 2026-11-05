---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 20f9e646cf3808574492182c8449409a
    PropagateID: 20f9e646cf3808574492182c8449409a
    ReservedCode1: 304502206008cf088955e3fb801fae66d2941ee6fa3675af9a81646ec896556285eee7ae022100a254d2092b296ab27ba133b57eeed0ade4a587ac52fc8fbdb0c2021f494233c3
    ReservedCode2: 3046022100e60a1bb86866a30bacad62925798825b2bb9e9e2e5af4b08cde2ada1e6edda07022100afef4e1724265f24286098f6217de073cafffb3bb9f6edc0ed4e3560761bb161
description: Maintains supplier pricing business logic for this workspace, including NLP matching, price analysis, listing decisions, and taobao API scripts. Use when the user asks to modify pricing rules, match scoring, analyze endpoints, batch analyze behavior, or suppliers data flow in extracted_project/skills/taobao/scripts.
name: supplier-pricing-core
---

# Supplier Pricing Core

Use this skill for backend business logic, with a portable vendor copy included.

## Scope

- Portable backend copy (preferred for migration):
  - `.cursor/skills/supplier-pricing-core/vendor/scripts/main.py`
  - `.cursor/skills/supplier-pricing-core/vendor/scripts/api_server.py`
- Workspace backend source:
  - `extracted_project/skills/taobao/scripts/main.py`
  - `extracted_project/skills/taobao/scripts/api_server.py`
- Data file:
  - `extracted_project/skills/taobao/data/suppliers.json`
- Do not treat frontend text as source of truth for rules. Frontend should follow backend outputs.

## Current business baseline

### Matching score

`final_score = brand*0.45 + name*0.40 + model*0.10 + cosine*0.05`

- `brand`: alias/dictionary hit score (`check_brand_match`)
- `name`: max(name in title, Levenshtein similarity)
- `model`: max(model in title, Levenshtein similarity)
- `cosine`: TF-IDF cosine on combined text

Thresholds:

- `>= 0.75` -> `exact`
- `>= 0.50` and `< 0.75` -> `similar`
- `< 0.50` -> `none`

### Listing decision

Use `deviation_from_avg = (supplier_price - avg_price) / avg_price`.

- `abs(deviation_from_avg) <= 0.10` -> `listed`
- `0.10 < abs(deviation_from_avg) <= 0.20` -> `review`
- `abs(deviation_from_avg) > 0.20` -> `delisted`

For no matches or invalid average price, return `review`.

## API behavior expectations

- `/api/analyze/<id>` and `/api/batch-analyze` must use the same market data path and same `should_list` rules.
- Batch analyze should persist `status` and `updated_at` back to `suppliers.json`.
- Status mapping to persisted goods:
  - `listed -> listed`
  - `review -> review`
  - `delisted -> delisted`
  - `rejected -> review`

## Runbook

Start backend (portable-first):

```bash
python .cursor/skills/supplier-pricing-core/scripts/run_backend.py
```

Quick health check:

```bash
python .cursor/skills/supplier-pricing-core/scripts/health_check.py
```

## Change workflow

1. Edit `main.py` for match score, analyze metrics, and `should_list`.
2. Edit `api_server.py` for endpoint fields and persistence behavior.
3. Keep API response fields stable for consumers:
   - `deviation_from_avg`, `action`, `reason`, `market_matches`
4. If rule semantics change, update `reference.md`.

## Additional details

- See [reference.md](reference.md) for architecture and checklist.

