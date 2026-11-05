---
name: openrouter
description: 从第一性原理深度解析OpenRouter的核心价值与使用方法。当用户询问OpenRouter是什么、如何接入多模型路由、OpenRouter与直接接API的区别、如何用OpenRouter做模型治理、成本控制或构建AI产品时使用此技能。
---

# OpenRouter：第一性原理深度解析

## 核心原点

**OpenRouter 本质上不是"一个模型"，而是"多模型访问与路由层"。**

从第一性原理看，OpenRouter 不是"又一个大模型"。它更像一层 **LLM 路由与控制层**。

它解决的不是"模型够不够强"，而是更底层的两个问题：

1. 如何更低成本地接入很多模型
2. 如何在不稳定、多供应商、多价格体系下，持续稳定地调用模型

### 一句话定义

> **OpenRouter = 模型市场 + 路由器 + 控制平面**
>
> 把模型这件事，从一次性接入，升级成可运营、可切换、可治理的系统能力。

---

## 一、第一性原理基础

任何 AI 应用，落地时都绕不开 4 个底层约束：

| 约束 | 问题 |
|------|------|
| 模型很多 | 接口不统一 |
| 单一供应商 | 会带来锁定风险 |
| 价格变化 | 限流、可用性一直在变 |
| 业务上线后 | 最怕中断、涨价、迁移困难 |

市场真正需要的，不只是"更强模型"，而是一个中间层，帮你统一处理：

- 模型选择
- API 兼容
- 供应商路由
- 故障切换
- 成本控制
- 团队治理

**OpenRouter 就是这层。**

---

## 二、What - OpenRouter 是什么

OpenRouter 是一个**统一的 LLM API 网关**。

- 一个账号、一套 key、一个主接口，访问 300+ 模型、60+ 活跃提供商
- **"One API for Any Model"**
- **"OpenAI SDK works out of the box"**

### 它不是什么

它不是替代 OpenAI、Anthropic、Google 这些模型厂商，而是把它们**抽象成统一入口**。

### 核心价值

- 统一 API
- 统一计费与分析
- 多家上游可用性汇聚
- 请求/响应格式与 OpenAI Chat API 高度相似

---

## 三、Why - 为什么要用 OpenRouter

### 第一层原因：降低复杂度

如果你直接接多个模型厂商，你要维护多套：

- API Key
- SDK
- 参数差异
- 限流规则
- 错误处理
- 计费面板

**OpenRouter 把这些收敛成一个统一接口**，并把 schema 规范化为接近 OpenAI Chat API 的格式。

### 第二层原因：避免供应商锁定

如果你的产品只绑一个模型，一旦价格、政策、性能、可用性变化，你的迁移成本会很高。

OpenRouter 让你把"业务代码"与"具体模型/提供商"解耦。

### 第三层原因：提高可用性

- 默认会在同一模型的多个提供商之间做路由
- 默认偏向价格更优的提供商
- 主模型失败、限流或拒答时**自动切换到备选模型**
- **启用 routing/fallback 时，只对成功的运行计费**

### 第四层原因：更容易控成本

- **推理价格不加价**，模型目录展示的价格就是你支付的推理价格
- 买 credits 时的充值手续费约 5.5%（最低 0.80 美元）

### 第五层原因：治理能力更强

| 功能 | 说明 |
|------|------|
| **BYOK** | 自带上游 provider key |
| **ZDR** | 按端点控制零数据保留 |
| **Presets** | 团队统一配置 |
| **Analytics** | 统一看使用情况 |

---

## 四、Who - 谁适合用 OpenRouter

最适合 4 类人：

### A. 做 AI 产品的人

要接多个模型做 A/B 测试、成本优化、自动切换，这类最适合。

### B. 做 Agent / Workflow 的人

Agent 对可用性、工具调用、多模型协作更敏感。OpenRouter 的 Responses API Beta 明确支持：
- reasoning
- tool calling
- web search

### C. 想减少供应商绑定的人

不想把产品绑死在单一模型上，OpenRouter 很适合做中间层。

### D. 团队协作场景

- 不同环境、不同业务线、不同成员共享统一配置
- 按环境创建不同 API key
- 设置 cap、alerts 和 activity logs

---

## 五、When - 什么时候该用 / 不该用

### 更适合用 OpenRouter 的情况

- 你要同时试很多模型
- 上线的是正式产品，需要更高可用性
- 想把模型切换从代码里解耦
- 要统一计费、统一监控
- 希望在价格和速度之间动态平衡
- 想保留 BYOK 的灵活性

### 不一定适合的情况

- 你只用一家模型，而且长期不会切换
- 你需要某厂商最原生、最特定的私有能力
- 你的合规策略要求只走某家私有专线或固定区域

> 直接接原厂，可能更简单。

---

## 六、Where - 在哪里使用

### A. 控制台

在 OpenRouter 网站上：

- 注册账号
- 购买 credits
- 创建 API key
- 查看模型目录
- 配置 Presets / Privacy / BYOK / Logs 等

### B. API

