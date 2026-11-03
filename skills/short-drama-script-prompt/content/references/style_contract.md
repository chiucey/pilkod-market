# Style Contract

## Document Character

This is a **lightweight prompt template document** — not a formal SOP manual, not a training guide, not a decorated professional document. It is meant for direct copy-paste use. Keep it plain, concise, and minimal.

## Reference Typography

- **Primary language**: Chinese (Simplified)
- **Reference font family**: SimSun / Microsoft YaHei (standard system Chinese document fonts)
- **Font classification**: Sans-serif to serif mixed (headings sans-serif feel, body serif-traditional Chinese document style)
- **Typography impression**: Clean, utilitarian, prompt-template style — readability over decoration

## CJK Font Strategy

Since this skill targets Chinese short drama content, assume Chinese/CJK output unless explicitly stated otherwise.

- **Single-font strategy**: Use one CJK-capable font consistently across all text paths
- **Recommended font stack**:
  - Primary: `Microsoft YaHei` (clean, modern, widely available)
  - Fallback: `SimSun` or `Source Han Sans SC`
- **Do not** mix hardcoded Latin-only fonts (e.g., Calibri, Helvetica, Georgia) with patched CJK segments in different components

## Heading Hierarchy

| Level | Marker | Usage |
|-------|--------|-------|
| H2 | `##` | Major sections (输出要求, 示例格式, 注意事项) |
| H3 | `###` | Sub-sections (出场人物, 位置关系, 剧本+情绪特写链, 情绪特写要求) |
| Body | plain | Descriptions, bullet items, dialogue |
| Bold | `**text**` | Emphasis on structural labels and key rules |
| Code | backticks | Example templates, fixed text blocks |

## Visual Treatment Rules

- **No decorative graphics**, charts, or images required
- **No cover page, back cover, or title page**
- **No table of contents**
- **No colored headings or accent colors** — black text only
- **No formatted tables with borders** — use bullet lists and plain text paragraphs instead
- **No page numbers, headers, or footers**
- Emphasis achieved through markdown bold and bracket markers only
- Monospace blocks for example templates
- Clean whitespace: blank lines before and after fixed elements (【场景图】, 【全局提示词】, 【强制声明】)
- Bullet lists using `-` prefix for specifications
- Numbered lists using `1. 2. 3.` for sequential cautions

## Color Palette

- **Text**: Black (#000000)
- **Background**: White (#FFFFFF)
- **No accent colors, no gold, no decorative colors**
- Headings use bold weight only — no color change, no size inflation

## Document Length

The reference is approximately **2 pages**. The output must remain similarly concise. Do not expand into a multi-chapter or multi-page elaborate document.
