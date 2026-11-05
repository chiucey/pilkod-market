# Agent Skills 平台数据库设计文档

---

## 1. 数据库选型与架构

### 1.1 数据库选型依据

| 场景 | 数据库类型 | 选型 | 理由 |
|------|-----------|------|------|
| 核心业务数据 | 关系型 | PostgreSQL 15 | 事务可靠、功能丰富、扩展性强 |
| 高频缓存 | 内存数据库 | Redis 7 Cluster | 高性能、支持多种数据结构 |
| 全文检索 | 搜索引擎 | Elasticsearch 8 | 强大搜索能力、分布式 |
| 文件元数据 | 文档型 | MongoDB 4.4 | 灵活Schema、日志存储 |
| 时序数据 | 时序数据库 | TimescaleDB | 高吞吐、压缩存储 |
| 图数据 | 图数据库 | Neo4j | 社交关系、推荐系统 |

### 1.2 数据库架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     数据库架构总览                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    PostgreSQL 主库集群                     │    │
│  │                                                         │    │
│  │  ┌─────────┐     ┌─────────┐     ┌─────────┐          │    │
│  │  │ Master  │ ◄──►│ Slave1  │ ◄──►│ Slave2  │          │    │
│  │  │  (写)   │     │  (读)   │     │  (读)   │          │    │
│  │  └────┬────┘     └────┬────┘     └────┬────┘          │    │
│  │       │                │                │               │    │
│  │  ┌────▼────┐     ┌────▼────┐     ┌────▼────┐          │    │
│  │  │ WAL日志  │     │ 备份    │     │ 备份    │          │    │
│  │  └─────────┘     └─────────┘     └─────────┘          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
│  │    Redis     │  │ Elasticsearch │  │      MongoDB       │  │
│  │   Cluster    │  │    Cluster    │  │      Replica       │  │
│  │  (3主3从)    │  │   (3节点)     │  │    Set (1主2从)    │  │
│  └──────────────┘  └──────────────┘  └────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 分库分表策略

| 策略 | 规则 | 适用场景 |
|------|------|----------|
| 垂直分库 | 按业务模块拆分 | 用户库/订单库/技能库 |
| 水平分表 | 按用户ID Hash | 大表（如日志表） |
| 读写分离 | 主库写、从库读 | 读多写少场景 |
| 冷热分离 | 按时间分区 | 历史数据归档 |

---

## 2. PostgreSQL 数据库设计

### 2.1 ER 实体关系图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    User     │     │   Skill     │     │   Order     │
├─────────────┤     ├─────────────┤     ├─────────────┤
│ id (PK)     │◄───┐│ id (PK)     │◄───┐│ id (PK)     │
│ email       │    ││ developerId │    ││ userId (FK) │
│ phone       │    ││ categoryId  │    ││ skillId (FK)│
│ nickname    │    ││ name        │    ││ orderNo     │
│ avatar      │    ││ description │    ││ amount      │
│ role        │    ││ price       │    ││ status      │
│ status      │    ││ status      │    ││ paidAt      │
└─────────────┘    ││ stats       │    │└─────────────┘
      │           └─────────────┘          │
      │                │                   │
      │           ┌────▼────┐              │
      │           │ Category │              │
      │           ├──────────┤              │
      │           │ id (PK) │              │
      │           │ name    │              │
      │           │ parentId│              │
      │           └──────────┘              │
      │                                    │
┌─────▼─────────┐                    ┌─────▼──────────┐
│ UserFavorite  │                    │    Review      │
├───────────────┤                    ├────────────────┤
│ id (PK)       │                    │ id (PK)        │
│ userId (FK)   │                    │ skillId (FK)   │
│ skillId (FK)  │                    │ userId (FK)    │
│ createdAt     │                    │ rating         │
└───────────────┘                    │ content        │
                                      │ status         │
                                      └────────────────┘
