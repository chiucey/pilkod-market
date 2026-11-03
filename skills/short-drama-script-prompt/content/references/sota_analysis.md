# SOTA Analysis

## Source Artifact

- **File**: `新建 DOCX 文档.docx`
- **Content type**: Prompt engineering template for short drama storyboard breakdown
- **Language**: Chinese (Simplified)
- **Creator credit**: Made By 光影矩阵
- **Document length**: ~2 pages
- **Document character**: Lightweight prompt template — NOT a formal SOP, training manual, or decorated professional document

## Visual Analysis

### Page Composition
- Simple, single-column text layout
- Standard document margins
- No columns, tables with borders, or complex grid structures
- Generous whitespace between content blocks
- Approximately 2 pages total

### Typography
- Standard Chinese document font (SimSun / Microsoft YaHei)
- `##` headings rendered as bold, slightly larger text
- `###` sub-headings rendered as bold text
- Body text in regular weight, standard size
- Bold (`**text**`) used for structural emphasis labels like `**每集拆分规格**:`
- Monospace/code blocks for the example template section

### Color and Accent
- **Absolutely no color usage** — entirely black text on white background
- No gold, no accent colors, no decorative colors
- Emphasis through bold weight and bracket symbols only

### Visual Density
- Low-to-medium density
- Structured through whitespace and hierarchical markdown-style markers
- Bullet lists (`-`) and numbered lists (`1. 2. 3.`) provide visual rhythm
- Code blocks (```) set apart the example template

### What the Reference Does NOT Have
This is critical for preventing over-decoration:
- ❌ No cover page or title page
- ❌ No back cover
- ❌ No table of contents
- ❌ No colored headings or accent colors
- ❌ No decorative borders or dividers
- ❌ No background colors or dark backgrounds
- ❌ No formatted tables with headers and borders
- ❌ No page numbers
- ❌ No headers or footers
- ❌ No watermarks or logos
- ❌ No chapter-style numbering system beyond simple `##` / `###`

## Structural Analysis

### Exact Section Hierarchy
The reference has exactly **3 top-level sections** with a specific internal hierarchy:

1. **## 输出要求**
   - `**每集拆分规格**:` (3 bullet items)
   - `**每组镜头必须包含**:`
     - `### 1. 出场人物` (plain text line)
     - `### 2. 位置关系` (4 bullet items)
     - `### 3. 剧本 + 情绪特写链（核心部分）`
       - `**剧本还原**:` (3 bullet items)
       - `**情绪特写链**（重点）:` (6 bullet items)
     - `### 4. 情绪特写要求` (4 bullet items)

2. **## 示例格式**
   - Code block (```) containing the per-shot template

3. **## 注意事项**
   - Numbered list with exactly 6 items

### Key Structural Patterns

- **Fixed/Variable split**: Three elements (【场景图】, 【全局提示词】, 【强制声明】) are explicitly marked as fixed and unchangeable; all other sections are variable per shot
- **Core emphasis**: The 【剧本 + 情绪特写链】 section is labeled as the core/focal element
- **Symbol convention**: △ for action/expression markers, 【】for dialogue wrapping
- **Time math**: 10 groups × 15s = 150s default per episode
- **Quality gate**: "禁止删减任何情节和台词，输出前必须核查" — completeness verification required

### Content Patterns

- Emotional descriptions target "muscle-level" specificity
- Shot style emphasizes close-ups over wide shots
- Camera direction favors multi-angle, high-budget movement
- Forbidden elements in generated video: music, subtitles, text overlays, UI

## Judge Feedback from Round 1

### Issues Identified
1. **Style mismatch**: Rollout output was a 15-page professionally styled SOP with cover page, TOC, gold headings, tables — reference is a simple 2-page plain text document
2. **Structure mismatch**: Rollout expanded 3 basic sections into 13 chapters with many subsections and added content not in reference
3. **Over-decoration**: Cover page, back cover, colored headings, formatted tables, page numbers, decorative elements were all added when the reference has none

### Fixes Applied in Round 2
1. Added **Style Guardrails — ABSOLUTE PROHIBITIONS** section with explicit ❌/✅ rules
2. Explicitly declared document character as "lightweight prompt template — NOT a formal SOP"
3. Restricted structure to exact 3-part layout with no expansion
4. Enforced black-on-white, no tables, no cover/TOC, ~2-page length constraint
5. Added explicit "What the Reference Does NOT Have" section in SOTA analysis

## Derived Contracts

### Style Contract
- Plain text with markdown conventions
- Bold for structural emphasis
- Code blocks for templates
- Whitespace-driven separation
- Black text on white only
- No decoration whatsoever

### Structure Contract
- Exactly 3 top-level sections
- 4 sub-sections under 输出要求
- Per-shot repetitive block structure with fixed elements
- Episode-level grouping with sequential numbering
- Time-range continuity within episodes
