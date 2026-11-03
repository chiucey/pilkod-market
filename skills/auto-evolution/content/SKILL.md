---
name: auto-evolution
description: |
  Post-task reflection ritual that Mavis runs after delivering a non-trivial
  task. Three outcomes are possible: (1) crystallize a new reusable skill from
  the just-completed workflow, (2) surgically improve an existing skill that
  the task exposed a real gap in, or (3) triage the skill registry — flag
  broken / never-used / low-priority skills and propose soft-quarantine.
  Paths 1 and 2 share the same worthiness gate, dedup check, and
  user-confirmation protocol. Path 3 is opt-in (user invokes or new-skill
  creation triggers a subsumption check). Use this skill when Mavis finishes
  a task and wants to consider crystallizing the workflow, when a loaded
  skill felt incomplete, or when the user says "tidy up skills", "audit
  skills", "prune", "skill cleanup", "把这次的工作沉淀成 skill", "改进
  一下 XXX skill", "XXX skill 漏了一个 case". Do NOT use for trivial
  single-step answers, one-off Q&A, casual chat, or tasks where the only
  "learning" is a personal preference (use memory instead). Do NOT use this
  to skip the dedup check, to write skills without user confirmation, to
  auto-delete quarantined skills, or to auto-improve auto-evolution itself
  (meta-recursion is out of scope for v1).
---

# Auto-Evolution

A end-of-task ritual. After Mavis finishes a piece of work, this skill
asks three questions:

1. **Is there a new reusable pattern worth crystallizing as a new skill?**
2. **Did the just-completed task expose a real gap in an existing skill
   that should be fixed in place?**
3. **Has the skill registry accumulated broken, never-loaded, or
   now-subsumed skills that should be triaged?**

Paths 1 and 2 share the same gate and confirmation discipline. Path 3 is
opt-in (it does not run on every task). All three paths require explicit
user confirmation before any file move or modification.

## Skill registry conventions

Two reserved directories live under `.skills/` and have specific meanings.
Both are conventions, not platform-enforced mechanisms — they only work if
Mavis (and the auto-evolution ritual) reads and follows them.

### `.skills/.quarantine/`

Soft-deleted skills. A skill moved here is **out of the live registry**:
Mavis does not load it for new tasks, and auto-evolution's path-1/2 audits
ignore it. The directory is **never auto-purged** — the user must explicitly
ask to restore (`mv .skills/.quarantine/<name> .skills/<name>/`) or to
hard-delete.

Each quarantined skill gets a sibling file `.quarantine.json` with shape:

```json
{
  "name": "<skill-name>",
  "quarantined_at": "<ISO-8601 timestamp>",
  "reason": "<one-line why>",
  "original_path": ".skills/<skill-name>/",
  "evidence": "<which bucket from the triage report>"
}
```

### `.skills/.low-priority/`

A social-contract directory. Skills placed here are **still loaded** by
Mavis, but auto-evolution and any future skill-routing logic should treat
them as fallback: when multiple skills match a request, prefer a
non-low-priority match first. **This is not enforced by the platform
today** — it relies on the agent reading this section and following it.
If/when Mavis grows a `weight:` or `priority:` frontmatter field, this
directory becomes a migration shim, not a load-bearing mechanism.

User can request moves in either direction:
- "Put `windows-exe-builder` in low-priority" → `mv .skills/windows-exe-builder .skills/.low-priority/`
- "Restore `windows-exe-builder` from low-priority" → `mv .skills/.low-priority/windows-exe-builder .skills/`

## Inputs to collect

The skill runs against the **just-completed task**, so most inputs come from
the current conversation. Confirm internally before drafting:

- **Task shape**: what was the user actually trying to do? (one sentence)
- **Tool sequence**: which tools/scripts/decision points were used?
- **Skills loaded during the task**: any name appearing in
  `<available_skills>` that was actually pulled into context
- **Recurrence signal**: has Mavis (or the user) mentioned a similar task
  before? Check the current session, recent sessions, and existing skills.
- **User's stated intent** (only if user explicitly invoked the skill):
  "one-off documentation" vs "make this a default workflow next time" vs
  "fix this gap in skill X"

## Procedure

### Part 1 — Worthiness gate (shared by both paths)

Skip both new-skill creation AND skill improvement if **any** of these are
true. The gate is conservative because every new/modified entry in the
skill registry affects future agent behavior.

- The task was a single-step Q&A, factual lookup, or casual conversation
- The workflow was a one-off debug of a unique bug (no recurrence signal)
- The "learning" is a user preference or fact → use `memory_append` /
  `memory_topic_*` instead, not a skill
