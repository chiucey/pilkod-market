---
name: stock-briefing-L
description: 股票简报生成技能（开盘简报 + 收盘简报）。当用户要求生成股票简报、设置定时推送、查看简报内容、修改自选股配置、或修复简报定时任务时触发。支持动态配置自选股列表、大盘指数追踪、量能分析、技术指标、主力资金多周期追踪、重要公告分析、走势研判及操作建议，并通过飞书群聊自动推送。
---

# 股票简报技能

## 核心能力

生成并推送 A 股股票简报（开盘版 / 收盘版），内容包含7大维度：

| 章节 | 内容 | 数据来源 |
|------|------|---------|
| 一、大盘环境 | A股指数、隔夜美股、VIX恐慌指数、A50夜盘、北向资金 | 新浪财经、英为财情、东方财富 |
| 二、自选股行情 | 最新价、昨收价、涨跌幅、成交额 | 新浪财经 |
| 三、量能追踪 | 5日/10日/30日均量、相对量、量能信号 | 新浪财经K线 |
| 四、技术指标 | MA5/MA20/MA60、RSI14、MACD、KDJ、买卖信号 | 新浪财经K线 |
| 五、主力资金 | 3日/5日/10日汇总、近10日明细、信号评级 | 东方财富 |
| 六、重要公告 | 个股近期公告标题和摘要 | 东方财富公告 |
| 七、走势研判 | 操作建议、支撑位、压力位、综合研判 | 综合分析 |

## 自选股配置

自选股列表保存在 `config/stocks.json`，**初始为空，需要用户自行添加**：

```json
{
  "stocks": [],
  "indices": [
    {"code": "sh000001", "name": "上证指数"},
    {"code": "sz399001", "name": "深证成指"},
    {"code": "sz399006", "name": "创业板指"}
  ]
}
```

**如何添加自选股：**
- 告诉技能「添加XXX股票到自选股」，技能会自动查询代码并更新配置
- 直接发送股票代码，如「sh601012」（上海）或「sz000963」（深圳）
- 发送股票名称，如「比亚迪」，技能会自动匹配正确的交易所代码

**配置管理命令：**
- 查看当前自选股：读取 `config/stocks.json`
- 添加股票：更新 `stocks` 数组，添加 `{"code": "sh/sz股票代码", "name": "股票名称"}`
- 删除股票：从 `stocks` 数组中移除对应条目

## 简报内容详解

### 一、大盘环境（世界局势分析）
- **A股主要指数**：上证、深证、创业板收盘点位和涨跌幅
- **隔夜美股**：道琼斯、纳斯达克、标普500走势
- **VIX恐慌指数**：衡量市场恐慌程度（<20平静，>30恐慌）
- **A50夜盘**：反映外围市场对A股的预期
- **北向资金**：沪股通+深股通净买入额（外资风向标）
- **开盘前综合研判**：汇总外围因素，给出开盘预期

### 五、主力资金（多周期追踪）
- **3日汇总**：短期主力动向
- **5日汇总**：中期趋势判断
- **10日汇总**：长期资金布局
- **信号评级**：积极建仓/温和流入/中性/净流出/主力出逃
- **近10日明细**：每日涨跌幅、主力净流入、净占比

### 六、重要公告
- 财报公告（年报、季报）
- 业绩预告（预增/预减）
- 股份回购计划
- 重大合同/合作
- 公告解读提示

### 七、走势研判与操作建议
- **操作建议**：关注/观望/回避
- **支撑位**：股价下跌的可能止跌位置
- **压力位**：股价上涨的可能受阻位置
- **综合研判**：技术面+资金面综合分析
- **详细操作建议**：具体买入/卖出/止损点位

## 定时任务

| 类型 | Cron 表达式 | 触发时间 |
|------|-------------|---------|
| 开盘简报（AM） | `55 8 * * 1-5` | 北京时间周一至周五 08:55 |
| 收盘简报（PM） | `0 16 * * 1-5` | 北京时间周一至周五 16:00 |

## 触发命令

**开盘简报：**
```bash
bash /workspace/skills/stock-briefing/scripts/run-briefing.sh AM
```

**收盘简报：**
```bash
bash /workspace/skills/stock-briefing/scripts/run-briefing.sh PM
```

**直接生成（手动触发）：**
```bash
python3 /workspace/skills/stock-briefing/scripts/stock_data.py AM   # 开盘版
python3 /workspace/skills/stock-briefing/scripts/stock_data.py PM  # 收盘版
```

## Cron Job 配置

两个 cron job 均指向 `run-briefing.sh`，超时 600 秒，isolated session：

```bash
openclaw cron add \
  --name "📈 股票开盘简报" \
  --schedule "55 8 * * 1-5" \
  --tz "Asia/Shanghai" \
  --payload-kind agentTurn \
  --payload-message "bash /workspace/skills/stock-briefing/scripts/run-briefing.sh AM" \
  --timeout 600

openclaw cron add \
  --name "📊 股票收盘简报" \
  --schedule "0 16 * * 1-5" \
  --tz "Asia/Shanghai" \
  --payload-kind agentTurn \
  --payload-message "bash /workspace/skills/stock-briefing/scripts/run-briefing.sh PM" \
  --timeout 600
```

## 数据源

| 数据类型 | 接口 | 说明 |
|----------|------|------|
| 实时行情 | `hq.sinajs.cn` | 价格/成交量/成交额 |
| K线数据 | `money.finance.sina.com.cn` | MA/RSI等技术指标 |
| 主力资金 | `push2his.eastmoney.com` | 3日/5日/10日汇总 |
| 公告信息 | `np-anotice-stock.eastmoney.com` | 个股公告 |
| 美股数据 | `hq.sinajs.cn` | 道指/纳指/标普500 |
| 北向资金 | `push2his.eastmoney.com` | 沪股通/深股通 |

## 飞书发送

```bash
openclaw message send \
  --channel feishu \
  --target "chat:飞书群聊ID" \
  --message "$(python3 /workspace/skills/stock-briefing/scripts/stock_data.py PM)"
```

## 目录结构

```
stock-briefing/
├── SKILL.md
├── _meta.json
├── config/
│   └── stocks.json           # 动态自选股配置
├── scripts/
│   ├── run-briefing.sh       # 触发脚本（被 cron 调用）
│   ├── stock_data.py         # 数据收集主脚本
│   └── is_trading_day.py     # 交易日判断
└── temp/
    └── briefing_latest.md    # 最新简报缓存
```

## 配置管理示例

**添加股票：**
```
用户：帮我把「比亚迪」加入自选股
技能：更新 config/stocks.json，添加 {"code": "sz002594", "name": "比亚迪"}
```

**删除股票：**
```
用户：从自选股中移除天融信
技能：从 config/stocks.json 删除 sz002212 相关的配置
```

**查看配置：**
```
用户：查看当前自选股
技能：读取并展示 config/stocks.json 内容
```
