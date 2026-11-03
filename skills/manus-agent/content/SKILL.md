---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 526d9017c302d22cfd3be02f4c34f9fb
    PropagateID: 526d9017c302d22cfd3be02f4c34f9fb
    ReservedCode1: 304402203aa8a224e174faad176fd250e90feb354fe8cbf6a358856d4416f0987662805902206068dbca7b206864df70fc363b6b21e5921e4667ae89453ad884f2e014fc8f8c
    ReservedCode2: 3045022028473991769d8663aa047de999f0ef818fd1242faca0896f71e587b32aaa564c022100ae1cbdeffb6574e4752ef99ded341a7004291119141b644db966dcfccda0a6e7
description: 类 Manus 通用任务执行者。当用户说"像 Manus 一样做xxx"、"帮我自主完成xxx（多步骤）"、"自动执行：xxx"等时触发。此技能将复杂任务拆解为多个步骤，自主规划并依次执行，交付完整结果，无需用户中途确认。触发关键词：像Manus一样、像manus一样，自主完成、多步骤执行、自动执行，分析并生成、帮我做、做完它、代替我完成。
name: manus-agent
---

# Manus-Agent：类 Manus 通用任务执行者

## 核心能力

接收一个复杂的、可能是多步骤的任务，**自主拆解、执行并交付完整结果**，中途不向用户请求确认。

**核心原则：用户已授权。**

---

## 执行流程

```
接收任务描述
    ↓
理解任务目标（识别关键产出）
    ↓
拆解执行步骤（2-10步，自然规划）
    ↓
依次执行（遇到错误自主尝试替代方案）
    ↓
交付成果（文件/链接/报告）
    ↓
汇报执行摘要
```

---

## 可调用工具模块

当任务需要浏览器自动化时，Manus-Agent 会调用 **browser-deep 模块**（已内置，无需额外安装）执行相关步骤。

### browser-deep 模块

| 能力 | 说明 |
|------|------|
| 登录后数据抓取 | 先完成登录，再进入数据提取 |
| 多步骤网页操作 | 搜索→点击→提取→导出，全自动串联 |
| JS 渲染页面 | 先 wait 再抓取，支持动态内容 |
| 表单填写提交 | 自动填表、自动提交、自动确认 |
| 分页数据提取 | 自动翻页+循环提取 |
| 动态页面监控 | 轮询等待关键元素变化 |

**browser-deep 模块已在 Manus-Agent 能力范围内，可直接调用。**

---

## 能力地图（与 browser-deep 协同）

| 任务类型 | 执行路径 |
|---------|---------|
| 公开数据搜索/抓取 | `batch_web_search` → 整理 → 生成报告 |
| **登录后可访问数据抓取** | **browser-deep**（登录→导航→提取）→ 分析 → 报告 |
| 多步网页操作（全自动）| **browser-deep**（操作链）→ 交付结果 |
| 定期监控+推送 | cron + **browser-deep**（定时抓取）→ message 推送 |
| 文件数据分析 | Python（pandas）→ 生成图表 → deploy |
| 搜索+深度调查 | `batch_web_search` + `extract_content_from_websites` → 整理报告 |

---

## 任务类型与工具选择

### 第一类：公开信息任务（无需登录）

**工具链**：`batch_web_search` + `extract_content_from_websites`

```
1. 多关键词并发搜索
2. 抓取目标页面内容
3. 内容结构化提取
4. 整理为报告/对比表
```

### 第二类：需要登录的数据任务（核心场景）

**工具链**：`browser-deep` 模块（browser 工具）

```
1. 启动浏览器（browser start）
2. 导航到登录页
3. 注入认证（cookies/手动登录）
4. 进入目标页面
5. 执行操作链（搜索→点击→提取）
6. 提取结构化数据
7. 关闭浏览器
8. 数据分析 + 生成报告
```

### 第三类：定时监控任务

**工具链**：`cron` + `browser-deep` + `message`

```
1. 配置 cron isolated session job
2. 每次触发：browser-deep 抓取数据
3. 对比历史数据（如有变化则生成报告）
4. 通过 message 推送到用户渠道
```

---

## 执行原则

### 错误自主处理

| 错误类型 | 处理策略 |
|---------|---------|
| 工具调用失败 | 等待1秒重试，最多3次 |
| 步骤失败 | 尝试替代方案（如搜索失败改用直接URL抓取）|
| 依赖文件不存在 | 自主判断用其他方式或跳过该步骤 |
| 任务过长 | 启用 cron 后台执行，完成后通知 |
| 验证码拦截 | **browser-deep** 抛出 `CAPTCHA_DETECTED`，在 skill 侧暂停流程等待人工处理 |

### 执行日志

每次执行后，在 `memory/manus-log-YYYY-MM-DD.md` 中记录：
```
## 执行日志 YYYY-MM-DD HH:mm

任务：[任务描述]
交付物：[路径或链接]
执行步骤：[步骤列表，含 browser-deep 调用记录]
耗时：[估算分钟]
备注：[备注]
```

---

## 输出格式

任务完成后，统一输出：

```
✅ 任务完成

📦 交付成果：
   - [成果1：文件路径/访问链接]
   - [成果2：...]

📋 执行摘要：
   - 执行步骤：[步骤1] → [步骤2 → browser-deep: 登录 → 抓取 → 提取] → [步骤3]
   - 耗时：约 X 分钟
   - 备注：[如有需人工处理的事项]
```

---

## 详细参考

- **browser-deep 模块规范**：`../browser-deep/SKILL.md`
- **browser-deep 进阶用法**：`../browser-deep/references/browser-advanced-usage.md`
- **能力策略参考**：`references/manus-capabilities.md`

---

## 使用示例

**触发方式（用户说）：**
> "像 Manus 一样，帮我去XX网站抓取我的订单数据，整理成Excel"
> "自主完成这个任务：登录XX平台，提取所有客户的交易记录，生成分析报告"
> "自动执行：每周五下午5点抓取XX后台数据，生成周报推送到我"
> "像manus一样，帮我从内部系统导出本月销售数据，做可视化页面"

**执行时内部流程（以登录类任务为例）：**
```
步骤1：browser-deep.start()  → 启动浏览器
步骤2：browser-deep.navigate(登录页)
步骤3：browser-deep.type(用户名框, 用户名) + type(密码框, 密码) + click(登录)
步骤4：browser-deep.wait()  → 等待登录完成
步骤5：browser-deep.navigate(目标数据页)
步骤6：browser-deep.evaluate(提取数据JS)
步骤7：browser-deep.close()  → 关闭浏览器
步骤8：Python 数据分析 + 生成 Excel
步骤9：汇报交付
```
