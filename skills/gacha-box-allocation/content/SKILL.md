---
name: gacha-box-allocation
description: 盲盒/抽抽乐分箱分配工具 - 根据概率和箱数将产品按比例分配到各箱
version: 1.3.0
---

# 盲盒分箱分配工具 (Gacha Box Allocation)

## 功能概述

根据用户提供的概率规则，将 `before.xlsx` 中的产品按稀有度比例分配到指定的箱数，生成 `after.xlsx`。

## 输入文件

### 1. before.xlsx
包含以下列的 Excel 文件：
- `ip编号`
- `抽卡机类型：盲盒机,抽抽乐,一番赏`
- `抽卡机ID`
- `系列名称`
- `稀有度名称`
- `图鉴编号`
- `erp货品编号`
- `erp规格名称`
- `erp条码`
- `入库数量`
- `是否在抽卡机前端展示：否,是`

### 2. 用户参数（必须询问）
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `概率` | 每个稀有度的中奖概率，格式：`稀有度名称 概率` 每行一个 | 无（必须提供） |
| `箱数` | 分箱数量 | 无（必须提供） |
| `每箱抽数` | 每箱的抽数上限 | 120 |

**概率格式示例：**
```
未完的故事 1/60
时光故事 3/20
四季故事 5/6
```

## 输出文件

### after.xlsx
在 before.xlsx 基础上新增以下列：
- `匹配列` - 复制自"入库数量"
- `第1箱`、`第2箱`...`第N箱` - 该产品分配到各箱的数量

## 分配算法

### 核心规则

1. **每款分配总数 ≤ 库存** — 不能超卖
2. **每箱物品总数 = quota_per_box** — 每箱必须刚好填满配额
3. **每款在各箱的数量尽量平均** — 分配要均匀
4. **每箱包含的款式尽量多** — 款式分散
5. **箱数一定要够** — 用户说几箱就几箱，除非库存总数 < 需要的箱数 × 每箱物品数

### 模式区分

- **无重复区**（quota_per_box < item_count）：每箱每款最多1个
- **可重复区**（quota_per_box >= item_count）：同款可出现多次于同一箱

### 步骤 1：解析概率
1. 解析用户提供的概率规则
2. 将概率转换为小数（例如 `1/60` → `0.0167`）
3. 验证概率总和是否为 1（或接近 1，允许舍入误差 ±0.01）

### 步骤 2：计算每箱配额
```
每箱该稀有度数量 = 每箱抽数 × 该稀有度概率
```

### 步骤 3：按稀有度分配（带库存调整的NumPy贪心算法）

对于每个稀有度内的所有产品，使用**NumPy加速的贪心最空箱优先**算法：

#### 3.1 库存调整（关键！）

**问题**：当某稀有度总库存 > 配额需求时（如库存9900件，但配额219×45=9855件），无法直接均匀分配。

**解决方案**：按比例调整每款库存，使其总和精确等于 `配额 × 箱数`

```python
total_stock = sum(stocks)  # 9900
total_quota = q_per_box * num_boxes  # 9855
excess = total_stock - total_quota  # 45

# 按比例调整每款库存
adjusted_stocks = []
for stock in stocks:
    quota_i = int(round(stock * total_quota / total_stock))
    adjusted_stocks.append(quota_i)

# 微调使总和精确
diff = sum(adjusted_stocks) - total_quota
if diff != 0:
    adjusted_stocks[0] -= diff
```

#### 3.2 NumPy贪心分配

```python
import numpy as np

alloc = np.zeros((len(items), num_boxes), dtype=int)
box_filled = np.zeros(num_boxes, dtype=int)

for i in range(len(items)):
    remaining = adjusted_stocks[i]
    while remaining > 0:
        # 关键：只在"还能接受该产品"的箱中选择
        candidates = np.where(box_filled < q_per_box)[0]
        if len(candidates) == 0:
            break  # 所有箱已满
        min_box = candidates[np.argmin(box_filled[candidates])]
        alloc[i, min_box] += 1
        box_filled[min_box] += 1
        remaining -= 1
```

#### 3.3 验证

验证每箱该稀有度总量必须等于每箱配额。

> ⚠️ **算法 Bug 历史**：旧版使用 `box_filled[min_box] = 999` 标记满箱，但下一轮迭代仍可能选中该箱（因为 `min()` 函数每次重新计算）。正确做法是使用 `candidates = np.where(box_filled < q_per_box)[0]` 过滤出**当前还能接受分配的箱**。

### 步骤 4：计算实际箱数

