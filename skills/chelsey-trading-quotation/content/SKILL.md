---
name: chelsey-trading-quotation
description: 生成 Chelsey Trading 出口报价单内容。基于固定 Word/PDF 模板输出商业报价和技术参数表。当用户要求制作报价单、生成 quotation、创建出口报价、输出报价文件时使用。
---

# Chelsey Trading Quotation Skill v1.0

## 概述

本 skill 用于生成 Chelsey Trading 出口报价单内容，基于固定 Word/PDF 模板。

**适用范围**：
- 无轨转运车 / 有轨电车
- 储罐 / IBC / 工业设备
- EXW / FOB / CIF 报价

**核心原则**：不重新设计版式，只输出可填充到模板的干净内容。

**关联文件**：
- `body-pack-template.md` - 项目数据采集模板
- `reusable-prompts.md` - 可复用 Prompt 库

---

## 核心规则

### 品牌规范

| 项目 | 规则 |
|------|------|
| Seller | 必须是 **CHELSEY TRADING** |
| 语调 | 专业、简洁、出口导向 |
| 语言 | 简单易读的商务英语 |
| 段落 | 避免冗长的法律条款 |

### 禁区（绝对不能出现）

- 中国供应商信息（公司名、电话、地址）
- 国内发票、VAT 发票相关词汇
- "translated from Chinese"、"supplier" 等暴露来源的词
- 任何让买家察觉中间商存在的内容

### 写作原则

> 写得像 Chelsey Trading 直接出具，不要有任何中间商痕迹。

---

## 文档结构

报价单由 **2 页** 组成：

| 页码 | 内容 |
|------|------|
| Page 1 | 商业报价（Header + Buyer Info + Product + Price + Terms + Notes） |
| Page 2 | 技术参数表（Header + 19 行参数） |

---

## Page 1 字段映射

### A. 头部信息

```
Seller:       CHELSEY TRADING
Main Title:   FORMAL QUOTATION
Product:      [产品名称]
Trade Term:   [贸易条款 + 目的港]
```

### B. 买家信息表

| 字段 | 占位符 |
|------|--------|
| Buyer | [BUYER NAME] + [BUYER COMPANY] |
| Destination Port | [DESTINATION PORT] |
| Quotation No. | [QUOTE NO.] |
| Date / Validity | [DATE] / [VALIDITY] |

### C. 产品摘要

| 字段 | 占位符 |
|------|--------|
| Product | [PRODUCT NAME] |
| Platform Size | [PLATFORM SIZE] |
| Quantity | [QUANTITY] |
| Application | [APPLICATION] |

### D. 价格框

| 字段 | 占位符 |
|------|--------|
| Price Term | Total [CIF/FOB/EXW] Price |
| Amount | [CURRENCY] [TOTAL PRICE] |
| Note | [PRICE NOTE / SPECIAL OFFER] |

### E. 商业条款

| 字段 | 占位符 | 默认值 |
|------|--------|--------|
| Payment Terms | [PAYMENT TERMS] | 30% T/T deposit in advance; 70% balance before shipment. |
| Lead Time | [LEAD TIME] | About 20 working days after receipt of deposit and final technical confirmation. |
| Warranty | [WARRANTY] | 12 months from the date of shipment for manufacturing defects. |
| Packing | [PACKING] | Standard export packing suitable for ocean transportation. |

### F. CIF/FOB 含与不含

**CIF Included**：
> Equipment cost, ocean freight, origin local charges, and marine insurance.

**CIF Excluded**：
> Import duty, customs clearance, destination port charges, inland transport after arrival, unloading, installation, and commissioning.

**FOB Included**：
> Equipment cost and origin local charges.

**FOB Excluded**：
> Ocean freight, marine insurance, import duty, customs clearance, destination port charges, inland transport, unloading, installation, and commissioning.

### G. 商业备注

最多 3 条，简洁 bullets。

---

## Page 2 技术参数表

### 表头

| 字段 | 占位符 |
|------|--------|
| Product | [PRODUCT TYPE] |
| Model | [MODEL] |
| Steering / Travel | [STEERING / TRAVEL] |
| Quantity | [QUANTITY] |

### 参数表格

列结构（5 列）：
- **No.** - 序号
- **Item** - 项目名称
- **Specification** - 规格
- **Unit** - 单位
- **Remarks** - 备注

标准行数：19 行（预留充足空间）

---

## 数量单位规则

| 项目类型 | 正确 | 错误 |
|----------|------|------|
| 整机 | **2 Units** | 2 Sets |
| 配件 | unit / set / pc / pcs | - |
| 长度 | mm | - |
| 时间 | h | hour / hours |
| 速度 | m/min | m/minute |

**绝对禁止混用**：同一份报价中不能同时出现 "2 Units" 和 "2 Sets"。

---

## 术语一致性规则

以下表达必须严格统一：

