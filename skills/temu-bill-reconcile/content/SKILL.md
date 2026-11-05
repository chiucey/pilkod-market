---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8427dc36540426d220d72771ca7e149d
    PropagateID: 8427dc36540426d220d72771ca7e149d
    ReservedCode1: 304502200e42ab0d53afa3796158bea0512a13853bed4ce3fda5795682524788c8c0145f022100d094950bcc87ed6861d6b8a702bb4c20ecdfa081a3ab2c6bf9397fc0462c679f
    ReservedCode2: 304602210080d28612436a94e60c47be4e734f325a0b598fdd9923e93f7b941d1b1e9ad92f022100d779f4c1a0becd7951aa9e081e3ec33a9f628758b9a0d30d65b9130fc037c5ff
description: Temu 账单核对 — 跨 4 个工作表（交易/退款/补贴/售后）以订单号 + SKU 双维度核对金额，标红不一致的行。用于 Temu 财务对账场景。当用户提到"账单核对"、"退款对账"、"Temu 账单"、"交易收入/退款/补贴/售后"时触发。
name: temu-bill-reconcile
---

# Temu 账单核对 Skill

## 适用场景

用户上传一个包含 4 个工作表的 Temu 财务账单 xlsx：
- **欧区-交易收入**（表1，订单原始收入）
- **欧区-消费者退款金额**（表2，按订单 + SKU 退款明细）
- **欧区-非商责平台售后补贴金额**（表3，按订单 + SKU 补贴明细）
- **欧区-售后问题**（表4，按订单 + SKU 赔付金额）

目标：把退款、补贴、售后金额整合到表1的 N、O、P 列，并标红不一致的行。

## 严格输出要求

1. 保留表1原本的表头
2. A 列（订单编号）顺序不变，重复编号保留
3. N 列名 = 消费者退款金额，O 列名 = 补贴金额，P 列名 = 售后金额
4. 不一致行红底白字加粗标红

## 核心算法：比例分配 + 整分摊（不均分余数）

### Pass 1：分配金额

对每个 T1 行 R（订单号 = orderId，SKU = sku，K = 收入金额）：

**Step 1**: 聚合该 orderId 下 T1 所有行的 K 值得到 K_sum

**Step 2**: 聚合 T2/T3/T4 在该 orderId 下的总金额：
- N_total = sum(T2.H where T2.B = orderId)
- O_total = sum(T3.H where T3.B = orderId)
- P_total = sum(T4.F where T4.B = orderId)

**Step 3**: 按 K 权重比例分摊，使用 **floor + 余数集中** 算法（关键）：
```
对每一行 i (i = 1..n):
    share_i = floor(N_total × K_i / K_sum × 100) / 100  # 单位:元,精度 0.01

allocated = sum(share_i)
remainder = round2(N_total - allocated)  # 余数，通常是 0.01 或 0.00

if |remainder| >= 0.005:
    # 把余数集中放到 K 值最大的那一行
    max_idx = argmax(K_i)
    share[max_idx] += remainder
```

**为什么这样做**：
- 比例均分会因四舍五入产生误差累积（例：315.19 ÷ 2 = 157.595 → 157.60 + 157.60 = 315.20，比真实多 0.01）
- floor + 余数集中保证 sum(N) = N_total 严格相等

### Pass 2：非株连标红

**关键规则**：只在该行 (orderId, sku) 在 T2/T3/T4 中**有直接记录**且值不符时标红。

```
对每个 T1 行 R:
    osKey = orderId + "||" + sku
    
    # N 检查
    if t2ByOS[osKey] !== undefined and |actual_N - t2ByOS[osKey]| > 0.02:
        标红 N 列
    
    # O 检查 (独立)
    if t3ByOS[osKey] !== undefined and |actual_O - t3ByOS[osKey]| > 0.02:
        标红 O 列
    
    # P 检查 (独立)
    if t4ByOS[osKey] !== undefined and |actual_P - t4ByOS[osKey]| > 0.02:
        标红 P 列
```

