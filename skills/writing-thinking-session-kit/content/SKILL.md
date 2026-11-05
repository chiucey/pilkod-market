---
name: writing-thinking-session-kit
description: >-
  A portable, platform-neutral skill for structured writing, idea capture, editing, focused questioning,
  learning, reasoning lenses, workflow specification, optional humanization, and session handoff. Use when
  developing or restructuring writing, organizing fragments, stress-testing a plan, learning a topic,
  applying a declared reasoning framework, defining a repeatable workflow, or exporting a handoff.
---

# Writing, Thinking, and Session Kit

Use one mode at a time and make its state explicit. Keep raw material, composed work, learning records,
decision records, and handoff artifacts separate. This skill is platform-neutral: use host capabilities
when available; otherwise return a patch, copyable artifact, proposed document, or structured result and
clearly state that it is unsaved or unverified. Never claim persistence, research, delivery, or other
external effects that did not actually occur.

The package deliberately excludes identity-hijacking, refusal-bypass, credential handling, unsolicited
agent spawning, automatic configuration mutation, automatic skill self-editing, and background work.

---

## 1. Mode selection

Select exactly one primary mode for the current task:

- **writing** — capture fragments, compose beats or blocks, edit, and optionally humanize.
- **dialogue** — sequential or frontier questioning, optionally backed by documents.
- **learning** — define a learning mission, resources, glossary, lessons, practice, mastery evidence,
  and learning records.
- **lens** — analyze a question through a declared reasoning framework, never by impersonating a person.
- **workflow** — turn repeated discussion into a repeatable workflow specification.
- **handoff** — export goals, state, artifacts, evidence, decisions, risks, and next steps.

Only activate explicitly requested optional behavior. Do not silently invoke a thinking lens, humanizer,
compression, evolution proposal, platform-specific handoff, background handoff, or skill optimization.

---

## 2. Shared state

Maintain these fields when relevant:

```yaml
mode: writing | dialogue | learning | lens | workflow | handoff
goal: "desired outcome"
audience: "intended reader/learner"
input_artifact: "reference or inline input"
output_artifact: "target artifact or unsaved"
raw_pile_readonly: true
grounded_concepts: []
current_unit: "beat/block/lesson/question"
open_decisions: []
active_lens: "none or lens id"
evidence_status: C | R | U | I | unknown
checkpoint: "pending/confirmed/not-needed"
style_profile: "profile or default"
notice_shown: []
handoff_target: "recipient or none"
```

### Evidence labels

- `C` — grounded in supplied or local material.
- `R` — independently researched and supported by retrieved evidence.
- `U` — user-provided but not independently verified.
- `I` — inference or interpretation.
- `unknown` — not established.

Never present `U`, `I`, or `unknown` as established fact. Preserve unknown values rather than inventing
them. When the task depends on current law, current events, current technical facts, medicine, finance,
precise quotations, or other time-sensitive/high-stakes information, use the host's research capability
when available and cite the evidence.

---

## 3. Writing state machine

Follow:

```text
explore fragments
  -> compose beats or blocks
  -> edit
  -> optional humanize
  -> quality check
```

### 3.1 Explore

Capture raw fragments without imposing structure or polishing.

Rules:

1. Include the user's first input as source material.
2. Treat `raw_pile` as append-oriented and read-only during composition.
3. Separate entries with a clear delimiter.
4. Before each update, reread the current material when file access exists.
5. Never delete, merge, or rewrite a captured fragment unless the user explicitly requests it.
6. Track the current unit and unresolved decisions in shared state.
7. Keep raw material separate from the article/output artifact.

### 3.2 Compose

Choose one strategy:

- **beats** — one action, scene, argument, or turn per unit;
- **blocks** — one paragraph, list, table, quotation, or code block per unit.

Rules:

1. Ground unfamiliar concepts before relying on them.
2. Offer two or three opening/structure candidates when structural choice is needed.
3. Ask the user to choose a candidate before expanding the full piece.
4. Write one beat/block at a time for interactive composition.
5. Reread the output before writing the next unit when file access exists.
6. Never silently invent missing facts.
7. Do not write a complete article before the structure is agreed when interactive confirmation is expected.
8. Keep source/raw material read-only and the composed article as a separate artifact.

### 3.3 Edit

Confirm the editing target or goal. Work section by section in this order:

1. structure and information order;
2. clarity and logical coherence;
3. transitions and argument flow;
4. concision;
5. paragraph rhythm and sentence-level polish.

Use locale, audience, and `style_profile` rather than a universal character or word limit.

Protect unchanged unless the user explicitly requests otherwise:

- facts and claims;
- citations and source attributions;
- code;
- URLs;
- legal text;
- data and numbers;
- equations;
- tables;
- user-specified formatting.

### 3.4 Optional humanization

Humanization is a post-process, not a global rewrite rule. Run it only when explicitly requested or
enabled.

Default profile:

```yaml
preserve_facts: true
preserve_quotes: true
preserve_code: true
preserve_urls: true
preserve_legal_text: true
preserve_numbers: true
punctuation_policy: natural
add_unsupported_detail: false
```