```

### 2.2 用户相关表

#### 2.2.1 用户基础信息表 (users)

```sql
-- 用户基础信息表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    avatar VARCHAR(500),
    role VARCHAR(20) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'developer', 'admin')),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'frozen', 'deleted')),
    developer_status VARCHAR(20) DEFAULT 'none' CHECK (developer_status IN ('none', 'pending', 'approved', 'rejected')),
    developer_certified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip INET,
    login_count INTEGER DEFAULT 0,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    real_name VARCHAR(50),
    id_card VARCHAR(18),
    id_card_front VARCHAR(500),
    id_card_back VARCHAR(500),
    company VARCHAR(100),
    position VARCHAR(50),
    bio TEXT,
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 索引设计
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL AND deleted_at IS NULL;
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- 注释
COMMENT ON TABLE users IS '用户基础信息表';
COMMENT ON COLUMN users.password_hash IS '使用bcrypt加密的密码哈希';
COMMENT ON COLUMN users.role IS '用户角色: user-普通用户, developer-开发者, admin-管理员';
COMMENT ON COLUMN users.developer_status IS '开发者认证状态';
COMMENT ON COLUMN users.settings IS '用户设置JSON配置';
```

#### 2.2.2 用户认证表 (user_auth)

```sql
-- 用户认证表（支持多种登录方式）
CREATE TABLE user_auth (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    auth_type VARCHAR(20) NOT NULL CHECK (auth_type IN ('password', 'phone', 'email', 'wechat', 'github', 'google')),
    identifier VARCHAR(255) NOT NULL,
    credential TEXT,
    verified BOOLEAN DEFAULT FALSE,
    bind_time TIMESTAMP WITH TIME ZONE,
    unbind_time TIMESTAMP WITH TIME ZONE,
    extra_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(auth_type, identifier)
);

CREATE INDEX idx_user_auth_user_id ON user_auth(user_id);
CREATE INDEX idx_user_auth_type_identifier ON user_auth(auth_type, identifier);

COMMENT ON TABLE user_auth IS '用户认证信息表，支持多种登录方式';
```

#### 2.2.3 用户 Token 表 (user_tokens)

```sql
-- 用户Token表
CREATE TABLE user_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('access', 'refresh', 'verify', 'reset_password')),
    token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_tokens_user_id ON user_tokens(user_id);
CREATE INDEX idx_user_tokens_token_hash ON user_tokens(token_hash);
CREATE INDEX idx_user_tokens_expires_at ON user_tokens(expires_at) WHERE revoked = FALSE;

COMMENT ON TABLE user_tokens IS '用户Token管理表';
```

#### 2.2.4 用户收藏表 (user_favorites)

```sql
-- 用户收藏表
CREATE TABLE user_favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id)
);

CREATE INDEX idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX idx_user_favorites_skill_id ON user_favorites(skill_id);

COMMENT ON TABLE user_favorites IS '用户收藏技能表';
```

### 2.3 技能相关表

#### 2.3.1 技能基础信息表 (skills)

```sql
-- 技能基础信息表
CREATE TABLE skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(120) NOT NULL UNIQUE,
    developer_id UUID NOT NULL REFERENCES users(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    short_desc VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(500),
    screenshots JSONB DEFAULT '[]',
    demo_url VARCHAR(500),
    documentation TEXT,
    pricing_type VARCHAR(20) NOT NULL DEFAULT 'free' CHECK (pricing_type IN ('free', 'one_time', 'subscription')),
    price INTEGER DEFAULT 0 CHECK (price >= 0 AND price <= 99999900),
    subscription_price INTEGER,
    subscription_period VARCHAR(10) DEFAULT 'month' CHECK (subscription_period IN ('month', 'year')),
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending', 'approved', 'rejected', 'online', 'offline')),
    reject_reason TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    offline_at TIMESTAMP WITH TIME ZONE,
    view_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    use_count INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    tags JSONB DEFAULT '[]',
    input_schema JSONB,
    output_schema JSONB,
    config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- 索引设计
CREATE INDEX idx_skills_developer_id ON skills(developer_id);
CREATE INDEX idx_skills_category_id ON skills(category_id);
CREATE INDEX idx_skills_status ON skills(status);
CREATE INDEX idx_skills_slug ON skills(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_skills_pricing_type ON skills(pricing_type);
CREATE INDEX idx_skills_rating ON skills(rating DESC);
CREATE INDEX idx_skills_view_count ON skills(view_count DESC);
CREATE INDEX idx_skills_created_at ON skills(created_at DESC);
CREATE INDEX idx_skills_published_at ON skills(published_at DESC);

-- 全文搜索索引
CREATE INDEX idx_skills_fulltext ON skills USING gin(to_tsvector('zhparse', name || ' ' || short_desc || ' ' || COALESCE(description, '')));

COMMENT ON TABLE skills IS '技能基础信息表';
COMMENT ON COLUMN skills.price IS '价格，单位：分';
COMMENT ON COLUMN skills.slug IS 'URL友好的唯一标识符';
```

#### 2.3.2 技能版本表 (skill_versions)

```sql
-- 技能版本表
CREATE TABLE skill_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    version VARCHAR(20) NOT NULL,
    changelog TEXT,
    source_package_url VARCHAR(500),
    package_size BIGINT,
    package_hash VARCHAR(64),
    input_schema JSONB,
    output_schema JSONB,
    dependencies JSONB DEFAULT '[]',
    test_results JSONB,
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'testing', 'passed', 'failed')),
    released_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(skill_id, version)
);

