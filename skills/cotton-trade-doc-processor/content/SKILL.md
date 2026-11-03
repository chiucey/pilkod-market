---
name: cotton-trade-doc-processor
description: 处理江苏绿韵数字科技有限公司仓管中心日常棉花贸易文档，识别最终转入绿韵的上游货转、仓单注销、下游货转及采销合同，按 11 位批号输出带字段级来源证据的系统兼容 JSON。
version: 6.0
---

# 仓管中心棉花贸易文档结构化提取技能

## 系统执行边界

本技能用于 CottonAI 最终结构化提取阶段。系统已经完成文件扫描、格式处理和内容转写，并提供：

- `Source File Tree`：当前企业文件夹结构。
- `Source Files`：当前任务可引用的来源文件相对路径。
- `Document Markdown`：PDF、图片、扫描件 OCR，以及 Word/Excel 原生结构和视觉复核结果。

最终执行模型只负责文件分类、跨文档关联、字段提取和校验，不得自行调用 PyMuPDF、Read、python-docx，不得重新读取本地路径、转换图片、创建临时文件或生成 Excel。

只返回一个 JSON 对象，不得返回解释、Markdown 代码围栏、注释或其他文本。根节点必须是 `items` 数组，一个有效棉花批号对应一条记录。

系统单独管理 `processingDate`、数据库持久化、人工审核和后续导出。不得输出 `remark`、`备注`、`error`、置信度或 Excel 文件信息等未定义字段。

## 输出 JSON 结构

```json
{
  "items": [
    {
      "date": "2026-01-05",
      "upstreamCompany": "中哲农产品有限公司",
      "warehouseName": "阿克苏银星物流有限公司",
      "productType": "新疆棉",
      "batchNumber": "65033251136",
      "weightTons": 42.944,
      "quantityPieces": 186,
      "downstreamCompany": "青岛旭鸿供应链有限公司",
      "entryDate": "2026-01-05",
      "exitDate": "2026-01-05",
      "sourceFile": "中哲转绿韵出库单.pdf",
      "sourceFiles": [
        "中哲转绿韵出库单.pdf",
        "ZX65033251136提货单.pdf",
        "货转转出/数科-青岛旭鸿货转.pdf"
      ],
      "sourceEvidence": [
        {
          "sourceFile": "中哲转绿韵出库单.pdf",
          "fieldKeys": ["date", "upstreamCompany", "warehouseName", "batchNumber", "entryDate"],
          "evidenceNote": "直接提供最终转入绿韵的货权关系、仓库、批号和转入日期"
        },
        {
          "sourceFile": "ZX65033251136提货单.pdf",
          "fieldKeys": ["warehouseName", "batchNumber", "weightTons", "quantityPieces"],
          "evidenceNote": "补充并校验当前批号的仓库、重量和件数"
        },
        {
          "sourceFile": "货转转出/数科-青岛旭鸿货转.pdf",
          "fieldKeys": ["batchNumber", "downstreamCompany", "exitDate"],
          "evidenceNote": "直接提供当前批号的下游公司和转出日期"
        }
      ]
    }
  ]
}
```

## 字段契约