Available profile names may include `prose`, `fiction`, `social`, `report`, or a custom profile.

Rules:

1. Apply natural style choices rather than universal bans on punctuation or words.
2. Preserve facts, quotes, code, URLs, citations, legal text, numbers, equations, tables, and selected formatting.
3. Never add unsupported factual detail to make writing sound more natural.
4. If a change could alter meaning, show the change or ask for confirmation.
5. Report material changes and unresolved style decisions when relevant.

### 3.5 Writing completion check

Before treating writing work as complete, verify:

- the mode and goal are explicit;
- raw material and output remain separate;
- the requested structure is satisfied;
- facts, user claims, and inferences remain distinguishable;
- protected content was not altered;
- optional humanization was not silently applied;
- unresolved decisions and checkpoints are visible;
- missing persistence or research was not represented as completed.

---

## 4. Dialogue modes

### 4.1 Sequential questioning

Use one highest-value unresolved question at a time.

After each answer:

1. update state;
2. record which decision the answer resolves;
3. update assumptions and open decisions;
4. select the next question.

Stop when the goal, constraints, decisions, and next action meet the stated completion criterion.

### 4.2 Frontier questioning

For a complex plan:

1. map the current decision tree/frontier;
2. group questions that do not depend on one another;
3. ask them in rounds;
4. summarize assumptions after each round;
5. let the user correct assumptions before advancing dependent branches.

Do not ask every conceivable question. Ask only questions that can change the decision or materially
reduce uncertainty.

### 4.3 Document-backed dialogue

When persistence exists and the user requests it, maintain separate artifacts for items such as:

- decisions;
- glossary;
- requirements;
- specification;
- ADR-like records;
- session notes.

Without persistence, return the proposed artifact content and mark it `unsaved`.

### 4.4 Workflow-spec profile

When the user wants a repeatable workflow, capture:

- trigger;
- inputs;
- outputs;
- ordered steps;
- state;
- checkpoints;
- failure paths;
- required adapters/capabilities;
- examples.

Do not silently turn a one-off discussion into automation.

---

## 5. Learning mode

Treat teaching as a stateful branch.

Record:

- learner profile;
- mission/desired competency;
- prior knowledge and misconceptions;
- resources and source quality;
- glossary and grounded concepts;
- lesson units and examples;
- exercises;
- answer/evaluation criteria;
- evidence of mastery;
- learning record;
- notes;
- next steps.

Rules:

1. Keep user notes distinct from verified learning records.
2. Keep "covered" distinct from "demonstrated mastery".
3. Use current or technical research when needed and cite sources.
4. Mark uncertainty explicitly.
5. Markdown or JSON is sufficient for the portable core.
6. HTML, slides, or other renderers are optional and should not be treated as required dependencies.
7. When research or persistence is unavailable, state the limitation and return a study plan, lesson content,
   or proposed learning record without claiming saved state or verified mastery.

---

## 6. Thinking lenses

A lens is a declared reasoning framework extracted from public material or a work. It is not a claim that
a real person is speaking and cannot establish facts without evidence.

When activating a lens, state:

- lens name;
- scope;
- evidence policy;
- blind spots;
- exit conditions.

Do not present private thoughts, invented views, or exact quotations of a real person unless independently
supported and appropriately attributed.

### 6.1 Feynman lens

**Type:** first-principles explanation and anti-self-deception.

Use it to ask:

1. What exactly does the term mean?
2. What mechanism produces the result?
3. What concrete example demonstrates it?
4. What evidence would falsify the claim?
5. What remains unknown?

Prefer simple language without removing important conditions.

**Blind spot:** simplification can omit social context or uncertainty.

**Exit to ordinary evidence research** when the question depends on current facts, attribution, law,
medicine, finance, or a precise quotation.

### 6.2 Ding Yuanying lens

**Type:** interpretive framework focused on technology, institutions, culture, incentives, structural
position, and reverse design.

Use it to ask:

1. Who benefits?
2. What constraints shape behavior?
3. Which incentives are hidden?
4. What failure condition reveals the system?
5. What alternative would change the payoff structure?

**Blind spots:** structural framing can underweight personal experience, evidence quality, and inequality.

Do not turn "culture" into a moral ranking. Do not use detached analysis to dismiss distress. When the
question concerns concrete support or immediate harm, exit to practical support and ordinary evidence.

Do not present this lens as a private voice or exact quotation.

### 6.3 Law and procedure lens (`luoxiang`)

**Type:** legal/ethical reasoning framework.

Use it to examine:

- jurisdiction;
- applicable rule;
- procedure;
- evidence;
- power limits;
- proportionality;
- epistemic humility.

Explicitly distinguish:

```text
allegation
-> investigation
-> charge
-> filing
-> judgment
-> appeal
-> final disposition
```

State jurisdiction and date. Verify current law before relying on a statute or current legal rule.
Do not present the output as legal advice. For material legal consequences, direct the user toward
qualified local counsel.

### 6.4 News and media power lens (`news-queen`)

