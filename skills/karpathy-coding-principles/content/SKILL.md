---
name: karpathy-coding-principles
description: 编码原则技能，融合 Andrej Karpathy 的 LLM 编码最佳实践。当用户要求遵循良好的编码规范、避免过度工程、实现简洁代码、进行最小化变更、目标驱动开发、或询问如何提高代码质量时使用此技能。
---

# Karpathy 编码原则

行为准则指南，用于减少常见的 LLM 编码错误。可根据项目需求与项目特定的指令合并使用。

**权衡：** 这些准则偏向于谨慎而非速度。对于简单任务，请自行判断。

## 1. 编码前先思考 (Think Before Coding)

**不要假设。不要隐藏困惑。要呈现权衡。**

实现前：
- 明确陈述你的假设。如果不确定，请提问。
- 如果存在多种解释，请呈现它们——不要静默选择。
- 如果存在更简单的方法，请说出来。在有正当理由时提出反对意见。
- 如果有不清楚的地方，停下来。说出是什么让你困惑。提问。

## 2. 简洁优先 (Simplicity First)

**最小化代码解决问题。不要投机。**

- 不添加超出要求的特性。
- 不要为单次使用的代码创建抽象。
- 不要添加未被请求的"灵活性"或"可配置性"。
- 不需要为不可能的场景添加错误处理。
- 如果你写了 200 行代码而它可以是 50 行，请重写。

问自己："资深工程师会说这过度复杂吗？"如果是，请简化。

## 3. 精准变更 (Surgical Changes)

**只触碰你必须触碰的。只清理你自己的烂摊子。**

编辑现有代码时：
- 不要"改进"相邻的代码、注释或格式。
- 不要重构没有损坏的东西。
- 匹配现有风格，即使你会用不同的方式编写。
- 如果你注意到无关的死代码，提出来——不要删除它。

当你的更改产生孤立代码时：
- 删除因你的更改而变得未使用的 imports/变量/函数。
- 除非被要求，否则不要删除预先存在的死代码。

测试：每行更改的代码都应该直接追溯到用户的请求。

## 4. 目标驱动执行 (Goal-Driven Execution)

**定义成功标准。循环直到验证通过。**

将任务转化为可验证的目标：
- "添加验证" → "为无效输入编写测试，然后让它们通过"
- "修复 bug" → "编写重现它的测试，然后让它通过"
- "重构 X" → "确保测试在重构前后都通过"

对于多步骤任务，陈述简要计划：
```
1. [步骤] → 验证：[检查项]
2. [步骤] → 验证：[检查项]
3. [步骤] → 验证：[检查项]
```

强有力的成功标准让你能够独立循环。弱标准（"让它工作"）需要不断澄清。

---

**这些准则正在起作用的表现：**
- diff 中不必要的更改减少
- 因过度复杂化而重写的情况减少
- 在实现之前提出澄清问题，而不是在犯错之后

## 反模式总结

| 原则 | 反模式 | 修复 |
|------|--------|------|
| 编码前先思考 | 静默假设文件格式、字段、范围 | 明确列出假设，提问以澄清 |
| 简洁优先 | 用策略模式处理单一折扣计算 | 一个函数，直到真正需要复杂性 |
| 精准变更 | 修复 bug 时重新格式化引号、添加类型提示 | 只更改修复报告问题的代码行 |
| 目标驱动 | "我会审查并改进代码" | "为 bug X 编写测试 → 让它通过 → 验证无回归" |

## 核心洞察

"过度复杂"的例子并非明显错误——它们遵循设计模式和最佳实践。问题在于**时机**：它们在需要之前添加复杂性，这会：
- 使代码更难理解
- 引入更多 bug
- 花费更长时间实现
- 更难测试

"简单"版本：
- 更容易理解
- 实现更快
- 更易于测试
- 以后可以在真正需要时重构

**好的代码是能够简单地解决今天问题的代码，而不是过早地解决明天的问题。**

---

## 实践示例

### 示例 1：隐藏假设

**用户请求：** "添加导出用户数据的功能"

**错误做法（假设错误）：**
```python
def export_users(format='json'):
    """导出所有用户到文件。"""
    users = User.query.all()
    if format == 'json':
        with open('users.json', 'w') as f:
            json.dump([u.to_dict() for u in users], f)
    elif format == 'csv':
        with open('users.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'name'])
            writer.writeheader()
            writer.writerows([u.to_dict() for u in users])
    return f"导出了 {len(users)} 个用户"
```

**问题：**
- 假设应该导出所有用户（分页？隐私？）
- 没有询问文件位置
- 假设包含哪些字段
- 没有检查实际数据结构就假设 CSV 字段名

**正确做法（呈现假设）：**

实现前，我需要澄清：
1. **范围**：导出所有用户还是过滤的子集？（隐私影响）
2. **格式**：你说"导出"——是指：
   - 浏览器中下载文件？
   - 带邮件通知的后台任务？
   - 返回数据的 API 端点？
