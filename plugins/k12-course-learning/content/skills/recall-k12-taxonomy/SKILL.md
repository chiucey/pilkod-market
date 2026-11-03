---
name: recall-k12-taxonomy
description: Search and inspect the Plugin's bundled K12 curriculum taxonomy without network access. Use when finding primary or middle-school micro-topics, filtering concepts by subject/domain/age/type, retrieving prerequisites and concepts unlocked next, checking mastery evidence, locating assessment prompts, or grounding a tutoring or HTML-visualization plan in the local os-taxonomy data.
---

# Recall K12 Taxonomy

Use the bundled Marble Skill Taxonomy as an offline retrieval index. Return candidate knowledge points and graph relationships without claiming they are the user's exact syllabus.

## Operating rules

- Remain stateless. Do not record searches, learner information, progress, or results.
- Use the local JSON only. Do not browse, authenticate, or call an external service.
- Treat user-provided textbooks and course files as the primary authority when available.
- Separate retrieved facts from your inference. Identify the selected topic ID and explain why it appears relevant.
- Preserve the Marble attribution when copying or adapting taxonomy text.
- Do not infer that a missing topic is absent from K12 education. The bundled dataset focuses on primary/elementary learning and is not a complete high-school curriculum.

## Search

Run from this Skill directory:

```bash
python3 ../../scripts/taxonomy_recall.py \
  --query "光的反射" \
  --subject 科学 \
  --age 11 \
  --limit 5 \
  --format json
```

Available filters:

- `--subject`: Computing, English, History, Learning to Learn, Life Skills, Mathematics, Personal & Social Development, or Science. Common Chinese subject names are mapped locally.
- `--domain`: case-insensitive partial domain name.
- `--age`: include only topics whose age range contains this integer.
- `--type`: CONCEPTUAL, PROCEDURAL, REPRESENTATIONAL, LANGUAGE, or META.
- `--limit`: return 1–50 candidates.

Common Chinese concept aliases are expanded from `../../data/query-aliases.zh-CN.json`. For an unmatched Chinese term, add an English translation to `--query`; do not modify the source taxonomy merely to improve one search.

## Inspect the graph

After choosing a candidate, retrieve its full topic plus related nodes:

```bash
python3 ../../scripts/taxonomy_recall.py \
  --topic-id mt_PifbJOuXrG \
  --depth 2 \
  --format json
```

Interpret edges precisely:

- `prerequisites`: concepts the selected topic depends on.
- `unlocks`: concepts that directly or indirectly depend on the selected topic.
- `hard`: the upstream dataset marks the dependency as necessary.
- `soft`: the upstream dataset marks it as useful grounding rather than strictly necessary.
- `reason`: the upstream one-line explanation for the relationship.

Use `--depth 1` for a compact lesson plan and `--depth 2` when preparing a broader learning path. Avoid larger depths unless the user asks for a graph-level exploration.

## List coverage

```bash
python3 ../../scripts/taxonomy_recall.py --list-subjects --format json
```

Use this before assuming that a subject or domain is covered.

## Response shape

Report:

1. the top candidate topic and stable ID;
2. age range, subject, domain, and type;
3. the retrieved description and mastery evidence;
4. 1–3 most relevant prerequisites;
5. 1–3 concepts it unlocks;
6. a short fit assessment labeled as inference;
7. the bundled source attribution.

When several candidates are plausible, show the difference and ask only if the choice materially changes the teaching plan. Otherwise select the best match and state the assumption.
