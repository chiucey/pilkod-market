---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 903f9a9c030e1e589d0285cda6547490
    PropagateID: 903f9a9c030e1e589d0285cda6547490
    ReservedCode1: 30440220468dd92253573c43ee05e70f6248d067e14c20903cd744706c66e4d4d0cedda60220408de6f26e62ca8e5cdbdc8b896ae59012bff05245f3a44f66993efc3e72e87e
    ReservedCode2: 3046022100fdcf48bbc1b149e3164d748d898f9baa8e834a977180e374d65d32855372d46b022100f1f051026c6e7b2b41d52ce1f92da9f7d95d51940fdca6999c7fc9903f260e0d
description: Xiaohongshu cartoon infographic series generator. Use when users mention "Xiaohongshu images", "XHS images", "RedNote infographics", "Xiaohongshu promotion", "social media infographic", or need to generate 1-10 cartoon-style image cards for Xiaohongshu/RedNote platform. Supports 11 visual styles (cute/fresh/warm/bold/minimal/retro/pop/notion/chalkboard/study-notes/screen-print) and 8 layouts (sparse/balanced/dense/list/comparison/flow/mindmap/quadrant).
name: xhs-cartoon-infographics
---

# XHS Cartoon Infographics Generator

小红书图文系列生成器 - 将复杂内容拆分为适合小红书平台的卡通风格图文卡片。

## 核心能力

- **多风格支持**：11种视觉风格自由切换
- **灵活布局**：8种信息布局模式
- **智能拆分**：自动将内容拆分为1-10张图片
- **风格一致**：使用参考图链确保系列视觉统一

## 工作流程

### 1. 内容分析

分析输入内容，识别：
- 内容类型（种草/干货/测评/教程/避坑）
- 关键卖点
- 目标受众
- 最佳视觉策略

### 2. 策略选择

三种差异化策略：

| 策略 | 特点 | 适用场景 |
|------|------|----------|
| A: 故事驱动 | 情感共鸣，个人经历为主线 | 评测、个人分享、转变故事 |
| B: 信息密集 | 价值优先，高效信息传递 | 教程、对比、产品评测 |
| C: 视觉优先 | 视觉冲击，氛围感强 | 高颜值产品、生活方式 |

### 3. 风格 + 布局组合

**11种视觉风格**：
- `cute` - 甜美可爱，少女风
- `fresh` - 清新自然
- `warm` - 温馨友好
- `bold` - 强视觉冲击
- `minimal` - 极简高级
- `retro` - 复古怀旧
- `pop` - 活力潮流
- `notion` - 手绘线稿，知性
- `chalkboard` - 黑板粉笔，教育风
- `study-notes` - 手写笔记风格
- `screen-print` - 丝网印刷，海报风

**8种布局模式**：
- `sparse` - 稀疏留白，重点突出
- `balanced` - 平衡布局，3-4个要点
- `dense` - 密集信息，知识卡片
- `list` - 清单枚举，排行榜
- `comparison` - 对比布局
- `flow` - 流程时间线
- `mindmap` - 中心放射思维导图
- `quadrant` - 四象限分类

### 4. 图片生成

使用 `image_synthesize` 工具生成卡通风格图片：

```bash
# 封面图（第一张）- 建立视觉锚点
image_synthesize(prompt="[基于策略和风格的详细描述]", output_file="01-cover.png")

# 内容图（后续图片）- 使用参考图保持一致
image_synthesize(prompt="[详细描述]", input_files=["01-cover.png"], output_file="02-content.png")
```

**关键原则**：
1. **首图锚点**：封面图确定整体视觉风格
2. **参考链**：后续图片使用封面作为参考
3. **风格卡片**：每张图片需包含风格元素（装饰、文字框、强调符号）

## 内容拆分原则

| 图片位置 | 类型 | 布局建议 | 内容策略 |
|----------|------|----------|----------|
| P1 | 封面 | sparse | 钩子 + 视觉冲击 |
| P2-P(N-1) | 内容 | balanced/dense/list | 核心价值分点 |
| PN | 结尾 | sparse/balanced | CTA/总结 |

## 快速预设

| 预设 | 风格 | 布局 | 适用场景 |
|------|------|------|----------|
| knowledge-card | notion | dense | 干货知识卡 |
| cute-share | cute | balanced | 少女种草 |
| warning | bold | list | 避坑指南 |
| tutorial | chalkboard | flow | 教程步骤 |
| poster | screen-print | sparse | 海报封面 |

## 输出文件结构

```
xhs-infographics/
├── 01-cover-[slug].png      # 封面
├── 02-content-[slug].png    # 内容页
├── ...
├── NN-ending-[slug].png     # 结尾
└── prompts/                 # 提示词备份
    ├── 01-cover.md
    └── ...
```

## 视觉元素配置

根据风格自动配置：
- 背景（纯色/渐变/纹理）
- 装饰元素（云朵/星星/植物/几何）
- 文字强调（花字/标签/箭头）
- 边框样式（圆角/手绘/几何）

详细定义见 `references/` 目录。

## 质量检查

生成后验证：
- [ ] 风格一致性（人物/配色/线条）
- [ ] 信息完整性（所有要点覆盖）
- [ ] 可读性（文字清晰，层级分明）
- [ ] XHS适配（竖版比例，建议3:4）
