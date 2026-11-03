# PubMed检索字段标签完整参考

## 可检索字段一览表

| 字段标签 | 全称 | 中文说明 | 示例 |
|---------|------|---------|------|
| [AU] | Author | 作者 | Zhang W[AU] |
| [TI] | Title | 标题 | cancer[TI] |
| [TIAB] | Title/Abstract | 标题/摘要 | immunotherapy[TIAB] |
| [AB] | Abstract | 摘要 | bioinformatics[AB] |
| [MH] | MeSH Terms | MeSH主题词 | diabetes mellitus[MH] |
| [MAJR] | MeSH Major Topic | 主要MeSH主题词 | neoplasms[MAJR] |
| [TW] | Text Word | 文本词 | treatment[TW] |
| [PT] | Publication Type | 文献类型 | review[PT] |
| [DP] | Date of Publication | 发表日期 | 2023[DP] |
| [DA] | Date of Entry | 入库日期 | 2023[DA] |
| [EDAT] | Entrez Date | Entrez索引日期 | 2023[EDAT] |
| [TA] | Journal | 期刊名称 | NEJM[TA] |
| [AID] | Article Identifier | 文章标识符 | 10.1056[DOI] |
| [FAU] | Full Author Name | 完整作者名 | Zhang Wei[FAU] |
| [CN] | Corporate Author | 机构作者 | WHO[CN] |
| [SI] | Secondary Source ID | 次级来源ID | PMID[SI] |
| [PMCID] | PMCID | PubMed Central ID | PMC[PMCID] |
| [GR] | Grant Number | 基金号 | R01[GR] |
| [LID] | Location ID | 位置ID | 10.1234[LID] |
| [doi] | DOI | 数字对象标识符 | 10.1056[doi] |
| [BOOK] | Book | 图书 | 书籍标题[BOOK] |
| [ALL] | All Fields | 所有字段 | (全部字段) |

## 布尔运算符

| 运算符 | 说明 | 示例 |
|--------|------|------|
| AND | 两个条件必须同时满足 | diabetes AND hypertension |
| OR | 任一条件满足即可 | aspirin OR salicylate |
| NOT | 排除包含某词的文章 | cancer NOT breast cancer |
| () | 优先级分组 | (A OR B) AND C |

## 文献类型 [PT]

| 类型 | 说明 | 使用场景 |
|------|------|---------|
| clinicaltrial | 临床试验 | 干预性研究 |
| randomizedcontrolledtrial | 随机对照试验 | 高质量证据 |
| controlledclinicaltrial | 对照临床试验 | 干预性研究 |
| meta-analysis | 荟萃分析 | 循证医学 |
| systematicreview | 系统综述 | 综合证据 |
| review | 综述 | 了解领域概况 |
| case-reports | 病例报告 | 罕见病例 |
| clinicaltrial, phase i | I期临床试验 | 安全性评估 |
| clinicaltrial, phase ii | II期临床试验 | 有效性评估 |
| clinicaltrial, phase iii | III期临床试验 | 确认性试验 |
| clinicaltrial, phase iv | IV期临床试验 | 上市后监测 |
| comparative study | 比较研究 | 对比分析 |
| evaluation study | 评估研究 | 效果评价 |
| multicenter study | 多中心研究 | 外部效度 |
| validation study | 验证研究 | 方法验证 |
| practice guideline | 实践指南 | 临床指导 |
| consensus development conference | 共识会议 | 专家共识 |
| historical article | 历史文章 | 历史回顾 |
| biography | 传记 | 人物介绍 |
| duplicate publication | 重复发表 | 注意排除 |
| editorial | 社论 | 专家观点 |
| letter | 信件 | 通信 |
| news | 新闻 | 时事报道 |
| newspaper article | 报纸文章 | 大众传播 |
| portrait | 肖像 | 人物介绍 |
| dataset | 数据集 | 数据共享 |
| webcast | 网络广播 | 在线讲座 |

## 语言 [LA]

| 缩写 | 语言 |
|------|------|
| eng | 英语 |
| chi | 中文 |
| jpn | 日语 |
| ger | 德语 |
| fre | 法语 |
| spa | 西班牙语 |
| ita | 意大利语 |
| por | 葡萄牙语 |
| rus | 俄语 |
| dut | 荷兰语 |
| pol | 波兰语 |
| swe | 瑞典语 |
| nor | 挪威语 |
| dan | 丹麦语 |
| fin | 芬兰语 |
| cze | 捷克语 |
| hun | 匈牙利语 |
| rum | 罗马尼亚语 |
| gre | 希腊语 |
| heb | 希伯来语 |
| ara | 阿拉伯语 |
| kor | 韩语 |
| tur | 土耳其语 |

## 研究特征字段

| 字段 | 说明 | 示例 |
|------|------|------|
| [MH:noexp] | 不扩展MeSH | 使用单个主题词 |
| [MAJ] | 主要主题词 | 该词是文章重点 |
| [OT] | Other Term | 其他关键词 |
| [Pharmacological Action] | 药理作用 | MeSH药理作用词 |
