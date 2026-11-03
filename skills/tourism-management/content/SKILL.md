---
name: tourism-management
description: This skill should be used when the user needs assistance with tourism management professional tasks, including academic paper writing, tour itinerary planning, hotel management analysis, tourism destination research, internship reports, coursework assignments, terminology translation, and any content related to tourism management education. Triggers when the user mentions tourism itinerary design, hotel KPI analysis, ecotourism, travel agency operations, tourism law, visitor satisfaction surveys, SWOT analysis for destinations, study tour (研学旅游), cultural-tourism integration (文旅融合), smart/digital tourism, rural tourism, red tourism, health & wellness tourism, night-time economy, DMO, RevPAR, ADR, SERVQUAL, Butler model, push-pull theory, or any tourism-related coursework, exam preparation, or professional task.
---

# 旅游管理专业技能

## 概述

本技能面向旅游管理专业学生（尤其是高校本科/专科生）及旅游行业从业者，提供覆盖旅游管理全专业方向的AI辅助支持，包括：学术论文写作（课程论文/学年论文/毕业论文）、旅游线路设计、酒店管理分析、景区管理、实习报告撰写（旅行社/酒店/景区/OTA全岗位）、专业术语翻译、文旅融合方案、研学旅游设计、**考试备考指导（导游证/教资/期末考试）**等高频学习与工作任务。

---

## 核心能力领域

### 1. 学术论文与作业写作
- 论文结构搭建（绪论、文献综述、研究设计、分析、结论）
- 摘要与关键词撰写（中英文）
- 研究方法选择（定量/定性/混合）
- 理论框架匹配（推拉理论、SERVQUAL、体验经济、Butler模型、场所依恋、文化认同等）
- 参考文献格式（GB/T 7714）
- 选题建议与论证（2024–2026热点方向）
- 文献综述撰写与综合评述

**参考资源：** `references/academic-writing-guide.md`（含论文结构、方法论、理论框架、期刊目录、最新选题）

---

### 2. 旅游线路规划设计
- 目的地资源分析（自然+人文）
- 行程天数与节奏安排
- SWOT分析与市场定位
- 费用预算编制（成本核算）
- 专项线路设计：研学旅游、亲子游、康养游、红色旅游、文化遗产游、夜间旅游
- 应急预案与注意事项

**模板资源：** `assets/tour-plan-template.md`（含通用线路 + 研学专项 + 康养专项模板）

**使用方式：** 读取模板后，根据用户提供的目的地、天数、主题等信息填充内容。

---

### 3. 酒店管理
- 星级酒店评定标准解读（GB/T 14308）
- 核心KPI计算（出租率 OCC、ADR、RevPAR、TRevPAR、GOP）
- 各部门职能与管理流程
- 服务质量评估（SERVQUAL五维度）
- 收益管理策略（Revenue Management）
- 民宿与精品酒店运营分析
- 酒店数字化转型：OTA、PMS、CRM、智能客房

**参考资源：** `references/knowledge-base.md`（酒店管理章节）

---

### 4. 旅游目的地分析
- SWOT/PESTEL分析框架应用
- Butler生命周期阶段判断与策略
- 客源市场分析
- 旅游资源评价（3A/4A/5A标准）
- 文旅融合策略（IP开发、沉浸式体验、非遗活化）
- 可持续旅游建议与碳中和方案

---

### 5. 研学旅游与专项旅游
- 研学旅游课程设计（主题、目标、课程大纲）
- 研学基地评估标准
- 红色旅游线路开发
- 康养旅游产品设计
- 乡村旅游振兴方案
- 夜间旅游经济方案

**参考资源：** `references/knowledge-base.md`（研学旅游与专项旅游章节）

---

### 6. 实习报告撰写
- 标准实习报告结构（目的、单位介绍、过程、收获、建议）
- 工作案例描述技巧
- 专业理论与实践结合表述
- OTA平台（携程/飞猪/美团）实习专项内容
- 酒店/旅行社/景区不同岗位实习模板

**模板资源：**
- `assets/internship-report-template.md`（旅行社通用模板 + OTA/电商专项）
- `assets/internship-templates-supplement.md`（**新增：景区管理专项 + 酒店管理全岗位专项**）

---

### 7. 专业术语与翻译
- 中英文旅游术语互译（A-Z完整对照）
- 专业词汇解释
- 英文摘要/关键词翻译与润色
- 文旅融合、数字旅游新兴术语

**参考资源：** `references/terminology.md`（A-Z术语对照表，含最新数字旅游词汇）

---

### 8. 考试备考指导（**新增**）

- 导游资格证：科目三《导游业务》+ 科目四《政策法规》高频考点
- 教师资格证：科目二《教育知识与能力》旅游教育相关考点
- 专业课期末考试：核心概念速记、理论速记卡、真题技巧

**参考资源：** `references/exam-prep-guide.md`（含高频考点速记表、口诀、备考计划）

---

### 9. 旅游法律法规
- 《旅游法》核心条款解读与案例分析
- 旅行社条例应用
- 导游资质与管理规范
- 旅游者权益保护实务
- 旅游纠纷处理程序（12301投诉热线）

**参考资源：** `references/knowledge-base.md`（法律法规章节）

---

## 工作流程指导

### 论文写作任务
1. 读取 `references/academic-writing-guide.md` 获取论文结构和理论框架
2. 确认论文主题、研究方法、字数要求、是否需要英文摘要
3. 按照标准结构逐节撰写，并提供写作建议
4. 参考文献按GB/T 7714格式生成
5. 如需检索文献，推荐中国知网（CNKI）、万方、Google Scholar

### 旅游线路设计任务
1. 读取 `assets/tour-plan-template.md` 获取完整模板
2. 向用户确认：目的地、天数、人数、预算、主题、目标客群
3. 结合 `references/knowledge-base.md` 填充目的地资源分析
4. 如为研学线路，额外补充课程目标、学习内容、安全须知
5. 输出完整的Markdown格式方案

### 酒店管理分析任务
1. 读取 `references/knowledge-base.md` 酒店管理章节
2. 计算关键KPI（需用户提供数据）
3. 应用SERVQUAL模型进行服务质量评估
4. 结合收益管理、数字化转型趋势提供管理建议

### 研学旅游设计任务
1. 读取 `references/knowledge-base.md` 研学旅游章节
2. 确认研学主题（自然/人文/科技/爱国/劳动）、目标年龄段
3. 设计课程目标 → 研学路线 → 活动方案 → 评价体系
4. 参照国家研学旅游标准（《研学旅行服务规范》GB/T 42052）

### 术语翻译任务
1. 读取 `references/terminology.md`
2. 直接查找对照表给出结果
3. 若术语表中未收录，基于专业知识进行翻译并说明
4. 英文摘要润色需关注学术表达规范

---

## 注意事项

- 论文写作时，始终强调学术诚信，所有引用须注明来源；AI生成内容须经学生自行修改完善
- 旅游线路报价仅作学习参考，实际价格需联系旅行社确认
- 法律法规内容以最新有效版本为准，建议查阅官方文件（文化和旅游部官网）
- 实习报告模板需根据用户实际实习情况个性化填写，避免套话
- 研学旅游方案需特别关注未成年人安全规范

---

*技能版本：v3.0 | 优化日期：2026-04-14*
