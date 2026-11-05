---
name: rednote-copywriter
description: 支持中英文输入生成小红书风格英文爆款文案及宣传海报；当用户需要"写小红书文案并配图"、"generate RedNote post with poster"、"小红书海报设计"时使用
---

# RedNote English Viral Copywriter

## Purpose

Generate high-converting English product copy in RedNote (Xiaohongshu) style, plus a matching promotional poster.
Accepts input in **both Chinese and English**; outputs English copy and poster.
Output includes three sections: **Title**, **Body**, **Hashtags**, and a **Promotional Poster**.

The writing style balances authenticity, aspiration, and relatability — personal
and community-driven rather than corporate or promotional.

The poster style follows RedNote's aesthetic: high visual appeal, Instagram-inspired, lifestyle-oriented, and clean.

---

## Input Handling

Accept inputs in **both Chinese and English**. When the user provides information in Chinese, understand the content and generate English copy in the output format.

Accept any combination of the following from the user:

| Input | How to use |
|---|---|
| **Product name** | Feature prominently in title and/or opening line |
| **Short description** | Extract key benefits, unique features, and target audience |
| **Chinese input (产品描述/要求)** | Understand Chinese product descriptions or requirements and translate key points into English copy |
| **Image** | Analyze visual elements — texture, color, packaging, aesthetic — and incorporate sensory details into the copy |
| **Style preference** | Apply the corresponding tone profile (see Tone section below) |
| **Poster style** | Optional: Specify visual preference (minimalist, lifestyle, bold, soft, etc.) - auto-match to product category if not specified |
| **Category** | Auto-detect from description/image if not stated; use to select hashtag set and poster visual style |
| **Post length** | Default to "standard" (150–250 words body) unless user specifies short/detailed |

If the user does not specify a style, **infer the most appropriate tone** based on the product category and description.

---

## Workflow

### Step 1 — Gather and Analyze Inputs
- Read all provided product details
- **Language recognition**: Detect if the input is in Chinese or English
- If input is in Chinese, understand the content and extract key information (product features, benefits, target audience, etc.)
- If an image is provided, extract: aesthetic feel, color palette, packaging style, visible textures or materials
- Identify product category (beauty, fashion, food, home, tech, travel, fitness, other)
- Note any explicit style instruction from the user
- **Output language**: Always generate the final copy in English, regardless of input language

### Step 2 — Load Reference Material
- Load `references/copywriting-guide.md` for title formulas, body structure, tone profiles, and viral language patterns
- Load `references/hashtag-strategy.md` for the 3-tier hashtag system and category-specific hashtag sets

### Step 3 — Write the Title
- Apply one of the proven hook title patterns from the copywriting guide
- Keep under 20 words; include 1–2 relevant emojis
- Must create curiosity, promise a benefit, or address a pain point

### Step 4 — Write the Body
Follow the five-part body structure from the copywriting guide:
1. **Opening hook** — personal story, bold claim, or relatable scenario
2. **Product introduction** — name, what it is, standout feature
3. **Experience / story** — sensory details, specific reactions, results
4. **Key benefits** — 3–5 bullet points with emojis
5. **Closing CTA** — warm recommendation or engagement question

Apply the appropriate tone profile for the product category.
Use line breaks generously for scannability.
Incorporate 1–2 viral power phrases naturally (do not force them).

### Step 5 — Select Hashtags
- Choose 8–15 hashtags using the 3-tier system from the hashtag strategy guide
- Include 4–5 niche, 3–4 mid, 2–3 broad tags
- Add 1–2 RedNote platform tags (`#rednote`, `#notsponsored`, etc.)
- Place all hashtags at the end, on their own line

### Step 6 — Generate Promotional Poster
Based on the generated copy, create a matching promotional poster with the following guidelines:

**Visual Style Selection (by category):**
- **Beauty & Skincare**: Clean background, soft lighting, product close-up, minimalist, high-key lighting
- **Fashion & Accessories**: Styled outfit scene, Instagram-inspired flat lay, natural lighting, lifestyle aesthetic
- **Food & Snacks**: Food close-up, warm color tones, lifestyle scene, appetizing presentation
- **Home & Lifestyle**: Interior setting, cozy atmosphere, product in use, warm and inviting
- **Tech & Gadgets**: Modern feel, clean background, product details, sleek and futuristic
- **Travel & Experience**: Scenic or destination elements, sense of exploration, adventure vibe
- **Fitness & Wellness**: Active setting, motivational atmosphere, clean and energetic

**Poster Design Elements:**
- **Main text (large)**: English title from the copy
- **Subtext (medium)**: Product name
- **Bullet points (small)**: 2-3 key benefits from the body copy
- **Layout**: Clean, ample white space, balanced composition
- **Color palette**: Match product category aesthetic (soft pastels, bold colors, or muted earth tones)
- **Typography**: Modern, clean, readable fonts

**Text Placement Rules:**
- Main title: Prominent, at top or upper section
- Product name: Below title or overlaid on image
- Key benefits: Bottom section or side panel
- Avoid covering product main features or focal points

Generate the poster using image generation capabilities with a detailed prompt incorporating these elements.

### Step 7 — Final Output Format

Present the complete copy and poster in this format:

```
📌 TITLE
[title here]

✍️ BODY
[body copy here]

🏷️ HASHTAGS
[hashtag string here]

🖼️ PROMOTIONAL POSTER
[generate and display the poster image here]
```

The poster should match the copy's tone and product category, with English text elements integrated naturally.

---

## Style Reference

| Style | When to use | Key characteristics |
|---|---|---|
| **Aesthetic / Lifestyle** | Home, fashion accessories, curated products | Soft, curated, vibe-forward, aspirational |
| **Honest Review / UGC** | Skincare, beauty, supplements | Personal, trust-building, before/after, real results |
| **Hype / Trendy** | Viral products, limited edition, collabs | Energetic, urgency, community language, trend-aware |
| **Cozy / Comfort** | Food, wellness, home goods | Warm, sensory, slow-life, indulgent |
| **Minimalist / Premium** | Tech, luxury goods, investment pieces | Clean, confident, understated, quality-focused |

---

## Quality Checklist

Before outputting, verify:
- [ ] Title uses a hook pattern and stays under 20 words
- [ ] Body has all 5 structural sections
- [ ] Sensory/specific details included (not generic praise)
- [ ] Tone matches product category
- [ ] 1–2 viral phrases used naturally
- [ ] 8–15 hashtags across all 3 tiers
- [ ] No corporate ad-speak or wall-of-text
- [ ] Emojis used purposefully, not excessively (max 10 total)
- [ ] **Poster visual style matches product category**
- [ ] **Poster includes English text: title, product name, 2-3 key benefits**
- [ ] **Poster text is readable and well-positioned (not covering main features)**
- [ ] **Poster has clean layout with ample white space**
- [ ] **Overall poster aesthetic follows RedNote style (ins-inspired, high visual appeal)**
