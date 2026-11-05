---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 420b401ada38613bfe87393254544d50
    PropagateID: 420b401ada38613bfe87393254544d50
    ReservedCode1: 3046022100a1afbec81707fdf0c2f4afa29bed8e435e7fddc83d94fbe6908b70d60d1fb90d0221009ea300ce3324f84679408e7a29973f5355e8634855652835dfd0493bb2736d32
    ReservedCode2: 304602210081a5cd937ec254af41954bf7cd2236a7f0cb4a5ba31d5bf1b6b4fdef099a33f3022100dbe1709809db5a6c8b75eadc89746984f50e123c30157a357d41fb57c444910d
description: GitLink 开源课程创建助手：当知识工作者/高校老师需要创建开源课程项目时触发。自动化完成仓库创建、README生成、Issue学习任务创建等全流程。
metadata:
    cliHelp: gitlink-cli --help
    requires:
        bins:
            - gitlink-cli
name: gitlink-course-creator
version: 1.0.0
---

# GitLink 开源课程创建助手

**CRITICAL — 开始前必须先阅读 [`../gitlink-shared/SKILL.md`](../gitlink-shared/SKILL.md)，其中包含认证、权限处理和 API 注意事项。**

> **功能说明**：本 Skill 帮助用户快速在 CCF GitLink 平台创建标准化开源课程项目，包含仓库初始化、README生成、学习任务Issue创建等完整工作流。

---

## 触发条件

当用户表达以下意图时触发本 Skill：

- "创建一个开源课程项目"
- "在GitLink创建课程仓库"
- "我想建一个教学课程"
- "帮我初始化一个课程项目"
- "创建开源课程"
- "建立课程仓库"
- "创建一个课程到某组织下"

---

## 完整工作流程

### Step 0: 前置检查

执行任何操作前，先检查认证状态：

```bash
gitlink-cli auth status
```

如果未登录，引导用户执行：
```bash
gitlink-cli auth login
```

---

### Step 1: 信息收集

通过对话收集以下必要信息：

| 必填字段 | 说明 | 示例 |
|----------|------|------|
| `course_name` | 课程名称（英文，用于仓库名） | "AI-Paper-Writing" |
| `course_title` | 课程标题（中文，用于README） | "AI论文写作实战" |
| `course_description` | 课程简介 | "面向科研工作者的AI辅助论文写作教程" |
| `target_learners` | 目标学习者 | "本科生、研究生、高校教师" |
| `chapters` | 章节列表（数组） | ["文献检索", "论文写作", "投稿指南"] |
| `organization` | **组织名称（必填）** | "Lab4AI" |

| 可选字段 | 说明 |
|----------|------|
| `license` | 开源许可证偏好 |
| `learning_goals` | 学习目标（多个，用-分隔） |
| `tools_needed` | 所需工具列表 |

**许可证选项（供用户选择）**：

| 许可证 | 说明 | 适用场景 |
|--------|------|----------|
| MIT License | 宽松，允许商业使用 | 商业友好型课程 |
| Apache 2.0 | 允许专利授权 | 需要专利保护 |
| GPL 3.0 | 要求衍生作品也开源 | 强制开源传播 |
| CC BY-SA 4.0 | 知识共享，相同方式共享 | 知识类课程 |
| MulanPSL-2.0 | 中文开源许可证 | 中文开源项目 |
| 不选择 | 留空，稍后手动添加 | 用户自行决定 |

**信息收集示例对话**：

```
用户: 帮我创建一个开源课程
助手: 好的！我来帮您在 GitLink 创建开源课程项目。请提供以下信息：

1. 组织名称（课程归属的组织）：<组织名>
2. 课程名称（英文，用于仓库名）：<课程英文名>
3. 课程标题（中文）：<课程中文名>
4. 课程简介：<一句话描述>
5. 目标学习者：<谁适合学习>
6. 课程章节：<章节列表，逗号分隔>
7. 开源许可证：（可选）MIT/Apache/GPL/CC BY-SA/MulanPSL/不选择

或者，您也可以直接粘贴课程大纲，我会自动解析。
```

---

### Step 2: 创建仓库

```bash
# 确定组织名称（必填）
OWNER="${organization}"

# 创建仓库（在组织下）
gitlink-cli repo +create \
  --owner "${OWNER}" \
  --name "${course_name}" \
  --description "${course_description}"
```

---

### Step 3: 生成标准 README

基于以下模板生成 README 内容：

