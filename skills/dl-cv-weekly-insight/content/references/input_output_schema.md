# 输入输出模式详解

## 输入参数 (Input Schema)

```json
{
  "type": "object",
  "properties": {
    "time_range": {
      "type": "integer",
      "description": "检索时间范围（天）",
      "default": 14,
      "minimum": 7,
      "maximum": 30
    },
    "categories": {
      "type": "array",
      "description": "arXiv 分类目录",
      "default": ["cs.CV", "cs.LG", "cs.AI"],
      "items": {
        "type": "string",
        "enum": ["cs.CV", "cs.LG", "cs.AI", "cs.CL", "cs.RO", "eess.IV"]
      }
    },
    "max_papers": {
      "type": "integer",
      "description": "最大检索论文数",
      "default": 300,
      "minimum": 100,
      "maximum": 500
    },
    "focus_areas": {
      "type": "array",
      "description": "重点关注的技术方向",
      "default": ["architecture", "generative", "multimodal", "efficiency"],
      "items": {
        "type": "string",
        "enum": ["architecture", "generative", "multimodal", "3d_vision", "video", "efficiency", "theory", "applications"]
      }
    },
    "output_format": {
      "type": "string",
      "description": "输出格式",
      "default": "markdown",
      "enum": ["markdown", "json", "html"]
    },
    "include_code": {
      "type": "boolean",
      "description": "是否包含代码片段和复现建议",
      "default": true
    }
  }
}
```

## 输出模式 (Output Schema)

```json
{
  "type": "object",
  "properties": {
    "report_meta": {
      "type": "object",
      "properties": {
        "generated_at": {"type": "string", "format": "date-time"},
        "time_range": {"type": "string"},
        "total_papers": {"type": "integer"},
        "candidate_pool_size": {"type": "integer"}
      }
    },
    "field_overview": {
      "type": "object",
      "properties": {
        "topic_distribution": {"type": "array"},
        "institution_ranking": {"type": "array"},
        "open_source_trends": {"type": "array"}
      }
    },
    "top10_candidates": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "rank": {"type": "integer"},
          "title": {"type": "string"},
          "authors": {"type": "array"},
          "institution": {"type": "string"},
          "arxiv_id": {"type": "string"},
          "innovation_score": {"type": "number"},
          "key_innovation": {"type": "string"},
          "open_source": {"type": "boolean"}
        }
      }
    },
    "top3_deep_dive": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "rank": {"type": "integer"},
          "paper_info": {"type": "object"},
          "problem_motivation": {"type": "object"},
          "methodology": {"type": "object"},
          "experiments": {"type": "object"},
          "critical_assessment": {"type": "object"},
          "impact_forecast": {"type": "object"},
          "key_resources": {"type": "object"}
        }
      }
    },
    "trend_summary": {
      "type": "object",
      "properties": {
        "tech_trends": {"type": "array"},
        "methodology_evolution": {"type": "object"},
        "research_suggestions": {"type": "array"}
      }
    },
    "appendix": {
      "type": "object",
      "properties": {
        "full_scoring_table": {"type": "array"},
        "search_config": {"type": "object"},
        "excluded_papers": {"type": "array"}
      }
    }
  }
}
```

## Top-3 深度解读结构

### paper_info
- title: 论文标题
- authors: 作者列表
- institution: 机构信息
- arxiv_id: arXiv ID
- github_url: GitHub 链接（如有）
- published_date: 发表日期

### problem_motivation
- core_problem: 核心问题描述
- background: 背景与动机
- existing_gaps: 现有方法的不足
- paper_claim: 论文声称解决的问题

### methodology
- core_contribution: 核心贡献点
- technical_details: 技术细节
- key_architecture: 关键架构设计
- novel_components: 创新组件

### experiments
- main_results: 主要实验结果
- comparison_methods: 对比方法
- datasets: 使用的数据集
- ablation_study: 消融实验
- limitations: 实验局限性

### critical_assessment
- strengths: 优势
- weaknesses: 劣势
- comparison_fairness: 对比公平性
- reproducibility: 可复现性评估

### impact_forecast
- academic_impact: 学术影响
- industry_value: 工业价值
- follow_up_directions: 跟进方向
- potential_applications: 潜在应用

### key_resources
- must_read_sections: 必读章节
- code_entry: 代码入口
- reproduction_guide: 复现指南
- hardware_requirements: 硬件需求
