---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4fa3ef82dea005d59bec42d346f75293
    PropagateID: 4fa3ef82dea005d59bec42d346f75293
    ReservedCode1: 304502206b174f7e84652eed89c639b992618298a1379f7fba8810c19180725c72ff8d2d022100fe01d97282be80367c684cb7444ac472e25c00fb572232b1f0ab8668bfce63ef
    ReservedCode2: 304502210086dc53dd47b3c3195c2c463556d793bbe3a1b6a46beb3bff02bd74cc4aab0b0c022020e65edebd93f6cc2d7b6414aba22de935d0c782cdffd8774811ea3ee0efd737
description: 四模型CLI Agent优化矩阵。MiMo/Gemini/Claude/通用模型选型决策树+参数速查表。
name: cli-agent-universal-matrix
platforms:
    - OpenClaw
tags:
    - model-optimization
    - universal-matrix
    - MiMo
    - Gemini
    - Claude-Code
    - decision-matrix
version: 1.0.0
---

# 通用AI模型CLI Agent优化矩阵
> 版本：v1.0.0
> 来源：Claude Code架构研究 × MiMo × Gemini优化指南整合
> 定位：模型选型决策台 / 架构迁移手册

---

## 核心结论

```
Claude Code的12层Harness中：
  → 约70%是模型无关的，任何支持function calling的模型都能用
  → 约20%需要调整参数（压缩阈值、工具描述长度）
  → 约10%是Claude/模型专属的，无法迁移
```

---

## 一、模块迁移矩阵（模型无关 vs 专属）

| 模块 | 模型无关？ | 复用难度 | 说明 |
|------|-----------|---------|------|
| **核心代理循环** | ✅ 完全 | 低 | while(true)+tool_use循环，任何function calling模型 |
| **工具系统(buildTool)** | ✅ 完全 | 低 | validate→perm→call生命周期与模型无关 |
| **权限系统(5层)** | ✅ 完全 | 中 | Hook/规则/提示与模型无关 |
| **上下文压缩框架** | ✅ 完全 | 中 | 框架通用，阈值需调整 |
| **子Agent隔离** | ✅ 完全 | 低 | messages[]隔离，通用 |
| **Feature Flag+DCE** | ✅ 完全 | 低 | 构建时技术，与模型无关 |
| **MCP集成** | ✅ 完全 | 低 | 开放协议 |
| **KAIROS自主框架** | ✅ 框架 | 中 | 心跳/自主执行框架可复用 |
| **桥接层** | ⚠️ 部分 | 高 | 协议通用，认证体系依赖Anthropic |
| **Capybara v8补丁** | ❌ 专属 | N/A | 针对特定模型bug |
| **卧底模式** | ❌ 专属 | N/A | Anthropic组织级需求 |
| **遥测体系** | ⚠️ 部分 | 中 | 框架通用，端点/Token专属 |
| **代号保护** | ❌ 专属 | N/A | Anthropic IP保护 |

---

## 二、模型选型决策树

```
任务来了 → 用哪个模型？
  │
  ├─ 上下文窗口分析
  │   ├─ < 200K tokens → MiMo方案
  │   ├─ 200K - 500K → 通用方案（Claude优化版）
  │   └─ > 500K → Gemini方案
  │
  ├─ 任务类型
  │   ├─ coding/函数调用 → MiMo（代码能力强）
  │   ├─ 大型代码库分析 → Gemini（窗口大+并行）
  │   ├─ 多模态任务 → Gemini（原生支持）
  │   ├─ 7×24自主运行 → Claude Code（KAIROS）
  │   └─ 写作/创意 → OpenClaw路由表 → 分发到expert
  │
  └─ 特殊需求
      ├─ 减少幻觉 → Gemini + Search Grounding
      ├─ 实时搜索 → Gemini + Grounding
      └─ 终端生态 → Claude Code
```

---

## 三、四模型优化参数速查

| 参数 | Claude默认值 | MiMo优化 | Gemini优化 | 通用建议 |
|------|------------|---------|----------|--------|
| COMPRESSION_THRESHOLD | 80% | **60%** | **95%** | 窗口越小越激进 |
| SNIP_THRESHOLD | 70% | **45%** | **70%** | 按需调整 |
| HARD_TRUNCATE | 95% | **90%** | **99%** | 保守 |
| SESSION_BUDGET | 50K | 30K | **500K** | 窗口的40-60% |
| 工具并行 | 串行 | 串行 | **并行默认** | 无依赖则并行 |
| 工具描述长度 | 50字 | **≤30字** | 50字 | 按窗口大小调整 |
| 多模态 | 基础 | 有限 | **原生** | 按模型能力 |
| Search Grounding | 无 | 无 | **有** | Gemini独家 |

---

## 四、模型专属能力地图

```
MiMo（小米）：
  ✅ function calling
  ✅ reasoning mode (think tokens)
  ✅ OpenAI-compatible SDK
  ⚠️ 窗口较小 → 需激进压缩
  ⚠️ 多模态有限

Gemini（谷歌）：
  ✅ 1M-2M窗口
  ✅ 并行function calling
  ✅ 原生多模态（图像/视频/音频）
  ✅ Google Search Grounding
  ✅ 内置Code Execution
  ❌ 7×24自主运行不支持

Claude（Anthropic）：
  ✅ 最强代码补全（Sonnet 4）
  ✅ KAIROS 7×24自主
  ✅ 终端UI生态
  ✅ 安全过滤最成熟
  ❌ 窗口较小（200K）

通用（其他模型）：
  ✅ 原理可复用
  ⚠️ 按窗口大小选压缩策略
  ⚠️ 工具系统按需精简
```

---

## 五、OpenClaw多模型路由建议

```json
{
  "model_routing": {
    "短任务（<10K token）": {
      "model": "MiMo",
      "reason": "成本低，响应快"
    },
    "写作任务（10K-50K）": {
      "model": "Claude",
      "reason": "写作质量最高，expert系统完整"
    },
    "大型分析（>100K）": {
      "model": "Gemini",
      "reason": "1M窗口，不用压缩"
    },
    "实时搜索任务": {
      "model": "Gemini",
      "reason": "Search Grounding减少幻觉"
    },
    "自主7×24监控": {
      "model": "Claude + KAIROS",
      "reason": "唯一支持KAIROS模式"
    }
  }
}
```

---

## 六、架构复用优先级

| 优先级 | 模块 | 工作量 | 收益 |
|--------|------|--------|------|
| 🔴 P0 | 工具生命周期（buildTool精简版） | 1天 | 所有模型通用 |
| 🔴 P0 | 压缩阈值配置化 | 2小时 | 按模型自动切换 |
| 🟡 P1 | 子Agent隔离模板 | 1天 | 多Agent稳定性 |
| 🟡 P1 | MCP集成标准化 | 2天 | 扩展工具生态 |
| 🟢 P2 | KAIROS式心跳框架 | 3天 | 自主运行能力 |
| 🟢 P2 | Gemini并行function calling | 1天 | 效率3-5倍提升 |

---

*版本：v1.0.0 | 2026-04-02*
*完整参考：`/workspace/技术研究/Claude_Code多模型优化/通用矩阵/原文.md`*