CREATE INDEX idx_skill_versions_skill_id ON skill_versions(skill_id);
CREATE INDEX idx_skill_versions_status ON skill_versions(status);

COMMENT ON TABLE skill_versions IS '技能版本历史表';
```

#### 2.3.3 技能分类表 (categories)

```sql
-- 技能分类表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    slug VARCHAR(60) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    icon VARCHAR(100),
    description VARCHAR(200),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    skill_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_sort_order ON categories(sort_order);

COMMENT ON TABLE categories IS '技能分类表，支持多级分类';
```

#### 2.3.4 技能评价表 (reviews)

```sql
-- 技能评价表
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    skill_id UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    order_id UUID REFERENCES orders(id),
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    pros TEXT,
    cons TEXT,
    images JSONB DEFAULT '[]',
    helpful_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'hidden', 'deleted')),
    reply_content TEXT,
    replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reviews_skill_id ON reviews(skill_id);
CREATE INDEX idx_reviews_user_id ON reviews(user_id);
CREATE INDEX idx_reviews_rating ON reviews(rating);
CREATE INDEX idx_reviews_created_at ON reviews(created_at DESC);

-- 唯一约束：每个用户对每个技能只能评价一次
CREATE UNIQUE INDEX idx_reviews_user_skill ON reviews(user_id, skill_id) WHERE status != 'deleted';

COMMENT ON TABLE reviews IS '技能评价表';
```

### 2.4 订单相关表

#### 2.4.1 订单表 (orders)

```sql
-- 订单表
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no VARCHAR(32) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id),
    skill_id UUID NOT NULL REFERENCES skills(id),
    developer_id UUID NOT NULL REFERENCES users(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('purchase', 'subscription', 'upgrade', 'gift')),
    subscription_id UUID,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    discount_amount INTEGER DEFAULT 0,
    coupon_id UUID,
    final_amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded', 'expired')),
    payment_method VARCHAR(20),
    payment_id VARCHAR(100),
    payment_time TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancel_reason VARCHAR(200),
    refund_amount INTEGER DEFAULT 0,
    refund_reason TEXT,
    refund_time TIMESTAMP WITH TIME ZONE,
    expire_at TIMESTAMP WITH TIME ZONE NOT NULL,
    invoice_id UUID,
    remark TEXT,
    client_ip INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引设计
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_skill_id ON orders(skill_id);
CREATE INDEX idx_orders_developer_id ON orders(developer_id);
CREATE INDEX idx_orders_order_no ON orders(order_no);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at DESC);
CREATE INDEX idx_orders_expire_at ON orders(expire_at) WHERE status = 'pending';

