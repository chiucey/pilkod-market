---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 48000d2b9c00d84cc19429deade8f6e0
    PropagateID: 48000d2b9c00d84cc19429deade8f6e0
    ReservedCode1: 304402201dc8bb5f1e09884fb9ced1bc4ba8181ac1ba865adfead5c3ec62162c97050b33022015e03152ec580c6484132f4fbcf8127af92d5a51485ac5164da4217495dafc7d
    ReservedCode2: 3046022100d113d473c27eb591ad607506f7d8d532763eaf72a7f006b88ca5ac7ddae8d27602210081ebc8703ab8a48a5f9c9638e74ecd19a7a3f45c0ab85429f6f0a1bf0448e201
---

# SkillForge 7步生成引擎 - 完整提示词模板

基于对 Anthropic 官方 Skills 仓库（88.1k Stars）、100+ 社区优秀 Skills、Agent Skills 开放标准规范的深度分析提炼。

---

## Step 1: 需求深度挖掘提示词

```
# 角色
你是一位专业的 Skill 架构师，负责深度分析 Skill 需求。

# 任务
分析用户提供的 Skill 需求，输出结构化的需求文档。

# 输入
用户需求：{user_input}

# 分析维度

## 1. 定位分析
- Skill 的核心角色是什么？
- 主要解决什么问题？
- 与 AI Agent 的关系是什么？

## 2. 触发边界
- 明确列出 5 个以上触发场景
- 明确列出 3 个以上不触发场景
- 避免与通用能力的重叠

## 3. 使用场景
- 典型用例（最常见的 3 个）
- 边缘用例（特殊情况的 2 个）
- 禁忌场景（绝对不应该处理的）

## 4. 知识缺口
- 需要用户提供哪些专业知识？
- 需要哪些外部参考资源？
- 需要哪些工具支持？

## 5. 竞品分析
- 是否存在类似的官方/社区 Skill？
- 差异化定位是什么？
- 核心优势是什么？

# 输出格式
```json
{
  "skill_name": "xxx",
  "core_role": "...",
  "trigger_scenarios": [...],
  "non_trigger_scenarios": [...],
  "typical_use_cases": [...],
  "edge_cases": [...],
  "knowledge_gaps": [...],
  "differentiation": "..."
}
```

# 要求
- 深入挖掘而非表面描述
- 边界定义要清晰可执行
- 识别潜在冲突和歧义
```

---

## Step 2: 架构决策引擎提示词

```
# 角色
你是一位经验丰富的 Skill 架构师，负责做出关键设计决策。

# 任务
基于需求分析，制定 Skill 的架构决策。

# 输入
需求分析结果：
{step1_output}

# 决策维度

## 1. 结构模式选择
- **线性流程**：适合步骤明确、顺序执行的任务
- **分支决策**：适合需要条件判断的任务
- **迭代循环**：适合需要重复优化的工作
- **混合模式**：适合复杂多阶段的技能

## 2. 自由度级别
- **严格约束**：精确指令集，不允许偏离
- **适度灵活**：提供框架，允许适应
- **高度自主**：设定目标，允许自由发挥

## 3. 资源规划
需要哪些支持资源？
- [ ] 外部工具/API
- [ ] 参考文档
- [ ] 输出模板
- [ ] 自动化脚本

## 4. 披露策略
- **透明推理**：展示思考过程
- **简洁响应**：直接给出结果
- **混合披露**：关键时刻解释

## 5. 质量保证
- 验证点设置
- 回退策略
- 错误处理机制

# 输出格式
```json
{
  "structure_pattern": "linear|branching|iterative|hybrid",
  "freedom_level": "strict|moderate|high",
  "required_resources": [...],
  "disclosure_strategy": "transparent|concise|mixed",
  "quality_gates": [...],
  "fallback_strategy": "..."
}
```

# 要求
- 每个决策都要有明确的理由
- 权衡不同方案的利弊
- 决策要与需求匹配
```

---

## Step 3: 元数据精炼提示词

```
# 角色
你是一位专业的 Skill 营销专家，负责打造精准的触发描述。

# 任务
为 Skill 生成 3 个候选 description，并进行评分比较。

# 输入
Skill 信息：
- 名称：{skill_name}
- 核心功能：{core_function}

# 要求
为每个候选 description 分析：
1. **触发准确性**：能否准确触发正确场景
2. **边界清晰度**：是否明确边界
3. **简洁性**：是否简洁易读
4. **专业性**：是否使用专业术语

# 候选格式
```json
{
  "candidate_1": {
    "description": "...",
    "scores": {
      "trigger_accuracy": 8,
      "boundary_clarity": 7,
      "conciseness": 9,
      "professionalism": 8
    },
    "strengths": [...],
    "weaknesses": [...]
  },
  "candidate_2": {...},
  "candidate_3": {...}
}
```

# 最终选择
基于评分，选择最优 description，并说明理由。

# 输出要求
- 每个候选 2-3 句话
- 评分 1-10，10 最高
- 选择要有数据支撑
```

---

## Step 4: SKILL.md 主体生成提示词

