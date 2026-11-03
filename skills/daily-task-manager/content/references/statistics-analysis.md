# 统计分析方法

## 统计指标体系

### 1. 基础完成指标

| 指标 | 计算公式 | 说明 |
|------|----------|------|
| 完成率 | 已完成数/总任务数 | 整体完成情况 |
| A级完成率 | A已完成/A总数 | 核心任务达成 |
| B级完成率 | B已完成/B总数 | 重要任务达成 |
| 及时完成率 | 当日完成/当日新增 | 新增任务完成效率 |
| 继承任务完成率 | 继承完成/继承总数 | 遗留任务处理效率 |

### 2. 时间维度指标

| 指标 | 计算方式 | 应用场景 |
|------|----------|----------|
| 日均任务数 | 总任务数/天数 | 工作量评估 |
| 完成耗时 | 平均完成时间 | 时间管理优化 |
| 高效时段 | 完成率最高时段 | 最佳工作时段推荐 |
| 延迟趋势 | C/D级占比变化 | 任务复杂度追踪 |

### 3. 行为模式指标

| 指标 | 说明 |
|------|------|
| 任务添加峰值 | 用户最常添加任务的时段/日期 |
| 完成时间偏好 | 用户倾向于何时完成任务 |
| 优先级漂移 | 任务优先级是否经常被调整 |
| 任务来源分布 | 新增 vs 继承任务比例 |

## 统计分析查询

### 基础统计（日/周/月）

```sql
-- 每日统计
SELECT
  COUNT(*) as total_tasks,
  COUNT(*) FILTER (WHERE status = 'completed') as completed,
  COUNT(*) FILTER (WHERE priority = 'A') as priority_a,
  COUNT(*) FILTER (WHERE priority = 'A' AND status = 'completed') as priority_a_done,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC /
    NULLIF(COUNT(*), 0) * 100, 2
  ) as completion_rate
FROM tasks
WHERE user_id = $1 AND created_date = $2;
```

### 周趋势分析

```sql
-- 近7天趋势
SELECT
  date,
  total_tasks,
  completed_tasks,
  completion_rate,
  priority_a,
  priority_b,
  LAG(completed_tasks) OVER (ORDER BY date) as yesterday_completed,
  completed_tasks - LAG(completed_tasks) OVER (ORDER BY date) as change
FROM daily_stats
WHERE user_id = $1
  AND date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date ASC;
```

### 月度汇总

```sql
-- 月度汇总统计
SELECT
  DATE_TRUNC('month', date) as month,
  AVG(total_tasks)::INTEGER as avg_daily_tasks,
  AVG(completion_rate) as avg_completion_rate,
  SUM(total_tasks) as total_tasks,
  SUM(completed_tasks) as completed_tasks,
  MAX(completion_rate) as best_day,
  MIN(completion_rate) as worst_day,
  COUNT(*) FILTER (WHERE completion_rate >= 80) as good_days
FROM daily_stats
WHERE user_id = $1
  AND date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
GROUP BY DATE_TRUNC('month', date);
```

### 优先级分析

```sql
-- 优先级完成率对比
SELECT
  priority,
  COUNT(*) as total,
  COUNT(*) FILTER (WHERE status = 'completed') as completed,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC /
    COUNT(*) * 100, 2
  ) as completion_rate
FROM tasks
WHERE user_id = $1
  AND created_date >= $2
  AND created_date <= $3
GROUP BY priority
ORDER BY
  CASE priority
    WHEN 'A' THEN 1
    WHEN 'B' THEN 2
    WHEN 'C' THEN 3
    WHEN 'D' THEN 4
  END;
```

## 统计分析前端组件

### 统计卡片组件

```javascript
function StatCard({ title, value, change, trend, icon }) {
  const trendColor = trend === 'up' ? 'text-green-500' : 'text-red-500';
  const trendIcon = trend === 'up' ? '↑' : '↓';

  return (
    <div className="bg-white rounded-xl shadow-sm p-4">
      <div className="flex items-center justify-between">
        <span className="text-gray-500 text-sm">{title}</span>
        <span className="text-lg">{icon}</span>
      </div>
      <div className="mt-2">
        <span className="text-2xl font-bold">{value}</span>
        {change && (
          <span className={`ml-2 text-sm ${trendColor}`}>
            {trendIcon}{change}
          </span>
        )}
      </div>
    </div>
  );
}
```

### 周趋势图表

```javascript
function WeekTrendChart({ data }) {
  const maxValue = Math.max(...data.map(d => d.total_tasks));

  return (
    <div className="flex items-end justify-between h-40 gap-2">
      {data.map((day, i) => (
        <div key={i} className="flex-1 flex flex-col items-center">
          <div className="w-full bg-gray-200 rounded-t relative h-full">
            <div
              className="absolute bottom-0 w-full bg-blue-500 rounded-t"
              style={{ height: `${(day.completed_tasks / maxValue) * 100}%` }}
            />
          </div>
          <span className="text-xs mt-2">{day.label}</span>
          <span className="text-xs text-gray-500">{day.completed_tasks}/{day.total_tasks}</span>
        </div>
      ))}
    </div>
  );
}
```

### 复盘报告生成

```javascript
function generateWeeklyReport(userId, weekStart) {
  return {
    period: `${weekStart} ~ ${weekStart + 6}`,
    summary: {
      totalTasks: sumWeekly('total_tasks'),
      completed: sumWeekly('completed_tasks'),
      completionRate: avgWeekly('completion_rate'),
    },
    byPriority: {
      A: { total: countWeekly('A'), completed: countCompletedWeekly('A'), rate: calcRateWeekly('A') },
      B: { total: countWeekly('B'), completed: countCompletedWeekly('B'), rate: calcRateWeekly('B') },
      C: { total: countWeekly('C'), completed: countCompletedWeekly('C'), rate: calcRateWeekly('C') },
      D: { total: countWeekly('D'), completed: countCompletedWeekly('D'), rate: calcRateWeekly('D') },
    },
    insights: generateInsights(data),
    recommendations: generateRecommendations(data)
  };
}
```

## 数据可视化建议

1. **完成率环形图** - 直观展示整体完成情况
2. **优先级柱状图** - 对比各级别完成率
3. **周趋势折线图** - 追踪每日变化趋势
4. **热力图** - 按时间段展示任务分布
