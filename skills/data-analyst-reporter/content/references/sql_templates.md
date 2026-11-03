# SQL 分析模板库

经过验证的生产级 SQL 查询模板，适用于常见业务分析场景。所有模板均基于标准 ANSI SQL，可适配 BigQuery、Snowflake、PostgreSQL、MySQL 等主流数据仓库。

---

## 1. 高管仪表板 — 月度核心指标

```sql
-- 月度关键业务指标仪表板
WITH monthly_metrics AS (
  SELECT
    DATE_TRUNC('month', date)          AS month,
    SUM(revenue)                        AS monthly_revenue,
    COUNT(DISTINCT customer_id)         AS active_customers,
    COUNT(DISTINCT order_id)            AS total_orders,
    AVG(order_value)                    AS avg_order_value,
    SUM(revenue) / COUNT(DISTINCT customer_id) AS revenue_per_customer
  FROM transactions
  WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 13 MONTH)  -- 13个月含当月
  GROUP BY DATE_TRUNC('month', date)
),
growth_calculations AS (
  SELECT *,
    LAG(monthly_revenue, 1)  OVER (ORDER BY month) AS prev_month_revenue,
    LAG(monthly_revenue, 12) OVER (ORDER BY month) AS prev_year_revenue,
    ROUND(
      (monthly_revenue - LAG(monthly_revenue,1) OVER (ORDER BY month)) /
       NULLIF(LAG(monthly_revenue,1) OVER (ORDER BY month), 0) * 100, 2
    ) AS mom_growth_pct,
    ROUND(
      (monthly_revenue - LAG(monthly_revenue,12) OVER (ORDER BY month)) /
       NULLIF(LAG(monthly_revenue,12) OVER (ORDER BY month), 0) * 100, 2
    ) AS yoy_growth_pct
  FROM monthly_metrics
)
SELECT
  month,
  monthly_revenue,
  active_customers,
  total_orders,
  avg_order_value,
  revenue_per_customer,
  mom_growth_pct,
  yoy_growth_pct,
  CASE
    WHEN mom_growth_pct > 10  THEN '高增长 🟢'
    WHEN mom_growth_pct > 0   THEN '正增长 🟡'
    WHEN mom_growth_pct IS NULL THEN '无数据 ⚪'
    ELSE '下滑 🔴'
  END AS growth_status
FROM growth_calculations
ORDER BY month DESC;
```

---

## 2. 客户保留与流失分析

```sql
-- 月度客户留存与流失率
WITH customer_activity AS (
  SELECT
    customer_id,
    DATE_TRUNC('month', order_date) AS order_month
  FROM orders
  GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
cohort_analysis AS (
  SELECT
    customer_id,
    MIN(order_month) AS cohort_month   -- 首次购买月
  FROM customer_activity
  GROUP BY customer_id
),
retention AS (
  SELECT
    c.cohort_month,
    a.order_month,
    DATEDIFF('month', c.cohort_month, a.order_month) AS months_since_first,
    COUNT(DISTINCT a.customer_id) AS retained_customers
  FROM cohort_analysis c
  JOIN customer_activity a ON c.customer_id = a.customer_id
  GROUP BY c.cohort_month, a.order_month, months_since_first
),
cohort_size AS (
  SELECT cohort_month, COUNT(DISTINCT customer_id) AS cohort_customers
  FROM cohort_analysis
  GROUP BY cohort_month
)
SELECT
  r.cohort_month,
  r.months_since_first,
  cs.cohort_customers,
  r.retained_customers,
  ROUND(r.retained_customers::FLOAT / cs.cohort_customers * 100, 2) AS retention_rate
FROM retention r
JOIN cohort_size cs ON r.cohort_month = cs.cohort_month
ORDER BY r.cohort_month, r.months_since_first;
```

---

## 3. 营销归因分析 — 多触点模型

```sql
-- U型归因（首触40% + 末触40% + 中间触点均分20%）
WITH customer_touchpoints AS (
  SELECT
    customer_id,
    channel,
    campaign_name,
    touchpoint_date,
    conversion_date,
    revenue,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY touchpoint_date)        AS touch_seq,
    COUNT(*)      OVER (PARTITION BY customer_id)                                AS total_touches
  FROM marketing_touchpoints mt
  JOIN conversions c USING (customer_id)
  WHERE mt.touchpoint_date <= c.conversion_date
),
attribution_weights AS (
  SELECT *,
    CASE
      WHEN total_touches = 1                          THEN 1.0
      WHEN touch_seq = 1                              THEN 0.4
      WHEN touch_seq = total_touches                  THEN 0.4
      ELSE 0.2 / NULLIF(total_touches - 2, 0)
    END AS weight
  FROM customer_touchpoints
)
SELECT
  channel,
  campaign_name,
  ROUND(SUM(revenue * weight), 2)        AS attributed_revenue,
  COUNT(DISTINCT customer_id)            AS attributed_conversions,
  ROUND(SUM(revenue * weight) /
    NULLIF(COUNT(DISTINCT customer_id),0), 2) AS revenue_per_conversion
FROM attribution_weights
GROUP BY channel, campaign_name
ORDER BY attributed_revenue DESC;
```

---

## 4. 活动 ROI 汇总

