# 数据采集规范

## 一、数据采集体系架构

### 1.1 采集体系设计原则

| 原则 | 说明 | 示例 |
|-----|-----|-----|
| 完整性 | 覆盖客服全链路关键节点 | 入口→服务→完成→复访 |
| 准确性 | 数据定义清晰、口径一致 | 统一指标编码和计算公式 |
| 时效性 | 满足业务分析的时间要求 | 实时/准实时/批量 |
| 安全性 | 符合数据安全和隐私要求 | 脱敏处理、权限控制 |
| 可扩展性 | 支持业务变化和需求迭代 | 预留扩展字段 |

### 1.2 数据源分类

| 数据源类型 | 数据内容 | 采集方式 | 典型系统 |
|-----------|---------|---------|---------|
| 行为数据 | 用户操作行为轨迹 | 埋点采集 | 前端/APP |
| 业务数据 | 客服业务流程数据 | 系统对接 | 工单系统/CRM |
| 反馈数据 | 客户评价和反馈 | 接口获取 | 评价系统 |
| 运营数据 | 客服运营管理数据 | 系统对接 | 排班系统/培训系统 |

---

## 二、埋点设计方案

### 2.1 埋点命名规范

**事件命名格式**：`[页面]_[操作]_[对象]`

| 组成部分 | 说明 | 示例 |
|---------|-----|-----|
| 页面 | 发生操作的页面/模块 | chat, ticket, order |
| 操作 | 用户或系统的行为动作 | click, submit, view, load |
| 对象 | 操作的具体对象 | message, button, form |

**属性命名格式**：`[实体]_[属性类型]_[属性名]`

| 组成部分 | 说明 | 示例 |
|---------|-----|-----|
| 实体 | 属性所属的实体 | user, session, message |
| 属性类型 | 属性的类别 | id, type, time, status |
| 属性名 | 具体的属性名称 | id, source, channel |

**命名示例**：

```javascript
// 事件命名
"chat_page_view"           // 聊天页面浏览
"chat_message_submit"      // 聊天消息提交
"chat_robot_response"     // 机器人响应
"chat_human_connect"      // 人工接入
"chat_session_end"        // 会话结束
"chat_satisfaction_submit" // 满意度提交

// 属性命名
"user_id"                 // 用户ID
"session_id"              // 会话ID
"message_type"            // 消息类型
"channel_source"          // 渠道来源
"response_time"          // 响应时间
"agent_id"                // 客服ID
```

### 2.2 核心埋点事件

#### 2.2.1 客户入口事件

```javascript
// 事件：chat入口页浏览
{
  event: "chat_entrance_view",
  properties: {
    // 通用属性
    user_id: "U123456",          // 用户ID（脱敏）
    session_id: "S789012",         // 会话ID
    timestamp: 1704067200000,     // 时间戳
    channel: "web",               // 渠道：web/app/wap/小程序

    // 入口属性
    entrance_type: "home_button", // 入口类型：首页按钮/客服悬浮球/订单页/帮助中心
    source_page: "product_detail", // 来源页面
    referrer: "https://xxx.com",  // 来源URL
    device_type: "PC",            // 设备类型：PC/Mobile/Pad
    os_type: "Windows",          // 操作系统
    browser: "Chrome",           // 浏览器
  }
}

// 事件：进入聊天页
{
  event: "chat_page_view",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,
    channel: "web",
    entrance_type: "home_button",
    page_url: "https://xxx.com/chat",
  }
}
```

#### 2.2.2 智能服务事件

```javascript
// 事件：机器人问题识别
{
  event: "chat_robot_recognize",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    // 问题识别属性
    input_text: "查询订单状态",     // 用户输入（脱敏）
    intent_category: "order_query", // 意图分类
    intent_confidence: 0.92,      // 识别置信度
    knowledge_id: "K001",         // 知识库ID
    answer_content: "您的订单已发货...", // 答案内容（脱敏）
  }
}

// 事件：机器人问题解决
{
  event: "chat_robot_resolve",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    intent_category: "order_query",
    resolve_status: "resolved",    // resolved/unresolved/escalated
    conversation_turns: 2,        // 对话轮次
    resolution_time: 15,         // 解决时长（秒）
  }
}
```

#### 2.2.3 人工服务事件

