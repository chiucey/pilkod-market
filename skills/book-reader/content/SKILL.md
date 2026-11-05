---
name: book-reader
description: Local book knowledge base management (enhanced). Activated when users provide book files (PDF/epub/mobi) and request storage, or ask about book content in the library. Supports: PDF, TXT, MD, EPUB.
---

# Book Reader - Local Book Knowledge Base (Enhanced)

> Supported formats: PDF, TXT, MD, EPUB (Import an ebook directly into your knowledge base and start asking questions immediately)

## Storage Structure

```
/workspace/library/
  <book-title>/
    metadata.json      # title, author, import time, chapter count
    toc.md             # table of contents
    index.json         # chapter summary index (Route B core)
    chapter_01.md      # Chapter 1 full content
    chapter_02.md      # Chapter 2 full content
    ...
```

## Route B: Chapter Summary Index

During import, automatically generate 100-character summary for each chapter, stored in `index.json`:
```json
{
  "chapters": [
    {"id": 1, "title": "Chapter 1 Title", "summary": "Chapter summary...", "file": "chapter_01.md"},
    {"id": 2, "title": "Chapter 2 Title", "summary": "Chapter summary...", "file": "chapter_02.md"}
  ]
}
```

## Q&A Flow

1. **User Question** → Read all summaries from `index.json` → Find most relevant 2-3 chapters
2. **Close Reading** → Read corresponding `chapter_xx.md` files
3. **Organize Answer** → Provide answer combining original text and summaries

## Core Scripts

### Import Book (Route B)
```bash
python3 /workspace/skills/book-reader/scripts/import_book.py <file-path> [book-title]
```
- Extract text and split by chapters
- **Auto-generate 100-character summary per chapter** (via LLM)
- Generate `metadata.json`, `toc.md`, `index.json`

### Search Book
```bash
python3 /workspace/skills/book-reader/scripts/search_book.py <book-title> <keywords>
```
- Search keywords in `index.json` summaries, quickly locate relevant chapters
- Return related chapter list and keyword passages

### List Library
```bash
python3 /workspace/skills/book-reader/scripts/list_library.py
```
- List all books in the library with basic info

### Ask Book (Enhanced Retrieval)
```bash
python3 /workspace/skills/book-reader/scripts/ask_book.py <book-title> <question>
```
- Read `index.json` → Locate relevant chapters → Read original text → Return answer and analysis

## Supported Formats

- **PDF**: Using pymupdf (recommended), fallback to pdfminer
- **EPUB**: Using epubfy
- **TXT/MD**: Direct line reading, split by chapter markers
- **Word (.docx)**: Using python-docx

## Chapter Detection Rules

Detect chapter titles in the following order:
1. PDF: Multi-level headings (h1/h2/h3) + chapter names in page headers
2. Common formats: `Chapter X`, `第X章`, `第一章`
3. Regex patterns: `^第[一二三四五六七八九十百千\d]+[章节篇部]`, `^Chapter\s+\d+`

## Import Flow Details

1. Read file, extract plain text
2. Split by chapters, each chapter as one `.md` file
3. Call LLM to generate 100-character summary per chapter
4. Aggregate all summaries to generate `index.json`
5. Generate `toc.md` table of contents

## Notes

- For books over 500 pages, process in batches to avoid memory overflow
- Traditional Chinese books auto-detected, optional simplified/traditional conversion
- Check if book exists before import to avoid duplicates
- `index.json` is a critical file; deletion requires regenerating summaries
