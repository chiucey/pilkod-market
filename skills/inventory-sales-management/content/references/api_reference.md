---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 9d75775f4476ffbe6fb0cb10d713aca8
    PropagateID: 9d75775f4476ffbe6fb0cb10d713aca8
    ReservedCode1: 3046022100fe2e743772e14329c06862481f13481bbc966d03d83df14dd1a64a3a64e82860022100c3b776c6fc5333b438c07e2f4763239829a940761422e9fee3bc1d510336c9ae
    ReservedCode2: 3044022028c66b128174b26ff31b90b793797a8ebb00c9be27b9a355f8ae83fa84c5006a022020789b75467a12047dd424f3ab4c6706da74e294ddab2b39d8b5f601c4139fd5
---

# 进销存API接口参考

## 一、基础信息

### 1.1 接口规范
- 协议：HTTPS
- 数据格式：JSON
- 字符编码：UTF-8
- 认证方式：Token认证

### 1.2 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### 1.3 错误码
| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

## 二、商品接口

### 2.1 获取商品列表
```
GET /api/products
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| category | string | 否 | 商品分类 |
| keyword | string | 否 | 关键词搜索 |
| is_active | bool | 否 | 是否启用 |

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "list": [
      {
        "product_id": "P001",
        "product_name": "商品A",
        "category": "成品",
        "unit": "件",
        "purchase_price": 100.00,
        "sale_price": 150.00
      }
    ]
  }
}
```

### 2.2 获取商品详情
```
GET /api/products/{product_id}
```

### 2.3 新增商品
```
POST /api/products
```

**请求参数**：
```json
{
  "product_id": "P001",
  "product_name": "商品A",
  "category": "成品",
  "unit": "件",
  "purchase_price": 100.00,
  "sale_price": 150.00,
  "min_stock": 10,
  "remark": "备注"
}
```

### 2.4 更新商品
```
PUT /api/products/{product_id}
```

### 2.5 删除商品
```
DELETE /api/products/{product_id}
```

## 三、采购接口

### 3.1 采购入库
```
POST /api/purchase/in
```

**请求参数**：
```json
{
  "supplier_id": "S001",
  "warehouse_id": "W001",
  "order_date": "2024-01-15",
  "items": [
    {
      "product_id": "P001",
      "quantity": 10,
      "price": 100.00,
      "remark": ""
    }
  ],
  "remark": "备注"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "order_id": "PI-20240115-001",
    "total_amount": 1000.00,
    "items_count": 1
  }
}
```

### 3.2 采购退货
```
POST /api/purchase/return
```

**请求参数**：
```json
{
  "source_order_id": "PI-20240115-001",
  "items": [
    {
      "product_id": "P001",
      "quantity": 2
    }
  ],
  "reason": "质量问题",
  "remark": "备注"
}
```

### 3.3 采购单列表
```
GET /api/purchase/orders
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |
| supplier_id | string | 否 | 供应商 |
| status | string | 否 | 状态 |

### 3.4 采购单详情
```
GET /api/purchase/orders/{order_id}
```

## 四、销售接口

### 4.1 销售出库
```
POST /api/sale/out
```

**请求参数**：
```json
{
  "customer_id": "C001",
  "warehouse_id": "W001",
  "order_date": "2024-01-15",
  "discount_rate": 0.95,
  "items": [
    {
      "product_id": "P001",
      "quantity": 5,
      "price": 150.00,
      "remark": ""
    }
  ],
  "remark": "备注"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "order_id": "SI-20240115-001",
    "total_amount": 712.50,
    "profit": 250.00
  }
}
```

### 4.2 销售退货
```
POST /api/sale/return
```

### 4.3 销售单列表
```
GET /api/sale/orders
```

### 4.4 销售单详情
```
GET /api/sale/orders/{order_id}
```

## 五、库存接口

### 5.1 库存查询
```
GET /api/stock
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| warehouse_id | string | 否 | 仓库 |
| product_id | string | 否 | 商品 |
| warning_only | bool | 否 | 仅预警 |

### 5.2 库存预警
```
GET /api/stock/warnings
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "warnings": [
      {
        "product_id": "P001",
        "product_name": "商品A",
        "warehouse_id": "W001",
        "current_qty": 5,
        "min_stock": 10,
        "shortage": 5
      }
    ]
  }
}
```

### 5.3 库存调拨
```
POST /api/stock/transfer
```

**请求参数**：
```json
{
  "product_id": "P001",
  "from_warehouse_id": "W001",
  "to_warehouse_id": "W002",
  "quantity": 10,
  "remark": "调拨原因"
}
```

### 5.4 库存流水
```
GET /api/stock/flows
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| product_id | string | 否 | 商品 |
| warehouse_id | string | 否 | 仓库 |
| flow_type | string | 否 | 流水类型 |
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |

## 六、盘点接口

### 6.1 创建盘点单
```
POST /api/check/create
```

**请求参数**：
```json
{
  "warehouse_id": "W001",
  "check_date": "2024-01-15",
  "remark": "备注"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "order_id": "CHK-20240115-001",
    "products": [
      {
        "product_id": "P001",
        "product_name": "商品A",
        "book_qty": 100
      }
    ]
  }
}
```

### 6.2 录入盘点数据
```
POST /api/check/input
```

**请求参数**：
```json
{
  "order_id": "CHK-20240115-001",
  "items": [
    {
      "product_id": "P001",
      "check_qty": 98
    }
  ]
}
```

### 6.3 确认盘点
```
POST /api/check/confirm
```

**请求参数**：
```json
{
  "order_id": "CHK-20240115-001",
  "handle_type": "adjust",
  "remark": "备注"
}
```

### 6.4 盘点单列表
```
GET /api/check/orders
```

## 七、报表接口

### 7.1 库存汇总表
```
GET /api/reports/stock_summary
```

### 7.2 采购汇总表
```
GET /api/reports/purchase_summary
```

**请求参数**：
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| group_by | string | 否 | 分组：supplier/month |
| start_date | date | 否 | 开始日期 |
| end_date | date | 否 | 结束日期 |

### 7.3 销售汇总表
```
GET /api/reports/sale_summary
```

### 7.4 毛利分析表
```
GET /api/reports/profit_analysis
```

### 7.5 应收应付报表
```
GET /api/reports/receivable_payable
```
