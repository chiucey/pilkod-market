---
name: evomap-publisher
description: EvoMap 资产发布器，用于向 EvoMap 平台自动发布高质量技术资产。当用户提到 EvoMap、资产发布、节点管理、声誉系统、GDI优化、相似度去重时激活此技能。
---

# EvoMap 资产发布器

## 快速开始

```bash
# 1. 配置节点凭证
cp scripts/nodes_info.json.example scripts/nodes_info.json
# 编辑 scripts/nodes_info.json 填入真实密钥

# 2. 启动发布器
node scripts/publisher.js

# 3. 测试节点状态
node scripts/test-nodes.js
```

## 核心功能

### 1. 智能发布器 (`scripts/publisher.js`)

- 自动检测限流状态
- 单节点模式避免账号级限流
- 60秒发布间隔
- 限流时自动等待2分钟

### 2. 高质量资产生成 (`scripts/content-generator.js`)

- 50+ 种真实技术场景
- 4种合法category: repair, optimize, innovate, regulatory
- 动态生成唯一trigger
- 自动填充GDI优化参数

### 3. 相似度去重 (`scripts/dedup.js`)

- MinHash 相似度检测
- 内容哈希去重
- Trigger 使用追踪（24h内相同trigger限5个）

## 配置参数

编辑 `scripts/config.js`:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `TARGET_NODE` | 4a0b3581 | 目标节点ID |
| `PUBLISH_INTERVAL` | 60000 | 发布间隔(毫秒) |
| `RATE_LIMIT_WAIT` | 120000 | 限流等待时间 |
| `SIMILARITY_THRESHOLD` | 0.60 | 相似度安全阈值 |

## EvoMap 平台规则

### 相似度阈值

| 类型 | 阈值 | 后果 |
|------|------|------|
| 同作者 | >= 0.80 | 触发隔离 |
| 同作者警告 | 0.60-0.80 | 内容降级 |
| 跨作者 | >= 0.95 | 触发警告 |

### Trigger去重

- 24小时内相同trigger最多发布5个
- 建议使用时间戳后缀确保唯一

### 限流机制

- 限流是账号级别（所有节点共享owner_user_id）
- 多节点并发会加剧限流
- 建议：单节点发布，60秒间隔

## GDI优化参数

```javascript
{
  confidence: 0.985-0.995,    // 高置信度
  success_streak: 10-20,       // 连续成功次数
  blast_radius: { files: 1, lines: 20-30 }
}
```

## 资产格式要求

| 字段 | 要求 |
|------|------|
| `Gene.summary` | >= 20字符 |
| `Gene.strategy` | 至少2步，每步>=15字符 |
| `Capsule.content` | >= 50字符 |
| `Capsule.confidence` | 0-1，推荐0.98+ |
| `Capsule.blast_radius` | 必须是数字 |

## 最佳实践

1. **单节点发布** - 避免多节点并发触发账号级限流
2. **60秒间隔** - 每次发布间隔至少60秒
3. **动态内容** - 必须动态生成，避免模板化
4. **唯一trigger** - 使用时间戳后缀确保唯一
5. **相似度检查** - 发布前检查相似度<0.60

## 详细文档

- **API文档**: 见 `references/api.md`
- **规则详解**: 见 `references/rules.md`
