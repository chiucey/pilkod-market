---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 59a986521dc1b420a70dd9720659e0e9
    PropagateID: 59a986521dc1b420a70dd9720659e0e9
    ReservedCode1: 3045022062cc12c9f16c02705db6c08d5c92fa7210395a7d6ccf5698633d3c96d59994a0022100a642d99280e95a47297d9cbe3c168b6d0dfe605f992ab9c24fbf7a61d422069f
    ReservedCode2: 3045022100eb514256c3552a4cd217a44931082a3724e6b29952d6efacca744cefe484979e022042fc16182fce831abb99e852cbe3c7cc5f0fca6382a9b62880b08f6bf5740de3
---

# 数据源参考

## 搜索关键词模板

### 天气数据

**数据源**：wttr.in（唯一来源）

**API 调用**：
```
https://wttr.in/{地点}?format=j1
```

**默认地点**：泉州（当用户未指定时）
```
https://wttr.in/Quanzhou?format=j1
```

**地点获取规则**：
1. 用户明确指定地点 → 使用用户指定地点
2. 用户未指定 → 默认使用"泉州"

---

### 热点资讯

#### 微博热搜
| 来源 | URL |
|------|-----|
| 微博官网 | https://s.weibo.com/top/summary?cate=realtimehot |
| 今日热榜聚合 | https://tophub.today/n/KqndgxeLl9 |

**搜索关键词**: `微博热搜榜 今日` / `weibo hot search today`

#### 小红书热门
| 来源 | URL |
|------|-----|
| 新榜 | https://www.newrank.cn/ranktopic/xiaohongshu/ |
| 千瓜数据 | https://www.qian-gua.com/blog/tags/37/ |
| 今日热榜 | https://tophub.today/n/xiaohongshu |

**搜索关键词**: `小红书热门话题 今日` / `xiaohongshu trending today`

#### 知乎热榜
| 来源 | URL |
|------|-----|
| 知乎官网 | https://www.zhihu.com/knowledge-plan/hot-question/hot/0/hour |
| 今日热榜聚合 | https://tophub.today/n/mproPpoq6O |

**搜索关键词**: `知乎热榜 今日` / `zhihu hot list today`

#### 国际热点
| 来源 | URL |
|------|-----|
| Google Trends | https://trends.google.com |
| CNN | https://www.cnn.com |
| Reuters | https://www.reuters.com |
| BBC | https://www.bbc.com |
| Twitter/X | https://x.com |

**搜索关键词**: `Google Trends world trending` / `CNN Reuters top news today`

**注意**: 必须翻译为中文输出，优先选择具有广泛影响力的国际大事

---

### 财经数据

#### A股行情（权威数据源）

| 指数 | 新浪财经 | 东方财富 | 同花顺 |
|------|----------|----------|--------|
| 上证指数 | https://gu.sina.cn/ | https://quote.eastmoney.com/zs000001.html | https://q.stock.sohu.com/zs/000001/ |
| 深证成指 | https://gu.sina.cn/ | https://quote.eastmoney.com/zs399001.html | https://q.stock.sohu.com/zs/399001/ |
| 创业板指 | https://gu.sina.cn/ | https://quote.eastmoney.com/zs399006.html | https://q.stock.sohu.com/zs/399006/ |

**搜索关键词模板**:
- 上证指数: `新浪财经 上证指数 今日收盘 2026` / `东方财富 上证指数 今日行情`
- 深证成指: `新浪财经 深证成指 今日收盘 2026`
- 创业板指: `东方财富 创业板指 今日行情 2026`

#### 美股行情

| 指数 | Yahoo Finance | 新浪财经（翻译） |
|------|---------------|------------------|
| 道琼斯 | https://finance.yahoo.com/quote/%5EDJI/ | 国际市场翻译 |
| 纳斯达克 | https://finance.yahoo.com/quote/%5EIXIC/ | 国际市场翻译 |
| 标普500 | https://finance.yahoo.com/quote/%5EGSPC/ | 国际市场翻译 |

**搜索关键词模板**:
- `site:finance.yahoo.com Dow Jones Nasdaq S&P 500 today`
- `Yahoo Finance US stock market today 2026`
- `道琼斯 纳斯达克 标普500 今日收盘`

#### 港股行情

| 指数 | 搜索关键词 |
|------|-----------|
| 恒生指数 | `恒生指数 今日收盘 2026` / `site:finance.yahoo.com HSI Hong Kong` |
| 国企指数 | `国企指数 今日收盘 2026` |

#### 大宗商品

| 商品 | Yahoo Finance | 搜索关键词 |
|------|---------------|-----------|
| 黄金 | https://finance.yahoo.com/quote/GC%3DF/ | `黄金价格 今日 美元/盎司 2026` |
| WTI原油 | https://finance.yahoo.com/quote/CL%3DF/ | `WTI原油价格 今日 美元/桶 2026` |
| 布伦特原油 | https://finance.yahoo.com/quote/BZ%3DF/ | `布伦特原油价格 今日 美元/桶 2026` |

#### 加密货币（币安）

| 币种 | Binance URL | 搜索关键词 |
|------|-------------|-----------|
| BTC/USDT | https://www.binance.com/zh-CN/price/bitcoin | `Binance BTC USDT price today 2026` |
| ETH/USDT | https://www.binance.com/zh-CN/price/ethereum | `Binance ETH USDT price today 2026` |
|          |                                              |                                     |

**备用数据源**:
- CoinMarketCap: https://coinmarketcap.com
- CoinGecko: https://www.coingecko.com

### 热点板块