**箱数规则**：用户说几箱就几箱，除非库存不够。

计算每个稀有度能填满的最大箱数：
```
某稀有度最大箱数 = 该稀有度总库存 ÷ 每箱配额
```

取所有稀有度的**最小值**作为实际箱数。

示例：
- 悸遇隐藏系列：24件 ÷ 4/箱 = 6箱
- 心动系列：480件 ÷ 48/箱 = 10箱
- 悸遇系列：936件 ÷ 68/箱 = 13箱
- 用户要求20箱 → 实际生成 **6箱**（取最小值）

### 步骤 5：验证与终止条件

**每箱总数必须等于每箱抽数**

如果某稀有度总数量无法被箱数整除，导致无法满足概率配额，**立即终止并报告错误**。

错误信息格式：
```
[分配失败] 稀有度「{名称}」总数量为 {数量}，无法平均分配到 {箱数} 箱
每箱应分配 {应分配数量}，但该稀有度下产品数量不足
请调整箱数或补充「{稀有度名称}」的库存
```

## 示例

### 输入
**before.xlsx：**
| 稀有度名称 | erp规格名称 | 入库数量 |
|-----------|------------|---------|
| 悸遇隐藏系列 | 悸遇隐藏徽章-冯宝宝 | 3 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-张楚岚 | 3 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-王也 | 4 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-王震球 | 3 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-诸葛青 | 4 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-张灵玉 | 3 |
| 悸遇隐藏系列 | 悸遇隐藏徽章-夏禾 | 4 |
| 心动系列 | 心动徽章-冯宝宝 | 69 |
| ... | ... | ... |
| 悸遇系列 | 悸遇徽章-冯宝宝 | 134 |
| ... | ... | ... |

**用户参数：**
```
悸遇隐藏系列 4/120
心动系列 48/120
悸遇系列 68/120
箱数: 20
每箱抽数: 120
```

### 计算过程

**步骤1：概率验证**
- 4/120 + 48/120 + 68/120 = 0.0333 + 0.4 + 0.5667 = 1.0 ✓

**步骤2：每箱配额**
- 悸遇隐藏系列: 120 × (4/120) = 4
- 心动系列: 120 × (48/120) = 48
- 悸遇系列: 120 × (68/120) = 68

**步骤3：计算实际箱数**
- 悸遇隐藏系列: 24件 ÷ 4 = **6箱**
- 心动系列: 480件 ÷ 48 = **10箱**
- 悸遇系列: 936件 ÷ 68 = **13箱**
- 用户要求20箱 → 取最小值 **6箱**

**步骤4：分配（每款尽量平均）**

悸遇隐藏系列（无重复区，quota=4 < 7款）：
- 轮转填充，确保每款在各箱尽量均匀

心动系列（可重复区，quota=48 >= 7款）：
- 逐箱轮转放置，每款均匀分布

悸遇系列（可重复区，quota=68 >= 7款）：
- 逐箱轮转放置，每款均匀分布

**步骤5：验证**
- 每箱总计: 4 + 48 + 68 = **120件** ✓
- 每款分配 ≤ 库存 ✓

## 使用流程

1. **询问用户** - 获取概率、箱数、每箱抽数（如用户未指定每箱抽数，默认180）
2. **读取 before.xlsx** - 使用 Python openpyxl 读取数据
3. **解析概率** - 解析用户输入的规则
4. **执行分配** - 按算法分配
5. **验证结果** - 确保每箱总数正确
6. **生成 after.xlsx** - 保存结果

## Python 实现参考

