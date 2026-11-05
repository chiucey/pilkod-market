# Character Template

This template defines how to create character specifications for comic generation.

## ⚠️ CRITICAL: Consistency Requirements

**角色一致性是漫画质量的关键**。Character definition 必须完整、详细，因为在生成所有页面图像时，这些描述会被引用以确保角色在所有页面中保持一致。

**必须遵循的原则**:
- 每个角色的所有视觉特征必须**完整描述**，不能遗漏任何细节
- 服装描述必须详细到可以确保在不同页面中保持一致
- 标志性特征必须明确列出并持续强调
- 这些定义会被复制到每个页面的图像生成提示词中

## Structure

Each character definition lives in `characters-{approach}/characters.md` with corresponding `characters.png` reference image.

## characters.md Format

```yaml
---
style: [style-name]
aspect_ratio: ["3:4" | "4:3" | "16:9"]
estimated_count: [number of characters]
---

## Character Name (Role)

**Visual Identity**
- Age: [specific age or age range]
- Build: [height, weight, body type]
- Hair: [color, style, length, any distinctive features]
- Face: [face shape, eye color and shape, nose, mouth, any distinguishing marks]
- Clothing: [detailed description of outfit, including color, fabric, style, any accessories]
- Distinguishing Features: [any unique physical traits, scars, tattoos, etc.]
- Overall Impression: [brief character summary]

**Expression Range**
- Default: [typical resting expression]
- [Emotion 1]: [detailed description of how it manifests]
- [Emotion 2]: [detailed description of how it manifests]
- [Add as needed for key story emotions]

**Key Props/Accessories**
- [Item 1]: [detailed appearance and how it's used/carried]
- [Item 2]: [detailed appearance and how it's used/carried]

**Panel Presence**
- Typical Composition: [how character is typically framed]
- Characteristic Poses: [2-3 detailed pose descriptions]
- Relationship to Other Characters: [how positioned relative to others]
```

## Visual Identity Writing Guide

**为保持一致性，Visual Identity 必须包含以下所有要素**:

1. **Age**: 具体年龄或年龄范围（如 "30-35岁"、"青春期后期"）
2. **Body**: 身高、体型、体态（如 "中等身高，略显瘦弱，驼背"）
3. **Hair**:
   - 颜色（如 "深褐色"）
   - 发型和长度（如 "中等长度，略显凌乱"）
   - 特殊特征（如 "右侧有一撮白发"）
4. **Face**:
   - 脸型（如 "椭圆形"、"方形"）
   - 眼睛：颜色、形状、大小（如 "深棕色圆形眼睛，略带疲惫"）
   - 鼻子和嘴巴的特征
   - 任何 distinguishing marks（如 "左脸颊有浅色疤痕"）
5. **Clothing** (⚠️ 最重要):
   - 上衣：类型、颜色、面料、剪裁（如 "深蓝色粗花呢夹克，略微宽松"）
   - 下装：类型、颜色、款式（如 "灰色灯芯绒裤子，稍显陈旧"）
   - 鞋子：类型、颜色（如 "磨损的棕色皮鞋"）
   - 配饰：手表、眼镜、项链等（如 "金属边眼镜，略显厚重"）
   - 衣着细节：如 "领子总是敞开"、"袖口有墨水渍"
6. **Distinguishing Features**: 任何独特的身体特征
7. **Overall Impression**: 一句话概括角色给人的整体印象

**✅ 好的 Clothing 描述示例**:
```
Clothing: 深蓝色粗花呢夹克，衣领微卷，袖口有墨水渍；内穿米色高领毛衣；灰色灯芯绒长裤，膝盖处有轻微磨损；黑色皮鞋，鞋跟外侧有磨损。总是看起来像刚从实验室出来。
```

**❌ 不够详细的 Clothing 描述示例**:
```
Clothing: 蓝色夹克和裤子
```

## Example: Complete Character Definition

