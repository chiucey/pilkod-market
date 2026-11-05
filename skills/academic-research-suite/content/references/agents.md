# 智能体详细职责说明

## 深度研究智能体 (Deep Research Agents)

### 1. 研究问题智能体 (Research Question Agent)
- **职责**: 使用 FINER 框架 (Feasible, Interesting, Novel, Ethical, Relevant) 明确研究问题
- **输入**: 用户主题描述
- **输出**: 结构化研究问题 + 假设

### 2. 研究架构师 (Research Architect)
- **职责**: 设计完整方法论架构
- **输出**: 研究设计路线图、数据收集计划、分析策略

### 3. 文献检索智能体 (Bibliography Agent)
- **职责**: 系统性文献搜索
- **技能**: PRISMA 流程、布尔检索、数据库选择 (PubMed, Web of Science, Scopus, etc.)
- **输出**: 检索策略 + 文献列表

### 4. 来源验证智能体 (Source Verification Agent)
- **职责**: 证据分级与掠夺性期刊检测
- **输出**: 来源可信度评分 + 预警列表

### 5. 综合智能体 (Synthesis Agent)
- **职责**: 跨来源整合分析
- **技能**: 主题建模、概念映射、差距识别
- **输出**: 综合分析报告

### 6. 报告撰写智能体 (Report Compiler)
- **职责**: 生成学术格式报告
- **格式**: APA 7.0 (默认)
- **输出**: 结构化研究报告

### 7. 主编 (Editor-in-Chief)
- **职责**: Q1 期刊编辑视角评审
- **评估**: 期刊匹配度、创新性、学术意义

### 8. 魔鬼代言人 (Devil's Advocate)
- **职责**: 假设质疑与逻辑挑战
- **检查点**: 3 个关键质疑点
- **输出**: 潜在弱点报告

### 9. 伦理审查智能体 (Ethics Review Agent)
- **职责**: AI 披露验证与归因完整性
- **检查**: 伦理合规性、AI 使用透明度

### 10. 苏格拉底导师 (Socratic Mentor)
- **职责**: 引导式研究对话
- **方法**: 苏格拉底提问法
- **收敛标准**: 确保研究深度

### 11. 偏倚风险智能体 (Risk of Bias Agent)
- **职责**: 系统评价偏倚评估
- **工具**: RoB 2 (随机试验)、ROBINS-I (非随机干预研究)
- **输出**: 偏倚风险矩阵

### 12. 元分析智能体 (Meta-Analysis Agent)
- **职责**: 定量综合分析
- **技能**: 效应量计算、异质性检验 (I²)、森林图、GRADE 评级
- **输出**: 元分析结果

### 13. 监控智能体 (Monitoring Agent)
- **职责**: 持续文献监控
- **功能**: 预警系统、新文献通知

---

## 学术论文写作智能体 (Academic Paper Agents)

### 1. 摄入智能体 (Intake Agent)
- **职责**: 配置访谈与需求分析
- **检测**: 意图识别、手动/自动模式切换

### 2. 文献策略师 (Literature Strategist)
- **职责**: 搜索策略与注释文献
- **输出**: annotated bibliography

### 3. 结构架构师 (Structure Architect)
- **职责**: 论文大纲与字数分配
- **支持结构**: IMRaD, 主题综述, 理论分析, 案例研究, 政策简报, 会议论文

### 4. 论据构建智能体 (Argument Builder)
- **职责**: 论点 + 论据链构建
- **技能**: 逻辑论证、反驳预设

### 5. 起草智能体 (Draft Writer)
- **职责**: 分节撰写
- **模式**: 逐节或全稿

### 6. 引用合规智能体 (Citation Compliance)
- **职责**: 多格式引用审计与转换
- **格式**: APA 7.0, IEEE, Chicago, MLA, Vancouver

### 7. 双语摘要智能体 (Abstract Bilingual)
- **职责**: 中英文摘要生成
- **格式**: 结构化摘要

### 8. 同行评审智能体 (Peer Reviewer)
- **职责**: 5 维度评审 (最多 2 轮)
- **输出**: 评审报告

### 9. 格式化智能体 (Formatter)
- **职责**: 多格式输出
- **格式**: LaTeX, DOCX, PDF, Markdown

### 10. 苏格拉底导师 (Socratic Mentor)
- **职责**: 章节级引导规划
- **方法**: 引导用户逐步完成

### 11. 可视化智能体 (Visualization Agent)
- **职责**: 图表生成
- **支持**: 9 种图表类型、matplotlib、ggplot2

### 12. 修改教练智能体 (Revision Coach Agent)
- **职责**: 审稿意见解析与修改路线图
- **输入**: 审稿意见
- **输出**: Revision Roadmap

---

## 同行评审智能体 (Paper Reviewer Agents)

### 1. 领域分析师 (Field Analyst)
- **职责**: 领域识别与评审人格配置

### 2. 主编 (Editor-in-Chief)
- **评估**: 期刊匹配、创新性、学术意义

### 3. 方法论评审 (Methodology Reviewer)
- **评估**: 研究设计、统计方法、可重复性

### 4. 领域评审 (Domain Reviewer)
- **评估**: 文献覆盖、理论框架

### 5. 视角评审 (Perspective Reviewer)
- **评估**: 跨学科影响、实践价值

### 6. 魔鬼代言人评审 (Devil's Advocate Reviewer)
- **评估**: 核心论点质疑、逻辑谬误

### 7. 编辑综合 (Editorial Synthesizer)
- **职责**: 共识分析与 Rubric 评分
- **输出**: 0-100 质量评分 + 决策建议
