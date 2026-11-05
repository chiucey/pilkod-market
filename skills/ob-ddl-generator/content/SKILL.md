---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 98801c6ab4900f99178bf3968f58d76b
    PropagateID: 98801c6ab4900f99178bf3968f58d76b
    ReservedCode1: 3045022015df5a5001900d2795cb815b4dc2d56f9c2a74265fda3367840d2c2a7fd5d338022100f88fecdab0a2fb56c8f3a33657e983a3ce56d7e6d81ebe0c6a8cb825b879a956
    ReservedCode2: 30450220723e0500cc93b126fed7d5c65e116b163c1424f43cacd673ba96ffb78597f72d022100a645ca9637e0a3248584c5288013360e8b5653d0c516a9f67221c718aa85c65b
description: OceanBase Oracle DDL 生成器。根据 Excel 表结构文件生成 OceanBase for Oracle 的建表 DDL 语句。当用户要求"帮我创建ob库的DDL"、"生成OceanBase DDL"、"根据表结构生成DDL"、"Excel转DDL"时使用此技能。
name: ob-ddl-generator
---

# OceanBase Oracle DDL 生成器

根据 Excel 表结构描述文件，自动生成 OceanBase for Oracle 数据库的建表 DDL 语句。

## 核心功能

- 读取 Excel 表结构文件，解析字段信息
- 生成符合 OceanBase for Oracle 语法的 CREATE TABLE DDL
- 支持主键、唯一约束、索引的自动创建
- 输出文件保存至 `/workspace/表结构DDL/` 目录

## Excel 列映射规则

| Excel 列 | 内容 | DDL 映射 |
|----------|------|----------|
| B列 | 表英文名称 | 表名 (TABLE_NAME) |
| C列 | 表中文名称 | 表注释 (COMMENT ON TABLE) |
| E列 | 列名 | 字段名 (COLUMN_NAME) |
| F列 | 列注释 | 字段注释 (COMMENT ON COLUMN) |
| G列 | 原始数据类型 | 数据类型 (DATA_TYPE) |
| I列 | 数据长度 | 长度 (如 VARCHAR2(100)) |
| J列 | 数据精度 | 精度 (如 NUMBER(10,2)) |
| K列 | 非空约束 | 值=M/PK → 主键字段 |
| L列 | 唯一性约束 | 值=是 → 唯一约束 |
| M列 | 创建索引 | 值=是 → 创建索引 |

## 执行流程

### 1. 接收文件

接收用户提供的 Excel 文件路径（.xlsx 格式）。

### 2. 读取 Excel

使用 openpyxl 库读取 Excel 文件：
- 第一行：标题行
- 第二行起：字段数据
- 按 B列（表英文名称）分组字段

### 3. 生成 DDL

对于每个表，生成以下 DDL：

```sql
-- 创建表
CREATE TABLE "表名" (
    字段1 数据类型 [DEFAULT 值] [NOT NULL],
    字段2 数据类型,
    ...
    [PRIMARY KEY (字段1, 字段2...)],
    [CONSTRAINT uk_xxx UNIQUE (字段名)],
    ...
);

-- 表注释
COMMENT ON TABLE "表名" IS '表中文名称';

-- 字段注释
COMMENT ON COLUMN "表名"."字段1" IS '字段注释';
COMMENT ON COLUMN "表名"."字段2" IS '字段注释';

-- 索引
CREATE [UNIQUE] INDEX idx_xxx ON "表名"("字段名");
```

### 4. 保存输出

- 创建目录：`/workspace/表结构DDL/`
- 输出文件：与上传文件同名 + `_ob_for_oracle.sql`
- 编码：UTF-8

## 数据类型转换规则

Excel 中的原始数据类型直接使用，DDL 生成时需确保：
- VARCHAR 系列：`VARCHAR2(长度)`
- NUMBER 系列：`NUMBER(总长度, 精度)` 或 `NUMBER(长度)`
- DATE 类型：`DATE`
- CLOB/BLOB：`CLOB` / `BLOB`

## 约束处理

### 主键约束
- K列（非空约束）值为 `M/PK` 的字段作为主键
- 多个主键字段创建为复合主键

### 唯一约束
- L列（唯一性约束）值为 `是` 的字段
- 自动生成唯一约束名：`uk_表名_字段名`

### 索引
- M列（创建索引）值为 `是` 的字段
- 自动生成索引名：`idx_表名_字段名`

## 输出示例

```sql
-- ============================================
-- OceanBase for Oracle 建表脚本
-- 生成时间: 2024-01-15 10:30:00
-- 源文件: 住房公积金表结构.xlsx
-- ============================================

-- ----------------------------
-- 公积金账户信息表
-- ----------------------------
CREATE TABLE "GJJ_ZHHJ" (
    "ZHHJ_ID" NUMBER(20) NOT NULL,
    "ZHHJ_BH" VARCHAR2(50) NOT NULL,
    "ZHHJ_XM" VARCHAR2(100),
    "ZHHJ_SJ" DATE,
    "CREATE_TIME" DATE DEFAULT SYSDATE NOT NULL,
    PRIMARY KEY ("ZHHJ_ID", "ZHHJ_BH")
);

COMMENT ON TABLE "GJJ_ZHHJ" IS '公积金账户信息';

COMMENT ON COLUMN "GJJ_ZHHJ"."ZHHJ_ID" IS '账户汇聚ID';
COMMENT ON COLUMN "GJJ_ZHHJ"."ZHHJ_BH" IS '账户编号';
COMMENT ON COLUMN "GJJ_ZHHJ"."ZHHJ_XM" IS '姓名';
COMMENT ON COLUMN "GJJ_ZHHJ"."ZHHJ_SJ" IS '开户时间';
COMMENT ON COLUMN "GJJ_ZHHJ"."CREATE_TIME" IS '创建时间';

CREATE UNIQUE INDEX "uk_gjj_zhhj_zhhj_bh" ON "GJJ_ZHHJ"("ZHHJ_BH");
CREATE INDEX "idx_gjj_zhhj_zhhj_xm" ON "GJJ_ZHHJ"("ZHHJ_XM");
```

## 错误处理

- 文件不存在：提示用户检查文件路径
- Excel 格式错误：提示缺少必要列
- 空数据：提示 Excel 文件无有效数据
- 编码问题：使用 UTF-8 编码保存

## 依赖

- Python 3.x
- openpyxl 库（用于读取 Excel 文件）
