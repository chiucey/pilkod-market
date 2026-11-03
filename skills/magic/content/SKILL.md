---
name: magic
description: Create original knowledge comics from text content. Supports multiple visual styles (classic, dramatic, warm, sepia, vibrant, ohmsha, realistic, wuxia, shoujo) and layouts (standard, cinematic, dense, splash, mixed, webtoon). Automatically analyzes content, generates storyboards, creates characters, and produces comic pages.
dependency:
  system:
    - which gm || which convert
---

# Knowledge Comic Creator

Create original knowledge comics with multiple visual styles.

## Usage

```
/magic posts/turing-story/source.md
/magic  # then paste content
```

## Options

| Option | Values |
| --- | --- |
| `--style` | classic (default), dramatic, warm, sepia, vibrant, ohmsha, realistic, wuxia, shoujo, or custom description |
| `--layout` | standard (default), cinematic, dense, splash, mixed, webtoon |
| `--aspect` | 3:4 (default, portrait), 4:3 (landscape), 16:9 (widescreen) |
| `--lang` | auto (default), zh, en, ja, etc. |

Style × Layout × Aspect can be freely combined. Custom styles can be described in natural language.

__Aspect ratio is consistent across all pages in a comic.__

## Auto Selection

| Content Signals | Style | Layout |
| --- | --- | --- |
| Tutorial, how-to, beginner | ohmsha | webtoon |
| Computing, AI, programming | ohmsha | dense |
| Pre-1950, classical, ancient | sepia | cinematic |
| Personal story, mentor | warm | standard |
| Conflict, breakthrough | dramatic | splash |
| Wine, food, business, lifestyle, professional | realistic | cinematic |
| Martial arts, wuxia, xianxia, Chinese historical | wuxia | splash |
| Romance, love, school life, friendship, emotional | shoujo | standard |
| Biography, balanced | classic | mixed |

## Script Directory

__Important__: All scripts are located in the `scripts/` subdirectory of this skill.

__Agent Execution Instructions__:

1. 脚本路径: `<skill-directory>/scripts/merge-to-pdf.ts`
2. 执行前需要: 安装 GraphicsMagick (`brew install graphicsmagick`) 或 ImageMagick
3. 执行命令: `bun <skill-directory>/scripts/merge-to-pdf.ts <comic-directory>`

__Script Reference__:

| Script | Purpose |
| --- | --- |
| `merge-to-pdf.ts` | Merge comic pages into PDF |

**Usage**: 脚本需要 GraphicsMagick 或 ImageMagick 依赖。执行方式:
```bash
cd <skill-directory> && bun scripts/merge-to-pdf.ts <comic-directory>
```

## File Structure

Each session creates an independent directory named by content slug:

```
comic/{topic-slug}/
├── source-{slug}.{ext}            # Source files (text, images, etc.)
├── analysis.md                    # Deep analysis results (YAML+MD)
├── storyboard-chronological.md    # Variant A (preserved)
├── storyboard-thematic.md         # Variant B (preserved)
├── storyboard-character.md        # Variant C (preserved)
├── characters-chronological/      # Variant A chars (preserved)
│   ├── characters.md
│   └── characters.png
├── characters-thematic/           # Variant B chars (preserved)
│   ├── characters.md
│   └── characters.png
├── characters-character/          # Variant C chars (preserved)
│   ├── characters.md
│   └── characters.png
├── storyboard.md                  # Final selected
├── characters/                    # Final selected
│   ├── characters.md
│   └── characters.png
├── style-reference.png            # ⚠️ CRITICAL: First page as style reference (mandatory)
├── prompts/                       # Image generation prompts (for tracking)
│   ├── 00-cover-[slug].md
│   └── NN-page-[slug].md
├── 00-cover-[slug].png            # Final comic pages
├── NN-page-[slug].png
└── {topic-slug}.pdf
```

**style-reference.png 的生成时机**:
- 在第一页（封面或第一故事页）生成并确认质量后
- 将该页面复制为 `style-reference.png`
- 该文件将作为所有后续页面的**唯一风格权威参考**
- 所有后续页面生成时**必须使用**此参考图像

__Slug Generation__:

1. Extract main topic from content (2-4 words, kebab-case)
2. Example: "Alan Turing Biography" → `alan-turing-bio`