- The pattern already exists as a skill AND no gap was exposed in this
  task → don't touch the existing skill just to feel productive
- **No preserved knowledge**: the workflow worked first-try with no
  gotchas, and each step is already covered by an existing tool's
  documented behavior
- **The scenario itself is suspect**: the apparent success depends on a
  conflation, approximation, or "happens to work for this trivial case"
  coincidence (e.g. static-file deploy masquerading as a live service)
- **Self-referential callback landed on Mavis**: if the user used a callback
  (referencing Mavis's own tools, data, or prior outputs) to refute a
  verdict Mavis gave, audit the prior reasoning for a hidden
  concept-conflation (e.g. "information" vs "user information",
  "learning" vs "storing user behavior"). A landing callback is a strong
  signal that an applied skill's mental model has a blind spot worth
  fixing in place — this is exactly the improvement case, not the
  "no action" case
- **Improvement is purely stylistic**: "this wording feels off" is not a
  gap. Real gaps are missing steps, wrong assumptions, missing failure
  modes, broken trigger phrases, or tools the skill doesn't reference

Reason: skill spam and skill-edit spam both pollute the registry. A
modification silently affects every future agent run that loads the skill,
so the bar for both creation and improvement is the same.

### Part 2 — Decide which path(s) apply

Run these two audits in parallel. They are not mutually exclusive.

**Audit A — New-skill candidacy.** If the gate in Part 1 passes, articulate
the candidate pattern in one sentence: "Mavis should be able to do X
whenever Y happens." If you can't fill in concrete Y phrases, the pattern
isn't sharp enough yet.

**Audit B — Loaded-skill improvement.** For each skill that was loaded
during the task, ask:
- Did the task expose a missing step the skill didn't cover?
- Did the skill make a wrong assumption that broke during the task?
- Is there a new gotcha the Failure handling section should mention?
- Did the user correct Mavis's application of the skill (signal: skill
  was unclear at the trigger point)?
- Is the skill's `description` triggering too narrowly or too broadly
  based on this task's outcome?
- **Did the task falsify an out-of-scope claim?** If the skill lists
  feature X as "out of scope for v1" but the task just demonstrated X is
  achievable in this sandbox, the scope line is now wrong — propose
  removing or rewording it, not just adding a new section. Real example:
  `android-apk-builder` originally said "App icon design" was out of
  scope, but a real custom-icon task proved it's just an undocumented
  in-scope workflow — the fix was a scope-line edit plus a new doc
  section, not just the section alone.

If yes to any, the loaded skill is an improvement candidate. If no across
the board, no improvement is needed.

**Note:** Audit B does NOT improve skills that weren't loaded. A skill
sitting unused in `/workspace/.skills/` is not auto-improved just because
Mavis happened to think of an idea. Improvements come from real task
exposure, not from idle ideation.

### Part 3 — Dedup (for new-skill path only)

Before drafting a new skill:
- List `.skills/` directories (`ls /workspace/.skills/`)
- Read the frontmatter `description` of any skill whose name or
  description overlaps the candidate's keyword space
- If an existing skill already covers ≥ 70% of the use case, treat the
  overlap as Audit B (improvement opportunity) instead of creating a
  parallel skill
- If unsure, lean toward improvement over proliferation

### Part 4 — Draft proposals / diffs

**For new skills:** follow `skill-creator` conventions:
- Frontmatter `name` (kebab-case, matches directory) and `description`
  containing all 4 elements from `description-rubric.md` (What / When /
  Near misses / moderate pushiness)
- Body sections: Procedure, Output contract, Failure handling, Examples
- ≤ 300 lines in main file; move bulk content to `references/`
- No `README.md`, `CHANGELOG.md`, `install.sh`, `.env*`
- No `ALWAYS` / `NEVER` / `MUST` in the procedure; write why instead

**For improvements:** surgical edit discipline. Each edit must be
reviewable as a single coherent change.
- **One change per commit.** Do not bundle "tweak frontmatter" + "add
  failure mode" + "reorder procedure" in one proposal. Each gets its own
  proposal and its own user confirmation.
- **Preserve everything else.** Read the existing SKILL.md end-to-end
  first, then make the minimal edit that addresses the gap. Resist the
  urge to rewrite neighboring sections "while I'm here".
- **Show the diff explicitly.** Format:
  - File: `.skills/<name>/SKILL.md`
  - Section: `<section name>`
  - Before: `<the existing text, quoted>`
  - After: `<the proposed text, quoted>`
  - Reason: `<one-line: what gap this closes>`
