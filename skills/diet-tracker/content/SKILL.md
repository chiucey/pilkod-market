---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: add87456f5f6746fb1641d03e7aecbd5
    PropagateID: add87456f5f6746fb1641d03e7aecbd5
    ReservedCode1: 3044022056a6939442d6518609a981dfbea9587c305f6fadaf6371dbdb6536c9cc90fd6902205976f4cc7142a9de78281e64da44314e01c78a71d5796806148484c11003adc6
    ReservedCode2: 3046022100b3f86d27e8280a2f20af8fd396bb061042306933aca62e9fef1bb9921754ddc3022100bc597010b036542f811f54cb3d9bcc803500e9bbc06690bb88138f732c607bac
description: 平哥的减脂饮食追踪技能。当平哥发送食物照片、报体重、记录饮食数据时，自动执行：分析食物→估算热量→存档图片→更新日记文件→更新媒体索引。不要凭感觉填数据，严格按规范执行。触发场景：(1) 收到食物照片 (2) 报告体重 (3) 要求生成日报/报告 (4) 查询历史记录
name: diet-tracker
---

# Diet Tracker — 减脂饮食追踪规范

## 核心原则

每次收到平哥的饮食相关消息，**必须按顺序执行以下步骤**，不得跳过：

1. **分析食物** → 用 images_understand 识别内容
2. **估算热量** → 输出 kcal 范围
3. **立即存档** → cp 到 `memory/imgs/`
4. **更新日记** → 写入 `memory/YYYY-MM-DD.md`
5. **更新索引** → 追加到 `memory/media_index.md`

---

## 文件规范

### 每日日记：`memory/YYYY-MM-DD.md`

每次编辑前先读取文件，再用 edit 修改。

```
# YYYY-MM-DD Daily Log

## 📊 体重记录
- **晨起体重**: XX.X KG ⏰ HH:MM
- 昨日（MM-DD）: XX.X KG
- 累计减重: X.X KG（计划起始日基准 → 当前）
- 目标体重: 85 KG
- 距目标: XX.X KG
- BMI: XX.X（身高183cm固定）

## 🍽️ 饮食记录
- **早餐** ⏰ HH:MM — [食物名称] → 约 XXX kcal
- **午餐** ⏰ HH:MM — [食物名称] → 约 XXX kcal
- **下午茶** ⏰ HH:MM — [食物名称] → 约 XXX kcal
- **晚餐** ⏰ HH:MM — [食物名称] → 约 XXX kcal
- **晚加餐** ⏰ HH:MM — [食物名称] → 约 XXX kcal
- **全天合计**: 约 XXXX kcal（目标2000kcal，超出约XXXkcal）

## 🏃 运动记录
- （待更新）

## 💧 状态
- 饮水量：待记录
- 睡眠：待记录

## 📝 备注
- 📎 图片存档：
  - `imgs/YYYY-MM-DD-xxx.jpg` — [内容描述]
```

### 媒体索引：`memory/media_index.md`

每次存档后，在"4月"表格最前面插入新行：

```
| 04-13 | 📷 | 晚加餐 — 黄李子3颗 | `imgs/2026-04-13-evening-snack.jpg` |
```

---

## 热量估算标准

| 食物类型 | 单份热量 |
|---------|---------|
| 面包/糕点 | 150-300 kcal/块 |
| 咖啡（拿铁/美式） | 50-200 kcal |
| 中式炒菜（一份） | 200-400 kcal |
| 火锅（牛肉200g） | 300-400 kcal |
| 米饭（一碗） | 260-300 kcal |
| 水果（苹果/梨/李子） | 30-60 kcal/个 |
| 啤酒（500ml） | 180-250 kcal |
| 奶昔/奶茶 | 200-400 kcal |

---

## 报告生成规范

生成任何日报/报告前，**必须先读取 report_data_schema.md** 核对数据项完整性。

报告日期校验：标题日期 **必须等于今日实际日期**，发送前逐项核对。

---

## 常见错误预防

- ❌ 不得用"顺手"的数字替代实际数据
- ❌ 不得发送未经校验日期的报告
- ❌ 不得只分析不存档（图片必须当日归档）
- ❌ 不得在报告内虚构数据（缺失项标注"待更新"）

---

## 参考文件

- `references/report_data_schema.md` — 报告必须包含的数据项清单
- `references/daily_format.md` — 每日日记详细格式说明
- `references/calorie_reference.md` — 常见食物热量参考表
