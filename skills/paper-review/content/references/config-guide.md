# Paper Review 配置文件参考

## 默认配置（ai4bio-paper-review 等效）

```json
{
  "name": "default-ai4bio",
  "topic": "AI for Biology (RNA + 蛋白质)",
  "topic_keywords": [
    "rna protein ai deep learning 2025",
    "alphafold esmfold protein structure 2025",
    "rna structure prediction deep learning 2025",
    "foundation model protein language model 2025",
    "diffusion model protein design 2025",
    "graph neural network biology 2025"
  ],
  "platforms": ["arxiv", "nature", "ccf", "biorxiv", "pwcb"],
  "evaluation": {
    "dimensions": [
      { "name": "创新性",    "weight": 0.25, "question": "是否提出新问题/新方法/新框架？突破性如何？" },
      { "name": "可复现性",  "weight": 0.25, "question": "代码开源？数据公开？环境可搭建？" },
      { "name": "可拓展性",  "weight": 0.20, "question": "能否迁移到其他任务/领域？Scaling表现？" },
      { "name": "优化潜力",  "weight": 0.20, "question": "是否有明显瓶颈？计算代价/精度差距？" },
      { "name": "影响力",    "weight": 0.10, "question": "解决的现实问题有多重要？实验验证充分吗？" }
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

## 配置项完整说明

### name
配置文件名称，用于报告目录命名。

### topic
调研主题，一句话描述。

### topic_keywords
**最关键的配置**。搜索时转换为多个搜索查询，支持以下格式：
- 普通关键词：`"protein structure prediction"`
- 年份限定：`"protein ai 2024 2025"`
- 来源限定：`"site:arxiv.org protein ai"`
- 组合查询：`"protein AND diffusion AND design"`

### platforms
可选（若为空或省略则默认全部）：
- `arxiv` — arxiv.org（含各子版cs.LG/q-bio等）
- `nature` — Nature正刊及子刊（Nature Methods/Biotechnology/Machine Intelligence等）
- `ccf` — CCF推荐A类会议（ICML/NeurIPS/ICLR/CVPR/AAAI/ACL等）
- `science` — Science正刊及子刊
- `cell` — Cell正刊及子刊
- `biorxiv` / `medrxiv` — 预印本平台
- `pwcb` — Papers with Code（含代码论文）
- `pubmed` — 生物医学文献库
- `semantic` — Semantic Scholar（学术搜索）

### evaluation.dimensions
**完全可自定义**。每个维度包含：
- `name`：维度名称
- `weight`：权重（总和须为1.0，可不严格等于1.0，系统会自动归一化）
- `question`：评估时需要回答的核心问题（帮助模型给出有依据的打分）

#### 示例：学术顶会论文评估（偏学术）
```json
"dimensions": [
  { "name": "理论创新性", "weight": 0.30, "question": "是否提出全新的理论/方法/分析框架？" },
  { "name": "实验完整性", "weight": 0.25, "question": "实验是否充分验证了方法的有效性？" },
  { "name": "可复现性",   "weight": 0.20, "question": "代码/数据/细节是否充分公开？" },
  { "name": "写作质量",   "weight": 0.15, "question": "论文写作是否清晰、逻辑严密？" },
  { "name": "引用影响力", "weight": 0.10, "question": "是否已有大量引用或成为领域标杆？" }
]
```

#### 示例：工业落地评估（偏工程）
```json
"dimensions": [
  { "name": "任务匹配度", "weight": 0.30, "question": "是否直接解决目标工业场景的核心问题？" },
  { "name": "部署可行性", "weight": 0.25, "question": "模型规模/推理延迟/硬件需求是否可接受？" },
  { "name": "数据依赖",   "weight": 0.20, "question": "训练数据需求是否可满足？是否依赖私有数据？" },
  { "name": "可维护性",   "weight": 0.15, "question": "代码质量/文档/社区活跃度如何？" },
  { "name": "商业价值",   "weight": 0.10, "question": "解决该问题能带来多大商业/业务价值？" }
]
```

#### 示例：前沿技术追踪（轻量评估）
```json
"dimensions": [
  { "name": "技术新颖度", "weight": 0.40, "question": "是否引入了新模型/新范式/新思路？" },
  { "name": "热度关注度", "weight": 0.35, "question": "是否引起广泛讨论？GitHub stars/引用量如何？" },
  { "name": "可跟进性",   "weight": 0.25, "question": "我方是否有能力在此方向上开展研究/落地？" }
]
```

### evaluation.min_papers / max_papers
调研论文数量范围。默认 5-20 篇。

### output.format
可选：
- `standard`（默认）— papers.md + analysis.md + summary.md 三文件
- `compact` — 仅 summary.md，单文件输出
- `table` — 仅评估表格，所有论文平铺，适合导入 Excel

### output.include_improvements
是否包含改进方向。设为 `false` 则只输出论文列表和评估分数。

### output.improvement_count
每篇论文输出几个改进方向。默认为 3 个。
