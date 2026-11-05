---
name: tech-evidence-research
description: >-
  Research and verify technology, digital-product, and AI news, model claims, benchmarks, releases,
  versions, APIs, specifications, licenses, safety statements, and technical literature. Use for dated
  tech briefings, evidence-based AI or product verification, or paper discovery and synthesis.
---

# Technology Evidence Research

Choose one mode: news briefing, technology/AI verification, or paper research. Keep discovery, verification, and synthesis distinct. This skill is platform-neutral and requires capabilities rather than named providers.

## 1. Choose the mode

- **Briefing:** several recent technology, digital-product, or AI stories within a defined time window.
- **Verification:** one or more claims about capability, performance, price, API behavior, release, version, specification, license, training data, privacy, copyright, or safety.
- **Paper research:** find, expand, read, compare, and synthesize papers, whitepapers, technical reports, or scholarly sources.

If a briefing contains a disputed factual claim, flag it for verification rather than silently upgrading it to fact. If an image/video is central to the claim, use a media-provenance capability separately.

## 2. Freeze the subject and conditions

For verification, record the exact product/model, version/build/API model ID, region, plan, endpoint, release/documentation date, test date, hardware, software/runtime, dataset, benchmark harness, prompt/tool settings, and comparison set. Unknown conditions remain unknown; do not substitute the latest version without saying so.

For a briefing, record time window, topic, language, region, freshness cutoff, and intended audience. For papers, record query, inclusion/exclusion criteria, target number, publication window, source types, and whether full text is required.

## 3. Collect source-of-record evidence

Prefer official release notes, versioned documentation, model/system cards, license terms, security advisories, regulator statements, original papers, repositories, and reproducible artifacts. Marketing copy establishes what a publisher claims; it does not establish real-world performance or legal effect by itself.

For paper research, search the paper graph, inspect canonical metadata, and read the body when the question concerns methods, scores, comparisons, attribution, or limitations. An abstract or ranking screenshot is not enough for a decisive technical claim.

### 3.1 Technology source pool

Use configurable source classes rather than a mandatory outlet list:

- vendor release notes, documentation, blogs, model/system cards, and repositories;
- standards bodies, regulators, security advisories, and research organizations;
- original papers, preprints, benchmarks, datasets, and code;
- reputable technology journalism and trade press;
- community posts and social discussion as leads.

Record language, region, publication date, update date, source relation, and whether the page is primary, independent, or derivative. A source pool should be reviewed for scope and freshness over time.

## 4. Run the selected mode

### 4.1 News briefing

1. Search official releases, reputable news, trade sources, and community leads.
2. Deduplicate by event and source relationship; repost count is not independent confirmation.
3. Rank major events, releases, product changes, research, and industry developments.
4. Read full pages for important details and preserve publication dates.
5. Output a dated briefing with headline, product/release, AI/model, industry/company, theme timeline, caveats, and source links.

#### Briefing conditions

Record cutoff, time window, language, region, topic, and audience. Collect official releases, reputable reporting, trade sources, community leads, and research updates. Read important pages rather than relying on headlines or snippets.

Deduplicate by event, original source, wire copy, press release, and quotation. Rank impact, product/release relevance, research significance, and industry consequence. Label developing or disputed items and route a single factual dispute to a verification workflow.

#### Suggested briefing output

```markdown
# <date> Technology briefing
## Top stories
## Products and releases
## AI and models
## Research and standards
## Industry and companies
## Disputed or unverified items
## Sources with publication dates
```

### 4.2 Technology and AI verification

1. Atomize capability, metric, price, context limit, API, specification, version, license, safety, privacy, or training-data claims.
2. Compare official declaration with independent evidence and reproducible results.
3. Consult the benchmark, license, model-version, and AI-safety reference sections below as needed.
4. Check counterevidence, test limitations, data contamination, cherry-picking, and harness differences.
5. Record every material claim in the evidence-ledger format (Section 7).
6. Use these states: official claim, independently supported, reproducible, contested, not established, contradicted.

#### Verification approach

Split claims into capability, metric, price, context limit, API behavior, specification, version, license, training data, privacy, copyright, or safety. Freeze subject and conditions. Start with official documentation, release notes, model/system cards, license, and security advisories; then check original papers, benchmark methods, independent tests, and reproducible artifacts.

Separate:

- official claim;
- independent support;
- reproducible result;
- contested evidence;
- not established;
- contradicted.

A vendor score, leaderboard screenshot, or marketing statement is not enough without date, version, harness, dataset, hardware, method, and limitations.

### 4.3 Paper research

1. Search papers by concept, method, task, dataset, and date.
2. Expand similar papers, citers, references, and research families when the question is broad.
3. Inspect author, venue, date, version, DOI, repository, and paper type.
4. Read the body for method, result, comparison, attribution, and limitations.
5. Distinguish peer-reviewed paper, preprint, vendor report, whitepaper, blog, and news article.
6. Return a literature synthesis with key papers, consensus, debates, open questions, trends, sources, and rerun inputs.

#### Paper research approach

For broad queries, search a paper family rather than stopping at the first result. Expand similar papers, citers, and references, then inspect canonical metadata and read the body for methods, scores, comparisons, attribution, and limitations. Distinguish peer-reviewed work, preprints, vendor reports, whitepapers, technical blogs, and journalism.

