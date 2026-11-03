# Express Tracker - Query Channels Reference

## Primary Query Platforms

### 1. Kuaidi100

**Website**: https://www.kuaidi100.com

**API Endpoint**:
```
GET https://www.kuaidi100.com/query?type={code}&postid={tracking_number}
```

**Parameters**:
- `type`: Express company code (e.g., sf, yto, ems)
- `postid`: Tracking number

**Response**: JSON format

**Code Mapping**:
| Company | Code |
|---------|------|
| Shunfeng | sf |
| YTO | yto |
| ZTO | zto |
| Yunda | yunda |
| STO | shentong |
| EMS | ems |
| JD | jd |
| Debang | debang |
| J&T | jt |

### 2. Cainiao

**Website**: https://www.cainiao.com

**Features**:
- Official Alibaba logistics platform
- Good for Taobao/Tmall orders
- Real-time tracking updates
- Notification service

**Query Method**: Web scraping

### 3. 17Track

**Website**: https://www.17track.net

**Features**:
- Universal tracking platform
- Support for 500+ carriers worldwide
- Mobile app available
- Multi-language support

### 4. Official Express Websites

#### Shunfeng
- Website: https://www.sf-express.com
- Hotline: 95338

#### YTO
- Website: https://www.yto.net.cn
- Hotline: 95554

#### ZTO
- Website: https://www.zto.com
- Hotline: 95311

#### Yunda
- Website: https://www.yundaex.com
- Hotline: 95546

#### STO
- Website: https://www.sto.cn
- Hotline: 95543

#### EMS
- Website: https://www.ems.com.cn
- Hotline: 11183

#### JD Logistics
- Website: https://www.jdwl.com
- Hotline: 950616

#### Debang
- Website: https://www.deppon.com
- Hotline: 95353

#### J&T Express
- Website: https://www.jtexpress.com
- Hotline: 956025

## International Express

### DHL
- Website: https://www.dhl.com
- Tracking URL: https://www.dhl.com/cn-en/home/tracking.html

### FedEx
- Website: https://www.fedex.com
- Tracking URL: https://www.fedex.com/fedextrack/

### UPS
- Website: https://www.ups.com
- Tracking URL: https://www.ups.com/track

### TNT
- Website: https://www.tnt.com
- Tracking URL: https://www.tnt.com/express/zh_cn/site/home.html

### Aramex
- Website: https://www.aramex.com
- Tracking URL: https://www.aramex.com/track

## Search Engine Query

### Baidu Search

**Query Format**:
```
{tracking_number} tracking
{tracking_number} express query
```

## Query Response Format

### Kuaidi100 JSON Response

```json
{
  "message": "ok",
  "nu": "777398524745366",
  "com": "shentong",
  "ischeck": "1",
  "condition": "F00",
  "status": "200",
  "state": "3",
  "data": [
    {
      "time": "2026-04-09 22:47:36",
      "ftime": "2026-04-09 22:47:36",
      "context": "Package departed for next destination",
      "location": "Hebei Province"
    },
    {
      "time": "2026-04-09 18:58:35",
      "ftime": "2026-04-09 18:58:35",
      "context": "Package picked up by courier",
      "location": "Hebei Province"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| message | string | API response message |
| nu | string | Tracking number |
| com | string | Company code |
| ischeck | string | Whether checked (0/1) |
| status | string | Query status (200=success) |
| state | string | Delivery state code |
| data | array | Tracking events |
| time | string | Event time |
| ftime | string | Formatted time |
| context | string | Event description |
| location | string | Event location |

## State Code Reference

| Code | Status |
|------|--------|
| 0 | Pending |
| 1 | Picked Up |
| 2 | In Transit |
| 3 | Delivering |
| 4 | Delivered |
| 5 | Rejected |
| 6 | Returning |
| 7 | Returned |
| 8 | Exception |