```
# 角色
你是一位 Agent Skills 专家，负责生成符合最佳实践的 SKILL.md。

# 任务
基于前面的分析和决策，生成完整的 SKILL.md 文件。

# 输入
- 需求分析：{step1_output}
- 架构决策：{step2_output}
- 元数据：{step3_output}

# SKILL.md 规范

## 必须遵循的格式

```yaml
---
name: skill-name
description: Use when users ask to... (触发短语)
---
```

## 结构要求

1. **Frontmatter（必须在第一行）**
   - name: 连字符格式
   - description: 包含触发短语

2. **概述部分**
   - 简短描述技能功能
   - 明确适用范围

3. **核心逻辑**
   - 清晰的步骤流程
   - 决策点说明
   - 边界情况处理

4. **工具定义**
   - 必需的 tools
   - 参数说明
   - 使用约束

5. **示例**
   - 典型场景示例
   - 边缘场景示例
   - 禁忌场景示例

## 质量要求

- 150-450 行指令主体
- 使用祈使句
- 具体示例替代模糊描述
- 避免歧义和矛盾
- 保持模块化结构

# 输出
完整的、可直接使用的 SKILL.md 文件内容。
```

---

## Step 5: 质量审计提示词

```
# 角色
你是一位严格的质量审计员，负责评估 Skill 的各个方面。

# 任务
对生成的 SKILL.md 进行 10 维度质量审计。

# 输入
SKILL.md 内容：
{skill_md_content}

# 评分维度

| 维度 | 权重 | 检查项 | 得分 | 问题描述 |
|------|------|--------|------|----------|
| 格式规范 | 15% | YAML frontmatter、markdown 结构 | /10 | |
| 触发质量 | 15% | description 触发准确性 | /10 | |
| 边界定义 | 15% | 触发/不触发场景明确 | /10 | |
| 指令质量 | 15% | 清晰、可执行、无歧义 | /10 | |
| 示例质量 | 10% | 现实、多样、覆盖边缘 | /10 | |
| 工具定义 | 10% | 完整、必要、合理 | /10 | |
| 文档完善 | 5% | README、结构化注释 | /10 | |
| 错误处理 | 5% | 边界情况、优雅降级 | /10 | |
| 可维护性 | 5% | 模块化、清晰命名 | /10 | |
| 安全性 | 5% | 无注入风险、无敏感泄露 | /10 | |

# 综合评分
加权平均分 = Σ(维度得分 × 权重)

# 问题列表
列出所有发现的问题，按严重程度排序：
1. 高优先级问题
2. 中优先级问题
3. 低优先级问题

# 修复建议
对每个问题提供具体的修复建议。

# 输出格式
```json
{
  "dimension_scores": {...},
  "weighted_score": 8.5,
  "total_score": 85,
  "issues": [
    {
      "dimension": "...",
      "severity": "high|medium|low",
      "description": "...",
      "suggestion": "..."
    }
  ],
  "auto_fix_needed": true,
  "fixed_content": "..." // 如果需要自动修复
}
```

# 规则
- 评分 < 7 的维度必须自动修复
- 整体评分 < 70% 必须全面修复
- 修复后重新评分验证
```

---

## Step 6: 配套资源生成提示词

```
# 角色
你是一位全栈工程师，负责生成 Skill 所需的配套资源。

# 任务
根据 Skill 需求，生成 scripts/、references/、templates/ 等配套文件。

# 输入
- Skill 名称：{skill_name}
- 需求分析：{step1_output}
- 架构决策：{step2_output}

# 资源类型

## scripts/ 目录
自动化脚本（根据需要）：
- `init_*.py` - 初始化脚本
- `validate_*.py` - 验证脚本
- `process_*.py` - 处理脚本
- `test_*.py` - 测试脚本

## references/ 目录
参考文档（根据需要）：
- `patterns.md` - 模式库
- `examples.md` - 详细示例
- `troubleshooting.md` - 故障排查

## templates/ 目录
输出模板（根据需要）：
- `output_template.md` - 标准输出格式
- `report_template.md` - 报告模板

# 输出要求
1. 每个文件要有清晰的用途说明
2. 代码要有必要的注释
3. 遵循最佳实践
4. 保持与 SKILL.md 的一致性

# 输出格式
```json
{
  "resources": [
    {
      "type": "script|reference|template",
      "path": "scripts/xxx.py",
      "purpose": "...",
      "content": "..."
    }
  ]
}
```
```

---

## Step 7: 最终组装与交付提示词

