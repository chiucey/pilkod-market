---
name: nano-research
description: 端到端自主 AI 科研引擎，用于从研究想法到完整论文的自动化。当用户要求进行学术研究、生成论文、运行实验、分析结果、自动撰写 LaTeX 论文，或需要 AI 辅助科研流程时使用。支持 NeurIPS/ICML/arXiv 等多格式论文输出。
---

# NanoResearch 技能

端到端自主 AI 科研引擎，自动化完整的科学研究流程——从研究想法到完整论文。

## 核心能力

| 能力 | 说明 |
|------|------|
| 文献检索 | OpenAlex + Semantic Scholar 自动搜索 |
| 实验设计 | 自动生成实验方案 |
| 代码生成 | 完整可运行的实验代码 |
| GPU 执行 | 本地 GPU / SLURM 集群自动训练 |
| 结果分析 | 解析真实训练日志 |
| 图表生成 | 基于真实数据生成论文配图 |
| 论文撰写 | 完整 LaTeX 论文 |

## 9 阶段流水线

```
研究课题
    ↓
IDEATION → PLANNING → SETUP → CODING → EXECUTION → ANALYSIS → FIGURE_GEN → WRITING → REVIEW
    ↓
导出: paper.pdf / paper.tex / references.bib / figures / code / data
```

| 阶段 | 功能 |
|------|------|
| `IDEATION` | 文献检索与创意生成 |
| `PLANNING` | 实验方案设计 |
| `SETUP` | 环境准备 |
| `CODING` | 代码生成 |
| `EXECUTION` | **实验执行（本地 GPU / SLURM）** |
| `ANALYSIS` | 结果分析 |
| `FIGURE_GEN` | 图表生成 |
| `WRITING` | 论文撰写 |
| `REVIEW` | 审稿与修订 |

## 使用方式

### 完整流水线
```
nanoresearch run --topic "研究课题" --format neurips2025 --verbose
```

### 断点恢复
```
nanoresearch resume --workspace ~/.nanobot/workspace/research/{session_id} --verbose
```

### 导出论文
```
nanoresearch export --workspace ~/.nanobot/workspace/research/{session_id} --output ./my_paper
```

### 仅生成论文（跳过实验）
在配置中设置 `"skip_stages": ["SETUP", "CODING", "EXECUTION", "ANALYSIS"]`

## 论文格式

| 格式 | 用途 |
|------|------|
| `arxiv` | arXiv 预印本 |
| `icml` | ICML 会议 |
| `neurips` | NeurIPS 会议 |
| `neurips2025` | NeurIPS 2025 |

## 推荐模型（按阶段）

| 阶段 | 任务 | 推荐模型 |
|------|------|----------|
| `ideation` | 文献 + 假说 | DeepSeek-V3.2 |
| `planning` | 实验设计 | Claude Sonnet 4.6 |
| `code_gen` | 代码生成 | GPT-5.2-Codex / Claude Opus 4.6 |
| `writing` | 论文撰写 | Claude Opus 4.6 |
| `figure_gen` | 架构图 | Gemini 3.1 Flash |

## 配置要求

需要 OpenAI 兼容 API 端点：
```json
{
  "research": {
    "base_url": "https://your-endpoint/v1/",
    "api_key": "your-api-key"
  }
}
```

## 输出结构

```
my_paper/
├── paper.pdf
├── paper.tex
├── references.bib
├── figures/
├── code/
├── data/
└── manifest.json
```

## 关键优势

- **真实实验数据**：每个数据点、表格、图表都来自实际实验，非 LLM 编造
- **断点续跑**：任意阶段可从检查点恢复
- **多模型协作**：按阶段自动路由到最适合的模型
- **GPU 集群支持**：本地 GPU 或 SLURM 集群自动执行
