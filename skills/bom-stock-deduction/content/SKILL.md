---
name: bom-stock-deduction
description: |
  Extended BOM inventory workflow: (1) compare against YiBo supplier stock and annotate supply source, (2) deduct re-production consumption from existing stock. Use when the user needs to: (1) perform YiBo supplier stock comparison on non-KG materials, (2) update stock status to "一博供" based on YiBo availability, (3) deduct re-production material consumption from current inventory, (4) identify materials that become insufficient after deduction. Triggered by phrases like "一博供应比对", "扣减复投", "库存扣减", or when the user uploads a document list with re-production BOMs on top of an existing matched BOM file.
---

# BOM Stock Deduction & YiBo Supply Check

This skill has two phases. Execute them sequentially based on user request.

## Phase 1: YiBo Supply Comparison

### Input Files

Request from user:
1. **BOM Matching Result** (BOM库存匹配结果) — the output from `bom-stock-matcher` skill, with these additional columns:
   - `一博物料库存` (YiBo stock levels: `10K+`, `3K+`, `1K+`, `1K-`, `1K-库存不足`)
   - `零件状态` (part status: "正常供货", "停产", "不用于新设计", or empty)
   - `一博问题` (YiBo issue notes, may be empty)
   - `库存状态` (current status from matcher, e.g. "客供：上架库存")
   - `需求数量(N套)` (requirement quantity)

### YiBo Stock Parsing

Convert `一博物料库存` text to numeric values:
```
"10K+" → 10000
"3K+"  → 3000
"1K+"  → 1000
"1K-"  → 500
"1K-，库存不足" or contains "库存不足" → 0
NaN/empty → 0
```

### Comparison Rules

1. **Filter rows where `库存状态` ≠ "客供：上架库存"** — only these need YiBo check
2. For each filtered row, compare parsed YiBo stock vs requirement:
   - If YiBo stock ≥ requirement → **update `库存状态` = "一博供"**
   - If YiBo stock < requirement → **highlight entire row in yellow**
3. For `一博问题` column cells:
   - If `一博问题` is not empty AND `库存状态` = "一博供" → **green fill**
   - If `零件状态` ≠ "正常供货" → **green fill** + append "；请一博在线重新选型"

### Output

Update the same Excel with modified `库存状态` and colored cells.

---

## Phase 2: Re-Production Stock Deduction

### Input Files

Request from user:
1. **Document List** (单据列表) — must contain:
   - `物料名称` (material name, e.g. "电路板,S801PE1600TP_V1_0")
   - `数量` (quantity ordered)
   - `单据日期` (document date)

2. **Daily Worksheet Report** (工单调拨齐套报表) — must contain:
   - `成品名称` (product name)
   - `物料编码`, `物料名称` (material info)

3. **Re-Production BOMs** (复投BOM) — one or more files, each must contain:
   - `物料编码` (material code)
   - `复投XX套用量` (re-production quantity for XX sets)
   - `供料方式` / `复投供料方式` (supply method, e.g. "客供：上架库存", "一博供")

### Deduction Logic

1. **Filter S801 materials from document list**:
   - Select rows where `物料名称` starts with "电路板,S801"
   - Select rows where `单据日期` is within the last 4 days (current date - 4 days to current date)

2. **Check against worksheet**:
   - For each selected S801 material, check if it appears in the worksheet `成品名称` column
   - If **NOT found** in worksheet → this material needs stock deduction

3. **Calculate deduction amount**:
   - From each re-production BOM, filter rows where supply method = "客供：上架库存"
   - Group by material code and sum `复投XX套用量`
   - Only materials present in **both** re-production BOMs (intersection) are deducted

4. **Apply deduction to main BOM**:
   ```
   扣减后库存 = 原库存总数量 - TP复投用量 - DS复投用量
   ```
   - Update `库存总数量` column with deducted value
   - If 扣减后库存 < 需求数量 → highlight row red, update status to "扣减后库存不足"
   - If still sufficient → append deduction info to status (e.g. "客供：上架库存(已扣TP11997+DS17043)")

### Key Rules

- Only deduct materials with supply method = "客供：上架库存" — do NOT deduct "一博供" materials
- When a material appears multiple times in a BOM (different designators), sum all quantities before deduction
- Deduct from the MAIN BOM's `库存总数量`, not from YiBo stock
- Track both TP (S801PE1600TP) and DS (S801DPS256TP) deductions separately for status annotation

## Complete Workflow Order

1. Run Phase 1 (YiBo comparison) first if the user provides YiBo data
2. Run Phase 2 (re-production deduction) if the user provides document list + re-production BOMs
3. Both phases can run independently or sequentially on the same file
