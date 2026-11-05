---
name: skill-guardian
description: OpenClaw 技能守护者。智能检测技能冲突、自动融合重复技能、升级技能、管理技能版本。当用户提到"检测技能冲突"、"检查技能重复"、"融合技能"、"合并技能"、"技能乱了"、"技能冲突"、"清理技能"、"整理技能"、"安装新技能"时使用。
---

# OpenClaw 技能守护者

## 触发条件

当用户提到以下关键词时自动触发：
- "检测技能冲突"、"检查技能重复"
- "融合技能"、"合并技能"
- "技能乱了"、"技能冲突"
- "清理技能"、"整理技能"
- "安装新技能"（自动触发预检）

## 技能冲突判断矩阵

| 条件 | 不融合 | 建议融合 | 必须融合 |
|------|--------|----------|----------|
| 名称 | 不同 | - | **同名** |
| 触发词重合度 | < 30% | 30%-60% | > 60% |
| 功能描述重合 | < 20% | 20%-50% | > 50% |
| 解决问题 | 不同 | 可能相同 | **相同** |

## 触发规则

```
必须融合（立即执行）
  - 同名技能（名称完全相同）
  - 触发词重合度 > 60%

建议融合（询问用户）
  - 触发词重合度 30%-60%
  - 功能描述重合度 > 50%

不融合（保持现状）
  - 触发词重合度 < 30%
  - 功能描述重合度 < 20%
```

## 核心功能

### 1. 技能冲突检测

扫描所有技能，检测以下问题：
- 同名技能
- 触发词高度相似
- 功能描述重叠
- 修复方案冲突

### 2. 智能融合

融合原则：
1. **触发词取并集**（union，去重）
2. **修复方案保留全部**
3. **保留环境特定配置**
4. **记录版本历史**

### 3. 版本管理

归档目录结构：
```
~/.openclaw/workspace/skills/
├── openclaw-doctor/          ← 当前主版本
│   └── SKILL.md
└── archive/                   ← 旧版本归档
    ├── openclaw-doctor.v1/
    └── openclaw-doctor.v2/
```

## Jaccard 相似度计算

```
相似度 = |A ∩ B| / |A ∪ B|

A = 技能A的触发词集合
B = 技能B的触发词集合
```

**执行脚本**：
```bash
python /workspace/temp-skills/skill-guardian/scripts/jaccard_validator.py \
  --skill-a "诊断,修复,问题" \
  --skill-b "诊断,修复,优化"
```

## 技能预检流程

```
安装新技能 X：
  ↓
1. 检测 workspace/skills/ 中是否有同名技能
  ↓ 存在同名
2. 计算触发词 Jaccard 相似度
  ↓
3. 相似度 > 60%?
     ↓ Yes
   立即触发融合
     ↓ No
4. 相似度 > 30%?
     ↓ Yes
   询问用户是否融合
     ↓ No
5. 无需融合，直接安装
```

## 版本历史格式

在 SKILL.md 顶部记录：

```yaml
---
name: skill-name
version-history:
  - v3 : 2026-04-06 - 融合 v1 + v2
  - v2 : 2026-04-05 - 新增功能X
  - v1 : 2026-04-01 - 初始版本
triggers:
  - 触发词A
  - 触发词B
---
```

## 执行命令

### 检测冲突
```bash
openclaw skills list
```

### 手动融合
```bash
python /workspace/temp-skills/skill-guardian/scripts/skill-guardian.py \
  --merge "技能A" "技能B"
```

### 验证相似度
```bash
python /workspace/temp-skills/skill-guardian/scripts/jaccard_validator.py \
  --skill-a-file "/path/to/skill-a/SKILL.md" \
  --skill-b-file "/path/to/skill-b/SKILL.md"
```

## 常见问题

### Q: 融合后会不会丢失功能？
A: 不会。融合采用 union 策略，保留所有触发词和修复方案。

### Q: 不想融合怎么办？
A: 使用 `--skip-merge` 参数直接覆盖旧版本。

### Q: 融合错了能恢复吗？
A: 可以。旧版本已归档在 `archive/` 目录中。

## 相关命令

```bash
openclaw skills list          # 列出所有技能
openclaw skills info <name>   # 查看技能详情
openclaw skills search <kw>   # 搜索技能
```

*此技能确保 OpenClaw 技能库整洁、高效*
