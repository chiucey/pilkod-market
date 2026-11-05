---
name: performance-metrics-dashboard
description: Provides real-time performance metrics and visualization for the evolution engine, tracking evolution cycles, success rates, gene utilization, and system health. Use when monitoring evolver performance, diagnosing issues, or generating performance reports.
---

# Performance Metrics Dashboard

实时性能指标和可视化仪表板，用于监控进化引擎的运行状态。

## 功能特性

- 📊 **进化统计**: 总周期数、成功率、近期趋势
- 🧬 **基因利用率**: 最常用基因、基因分布
- 🎯 **意图分布**: Repair/Optimize/Innovate 比例
- 💾 **系统健康**: 内存图大小、事件数量、健康状态
- 📈 **性能评估**: 整体效率、创新率

## 使用方式

### 在 Node.js 中使用

```javascript
const metrics = require('./skills/performance-metrics-dashboard');

// 获取完整报告（文本格式）
const report = metrics.main();
console.log(report);

// 获取 JSON 格式数据
const data = metrics.main({ format: 'json' });
console.log(data);

// 单独获取进化统计
const evolutionStats = metrics.calculateEvolutionStats();

// 单独获取系统健康
const systemHealth = metrics.getSystemHealth();

// 生成仪表板数据
const dashboard = metrics.generateDashboardData();
```

### 命令行使用

```bash
cd /root/.openclaw/skills/evolver-1.39.0
node -e "console.log(require('./skills/performance-metrics-dashboard').main())"
```

## 输出示例

```
📊 Evolver Performance Metrics Dashboard
==================================================
Generated: 3/30/2026, 2:40:00 AM

🔄 Evolution Statistics
------------------------------
Total Cycles: 150
Success Rate: 94.67%
Recent Success Rate (last 10): 95.00%
Active Genes: 12
Most Used Gene: gene_gep_repair_from_errors (85 uses)
Average Blast Radius: 2.3 files/cycle

Intent Distribution:
  Repair: 80
  Optimize: 25
  Innovate: 45

💾 System Health
------------------------------
Memory Graph: 3200 KB (54550 events)
Memory Health: ⚠️ warning
Node: v22.17.0 (linux/x64)

📈 Performance Assessment
------------------------------
Overall Efficiency: excellent
Innovation Rate: 30.00%

==================================================
```

## 使用场景

1. **定期检查**: 在心跳检查时运行，监控进化系统健康
2. **问题诊断**: 当成功率下降或失败率上升时分析原因
3. **优化决策**: 根据创新率调整进化策略
4. **报告生成**: 生成 Feishu 卡片报告发送给用户

## 集成示例

### 与 Feishu 集成

```javascript
const metrics = require('./skills/performance-metrics-dashboard');
const post = require('./skills/feishu-post');

const report = metrics.main();
await post.send({ text: report });
```

### 定时检查

```javascript
// 在 HEARTBEAT.md 中添加
- 检查 evolver 性能指标
- 成功率 < 80% 时告警
- 内存图 > 100MB 时压缩
```

## 指标说明

### 成功率 (Success Rate)
- **> 90%**: Excellent - 系统运行良好
- **70-90%**: Good - 正常波动
- **< 70%**: Needs Improvement - 需要检查失败原因

### 创新率 (Innovation Rate)
- 建议保持在 40-60% 之间
- 过低表示系统过于保守
- 过高可能表示稳定性不足

### 内存图健康
- **< 100MB**: Healthy
- **> 100MB**: Warning - 考虑压缩
- **> 500MB**: Critical - 立即压缩

## 相关文件

- `assets/gep/capsules.json` - 进化胶囊数据
- `assets/gep/genes.json` - 基因库数据
- `memory/memory_graph.jsonl` - 内存图事件

## 注意事项

1. 仪表板读取本地文件，确保在 evolver 目录内运行
2. 首次运行可能需要几秒钟加载数据
3. 内存图过大时会影响加载速度，定期压缩
