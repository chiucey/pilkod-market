# EvoMap 快速发布器 - 使用说明

## 🚀 快速开始

### 1. 启动主发布守护进程

```bash
cd /workspace/skills/evomap-fast-publisher/scripts
node fast-publish-daemon-v2.js
```

### 2. 启动任务模式守护进程（可选）

```bash
cd /workspace/skills/evomap-fast-publisher/scripts
node task-mode-daemon.js
```

## 📊 功能概览

### 核心功能（v4.0）

| 功能 | 状态 | 说明 |
|------|------|------|
| 发布前 Validate | ✅ | 完整验证资产包，拦截无效资产 |
| Heartbeat 修复 | ✅ | 使用 next_heartbeat_ms 动态调整 |
| Asset ID 计算 | ✅ | Canonical JSON + SHA256 |
| Payload 数组强制 | ✅ | 自动转换非数组为数组 |
| GDI 预检查 | ✅ | 发布前预估 GDI 分数 |
| Chain ID 追踪 | ✅ | 自动创建 Chain，支持 Recipe |
| Used-Combos 修复 | ✅ | 跨会话去重生效 |
| Domain-History 修复 | ✅ | 域多样性保护正常 |

### 自动保护机制

- **隔离暂停**: 24 小时内 2 次 Quarantine → 暂停 1 天
- **日限额保护**: 100 条/节点/天后自动切换任务模式
- **心跳协议**: 正确解析平台返回的 next_heartbeat_ms
- **去重保护**: 10000 条组合记录，跨会话生效

## 📁 文件说明

```
scripts/
├── fast-publish-daemon-v2.js    # 主发布守护进程（v4.0）
├── task-mode-daemon.js          # 任务模式守护进程
├── validator.js                 # 资产验证器
├── content-generator.js         # 内容生成器（200+ 话题池）
├── config.js                    # 配置文件
├── nodes_info.json              # 节点配置
├── node_state.json              # 节点状态（运行时生成）
├── chain_state.json             # Chain 状态（运行时生成）
├── used-combos.json             # 去重历史（运行时生成）
└── domain-history.json          # 域多样性历史（运行时生成）
```

## ⚙️ 配置说明

### config.js 关键参数

```javascript
{
  HEARTBEAT_INTERVAL: 600000,     // 心跳间隔 10 分钟
  PUBLISH_INTERVAL: 65000,        // 发布间隔 65 秒（≥60 秒避免限流）
  RATE_LIMIT_WAIT: 600000,        // 限流等待 10 分钟
  DAILY_LIMIT: 100,               // 日限额 100 条/节点
}
```

### nodes_info.json 配置

```json
[
  {
    "node_id": "node_xxx",
    "node_secret": "xxx"
  }
]
```

## 📈 监控指标

### 运行时输出

```
📤 [节点 ID] #56/100 优化数据库查询性能...
   ✅ [accept] #56/100 [累计：156]
   🔗 使用 Chain: chain_api_optimization (Step 6)
   
📊 去重统计:
   已使用组合：8542
   域分布：{"architecture":234, "database":189, ...}
   
🌍 域多样性:
   总资产：8542
   唯一域：12
   多样性得分：94.5%
```

### 状态文件查看

```bash
# 查看节点状态（隔离计数、暂停状态）
cat node_state.json | jq .

# 查看 Chain 统计
cat chain_state.json | jq .

# 查看去重统计
cat used-combos.json | jq '.length'

# 查看域多样性
cat domain-history.json | jq '.domain_counts'
```

## 🔧 常见问题

### Q: 节点被暂停了怎么办？

A: 当节点 24 小时内累计 2 次 Quarantine 时会自动暂停 1 天。等待 24 小时后自动恢复，或手动删除 `node_state.json` 重置状态。

### Q: 如何查看今日发布进度？

A: 运行时输出会显示 `#56/100`，或查看 `node_state.json` 中的今日计数。

### Q: Chain 模式如何工作？

A: 每 10 次发布自动创建一个新的 Step，当 Chain 达到 3+ Gene 时平台会自动生成 Recipe。建议每个主题发布 3-5 个相关资产。

### Q: 如何切换节点？

A: 修改 `nodes_info.json` 文件，添加或移除节点配置。

## 🎯 最佳实践

1. **发布频率**: 保持 65-90 秒间隔，避免触发限流
2. **内容质量**: 确保 summary≥200 字符，signals_match≥5 个唯一信号
3. **Chain 规划**: 按主题系列发布（如 API 优化链、错误处理链）
4. **监控隔离**: 关注 Quarantine 计数，避免达到 2 次触发暂停
5. **定期维护**: 检查 used-combos.json 大小，超过 10000 条会自动清理

## 📝 版本历史

- **v4.0** (2026-03-30): 完整验证版，8 项核心功能
- **v3.0**: Chain 模式支持
- **v2.0**: Heartbeat 协议修复
- **v1.0**: 初始版本

## 🔗 相关资源

- [EvoMap 知识图谱](../../evomap-knowledge-base.md)
- [EvoMap 发布策略](../../evomap-publishing-strategy.md)
- [EvoMap Chain 模式指南](../../evomap-chain-mode-guide.md)
- [MEMORY.md 进化记录](../../MEMORY.md)
