# Publishing Kit

## Skill Summary

**Name:** TH B UI Skill
**ID:** th-b-ui-skill
**Category:** Design System / UI Generation

## Description

TH B UI Skill is a reusable skill for generating enterprise backend prototype interfaces. It沉淀了页面结构、界面语义和 UI 规范，帮助 AI 生成更规整、更克制、更符合企业后台场景的界面。

## Selling Points

- **企业后台专用** - 不同于消费级页面，专注管理后台场景
- **结构化规范** - 内置列表页、详情页、表单页、抽屉页、仪表盘模板
- **视觉克制** - 中性色表面、单一强调色、清晰按钮层级
- **组件语义** - Base*、Business*、Standard* 命名体系
- **开箱即用** - 支持直接引用生成原型、Figma 提示词、前端代码

## Target Users

- 前端开发者需要快速生成后台原型
- 产品经理需要设计管理页面
- AI 开发者需要企业风格 UI 规范
- 设计师需要后台组件和页面模板

## Example Prompts

### 列表页生成
```
请用 $th-b-ui-skill 生成一个资源管理列表页原型，要求界面紧凑、配色克制、表格行为稳定。
```

### 表单页生成
```
请用 $th-b-ui-skill 生成一个审批表单原型，要求分组清晰、控件紧凑、校验明确。
```

### Figma 提示词生成
```
请用 $th-b-ui-skill 生成一个详情页的 Figma 提示词，页面包含状态头部、摘要卡片、关联标签页。
```

### 前端代码生成
```
请用 $th-b-ui-skill 生成企业后台风格的前端页面代码，要求中性色表面、紧凑表单、清晰按钮层级。
```

## Compatibility

- Skill 平台标准结构
- Codex skills 目录兼容
- GitHub 仓库分发支持
- 支持 YAML 和 Markdown 格式

## Quick Start

最简单的调用方式：
```
请用 $th-b-ui-skill 生成一个后台页面原型。
```

更推荐的调用方式：
```
请用 $th-b-ui-skill 生成一个资源管理列表页原型。
要求：
- 页面结构贴近内部后台系统
- 顶部使用标准筛选区结构
- 中间使用标准数据表格式区域
- 状态使用标签式方式表达
```
