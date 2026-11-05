---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: d99382b018b0581be547c8c8e3f34980
    PropagateID: d99382b018b0581be547c8c8e3f34980
    ReservedCode1: 3046022100df7396b2c26a324c1fa8ced76791cb317c9fee8d71465a671f239c1950667c0c022100cfe95e6b2148a80c7217c1aa277f4f5b42b1c19b4c6f3b85c591bae0f3cf617b
    ReservedCode2: 3045022100aee9860ba2363c8fbe3d59cc07efb5f0aa3584605b56acdff108e2a63729a989022005b77074aa020fa582ee2fa9ff76af97daf599040977df612c03af1bee9e2e47
---

---
name: sortOrderAnalyse
skill_name: sortOrderAnalyse
description: 通过 HTTP 请求获取派单日志数据，从 secondDispatchDetail 字段解析派单信息，统计各种原因出现次数，识别未达标司机的问题原因。
---

# 司机派单日志分析技能 v2（网络版）

## 技能描述

通过 HTTP 请求获取派单日志数据，从 `secondDispatchDetail` 字段解析派单信息，统计各种原因出现次数，识别未达标司机的问题原因。

## 输入

- 用户提供派单日志 URL（格式如：`https://bes-f4.schengle.com/sortOrderLogPath/importSort{timestamp}.json`）
- 或提供直接的文件路径（本地 `.txt` / `.json`）
- 分析维度：
  1. 派单原因统计（按出现次数排序）
  2. 各司机派单成功次数统计
  3. 未达到4单的司机被拒原因分析

## 数据结构

URL 返回的 JSON 数据中，`secondDispatchDetail` 字段结构如下：

```json
{
  "secondDispatchDetail": {
    "20260510-03754": [
      {"D00619711": "该司机T+1日司机休息"},
      {"D00619712": "车辆等级不匹配!"}
    ]
  }
}
```

其中：
- **键**：订单号
- **值**：列表，每个元素是 `{司机ID: 原因}` 格式

## 分析流程

### Step 1: 获取数据

**方式A - 网络请求**：
```python
import urllib.request
import json

def fetch_dispatch_data(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode('utf-8'))
```

**方式B - 本地文件**：
```python
with open('文件路径', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### Step 2: 解析数据

从 JSON 中提取 `secondDispatchDetail` 字段：

```python
dispatch_data = data.get('secondDispatchDetail', data)  # 兼容两种格式
```

### Step 3: 基础统计

统计以下指标：
- 总订单数：`len(dispatch_data)`
- 派单成功订单数：统计包含 `订单派单成功` 的订单
- 派单成功率
- 涉及司机数

### Step 4: 派单原因统计

提取所有原因并进行计数，简化原因名称：
- `司机前置订单距离不满足`
- `司机后置订单距离不满足`
- `司机前置订单时间不满足`
- `司机后置订单时间不满足`
- `前订单等待时间过长`（前value:xxx）
- `后订单间隔时间过长`（后value:xxx）
- 其他原因保持原样

输出格式：
| 排名 | 原因 | 次数 | 占比 |
|------|------|------|------|

### Step 5: 各司机派单成功次数

识别每个订单中 `订单派单成功` 的司机，每个订单每位司机只计一次。

输出格式：
| 排名 | 司机ID | 成功次数 | 占比 |
|------|--------|----------|------|

### Step 6: 未达标司机分析

找出成功次数 **< 4** 的司机，统计其被拒绝原因：

**总体原因排名**：
| 排名 | 被拒原因 | 次数 |
|------|----------|------|

**各司机明细**：
| 司机 | 成功 | 被拒 | TOP 3 被拒原因 |

### Step 7: 关键发现

根据数据输出 3-5 条关键发现。

## 输出模板

```
======================================================================
{地区}数据 - 派单日志分析报告
======================================================================

### 一、基础统计
| 指标 | 数值 |
|------|------|
| 总订单数 | XX |
| 派单成功订单数 | XX |
| 派单成功率 | XX% |
| 涉及司机数 | XX |

---

### 二、派单原因统计（按出现次数）
| 排名 | 原因 | 次数 | 占比 |
|------|------|------|------|
| 1 | ... | XXX | XX.X% |
| ... | ... | ... | ... |

---

### 三、各司机派单成功次数
| 排名 | 司机ID | 成功次数 | 占比 |
|------|--------|----------|------|
| 1 | Dxxxxx | XX | XX.X% |
| ... | ... | ... | ... |

---

### 四、未达到4单的司机被拒原因分析

**未达标司机数：X位**

#### 1. 总体被拒原因排名
| 排名 | 被拒原因 | 次数 |
|------|----------|------|

#### 2. 各司机被拒原因明细
| 司机 | 成功 | 被拒 | TOP 3 被拒原因 |
|------|------|------|---------------|
| Dxxxxx | X单 | XXX次 | ①xxx ②xxx ③xxx |

---

### 五、关键发现
1. ...
2. ...
```

## 执行命令

```python
import urllib.request
import json

def analyze_dispatch_data(data):
    dispatch_data = data.get('secondDispatchDetail', data)
    
    reason_counts = {}
    driver_success = {}
    driver_reject_reasons = {}
    
    for order_no, entries in dispatch_data.items():
        success_drivers = set()
        
        for entry in entries:
            for driver_id, reason in entry.items():
                # 简化原因
                if 'orderNo:' in reason:
                    if '司机前置订单距离不满足' in reason:
                        simple_reason = '司机前置订单距离不满足'
                    elif '司机后置订单距离不满足' in reason:
                        simple_reason = '司机后置订单距离不满足'
                    elif '司机前置订单时间不满足' in reason:
                        simple_reason = '司机前置订单时间不满足'
                    elif '司机后置订单时间不满足' in reason:
                        simple_reason = '司机后置订单时间不满足'
                    elif '前value:' in reason:
                        simple_reason = '前订单等待时间过长'
                    elif '后value:' in reason:
                        simple_reason = '后订单间隔时间过长'
                    else:
                        simple_reason = reason.split(' orderNo:')[0]
                else:
                    simple_reason = reason
                
                reason_counts[simple_reason] = reason_counts.get(simple_reason, 0) + 1
                
                if driver_id:
                    if reason == '订单派单成功':
                        success_drivers.add(driver_id)
        
        for driver in success_drivers:
            driver_success[driver] = driver_success.get(driver, 0) + 1
    
    # 后续统计...
    return reason_counts, driver_success

# 使用示例
url = '用户提供URL'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=60) as response:
    data = json.loads(response.read().decode('utf-8'))

reason_counts, driver_success = analyze_dispatch_data(data)
```

## 适用场景

- 通过 API/URL 获取实时派单数据
- 分析单个城市/地区的派单数据
- 对比多个城市的派单成功率
- 识别司机派单瓶颈，优化调度策略