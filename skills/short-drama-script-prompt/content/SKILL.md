---
name: short-drama-script-prompt
description: Convert short drama scripts into structured AI video generation prompt templates with shot-by-shot emotional breakdowns. Use when the user provides a script and wants structured video generation prompts, short drama storyboard breakdowns, TikTok/Douyin short drama prompts, script-to-prompt conversion, episode shot decomposition, or any task involving transforming narrative scripts into per-shot AI generation instructions with character positioning, emotional close-ups, and camera direction. Supports Chinese short dramas and viral short-form video content production. Output is a lightweight prompt template document, NOT a formal SOP manual.
---

# Short Drama Script-to-Prompt Generator

Convert short drama scripts into structured, per-shot AI video generation prompts optimized for short-form drama platforms (Douyin/TikTok).

## CRITICAL: Document Character

The output is a **lightweight prompt template** — a simple, copy-paste-ready specification document. It is **NOT** a formal SOP manual, training guide, or elaborate multi-chapter handbook. The reference is a 2-page plain text document with minimal formatting. **Never transform it into a decorated or expanded document.**

## Reference Source

- **Reference type**: Uploaded artifact (DOCX)
- **Reference artifact type**: DOCX
- **Reference File Type**: DOCX
- **Style contract**: Concrete reference — plain markdown-style text with bold headings, bullet lists, code blocks, and black-on-white minimal formatting
- **Structure contract**: Concrete reference — exactly 3 top-level sections (输出要求, 示例格式, 注意事项) with 4 sub-sections under 输出要求

## Supported Outputs

| Format | Support |
|--------|---------|
| DOCX | Primary (default) — matches reference artifact type |
| Markdown / Plain text | Supported |
| PDF | Supported |

**Default output selection**: When the user does not specify a format, output as DOCX. The DOCX must preserve the same plain, lightweight character as the reference — simple black text on white background, bold headings, bullet lists, code blocks, and numbered lists. No professional document styling.

## Style Guardrails — ABSOLUTE PROHIBITIONS

When generating any output format, **NEVER** add any of the following. The reference has NONE of these:

- ❌ Cover page, back cover, or title page
- ❌ Table of contents
- ❌ Colored headings, gold accents, or any accent colors
- ❌ Decorative borders, dividers, background colors, or dark backgrounds
- ❌ Formatted tables with headers and borders (the reference uses bullet lists and plain text, not tables)
- ❌ Page numbers, headers, or footers
- ❌ Watermarks, logos, or brand marks
- ❌ Chapter-style numbering beyond the reference's simple `##` / `###` hierarchy
- ❌ Expansion beyond ~2 pages — the reference is concise

**Permitted formatting only**:
- ✅ `##` and `###` markdown-style headings (bold, slightly larger text)
- ✅ `**bold**` for emphasis on structural labels
- ✅ `-` bullet lists for specifications
- ✅ `1. 2. 3.` numbered lists for sequential notes
- ✅ ` ``` ` code blocks for the example template
- ✅ Blank lines for visual separation
- ✅ Black text on white background only

## Structure Contract — Exact 3-Part Layout

The output must match the reference's exact section hierarchy. Do NOT expand, reorganize, or add chapters.

```
第 X 集 场景描述
第 N 组 00:00-00:15
【出场人物】角色A、角色B
【位置关系】角色A站在门口，角色B端坐沙发...

【场景图】参考@图片 的场景布局，将人物放置在对应的位置根据剧本描述的对话内容和人物神态动作，生成连贯的室内对话视频
【全局提示词】你自己安排爆款短剧风格多机位与高预算运镜，多角度特写，超特写（避免全景）
【强制声明】：无背景音乐；无字幕，无文字叠加，无 UI，禁止出文字字幕在画面中

