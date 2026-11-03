---
name: anthropic-skills-explorer
description: 浏览和探索 Anthropic Skills 仓库的专家助手。当用户要求查看 Claude 官方技能列表、了解可用的 skills、查询特定技能详情、或需要从 anthropics/skills 仓库获取技能信息时使用。
---

# Anthropic Skills Explorer

Anthropic Skills Explorer 是一个专门用于浏览和探索 Anthropic 官方 Claude Skills 仓库的技能。该仓库包含 16+ 个精心设计的技能示例，涵盖文档处理、设计、测试等多个领域。

## 技能列表概览

| # | Skill Name | 描述 |
|---|------------|------|
| 1 | algorithmic-art | 算法艺术创作技能 |
| 2 | brand-guidelines | 品牌指南管理技能 |
| 3 | canvas-design | Canvas 设计技能 |
| 4 | doc-coauthoring | 文档协作技能 |
| 5 | docx | Word 文档处理技能 |
| 6 | frontend-design | 前端设计技能 |
| 7 | internal-comms | 内部沟通技能 |
| 8 | mcp-builder | MCP 构建器技能 |
| 9 | pdf | PDF 处理技能 |
| 10 | pptx | PowerPoint 处理技能 |
| 11 | skill-creator | 技能创建技能 |
| 12 | slack-gif-creator | Slack GIF 创建技能 |
| 13 | theme-factory | 主题工厂技能 |
| 14 | web-artifacts-builder | Web 构建器技能 |
| 15 | webapp-testing | Web 应用测试技能 |
| 16 | xlsx | Excel 处理技能 |

## 核心技能详解

### skill-creator
用于创建、重构和投产 Agent Skills 的专家代理。采用工程优先工作流程。

### docx
Word 文档处理技能，支持创建、编辑 .docx 文件，包括注释和修订追踪功能。

### pdf
PDF 处理技能，支持 PDF 内容提取、表单填写等操作。

### mcp-builder
Model Context Protocol (MCP) 构建器技能，用于构建 MCP 服务器和工具。

### xlsx
Excel 电子表格处理技能，支持创建、编辑 .xlsx 文件。

### pptx
PowerPoint 演示文稿处理技能，支持创建、编辑 .pptx 文件。

### frontend-design
前端设计技能，用于创建高质量的 Web 界面和组件。

### webapp-testing
Web 应用测试技能，用于测试 Web 应用的功能和性能。

## 使用方法

### 1. 浏览所有技能
当用户询问"有哪些 Claude skills"或"查看所有技能"时，提取仓库页面内容并展示技能列表。

### 2. 查询特定技能详情
当用户指定某个技能名称时，直接访问该技能的 SKILL.md 文件并提取详细信息。

### 3. 获取技能内容
对于需要查看具体技能实现的请求，访问对应技能的 GitHub 页面，提取 SKILL.md 的完整内容。

## 仓库信息

- **GitHub 仓库**: https://github.com/anthropics/skills
- **Skills 目录**: https://github.com/anthropics/skills/tree/main/skills
- **星标数**: 51.5k+
- **Fork 数**: 5k+

## 快速开始

1. 用户提出关于 Claude skills 的问题
2. 确定用户需求：浏览全部技能 or 查看特定技能详情
3. 使用 `extract_content_from_websites` 工具提取相应内容
4. 整理并呈现结果给用户

## 示例查询

- "Anthropic 有哪些可用的 skills？"
- "查看 docx 技能的详细信息"
- "skill-creator 是做什么的？"
- "frontend-design 技能的功能有哪些？"
