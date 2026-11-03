---
name: html-presentation-generator
description: "Generate professional multi-page HTML presentations (PPT). Creates slide decks with cover, TOC, section dividers, content pages, and summary slides. Supports export to PDF/PPTX. TRIGGERS: PPT, 演示文稿, presentation, HTML slides, 幻灯片, slide deck, 汇报, 报告."
---

# HTML Presentation Generator

## Overview

You are an expert at generating complete multi-page HTML presentations. Each slide is a standalone HTML file rendered at 960×540px. You handle the full pipeline: research → color/font selection → outline planning → slide-by-slide generation (with image generation and visual verification) → final deployment. All slides are static HTML suitable for browser viewing and PPTX export.

## Workflow

Follow these steps in order for every presentation:

### Step 1 — Research (if needed)

If you lack domain knowledge about the user's topic, perform deep research first:
- Search the web for key facts, data, and context
- Validate information from multiple sources
- Organize findings to inform slide content

### Step 2 — Choose Color Palette & Font

Select a color palette from the **Color Palette Reference** section below based on the topic and audience. The font is fixed:

> **⚠️ MANDATORY FONT**: All presentations use `Times New Roman` for both Chinese and English text.
> `font-family: 'Times New Roman', serif;`

### Step 3 — Plan the Outline

Using the **Slide Page Types** section below, create a complete slide outline:
1. Classify every slide as exactly one of the 5 page types
2. For content pages, assign a content subtype
3. Ensure variety in layouts across slides
4. Typical structure: Cover → TOC → [Section Divider → Content Pages...] → Summary

### Step 4 — Generate Slides

Generate each slide as an individual HTML file. Process up to 5 slides concurrently (not more).

For **each slide**, follow the page-type-specific workflow below. Every slide must:
1. Be saved as `slides/slide-01.html`, `slides/slide-02.html`, etc. (zero-padded two digits)
2. Store any generated images in `slides/imgs/`
3. Use the exact 960×540 `.slide-content` dimensions
4. Use `Times New Roman` font for all text (Chinese and English)
5. After writing HTML, take a screenshot using `get_html_presentation_screenshot` and verify with `images_understand` — check for layout correctness, no text overlaps, no misplaced elements, and page number badge presence (except cover). Fix any issues before moving on.

### Step 5 — Deploy

Use the `deploy_html_presentation` tool to merge all slides and deploy the final presentation.

---

## Slide Page Types

Classify **every slide** as exactly one of these 5 types. This prevents layout drift and keeps the deck consistent.

### Type 1: Cover Page

**Use for**: Opening slide, tone setting.

**Content elements**:
- Main Title (72–120px, bold, commanding — the visual anchor)
- Subtitle (28–40px, clearly secondary)
- Supporting text / presenter / date (18–24px, subtle)
- Meta info (14–18px)
- Background image or strong visual motif

**Font size hierarchy**:

| Element | Size | Notes |
|---------|------|-------|
| Main Title | 72–120px | Bold, 3–5× base |
| Subtitle | 28–40px | 1.5–2× base |
| Supporting Text | 18–24px | Base |
| Meta Info | 14–18px | 0.7–1× base |

**Layout options**:

1. **Asymmetric Left-Right** — Text on one side, image on the other
   ```
   |  Title & Subtitle  |    Visual/Image    |
   |  Description       |                    |
   ```
2. **Center-Aligned** — Content centered over background image
   ```
   |           [Background Image]           |
   |              MAIN TITLE                |
   |              Subtitle                  |
   ```

**Design decisions**: Purpose (corporate/creative/educational)? Audience? Tone? Content volume?

**Image generation**: **MANDATORY**. You MUST call `GenerateImage` to create at least one image for the cover. Do NOT proceed to HTML until you have a valid image path.

**Workflow**:
1. Analyze topic, audience, purpose
2. Generate image (MANDATORY) — wait for file path
3. Choose layout
4. Write HTML (embed actual image path, never a placeholder)
5. Screenshot + verify

**No page number badge on cover page.**

---

### Type 2: Table of Contents

**Use for**: Navigation, expectation setting (3–5 sections).

**Content elements**:
- Page title ("Table of Contents" / "Agenda" / "Overview")
- Section numbers (01, 02… or I, II…)
- Section titles
- Optional one-line descriptions
- **Page number badge (MANDATORY)** — see Appendix G

**Font size hierarchy**:

| Element | Size |
|---------|------|
| Page Title | 36–44px |
| Section Number | 28–36px |
| Section Title | 20–28px |
| Description | 14–16px |

**Layout options**:

1. **Numbered Vertical List** — Clean left-aligned structure
   ```
   |  TABLE OF CONTENTS            |
   |  01  Section Title One         |
   |  02  Section Title Two         |
   ```
2. **Two-Column Grid** — 2×N grid with numbers + titles
3. **Sidebar Navigation** — Colored sidebar with section markers
4. **Card-Based** — Section cards in a row/grid

**Image generation**: OPTIONAL — most TOC slides work best with clean typography + SVG decorations.

**Workflow**:
1. Analyze section list and count
2. Choose layout (3 sections → vertical; 4–6 → grid/compact; 7+ → multi-column)
3. Plan visual hierarchy
4. Generate image (optional)
5. Write HTML with page number badge
6. Screenshot + verify

---

### Type 3: Section Divider

**Use for**: Clear transitions between major parts.

**Content elements**:
- Section number (72–120px, bold, accent color — the dominant element)
- Section title (36–48px, bold, primary color)
- Optional intro text (16–20px, light, muted)
- SVG accent shapes (bars, lines, geometric blocks)
- **Page number badge (MANDATORY)** — see Appendix G

**Layout options**:

1. **Bold Center** — Number + title centered
2. **Left-Aligned with Accent Block** — Colored bar on left
3. **Split Background** — Two color zones
4. **Full-Bleed Background with Overlay** — Strong bg color, semi-transparent number

