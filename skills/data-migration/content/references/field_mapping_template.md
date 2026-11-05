# 字段映射模板参考

## 常见映射场景

### 1. 数据库字段重命名

```python
# 简单字段重命名
mapping = {
    "old_name": "new_name",
    "customer_id": "user_id",
    "create_time": "created_at"
}

# 使用 pandas 重命名
df = df.rename(columns=mapping)
```

### 2. 数据类型转换

```python
# 日期格式转换
df["date_str"] = pd.to_datetime(df["date_str"], format="%Y-%m-%d")
df["date_str"] = df["date_str"].dt.strftime("%Y/%m/%d")

# 数值类型转换
df["price"] = df["price"].astype(float)
df["quantity"] = df["quantity"].astype(int)

# 字符串处理
df["phone"] = df["phone"].str.replace("-", "")
df["name"] = df["name"].str.strip().str.upper()
```

### 3. 枚举值映射

```python
status_mapping = {
    "PENDING": 0,
    "PROCESSING": 1,
    "COMPLETED": 2,
    "FAILED": -1
}

df["status_code"] = df["status"].map(status_mapping)
```

### 4. JSON 字段展开

```python
# 展开嵌套 JSON
import json

df["address_json"] = df["address_json"].apply(json.loads)
df = pd.concat([
    df.drop(["address_json"], axis=1),
    df["address_json"].apply(pd.Series)
], axis=1)
```

### 5. 多字段合并

```python
# 合并姓和名
df["full_name"] = df["first_name"] + " " + df["last_name"]

# 日期时间组合
df["datetime"] = pd.to_datetime(
    df["date"].astype(str) + " " + df["time"].astype(str),
    format="%Y-%m-%d %H:%M:%S"
)
```

### 6. 条件映射

```python
# 根据条件设置值
df["category"] = df["amount"].apply(
    lambda x: "高" if x > 1000 else ("中" if x > 500 else "低")
)

# 使用 np.where
import numpy as np
df["vip_level"] = np.where(df["total_amount"] > 10000, "VIP", "普通")
```

## 常用数据库字段映射规则

### MySQL → PostgreSQL

| MySQL 类型 | PostgreSQL 类型 | 转换说明 |
|-----------|----------------|---------|
| TINYINT | SMALLINT | 微小整数 |
| INT | INTEGER | 标准整数 |
| BIGINT | BIGINT | 大整数 |
| VARCHAR(n) | VARCHAR(n) | 可变字符串 |
| TEXT | TEXT | 长文本 |
| DATETIME | TIMESTAMP | 日期时间 |
| BOOL | BOOLEAN | 布尔值 |

### Oracle → MySQL

| Oracle 类型 | MySQL 类型 | 转换说明 |
|------------|-----------|---------|
| NUMBER(p,s) | DECIMAL(p,s) | 数值 |
| VARCHAR2(n) | VARCHAR(n) | 可变字符串 |
| CLOB | LONGTEXT | 大文本 |
| DATE | DATETIME | 日期时间 |
| TIMESTAMP | TIMESTAMP | 时间戳 |

## 常见问题处理

### 1. 编码问题

```python
# 读取时指定编码
df = pd.read_csv("file.csv", encoding="gbk")
df = pd.read_csv("file.csv", encoding="latin1")

# 写入时指定编码
df.to_csv("output.csv", encoding="utf-8-sig")  # UTF-8 with BOM
```

### 2. 日期格式差异

```python
# 中国日期格式: 2024年01月15日
df["date_cn"] = pd.to_datetime(
    df["date_cn"].str.replace("年", "-").str.replace("月", "-").str.replace("日", "")
)

# 统一转换为标准格式
df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
```

### 3. 空值处理

```python
# 数值列空值填充
df["age"] = df["age"].fillna(0)
df["price"] = df["price"].fillna(df["price"].median())

# 字符串列空值填充
df["name"] = df["name"].fillna("未知")
df["remark"] = df["remark"].fillna("")

# 删除空值行
df = df.dropna(subset=["required_field"])
```
