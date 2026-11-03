---
name: weekly-report
description: 管理工作周报，支持每日工作内容登记累积和周报汇总生成。当用户提到周报、工作汇报、每日登记、工作总结、周报汇总、企微推送时必须使用此技能。可通过企微机器人推送周报，支持任务延续性追踪。
dependency:
  npm:
    - axios@^1.6.0
    - dayjs@^1.11.10
---

# 周报管理

## 任务目标
- 本 Skill 用于：个人/团队工作周报管理
- 能力：
  - 每日工作内容登记与累积
  - 按周汇总生成格式化周报
  - 参考历史周报保持任务延续性
  - 通过企微机器人推送周报
- 触发：当用户提到"写周报"、"登记工作内容"、"汇总周报"、"推送企微"时使用

## 前置准备
- 依赖说明：axios 用于 HTTP 请求，dayjs 用于日期处理
- 配置文件：`.weekly-report-config.json` 存储在技能目录下
  - 首次使用时，如配置不存在会提示用户输入 Webhook URL
  - 后续使用直接读取，如需修改可直接编辑该文件或使用 `init-config.js update` 命令

## 操作步骤

### 1. 每日工作内容登记
1. 收集用户输入的日期、工作内容、完成状态、备注
2. 调用 `scripts/daily-log.js add <date> <content> <status> [remark]` 将数据追加存储到本地 JSON 文件
   - 状态支持英文简写：completed/done→已完成, inprogress→进行中, pending→待开始
3. 按日期自动归档，支持多日期累积

### 2. 周报汇总生成
1. 确定目标周（默认本周，可指定日期范围）
2. 调用 `scripts/weekly-summary.js` 读取该周所有日记录
3. 参考上个月的周报内容（调用 `scripts/history-reference.js`）
4. 按标准格式生成周报，包含：
   - 本周完成工作
   - 进行中任务
   - 下周计划
   - 问题与风险
5. 输出格式化周报文本

### 3. 企微机器人推送
1. 检查 `.weekly-report-config.json` 配置是否存在
2. 调用 `scripts/weekly-summary.js push [weekStart]` 生成并推送周报（推荐）
   - 或使用 `echo "内容" | node scripts/sync-wecom.js sync` 从 stdin 读取内容推送
3. 返回推送结果

**注意：** 避免通过命令行参数直接传递 Markdown 内容，推荐使用 stdin 管道或 push 命令

## 资源索引

### 脚本工具
- **[scripts/daily-log.js](scripts/daily-log.js)**
  - 用途：每日工作内容登记与存储
  - 触发时机：当用户需要记录当天或指定日期的工作内容时，**必须调用此脚本**
  - 输入：`add <date> <content> <status> [remark]`
  - 状态支持：completed/done→已完成, inprogress→进行中, pending→待开始
  - 输出：存储成功确认

- **[scripts/weekly-summary.js](scripts/weekly-summary.js)**
  - 用途：按周汇总生成格式化周报，支持推送和 HTML 生成
  - 触发时机：当用户需要生成周报时，**必须调用此脚本**
  - 命令：
    - `generate [weekStart]` - 仅生成 Markdown 周报
    - `push [weekStart] [--no-push] [--html] [--html-path <path>]` - 生成并推送企微
    - `html [weekStart] [outputPath]` - 生成 HTML 报告文件
  - 输出：格式化周报文本 / 推送结果 / HTML 文件

- **[scripts/markdown-to-html.js](scripts/markdown-to-html.js)**
  - 用途：将周报数据转换为 HTML 格式（使用 assets/templates/weekly-report.html 模板）
  - 触发时机：当用户需要生成可视化 HTML 周报时
  - 输入：从 stdin 读取 JSON 数据，或通过 weekly-summary.js html 命令调用
  - 输出：HTML 文件

- **[scripts/history-reference.js](scripts/history-reference.js)**
  - 用途：读取历史周报作为参考
  - 触发时机：生成周报前，**必须先调用此脚本**获取上月周报内容
  - 输入：查询月份
  - 输出：历史周报数据

- **[scripts/sync-wecom.js](scripts/sync-wecom.js)**
  - 用途：通过企微机器人 Webhook 推送周报
  - 触发时机：当用户要求推送至企微时，**必须调用此脚本**
  - 输入：周报内容（支持 stdin 管道输入）
  - 输出：推送结果

- **[scripts/init-config.js](scripts/init-config.js)**
  - 用途：初始化配置文件
  - 触发时机：首次使用时，**必须先调用此脚本**创建配置
  - 输出：配置文件创建确认

### 参考文档
- **[references/weekly-template.md](references/weekly-template.md)**
  - 内容：标准周报格式模板和示例
  - 使用时机：在生成周报前，**必须先读取此文档**了解格式规范
  - 关键作用：确保周报格式统一规范

- **[references/data-format.md](references/data-format.md)**
  - 内容：数据存储格式和字段定义
  - 使用时机：开发或调试时参考
  - 关键作用：理解数据结构

### 静态资源
- **[assets/templates/](assets/templates/)**
  - 内容：周报 HTML/Markdown 模板文件
  - 使用方式：生成可视化周报时，**直接使用此资源**

## 注意事项
- **附件读取规则**：生成周报前，**必须优先读取** [references/weekly-template.md](references/weekly-template.md) 了解完整的格式规范
- **脚本调用规则**：涉及数据存储、历史查询、企微同步等操作时，**立即调用** scripts/ 中的对应脚本，而不是尝试自行处理
- **资源使用规则**：需要模板时，**直接使用** assets/templates/ 中的文件
- 数据存储在 `./.weekly-report-data/` 目录下，按年月分文件存储
- 首次使用需运行 `node scripts/init-config.js` 初始化配置
- 企微推送需要配置企业微信机器人 Webhook URL