```markdown
# {{course_title}}

## 1. 课程概述

{{course_description}}

## 2. 学习目标

{{#each learning_goals}}
* {{this}}
{{/each}}

## 3. 适合的学习者

{{target_learners}}

## 4. 课程结构

| 章节 | 章节名称 | 主要内容 | 学习目标 |
|------|----------|----------|----------|
{{#each chapters}}
| 第{{add @index 1}}章 | {{this.name}} | {{this.content}} | {{this.goal}} |
{{/each}}

## 5. 实操演练

本课程秉持"做中学 (Learning by Doing)"原则，实验演练贯穿全章节。所有实操均围绕真实学习场景设计。

**核心要求**：学习者需跟随章节进度，逐步构建自己的学习成果。

**工具生态**：课程将统一推荐并演示适配学习场景的主流工具组合。

## 6. 课程打卡指引

为了记录你的学习成长，本课程采用 **'Issue' 评论打卡**的方式。

学员们在完成每节课程的学习后，请在对应 Issue 下方点击"添加评论"，提交你的学习心得与实操产出：

{{#each chapters}}
* 【打卡】任务{{add @index 1}}——{{this.name}}
{{/each}}

## 7. 共创与贡献

本课程仓库为开放共创模式，欢迎所有学习者参与贡献。

**贡献方向**：
* 补充您所在领域的专属提示词或学习心得
* 贡献优秀的学习案例（请确保已脱敏）
* 分享好用的学习工具
* 修复各章节文档中的错漏之处

**贡献方式**：通过仓库提交 Issue 的方式进行分享。

## 8. 如何使用此仓库

1. **渐进式学习**：按照章节顺序推进，结合视频演示
2. **完成闭环**：每章学习后，完成并提交实操产出
3. **资源获取**：仓库 `docs/` 目录下包含各章节的详细文稿
4. **问题反馈**：在仓库 Issues 中带图提交

## 9. 许可说明

{{#if license}}
本课程采用 **{{license}}** 开源许可证。

* **许可证内容**：详细内容请参阅项目根目录的 `LICENSE` 文件
* **非商业用途**：任何人可免费查看、学习、分享本仓库内容
* **署名要求**：引用、分享本仓库内容时，需注明原作者及仓库来源
{{#if_eq license "CC BY-SA 4.0"}}
* **相同方式共享**：修改、衍生本仓库内容后，需以相同许可证授权发布
{{/if_eq}}
{{#if_eq license "GPL 3.0"}}
* **相同方式共享**：修改、衍生本仓库内容后，需以相同许可证授权发布
{{/if_eq}}
{{else}}
本课程暂无指定许可证。课程创建者可后续添加 LICENSE 文件。

**推荐许可证选项**：
- MIT License（宽松）
- Apache 2.0（允许专利授权）
- CC BY-SA 4.0（知识共享）
- MulanPSL-2.0（中文开源）
{{/if}}

---

*课程仓库：https://www.gitlink.org.cn/{{OWNER}}/{{course_name}}*
```

---

### Step 4: 上传 README

```bash
# 生成 base64 编码的 README 内容
README_CONTENT="<上面生成的 README 内容>"
ENCODED_CONTENT=$(echo -n "$README_CONTENT" | base64)

# 上传 README.md
gitlink-cli api POST /${OWNER}/${course_name}/create_file --body "{
  \"filepath\": \"README.md\",
  \"content\": \"$ENCODED_CONTENT\",
  \"branch\": \"master\",
  \"message\": \"initial: add README with course overview\"
}"
```

---

### Step 5: 创建学习任务 Issue

对于每个章节，创建一个打卡 Issue：

```bash
# 遍历章节创建 Issue
for i in "${!chapters[@]}"; do
  chapter="${chapters[$i]}"
  chapter_num=$((i+1))

  gitlink-cli issue +create \
    --owner "${OWNER}" \
    --repo "${course_name}" \
    --title "【打卡】任务${chapter_num}：${chapter}" \
    --body "## 学习目标

掌握本章内容，完成对应的实操练习。

## 任务内容

1. 学习第 ${chapter_num} 章内容
2. 完成章节对应的实操练习
3. 整理学习笔记

## 提交要求

完成学习后，在本 Issue 下方的评论区提交：

```
- 学习时长：XX 分钟
- 掌握程度：★★★☆☆
- 学习心得：...
- 实操截图：（可选）
```

## 相关资源

- 章节文档：docs/chapter${chapter_num}.md
- 上一章：${prev_chapter}
- 下一章：${next_chapter}
"
done
```

---

### Step 6: 创建目录结构

