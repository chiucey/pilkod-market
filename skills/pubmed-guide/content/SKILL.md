---
name: pubmed-guide
description: PubMed数据库使用指南助手。当用户询问如何使用PubMed数据库、进行文献检索、医学论文写作、MeSH主题词检索、PICO检索、高级检索策略、期刊筛选、文献管理等问题时使用。适用于科研工作者、医学生、研究生的医学研究全流程支持。
---

# PubMed数据库使用指南助手

## 核心能力

作为专业的PubMed数据库使用指南助手，本技能为您提供全面的文献检索支持，覆盖从基础检索到高级策略的完整知识体系。

## 一、PubMed基础介绍

### 1.1 什么是PubMed

PubMed是由美国国家医学图书馆(NLM)开发的免费生物医学文献数据库，包含超过3500万篇生物医学文献摘要，涵盖：
- 医学、护理、牙科、兽医、公共卫生等临床文献
- 生命科学领域的科研论文
- 链接到出版商的全文文章（部分免费）

### 1.2 PubMed网址与界面

- **访问地址**: https://pubmed.ncbi.nlm.nih.gov/
- **主要功能区**:
  - 搜索框：位于页面顶部
  - 高级检索：点击搜索框旁的"Advanced"链接
  - 筛选器：左侧边栏提供多种筛选选项
  - 筛选历史：支持复杂检索逻辑

## 二、基础检索技巧

### 2.1 简单检索

**使用方法**:
1. 在搜索框中输入关键词
2. 按Enter或点击"Search"按钮
3. 系统自动匹配标题、摘要和相关字段

**检索示例**:
```
diabetes treatment
cancer immunotherapy
COVID-19 vaccine
```

### 2.2 字段标签检索

使用方括号 `[ ]` 指定检索字段，提**高检索精确度**：

| 字段标签 | 说明 | 示例 |
|---------|------|------|
| [TI] | 标题 | diabetes[TI] |
| [AB] | 摘要 | immunotherapy[AB] |
| [AU] | 作者 | Smith JA[AU] |
| [DP] | 发表日期 | 2023[DP] |
| [TA] | 期刊名称 | NEJM[TA] |
| [MH] | MeSH主题词 | neoplasms[MH] |
| [PT] | 文献类型 | review[PT] |

### 2.3 常用字段检索示例

```pubmed
# 检索特定作者的论文
Zhang W[Author]

# 检索特定期刊的文章
Lancet[Journal]

# 检索特定年份的文献
2022[Publication Date]

# 检索特定文献类型的文章
clinical trial[Publication Type]

# 组合检索：在标题中包含"treatment"的糖尿病论文
diabetes[Title] AND treatment[Title]
```

## 三、高级检索

### 3.1 布尔运算符

使用逻辑运算符构建复杂检索：

| 运算符 | 符号 | 说明 |
|--------|------|------|
| AND | 与 | 同时包含两个词 |
| OR | 或 | 包含任一词 |
| NOT | 非 | 排除某词 |

**示例**:
```
# 检索同时包含糖尿病和心脏病的文献
diabetes AND heart disease

# 检索包含胰腺癌或肝癌的文献
pancreatic cancer OR liver cancer

# 检索糖尿病但排除1型糖尿病
diabetes NOT "type 1 diabetes"
```

### 3.2 高级检索页面

点击"Advanced"进入高级检索界面：

1. **构建检索式**：通过下拉菜单选择字段和布尔运算符
2. **检索历史**：查看历史检索并可组合使用
3. **预览结果**：添加检索式前可预览匹配数量

### 3.3 高级检索示例

```pubmed
# 例1：查找2020-2024年关于免疫治疗的综述
(immunotherapy[Title/Abstract]) AND
(review[Publication Type]) AND
("2020"[Date - Publication] : "2024"[Date - Publication])

# 例2：查找某特定医院发表的论文
("Massachusetts General Hospital"[Affiliation]) AND
(oncology[MeSH Terms])

# 例3：查找有DOI的开放获取文章
(open access[Filter]) AND (has abstract[Filter])
```

### 3.4 截词检索

使用 `*` 进行截词，匹配词根：

```
biolog*  →  biology, biological, biologist
tumor*  →  tumor, tumors, tumorous
```

## 四、MeSH主题词检索

### 4.1 什么是MeSH

MeSH (Medical Subject Headings) 是NLM编制的受控词汇表，用于标引和检索生物医学文献。MeSH提供：
- 标准化术语
- 主题词层级结构
- 主题词树状结构

### 4.2 MeSH检索方法

**方法一：通过MeSH数据库检索**

1. 访问：https://www.ncbi.nlm.nih.gov/mesh/
2. 输入概念词
3. 选择合适的主题词
4. 查看主题词详细信息和树状结构

**方法二：在PubMed中使用主题词检索**

```
# 使用主题词标签 [MeSH Terms]
neoplasms[MeSH Terms]

# 使用限定符/副主题词
neoplasms/therapy[MeSH Terms]
```

### 4.3 常用副主题词

| 副主题词 | 缩写 | 说明 |
|---------|------|------|
| /therapy | /ther | 治疗 |
| /diagnosis | /diag | 诊断 |
| /etiology | /etiol | 病因 |
| /prevention | /prev | 预防 |
| /pharmacology | /pharmacol | 药理学 |
| /adverse effects | /adv eff | 不良反应 |
| /genetics | /genet | 遗传学 |
| /metabolism | /metab | 代谢 |

### 4.4 MeSH主题词检索示例

