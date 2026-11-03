---
name: paper-review
description: 通用意论文调研与技术评估工具。当用户需要搜索、调研任意主题论文时激活，支持自定义主题、论文来源、评估体系和呈现方式。覆盖 arxiv、biorxiv、CCF顶会、Nature/Science/Cell系列、Papers with Code、PubMed、语义 Scholar 等全平台。自动完成：自定义检索 → 信息提取 → 可配置多维评估 → 灵活格式输出。触发关键词：论文调研、文献综述、paper survey、review of literature、技术调研、行业报告、Research review。
---

# Paper Review — 通用意论文调研框架

## 核心能力

```
用户自定义 → 论文检索 → 深度分析 → 结构化报告
   ↑                                         ↓
  config.json (或对话配置)          输出: papers.md / analysis.md / summary.md
```

## 与 ai4bio-paper-review 的关系

`paper-review` 是 `ai4bio-paper-review` 的**超集**，将 AI4Biology 领域的五维评估体系解耦为可插拔模块，用户可：
- 完全继承默认配置（等价于 ai4bio-paper-review）
- 部分修改（只换主题或只换评估维度）
- 完全重写（自定义所有字段）

---

## 第一步：确认调研配置

收到调研需求后，**先读取用户的配置偏好**（若已存在配置文件则加载，否则引导用户选择）：

### 对话配置（快速模式）

如果用户没有预先配置，通过 3 个问题确认配置：

```
① 主题是什么？（如：蛋白质设计、量子计算、自动驾驶感知、大模型推理优化…）
② 覆盖哪些来源？（默认全部：arxiv + CCF顶会 + Nature/Science + biorxiv + Papers with Code）
③ 评估哪些维度？（默认：创新性 / 可复现性 / 可拓展性 / 优化潜力 / 影响力）
④ 报告呈现方式？（默认：标准论文卡格式）
```

### 配置文件模式（标准模式）

若用户预先创建了配置文件（`/workspace/paper-reviews/configs/<name>.json`），则直接读取：

```json
{
  "name": "AI4Bio-RNA-Protein",
  "topic": "RNA + 蛋白质 + AI",
  "topic_keywords": ["rna protein ai deep learning", "alphafold esmfold", "..."],
  "platforms": ["arxiv", "nature", "ccf", "biorxiv", "pwcb"],
  "evaluation": {
    "dimensions": [
      { "name": "创新性",    "weight": 0.25, "question": "是否提出新问题/新方法/新框架？" },
      { "name": "可复现性",  "weight": 0.25, "question": "代码开源？数据可获取？环境可搭建？" },
      { "name": "可拓展性",  "weight": 0.20, "question": "能否迁移到其他任务/领域？" },
      { "name": "优化潜力",  "weight": 0.20, "question": "是否有明显瓶颈可改进？" },
      { "name": "影响力",    "weight": 0.10, "question": "解决的现实问题有多重要？" }
    ],
    "min_papers": 5,
    "max_papers": 20
  },
  "output": {
    "format": "standard",
    "include_summary_table": true,
    "include_improvements": true,
    "improvement_count": 3
  }
}
```

---

## 第二步：执行检索

### 平台优先级映射

| 平台 | 搜索方式 | URL模板 |
|---|---|---|
| arxiv | batch_web_search | site:arxiv.org/abs/ + keywords |
| CCF顶会 (ICML/NeurIPS/ICLR/Nature子刊) | batch_web_search | conference/venue + year + keywords |
| Nature/Science/Cell | batch_web_search + extract_content | journal name + keywords |
| biorxiv/medrxiv | batch_web_search | site:biorxiv.org + keywords |
| Papers with Code | batch_web_search | site:paperswithcode.com + keywords |
| PubMed | batch_web_search | site:pubmed.ncbi.nlm.nih.gov + keywords |

### 搜索执行规范

**至少 3 轮搜索，每轮 3-5 个查询：**

```
# 第1轮：核心主题搜索（5个查询）
[用户主题 + 方法/模型/最新进展 + 年份]
[用户主题 + survey review 2024 2025]
[用户主题 + 开源 代码 github 2025]
[用户主题 + SOTA state of the art 2025]
[用户主题 + challenge limitation problem]

# 第2轮：顶会/顶刊定向搜索
[CCF-A 会议名称 + 2025 + 用户主题]
[Nature Science Cell + 2025 + 用户主题]
[顶会Best Paper + 2025 + 用户主题]

# 第3轮：代码与复现搜索
[Papers with Code + 用户主题 + 2025]
[github star 500 + 用户主题 + 深度学习 2025]
```

