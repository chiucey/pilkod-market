---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2cf73913b92326c2385c9c9e62decd3f
    PropagateID: 2cf73913b92326c2385c9c9e62decd3f
    ReservedCode1: 3044022031f15f6f3976fdaca26589319a30739b77d270e891942613b3709f2ad74132d102203457bb282843c68638ff0c5753f21b14073529616c477e97893a2a6c35447ad6
    ReservedCode2: 3045022100a7971ac9e93efb9bee0622072b1703cb6ea766e426a18c7fcff372a35a5c38e5022059a64c847a11093bfad7f73c40088284b54217bd48b465169364b5cbcca5a68c
---

# 文档类型与解析指南

## 支持的文档格式

### 1. PDF 文档
**特点**：
- 跨平台兼容性最佳
- 保持原始排版格式
- 可能包含扫描图片（非文本）

**解析工具**：
- `extract_pdfs_key_info`: 快速提取关键信息
- `extract_pdfs_full_content`: 完整提取文本内容

**适用场景**：
- 学术论文
- 技术手册
- 电子书籍
- 报告文档

### 2. Word 文档 (.docx)
**特点**：
- 结构化程度高
- 包含标题、列表等元信息
- 支持跟踪修订和批注

**解析建议**：
- 直接读取文件内容
- 提取段落和标题结构

**适用场景**：
- 商业文档
- 合同协议
- 项目报告

### 3. 纯文本 (.txt)
**特点**：
- 格式简单
- 无样式信息
- 易于直接处理

**解析建议**：
- 使用 Read 工具直接读取
- 处理编码问题（UTF-8、GBK）

**适用场景**：
- 日志文件
- 配置文件
- 代码注释

### 4. Markdown (.md)
**特点**：
- 结构清晰
- 支持代码块
- 轻量级标记语言

**解析建议**：
- 直接读取文件内容
- 识别标题层级和代码块

**适用场景**：
- 技术文档
- README 文件
- 博客文章

## 文档结构识别

### 学术论文结构
```
1. 摘要 (Abstract)
2. 引言 (Introduction)
3. 相关工作 (Related Work)
4. 方法 (Methodology)
5. 实验 (Experiments)
6. 结论 (Conclusion)
7. 参考文献 (References)
```

### 技术文档结构
```
1. 概述 (Overview)
2. 安装指南 (Installation)
3. 快速开始 (Quick Start)
4. 核心功能 (Core Features)
5. API 参考 (API Reference)
6. 常见问题 (FAQ)
```

### 商业报告结构
```
1. 执行摘要 (Executive Summary)
2. 背景介绍 (Background)
3. 市场分析 (Market Analysis)
4. 竞争分析 (Competitive Analysis)
5. 策略建议 (Recommendations)
6. 附录 (Appendix)
```

## 关键信息提取模式

### 论文关键信息
- 标题
- 作者
- 机构
- 发表年份
- 摘要
- 关键词
- 主要贡献
- 实验结果

### 合同关键信息
- 合同双方
- 签订日期
- 有效期
- 主要条款
- 违约责任
- 终止条件

### 报告关键信息
- 报告标题
- 发布机构
- 发布日期
- 报告期间
- 主要发现
- 核心数据
- 建议措施
