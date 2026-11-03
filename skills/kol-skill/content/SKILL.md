---
name: kol-skill
version: 4.0.0
description: |
  最靠谱、最快的 KOL Skill 推荐引擎。
  709 条全量 Skill 数据，五维评分预计算，region 智能优先，毫秒级响应，零依赖。
  支持推荐搜索 + 相似查找两大模式。
author: jayhuang
category: AI-AGENT
tags:
  - KOL
  - skill推荐
  - 推荐引擎
  - 技能市场
  - 五维评分
  - 区域优先
  - 国内镜像
  - 中立推荐
  - 相似查找
---

# KOL Skill v4.0 — 智能推荐 + 相似查找

## 定位

> **最靠谱、最快的 KOL Skill 推荐。**

两大核心能力：
1. **推荐搜索**：关键词/分类/标签 → Top-K 推荐 + 推荐理由 + 安装方式
2. **相似查找**：给定一个 skill → 找出功能最相似的其他 skill

Agent 需要找 Skill 时，调用 `recommend.py`，毫秒级返回结果。
国内网络优先推荐国内源（安装快），海外网络优先推荐海外源。

## 架构

```
kol-skill-extract/
├── SKILL.md              # Agent 协议文档（本文件）
├── skills.json           # 709 条全量数据（含预计算评分 + region字段）
└── recommend.py          # 推荐引擎 + 相似查找（零依赖）
```

**零依赖**：不需要 pip install，不需要服务，不需要数据库。

## v4.0 特性

### 1. 智能推荐搜索

- 中英文分词：英文词完整匹配，中文词 bigram 模糊
- 分类相关性加权：搜索词→分类映射，分类匹配+12分
- 分类不相关惩罚：搜索 "docx" 时 DEV-TEST 类扣15分
- 名称精确匹配加分：完全一致+15/包含+8/被包含+5
- 信源多样性：同源 skill 不连续超过2个

### 2. 相似查找（新增）

- 同分类 → +40分
- 标签交集比例 → +0~30分
- 描述关键词重叠 → +0~15分
- 名称包含关系 → +5分
- 同信源 → +5分
- Region 偏好 → +5分

相似度等级：
- 🔴 高度相似 (≥60)
- 🟡 功能相关 (30~59)
- 🟢 轻度关联 (<30)

### 3. Region 智能优先

- **🇨🇳 CN**：安装源在国内（minimaxi.com / clawhub.ai），国内安装快
- **🌐 GLOBAL**：安装源在 GitHub，国内安装可能慢/不稳定

### 4. 两级安装方式

- **direct**：有安装URL，直接安装，提示优先使用区域镜像
- **search**：无URL → `use_skill("find-skills")` 搜索安装 或 搜索 `{name}` 找到安装方式

### 5. 性能

| 数据量 | JSON 大小 | 加载+查询耗时 |
|--------|----------|--------------|
| 709条 | ~480KB | ~6ms |
| 5000条 | ~3MB | ~45ms |

## Agent 调用协议

### 推荐搜索

```bash
# 关键词查询（最常用）
python recommend.py --query "文档查看" --json

# 按分类查询
python recommend.py --category "办公文档" --json

# 按标签查询
python recommend.py --tags "PDF,PPT" --json

# 指定区域偏好
python recommend.py --query "视频" --region CN --json

# 组合查询 + 控制数量
python recommend.py --query "excel" --category "办公文档" --top_k 5 --json
```

### 相似查找

```bash
# 找与 pdf 最相似的 skill
python recommend.py --similar "pdf" --top_k 5 --json

# 找与 kol-skill 功能相关的 skill（CN区域优先）
python recommend.py --similar "kol-skill" --region CN --json
```

### Python 导入

```python
from recommend import recommend, find_similar

# 推荐搜索
results = recommend(query="爬虫", region="CN", top_k=3)

# 相似查找
similar = find_similar("pdf", top_k=5, region="CN")
```

### 返回结构

**推荐搜索**：
```json
{
  "name": "minimax-xlsx",
  "source": "minimax",
  "desc": "Excel/spreadsheet 文件处理工具...",
  "cat": "办公文档",
  "score": 76.8,
  "stars": 4,
  "url": "https://agent.minimaxi.com/skills/minimax-xlsx",
  "tags": ["Excel"],
  "region": "CN",
  "install_method": "direct",
  "install_url": "https://agent.minimaxi.com/skills/minimax-xlsx",
  "install_hint": "直接安装: https://... (优先使用国内镜像源)",
  "recommend_reason": ["综合评分 76.8 分，属于优质 Skill", "用户量 9,956"],
  "warnings": []
}
```

