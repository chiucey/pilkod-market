---
name: research-analyzer
description: 综合研究分析工具 - 整合多源搜索、学术文献、数据分析，一键生成研究报告 (Security Fixed)
homepage: https://github.com/openclaw/research-analyzer
metadata: {"openclaw":{"emoji":"🔬","requires":{"bins":["node","curl"],"env":["TAVILY_API_KEY"]},"primaryEnv":"TAVILY_API_KEY"}}
---

# Research Analyzer 🔬

一站式研究分析工具，整合网络搜索、学术文献、数据分析，快速生成专业研究报告。

## 功能特性

- 🔍 **多源搜索** - Tavily 网络搜索 + 百度学术
- 📊 **数据分析** - 自动提取关键信息和趋势
- 📝 **报告生成** - 结构化研究报告输出
- 🌐 **双语支持** - 中英文混合搜索和分析

## 快速开始

### 基础研究
```bash
node {baseDir}/scripts/research.mjs "研究主题"
```

### 深度研究
```bash
node {baseDir}/scripts/research.mjs "研究主题" --deep --output report.md
```

### 学术文献搜索
```bash
node {baseDir}/scripts/research.mjs "研究主题" --scholar
```

## 使用场景

### 场景1：市场研究
```bash
node scripts/research.mjs "AI Agent 市场趋势 2025" --deep
```

### 场景2：学术研究
```bash
node scripts/research.mjs "机器学习在医疗诊断中的应用" --scholar --abstract
```

### 场景3：竞品分析
```bash
node scripts/research.mjs "OpenAI vs Claude vs Gemini 对比分析" --compare
```

### 场景4：技术调研
```bash
node scripts/research.mjs "Rust vs Go 性能对比" --tech
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--deep` | 深度搜索模式 | false |
| `--scholar` | 学术文献搜索 | false |
| `--abstract` | 包含论文摘要 | false |
| `--compare` | 对比分析模式 | false |
| `--tech` | 技术调研模式 | false |
| `--output <file>` | 输出文件 | 控制台 |
| `--max-results <n>` | 最大结果数 | 10 |

## 输出格式

### 标准报告
```markdown
# 研究报告: [主题]

## 执行摘要
...

## 关键发现
...

## 数据来源
...

## 结论与建议
...
```

## 依赖配置

需要设置 Tavily API Key（仅通过环境变量）：
```bash
export TAVILY_API_KEY="tvly-xxx"
```

**安全说明**:
- API Key 仅通过环境变量读取
- 不会读取任何本地配置文件
- 不会访问用户敏感目录

## 许可

MIT License
