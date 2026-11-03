# NLP智能客服机器人设计模式参考

## 一、流程类型设计模式

### 1.1 单轮问答模式

#### 基础模式

```
[用户输入] → [意图识别] → [知识库检索] → [答案匹配] → [回复输出]
```

#### 变体模式

**带置信度的单轮问答：**
```
[用户输入] → [意图识别 + 置信度计算]
    ├─ 高置信度(>0.85) → 直接回复
    ├─ 中置信度(0.5-0.85) → 回复 + 请用户确认
    └─ 低置信度(<0.5) → 澄清问题
```

### 1.2 多轮对话模式

#### 信息收集型

```
开始 → [询问字段1] → [询问字段2] → ... → [询问字段N] → [信息校验] → [生成答案] → 结束
```

**设计要点：**
- 每个字段询问独立，支持中途退出
- 支持上下文补充和修正
- 字段缺失时的默认值或跳过策略

#### 问题诊断型

```
开始 → [收集症状] → [追问细节] → [缩小范围] → [定位问题] → [提供方案] → 结束
```

**设计要点：**
- 使用决策树结构
- 支持回退到上一步
- 记录诊断路径用于优化

### 1.3 混合模式

#### 模式结构

```
[主入口] → [单轮快速响应] / [多轮深度服务]
    │
    ├─ 简单问题 → 单轮处理
    ├─ 复杂问题 → 多轮处理
    └─ 复合问题 → 任务分解 → 分发处理
```

## 二、意图识别设计模式

### 2.1 意图层次结构

```
L1: 一级意图（业务域）
  │
  └─ L2: 二级意图（业务功能）
       │
       └─ L3: 三级意图（具体场景）
```

**示例（电商场景）：**
```
shopping (L1)
├── product_inquiry (L2)
│   ├── price_query (L3)
│   ├── stock_query (L3)
│   └── specification_query (L3)
├── order_management (L2)
│   ├── order_status (L3)
│   ├── order_cancel (L3)
│   └── order_modify (L3)
└── aftersales (L2)
    ├── return_request (L3)
    ├── refund_status (L3)
    └── complaint (L3)
```

### 2.2 意图混淆处理

**策略1: 优先级排序**
```
意图A (优先级1) → 意图B (优先级2) → 意图C (优先级3)
```

**策略2: 置信度阈值**
```
if top_confidence > threshold1:
    直接返回
elif top_confidence > threshold2:
    返回 + 确认
else:
    澄清或追问
```

**策略3: 意图组合**
```
检测到意图A + 意图B → 执行意图A后提示意图B相关
```

## 三、交互设计模式

### 3.1 文本交互模式

#### 渐进式披露

```
[简短回复] → [用户追问] → [详细说明] → [补充信息]
```

**适用场景：**
- 复杂问题的解答
- 需要用户逐步了解的场景
- 避免信息过载

#### 卡片式回复

```
┌─────────────────────────┐
│  标题                    │
├─────────────────────────┤
│  内容说明                │
│  • 要点1                 │
│  • 要点2                 │
├─────────────────────────┤
│  [操作按钮1] [操作按钮2] │
└─────────────────────────┘
```

### 3.2 API交互模式

#### 同步查询模式

```
用户请求 → 参数提取 → API调用 → 结果格式化 → 回复输出
```

#### 异步处理模式

```
用户请求 → 任务创建 → 任务确认 → 后台处理 → 结果通知
```

**适用场景：**
- 耗时的数据处理
- 需要人工审核的操作
- 批量任务处理

### 3.3 富媒体配置模式

#### 图片配置

```json
{
  "type": "image",
  "url": "https://cdn.example.com/image.jpg",
  "alt": "产品展示图",
  "thumbnail": "https://cdn.example.com/thumb.jpg",
  "actions": [
    {"label": "查看大图", "type": "enlarge"},
    {"label": "保存", "type": "download"}
  ]
}
```

#### 视频配置

```json
{
  "type": "video",
  "url": "https://cdn.example.com/video.mp4",
  "poster": "https://cdn.example.com/poster.jpg",
  "duration": 120,
  "controls": ["play", "pause", "mute", "fullscreen"],
  "subtitle": {
    "url": "https://cdn.example.com/subtitle.vtt",
    "default": true
  }
}
```

## 四、策略配置模式

### 4.1 寒暄处理策略

#### 寒暄分类

| 类型 | 示例 | 处理策略 |
|-----|------|---------|
| 问候 | 你好、早上好 | 简短问候 + 询问需求 |
| 感谢 | 谢谢、多谢 | 礼貌回应 + 询问其他 |
| 道歉 | 对不起、抱歉 | 表达歉意 + 询问能否帮助 |
| 告别 | 再见、拜拜 | 友好告别 + 祝福 |
| 闲聊 | 今天天气不错 | 简短回应 + 自然转回业务 |

#### 处理流程

```
用户输入 → 寒暄检测
    │
    ├─ 是寒暄 → 寒暄库匹配 → 生成回复 → 自然转回业务
    └─ 否寒暄 → 业务意图处理
```

### 4.2 敏感内容处理

#### 敏感信息识别