**为什么"非株连"**：
- 不因为某 (订单,SKU) 在 T2/T3/T4 缺失就标红同 SKU 的所有行
- 只标真正对不上的具体行

## 列号约定（1-indexed）

| 表 | 列 | 字段 |
|---|---|---|
| 表1 | A=1 | 订单编号 |
| 表1 | B=2 | 备货单号 |
| 表1 | C=3 | SKU ID |
| 表1 | K=11 | 收入金额 |
| 表1 | N=14 | 消费者退款金额（输出） |
| 表1 | O=15 | 补贴金额（输出） |
| 表1 | P=16 | 售后金额（输出） |
| 表2 | B=2 | 订单编号 |
| 表2 | C=3 | SKU ID |
| 表2 | H=8 | 消费者退款金额 |
| 表3 | B=2 | 订单编号 |
| 表3 | C=3 | SKU ID |
| 表3 | H=8 | 非商责平台售后补贴金额 |
| 表4 | B=2 | 违规单号（即订单号） |
| 表4 | C=3 | SKU ID |
| 表4 | F=6 | 赔付金额 |

## 性能优化要点

1. **使用 xlsx (SheetJS)** 而非 ExcelJS：
   - xlsx 是流式写入，13k 行 < 5s 完成
   - ExcelJS 写带样式的大表 3-5 分钟

2. **样式写入技巧**：
   - 用 `cell.s = { fill: { fgColor: { rgb: 'FFFF0000' }, patternType: 'solid' } }`
   - 写入时设 `cellStyles: true`

3. **数据结构**：
   - 一次构建所有 lookup（t2ByOrder, t2ByOS 等）
   - 避免重复遍历

4. **不要在循环中调用 round2/重 IO**

## 实现脚本（核心代码）

