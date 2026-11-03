# 判断规则表

## ⚠️ 关键概念区分（必读）

### NOR递交规则 vs Laytime计算规则（两个独立概念）

**这两个规则互不影响，必须分别判断！**

#### 1. NOR递交规则

**只决定**：NOR何时可以递交、何时生效

| 条款 | 含义 | 示例 |
|------|------|------|
| 办公时间递交 | NOR只能在MON-FRI 0800-1700递交 | NOR窗口外递交 → 视为下一窗口时间递交 |
| WIPON/WIBON | 无论在港与否、无论靠泊与否都可递交 | 锚地可递交NOR |
| ATDNSHINC | 任何时间（包括周末节假日）都可递交 | 周六可递交NOR并立即生效 |

**注意**：ATDNSHINC只影响NOR递交时间，不影响laytime计算！

#### 2. Laytime计算规则

**只决定**：哪些时间计入laytime

| 条款 | 含义 | 示例 |
|------|------|------|
| WWD | 天气工作日（恶劣天气不计数） | 下雨时间排除 |
| SHEX | 周末不计数 | SAT/SUN排除 |
| SATSHEXEIU | 周末不计数，即使用了也不计 | SAT/SUN排除 |
| SHINC | 周末计数 | SAT/SUN计入 |

#### 3. 典型混淆案例

**案例：YU XIAO FENG第二港（YANG PU）**

- **NOR条款**：ATDNSHINC
- **卸货条款**：8,000 MT/WWD SHEX

**错误理解**：
```
❌ ATDNSHINC → 周末递交NOR → 周末也计数
```

**正确理解**：
```
✅ ATDNSHINC → 周六06:24递交NOR立即生效
✅ WWD SHEX → 但周六日时间仍然不计数（SHEX排除周末）
```

**时间线**：
```
21-MAR SAT 06:24  NOR递交并生效（ATDNSHINC允许）
21-MAR SAT 06:24  Laytime开始计算
21-MAR SAT 06:24-24:00  ❌ EXCL（SHEX排除周六）
22-MAR SUN 00:00-24:00  ❌ EXCL（SHEX排除周日）
23-MAR MON 00:00-08:00  ❌ EXCL（Before 08:00）
23-MAR MON 08:00-24:00  ✅ INCL（工作日，laytime计入）
```

#### 4. 判断流程（强制遵守）

```
步骤1：确定NOR递交规则
└── 识别合同中的NOR条款（办公时间/WIPON/WIBON/ATDNSHINC等）
└── 判断NOR何时递交、何时生效

步骤2：确定Laytime起算时间
└── 根据合同起算条款（下一工作日08:00 / 立即起算等）
└── 结合NOR生效时间计算

步骤3：确定Laytime计算规则
└── 识别卸货率条款（WWD/SHEX/SHINC/SATSHEXEIU等）
└── 独立判断每个时间段是否计入

⚠️ 步骤1和步骤3是独立的！不要混为一谈！
```

#### 5. 常见条款组合

| NOR条款 | 卸货条款 | NOR递交 | Laytime计算 |
|---------|----------|---------|-------------|
| 办公时间 | WWD SHEX | 仅工作日窗口内 | 周末排除 |
| ATDNSHINC | WWD SHEX | 任何时间 | 周末排除 |
| ATDNSHINC | SHINC | 任何时间 | 周末计入 |
| 办公时间 | SHINC | 仅工作日窗口内 | 周末计入 |

---

## 复合事件拆分规则（重要）

### 定义

**复合事件**：同一条SOF记录中包含多个性质不同的子事件，需要拆分为多条记录分别判断。

### 典型场景

| 场景 | 原始记录 | 拆分逻辑 |
|------|----------|----------|
| 检疫等待+下雨 | WAITING FOR CLEARANCE. RAIN: 0000-0200 | 拆分为：下雨段（EXCL）+ 非下雨段（INCL） |
| 等泊位+雾 | WAITING FOR BERTH. FOG: 0930-1230 | 拆分为：雾段（EXCL）+ 非雾段（INCL） |
| 装卸中断+雨 | DISCHARGING. RAIN FROM 1700-2015 | 拆分为：装卸段（INCL）+ 雨天段（EXCL） |

