# News Monitor 配置文件

> 修改此文件来自定义你的新闻追踪范围。支持多行业/多关键词配置。

---

## 追踪行业

eSIM（嵌入式SIM卡）行业

---

## 关键词列表

### 核心关键词（必须包含）

- eSIM
- eUICC
- 嵌入式SIM

### 行业变体词（按需增删）

- eSIM手机
- eSIM运营商
- eSIM芯片
- eSIM模组
- eSIM产品
- eSIM终端
- 物联网SIM
- 联通 eSIM
- 中国移动 eSIM
- 中国电信 eSIM
- 紫光同芯
- 移远通信 eSIM
- 广和通
- 华大电子
- 汇顶科技
- 美格智能
- 芯昇科技
- 东信和平
- 恒宝股份
- 捷德 eSIM
- 华为终端 eSIM
- 荣耀终端 eSIM

---

## RSS 源列表

> 将以下 JSON 写入 `~/.openclaw/news-monitor/rss-sources.json`，由 `rss-reader` 技能驱动

```json
[
  { "url": "https://www.rcrwireless.com/tag/esim/feed/", "name": "RCR Wireless", "category": "行业媒体" },
  { "url": "https://www.c114.net.cn/rss/", "name": "C114通信网", "category": "行业媒体" },
  { "url": "https://trustedconnectivityalliance.org/feed/", "name": "TCA", "category": "联盟" },
  { "url": "https://www.thalesgroup.com/en/feed", "name": "Thales", "category": "芯片商" },
  { "url": "https://blog.st.com/feed/", "name": "STMicroelectronics", "category": "芯片商" }
]
```

---

## 微信公众号关键词（用于搜索）

> 微信公众号有反爬限制，通过搜索引擎找第三方转载页面

- 联通 eSIM
- 中国移动 eSIM
- 中国电信 eSIM
- 紫光同芯
- 移远通信
- 广和通FIBOCOM
- 华大电子
- 汇顶科技
- 美格智能
- 物联网智库
- 物联传媒
- 芯昇科技
- 东信和平
- 运营商段子手

---

## 行业媒体 site 搜索列表

> 用于 batch_web_search 中的 site: 定向查询

- site:caict.ac.cn
- site:cww.net.cn
- site:c114.com.cn
- site:gsma.com
- site:ithome.com
- site:36kr.com
- site:ifeng.com
- site:gsmarena.com
