# Harness 工程文档风格指南

## 概述

本文档定义了 Harness 工程文档的写作标准，所有工程文档必须遵循此标准。

**核心原则**：
- 以用户为中心，而非以系统为中心
- 思考"用户旅程"而非"教科书"
- 渐进式披露，避免信息过载

## 语言风格

### 对话式语调

使用随意、对话式的语调。保持句子简短，使用现在时。

**正确**：
```markdown
You can run Docker-in-Docker in a Background step.
```

**错误**：
```markdown
The user can run Docker-in-Docker in a Background step.
```

### 不使用 "Please"

作为权威，可以友好/非正式，但不需要过度礼貌。

**正确**：
```markdown
Run the pipeline again.
```

**错误**：
```markdown
Please try running the pipeline again.
```

### 现在时、主动语态

**指令示例**：

**正确**：
```markdown
Install a delegate in your Kubernetes cluster.
```

**错误**：
```markdown
You will need to install a delegate in your Kubernetes cluster.
```

**结果示例**：

**更好**：
```markdown
You can find the delegate on the Delegates list.
```

**错误**：
```markdown
The delegate will be added to the Delegates list.
```

### 文化敏感性

避免：
- 能力歧视语言（如 "cripple"）
- 性别化语言（如 "every man"）
- 暴力语言（如 "kill"）

## 格式规范

### 标题

- 使用 ATX 风格（# 符号）
- 每个文档只有一个 H1
- 标题层级不跳级
- 不在标题中使用代码格式

### UI 元素

使用粗体标记 UI 元素：

```markdown
Select **Save**.
Navigate to **Project Settings**.
```

### 代码

- 行内代码使用反引号
- 代码块必须指定语言
- 不在标题中使用代码格式

### 链接

使用描述性链接文本：

**正确**：
```markdown
For more information, see [Create a CI pipeline](./create-pipeline.md).
```

**错误**：
```markdown
For more information, click [here](./create-pipeline.md).
```

## 信息架构

### 核心问题

每个功能必须回答：
- **What** - 这个功能能做什么？
- **Why** - 为什么用户需要使用它？
- **How** - 如何使用它？

### 用户旅程思维

不要逐屏描述功能，而是思考：
- 作为用户使用这个功能的体验是什么？
- 用户想要达成什么目标？

### 渐进式披露

- 使用文件夹创建层次结构
- 使用标签页、详情块组织内容
- 关键信息不要隐藏在折叠块中

## 追溯性要求

### ID 格式

| 文档类型 | ID 格式 | 示例 |
|:---------|:--------|:-----|
| 场景 | SC-NNN | SC-001 |
| 用例 | UC-NNN | UC-001 |
| 需求 | REQ-NNN | REQ-001 |
| 测试用例 | TC-NNN | TC-001 |
| 验收标准 | AC-NNN-M | AC-001-1 |
| 观测指标 | OBS-NNN | OBS-001 |

### 追溯关系

- 每个用例必须追溯到场景
- 每个需求必须追溯到用例
- 每个测试用例必须追溯到需求
- 每个验收标准必须追溯到需求

## 校验检查清单

### 语言风格

- [ ] 使用现在时
- [ ] 使用主动语态
- [ ] 不使用 "please"
- [ ] 直接对用户说话（"You"）

### 格式规范

- [ ] 只有一个 H1 标题
- [ ] UI 元素使用粗体
- [ ] 代码块指定语言
- [ ] 链接文本描述性强

### 追溯性

- [ ] 所有 ID 格式正确
- [ ] 追溯关系完整
- [ ] 引用的 ID 存在
