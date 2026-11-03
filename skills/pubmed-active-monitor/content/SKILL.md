---
name: pubmed-active-monitor
description: PubMed Active Monitoring and Push Notifications. When new literature is published on key topics like medical team research directions, CSCO guidelines, proactively search and push abstracts instead of waiting for daily Cron passive scanning. Triggers: literature monitoring, PubMed push, medical literature update, CSCO guideline tracking, medical team research.
---

# PubMed 文献主动监控与推送

## 核心功能

当医疗团队、CSCO 指南等关键话题有新文献发表时，主动搜索 PubMed 并推送摘要摘要，而不是等待每日 Cron 被动扫描。

## 工作流程

### 步骤 1：确定监控主题

收集以下信息构建搜索查询：

1. **医疗团队研究方向**：肿瘤、心血管、神经等具体领域
2. **指南追踪**：CSCO、NCCN、ESMO 等指南相关更新
3. **关键词组合**：使用布尔逻辑 (AND/OR) 组合术语

### 步骤 2：PubMed API 搜索

使用 NCBI Entrez API 执行搜索：

```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
?db=pubmed
&term=(oncology[MeSH Terms]) AND (CSCO[Title/Abstract])
&retmax=20
&retmode=json
&sort=date
```

### 步骤 3：获取文献详情

对每篇新文献获取详细信息：

```
GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
?db=pubmed
&id={pmid}
&retmode=json
```

### 步骤 4：生成摘要摘要

为每篇文献生成结构化摘要：

- **标题**：英文标题
- **作者**：第一作者及通讯作者
- **期刊**：期刊名称、发表年份
- **摘要**：原文摘要或 AI 生成的简短摘要
- **关键词**：MeSH 主题词
- **DOI**：文章链接

### 步骤 5：推送通知

将摘要摘要整合为可读的报告格式，包含：

- 文献列表（按时间排序）
- 每篇文献的核心信息
- 原文链接

## 常用搜索模式

### 肿瘤领域

```
(cancer[Title/Abstract] OR oncology[MeSH Terms])
AND (clinical trial[Publication Type] OR guideline[Publication Type])
AND ("2024"[Date - Publication] : "2025"[Date - Publication])
```

### CSCO 指南相关

```
CSCO[Title/Abstract] AND (guideline[Title/Abstract] OR consensus[Title/Abstract])
```

### 精准医疗

```
precision medicine[Title/Abstract] AND (biomarker[Title/Abstract] OR genomics[MeSH Terms])
```

## 输出格式

```
## 新文献推送报告

**监控主题**：{topic}
**搜索时间**：{timestamp}
**发现文献**：{count} 篇

---

### 1. {Title}
- **PMID**: {pmid}
- **作者**: {authors}
- **期刊**: {journal} ({year})
- **类型**: {pub_type}
- **摘要**: {abstract}
- **链接**: https://pubmed.ncbi.nlm.nih.gov/{pmid}/
```

## 注意事项

- 优先搜索近 7 天内发表的文献
- 过滤掉非英文文献（如需要）
- 排除已推送过的文献（维护已推送列表）
- 对于高影响力期刊（Nature Medicine, NEJM, Lancet Oncology 等）优先处理
