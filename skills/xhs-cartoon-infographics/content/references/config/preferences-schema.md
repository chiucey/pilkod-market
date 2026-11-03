# Preferences Schema

## EXTEND.md Configuration

Location: Project directory `.baoyu-skills/baoyu-xhs-images/EXTEND.md`

## Schema

```yaml
version: "1.0"

# Language preference
language: zh-CN  # zh-CN | en-US | auto

# Watermark settings
watermark:
  enabled: false  # true | false
  text: ""        # Watermark text
  position: bottom-right  # top-left | top-right | bottom-left | bottom-right
  opacity: 0.3    # 0.1 - 1.0

# Default style and layout
defaults:
  style: auto     # auto | cute | fresh | warm | bold | minimal | retro | pop | notion | chalkboard | study-notes | screen-print
  layout: auto    # auto | sparse | balanced | dense | list | comparison | flow | mindmap | quadrant

# Output settings
output:
  format: png     # png | jpg
  quality: high   # standard | high
  naming: "{index}-{type}-{slug}"  # File naming pattern

# Style preferences (custom overrides)
styles:
  cute:
    custom_colors: []  # Override default colors
    custom_decorations: []  # Add custom decorations
  # ... other styles
```

## First-Time Setup Questions

### Q1: Language

**Question**: 请选择您偏好的内容语言 / Please select your preferred language

| Option | Description |
|--------|-------------|
| 中文 | 中文内容优先 |
| English | English content preferred |
| Auto | 根据内容自动检测 |

### Q2: Watermark

**Question**: 是否添加水印？/ Add watermark to images?

| Option | Description |
|--------|-------------|
| 否 (No) | 不添加水印 |
| 是 (Yes) | 添加文字水印 |

### Q3: Default Style

**Question**: 偏好的视觉风格？/ Preferred visual style?

| Option | Style | Description |
|--------|-------|-------------|
| 自动 | auto | 根据内容自动推荐 |
| 甜美可爱 | cute | 少女风、粉色系 |
| 清新自然 | fresh | 绿色系、自然感 |
| 温馨友好 | warm | 暖色调、亲切感 |
| 强视觉 | bold | 高对比、冲击力 |
| 极简高级 | minimal | 简洁留白、专业感 |
| 复古怀旧 | retro | 焦糖色、经典感 |
| 活力潮流 | pop | 彩虹色、年轻态 |
| 知性手绘 | notion | 线稿图、知识感 |
| 黑板粉笔 | chalkboard | 教育风、学习笔记 |
| 手写笔记 | study-notes | 真实手写、标注风 |
| 丝网印刷 | screen-print | 海报风、艺术感 |

### Q4: Default Layout

**Question**: 偏好的布局模式？/ Preferred layout mode?

| Option | Layout | Description |
|--------|--------|-------------|
| 自动 | auto | 根据内容自动推荐 |
| 稀疏留白 | sparse | 封面风、重点突出 |
| 平衡布局 | balanced | 标准内容、均衡分区 |
| 密集信息 | dense | 干货卡、高信息量 |
| 清单枚举 | list | 排行风、步骤列表 |
| 对比布局 | comparison | 左右对比、正反分析 |
| 流程时间线 | flow | 步骤风、教程流程 |
| 思维导图 | mindmap | 中心放射、知识脉络 |
| 四象限 | quadrant | 分类风、矩阵分析 |