```bash
# 创建 docs 目录
DOCS_CONTENT="# 课程文档目录\n\n本目录存放课程各章节的详细文档。"
ENCODED_DOCS=$(echo -n "$DOCS_CONTENT" | base64)
gitlink-cli api POST /${OWNER}/${course_name}/create_file --body "{
  \"filepath\": \"docs/README.md\",
  \"content\": \"$ENCODED_DOCS\",
  \"branch\": \"master\",
  \"message\": \"initial: add docs directory\"
}"

# 创建 assets 目录
ASSETS_CONTENT="# 课程资源目录\n\n本目录存放课程相关的图片、视频等资源文件。"
ENCODED_ASSETS=$(echo -n "$ASSETS_CONTENT" | base64)
gitlink-cli api POST /${OWNER}/${course_name}/create_file --body "{
  \"filepath\": \"assets/README.md\",
  \"content\": \"$ENCODED_ASSETS\",
  \"branch\": \"master\",
  \"message\": \"initial: add assets directory\"
}"
```

---

## 完整执行示例

```bash
#!/bin/bash
# GitLink 开源课程创建脚本示例

# 配置
COURSE_NAME="ai-paper-writing"
COURSE_TITLE="AI论文写作实战"
COURSE_DESC="面向科研工作者的AI辅助论文写作教程"
TARGET_LEARNERS="本科生、研究生、高校教师"
OWNER="zhangsan"

# 章节
CHAPTERS=("文献检索与选题挖掘" "文献管理与沉浸阅读" "高效写作与草稿生成" "语言润色与降重")

# 1. 创建仓库
gitlink-cli repo +create \
  --name "$COURSE_NAME" \
  --description "$COURSE_DESC"

# 2. 上传 README（省略具体内容）
echo "生成并上传 README..."

# 3. 创建学习任务 Issue
for i in "${!CHAPTERS[@]}"; do
  gitlink-cli issue +create \
    --owner "$OWNER" \
    --repo "$COURSE_NAME" \
    --title "【打卡】任务$((i+1))：${CHAPTERS[$i]}" \
    --body "## 学习任务 $((i+1))

完成第 $((i+1)) 章的学习...

## 打卡格式
- 学习时长：
- 掌握程度：
- 学习心得：
"
done

# 4. 创建目录结构
echo "创建目录结构..."

echo "✅ 课程项目创建完成！"
```

---

## 输出格式

完成创建后，输出以下信息：

```markdown
## ✅ 开源课程项目创建完成！

**仓库地址**: https://www.gitlink.org.cn/{OWNER}/{course_name}

**创建内容**:
- ✅ 仓库创建完成
- ✅ README.md 已上传
- ✅ {n} 个学习任务 Issue 已创建
- ✅ docs/ 目录已初始化
- ✅ assets/ 目录已初始化

**下一步操作**:
1. 访问仓库，上传课程文档到 `docs/` 目录
2. 在各 Issue 下添加详细的打卡要求
3. 可以通过 Git 克隆仓库进行本地开发：
   ```bash
   git clone https://www.gitlink.org.cn/{OWNER}/{course_name}.git
   ```

**参考优秀课程**:
- [AI_Paper](https://www.gitlink.org.cn/Lab4AI/AI_Paper)
- [OpenClaw-Course](https://www.gitlink.org.cn/p58142970/OpenClaw-Course)
- [Git4GenThinking](https://www.gitlink.org.cn/Gitconomy/Git4GenThinking)
```

---

## 注意事项

1. **仓库名为英文**：GitLink 仓库名建议使用英文，便于 URL 显示
2. **章节 Issue 数量**：建议创建 3-10 个学习任务 Issue，避免过多导致负担
3. **README 完整性**：上传后建议在网页端补充更多细节，如视频链接、配套资源等
4. **分支约定**：GitLink 默认主分支为 `master`，CLI 会自动处理 `main` 与 `master` 的映射

---

## 错误处理

| 错误 | 处理方式 |
|------|----------|
| 401 未认证 | 引导用户执行 `gitlink-cli auth login` |
| 403 权限不足 | 确认 owner/repo 是否正确，或用户是否有写入权限 |
| 仓库已存在 | 询问用户是否使用已有仓库，或使用新名称 |
| API 请求失败 | 检查网络连接，或尝试重新执行 |

---

## 相关 Skills

- [gitlink-repo](../gitlink-repo/SKILL.md) - 仓库操作
- [gitlink-issue](../gitlink-issue/SKILL.md) - Issue 管理
- [gitlink-shared](../gitlink-shared/SKILL.md) - 认证与共享规则