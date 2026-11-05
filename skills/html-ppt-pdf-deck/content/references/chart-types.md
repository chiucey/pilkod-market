# Chart.js 图表配置参考

## 圆环图 (Doughnut)

```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['红', '蓝', '绿'],
    datasets: [{
      data: [300, 50, 100],
      backgroundColor: ['#ef4444', '#3b82f6', '#22c55e'],
      borderWidth: 0
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.2,
    cutout: '60%',
    plugins: {
      legend: {
        position: 'right',
        labels: { padding: 16, font: { size: 13 } }
      }
    }
  }
});
```

## 柱状图 (Bar)

```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['1月', '2月', '3月', '4月'],
    datasets: [{
      label: '销售额',
      data: [65, 59, 80, 81],
      backgroundColor: '#3b82f6',
      borderRadius: 4
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true }
    }
  }
});
```

## 折线图 (Line)

```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['周一', '周二', '周三', '周四', '周五'],
    datasets: [{
      label: '访问量',
      data: [12, 19, 15, 22, 30],
      borderColor: '#8b5cf6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      fill: true,
      tension: 0.3
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 2,
    plugins: {
      legend: { position: 'top' }
    }
  }
});
```

## 雷达图 (Radar)

```javascript
new Chart(ctx, {
  type: 'radar',
  data: {
    labels: ['速度', '力量', '耐力', '技术', '防守'],
    datasets: [{
      label: '球员A',
      data: [85, 78, 92, 88, 75],
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.2)'
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.2,
    plugins: {
      legend: { position: 'right' }
    },
    scales: {
      r: {
        beginAtZero: true,
        max: 100
      }
    }
  }
});
```

## 饼图 (Pie)

```javascript
new Chart(ctx, {
  type: 'pie',
  data: {
    labels: ['直接访问', '搜索引擎', '推荐链接', '广告'],
    datasets: [{
      data: [335, 310, 234, 135],
      backgroundColor: [
        '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'
      ]
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: true,
    aspectRatio: 1.3,
    plugins: {
      legend: {
        position: 'right',
        labels: { padding: 12 }
      }
    }
  }
});
```

## 组合图表

```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [
      {
        type: 'bar',
        label: '收入',
        data: [65, 59, 80, 81],
        backgroundColor: '#3b82f6',
        order: 2
      },
      {
        type: 'line',
        label: '增长率',
        data: [null, 15, 35, 42],
        borderColor: '#22c55e',
        tension: 0.3,
        yAxisID: 'y1',
        order: 1
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' }
    },
    scales: {
      y: { type: 'linear', position: 'left' },
      y1: { type: 'linear', position: 'right', grid: { drawOnChartArea: false } }
    }
  }
});
```
