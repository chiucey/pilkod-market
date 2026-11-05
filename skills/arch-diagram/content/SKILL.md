---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4fc0d8ea0812608189e80fc20d89338b
    PropagateID: 4fc0d8ea0812608189e80fc20d89338b
    ReservedCode1: 30460221008048865d9201632cacd4b4eb672dc6c527662450755eee149b59e8cacc2e61a8022100ad2f114cb3e1ae7e1411dbc8ce67f83c6d74f7f20f6982991ab1152623282f79
    ReservedCode2: 304502200c0eb34274b197b0c4d6f540421c9927ff847ba99879f8cb04e6f35097832045022100fa6af977c35fec2932512f2d37bbf93749a731ee3b339758c8e2abb6a15bd8aa
description: 企业级 IT/AI 系统架构图生成技能。当用户需要画架构图、系统拓扑图、分层结构图、技术架构图时激活，支持从文案描述或大纲自动生成图像。适用场景：AI战略规划图、IT系统架构图、云原生架构图、企业技术中台架构图、微服务架构图、Agent 全栈架构图。输出 draw.io XML（可编辑）或 AI 生图（高清图片）。
name: arch-diagram
---

# Arch Diagram - 企业级架构图生成技能

## 核心能力

将文案大纲或结构化描述 → 转换为：
1. **AI 高清架构图**（默认，快速精美）
2. **draw.io XML 文件**（可导入 draw.io 编辑）

---

## 架构图设计规范（必须遵循）

### 布局规则

- **层级顺序**：自下而上，从基础设施到应用场景（除非用户指定倒置）
- **层数控制**：5～7 层为宜（过多则拥挤，过少则信息不足）
- **层级标题**：每层顶部置中，用深色横条+白色粗体字，宽度撑满整图
- **模块卡片**：纯矩形，无阴影、无渐变、无圆角（或极小圆角 2px）
- **间距**：模块之间留 8-12px 空隙，同层模块高度对齐
- **列布局**：支持单栏、双栏、三栏并列（按内容密度选择）

### 颜色规范

```
基础设施层：  #2D3748 (深灰)
数据平台层：  #4A5568 (中灰)
模型/能力层： #3182CE (中蓝) 或 #805AD5 (紫)
开发平台层：  #4299E1 (浅蓝)
应用场景层：  #38B2AC (青绿) 或 #319795 (深青)
模块背景色：  #EDF2F7 (浅灰白) 白色模块用 #F7FAFC
文字颜色：    深色背景用白色 #FFFFFF，浅色背景用 #1A202C
强调色：      #3182CE (蓝)  #38A169 (绿)  #D69E2E (金)  #E53E3E (红)
```

### 连接线规则

**默认：无连接线**。层与层之间通过垂直堆叠的紧密感暗示调用关系。
如需箭头，在两栏之间用细虚线表示，不使用实体箭头。

### 字体与排版

- 层级标题：14-16px，加粗，白色
- 子模块标题：12px，加粗，深色
- 模块内容：10-11px，常规，深色
- 全部使用无衬线字体（微软雅黑 / Source Han Sans / Noto Sans CJK）
- 中英文混排时中文优先

---

## 工作流程

### Step 1：提取架构层次

分析用户提供的内容，识别：
- 有哪些逻辑层级（从底到顶）
- 每层包含哪些模块
- 是否存在"两横"/"三纵"等特殊结构

**常见层级模板**：

```
Tier 1 (底层/底座)：基础设施层
  - 计算、存储、网络、安全

Tier 2：数据平台层
  - 数据湖 / 数据仓库 / 数据治理 / ETL

Tier 3：模型与知识层
  - 大模型 / 知识图谱 / RAG / 向量数据库

Tier 4：平台工具层
  - AI 中台 / 开发平台 / 运维平台

Tier 5：应用场景层
  - 具体业务应用 / Agent / 对外服务
```

### Step 2：选择输出格式

| 场景 | 推荐格式 |
|------|---------|
| 快速演示 / 汇报 | AI 生图 |
| 需要后续编辑标注 | draw.io XML |
| 追求像素级精准 | draw.io XML + AI 生图对照 |

### Step 3：生成图像（AI 生图模式）

根据层级结构构建生图 prompt，包含：
1. 布局描述（垂直堆叠、层数、每层模块列表）
2. 颜色规范（精确色值）
3. 禁止项（无阴影、无渐变、无3D效果）
4. 风格锁定（draw.io flat style, enterprise architecture diagram）

**生图 Prompt 模板**：

```
Professional enterprise [行业] [系统类型] architecture diagram, 
vertical stacked layered style on white background.

[层级数] horizontal layers stacked bottom to top, each layer has:
- Dark colored header bar with white bold layer name at top of each section
- Grid of white/light colored rectangle cards below header
- NO connection lines between layers, use proximity stacking
- NO shadows, NO gradients, NO 3D effects
- Flat enterprise corporate style, clean geometric shapes

Bottom layer (Foundation): [模块列表]
Layer 2: [模块列表]
Layer 3: [模块列表]
Top layer (Application): [模块列表]

Color palette: [精确色值]
Text: Chinese primary labels, clean sans-serif, centered in cards
Aspect ratio: 16:9
```

### Step 4：生成 draw.io XML（可选）

为每一层创建 `<mxCell>` 节点，按 draw.io XML schema 组装。

draw.io XML 核心结构：
```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <!-- Layer Group -->
    <mxCell id="layer1" value="Layer Name" style="shape=rect;fillColor=#XXXXXX;fontStyle=1;fontColor=#FFFFFF;" vertex="1" parent="1"/>
    <!-- Module Cards -->
    <mxCell id="mod1" value="Module" style="shape=rect;fillColor=#YYYYYY;strokeColor=#CCCCCC;rounded=0;" vertex="1" parent="1"/>
  </root>
</mxGraphModel>
```

**颜色填充规则（draw.io）**：
- 层级标题行：`fillColor=[层级主色];fontColor=#FFFFFF;fontStyle=1`
- 模块卡片：`fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1`
- 选中/重点：`fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=2`

---

## 典型布局模式

### 模式 A：标准金字塔（战略规划类）
```
        [应用/战略层 - 尖顶]
    [平台/能力层]
  [基础设施/数据层]
```
用于：AI战略规划、技术路线图

### 模式 B：全栈分层（技术架构类）
```
[应用场景层]
[平台工具层]
[模型知识层]
[数据平台层]
[基础设施层]
```
用于：AI全栈架构、IT系统架构、云原生架构

### 模式 C：矩阵型（三纵+两横）
```
  [统一入口平台]
产品能力 | 组织能力 | 个人能力
  自建层 + 引入层
    治理/底座
```
用于：有明确职能分工的企业架构

---

## 参考资料

- `references/architecture-patterns.md` — 常见行业架构模板（AI、汽车、金融、电商）
- `references/drawio-templates.md` — draw.io XML 模板与 schema 说明
- `references/color-palettes.md` — 行业配色方案参考

---

## 输出规范

生成文件一律保存到 `/workspace/output/[主题]-[日期].png` 或 `/workspace/output/[主题]-[日期].xml`，
在回复中直接展示图片或提供 XML 文件下载。
