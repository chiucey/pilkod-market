---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: cd620c99600b11fc2a72960d08eba749
    PropagateID: cd620c99600b11fc2a72960d08eba749
    ReservedCode1: 3045022100bea0cdcd4f5c3cc4676119df57fb2df9052f8be131ab7c95207e8d3ec3ecafee0220727a4bd021a38070bb2792d5e2617e3c877110d838ab10ddbc521db8054373d6
    ReservedCode2: 3045022100a6da6dd7b3fc1bea48eccd8cd3e591916e1632159f00d04c4c8d2ceaf7b1f893022027e8a4fc82058a1335b5d7dbd520ed8125f537d42e1365d218466284253a5b50
---

# 进销存数据结构参考

## 一、数据库表结构

### 1.1 商品主表 (products)
```sql
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,      -- 商品编码
    product_name VARCHAR(200) NOT NULL,     -- 商品名称
    category VARCHAR(100),                  -- 商品分类
    unit VARCHAR(20),                       -- 计量单位
    purchase_price DECIMAL(12,2),          -- 采购单价
    sale_price DECIMAL(12,2),               -- 销售单价
    cost_price DECIMAL(12,2),               -- 成本单价
    supplier_id VARCHAR(50),               -- 默认供应商
    barcode VARCHAR(50),                   -- 条码
    spec VARCHAR(200),                     -- 规格型号
    color VARCHAR(50),                     -- 颜色
    size VARCHAR(50),                      -- 尺寸
    weight DECIMAL(10,3),                  -- 重量
    min_stock INT DEFAULT 0,              -- 最低库存
    max_stock INT DEFAULT 0,              -- 最高库存
    is_active BOOLEAN DEFAULT TRUE,        -- 是否启用
    remark TEXT,                           -- 备注
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.2 仓库表 (warehouses)
```sql
CREATE TABLE warehouses (
    warehouse_id VARCHAR(50) PRIMARY KEY,  -- 仓库编码
    warehouse_name VARCHAR(200) NOT NULL,   -- 仓库名称
    warehouse_type VARCHAR(50),             -- 仓库类型
    address VARCHAR(500),                  -- 地址
    manager VARCHAR(100),                   -- 负责人
    contact VARCHAR(100),                   -- 联系电话
    is_default BOOLEAN DEFAULT FALSE,       -- 是否默认
    is_active BOOLEAN DEFAULT TRUE,         -- 是否启用
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.3 库存表 (stock)
```sql
CREATE TABLE stock (
    id INT PRIMARY KEY AUTO_INCREMENT,
    product_id VARCHAR(50) NOT NULL,       -- 商品编码
    warehouse_id VARCHAR(50) NOT NULL,    -- 仓库编码
    quantity INT DEFAULT 0,                -- 当前库存
    frozen_quantity INT DEFAULT 0,         -- 冻结库存
    available_quantity INT GENERATED ALWAYS AS (quantity - frozen_quantity) STORED,
    last_in_date DATETIME,                 -- 最后入库日期
    last_out_date DATETIME,                -- 最后出库日期
    update_time DATETIME DEFAULT NOW(),
    UNIQUE KEY uk_product_warehouse (product_id, warehouse_id)
);
```

### 1.4 供应商表 (suppliers)
```sql
CREATE TABLE suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,    -- 供应商编码
    supplier_name VARCHAR(200) NOT NULL,   -- 供应商名称
    contact VARCHAR(100),                  -- 联系人
    phone VARCHAR(50),                     -- 电话
    mobile VARCHAR(50),                    -- 手机
    fax VARCHAR(50),                       -- 传真
    email VARCHAR(100),                    -- 邮箱
    address VARCHAR(500),                  -- 地址
    bank VARCHAR(200),                     -- 开户银行
    account_no VARCHAR(100),               -- 银行账号
    tax_no VARCHAR(100),                   -- 税号
    credit_limit DECIMAL(12,2),            -- 信用额度
    payment_terms VARCHAR(100),            -- 付款条件
    is_active BOOLEAN DEFAULT TRUE,
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.5 客户表 (customers)
```sql
CREATE TABLE customers (
    customer_id VARCHAR(50) PRIMARY KEY,   -- 客户编码
    customer_name VARCHAR(200) NOT NULL,    -- 客户名称
    customer_type VARCHAR(50),             -- 客户类型
    contact VARCHAR(100),                  -- 联系人
    phone VARCHAR(50),                     -- 电话
    mobile VARCHAR(50),                    -- 手机
    email VARCHAR(100),                    -- 邮箱
    address VARCHAR(500),                  -- 地址
    bank VARCHAR(200),                     -- 开户银行
    account_no VARCHAR(100),               -- 银行账号
    tax_no VARCHAR(100),                   -- 税号
    credit_limit DECIMAL(12,2),            -- 信用额度
    receivable DECIMAL(12,2) DEFAULT 0,    -- 应收余额
    is_active BOOLEAN DEFAULT TRUE,
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.6 采购单主表 (purchase_orders)
```sql
CREATE TABLE purchase_orders (
    order_id VARCHAR(50) PRIMARY KEY,       -- 采购单号
    order_type VARCHAR(20),                -- 单据类型
    supplier_id VARCHAR(50),               -- 供应商
    order_date DATE NOT NULL,              -- 单据日期
    total_amount DECIMAL(12,2),           -- 单据金额
    paid_amount DECIMAL(12,2) DEFAULT 0,   -- 已付款
    status VARCHAR(20) DEFAULT 'draft',   -- 状态
    operator VARCHAR(100),                -- 操作员
    approve_by VARCHAR(100),              -- 审核人
    approve_time DATETIME,                 -- 审核时间
    warehouse_id VARCHAR(50),              -- 入库仓库
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.7 采购单明细表 (purchase_order_items)
```sql
CREATE TABLE purchase_order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) NOT NULL,         -- 采购单号
    line_no INT,                           -- 行号
    product_id VARCHAR(50) NOT NULL,       -- 商品编码
    product_name VARCHAR(200),             -- 商品名称
    unit VARCHAR(20),                      -- 单位
    quantity INT,                           -- 数量
    price DECIMAL(12,2),                   -- 单价
    amount DECIMAL(12,2),                  -- 金额
    tax_rate DECIMAL(5,2),                 -- 税率
    tax_amount DECIMAL(12,2),              -- 税额
    delivered_qty INT DEFAULT 0,           -- 已交货数量
    remark TEXT,
    FOREIGN KEY (order_id) REFERENCES purchase_orders(order_id)
);
```

### 1.8 销售单主表 (sale_orders)
```sql
CREATE TABLE sale_orders (
    order_id VARCHAR(50) PRIMARY KEY,       -- 销售单号
    order_type VARCHAR(20),                 -- 单据类型
    customer_id VARCHAR(50),               -- 客户
    order_date DATE NOT NULL,              -- 单据日期
    total_amount DECIMAL(12,2),           -- 单据金额
    received_amount DECIMAL(12,2) DEFAULT 0, -- 已收款
    discount_amount DECIMAL(12,2) DEFAULT 0, -- 折扣
    status VARCHAR(20) DEFAULT 'draft',   -- 状态
    operator VARCHAR(100),                -- 操作员
    approve_by VARCHAR(100),              -- 审核人
    approve_time DATETIME,                 -- 审核时间
    warehouse_id VARCHAR(50),              -- 出库仓库
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.9 销售单明细表 (sale_order_items)
```sql
CREATE TABLE sale_order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) NOT NULL,          -- 销售单号
    line_no INT,                            -- 行号
    product_id VARCHAR(50) NOT NULL,        -- 商品编码
    product_name VARCHAR(200),              -- 商品名称
    unit VARCHAR(20),                       -- 单位
    quantity INT,                           -- 数量
    price DECIMAL(12,2),                    -- 单价
    amount DECIMAL(12,2),                   -- 金额
    tax_rate DECIMAL(5,2),                  -- 税率
    tax_amount DECIMAL(12,2),              -- 税额
    delivered_qty INT DEFAULT 0,           -- 已交货数量
    remark TEXT,
    FOREIGN KEY (order_id) REFERENCES sale_orders(order_id)
);
```

### 1.10 库存流水表 (stock_flow)
```sql
CREATE TABLE stock_flow (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flow_no VARCHAR(50) NOT NULL,          -- 流水号
    product_id VARCHAR(50) NOT NULL,       -- 商品编码
    warehouse_id VARCHAR(50) NOT NULL,    -- 仓库编码
    flow_type VARCHAR(20),                -- 流水类型
    bill_type VARCHAR(20),                -- 单据类型
    bill_no VARCHAR(50),                  -- 单据编号
    in_quantity INT DEFAULT 0,            -- 入库数量
    out_quantity INT DEFAULT 0,           -- 出库数量
    before_qty INT,                        -- 变动前数量
    after_qty INT,                         -- 变动后数量
    price DECIMAL(12,2),                  -- 单价
    amount DECIMAL(12,2),                 -- 金额
    operator VARCHAR(100),                -- 操作员
    operate_time DATETIME DEFAULT NOW(),
    remark TEXT,
    INDEX idx_product (product_id),
    INDEX idx_warehouse (warehouse_id),
    INDEX idx_operate_time (operate_time)
);
```

### 1.11 盘点单表 (check_orders)
```sql
CREATE TABLE check_orders (
    order_id VARCHAR(50) PRIMARY KEY,      -- 盘点单号
    warehouse_id VARCHAR(50) NOT NULL,     -- 盘点仓库
    check_date DATE NOT NULL,              -- 盘点日期
    status VARCHAR(20) DEFAULT 'ongoing', -- 状态
    checker VARCHAR(100),                  -- 盘点人
    total_products INT,                    -- 总品种数
    profit_qty INT,                        -- 盘盈数量
    loss_qty INT,                          -- 盘亏数量
    profit_amount DECIMAL(12,2),          -- 盘盈金额
    loss_amount DECIMAL(12,2),            -- 盘亏金额
    approve_by VARCHAR(100),              -- 审核人
    approve_time DATETIME,                 -- 审核时间
    remark TEXT,
    create_time DATETIME DEFAULT NOW(),
    update_time DATETIME DEFAULT NOW()
);
```

### 1.12 盘点明细表 (check_order_items)
```sql
CREATE TABLE check_order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id VARCHAR(50) NOT NULL,         -- 盘点单号
    line_no INT,                           -- 行号
    product_id VARCHAR(50) NOT NULL,       -- 商品编码
    product_name VARCHAR(200),             -- 商品名称
    unit VARCHAR(20),                      -- 单位
    book_qty INT,                          -- 账面数量
    check_qty INT,                         -- 实盘数量
    diff_qty INT,                          -- 差异数量
    price DECIMAL(12,2),                   -- 单价
    diff_amount DECIMAL(12,2),            -- 差异金额
    status VARCHAR(20) DEFAULT 'pending', -- 状态
    handle_type VARCHAR(20),               -- 处理方式
    remark TEXT,
    FOREIGN KEY (order_id) REFERENCES check_orders(order_id)
);
```

## 二、数据字典

### 2.1 单据状态
| 状态码 | 状态名 | 说明 |
|--------|--------|------|
| draft | 草稿 | 刚创建，尚未提交 |
| submitted | 已提交 | 已提交待审核 |
| approved | 已审核 | 审核通过 |
| in_progress | 进行中 | 部分执行 |
| completed | 已完成 | 全部执行完成 |
| cancelled | 已取消 | 已取消 |
| closed | 已关闭 | 流程结束 |

### 2.2 流水类型
| 类型码 | 类型名 | 说明 |
|--------|--------|------|
| PI | 采购入库 | 采购入库产生 |
| PR | 采购退货 | 采购退货产生 |
| SI | 销售出库 | 销售出库产生 |
| SR | 销售退货 | 销售退货产生 |
| IT | 库存调拨 | 调拨出库 |
| IA | 库存调整 | 盘盈盘亏调整 |
| OT | 其他入库 | 其他原因入库 |
| OO | 其他出库 | 其他原因出库 |

### 2.3 处理方式
| 方式码 | 方式名 | 说明 |
|--------|--------|------|
| adjust | 调整库存 | 直接调整库存 |
| pending | 待查 | 暂不处理 |
| writeoff | 报损 | 作为损失处理 |
| inventory | 盘盈入库 | 作为盘盈处理 |
