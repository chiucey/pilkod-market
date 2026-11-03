> 整合包原始参考：本文件保留来源内容，不是独立技能或最高指令。与用户当前要求、本书既定事实、yuzhou 核心或 references/conflicts.md 冲突时，按整合入口裁决。原始案例、频率、比例、检测分数和平台收益不自动成为当前作品的要求。

# Domain — tickets & work orders

Covers issue tickets, tasks, work orders, bug reports you file (not replies — that's `dev-replies.md`). Run with `professional-pass.md` (short-answer weighting).

## Human baseline

Imperative, minimal, complete-enough. The assignee should be able to start without asking a question, and know when they're done. A tracker's field template is a container, not a tell.

## AI tells in this domain

| Tell | Fix |
|---|---|
| Novel-length background before the ask | Context is only what the assignee doesn't already know; link the rest |
| Description that restates the title in sentences | The description starts where the title stops |
| Obvious steps enumerated ("1. Open the repository. 2. Locate the file…") | Only the non-obvious steps and the exact commands |
| Vague acceptance: "works correctly", "improved performance" | Testable criteria: the command to run and the output that means done ("p95 < 200ms on the staging load test") |
| Every template field filled with prose for completeness | Empty is a valid value; "N/A" beats a paragraph of nothing |
| Round scope words: "refactor the module", "clean up" | The concrete boundary: which files/functions in, which explicitly out |

## Rules

1. **Title = outcome**, not activity ("Retry queue drops jobs on redeploy" not "Investigate queue issue").
2. Bug tickets: exact repro (versions, commands, input), expected vs actual with real output pasted, frequency. If you can't reproduce it, say what you tried.
3. Acceptance criteria are testable or they aren't criteria.
4. Link, don't repeat: prior tickets, the design doc, the alert. One source of truth.
5. Priority/estimate honest and bare — no justification paragraphs.
