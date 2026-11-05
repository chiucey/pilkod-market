# 数据源规范:恒生优先(2026-10-23 落地)

## 0. 数据源优先级(硬约束)

| 优先级 | 数据源 | 说明 |
|:-:|---|---|
| **1** | **恒生金融数据库(MiniMax Finance)** | 官方数据接口,字段口径明确、**自带守恒校验**、覆盖野人哥体系所需的全部模块。**默认走这个** |
| 2 | 东方财富 | 降级。资金流字段需自行校验口径(`f52`=主力,`f53`=小单,`f54`=中单,`f55`=大单,`f56`=超大单) |
| 3 | 腾讯行情 | 降级。实时行情与**全天分时轨迹**最稳(恒生分时只给最近 30 分钟) |
| 4 | 新浪行情 | 兜底。日线 / 资金流降级源,**缺换手率、量比、振幅** |

**降级是按模块独立进行的**:实时行情可能来自恒生、日线来自东财、分时来自腾讯,输出里逐项标注实际来源。
**不同源口径不可直接比数值,只可比方向与相对变化。**

调用封装:`scripts/hengsheng.py`(恒生)+ `scripts/fetch.py`(统一编排 + 降级链)。

```bash
python3 scripts/fetch.py 002614 --days 14          # 行情+资金流+分时
python3 scripts/fetch.py 002614 --days 14 --events  # 追加事件风险快检
python3 scripts/fetch.py 002614 --json              # 机器可读
```

---

## 1. 恒生 api_id → 野人哥体系模块 对照表

这一节是本 skill 的核心索引:**每个判断模块该调哪个 api_id**。

| 野人哥模块 | api_id | 关键字段 | 用在哪 |
|---|---|---|---|
| **实时行情** | `AShareLiveQuote` | latestPrice / avgPrice / bidGrp / offerGrp(五档) / buyinVolumeLot(**内盘**) / selloutVolumeLot(**外盘**) / entrustRate / turnoverRate / volumeRate / limitUpPrice / limitDownPrice / pettm / pblf / negotiableMV / tradeStatus | 第1段数据快照;判断是否在均价线上/下;涨跌停价 |
| **分时(近30分钟)** | `AShareTickQuote` | tradingTimestamp / latestPrice / **avgPrice** / turnoverVolumeLot(累计万手) | 均价线是否跟随创新低(承接力判定) |
| **全天分时轨迹** | 腾讯 `minute/query` | 逐分钟价+累计量 | 日高/日低出现时点 + 当时累计量占比 |
| **日线行情** | `StockDailyQuote` | openprice/closeprice/highprice/lowprice / **avgprice(均价)** / changepct / **rangepct(振幅)** / **turnoverrate(换手率)** / **volumeRatio(量比)** / turnovervalue / turnoverdeals / ifsuspend | 第2段合并表;量价六原则落位;锚点(5日线/大阳半分位) |
| **★个股资金流向** | `AStockCashFlow` | **hugenetbuyvalue(特大单)** / **largenetbuyvalue(大单)** / **largenetbuyvaluedde(主力DDE=特大+大)** / mediumnetbuyvalue(中单) / smallnetbuyvalue(小单) / largenetbuyvaluedderatio(资金比%) / risingupdays(连红天数) | **第4段六标准打分**的主力证据 |
| **实时资金流** | `RealStockFundFlow` | mainNetIn(主力净额) / retailNetIn(散户净额) / main5NetIn / main10NetIn / **continuesInDays(主力连续流入天数)** / superGrpNetTurnover / largeNetTurnover | 主力控盘强度;"连续流入N天"是野人体系判断控盘的关键 |
| **区间行情** | `StockRangeQuotation` | changepctbt(区间涨跌) / **maxdrawdown(最大回撤)** / limitupdaysbt / limitdwondaysbt / turnoverrateperdaybt(日均换手) / updaysbt / dwondaysbt | 位置判断;盈亏比里的"上方空间"参考 |
| **情绪周期(全市场)** | `MarketLimitUpDownCount` | **uplimitCount(涨停家数)** / **downlimitCount(跌停家数)** / upCount / downCount / memberCount | **第7段情绪周期五阶段判定** |
| **板块排行** | `SectorRank` | prodName / pxChangeRate / riseCount / fallCount / upLimitCount / downLimitCount / turnoverRatio | 第6段板块强弱;找主线 |
| **所属概念** | `StockBelongConcept` | conceptname / indate / **inreason(纳入原因)** | 主线五步法第1步"消息级别"的素材;概念介绍 |
| **财报预约披露** | `FinanceReportDisclosure` | reportdate / datetype / **reservediscdate(最新预约披露日)** / actualdate | **第10段事件风险**:披露前5个交易日一律降档 |
| **股东户数** | `ShareholderNum` | enddate / shnum / **shnumchange(较上期增减)** / averageholdsum / **top10stockholdersamount** | 户数大增=散户接盘;骤降=筹码集中 |
| **限售解禁** | `RestrictedStockLifting` | startdateforfloating / newmarketableashares / **newmarketableasharespercent** / sourcetype | 解禁前后抛压 |
| **增减持计划** | `ShareholdingChangePlan` | shname / transferplantype / eventprocedure / promisebegindate / shareceiling / ratioceiling | 减持预期;现价远高于减持价=卖方成本极低 |
| **重要股东交易** | `KeyHolderTrande` | shareholdername / trandetype / changevolume / **avgprice** / holdratioafterchange | 同上,含实际成交均价 |
| **业绩预告** | `PerformanceForecast` | forcasttype(首亏/预增) / minnetprofit / maxnetprofit / minetprofityoy / forcastreason | 事件风险;"首亏 + 负PE"=纯题材票 |
| **估值** | `StockValueAnalysis` | **pe(TTM)** / pb / ps / pcfttm / totalmv / dividendratio | 事件风险:PE上百倍+亏损=按情绪对待,不能按价值持有 |
| **龙虎榜** | `DailyStockHeroDetails` | rankingreason(上榜原因) / abnormalbuysum / abnormalsalesum / **净买额** | 席位是买还是卖;跌停日"日跌幅偏离值达7%"是强证据 |
| **融资融券** | `StockSecuritiesMargin` | financevalue(融资余额) / financebuynetvalue(融资净买入) | 杠杆资金在追高还是在撤 |

