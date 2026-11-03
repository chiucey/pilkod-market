---
name: 资产道具生成
description: 为 Seedance 视频脚本生成资产道具提示词。当用户需要创建道具参考图、为 AI 视频生成资产提示词、或需要为 Nano Banana 图像生成描述道具时使用。核心流程：识别道具 → 选择展示角度 → 生成提示词。触发词：资产道具生成、道具提示词生成、创建道具图片、生成 prop prompt、create prop reference
---

# 资产道具生成器

## Overview

This skill generates optimized prompts for Nano Banana image generation when creating prop assets for Seedance video scripts. **The core principle: always ask users to select a display angle BEFORE generating prompts.**

---

## Workflow

### Step 1: Identify the Prop

Confirm what prop the user wants to generate and its basic attributes (age, color, material).

### Step 2: Select Display Angle (MANDATORY)

**Must present angle options to users BEFORE generating prompts.**

### Step 3: Generate Prompt

Apply the selected angle template combined with material, condition, and scene elements.

---

## Angle Selection Framework

### Core Angles

| Angle | Description | Best For |
|-------|-------------|----------|
| **Front** | Direct view, showing front features | Boxes, cups, clothing, doors |
| **Side** | 90° from camera, showing profile | Tables, cabinets, vehicles, books |
| **45° Angled** | Shows depth and 3D form | Electronics, shoes, jewelry (recommended for most items) |
| **Back** | Showing rear details | Backpacks, chair backs, phone backs |
| **Top-Down** | Looking down from above | Desktop items, plates, keyboards |
| **Bottom-Up** | Looking up from below | Drones, ceiling lights |
| **Close-Up** | Focusing on specific detail | Any prop's specific feature |
| **Mounted** | Shown installed on carrier | Phone mounts, helmets, mirrors |
| **Laid Flat** | Flat display | Clothes, maps, flat fabric |
| **Handheld** | Being held by someone | Drinks, phones, umbrellas, food |

### Angle Selection by Prop Type

| Prop Category | Recommended Angles |
|---------------|-------------------|
| Box-shaped items | Front / 45° Angled |
| Cylindrical items | Front / 45° Angled |
| Clothing/accessories | Front / Laid Flat / 45° Angled |
| Vehicles | 45° Angled / Front |
| Electronics | 45° Angled |
| Furniture | 45° Angled / Front |
| Shoes | 45° Angled / Side |
| Food/beverages | Top-Down / 45° Angled |
| Mounted props | Mounted |

---

## Prompt Generation Framework

### Six Essential Elements

**1. Display Angle (MOST CRITICAL)**
> [Prop name] [selected angle] facing camera, [visible features] in view

**2. Complete Form**
> [Shape], [structure], [main components]

**3. Material & Texture**
> [Material] material, [color] color, [texture description]

**4. Details & Condition**
> [Age/use level], [wear marks], [special details]

**5. Scene Adaptation**
> [Mounting/placement state], [usage scenario], [carrier environment]

**6. Quality Requirements**
> 4K ultra clear, cinematic quality, rich details, stable image

### Standard Template

> **[Prop name] [angle] facing camera, [visible features], [material] material, [color] color, [details], [condition], [scene state], 4K ultra clear, cinematic quality, rich details, stable image**

---

## Output Format

When triggered, output in this sequence:

1. **Confirm Prop**: Verify what prop needs to be generated
2. **Angle Options**: List suitable display angles for this prop
3. **Request Selection**: Ask user to choose display angle
4. **Generate Prompt**: Create complete Nano Banana prompt based on selected angle
5. **Angle Explanation**: Explain why this angle suits the prop

---

## Inquiry Script Template

> "What angle would you like for this [prop name]?"
>
> Recommended options:
> - **Front**: Show front features like logo, label, front design
> - **Side**: Show profile and thickness
> - **45° Angled**: Show 3D depth (recommended for most items)
> - **Back**: Show rear design
> - **Top-Down**: Show top view from above
> - **Mounted**: Show prop installed on actual carrier
> - **Handheld**: Show prop being held by someone
>
> Please select an angle, or describe any other display approach you need.

---

## Key Principles

1. **Ask Angle First**: Must list angle options before generating prompts
2. **Recommend Suitable Angles**: Suggest 2-3 best angles based on prop type
3. **Allow Custom Angles**: Allow user-defined angles for special scenarios
4. **Concise Descriptions**: Keep prompts under 100 characters, focus on angle and key features
5. **Scene Adaptation First**: Match prop style to script scenario
6. **Angle Correction**: If result has wrong angle, add enforcement constraint at start: "[prop] facing camera at [specified angle]"

---

## Reference Materials

For detailed reference materials including:
- Complete material and texture vocabulary
- Wear condition descriptions
- Scene vocabulary
- Case studies and examples

See: `references/property-vocabulary.md`