| 场景 | 正确写法 |
|------|----------|
| 转向/行走 | `360° steering / straight travel` |
| 轮子描述 | `polyurethane-coated wheel` |
| 充电器功能 | `auto-stop when fully charged` |
| 续航描述 | `continuous operation under full load` |
| 控制箱功能 | `with emergency stop and speed regulation` |
| 安全系数 | `Maximum impact load: 25 ton` |
| 转向方式 | `forward / backward / left / right travel steering` |
| 包装描述 | `standard export packing suitable for ocean transportation` |
| 保险 | `marine insurance` |
| 超长货物 | `full container loading` |

---

## 默认商业术语

当项目数据未指定时，使用以下默认值：

### Payment Terms
```
30% T/T deposit in advance; 70% balance before shipment.
```

### Lead Time
```
About 20 working days after receipt of deposit and final technical confirmation.
```

### Warranty
```
12 months from the date of shipment for manufacturing defects.
```

### Packing
```
Standard export packing suitable for ocean transportation.
```

---

## 商业备注模板

### 超长货物备注
```
Due to the extra-long cart length, shipment must be arranged by full container loading,
which results in relatively high logistics cost.
```

### 卸货备注
```
Buyer shall prepare suitable unloading equipment at site.
```

### 电池备注
```
Lead-acid battery SDS is available upon request.
```

### 标准 3 条备注组合
```
1. This offer is based on the current confirmed specification and quantity of [X] units.
2. Due to the extra-long cart length, shipment must be arranged by full container loading,
   which results in relatively high logistics cost.
3. Buyer shall prepare suitable unloading equipment at site. Lead-acid battery SDS is
   available upon request.
```

---

## 工作流

### Step 1: 读取项目输入
收集以下信息：
- Trade Term (EXW/FOB/CIF)
- Buyer (姓名 + 公司)
- Destination Port
- Product (产品名称)
- Model (型号)
- Quantity (数量)
- Platform Size (长 x 宽 mm)
- Application (用途)
- 其他技术参数

### Step 2: 生成 Page 1 内容
按字段顺序填充：
1. Header 信息
2. Buyer Meta 信息
3. Product Summary
4. Price Box
5. Commercial Terms
6. Included / Excluded
7. Commercial Notes (最多 3 条)

### Step 3: 生成 Page 2 内容
1. Technical Parameter Header
2. 19 行参数表格

### Step 4: QA 检查
- [ ] Quantity = "X Units"（不是 Sets）
- [ ] Trade Term 与标题一致
- [ ] Price Term 正确
- [ ] Destination Port 正确
- [ ] Model 正确
- [ ] 技术参数单位无混用
- [ ] 备注数量 ≤ 3 条

### Step 5: 输出
输出干净的文本内容，可直接填充到 Word 模板。

---

## 给其他 AI 的 Prompt 模板

```
You are preparing content for a Chelsey Trading export quotation using an existing
fixed Word template.

Your task is to generate only the structured quotation content, not a new layout.

Requirements:
- Seller must be CHELSEY TRADING
- Tone must be professional, concise, export-oriented
- Do not mention any Chinese supplier, domestic invoice, VAT invoice, or source translation
- Keep terminology consistent with the skill pack
- Whole machine quantity must use "Units"
- Output must follow the exact structure below

Output structure:
1. QUOTATION PAGE CONTENT
2. TECHNICAL PARAMETER HEADER
3. TECHNICAL PARAMETER TABLE
4. QA CHECKLIST

Project input:
[PASTE PROJECT DATA HERE]

Use these standard defaults unless project input says otherwise:
- Payment Terms: 30% T/T deposit in advance; 70% balance before shipment.
- Lead Time: About 20 working days after receipt of deposit and final technical confirmation.
- Warranty: 12 months from the date of shipment for manufacturing defects.
- Packing: Standard export packing suitable for ocean transportation.
- CIF Included: Equipment cost, ocean freight, origin local charges, and marine insurance.
- CIF Excluded: Import duty, customs clearance, destination port charges, inland transport
  after arrival, unloading, installation, and commissioning.
- FOB Included: Equipment cost and origin local charges.
- FOB Excluded: Ocean freight, marine insurance, import duty, customs clearance, destination
  port charges, inland transport, unloading, installation, and commissioning.

Commercial note style:
- Keep to 2–3 short bullets maximum
- If cargo is extra-long, mention full container loading and higher logistics cost
- If lead-acid battery applies, say SDS is available upon request
```

---

## 文件依赖

| 文件 | 用途 |
|------|------|
| `Chelsey_Trading_Quotation_Template_V1.docx` | 版式模板 |
| `body-pack-template.md` | 项目数据采集模板 |
| `reusable-prompts.md` | 可复用 Prompt 库 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2026-04-22 | 初始版本 |

---

## 作者

MiniMax Agent - 基于 Chelsey Trading Quote Skill Pack v1 整理