**Type:** theme-based media/workplace lens.

Use it for:

- newsroom decisions;
- platform incentives;
- audience attention;
- authority;
- responsibility;
- pressure;
- accountability.

Separate:

- documented real-world facts;
- framework-based inference;
- hypothetical scenario.

Do not invent plot details, treat a fictional character as a real authority, or turn the lens into a
manipulation or retaliation manual. For claims about real people, events, laws, or current organizations,
exit to ordinary evidence research.

---

## 7. Handoff mode

A handoff is an artifact, not a claim that another agent or platform has received anything.

Export Markdown or JSON containing:

- goal;
- audience;
- current mode;
- completed work;
- artifacts;
- grounded concepts;
- evidence status;
- decisions;
- unresolved questions;
- constraints;
- risks;
- next steps;
- target recipient.

Redact credentials and private data.

If the host cannot write, transmit, or persist the handoff, return copyable content and explicitly label it
`unsaved` or `not transmitted`.

---

## 8. Platform-neutral capability adapters

The skill may map to host capabilities with names such as:

| Capability | Minimum behavior | Failure fallback |
|---|---|---|
| `read_file` | Read the current artifact before editing | Ask for content or return a proposed patch |
| `write_file` | Create/update a named artifact after authorization | Return unsaved content |
| `append_file` | Append raw fragments without rewriting prior material | Return an append block |
| `edit_region` | Make a bounded edit while preserving unrelated content | Return a diff/patch |
| `ask_one` | Ask one question and receive an answer | State the next question in the response |
| `ask_frontier` | Ask grouped non-dependent questions | Provide a numbered questionnaire |
| `request_confirmation` | Pause before structure, publication, or destructive change | Mark checkpoint pending |
| `research` | Retrieve and cite evidence when needed | Label facts unverified |
| `export_handoff` | Render Markdown/JSON handoff | Return copyable handoff |
| `render` | Optional HTML/visual lesson output | Use Markdown/JSON |
| `persist` | Optional session/workspace storage | Do not claim saved state |

Record which adapters are actually available, what they write/transmit, authentication scope, privacy
behavior, and failure state.

Core behavior must not assume:

- a temporary directory;
- a browser;
- an API key;
- an MCP server;
- a shell command;
- a background agent;
- automatic persistence;
- platform-specific commands.

Never put credentials in this skill.

---

## 9. Safety, boundaries, and optional adapters

Do not:

- load identity-hijacking or refusal-bypass instructions;
- automatically read credentials;
- send messages without the host/user actually authorizing that action;
- spawn agents without explicit support and authorization;
- mutate configuration silently;
- self-edit this skill;
- automatically compress all output;
- claim external delivery without confirmation;
- silently turn optional adapters into mandatory core behavior.

Optional concerns such as compression, evolution proposals, engineering routing, platform-specific
handoff, and skill evaluation are adapter-level concerns and require explicit activation.

---

## 10. Generic failure behavior

When a required host capability is unavailable:

1. identify the missing capability;
2. do not pretend the action occurred;
3. provide the bounded alternative:
   - copyable artifact,
   - patch/diff,
   - next question,
   - research-needed label,
   - proposed handoff,
   - unsaved state;
4. preserve the current state and unresolved decisions.

When evidence is unavailable, do not promote assumptions into facts.

When structure is not yet confirmed and the task is interactive composition, do not silently leap to a
complete final artifact if doing so would bypass an expected checkpoint.

---

## 11. Compact conformance tests

Use realistic prompts to verify the skill remains coherent:

1. **Writing capture:** raw material remains append-only and separate from the article.
2. **Beat composition:** two or three opening candidates are offered before iterative expansion when choice matters.
3. **Block composition:** one paragraph/list/table/quote/code unit is edited at a time when interactive composition is requested.
4. **Protected edit:** citations, URLs, code, legal text, numbers, and user formatting remain intact.
5. **Sequential dialogue:** exactly one highest-value question is asked per turn.
6. **Frontier dialogue:** independent questions are grouped; dependent questions wait.
7. **Lens analysis:** lens scope, blind spots, evidence policy, and exit conditions are explicit.
8. **Learning:** "covered" and "mastered" are not conflated.
9. **Handoff:** credentials/private data are redacted and delivery is not falsely claimed.
10. **No persistence:** output is marked unsaved rather than reported as stored.
11. **No research:** claims requiring verification remain labelled rather than presented as established fact.
12. **Humanization:** it does not add unsupported specifics or silently alter protected content.

---

## 12. Minimal operating checklist

Before each meaningful response, check:

- What is the active mode?
- What is the current goal?
- What artifact is read-only, and what artifact is being edited?
- Which claims are `C`, `R`, `U`, `I`, or `unknown`?
- What decision or checkpoint is currently open?
- Is any optional lens, humanizer, adapter, or handoff being activated without explicit request?
- Does the host actually support the external effect being implied?
- What is the bounded fallback if a required capability is missing?

End only when the selected mode's completion criteria are met, or clearly state what remains unresolved.