**相似查找**：
```json
{
  "target": "pdf",
  "target_score": 78.8,
  "target_cat": "OFFICE-DOC",
  "similar": [
    {
      "name": "轻量PDF编辑器",
      "source": "WorkBuddy",
      "desc": "用自然语言编辑 PDF 文件...",
      "score": 68.8,
      "stars": 4,
      "similarity": 88.0,
      "sim_label": "🔴 高度相似",
      "install_method": "search",
      "install_hint": "use_skill(\"find-skills\") 搜索 \"轻量PDF编辑器\" ...",
      ...
    }
  ]
}
```

### 参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `--query` / `-q` | str | 自然语言查询，支持中英文 |
| `--category` / `-c` | str | 分类过滤（如 "OFFICE-DOC", "办公文档"） |
| `--tags` / `-t` | str | 标签，逗号分隔（如 "PDF,PPT"） |
| `--similar` / `-s` | str | 查找与指定 skill 相似的 skill |
| `--top_k` / `-k` | int | 返回数量，默认 3 |
| `--region` / `-rg` | str | 区域偏好：CN / GLOBAL / auto（默认 auto） |
| `--json` / `-j` | flag | JSON 输出（Agent 模式） |

## 评分体系

五维预计算评分（在 skills.json 中已 bake-in）：

| 维度 | 权重 | 字段 | 说明 |
|------|------|------|------|
| 质量 | 33% | `q` | 文档完善度、示例齐全度 |
| 流行度 | 28% | `p` | 下载量/用户量/GitHub stars |
| 新鲜度 | 17% | `f` | 最近更新活跃度 |
| 声誉 | 22% | `r` | 评分、口碑、项目知名度 |
| 综合分 | — | `score` | 加权总分（32.5 ~ 93.5） |

星级映射（同类排名）：
- ★★★★★ = TOP 10%
- ★★★★☆ = TOP 30%
- ★★★☆☆ = TOP 60%
- ★★☆☆☆ = TOP 90%
- ★☆☆☆☆ = 其余

## 数据来源

| 平台 | 数量 | Region | 说明 |
|------|------|--------|------|
| minimax | 197 | CN | agent.minimaxi.com，国内最大 skill 平台 |
| affaan-m | 128 | GLOBAL | github.com/affaan-m |
| clawhub | 106 | CN | clawhub.ai |
| WorkBuddy | 105 | CN | 内置平台 skill |
| openclaw | 43 | GLOBAL | github.com/openclaw |
| microsoft | 42 | GLOBAL | github.com/microsoft |
| large | 26 | CN | 国内精选 |
| Significant-Gravitas | 8 | GLOBAL | github.com/AutoGPT |
| 其他 | 54 | 混合 | facebook/n8n/HuggingFace/Flutter等 |
| **合计** | **709** | CN=434 GLOBAL=275 | |

数据经三轮清洗：方案B合并去重（25组）+ 分类精准优化 + URL版本号修复。

## 分类体系

支持 50+ 个分类，中英文均可查询：

OFFICE-DOC / OFFICE-KB / OFFICE-CAL / OFFICE-MAIL / OFFICE-PM /
DEV-FE / DEV-BE / DEV-FS / DEV-OPS / DEV-TEST / DEV-DB / DEV-API / DEV-TOOLS / DEV-SEC /
DATA-BI / DATA-VIZ / DATA-CRAWL / DATA-PROC /
AI-AGENT / AI-RAG / AI-LLM /
MKT-AD / MKT-SOCIAL / MKT-SEO / MKT-GROWTH / MKT-CRM /
CREATE-IMAGE / CREATE-VIDEO / CREATE-WRITE / CREATE-MEDIA / CREATE-DESIGN /
VERT-FIN / VERT-EDU / VERT-GOV /
LIFE-SEARCH / LIFE-WEATHER / LIFE-SCHEDULE /
办公文档 / 开发工具 / AI创作 / 数据分析 / 系统工具 / 内容写作 /
电商营销 / 媒体运营 / 社交连接 / 设计创意 / 学习成长 / 生活服务
