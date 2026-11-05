---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304502204ad5bfb3cd5935cd77bd0f9b12a84f64e3fb61a0d197a100b7242be2e6448852022100e89e9e8cf477a52d6678094105d8e6390eef8de0b266670ee213aaa6295edcf3
    ReservedCode2: 3046022100c9f615e46d270fb1b7f2c22054613cd8996750ffd02cda965a112eefce84fd64022100d2fd31d0c77508101a3e6c331bfb22d15309b86028a6dd3ff62fbc2ea447efdb
---

# zshlpay 数据库规范文档

## 数据库设计原则

1. **表命名规范**: 使用小写字母，单词间用下划线分隔
2. **字段命名规范**: 使用小写字母，单词间用下划线分隔
3. **主键**: 所有表必须有 `id` 字段作为主键，类型为 `bigint`
4. **公共字段**: 所有业务表必须包含以下字段：
   - `create_time` - 创建时间
   - `create_by` - 创建人
   - `update_time` - 更新时间
   - `update_by` - 更新人
   - `del_flag` - 删除标志 (0-正常, 1-删除)
   - `remark` - 备注

## 核心表结构

### 1. 商户表 (pay_merchant)

```sql
CREATE TABLE pay_merchant (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    merchant_no     VARCHAR(32) NOT NULL UNIQUE COMMENT '商户号',
    merchant_name   VARCHAR(128) NOT NULL COMMENT '商户名称',
    merchant_type   TINYINT NOT NULL DEFAULT 1 COMMENT '商户类型: 1-个人, 2-企业',
    contact_name    VARCHAR(64) COMMENT '联系人姓名',
    contact_phone   VARCHAR(20) COMMENT '联系人电话',
    contact_email   VARCHAR(128) COMMENT '联系人邮箱',
    license_no      VARCHAR(64) COMMENT '营业执照号',
    license_img      VARCHAR(256) COMMENT '营业执照图片',
    settlement_type TINYINT NOT NULL DEFAULT 1 COMMENT '结算类型: 1-T+1, 2-T+0',
    status          TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-待审核, 1-审核通过, 2-审核拒绝, 3-禁用',
    balance         DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '账户余额',
    frozen_amount   DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '冻结金额',
    api_key         VARCHAR(64) COMMENT 'API密钥',
    callback_url    VARCHAR(256) COMMENT '异步回调地址',
    return_url      VARCHAR(256) COMMENT '同步跳转地址',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志: 0-正常, 1-删除',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_merchant_no (merchant_no),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商户表';
```

### 2. 支付通道表 (pay_channel)

```sql
CREATE TABLE pay_channel (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    channel_code    VARCHAR(32) NOT NULL UNIQUE COMMENT '通道编码',
    channel_name    VARCHAR(64) NOT NULL COMMENT '通道名称',
    channel_type    TINYINT NOT NULL COMMENT '通道类型: 1-微信, 2-支付宝, 3-银联, 4-其他',
    app_id          VARCHAR(128) COMMENT '应用ID',
    mch_id          VARCHAR(64) COMMENT '商户号',
    api_key         VARCHAR(256) COMMENT 'API密钥',
    cert_path       VARCHAR(256) COMMENT '证书路径',
    status          TINYINT NOT NULL DEFAULT 0 COMMENT '状态: 0-禁用, 1-启用',
    rate            DECIMAL(6,5) NOT NULL DEFAULT 0.00000 COMMENT '通道费率',
    min_amount      DECIMAL(10,2) NOT NULL DEFAULT 0.01 COMMENT '最小金额',
    max_amount      DECIMAL(10,2) NOT NULL DEFAULT 999999.99 COMMENT '最大金额',
    sort            INT NOT NULL DEFAULT 0 COMMENT '排序',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_channel_code (channel_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付通道表';
```

### 3. 支付订单表 (pay_order)