**Design decisions**: Corporate → accent block; Creative → full-bleed; Minimal → bold center. Divider style must be consistent across all dividers in one deck.

**Image generation**: OPTIONAL — most dividers work best with bold typography + solid colors + SVG accents.

**Workflow**:
1. Analyze section number, title, intro
2. Choose layout
3. Generate image (optional)
4. Write HTML with page number badge
5. Screenshot + verify

---

### Type 4: Content Page

**Use for**: The core information slides. Each content page belongs to exactly ONE subtype.

**Content subtypes**:

#### 4a. Text
- Bullets, quotes, short paragraphs
- Must include icons or SVG shapes — never plain text only
```
|  SLIDE TITLE                          |
|  • Bullet point one                   |
|  • Bullet point two                   |
|  • Bullet point three                 |
```

#### 4b. Mixed Media
- Two-column: image on one side, text on the other
```
|  SLIDE TITLE                          |
|  Text content     |  [Image/Visual]   |
|  and bullets      |                   |
```

#### 4c. Data Visualization
- SVG chart (bar/progress/ring) + 1–3 key takeaways + data source
```
|  SLIDE TITLE                          |
|  [SVG Chart]      |  Key Takeaway 1   |
|                   |  Key Takeaway 2   |
|                   Source: xxx          |
```

#### 4d. Comparison
- Side-by-side columns/cards (A vs B, pros/cons)
```
|  SLIDE TITLE                          |
|  ┌─ Option A ─┐  ┌─ Option B ─┐      |
|  │  Detail 1  │  │  Detail 1  │      |
|  └────────────┘  └────────────┘      |
```

#### 4e. Timeline / Process
- Steps with arrows, numbered connectors
```
|  SLIDE TITLE                          |
|  [1] ──→ [2] ──→ [3] ──→ [4]         |
|  Step    Step    Step    Step          |
```

#### 4f. Image Showcase
- Hero image as primary element, text supporting
```
|  SLIDE TITLE                          |
|  ┌────────────────────────────────┐   |
|  │         [Hero Image]           │   |
|  └────────────────────────────────┘   |
|  Caption or supporting text           |
```

**Font size hierarchy**:

| Element | Size | Notes |
|---------|------|-------|
| Slide Title | 36–44px | Bold, top of slide |
| Section Header | 20–24px | Bold, sub-sections |
| Body Text | 14–16px | Regular weight, LEFT-ALIGNED |
| Captions / Source | 10–12px | Muted color |
| Stat Callout | 60–72px | Large bold numbers |

**Content elements (all content pages)**:
1. Slide Title — always required, top of slide
2. Body Content — based on subtype
3. Visual Element — image, chart, icon, or SVG shape — ALWAYS required
4. Source / Caption — include when showing data
5. **Page number badge (MANDATORY)** — see Appendix G

**Key principles**:
- Left-align body text — never center paragraphs or bullet lists
- Title must be 36pt+ for contrast with 14–16pt body
- 0.5″ minimum margins, 0.3–0.5″ between content blocks
- Each content slide should use a different layout from the previous one

**Image generation**: **MANDATORY**. Call `GenerateImage` for every content page:
- Mixed Media / Image Showcase → hero image
- Text / Data / Comparison / Timeline → supporting illustration or thematic element

**Workflow**:
1. Analyze content, determine subtype
2. Generate image (MANDATORY) — wait for file path
3. Choose layout variant for the subtype
4. Write HTML with page number badge
5. Screenshot + verify (layout matches subtype, no overlaps, badge present)

---

### Type 5: Summary / Closing Page

**Use for**: Wrap-up, action items, thank-you.

**Content elements**:
- Closing title (48–72px, bold)
- Takeaway points (18–24px, scannable)
- Call to action / next steps
- Contact info (14–16px, muted)
- **Page number badge (MANDATORY)** — see Appendix G

**Layout options**:

1. **Key Takeaways** — 3–5 points with icons/check marks
2. **CTA / Next Steps** — Action items + contact info
3. **Thank You / Contact** — Centered thank-you + contact details
4. **Split Recap** — Left: takeaways; Right: CTA/contact

**Image generation**: OPTIONAL — most summary slides work best with clean typography + SVG accents.

**Workflow**:
1. Analyze closing content type
2. Choose layout
3. Generate image (optional)
4. Write HTML with page number badge
5. Screenshot + verify

---

## Color Palette Reference

Select ONE palette for the entire presentation based on topic and audience.

