# 每日日记格式说明

## 文件位置
`memory/YYYY-MM-DD.md`

## 完整格式模板

```markdown
# YYYY-MM-DD Daily Log

## 📊 体重记录
- **晨起体重**: XX.X KG ⏰ HH:MM
- 昨日（MM-DD）: XX.X KG
- 累计减重: X.X KG（计划起始日基准102.4KG → 当前）
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
- [运动类型] ⏰ HH:MM — [距离/时长] → 消耗约 XXX kcal

## 💧 状态
- 饮水量：X L
- 睡眠：X 小时

## 📝 备注
- 备注内容
- 📎 图片存档：
  - `imgs/YYYY-MM-DD-xxx.jpg` — [内容描述]
```

## 时间戳格式
- 体重记录：⏰ HH:MM（24小时制）
- 饮食记录：⏰ HH:MM（24小时制）
- 所有时间使用当地时间

## 热量估算要求
- 必须给出估算范围（最小-最大）
- 格式：`→ 约 XXX-YYY kcal`
- 不得虚构：无法估算时标注"待评估"

## 编辑流程
1. 先用 read 工具读取当前文件内容
2. 确认要修改的位置
3. 用 edit 工具精确替换（old_string 必须完全匹配）
4. 编辑后再次 read 确认修改成功

## 存档节点
- 收到图片后立即存档，禁止只分析不存
- 每次存档后同步更新 media_index.md
- 存档路径：`memory/imgs/YYYY-MM-DD-描述.webp`
