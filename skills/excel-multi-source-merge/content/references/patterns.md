# Excel 多源合并参考手册

## 常用匹配模式详解

### 1. 一对一匹配 (1:1)

两个文件按唯一键匹配，每条记录只匹配一条。

```
文件A: users.csv (user_id, name, email)
文件B: profiles.csv (user_id, age, city)

结果: 合并后每行包含两个文件的全部信息
```

### 2. 一对多匹配 (1:N)

主表一条记录匹配附表多条记录。

```
主表: orders (order_id, customer_id, date, total)
附表: order_items (item_id, order_id, product, quantity)

结果: 每个订单展开为多行(按商品数量)
```

### 3. 多对多匹配 (N:N)

按多个字段组合进行匹配。

```
文件A: sales (date, product_code, region)
文件B: inventory (date, product_code, warehouse, stock)

匹配键: date + product_code
```

### 4. 条件筛选提取

不进行表间匹配，只按条件从单个文件提取。

```
条件: amount > 10000 AND status = 'pending'
```

## 数据转换规则

### 类型转换

| 原始类型 | 目标类型 | 代码 |
|---------|---------|------|
| 字符串数字 | 数值 | `df['col'] = pd.to_numeric(df['col'])` |
| 日期字符串 | 日期 | `df['date'] = pd.to_datetime(df['date'])` |
| 数值 | 字符串 | `df['col'] = df['col'].astype(str)` |

### 计算字段

```python
# 合计计算
df['total'] = df['quantity'] * df['price']

# 百分比计算
df['percentage'] = df['value'] / df['total'] * 100

# 日期差计算
df['days'] = (df['end_date'] - df['start_date']).days
```

### 数据清洗

```python
# 去除空格
df['name'] = df['name'].str.strip()

# 统一大小写
df['code'] = df['code'].str.upper()

# 填充空值
df['amount'].fillna(0, inplace=True)

# 删除重复行
df.drop_duplicates(inplace=True)
```

## 输出格式选项

### 简单表格
- 默认格式
- 列名在第一行
- 数据紧凑排列

### 格式化表格
- 冻结首行
- 自动列宽
- 交替行颜色
- 数字格式化(千分位)

### 多Sheet输出
- Sheet1: 合并主数据
- Sheet2: 汇总统计
- Sheet3: 异常数据记录

## 错误处理

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| KeyError | 列名不存在 | 检查列名大小写，使用strip()清理 |
| MergeError | 匹配键类型不一致 | 统一数据类型后合并 |
| FileNotFoundError | 文件路径错误 | 使用绝对路径或用户上传文件 |
| ValueError | 空值或格式错误 | 使用pd.to_numeric(errors='coerce') |

### 空值处理策略

1. **保留**: 在输出中用空字符串或N/A表示
2. **删除**: 删除包含空值的行 `df.dropna()`
3. **填充**: 用指定值填充 `df.fillna(value)`
4. **前向填充**: 用上一行值填充 `df.fillna(method='ffill')`
