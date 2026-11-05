# 股市板块研究数据源参考

## A股市场数据源

### 主要平台

| 平台 | 网址 | 主要功能 |
|-----|------|---------|
| 东方财富 | eastmoney.com | 行业板块、概念板块、主力资金流向 |
| 同花顺 | 10jqka.com.cn | 板块轮动、资金博弈、行情数据 |
| 雪球 | xueqiu.com | 板块讨论、投资者情绪、组合跟踪 |
| 乌龟量化 | uquant.org | 历史数据、回测工具、量化分析 |
| 聚宽 | joinquant.com | 研究数据、API接口、策略回测 |

### 关键数据接口

```
东方财富数据接口：
- 行业板块列表：get_industries()
- 板块资金流向：get_money_flow()
- 概念板块：get_concept()

同花顺数据接口：
- 板块行情：get_plate_list()
- 资金流向：get_money_flow_data()
```

## 港股市场数据源

### 主要平台

| 平台 | 网址 | 主要功能 |
|-----|------|---------|
| 披露易 | hkexnews.hk | 港交所公告、财务报告 |
| 富途牛牛 | futu.com | 港股实时行情、资讯 |
| 老虎证券 | itiger.com | 港股打新、社区讨论 |
| 阿斯达克 | aastocks.com | 港股实时数据、新闻 |

### 港股板块分类

```
恒生行业分类 (HSICS)：
- 能源业
- 原材料业
- 工业
- 非必需消费
- 常能消费
- 医疗保健
- 金融业
- 地产建筑业
- 电讯业
- 公用事业
- 资讯科技业
```

## 美股市场数据源

### 主要平台

| 平台 | 网址 | 主要功能 |
|-----|------|---------|
| SEC EDGAR | sec.gov | 美股财报、监管文件 |
| Yahoo Finance | finance.yahoo.com | 美股行情、新闻、图表 |
| Seeking Alpha | seekingalpha.com | 分析师观点、财务分析 |
| Finviz | finviz.com | 板块筛选、图表分析 |
| Macrotrends | macrotrends.net | 美股估值、市盈率历史 |

### 美股板块分类 (GICS)

```
11个标准行业板块：
1. 信息技术 (Information Technology)
2. 医疗保健 (Health Care)
3. 金融 (Financials)
4. 非必需消费 (Consumer Discretionary)
5. 通讯服务 (Communication Services)
6. 工业 (Industrials)
7. 必选消费 (Consumer Staples)
8. 能源 (Energy)
9. 公用事业 (Utilities)
10. 房地产 (Real Estate)
11. 材料 (Materials)
```

## ETF基金数据源

ETF是研究板块的重要工具：

```
A股板块ETF：
- 沪深300ETF (510300)
- 创业板ETF (159915)
- 行业ETF系列

港股ETF：
- 恒生科技ETF
- 恒生医疗ETF
- 中国互联ETF

美股ETF：
- SPY (标普500)
- QQQ (纳斯达克100)
- 行业Sector ETFs (XLK, XLV, XLF等)
```

## 产业链研究资源

### 宏观数据

| 来源 | 网址 | 数据类型 |
|-----|------|---------|
| 国家统计局 | stats.gov.cn | 宏观经济、产业结构 |
| 世界银行 | worldbank.org | 全球产业链数据 |
| UNCTAD | unctad.org | 国际贸易、跨国投资 |

### 行业协会

```
半导体：SEMI (semi.org)
新能源汽车：IEA (iea.org)
医药：CPhI, R&D Pharma
光伏：CPIA (china-nengyuan.com)
```

## 跨市场对比指标

### 估值对比维度

```
市盈率 (PE)：
- 静态PE = 当前股价 / 上年度EPS
- 动态PE = 当前股价 / 预估年度EPS
- 市盈率百分位 = 当前PE在历史区间位置

市净率 (PB)：
- PB = 股价 / 每股净资产
- 用于金融、周期行业

市销率 (PS)：
- PS = 股价 / 每股营收
- 适用于成长型企业
```

### 盈利对比维度

```
毛利率 = (营收 - 成本) / 营收
净利率 = 净利润 / 营收
ROE = 净利润 / 净资产
ROA = 净利润 / 总资产
```