- **No silent style edits.** A wording change is improvement only if it
  fixes a real ambiguity, not if it just feels better.
- **No frontmatter rewrites for cosmetic reasons.** Trigger phrases
  change when they were wrong (missed legitimate trigger, fired on
  non-target), not when they were merely improvable in tone.

### Part 5 — Surface to the user

Do NOT silently write any file (new or modified). The proposal must
include, for each item:
- For new skill: name, one-line capability, trigger phrases, dedup
  verdict, file path
- For improvement: target skill name, section, before/after diff, reason
- Whether they're independent (separate yes/no) or coupled (both needed
  for the change to make sense)

Ask: "要落地吗？回个 yes 我就改。" (Use "建" or "改" based on whether
it's new or improvement — clarity over brevity.)

### Part 6 — Commit or decline

- Yes → apply edits, then optionally `skill-creator` Step 6 eval if the
  user wants the changed skill battle-tested
- No → drop the draft, do not save a half-product
- Partial yes (e.g. "improve but don't create") → apply only the
  approved changes

### Part 7 — Reflect in reply

The final task delivery message should include a one-line footer per
decision (see Output contract), so the user knows the ritual ran and
trusts the gate.

### Part 8 — Skill Triage (opt-in, off the critical path)

Triage audits the **whole** skill registry, not just the skills used in
the current task. It is **not** part of every task's auto-evolution run —
that would be too noisy. Triage fires on three triggers:

- **T1 — User invocation**: user says "tidy up skills", "audit",
  "prune", "skill cleanup", "看一下哪些 skill 没用了", or similar
- **T2 — Subsumption check (auto, internal)**: Part 4 just created a
  new skill. After the new skill lands, run a quick check: does any
  existing skill now have ≥ 70% overlap with the new one? If yes, the
  existing skill is a quarantine candidate — surface it, do not auto-move
- **T3 — User opt-in (off by default)**: user has said "以后每次任务结束
  都跑一次 triage" or set `auto_triage: true` in some future config.
  Until that opt-in exists, T3 does not fire

If no trigger fires, **Part 8 is skipped entirely** — Paths 1 and 2 work
exactly as before.

#### Triage procedure (when T1 or T2 fires)

1. **Enumerate the registry.** List `.skills/<name>/SKILL.md` for every
   subdirectory. Skip reserved directories (`.quarantine/`, `.low-priority/`,
   anything starting with `.`).

2. **Frontmatter validation.** For each skill, verify:
   - File starts with `---\n` (YAML frontmatter present)
   - `name` field exists, is kebab-case, matches directory name
   - `description` field exists and contains all 4 elements from
     `description-rubric.md` (What / When / Near misses / moderate
     pushiness) — heuristic: description ≥ 3 lines, mentions "Do NOT use"
     or equivalent near-miss phrasing, ≥ 2 trigger phrases

3. **Reference validation.** Scan body for `references/`, `scripts/`,
   `.md` paths. For each, verify the file exists. A broken reference
   fails the audit.

4. **Usage signal (mark weak).** For each skill, check:
   - Does its name appear in any agent memory topic? (`memory_search`)
   - Has it been explicitly mentioned in the current session?
   - **Caveat:** both signals are weak. A skill can be high-value but
     rarely invoked (Android APK build, annual report generation). Mark
     any "rarely used" finding with `⚠️ weak signal` in the report.

5. **Categorize into buckets:**

   - **Bucket A — Definitely broken**: invalid frontmatter, missing
     fields, broken internal references. **Action candidate: fix or
     quarantine.**
   - **Bucket B — Quarantine candidate**: frontmatter valid, references
     valid, **never loaded** in any tracked signal **AND** no memory
     mention **AND** ≥ 30 days since the file was created. All three
     must hold. **Action candidate: quarantine (with user confirmation).**
   - **Bucket C — Low signal, leave alone**: valid skill, but weak
     usage signal. **Action: report only, do not propose moves.** A
     skill can be "rare" without being "dead".
   - **Bucket D — Healthy**: no findings. Silent in the report.

6. **Surface the triage report.** Use this format:

   ```
   🗂️  Skill Triage Report
   ──────────────────────
   [A] Definitely broken (fix or quarantine):
       - <name>: <what's wrong>
   [B] Quarantine candidates (need ≥3 conditions to land here):
       - <name>: valid ✓ | never loaded ✓ | no memory ref ✓ | age 47d
   [C] Weak signal only (no action proposed):
       - <name>: valid ✓ | 0 memory refs ⚠️ weak signal
   [D] Healthy: <N> skills skipped

   Quarantine [B]? Reply "quarantine <name>" or "quarantine B" or "skip".
   Fix [A]? Reply "fix <name>: <how>".
   ```

7. **Apply on confirmation.**
   - "quarantine B" or "quarantine <name>" →
     `mkdir -p .skills/.quarantine && mv .skills/<name> .skills/.quarantine/<name>`
     then write `.skills/.quarantine/<name>/.quarantine.json` with the
     metadata shape defined in **Skill registry conventions**.
   - "fix <name>: <how>" → treat as Path 2 (improvement) — surface a
     diff, get separate confirmation per Part 5.
   - "skip" / "ignore" / no reply within the natural conversation →
     no action.

#### Restore from quarantine

User can always say "restore <name>" →
`mv .skills/.quarantine/<name> .skills/<name>`. This is a single-command
action, no auto-evolution ceremony required. Mavis can do it directly
when the user asks.

## Output contract

At the end of every non-trivial task delivery, Mavis's reply may contain
up to three footers (one per path), drawn from:

- **Skill created** — "已沉淀为 `.skills/<name>/`：<one-line>"
- **Skill improvement applied** — "已改 `.skills/<name>/` 的 `<section>`：<one-line>"
- **Skill quarantined** — "已 quarantine `.skills/<name>/`：<reason>。回 `restore <name>` 撤回。"
- **Skill create proposed, awaiting confirmation** —
  "这次可以做个 `<name>` skill：<one-line>。落地吗？"
- **Skill improvement proposed, awaiting confirmation** —
  "`<name>` 漏了 `<gap>`：<diff>。改吗？"
- **Triage report** — "🗂️ Skill Triage: A=1 B=2 C=3 D=45 — quarantine B? fix A: <how>?"
- **No action needed** — silent (do not narrate the negative verdict;
  the ritual is internal unless the user invoked the skill explicitly)

If the user invoked the skill themselves, always narrate the verdict
explicitly, even when negative.

## Failure handling

- **Worthiness gate fails** → no action, no narration (unless user asked)
- **Dedup shows ≥ 70% overlap** → convert new-skill path into
  improvement path, re-enter at Part 2 Audit B
- **User declines** → delete any partially-written draft files; never
  leave a half-product
- **Improvement scope creeps mid-edit** → stop, surface the additional
  change as a separate proposal, do not silently fold it in
- **Edit breaks frontmatter contract** → the 4 description elements must
  remain intact; if a trigger-phrase change collapses a near-miss
  distinction, restore it
- **Improvement is so small it's trivial** (one phrase, one example) →
  apply the discipline anyway: surface the diff, get confirmation.
  Consistency builds trust faster than silent auto-fix.
- **Two paths conflict** (e.g. user says "create new" but overlap is
  90% with an existing skill) → surface the conflict, do not silently
  choose
- **Triage Bucket B has only 1-2 weak conditions met** (e.g. valid +
  never loaded but only 5 days old) → downgrade to Bucket C, do not
  propose quarantine. Weak signals don't justify moves.
- **Triage finds 0 broken + 0 quarantine candidates + N weak signals** →
  report only Bucket C, do not propose any moves. Triage is a status
  report when the registry is healthy.
- **Quarantine move fails** (e.g. cross-device link, permission) →
  stop, report the failure with the exact error, do not retry
  automatically. The skill stays where it was.
- **Restore from quarantine requested but name collides** with an
  existing skill → refuse, surface the collision, do not overwrite
- **T2 subsumption check fires but the "subsumed" skill is the one
  Mavis loaded for this very task** → false positive. The skill was
  just used, by definition it can't be unused. Mark as not-a-candidate.

## Examples

**Example 1 — New skill path (gate passes).**

Mavis just spent 30 minutes setting up a Playwright + stealth config
inside the sandbox, hit 6 specific gotchas (PEP 668, missing templates,
wrong PLAYWRIGHT_BROWSERS_PATH, etc.), and wrote a working `install.sh`.

Verdict: skill-worthy. Proposal:
> 这次的工作其实是个可复用的 sandbox-stealth-browser 装配流程，踩了 6 个坑。
> 要不要沉淀成 `.skills/sandbox-stealth-browser-installer/`？回 yes 我就建。

**Example 2 — Improvement path (gate passes, dedup wins).**

Mavis just used `minimax-docx` to fill a 5-page Word form, hit a gotcha
the skill didn't cover (e.g. "section break before page break" wasn't
mentioned), and the user had to correct the output.

