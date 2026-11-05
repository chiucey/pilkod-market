# 文件审查模板配置指南

本文档详细说明如何配置文件审查模板，以满足不同业务场景的需求。

## 模板配置文件结构

模板配置是一个 JSON 文件，包含以下主要部分：

```json
{
  "template_name": "模板名称",
  "file_type": "excel|csv|json",
  "required_columns": [],
  "nullable_columns": [],
  "column_order": [],
  "data_types": {},
  "value_ranges": {},
  "cross_file_rules": [],
  "null_check_columns": []
}
```

## 字段说明

### 基础配置

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| template_name | string | 是 | 模板名称，用于标识不同的审查配置 |
| file_type | string | 是 | 支持的文件类型：excel、csv、json |
| required_columns | array | 是 | 必填栏位列表，这些栏位不能为空 |
| nullable_columns | array | 否 | 可为空的栏位列表 |
| column_order | array | 否 | 期望的栏位顺序 |

### 数据类型定义

```json
"data_types": {
  "栏位名": "string|number|date|datetime|boolean"
}
```

支持的类型：
- **string**: 字符串类型
- **number**: 数值类型（整数或浮点数）
- **date**: 日期格式（YYYY-MM-DD）
- **datetime**: 日期时间格式
- **boolean**: 布尔值

### 值域约束

```json
"value_ranges": {
  "栏位名": {
    "min": 数值,
    "max": 数值,
    "pattern": "正则表达式",
    "allowed_values": ["值1", "值2"]
  }
}
```

示例：
```json
"value_ranges": {
  "金额": {
    "min": 0,
    "max": 1000000
  },
  "状态": {
    "allowed_values": ["待处理", "处理中", "已完成"]
  },
  "手机号": {
    "pattern": "^1[3-9]\\d{9}$"
  }
}
```

## 跨文件审查规则

跨文件规则用于验证不同文件之间的数据逻辑关系。

### 规则类型

#### 1. 汇总验证规则

验证主表金额与明细表汇总金额的一致性。

```json
{
  "rule_name": "订单金额汇总验证",
  "description": "订单表金额应等于明细表金额之和",
  "master_file": "orders.csv",
  "detail_file": "order_items.csv",
  "master_key": "订单号",
  "detail_key": "订单号",
  "master_field": "订单金额",
  "detail_field": "小计金额",
  "aggregation": "sum",
  "tolerance": 0.01
}
```

参数说明：
- **master_file**: 主表文件名
- **detail_file**: 明细表文件名
- **master_key**: 主表关联键
- **detail_key**: 明细表关联键
- **master_field**: 主表金额栏位
- **detail_field**: 明细表金额栏位
- **aggregation**: 聚合方式（sum/count/avg/max/min）
- **tolerance**: 允许的误差范围

#### 2. 外键关联验证

验证一个文件中的关联键是否在另一个文件中存在。

```json
{
  "rule_name": "客户ID关联验证",
  "description": "订单表中的客户ID必须在客户表中存在",
  "source_file": "orders.csv",
  "target_file": "customers.csv",
  "source_key": "客户ID",
  "target_key": "客户ID",
  "validation_type": "foreign_key",
  "allow_null": false
}
```

#### 3. 业务逻辑规则

自定义业务逻辑验证。

```json
{
  "rule_name": "日期逻辑验证",
  "description": "结束日期必须晚于开始日期",
  "file": "projects.csv",
  "validation_type": "custom",
  "condition": "结束日期 > 开始日期",
  "columns": ["开始日期", "结束日期"]
}
```

## 空值检查配置

### 简单模式

指定必须检查空值的栏位：

```json
"null_check_columns": ["订单号", "客户名称", "金额", "下单日期"]
```

### 高级模式

为不同栏位设置不同的空值标准：

```json
"null_check_rules": {
  "订单号": {
    "check_empty": true,
    "check_whitespace": true,
    "check_null": true
  },
  "金额": {
    "check_empty": true,
    "check_zero": true,
    "min_value": 0.01
  }
}
```

## 完整模板示例

### 订单审查模板

```json
{
  "template_name": "订单数据审查模板",
  "file_type": "excel",
  "required_columns": ["订单号", "客户名称", "客户ID", "订单金额", "下单日期", "订单状态"],
  "nullable_columns": ["备注", "折扣金额", "优惠码"],
  "column_order": ["订单号", "客户名称", "客户ID", "订单金额", "下单日期", "订单状态", "备注"],
  "data_types": {
    "订单号": "string",
    "客户ID": "string",
    "客户名称": "string",
    "订单金额": "number",
    "下单日期": "date",
    "订单状态": "string",
    "折扣金额": "number",
    "备注": "string"
  },
  "value_ranges": {
    "订单金额": {
      "min": 0.01,
      "max": 1000000
    },
    "订单状态": {
      "allowed_values": ["待支付", "已支付", "已完成", "已取消", "已退款"]
    },
    "客户ID": {
      "pattern": "^C\\d{6}$"
    }
  },
  "null_check_columns": ["订单号", "客户ID", "订单金额", "下单日期"],
  "cross_file_rules": [
    {
      "rule_name": "客户ID存在性验证",
      "description": "订单表中的客户ID必须在客户表中存在",
      "source_file": "orders.xlsx",
      "target_file": "customers.xlsx",
      "source_key": "客户ID",
      "target_key": "客户ID",
      "validation_type": "foreign_key",
      "allow_null": false
    }
  ]
}
```

### 财务报表审查模板

```json
{
  "template_name": "财务报表审查模板",
  "file_type": "csv",
  "required_columns": ["科目编码", "科目名称", "期初余额", "本期发生额", "期末余额"],
  "nullable_columns": ["辅助核算", "备注"],
  "data_types": {
    "科目编码": "string",
    "科目名称": "string",
    "期初余额": "number",
    "本期借方": "number",
    "本期贷方": "number",
    "期末余额": "number"
  },
  "value_ranges": {
    "期初余额": {
      "min": -999999999,
      "max": 999999999
    }
  },
  "cross_file_rules": [
    {
      "rule_name": "余额计算验证",
      "description": "期末余额 = 期初余额 + 本期借方 - 本期贷方",
      "file": "financial_report.csv",
      "validation_type": "calculation",
      "formula": "期末余额 = 期初余额 + 本期借方 - 本期贷方",
      "tolerance": 0.01,
      "columns": ["期初余额", "本期借方", "本期贷方", "期末余额"]
    }
  ],
  "null_check_columns": ["科目编码", "科目名称", "期末余额"]
}
```

## 使用建议

1. **分场景配置**: 为不同业务场景创建独立的模板文件
2. **版本管理**: 模板变更时记录版本号和变更说明
3. **默认值**: 为常用配置设置合理的默认值，减少重复配置
4. **规则优先级**: 必填栏位 > 数据类型 > 值域约束 > 业务规则
5. **错误处理**: 为每个规则设置合理的容错范围

## 常见问题

### Q: 如何处理嵌套的 JSON 文件？

A: 使用点号语法访问嵌套字段，例如：`user.profile.name`

### Q: 如何处理多个同名文件？

A: 使用文件路径或添加文件索引，例如：`orders_2024.csv`、`orders_2025.csv`

### Q: 如何验证条件空值？

A: 使用条件规则，例如："仅当状态为已完成时，完工日期才不能为空"