```pubmed
# 检索糖尿病治疗的文献
Diabetes Mellitus/therapy[MeSH Terms]

# 检索肺癌诊断的文献
Lung Neoplasms/diagnosis[MeSH Terms]

# 检索药物不良反应的文献
(drug name[Substance Name]) AND (adverse effects[MeSH Terms])

# 使用主题词主要主题限定（不包含更广义的主题词）
neoplasms[MAJR]
```

### 4.5 MeSH层级结构

MeSH主题词呈树状结构，从广义到专指：

```
Diseases (C)
├── Neoplasms (C04)
│   ├── Neoplasms by Site (C04.588)
│   │   ├── Digestive System Neoplasms (C04.588.274)
│   │   │   ├── Liver Neoplasms (C04.588.274.505)
│   │   │   └── Pancreatic Neoplasms (C04.588.274.665)
```

**爆炸检索(Explosion)**: 选择父主题词时，系统自动包含其所有下位词。

## 五、PICO检索策略

### 5.1 PICO框架介绍

PICO是一种循证医学文献检索框架：

| 元素 | 说明 | 示例 |
|------|------|------|
| P - Patient/Problem | 患者或问题 | 2型糖尿病患者 |
| I - Intervention | 干预措施 | 二甲双胍治疗 |
| C - Comparison | 对照 | 安慰剂 |
| O - Outcome | 结局 | 血糖控制 |

### 5.2 PICO检索示例

**临床问题**: 二甲双胍对2型糖尿病患者的心血管保护效果如何？

**PICO分解**:
```
P: type 2 diabetes mellitus
I: metformin
C: placebo or standard treatment
O: cardiovascular outcomes
```

**检索式构建**:
```pubmed
("type 2 diabetes mellitus"[MeSH Terms]) AND
(metformin[MeSH Terms]) AND
(cardiovascular[Title/Abstract])
```

### 5.3 不同研究类型的PICO

| 研究类型 | PICO关注点 | 检索过滤器 |
|---------|-----------|-----------|
| 治疗 | I vs C的疗效比较 | Clinical Trial[pt] |
| 诊断 | I的准确性 | sensitivity and specificity |
| 预后 | 疾病结局 | cohort study |
| 病因 | 暴露因素 | etiological study |
| 系统评价 | 综合证据 | Meta-Analysis[pt] |

## 六、期刊检索

### 6.1 按期刊名称检索

```pubmed
# 检索特定期刊发表的文章
"New England Journal of Medicine"[Journal]

# 期刊缩写检索
NEJM[Journal]

# 多个期刊检索
(Lancet[Journal] OR BMJ[Journal])
```

### 6.2 期刊筛选器

PubMed提供多种期刊筛选：
- 核心临床期刊 (Core Clinical Journals)
- 牙科文献
- 护理文献
- 生物医学文献

### 6.3 期刊影响因子相关

PubMed不直接显示影响因子，可结合以下方式：
1. 使用外部工具（Journal Citation Reports）
2. 关注高被引文章
3. 查看期刊排名

## 七、筛选与精炼

### 7.1 常用筛选条件

| 筛选器 | 说明 |
|--------|------|
| Article types | 文献类型（综述、临床试验等） |
| Text availability | 全文可得性 |
| Publication dates | 发表日期 |
| Species | 物种（人类/动物） |
| Languages | 语言 |
| Sex | 性别 |

### 7.2 文献类型检索

```pubmed
# 系统综述
systematic review[Publication Type]

# 荟萃分析
meta-analysis[Publication Type]

# 临床试验
clinical trial[Publication Type]

# 随机对照试验
randomized controlled trial[Publication Type]

# 指南
practice guideline[Publication Type]

# 病例报告
case reports[Publication Type]
```

## 八、文献管理与导出

### 8.1 导出到文献管理软件

1. 选择目标文献（勾选复选框）
2. 点击"Cite"按钮
3. 选择引用格式（APA、MLA等）
4. 复制或导出到文献管理器

### 8.2 批量导出

- 使用"Send to"功能
- 支持格式：Citation、RIS、BIBTEX、PMID列表
- 导出到Google Scholar、EndNote、Zotero等

## 九、实用检索模板

### 9.1 系统综述检索模板

```pubmed
# 结构化检索策略
("search terms for condition"[MeSH Terms]) AND
("search terms for intervention"[MeSH Terms]) AND
("systematic review"[Publication Type] OR
"meta-analysis"[Publication Type])
```

### 9.2 临床指南检索模板

```pubmed
("condition"[MeSH Terms]) AND
("practice guideline"[Publication Type])
```

### 9.3 临床试验检索模板

```pubmed
("condition"[MeSH Terms]) AND
("intervention"[MeSH Terms]) AND
("clinical trial"[Publication Type])
```

## 十、常见问题解答

### Q1: 如何获取全文？
A: 点击文献标题下的"Full Text Links"，部分文章可免费获取（Open Access）。

### Q2: 如何保存检索策略？
A: 使用"Create alert"功能，设置定期邮件提醒。

### Q3: 如何查找某领域的高影响力文章？
A: 使用"Citation booster"或按"Most cited"排序。

### Q4: 如何提高检索效率？
A:
1. 使用MeSH主题词代替自由词
2. 利用高级检索构建复杂查询
3. 保存常用检索式

---

## 快速检索公式

### 基础公式
```
关键词[字段] AND 关键词[字段] OR 关键词[字段]
```

### 循证医学公式
```
(Population) AND (Intervention) AND (Outcome) AND (Study Type)
```

### 综述检索公式
```
(疾病主题词) AND (干预主题词) AND (review[pt] OR meta-analysis[pt])
```

---

*本指南由MiniMax Agent生成，帮助您高效使用PubMed数据库进行医学文献检索。*
