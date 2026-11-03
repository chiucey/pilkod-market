---
name: sql-for-excel
description: SQL for Excel Workbench - Upload multiple Excel files, convert them to virtual database tables, and perform SQL operations (CRUD). Export query results to Excel. Use when users ask to query Excel with SQL, operate Excel as database, cross-table Excel queries, or export SQL results to Excel.
---

# Excel SQL工作台

## 技能概述

Excel SQL工作台是一个强大的数据处理工具，它将Excel文件转换为虚拟SQL数据库，让用户能够使用熟悉的SQL语法来操作Excel数据。

## 核心功能

### 1. Excel文件上传与管理
- 支持上传多个Excel文件（.xlsx, .xls格式）
- 自动识别每个文件的Sheet页
- 将每个Sheet映射为独立的数据库表
- 表名自动转换为小写并去除空格

### 2. SQL查询支持
- **SELECT查询**: 查询和筛选数据
- **INSERT语句**: 插入新记录
- **UPDATE语句**: 更新现有记录
- **DELETE语句**: 删除记录
- **JOIN操作**: 跨表关联查询
- **聚合函数**: COUNT, SUM, AVG, MIN, MAX等
- **GROUP BY**: 数据分组
- **ORDER BY**: 结果排序

### 3. 结果导出
- 将查询结果导出为Excel文件
- 支持自定义导出文件名
- 保留原始数据类型

## 表名映射规则

上传的Excel文件会按照以下规则转换为表名：

| Excel文件名 | Sheet名 | 生成的表名 |
|------------|---------|-----------|
| sales_data.xlsx | Sheet1 | sales_data_sheet1 |
| users.xlsx | Users | users_users |
| report.xlsx | Summary | report_summary |

## 使用示例

### 示例1: 基本查询
```sql
SELECT * FROM sales_data_sheet1 WHERE amount > 1000
```

### 示例2: 跨表关联查询
```sql
SELECT a.name, b.order_count
FROM users_users a
LEFT JOIN orders_summary b ON a.id = b.user_id
```

### 示例3: 数据统计
```sql
SELECT category, SUM(amount) as total
FROM sales_data_sheet1
GROUP BY category
ORDER BY total DESC
```

### 示例4: 插入数据
```sql
INSERT INTO sales_data_sheet1 (id, name, amount) VALUES (1, 'Product A', 500)
```

### 示例5: 更新数据
```sql
UPDATE sales_data_sheet1 SET amount = 1500 WHERE id = 1
```

### 示例6: 删除数据
```sql
DELETE FROM sales_data_sheet1 WHERE amount < 100
```

## 技术实现

- **后端**: Python + SQLite + Pandas
- **前端**: Streamlit Web界面
- **Excel处理**: openpyxl, pandas
- **SQL引擎**: SQLite3（内存数据库）

## 注意事项

1. 表名会自动转小写，SQL语句中不区分大小写
2. 删除和更新操作需要谨慎使用
3. 支持标准的SQLite语法
4. Excel的第一行会被自动识别为列名