| 字段 | 类型 | 规则 |
|---|---|---|
| `date` | string/null | 当前批号业务日期。优先使用 `entryDate`，其次使用同批仓单注销日期，格式 `YYYY-MM-DD`。不是 `processingDate`。 |
| `upstreamCompany` | string/null | 最后一步把当前批号货权转入江苏绿韵数字科技有限公司的直接上游公司全称。 |
| `warehouseName` | string/null | 当前批号仓库全称，优先取最终上游货转文件，缺失时用同批仓单注销文件补全。 |
| `productType` | string | 固定为 `新疆棉`。 |
| `batchNumber` | string | 棉花批号主键，必须是 11 位数字字符串。 |
| `weightTons` | number/null | 当前批号重量，单位吨。 |
| `quantityPieces` | integer/null | 当前批号件数，单位件。 |
| `downstreamCompany` | string/null | 绿韵将当前批号转出的下游公司全称；下游货转缺失时可由销售合同补充。 |
| `entryDate` | string/null | 当前批号最后一步转入绿韵的日期，格式 `YYYY-MM-DD`。 |
| `exitDate` | string/null | 当前批号从绿韵转给下游的日期，格式 `YYYY-MM-DD`；无匹配下游货转时为 `null`。 |
| `sourceFile` | string | 当前记录最关键证据文件相对路径，必须等于 `sourceFiles[0]`。 |
| `sourceFiles` | string[] | 支持当前记录人工审核的全部来源文件相对路径，必须非空、去重并来自当前任务 Source Files。 |
| `sourceEvidence` | object[] | 非空字段级证据数组；每项只包含 `sourceFile`、`fieldKeys`、`evidenceNote`。 |

`sourceEvidence.fieldKeys` 只允许使用：`date`、`upstreamCompany`、`warehouseName`、`productType`、`batchNumber`、`weightTons`、`quantityPieces`、`downstreamCompany`、`entryDate`、`exitDate`。

## 业务角色与文件分类

江苏绿韵数字科技有限公司是贸易中间商：从上游公司买入货物，再销售给下游公司。

必须根据正文中的交易主体和货权方向分类，文件名和文件夹名只作辅助：

| 文件类型 | 内容定义 | 字段用途 |
|---|---|---|
| 采购合同 | 绿韵从上游公司采购货物 | 校验上游；仓单注销缺失时，按明确批号补充件数和重量 |
| 销售合同 | 绿韵向下游公司销售货物 | 下游货转缺失时补充 `downstreamCompany`，不得提供 `exitDate` |
| 上游货转文件 | 上游将货权转至绿韵，包括货权转移单、货权转让单、出库单、提货单、收货确认单等 | 确定上游、批号、仓库、转入日期 |
| 仓单注销文件 | 全国棉花交易市场或郑商体系的仓单注销、提货类文件 | 按批号确定或补充仓库、件数、重量、业务日期 |
| 下游货转文件 | 绿韵将货权转至下游，包括货权转移单、货权转让单、出库单、提货单、收货确认单等 | 确定下游公司和转出日期 |

## 文件处理与过滤

日常核心格式为 `.PDF`、`.JPG`、`.JPEG`、`.PNG`、`.DOCX`，扩展名不区分大小写。若系统已提供 `.DOC`、`.XLS`、`.XLSX` 的 Document Markdown，也必须按本技能规则处理，不得丢弃有效证据。

必须跳过且不得加入来源证据：

- `在库留痕/` 下全部文件。
- 文件名包含 `点价`、`结算`、`库费`、`补充` 的文件。
- `Thumbs.db`、`.DS_Store` 等系统文件。
- 风险告知、费用说明等不提供本技能业务字段的文件。
- 只支持其他批号或其他企业文件夹、与当前记录无关的文件。

同名文件必须按完整相对路径区分，不得因 basename 相同而覆盖、合并或误关联。文件路径必须原样复制自 Source Files。

## Office 与 OCR 取值优先级

Office Document Markdown 可能包含原生结构、页面视觉复核和内嵌图片 OCR：

- 段落顺序、表格行列、工作表、显示值、公式结果、批号、件数、重量和标准日期优先使用原生结构。
- 印章、签字、手写日期、浮动文本框、绘图和图片文字优先使用视觉复核。
- 视觉 OCR 与可靠原生数字冲突时，不得直接覆盖，必须用同批其他单据校验。
- Excel 工作表必须独立理解；不得跨工作表拼接同一行号，不得把合并区域汇总值复制给每个批号。
- 隐藏工作表、隐藏行和隐藏列默认只作辅助，除非其他有效单据证明其属于当前交易。
- OCR 中出现 LaTeX 包裹的普通文字时按业务文字理解，不得把公式符号当作字段值。

## 标准处理流程

