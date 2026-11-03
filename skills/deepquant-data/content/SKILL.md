---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: eafe19e7d4b4f103d896c956c3d7c46b
    PropagateID: eafe19e7d4b4f103d896c956c3d7c46b
    ReservedCode1: 3045022000d7e4dab579caebe22385f5ae88e2b5233dd33a6af060364de2a6977f97be44022100fd26cc6bf6b18326f5f370f45e10bd84f7633c6c77ea7bb3baf3afd79a46364d
    ReservedCode2: 3045022100bc4b61b7079024358a163819b738944aa1d101b4faaae1db37af7fbfad95c4eb02205fc28b4c2e092f4fe788bfa2570bb5dc0bdc5d4477fa3f1d55213a51fd1160fe
description: DeepQuant 深度量化数据服务。提供中国金融市场数据查询服务，包括A股、指数、基金、可转债等市场行情数据，上市公司基本信息、财务数据、股本发行数据，以及一致性预期数据。当用户请求查询股票/基金/可转债数据、获取上市公司信息、分析财务指标、查询分析师预期数据时使用。
name: deepquant-data
---

# DeepQuant 深度量化数据服务

提供中国金融市场的全面数据查询服务，基于 Tushare Pro 接口实现。

## 核心能力

### 1. 市场行情数据

- **A股数据**：实时/历史行情、涨跌幅、成交量、换手率等
- **指数数据**：上证指数、深证成指、创业板指、科创50等主要指数
- **基金数据**：公募基金净值、规模、持仓、重仓股等
- **可转债数据**：可转债行情、转股价值、溢价率、债底等

### 2. 上市公司数据

- **基本信息**：公司概况、行业分类、上市时间、股本结构等
- **财务数据**：营收、净利润、资产负债率、毛利率等
- **股本发行**：限售股解禁、增发配股、股权激励等
- **股东数据**：股东户数、前十大股东、机构持仓等

### 3. 一致性预期数据

- **分析师预期**：盈利预测、目标价、评级统计
- **业绩预告**：业绩预告类型、预计净利润变动
- **业绩快报**：未经审计的业绩数据
- **一致预期**：综合券商预测的均值/中位数

## 触发场景

以下场景会自动触发本技能：

- "查询 XX 股票的近期行情"
- "帮我看看 XX 基金的基本信息"
- "获取 XX 可转债的数据"
- "XX 上市公司的财务数据"
- "查询 XX 的基本面分析"
- "XX 股票的一致性预期"
- "帮我分析 XX 的投资价值"
- "获取 XX 行业的宏观数据"

## 执行流程

### 步骤 1：解析查询意图

识别用户查询的数据类型：
- 市场行情类 → 使用行情接口
- 基本信息类 → 使用公司接口
- 财务数据类 → 使用财务接口
- 预期数据类 → 使用预期接口

### 步骤 2：参数提取

从查询中提取关键参数：
- 股票/基金代码（如 600519、000001）
- 时间范围（如近一周、近一年）
- 数据字段（如涨跌幅、市盈率）

### 步骤 3：数据获取

调用 Tushare Pro API 获取数据：
```python
import tushare as ts

# 设置 token
pro = ts.pro_api(TUSHARE_TOKEN)

# 股票日线行情
df = pro.daily(ts_code='000001.SZ', start_date='20240101', end_date='20240327')

# 上市公司基本信息
df = pro.stock_basic(ts_code='000001.SZ', fields='ts_code,name,industry,market')

# 财务数据
df = pro.fina_indicator(ts_code='000001.SZ', start_date='20230101')

# 一致性预期
df = pro.consensus_pre(ts_code='000001.SZ', ann_date='20240101')
```

### 步骤 4：数据处理与展示

根据数据类型格式化输出：
- 行情数据：表格形式展示
- 财务数据：关键指标卡片
- 预期数据：趋势图表+统计值

## 输出格式

### 标准响应结构

```json
{
  "success": true,
  "data_type": "market_data|basic_info|financial|consensus",
  "data": {
    "records": [...],
    "summary": {
      "total": 100,
      "fields": ["ts_code", "trade_date", "open", "high", "low", "close"]
    }
  },
  "metadata": {
    "query_time": "2024-03-27 11:22:24",
    "data_source": "Tushare Pro"
  }
}
```

### 表格展示

使用清晰的表格格式呈现数据，包含：
- 列标题：字段名称
- 行数据：具体数值
- 底部：汇总统计

## 注意事项

1. **接口限流**：注意 Tushare Pro 的接口调用频率限制
2. **数据时效**：部分数据存在1-3天延迟
3. **权限要求**：部分高级数据需要更高的积分权限
4. **合规提示**：数据分析结果仅供参考，不构成投资建议

## 错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 网络超时 | 重试3次，间隔2秒 |
| 权限不足 | 返回提示，列出可用数据范围 |
| 数据不存在 | 返回空结果集，提示检查代码 |
| 参数错误 | 返回参数格式要求 |

## 依赖资源

- Tushare Pro API Token
- 网络连接（HTTP/HTTPS）
- 数据缓存策略（可选）

## 相关技能

- `tushare-finance`：底层金融数据接口（已集成）
- `stock-analyzer`：股票分析增强功能
- `portfolio-optimizer`：投资组合优化
