# 边际跟踪器字段契约（marginal tracker schema）

本工具的存储形态是 **topic → event chain**：一个文件可以挂多个主题（topic），每个主题挂一条按时间顺序、仅追加的事件链（event chain）。下列字段在 JSON 输入、CSV / XLSX 工作簿、数据库以及结构化输出中通用。**空字段保留可见**，不要凭空填值。

## 顶层结构

```json
{
  "topics": [
    { "topic_id": "...", "topic": "...", "events": [ ... ] },
    { "topic_id": "...", "topic": "...", "events": [ ... ] }
  ]
}
```

容错的等价形态：

- 顶层数组键可以叫 `topics` / `threads` / `chains` / `tracks`
- 单主题时也可直接顶层写 `{topic: "...", events: [...]}`
- 单主题内事件数组可以叫 `events` / `timeline` / `history` / `entries` / `items`

## Topic 元字段

| 字段 | 含义 |
|---|---|
| `topic_id` | 文件名安全的稳定 id；省略时由 `topic` 名 slug 化生成。同文件内重复会自动加 `-2`/`-3` 后缀 |
| `topic` | 主题人类可读名称（"Nvidia AI capex cycle"） |
| `summary` | 一句话主题说明 |
| `status` | 主题当前判定（`intact` / `watch` / `impaired` / `broken` / `changed` / `untested` / `retired` 等，沿用论点状态词表） |
| `created_at` | 主题建立日期 |
| `last_updated` | 最近一次事件追加日期 |
| `tags` | 自由标签，数组或逗号分隔串均可 |
| `event_count` | 脚本自动计算：链上已填充事件数 |
| `head_event_id` | 脚本自动计算：链的最早事件 id |
| `tail_event_id` | 脚本自动计算：链的最近事件 id |

## Event 字段

每条事件是链上一个节点，记录"这一刻边际上发生了什么"。

| 字段 | 含义 |
|---|---|
| `event_id` | 链节点 id，例如 `E001`。在 topic 内唯一。不写则脚本仍会落行，但下一行的自动 `prev_event_id` 链回填会断 |
| `prev_event_id` | 前驱事件 id。**省略时**脚本会按数组顺序自动指向上一行的 `event_id`，方便快速录入；要做"分叉"或"无前驱"明确写 `null` 或留空 |
| `date` | 事件发生日期（建议 `YYYY-MM-DD` 或带时分） |
| `sequence` | 链上序号，省略时按数组顺序自动填 1, 2, 3… |
| `headline` | 一句话标题 |
| `fact` | 事实陈述（带数字、单位、口径） |
| `source` | 来源名称（"MSFT Q2 FY26 call"、"Bloomberg"…） |
| `source_type` | `earnings_call` / `filing` / `news` / `expert_call` / `model` / `mgmt_meeting` / `internal` / … |
| `signal` | 信号方向，沿用论点信号词表：`+2 strongly confirming` / `+1 mildly confirming` / `0 neutral` / `mixed` / `-1 mildly weakening` / `-2 strongly weakening` / `break/invalidating` / `untested` |
| `marginal_change` | **本工具的核心字段**：此事件在边际上把状态从什么改成了什么 |
| `interpretation` | 对该事实的解读，区分基本面 / 估值 / 仓位 |
| `evidence_quality` | `high` / `medium` / `low` |
| `impact` | 对模型 / 估值 / 风险回报 / 仓位 / 确信度的具体影响 |
| `linked_event_ids` | 同链多前驱或跨 topic 链接，逗号分隔的 id 串 |
| `follow_up` | 后续动作或下一个验证点 |

## 信号词表

证据信号可选值（与单标的论点跟踪一致）：`+2 strongly confirming`、`+1 mildly confirming`、`0 neutral`、`mixed`、`-1 mildly weakening`、`-2 strongly weakening`、`break/invalidating`、`untested`。

**证据信号是定性纪律工具，不是加和评分体系**。除非用户提供或继承已定义的方法，不要将其汇总为支柱得分、加权方向或评分图。PM 判断在解释充分时可以覆盖机械化状态。

## Topic 状态

- **Strengthening**：核心边际持续确认，风险回报仍具吸引力。
- **Intact**：核心边际稳定，无重大反驳。
- **Watch**：出现 1 个核心隐患，或多个次要警告。
- **Impaired**：核心边际承压或 KPI 反复不达预期。
- **Broken**：终止条件被触发，或原始前提失败。
- **Changed**：原本的理由不再主导，需要显性批准。
- **Untested**：暂无决定性验证。
- **Retired**：仓位 / 覆盖已关闭。

**状态对齐规则**：当链上最近若干个事件的 `signal` 集中在 `-1` / `-2` / `break` 时，topic `status` 默认应反映为 `Watch` / `Impaired` / `Broken`；上调到更轻判定时，必须能在事件链里指出有证据支撑的覆盖事件。

## 链结构与追加纪律

- **仅追加**：事件链一旦录入，不得删除、合并、覆盖既有事件；纠正用新事件追加并 `linked_event_ids` 指回原条目。
- **链可重建**：通过 `prev_event_id` 与 `linked_event_ids` 可以从扁平 CSV 重建一棵 DAG（默认线性，跨链回引时变成 DAG）。
- **每条边际变化都来自一个事件**：不要在 topic 元字段里直接改 `status` 而不留事件——`status` 的每次跳变都应该有一条对应事件解释原因。

## 证券论点就绪度（沿用）

- **Ready**：当前市场 / 估值 / 组合输入足以支撑所述行动。
- **Conditional**：公司 / 证券解读可用，但有点名的实施输入仍开放。
- **Re-underwrite**：链上证据需要重新审视模型 / 估值 / 行动框架。
- **Not decision-grade**：市场 / 估值 / 组合输入缺失，无法做出证券结论。

## 行动阈值来源（沿用）

- `Inherited threshold`：来自原始承销研究或既有跟踪器。
- `Draft threshold for PM confirmation`：本次更新生成，尚未批准。
- `Approved monitoring rule`：用户或既定组合流程已明示接受。

## 公开股票组合监控扩展字段

按相关性追加到 event 字段或 topic 元字段：

- **Topic 元**：`benchmark_weight`、`active_weight`、`portfolio_role`、`liquidity_score`、`crowding_read`、`index_etf_flow_exposure`、`priced_in_status`、`position_action`、`security_thesis_readiness`。
- **Event**：`priced_in_read`、`benchmark_or_flow_impact`、`position_action`、`portfolio_relevance`、`diligence_source_needed`。

**事件链始终只追加**。未走过决策日志的更新，不得覆盖既有 topic 历史。