| # | 名称 | 色值 | 风格 | 适用场景 | 建议 |
|---|------|------|------|----------|------|
| 1 | 现代与健康 | `#006d77` `#83c5be` `#edf6f9` `#ffddd2` `#e29578` | 清新、治愈 | 医疗健康、心理咨询、护肤品、瑜伽Spa | 深青做标题，浅粉做背景 |
| 2 | 商务与权威 | `#2b2d42` `#8d99ae` `#edf2f4` `#ef233c` `#d90429` | 严谨、经典 | 年度汇报、金融分析、企业介绍、政务报告 | 深蓝显专业，亮红强调数据 |
| 3 | 自然与户外 | `#606c38` `#283618` `#fefae0` `#dda15e` `#bc6c25` | 沉稳、大地色 | 户外用品、环境保护、农业项目、历史文化 | 深绿为底，米色为字 |
| 4 | 复古与学院 | `#780000` `#c1121f` `#fdf0d5` `#003049` `#669bbc` | 经典、书卷气 | 学术讲座、历史回顾、博物馆、复古品牌 | 深红与深蓝对比强烈 |
| 5 | 柔美与创意 | `#cdb4db` `#ffc8dd` `#ffafcc` `#bde0fe` `#a2d2ff` | 梦幻、糖果色 | 母婴产品、甜品店、女性时尚、幼儿园 | 文字用深灰或黑色 |
| 6 | 波西米亚 | `#ccd5ae` `#e9edc9` `#fefae0` `#faedcd` `#d4a373` | 温柔、低饱和 | 婚礼策划、家居软装、有机食品、慢生活 | 米色背景，绿棕点缀 |
| 7 | 活力与科技 | `#8ecae6` `#219ebc` `#023047` `#ffb703` `#fb8500` | 高能量、运动 | 体育赛事、健身房、创业路演、少儿教育 | 深蓝稳重心，橙色做焦点 |
| 8 | 匠心与手作 | `#7f5539` `#a68a64` `#ede0d4` `#656d4a` `#414833` | 质朴、咖啡调 | 咖啡店、手工艺品、传统文化、烘焙教学 | 适合纸质/皮革质感 |
| 9 | 科技与夜景 | `#000814` `#001d3d` `#003566` `#ffc300` `#ffd60a` | 深邃、高亮 | 科技发布会、星空天文、夜间经济、高端汽车 | 必须用深色模式 |
| 10 | 教育与图表 | `#264653` `#2a9d8f` `#e9c46a` `#f4a261` `#e76f51` | 清晰、逻辑强 | 统计报告、教育培训、市场分析、通用商务 | 完美的图表配色 |
| 11 | 森林与环保 | `#dad7cd` `#a3b18a` `#588157` `#3a5a40` `#344e41` | 单色渐变、森系 | 园林设计、ESG报告、环保公益、植物研究 | 单色系安全不会乱 |
| 12 | 优雅与时尚 | `#edafb8` `#f7e1d7` `#dedbd2` `#b0c4b1` `#4a5759` | 低饱和、莫兰迪 | 高定服装、艺术画廊、美妆品牌、杂志风 | 留白是关键 |
| 13 | 艺术与美食 | `#335c67` `#fff3b0` `#e09f3e` `#9e2a2b` `#540b0e` | 浓郁、复古画报 | 美食纪录片、艺术展、民族风情、复古餐厅 | 适合大色块拼接 |
| 14 | 轻奢与神秘 | `#22223b` `#4a4e69` `#9a8c98` `#c9ada7` `#f2e9e4` | 冷艳、紫调 | 珠宝展示、酒店管理、高端咨询、心理学 | 紫色营造高端氛围 |
| 15 | 纯净科技蓝 | `#03045e` `#0077b6` `#00b4d8` `#90e0ef` `#caf0f8` | 未来感、纯净 | 云计算/AI、水利海洋、医院医疗、洁净能源 | 从深海到天空的渐变 |
| 16 | 海岸珊瑚 | `#0081a7` `#00afb9` `#fdfcdc` `#fed9b7` `#f07167` | 清爽、夏日感 | 旅游度假、夏季活动、饮品品牌、海洋主题 | 青色与珊瑚色互补亮眼 |
| 17 | 活力橙薄荷 | `#ff9f1c` `#ffbf69` `#ffffff` `#cbf3f0` `#2ec4b6` | 明亮、欢快 | 儿童活动、促销海报、快消品、社交媒体 | 橙色吸睛，薄荷绿清爽 |
| 18 | 铂金白金 | `#0a0a0a` `#0070F3` `#D4AF37` `#f5f5f5` `#ffffff` | 高端、专业 | Agent产品、企业官网、金融科技、高端品牌 | 白金主调，蓝色行动，金色强调 |

### Agent Design System — 完整色板

基于 tokens.css/ts 的 Platinum White-Gold Theme，提供完整色阶供精细设计使用。

#### White 白色系（背景与浅色表面）

| 色阶 | 色值 | 用途 |
|------|------|------|
| white-0 | `#ffffff` | 主背景 |
| white-50 | `#fefefe` | 略带暖调的白 |
| white-75 | `#fcfcfc` | 微灰白 |
| white-100 | `#fafafa` | 次级背景 |
| white-200 | `#f7f7f7` | 卡片背景 |
| white-300 | `#f5f5f5` | 三级背景 |
| white-400 | `#f0f0f0` | 分隔区域 |
| white-500 | `#ebebeb` | 边框浅色 |
| white-600 | `#e5e5e5` | 禁用态背景 |
| white-700 | `#e0e0e0` | 深灰白 |
| white-800 | `#d9d9d9` | 占位符 |
| white-900 | `#d4d4d4` | 分隔线 |
| white-1000 | `#cccccc` | 最深白 |

#### Gold 金色系（铂金商务强调色）

| 色阶 | 色值 | 用途 |
|------|------|------|
| gold-25 | `#FFFDF5` | 极浅金背景 |
| gold-50 | `#FEF9E7` | 浅金背景 |
| gold-75 | `#FCF3D0` | 淡金高亮 |
| gold-100 | `#FAECB8` | 金色 hover 态 |
| gold-200 | `#F5DC8A` | 亮金强调 |
| gold-300 | `#E8C860` | 金色悬停 |
| gold-400 | `#D4AF37` | **主金色（核心）** |
| gold-500 | `#B8972E` | 金色文字 |
| gold-600 | `#9A7E26` | 深金强调 |
| gold-700 | `#7C651E` | 暗金边框 |
| gold-800 | `#5E4C16` | 深金背景 |
| gold-900 | `#40330F` | 极深金 |
| gold-1000 | `#221A08` | 黑金 |

#### Blue 蓝色系（主操作色）

| 色阶 | 色值 | 用途 |
|------|------|------|
| blue-25 | `#F0F7FF` | 极浅蓝背景 |
| blue-50 | `#E0EFFF` | 信息提示背景 |
| blue-75 | `#C2DFFF` | 浅蓝高亮 |
| blue-100 | `#A3CFFF` | 禁用态蓝 |
| blue-200 | `#66AFFF` | 亮蓝 |
| blue-300 | `#338FFF` | 蓝色悬停 |
| blue-400 | `#0070F3` | **主蓝色（核心）** |
| blue-500 | `#005FCC` | 蓝色文字 |
| blue-600 | `#004FA6` | 深蓝强调 |
| blue-700 | `#003F80` | 暗蓝边框 |
| blue-800 | `#002F5A` | 深蓝背景 |
| blue-900 | `#001F3D` | 极深蓝 |
| blue-1000 | `#001026` | 黑蓝 |

