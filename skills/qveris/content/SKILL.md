# QVeris 数据引擎 · SKILL.md

> 插件版本：2026.3.23 | 更新：2026-03-29

## 插件简介

QVeris（qveris.ai / qveris.cn）是 AI Agent 数据接入引擎，整合 10,000+ 真实世界 API 接口，支持 A股、港股、美股、外汇、期货、宏观等多品类数据。

**已安装插件：`@qverisai/qveris`**

---

## 三个核心工具

### 1. qveris_discover
通过自然语言搜索可用工具接口。

```
输入示例：
- "A股实时行情"
- "股票历史K线"
- "北向资金流向"
- "财务报表数据"
- "期货持仓"
```

### 2. qveris_inspect
查看某个工具的详细参数和用法示例。

```
输入：工具ID（从 discover 结果中获取）
输出：参数说明、返回格式、调用示例
```

### 3. qveris_call
执行已发现的工具接口。

```
输入：工具ID + 参数 JSON
输出：接口返回数据
```

---

## 典型工作流

```
Step 1：发现工具
→ qveris_discover(query="A股尾盘涨幅排行")

Step 2（如需要）：查看详情
→ qveris_inspect(tool_id="具体工具ID")

Step 3：执行调用
→ qveris_call(tool_id="具体工具ID", params={...})
```

---

## 在顺顺选股系统中的用途

| 用途 | QVeris 工具 | 说明 |
|------|------------|------|
| 补充日K线数据 | eastmoney_stock_kline | 备用数据源 |
| 补充财务数据 | financial_statement | PB、PE、ROE |
| 板块资金流 | sector_flow | 北向资金板块分布 |
| 宏观数据 | macro_indicator | 利率、汇率、CPI |

---

## API Key 配置

```
API Key: sk-EWuBOIYNNql10MfrX4T4sELRjRHH53uZ2jzlsvDh0Wo
Region:  cn（qveris.cn）
配置位置：openclaw.json → plugins.entries.qveris.config
```

---

## 激活方式

Gateway 重启后自动加载（QVeris 已在 `plugins.allow` 和 `tools.alsoAllow` 中注册）。

重启命令：手动在 MaxClaw 设置中点击重启

---

## 状态检查

```bash
# 检查插件是否加载
openclaw plugins inspect qveris

# 预期输出
Status: loaded
Tools: qveris_discover, qveris_inspect, qveris_call
```

---

## 注意事项

1. **API Key 安全**：Key 已写入配置，不要对外分享
2. **免费额度**：qveris.cn 有免费调用额度，超额后需付费
3. **区域配置**：中国用户用 `region: cn`，全球用户用 `region: global`
4. **工具超时**：`qveris_call` 默认超时 60 秒，批量调用需注意
5. **数据覆盖**：优先用东方财富免费 API（已完整覆盖），QVeris 作为补充

---

*本 Skill 由顺顺自动生成 | 2026-03-29*
