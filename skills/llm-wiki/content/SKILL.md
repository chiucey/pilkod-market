---
name: llm-wiki
description: Build and maintain personal knowledge bases using LLMs with incremental wiki synthesis. Use when users want to create a personal wiki, knowledge management system, research notebook, or second brain powered by LLM agents.
---

# LLM Wiki Skill

A pattern for building personal knowledge bases using LLMs. This skill implements the wiki-based knowledge management approach where the LLM incrementally builds and maintains a persistent, structured, interlinked collection of markdown files.

## Core Concept

Instead of traditional RAG (retrieve and generate) where the LLM rediscovers knowledge from scratch on every question, this skill maintains a **persistent wiki** that sits between you and the raw sources. When you add new sources, the LLM integrates the information into the existing wiki — updating entity pages, revising summaries, noting contradictions, and strengthening synthesis.

**Key advantage:** Cross-references are already there. Contradictions are flagged. The synthesis already reflects everything you've read.

## Directory Structure

```
project/
├── CLAUDE.md          # Schema - instructions for how the LLM should work
├── raw/               # Immutable source documents
│   ├── sources/
│   └── assets/
├── wiki/              # LLM-generated content
│   ├── index.md       # Content catalog
│   ├── log.md         # Chronological activity log
│   ├── entities/      # Entity pages (people, companies, concepts)
│   ├── topics/         # Topic summaries
│   ├── summaries/      # Source summaries
│   └── synthesis/      # Cross-topic synthesis
└── schemas/           # Page templates
```

## Three-Layer Architecture

### Layer 1: Raw Sources
- Curated collection of source documents (articles, papers, images, data)
- **Immutable** — the LLM reads from them but never modifies them
- This is the source of truth

### Layer 2: The Wiki
- LLM-generated markdown files including:
  - Summaries of ingested sources
  - Entity pages (people, organizations, concepts)
  - Topic overviews
  - Comparisons and synthesis
- The LLM owns this layer entirely

### Layer 3: The Schema
- A configuration file (CLAUDE.md) that defines:
  - Wiki structure and conventions
  - Page templates and formats
  - Workflows for ingest, query, and lint
  - Naming conventions and frontmatter standards

## Core Operations

### 1. Ingest Operation

When adding a new source:

```markdown
## Ingest Workflow

1. **Read**: LLM reads the new source document
2. **Discuss**: Highlights key takeaways with the user
3. **Summary**: Creates a summary page in `wiki/summaries/`
4. **Index Update**: Updates `index.md` with the new entry
5. **Entity Update**: Updates relevant entity pages in `wiki/entities/`
6. **Topic Update**: Revises topic pages if relevant
7. **Log**: Appends entry to `log.md`
```

**Log entry format:**
```markdown
## [YYYY-MM-DD] ingest | Source Title
- Source: raw/sources/document.pdf
- Key findings: ...
- Wiki updates: entities/person-x.md, topics/topic-y.md
```

### 2. Query Operation

When answering a question:

1. Read `index.md` to find relevant pages
2. Drill into specific pages
3. Synthesize answer with citations
4. Optionally file good answers back into the wiki as new pages

**Answer formats:**
- Markdown page
- Comparison table
- Slide deck (Marp format)
- Chart (matplotlib)
- Canvas visualization

### 3. Lint Operation

Periodically health-check the wiki:

- **Contradictions** between pages
- **Stale claims** superseded by newer sources
- **Orphan pages** with no inbound links
- **Missing pages** for important concepts
- **Missing cross-references**
- **Data gaps** that could be filled with web search

## Required Files

### CLAUDE.md (Schema)

```markdown
# LLM Wiki Configuration

## Structure
- Raw sources: `./raw/sources/`
- Wiki: `./wiki/`
- Index: `./wiki/index.md`
- Log: `./wiki/log.md`

## Conventions

### Page Naming
- entities: `kebab-case.md` (e.g., `elon-musk.md`)
- topics: `kebab-case.md` (e.g., `large-language-models.md`)
- summaries: `source-title-slug.md`

### Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
related: [entity-name, topic-name]
---
```

### Link Format
- Internal: `[[page-title]]` or `[text](page.md)`
- External: `[text](url)`

## Index Format

```markdown
# Wiki Index

## Summaries (N)
<!-- List of ingested source summaries -->

## Entities (N)
<!-- List of entity pages -->

## Topics (N)
<!-- List of topic pages -->

## Synthesis (N)
<!-- Cross-topic synthesis pages -->
```

## Log Format

```markdown
# Activity Log

<!-- Entries in reverse chronological order -->
## [YYYY-MM-DD] type | Title
Details...

## [YYYY-MM-DD] type | Title
Details...
```

## Use Cases

- **Personal**: Goals, health, psychology, self-improvement tracking
- **Research**: Deep dives on topics over weeks/months
- **Book Reading**: Build pages for characters, themes, plot threads
- **Business**: Internal wikis fed by Slack, meeting transcripts
- **Competitive Analysis**: Due diligence, market research
- **Learning**: Course notes, hobby deep-dives, trip planning

## Recommended Tools

- **Obsidian**: Local markdown wiki with graph view
- **Obsidian Web Clipper**: Browser extension to save articles as markdown
- **qmd**: Local search engine for markdown (BM25/vector + LLM reranking)
- **Marp**: Markdown-based slide decks
- **Dataview**: Obsidian plugin for querying page frontmatter
- **Git**: Version history for wiki comes free

## Why This Works

The tedious part of maintaining a knowledge base is **not** the reading or thinking — it's the bookkeeping:
- Updating cross-references
- Keeping summaries current
- Noting contradictions
- Maintaining consistency across dozens of pages

**Humans abandon wikis** because maintenance burden grows faster than value.

**LLMs don't get bored**, don't forget to update cross-references, and can touch 15 files in one pass.

**Division of labor:**
- Human: Curate sources, direct analysis, ask good questions, think about meaning
- LLM: Everything else — the actual bookkeeping and synthesis

## Implementation Workflow

### Start a New Wiki

1. Create directory structure
2. Write `CLAUDE.md` with schema
3. Create initial `index.md` and `log.md`
4. Begin ingesting sources

### Process a Source

```
User: "Please ingest this paper about transformers"
Assistant:
1. Creates summary in wiki/summaries/
2. Extracts entities and creates/updates pages
3. Updates topic summaries
4. Updates index.md
5. Logs the ingest
```

### Answer a Question

```
User: "What do we know about attention mechanisms?"
Assistant:
1. Reads index.md to find relevant pages
2. Reads attention-related pages
3. Synthesizes answer with citations
4. Optionally saves as new synthesis page
```

### Maintain the Wiki

```
User: "Lint the wiki"
Assistant:
1. Scans for contradictions
2. Checks for stale content
3. Finds orphan pages
4. Identifies missing cross-references
5. Reports findings and optionally fixes issues
```

## Best Practices

1. **Immutable sources**: Never modify raw sources
2. **Atomic commits**: Each ingest is a logical unit
3. **Consistent frontmatter**: Enables Dataview queries
4. **Link everything**: Cross-reference liberally
5. **Log everything**: Chronological record helps track evolution
6. **Periodic linting**: Keep wiki healthy
7. **File back**: Save good answers as wiki pages
