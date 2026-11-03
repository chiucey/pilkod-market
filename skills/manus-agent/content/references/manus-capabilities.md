# Manus-Agent 能力详解与执行策略

---

## 一、能力地图与工具选择

| 任务类型 | 推荐工具/方式 |
|---------|-------------|
| 文件读取（docx/xlsx/csv/pdf）| Python脚本（pandas/openpyxl/pdfplumber）|
| 数据清洗/去重 | Python + 正则 |
| 统计分析 | Python（pandas/numpy）|
| 图表生成 | Python（matplotlib/plotly）或 HTML + ECharts |
| 网页部署 | `deploy` 工具 |
| **公开网页信息搜索** | `batch_web_search` + `extract_content_from_websites` |
| **登录后网页数据抓取** | **`browser-deep` 模块（browser 工具）** |
| **多步骤网页操作（全自动）** | **`browser-deep` 模块** |
| **定期监控推送** | `cron` + `browser-deep` + `message` |
| 报告生成 | Markdown → Python-docx 或 HTML |
| 定时任务 | `cron`（isolated session，announce delivery）|
| 发送通知 | `message` 工具（若配置了渠道）|

---

## 二、browser-deep 模块集成说明

browser-deep 是 Manus-Agent 执行层最重要的能力扩展，专门处理**需要浏览器环境**的任务。

### 何时调用 browser-deep

满足以下任一条件时，应调用 browser-deep 模块：

1. 目标网站需要登录才能访问数据
2. 需要执行多步骤操作（搜索→点击→提取→翻页）
3. 页面内容通过 JavaScript 动态渲染，curl/requests 无法直接获取
4. 需要提取的内容分散在多个标签页中
5. 需要填表并提交获取结果
6. 数据提取需要维持 Session/Cookie 状态

### browser-deep 调用流程（在 manus-agent 中）

```
Manus-Agent 任务规划
    ↓
识别为"需要浏览器操作"类型
    ↓
调用 browser-deep（通过 browser 工具）
    ↓
browser.start()  → 启动浏览器
    ↓
执行操作链（见下方典型模板）
    ↓
提取结构化数据（evaluate/snapshot）
    ↓
browser.close()  → 关闭浏览器
    ↓
返回结构化数据给 Manus-Agent
    ↓
Manus-Agent 继续执行：分析 → 生成 → 交付
```

---

## 三、典型任务执行模板

### 模板A：公开数据抓取（无需登录）

```
步骤1：batch_web_search（并发多关键词）
步骤2：extract_content_from_websites（批量抓取页面）
步骤3：Python 数据清洗与结构化
步骤4：生成分析报告（Markdown/HTML）
步骤5：deploy 部署（可选）
步骤6：汇报交付
```

### 模板B：登录后数据提取（核心场景）

```
步骤1：browser.start()  → 启动独立浏览器
步骤2：navigate(登录页 URL)
步骤3：snapshot(获取输入框 ref)
步骤4：type(用户名 ref, 用户名) + type(密码 ref, 密码)
步骤5：click(登录按钮) + wait(跳转完成)
步骤6：snapshot(验证登录成功)
步骤7：navigate(目标数据页 URL)
步骤8：wait(数据加载) + snapshot
步骤9：evaluate(自定义 JS 提取结构化数据)
步骤10：判断是否有下一页 → 循环步骤8-9
步骤11：close()  → 关闭浏览器
步骤12：Python 数据分析 + 生成报告/图表
步骤13：汇报交付
```

### 模板C：定时监控任务

```
步骤1：cron 配置 isolated session job
步骤2：每次触发时，browser-deep 抓取最新数据
步骤3：与上次数据对比（如启用 diff）
步骤4：生成增量报告（如有变化）
步骤5：message 推送到用户渠道（如配置）
步骤6：announce 到 main session
```

---

## 四、执行决策规则

### 4.1 任务类型快速判断

```
问自己：这个任务需要访问网页吗？
  ↓ 是
目标网站需要登录吗？
  ↓ 否 → 调用 batch_web_search + extract_content_from_websites
  ↓ 是 → 调用 browser-deep
  ↓ 不确定 → 先尝试 extract_content_from_websites
           失败后切换到 browser-deep
```

### 4.2 步骤数量控制

- 简单任务：2-3步
- 中等任务：4-6步
- 复杂任务：7-10步
- 超过10步：拆成两个子任务或优先完成核心步骤

### 4.3 降级策略

| 情况 | 降级方式 |
|------|---------|
| 某个工具不可用 | 用其他工具替代（如部署失败则改为输出HTML文件）|
| 数据格式读取失败 | 尝试其他解析方式，仍失败则告知用户并提供手动方案 |
| 搜索无结果 | 调整关键词重试，仍无则如实告知并提供替代分析 |
| browser-deep 失败 | 降级到 extract_content_from_websites 尝试 |
| 任务过于庞大 | 聚焦核心产出，省略附加内容，告知用户可后续深化 |

---

## 五、结果交付规范

### 5.1 文件输出

- 所有生成的文件存入 `/workspace/outputs/任务名-日期/` 目录
- 优先输出可直接使用的文件（HTML/docx/xlsx）
- 报告类文件优先 Markdown，可转换格式的再转换

### 5.2 链接交付

- 已部署的网页/应用，输出公网访问链接
- 使用 `deploy` 工具后返回的 URL 即为交付链接

### 5.3 日志记录

每次执行完毕，在 `memory/manus-log-YYYY-MM-DD.md` 中记录：
```
## 执行日志 YYYY-MM-DD HH:mm

任务：[任务描述]
执行者：manus-agent（含 browser-deep 调用）
交付物：[路径或链接]
执行步骤：[步骤列表，含 browser-deep 操作记录]
耗时：[估算分钟]
备注：[备注]
```

---

## 六、自主管控规则

### 6.1 提前终止条件

如遇到以下情况，自主终止任务并汇报：
- 核心数据完全无法获取（无替代来源）
- 目标系统明确拒绝访问
- Session/Cookie 失效且无法重新登录
- 任务在3倍预期时间内仍未完成

### 6.2 验证码/反爬处理

当 browser-deep 报告 `CAPTCHA_DETECTED` 或检测到反爬拦截时：
1. 记录当前操作步骤和页面状态
2. 通知用户需要人工介入（提供截图或快照作为凭证）
3. 用户处理完毕后，从断点恢复继续执行
