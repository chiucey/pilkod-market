---
name: ai-self-evolver
description: AI self-evolution skill. Automatically crawls AI tools, source code and news, intelligently filters valuable content based on user habits, and automatically installs GitHub projects, AI tools and source code. Trigger scenarios: AI self-evolution, automatic tool installation, crawling AI source code, discovering new AI tools, automatic GitHub project installation, AI tool auto-discovery.
---

# AI自进化技能

## 功能概述

本技能让AI具备自我进化能力，通过以下方式持续提升：

1. **自动爬取** - 从多个来源监控AI相关资讯和源码
2. **智能筛选** - 根据用户使用习惯判断内容价值
3. **自动安装** - 一键安装有价值的工具和项目
4. **自动触发** - 检测到相关内容立即处理

## 数据来源

### 主要监控源

| 来源 | 类型 | 监控内容 |
|------|------|----------|
| GitHub Trending | AI/ML项目 | 新兴开源AI项目 |
| Hacker News | 科技资讯 | AI相关讨论和发布 |
| arXiv | 学术论文 | 最新AI研究论文 |
| 技术博客 | 深度文章 | 工具使用教程 |
| AI导航站 | 工具聚合 | 新上线的AI工具 |

### 关键词过滤

优先关注以下类型内容：
- Agent/智能体相关
- 开源LLM/模型相关
- 开发框架和工具
- 自动化脚本和技能
- 泄露源码/数据集

## 筛选算法

### 价值评估维度

```
价值分数 = 相关性(40%) + 实用性(30%) + 新颖度(20%) + 质量(10%)
```

### 筛选条件

1. **必须通过**
   - 与AI/开发领域相关
   - 非恶意/钓鱼内容
   - 至少10 stars或5 stars且高增长

2. **优先通过**
   - 与用户近期使用技能相关
   - 官方仓库优先fork
   - 活跃维护的项目
   - 有详细文档

3. **降级处理**
   - 过于小众的工具（<50 stars且无特色）
   - 已安装过的重复项目
   - 明显过时的项目

## 执行流程

### 1. 定时检查（每日）

```python
# 伪代码
while True:
    sources = ["github", "hn", "arxiv"]
    items = []

    for source in sources:
        items.extend(fetch_new_items(source))

    scored_items = [score(item) for item in items]
    sorted_items = sorted(scored_items, key=lambda x: x.score, reverse=True)

    # 前10%高价值内容自动安装
    auto_install = [item for item in sorted_items if item.score > threshold]

    # 其余通知用户
    notify_user(sorted_items[:20])
```

### 2. 实时监控

- 监听关键词：`agent`, `llm`, `ai tool`, `github leak`
- 检测到高相关性内容立即触发评估

### 3. 安装流程

```
发现项目 → 克隆源码 → 安装依赖 → 验证运行 → 记录到技能库
```

## 偏好学习

### 观察维度

1. **使用频率** - 哪些技能被频繁使用
2. **完成率** - 哪些任务类型成功率高
3. **反馈** - 用户明确的好评/差评
4. **上下文** - 近期任务的领域和工具

### 权重调整

```python
# 根据使用习惯调整筛选权重
if user.uses("code") frequently:
    weights["code_related"] *= 1.2

if user.ignores("image_gen"):
    weights["image_related"] *= 0.5
```

## 安全机制

### 禁止自动安装

- 需要登录的GitHub项目
- 非开源/许可证不明
- 包含二进制文件
- 低于安全评分的项目

### 安装前验证

1. 代码静态分析
2. 依赖安全扫描
3. 沙箱测试运行
4. 用户确认（高权限操作）

## 使用方式

### 主动触发

```
"帮我看看最近有什么新的AI工具"
"检查GitHub上的AI Agent项目"
"搜索最新的开源LLM"
```

### 自动触发

- 定时任务（每日/每周）
- 检测到相关关键词
- 用户询问相关话题时推荐

## 输出格式

### 发现报告

```markdown
## AI工具发现报告 [日期]

### 自动安装 ✅
- [项目名](链接) - 评分98 - 安装原因

### 推荐安装 🔔
- [项目名](链接) - 评分85 - 推荐原因

### 值得关注 📌
- [项目名](链接) - 评分72 - 简要说明
```

## 相关文档

- [数据源配置](references/data-sources.md)
- [评分算法详解](references/scoring-algorithm.md)
- [安装脚本模板](references/install-templates.md)
