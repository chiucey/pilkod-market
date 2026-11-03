---
name: pubmed-chemistry-search
description: 检索 PubMed 数据库中的学术文献，特别擅长化学领域和生物化学研究。当用户要求查找化学文献、搜索生物化学研究、获取药物化学资料、检索有机化学文献、或进行学术文献调研时使用。
---

# PubMed 化学文献检索技能

本技能提供 PubMed 数据库的专业文献检索能力，专注于化学、生物化学、药物化学和有机化学领域。

## 核心能力

1. **化学文献检索**：通过 PubMed E-utilities API 接入数据库
2. **MeSH 术语优化**：使用化学相关的医学主题词表进行精准检索
3. **多维度过滤**：支持年份、期刊、化合物名称等过滤条件
4. **批量获取**：支持获取文献摘要和元数据

## 使用方法

### 基础检索

当用户提供化学相关检索需求时，使用以下工作流程：

1. **解析检索关键词**
   - 识别化学物质名称、CAS 号、化合物名称
   - 识别研究类型（合成、表征、反应机理等）
   - 识别生物化学相关术语（酶、蛋白质通路、代谢等）

2. **构建检索策略**
   - 使用 PubMed ESearch API
   - 基础格式：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax={count}&retmode=json`
   - 化学领域优先使用 MeSH 术语检索

3. **获取详细结果**
   - 使用 EFetch API 获取摘要
   - 格式：`https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={ids}&rettype=abstract&retmode=xml`

### 化学领域检索策略

**常用化学 MeSH 术语：**
- Chemistry, Organic（有机化学）
- Chemistry, Pharmaceutical（药物化学）
- Biochemistry（生物化学）
- Molecular Structure（分子结构）
- Chemical Phenomena（化学现象）
- Pharmaceutical Preparations（药物制剂）
- Proteins（蛋白质）
- Enzymes（酶）

**检索示例：**
```
"aspirin"[MeSH Terms] OR "acetylsalicylic acid"[Title/Abstract]
```

### 高级检索

对于复杂检索需求：
1. 使用 PubMed Advanced Search Builder 语法
2. 结合 MeSH 术语和自由词检索
3. 使用布尔运算符 (AND, OR, NOT) 组合检索

## 输出格式

检索结果应包含：
- **文献标题**：原始英文标题
- **作者列表**：第一作者和通讯作者标注
- **期刊信息**：期刊名称、年份、卷期页码
- **DOI**：数字对象标识符
- **摘要**：英文摘要（如有）
- **MeSH 术语**：文献标注的医学主题词

## 注意事项

1. PubMed API 限制：每秒最多 3 个请求，需遵守速率限制
2. 结果数量限制：单次检索最多返回 100,000 条记录
3. 优先使用 MeSH Terms 而非自由词以提高查准率
4. 化学检索建议同时使用化学名称和 CAS 号进行检索
5. 结果排序建议：相关性 > 发表时间 > 引用次数
