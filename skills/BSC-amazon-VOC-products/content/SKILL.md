---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: ca1979a61977255097b8440bb33d5e07
    PropagateID: ca1979a61977255097b8440bb33d5e07
    ReservedCode1: 3046022100dc6c8a3f8ea1e5ce8adb77e326be3bb2616facf5277cec8b06d78c28829edf7f022100be81f6df760dbc45d8313cc30c2e53e111a89085c3afccd96da301c4720cab39
    ReservedCode2: 3046022100c7b5647c3218b70f6f1e7cc382980875ec6adf001150518a1528fe5528745b6d022100a97bf11726df73ec2c934c36a6dad717a18f314daab79002c74704206378ae31
description: 面向 Amazon 选品、VOC、竞品与关键词研究的深度分析技能。它会围绕一个需求词产出本地 `data.json`、`report.md`、`charts/`、`charts_manifest.json`，并在环境可用时发布飞书文档。只要用户提到 Amazon 选品判断、关键词机会、评论痛点、竞品研究、立项报告、Listing / PPC 依据、飞书交付，就应优先使用本技能。
name: BSC-amazon-VOC-products
---

# BSC-amazon-VOC-products

这是一个适合直接拿来做 Amazon 选品研究交付的技能。
它不是只返回几段零散数据，而是尽量把一条完整分析链路跑通，最终产出：`data.json`、`report.md`、`charts/`、`charts_manifest.json`，以及可选的 `feishu_publish_result.json`。

## 适用场景

当用户出现下面这些意图时，优先使用本技能：
- 想判断某个 Amazon 产品方向到底值不值得做
- 想围绕某个关键词做深度 VOC / 评论 / 趋势 / 竞争研究
- 想输出一份可以交给老板、运营或客户的立项分析
- 想为 Listing、PPC、价格策略、图文表达提供依据
- 想把本地研究结果继续同步到飞书文档

## 核心原则

- 本地结果优先，飞书只是交付层
- 不恢复 `dashboard.html` 作为主产物
- 图表是报告增强层，不是第二套平行系统
- 增强维度失败允许降级，但不能阻断基础交付
- 报告要有证据链和建议动作，不只是堆数据

## 主链路

`data.json` → `charts/` → `report.md` → `feishu_publish_result.json`

## 功能覆盖

- **市场判断**：类目映射、Top100、趋势、规模与竞争基础面
- **关键词研究**：核心词、延伸词、SERP、搜索趋势、流量入口
- **竞争分析**：价格带、评分带、评论带、卖家来源、代表竞品拆解
- **VOC 洞察**：正负评主题、痛点、购买理由、质量与适配风险
- **供应链线索**：1688 相似货源与粗粒度成本参考
- **图表增强**：从 `data.json` 生成静态 SVG 图表并混排进 `report.md`
- **飞书交付**：先创建正文，再逐张追加上传本地图表
- **执行延伸**：可继续输出 Listing、PPC、定价、主图 / 副图表达建议

## 运行要求

- Claude Code CLI
- Python 3.10+
- 可用的 Sorftime API Key
- `node`
- `lark-cli`（如果需要发布飞书）

## 命令示例

```bash
python BSC-amazon-VOC-products/run_analysis.py "barbell clamps" US
python BSC-amazon-VOC-products/run_analysis.py "weight bar clips" US --no-publish
python BSC-amazon-VOC-products/run_analysis.py "standing desk" US --api-key "YOUR_API_KEY"
```

## 工作流程

### 1. Collect data
`collect_data.py` 负责采集并归一化市场数据、关键词、竞品、评论、VOC 等

### 2. Render charts
`render_charts.py` 从 `data.json` 生成本地图表与 `charts_manifest.json`

### 3. Build report
`build_report.py` 生成唯一主报告 `report.md`

### 4. Publish to Feishu
`publish_feishu_doc.py` 按"两段式发布"执行飞书文档交付

## 输出结构

```
voc-products-reports/
└── {keyword}_{site}_{YYYYMMDD}/
    ├── data.json
    ├── report.md
    ├── charts_manifest.json
    ├── charts/
    │   ├── price_bands.svg
    │   ├── rating_bands.svg
    │   ├── review_bands.svg
    │   └── ...
    ├── feishu_publish_result.json
    └── raw/
        └── ...
```

## 最低完成标准

任务完成后至少满足：
- 存在 `data.json`
- 存在 `report.md`
- 存在 `charts_manifest.json`
- 存在 `charts/`
- 不生成 `dashboard.html`
- 报告在缺失部分维度时仍可读、可交付
