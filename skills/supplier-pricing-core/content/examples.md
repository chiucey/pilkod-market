---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 953ffa3239925725696e489fa105e1ae
    PropagateID: 953ffa3239925725696e489fa105e1ae
    ReservedCode1: 304502206ed6d430b658f80a2954229eeda9e252fc40c0ffe1d44ef1f670405df0166db0022100cc4a699e7800b5f5153346a89f992df678c260aeee2e2b6d9622d12ae533de30
    ReservedCode2: 30440220073e7e3c287f74fb008890f458f2c185824cf92c2565fc8f535ff2237ffcd38402206cf318adb4ceb30304385dc63dc5eb54eb19949f698b552bd2940777e4d36909
---

# Examples

## Example: adjust listing thresholds

User asks: "Change review range from 10%-20% to 10%-15%."

Expected edits:

- `extracted_project/skills/taobao/scripts/main.py`
  - update `THRESHOLD_AVG_REVIEW`
  - keep `should_list` wording aligned
- `extracted_project/skills/taobao/scripts/api_server.py`
  - no logic duplication; keep using `should_list`

## Example: explain a match score

User asks: "Why did this title get similar instead of exact?"

Expected approach:

1. Read `NLPMatcher.match_score`.
2. Break down brand/name/model/cosine contributions.
3. Compare final score to 0.75 threshold.

## Example: keep batch and single analyze consistent

User asks: "Batch result differs from single analyze."

Expected checks:

1. Both endpoints call same market fetch path.
2. Both use same matcher threshold.
3. Both call `should_list`.
4. Batch persists status updates.

