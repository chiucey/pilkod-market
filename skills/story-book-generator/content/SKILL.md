---
name: story-book-generator
description: 儿童绘本故事生成专家。创作10-15页中文绘本故事并生成水彩手绘风格插画。触发词：绘本、故事生成、讲故事、儿童故事、创作故事。
---

# 绘本故事生成专家

本技能帮助你创作优质的儿童绘本故事，包含精美的水彩手绘风格插画和简洁有趣的文字。

> **重要说明**：本技能生成的图片，文字直接嵌入画面中，不是放在图片下方。文字位于画面留白区域，纯黑字，无彩色底带，严格遵循参考图的排版规范。

> **Skill 文件说明**：本技能包含两个文件：
> - `SKILL.md`：技能主文件（本文件）
> - `style-ref.jpg`：画风参考图，所有图片生成均以此为风格锚点

---

## 文字嵌入规范（核心，必须严格遵循）

### 文字嵌入方式

根据对参考图的深度分析，文字嵌入遵循以下规范：

**文字位置**：
- 统一放置在画面**左下角**或**右下角**的白色留白区域
- 文字必须位于插画主体之外的留白处，不得覆盖角色和关键视觉元素
- 如果插画左侧留白充足则放左下角，右侧充足则放右下角

**文字样式**：
- **字体颜色**：纯黑色（#000000）
- **字体类型**：中文宋体/楷体风格（serif）
- **字号**：适中，既能清晰阅读，又不喧宾夺主
- **排列**：人工手动换行，2行，左对齐
- **行间距**：宽松（约等于1个文字高度），营造呼吸感
- **标点**：使用全角中文标点（，。？！""）

**背景处理**：
- ❌ **禁止**：文字下方无任何底色背景、色块填充或对话框
- ❌ **禁止**：不使用黄色/彩色条带承载文字
- ✅ **正确**：文字直接覆盖在画面的纯白色背景之上，如同印在纸张上一样

**⚠️ 重要提醒**：
> AI 图片生成工具对中文字符的渲染能力有限。Prompt 中的中文文字仅供参考，实际文字以**图片下方的文案说明**为准。
> 但生成图片时，Prompt 中仍需写明文字内容和位置要求，以便在支持文字渲染的模型中获得最佳效果。

---

## 核心流程

### 第一步：理解用户需求

首先了解以下信息：
- **故事主题**：关于什么？（如：友谊、勇气、卫生习惯、克服恐惧等）
- **主角设定**：什么小动物？（如兔子、小熊、小狐狸等；如用户未指定，结合主题自行选择合适的小动物）
- **目标年龄**：2-4岁 / 4-6岁？
- **页数要求**：默认12页，可接受10-15页

---

### 第二步：规划故事结构并输出文字

使用下方「故事结构模板」规划完整故事，**输出所有页面的文字内容**后，等待用户确认：

> 询问用户：「故事内容您看一下，确认没问题后我开始生成插画 ✅」

**故事结构**：

```
第1页（封面）  ：标题 + 主视觉
第2-3页（起）  ：角色登场 + 情境设定
第4-7页（承）  ：问题/冲突出现，逐步升级
第8-10页（转） ：意外转折，开始解决问题
第11-13页（合）：问题解决，圆满结局
第14-15页（尾）：情感升华 + 互动问题
```

**文字写作要求**：
- 每页 2-4 句话，语言简洁、口语化
- 适合 2-6 岁儿童理解
- 善用重复句式增加韵律感（如「不要不要！」）
- 多用拟声词（「哗啦啦」「滴滴答」「咚咚咚」）
- 多用感叹句表达情绪（「哇，好大呀！」）

---

### 第三步：生成角色设定图（保证视觉连贯性的关键）

用户确认故事文字后，**第一件事**是生成一张「角色设定图」。

**目的**：后续所有插画都以此图为参考，保证主角在每页的颜色、体型、眼睛比例完全一致。

**调用工具**：`image_synthesize`

**角色设定图提示词模板**：
```
工具：image_synthesize
input_files: ["style-ref.jpg"]
prompt: Character design sheet for children's picture book,
        [动物名称] as main character, front view and 3/4 view side by side,
        cute chubby round body, big round expressive eyes, [主色调] color,
        same art style as reference image,
        watercolor illustration, hand-drawn style, naive art,
        white background, multiple poses reference sheet,
        consistent character design, 2K resolution, no text
output_file: character-reference.png
```

**输出文件名**：`character-reference.png`

生成后展示给用户确认，如不满意可重新生成。

---

### 第四步：批量生成插画（并行加速）

角色确认后，将 **character-reference.png** 作为所有页面图片的 `input_files`，确保角色一致性。

**并行生成策略**：将页面分3批同时生成，大幅缩短等待时间：
- **第1批**：第1-5页（同时生成）
- **第2批**：第6-10页（同时生成）
- **第3批**：第11-15页（同时生成）

**单页图片调用格式**：
```
工具：image_synthesize
input_files: ["character-reference.png", "style-ref.jpg"]
             ↑ 角色参考图（保证角色一致）  ↑ 画风参考图（保证风格一致）
prompt: 见下方「图片生成提示词模板」
output_file: story_v3_p01.png（依次命名）
```

