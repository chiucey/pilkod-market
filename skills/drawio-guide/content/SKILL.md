---
name: drawio-guide
license: MIT
metadata:
  version: "7.0"
  category: diagram-visualization
  author: MiniMax Agent
  sources:
    - "draw.io Official Documentation"
    - "diagrams.net Shape Library"
triggers:
  - draw.io
  - diagrams.net
  - flowchart
  - 流程图
  - 组织架构图
  - 业务流程图
  - 画图
  - 图形图表
  - 行政图示
  - drawio教程
  - 怎么画图
description: >
  This skill should be used when users need help with draw.io (diagrams.net) for creating
  flowcharts, organizational charts, business process diagrams, or administrative visualizations.
  Supports Chinese administrative document diagrams, academic research frameworks, meeting flowcharts,
  and more. Use this skill whenever the user wants to create, edit, or export diagrams.
---

# drawio-guide

draw.io（又称 diagrams.net）是一款免费、跨平台的在线图表制作工具，无需安装即可使用。

## Quick Start

### 访问方式

1. **在线版**：访问 https://app.diagrams.net/
2. **桌面版**：下载安装包（Windows/Mac/Linux均支持）
3. **无需注册**即可使用基本功能

### 基础界面

- **左侧**：图形库（常用形状、基本流程图、形状库）
- **中间**：画布编辑区
- **右侧**：样式面板（颜色、线条、阴影等）
- **顶部**：菜单栏（文件、编辑、查看、排列等）

## Task Guide

### Task 1: 组织架构图

行政工作中最常用的图示类型。

**操作步骤：**
1. 选择空白模板 → "基本" → "组织结构图"
2. 或手动创建：从左侧拖入"流程图形状" → "主管"
3. 依次添加"副主管"、"员工"等形状
4. 使用 **连接线** 连接各层级
5. 编辑文字：双击形状输入内容
6. 调整布局：使用"排列" → "分布"自动对齐

### Task 2: 业务流程图

用于展示工作流程、审批流程等。

**常用符号：**

| 符号 | 名称 | 用途 |
|-----|------|-----|
| 矩形 | 流程/处理 | 表示具体操作步骤 |
| 菱形 | 判断 | 表示条件分支 |
| 椭圆形 | 开始/结束 | 表示流程起点和终点 |
| 箭头 | 连接线 | 表示流程方向 |

### Task 3: 导出高分辨率图片

1. 文件 → 另存为 → 选择格式
2. 推荐格式：**PNG**（常用，透明背景）、**SVG**（矢量）、**PDF**（打印）
3. 高级导出：调整缩放比例（论文建议 2x 或 3x）

### Task 4: 快捷键

| 快捷键 | 功能 |
|-------|------|
| Ctrl + C / V | 复制 / 粘贴 |
| Ctrl + Z | 撤销 |
| Ctrl + G | 成组 |
| Ctrl + D | 复制并偏移 |
| TAB | 在形状内添加标签 |

### Task 5: AI辅助绘图

利用AI大模型加速draw.io图形创建。

**方法：让AI生成 Mermaid 或 PlantUML 代码，在 draw.io 中选择"文件" → "打开" → 粘贴代码**

draw.io 支持直接解析 Mermaid 语法。

## Workflow Decision Tree

```
用户请求 → 判断图示类型
    ↓
├─ 组织架构图 → Task 1
├─ 业务流程图 → Task 2
├─ 导出图片 → Task 3
├─ 快捷键 → Task 4
├─ AI辅助绘图 → Task 5
└─ 其他 → 参考 references/
```

## References

| 文件 | 说明 |
|------|------|
| references/admin-flowchart-templates.md | 行政常用流程图模板（26个场景） |
| references/shapes-guide.md | draw.io 形状库完整指南 |
| references/ai-prompts.md | AI辅助绘图提示词模板库 |
| references/team-collab.md | 团队协作最佳实践 |

## Assets

| 文件 | 用途 |
|------|------|
| assets/flowchart-basics.drawio | 基础流程图模板 |
| assets/swimlane-template.drawio | 泳道流程图模板 |
| assets/framework-template.drawio | 学术研究框架图 |

## Scripts

| 脚本 | 功能 |
|------|------|
| scripts/batch_style.py | 批量应用预设样式到图形 |
| scripts/gen_template.py | 命令行生成流程图模板 |

**使用方法：**
```bash
# 批量应用样式
python scripts/batch_style.py 行政蓝 output.drawio

# 生成模板
python scripts/gen_template.py 公文处理
```
