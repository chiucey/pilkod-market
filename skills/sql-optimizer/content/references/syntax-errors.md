# SQL常见语法错误速查

## MySQL常见错误
- 反引号使用：\`field_name\`（仅MySQL）
- 日期字面量：`'2024-01-01'` 或 `DATE '2024-01-01'`
- 字符串拼接：`CONCAT()` 而非 `||`
- 自动类型转换：`LIMIT 10, 20` vs `LIMIT 10 OFFSET 20`

## PostgreSQL常见错误
- 双引号用于标识符：`"field_name"`
- 字符串拼接：`||` 或 `CONCAT()`
- LIMIT/OFFSET：`LIMIT 10 OFFSET 20`
- JSON操作符：`->` `->>` `#>`

## Oracle常见错误
- 字符串用单引号
- 空字符串=NULL
- ROWNUM分页技巧
- NVL vs COALESCE

## 通用错误模式

### 1. 引号混淆
```sql
-- 错误
SELECT * FROM users WHERE name = "John";

-- 正确（MySQL）
SELECT * FROM users WHERE name = 'John';
```

### 2. 缺少分隔符
```sql
-- 错误：字段列表未分隔
SELECT id name age FROM users;

-- 正确
SELECT id, name, age FROM users;
```

### 3. 括号不匹配
```sql
-- 错误
SELECT * FROM users WHERE id IN (1, 2, 3;

-- 正确
SELECT * FROM users WHERE id IN (1, 2, 3);
```

### 4. 关键字拼写错误
- `SELECE` → `SELECT`
- `FORM` → `FROM`
- `WHEER` → `WHERE`
- `GROUPBY` → `GROUP BY`

### 5. 别名引用错误
```sql
-- 错误：不能在WHERE中使用别名
SELECT id AS user_id FROM users WHERE user_id > 100;

-- 正确：使用原字段或包一层
SELECT id AS user_id FROM users WHERE id > 100;
```

### 6. 聚合函数使用错误
```sql
-- 错误：SELECT聚合和非聚合混用无GROUP BY
SELECT name, COUNT(*) FROM users;

-- 正确
SELECT name, COUNT(*) FROM users GROUP BY name;
```
