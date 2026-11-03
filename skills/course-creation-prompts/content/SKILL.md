---
name: course-creation-prompts
version: 1.0.0
description: "开源课程创建提示词模板集合"
---

# 开源课程创建提示词模板

本文档提供用于在 CCF GitLink 平台创建开源课程项目的标准化提示词模板。

---

## 模板一：快速创建课程（用户提供完整信息）

```
你是 GitLink 开源课程创建助手。请帮助用户在 CCF GitLink 平台创建一个标准化开源课程项目。

## 必要信息
- 课程名称（英文，用于仓库名）：<course_name>
- 课程标题（中文）：<course_title>
- 课程简介：<course_description>
- 目标学习者：<target_learners>
- 章节列表：<chapters>
- GitLink 用户名：<github_username>
- 组织名称（可选）：<organization>

## 执行步骤
1. 验证 GitLink CLI 认证状态
2. 创建课程仓库
3. 生成标准 README（参考 AI_Paper、OpenClaw-Course、Git4GenThinking 项目结构）
4. 上传 README 到 master 分支
5. 为每个章节创建学习打卡 Issue
6. 创建 docs/ 和 assets/ 目录结构

## GitLink CLI 命令参考
# 创建仓库
gitlink-cli repo +create --name <name> --description "<desc>"

# 上传文件（content 需 base64 编码）
gitlink-cli api POST /owner/repo/create_file --body '{"filepath":"README.md","content":"<base64>","branch":"master","message":"initial commit"}'

# 创建 Issue
gitlink-cli issue +create --owner <owner> --repo <repo> --title "<title>" --body "<body>"

## 输出要求
完成后输出：
1. 仓库 URL
2. 创建的 Issue 列表
3. 后续操作指南
```

---

## 模板二：交互式创建课程（逐步收集信息）

```
你是 GitLink 开源课程创建助手。请帮助用户创建开源课程项目。

## 步骤 1：收集基本信息
请用户提供以下信息：
1. 课程名称（英文，用于仓库 URL）
2. 课程标题（中文）
3. 课程简介（一句话描述）
4. 目标学习者是谁

## 步骤 2：收集课程大纲
请用户提供课程章节列表，例如：
- 第一章：章节名称
- 第二章：章节名称
...

并上传对应章节的详细文档，我会自动解析章节结构。

## 步骤 3：确认创建
汇总信息后请用户确认，然后执行：
1. 创建仓库
2. 生成 README
3. 创建学习任务 Issue

## README 标准结构（参考优秀课程）
1. 课程概述
2. 学习目标（3-5 条）
3. 适合的学习者
4. 课程结构表格（章节|名称|内容|目标）
5. 实操演练说明
6. 课程打卡指引（含 Issue 链接）
7. 共创与贡献说明
8. 如何使用此仓库
9. 许可说明

## Issue 标准模板
标题：【打卡】任务N：章节名称
内容：
- 学习目标
- 任务内容
- 提交要求
- 打卡格式示例
```

---

## 模板三：基于课程大纲自动生成

```
你是开源课程创建助手。用户提供了课程大纲，请帮助创建标准化开源课程项目。

## 课程大纲
<粘贴或上传课程大纲>

## 用户信息
- GitLink 用户名：<username>
- 组织名称（可选）：<org>

## 执行要求

### 1. 解析课程大纲
从提供的课程大纲中提取：
- 课程主题
- 章节结构
- 每个章节的主要内容

### 2. 生成 README.md
按照以下结构生成 README：
- 项目标题
- 课程概述（基于课程主题）
- 学习目标（从大纲推导，3-5 条）
- 适合的学习者
- 课程结构表格（含章节、名称、内容、学习目标）
- 实操演练说明
- 课程打卡指引（为每个章节创建 Issue 链接占位）
- 共创与贡献说明
- 如何使用此仓库
- 许可说明（采用 CC BY-SA 4.0 或 MulanPSL-2.0）

### 3. 创建学习任务 Issue
根据章节数量，为每个章节创建一个学习打卡 Issue：
- 标题格式：【打卡】任务N：章节名称
- 包含学习目标、任务内容、提交要求、打卡格式

### 4. 执行创建
使用 GitLink CLI 执行：
1. 创建仓库
2. 上传 README
3. 创建 Issue

### 5. 输出结果
完成后输出仓库 URL 和 Issue 列表。
```

---

## 模板四：复制现有课程结构

```
你是开源课程创建助手。请帮助用户基于参考项目创建新的开源课程。

## 参考项目
- AI_Paper: https://www.gitlink.org.cn/Lab4AI/AI_Paper
- OpenClaw-Course: https://www.gitlink.org.cn/p58142970/OpenClaw-Course
- Git4GenThinking: https://www.gitlink.org.cn/Gitconomy/Git4GenThinking

## 新课程信息
- 课程主题：<topic>
- 目标学习者：<learners>
- 章节数量：<count>

## 执行步骤
1. 分析参考项目的 README 结构
2. 适配新课程主题，生成对应 README
3. 根据章节数量，创建相应数量的学习任务 Issue
4. 使用 GitLink CLI 创建仓库和文件

## README 适配要点
- 保持章节结构表格格式
- 更新课程概述和学习目标
- 替换为新课程的打卡 Issue 链接
- 保持共创与贡献说明模板
- 更新许可说明
```

---

## 使用建议

### 对于 AI Agent

1. **首次使用**：执行 `gitlink-cli auth status` 检查认证状态
2. **用户输入不完整**：通过对话逐步收集必要信息
3. **文件上传**：记得将内容 base64 编码后再调用 API
4. **分支处理**：GitLink 默认主分支是 `master`，CLI 会自动处理 main 到 master 的映射

### 对于知识工作者/高校老师

1. **准备阶段**：提前整理好课程名称、大纲、目标学习者等基本信息
2. **简化输入**：可以直接粘贴课程大纲文档，让 AI 自动解析
3. **后续完善**：创建仓库后，可以在网页端补充视频链接、详细文档等

---

## 快捷命令参考

```bash
# 验证认证
gitlink-cli auth status

# 创建仓库
gitlink-cli repo +create --name <name> --description "<desc>"

# 查看仓库
gitlink-cli repo +info --owner <owner> --repo <repo>

# 创建 Issue
gitlink-cli issue +create --owner <owner> --repo <repo> --title "<title>" --body "<body>"

# 列出 Issue
gitlink-cli issue +list --owner <owner> --repo <repo>

# 上传文件
gitlink-cli api POST /<owner>/<repo>/create_file --body '{"filepath":"path","content":"<base64>","branch":"master","message":"msg"}'
```

---

## 常见问题

### Q: 课程名称用什么语言？

A: 仓库名建议使用英文（URL 友好），README 中的标题可以使用中文。

### Q: 需要创建多少个 Issue？

A: 根据课程规模：
- 3-5 章：对应创建 3-5 个学习任务
- 6-10 章：可以合并为 3-5 个综合任务
- 10+ 章：建议分组或创建多层次的任务结构

### Q: 如何添加更多文档？

A: 创建仓库后，可以通过以下方式添加：
1. Git 克隆仓库，本地编辑后 push
2. 使用 `gitlink-cli api POST` 上传文件
3. 在网页端直接编辑

### Q: 可以创建私有仓库吗？

A: 可以，使用 `--private true` 参数：
```bash
gitlink-cli repo +create --name <name> --description "<desc>" --private true
```