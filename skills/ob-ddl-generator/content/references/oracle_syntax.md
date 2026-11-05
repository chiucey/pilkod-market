---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: fc7d2570af6ddba37a3b284dd1ea9884
    PropagateID: fc7d2570af6ddba37a3b284dd1ea9884
    ReservedCode1: 3045022100baeb0991596fd00b8de068328d7098438bf1194de836151ea71283c7a154370d02203baa43e3987e87755bc8136caf14407867d674b42524d15ecc56979e1b7fb39d
    ReservedCode2: 3046022100fc7577675c228cb9a1551e74fab3ccdf473b8787faa0b8dcfc46a5710adf34bf022100f3ca6a7dc7a111409597b1db0b4cdce6b8f161e5122a9a57c1ebb2901e78b864
---

# OceanBase for Oracle 语法参考

本文档提供 OceanBase for Oracle 模式下创建表结构的相关语法参考。

## 1. CREATE TABLE 基本语法

```sql
CREATE TABLE table_name (
    column_name datatype [DEFAULT expr] [NOT NULL],
    ...
    [PRIMARY KEY (column_name, ...)],
    [CONSTRAINT constraint_name UNIQUE (column_name, ...)]
);
```

### 参数说明

| 参数 | 说明 |
|------|------|
| table_name | 表名，需使用双引号包裹以保留大小写 |
| column_name | 列名 |
| datatype | 数据类型 |
| DEFAULT expr | 列默认值表达式 |
| NOT NULL | 非空约束 |

## 2. 常用数据类型

### 字符类型

| 数据类型 | 说明 | 语法示例 |
|----------|------|----------|
| VARCHAR2 | 可变长度字符 | `VARCHAR2(255)` |
| CHAR | 定长字符 | `CHAR(1)` |
| CLOB | 大文本对象 | `CLOB` |
| NVARCHAR2 | Unicode 可变长度字符 | `NVARCHAR2(100)` |

### 数值类型

| 数据类型 | 说明 | 语法示例 |
|----------|------|----------|
| NUMBER | 数值 | `NUMBER(10)`、`NUMBER(10,2)` |
| FLOAT | 浮点数 | `FLOAT(53)` |
| BINARY_FLOAT | 32位浮点 | `BINARY_FLOAT` |
| BINARY_DOUBLE | 64位浮点 | `BINARY_DOUBLE` |

### 日期时间类型

| 数据类型 | 说明 | 语法示例 |
|----------|------|----------|
| DATE | 日期时间 | `DATE` |
| TIMESTAMP | 时间戳 | `TIMESTAMP(6)` |
| TIMESTAMP WITH TIME ZONE | 带时区时间戳 | `TIMESTAMP(6) WITH TIME ZONE` |

### 大对象类型

| 数据类型 | 说明 |
|----------|------|
| CLOB | 字符大对象 (最大 128TB) |
| BLOB | 二进制大对象 (最大 128TB) |
| NCLOB | Unicode 大对象 |

## 3. 约束语法

### 3.1 主键约束

```sql
-- 列级定义
column_name datatype PRIMARY KEY

-- 表级定义
PRIMARY KEY (col1, col2, ...)  -- 复合主键
```

### 3.2 唯一约束

```sql
-- 创建唯一索引/约束
CREATE UNIQUE INDEX index_name ON table_name(column_name);
```

### 3.3 检查约束

```sql
ALTER TABLE table_name
ADD CONSTRAINT constraint_name
CHECK (column_name IN ('A', 'B', 'C'));
```

### 3.4 外键约束

```sql
ALTER TABLE child_table
ADD CONSTRAINT fk_name
FOREIGN KEY (column_name)
REFERENCES parent_table(column_name);
```

## 4. 索引语法

### 4.1 创建索引

```sql
-- 普通索引
CREATE INDEX index_name ON table_name(column_name);

-- 唯一索引
CREATE UNIQUE INDEX index_name ON table_name(column_name);

-- 复合索引
CREATE INDEX index_name ON table_name(col1, col2, col3);

-- 函数索引
CREATE INDEX index_name ON table_name(UPPER(column_name));
```

### 4.2 索引命名规范

建议命名格式：
- 普通索引: `idx_表名_字段名`
- 唯一索引: `uk_表名_字段名`
- 主键索引: `pk_表名`

## 5. 注释语法

### 5.1 表注释

```sql
COMMENT ON TABLE table_name IS '表注释内容';
```

### 5.2 列注释

```sql
COMMENT ON COLUMN table_name.column_name IS '列注释内容';
```

