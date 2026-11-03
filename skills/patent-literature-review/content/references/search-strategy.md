---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: c499c2b6f6e808b4f7a80a96a52b5a3f
    PropagateID: c499c2b6f6e808b4f7a80a96a52b5a3f
    ReservedCode1: 3046022100985c680654a8eedc1baf1838a0c84e14bca2d50b0d3edbe3914b966329a3649f022100e0bb9ee257b994fce8e101aee5b73b624bca15af6351cb818b9771ca2a4fc000
    ReservedCode2: 304502206a60250f07baa18dd4ac4cb5e621fa30d7db4c224ec4dd8075761f2ef83a2acb02210080871c3df3f15fe76ce8220b4422ea5603b1ceb218c77e45a373397fbd4c8a1c
---

# PubMed检索策略

本文档记录专利文献检索的标准策略，包括检索式构建方法、筛选标准和优化技巧。每次完成检索任务后需进行复盘并更新本文档。

## 核心检索原则

1. **全面性**：确保检索覆盖专利文献的所有关键技术点
2. **准确性**：使用精确的检索词避免无关结果
3. **可重复性**：每次检索策略可被复现和验证

## 检索式构建方法

### 1. 关键词提取层级

| 层级 | 类型 | 示例 |
|------|------|------|
| L1 | 技术领域核心词 | CRISPR, gene therapy, immunotherapy |
| L2 | 技术特征词 | Cas9, sgRNA, delivery system |
| L3 | 应用场景词 | cancer, tumor, autoimmune disease |
| L4 | 方法/化合物名 | lipid nanoparticle, viral vector |

### 2. 检索式结构模板

```
((L1_term1 OR L1_term2) AND (L2_term1 OR L2_term2)) OR
((L1_term1) AND (L3_term1 OR L3_term2)) OR
((L4_specific_term))
```

### 3. 检索运算符使用

- **AND**：同时出现，缩小范围
- **OR**：任一出现，扩大范围
- **NOT**：排除特定词
- **引号**：`"exact phrase"` 精确匹配
- **截词符**：`therap*` 匹配 therapy, therapies, therapeutic

### 4. PubMed字段标识

| 字段 | 标识 | 用途 |
|------|------|------|
| Title | [ti] | 标题检索 |
| Abstract | [ab] | 摘要检索 |
| MeSH Terms | [mh] | 医学主题词 |
| Publication Type | [pt] | 限定文献类型 |
| Date | [dp] | 限定时间范围 |
| Author | [au] | 作者检索 |

### 5. 检索式示例

**示例1：CRISPR基因编辑肿瘤治疗**
```
("CRISPR-Cas9"[tiab] OR "CRISPR"[tiab] OR "gene editing"[tiab])
AND ("cancer"[tiab] OR "tumor"[tiab] OR "oncology"[tiab])
AND ("therapy"[tiab] OR "treatment"[tiab])
```

**示例2：小分子药物递送**
```
("nanoparticle"[tiab] OR "liposome"[tiab] OR "micelle"[tiab])
AND ("drug delivery"[tiab] OR "formulation"[tiab])
AND ("small molecule"[tiab] OR "hydrophobic drug"[tiab])
```

## 筛选标准

### 相关性评分矩阵

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 技术匹配度 | 40% | 核心关键词重合度 |
| 研究新颖性 | 25% | 发表时间≤5年 |
| 影响力 | 20% | 期刊影响因子/被引次数 |
| 方法相似性 | 15% | 实验方法与专利技术相近 |

### 筛选阈值

- 评分 ≥ 8 分：必选
- 评分 6-7 分：候选，需对比
- 评分 < 6 分：排除

## 检索优化策略

### 结果过多时
1. 增加AND连接词
2. 使用更具体的MeSH术语
3. 限定更近的时间范围
4. 增加字段限定 [tiab]

### 结果过少时
1. 使用OR添加同义词
2. 放宽时间限制
3. 移除过于具体的检索词
4. 使用截词符扩展

### 特殊处理

- **扫描件PDF**：使用 `extract_pdfs_full_content` 获取完整文本
- **中文专利**：翻译关键术语后检索英文文献
- **新领域**：优先检索Review类文献了解概貌

## API使用规范

### PubMed E-utilities

- 请求间隔：≥0.3秒
- 单次最大结果：10000条
- 推荐分页：每次20-50条

### 端点说明

```
ESearch: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
EFetch:  https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
ESummary: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
```

## 复盘记录

| 日期 | 任务 | 问题 | 解决方案 | 更新内容 |
|------|------|------|----------|----------|
| - | - | - | - | - |