```
https://openrouter.ai/api/v1/chat/completions
https://openrouter.ai/api/v1/responses
```

**Responses API Beta** 是无状态的，每次请求都要自己带上完整上下文。

---

## 七、How - 如何使用 OpenRouter

### 最小可用路径（5步）

#### 第1步：注册并充值

创建账号 → 添加 credits → 创建 API key。credits 是预存款，用于后续推理消费。

#### 第2步：把它当成 OpenAI 兼容接口来接

两种方式：
1. 直接 POST 到 OpenRouter 接口
2. **使用 OpenAI SDK，把 baseURL 改成 `https://openrouter.ai/api/v1`**

#### 第3步：先选一个模型 slug 跑通

例如 `openai/gpt-5.2`。模型目录 API 会返回标准化元数据：
- id、上下文长度
- 支持参数
- 价格
- 输入输出模态

#### 第4步：再做路由与 fallback

**先跑通，再优化。不要一上来就堆复杂路由。**

#### 第5步：最后做治理

把以下都收进 **Presets**，避免散落在代码里：

- provider 偏好
- fallback 模型
- system prompt
- 参数模板

---

## 八、How much - 成本怎么理解

OpenRouter 的成本要拆成三层：

### A. 模型推理费

**不加价**，按模型目录展示的价格付费。

不同模型可按以下方式计费：
- 输入 token
- 输出 token
- 请求次数
- 图片
- web search
- reasoning token

### B. 充值手续费

买 credits 时收 **5.5%** 手续费，最低 0.80 美元。

### C. BYOK 费用

- 每月前 100 万次 BYOK 请求免费
- 之后按正常费用的 **5%** 收费

### 其他说明

- Pay-as-you-go：**无最低消费、无锁定**
- 免费层：50 次/天、20 RPM

---

## 九、正确使用指南（5大用法）

### 用法一：把它当统一入口，不要当神奇模型

**最常见误区**：把 OpenRouter 当成一个独立大模型。

**更准确的理解**：
> 你在做的，不是"选 OpenRouter"，而是"通过 OpenRouter 管理多模型策略"。

### 用法二：先固定模型，后做 fallback

建议顺序：

1. 先用一个模型跑通主链路
2. 再加同模型多 provider 路由
3. 最后再加跨模型 fallback

**这样问题定位最清楚。**

### 用法三：把"业务语义"和"模型实现"分开

**代码里不要写死**：
- 这个接口永远用某某模型
- 这个 prompt 永远跟某 provider 绑定

**更好的做法**：
- 代码里只表达"这是客服分类器"
- 具体用什么模型、什么 provider、什么参数，由 **Preset** 决定

### 用法四：对正式业务，优先设计三层兜底

| 层级 | 说明 |
|------|------|
| **第一层** | 同模型多 provider —— 同一个模型交给多个 provider 路由 |
| **第二层** | 跨模型 fallback —— 主模型失败时切到备选模型 |
| **第三层** | BYOK —— 核心业务保留自己的上游 key |

### 用法五：隐私要求高时，先看数据策略

OpenRouter 文档说明：

- 默认**不存储** prompts / responses
- 但会保存请求**元数据**（token 数、延迟等）
- provider 侧的数据保留策略仍可能不同
- ZDR 是按端点能力管理的，不是所有路径天然等价

**高敏场景的正确动作**：

1. 检查 provider policy
2. 开启合适的 privacy 设置
3. 必要时限制 provider / region

---

## 十、最小接入示例

用 OpenAI SDK 的方式最省事：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_API_KEY"
)

resp = client.chat.completions.create(
    model="openai/gpt-5.2",
    messages=[
        {"role": "system", "content": "你是一个简洁的中文助手。"},
        {"role": "user", "content": "请用一句话解释第一性原理。"}
    ]
)

print(resp.choices[0].message.content)
```

**核心价值**：你后面可以很容易把 model 换掉，甚至进一步换成 preset。

---

## 十一、快速开始顺序

如果现在就要开始，用这条顺序最稳：

1. 注册 OpenRouter
2. 充少量 credits
3. 创建一个 dev key
4. 用 OpenAI SDK 改 baseURL 先跑通
5. 选 1 个主模型
6. 加 1 个 fallback 模型
7. 把 prompt 和参数收进 preset
8. 再决定是否接 BYOK / ZDR / region routing

---

## 极简结论

### 为什么用 OpenRouter

因为你真正需要的是**稳定性、灵活性、成本控制和治理**，而不是只连上某一家模型。

### 如何用 OpenRouter

1. 先把它当**统一入口**
2. 再把路由、fallback、preset、BYOK、隐私策略**逐层加上去**

---

## 四大核心价值总结

| 问题 | OpenRouter 解决方案 |
|------|---------------------|
| **接入成本** | 统一 API，减少重复接入 |
| **连续性** | provider 路由 + model fallback，降低中断风险 |
| **经济性** | 默认价格优先路由，推理价格不加价 |
| **治理** | Presets、BYOK、ZDR、日志与活动追踪，方便团队化 |