### 拆分识别信号

**雨天信号**：
- `RAIN PERIODS: 0000-0200, 0606-1045`
- `RAIN FROM 1700-2015`
- `RAIN AT 0930-1230`
- `RAIN: 0000-0200`

**恶劣天气信号**：
- `FOG PERIODS`
- `STORM PERIODS`
- `HEAVY SEA`

### 拆分方法

**步骤1：解析时间段**
- 提取主事件的时间范围（如0000-2400）
- 提取天气事件的时间段列表（如RAIN: 0000-0200, 0606-1045）

**步骤2：按时间轴拆分**
- 按时间顺序排列所有边界点
- 生成连续的子时间段
- 标注每个子时间段是否为天气事件

**步骤3：分别判断**
- 天气时间段：EXCL（滞期前）/ INCL（滞期后）
- 非天气时间段：按主事件性质判断

### 完整示例

**输入**：
```
30-MAR MON 0000-2400 "WAITING FOR CARGO SAMPLING. RAIN PERIODS: 0000-0200, 0606-1045, 1340-1512"
```

**拆分过程**：
```
原始时间段: 0000-2400 (24h)
天气时间段: 0000-0200, 0606-1045, 1340-1512

时间轴拆分:
- 0000-0200: RAIN (2.0h) → EXCL
- 0200-0606: WAITING (4.1h) → INCL
- 0606-1045: RAIN (4.65h) → EXCL
- 1045-1340: WAITING (2.92h) → INCL
- 1340-1512: RAIN (2.53h) → EXCL
- 1512-2400: WAITING (7.8h) → INCL

时间总和验证: 2.0 + 4.1 + 4.65 + 2.92 + 2.53 + 7.8 = 24.0h ✓
```

**输出JSON**：
```json
[
  {"time_range": "0000-0200", "event": "SUSPENDED DUE TO RAIN", "hours": 2.0, "status": "EXCL", "reason": "Weather interruption - rain (WWD clause)"},
  {"time_range": "0200-0606", "event": "WAITING FOR CARGO SAMPLING", "hours": 4.1, "status": "INCL", "reason": "Working day, waiting for clearance"},
  {"time_range": "0606-1045", "event": "SUSPENDED DUE TO RAIN", "hours": 4.65, "status": "EXCL", "reason": "Weather interruption - rain (WWD clause)"},
  {"time_range": "1045-1340", "event": "WAITING FOR CARGO SAMPLING", "hours": 2.92, "status": "INCL", "reason": "Working day, waiting for clearance"},
  {"time_range": "1340-1512", "event": "SUSPENDED DUE TO RAIN", "hours": 2.53, "status": "EXCL", "reason": "Weather interruption - rain (WWD clause)"},
  {"time_range": "1512-2400", "event": "WAITING FOR CARGO SAMPLING", "hours": 7.8, "status": "INCL", "reason": "Working day, waiting for clearance"}
]
```

### 特殊情况处理

1. **周末/节假日内的天气事件**
   - 周末整体EXCL，不需要拆分天气
   - 拆分也是EXCL，无意义

2. **移泊期间的天气事件**
   - 移泊本身EXCL，不需要拆分天气
   - Shifting永远是EXCL

3. **跨日期的天气事件**
   - 按日期拆分后再判断
   - 例如RAIN FROM 2300-0100，拆分为2300-2400和0000-0100

### LLM判断Prompt示例

```
请判断以下SOF记录，如果包含复合事件（如检疫等待+下雨），请拆分为多条记录：

输入：
30-MAR MON 0000-2400 "WAITING FOR CARGO SAMPLING. RAIN PERIODS: 0000-0200, 0606-1045, 1340-1512"

要求：
1. 识别下雨时间段
2. 拆分为雨天段和非雨天段
3. 分别判断INCL/EXCL
4. 保持时间连续性
5. 时间总和=原始时间
```

---

## 默认排除规则

