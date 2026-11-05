---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022004e56304c7b57dfe655158f846be746cd76ce50c2ec1a29b383930736a8477bd022100d935ad472b26ca3301b6b865ae3fb1f2ae3cc56aaeca603c8ef1bbaf8219340d
    ReservedCode2: 3046022100bde1426f33eb78200e986f22532f76814451a8bf49dc46e47b645279c6da473d022100a3485bf6118d155575263801d782d3f961dc51815a17011b87d4a3279f0212bf
---

# 模块间数据流向详解

## 数据流向总图

```
┌─────────────────┐
│   ThemeAnchor   │ ← 故事概念/平台/受众
└────────┬────────┘
         │ 一句话故事/赛道/价值边界
         ▼
┌─────────────────┐
│   WorldForge │ ← 规则聚焦点
└────────┬────────┘
         │ 世界规则×冲突触发点
         ▼
┌─────────────────┐
│   CharSmith     │ ← 欲望/伤口/限制
└────────┬────────┘
         │ 人物设定×关系网
         ▼
┌─────────────────┐
│   PlotFrame │ ← 事件链
└────────┬────────┘
         │ 矛盾节点
         ▼
┌─────────────────┐
│   EpBuilder     │ ← 单集目标与爆点
└────────┬────────┘
         │ 分集钩点
         ▼
┌─────────────────┐
│  ClimaxLadder   │ ← 重大反转
└────────┬────────┘
         │ 反转×高潮策划
         ▼
┌─────────────────┐
│  ThrillEngine   │ ← 爽点强度表
└────────┬────────┘
         │ 爽点分布×强度
         ▼
┌─────────────────┐
│  DialogueForge  │ ← 分集冲突
└─────────────────┘
```

## 横向数据流

### ThemeAnchor → WorldForge
- **输入**：`ThemeAnchor` 的「一句话故事/赛道/价值边界」
- **决定**：`WorldForge` 的「规则聚焦点」
- **原理**：赛道定位决定需要构建什么样的世界规则来承载冲突

### WorldForge + CharSmith → PlotFrame
- **输入**：`WorldForge` 的「规则×冲突触发点」+ `CharSmith` 的「欲望/伤口/限制」
- **驱动**：`PlotFrame` 的「事件链」
- **原理**：人物在规则下的欲望与世界的冲突碰撞产生事件

### PlotFrame → EpBuilder
- **输入**：`PlotFrame` 的「矛盾节点」
- **拆分**：`EpBuilder` 的「单集目标与爆点」
- **原理**：主线矛盾分解为每集的小冲突

### EpBuilder + ThrillEngine → PacePay
- **输入**：`EpBuilder` 的「分集钩点」+ `ThrillEngine` 的「爽点强度表」
- **布局**：`PacePay` 的「付费节点」
- **原理**：钩点与爽点结合确定最佳付费触发位置

### ClimaxLadder → PacePay
- **输入**：`ClimaxLadder` 的「重大反转」
- **对齐**：`PacePay` 的「付费前置悬念/付费后强度提升」
- **原理**：反转前的悬念是最佳付费时机

### DialogueForge ↔ EpBuilder
- **双向关系**：
  - `DialogueForge` 将「分集冲突」具体化（台词/动作）
  - 可反哺 `EpBuilder` 做微调
- **原理**：对话创作中发现的新细节反写回分集设计

### GenderTune
- **介入点**：
  - 分集冲突 (`EpBuilder`)
  - 对话冲突 (`DialogueForge`)
  - 分集节奏 (`PacePay`)
- **原理**：在「台词/场景/节奏」三处做频向微调

### ThemeLift
- **回写位置**：
  - 结局设计
  - 关键集数（第X集第Y分钟）
  - 情感曲线
- **原理**：用「主题陈述/情绪曲线/记忆锚点」回写，形成主旨闭环

## 反馈回路

```
ThemeLift ──→ PlotFrame ──→ EpBuilder
  │ │              │
  │ 回写结局 │ 修正转折点 │ 微调单集
  │主题落点     │ 矛盾升级      │
  ▼              ▼              ▼
PlotFrame ← EpBuilder ← DialogueForge
```

## 阶段划分

### 第一阶段：创意阶段
1. ThemeAnchor → 2. WorldForge → 3. CharSmith

**产出**：世界观 + 人物体系

### 第二阶段：架构阶段
4. PlotFrame → 5. EpBuilder

**产出**：主线框架 + 分集设计

### 第三阶段：优化阶段
6. ClimaxLadder → 7. ThrillEngine → 8. DialogueForge

**产出**：冲突强化 + 爽点布局 + 高张力对话

### 第四阶段：适配阶段
9. GenderTune → 10. PacePay → 11. ThemeLift

**产出**：受众适配 + 付费设计 + 主题闭环

## 快速启动模式

当用户提供的信息不完整时，可按以下模式启动：

**模式A：最小启动**（仅提供故事概念）
```
ThemeAnchor → PlotFrame → EpBuilder → PacePay
```

**模式B：人物优先**（提供人物设想）
```
CharSmith → PlotFrame → EpBuilder → ThrillEngine
```

**模式C：冲突优先**（提供核心冲突）
```
WorldForge → PlotFrame → ClimaxLadder → EpBuilder
```