```sql
CREATE TABLE pay_order (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    trade_no        VARCHAR(32) NOT NULL UNIQUE COMMENT '支付单号',
    order_no        VARCHAR(32) NOT NULL COMMENT '商户订单号',
    merchant_no     VARCHAR(32) NOT NULL COMMENT '商户号',
    channel_code    VARCHAR(32) NOT NULL COMMENT '通道编码',
    channel_trade_no VARCHAR(64) COMMENT '通道订单号',

    amount          DECIMAL(15,2) NOT NULL COMMENT '订单金额',
    actual_amount   DECIMAL(15,2) NOT NULL COMMENT '实际支付金额',
    refund_amount   DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '已退款金额',

    subject         VARCHAR(256) NOT NULL COMMENT '商品标题',
    body            VARCHAR(512) COMMENT '商品描述',
    attach          VARCHAR(512) COMMENT '附加数据',

    status          TINYINT NOT NULL DEFAULT 0 COMMENT '订单状态: 0-待支付, 1-支付中, 2-支付成功, 3-支付失败, 4-已取消, 5-已退款, 6-部分退款',
    pay_time        DATETIME COMMENT '支付时间',
    expire_time     DATETIME COMMENT '过期时间',

    notify_url      VARCHAR(256) COMMENT '异步通知地址',
    return_url      VARCHAR(256) COMMENT '同步跳转地址',
    client_ip        VARCHAR(64) COMMENT '客户端IP',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_trade_no (trade_no),
    INDEX idx_order_no (order_no),
    INDEX idx_merchant_no (merchant_no),
    INDEX idx_channel_code (channel_code),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='支付订单表';
```

### 4. 退款记录表 (pay_refund)

```sql
CREATE TABLE pay_refund (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    refund_no       VARCHAR(32) NOT NULL UNIQUE COMMENT '退款单号',
    trade_no        VARCHAR(32) NOT NULL COMMENT '支付单号',
    order_no        VARCHAR(32) NOT NULL COMMENT '商户订单号',
    merchant_no     VARCHAR(32) NOT NULL COMMENT '商户号',
    channel_code    VARCHAR(32) NOT NULL COMMENT '通道编码',
    channel_refund_no VARCHAR(64) COMMENT '通道退款单号',

    amount          DECIMAL(15,2) NOT NULL COMMENT '订单金额',
    refund_amount   DECIMAL(15,2) NOT NULL COMMENT '退款金额',

    reason          VARCHAR(256) COMMENT '退款原因',
    status          TINYINT NOT NULL DEFAULT 0 COMMENT '退款状态: 0-处理中, 1-退款成功, 2-退款失败',
    finish_time     DATETIME COMMENT '完成时间',

    operator        VARCHAR(64) COMMENT '操作人',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_refund_no (refund_no),
    INDEX idx_trade_no (trade_no),
    INDEX idx_merchant_no (merchant_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='退款记录表';
```

### 5. 结算记录表 (pay_settlement)

```sql
CREATE TABLE pay_settlement (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    settlement_no   VARCHAR(32) NOT NULL UNIQUE COMMENT '结算单号',
    merchant_no     VARCHAR(32) NOT NULL COMMENT '商户号',

    total_amount    DECIMAL(15,2) NOT NULL COMMENT '结算总金额',
    service_fee     DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '服务费',
    actual_amount   DECIMAL(15,2) NOT NULL COMMENT '实际结算金额',

    order_count     INT NOT NULL DEFAULT 0 COMMENT '订单数量',
    refund_amount   DECIMAL(15,2) NOT NULL DEFAULT 0.00 COMMENT '退款金额',

    bank_name       VARCHAR(64) COMMENT '银行名称',
    bank_account    VARCHAR(32) COMMENT '银行账号',
    bank_no         VARCHAR(32) COMMENT '行号',

    status          TINYINT NOT NULL DEFAULT 0 COMMENT '结算状态: 0-待处理, 1-处理中, 2-已结算, 3-结算失败',
    apply_time      DATETIME NOT NULL COMMENT '申请时间',
    settle_time     DATETIME COMMENT '结算时间',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_settlement_no (settlement_no),
    INDEX idx_merchant_no (merchant_no),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='结算记录表';
```

### 6. 操作日志表 (pay_log)