| rule_id | description | laytime_phase | demurrage_phase | source | remarks |
|---------|-------------|---------------|-----------------|--------|---------|
| SHIFTING | 移泊（ANCHOR UP, POB, NAVIGATION等） | exclude | exclude | implied | 船东行为 |
| OWNER_DELAY | 船东原因延误 | exclude | exclude | implied | 如设备故障、船员罢工 |
| PILOT_WAIT | 等待引航员（非天气原因） | exclude | exclude | implied | 船东行为 |
| WEATHER | 恶劣天气（RAIN, FOG等） | exclude | include | once_on_demurrage | WWD条款 |
| WEEKEND | 周末（Sat/Sun） | exclude | include | contract | SATSHEXEIU等 |
| HOLIDAY | 节假日 | exclude | include | contract | SHEX等 |
| PORT_CLOSE | 港口关闭 | include | include | default | 不可抗力 |
| QUARANTINE | 检疫延误 | include | include | default | 不可抗力 |
| STRIKE | 罢工 | include | include | contract可覆盖 | 需看合同 |
| WAITING_BERTH | 等泊位 | include | include | contract可覆盖 | 需看合同 |

## 规则说明

### SHIFTING（移泊）

**定义**：从锚地移动到泊位的过程

**事件关键词**：
- ANCHOR AWEIGH
- PILOT ON BOARD
- PROCEEDED TO BERTH
- FIRST LINE ASHORE
- ALL MADE FAST

**判断逻辑**：
- laytime期间：排除（船东行为）
- 滞期期间：排除（即使是滞期，船东行为仍排除）

### WEATHER（恶劣天气）

**定义**：影响装卸作业的天气条件

**事件关键词**：
- RAIN
- FOG
- STORM
- HEAVY SEA

**判断逻辑**：
- laytime期间：排除（WWD条款）
- 滞期期间：计入（一旦滞期永久滞期）

### WEEKEND（周末）

**定义**：周六、周日

**判断逻辑**：
- laytime期间：排除（SHEX条款）
- 滞期期间：计入（一旦滞期永久滞期）

**例外情况**：
- 如果合同明确约定"滞期期间周末仍排除"，按合同执行
- 如果是调休工作日，视为工作日

### HOLIDAY（节假日）

**定义**：法定节假日

**判断逻辑**：
- laytime期间：排除（SHEX条款）
- 滞期期间：计入（一旦滞期永久滞期）

**中国港口节假日**：
- 春节
- 清明节
- 劳动节
- 端午节
- 中秋节
- 国庆节

需查阅 `china_holidays_2026.json`

## 合同覆盖

如果合同明确约定与默认规则不同，按合同执行。

**contract.json 覆盖格式**：

```json
{
  "exclusion_overrides": {
    "STRIKE": {
      "laytime_phase": "exclude",
      "demurrage_phase": "exclude"
    },
    "WAITING_BERTH": {
      "laytime_phase": "exclude",
      "demurrage_phase": "exclude"
    }
  }
}
```

## 判断三原则（按优先级）

```
1. 合同有明示？
   └── 有 → 按合同条款执行（第一原则）

2. 合同无明示，查默认规则表？
   └── 有 → 按默认规则执行（第二原则）

3. 无规则可依？
   └── RAG 查书（第三原则）
   └── 无依据 → 标注"待确认"，按"计入"处理
```

## "一旦滞期，永久滞期"原则

### 含义

一旦laytime届满、船舶进入滞期状态，后续所有时间都计入——**不论是否周末、节假日、天气原因**。

### 法律依据

- Lord Reid 在 *The Spalmatori* [1964] 案中的经典解释：
  > "如果承租人在laytime内完成卸货，罢工就不会造成损失——所以滞期后的损失由承租人承担更合理"

- Voylayrules 1993定义："Demurrage shall not be subject to laytime exceptions"

### 唯一例外

1. **合同明确约定**：必须有非常明确的语言（一般性措辞不够）
2. **船东过错**：如船舶不适航、设备故障导致延误

### 滞期后仍排除的情况

| 情况 | 是否计入 | 原因 |
|------|----------|------|
| Shifting/移泊 | ❌ 不计入 | 船东行为 |
| 船东原因延误 | ❌ 不计入 | 船东过错 |
| 合同明确排除 | ❌ 不计入 | 合同约定 |
| 周末/节假日 | ✅ 计入 | 一旦滞期永久滞期 |
| 恶劣天气 | ✅ 计入 | 一旦滞期永久滞期 |
| 罢工 | 看合同 | 需明确条款 |
