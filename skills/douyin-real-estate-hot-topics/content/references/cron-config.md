# 定时任务配置指南

## Cron表达式说明

```
┌───────────── 分钟 (0-59)
│ ┌───────────── 小时 (0-23)
│ │ ┌───────────── 日期 (1-31)
│ │ │ ┌───────────── 月份 (1-12)
│ │ │ │ ┌───────────── 星期 (0-7, 0和7是周日)
│ │ │ │ │
* * * * *
```

## 推荐配置

### 每日房产日报（早上9点）

```json
{
  "job_title": "抖音房产热门话题日报",
  "cron_expression": "0 9 * * *",
  "job_instruction": "执行douyin-real-estate-hot-topics技能，搜索当日抖音房产热门话题前10名，提取浏览量、类型、出处信息，生成结构化日报并保存到data/daily_report_{date}.md"
}
```

### 每日房产晚报（晚上8点）

```json
{
  "job_title": "抖音房产热门话题晚报",
  "cron_expression": "0 20 * * *",
  "job_instruction": "执行douyin-real-estate-hot-topics技能，搜索当日抖音房产热门话题前10名，提取浏览量、类型、出处信息，生成结构化晚报并保存到data/evening_report_{date}.md"
}
```

### 工作日早报（周一至周五9点）

```json
{
  "job_title": "工作日房产热门话题早报",
  "cron_expression": "0 9 * * 1-5",
  "job_instruction": "执行douyin-real-estate-hot-topics技能，搜索当日抖音房产热门话题前10名，仅在工作日执行，生成日报并保存到data/weekday_report_{date}.md"
}
```

## 输出文件命名规范

- 日报: `daily_report_YYYY-MM-DD.md`
- 晚报: `evening_report_YYYY-MM-DD.md`
- 周报: `weekly_report_YYYY-WXX.md`
- 月报: `monthly_report_YYYY-MM.md`

## 数据保存路径

```
data/
├── daily/
│   └── daily_report_2024-01-01.md
├── weekly/
│   └── weekly_report_2024-W01.md
└── monthly/
    └── monthly_report_2024-01.md
```