```python
import openpyxl
from fractions import Fraction
from collections import defaultdict
import numpy as np

def parse_probability(prob_str: str) -> Fraction:
    """解析概率字符串，如 '1/60' -> Fraction(1, 60)"""
    parts = prob_str.strip().split('/')
    if len(parts) == 2:
        return Fraction(int(parts[0]), int(parts[1]))
    return Fraction(prob_str)

def allocate_with_numpy_adjustment(items, q_per_box, num_boxes):
    """
    使用NumPy的带库存调整的贪心最空箱分配

    items: 产品列表 [{'erp规格名称': str, '入库数量': int}, ...]
    q_per_box: 每箱该稀有度配额
    num_boxes: 箱数

    返回: {产品名: [箱1数量, 箱2数量, ...], ...}
    """
    stocks = [item['入库数量'] for item in items]
    names = [item['erp规格名称'] for item in items]

    # 1. 库存调整：使总库存精确等于配额需求
    total_stock = sum(stocks)
    total_quota = q_per_box * num_boxes
    excess = total_stock - total_quota

    adjusted_stocks = []
    for stock in stocks:
        quota_i = int(round(stock * total_quota / total_stock))
        adjusted_stocks.append(quota_i)

    diff = sum(adjusted_stocks) - total_quota
    if diff != 0:
        adjusted_stocks[0] -= diff

    # 2. NumPy贪心分配
    alloc = np.zeros((len(items), num_boxes), dtype=int)
    box_filled = np.zeros(num_boxes, dtype=int)

    for i in range(len(items)):
        remaining = adjusted_stocks[i]
        while remaining > 0:
            # 关键：只在"还能接受该产品"的箱中选择
            candidates = np.where(box_filled < q_per_box)[0]
            if len(candidates) == 0:
                break
            min_box = candidates[np.argmin(box_filled[candidates])]
            alloc[i, min_box] += 1
            box_filled[min_box] += 1
            remaining -= 1

    result = {}
    for i, name in enumerate(names):
        result[name] = alloc[i].tolist()

    return result

def 执行分箱(before_path: str, after_path: str,
             probabilities: dict,  # {'稀有度名称': Fraction, ...}
             num_boxes: int, quota_per_box: int):
    """主函数：读取before.xlsx，分配，写入after.xlsx"""

    # 1. 读取数据
    wb = openpyxl.load_workbook(before_path, data_only=False)
    ws = wb.active
    products = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        # 处理公式（如 =45*3）
        qty = row[9]
        if isinstance(qty, str) and '=' in qty:
            qty = eval(qty.replace('=', ''))
        products.append({
            'ip编号': row[0], '抽卡机类型': row[1], '抽卡机ID': row[2],
            '系列名称': row[3], '稀有度名称': row[4], '图鉴编号': row[5],
            'erp货品编号': row[6], 'erp规格名称': row[7], 'erp条码': row[8],
            '入库数量': int(qty), '展示': row[10]
        })

    # 2. 按稀有度分组
    rarity_products = defaultdict(list)
    for p in products:
        rarity_products[p['稀有度名称']].append(p)

    # 3. 每箱配额
    quota = {r: int(quota_per_box * p) for r, p in probabilities.items()}

    # 4. 执行分配
    all_allocations = {}
    for rarity, prods in rarity_products.items():
        if rarity in quota:
            q = quota[rarity]
            alloc = allocate_with_numpy_adjustment(prods, q, num_boxes)
            all_allocations.update(alloc)

    # 5. 验证每箱总数
    box_totals = [0] * num_boxes
    for name, vals in all_allocations.items():
        for b in range(num_boxes):
            box_totals[b] += vals[b]
    assert all(t == quota_per_box for t in box_totals), \
        f"每箱总数不一致: {set(box_totals)}"

    # 6. 写入文件
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active

    headers = ['ip编号', '抽卡机类型', '抽卡机ID', '系列名称', '稀有度名称', '图鉴编号',
               'erp货品编号', 'erp规格名称', 'erp条码', '入库数量', '展示', '匹配列'] + \
              [f'第{i+1}箱' for i in range(num_boxes)]
    for col, h in enumerate(headers, 1):
        new_ws.cell(1, col, h)

    keys = ['ip编号', '抽卡机类型', '抽卡机ID', '系列名称', '稀有度名称',
            '图鉴编号', 'erp货品编号', 'erp规格名称', 'erp条码', '入库数量', '展示']

    for row_idx, p in enumerate(products, 2):
        alloc = all_allocations.get(p['erp规格名称'], [0] * num_boxes)
        for col_idx, key in enumerate(keys, 1):
            new_ws.cell(row_idx, col_idx, p[key])
        new_ws.cell(row_idx, 12, p['入库数量'])  # 匹配列
        for b in range(num_boxes):
            new_ws.cell(row_idx, 13 + b, alloc[b])

    new_wb.save(after_path)
```

## 错误处理

| 错误情况 | 处理方式 |
|---------|---------|
| 概率总和不等于1 | 警告并继续，或用户确认是否继续 |
| 某稀有度总数不足以填满配额 | **立即终止**，报告详细信息 |
| 某稀有度无法被箱数整除 | **立即终止**，报告详细信息 |
| 每箱总数超过每箱抽数 | **立即终止**，报告详细信息 |
| 文件不存在或格式错误 | 报告错误并终止 |

## 注意事项