__Conflict Resolution__:
If `comic/{topic-slug}/` already exists:

- Append timestamp: `{topic-slug}-YYYYMMDD-HHMMSS`
- Example: `turing-story` exists → `turing-story-20260118-143052`

__Source Files__:
Copy all sources with naming `source-{slug}.{ext}`:

- `source-biography.md`, `source-portrait.jpg`, `source-timeline.png`, etc.
- Multiple sources supported: text, images, files from conversation

## Quality Guidelines

### Narrative Logic

漫画故事必须符合常识和逻辑性：

- **因果关系**: 每个情节转折必须有合理的因果关系，不能出现突兀或无依据的变化
- **人物动机**: 所有角色的行为和决策必须有明确、可信的动机
- **时间线一致**: 故事时间线必须连贯，避免逻辑矛盾或时间错乱
- **真实性**: 即使是虚构内容，也要符合现实世界的物理规律和社会常识（除非是明确的幻想题材）
- **情感合理**: 人物的情感反应和变化必须符合其性格背景和当前情境

### Text Generation

漫画中的文字内容遵循以下原则：

- **默认语言**: 如果用户没有特别要求，所有对话、旁白、标注等文字默认使用**简体中文**
- **文字质量**: 必须确保文字正确无误，避免错别字、畸形字、乱码等问题
- **一致性**: 同一角色、同一术语在不同页面中的表达必须保持一致
- **可读性**: 文字大小、字体选择要确保在漫画页面中清晰可读
- **文化适配**: 翻译内容要考虑目标受众的文化背景，避免直译导致的表达生硬

### Visual-Text Coordination

- 文字与画面必须协调一致，避免文字描述与视觉画面产生矛盾
- 对话气泡的位置和形状要符合阅读习惯和视觉流程
- 旁白和标注的放置要不干扰主要视觉焦点

### Visual Consistency

**Style Consistency (风格一致性)**:
- **统一风格**: 整本漫画的所有页面必须使用**同一种视觉风格**，不能混用不同风格
- **Prompt 一致性**: 每个页面的图像生成提示词必须包含完整的风格描述，确保风格参数一致
- **调色板统一**: 同一漫画的色彩基调（色调、饱和度、对比度）在所有页面保持一致
- **技法统一**: 线条风格、阴影处理、背景细节处理方式在所有页面保持一致

**Character Consistency (角色一致性)**:
- **固定特征**: 每个角色的外貌特征（发型、脸型、眼形、身高等）在所有页面必须完全一致
- **服装统一**: 同一角色在不同页面穿着的服装必须保持一致，除非剧情有明确变化（如换装场景）
- **表情范围**: 建立每个角色的表情范围表，确保不同页面的表情变化符合角色性格设定
- **标志性元素**: 每个角色的标志性道具或配饰（如特殊物品、首饰、武器等）必须始终出现

**Environment Consistency (环境一致性)**:
- **场景统一**: 同一地点或场景在不同页面出现时，背景元素、建筑细节、空间布局必须保持一致
- **时间一致性**: 同一场景的时间光影（早晨、中午、傍晚、夜间）必须符合剧情时间线
- **道具一致性**: 场景中出现的道具、家具、装饰等在不同页面出现时保持一致

**⚠️ CRITICAL: 参考图像控制（防止风格漂移的强制性措施）**

**问题根源**: 即使使用相同的提示词模板，AI 模型仍可能在不同生成中产生轻微风格变化。

**解决方案 - 三层参考图像系统**:

**第一层：风格参考图像**
- 在生成**第一页**时，生成一张风格参考图
- 该图应包含：典型场景、典型角色、完整展示该风格的所有视觉元素
- 保存为 `style-reference.png`
- 在生成后续所有页面时，**必须使用这张风格参考图作为参考**
- 在提示词中明确标注："Use this reference image as the ONLY visual style guide. Do not deviate from it."

**第二层：角色参考图像**
- `characters/characters.png` 包含所有角色的完整视觉定义
- 每个角色都有清晰的正面、侧面、表情展示
- 在生成任何包含角色的页面时，**必须使用角色参考图**
- 在提示词中明确标注："Characters must match EXACTLY the appearance in the reference image. Do not change any visual traits."