【剧本 + 情绪特写链】角色A推门而入，脸上堆着刻意讨好的假笑，扬声喊出台词【台词内容】△表情描述，肢体动作...
```

### Top-Level Structure (never expand beyond these 3 sections)

1. **## 输出要求**
   - **每集拆分规格** (bullet list: 10组镜头×15秒, time format, overflow rule)
   - **每组镜头必须包含**
     - ### 1. 出场人物 (plain text description)
     - ### 2. 位置关系 (bullet list: 站位/坐位, 空间关系, 面向方向, 场景布局)
     - ### 3. 剧本 + 情绪特写链（核心部分）
       - **剧本还原** (bullet list: 完整还原台词, 保留标点, 按说话顺序)
       - **情绪特写链**（重点） (bullet list: 面部表情细节, 眼神变化, 肢体动作细节, 情绪层次变化, 特殊道具细节, 氛围营造)
     - ### 4. 情绪特写要求 (bullet list: 面部表情, 眼神, 肢体, 声音)

2. **## 示例格式** (code block containing the exact template shown above)

3. **## 注意事项** (numbered list: 1–6 items exactly as in reference)

### Per-Shot Output Structure (within generated prompts)

| Section | Content | Fixed / Variable |
|---------|---------|-----------------|
| Episode header | `第 X 集 场景描述` | Variable |
| Shot group header | `第 N 组 00:00-00:15` | Variable |
| 【出场人物】 | Character names, `、` separated | Variable |
| 【位置关系】 | Standing/sitting, spatial relations, facing direction, scene layout | Variable |
| *(blank line)* | | Fixed |
| 【场景图】 | Fixed text | **Fixed** |
| 【全局提示词】 | Fixed text | **Fixed** |
| 【强制声明】 | Fixed text | **Fixed** |
| *(blank line)* | | Fixed |
| 【剧本 + 情绪特写链】 | Script + emotional close-up chain | Variable |

> **Note**: The parenthetical line "（【场景图】和 【全局提示词】 和【强制声明】 为固定不变项 直接输出即可，无需任何处理，但前后需要空一行）" is a documentation instruction only — do NOT include it in actual prompt output.

## Workflow

1. **Receive and analyze the script**
   - Identify total episode duration
   - Confirm with user if duration is unclear
   - Map episode count and scene boundaries

2. **Determine shot-group count**
   - Default: 10 groups × 15 seconds = 150 seconds per episode
   - Time range format per group: `00:00-00:15`, `00:15-00:30`, etc.
   - Maximum 15 seconds per group; overflow extends to next group
   - Adapt if user specifies different episode length

3. **Process episode by episode**
   - For each episode, output a complete shot-breakdown block
   - Maintain chronological dialogue order
   - Preserve all original punctuation in dialogue

4. **Generate per-shot prompts**
   - Build the six mandatory sections per shot group (see Structure Contract)
   - Ensure emotional continuity and escalation across groups
   - End each episode with suspense or emotional climax

5. **Quality check**
   - Verify no plot or dialogue has been omitted
   - Verify fixed elements are present and unmodified
   - Verify △ markers and 【】 dialogue wrappers are correctly applied

## Core Section: 【剧本 + 情绪特写链】

**A. 剧本还原 (Script Restoration)**
- Restore complete dialogue for this time segment
- Preserve all punctuation marks exactly
- Arrange in speaking order

**B. 情绪特写链 (Emotional Close-up Chain)** — the focal element
For every character present in this shot, describe in order:
- Facial expression details (muscle-level specificity): corner-of-mouth twitching, reddened eye rims, sudden pupil contraction, etc.
- Eye changes: pupil dilation, gaze direction, emotional tone (bewildered, resentful, manic, icy, etc.)
- Body movement details: finger trembling, half-step backward, forward lean, stiffness, collapse, etc.
- Emotional layer transitions: how emotion evolves within the shot
- Special prop details: lighter, gasoline, suitcase, etc.
- Atmosphere construction: tension, warmth, dread, etc.

## Special Markers

| Marker | Usage |
|--------|-------|
| `△` | Prefix for action and expression descriptions |
| `【】` | Wrap all spoken dialogue |
| `**` | Bold emphasis for structural headers (in markdown/DOCX output) |

## Platform-Specific Rules

### Douyin / TikTok Short Drama Conventions
- **Shot style**: Multi-camera, high-budget camera movement, multi-angle close-ups, ultra-close-ups (avoid wide shots)
- **Pacing**: Rapid emotional escalation, cliffhanger endings
- **Camera**: Emphasis on facial close-ups rather than establishing shots
- **Duration**: Episodes typically 60–150 seconds; adapt group count accordingly
- **Forbidden in frame**: Background music indicators, subtitles, text overlays, UI elements, any on-screen text

## Cautions (输出注意事项)

1. Emotional close-ups must reach muscle-level specificity
2. Use `△` symbol consistently to mark actions and expressions
3. Wrap all dialogue in `【】`
4. Maintain plot continuity and emotional escalation across shot groups
5. Final shot group of each episode must end with suspense or emotional climax
6. Never delete any plot point or dialogue line — verify completeness before output

## Typography

- **Primary language**: Chinese (Simplified)
- **Reference font**: Standard system Chinese fonts (SimSun / Microsoft YaHei equivalent)
- **Font strategy**: Use one consistent CJK-capable font family throughout. When generating DOCX/PDF, select a widely available Chinese font (e.g., Microsoft YaHei, SimSun, or Source Han Sans). Do not mix Latin-only defaults with patched CJK segments.
- **Heading hierarchy**: `##` for major sections (输出要求, 示例格式, 注意事项), `###` for sub-sections (出场人物, 位置关系, etc.)
- **Body text**: Regular weight, standard size for Chinese documents
- **Color**: Black text on white background only — no accent colors

## Runtime Adaptation

When user provides a script:
- **If total duration is specified**: recalculate group count (duration ÷ 15s per group, rounding up)
- **If total duration is not specified**: ask user to confirm before outputting; default to 10 groups (150s)
- **If script spans multiple episodes**: process each episode separately with its own header
- **If script contains scene changes within one episode**: assign new scene descriptions to the header while keeping chronological group numbering
- **If output format is requested as DOCX/PDF**: preserve the same plain, lightweight structure; use consistent CJK font; apply bold formatting to section headers; **never add cover pages, TOCs, colored headings, tables, or decorative elements**