```javascript
// 事件：请求人工
{
  event: "chat_human_request",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    request_reason: "robot_unresolved", // 请求原因
    robot_resolve_turns: 3,      // 机器人处理轮次
    escalation_intent: "人工客服", // 升级意图表达
  }
}

// 事件：人工接入
{
  event: "chat_human_connect",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    agent_id: "A001",            // 客服ID
    agent_name: "张三",           // 客服姓名（脱敏）
    agent_group: "华南组",        // 客服组
    queue_name: "普通客服",       // 队列名称
    wait_duration: 45,          // 等待时长（秒）
    queue_position: 3,          // 排队位置
  }
}

// 事件：人工会话开始
{
  event: "chat_human_session_start",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    agent_id: "A001",
    user_message_count: 5,       // 用户消息数
    agent_message_count: 3,      // 客服消息数
  }
}
```

#### 2.2.4 会话结束事件

```javascript
// 事件：会话结束
{
  event: "chat_session_end",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    end_type: "user_close",      // 结束类型：user_close/agent_close/system_close
    session_duration: 320,      // 会话总时长（秒）
    total_messages: 12,          // 总会话消息数
    robot_messages: 8,          // 机器人消息数
    human_messages: 4,          // 人工消息数
    escalation_count: 0,        // 升级次数

    // 问题解决属性
    resolution_status: "resolved", // resolved/unresolved
    is_first_resolved: true,    // 是否首次解决
  }
}

// 事件：满意度评价
{
  event: "chat_satisfaction_submit",
  properties: {
    user_id: "U123456",
    session_id: "S789012",
    timestamp: 1704067200000,

    satisfaction_score: 5,      // 满意度评分（1-5）
    is_satisfied: true,         // 是否满意
    feedback_tags: ["响应快", "专业"], // 反馈标签
    feedback_text: "服务很好...", // 反馈文本（脱敏）
    has_feedback: true,         // 是否有文字反馈
  }
}
```

### 2.3 用户属性设计

| 属性名称 | 字段 | 类型 | 说明 |
|---------|-----|-----|-----|
| 用户ID | user_id | String | 脱敏处理 |
| 用户等级 | user_level | String | VIP/普通/新用户 |
| 客户类型 | customer_type | String | 个人/企业 |
| 会员等级 | member_level | String | 青铜/白银/黄金/钻石 |
| 注册时长 | register_days | Integer | 注册天数 |
| 累计订单数 | total_orders | Integer | 累计订单数 |
| 累计消费金额 | total_amount | Decimal | 累计消费金额 |
| 归属区域 | region | String | 所属区域 |
| 首选渠道 | preferred_channel | String | 首选联系渠道 |
| 历史咨询次数 | historical_contacts | Integer | 历史咨询次数 |

### 2.4 会话属性设计

| 属性名称 | 字段 | 类型 | 说明 |
|---------|-----|-----|-----|
| 会话ID | session_id | String | 唯一标识 |
| 渠道来源 | channel | String | web/app/wap/小程序 |
| 入口类型 | entrance_type | String | 入口位置 |
| 设备类型 | device_type | String | PC/Mobile/Pad |
| 问题类型 | issue_category | String | 问题大类 |
| 问题细类 | issue_subcategory | String | 问题小类 |
| 服务类型 | service_type | String | 咨询/投诉/售后 |
| 会话来源 | session_source | String | 首次/复访 |
| 复访原因 | recontact_reason | String | 复访原因 |

---

## 三、数据字典规范

### 3.1 渠道编码

| 渠道编码 | 渠道名称 | 说明 |
|---------|---------|-----|
| WEB | 网页端 | PC端网页 |
| APP | APP端 | iOS/Android |
| WAP | H5端 | 移动端网页 |
| MINI | 小程序 | 微信/支付宝小程序 |
| WX | 微信客服 | 微信公众号/小程序 |
| WB | 微博 | 微博客服 |
| ALI | 支付宝 | 支付宝小程序/生活号 |

### 3.2 问题类型编码

| 问题大类 | 问题细类 | 编码规则 |
|---------|---------|---------|
| 咨询类 | 商品咨询、价格咨询、活动咨询 | CONS-XXX |
| 订单类 | 订单查询、订单修改、订单取消 | ORDR-XXX |
| 售后类 | 退款申请、退货申请、换货申请 | SRVC-XXX |
| 投诉类 | 服务投诉、商品投诉、物流投诉 | CMPL-XXX |
| 建议类 | 功能建议、服务建议 | SUGG-XXX |
| 其他类 | 其他问题 | OTHR-XXX |

### 3.3 服务类型编码

| 服务类型 | 编码 | 说明 |
|---------|-----|-----|
| 售前咨询 | pre_sale | 购买前的咨询 |
| 售中跟进 | sale_process | 购买中的问题跟进 |
| 售后服务 | after_sale | 购买后的服务支持 |
| 投诉处理 | complaint | 客户投诉处理 |
| 主动服务 | proactive | 主动外呼服务 |

