---
name: agent-brain
description: 智能体质量保障与需求追踪专家。当用户要求代码审查、bug检测、逻辑校验、需求确认、效率优化、执行质量把控，或智能体反复修改仍无法达到预期时使用。触发场景包括：代码质量检查、bug修复验证、需求一致性追踪、代码重构建议、性能优化、输出质量评估。
---

# 智能体大脑 (Agent Brain)

## 核心能力

智能体大脑是一个全方位质量保障系统，帮助智能体在迭代开发过程中保持代码质量、逻辑正确性和需求一致性。

## 执行工作流

### 1. 需求追踪模块 (Requirement Tracker)

**功能**：自动记录和追踪用户需求，避免需求漂移。

**执行步骤**：
1. 当用户提出新需求时，调用 `check_requirement_consistency` 检查与历史需求的一致性
2. 如果发现冲突，生成冲突报告并请求用户确认
3. 每次需求变更后更新需求追踪记录
4. 维护需求变更历史，便于回溯

**输出格式**：
```json
{
  "requirement_id": "REQ-001",
  "original_requirement": "用户原始需求描述",
  "current_requirement": "当前需求描述",
  "consistency_status": "consistent|conflict|ambiguous",
  "conflict_details": [],
  "change_history": []
}
```

### 2. 代码审查模块 (Code Reviewer)

**功能**：自动化代码质量检查和bug检测。

**执行步骤**：
1. 扫描目标代码文件
2. 执行多维度检查：
   - 语法错误检测
   - 潜在bug识别（空指针、内存泄漏、资源未关闭等）
   - 代码风格一致性
   - 安全漏洞扫描
   - 依赖完整性检查
3. 生成审查报告
4. 提供修复建议

**检查清单**：
- [ ] 语法正确性
- [ ] 边界条件处理
- [ ] 异常处理完整性
- [ ] 资源管理（文件、连接、内存）
- [ ] 安全敏感操作
- [ ] 代码重复度
- [ ] 命名规范性
- [ ] 注释完整性

### 3. 逻辑验证模块 (Logic Validator)

**功能**：验证代码逻辑与用户需求的匹配度。

**执行步骤**：
1. 解析用户需求的预期行为
2. 追踪代码执行路径
3. 验证输出与预期的一致性
4. 检测逻辑缺陷和边缘情况

**验证方法**：
- 状态机验证
- 业务流程图对比
- 输入输出边界测试
- 条件分支覆盖检查

### 4. 效率审查模块 (Efficiency Auditor)

**功能**：评估代码执行效率和资源使用。

**执行步骤**：
1. 分析算法复杂度（时间/空间）
2. 检查性能瓶颈点
3. 评估资源使用合理性
4. 提供优化建议

**评估维度**：
- 时间复杂度（O(n)、O(log n)等）
- 空间复杂度
- 数据库查询效率
- API调用次数
- 缓存策略合理性

### 5. 质量把控模块 (Quality Guardian)

**功能**：确保最终输出符合质量标准。

**执行步骤**：
1. 验证输出格式是否符合预期
2. 检查数据完整性
3. 评估用户体验
4. 生成质量报告

## 决策矩阵

| 场景 | 检测动作 | 用户交互 |
|------|----------|----------|
| 新需求 | 需求一致性检查 | 冲突时弹窗确认 |
| 代码修改 | 自动触发代码审查 | 严重问题暂停执行 |
| 逻辑变更 | 执行逻辑验证 | 逻辑错误时提示 |
| 性能问题 | 效率审查 | 瓶颈严重时警告 |
| 输出异常 | 质量把控检查 | 质量问题重试 |

## 输出报告格式

```json
{
  "task_id": "任务ID",
  "review_timestamp": "审查时间戳",
  "modules_executed": ["模块列表"],
  "findings": {
    "critical": [],
    "warnings": [],
    "suggestions": []
  },
  "requirement_alignment": {
    "status": "aligned|misaligned|partial",
    "details": "对齐情况说明"
  },
  "quality_score": 85,
  "next_actions": ["建议的修复动作"]
}
```

## 使用场景

**触发条件**：
1. 智能体完成代码修改后
2. 用户提出新的需求变更
3. 智能体遇到难以解决的问题
4. 代码迭代超过3次仍有问题
5. 用户要求进行代码审查

**调用方式**：
当需要执行质量保障时，直接调用此技能的各个模块。

## 核心原则

1. **以终为始**：始终站在用户原始需求角度评估
2. **增量审查**：每次变更后立即审查，避免累积问题
3. **可追溯**：维护完整的需求和修改历史
4. **主动预警**：在问题扩大前主动发现并提示
5. **用户确认**：重大变更必须获得用户确认

## 集成接口

```python
# 伪代码示例
class AgentBrain:
    def __init__(self):
        self.requirement_tracker = RequirementTracker()
        self.code_reviewer = CodeReviewer()
        self.logic_validator = LogicValidator()
        self.efficiency_auditor = EfficiencyAuditor()
        self.quality_guardian = QualityGuardian()

    def full_review(self, code, requirements):
        """执行完整审查"""
        # 1. 需求一致性检查
        req_status = self.requirement_tracker.check(requirements)
        # 2. 代码审查
        code_issues = self.code_reviewer.analyze(code)
        # 3. 逻辑验证
        logic_checks = self.logic_validator.validate(code, requirements)
        # 4. 效率审查
        efficiency_report = self.efficiency_auditor.audit(code)
        # 5. 质量把控
        quality_report = self.quality_guardian.check(code, requirements)

        return self.generate_report(...)

    def requirement_check(self, new_requirement):
        """检查需求一致性"""
        return self.requirement_tracker.check_consistency(new_requirement)
```

## 参考资源

详细的设计模式和集成指南请参考 `references/` 目录。
