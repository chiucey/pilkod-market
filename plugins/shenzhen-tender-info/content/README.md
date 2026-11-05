# 深交易投标信息查询（shenzhen-tender-info）

面向深圳投标人员的本地 MiniMax 插件：输入工程名称，查出该项目在**深圳公共资源交易网**上的全流程进度，并下载已公开的开标报告、评标报告与中标结果资料。

## 组成

| 能力 | 内容 |
| --- | --- |
| MCP 服务器 | `tender-server`（stdio, Node, 零依赖）：`project_progress` / `get_notice` / `download_docs` / `list_notices` / `list_channels` |
| Skill | `tender-search`：查询流程、阶段与文件对照表、下载能力边界、输出格式 |
| 子智能体 | `tender-analyst`：项目跟踪、评标资料抓取与复盘分析（委派名 `shenzhen-tender-info:tender-analyst`） |
| Hook | `UserPromptSubmit`：提示里出现投标相关词时，注入工具用法与判定口径 |

## 安装位置

D:\.minimaxcode\.minimax\plugins\shenzhen-tender-info\

由 MiniMax Code Desktop 自动扫描识别。子智能体能力需要支持 Plugin subagent 的客户端版本。

## 用法

```
查一下院容院貌提升改造工程现在到哪一步了
把罗沙路改扩建工程的评标报告和开标记录下载到 E:\投标资料\罗沙路
罗沙路改扩建工程中标了吗，中标单位和报价是多少
```

## 工具

### project_progress

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| title | string | 必填 | 工程名称关键词 |
| scope | string | jsgc | jsgc=建设工程，zfcg=政府采购，all=两者 |
| size | integer | 30 | 每渠道最多条数，最大 100 |

返回按项目编号聚合的进度：当前阶段、是否已截标（`bidClosed`）、是否已进入评标（`enteredEvaluation`）、全流程时间线，以及可下载报告入口 `availableDocs`（含 `noticeId`、`releaseTime`，用于后续定位政府采购静态页）。

阶段顺序：意向阶段 → 投标中 → 已截标 → 已开标 → 评标中 → 评标完成 → 已定标 → 已中标。

### get_notice

入参 `contentId`（政府采购可另传 `noticeId` / `releaseTime` / `noticeTypeCode`）。返回标题、发布时间、项目编号、区域、正文纯文本，以及全部附件直链（按 `docClass` 分类）。

### download_docs

| 参数 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| contentId | string | 是 | 公告 id |
| destDir | string | 是 | 本地保存目录（绝对路径） |
| docClass | array | 否 | kbreport 开标报告 / pingbiao 评标报告 / zhongbiao 中标信息 / zixing 资信资格文件；留空为全部 |
| noticeId / releaseTime | string | 否 | 政府采购公告定位静态页用，来自 `project_progress` |
| maxMB | integer | 否 | 单文件上限 MB，默认 300 |

### list_notices / list_channels

按渠道浏览公告；列出渠道、阶段表与附件分类。

## 评标报告的命名

评标报告公示里的评标报告按评审分组命名，实测三种都存在：

- `技术组评标报告.pdf` —— 技术标评审组
- `商务组评标报告.pdf` —— 商务标评审组
- `综合组评标报告.pdf` —— 单一评审组（全过程造价咨询、货物服务类常见）

可能还有 `商务组否决投标汇总表.pdf`。所以**不要预设文件名**，用 `get_notice` 看实际附件清单再下载。

## 下载能力边界

| | 建设工程 | 政府采购 |
| --- | --- | --- |
| 附件来源 | 主站详情页正文 | `zfcg.szggzy.com:8081` 静态页 |
| 自动下载 | 可以，直链免登录 | 不行，受图形验证码保护 |

政府采购附件需在浏览器里通过验证码弹窗下载。工具会返回 `manualRequired` 与 `staticUrl`，照实转告用户即可。

## 数据与口径

- 数据源：`https://www.szggzy.com`（深圳公共资源交易网），经实测的公告列表与详情接口。
- **只覆盖深圳本地平台**，不含其他省市与全国性交易平台。
- 结论字段以公告详情与附件为准，列表页只提供线索。
- 平台实际公开哪些文件以 `get_notice` 的附件清单为准；未公开的写「平台未公开」，不做推测。
- 各投标人的资信标文件会逐个列出，实测单公告可达 15~20 份、部分单份超 90 MB，批量下载前先说明体积。
- 每次返回带 `fetchedAt`，报告须写明查询时点。

## 生成投稿包

官方投稿（https://agent.minimax.cn/docs/code/agents/plugin-submission）的表单不受理 Hook，生产发布只接受默认图标，受理范围为 App/MCP/Skill。本地包保留 Hook、深色图标与子智能体以便日常使用，用脚本一键产出合规投稿包：

```
node tools/build-submission.mjs --out E:\投稿包\shenzhen-tender-info-1.0.0.zip
```

脚本会剥离 `hooks/`、`agents/`、`icon-dark.png` 与 manifest 里的 `hooks`/`agents`/`darkIcon` 字段，保留 MCP 与两个 Skill，然后自检包结构并输出 SHA-256。

每次更新后再跑一次即可，产出始终符合投稿规范。
## 目录结构

```
shenzhen-tender-info/
  .minimax-plugin/plugin.json
  icon.png / icon-dark.png
  servers.mcp.json
  server.mjs
  skills/tender-search/SKILL.md
  agents/tender-analyst.md
  hooks/hooks.json
  scripts/hook-prompt.mjs
  README.md
```
