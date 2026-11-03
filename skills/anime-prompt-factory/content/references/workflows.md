# 组合工作流

> 三套经过验证的 Prompt 链，覆盖完整创作路径

---

## 工作流 A · 角色诞生流

**适用场景**：从零开始创作一个完整的OC角色，获得全套视觉素材

**预计时长**：3小时（包含迭代时间）

**Prompt链**：

```
P11 OC三视图
    ↓
P13 OC技能卡
    ↓
P21 番剧PV海报
    ↓
附赠 表情包九宫格
```

### 第一步：P11 OC三视图

**目标**：建立角色的基础视觉身份

**输入变量**：
```
OC_NAME_LORE: [角色名 + 一句话世界观]
AGE_GENDER: [年龄 + 性别]
RACE_IDENTITY: [种族/身份]
BODY_TYPE: [体型]
APPEARANCE_DETAILS: [外观特征]
OUTFIT_THEME: [服装主题]
SIGNATURE_ELEMENT: [标志性元素]
WEAPON: [武器]
```

**输出**：
- 三视图主Prompt（正面/侧面/背面）
- 负面Prompt
- 角色设定档文本

### 第二步：P13 OC技能卡

**目标**：为角色设计游戏风格的能力展示

**输入变量**：
```
CARD_THEME_COLOR: [基于三视图的配色]
ELEMENT_TYPE: [元素属性]
RARITY: [稀有度 1-6星]
POSE: [释放技能瞬间/独站持武器]
DECORATION_MOTIF: [装饰主题]
```

**输出**：
- 技能卡主Prompt
- 负面Prompt
- 技能描述（1主动+1被动+1大招）

### 第三步：P21 番剧PV海报

**目标**：产出角色的高光时刻视觉

**输入变量**：
```
ANIME_TITLE_LORE: [世界观设定沿用]
MAIN_CHARACTER: [沿用P11外观描述]
TITLE_POSITION: [底部居中/顶部/左侧竖排]
WORLD_BACKGROUND: [基于设定的背景]
COLOR_GRADING: [紫蓝主调+金色高光]
EMOTIONAL_TONE: [决战前夕/希望与绝望并存]
```

**输出**：
- 番剧风海报Prompt
- 参数建议
- 标题文案建议

### 第四步：表情包九宫格

**目标**：为角色创建可复用的表情素材

**输入变量**：
```
OC基础设定: [沿用P11-P13的角色设定]
表情列表: [微笑/大哭/生气/卖萌/傲娇/无语/得意/慌张/温柔]
宫格数: [9宫格（推荐）/ 12宫格 / 16宫格]
```

**输出**：9张连贯的表情图Prompt

### 产出物清单

| 素材 | 用途 |
|------|------|
| 三视图 | 角色设计档案、周边制作基底 |
| 技能卡 | 游戏化内容、社交媒体展示 |
| PV海报 | 宣发素材、壁纸 |
| 表情包 | 社交互动、二创素材 |

---

## 工作流 B · 漫展救援流

**适用场景**：将漫展/Cos照片转化为可用于不同平台的优质内容

**预计时长**：1-2小时

**Prompt链**：

```
P16 光线救援
    ↓
P17 背景替换
    ↓
P18 妆容增强
```

### 第一步：P16 光线救援

**目标**：修复展馆恶劣光线，重建专业光照

**输入变量**：
```
IMAGE_MODEL_OR_TOOL: [SD WebUI / ComfyUI / Midjourney]
COS_CHARACTER: [Cos的角色]
TARGET_LIGHTING: [黄金时刻顺光/棚拍柔光/夕阳逆光剪影]
TARGET_BACKGROUND: [原背景虚化/替换为XX]
```

**输出**：
- img2img/inpaint 指令
- denoising strength 建议（0.35-0.45）
- inpaint 区域建议

**避坑提醒**：
- denoising 不要超过0.5，否则Cos服细节会丢失
- 面部区域不要进inpaint蒙版

### 第二步：P17 背景虚化替换

**目标**：让人物从嘈杂展馆中"脱离"

**输入变量**：
```
替换场景: [樱花树下/海边黄昏/神殿废墟/云端/二次元背景板]
```

**输出**：
- 背景替换Prompt
- 边缘融合建议

**可选变体**：
- 半二次元化：保留照片质感但动漫化
- 全CG化：完全转换为二次元风格

### 第三步：P18 妆容增强

**目标**：提升Cos妆的细节表现