COMMENT ON TABLE orders IS '订单表';
COMMENT ON COLUMN orders.amount IS '订单金额，单位：分';
```

#### 2.4.2 订阅表 (subscriptions)

```sql
-- 用户订阅表
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    skill_id UUID NOT NULL REFERENCES skills(id),
    order_id UUID REFERENCES orders(id),
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'cancelled', 'pending')),
    start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    end_at TIMESTAMP WITH TIME ZONE NOT NULL,
    auto_renew BOOLEAN DEFAULT TRUE,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    renewed_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, skill_id, start_at)
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_skill_id ON subscriptions(skill_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_end_at ON subscriptions(end_at) WHERE status = 'active';

COMMENT ON TABLE subscriptions IS '用户订阅记录表';
```

#### 2.4.3 优惠券表 (coupons)

```sql
-- 优惠券表
CREATE TABLE coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('fixed', 'percentage', 'fixed_skill')),
    value INTEGER NOT NULL,
    min_amount INTEGER DEFAULT 0,
    max_discount_amount INTEGER,
    skill_id UUID REFERENCES skills(id),
    total_count INTEGER,
    used_count INTEGER DEFAULT 0,
    per_user_limit INTEGER DEFAULT 1,
    valid_from TIMESTAMP WITH TIME ZONE NOT NULL,
    valid_until TIMESTAMP WITH TIME ZONE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coupons_code ON coupons(code);
CREATE INDEX idx_coupons_valid_period ON coupons(valid_from, valid_until);

COMMENT ON TABLE coupons IS '优惠券表';
```

#### 2.4.4 用户优惠券表 (user_coupons)

```sql
-- 用户优惠券表
CREATE TABLE user_coupons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    coupon_id UUID NOT NULL REFERENCES coupons(id),
    order_id UUID REFERENCES orders(id),
    status VARCHAR(20) DEFAULT 'unused' CHECK (status IN ('unused', 'used', 'expired')),
    received_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    used_at TIMESTAMP WITH TIME ZONE,
    expire_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, coupon_id, status) -- 防止重复领取
);

CREATE INDEX idx_user_coupons_user_id ON user_coupons(user_id);
CREATE INDEX idx_user_coupons_status ON user_coupons(status);

COMMENT ON TABLE user_coupons IS '用户优惠券领取记录表';
```

### 2.5 支付相关表

#### 2.5.1 支付记录表 (payments)

```sql
-- 支付记录表
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_no VARCHAR(64) NOT NULL UNIQUE,
    order_id UUID NOT NULL REFERENCES orders(id),
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('alipay', 'wechat', 'bank_card')),
    channel_order_no VARCHAR(128),
    total_amount INTEGER NOT NULL,
    actual_amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'CNY',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'success', 'failed', 'refunded', 'partial_refunded')),
    payment_time TIMESTAMP WITH TIME ZONE,
    callback_data JSONB,
    error_code VARCHAR(50),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_order_id ON payments(order_id);
CREATE INDEX idx_payments_channel_order_no ON payments(channel_order_no);
CREATE INDEX idx_payments_status ON payments(status);

COMMENT ON TABLE payments IS '支付记录表';
```

#### 2.5.2 开发者收益表 (developer_earnings)

```sql
-- 开发者收益表
CREATE TABLE developer_earnings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    developer_id UUID NOT NULL REFERENCES users(id),
    order_id UUID REFERENCES orders(id),
    subscription_id UUID,
    skill_id UUID NOT NULL REFERENCES skills(id),
    type VARCHAR(20) NOT NULL CHECK (type IN ('sale', 'subscription', 'refund')),
    gross_amount INTEGER NOT NULL,
    commission_rate DECIMAL(5,4) NOT NULL,
    commission_amount INTEGER NOT NULL,
    net_amount INTEGER NOT NULL,
    platform_fee INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'settled', 'withdrawn', 'frozen')),
    settled_at TIMESTAMP WITH TIME ZONE,
    withdrawal_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_developer_earnings_developer_id ON developer_earnings(developer_id);
