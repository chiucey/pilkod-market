---
name: wiki-creator
description: >-
  A specialized skill for generating technical Wiki documentation, glossary, and knowledge base from solution descriptions, whitepapers, technical documents, or any text content. This skill automatically extracts technical keywords, terminology, and professional concepts, organizes them into a categorized index, and generates individual detail pages for each term — all as a self-contained, navigable HTML Wiki. Use when the user says things like (or similar variations): "帮我生成 wiki", "制作技术词条", "制作术语表", "制作词汇表", "术语解释", "名词解释", "关键词提取", "概念说明", "解释文档里的专业词汇", "给这个方案创建一个知识库", "创建一个百科", "这个方案有哪些关键技术", "帮我把专业术语整理一下", "整理术语", "技术文档生成", "解决方案白皮书", "make a wiki", "create term glossary", "create vocabulary list", "create terminology list", "technical glossary", "knowledge base", "explain technical terms", "extract keywords from document", "technical documentation", "whitepaper summary", "term explanation", "概念词汇整理", "技术概念解释", "AI documentation generator".
---

# Wiki Creator

## Purpose

Generate a self-contained, navigable technical Wiki from user-provided solution documents or technical descriptions. The Wiki helps readers quickly understand complex professional terminology by providing:

1. **Index Page** (`index.html`): A categorized, alphabetically/logically ordered directory of all technical keywords, each linking to its detail page.
2. **Detail Pages** (`terms/<term-id>.html`): Individual pages for each term, with rich explanations, cross-links to related Wiki terms, and external references.

Only include terms that are **technically complex** and require domain knowledge — skip trivial words, product names, and self-explanatory concepts.

---

## Workflow

### Phase 1: Analyze Input Document

Read the user's uploaded document or pasted text carefully. Identify all **technically significant** keywords and concepts:

- Include: protocols, architectures, algorithms, design patterns, specialized data formats, domain-specific frameworks, hardware concepts, security mechanisms, mathematical models, etc.
- Exclude: generic IT terms every developer knows (e.g., "server", "database", "file"), brand names used without explanation, overly vague terms.

For each identified term, collect:
- **Term name** (canonical English or Chinese name)
- **Aliases** (abbreviations, alternate names)
- **Category** (e.g., 网络协议, 安全机制, 存储架构, AI/ML, 区块链, 工业控制, etc.)
- **Complexity level**: HIGH (needs detailed explanation with sub-concepts) or MEDIUM (can be explained in a few paragraphs)
- **Related terms** (within the same document)
- **Key external references** (official specs, Wikipedia, reputable sources)

### Phase 2: Plan Term Coverage and Categories

Group terms into logical categories. For HIGH complexity terms, plan whether their detail pages will need:
- Sub-section anchors within the same page
- Cross-links to other Wiki terms
- External links (official documentation, RFCs, papers)

Produce a structured outline like:

```
Category A (e.g., 通信协议)
  ├── Term 1 (HIGH)
  └── Term 2 (MEDIUM)
Category B (e.g., 安全机制)
  ├── Term 3 (HIGH)
  └── Term 4 (MEDIUM)
...
```

Confirm this outline with the user before proceeding to generation, unless the user has asked for direct output.

### Phase 3: Generate Wiki Files

Generate a complete Wiki as HTML files. Load `references/wiki-template.md` for the precise HTML structure, CSS design system, and component patterns to use.

#### File Structure

```
wiki-output/
├── index.html          ← Directory/Index page
└── terms/
    ├── <term-id-1>.html
    ├── <term-id-2>.html
    └── ...
```

#### Index Page Requirements

- Page title: "{Document/Project Name} 技术 Wiki"
- Include a brief description of the source document
- Group terms by category
- Within each category, list terms alphabetically (or by logical dependency order)
- Each term entry must show:
  - Term name (as a clickable link → detail page)
  - One-line summary (≤ 30 Chinese characters or ≤ 60 English characters)
  - Category badge
- Add a search/filter bar (pure HTML+JS, no external dependencies)
- Include a stats bar: total term count, category count, last generated date

#### Detail Page Requirements

Each term's detail page must include:

1. **Header**: Term name, aliases in parentheses, category badge, back-to-index link
2. **Definition**: Clear, concise definition (1–3 sentences)
3. **Technical Deep Dive**: Detailed explanation suited to the complexity level
   - For HIGH complexity: use `<h3>` sub-sections, diagrams described as ASCII art or structured lists
   - For MEDIUM complexity: 2–4 paragraphs
4. **Why It Matters** (在本方案中的作用): Explain the term's role in the source document's context
5. **Related Terms** (相关词条): Links to other Wiki pages for related terms
6. **External References** (延伸阅读): 2–5 authoritative links (official docs, RFCs, Wikipedia, papers)
7. **Footer**: navigation arrows (← previous term, → next term), back-to-index

For HIGH complexity terms where sub-concepts are themselves Wiki terms, add inline `<a href="../terms/<id>.html">` cross-links within the explanation text.

### Phase 4: Output and Delivery

- Write all files to `wiki-output/` within the current workspace
- Ensure all links use relative paths (no absolute paths)
- Verify every term in the index has a corresponding detail page
- Open `index.html` preview for the user using the preview tool
- Report: total terms generated, categories, any terms skipped and why

---

## Quality Standards

- **Language**: Match the user's language. If the source document is Chinese, write Wiki in Chinese with English technical terms in parentheses. If English, write in English.
- **No external CDN dependencies**: All CSS and JS must be inline or in a `<style>`/`<script>` block. The Wiki must work offline.
- **Consistent visual design**: Use the design system defined in `references/wiki-template.md`.
- **Accuracy over completeness**: If uncertain about a term's definition, note it clearly rather than fabricate content. Use web search to verify definitions when needed.
- **Cross-link integrity**: Every "Related Terms" link must point to an actual page that exists in the output.

---

## Resource References

- `references/wiki-template.md`: HTML/CSS design system, component patterns, and code templates for building the Wiki pages. Load this before starting Phase 3.