---

## 2. 恒生资金流口径(已验证,不用猜)

```
主力净额(DDE) = 特大单净买入额 + 大单净买入额
守恒:主力DDE + 中单净买入额 + 小单净买入额 == 0
```

**验证样例(深桑达A 2026-10-22,跌停日)**
| 特大单 | 大单 | 主力DDE | 中单 | 小单 | 守恒 |
|---:|---:|---:|---:|---:|:-:|
| -16,015.32 | -4,779.96 | **-20,795.28** | +9,053.69 | +11,741.59 | ✅ 0.00 |

**恒生的 `largenetbuyvaluedde` 就是东财的 `f52`("主力净额")的真身。**
之前把东财 f53/f54 误读成"超大单/大单"、导致结论完全反向的坑,在恒生这里不存在——字段中文名直接写在列头。

---

## 3. 东财降级源的口径校验(仍要保留)

| 字段 | 含义 | 校验式 |
|---|---|---|
| f52 | 主力净额(=大单+超大单) | `f55+f56 == f52` |
| f53 | **小单** | `f53+f54+f55+f56 ≈ 0` |
| f54 | **中单** | |
| f55 | 大单 | |
| f56 | 超大单 | |

`fetch.py` 每次都会跑这个守恒校验,**校验不过就在输出里打 ⚠️,并且该资金流不可用于下结论**。

---

## 4. 恒生接口的已知限制(别踩)

| 限制 | 影响 | 应对 |
|---|---|---|
| `AShareTickQuote` **只返回最近 30 分钟**,`pageNo>1` 为空 | 拿不到全天分时 | 全天轨迹用腾讯 `minute/query`;恒生的 avgPrice 用于均价线判定 |
| `SectorRank` 是实时接口,**盘前返回全 0** | 板块排行在开盘前不可用 | 盘前用上一交易日数据或盘后查询 |
| `AShareLiveQuote` 集合竞价前 `latestPrice=0` | 实时价取不到 | 用 `prevClosePrice` 占位并标注"未开盘";估值/市值/涨跌停价仍有效 |
| `StockDailyQuote` 返回**最新在前(倒序)** | 取末尾会拿到最旧数据 | `hengsheng.py` 内已统一按日期**升序**输出,下游一律取 `[-N:]` |
| 6 位代码必须补后缀 | 裸代码会被当聚源内码打错标的 | `000032.SZ` / `600760.SH` / `300589.SZ` / `8xx→.BJ` |
| 金额字段是 `"11.42亿元"` 这类字符串 | 直接转 float 得 None | `_amt()` 解析 |
| 恒生调用走 `mcode-tools` CLI,**单次 2-5 秒** | 一次完整取数 20-40 秒 | 可接受;批量多股用 `batch` 模式或 `format:"csv"` |

---

## 5. 各模块的取数建议

| 分析段 | 必取 | 建议取 |
|---|---|---|
| 1 数据快照 | `AShareLiveQuote` | `RealStockFundFlow` |
| 2 日线+资金流合并表 | `StockDailyQuote` + `AStockCashFlow` | `StockRangeQuotation` |
| 3 主力四阶段 | 同上 | `StockBelongConcept` |
| 4 六标准打分 | `AStockCashFlow` + `StockDailyQuote` + 板块(`SectorRank`) | `DailyStockHeroDetails` |
| 5 量价+承接力 | `StockDailyQuote` + 全天分时(腾讯) | `AShareTickQuote`(均价) |
| 6 板块五步法+角色 | `StockBelongConcept` + `SectorRank` | `StockBelongIndustry` |
| 7 情绪周期+仓位 | `MarketLimitUpDownCount` | `SectorRank` |
| 8 状态四档 | 前面全部 | `StockRangeQuotation`(盈亏比空间) |
| 9 关键价位 | `StockDailyQuote` | `StockRangeQuotation` |
| 10 风险+事件 | `FinanceReportDisclosure` `ShareholderNum` `RestrictedStockLifting` `ShareholdingChangePlan` `PerformanceForecast` `StockValueAnalysis` `DailyStockHeroDetails` `StockSecuritiesMargin` | `KeyHolderTrande` |

**一次性全取:`python3 scripts/fetch.py <code> --days 14 --events`**