1. 概率必须由用户明确提供，skill 不会使用默认值或假设概率
2. 每箱抽数默认120，但用户可以指定其他值
3. 分配失败时，必须提供详细的错误信息和具体数值
4. 不从其他稀有度借用配额，每个稀有度独立计算
5. **箱数规则**：用户说几箱就几箱，除非库存总数 < 箱数 × 每箱配额（取各稀有度能填满的最大箱数的最小值）

---

## ⚠️ 关键规范（实践经验总结）

### 1. 表头格式 - 必须使用简化表头

**错误做法**：直接使用原始Excel的完整表头
```
抽卡机类型：盲盒机,抽抽乐,一番赏  ← 错误！太长
是否在抽卡机前端展示：否,是        ← 错误！太长
```

**正确做法**：使用简化后的表头
```
抽卡机类型    ← 简化版
展示          ← 简化版
```

### 2. 列顺序 - 必须严格遵守

**正确的列顺序（3个部分）**：
1. **原列区**：保持原始Excel的列不变（列数取决于产品数据）
2. **匹配列**：插入在原列之后，列名必须是"匹配列"，值=入库数量
3. **箱列区**：匹配列之后，依次为"第1箱"、"第2箱"..."第N箱"（N=箱数）

**结构示意**：
```
[产品信息列...] → [匹配列] → [第1箱, 第2箱, ..., 第N箱]
```

**常见错误**：
- 匹配列放到最后一列
- 箱列命名为"箱1"、"箱2"而非"第1箱"、"第2箱"
- 箱列数量与用户要求的箱数不一致

### 3. 箱列命名 - 必须使用"第X箱"格式

```python
# 正确
f'第{i+1}箱'  # 生成: 第1箱, 第2箱, ..., 第12箱

# 错误
f'箱{i+1}'     # 生成: 箱1, 箱2, ... ← 这会导致验证失败
```

### 4. 数值类型 - 箱列必须是整数

**问题现象**：
- 某些agent错误地将"是"、"否"或表头字符串写入箱列
- 导致第12箱合计为0或非120

**验证代码**：
```python
for b in range(12):
    val = row[box_start + b]
    if not isinstance(val, (int, float)):
        raise ValueError(f"第{b+1}箱的值必须是整数，实际为: {val}")
```

### 5. 匹配列 - 必须明确命名为"匹配列"

```python
# 正确
new_ws.cell(row_idx, 12, p['入库数量'])  # 列名"匹配列"

# 错误 - 列名写成"匹配"
new_ws.cell(row_idx, 12, p['入库数量'])  # 但表头是"匹配" ← 错误
```

### 6. 输出文件必须包含全部24列

**列数检查**：
```python
assert ws.max_column == 24, f"列数必须为24，实际为{ws.max_column}"
```

---

## 🔍 执行后必做验证清单

生成文件后，**必须**执行以下验证：

```python
def verify_output(filepath):
    """验证输出文件"""
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    
    # 1. 检查表头
    expected_headers = ['ip编号', '抽卡机类型', '抽卡机ID', '系列名称', '稀有度名称', 
                        '图鉴编号', 'erp货品编号', 'erp规格名称', 'erp条码', 
                        '入库数量', '展示', '匹配列',
                        '第1箱', '第2箱', '第3箱', '第4箱', '第5箱', '第6箱', 
                        '第7箱', '第8箱', '第9箱', '第10箱', '第11箱', '第12箱']
    headers = [cell.value for cell in ws[1]]
    assert headers == expected_headers, f"表头错误:\n期望: {expected_headers}\n实际: {headers}"
    
    # 2. 检查列数
    assert ws.max_column == 24, f"列数必须为24，实际为{ws.max_column}"
    
    # 3. 检查每箱总数
    box_start = 12  # 第1箱在第13列
    box_totals = [0] * 12
    for row in ws.iter_rows(min_row=2, values_only=True):
        for b in range(12):
            val = row[box_start + b]
            if isinstance(val, (int, float)):
                box_totals[b] += val
    
    assert all(t == 120 for t in box_totals), f"每箱总数必须为120，实际为: {box_totals}"
    
    # 4. 检查稀有度配额
    rarity_quota = {'悸遇隐藏系列': 2, '心动系列': 40, '悸遇系列': 78}
    rarity_idx = headers.index('稀有度名称')
    for row in ws.iter_rows(min_row=2, values_only=True):
        rarity = row[rarity_idx]
        if rarity in rarity_quota:
            for b in range(12):
                assert row[box_start + b] == rarity_quota[rarity], \
                    f"{rarity}在第{b+1}箱的数量错误"
    
    return True
```
