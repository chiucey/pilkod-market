---
name: gold-price-monitor
description: 监控工商银行积存金和建设银行贵金属价格，当价格突破用户设定的基准线时推送通知。当用户要求监控金价、设置价格提醒、积存金价格报警、贵金属投资提醒时使用。
---

# 贵金属价格监控技能

监控工商银行积存金、建设银行贵金属的实时价格，支持设置基准线和阈值触发通知。

## 数据源

| 银行 | 产品 | 数据接口 |
|------|------|----------|
| 工商银行 | 积存金 | `https://mybank.icbc.com.cn/icbc/newperbank/perbank3/gold/goldaccrual_query_out.jsp` |
| 建设银行 | 黄金积存 | `https://gold.ccb.com/` |
| 建设银行 | 易存金 | 各地方建行贵金属页面 |

## 价格获取流程

### 1. 获取工商银行积存金价格

```python
import requests
from bs4 import BeautifulSoup

def get_icbc_gold_price():
    """获取工商银行积存金实时价格"""
    url = "https://mybank.icbc.com.cn/icbc/newperbank/perbank3/gold/goldaccrual_query_out.jsp"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 解析表格数据
    prices = {}
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # 跳过表头
            cols = row.find_all('td')
            if len(cols) >= 8:
                product = cols[0].text.strip()
                buy_price = cols[1].text.strip()  # 实时主动积存价格
                sell_price = cols[7].text.strip()  # 赎回价
                prices[product] = {'买入价': buy_price, '赎回价': sell_price}
    return prices
```

### 2. 获取建设银行贵金属价格

```python
def get_ccb_gold_price():
    """获取建设银行贵金属实时价格"""
    url = "https://gold.ccb.com/cn/gold/hjhq.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    # 建行页面为HTML表格，按实际页面结构解析
    # 积存金: 主动积存买入价、赎回价
    return prices
```

## 价格监控配置

### 用户配置模板

```yaml
monitoring:
  targets:
    - bank: icbc
      product: 积存金
      price_type: 买入价  # 买入价/赎回价
      baseline: 600.00      # 基准线（元/克）
      threshold: 5.0        # 触发阈值（元），价格偏离基准线超过此值时通知
      direction: both       # both/above/below - 双向/只监控高于/只监控低于

    - bank: ccb
      product: 黄金积存
      price_type: 主动积存价
      baseline: 600.00
      threshold: 10.0
      direction: above      # 金价超过600时通知

  check_interval: 3600      # 检查间隔（秒），默认1小时
  notify_channels:
    - email
    - webhook           # 自定义webhook URL
```

## 监控逻辑

```
价格监控算法:
1. 获取当前价格 P_current
2. 计算偏离值 delta = P_current - baseline
3. 判断触发条件:
   - direction=both: |delta| >= threshold
   - direction=above: delta >= threshold
   - direction=below: delta <= -threshold
4. 满足条件时发送通知
5. 记录触发日志，避免重复通知（冷却期30分钟）
```

## 通知消息格式

```json
{
  "type": "gold_price_alert",
  "timestamp": "2026-04-02T10:30:00+08:00",
  "alert": {
    "bank": "工商银行",
    "product": "积存金",
    "price_type": "买入价",
    "current_price": 605.50,
    "baseline": 600.00,
    "change": +5.50,
    "change_percent": +0.92,
    "threshold": 5.0,
    "direction": "above"
  },
  "message": "【金价提醒】工商银行积存金买入价已达605.50元/克，较基准价600.00元上涨5.50元（+0.92%），已触发阈值5.0元"
}
```

## 使用示例

### 示例1：监控工行积存金买入价

用户配置：
- 基准线：600元/克
- 阈值：10元
- 方向：above（金价超过610元时提醒）

### 示例2：双向监控建行黄金积存

用户配置：
- 基准线：580元/克
- 阈值：8元
- 方向：both（金价波动超过8元时提醒）

### 示例3：设置多个银行产品同时监控

```yaml
monitoring:
  targets:
    - bank: icbc
      product: 积存金
      baseline: 600
      threshold: 10
    - bank: ccb
      product: 黄金积存
      baseline: 580
      threshold: 8
```

## 定时任务配置

推荐使用系统cron任务定期执行监控：

```bash
# 每小时检查一次
0 * * * * /usr/bin/python3 /path/to/monitor.py --config config.yaml

# 交易时段每15分钟检查一次（9:00-15:00）
*/15 9-14 * * 1-5 /usr/bin/python3 /path/to/monitor.py --config config.yaml
```

## 注意事项

1. **数据延迟**：银行官网数据可能有15分钟延迟
2. **交易时间**：建议在交易时段内检查（周一9:00至周六4:00）
3. **冷却机制**：同一产品触发后需等待30分钟才能再次触发
4. **网络要求**：需要稳定网络连接访问银行页面
5. **数据验证**：获取后需验证数据有效性，异常时跳过本次检查

## 参考资料

- [工商银行积存金行情页面](references/icbc_gold_reference.md)
- [建设银行贵金属页面](references/ccb_gold_reference.md)
