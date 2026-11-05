# 跟踪器物化工具

运行 `scripts/materialize_marginal_tracker.py` 可生成一份新的本地 CSV 包;当 `openpyxl` 已安装时,可附带打包为 XLSX。该辅助工具**只做脚手架**——不决定事件信号、不负责最终呈现格式、不会原位编辑既有跟踪器。

```bash
python scripts/materialize_marginal_tracker.py [tracker_input.json] --output-dir output
```

## 输入 JSON 结构

顶层是一个 `topics` 数组(或 `threads` / `chains` / `tracks` 任一别名)。每个 topic 是一条独立的事件链:

```json
{
  "topics": [
    {
      "topic_id": "nvda-capex",
      "topic": "Nvidia AI capex cycle",
      "summary": "Hyperscaler capex trajectory and NVDA share.",
      "status": "intact",
      "created_at": "2026-01-15",
      "tags": ["semis", "ai", "us"],
      "events": [
        {
          "event_id": "E001",
          "date": "2026-02-10",
          "headline": "MSFT raises FY26 capex guide by 15%",
          "fact": "MSFT FY26 capex now $95B vs $82B prior.",
          "source": "MSFT Q2 FY26 call",
          "signal": "+1 mildly confirming",
          "marginal_change": "Hyperscaler capex envelope expanded.",
          "interpretation": "...",
          "impact": "FY26 revenue +3%, EPS +5%"
        },
        {
          "event_id": "E002",
          "prev_event_id": "E001",
          "date": "2026-03-05",
          "headline": "..."
        }
      ]
    }
  ]
}
```

**容错点**:

- 顶层只有 `topic` / `events` 也接受(当作单 topic)
- 单个 topic 内 `events` 可以省略 `prev_event_id`——脚本会按数组顺序自动串成链
- `events` 也可写成 `timeline` / `history` / `entries` / `items`
- 字段名大小写、空格、连字符不敏感(`Event ID` 与 `event_id` 同义)
- 任何字段都可省略,空字段以可见的方式落表

## Topic 元字段

`topic_id`、`topic`、`summary`、`status`、`created_at`、`last_updated`、`tags`,以及脚本自动计算的 `event_count`、`head_event_id`、`tail_event_id`。

## Event 字段

`event_id`、`prev_event_id`、`date`、`sequence`、`headline`、`fact`、`source`、`source_type`、`signal`、`marginal_change`、`interpretation`、`evidence_quality`、`impact`、`linked_event_ids`(跨链或同链多前驱)、`follow_up`。

## 产物

- `topics.csv` — 全部 topic 索引,含链 head/tail
- `events__<topic_id>.csv` — 每个 topic 一张事件链表
- `run_log.json` + `manifest.json`
- 依赖具备时,尽力产出单文件 XLSX

可选的 XLSX 工作簿以 `Cover` 选项卡开头,呈现 topic 总数、事件总数、每个 topic 的链长与首尾;随后是 `topics` 索引选项卡,然后每个 topic 一个选项卡。更新时使用新的输出目录 / 文件;除非用户明确授权,不要覆写既有工作簿。

最终的跟踪器更新交付:默认把跟踪器摘要、事件链、支柱状态、行动阈值与证据缺口整理为 `visual-page brief`,调用 `visual-page` 生成 GUI/HTML 审查页。XLSX/CSV 只作为用户明确要求或审计/导入支持附件。若生成 XLSX,按需打磨工作簿布局,使首屏 `Cover` 紧凑、可读,详细事件留在各 topic 选项卡;除非用户明确要求,不要加入数值评分图。