**第三层：场景参考图像**
- 如果有重复出现的场景（如办公室、教室等），生成该场景的参考图
- 保存为 `scene-reference-[scene-name].png`
- 在生成该场景的任何页面时，**必须使用场景参考图**
- 在提示词中明确标注："Environment must match EXACTLY the reference image. Keep all background details consistent."

**Consistency Enforcement Methods (一致性保证方法)**:

1. **Reference-Based Generation (基于参考图像的生成)**:
   - **强制性要求**: 所有后续页面生成时，必须同时传入风格参考图和角色参考图
   - 提示词结构（按优先级）：
     ```
     [STRICT STYLE REFERENCE - style-reference.png]
     "Visual style must MATCH EXACTLY the style-reference.png. Do not deviate."
     
     [CHARACTER REFERENCE - characters/characters.png]
     "Characters must match EXACTLY the reference image. Keep all visual traits identical."
     
     [Style Template - for additional guidance]
     [Character Reference Summary - for additional details]
     [Page-specific visual details from storyboard]
     ```
   - 如果图像生成工具不支持多图参考，按以下优先级：
     1. 风格参考图（最重要）
     2. 角色参考图（如果有角色）
     3. 场景参考图（如果有重复场景）

2. **Style Template (风格模板)**:
   - 为确定的风格创建风格描述模板，包含：
     * 整体视觉风格关键词（如 "Japanese manga style, clean lines, vibrant colors"）
     * 线条风格描述（如 "thin crisp outlines"）
     * 色彩基调描述（如 "warm pastel palette, balanced saturation"）
     * 阴影处理方式（如 "soft shading, moderate contrast"）
   - 每个页面的提示词必须包含完整的风格模板描述

3. **Prompt Consistency Check (提示词一致性检查)**:
   - 每个页面的图像生成提示词必须包含：
     * 确认的完整风格描述（从风格模板复制）
     * 所有出场角色的完整特征描述（从 characters.md 复制）
     * 确认的宽高比参数
   - 禁止省略或简化任何风格或角色特征描述

4. **Batch Generation (批量生成)**:
   - 如果图像生成工具支持，使用同一 session ID 批量生成所有页面
   - 确保所有图像使用相同的风格参数

5. **第一页作为风格锚点**:
   - 第一页生成后，仔细检查风格是否符合预期
   - 如果满意，将该页面的图像文件作为 `style-reference.png`
   - 如果不满意，重新生成直到风格完美符合预期

## Workflow

### Step 1: Analyze Content → `analysis.md`

Read source content, save it if needed, and perform deep analysis.

__Actions__:

1. __Save source content__ (if not already a file):
   - If user provides a file path: use as-is
   - If user pastes content: save to `source.md` in target directory
2. Read source content
3. __Deep analysis__ following `references/analysis-framework.md`:
   - Target audience identification
   - Value proposition for readers
   - Core themes and narrative potential
   - Key figures and their story arcs
4. Detect source language
5. Determine recommended page count:
   - Short story: 5-8 pages
   - Medium complexity: 9-15 pages
   - Full biography: 16-25 pages
6. Analyze content signals for style/layout recommendations
7. __Save to `analysis.md`__

__analysis.md Format__:

```yaml
---
title: "Alan Turing: Father of Computing"
topic: Biography
time_span: 1912-1954
source_language: en
user_language: zh
aspect_ratio: "3:4"
recommended_page_count: 12
---

## Target Audience

- **Primary**: Tech enthusiasts curious about computing history
- **Secondary**: Students learning about scientific breakthroughs
- **Tertiary**: General readers interested in biographical stories

## Value Proposition

What readers will gain:
1. Understanding of how modern computing was born
2. Emotional connection to a brilliant but tragic figure
3. Appreciation for the human cost of innovation

## Core Themes

| Theme | Narrative Potential | Visual Opportunity |
|-------|--------------------|--------------------|
| Genius vs. Society | High conflict, dramatic arcs | Contrast scenes |
| Code-breaking | Mystery, tension | Technical diagrams as art |
| Personal tragedy | Emotional depth | Intimate, somber panels |

## Key Figures & Story Arcs

### Alan Turing (Protagonist)
- **Arc**: Misunderstood genius → War hero → Tragic end
- **Visual identity**: Disheveled academic, intense eyes
- **Key moments**: Enigma breakthrough, arrest, final days

### Christopher Morcom (Catalyst)
- **Role**: Early friend whose death shaped Turing
- **Visual identity**: Youthful, bright
- **Key moments**: School friendship, sudden death

## Content Signals

- "biography" → classic + mixed
- "computing history" → ohmsha + dense
- "personal tragedy" → dramatic + splash

## Recommended Approaches

1. **Chronological** - follow life timeline (recommended for biography)
2. **Thematic** - organize by contributions (good for educational focus)
3. **Character-focused** - relationships drive narrative (good for emotional impact)
```

