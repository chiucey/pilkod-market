# LAYTIME计算完整工作流

## 阶段1: 解析

### 1.1 解析SOF

读取 Statement of Facts 文件，提取：
- 船名 (Vessel Name)
- 港口 (Port)
- 货物量 (Cargo Quantity) - **精确读取，不估算**
- 事件时间线 (Timeline Events)
- 卸货率 (Discharge Rate)
- 滞期费率 (Demurrage Rate)
- 速遣费率 (Despatch Rate)

输出 `extracted/sof_parsed.json`：

```json
{
  "vessel": "M/V BAKKEDAL",
  "port": "ZHANGZHOU",
  "cargo": {
    "type": "AUSTRALIAN BARLEY",
    "quantity_mt": 21000
  },
  "timeline": [
    {
      "start_time": "2026-03-23T10:30",
      "end_time": "2026-03-23T24:00",
      "event": "ARRIVED AND NOR TENDERED",
      "day_of_week": "MON",
      "weather": null,
      "is_shifting": false
    }
  ]
}
```

### 1.2 解析合同条款

读取合同文件，提取关键条款：
- Laytime条款
- NOR递交窗口
- 起算时间规则
- 排除时间规则（SHEX, SHINC等）
- 移泊条款
- 天气条款

输出 `extracted/contract.json`：

```json
{
  "discharge_rate": {
    "rate": 8000,
    "unit": "MT/WWD",
    "terms": "SHEX"
  },
  "nor_window": {
    "hours": "08:00-17:00",
    "days": "MON-FRI"
  },
  "laytime_commencement": "Next working day 08:00",
  "exclusion_rules": {
    "WEEKEND": {
      "description": "周末（周六/周日）",
      "laytime_phase": "exclude",
      "demurrage_phase": "include",
      "source": "SHEX clause"
    },
    "HOLIDAY": {
      "description": "法定节假日",
      "laytime_phase": "exclude",
      "demurrage_phase": "include",
      "source": "SHEX clause"
    },
    "WEATHER": {
      "description": "恶劣天气（雨、雾等）",
      "laytime_phase": "exclude",
      "demurrage_phase": "include",
      "source": "WWD clause"
    },
    "SHIFTING": {
      "description": "移泊（锚地→泊位）",
      "laytime_phase": "exclude",
      "demurrage_phase": "exclude",
      "source": "implied"
    }
  },
  "demurrage_rate": 15825,
  "despatch_rate": 7912.5,
  "allowed_laytime_hours": 63.0
}
```

### 1.3 假期索引（中国港口必做）

如果是卸货港在中国，读取 `china_holidays_2026.json`，匹配SOF时间范围内的假期。

在 `sof_parsed.json` 中添加 `holiday_matches` 字段。

---

## 阶段2: 第一轮LLM判断

**输入**：`contract.json` + `sof_parsed.json`

**输出**：`extracted/judgments1.json`

**要求**：
- 逐条判断是否计入（基于合同条款：SHEX、WWD等）
- **不考虑"一旦滞期永久滞期"**
- 输出status + reason + hours
- **复合事件必须拆分**（详见下方说明）

### 复合事件拆分规则

**识别信号**：SOF记录中包含以下模式：
- `RAIN PERIODS: 0000-0200, 0606-1045`
- `RAIN FROM 1700-2015`
- `RAIN AT 0930-1230`
- `FOG PERIODS`、`STORM PERIODS`

**拆分方法**：
1. 解析下雨/恶劣天气时间段
2. 将原始时间段按天气时间段拆分为多个子段
3. 分别判断每个子段的INCL/EXCL

**示例**：

```
原始记录:
30-MAR MON 0000-2400 "WAITING FOR CARGO SAMPLING. RAIN PERIODS: 0000-0200, 0606-1045, 1340-1512"

拆分后:
- 0000-0200: RAIN → EXCL (2.0h)
- 0200-0606: WAITING FOR SAMPLING → INCL (4.1h)
- 0606-1045: RAIN → EXCL (4.65h)
- 1045-1340: WAITING FOR SAMPLING → INCL (2.92h)
- 1340-1512: RAIN → EXCL (2.53h)
- 1512-2400: WAITING FOR SAMPLING → INCL (7.8h)
```

**判断原则**：
- 下雨时间段：EXCL（WWD条款）
- 非下雨时间段：按主事件性质判断
- 时间总和必须等于原始时间段

**输出格式**：

```json
{
  "case_id": "BAKKEDAL_ZHANGZHOU_BARLEY",
  "allowed_hours": 63.0,
  "timeline": [
    {
      "time_key": "2026-03-23T10:30",
      "date": "2026-03-23",
      "day": "MON",
      "time_range": "1030-2400",
      "event": "ARRIVED AND NOR TENDERED",
      "hours": 13.5,
      "status": "EXCL",
      "reason": "Before laytime commenced (next working day 08:00)",
      "user_modified": false
    },
    {
      "time_key": "2026-03-24T00:00",
      "date": "2026-03-24",
      "day": "TUE",
      "time_range": "0000-2400",
      "event": "WAITING FOR BERTH",
      "hours": 24.0,
      "status": "INCL",
      "reason": "Working day, laytime commenced at 08:00",
      "user_modified": false
    },
    {
      "time_key": "2026-03-28T00:00",
      "date": "2026-03-28",
      "day": "SAT",
      "time_range": "0000-2400",
      "event": "WAITING FOR CLEARANCE",
      "hours": 24.0,
      "status": "EXCL",
      "reason": "Saturday - SHEX",
      "user_modified": false
    }
  ]
}
```

