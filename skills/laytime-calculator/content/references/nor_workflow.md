# NOR/Laytime起算工作流

## 强制要求

**此工作流必须在判断其他时间段之前完成。必须逐步输出每个步骤的结果，不得跳过。**

---

## 步骤1: 确定NOR递交事实

```
输入：SOF
输出：NOR_TENDERED = {日期时间}

示例：
  NOR_TENDERED = 2026-03-23 10:30 MON
```

---

## 步骤2: 判断NOR是否Valid

```
□ 读取合同NOR窗口条款
  - 窗口时间：____
  - 窗口日期：____
  - 排除日期：____

□ 判断NOR_TENDERED是否在窗口内
  - 时间是否在窗口小时内？____
  - 日期是否在窗口日期内？____
  - 判断结果：____

□ 输出：
  - NOR_VALID = {true/false}
  - 如果valid：NOR_VALID_TIME = NOR_TENDERED
  - 如果not valid：需要进入步骤3B
```

### 常见NOR窗口条款

| 条款 | 窗口时间 | 窗口日期 | 说明 |
|------|----------|----------|------|
| Office hours | 08:00-17:00 | MON-FRI | 工作时间 |
| 24 hours | 00:00-24:00 | 每日 | 全天 |
| WWD | 08:00-17:00 | 工作日 | 天气工作日 |
| SHINC | 00:00-24:00 | 每日 | 含周末节假日 |

---

## 步骤3A: 如果NOR Valid

```
□ 读取合同起算规则条款
  - 条款原文：____
  - 规则解读：____

□ 计算起算时间
  - 起算规则要求：____
  - 需要找到"下一个工作日"？____

□ 执行步骤4：计算下一个工作日

□ 输出：
  - LAYTIME_COMMENCED = {日期时间}
  - 依据：{合同条款原文}
```

### 常见起算规则

| 条款 | 起算时间 | 示例 |
|------|----------|------|
| Next working day 08:00 | 下一工作日08:00 | NOR 23日10:30 → 24日08:00 |
| 24 hours after NOR | NOR后24小时 | NOR 23日10:30 → 24日10:30 |
| Same day if before XX:XX | 当天/次日分界 | NOR 10:00 → 当天，NOR 14:00 → 次日 |

---

## 步骤3B: 如果NOR Not Valid

```
□ 读取合同关于无效NOR的处理条款
  - 条款原文：____
  - 处理方式：____
    □ 视为在下一个可递交时间自动递交
    □ 必须重新递交

□ 计算下一个可递交窗口
  - 从NOR_TENDERED开始向后查找
  - 排除：周六/周日/假期
  - 下一个可递交窗口 = ____

□ NOR_DEEMED_TIME = 下一个可递交窗口的第一刻时间

□ 读取合同起算规则条款
  - 条款原文：____
  - 规则解读：____

□ 执行步骤4：计算下一个工作日

□ 输出：
  - NOR_DEEMED_TIME = {日期时间}
  - LAYTIME_COMMENCED = {日期时间}
  - 依据：{合同条款原文}
```

---

## 步骤4: 计算"下一个工作日"（必须检查假期）

```
□ 读取假期文件
  - 文件路径：用户上传/AL_WATHBA_ZHANGZHOU_JIANGYIN_BARLEY/uploads/china_holidays_2026.json
  - 或从sof_parsed.json的holiday_matches读取

□ 检查目标日期
  目标日期：____
  □ 是否为周六？____
  □ 是否为周日？____
  □ 是否为假期？____

□ 如果是休息日，向后推移
  - 下一个候选日期：____
  - 重复检查直到找到工作日

□ 检查调休（周末改为工作日）
  - 读取china_holidays_2026.json的workdays_on_weekend
  - 目标日期是否在调休列表中？____
  - 如果是，视为工作日

□ 输出：
  - NEXT_WORKING_DAY = {日期}
```

---

## 步骤5: 输出完整时间线

```
========================================
NOR/LAYTIME时间线
========================================
NOR_TENDERED: {日期时间}
NOR_VALID: {true/false}
NOR_VALID_TIME / NOR_DEEMED_TIME: {日期时间}
LAYTIME_COMMENCED: {日期时间}

依据：
- NOR窗口条款：{原文}
- 起算规则条款：{原文}
- 假期排除：{具体日期}
========================================
```

---

## 此时间线必须写入sof_parsed.json的nor_timeline字段

```json
{
  "nor_timeline": {
    "nor_tendered": "2026-03-23T10:30",
    "nor_valid": true,
    "nor_valid_time": "2026-03-23T10:30",
    "laytime_commenced": "2026-03-24T08:00",
    "clause_reference": {
      "nor_window": "08:00-17:00 MON-FRI",
      "commencement": "Next working day 08:00"
    },
    "holidays_excluded": ["2026-03-23"]
  }
}
```

---

## 常见错误

| 错误 | 正确理解 |
|------|----------|
| NOR Valid = Laytime Commenced | ❌ 错误。NOR可能在窗口内递交，但laytime仍需按起算规则计算 |
| 周末递交NOR视为周一递交 | ❌ 错误。需要看合同条款，可能视为周一递交，laytime周二起算 |
| 假期不看当年假期表 | ❌ 错误。必须查阅当年的假期文件，每年不同 |
| 不检查调休 | ❌ 错误。中国有调休制度，周末可能是工作日 |
