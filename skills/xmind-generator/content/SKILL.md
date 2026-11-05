---
name: xmind-generator
description: 生成、创建、导出 XMind 思维导图文件，或将主题内容可视化为思维导图格式时使用。触发短语包括"生成XMind"、"创建思维导图"、"导出xmind"、"帮我做个思维导图"等。支持关系连接、概要标记、备注信息、优先级标签、主题配色、多种布局结构、文本格式化、形状样式和分支曲线等功能。
---

# XMind 思维导图生成器

## 功能概述

此技能可生成标准的 `.xmind` 思维导图文件，支持丰富的视觉元素和结构化布局。

## 使用流程

### 1. 解析用户需求

收集以下信息（通过交互表单或直接解析）：

| 参数 | 说明 | 必填 |
|------|------|------|
| title | 导图标题 | 是 |
| topics | 主题结构（支持嵌套JSON或Markdown格式） | 是 |
| structure | 布局结构类型 | 否 |
| theme | 配色主题 | 否 |
| features | 高级功能配置 | 否 |

### 2. 调用生成器

使用 `xmind_generator.py` 脚本生成文件：

```bash
python /workspace/temp-skills/xmind-generator/scripts/xmind_generator.py \
  --title "导图标题" \
  --topics topics.json \
  --output output.xmind \
  --structure logic.right \
  --theme rainbow
```

### 3. 输出文件

生成的文件保存到用户指定路径或工作目录。

## 支持的功能

### 布局结构 (structureClass)

| 值 | 说明 |
|----|------|
| `org.xmind.ui.logic.right` | 逻辑向右（默认） |
| `org.xmind.ui.logic.left` | 逻辑向左 |
| `org.xmind.ui.map` | 辐射状 |
| `org.xmind.ui.tree.right` | 树状向右 |
| `org.xmind.ui.tree.left` | 树状向左 |
| `org.xmind.ui.organization.top` | 组织图向上 |
| `org.xmind.ui.organization.bottom` | 组织图向下 |
| `org.xmind.ui.chronological.top` | 时间线向上 |
| `org.xmind.ui.chronological.right` | 时间线向右 |

### 主题配色 (colorThemeId)

| 值 | 说明 |
|----|------|
| `Rainbow-#000229-MULTI_LINE_COLORS` | 彩虹色系 |
| `Fresh-#006B3C-MULTI_LINE_COLORS` | 清新绿 |
| `Ocean-#004B66-MULTI_LINE_COLORS` | 海洋蓝 |
| `Passion-#99142F-MULTI_LINE_COLORS` | 热情红 |
| `Purple-#4D49BE-MULTI_LINE_COLORS` | 紫罗兰 |
| `Monochrome-#333333-MULTI_LINE_COLORS` | 单色调 |

### 形状样式 (shape-class)

| 值 | 说明 |
|----|------|
| `org.xmind.topicShape.roundedRect` | 圆角矩形（默认） |
| `org.xmind.topicShape.rect` | 矩形 |
| `org.xmind.topicShape.ellipse` | 椭圆 |
| `org.xmind.topicShape.underline` | 下划线 |
| `org.xmind.topicShape.none` | 无形状 |

### 分支样式 (line-class)

| 值 | 说明 |
|----|------|
| `org.xmind.branchConnection.roundedElbow` | 圆角弯曲线（默认） |
| `org.xmind.branchConnection.straight` | 直线 |
| `org.xmind.branchConnection.curved` | 曲线 |
| `org.xmind.branchConnection.bezier` | 贝塞尔曲线 |

### 高级功能

#### 关系连接 (relationships)
连接两个不相关的主题：
```json
{
  "id": "uuid",
  "end1Id": "topic1-id",
  "end2Id": "topic2-id",
  "controlPoints": {
    "0": {"x": 46.5, "y": -33.25},
    "1": {"x": 64.5, "y": 42.25}
  }
}
```

#### 概要标记 (summaries)
为多个连续主题添加概要：
```json
{
  "id": "summary-uuid",
  "range": "(0,3)",
  "topicId": "summary-topic-id"
}
```

#### 备注信息 (notes)
为主题添加详细说明：
```json
{
  "content": "这是备注内容，支持多行文本..."
}
```

#### 标签标记 (labels)
为主题添加视觉标记：
```json
{
  "priority": 1,
  "task": {"status": "inProgress"}
}
```

#### 文本格式
```json
{
  "fontFamily": "Droid Serif",
  "fontSize": "18pt",
  "fontWeight": "400",
  "fontStyle": "normal",
  "color": "#000229"
}
```

## 主题级别配置

### 中心主题 (centralTopic)
- 默认字体大小：30pt
- 默认线宽：3pt
- 默认颜色：#000229

### 主分支 (mainTopic)
- 默认字体大小：18pt
- 默认线宽：继承

### 子主题 (subTopic)
- 默认字体大小：14pt
- 默认线宽：2pt

## 输出规范

- 文件格式：`.xmind` (ZIP压缩包)
- 编码：UTF-8
- JSON结构版本：2
- 布局引擎版本：3

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 缺少标题 | 提示用户输入 |
| 无效的topic ID | 使用自动生成的UUID |
| 文件写入失败 | 提示检查路径权限 |

## 参考资源

- 详细配置示例：`references/examples.md`
- 完整参数参考：`references/full_reference.md`
- API使用模板：`assets/templates/`

## 完整示例

### 简单JSON格式（推荐）

```json
{
  "root": "导图标题",
  "topics": [
    {
      "title": "主题1",
      "notes": "这是主题1的备注说明",
      "topics": [
        {"title": "子主题1.1"},
        {"title": "子主题1.2"}
      ]
    },
    {
      "title": "主题2",
      "labels": ["priority-high"],
      "topics": [
        {"title": "子主题2.1"},
        {"title": "子主题2.2"}
      ]
    }
  ]
}
```

### 标准JSON格式（兼容旧版本）

```json
{
  "root": "导图标题",
  "structure": {
    "topics": [
      {
        "title": "主题1",
        "notes": {
          "plain": {
            "content": "备注内容"
          }
        },
        "topics": [
          {"title": "子主题1.1"},
          {"title": "子主题1.2"}
        ]
      }
    ]
  }
}
```

### 使用方法

```bash
python /workspace/.minimax/skills/xmind-generator/scripts/xmind_generator.py \
  --title "我的思维导图" \
  --topics topics.json \
  --output output.xmind \
  --theme ocean
```

### Markdown格式

```bash
python xmind_generator.py \
  --title "项目计划" \
  --markdown "# 项目计划\n## 需求分析\n### 用户调研\n## 设计阶段\n### UI设计" \
  --output project_plan.xmind
```
