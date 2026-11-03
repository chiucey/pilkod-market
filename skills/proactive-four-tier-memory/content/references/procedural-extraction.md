# Procedural Memory Extraction（程序性记忆提取）

## 核心定位

程序性记忆是"会做什么"的知识，与语义记忆的"知道什么"互补。

**为什么重要**：
- 人类通过练习学会技能，而非记住所有步骤
- AI需要沉淀"会做"的能力，而非每次重新组合
- 重复≥3次的操作值得模板化

## 提取触发条件

| 触发信号 | 阈值 | 说明 |
|---------|------|------|
| 相同操作重复 | ≥3次 | 高度相似的操作序列 |
| 相同错误重复 | ≥2次 | 同一个错误需要记住修复 |
| 成功模式 | ≥3次 | 方法连续成功 |
| 用户显式要求 | 1次 | "记住这个流程" |

## 提取流程

```
1. 模式识别
   输入：Episodic Memory（最近30天）
   处理：LLM分析事件序列
   输出：候选程序性记忆列表

2. 模板生成
   输入：候选模式
   处理：生成标准化模板
   输出：写入程序性记忆存储

3. 验证
   输入：新生成的模板
   处理：验证完整性
   输出：通过→写入；失败→待审核
```

## 程序性记忆格式

```yaml
procedural_memories:
  - id: "proc_001"
    type: "workflow|error_fix|shortcut|code_pattern"
    name: "名称"
    triggers: ["触发词1", "触发词2"]
    steps: ["步骤1", "步骤2"]
    success_rate: 0.0-1.0
    usage_count: 5
    last_used: "2026-03-25"
    derived_from: ["ep_001", "ep_002"]
```

## 有效性检查

```python
def check_freshness(proc):
    """检查程序性记忆是否仍然有效"""

    # 超过90天未使用
    if days_since(proc.last_used) > 90:
        return "stale"

    # 成功率持续下降
    if proc.recent_success_rate < 0.5 and proc.usage_count > 5:
        return "deprecated"

    # 依赖已变更
    if has_broken_dependencies(proc):
        return "broken"

    return "valid"
```

## 使用示例

**场景**：用户多次初始化React项目

```
Episodic记录：
- ep_20260320: 用户用Vite初始化React项目
- ep_20260322: 用户再次用Vite初始化React项目
- ep_20260325: 用户第三次初始化React项目

检测结果：相同操作≥3次 → 提取为程序性记忆

程序性记忆：
- name: "React+Vite项目初始化"
- triggers: ["新项目", "初始化", "React"]
- steps: ["npm create vite@latest", "npm install", "配置ESLint"]
- success_rate: 1.0

下次用户说"新项目" → 主动提示使用此流程
```
