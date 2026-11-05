---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 383a3be6193c4bf6d2eb08612a67edb6
    PropagateID: 383a3be6193c4bf6d2eb08612a67edb6
    ReservedCode1: 3046022100f4307f4e97604057ba538e451e00930f1e8c395e45e56ca6f08cd339ae8d0fc002210097b803d1f4b054f94e77f14cbe3ebad0939c20b5155b3a569145ead8010a0e18
    ReservedCode2: 3046022100e1e1bc849bf798b690e9dbbb4d224208f7093f26dcacf3f6e06b65e48ae945d2022100940c3596a2ea3d8c5382f557e95a50b55f891977edd06462ac4115bfe0b10754
description: AI + 医疗学术文献每周追踪报告生成器。当用户说"帮我整理本周AI医疗研究简报"、"生成AI4Healthcare周报"、"整理这周AI医疗论文"时触发。每周一自动生成，报告以中文撰写，直接在当前对话回复。
name: ai4healthcare-weekly-tracker
---

# AI4Healthcare Weekly Tracker

每周 AI + 医疗领域学术文献追踪报告生成器。聚焦深度学习、医学影像、NLP 医疗应用、临床决策支持等方向，输出结构化周报。

## 核心搜索关键词

**核心主题（每次必搜）：**
- "deep learning healthcare"
- "medical AI"
- "clinical decision support AI"
- "AI medical imaging"
- "healthcare machine learning"
- "AI diagnosis"
- "clinical NLP"
- "medical transformers"

**扩展关键词（轮换补充）：**
- "federated learning healthcare"
- "explainable AI healthcare"
- "AI drug discovery"
- "clinical prediction model"
- "multimodal medical AI"

**数据来源优先级：**
1. arXiv (cs.AI, cs.LG, cs.CV) — 最新预印本
2. PubMed — 经同行评审论文
3. Semantic Scholar — 补充覆盖
4. Google Scholar — 全面检索

---

## 报告结构

每次生成完整报告，结构如下：

### 一、调研概览

- **检索时间范围**：上周一至周日（精确到天）
- **数据来源**：各来源检索到的论文数量、去重后总数
- **核心趋势**：2-3 句话描述本周最重要趋势
- **高频关键词**：Top 10 关键词 + 词频可视化（用文字图形表示）

### 二、Top-10 精选研究

每篇包含：

| 字段 | 说明 |
|------|------|
| 标题 | 英文原标题 |
| 作者 | 前三位 + et al. |
| 时间 | 发布/更新日期 |
| 来源 | arXiv / PubMed / 其他 |
| 链接 | 论文链接 |
| 入选理由 | 为什么本周值得看（1 句话） |
| 中文摘要 | 200-300 字，结构：[背景]→[方法]→[结果]→[结论] |
| Novelty | 核心创新点，1-2 句话 |
| 深度点评·亮点 | 3 个具体亮点，条理清晰 |
| 深度点评·不足 | 2 个具体不足，客观指出，措辞专业 |

**筛选标准（按优先级排序）：**
1. 发布时间最近一周内
2. 与 AI + 医疗核心主题高度相关
3. arXiv 新提交或高引用
4. 多源重复取最早版本

### 三、精选 3 篇精读推荐

| 字段 | 说明 |
|------|------|
| Paper 标题 | |
| 推荐理由 | 为什么值得精读（300字内），具体说明：①这篇解决了什么问题；②用了什么方法；③对后续研究有什么启发 |
| 适合谁读 | 研究者 / 工程师 / 入门者 |

---

## 报告撰写规范

- **语言**：全中文，专业但可读
- **标题/作者/链接**：保留英文原貌
- **链接格式**：直接显示 URL，可点击
- **时间格式**：如"2026-04-07"，统一 YYYY-MM-DD
- **亮点/不足**：具体、有依据，不空洞
- **精读理由**：有观点，客观推荐

## 执行流程

1. 确定检索时间范围（上周一 ~ 上周日）
2. 使用 `batch_web_search` 并发搜索核心关键词（每次最多 10 个 query）
3. 如结果不足 10 篇，扩大关键词再搜
4. 整理、去重（DOI / 标题相似度）
5. 按相关性 + 时间排序，选取 Top 10
6. 对每篇使用 `extract_content_from_websites` 获取摘要（如有必要）
7. 生成完整报告
8. 直接在当前对话回复完整报告，不额外调用其他工具

## 注意事项

- 搜索时附加当前年份，精确检索：`[keyword] 2026`
- 如某方向本周无新论文，报告中注明"本周该方向无新增重要论文"
- 多个来源出现同一篇，取最早版本并在报告中注明
- 报告开头注明"检索时间范围：YYYY-MM-DD 至 YYYY-MM-DD"
