---
name: doubao-query-materials
description: Professional research skill for global policy and primary source retrieval. Supports Chinese queries, searches official government publications, international organization documents, raw datasets worldwide, outputs structured Chinese results with full traceability for research institute use.
author: Research Institute
version: 1.0
tags:
  - research
  - policy
  - primary-sources
  - global
  - chinese-query
trigger:
  - 查一下
  - 帮我找
  - 查询
  - 搜索
  - 溯源
  - 核实
  - research
  - look up
  - find primary sources
---

# Query Materials Skill Specification
## 1. Core Purpose
Retrieve international policies, official documents, primary sources and raw statistical data globally using Chinese as the query language.
Prioritize authoritative sources: government official gazettes, international organizations (UN, WB, IMF, OECD, WTO, EU), original acts and research reports.
Output professional, traceable results in Chinese for policy research.

## 2. Trigger Conditions
- User queries involve global/cross-border/international policies and regulations
- User requests primary source tracing, verification or in-depth research
- User uses Chinese or English trigger keywords defined in the YAML header
- Exclude: Pure domestic policy queries, basic common sense questions

## 3. Search Strategy
### 3.1 Retrieval Tools
- WebSearch: Automatically expand Chinese keywords to target language + English for global retrieval
- WebFetch: Directly obtain original official documents (EUR-Lex, UN Docs, World Bank Open Data)

### 3.2 Source Priority (Highest to Lowest)
1. National government and regulatory official primary publications
2. International organizations' original documents and raw datasets
3. Top global think tank research reports
4. Peer-reviewed academic papers (SSCI/SCI)
5. Authoritative international media (marked as non-primary sources)

### 3.3 Professional Rules
- Language: Chinese input, multilingual retrieval, Chinese output
- Traceability: Only use original official texts, reject third-party interpretations
- Timeliness: Prioritize valid policies from the past 5 years
- Conflict Handling: Cite all conflicting primary sources and mark differences

## 4. Output Format
### Simple Query (1-2 Primary Sources)
- Core conclusion
- Primary source details (name, publisher, official link, language, validity)
- Timeliness information

### Moderate Query (3-5 Primary Sources / Cross-country Comparison)
- Executive summary
- Key information by country/organization
- Commonalities and divergences
- Source traceability table

### Deep Research (Complex Global Policy)
- Full research report
- Multi-dimensional analysis
- Primary source summary table
- Research limitations

## 5. Citation Standard
- Official documents: Publisher + Document ID + Date + URL
- International organization reports: Institution + Report ID + Year + URL
- Raw datasets: Name + Version + Update time + Download link
- Translation note: For research reference only, subject to official original text

## 6. Quality Assurance
- All core information from authoritative primary sources
- Policy validity and timeliness verified
- Non-Chinese sources with original links and Chinese translation
- All data and sources are verifiable
- Clear statement of research limitations
- Format matches the complexity of user queries