---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4b2cd18c707196ecabbedc11ebb87c4c
    PropagateID: 4b2cd18c707196ecabbedc11ebb87c4c
    ReservedCode1: 304402200a13909b3e689e15e714983a92f114cd255ad123d330a6f1aa19b8227e4e0dff02202be5ccc6bd58ff8e0f61588399677f6e64312cf23b9a124c758c939383bb344b
    ReservedCode2: 30450220247c707923bdc77d35f3c5aed997d0a74c5f5b7ac97ac6c6d1d3cda06ac46915022100f723fbe9703e5422c6f44ae2bcfb22fa26fd4705df8f26b0dfd0d84e113f0de4
description: 将代码项目翻译为自然语言逻辑框架。当用户要求"分析项目结构"、"解释代码"、"把代码翻译成人话"、"生成项目文档"、"看不懂代码帮我看看"时触发。此 skill 读取项目文件结构，分析各模块功能，用自然语言输出整个项目的组织框架和每个区域的作用，让非技术人员也能看懂一个代码项目在做什么。
name: code-to-narrative
---

# code-to-narrative

将代码项目翻译为自然语言逻辑框架。

## 工作流程

### 第一步：确认项目路径

- 如果用户在当前 workspace 内：项目路径为 `/workspace`
- 如果用户指定了路径：用指定路径
- 如果项目不在 workspace 内，先问清楚路径

### 第二步：运行分析脚本

```bash
python3 /workspace/skills/code-to-narrative/scripts/analyze_project.py <项目路径>
```

输出为 JSON，包含：
- `tree`：项目目录树
- `language`：主语言
- `entry_points`：入口文件和配置文件
- `modules`：各目录下的关键文件和功能摘要

### 第三步：生成自然语言框架文档

根据 JSON 结果，用中文生成如下结构的文档：

```
# 📦 项目名称 — 自然语言框架说明

## 一、项目是什么（整体概述）

用 2-3 句话说明这个项目是做什么的，基于入口文件（main.py / index.js 等）和项目结构推断。

技术栈：[主语言] + [识别到的框架/工具]

---

## 二、项目整体结构（目录树）

用目录树展示，要求：
- 📁 代表文件夹
- 🐍 Python / 📄 JS+TS / ⚙️ 配置 / 📃 其他
- 省略不重要的文件（.gitignore, __pycache__ 等）

---

## 三、各模块功能说明

按目录树顺序，逐个模块用自然语言说明：

### 3.1 [模块名称/目录名]

**位置**：`src/`（相对路径）
**做什么**：用一段简洁的话说明这个模块的核心职责（1-2 句）
**包含哪些文件**：
- `main.py`：主逻辑，负责 [...]
- `utils.py`：工具函数集合，提供 [...]
- `config.py`：配置文件，管理 [...]

**供其他模块调用方式**：
- import from `utils` → `get_config()`
- 被 `main` 调用

---

## 四、模块之间的关系

用箭头 + 文字说明：

```
main.py（入口）
  ↓ 调用
config.py（读取配置）
  ↓ 提供数据
utils.py（处理数据）
  ↓ 返回结果
main.py
```

---

## 五、入口文件和启动方式

说明如何运行这个项目，格式：
- 开发环境：`npm run dev` / `python3 main.py`
- 生产环境：`npm start`
- 需要的环境变量：`.env.example` 中定义了哪些

---

## 六、一句话总结

用一句话概括整个项目在做什么。
```

## 撰写原则

- **语言**：全中文，非技术人员也能看懂
- **语气**：专业但通俗，禁止直接照搬代码注释
- **结构**：先整体后局部，先框架后细节
- **深度**：只解释"做什么"和"怎么组织"，不解释具体实现逻辑
- **模块关系**：必须画出模块之间的调用/依赖关系，这是核心价值
- **避免**：不要写代码、不要贴大段源码、不要出现技术术语（除非有通俗解释）

## 质量标准

一个好的自然语言框架文档，非技术人员读完后应该能回答：
1. 这个项目是做什么的？
2. 它分为哪几个大部分？
3. 每个部分是干什么的？
4. 这些部分是怎么串联起来的？