---

## 阶段3: 第一轮Python累加 + 找滞期点

**输入**：`judgments1.json` + `allowed_hours`

**输出**：`extracted/interim_result.json`

**Python脚本逻辑**：

```python
def find_demurrage_point(judgments, allowed_hours):
    acc_hours = 0
    prev_acc = 0
    
    for i, record in enumerate(judgments['timeline']):
        if record['status'] == 'INCL':
            prev_acc = acc_hours
            acc_hours += record['hours']
            
            # 检查是否刚超过allowed
            if prev_acc < allowed_hours and acc_hours >= allowed_hours:
                # 这条记录跨越滞期点！
                return {
                    "index": i,
                    "time_key": record['time_key'],
                    "hours_before_demurrage": allowed_hours - prev_acc,
                    "hours_after_demurrage": acc_hours - allowed_hours,
                    "exact_demurrage_time": calculate_exact_time(record, allowed_hours - prev_acc)
                }
    
    return None  # 没有滞期
```

**输出格式**：

```json
{
  "total_hours_used": 202.32,
  "demurrage_point": {
    "index": 23,
    "time_key": "2026-03-27T14:00",
    "hours_before_demurrage": 3.5,
    "hours_after_demurrage": 1.5,
    "exact_demurrage_time": "2026-03-27T14:32"
  },
  "summary": {
    "allowed_hours": 63.0,
    "used_hours": 202.32,
    "exceeded_hours": 139.32
  }
}
```

---

## 阶段4: 第二轮LLM判断（滞期后重新判断）

**输入**：`judgments1.json` + `interim_result.json`

**输出**：`extracted/judgments2.json`

**要求**：

1. **滞期点之前的记录**：保持不变

2. **滞期点那条记录**：拆分（如果需要）
   ```json
   {
     "time_key": "2026-03-27T14:00",
     "event": "WAITING FOR CLEARANCE",
     "split": true,
     "part1": {
       "hours": 3.5,
       "status": "INCL",
       "reason": "Working day. DEMURRAGE STARTED at 14:32"
     },
     "part2": {
       "hours": 1.5,
       "status": "INCL",
       "reason": "On Demurrage"
     }
   }
   ```

3. **滞期点之后的记录**：按"一旦滞期永久滞期"重新判断
   - 周末/节假日 → 改为 INCL
   - 雨天 → 改为 INCL
   - Shifting → 保持 EXCL
   - reason 改为 "On Demurrage"

**输出格式**：同 `judgments1.json`，但滞期点后的判断已更新

---

## 阶段5: 用户修改（可中断点）

**输入**：`judgments2.json`

**输出**：`judgments_final.json` + `judgments_changelog.json`

**用户修改示例**：
```
用户: "03-27 14:00 这条应该是 INCL"
```

**处理流程**：
1. 用时间戳定位 `2026-03-27T14:00` 的条目
2. 修改 status 和 reason
3. 设置 `user_confirmed: true`
4. 添加修改记录到 changelog
5. 生成 `judgments_final.json`

**changelog格式**：

```json
[
  {
    "timestamp": "2026-04-16T15:30:00",
    "time_key": "2026-03-27T14:00",
    "modification": {
      "field": "status",
      "old": "EXCL",
      "new": "INCL"
    },
    "reason": "用户确认：该时段应计入",
    "modified_by": "user"
  }
]
```

---

## 阶段6: 第二轮Python计算（最终结果）

**输入**：`judgments_final.json` + `allowed_hours`

**输出**：`calculation/result.json`

**Python脚本逻辑**：

```python
def calculate_final_result(judgments, allowed_hours, demurrage_rate, despatch_rate):
    timeline = []
    acc_hours = 0
    
    for record in judgments['timeline']:
        if record['status'] == 'INCL':
            acc_hours += record['hours']
        
        timeline.append({
            **record,
            "count_h": record['hours'] if record['status'] == 'INCL' else None,
            "cumulative": acc_hours if record['status'] == 'INCL' else acc_hours
        })
    
    # 计算结果
    if acc_hours <= allowed_hours:
        time_saved = allowed_hours - acc_hours
        amount = time_saved * (despatch_rate / 24)
        result_type = "DESPATCH"
    else:
        time_exceeded = acc_hours - allowed_hours
        amount = time_exceeded * (demurrage_rate / 24)
        result_type = "DEMURRAGE"
    
    return {
        "timeline": timeline,
        "time_result": {
            "type": result_type,
            "hours": abs(allowed_hours - acc_hours)
        },
        "amount": {
            "type": result_type,
            "value": amount,
            "currency": "USD"
        }
    }
```

**输出格式**：按 `RESULT_SCHEMA.md` 标准

---

## 阶段7: 渲染HTML/PDF

**输入**：`result.json`

**输出**：`calculation/output/LTC_*.html`

**执行**：

```bash
python3 基础设定/LAYTIME_TEMPLATES/render_laytime_v2.py 用户上传/{案例目录}
```

**PDF生成**：

```bash
wkhtmltopdf --enable-local-file-access --page-size A4 --orientation Landscape --margin-top 10mm --margin-bottom 10mm --margin-left 12mm --margin-right 12mm input.html output.pdf
```