```json
{
  "sensitive_fields": [
    {"name": "身份证号", "pattern": "\\d{17}[\\dXx]", "action": "mask"},
    {"name": "手机号", "pattern": "1[3-9]\\d{9}", "action": "mask"},
    {"name": "银行卡", "pattern": "\\d{16,19}", "action": "mask"},
    {"name": "密码", "pattern": "(password|pwd|密码)", "action": "warn"}
  ]
}
```

#### 合规检查规则

```json
{
  "compliance_rules": [
    {"type": "medical_advice", "action": "escalate"},
    {"type": "financial_investment", "action": "disclaimer"},
    {"type": "legal_consultation", "action": "escalate"},
    {"type": "political_content", "action": "block"}
  ]
}
```

### 4.3 转人工策略

#### 转人工触发条件配置

```json
{
  "escalation_triggers": [
    {"type": "explicit_request", "keywords": ["人工", "客服", "转接"], "confidence": 0.9},
    {"type": "emotion_detect", "negative_score": 0.8, "consecutive_turns": 2},
    {"type": "failed_attempts", "max_attempts": 3},
    {"type": "high_risk_operation", "operations": ["refund_cancel", "complaint"]},
    {"type": "system_error", "error_codes": ["timeout", "api_error"]}
  ]
}
```

#### 转人工流程

```
触发转人工 → 情绪安抚话术 → 上下文保存 → 技能组路由 → 排队等待 → 超时处理
```

## 五、对话管理设计模式

### 5.1 状态机设计

#### 简单状态机

```
INIT → PROCESSING → RESPONDING → COMPLETED
                        ↓
                   INTERRUPTED → TRANSFER_HUMAN
```

#### 复杂状态机（多轮对话）

```
状态: {session_id, current_node, context_data, history}

节点: {
  node_id,
  type: "ask|confirm|inform|action",
  params: {...},
  transitions: [
    {condition, next_node, action}
  ]
}
```

### 5.2 上下文管理

#### 上下文数据结构

```json
{
  "session_id": "xxx",
  "user_id": "xxx",
  "turn_count": 5,
  "context": {
    "collected_info": {
      "order_id": "ORD123",
      "product_name": "产品A"
    },
    "intent_stack": ["product_inquiry", "price_query"],
    "last_node": "price_query",
    "metadata": {
      "channel": "web",
      "device": "mobile"
    }
  },
  "history": [
    {"role": "user", "content": "...", "timestamp": 1234567890},
    {"role": "bot", "content": "...", "timestamp": 1234567891}
  ]
}
```

### 5.3 异常处理设计

#### 输入异常处理

| 异常类型 | 处理策略 |
|---------|---------|
| 空输入 | 礼貌提示输入内容 |
| 无效格式 | 格式示例 + 重新输入 |
| 乱码/特殊字符 | 自动清理 + 提示 |
| 超长输入 | 截断处理 + 提示 |

#### 系统异常处理

```
API超时 → 重试N次 → 失败 → 友好提示 + 备选方案
API错误 → 错误分类 → 针对性错误消息
系统宕机 → 预设兜底回复 → 问题记录
```

## 六、体验优化设计模式

### 6.1 响应体验优化

#### 流式输出模式

```python
async def stream_response(answer: str, websocket):
    """逐句流式输出，提升感知响应速度"""
    sentences = split_sentences(answer)
    for sentence in sentences:
        await websocket.send(sentence)
        await asyncio.sleep(0.1)  # 控制输出节奏
```

#### Typing指示器

```
用户发送消息 → 系统立即返回typing状态 → 实际处理 → 真实回复
```

### 6.2 纠错容错机制

#### 输入纠错

```json
{
  "corrections": {
    "enable": true,
    "types": [
      {"type": "pinyin", "example": "wenzhen" → "问诊"},
      {"type": "typo", "threshold": 0.8},
      {"type": "abbr", "mapping": {"VIP": "会员"}}
    ]
  }
}
```

#### 多轮修正

```
用户: 我想查一下订单 [订单号]
助手: 您想查询的订单号是[订单号]
用户: 不对，是[新订单号]
助手: 好的，已更新为[新订单号]，为您查询...
```

### 6.3 个性化策略

#### 用户画像适配

```json
{
  "persona_rules": {
    "new_user": {
      "response_style": "tutorial",
      "detail_level": "high",
      "add_guidance": true
    },
    "frequent_user": {
      "response_style": "concise",
      "detail_level": "medium",
      "skip_basics": true
    },
    "vip_user": {
      "response_style": "premium",
      "detail_level": "high",
      "personalized_greeting": true
    }
  }
}
```

## 七、质量评估指标

### 7.1 对话质量指标

| 指标 | 目标值 | 说明 |
|-----|-------|------|
| 意图识别准确率 | ≥95% | 正确识别的意图数/总意图数 |
| 首次解决率 | ≥80% | 单轮对话解决问题的比例 |
| 平均对话轮次 | ≤5轮 | 复杂问题平均对话轮数 |
| 用户满意度 | ≥4.5/5 | 交互后用户评分 |
| 转人工率 | ≤15% | 需要人工介入的比例 |

### 7.2 性能指标

| 指标 | 目标值 |
|-----|-------|
| 首响应时间 | <500ms |
| 平均响应时间 | <1s |
| 并发处理能力 | >1000 QPS |
| 系统可用性 | >99.9% |