1. 读取 Source File Tree、Source Files 和全部 Document Markdown，先应用硬跳过规则。
2. 按正文识别采购合同、销售合同、上游货转、仓单注销和下游货转。
3. 构建货权链，只保留最后一步直接转入绿韵的上游货转，排除前置链路。
4. 从目标上游货转的表格、正文、备注和附件清单提取有效批号，每个批号建立独立记录。
5. 按批号关联仓单注销；无匹配仓单注销时，再用明确列出当前批号的采购合同补充件数和重量。
6. 按批号关联 `货转转出/` 下游货转；缺失时只用销售合同补充下游公司，转出日期保持 `null`。
7. 校验公司、仓库、批号、件数、重量和日期；缺失或冲突字段使用 `null`，继续处理其他字段和批号。
8. 生成主来源、来源列表和字段级证据，完成自检后只返回 JSON。

## 核心抽取规则

### 最终上游货转

- 目标文件必须明确表示转入方、购货单位、提货单位、新货权人或收货方为江苏绿韵数字科技有限公司、绿韵数科或可明确对应绿韵的主体。
- `upstreamCompany` 只取该最后一步的转出方。采购合同只能校验，不能替代最终货权关系。
- 多跳链路中的前置转让方不得输出为上游，不得作为当前记录主来源。
- 上游货转优先提供 `upstreamCompany`、`warehouseName`、`batchNumber`、`quantityPieces`、`entryDate`。

### 批号与拆分

- `batchNumber` 必须匹配 `^\d{11}$`，保持字符串，不得转为数值或科学计数法。
- 检查表格、正文、备注、页脚和附件清单，不得只检查表格。
- 不得把合同号、仓单号、验证码、货权编号或日期误作批号。
- 一个批号一条记录；同一企业文件夹内重复出现的同一批号合并证据，不重复输出。
- 汇总行包含多个批号时必须拆分；不得复制或平均分配汇总件数、汇总重量。
- 共享文件包含多个批号时，只输出当前企业文件夹对应或其他有效单据明确支持的批号，不跨文件夹扩张结果。

### 件数与重量

取值优先级：

1. 匹配当前批号的全国棉花交易市场或郑商体系仓单注销、提货文件。
2. 仓单注销缺失时，明确列出当前批号的采购合同。
3. 上游货转中明确对应当前批号的明细值，可用于交叉校验。

`quantityPieces` 必须为整数。`weightTons` 必须为吨；原文为千克时按 `1000 千克 = 1 吨` 换算。不得把金额、单价、总件数或总重量当作当前批号值。

### 仓库

- 优先取最终上游货转中的收货仓库、发货仓库、致某仓库或存放仓库。
- 缺失时取同批仓单注销中的指定交割仓库或监管仓库。
- 不得把贸易主体、转出方、货主或监管机构误作仓库。

### 下游与转出

- 只有 `货转转出/`、下游货权转移确认或收货确认文件明确匹配当前批号时，才填写 `exitDate`。
- 下游货转缺失或只包含其他批号时，可由销售合同补充 `downstreamCompany`，但 `exitDate` 必须为 `null`。
- 不得使用销售合同日期或被跳过文件中的日期填写 `exitDate`。

### 日期

- `entryDate` 首选最终上游货转的落款、盖章、出库或货权生效日期。
- 目标上游货转已明确支持当前批号但 OCR 漏日期时，可用同批仓单注销业务日期兜底；必须同时保留两份来源并标注跨文档推断。
- `date` 是业务日期，优先等于 `entryDate`；`entryDate` 仍不明确时可使用同批仓单注销日期，否则为 `null`。
- `processingDate` 由系统根据任务目录确定，不得输出为额外字段，也不得用模型运行当天日期替代业务日期。
- 日期统一为 `YYYY-MM-DD`，不完整或无法确认时为 `null`。

## 异常决策表

