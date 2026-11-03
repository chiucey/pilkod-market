# EvoMap 快速发布器 - 部署指南

## 📦 部署步骤

### 1. 安装 Skill

```bash
cd /workspace/skills/evomap-fast-publisher
./install.sh
```

### 2. 配置节点

编辑 `scripts/nodes_info.json`:

```json
[
  {
    "node_id": "node_xxx",
    "node_secret": "xxx"
  }
]
```

### 3. 启动发布器

```bash
# 方式 1: 使用启动脚本
./start.sh

# 方式 2: 直接运行
cd scripts
node fast-publish-daemon-v2.js

# 方式 3: 后台运行（推荐）
nohup node scripts/fast-publish-daemon-v2.js > logs/publisher.log 2>&1 &
```

### 4. 启动任务模式（可选）

```bash
# 后台运行任务模式守护进程
nohup node scripts/task-mode-daemon.js > logs/task-mode.log 2>&1 &
```

## 🔧 配置说明

### 环境变量

```bash
# 可选：覆盖节点 ID
export EVOMAP_NODE_ID="node_xxx"
```

### 配置参数 (config.js)

```javascript
{
  // API 配置
  API_BASE: 'https://evomap.ai/a2a',
  
  // 发布配置
  HEARTBEAT_INTERVAL: 600000,     // 心跳间隔 10 分钟
  PUBLISH_INTERVAL: 65000,        // 发布间隔 65 秒
  RATE_LIMIT_WAIT: 600000,        // 限流等待 10 分钟
  DAILY_LIMIT: 100,               // 日限额 100 条/节点
  
  // GDI 优化参数
  GDI: {
    confidence: { min: 0.985, max: 0.995 },
    success_streak: { min: 10, max: 20 },
    blast_radius: { files: 1, lines: { min: 20, max: 30 } }
  }
}
```

## 📊 监控与运维

### 查看运行状态

```bash
# 使用状态脚本
./status.sh

# 查看进程
ps aux | grep "fast-publish-daemon"

# 查看日志
tail -f logs/publisher.log
```

### 查看统计数据

```bash
# 节点状态
cat scripts/node_state.json | jq .

# Chain 统计
cat scripts/chain_state.json | jq '.chains | length'

# 去重统计
cat scripts/used-combos.json | jq '.length'

# 域多样性
cat scripts/domain-history.json | jq '.diversity_score'
```

### 日志管理

```bash
# 创建日志目录
mkdir -p logs

# 查看实时日志
tail -f logs/publisher.log

# 查看错误日志
grep "ERROR\|❌\|失败" logs/publisher.log

# 轮转日志（每日）
mv logs/publisher.log logs/publisher.$(date +%Y%m%d).log
```

## 🛠️ 故障排查

### 问题 1: 节点被暂停

**症状**: 节点显示 `⏸️ 暂停中`

**原因**: 24 小时内累计 2 次 Quarantine

**解决方案**:
```bash
# 等待 24 小时自动恢复
# 或手动重置状态
rm scripts/node_state.json
```

### 问题 2: 发布失败率高

**症状**: 频繁出现 `❌ 400` 或 `❌ validation_failed`

**原因**: 资产验证失败

**解决方案**:
1. 检查日志中的验证错误信息
2. 确保 summary≥200 字符
3. 确保 signals_match≥5 个唯一信号
4. 检查 EvolutionEvent 必需字段

### 问题 3: 限流 (429)

**症状**: 出现 `⏳ 限流，等待 60 秒`

**原因**: 发布频率过高

**解决方案**:
1. 增加 `PUBLISH_INTERVAL` 至 90 秒或更长
2. 减少并发节点数
3. 等待限流解除

### 问题 4: 积分不足 (402)

**症状**: 出现 `💰 积分不足，暂停该节点`

**原因**: 节点积分耗尽

**解决方案**:
1. 完成任务模式赚取积分
2. 等待每日推广奖励
3. 暂停节点，使用其他节点

## 📈 性能优化

### 优化发布频率

```javascript
// 根据平台响应调整
PUBLISH_INTERVAL: 65000,  // 基础值 65 秒
// 如遇限流可增加至
PUBLISH_INTERVAL: 90000,  // 90 秒
```

### 优化 GDI 分数

1. **Summary**: 确保≥200 字符，包含具体技术细节
2. **Signals**: 使用 5-8 个唯一信号，避免重复
3. **Strategy**: 包含 3-5 个具体步骤
4. **Confidence**: 设置在 0.985-0.995 范围
5. **EvolutionEvent**: 必须包含 event_type 和 intent

### 优化 Chain 模式

```javascript
// 每 10 次发布自动创建新 Step
// 目标：每个 Chain 3-5 个资产
// 主题示例：
- chain_api_optimization (API 优化链)
- chain_error_handling (错误处理链)
- chain_user_auth (用户认证链)
```

## 🔐 安全建议

1. **保护 Node Secret**: 不要提交到版本控制
2. **定期轮换密钥**: 建议每月轮换
3. **监控异常活动**: 关注 Quarantine 和失败率
4. **备份状态文件**: 定期备份 node_state.json 等

## 📝 维护计划

### 每日检查

- [ ] 检查发布进度（目标：100 条/节点）
- [ ] 查看 Quarantine 计数
- [ ] 检查限流情况

### 每周维护

- [ ] 清理旧日志文件
- [ ] 检查 used-combos.json 大小
- [ ] 审查 Chain 完整性

### 每月任务

- [ ] 轮换 Node Secret
- [ ] 审查发布策略
- [ ] 更新话题池和模板

## 📞 支持

- **文档**: `/workspace/skills/evomap-fast-publisher/README.md`
- **相关资源**:
  - [EvoMap 知识图谱](../../evomap-knowledge-base.md)
  - [EvoMap 发布策略](../../evomap-publishing-strategy.md)
  - [EvoMap Chain 模式指南](../../evomap-chain-mode-guide.md)
