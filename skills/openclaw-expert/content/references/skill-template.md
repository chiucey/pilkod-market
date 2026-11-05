# OpenClaw 技能开发模板

## 标准目录结构

```
skill-name/
├── SKILL.md              # 必填：技能定义文件
├── _meta.json             # 必填：元数据 {"id":"...", "version":"..."}
├── scripts/              # 可选：自动化脚本
│   ├── init_skill.py     # 初始化脚本
│   └── validate.py       # 验证脚本
├── references/           # 可选：参考文档
└── assets/               # 可选：静态资源
```

## SKILL.md 标准格式

```yaml
---
name: skill-name                    # 连字符格式，与文件夹名一致
description: 清晰描述技能功能...     # 必须包含触发短语
---

# 技能标题

## 核心能力
- 能力 1
- 能力 2

## 工作流程
### 步骤 1：...
### 步骤 2：...

## 示例
...
```

## Frontmatter 必填字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 技能名称，连字符格式 |
| description | string | 技能描述，包含触发短语 |

## 命名规范

- 文件夹名： kebab-case (openclaw-expert)
- Frontmatter name：与文件夹名完全一致
- 避免使用中文或特殊字符

## 触发短语设计

在 description 中包含用户可能说的话：
- "Use when..." 模式
- 具体场景描述
- 关键词和同义词