**输入变量**：
```
强化部位: [眼妆/唇妆/假睫毛/高光/整体协调]
角色妆容关键词: [基于Cos角色的妆容描述]
```

**输出**：
- 妆容增强Prompt
- Inpaint局部区域建议

### 产出物清单

| 素材 | 平台建议 |
|------|---------|
| 原片修复版 | 微博、小红书原图党 |
| 半二次元化版 | B站、抖音过渡风格 |
| 全CG化版 | 二次元专属平台、同人创作 |

---

## 工作流 C · 头像系列号流

**适用场景**：打造小红书/微博头像号的长期发图节奏

**预计时长**：2-3小时

**Prompt链**：

```
P06 萌系头像（春版）
    ↓
变体 季节微调（夏/秋/冬）
```

### 第一步：基础版 P06 萌系头像

**输入变量**：
```
CHARACTER_TYPE: [猫娘/兔耳娘/元气JK/邻家姐姐]
COLOR_THEME: [主色+辅色选择]
HAIR_STYLE_COLOR: [发型+发色]
EYE_COLOR: [瞳色]
ACCESSORY: [配饰1-2件]
EXPRESSION: [微笑]
BACKGROUND_TYPE: [纯色/几何渐变]
```

**输出**：
- 春版主Prompt
- 参数组合（保守/标准/激进）
- 春季限定元素建议

### 第二步：季节变体

**变体元素叠加**：

| 季节 | 背景/元素叠加 | 色调调整 |
|------|-------------|---------|
| 春版 | 樱花、粉色系、春风 | 暖粉 #FFB7C5 |
| 夏版 | 海浪、蓝天、蝉鸣 | 清新蓝绿 #87CEEB |
| 秋版 | 红叶、枫叶、暖阳 | 枫叶红 #D2691E |
| 冬版 | 雪花、围巾、暖灯 | 冷蓝白 #E6F3FF |

### 四季示例Prompt扩展

**春版叠加**：
```
...cherry blossom petals falling, spring breeze,
pink sakura gradient background, romantic spring atmosphere
```

**夏版叠加**：
```
...ocean waves background, summer sunset, clear blue sky,
tropical flowers, refreshing summer vibes
```

**秋版叠加**：
```
...autumn maple leaves falling, golden hour warm lighting,
red and orange foliage background, cozy autumn atmosphere
```

**冬版叠加**：
```
...snowflakes falling, winter night sky, warm street lamp glow,
scarf around neck, soft white snow background
```

### 统一性保障技巧

1. **固定视觉锚点**：
   - 瞳色、发型基础款不变
   - 只变化背景和配饰季节元素

2. **参数一致性**：
   - 建议固定 stylize 值（如180）
   - 固定 aspect ratio（如 1:1）
   - 使用同一 IMAGE_MODEL

3. **批处理建议**：
   - 先生成春版，确定满意后
   - 只修改背景/季节元素关键词
   - 保持其他参数完全一致

### 产出物清单

| 素材 | 用途 |
|------|------|
| 四季头像×4 | 头像号主视觉 |
| 季节文案 | 配合图片的社媒文案 |
| 系列感说明 | 统一账号风格定位 |

---

## 工作流选择指南

| 你的需求 | 推荐工作流 |
|---------|-----------|
| 从零创作OC，有完整世界观 | A 角色诞生流 |
| 漫展/Cos照片后期处理 | B 漫展救援流 |
| 打造头像系列账号 | C 头像系列号流 |
| 快速出单张高质量图 | 单独使用对应分类Prompt |

---

## 高级技巧

### 技巧1：风格混搭

把不同分类的关键词叠加，能产生意想不到的效果：

**示例**：BA光环 + 番剧PV构图
```
[BA相关]
glowing halo above head with geometric fragments,
Millennium Science school uniform
[PV构图]
cinematic composition, character occupies left third,
dramatic atmosphere
```

### 技巧2：负面词定制

针对你具体出现的问题定制负面词：

**常见问题 → 追加负面词**：
| 问题 | 追加负面词 |
|------|-----------|
| 总是画成猫耳 | `cat ears, animal ears, no animal features` |
| 服装总是不对 | `wrong costume, inaccurate clothing` |
| 背景太乱 | `cluttered background, busy background` |
| 脸型漂移 | `identity drift, different face shape` |

### 技巧3：LLM自我审查

生成Prompt后，让LLM用一句话评价可能出问题的地方：

```
Prompt: "请检查上面生成的Prompt，指出哪里可能有冲突词或可能导致出图问题。"
```

这一步能帮你省好几次试错。