---

### 第五步：整合输出最终绘本

图片全部生成后，按以下格式输出完整绘本：

```markdown
## [故事标题]

---
**第1页** | 封面

![封面插画](story_v3_cover.png)
文字：《[标题]》

---
**第2页** | 角色登场

![角色图](story_v3_p01.png)
文字：小[动物名]住在一片美丽的[地方]。
      它最喜欢……

---
（继续每一页，格式相同）
```

---

## 图片生成提示词模板（含文字嵌入）

### 封面图模板

```
Children's picture book cover: [核心场景描述].
Chinese title text "[故事标题]" placed at TOP CENTER of white background in bold black Chinese serif font, large size.
[补充画面描述].
watercolor illustration, hand-drawn style, naive art, pastel colors, clean white background, 2K resolution
```

### 正文页模板（核心，必须严格遵循）

```
Children's picture book illustration: [场景画面描述].
Text in BOTTOM LEFT CORNER on pure white background, black Chinese serif font,
2 lines left-aligned: "[第1行文字内容][第2行文字内容]"
NO colored strip, text directly on white space, no background color behind text.
[补充画面描述，避免文字区域被遮挡].
watercolor illustration, hand-drawn style, naive art, pastel colors, clean white background, 2K resolution
```

**Prompt 关键词固定搭配（每张图必须包含）**：
- `Text in BOTTOM LEFT CORNER on pure white background`
- `black Chinese serif font`
- `2 lines left-aligned`
- `NO colored strip`
- `text directly on white space`

### 结尾/互动页模板

```
Children's picture book illustration: [场景描述].
Text in BOTTOM LEFT CORNER on pure white background, black Chinese serif font,
2 lines left-aligned: "[互动问题/金句]"
NO colored strip, text directly on white space.
watercolor illustration, hand-drawn style, naive art, pastel colors, clean white background, 2K resolution
```

### 负面提示词（避免出现）

```
realistic, photograph, anime style, cartoon, dark colors,
complex background, busy composition, adult themes,
low quality, blurry, distorted, colored text background,
text with color strip, text with shadow
```

---

## 图片风格规范

### 核心画风

| 特征 | 描述 |
|------|------|
| 主要技法 | 水彩手绘风格（Watercolor） |
| 艺术风格 | 稚拙美（Naive Art） |
| 表现手法 | 拟人化动物角色 |
| 质感 | 透明晕染，自然笔触，手绘感 |
| 背景 | 纯白极简，大量留白 |

### 色调搭配

| 场景 | 推荐配色 |
|------|----------|
| 夜晚/月光主题 | 银蓝 + 明黄 + 柔白 |
| 户外/自然主题 | 天蓝 + 明黄 + 棕色 |
| 温馨/亲情主题 | 粉色 + 橙色 + 暖黄 |
| 友谊/冒险主题 | 绿色 + 橙色 + 紫色 |

### 构图原则

- **大小对比**：主角与配角体型形成反差（制造幽默感）
- **极简留白**：背景纯白，无复杂环境，文字区域必须保持干净白色
- **局部特写**：聚焦角色表情和动作
- **构图比例**：主体角色占 60-70%，配角/道具占 20-30%，左下/右下角留给文字

### 线条特点

- 非闭合轮廓，线条留有呼吸感
- 粗细变化，关键部位线条较粗
- 轻微颤抖感，增加手绘气息
- 配合动作线、表情线表现运动和情绪

---

## 故事结构详细模板

### 各页内容指引

**第1页：封面（吸引注意）**
```
图片：主视觉图，展示故事核心场景和主角
文字：《[故事标题]》（位于页面顶部中央）
```

**第2页：角色登场（建立连接）**
```
图片：展示主角的生活环境和日常状态
文字：介绍主角是谁、住在哪里、平时喜欢做什么（2-3句）
```

**第3页：问题初现（制造期待）**
```
图片：展示问题或需求的出现
文字：引出故事矛盾点（2-3句）
```

**第4-7页：冲突发展（增加张力）**
```
每页展示一个情节发展，冲突逐渐升级
```

**第8-10页：转折解决（意外惊喜）**
```
出现意想不到的解决方案
```

**第11-13页：圆满结局**
```
问题解决，主角获得成长
```

**第14-15页：情感升华 + 互动**
```
留下回味，引发共鸣
互动页：小朋友们，[互动问题]？
```

---

## 角色一致性检查清单

图片全部生成后，对比各页检查：
- [ ] 主角颜色是否一致
- [ ] 体型比例是否一致
- [ ] 眼睛大小和位置是否一致
- [ ] 线条风格是否统一
- [ ] 色调是否统一
- [ ] 文字均在左下角/右下角白色留白区域，无彩色底带

如有明显偏差，重新生成该页并说明原因。

---

## 适用故事主题

- **勇气主题**：克服恐惧、勇敢面对
- **情感教育**：分享、友谊、克服恐惧
- **卫生习惯**：不爱洗澡、刷牙的重要性
- **友谊故事**：体型差异的朋友、孤独的小动物
- **想象力**：奇妙的冒险、有趣的误会
