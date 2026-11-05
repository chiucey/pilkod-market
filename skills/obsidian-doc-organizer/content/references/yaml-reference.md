# YAML Frontmatter 参考文档

本文档提供 Obsidian 文档整理技能的 YAML 属性完整参考。

---

## 普通文档 YAML 示例

### 示例 1：AI 工具类文档

```yaml
---
description: Kimi CLI安装配置与版本更新完整指南
source_url: https://platform.moonshot.cn/docs/guide/kimi-cli-support
github_url: https://github.com/MoonshotAI/kimi-cli
images_folder: images/
original_topic: KimiCLI安装、安装及版本更新
---
```

### 示例 2：编程语言类文档

```yaml
---
description: Python基础语法、数据类型、控制结构学习指南
source_url: https://docs.python.org/3/tutorial/
images_folder: images/
original_topic: Python入门教程、基础语法
---
```

### 示例 3：框架技术类文档

```yaml
---
description: React Hooks完整指南与最佳实践
source_url: https://react.dev/reference/react
github_url: https://github.com/facebook/react
images_folder: images/
original_topic: React Hooks使用、useState、useEffect
---
```

---

## README 文档 YAML 示例

```yaml
---
description: Kimi CLI完整使用指南、SDK开发文档、Skill资源索引
tags: [index, ai, kimi, cli, tool, sdk]
---
```

---

## YAML 属性填写规范

### 普通文档属性

| 属性名 | 必需性 | 说明 | 示例 |
|-------|-------|------|------|
| `description` | 必需 | 控制在50字以内，清晰描述核心内容 | `Kimi CLI安装配置与版本更新指南` |
| `source_url` | 推荐 | 原始文档的在线来源链接 | `https://example.com/docs` |
| `github_url` | 可选 | 相关GitHub项目仓库链接 | `https://github.com/user/repo` |
| `images_folder` | 必需 | 固定填写 `images/` | `images/` |
| `original_topic` | 必需 | 忠实填写原始文档的完整标题 | `原始文档标题` |

### README 文档属性

| 属性名 | 必需性 | 说明 | 示例 |
|-------|-------|------|------|
| `description` | 必需 | 不超过50字，一句话概括文件夹核心内容 | `Python编程基础与进阶指南` |
| `tags` | 必需 | 必须包含 `index`，其他根据内容添加 | `[index, python, programming]` |

---

## 标签体系参考

### AI 工具类

```yaml
tags: [index, ai, kimi, cli, tool, mcp, skill]
```

适用场景：
- Kimi CLI
- ChatGPT
- Claude
- 其他 AI 助手工具

### 编程开发类

```yaml
tags: [index, python, javascript, golang, sdk, api]
```

适用场景：
- Python 编程
- JavaScript/TypeScript
- Go 语言
- API 开发

### 框架技术类

```yaml
tags: [index, react, vue, frontend, backend, framework]
```

适用场景：
- React
- Vue
- Angular
- Svelte

### 数据库类

```yaml
tags: [index, database, mysql, postgresql, mongodb]
```

适用场景：
- MySQL
- PostgreSQL
- MongoDB
- Redis

### DevOps 类

```yaml
tags: [index, devops, docker, kubernetes, ci-cd]
```

适用场景：
- Docker 容器
- Kubernetes
- CI/CD 流水线
- 云原生

---

## 质量检查清单

整理完成后，使用以下清单进行自检：

- [ ] 所有 YAML 属性填写完整准确
- [ ] `description` 符合 50 字限制
- [ ] README 的 `tags` 包含 `index`
- [ ] 属性顺序一致
- [ ] 格式符合标准 YAML frontmatter 规范
- [ ] `images_folder` 固定为 `images/`

---

## 常见错误避免

### ❌ 错误示例

```yaml
---
Description: 这里是描述（大小写错误）
description: 这个描述太长了，超过了五十个字的限制，包含了太多不必要的词汇内容
tags: [INDEX, AI, KIMI]  # 使用大写
---
```

### ✅ 正确示例

```yaml
---
description: 简明扼要的描述
tags: [index, ai, kimi]
---
```

---

## 文档维护

**最后更新**：2026-03-27
**维护者**：Obsidian Doc Organizer 技能