3. **字段**：包含哪些用户字段？（某些可能敏感）
4. **数量**：通常有多少用户？（影响实现方式）

最简单的方法：添加返回分页 JSON 的 API 端点。
文件导出需要更多信息。您偏好哪种方式？

### 示例 2：过度抽象

**用户请求：** "添加计算折扣的函数"

**错误做法（过度工程）：**
```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Union
from dataclasses import dataclass

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage

    def calculate(self, amount: float) -> float:
        return amount * (self.percentage / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, fixed_amount: float):
        self.fixed_amount = fixed_amount

    def calculate(self, amount: float) -> float:
        return min(self.fixed_amount, amount)

@dataclass
class DiscountConfig:
    strategy: DiscountStrategy
    min_purchase: float = 0.0
    max_discount: float = float('inf')

class DiscountCalculator:
    def __init__(self, config: DiscountConfig):
        self.config = config

    def apply_discount(self, amount: float) -> float:
        if amount < self.config.min_purchase:
            return 0
        discount = self.config.strategy.calculate(amount)
        return min(discount, self.config.max_discount)
```

**正确做法（简单）：**
```python
def calculate_discount(amount: float, percent: float) -> float:
    """计算折扣金额。percent 应该是 0-100。"""
    return amount * (percent / 100)

# 使用
discount = calculate_discount(100.0, 10.0)  # 减 10 美元
```

**何时添加复杂性：** 只有在真正需要多种折扣类型时。如果后续需要，届时再重构。

### 示例 3：精准变更

**用户请求：** "修复空邮箱导致验证器崩溃的 bug"

**错误做法（变更过多）：**
```diff
def validate_user(user_data):
-    # 检查邮箱格式
-    if not user_data.get('email'):
+    """验证用户数据。"""
+    email = user_data.get('email', '').strip()
+
+    # 验证邮箱
+    if not email:
        raise ValueError("邮箱必填")
-
-    # 基本邮箱验证
-    if '@' not in user_data['email']:
+    if '@' not in email or '.' not in email.split('@')[1]:
        raise ValueError("无效的邮箱")

-    # 检查用户名
-    if not user_data.get('username'):
+    # 验证用户名
+    username = user_data.get('username', '').strip()
+    if not username:
        raise ValueError("用户名必填")
+    if len(username) < 3:
+        raise ValueError("用户名太短")
+    if not username.isalnum():
+        raise ValueError("用户名必须是字母数字")

return True
```

**问题：**
- "改进了"超出 bug 修复范围的邮箱验证
- 添加了没人要求的用户名验证
- 更改了注释
- 添加了文档字符串

**正确做法（精准）：**
```diff
def validate_user(user_data):
    # 检查邮箱格式
-    if not user_data.get('email'):
+    email = user_data.get('email', '')
+    if not email or not email.strip():
        raise ValueError("邮箱必填")

    # 基本邮箱验证
-    if '@' not in user_data['email']:
+    if '@' not in email:
        raise ValueError("无效的邮箱")

    # 检查用户名
    if not user_data.get('username'):
        raise ValueError("用户名必填")

return True
```

**只更改了：** 修复空邮箱处理的具体代码行。

### 示例 4：目标驱动执行

**用户请求：** "添加 API 限流"

**错误做法（一次性全部实现）：**
```python
# 用 Redis、多种策略、配置系统和监控实现完整限流
# 一次提交 300 行代码
# 没有明确的验证步骤
```

**正确做法（增量验证）：**

限流计划：

1. 添加基本的内存限流（单个端点）
   验证：
   - 测试：100 个请求 → 前 10 个成功，其余得到 429
   - 手动：curl 端点 11 次，看到限流错误

2. 提取为中间件（应用到所有端点）
   验证：
   - 测试：限流应用于 /users 和 /posts
   - 现有端点测试仍然通过

3. 添加 Redis 后端（用于多服务器）
   验证：
   - 测试：限流在应用重启后持续
   - 测试：两个应用实例共享限流计数器

4. 添加配置（每个端点的限流）
   验证：
   - 测试：/search 允许 10/分钟，/users 允许 100/分钟
   - 配置文件正确解析

每个步骤都可以独立验证和部署。
从步骤 1 开始？

---

## 何时偏离准则

对于以下情况，可以偏离这些准则：
- **明确的项目要求**：项目有既定的样式或架构要求
- **已存在的复杂代码库**：匹配周围代码的风格
- **时间敏感任务**：用户明确要求快速实现
- **学习/教程场景**：解释概念时需要演示模式

**判断标准**：用户的目标是什么？如果是快速原型，过度工程化可能没问题。如果是生产代码，优先考虑简洁。

---

*这些原则基于 Andrej Karpathy 关于 LLM 编码陷阱的观察，旨在帮助 AI 助手产生更高质量的代码输出。*
