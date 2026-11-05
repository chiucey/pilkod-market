---
name: anime-prompt-factory
description: 二次元AI绘图Prompt生成器。当用户要求生成动漫头像、二次元头像、OC角色卡、真人动漫化、漫展返图修复、CG海报、CP双人图Prompt，或要求用ChatGPT/Claude写Midjourney/NovelAI提示词时使用。支持关键词：二次元、Anime、AI绘图、头像生成、角色设计、OC、人设、Cosplay。
---

# 二次元出片公式 · Anime Prompt Factory

## 核心能力

将用户需求转化为可直喂图像生成模型的精修Prompt。

**支持模型**：Midjourney v6 / NovelAI v3 / SDXL / Niji Journey 6

---

## 工作流程

### 步骤1：识别用户意图

用户可能处于以下场景之一：

| 场景 | 触发关键词 | 输出 |
|------|-----------|------|
| 真人动漫化 | 照片转动漫、真人动漫化、日漫风 | P01-P05模板 |
| 二次头像生成 | 头像、萌系、美少年、暗黑系 | P06-P10模板 |
| OC角色卡 | OC、人设、三视图、技能卡 | P11-P15模板 |
| 漫展返图救援 | 漫展、Cos、返图、光线修复 | P16-P19模板 |
| CG海报制作 | 海报、PV、战斗、番剧风 | P20-P24模板 |
| CP双人图 | CP、双人、情侣、互动 | P25-P28模板 |

### 步骤2：收集关键变量

根据用户选择的模板，收集以下核心变量：

**通用变量（所有模板）**：
- `IMAGE_MODEL`：目标图像模型
- `CHARACTER_MOOD`：性格调性（元气/清冷/温柔/暗黑）
- `LIGHTING_STYLE`：光照风格
- `FRAMING`：构图方式

**按需收集的变量**（见 references/prompts.md 各模板定义表）

### 步骤3：生成Prompt

按以下结构输出：

```
## 主Prompt
[IMAGE_MODEL] 优化的完整提示词

## 负面Prompt
[排除风格漂移、崩坏等问题的关键词]

## 参数建议
- Aspect Ratio: [建议比例]
- Stylize: [建议值]
- 其他参数: [特定模型参数]

## 中文解读
[一句话解释这张图的调性，方便用户向他人说明]
```

### 步骤4：应用风格DNA（可选）

如用户有特定风格偏好，从 references/style-dna.md 加载对应工作室词库叠加。

### 步骤5：推荐工作流（可选）

如用户需要完整创作路径，推荐 references/workflows.md 中的组合流。

---

## 避坑提示

生成Prompt后，自动添加以下提醒：

1. **人脸保真极限**：真人转动漫相似度预期70-80%，非100%
2. **版权风险**：Cos真实角色的产出仅用于个人/同人，不商用
3. **风格叠加限制**：单次最多叠加2个工作室风格，避免漂移

---

## 变量速查表

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| IMAGE_MODEL | 目标模型 | Midjourney v6 / NovelAI v3 / Niji 6 |
| ANIME_STYLE | 动漫风格 | 京阿尼/新海诚/蔚蓝档案/原神 |
| FACE_FEATURES | 面部特征 | 单眼皮、高鼻梁、痣的位置 |
| CHARACTER_MOOD | 性格调性 | 元气/清冷/温柔/暗黑 |
| OUTFIT_STYLE | 服装风格 | JK制服/古风/校园便服/战斗装 |
| BACKGROUND_VIBE | 背景氛围 | 樱花校园/海边夕阳/都市夜景 |
| LIGHTING_STYLE | 光照 | 黄金时刻/棚拍柔光/月光 |
| FRAMING | 构图 | 胸像/半身/全身/特写 |

---

## 模板分类索引

详细模板定义见 references/prompts.md：

- **P01-P05**：真人动漫化（5套）
- **P06-P10**：二次头像生成（5套）
- **P11-P15**：OC角色卡设计（5套）
- **P16-P19**：漫展返图救援（4套）
- **P20-P24**：CG海报制作（5套）
- **P25-P28**：CP双人图（4套）

变体Prompt见 references/prompts.md #变体与附赠

工作流组合见 references/workflows.md