Verdict: skill-worthy as improvement, not new. Proposal:
> `minimax-docx` 在 `<page layout>` section 漏了 "section break vs page
> break" 的区分。补一句：<proposed text>。改吗？

**Example 3 — Both paths at once.**

Mavis just wrote a Flask app AND used the `website_deploy` skill to
publish it. Two things happen:
- New-skill path: the Flask workflow has its own pattern → propose new
  skill
- Improvement path: `website_deploy` skill's `description` didn't
  mention Flask specifically, so Mavis had to improvise → propose
  adding a Flask example to `website_deploy`

Surface both, ask for confirmation on each independently.

**Counter-example A (gate fails, both paths).** Mavis just answered
"What's the capital of France?" → no proposal, no narration.

**Counter-example B (gate fails, improvement only).** Mavis just used
`xlsx` to read a CSV. The skill worked fine. Nothing to improve, nothing
new to create. Silent.

**Counter-example C (improvement rejected as stylistic).** Mavis thinks
a skill's wording could be tighter. Reject: no gap was exposed, this is
preference, not improvement. Suggest the user open a `memory_topic_*` or
ask the skill author directly.

**Example 4 — Triage path (T1, user-invoked).**

User: "tidy up the skills."

Mavis runs Part 8 over `.skills/`:

```
🗂️  Skill Triage Report
──────────────────────
[A] Definitely broken (fix or quarantine):
    - docx-formatter: frontmatter `description` missing "Near misses" element
[B] Quarantine candidates (need ≥3 conditions to land here):
    - old-csv-merger: valid ✓ | never loaded ✓ | 0 memory refs ✓ | age 92d ✓
[C] Weak signal only (no action proposed):
    - windows-exe-builder: valid ✓ | 0 memory refs ⚠️ weak signal
    - minimax-pptx: valid ✓ | last mention 14d ago ⚠️ weak signal
[D] Healthy: 41 skills skipped

Quarantine B? Reply "quarantine old-csv-merger" or "skip".
Fix A? Reply "fix docx-formatter: rewrite description to add Near misses".
```