```sql
CREATE TABLE pay_log (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    type            VARCHAR(32) COMMENT '日志类型',
    title           VARCHAR(128) COMMENT '日志标题',
    merchant_no     VARCHAR(32) COMMENT '商户号',
    operator        VARCHAR(64) COMMENT '操作人',
    operate_ip      VARCHAR(64) COMMENT '操作IP',
    operate_url     VARCHAR(256) COMMENT '请求地址',
    request_method  VARCHAR(10) COMMENT '请求方法',
    request_params  TEXT COMMENT '请求参数',
    response_data   TEXT COMMENT '返回数据',
    error_msg       TEXT COMMENT '错误信息',
    execute_time    BIGINT COMMENT '执行时间(毫秒)',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',

    INDEX idx_type (type),
    INDEX idx_merchant_no (merchant_no),
    INDEX idx_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='操作日志表';
```

### 7. 系统配置表 (pay_config)

```sql
CREATE TABLE pay_config (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    config_key      VARCHAR(64) NOT NULL UNIQUE COMMENT '配置键',
    config_value    TEXT COMMENT '配置值',
    config_type     VARCHAR(32) COMMENT '配置类型',
    config_name     VARCHAR(128) COMMENT '配置名称',
    sort            INT NOT NULL DEFAULT 0 COMMENT '排序',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_config_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='系统配置表';
```

### 8. 门店表 (pay_store)

```sql
CREATE TABLE pay_store (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    store_no        VARCHAR(32) NOT NULL UNIQUE COMMENT '门店号',
    merchant_no     VARCHAR(32) NOT NULL COMMENT '商户号',
    store_name      VARCHAR(128) NOT NULL COMMENT '门店名称',
    store_type      TINYINT DEFAULT 1 COMMENT '门店类型: 1-直营, 2-加盟',
    province        VARCHAR(32) COMMENT '省份',
    city            VARCHAR(32) COMMENT '城市',
    district        VARCHAR(32) COMMENT '区/县',
    address         VARCHAR(256) COMMENT '详细地址',
    contact_name    VARCHAR(64) COMMENT '联系人',
    contact_phone   VARCHAR(20) COMMENT '联系电话',
    status          TINYINT NOT NULL DEFAULT 1 COMMENT '状态: 0-禁用, 1-启用',

    -- 公共字段
    create_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    create_by       VARCHAR(64) COMMENT '创建人',
    update_time     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    update_by       VARCHAR(64) COMMENT '更新人',
    del_flag        TINYINT NOT NULL DEFAULT 0 COMMENT '删除标志',
    remark          VARCHAR(512) COMMENT '备注',

    INDEX idx_store_no (store_no),
    INDEX idx_merchant_no (merchant_no),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='门店表';
```

## 索引设计原则

1. **主键索引**: 每张表必须有主键索引
2. **唯一索引**: 用于需要保证唯一性的字段
3. **普通索引**: 用于经常查询的字段
4. **联合索引**: 用于多条件查询，遵循最左前缀原则
5. **避免过多索引**: 每个表索引数量不超过5个

## 数据类型选择

| 业务场景 | 推荐类型 | 说明 |
|----------|----------|------|
| 主键ID | BIGINT | 自增主键 |
| 金额 | DECIMAL(15,2) | 精确存储 |
| 状态标志 | TINYINT | 节省空间 |
| 日期时间 | DATETIME | 带时分秒 |
| 长文本 | TEXT | 大文本内容 |
| 短字符串 | VARCHAR(64/128/256) | 根据实际长度选择 |

## 国产数据库适配说明

### 达梦数据库 (DM)
- 使用 `VARCHAR2` 替换 `VARCHAR`（兼容模式）
- 序列替代自增主键
- 分页使用 `ROWNUM`

### 人大金仓 (Kingbase)
- 兼容PostgreSQL语法
- 序列替代自增主键
- 使用 `LIMIT OFFSET` 分页

### GaussDB / OceanBase
- 兼容MySQL语法
- 可使用自增主键
- 使用 `LIMIT OFFSET` 分页

### 注意事项
1. 字段名避免使用数据库保留字
2. 金额字段统一使用 `DECIMAL`
3. 字符串长度预留足够空间
4. 敏感信息加密存储
5. 重要数据添加审计字段