```yaml
---
style: sepia
aspect_ratio: "3:4"
estimated_count: 4
---

## Alan Turing (Protagonist)

**Visual Identity**
- Age:20s-40s throughout story
- Lean, slightly awkward build
- Messy dark hair, always looks like he just woke up
- Intense, unfocused eyes (thinking about problems)
- Wears rumpled tweed jackets, sweater vests, unbuttoned collars
- Often has ink stains on fingers/cuffs
- Distinguishing feature: Runner's physique, talks with hands

**Expression Range**
- Default: Distracted, abstracted (thinking)
- Excited: Eyes light up, rapid hand gestures, talks fast
- Frustrated: Bites lip, paces, runs fingers through hair
- Sad: Withdrawn, shoulders slump, avoids eye contact
- Triumphant: Quiet smile, look of profound satisfaction

**Key Props/Accessories**
- Pencil/notebook: Always jotting down ideas
- Enigma machine diagrams: Pocket reference cards
- Running shoes: Even in academic settings
- Apple: Symbolic prop (appears at beginning and end)

**Panel Presence**
- Often offset from other characters (physically or mentally)
- Frequently shown in close-up during thinking moments
- Action: Running, pacing, chalkboard work, machine operation
- Lighting: Often spotlighted against dark backgrounds (isolated genius)

## Christopher Morcom (Catalyst)

**Visual Identity**
- Age: 17-18 (appears in flashback)
- Bright, open face, wholesome appearance
- Neat appearance, school uniform properly worn
- Curious eyes, ready smile
- Contrast with Turing's disorder

**Expression Range**
- Default: Friendly, interested
- Excited: Shared enthusiasm with Turing
- Supportive: Listening intently, encouraging
- (Deceased scenes): Ghostly, ethereal quality

**Key Props/Accessories**
- Chemistry equipment: Shared experiments
- Science textbooks: Bonding over reading
- Bicycle: School transportation

**Panel Presence**
- Often placed at Turing's side (equal partnership)
- Warm lighting around him (memory/halo effect)
- Flashback scenes: Sepia-tinged, slightly faded

## Joan Clarke (Colleague/Friend)

**Visual Identity**
- Age: 20s-30s
- Professional, neat appearance
- Practical clothing ( wartime work)
- Intelligent, focused eyes
- Distinguishing feature: Only one who truly understands Turing's mind

**Expression Range**
- Default: Concentrated, professional
- Amused: Turing's eccentricities
- Respectful: Recognizes his genius
- Romantic: Subtle, unspoken feelings

**Key Props/Accessories**
- Code sheets: Doing actual work
- Tea cup: British normalcy in high-pressure environment

**Panel Presence**
- Often working alongside Turing at desks/machines
- Comfortable silence panels (mutual understanding)
- Respectful distance (professional boundaries)

## Commander Denniston (Authority/Antagonist)

**Visual Identity**
- Age: 40s-50s
- Military bearing, stiff posture
- Immaculate uniform
- Stern, judgmental expression
- Distinguishing feature: Represent establishment that doubts Turing

**Expression Range**
- Default: Disapproving, skeptical
- Frustrated: Turing's insubordination
- Grudging respect: After results
- Official: Military formality

**Key Props/Accessories**
- Official documents: Obstacles/bureaucracy
- Military cap: Authority symbol

**Panel Presence**
- Often framed from below (authority angle)
- Shown in doorways/windows (barrier figure)
- Cluttered office (establishment weight) vs. Turing's sparse focus
```

## Style-Specific Character Guidelines

### Sepia Style Characters

- **Color palette**: Warm browns, aged photograph feel
- **Line work**: Slightly softer edges, nostalgic quality
- **Clothing**: Period-accurate (1940s British)
- **Texture**: Film grain, slight vignette

### Ohmsha Style Characters

Use Doraemon cast by default:

- 大雄 (Nobita): Curious learner, asks questions, makes mistakes
- 哆啦A梦 (Doraemon): Mentor with gadgets, explains concepts
- 胖虎 (Gian): Antagonist, represents obstacles/misconceptions
- 静香 (Shizuka): Supportive friend, asks clarifying questions

Only create custom characters if explicitly requested.

### Classic Style Characters

- Balanced realism and stylization
- Clear visual distinction between characters
- Expressive but not exaggerated features

### Dramatic Style Characters

- High contrast lighting
- Exaggerated expressions for emotional impact
- Dynamic poses and composition

### Warm Style Characters

- Soft, approachable features
- Gentle expressions
- Rounded shapes (friendlier)

## Character Generation Process

1. **Identify characters**: From analysis key figures (2-6 characters typically)
2. **Define roles**: Protagonist, antagonist, catalyst, mentor, etc.
3. **Visual identity**: Concrete details for consistent rendering
4. **Expression range**: Essential emotions for story beats
5. **Props**: Meaningful accessories that characterize
6. **Panel presence**: How they typically appear in scenes
7. **Generate reference sheet**: Create `characters.png` with all characters in style

## Reference Image Tips

For `characters.png`:

- Show each character in multiple angles (front, 3/4, profile if possible)
- Include expression range
- Show key props
- Maintain consistent scale between characters
- Include character names/labels
- Ensure style matches selected comic style

## Character Consistency Checklist

- ✓ Consistent proportions across panels
- ✓ Identifiable from silhouette alone
- ✓ Props appear consistently
- ✓ Aging progression clear (if story spans years)
- ✓ Style-specific traits applied (sepia warm tones, etc.)