```sql
SELECT
  campaign_name,
  channel,
  SUM(spend)                                           AS total_spend,
  SUM(attributed_revenue)                              AS total_revenue,
  SUM(attributed_revenue) - SUM(spend)                 AS gross_profit,
  ROUND((SUM(attributed_revenue) - SUM(spend)) /
         NULLIF(SUM(spend), 0) * 100, 2)               AS roi_pct,
  ROUND(SUM(attributed_revenue) /
         NULLIF(SUM(spend), 0), 2)                     AS roas,
  COUNT(DISTINCT conversions)                          AS total_conversions,
  ROUND(SUM(spend) /
         NULLIF(COUNT(DISTINCT conversions),0), 2)     AS cost_per_conversion
FROM campaign_performance
WHERE date >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
GROUP BY campaign_name, channel
HAVING SUM(spend) > 100
ORDER BY roi_pct DESC;
```

---

## 5. 漏斗转化分析

```sql
-- 用户转化漏斗（各阶段转化率）
WITH funnel_stages AS (
  SELECT
    DATE_TRUNC('week', event_date) AS week,
    COUNT(DISTINCT CASE WHEN stage = 'visit'    THEN user_id END) AS visits,
    COUNT(DISTINCT CASE WHEN stage = 'signup'   THEN user_id END) AS signups,
    COUNT(DISTINCT CASE WHEN stage = 'trial'    THEN user_id END) AS trials,
    COUNT(DISTINCT CASE WHEN stage = 'purchase' THEN user_id END) AS purchases
  FROM user_events
  WHERE event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 WEEK)
  GROUP BY DATE_TRUNC('week', event_date)
)
SELECT
  week,
  visits,
  signups,
  trials,
  purchases,
  ROUND(signups::FLOAT   / NULLIF(visits, 0)   * 100, 2) AS visit_to_signup_pct,
  ROUND(trials::FLOAT    / NULLIF(signups, 0)  * 100, 2) AS signup_to_trial_pct,
  ROUND(purchases::FLOAT / NULLIF(trials, 0)   * 100, 2) AS trial_to_purchase_pct,
  ROUND(purchases::FLOAT / NULLIF(visits, 0)   * 100, 2) AS overall_conversion_pct
FROM funnel_stages
ORDER BY week DESC;
```

---

## 6. 产品使用频率分析

```sql
-- DAU / WAU / MAU 及黏性指数
WITH dau AS (
  SELECT event_date, COUNT(DISTINCT user_id) AS daily_users
  FROM user_events GROUP BY event_date
),
wau AS (
  SELECT
    DATE_TRUNC('week', event_date) AS week,
    COUNT(DISTINCT user_id)        AS weekly_users
  FROM user_events GROUP BY DATE_TRUNC('week', event_date)
),
mau AS (
  SELECT
    DATE_TRUNC('month', event_date) AS month,
    COUNT(DISTINCT user_id)         AS monthly_users
  FROM user_events GROUP BY DATE_TRUNC('month', event_date)
)
SELECT
  m.month,
  m.monthly_users              AS mau,
  AVG(d.daily_users)           AS avg_dau,
  ROUND(AVG(d.daily_users) /
    NULLIF(m.monthly_users,0) * 100, 2) AS dau_mau_ratio
FROM mau m
JOIN dau d ON DATE_TRUNC('month', d.event_date) = m.month
GROUP BY m.month, m.monthly_users
ORDER BY m.month DESC;
```

---

## 7. 数据质量检查

```sql
-- 快速数据质量审计
SELECT
  'total_rows'         AS check_name, COUNT(*)                           AS value FROM your_table
UNION ALL
SELECT 'null_key_field',  COUNT(*) - COUNT(key_field)                   FROM your_table
UNION ALL
SELECT 'null_date',       COUNT(*) - COUNT(date_field)                  FROM your_table
UNION ALL
SELECT 'null_amount',     COUNT(*) - COUNT(amount_field)                FROM your_table
UNION ALL
SELECT 'duplicate_keys',
  COUNT(*) - COUNT(DISTINCT key_field)                                   FROM your_table
UNION ALL
SELECT 'negative_amounts',
  COUNT(CASE WHEN amount_field < 0 THEN 1 END)                          FROM your_table
UNION ALL
SELECT 'future_dates',
  COUNT(CASE WHEN date_field > CURRENT_DATE() THEN 1 END)               FROM your_table;
```

---

## 适配说明

| 函数 | BigQuery | Snowflake | PostgreSQL | MySQL |
|------|----------|-----------|------------|-------|
| 日期截断 | `DATE_TRUNC(date, MONTH)` | `DATE_TRUNC('month', date)` | `DATE_TRUNC('month', date)` | `DATE_FORMAT(date,'%Y-%m-01')` |
| 日期差值 | `DATE_DIFF(a,b,DAY)` | `DATEDIFF('day',b,a)` | `a - b` | `DATEDIFF(a,b)` |
| 类型转换 | `CAST(x AS FLOAT64)` | `x::FLOAT` | `x::FLOAT` | `CAST(x AS DECIMAL)` |
| 行号 | `ROW_NUMBER() OVER(...)` | ✅ 相同 | ✅ 相同 | ✅ 相同（MySQL 8+） |