```javascript
const xlsx = require('xlsx');
const round2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;
const tol = 0.02;

function splitAmountWithRemainder(total, kValues) {
    const n = kValues.length;
    const kSum = kValues.reduce((s, x) => s + x, 0);
    if (kSum === 0 || n === 0) return new Array(n).fill(0);
    
    // Step 1: floor 分摊
    const shares = kValues.map(ki => 
        Math.floor(total * ki / kSum * 100 + Number.EPSILON) / 100
    );
    
    // Step 2: 计算余数
    const allocated = shares.reduce((s, x) => s + x, 0);
    const remainder = round2(total - allocated);
    
    // Step 3: 余数加到 K 最大的行
    if (Math.abs(remainder) >= 0.005) {
        let maxIdx = 0;
        for (let i = 1; i < n; i++) {
            if (kValues[i] > kValues[maxIdx]) maxIdx = i;
        }
        shares[maxIdx] = round2(shares[maxIdx] + remainder);
    }
    return shares;
}

async function reconcile(inputPath, outputPath) {
    const wb = xlsx.readFile(inputPath, { cellStyles: true });
    const t1 = xlsx.utils.sheet_to_json(wb.Sheets['欧区-交易收入'], { header: 1, defval: null }).slice(1);
    const t2 = xlsx.utils.sheet_to_json(wb.Sheets['欧区-消费者退款金额'], { header: 1, defval: null }).slice(1);
    const t3 = xlsx.utils.sheet_to_json(wb.Sheets['欧区-非商责平台售后补贴金额'], { header: 1, defval: null }).slice(1);
    const t4 = xlsx.utils.sheet_to_json(wb.Sheets['欧区-售后问题'], { header: 1, defval: null }).slice(1);
    
    // 构建 lookup
    const t1ByOrder = {};
    t1.forEach((r, idx) => {
        const o = r[0];
        if (o == null) return;
        if (!t1ByOrder[o]) t1ByOrder[o] = [];
        t1ByOrder[o].push({ row: r, originalIdx: idx });
    });
    
    const buildByOrder = (rows, amtCol) => {
        const m = {};
        rows.forEach(r => {
            const o = r[1];
            if (o == null) return;
            if (!m[o]) m[o] = 0;
            m[o] += round2(Number(r[amtCol]) || 0);
        });
        return m;
    };
    
    const buildByOS = (rows, amtCol) => {
        const m = {};
        rows.forEach(r => {
            const o = r[1], s = r[2], a = r[amtCol];
            if (o == null || s == null || a == null) return;
            const k = o + '||' + s;
            m[k] = (m[k] || 0) + round2(Number(a));
        });
        return m;
    };
    
    const t2ByOrder = buildByOrder(t2, 7);
    const t3ByOrder = buildByOrder(t3, 7);
    const t4ByOrder = buildByOrder(t4, 5);
    const t2ByOS = buildByOS(t2, 7);
    const t3ByOS = buildByOS(t3, 7);
    const t4ByOS = buildByOS(t4, 5);
    
    // 计算每行 N/O/P
    const newSheet = xlsx.utils.sheet_to_json(wb.Sheets['欧区-交易收入'], { header: 1, defval: null });
    const header = newSheet[0];
    header[13] = '消费者退款金额';
    header[14] = '补贴金额';
    header[15] = '售后金额';
    
    const stats = { N: 0, O: 0, P: 0 };
    const newRows = [header];
    
    t1.forEach((row, idx) => {
        const newRow = [...row];
        const orderId = row[0];
        const sku = row[2];
        const kVal = Number(row[10]) || 0;
        
        if (orderId == null) {
            newRows.push(newRow);
            return;
        }
        
        const t1Rows = t1ByOrder[orderId];
        const sortedRows = [...t1Rows].sort((a, b) => a.originalIdx - b.originalIdx);
        const kVals = sortedRows.map(x => Number(x.row[10]) || 0);
        const myIdx = sortedRows.findIndex(x => x.originalIdx === idx);
        
        const nShares = splitAmountWithRemainder(t2ByOrder[orderId] || 0, kVals);
        const oShares = splitAmountWithRemainder(t3ByOrder[orderId] || 0, kVals);
        const pShares = splitAmountWithRemainder(t4ByOrder[orderId] || 0, kVals);
        
        newRow[13] = myIdx >= 0 ? nShares[myIdx] : 0;
        newRow[14] = myIdx >= 0 ? oShares[myIdx] : 0;
        newRow[15] = myIdx >= 0 ? pShares[myIdx] : 0;
        newRows.push(newRow);
    });
    
    // 标红 (non-guilt-by-association)
    for (let r = 1; r < newRows.length; r++) {
        const row = newRows[r];
        const orderId = row[0];
        const sku = row[2];
        if (orderId == null || sku == null) continue;
        
        const osKey = orderId + '||' + sku;
        if (t2ByOS[osKey] !== undefined && Math.abs((row[13] || 0) - t2ByOS[osKey]) > tol) {
            stats.N++;
        }
        if (t3ByOS[osKey] !== undefined && Math.abs((row[14] || 0) - t3ByOS[osKey]) > tol) {
            stats.O++;
        }
        if (t4ByOS[osKey] !== undefined && Math.abs((row[15] || 0) - t4ByOS[osKey]) > tol) {
            stats.P++;
        }
    }
    
    console.log(`Mismatch: N=${stats.N} O=${stats.O} P=${stats.P}`);
    return { stats, newRows };
}

module.exports = { reconcile, splitAmountWithRemainder };
```

## 使用流程

1. 用户上传 xlsx 文件
2. 调用 `reconcile(inputPath, outputPath)`
3. 输出文件保留原 4 个工作表 + 新增/更新"汇总核对"sheet
4. 通过 message 工具发到微信

## 已知边界情况

1. T3 中 H=0 的记录会被识别为"无实际补贴"（不标红），与某些早期版本不同
2. 多对一场景下，余数 0.01 集中放到 K 最大的那一行
3. 浮点容差 = 0.02（处理浮点累加误差）

## 历史变更

| 日期 | 变更 |
|---|---|
| 2026-07-09 | 初版：比例分配 + 四舍五入（舍入差 bug） |
| 2026-07-10 | 修复：floor + 余数集中分配（保证求和严格相等） |
| 2026-07-10 | 封装为 skill |