#### Suggested paper output

```markdown
# Literature review: <topic>
## Query and inclusion rules
## Abstract
## Key papers
## Themes and consensus
## Open questions and debates
## Emerging trends
## Limitations and inaccessible full text
## Sources
## Rerun inputs
```

A related-paper link does not replace reading the cited paper. Abstract-only evidence must be labelled.

## 5. Keep evidence and uncertainty visible

"Not found" is not "false". A missing leaderboard condition is not a benchmark result. Different harnesses are not directly comparable. Separate official policy, technical control, observed behavior, incident report, and legal/regulatory finding.

Record publication time, capture time, version, reporting/test period, source relationship, excerpt, support/refute status, confidence, contradictions, and access limits. If a PDF, source, or benchmark is inaccessible, state which conclusion cannot be made.

## 6. Output

Use Markdown or JSON/YAML. Verification output should include: claim, version/date/conditions, official evidence, independent evidence, reproduction, contradictions/limits, verdict, evidence ledger, and access limits. Briefing output should include: cutoff, categories, dated items, duplicate-source notes, disputed items, and sources. Paper output should include: query, method, key papers, themes, debates, limitations, sources, and rerun inputs.

## 7. Evidence ledger format

Record every material claim using the structure below. Keep source authority separate from claim confidence. Do not infer missing version, date, benchmark condition, or license.

```yaml
claim: "atomic technical claim"
claim_type: fact | interpretation | prediction | definition
value: "reported value or statement"
unit: "unit or unknown"
version: "model/product version or unknown"
conditions: "test, region, plan, or unknown"
source_url: "https://..."
source_org: "publisher or institution"
published_at: "ISO-8601 or unknown"
captured_at: "ISO-8601"
source_relation: primary | independent | derivative | repost | same_event_unknown
excerpt: "short quote"
supports_or_refutes: supports | refutes | mixed | context_only
status: official_claim | independently_supported | reproducible | contested | not_established | contradicted
confidence: high | medium | low | unresolved
contradictions: []
access_limit: none | login | paywall | regional | snippet_only | unavailable_tool | other
```

## 8. Reference checklists

### 8.1 Benchmark checklist

Capture benchmark/task, dataset/split, model version, prompt/harness, hardware, runtime, sampling/tool settings, date, sample size, baseline, comparison set, evaluator, and known limitations. Mark vendor-run, independent, or reproduced. Do not compare scores from different harnesses as if they were the same measurement. Record contamination, cherry-picking, and missing methodology as limitations.

### 8.2 Licenses and terms

Record exact license and version, copyright holder, code versus weights, commercial-use clause, attribution, redistribution, acceptable-use restrictions, geographic/sector limits, and API terms. Separate open-source code, model-weight terms, dataset terms, and API terms. If the actual terms cannot be read, mark legal status unresolved rather than assuming "open" or commercially usable.

### 8.3 Model and product version

Record public name, exact model ID/build/firmware, release and deprecation dates, documentation revision, test date, capture date, region, plan, endpoint, and feature flags. When sources disagree, prefer the source closest to the version and time under study. State when results may have changed after testing.

### 8.4 AI safety, privacy, and policy

Distinguish vendor policy, technical control, observed behavior, incident report, regulator/court finding, and independent audit. For copyright/training-data claims record jurisdiction, date, data category, and whether evidence concerns a policy, alleged use, or legal ruling. For incidents preserve affected version, timeline, impact, remediation, confirmation status, and unresolved allegations.

## 9. Platform adapters

Required capabilities may include web search, source/page/PDF reading, paper search, paper-graph expansion, benchmark reading, license reading, version resolution, evidence recording, and structured output. Map them to the host using the table below. Missing capabilities produce a bounded result and explicit `unable_to_verify` fields.

| Capability | Minimum output | Optional adapter examples |
|---|---|---|
| `source_search` | URL, title, publisher, date, snippet | native search, regional/semantic search |
| `page_extract` | readable page/PDF and capture metadata | page reader, crawler, document parser |
| `search_papers` | paper metadata and stable link | scholarly index, repository search |
| `expand_paper_graph` | similar/citers/references with relation | citation graph service |
| `read_paper_claim` | body excerpt, section, method/result/limit | PDF/text reader |
| `benchmark_check` | score plus harness, dataset, hardware, date | benchmark registry or test artifact |
| `license_check` | exact terms and version | repository/license/document reader |
| `version_resolve` | release/build/endpoint and dates | release feed, docs history, API metadata |
| `evidence_ledger` | structured claim/source records | host schema or ledger |
| `structured_output` | Markdown plus JSON/YAML fields | host renderer |

Record auth, quota, region, freshness, citation support, extraction quality, privacy behavior, and failure state. If a PDF or page cannot be read, preserve that limitation. Do not put credentials in this skill.

## Completion check

The mode and scope are explicit; exact version and conditions are not silently substituted; official and independent evidence are separate; benchmark methodology and license terms are readable or marked unavailable; dates and versions are visible; source relationships and conflicts are recorded; and the conclusion does not exceed the evidence.
