---
name: dl-cv-weekly-insight
description: 检索并分析深度学习与计算机视觉领域近两周 arXiv 热点论文，进行创新性量化评估，深度解读 Top-3 最具创新工作。当用户要求分析 CV/DL 最新论文、追踪领域热点、生成学术报告、检索 arXiv 论文、评估论文创新性时使用。
---

# DL-CV-Weekly-Insight

## 功能概述

本 Skill 提供端到端的学术论文智能分析服务：

1. **智能检索**: 自动抓取 arXiv 近两周 CV/DL 领域论文，交叉验证 Twitter、PapersWithCode、GitHub 热度
2. **量化评估**: 5 维度创新评分体系（方法新颖性、问题重要性、实验说服力、潜在影响力、可复现性）
3. **深度解读**: 对 Top-3 论文进行结构化专业分析，包含方法拆解、实验验证、趋势预测
4. **趋势洞察**: 生成领域热点分布、机构活跃度、技术演进方向等综合报告

## 输入参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| time_range | integer | 检索时间范围（天，7-30） | 14 |
| categories | array | arXiv 分类目录 | ["cs.CV", "cs.LG", "cs.AI"] |
| max_papers | integer | 最大检索论文数（100-500） | 300 |
| focus_areas | array | 重点关注的技术方向 | architecture, generative, multimodal, efficiency |
| output_format | string | 输出格式 | markdown |
| include_code | boolean | 是否包含代码片段 | true |

## 评分体系

5 维度加权评分：

| 维度 | 权重 | 数据来源 |
|------|------|----------|
| 方法新颖性 | 30% | 论文方法章节 |
| 问题重要性 | 25% | 引言动机分析 |
| 实验说服力 | 20% | 实验章节 |
| 潜在影响力 | 15% | 讨论/相关工作 |
| 可复现性 | 10% | GitHub/补充材料 |

**筛选规则**: 总分 ≥ 7.5 进入候选池，Top-10 进入深度分析

## 执行流程

1. **数据检索**: Query arXiv API → Fetch Twitter/X Discussions → Check PapersWithCode Trends → Monitor GitHub Stars
2. **创新评分**: 5 维度量化评估 → 筛选候选池 → 排序 Top-10
3. **深度分析**: PDF 精读 → 代码分析 → 社区验证 → 影响预测

## 输出结构

```json
{
  "report_meta": { "generated_at", "time_range", "total_papers" },
  "field_overview": { "topic_distribution", "institution_ranking", "open_source_trends" },
  "top10_candidates": [{ "rank", "title", "authors", "innovation_score", "key_innovation" }],
  "top3_deep_dive": [{ "paper_info", "problem_motivation", "methodology", "experiments", "critical_assessment", "impact_forecast" }],
  "trend_summary": { "tech_trends", "methodology_evolution", "research_suggestions" }
}
```

## 工具配置

### 必选工具
- `mcp__matrix__batch_web_search`: 检索 arXiv、Twitter、Reddit 热点
- `mcp__matrix__extract_content_from_websites`: 提取论文、GitHub 项目页面
- `mcp__matrix__extract_pdfs_key_info`: 深度分析论文 PDF

### API 限制
- arXiv: 1 request/3 seconds
- GitHub: 60 requests/hour (unauthenticated)

## 错误处理

| 错误类型 | 处理策略 | 降级方案 |
|----------|----------|----------|
| arXiv API 限流 | 指数退避重试 (3次) | 切换至 RSS feed |
| 论文 PDF 无法获取 | 标记 "待补充" | 仅基于摘要分析 |
| GitHub API 限制 | 使用未认证缓存 | 跳过开源验证 |
| 近14天论文不足 | 自动扩展至 21 天 | 输出警告说明 |

## 使用示例

```bash
# 默认配置 (近14天, CV/LG/AI)
python -m skill.dl_cv_weekly_insight

# 自定义配置
python -m skill.dl_cv_weekly_insight --time-range 21 --categories cs.CV cs.RO --focus 3d_vision
```

## 版本历史

- v1.0.0: 初始版本发布