| 来源 | URL | 搜索关键词 |
|------|-----|-----------|
| 东方财富 | https://quote.eastmoney.com/center/boardlist.html | `东方财富 行业板块 今日涨幅 2026` |
| 同花顺 | https://www.10jqka.com.cn/ | `同花顺 热门板块 今日 2026` |
| 新浪财经 | https://vip.stock.finance.sina.com.cn/ | `新浪财经 行业板块 今日涨跌` |

---

## API 备用方案

当网络搜索不可用时，使用股票工具获取数据：

| 市场 | 工具 | 标的 |
|------|------|------|
| 美股 | `stocks_price` | ^DJI (道琼斯), ^IXIC (纳斯达克), ^GSPC (标普500) |
| A股 | `stocks_price` | 000001.SS (上证), 399001.SZ (深证), 399006.SZ (创业板) |
| 港股 | `stocks_price` | ^HSI (恒生), ^HSTECH (恒生科技) |

---

## 天气数据提取规范

### wttr.in API 返回字段

```json
{
  "current_condition": [
    {
      "temp_C": "19",        // 气温(℃)
      "FeelsLikeC": "19",    // 体感温度
      "weatherDesc": "Rain",  // 天气状况
      "windspeedKmph": "12", // 风速(km/h)
      "humidity": "93"        // 湿度(%)
    }
  ],
  "weather": [
    {
      "date": "2026-05-14",
      "maxTempC": "21",
      "minTempC": "19",
      "hourly": [...]
    }
  ]
}
```

### 输出格式示例

```
天气播报 | 泉州
【今日概况】
天气：小雨 | 气温：19°C | 体感：19°C | 风力：12km/h | 湿度：93%

【未来3天预报】
明天：小雨 / 19-21°C
后天：多云 / 20-26°C
大后天：晴 / 21-28°C

【出行建议】
1. 今日有小雨，外出请携带雨具
2. 空气湿度较大，注意防潮
```

---

## 热点数据提取规范

### 微博热搜提取

**URL**: https://s.weibo.com/top/summary?cate=realtimehot

**提取格式**:
```
微博热搜 TOP3
1. [热搜标题]
   📋 大致信息：[标题背后的热点事件/话题/人物简述]
   💬 一句话简评：[一句话点评热点影响或趋势]
2. [热搜标题]
   📋 大致信息：[标题背后的热点事件/话题/人物简述]
   💬 一句话简评：[一句话点评]
3. [热搜标题]
   📋 大致信息：[标题背后的热点事件/话题/人物简述]
   💬 一句话简评：[一句话点评]
```

### 小红书热门提取

**提取格式**:
```
小红书热门 TOP3
1. [话题标题]
   📋 大致信息：[话题内容/趋势简述]
   💬 一句话简评：[一句话点评话题趋势或热门原因]
2. [话题标题]
   📋 大致信息：[话题内容/趋势简述]
   💬 一句话简评：[一句话点评]
3. [话题标题]
   📋 大致信息：[话题内容/趋势简述]
   💬 一句话简评：[一句话点评]
```

### 知乎热榜提取

**URL**: https://www.zhihu.com/knowledge-plan/hot-question/hot/0/hour

**提取格式**:
```
知乎热榜 TOP3
1. [问题标题]
   📋 大致信息：[问题核心讨论内容简述]
   💬 一句话简评：[一句话点评问题关注度或讨论方向]
2. [问题标题]
   📋 大致信息：[问题核心讨论内容简述]
   💬 一句话简评：[一句话点评]
3. [问题标题]
   📋 大致信息：[问题核心讨论内容简述]
   💬 一句话简评：[一句话点评]
```

### 国际热点提取

**数据源优先级**:
1. Google Trends (https://trends.google.com)
2. CNN News (https://www.cnn.com)
3. Reuters (https://www.reuters.com)
4. BBC News (https://www.bbc.com)

**提取格式**:
```
国际热点 TOP3
1. [新闻标题]
   📋 大致信息：[新闻事件简述，包括时间、地点、相关方]
   💬 一句话简评：[一句话点评事件重要性或影响]
2. [新闻标题]
   📋 大致信息：[新闻事件简述]
   💬 一句话简评：[一句话点评]
3. [新闻标题]
   📋 大致信息：[新闻事件简述]
   💬 一句话简评：[一句话点评]
```

**注意**: 必须翻译为中文输出，优先选择具有广泛影响力的国际大事

---

## 输出数据精度要求

1. **价格**: 保留1-2位小数（如 33,456.78）
2. **涨跌幅**: 保留2位小数（如 +1.23% 或 -0.45%）
3. **成交量**: 使用亿/万单位（如 1.2万亿、8500亿）
4. **时间戳**: 使用YYYY-MM-DD格式（如 2026-05-13）

---

## 专业术语规范

| 场景 | 规范用语 |
|------|----------|
| 上涨 | ▲ / + / 收涨 |
| 下跌 | ▼ / - / 收跌 |
| 平盘 | ─ / 持平 |
| 强势 | 领涨、表现强劲 |
| 弱势 | 领跌、表现疲软 |

---

## 热点板块提取规范

**数据源**: 东方财富行业板块中心 (https://quote.eastmoney.com/center/boardlist.html)

**提取格式**:
```
热点板块 TOP3
| 板块名称 | 涨跌幅（相对昨日） | 代表股 |
|----------|--------|--------|
| XXX板块 | 相对昨日 +X.X% | XXX |
| XXX板块 | 相对昨日 +X.X% | XXX |
| XXX板块 | 相对昨日 +X.X% | XXX |
```