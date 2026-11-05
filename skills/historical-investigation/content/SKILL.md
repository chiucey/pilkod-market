---
name: historical-investigation
description: >-
  Verify historical events, people, dates, documents, figures, and narratives through primary sources,
  source criticism, timeline reconstruction, and transparent treatment of scholarly disagreement. Use when
  investigating historical truth, archives, historiography, provenance, old quotations, or historical claims.
---

# Historical Investigation

Use this skill for platform-neutral historical fact verification and source criticism. It establishes what the surviving evidence supports; it does not promise a single final “truth” when the record is incomplete or contested.

## Scope

Cover events, people, dates, places, institutions, documents, quotations, numbers, historical images, and causal narratives. Separate historical fact, scholarly interpretation, later legend, prediction, and definition. Do not treat a modern news workflow or a search result as a substitute for historical method.

## 1. Define the object

Record the precise claim, period, region or polity, languages, jurisdiction if relevant, desired depth, and cutoff date. Split broad questions into atomic claims:

- Did a person, institution, document, or event exist?
- When and where did it occur?
- What happened, according to which record?
- Is a quotation, number, title, or document genuine?
- Is a causal explanation contemporary evidence or later interpretation?

For each claim, state what evidence could support or disprove it. If the object is too vague, ask for a narrower claim or return `unable_to_verify`.

## 2. Find the source of record

Search in this order:

1. Contemporary archives, official records, manuscripts, inscriptions, registers, diaries, letters, court or administrative documents.
2. First-person memoirs and testimony, with memory and interest noted.
3. Original photographs, films, maps, or collection records.
4. Scholarly editions, peer-reviewed papers, monographs, theses, and annotated translations.
5. Reliable specialist syntheses.
6. General articles and online retellings as leads only.

Read the document, scan, transcription, or full paper when the claim depends on wording, figures, dates, omissions, or qualifications. A title, abstract, search snippet, or social preview is not decisive evidence.

## 3. Criticize each source

Apply the six tests of historical source criticism:

1. **Authenticity** — author, provenance, composition date, material, edition, forgery or later interpolation.
2. **Time** — distance between record and event; contemporary record or later recollection.
3. **Place** — author location, historical place names, geography, routes, and jurisdiction.
4. **Person** — identity, office, authorship, interest, political position, and access to information.
5. **Number** — units, scale, institutions, money, titles, calendar, and possible rhetorical exaggeration.
6. **Comparison** — independent sources, shared ancestry, transmission, omission, contradiction, and corroboration.

Do not equate an official record with an objective account of every detail. Record what the source proves directly: often it proves that a person or institution made a record, not that every assertion in it is accurate.

### Six tests (detail)

- **Authenticity:** Is the item genuine, interpolated, misattributed, or a later compilation? Check provenance, material, language, author, composition date, edition, and transmission.
- **Time:** How close is the record to the event? Was the author an eyewitness, contemporary, later compiler, or modern interpreter?
- **Place:** Could the author know the place? Do historical names, borders, routes, geography, and institutions fit the period?
- **Person:** Are the identity, office, authorship, access, interests, and political position established?
- **Number:** Do quantities, currency, titles, ranks, units, and calendar fit the period? Could rhetoric or copying explain the number?
- **Comparison:** Are sources independent? Do they share an ancestor, omit relevant details, corroborate, or contradict one another?

### Evidence layers

Separate:

1. what a source directly records;
2. what can be inferred from several records;
3. scholarly interpretation;
4. later legend, memory, or literary reconstruction.

An official or canonical text is evidence of how an institution recorded or framed an event. It is not automatically an unbiased account of every detail.

### Solitary records and absence

A single surviving record can establish that the record exists. It does not automatically establish every fact in the record. A missing record may reflect loss, restricted access, language, cataloguing, or survival bias. “Not found” is not “did not happen”.

## 4. Build a historical evidence ledger

For each material claim-source pair record the claim, source, source level, source relationship, excerpt, publication/capture time, version, and confidence. Add historical fields:

`event_date`, `composition_date`, `edition`, `volume_page`, `archive_id`, `calendar_system`, `translation`, `author_provenance`, `institutional_context`, `later_retelling`, `textual_variant`, `transmission_relationship`.

Use `unknown` or `not_available` rather than guessing. A single surviving record may establish that the record exists while leaving its narrative details unresolved.

### Ledger schema (YAML)