CREATE INDEX idx_developer_earnings_skill_id ON developer_earnings(skill_id);
CREATE INDEX idx_developer_earnings_status ON developer_earnings(status);
CREATE INDEX idx_developer_earnings_created_at ON developer_earnings(created_at DESC);

COMMENT ON TABLE developer_earnings IS '开发者收益表';
```

#### 2.5.3 提现记录表 (withdrawals)

```sql
-- 提现记录表
CREATE TABLE withdrawals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    withdrawal_no VARCHAR(32) NOT NULL UNIQUE,
    developer_id UUID NOT NULL REFERENCES users(id),
    amount INTEGER NOT NULL,
    fee INTEGER DEFAULT 0,
    actual_amount INTEGER NOT NULL,
    channel VARCHAR(20) NOT NULL CHECK (channel IN ('bank', 'alipay', 'wechat')),
    bank_account VARCHAR(50),
    bank_name VARCHAR(100),
    real_name VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'success', 'failed', 'cancelled')),
    transaction_no VARCHAR(128),
    process_time TIMESTAMP WITH TIME ZONE,
    fail_reason TEXT,
    remark TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_withdrawals_developer_id ON withdrawals(developer_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);

COMMENT ON TABLE withdrawals IS '开发者提现记录表';
```

### 2.6 审计日志表

#### 2.6.1 操作日志表 (operation_logs)

```sql
-- 操作日志表
CREATE TABLE operation_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    username VARCHAR(50),
    operation VARCHAR(50) NOT NULL,
    module VARCHAR(50) NOT NULL,
    method VARCHAR(100),
    request_url TEXT,
    request_method VARCHAR(10),
    request_params JSONB,
    request_body JSONB,
    response_data JSONB,
    status INTEGER DEFAULT 1,
    error_message TEXT,
    ip_address INET,
    user_agent TEXT,
    execution_time INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
) PARTITION BY RANGE (created_at);

-- 按月分区
CREATE TABLE operation_logs_2026_01 PARTITION OF operation_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE INDEX idx_operation_logs_user_id ON operation_logs(user_id);
CREATE INDEX idx_operation_logs_module ON operation_logs(module);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at DESC);

COMMENT ON TABLE operation_logs IS '操作审计日志表，按月分区';
```

---

## 3. Redis 缓存设计

### 3.1 Key 命名规范

```
{模块}:{业务}:{标识}:{属性}

示例：
user:session:{userId}           # 用户会话
skill:detail:{skillId}          # 技能详情缓存
skill:rating:{skillId}          # 技能评分缓存
order:status:{orderId}          # 订单状态缓存
rate:limit:{userId}:{api}       # 限流计数
lock:skill:publish:{skillId}    # 发布分布式锁
```

### 3.2 缓存策略

| 数据类型 | Key模式 | TTL | 更新策略 |
|----------|---------|-----|----------|
| 用户Session | user:session:{uid} | 24h | 登录时创建，登出时删除 |
| 用户信息 | user:info:{uid} | 1h | 主动失效 |
| 技能详情 | skill:detail:{id} | 5min | 自动过期+主动刷新 |
| 技能列表 | skill:list:{hash} | 1min | 自动过期 |
| 热门技能 | skill:top:{type} | 30min | 定时更新 |
| 分类列表 | category:tree | 1h | 主动失效 |
| 订单状态 | order:status:{id} | 30min | 变更时主动更新 |
| 验证码 | captcha:{key} | 5min | 自动过期 |
| 分布式锁 | lock:{resource}:{id} | 30s | 自动过期 |
| 限流计数 | rate:{userId}:{api} | 1min | 自动过期 |

### 3.3 Redis 数据结构使用

```sql
-- String: 简单值存储
SET skill:detail:{id} {json_data} EX 300

-- Hash: 对象存储
HSET user:profile:{id} name "张三" email "zhang@example.com"
HGET user:profile:{id} name

-- List: 队列/列表
LPUSH skill:search:queue {task_data}
BRPOP skill:search:queue 0

-- Set: 标签/去重
SADD skill:tags:{skillId} "翻译" "AI" "NLP"
SMEMBERS skill:tags:{skillId}

