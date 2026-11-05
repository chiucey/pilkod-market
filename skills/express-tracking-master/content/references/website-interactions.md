---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402202506efecacb4d39e16c8c265398e7cc7f80330023ee7e17b8112cf8e6afe9db1022022c476cc5525dbeb5710bd468931e92905c2a21f94d06579011c053c79295d46
    ReservedCode2: 3046022100be2be1e6b52dce9f80c4ca517344f9711233abab5a43a33af9a6f6161a31e080022100ffc0279771776033d782ba91ea76f238338a57165453efe75833788be26a1d5b
---

# Website Interactions Reference

## Overview

This skill uses `extract_content_from_websites` tool to query logistics tracking information. The primary method is through Baidu Search, which reliably returns complete tracking information.

## Query Method Priority

### 1. Baidu Search (Primary - MOST RELIABLE)

**Why Baidu Search?**
- Works reliably for all Chinese express companies
- Returns complete tracking timeline from pickup to delivery
- No API restrictions or rate limiting
- No authentication required

**Query URL Pattern**:
```
https://www.baidu.com/s?wd={tracking_number}+{company_name}+物流
```

**Examples**:
```
https://www.baidu.com/s?wd=JT5475523871856+极兔速递+物流
https://www.baidu.com/s?wd=SF1234567890+顺丰速运+物流
https://www.baidu.com/s?wd=YT1234567890+圆通速递+物流
```

**Extraction Prompt**:
```
Extract ALL tracking information, complete timeline, every delivery event, location, timestamp for tracking number {tracking_number}. Show the full shipping route from pickup to delivery.
```

### 2. Kuaidi100 API (Secondary - May Be Unreliable)

**URL**: https://www.kuaidi100.com/query?type={company_code}&postid={tracking_number}

**Note**: This API may return errors or no results for some tracking numbers. Use Baidu Search as primary.

**Company Codes**:
| Company | Code |
|---------|------|
| Shunfeng | sf |
| YTO | yto |
| ZTO | zhongtong |
| Yunda | yunda |
| STO | sto |
| EMS | ems |
| JD | jd |
| Debang | debang |
| J&T Express | jtexpress |

### 3. Express Official Websites (Tertiary)

| Company | URL |
|---------|-----|
| J&T Express | https://www.jtexpress.com.cn |
| STO | https://www.sto.cn |
| Yunda | https://www.yundaex.com |
| EMS | https://www.ems.com.cn |

### 4. 17Track (Quaternary)
- **URL**: https://www.17track.net
- **Best for**: International express

### 5. Cainiao (Quinary)
- **URL**: https://www.cainiao.com
- **Best for**: Alibaba/Taobao orders

## Query Flow

```
1. Parse user input to get tracking number and company name
2. Build Baidu Search URL: https://www.baidu.com/s?wd={number}+{company}+物流
3. Extract content from Baidu Search results
4. If no results, try Kuaidi100 API
5. If still no results, try express official website
6. If all fail, return error with customer service info
```

## Verified Tracking Results

### J&T Express JT5475523871856

| Time | Event | Location |
|------|-------|----------|
| 2026-04-13 09:19:54 | PICKUP | 廊坊霸州市网点 |
| 2026-04-13 09:47:31 | Departed | 廊坊霸州市 → 天津转运中心 |
| 2026-04-13 13:55:28 | Arrived | 天津转运中心 |
| 2026-04-13 13:57:05 | Departed | 天津 → 廊坊临空转运中心 |
| 2026-04-13 17:27:46 | Arrived | 廊坊临空转运中心 |
| 2026-04-13 18:09:11 | Departed | 廊坊临空 → 北京朝阳北工大 |
| 2026-04-13 22:03:31 | Arrived | 北京朝阳北工大网点 |
| 2026-04-13 22:04:04 | OUT FOR DELIVERY | 快递员：温学崇 17718506500 |
| 2026-04-14 02:57:57 | DELIVERED | 签收人：家门口l |

## Customer Service Hotlines

| Company | Phone |
|---------|-------|
| Shunfeng | 95338 |
| YTO | 95554 |
| ZTO | 95311 |
| Yunda | 95546 |
| STO | 95543 |
| EMS | 11183 |
| JD | 950616 |
| Debang | 95353 |
| J&T | 956025 |

## Best Practices

1. **Always start with Baidu Search** - Most reliable for Chinese express
2. **Include company name in search** - Improves accuracy
3. **Request complete timeline** - Prompt should ask for all events
4. **Display route summary** - Show complete shipping path
5. **Include courier info** - Phone numbers for follow-up