## 6. OceanBase 特有注意事项

### 6.1 标识符命名

- 表名、列名、索引名等标识符不区分大小写
- 如需保留大小写，使用双引号包裹：`"TableName"`
- 建议使用双引号包裹以避免与关键字冲突

### 6.2 长度限制

| 对象类型 | 最大长度 |
|----------|----------|
| 表名 | 128 字符 |
| 列名 | 128 字符 |
| 索引名 | 128 字符 |
| 约束名 | 128 字符 |

### 6.3 保留字

避免使用 OceanBase/Oracle 保留字作为标识符。常见保留字包括：
`TABLE, COLUMN, INDEX, SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER` 等

### 6.4 数据类型兼容性

OceanBase for Oracle 与 Oracle 数据库数据类型基本兼容，但仍需注意：
- 不支持 `LONG` 和 `LONG RAW` 类型（已弃用）
- 不支持 `RAW` 类型（建议使用 `BLOB` 替代）
- `TIMESTAMP` 默认精度为 6

## 7. DDL 示例

### 完整建表示例

```sql
-- 员工信息表
CREATE TABLE "HR_EMPLOYEE" (
    "EMP_ID" NUMBER(20) NOT NULL,
    "EMP_CODE" VARCHAR2(50) NOT NULL,
    "EMP_NAME" VARCHAR2(100),
    "EMP_EMAIL" VARCHAR2(100),
    "EMP_SALARY" NUMBER(10,2),
    "DEPT_ID" NUMBER(20),
    "HIRE_DATE" DATE,
    "STATUS" CHAR(1) DEFAULT '1',
    "CREATE_TIME" DATE DEFAULT SYSDATE NOT NULL,
    "UPDATE_TIME" DATE,
    PRIMARY KEY ("EMP_ID", "EMP_CODE")
);

-- 表注释
COMMENT ON TABLE "HR_EMPLOYEE" IS '员工信息表';

-- 字段注释
COMMENT ON COLUMN "HR_EMPLOYEE"."EMP_ID" IS '员工ID';
COMMENT ON COLUMN "HR_EMPLOYEE"."EMP_CODE" IS '员工编号';
COMMENT ON COLUMN "HR_EMPLOYEE"."EMP_NAME" IS '员工姓名';
COMMENT ON COLUMN "HR_EMPLOYEE"."EMP_EMAIL" IS '电子邮箱';
COMMENT ON COLUMN "HR_EMPLOYEE"."EMP_SALARY" IS '薪资';
COMMENT ON COLUMN "HR_EMPLOYEE"."DEPT_ID" IS '部门ID';
COMMENT ON COLUMN "HR_EMPLOYEE"."HIRE_DATE" IS '入职日期';
COMMENT ON COLUMN "HR_EMPLOYEE"."STATUS" IS '状态(0:离职 1:在职)';
COMMENT ON COLUMN "HR_EMPLOYEE"."CREATE_TIME" IS '创建时间';
COMMENT ON COLUMN "HR_EMPLOYEE"."UPDATE_TIME" IS '更新时间';

-- 唯一索引
CREATE UNIQUE INDEX "uk_hr_employee_emp_code" ON "HR_EMPLOYEE"("EMP_CODE");
CREATE UNIQUE INDEX "uk_hr_employee_emp_email" ON "HR_EMPLOYEE"("EMP_EMAIL");

-- 普通索引
CREATE INDEX "idx_hr_employee_dept_id" ON "HR_EMPLOYEE"("DEPT_ID");
CREATE INDEX "idx_hr_employee_hire_date" ON "HR_EMPLOYEE"("HIRE_DATE");
```

## 8. 常见问题

### Q1: 如何查看表结构？

```sql
DESC table_name;
-- 或
SELECT * FROM USER_TAB_COLUMNS WHERE TABLE_NAME = 'TABLE_NAME';
```

### Q2: 如何修改表结构？

```sql
-- 添加列
ALTER TABLE table_name ADD (column_name datatype);

-- 修改列
ALTER TABLE table_name MODIFY (column_name new_datatype);

-- 删除列
ALTER TABLE table_name DROP COLUMN column_name;
```

### Q3: 如何删除表？

```sql
DROP TABLE table_name PURGE;  -- PURGE 立即释放空间
-- 或
DROP TABLE table_name;  -- 放入回收站
```

### Q4: 如何重命名表/列？

```sql
-- 重命名表
RENAME old_table_name TO new_table_name;

-- 重命名列
ALTER TABLE table_name RENAME COLUMN old_col TO new_col;
```
