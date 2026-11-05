---
name: visualize-k12-concepts
description: Generate self-contained, interactive HTML lessons that make abstract primary and secondary school concepts easier to understand. Use for K12 concept explanations, visual teaching pages, interactive courseware, lesson previews, knowledge maps, simulations, active-recall checks, or when turning a textbook, worksheet, notes, PDF content, or a bundled taxonomy topic into an offline single-file HTML learning experience.
---

# Visualize K12 Concepts

Create one offline HTML file that teaches one coherent learning objective through a visual model, guided explanation, and a short understanding check. Preserve student thinking instead of turning the page into an answer sheet.

## Non-negotiable operating mode

- Treat every invocation as stateless. Do not read or write learner profiles, memory files, progress histories, cookies, `localStorage`, analytics, or remote state.
- Use the user's supplied files as the primary source. Use the bundled taxonomy only to retrieve related topics, prerequisites, evidence, and assessment prompts.
- Do not browse or call external services. This Plugin is offline and uses only the current request,
  user-supplied files, and bundled local resources.
- Keep generated pages self-contained: embed CSS, JavaScript, lesson data, and visual assets in one HTML file. Do not use CDNs, remote fonts, trackers, or authentication.
- Distinguish source facts from teaching analogies and inferred examples. Label assumptions when age, curriculum, or goal is not supplied.

## Workflow

### 1. Establish the lesson target

Extract or infer exactly one target concept, learner age or grade, prior knowledge, source material, and desired outcome. If a missing detail does not materially change the page, choose a reasonable default and record it in the lesson spec. If the request is homework, teach the method and use a new check question rather than exposing the submitted answer.

### 2. Prepare like a teacher

Apply the useful parts of `study-tutor` in a stateless session:

1. Identify prerequisites and likely misconceptions.
2. State one measurable learning goal.
3. Choose one everyday analogy, but mark where the analogy stops matching reality.
4. Build one worked explanation and one different check question.
5. Require active recall before revealing feedback.

Ignore the memory profile, scheduled review, and persistent progress instructions from `study-tutor`; they conflict with this Plugin's stateless requirement.

### 3. Recall local curriculum context

Run the Plugin-level retrieval script. Translate uncommon Chinese keywords to English in the query when needed; common aliases are expanded automatically.

```bash
python3 ../../scripts/taxonomy_recall.py \
  --query "光的反射" --subject 科学 --age 11 --limit 5 --format json
```

Inspect the selected topic and graph:

```bash
python3 ../../scripts/taxonomy_recall.py \
  --topic-id mt_PifbJOuXrG --depth 2 --format json
```

Treat a search result as a retrieval candidate, not proof that it matches the user's curriculum. Prefer the user's textbook when the two differ. Preserve the bundled Marble attribution in generated pages that reuse taxonomy text.

### 4. Choose the visual form

Read [visual-patterns.md](references/visual-patterns.md) when selecting the interaction. Match the model to the concept rather than decorating the page. Use `concept-map` as the safe fallback; use a specific simulation only when the model is accurate enough for the learner level.

### 5. Write the lesson specification

Read [lesson-spec.md](references/lesson-spec.md), then create a UTF-8 JSON spec. Keep the page focused enough for a 10–20 minute session. Include:

- a learner-facing question and measurable goal;
- prerequisites, core topic, and what it unlocks;
- one visual interaction with an observation prompt;
- 3–5 explanation steps;
- at least one misconception with a correction;
- 2–4 check questions that do not repeat the worked example;
- one closed-book recall prompt;
- source labels and assumptions.

### 6. Generate the page

```bash
python3 scripts/generate_visual_lesson.py \
  --spec /absolute/path/to/lesson.json \
  --output /absolute/path/to/index.html
```

Use `--validate-only` before generation when iterating on a spec. The generator uses [lesson-template.html](assets/lesson-template.html) and needs only Python 3.

### 7. Verify before handoff

Read [quality-checklist.md](references/quality-checklist.md) and verify the output. At minimum:

- confirm the file contains no `http://` or `https://` runtime dependency;
- when the active runtime supports a local preview, open it and exercise every control; otherwise
  perform static checks and disclose that browser interaction was not executed;
- check keyboard focus, narrow-screen layout, reduced-motion behavior, and print output;
- confirm quiz feedback stays hidden until the learner attempts an answer;
- confirm the visual does not imply a false causal or mathematical relationship.

Return the HTML path and a short summary of the learning design. Treat the HTML as a requested
deliverable, not stored learner state. When local preview is supported and requested, start a
request-scoped local server and provide the exact URL.

## Bundled resources

- `scripts/generate_visual_lesson.py`: validate a lesson spec and render one standalone HTML file.
- `assets/lesson-template.html`: responsive offline learning-page shell with built-in visual modes.
- `assets/example-light-reflection.json`: complete example spec for regression testing and previews.
- `references/lesson-spec.md`: schema and authoring contract.
- `references/visual-patterns.md`: concept-to-visual selection guidance.
- `references/quality-checklist.md`: content, interaction, accessibility, and offline checks.