### Step 2: Generate 3 Storyboard Variants

Create three distinct variants, each combining a narrative approach with a recommended style.

| Variant | Narrative Approach | Recommended Style | Layout |
| --- | --- | | --- |
| A | Chronological | sepia | cinematic |
| B | Thematic | ohmsha | dense |
| C | Character-focused | warm | standard |

__For each variant__:

1. __Generate storyboard__ (`storyboard-{approach}.md`):

   - YAML front matter with narrative_approach, recommended_style, recommended_layout, aspect_ratio
   - Cover design
   - Each page: layout, panel breakdown, visual prompts
   - **文字语言**: 默认使用简体中文（除非用户明确指定其他语言）
   - **逻辑检查**: 确保每个情节转折都有合理的因果关系，人物动机明确，时间线连贯
   - **文字质量**: 避免错别字、畸形字，确保所有对话和旁白清晰准确
   - Reference: `references/storyboard-template.md`
2. __Generate matching characters__ (`characters-{approach}/`):

   - `characters.md` - visual specs matching the recommended style (in user's preferred language)
   - `characters.png` - character reference sheet
   - Reference: `references/character-template.md`

__All variants are preserved after selection for reference.__

### Step 3: User Confirms All Options

__IMPORTANT__: Present ALL options in a single confirmation step using AskUserQuestion. Do NOT interrupt workflow with multiple separate confirmations.

__Determine which questions to ask__:

| Question | When to Ask |
| --- | --- |
| Storyboard variant | Always (required) |
| Visual style | Always (required) |
| Language | Only if `source_language ≠ user_language` |
| Aspect ratio | Only if user might prefer non-default (e.g., landscape content) |

__Language handling__:

- **默认语言**: 如果用户没有特别指定，漫画中的所有文字（对话、旁白、标注）默认使用**简体中文**
- If source language = user language: Just inform user (e.g., "Comic will be in Chinese")
- If different: Ask which language to use

__All storyboards and prompts are generated in the user's selected/preferred language.__

__Aspect ratio handling__:

- Default: 3:4 (portrait) - standard comic format
- Offer 4:3 (landscape) if content suits it (e.g., panoramic scenes, technical diagrams)
- Offer 16:9 (widescreen) for cinematic content

__AskUserQuestion format__ (example with all questions):

```
Question 1 (Storyboard): Which storyboard variant?
- A: Chronological + sepia (Recommended)
- B: Thematic + ohmsha
- C: Character-focused + warm
- Custom

Question 2 (Style): Which visual style?
- sepia (Recommended from variant)
- classic / dramatic / warm / sepia / vibrant / ohmsha / realistic / wuxia
- Custom description

Question 3 (Language) - only if mismatch:
- Chinese (source material language)
- English (your preference)

Question 4 (Aspect) - only if relevant:
- 3:4 Portrait (Recommended)
- 4:3 Landscape
- 16:9 Widescreen
```

__After confirmation__:

1. Copy selected storyboard → `storyboard.md`
2. Copy selected characters → `characters/`
3. Update YAML front matter with confirmed style, language, aspect_ratio
4. If style differs from variant's recommended: regenerate `characters/characters.png`
5. User may edit files directly for fine-tuning

### Step 4: Generate Images

With confirmed storyboard + style + aspect ratio:

**PRE-REQUISITE CONSISTENCY SETUP (一致性预设置)**:

1. **Create Style Template**: 为确认的风格创建标准化的风格描述模板
   ```markdown
   Style Template for [style-name]:
   - Overall style: [complete description]
   - Line work: [description]
   - Color palette: [description]
   - Shading: [description]
   - Background treatment: [description]
   ```

2. **Prepare Character Reference Summary**: 从 `characters/characters.md` 提取每个角色的关键特征摘要
   ```markdown
   Character: [Name]
   - Appearance: [complete visual traits]
   - Clothing: [detailed description]
   - Expression range: [key expressions]
   - Props/Accessories: [list]
   ```

**GENERATION PROCESS (生成流程)**:

**Phase 1: Generate First Page & Establish Style Reference**

1. **Generate the cover or first page** using the comprehensive prompt structure
2. **CRITICAL QUALITY CHECK**: 仔细检查第一页的风格是否完全符合预期
3. **Save as Style Reference**:
   - 如果满意：将第一页图像复制并重命名为 `style-reference.png`
   - 如果不满意：**必须重新生成**，直到风格完美符合预期
   - `style-reference.png` 将作为所有后续页面的**唯一风格权威参考**

**Phase 2: Batch Generate Remaining Pages (All Must Use Reference Images)**

__For each remaining page__:

1. **Read page content from storyboard.md**
2. **Construct comprehensive prompt** using following structure (按优先级排列):

   ```
   [HIGHEST PRIORITY - STYLE REFERENCE]
   "Use style-reference.png as the EXACT visual style guide."
   "Do NOT deviate from the style in this reference image."
   "All visual elements must match this reference EXACTLY."
   
   [HIGH PRIORITY - CHARACTER REFERENCE]
   "Use characters/characters.png as the EXACT character appearance guide."
   "Do NOT change any character's visual traits, clothing, or features."
   "Characters must look IDENTICAL to the reference image."
   
   [MEDIUM PRIORITY - STYLE TEMPLATE]
   [完整复制 Style Template 的所有内容]
   
   [MEDIUM PRIORITY - CHARACTER SUMMARY]
   [Page-specific Character Reference Summary - For All Characters in This Page]
   
   [LOW PRIORITY - PAGE DETAILS]
   [Page-specific visual details from storyboard]
   Panel layout: [from storyboard]
   Aspect ratio: [confirmed aspect_ratio]
   Language: [confirmed language - for any text in image]
   ```

3. **CRITICAL: 必须传入参考图像**:
   - 如果图像生成工具支持多图参考：同时传入 `style-reference.png` 和 `characters/characters.png`
   - 如果仅支持单图参考：
     * 优先级1：`style-reference.png`（如果本页有场景或背景）
     * 优先级2：`characters/characters.png`（如果本页主要是角色特写）
     * 优先级3：如果有重复场景，使用对应的 `scene-reference-[name].png`

4. Save prompt to `prompts/NN-{cover|page}-[slug].md` (in user's preferred language)
5. Generate image using confirmed style and aspect ratio
6. **IMMEDIATE CONSISTENCY CHECK**: 生成后立即与 `style-reference.png` 对比
   - 检查：色调是否一致？
   - 检查：线条风格是否一致？
   - 检查：阴影处理是否一致？
   - 检查：角色是否与 `characters/characters.png` 一致？
   - 如有任何不一致：**立即重新生成该页面**（不要等待）

7. Report progress after each generation

__Image Generation Skill Selection__:

- Check available image generation skills
- If multiple skills available, ask user preference

__Character Reference Handling__:

- **强制性要求**: 所有页面生成时，**必须**使用 `characters/characters.png` 作为角色参考
- 如果图像生成工具支持 reference image 参数：**必须传入** `characters/characters.png`
- 如果图像生成工具支持多图参考：同时传入 `style-reference.png` 和 `characters/characters.png`
- 如果工具不支持参考图像：将 `characters/characters.md` 的完整内容作为提示词的第一部分（优先级最高）

__Session Management__:
If image generation skill supports `--sessionId`:

1. Generate unique session ID: `comic-{topic-slug}-{timestamp}`
2. Use same session ID for all pages
3. Ensures visual consistency across generated images
4. **注意**: Session ID 的一致性不能替代参考图像的使用，**两者必须同时使用**

**QUALITY CONTROL (质量控制)**:

- 每生成一页后，**立即执行一致性检查**（不要等待所有页面生成完）：
  1. 与 `style-reference.png` 对比：色调、线条、阴影是否一致
  2. 与 `characters/characters.png` 对比：角色外貌、服装是否一致
  3. 与上一页对比：整体风格是否连贯
- **自动重新生成机制**:
  - 如发现任何不一致：**立即重新生成该页面**
  - 最多允许重新生成 3 次
  - 如 3 次后仍不一致：暂停并报告用户，询问是否调整参考图像或风格描述
- 记录每页使用的提示词到 `prompts/` 目录，便于追溯和调整
- 保存所有生成的版本（包括被拒绝的），命名格式：`NN-page-[slug]-attempt-[N].png`

### Step 5: Merge to PDF

After all images generated:

```bash
npx -y bun ${SKILL_DIR}/scripts/merge-to-pdf.ts <comic-dir>
```

Creates `{topic-slug}.pdf` with all pages as full-page images.

### Step 6: Completion Report

```
Comic Complete!
Title: [title] | Style: [style] | Pages: [count] | Aspect: [ratio] | Language: [lang]
Location: [path]
✓ analysis.md
✓ characters.png
✓ 00-cover-[slug].png ... NN-page-[slug].png
✓ {topic-slug}.pdf
```

## Page Modification

Support for modifying individual pages after initial generation.

### Edit Single Page

Regenerate a specific page with modified prompt:

1. Identify page to edit (e.g., `03-page-enigma-machine.png`)
2. Update prompt in `prompts/03-page-enigma-machine.md` if needed
3. If content changes significantly, update slug in filename
4. Regenerate image using same session ID and aspect ratio
5. Regenerate PDF

### Add New Page

Insert a new page at specified position:

1. Specify insertion position (e.g., after page 3)
2. Create new prompt with appropriate slug (e.g., `04-page-bletchley-park.md`)
3. Generate new page image (same aspect ratio)
4. __Renumber files__: All subsequent pages increment NN by 1
   - `04-page-tragedy.png` → `05-page-tragedy.png`
   - Slugs remain unchanged
5. Update `storyboard.md` with new page entry
6. Regenerate PDF

### Delete Page

Remove a page and renumber:

1. Identify page to delete (e.g., `03-page-enigma-machine.png`)
2. Remove image file and prompt file
3. __Renumber files__: All subsequent pages decrement NN by 1
   - `04-page-tragedy.png` → `03-page-tragedy.png`
   - Slugs remain unchanged
4. Update `storyboard.md` to remove page entry
5. Regenerate PDF

### File Naming Convention

Files use meaningful slugs for better readability:

```
NN-cover-[slug].png / NN-page-[slug].png
NN-cover-[slug].md / NN-page-[slug].md (in prompts/)
```

Examples:

- `00-cover-turing-story.png`
- `01-page-early-life.png`
- `02-page-cambridge-years.png`
- `03-page-enigma-machine.png`

__Slug rules__:

- Derived from page title/content (kebab-case)
- Must be unique within the comic
- When page content changes significantly, update slug accordingly

__Renumbering__:

- After add/delete, update NN prefix for affected pages
- Slug remains unchanged unless content changes
- Maintain sequential numbering with no gaps

## Style-Specific Guidelines

### Ohmsha Style (`--style ohmsha`)

Additional requirements for educational manga:

- __Default: Use Doraemon characters directly__ - No need to create new characters
  - 大雄 (Nobita): Student role, curious learner
  - 哆啦A梦 (Doraemon): Mentor role, explains concepts with gadgets
  - 胖虎 (Gian): Antagonist/challenge role, represents obstacles or misconceptions
  - 静香 (Shizuka): Supporting role, asks clarifying questions
- Custom characters only if explicitly requested: `--characters "Student:小明,Mentor:教授"`
- Must use visual metaphors (gadgets, action scenes) - NO talking heads
- Page titles: narrative style, not "Page X: Topic"

__Reference__: `references/ohmsha-guide.md` for detailed guidelines.

## References

Detailed templates and guidelines in `references/` directory:

- `analysis-framework.md` - Deep content analysis for comic adaptation
- `character-template.md` - Character definition format and examples
- `storyboard-template.md` - Storyboard structure and panel breakdown
- `ohmsha-guide.md` - Ohmsha manga style specifics
- `styles/` - Detailed style definitions
- `layouts/` - Detailed layout definitions

## Extension Support

Custom styles and configurations via EXTEND.md.

__Check paths__ (priority order):

1. `.baoyu-skills/baoyu-comic/EXTEND.md` (project)
2. `~/.baoyu-skills/baoyu-comic/EXTEND.md` (user)

If found, load before Step 1. Extension content overrides defaults.