| 场景 | 处理 |
|---|---|
| 多个上游货权链 | 只取最后一步转入绿韵的文件，前置链路排除 |
| 货转与仓单注销合并在一个 PDF | 按页和标题拆分理解，同一路径可支持多组字段 |
| 批号位于备注 | 从备注提取后逐批关联仓单注销 |
| 货转只有汇总件数或重量 | 拆批后按仓单注销或采购合同取明细，不平均分配 |
| 下游货转缺失 | 销售合同只补下游公司，`exitDate=null` |
| 下游货转只含其他批号 | 当前批号不得使用该文件的下游公司或日期 |
| 共享货转包含多个文件夹批号 | 只保留当前文件夹或其他有效单据支持的批号 |
| 上游货转 OCR 漏底部日期 | 检查视觉复核；仍缺失时用同批仓单注销日期兜底 |
| 原生 Office 与视觉 OCR 数字冲突 | 原生结构优先，并用同批其他文件校验 |
| 字段缺失、冲突或乱码 | 对应字段输出 `null`，不中断其他字段和批号 |

## 来源证据规则

- `sourceFile` 优先选择包含最终转入绿韵关系和当前批号的上游货转；否则选择同批仓单注销。
- `sourceFile` 必须为非空字符串，并且必须等于 `sourceFiles[0]`。
- `sourceFiles` 只包含支持当前批号或当前记录跨文档审核链的文件，不得无差别加入企业目录全部文件。
- `sourceFiles` 必须非空、去重，所有路径与 Source Files 中的相对路径完全一致；不得输出绝对路径、改写文件名、只保留 basename 或编造路径。
- 每个 `sourceEvidence.sourceFile` 必须存在于 `sourceFiles`；`sourceFiles` 中每个文件也必须至少对应一项 `sourceEvidence`。
- 每个 `fieldKeys` 必须非空，只列出该文件实际支持的字段；每个 `evidenceNote` 必须非空，只说明直接提供、补充、校验或跨文档推断。
- 除固定值 `productType` 外，每个非 `null` 业务字段必须至少被一个 `fieldKeys` 覆盖。
- 采购合同补充件数或重量、销售合同补充下游、仓单注销补日期时，必须在 `evidenceNote` 中明确说明兜底关系。

## 异常输出边界

- 单个文件失败、字段缺失或证据冲突不得阻断其他文件和批号。
- 无法可靠取得的值使用 `null`，不得使用空字符串、占位文字、乱码或推测值。
- 当前 Schema 不包含备注字段，不得增加 `remark` 或 `备注`；证据冲突只在相关 `evidenceNote` 中说明文件间校验关系。
- 没有有效 11 位批号时返回 `{"items":[]}`，不得生成 `PARSE-*` 或其他虚假批号。

## 输出校验

返回前必须自检：

- 只返回 JSON 对象，根节点为 `items` 数组。
- 每条记录只包含本技能定义的 13 个字段，不得输出中文旧字段名、备注或额外字段。
- `productType` 固定为 `新疆棉`。
- `batchNumber` 是匹配 `^\d{11}$` 的字符串。
- `quantityPieces` 为整数或 `null`；`weightTons` 为数字或 `null`，单位吨。
- `date`、`entryDate`、`exitDate` 为 `YYYY-MM-DD` 或 `null`。
- `sourceFile` 非空、来自 Source Files，并且等于非空去重数组 `sourceFiles` 的第一项。
- `sourceFiles` 只包含当前记录的有效审核来源，不包含跳过文件、无关文件或只匹配其他批号的文件。
- `sourceEvidence` 为非空对象数组，每项只包含非空的 `sourceFile`、`fieldKeys`、`evidenceNote`。
- `sourceFiles` 与 `sourceEvidence.sourceFile` 双向覆盖；`fieldKeys` 只使用允许的英文字段名。
- 除固定值 `productType` 外，每个非 `null` 业务字段都有字段级来源证据。
- 多批号已逐条拆分，未跨文件夹混入批号，未复制或平均分配汇总值。
- 所有文本无明显乱码；无法可靠恢复的业务字段已设为 `null`。
