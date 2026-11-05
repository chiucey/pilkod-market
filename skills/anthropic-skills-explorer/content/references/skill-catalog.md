# Anthropic Skills 参考目录

## 官方资源链接

### 仓库链接
- **主仓库**: https://github.com/anthropics/skills
- **Skills 目录**: https://github.com/anthropics/skills/tree/main/skills

### 各技能直接链接

| 技能名称 | GitHub 链接 |
|---------|------------|
| algorithmic-art | https://github.com/anthropics/skills/tree/main/skills/algorithmic-art |
| brand-guidelines | https://github.com/anthropics/skills/tree/main/skills/brand-guidelines |
| canvas-design | https://github.com/anthropics/skills/tree/main/skills/canvas-design |
| doc-coauthoring | https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring |
| docx | https://github.com/anthropics/skills/tree/main/skills/docx |
| frontend-design | https://github.com/anthropics/skills/tree/main/skills/frontend-design |
| internal-comms | https://github.com/anthropics/skills/tree/main/skills/internal-comms |
| mcp-builder | https://github.com/anthropics/skills/tree/main/skills/mcp-builder |
| pdf | https://github.com/anthropics/skills/tree/main/skills/pdf |
| pptx | https://github.com/anthropics/skills/tree/main/skills/pptx |
| skill-creator | https://github.com/anthropics/skills/tree/main/skills/skill-creator |
| slack-gif-creator | https://github.com/anthropics/skills/tree/main/skills/slack-gif-creator |
| theme-factory | https://github.com/anthropics/skills/tree/main/skills/theme-factory |
| web-artifacts-builder | https://github.com/anthropics/skills/tree/main/skills/web-artifacts-builder |
| webapp-testing | https://github.com/anthropics/skills/tree/main/skills/webapp-testing |
| xlsx | https://github.com/anthropics/skills/tree/main/skills/xlsx |

## SKILL.md 文件结构

每个技能通常包含以下文件结构：

```
skill-name/
├── SKILL.md          # 主技能文件（必需）
├── references/       # 参考文档目录
│   └── *.md         # 参考文档
├── scripts/          # 脚本目录
│   └── *.py / *.sh  # 辅助脚本
├── forms.md         # 表单相关文档（可选）
├── reference.md     # 参考文档（可选）
└── LICENSE.txt     # 许可证
```

## 技能分类

### 文档处理类
- docx - Word 文档
- pdf - PDF 文件
- xlsx - Excel 电子表格
- pptx - PowerPoint 演示文稿

### 设计类
- algorithmic-art - 算法艺术
- brand-guidelines - 品牌指南
- canvas-design - Canvas 设计
- frontend-design - 前端设计
- theme-factory - 主题工厂

### 开发工具类
- mcp-builder - MCP 服务器构建
- web-artifacts-builder - Web 构建器
- webapp-testing - Web 测试

### 协作与沟通
- doc-coauthoring - 文档协作
- internal-comms - 内部沟通

### 其他
- skill-creator - 技能创建器
- slack-gif-creator - Slack GIF 创建

## 提取技能详情的方法

### 方法 1: 提取目录列表
```
URL: https://github.com/anthropics/skills/tree/main/skills
工具: extract_content_from_websites
提示: 提取所有技能名称和描述
```

### 方法 2: 提取单个技能详情
```
URL: https://github.com/anthropics/skills/tree/main/skills/{skill-name}
工具: extract_content_from_websites
提示: 提取技能的完整描述、文件结构和功能
```

### 方法 3: 提取 SKILL.md 原文
```
URL: https://github.com/anthropics/skills/blob/main/skills/{skill-name}/SKILL.md
工具: extract_content_from_websites
提示: 提取 SKILL.md 的完整内容
```

## 常用提取提示词

### 提取技能列表
```
"Extract all skill names, descriptions, and any relevant information about the available skills in this repository"
```

### 提取单个技能详情
```
"Extract the full skill description, frontmatter, and any other relevant details about this skill"
```

### 提取文件内容
```
"Extract all the content from this file, including code, documentation, and any other text"
```