```yaml
claim: "atomic historical claim"
claim_type: fact | interpretation | tradition | prediction | definition
source_url: "https://..."
source_org: "author, archive, or institution"
source_level: S | A | B | C | D | unknown
source_relation: primary | independent | derivative | repost | same_event_unknown
quote: "short faithful excerpt"
event_date: "date or unknown"
composition_date: "date or unknown"
published_at: "date or unknown"
captured_at: "ISO-8601"
edition: "edition/version or unknown"
volume_page: "volume/page/section or unknown"
archive_id: "catalogue identifier or unknown"
calendar_system: "era/calendar or unknown"
translation: "translator/edition or unknown"
author_provenance: "known/uncertain/details"
institutional_context: "context or unknown"
later_retelling: false
textual_variant: "variant or none known"
transmission_relationship: "lineage or unknown"
supports_or_refutes: supports | refutes | mixed | context_only
confidence: high | medium | low | unresolved
contradictions: []
access_limit: none | login | paywall | regional | OCR_incomplete | snippet_only | unavailable_tool | other
```

A material conclusion needs a readable source record or an explicit evidence gap. Do not merge event date, composition date, publication date, and capture date into one generic date.

## 5. Compare independent evidence

Collect support and counterevidence across languages, regions, institutions, and scholarly viewpoints. Count evidence paths, not website names. Treat a shared document, transcription, wire story, edition, or repeated scholarly claim as one evidence family. When independence is unclear, use `same_event_unknown` and lower confidence.

Record contradictions rather than selecting the version that fits a preferred narrative.

### Source hierarchy

| Level | Typical material | Use |
|---|---|---|
| S | Contemporary primary record, archival image, inscription, original register, first-person document | Direct evidence; assess bias and completeness |
| A | Critical edition, peer-reviewed scholarship, archival catalogue, specialist monograph | Strong interpretation or edited access to primary material |
| B | Reputable synthesis, museum or institutional explanation, specialist journalism | Context and leads; inspect citations |
| C | Unsourced web article, personal post, popular retelling | Lead only |
| D | Myth-making, clickbait, fabricated quote or engagement content | Noise unless the claim is specifically about its circulation |

### Transmission relationships

Use `primary`, `independent`, `derivative`, `repost`, `same_event_unknown`, or a more precise host value. Track shared manuscripts, editions, translations, copied errors, common citations, and archival series. Different websites or books do not prove independence if they reproduce the same source.

### Source versus claim

Source level describes provenance and method. Claim confidence separately describes whether the particular proposition is supported. A high-level source can preserve a biased or incorrect claim; a low-level source can point to a useful primary record but cannot substitute for it.

## 6. Reconstruct the timeline

Keep these timestamps separate:

- event date;
- record or composition date;
- edition, revision, or transmission date;
- publication or digitization date;
- translation date;
- capture and verification date.

State the calendar, era name, date-conversion method, time-zone assumptions, date precision, and relationship between event and later testimony. Bind every timeline node to a source and evidence strength.

### Calendar normalization

For every conversion record:

- era name or regnal year;
- calendar system and convention;
- original date expression;
- converted date and conversion method;
- precision and uncertainty;
- timezone or local-day assumption where relevant;
- conflicting conversions.

Do not silently convert lunar, lunisolar, Julian, Gregorian, regnal, or local calendars. If a date cannot be normalized confidently, preserve the original and mark the normalized field unresolved.

### Timeline table

| Date as recorded | Normalized date | Event/record | Source | Evidence strength | Calendar/version note |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

Attach each node to a source record. A later account can describe an earlier event, but its composition date and distance from the event must remain visible.

## 7. Classify the historical result

Use the historical states:

- **确证 / confirmed** — multiple materially independent records converge with no material contradiction;
- **可证 / supported** — accepted by strong scholarship or evidence, with limited unresolved details;
- **存疑 / contested** — evidence is sparse, conflicting, derivative, or based on a lone record;
- **可疑 / doubtful** — materially inconsistent with provenance, chronology, geography, institutions, numbers, or readable primary evidence;
- **无法核实 / unable_to_verify** — decisive material is inaccessible or the claim is underspecified;
- **未找到公开证据 / no_public_evidence_found** — no public record was located, which is not proof of nonexistence;
- **单一幸存史料 / single_surviving_record** — only one surviving record was found and its existence is established separately from its contents.

Do not collapse “source exists,” “source says X,” and “X happened” into one result.

