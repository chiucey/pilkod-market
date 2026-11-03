---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1a3ea9c56a4b5c97b357e854464b2773
    PropagateID: 1a3ea9c56a4b5c97b357e854464b2773
    ReservedCode1: 304602210081ca85418229fa95c8a41620954adea9d5c80d828a6600ca733d0ce8b919e04f022100906e57721bb5a8712671f46944dc57cd7fbffce553dfbc9597c207a0793e079a
    ReservedCode2: 304402206947c4c24cfabeed8238807d84ce2ebee44f03af55445ea4c33c6efff914e55d022011fa81dd2b38cfde4ca1de36258d9949deb98976f95e70f453a37f9242b1114d
description: 自我迭代升级技能。当用户要求"升级技能"、"改进自己"、"迭代优化"、"自我进化"、"分析并改进你的表现"时使用。此技能能够分析自身执行历史，识别改进机会，并自动应用升级。
name: self-iterating-skill
---

# 自我迭代升级技能

## 核心能力

本技能具备自我观察、自我分析、自我规划和自我执行四层能力，实现持续的自我优化。

## 工作流程

### 阶段 1：自我观察 - 记录执行历史

1. 检查 `/workspace/temp-skills/self-iterating-skill/data/execution_log.json`
2. 记录当前执行：
   - 时间戳
   - 任务类型
   - 执行结果（成功/失败/部分成功）
   - 用户反馈（如果有）
   - 资源消耗
   - 识别的模式

### 阶段 2：自我分析 - 模式识别

调用 `scripts/analyze_performance.py` 执行分析：

```python
# 分析维度
success_rate = 成功次数 / 总执行次数
improvement_areas = 识别低效/错误的模式
strength_patterns = 表现出色的模式
resource_efficiency = 资源使用优化空间
```

识别的问题类型：
- **准确性**：判断错误、遗漏关键信息
- **效率**：执行步骤冗余、响应延迟
- **鲁棒性**：边界情况处理不当、异常处理缺失
- **可维护性**：代码重复、缺乏模块化

### 阶段 3：自我规划 - 生成改进方案

调用 `scripts/generate_improvements.py`：

1. **优先级排序**：按影响程度和实现难度排序
2. **具体建议**：
   - SKILL.md 内容优化
   - 新增脚本自动化
   - references 补充
   - 工作流程调整
3. **风险评估**：每个改进的潜在风险和回滚方案

### 阶段 4：自我执行 - 应用升级

调用 `scripts/apply_upgrades.py`：

1. 备份当前状态到 `data/backups/`
2. 应用通过验证的改进
3. 更新 `_meta.json` version
4. 验证升级后功能完整性

## 触发条件

当检测到以下意图时自动启动：
- "升级" / "改进" / "迭代" / "优化"
- "分析你的表现"
- "自我进化"
- "变得更好"

## 输出格式

执行完成后输出：

```
## 自我迭代报告

### 执行历史摘要
- 总执行次数：X
- 成功率：X%
- 平均响应时间：Xms

### 改进分析
#### 优势模式（保持）
- ...

#### 改进机会（优先级排序）
1. [高] ...
2. [中] ...
3. [低] ...

### 已应用的升级
- v1.0.0 → v1.1.0
- 具体改进项：...

### 下一步建议
- 监控改进效果
- 收集更多执行数据
- 规划下一轮迭代
```

## 质量门槛

- 执行日志必须完整记录
- 每个改进必须经过验证
- 版本号遵循语义化规范
- 备份必须可回滚

## 资源

- 脚本目录：`scripts/`
- 参考文档：`references/`
- 数据存储：`data/`