#### Gray 灰色系（文字与中性色）

| 色阶 | 色值 | 用途 |
|------|------|------|
| gray-0 | `#ffffff` | 白色 |
| gray-50 | `#fafafa` | 极浅灰 |
| gray-75 | `#f5f5f5` | 浅灰背景 |
| gray-100 | `#ededed` | 分隔线浅 |
| gray-200 | `#d4d4d4` | 边框浅 |
| gray-300 | `#a3a3a3` | 四级文字 |
| gray-400 | `#737373` | 三级文字 |
| gray-500 | `#525252` | 二级文字 |
| gray-600 | `#404040` | 深灰 |
| gray-700 | `#2e2e2e` | 暗色背景 |
| gray-800 | `#1f1f1f` | 深色背景 |
| gray-900 | `#141414` | 极深背景 |
| gray-1000 | `#0a0a0a` | **主文字色（核心）** |

#### 透明度色值

**Opacity Black（黑色透明）**

| 透明度 | 色值 | 用途 |
|--------|------|------|
| 0% | `#0a0a0a00` | 全透明 |
| 2% | `#0a0a0a05` | 微弱遮罩 |
| 4% | `#0a0a0a0a` | 次级交互背景 |
| 8% | `#0a0a0a14` | 边框/分隔 |
| 15% | `#0a0a0a26` | 按压态 |
| 20% | `#0a0a0a33` | 浅遮罩 |
| 25% | `#0a0a0a40` | 中遮罩 |
| 50% | `#0a0a0a80` | 半透明 |
| 70% | `#0a0a0ab2` | 深遮罩 |
| 80% | `#0a0a0acc` | 悬停态 |
| 90% | `#0a0a0ae5` | tooltip |
| 95% | `#0a0a0af2` | 弹窗 |

**Opacity White（白色透明）**

| 透明度 | 色值 | 用途 |
|--------|------|------|
| 0% | `#ffffff00` | 全透明 |
| 2% | `#ffffff05` | 微弱遮罩 |
| 4% | `#ffffff0a` | 次级交互背景 |
| 8% | `#ffffff12` | 边框/分隔 |
| 15% | `#ffffff26` | 按压态 |
| 20% | `#ffffff33` | 浅遮罩 |
| 25% | `#ffffff40` | 中遮罩 |
| 50% | `#ffffff80` | 半透明 |
| 70% | `#ffffffb2` | 深遮罩 |
| 80% | `#ffffffcc` | 悬停态 |
| 90% | `#ffffffe5` | tooltip |
| 95% | `#fffffff2` | 弹窗 |

---

## Design Style System

同一套设计可通过调整圆角（radius）和间距（spacing）呈现4种不同风格。根据场景选择合适的风格配方。

### 风格概览

| 风格 | 圆角范围 | 间距范围 | 适合场景 |
|---|---|---|---|
| **Sharp & Compact** | radius-4 ~ radius-6 | spacing-4 ~ spacing-12 | 数据密集型后台、表格、IDE、代码编辑器 |
| **Soft & Balanced** | radius-8 ~ radius-12 | spacing-8 ~ spacing-16 | 企业 SaaS、管理面板、通用 Web App |
| **Rounded & Spacious** | radius-16 ~ radius-24 | spacing-16 ~ spacing-32 | 消费级产品、营销页、社交应用 |
| **Pill & Airy** | radius-32 ~ radius-full | spacing-20 ~ spacing-48 | 移动端 Web、着陆页、品牌展示 |

### Sharp & Compact（锐利紧凑）

**视觉特征**: 方正、信息密度高、专业严肃感。

| 类别 | Token | 值 |
|---|---|---|
| 圆角-小 | --component-radius-sm | 4px |
| 圆角-中 | --component-radius-md | 4px |
| 圆角-大 | --component-radius-lg | 6px |
| 内间距-小 | --component-padding-sm | 4px |
| 内间距-中 | --component-padding-md | 8px |
| 内间距-大 | --component-padding-lg | 12px |
| 间隔-小 | --component-gap-sm | 4px |
| 间隔-中 | --component-gap-md | 8px |
| 间隔-大 | --component-gap-lg | 16px |
| 页面边距 | --page-margin | 16px |
| 区块间距 | --section-gap | 24px |

### Soft & Balanced（柔和均衡）

**视觉特征**: 适中的圆角、舒适的留白、专业又不失亲和。

| 类别 | Token | 值 |
|---|---|---|
| 圆角-小 | --component-radius-sm | 6px |
| 圆角-中 | --component-radius-md | 8px |
| 圆角-大 | --component-radius-lg | 12px |
| 内间距-小 | --component-padding-sm | 8px |
| 内间距-中 | --component-padding-md | 12px |
| 内间距-大 | --component-padding-lg | 16px |
| 间隔-小 | --component-gap-sm | 6px |
| 间隔-中 | --component-gap-md | 12px |
| 间隔-大 | --component-gap-lg | 24px |
| 页面边距 | --page-margin | 24px |
| 区块间距 | --section-gap | 32px |

### Rounded & Spacious（圆润宽松）

**视觉特征**: 大圆角、充裕留白、友好亲切、现代消费级感。

| 类别 | Token | 值 |
|---|---|---|
| 圆角-小 | --component-radius-sm | 10px |
| 圆角-中 | --component-radius-md | 16px |
| 圆角-大 | --component-radius-lg | 24px |
| 内间距-小 | --component-padding-sm | 12px |
| 内间距-中 | --component-padding-md | 20px |
| 内间距-大 | --component-padding-lg | 32px |
| 间隔-小 | --component-gap-sm | 10px |
| 间隔-中 | --component-gap-md | 16px |
| 间隔-大 | --component-gap-lg | 32px |
| 页面边距 | --page-margin | 32px |
| 区块间距 | --section-gap | 48px |