User: "quarantine old-csv-merger; fix docx-formatter later."

Mavis: `mkdir -p .skills/.quarantine && mv .skills/old-csv-merger
.skills/.quarantine/old-csv-merger` + writes
`.skills/.quarantine/old-csv-merger/.quarantine.json` with reason
"never loaded in 92d, no memory refs". Reports the move. Does NOT
touch `docx-formatter` (user said "later").

**Counter-example D (T2 false positive).** Mavis just created
`android-apk-builder` v2 with split signing scripts. Subsumption check
finds that `android-apk-builder` v1 has 80% overlap → BUT v1 was just
loaded for this very task, so the "never loaded" condition fails. v1
stays put. No false quarantine.

**Counter-example E (T1, healthy registry).** Triage fires, finds
0 broken + 0 candidates + 4 weak signals → report only Bucket C, no
moves proposed. The "tidy up" request gets a "registry is healthy,
here's the soft picture" answer, not a forced action.

## Out of scope (v1)

- **Auto-improving `auto-evolution` itself** based on the ritual
  running. Meta-recursion makes the failure mode invisible (a broken
  gate means silent acceptance of bad skills). Improvements to
  auto-evolution require explicit user request.
- **Truly auto-committing small edits** without user confirmation. The
  user can later relax this by saying "以后这种小改不用问我", at which
  point add a `## Auto-commit policy` section to this skill.
- **Bulk-rewriting skills that weren't loaded** during the task. The
  loaded-skill signal is what makes improvement evidence-based.
- **Auto-deletion of quarantined skills.** Quarantine is reversible.
  Hard-delete requires the user to explicitly say "permanently delete
  `<name>`" and Mavis confirms. Until that explicit request, nothing
  in `.skills/.quarantine/` is touched.
- **Auto-modifying skill `description` to "reduce weight".** Mavis
  skills have no `weight`/`priority` field. Narrowing the description
  changes the skill's identity, which is exactly the auto-evolution
  anti-pattern this skill warns against. Use `.low-priority/` directory
  instead — it preserves the skill's identity and signals deprioritization
  via convention.
- **Reliable per-skill usage tracking.** Mavis does not currently
  expose a "skill X was loaded N times" hook. Triage's Bucket B uses
  weak signals (no memory mention + never mentioned in current session
  + file age ≥ 30d). All such findings are marked `⚠️ weak signal` in
  the report. A high-value rare skill (annual report generation,
  Android APK build) is not a quarantine candidate just because it's
  rare.
- **Auto-running triage on every task end.** Triage is opt-in (T1) or
  triggered by T2 subsumption check. Running it every turn would spam
  the user with reports. User can later opt into "always run triage"
  by setting a config (out of scope for v1 to design the config).
