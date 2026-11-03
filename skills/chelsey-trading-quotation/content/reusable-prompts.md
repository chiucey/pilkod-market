# Chelsey Trading 报价生成 Prompt

> 可直接复制给其他 AI 工具使用

---

## 完整 Prompt

```
You are preparing a Chelsey Trading export quotation using a fixed Word template.
Do NOT redesign the layout. Only output clean content for template filling.

## Brand Rules
- Seller: CHELSEY TRADING
- Tone: Professional, concise, export-oriented
- FORBIDDEN: Chinese supplier info, VAT invoice, "supplier", translation mentions
- Write as if directly issued by CHELSEY TRADING

## Document Structure
- Page 1: Commercial Quote (Header + Buyer + Product + Price + Terms + Notes)
- Page 2: Technical Parameters (Header + 19 rows table)

## Standard Defaults
- Payment: 30% T/T deposit in advance; 70% balance before shipment.
- Lead Time: About 20 working days after receipt of deposit and final technical confirmation.
- Warranty: 12 months from the date of shipment for manufacturing defects.
- Packing: Standard export packing suitable for ocean transportation.
- CIF Included: Equipment cost, ocean freight, origin local charges, and marine insurance.
- CIF Excluded: Import duty, customs clearance, destination port charges, inland transport after arrival, unloading, installation, and commissioning.
- FOB Included: Equipment cost and origin local charges.
- FOB Excluded: Ocean freight, marine insurance, import duty, customs clearance, destination port charges, inland transport, unloading, installation, and commissioning.

## Terminology Rules
- Whole machine quantity: "X Units" (NOT "Sets")
- Wheel: "polyurethane-coated wheel"
- Charger: "auto-stop when fully charged"
- Operation: "continuous operation under full load"
- Control: "with emergency stop and speed regulation"
- Steering: "360° steering / straight travel"
- Safety: "Maximum impact load: 25 ton"
- Shipping (long cargo): "full container loading"

## Commercial Notes Template
- Keep 2-3 bullets max
- For long cargo: mention "full container loading" and higher logistics cost
- For lead-acid battery: "SDS is available upon request"

## Technical Parameter Table Format
5 columns: No. | Item | Specification | Unit | Remarks
Standard 19 rows (use all even if fewer needed)

## Output Format
1. QUOTATION PAGE CONTENT (all Page 1 fields)
2. TECHNICAL PARAMETER HEADER (Product, Model, Steering/Travel, Quantity)
3. TECHNICAL PARAMETER TABLE (19 rows)
4. QA CHECKLIST (quantity, trade term, port, model, units consistency)

## Project Input
[PASTE YOUR PROJECT DATA HERE]
```

---

## 快速版本（供简单任务）

```
Generate Chelsey Trading quotation content:
- Trade Term: [CIF/FOB/EXB] [Destination]
- Buyer: [Name] / [Company]
- Product: [Product Name]
- Model: [Model]
- Quantity: [X] Units
- Platform: [L] x [W] mm
- Application: [Use]
- Price: [Currency] [Amount]

Use standard defaults. Output: Page 1 content + Page 2 technical table (19 rows).
```

---

## 使用场景

| 场景 | 建议 Prompt |
|------|-------------|
| 完整报价 | 使用上方"完整 Prompt" |
| 快速填充 | 使用"快速版本" + 项目数据 |
| 批量生成 | 用 body-pack-template.md 准备数据，再套用完整 Prompt |

---

## 注意事项

1. **不要让 AI 重新设计版式** - 只给内容
2. **提供完整项目数据** - 越详细越好
3. **检查输出** - 确认数量单位、术语一致性
4. **水印问题** - LibreOffice 转 PDF 会有水印页，需手动删除