### Pill & Airy（胶囊通透）

**视觉特征**: 全圆角胶囊形、大量留白、轻盈通透、品牌展示感强。

| 类别 | Token | 值 |
|---|---|---|
| 圆角-小 | --component-radius-sm | 20px |
| 圆角-中 | --component-radius-md | 32px |
| 圆角-大 | --component-radius-lg | 999px (full) |
| 内间距-小 | --component-padding-sm | 12px |
| 内间距-中 | --component-padding-md | 24px |
| 内间距-大 | --component-padding-lg | 40px |
| 间隔-小 | --component-gap-sm | 12px |
| 间隔-中 | --component-gap-md | 24px |
| 间隔-大 | --component-gap-lg | 48px |
| 页面边距 | --page-margin | 40px |
| 区块间距 | --section-gap | 64px |

### 组件级风格映射表

| 组件 | Sharp | Soft | Rounded | Pill |
|---|---|---|---|---|
| **按钮** | radius-4, padding 8×16 | radius-6, padding 8×16 | radius-10, padding 12×20 | radius-full, padding 12×32 |
| **输入框** | radius-4, padding 8×12 | radius-6, padding 8×12 | radius-10, padding 10×16 | radius-full, padding 10×20 |
| **卡片** | radius-4, padding 8~12 | radius-8, padding 12~16 | radius-16, padding 20 | radius-24, padding 24~32 |
| **模态框** | radius-6, padding 16 | radius-12, padding 20 | radius-20, padding 24~32 | radius-32, padding 32~40 |
| **标签/Badge** | radius-4, padding 2×6 | radius-4, padding 2×8 | radius-6, padding 4×10 | radius-full, padding 4×12 |
| **头像** | radius-4 | radius-8 | radius-12 | radius-full |
| **下拉菜单** | radius-4, padding 4 | radius-6, padding 4 | radius-12, padding 8 | radius-16, padding 8 |
| **Toast/Alert** | radius-4, padding 8×12 | radius-8, padding 12×16 | radius-12, padding 16×20 | radius-full, padding 12×24 |
| **Tooltip** | radius-4, padding 4×8 | radius-6, padding 6×10 | radius-8, padding 8×12 | radius-full, padding 6×16 |

### 混搭原则

同一页面可组合不同风格级别，但需遵循以下规则：

**1. 外层容器 ≥ 内层圆角**
```
正确：外 > 内
  .card     { border-radius: 16px; }
  .card img { border-radius: 12px; }

错误：内 > 外 → 视觉溢出感
  .card     { border-radius: 8px;  }
  .card img { border-radius: 16px; }
```

**2. 信息密度决定间距**

| 区域类型 | 推荐风格 |
|---|---|
| 内容浏览区 | Spacious / Airy（宽松间距） |
| 工具栏/侧边栏 | Compact / Balanced（紧凑间距） |
| 表单/数据区 | Balanced（适中间距） |

**3. 交互元素与容器保持同一风格**

**4. 圆角与尺寸的比例关系**

| 元素尺寸 | Sharp | Soft | Rounded | Pill |
|---|---|---|---|---|
| 小（< 32px） | 4px | 4px | 8px | full |
| 中（32~64px） | 4px | 6~8px | 12~16px | full |
| 大（64~200px） | 4~6px | 8~12px | 16~24px | 32px |
| 超大（> 200px） | 6px | 12px | 24px | 32px |

### 快速选择指南

| 项目类型 | 推荐风格 | 原因 |
|---|---|---|
| 企业后台/Dashboard | Sharp & Compact | 信息密度高，专业感强 |
| SaaS产品/Web App | Soft & Balanced | 平衡专业与友好 |
| 消费级App/社交 | Rounded & Spacious | 亲切感，现代感 |
| 着陆页/品牌展示 | Pill & Airy | 品牌调性强，视觉冲击 |
| 数据可视化 | Sharp / Soft | 清晰的边界和对齐 |
| 移动端H5 | Rounded / Pill | 触控友好，圆角更易点击 |

---

## HTML Implementation Rules

### Appendix A — Responsive Scaling Snippet (REQUIRED)

Every slide HTML file MUST include this in `<head>` and before `</body>`:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
}
.slide-content {
  width: 960px;
  height: 540px;
  position: relative;
  transform-origin: center center;
}
</style>
<script>
function scaleSlide() {
  const slide = document.querySelector('.slide-content');
  if (!slide) return;
  const slideWidth = 960;
  const slideHeight = 540;
  const scaleX = window.innerWidth / slideWidth;
  const scaleY = window.innerHeight / slideHeight;
  const scale = Math.min(scaleX, scaleY);
  slide.style.width = slideWidth + 'px';
  slide.style.height = slideHeight + 'px';
  slide.style.transform = `scale(${scale})`;
  slide.style.transformOrigin = 'center center';
  slide.style.flexShrink = '0';
}
window.addEventListener('load', scaleSlide);
window.addEventListener('resize', scaleSlide);
</script>
```

### Appendix B — CSS Rules (REQUIRED)

#### ⚠️ Inline-Only CSS

**All CSS styles MUST be inline (except the snippet in Appendix A).**

- Do NOT use `<style>` blocks outside Appendix A
- Do NOT use external stylesheets
- Do NOT use CSS classes or class-based styling

```html
<!-- ✅ Correct: Inline styles -->
<div style="position:absolute; left:60px; top:120px; width:840px; height:240px; background:#023047;"></div>
<p style="position:absolute; left:60px; top:140px; font-size:28px; color:#ffffff;">Title</p>

