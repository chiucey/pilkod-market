---
name: essential
description: |
  OpenClaw 新手必备 Skills 清单。包含四大类基础技能：
  (1) 安全基础 - skill-vetter, exec-guard (安全扫描与运行时防护)
  (2) 核心能力 - 信息获取(浏览器/搜索)、记忆与进化、技能管理
  (3) 办公/开发增强 - 文档处理、代码管理
  (4) 场景扩展 - 天气、知识库、提醒等
  
  当用户询问如何配置 OpenClaw、新手入门、安装 Skills 时触发此 Skill。
---

# OpenClaw 新手必备 Skills

## 概述

本 Skill 整理了 OpenClaw 新手必备的 Skills，按优先级分为四层，优先安装前两类可覆盖 90% 日常需求。

---

## 一、安全基础（必装）

### 1. skill-vetter
- **功能**：安装前自动扫描技能代码，检查权限与风险
- **安装**：`npx clawhub install skill-vetter`
- **状态**：需外部 CLI

### 2. exec-guard  
- **功能**：运行时防护，禁止 rm/sudo/su 等高危命令
- **安装**：`npx clawhub install exec-guard`
- **状态**：需外部 CLI

---

## 二、核心能力（必装）

### 1. 信息获取

#### Tavily Search (已安装 ✓)
- **功能**：AI 专用高精度实时搜索
- **安装**：`npx clawhub install tavily-search`
- **状态**：✅ 已就绪

#### Agent Browser
- **功能**：浏览器自动化，可打开网页、提取内容
- **安装**：`npx clawhub install agent-browser`
- **状态**：需外部 CLI

### 2. 记忆与进化

#### memory_search / memory_get
- **功能**：检索历史对话与上下文
- **状态**：✅ 内置功能

### 3. 技能管理

#### find-skills
- **功能**：自动去 ClawHub 搜索并安装所需技能
- **安装**：`npx clawhub install find-skills`
- **状态**：需外部 CLI

---

## 三、办公/开发增强

### 1. 办公自动化

#### summarize
- **功能**：一键总结长文本、网页、文档
- **安装**：`npx clawhub install summarize`
- **状态**：✅ 内置 Skill

#### gog (Google Workspace)
- **功能**：打通 Gmail/日历/Drive/Docs
- **安装**：`npx clawhub install gog`
- **状态**：需外部 CLI

### 2. 开发/技术场景

#### github
- **功能**：代码仓库管理，提交、PR、Issues
- **安装**：`npx clawhub install github`
- **状态**：需外部 CLI

---

## 四、场景扩展

### weather (已就绪 ✓)
- **功能**：天气查询
- **状态**：✅ 已就绪

### 其他可选
- notion：联动 Notion
- obsidian：联动 Obsidian  
- trello：任务管理

---

## 快速安装命令

```bash
# 1. 安全（需外部 CLI）
npx clawhub install skill-vetter exec-guard

# 2. 信息获取
npx clawhub install tavily-search agent-browser

# 3. 记忆+管理
npx clawhub install self-improving-agent find-skills

# 4. 办公
npx clawhub install summarize gog

# 5. 开发
npx clawhub install github
```

---

## 已就绪 Skills（内置）

以下 Skills 已内置，直接可用：
- ✅ weather - 天气查询
- ✅ coding-agent - 编程任务委托
- ✅ healthcheck - 安全检查
- ✅ skill-creator - Skill 创建
- ✅ feishu-* - 飞书文档/云盘/权限/知识库

---

## 安全配置建议

```bash
# 开启白名单
openclaw config set skills.allowBundled true
openclaw config set skills.allowList ["tavily-search","multi-search-engine","agent-browser","self-improving-agent","find-skills","summarize","proactive-agent","read","write","edit","github"]
openclaw gateway restart
```