**每篇候选论文必须检索到：** 论文链接、代码仓库、作者信息、发表年份。

---

## 第三步：信息提取

每篇论文提取以下标准字段（可由配置增删）：

| 字段 | 说明 |
|---|---|
| title | 论文标题 |
| platform | 来源（arxiv-xxx/Nature/CCF-XXX/其他） |
| authors | 第一作者 + 通讯作者 |
| year | 发表年份 |
| url | 论文链接 |
| code_url | GitHub/HuggingFace 等代码链接 |
| venue | 期刊/会议名称 |
| tags | 主题标签（最多5个） |

---

## 第四步：多维评估（可配置）

根据配置中的 `evaluation.dimensions` 执行评估。

**评分标准（1-5分）：**

| 分值 | 含义 |
|---|---|
| 5 | 顶尖：领域突破性工作，代码完全开源，方法创新且可复现 |
| 4 | 优秀：有明显创新，代码基本可复现，有优化空间 |
| 3 | 良好：方法有效，代码或数据部分可获取，值得关注 |
| 2 | 一般：有ideas但实现/验证不足，了解动态即可 |
| 1 | 较差：推荐意义低 |

**总分计算：**
```
总分 = Σ(维度得分 × 权重)，归一化到1位小数
```

---

## 第五步：生成报告（可配置格式）

### 标准格式（默认）

```
/workspace/paper-reviews/<topic>/YYYY-MM-DD/
├── papers.md        # 论文列表（含平台/作者/链接/代码）
├── analysis.md      # 多维评估表格
└── summary.md       # 推荐报告（含方法核心+改进方向）
```

### summary.md 标准结构

每篇论文必须按以下格式输出：

```markdown
## 【论文N】论文标题

**平台：** 来源
**年份：** YYYY
**链接：** https://...
**代码：** https://github.com/...（未公开则注明）

**关键词：** keyword1 / keyword2 / keyword3

**方法核心：**  
3-5句完整技术描述，包括：模型架构、核心思想、关键技术、输入输出。

---

**改进方向 1：[方向名称]**
- 改进思路：具体如何改进
- 创新点：学术贡献
- 难度：⭐~⭐⭐⭐⭐⭐

**改进方向 2：...**
- ...

**改进方向 3：...**
- ...
```

### 极简格式（用户要求时激活）

```markdown
## 论文标题
- 来源 | 年份 | 代码
- 核心方法：一句话概括
- Top1改进：改进方向 → 创新点
```

### 表格格式（用户要求时激活）

输出 Markdown 表格，所有字段平铺，适合导入 Excel 或 Notion。

---

## 第六步：回复用户

报告生成后，回复用户：
1. 报告保存路径
2. 命中论文总数 + 推荐数量（🥇/🥈/🥉）
3. 最高优先级论文一句话推荐理由
4. 等待用户进一步指令（深入某篇/某个改进方向/导出其他格式）

---

## 执行流程图

```
用户请求调研
    ↓
加载配置文件 OR 对话确认配置
    ↓
生成搜索关键词（topic + 平台 + 年份 + 关键词）
    ↓
执行3轮搜索（≥15篇候选）
    ↓
过滤：去重 + 去掉相关性低的 + 按年份排序
    ↓
提取论文信息（title/platform/authors/url/code/tags）
    ↓
多维评估（按配置的权重打分）
    ↓
按总分排序，生成 papers.md + analysis.md + summary.md
    ↓
回复用户：报告路径 + 关键结论 + 最高推荐
```

---

## 注意事项

- 优先选择**近2年内**（2024-2026）发表的论文
- 代码仓库优先选择 GitHub stars > 300 或官方认证仓库
- 预印本（arxiv/biorxiv）需标注"预印本"状态，若已被顶刊接收需注明
- 每篇论文的**方法核心**必须写完整技术描述（3-5句），不得少于3句
- 每个**改进方向**必须包含"改进思路"+"创新点"+"难度"三个子字段
- 如果某篇论文代码未公开，不得虚构代码链接，须标注"未公开"
- 评估打分必须给出**具体理由**（1-2句话），不得只给分数无解释
- 如果用户指定了特定平台，**严格按用户指定平台搜索**，不得擅自添加
- 如果用户指定了特定评估维度，**严格按用户配置执行**，不得擅自添加