<!-- ❌ Wrong: Style blocks or classes -->
<style>
  .card { background:#023047; }
</style>
<div class="card"></div>
```

#### ⚠️ Background on .slide-content Directly

**Do NOT create a full-size background DIV inside `.slide-content`. Set the background directly on `.slide-content` itself.**

```html
<!-- ✅ Correct: Background directly on .slide-content -->
<div class="slide-content" style="background:#023047;">
  <p style="position:absolute; left:60px; top:140px; ...">Title</p>
</div>

<!-- ❌ Wrong: Nested full-size background DIV -->
<div class="slide-content">
  <div style="position:absolute; left:0; top:0; width:960px; height:540px; background:#023047;"></div>
  <p style="position:absolute; left:60px; top:140px; ...">Title</p>
</div>
```

#### ⚠️ No Bold for Body Text and Captions

- Body paragraphs, descriptions, and explanatory text → normal weight (400–500)
- Image captions, chart legends, footnotes → light-weight
- Reserve bold (`font-weight: 600+`) for titles, headings, and key emphasis only

### Appendix C — Color Palette Rules (REQUIRED)

#### ⚠️ Strict Color Palette Adherence

- All colors MUST come from the chosen palette
- Do NOT create or modify color values
- Do NOT use colors outside the palette
- **Only exception**: You may add opacity to palette colors (e.g., `rgba(r,g,b,0.1)`)

#### ⚠️ No Gradients Allowed

- No CSS `linear-gradient()`, `radial-gradient()`, `conic-gradient()`
- No SVG `<linearGradient>`, `<radialGradient>`
- All fills, backgrounds, borders → solid colors only

#### ⚠️ No Animations Allowed

- No CSS `animation`, `@keyframes`, or `transition`
- No JavaScript animations
- No hover effects with motion
- No SVG animations (`<animate>`, `<animateTransform>`, `<animateMotion>`)
- All slides are static presentation assets

**For visual hierarchy without gradients/animations:**
1. Use different colors from the palette
2. Use solid color + opacity overlay
3. Combine palette colors strategically

### Appendix D — SVG Conversion Constraints (CRITICAL)

The HTML-to-PPTX converter has STRICT SVG support limitations.

#### Supported SVG Elements (WHITELIST)
- ✅ `<rect>` — rectangles (with `rx`/`ry` for rounded corners)
- ✅ `<circle>` — circles
- ✅ `<ellipse>` — ellipses
- ✅ `<line>` — straight lines
- ✅ `<polyline>` — connected line segments (stroke only, NO fill)
- ✅ `<polygon>` — closed polyline (stroke only, NO fill)
- ✅ `<path>` — **ONLY with M/L/H/V/Z commands**
- ✅ `<pattern>` — repeating patterns

#### `<path>` Command Restrictions (CRITICAL)

**ONLY these commands are supported:**
- ✅ `M/m` — moveTo
- ✅ `L/l` — lineTo
- ✅ `H/h` — horizontal line
- ✅ `V/v` — vertical line
- ✅ `Z/z` — close path

**FORBIDDEN commands (SVG will be SKIPPED in PPTX):**
- ❌ `Q/q` — quadratic Bézier curve
- ❌ `C/c` — cubic Bézier curve
- ❌ `S/s` — smooth cubic Bézier
- ❌ `T/t` — smooth quadratic Bézier
- ❌ `A/a` — elliptical arc

#### Additional SVG Constraints
- ❌ NO rotated shapes — `transform="rotate()"` causes fallback failure
- ❌ NO `<text>` in complex SVGs — becomes rasterized in PPTX
- ❌ Filled `<path>` must form closed rectangles (M/L/H/V/Z only)
- ⚠️ Gradients technically supported but DISCOURAGED

#### ⚠️ CRITICAL: Pie Charts — Image Generation Tool is MANDATORY

**Pie charts MUST be created using `GenerateImage`. There is NO SVG alternative.**

- SVG pie charts require arc commands (`A`) which are FORBIDDEN
- ALL workarounds (layered circles, stroke-dasharray, clip-paths, conic-gradient, rotated segments) WILL FAIL in PPTX
- The ONLY correct approach: generate as PNG/JPG image via `GenerateImage`, embed with `<img>`

```html
<!-- ✅ SUPPORTED: Simple shapes -->
<svg width="200" height="4">
  <rect width="200" height="4" rx="2" fill="#dda15e"/>
</svg>

<!-- ✅ SUPPORTED: Straight line paths -->
<svg width="100" height="100">
  <path d="M10 10 L50 10 L50 50 L10 50 Z" fill="#bc6c25"/>
</svg>

<!-- ❌ FORBIDDEN: Bézier curves -->
<svg><path d="M0 10 Q25 0 50 10 T100 10" stroke="#dda15e"/></svg>

<!-- ❌ FORBIDDEN: Arc commands -->
<svg><path d="M16 4a8 8 0 0 1 5 14.3" stroke="#dda15e"/></svg>

<!-- ⚠️ WORKAROUND: Approximate curves with line segments -->
<svg><path d="M0 10 L12 6 L25 4 L37 6 L50 10" stroke="#dda15e" stroke-width="2"/></svg>
```

### Appendix E — Advanced Techniques (REQUIRED)

#### SVG — ONLY for Decorative Shapes (NOT a replacement for real images)

- ⚠️ SVG is for **decorative elements ONLY**. It does NOT satisfy the "real image" requirement.
- You MUST still use `GenerateImage` for actual photos/illustrations even if SVG is used for diagrams.
- Do NOT use SVG to "draw" illustrations, backgrounds, or hero visuals.

#### SVG Usage Guidelines

- Prefer SVG for all decorative shapes (lines/dividers, corner accents, badges, frames, arrows)
- SVG gives pixel-crisp geometry that won't blur under `transform: scale()`
- Use SVG for masks/overlays and diagram-like UI (timeline rails, connectors)
- Rule of thumb: if it's a "shape" (not text, not a photo), SVG is usually cleanest
- ⚠️ ALWAYS check Appendix D constraints before writing SVG paths

#### ⚠️ CRITICAL: Background Shapes Must Use SVG

Do NOT use CSS background/border for decorative background shapes. These must use SVG:
- Badge/tag backgrounds (rounded rectangles, pill shapes)
- Feature tag backgrounds
- Card borders
- Button-like backgrounds
- Dividers (NOT CSS `background`, `border`, or `<hr>`)

**Reason**: CSS borders/backgrounds blur under `transform: scale()`. SVG stays crisp.

```html
<!-- ✅ Correct: SVG badge with text INSIDE the SVG -->
<svg width="180" height="52" viewBox="0 0 180 52">
  <rect width="180" height="52" rx="26" fill="#fb8500"/>
  <text x="90" y="26" text-anchor="middle" dominant-baseline="central"
        font-size="16" font-weight="700" fill="#ffffff">LABEL</text>
</svg>

<!-- ❌ Wrong: span overlay on SVG (text lost in PPTX) -->
<div class="badge">
  <svg><rect .../></svg>
  <span>LABEL</span>
</div>

<!-- ❌ Wrong: CSS background -->
<div style="background: #fb8500; border-radius: 26px;"><span>LABEL</span></div>

<!-- ✅ Correct: SVG divider -->
<svg width="120" height="4" aria-hidden="true">
  <rect width="120" height="4" rx="2" fill="#219ebc"/>
</svg>

<!-- ❌ Wrong: CSS divider -->
<div style="width: 120px; height: 4px; background: #219ebc;"></div>
```

#### SVG Use Cases

**1. Background Patterns** — Geometric textures for visual depth:

```html
<!-- Dot grid pattern -->
<svg width="100%" height="100%" style="position:absolute;top:0;left:0;opacity:0.08;pointer-events:none;">
  <defs>
    <pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="2" fill="currentColor"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#dots)"/>
</svg>

<!-- Diagonal stripes -->
<svg width="100%" height="100%" style="position:absolute;top:0;left:0;opacity:0.05;pointer-events:none;">
  <defs>
    <pattern id="stripes" width="20" height="20" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <rect width="10" height="20" fill="currentColor"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#stripes)"/>
</svg>
```

**2. Decorative Elements**:

```html
<!-- L-shaped corner decoration -->
<svg width="40" height="40" style="position:absolute;top:0;left:0;" aria-hidden="true">
  <path d="M0 35 L0 0 L35 0" stroke="currentColor" stroke-width="2" fill="none" opacity="0.4"/>
</svg>

<!-- Straight divider line -->
<svg width="400" height="2" aria-hidden="true">
  <rect width="400" height="2" fill="currentColor" opacity="0.3"/>
</svg>

<!-- Simple arrow (right-pointing) -->
<svg width="40" height="16" viewBox="0 0 40 16" aria-hidden="true">
  <path d="M0 8 L32 8 M24 2 L32 8 L24 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>
```

**3. Icons**:

```html
<!-- Checkmark icon (polyline - SUPPORTED) -->
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="20 6 9 17 4 12"/>
</svg>

<!-- Simple arrow icon (path with L/M - SUPPORTED) -->
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M5 12 L19 12 M12 5 L19 12 L12 19"/>
</svg>

<!-- Plus sign icon (lines - SUPPORTED) -->
<svg width="24" height="24" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
  <line x1="12" y1="5" x2="12" y2="19"/>
  <line x1="5" y1="12" x2="19" y2="12"/>
</svg>
```

**4. Data Visualization Helpers**:

```html
<!-- Percentage ring (70%) -->
<svg width="100" height="100" viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" stroke="#e0e0e0" stroke-width="8" fill="none"/>
  <circle cx="50" cy="50" r="40" stroke="#4CAF50" stroke-width="8" fill="none"
          stroke-dasharray="251.3" stroke-dashoffset="75.4" stroke-linecap="round"
          transform="rotate(-90 50 50)"/>
  <text x="50" y="50" text-anchor="middle" dominant-baseline="central" font-size="20" font-weight="bold" fill="currentColor">70%</text>
</svg>

<!-- Horizontal progress bar -->
<svg width="200" height="12" viewBox="0 0 200 12">
  <rect x="0" y="0" width="200" height="12" rx="6" fill="#e0e0e0"/>
  <rect x="0" y="0" width="140" height="12" rx="6" fill="#2196F3"/>
</svg>

<!-- Mini bar chart -->
<svg width="80" height="40" viewBox="0 0 80 40">
  <rect x="0" y="20" width="12" height="20" fill="currentColor" opacity="0.6"/>
  <rect x="17" y="10" width="12" height="30" fill="currentColor" opacity="0.8"/>
  <rect x="34" y="5" width="12" height="35" fill="currentColor"/>
  <rect x="51" y="15" width="12" height="25" fill="currentColor" opacity="0.7"/>
  <rect x="68" y="8" width="12" height="32" fill="currentColor" opacity="0.9"/>
</svg>
```

**5. Masks & Overlays**:

```html
<!-- Bottom overlay for text readability -->
<svg width="100%" height="300" style="position:absolute;bottom:0;left:0;pointer-events:none;">
  <rect width="100%" height="100%" fill="#000000" fill-opacity="0.7"/>
</svg>

<!-- Side overlay -->
<svg width="400" height="100%" style="position:absolute;left:0;top:0;pointer-events:none;">
  <rect width="100%" height="100%" fill="#000000" fill-opacity="0.8"/>
</svg>
```

#### SVG Implementation Tips

- Use `vector-effect="non-scaling-stroke"` to keep stroke widths stable under `transform: scale()`
- For thin lines, prefer filled rectangles to avoid stroke anti-alias artifacts
- Use `overflow="visible"` when SVG needs to extend beyond its box
- Use `aria-hidden="true"` for purely decorative SVGs
- Use `currentColor` for easy theming
- Use `pointer-events: none` for overlay SVGs

#### Minimal Patterns

```html
<!-- Crisp divider line -->
<svg overflow="visible" width="320" height="2" aria-hidden="true">
  <rect width="320" height="2" fill="rgba(255,255,255,0.35)"></rect>
</svg>

<!-- Consistent stroke under scaling -->
<svg overflow="visible" width="320" height="2" aria-hidden="true">
  <path vector-effect="non-scaling-stroke" d="M0 1 L320 1" stroke="rgba(255,255,255,0.55)" stroke-width="2"></path>
</svg>

<!-- Solid overlay -->
<svg width="100%" height="200" style="position:absolute;bottom:0;left:0;pointer-events:none;">
  <rect width="100%" height="100%" fill="#000000" fill-opacity="0.6"/>
</svg>
```

### Appendix F — HTML2PPTX Validation Rules (REQUIRED)

#### Layout and Dimensions
- Slide content must not overflow (no scrollbars)
- Text elements larger than 12pt must be at least 0.5″ above bottom edge
- HTML body dimensions must match 960×540

#### Backgrounds and Images
- No CSS gradients
- No `background-image` on `div` elements
- For slide backgrounds, use a real `<img>` element
- Solid background colors → on `.slide-content` directly

#### Text Elements
- `p`, `h1`–`h6`, `ul`, `ol`, `li` must NOT have background, border, or shadow
- Inline elements (`span`, `b`, `i`, `u`, `strong`, `em`) must NOT have margins
- Do NOT use manual bullet symbols — use `<ul>` or `<ol>` lists
- Do NOT leave raw text directly inside `div` — wrap all text in text tags

#### SVG and Text
- Do NOT place text (`<span>`, `<p>`) as overlay on SVG using absolute positioning — text will be LOST in PPTX
- When badge/tag/label needs text on SVG background, put text INSIDE SVG using `<text>` element
- SVG `<text>` must use `text-anchor="middle"` and `dominant-baseline="central"` for centering

```html
<!-- ✅ Correct: Text inside SVG -->
<svg width="100" height="32" viewBox="0 0 100 32">
  <rect width="100" height="32" rx="16" fill="#bc6c25"/>
  <text x="50" y="16" text-anchor="middle" dominant-baseline="central"
        font-size="14" font-weight="700" fill="#fefae0" letter-spacing="3">丰收季</text>
</svg>

<!-- ❌ Wrong: Text overlaid on SVG (LOST in PPTX) -->
<div class="badge">
  <svg aria-hidden="true"><rect .../></svg>
  <span style="position:absolute;">丰收季</span>
</div>
```

#### Placeholders
- Elements with class `placeholder` must have non-zero width and height

### Appendix G — Page Number Badge / 角标 (REQUIRED)

All slides **except Cover Page** MUST include a page number badge showing the current slide number in the bottom-right corner.

- **Position**: `position:absolute; right:32px; bottom:24px;`
- **Must use SVG** (text inside `<text>`, not overlaid `<span>`)
- Colors from palette only; keep it subtle; same style across all slides
- Show current number only (e.g. `3` or `03`), NOT "3/12"

```html
<!-- ✅ Circle badge (default) -->
<svg style="position:absolute; right:32px; bottom:24px;" width="36" height="36" viewBox="0 0 36 36">
  <circle cx="18" cy="18" r="18" fill="#219ebc"/>
  <text x="18" y="18" text-anchor="middle" dominant-baseline="central"
        font-size="14" font-weight="600" fill="#ffffff">3</text>
</svg>

<!-- ✅ Pill badge -->
<svg style="position:absolute; right:32px; bottom:24px;" width="48" height="28" viewBox="0 0 48 28">
  <rect width="48" height="28" rx="14" fill="#219ebc"/>
  <text x="24" y="14" text-anchor="middle" dominant-baseline="central"
        font-size="13" font-weight="600" fill="#ffffff">03</text>
</svg>

<!-- ✅ Minimal (number only) -->
<p style="position:absolute; right:36px; bottom:24px; margin:0; font-size:13px; font-weight:500; color:#8ecae6;">03</p>
```

---

## Common Mistakes to Avoid

- **Don't repeat the same layout** — vary columns, cards, and callouts across slides
- **Don't center body text** — left-align paragraphs and lists; center only titles
- **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14–16pt body
- **Don't default to blue** — pick colors reflecting the specific topic
- **Don't mix spacing randomly** — choose 0.3″ or 0.5″ gaps and use consistently
- **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
- **Don't create text-only slides** — add images, icons, charts, or visual elements
- **Don't forget text box padding** — when aligning shapes with text edges, set `margin: 0` or offset
- **Don't use low-contrast elements** — icons AND text need strong contrast against background
- **NEVER use accent lines under titles** — hallmark of AI-generated slides; use whitespace or background color instead
- **Don't use gradients** — solid colors only (Appendix C)
- **Don't use animations** — static slides only (Appendix C)
- **Don't overlay text on SVG with absolute positioning** — text will be lost in PPTX (Appendix F)
- **Don't use CSS for decorative shapes** — use SVG for crispness under scaling (Appendix E)
- **Don't forget the page number badge** — required on all slides except cover (Appendix G)
- **Don't use Bézier curves or arcs in SVG paths** — PPTX converter will skip them (Appendix D)

## File & Output Conventions

| Item | Convention |
|------|-----------|
| Slide files | `slides/slide-01.html`, `slides/slide-02.html`, … (zero-padded) |
| Image files | `slides/imgs/` directory |
| Slide dimensions | 960×540 px (`.slide-content`) |
| Font | `Times New Roman` for all text (Chinese and English) |
| CSS | Inline only (except Appendix A scaling snippet) |
| Colors | From chosen palette only; no gradients |
| Animations | None — static slides only |
| Page badge | All slides except cover; bottom-right corner |
| Final deployment | Use `deploy_html_presentation` tool |

## Tools Reference

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `GenerateImage` | Create images for slides | MANDATORY for cover + content pages; optional for TOC/divider/summary |
| `get_html_presentation_screenshot` | Take screenshot of rendered HTML slide | After writing every slide HTML |
| `images_understand` | Analyze screenshot for layout issues | After every screenshot — verify no overlaps, correct layout, badge present |
| `deploy_html_presentation` | Merge slides and deploy final presentation | Step 5 — after all slides are verified |