-- Sorted Set: 排行榜/排序
ZADD skill:ranking:daily {score} {skillId}
ZREVRANGE skill:ranking:daily 0 9 WITHSCORES

-- HyperLogLog: UV统计
PFADD page:uv:20260329 {userId}
PFCOUNT page:uv:20260329

-- Bitmap: 签到/状态
SETBIT user:sign:{userId}:{year} {dayOfYear} 1
```

---

## 4. Elasticsearch 索引设计

### 4.1 技能搜索索引

```json
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "skill_analyzer": {
          "type": "custom",
          "tokenizer": "ik_max_word",
          "filter": ["lowercase", "asciifolding"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": { "type": "keyword" },
      "name": {
        "type": "text",
        "analyzer": "skill_analyzer",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "slug": { "type": "keyword" },
      "developer_id": { "type": "keyword" },
      "developer_name": { "type": "text" },
      "category_id": { "type": "integer" },
      "category_name": { "type": "keyword" },
      "short_desc": {
        "type": "text",
        "analyzer": "skill_analyzer"
      },
      "description": {
        "type": "text",
        "analyzer": "skill_analyzer"
      },
      "tags": { "type": "keyword" },
      "pricing_type": { "type": "keyword" },
      "price": { "type": "integer" },
      "rating": { "type": "float" },
      "review_count": { "type": "integer" },
      "view_count": { "type": "integer" },
      "use_count": { "type": "integer" },
      "status": { "type": "keyword" },
      "published_at": { "type": "date" },
      "created_at": { "type": "date" },
      "suggest": {
        "type": "completion",
        "analyzer": "simple"
      }
    }
  }
}
```

### 4.2 搜索建议索引

```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "keyword": { "type": "text" },
      "type": { "type": "keyword" },
      "skill_id": { "type": "keyword" },
      "popularity": { "type": "integer" },
      "updated_at": { "type": "date" }
    }
  }
}
```

---

## 5. 数据库高可用设计

### 5.1 读写分离架构

```
                    ┌─────────────┐
                    │   应用层    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
        │  主库写入 │ │  从库读取 │ │  从库读取 │
        │  (Master) │ │  (Slave1) │ │  (Slave2) │
        └───────────┘ └───────────┘ └───────────┘
```

### 5.2 备份策略

| 备份类型 | 频率 | 保留时间 | 说明 |
|----------|------|----------|------|
| 全量备份 | 每日凌晨2点 | 30天 | pg_dump全库 |
| 增量备份 | 每6小时 | 7天 | WAL日志归档 |
| 实时备份 | 实时 | - | 流复制到从库 |
| 跨区域备份 | 每日 | 90天 | 异地容灾 |

---

## 6. 数据库规范

### 6.1 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 表名 | 小写+下划线，复数形式 | users, skill_categories |
| 字段名 | 小写+下划线 | user_id, created_at |
| 索引名 | idx_{表名}_{字段名} | idx_users_email |
| 唯一索引 | uk_{表名}_{字段名} | uk_skills_slug |
| 外键名 | fk_{表名1}_{表名2} | fk_orders_user_id |
| 主键 | id (UUID类型) | id |

### 6.2 字段设计规范

- 所有表必须有 id, created_at, updated_at 字段
- 必须使用 UTC 时间：TIMESTAMP WITH TIME ZONE
- 金额统一使用分：INTEGER 类型
- 状态字段使用 VARCHAR 并定义 CHECK 约束
- JSONB 用于扩展字段和配置
- 软删除使用 deleted_at 字段
- IP 地址使用 INET 类型

### 6.3 索引设计原则

| 原则 | 说明 |
|------|------|
| 选择性高 | 优先在唯一或高选择性字段建索引 |
| 覆盖索引 | 将常用查询字段加入索引 |
| 联合索引 | 考虑字段顺序，区分度高的放前面 |
| 前缀索引 | 长字符串字段使用前缀索引 |
| 部分索引 | WHERE 条件过滤后建索引 |
| 避免冗余 | 不创建重复或无用索引 |