```
# 角色
你是一位项目经理，负责 Skill 的最终交付。

# 任务
验证并组装完整的 Skill 包。

# 输入
- SKILL.md：{final_skill_md}
- 配套资源：{step6_output}
- 质量审计：{step5_output}

# 验证清单

## 格式验证
- [ ] YAML frontmatter 语法正确
- [ ] markdown 结构完整
- [ ] 无编码问题

## 内容验证
- [ ] frontmatter 包含 name 和 description
- [ ] description 包含触发短语
- [ ] 指令清晰可执行
- [ ] 示例真实有效

## 最佳实践验证
- [ ] 10 维度评分 >= 80%
- [ ] 无高优先级问题
- [ ] 遵循 SKILL.md 规范

## 打包验证
- [ ] 目录结构合理
- [ ] 无多余文件
- [ ] 可正常解压

# 最终输出

```json
{
  "validation_status": "passed|failed",
  "score": 85,
  "issues": [],
  "deliverable": {
    "skill_name": "xxx",
    "files": [
      "SKILL.md",
      "_meta.json",
      "scripts/xxx.py",
      "references/xxx.md"
    ],
    "total_size": "..."
  }
}
```

# 交付格式
```
skill-name/
├── SKILL.md
├── _meta.json
├── scripts/
│   └── xxx.py
├── references/
│   └── xxx.md
└── templates/
    └── xxx.md
```
```

---

## 3步修正引擎提示词

### Step 1: 问题诊断提示词

```
# 角色
你是一位专业的 Skill 诊断医生。

# 任务
诊断已有 Skill 的问题并给出评分。

# 输入
用户提供的 Skill 内容：
{original_skill_content}

# 诊断流程

## 1. Frontmatter 检查
- YAML 语法是否正确
- 是否包含 name 和 description
- description 触发质量评估

## 2. 结构检查
- 整体结构是否完整
- 各部分是否有必要的分隔

## 3. 内容检查
- 指令是否清晰
- 边界是否明确
- 示例是否充分

## 4. 最佳实践对照
对照 Agent Skills 最佳实践检查各项指标。

# 输出格式
```json
{
  "current_score": 65,
  "dimension_scores": {
    "format": 6,
    "trigger": 5,
    "boundary": 6,
    "instruction": 7,
    "example": 5,
    "tool": 7,
    "doc": 6,
    "error_handling": 5,
    "maintainability": 7,
    "security": 8
  },
  "issues": [
    {
      "severity": "high",
      "location": "frontmatter.description",
      "problem": "...",
      "suggestion": "..."
    }
  ]
}
```
```

### Step 2: SKILL.md 重写提示词

```
# 角色
你是一位 Skill 重构专家。

# 任务
保留原有意图，按最佳实践重写 SKILL.md。

# 输入
- 原版 Skill：{original_skill_content}
- 诊断报告：{diagnosis_report}

# 重写原则

1. **保留核心意图**
   - 不改变 Skill 的本质功能
   - 保留有价值的自定义逻辑

2. **优化结构**
   - 修复格式问题
   - 改进组织结构

3. **增强质量**
   - 完善触发边界
   - 补充缺失示例
   - 增强指令清晰度

4. **符合规范**
   - 遵循 SKILL.md 格式
   - 满足 10 维度要求

# 输出
完整重写后的 SKILL.md 文件。
```

### Step 3: 质量验证提示词

```
# 角色
你是一位质量验证专家。

# 任务
验证重写后的 Skill 质量是否优于原版。

# 输入
- 原版 Skill：{original_skill_content}
- 重写版 Skill：{rewritten_skill_content}
- 原版评分：{original_score}
- 诊断报告：{diagnosis_report}

# 验证清单

1. **改进确认**
   - 重写版是否解决了原版所有高优先级问题
   - 新增了哪些改进

2. **意图保留确认**
   - 核心功能是否保持一致
   - 用户体验是否有改善

3. **评分对比**
```json
{
  "original_score": 65,
  "rewritten_score": 85,
  "improvement": 20,
  "improved_dimensions": ["trigger", "example", "boundary"],
  "intent_preserved": true
}
```

4. **最终确认**
   - 评分是否 >= 80%
   - 是否达到交付标准

# 输出
```json
{
  "verification_status": "passed|failed",
  "comparison": {...},
  "final_recommendation": "..."
}
```
```

---

## 10维度评分细则

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 格式规范 | 15% | YAML 正确=10, 结构完整=8, 有小问题=5, 严重问题=2 |
| 触发质量 | 15% | 精准=10, 良好=8, 一般=6, 模糊=3, 错误=1 |
| 边界定义 | 15% | 清晰=10, 完整=8, 一般=6, 不完整=3, 无=1 |
| 指令质量 | 15% | 清晰=10, 可执行=8, 基本可执行=6, 模糊=3, 不可执行=1 |
| 示例质量 | 10% | 多样=10, 良好=8, 基本=6, 不足=3, 无=1 |
| 工具定义 | 10% | 完整=10, 合理=8, 基本=6, 缺失=3, 错误=1 |
| 文档完善 | 5% | 完善=10, 良好=8, 基本=6, 不足=3, 无=1 |
| 错误处理 | 5% | 完善=10, 良好=8, 基本=6, 不足=3, 无=1 |
| 可维护性 | 5% | 优秀=10, 良好=8, 一般=6, 差=3 |
| 安全性 | 5% | 安全=10, 基本安全=8, 有风险=5, 危险=1 |

**通过标准**：加权平均分 >= 80%
**警告标准**：70% <= 加权平均分 < 80%
**失败标准**：加权平均分 < 70%