## 8. Write the report

Return a readable report and, when useful, the same claims and evidence as JSON or YAML. Include scope, cutoff time, claim table, source excerpts, source relationships, timeline, calendar notes, supporting and contrary evidence, scholarly disagreement, gaps, access limits, performed/unperformed checks, and next steps.

### Report template

```markdown
# 历史事实核验：<主题>

## 结论
- **状态**：确证 / 可证 / 存疑 / 可疑 / 无法核实 / 未找到公开证据 / 单一幸存史料
- **一句话结论**：
- **截止时间与范围**：
- **语言、地区、时期**：

## 原子主张
| ID | 主张 | 类型 | 可证伪条件 | 状态 |
|---|---|---|---|---|
| C1 |  | fact/interpretation/tradition |  |  |

## 史料与证据
| 主张 | 来源/摘录 | 史料等级 | 来源关系 | 事件/成书/版本日期 | 卷页/馆藏号 | 置信度 |
|---|---|---|---|---|---|---|

## 时间线与历法
| 原始日期 | 归一日期 | 事件/记录 | 依据 | 备注 |
|---|---|---|---|---|

## 六法检查
- 辨伪：
- 辨时：
- 辨地：
- 辨人：
- 辨数：
- 互证：

## 学术争议、反证与后世叙事
- 

## 来源关系与证据缺口
- 

## 访问限制、已执行与未执行检查
- 

## 下一步
- 

## 来源列表
1. 
```

Machine-readable output should preserve the ledger fields and include `claim_results`, `timeline`, `debates`, `gaps`, `limitations`, and `next_steps`.

## Completion check

Before finalizing, verify that each important claim has readable evidence or an explicit evidence gap; source provenance, edition, date system, volume/page or archive identifier are visible where relevant; derivative copies are not counted as independent; event, composition, edition, publication, translation, and capture dates are not conflated; and the conclusion does not exceed the surviving evidence.

## Platform adapters

The core needs capabilities rather than named products: web search, source/page/PDF reading, archive search, paper search, OCR/visual inspection, calendar/date conversion, structured output, and optional persistence.

| Capability | Minimum output | Optional adapter examples |
|---|---|---|
| `web_search` | query results with URL, title, publisher, date if known | native web search or semantic search |
| `source_fetch` | readable page, PDF, scan, transcription, or explicit failure | page reader, document parser, archive API |
| `archive_search` | catalogue metadata, archive ID, edition and access URL | library/archive catalogue |
| `paper_search` | paper metadata and readable body or stable abstract | scholarly index or repository |
| `ocr_visual` | OCR/transcription with confidence and image reference | OCR/vision tool |
| `calendar_convert` | original date, normalized date, method, uncertainty | calendar library or reference table |
| `structured_output` | Markdown plus JSON/YAML-compatible records | host renderer |
| `persist` | optional artifact storage | host project/workspace storage |

For each adapter record languages, source types, login/quota/region restrictions, OCR quality, output shape, and privacy behavior. If an adapter fails, record the affected evidence, try a documented alternative, narrow the claim, and preserve an unresolved state. Never turn an empty search or blocked archive into proof that an event or document did not exist.

## Archive and research resource pool

Use this as a replaceable discovery list, not a mandatory checklist. Availability, cataloguing, language, OCR, licensing, and regional access vary.

### Resource classes

- national, regional, university, military, court, religious, and municipal archives;
- libraries and manuscript/rare-book catalogues;
- critical editions and digitized primary texts;
- scholarly indexes, repositories, and full-text paper services;
- map, image, film, oral-history, and museum collections;
- newspapers, parliamentary records, gazettes, registers, and statistical series.

### Search practice

Search original title, author, institution, date, language, catalogue identifier, alternate spelling, historical place name, edition, volume, and quoted phrase. Follow references from a scholarly work back to the primary record. Prefer a scan or critical edition over an undated transcription.

### Access logging

Record URL, catalogue ID, retrieval date, edition, language, OCR quality, paywall/login/region limits, and whether the item is a scan, transcription, translation, or secondary description. A broken link or inaccessible catalogue is an access limit, not evidence of nonexistence. Seek a documented alternative copy without silently substituting a different edition.

## Boundary

“Historical truth” may remain contested. The skill separates a record's existence, what it says, what can be inferred, and what historians debate. Missing public evidence is not evidence of nonexistence.