### 3.4 结果编码

| 结果类型 | 编码 | 说明 |
|---------|-----|-----|
| 已解决 | resolved | 问题已完全解决 |
| 部分解决 | partially_resolved | 问题部分解决 |
| 未解决 | unresolved | 问题未解决 |
| 升级处理 | escalated | 升级至其他部门处理 |
| 无法处理 | unprocessable | 技术或权限限制无法处理 |
| 客户放弃 | customer_abandon | 客户主动关闭会话 |

---

## 四、数据质量监控

### 4.1 质量监控维度

| 维度 | 检查规则 | 告警阈值 |
|-----|---------|---------|
| 完整性 | 必填字段非空率 | <95% |
| 一致性 | 字段值分布异常 | 偏离基线>20% |
| 时效性 | 数据延迟时间 | >5分钟 |
| 准确性 | 计算结果校验 | 误差>1% |
| 唯一性 | ID重复率 | >0.1% |

### 4.2 质量监控规则示例

```sql
-- 规则1：会话记录完整性检查
SELECT
  COUNT(*) as total_sessions,
  SUM(CASE WHEN session_id IS NULL THEN 1 ELSE 0 END) as missing_session_id,
  SUM(CASE WHEN start_time IS NULL THEN 1 ELSE 0 END) as missing_start_time,
  SUM(CASE WHEN end_time IS NULL THEN 1 ELSE 0 END) as missing_end_time
FROM chat_sessions
WHERE date = CURRENT_DATE;

-- 规则2：会话时长异常检查
SELECT
  COUNT(*) as total_sessions,
  SUM(CASE WHEN duration < 0 OR duration > 7200 THEN 1 ELSE 0 END) as abnormal_duration
FROM chat_sessions
WHERE date = CURRENT_DATE;

-- 规则3：满意度数据分布检查
SELECT
  satisfaction_score,
  COUNT(*) as count
FROM chat_sessions
WHERE date = CURRENT_DATE
GROUP BY satisfaction_score
ORDER BY satisfaction_score;
```

### 4.3 数据质量日报模板

```markdown
# 数据质量日报：2024-01-15

## 一、整体数据概况

| 指标 | 今日数据 | 昨日数据 | 环比变化 |
|-----|---------|---------|---------|
| 会话总量 | 12,345 | 11,876 | +3.9% |
| 有效会话 | 12,123 | 11,654 | +4.0% |
| 数据完整率 | 99.2% | 99.1% | +0.1% |

## 二、质量问题汇总

| 问题类型 | 涉及会话数 | 影响说明 |
|---------|-----------|---------|
| 字段缺失 | 23 | 渠道来源字段为空 |
| 时长异常 | 5 | 会话时长>2小时 |
| 评价异常 | 2 | 评分超出1-5范围 |

## 三、根因分析与处理

| 问题 | 根因 | 处理措施 | 责任人 | 完成时间 |
|-----|-----|---------|-------|---------|
| 渠道来源为空 | H5端埋点版本未更新 | 推送新版本埋点SDK | 前端团队 | 2024-01-16 |
| 评价异常 | 历史数据修复 | 数据清洗脚本执行 | 数据团队 | 2024-01-15 |

## 四、待优化事项

- [ ] 推进H5端SDK升级
- [ ] 完善埋点校验机制
- [ ] 建立数据质量SLA
```

---

## 五、数据安全规范

### 5.1 敏感字段清单

| 字段类型 | 脱敏方式 | 示例 |
|---------|---------|-----|
| 用户ID | MD5哈希 | U123456 → 6d9d08a2... |
| 手机号 | 部分掩码 | 138****5678 |
| 姓名 | 部分掩码 | 张*丰 |
| 地址 | 部分掩码 | 北京市*** |
| 订单号 | 脱敏 | OD123456 → ORD***456 |
| 金额 | 保留精度 | 1234.56 |
| 评价内容 | 关键词过滤 | 涉敏词替换为*** |

### 5.2 权限控制规范

| 角色 | 可访问数据范围 | 数据脱敏要求 |
|-----|---------------|-------------|
| 一线客服 | 本会话数据 | 脱敏处理 |
| 客服组长 | 本组数据 | 脱敏处理 |
| 运营分析 | 聚合数据 | 脱敏处理 |
| 数据分析师 | 明细数据 | 申请审批 |
| 管理员 | 全量数据 | 全量权限 |

### 5.3 数据存储规范

- **存储周期**：明细数据保留3年，聚合数据保留5年
- **备份策略**：每日全量备份，每周增量备份
- **访问日志**：记录所有明细数据访问操作
- **数据销毁**：超过存储周期的数据定期清理