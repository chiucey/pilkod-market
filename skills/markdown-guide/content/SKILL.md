---
name: markdown-guide
description: 提供Markdown编写的完整指导与全面校验能力，包括代码嵌入、图表绘制、目录生成、多级内容组织、代码语法检查、拼写检查、图表完整性校验、跨文件校验、文档类型识别与标准格式校验；当用户需要创建或优化Markdown文档、编写技术文档、生成项目README、校验文档质量时使用
dependency:
  python:
  system:
    - npm install -g typescript ts-node @types/node
---

# Markdown 编写与校验指南

## 任务目标
- 本 Skill 用于：指导智能体编写规范、专业的 Markdown 文档，并提供全面的自动化校验能力
- 能力包含：语法指导、代码嵌入、图表绘制（Mermaid + PlantUML）、目录生成、多级内容组织、代码语法检查、拼写检查、工作流图表完整性校验、跨文件校验、文档类型识别与标准格式校验
- 触发条件：用户需要创建 Markdown 文档、优化现有文档、生成 README、编写技术文档、校验文档质量

## 前置准备

### 依赖安装
校验工具需要 Node.js 和 TypeScript 环境：

```bash
# 安装 TypeScript 和 ts-node
npm install -g typescript ts-node
```

### 智能体能力
智能体已具备文本分析和内容创作能力，可完成大部分编写和校验工作。

## 操作步骤

### 标准流程

**步骤 1：需求分析**
- 了解文档类型（README、技术文档、API 文档、设计文档等）
- 确认内容结构需求（是否需要目录、图表、代码示例等）
- 识别目标读者和使用场景

**步骤 2：结构设计**
- 根据文档类型选择合适模板：见 [references/document-templates/](references/document-templates/)
  - README 文档：[references/document-templates/readme.md](references/document-templates/readme.md)
  - API 文档：[references/document-templates/api-documentation.md](references/document-templates/api-documentation.md)
  - 技术指南：[references/document-templates/technical-guide.md](references/document-templates/technical-guide.md)
  - 变更日志：[references/document-templates/changelog.md](references/document-templates/changelog.md)
  - 贡献指南：[references/document-templates/contributing.md](references/document-templates/contributing.md)
  - 设计文档：[references/document-templates/design-doc.md](references/document-templates/design-doc.md)
- 确定标题层级（建议不超过 4 级）
- 规划需要插入的元素（代码块、图表、表格等）

**步骤 3：内容编写**
- 遵循语法规范：见 [references/syntax-guide.md](references/syntax-guide.md)
- 代码块嵌入：见 [references/code-blocks.md](references/code-blocks.md)
- 图表与表格：见 [references/diagrams.md](references/diagrams.md)
  - Mermaid 图表：流程图、时序图、类图、状态图等
  - PlantUML 图表：完整的 UML 图表支持
  - 表格：Markdown 表格和 HTML 表格

**步骤 4：目录生成**
- 自动目录：使用 `[toc]` 或 `[[toc]]`（取决于渲染器支持）
- 手动目录：按层级列出标题链接，示例：
  ```markdown
  ## 目录
  - [章节一](#章节一)
    - [小节1.1](#小节11)
  - [章节二](#章节二)
  ```

**步骤 5：校验修正（双重校验模式）**

**方式一：脚本自动校验（全面校验 + 兜底）**
```bash
# 校验单个文件
npx ts-node scripts/markdown-validator.ts <markdown-file>

# 校验目录下所有文件
npx ts-node scripts/markdown-validator.ts <directory>

# 启用跨文件校验
npx ts-node scripts/markdown-validator.ts --cross-file <directory>
```

**校验工具能力（模块化架构）：**

| 模块 | 校验内容 | 说明 |
|:-----|:---------|:-----|
| **基础校验** | 标题层级、目录一致性、链接图片语法、表格格式、列表格式 | 结构性检查 |
| **代码校验** | 语言类型标识、拼写错误、语法错误 | 代码块质量 |
| **图表校验** | Mermaid/PlantUML 语法、ASCII 艺术、实体提取 | 图表格式 |
| **工作流校验** | 流程图起点终点、分支完整性、节点可达性 | 工作流完整性 |
| **实体校验** | 实体映射、图表间关系、逻辑表达 | 跨图表一致性 |
| **跨文件校验** | 文件引用、实体一致性、逻辑一致性 | 多文件项目 |
| **文档类型校验** | 文档类型识别、标准格式校验、必选章节检查 | 文档规范性 |

**校验输出格式示例：**
```
============================================================
文件: example.md
文档类型: readme
评分: 85.0%
============================================================

❌ 错误 (2):
  [L10] 缺少必选章节: 许可证
    建议: 添加章节: ## 许可证
  [L25] 链接指向不存在的标题
    建议: 检查标题是否正确

⚠️  警告 (3):
  [L5] 文档包含多个 H1 标题
    建议: 建议只保留一个 H1 标题作为文档主标题
  [L15] 代码块未指定语言标识
    建议: 添加语言标识以启用语法高亮和校验

ℹ️  提示 (2):
  [L1] 建议添加章节: 贡献
  [L1] 建议添加章节: 变更日志

📊 统计:
  错误: 2
  警告: 3
  提示: 2
  总计: 7

📋 缺少章节: 许可证
```

**输出解读：**
- **文档类型**：自动识别的文档类型（readme/api-doc/design-doc 等）
- **评分**：基于必选章节和推荐章节的完成度评分
- **错误（❌）**：必须修复的问题，影响文档质量
- **警告（⚠️）**：建议修复的问题，提升文档质量
- **提示（ℹ️）**：优化建议，非必须修复
- **缺少章节**：列出所有缺失的必选章节

**方式二：智能体深度校验（语义理解）**
- 应用校验规则：见 [references/validation-rules.md](references/validation-rules.md)
- 代码校验规则：见 [references/code-validation.md](references/code-validation.md)
- 工作流图表校验：见 [references/workflow-diagram-validation.md](references/workflow-diagram-validation.md)
- 跨文件校验：见 [references/cross-file-validation.md](references/cross-file-validation.md)
- 实体与逻辑一致性：见 [references/document-consistency.md](references/document-consistency.md)
- 智能体进行语义分析和上下文理解
- 提供修正建议并应用修改

**双重校验流程：**
1. 先执行脚本校验 → 修正基础问题
2. 再由智能体深度校验 → 处理语义问题
3. 重新执行脚本校验 → 确保修正完成

### 可选分支

**场景 A：快速创建 README**
- 使用模板：[references/document-templates/readme.md](references/document-templates/readme.md)
- 标准结构：标题、描述、安装、使用、许可证
- 重点：简洁明了、代码示例、清晰的安装步骤

**场景 B：编写 API 文档**
- 使用模板：[references/document-templates/api-documentation.md](references/document-templates/api-documentation.md)
- 包含：认证说明、接口列表、参数表格、响应示例、错误码
- 重点：参数说明完整、示例可运行

**场景 C：编写技术指南**
- 使用模板：[references/document-templates/technical-guide.md](references/document-templates/technical-guide.md)
- 包含：前置条件、分步骤说明、验证方法、常见问题
- 重点：步骤清晰、可操作性强

**场景 D：编写设计文档**
- 使用模板：[references/document-templates/design-doc.md](references/document-templates/design-doc.md)
- 包含：背景、目标、方案设计、风险评估、实施计划
- 重点：决策有依据、风险有评估

**场景 E：校验多文件项目**
- 使用跨文件校验模式
- 检查文件间引用、实体定义、逻辑一致性
- 生成跨文件校验报告

**场景 F：绘制 UML 图表**
- Mermaid：适合简单的流程图、时序图（GitHub 原生支持）
- PlantUML：适合完整的 UML 建模（类图、用例图、组件图等）
- 参考 [references/diagrams.md](references/diagrams.md) 选择合适的图表类型

## 资源索引

### 文档模板
- **README 模板**：[references/document-templates/readme.md](references/document-templates/readme.md)
  - 项目入口文档标准结构
  - 必选/推荐章节说明
  - 质量检查要点

- **API 文档模板**：[references/document-templates/api-documentation.md](references/document-templates/api-documentation.md)
  - 接口文档标准格式
  - 认证、参数、响应、错误码说明
  - 多语言 SDK 示例

- **技术指南模板**：[references/document-templates/technical-guide.md](references/document-templates/technical-guide.md)
  - 步骤化教程结构
  - 前置条件和验证方法
  - 常见问题处理

- **变更日志模板**：[references/document-templates/changelog.md](references/document-templates/changelog.md)
  - 版本历史记录格式
  - 变更类型分类
  - 语义化版本规范

- **贡献指南模板**：[references/document-templates/contributing.md](references/document-templates/contributing.md)
  - 开发环境搭建
  - 代码规范和提交规范
  - Issue/PR 模板

- **设计文档模板**：[references/document-templates/design-doc.md](references/document-templates/design-doc.md)
  - 设计文档标准结构
  - 方案对比和风险评估
  - 实施计划和时间线

### 语法参考
- **语法规范**：[references/syntax-guide.md](references/syntax-guide.md)
  - 完整的 Markdown 语法说明
  - 标题、段落、列表、链接、引用等用法

- **代码嵌入**：[references/code-blocks.md](references/code-blocks.md)
  - 多语言代码块写法
  - 语法高亮、行号、高亮行

- **图表绘制**：[references/diagrams.md](references/diagrams.md)
  - Mermaid 图表：流程图、时序图、类图、状态图、ER图、甘特图等
  - PlantUML 图表：完整的 UML 图表支持
  - 表格：Markdown 表格和 HTML 表格

### 校验规则
- **基础校验规则**：[references/validation-rules.md](references/validation-rules.md)
  - 目录校验、图表格式校验
  - 常见错误和修正方法

- **代码校验规则**：[references/code-validation.md](references/code-validation.md)
  - 代码块语言类型校验
  - 拼写检查、语法检查

- **工作流图表校验**：[references/workflow-diagram-validation.md](references/workflow-diagram-validation.md)
  - 流程图/时序图/用例图/状态图完整性规则

- **跨文件校验**：[references/cross-file-validation.md](references/cross-file-validation.md)
  - 跨文件引用、实体一致性、逻辑一致性规则

- **实体与逻辑一致性**：[references/document-consistency.md](references/document-consistency.md)
  - 实体映射、图表关系、逻辑表达一致性

### 校验工具
- **主入口**：[scripts/markdown-validator.ts](scripts/markdown-validator.ts)
- **模块化架构**：
  - [scripts/validator/core.ts](scripts/validator/core.ts) - 核心类型定义和基础类
  - [scripts/validator/basic.ts](scripts/validator/basic.ts) - 基础校验模块
  - [scripts/validator/code.ts](scripts/validator/code.ts) - 代码校验模块
  - [scripts/validator/diagram.ts](scripts/validator/diagram.ts) - 图表校验模块
  - [scripts/validator/workflow.ts](scripts/validator/workflow.ts) - 工作流完整性校验
  - [scripts/validator/entity.ts](scripts/validator/entity.ts) - 实体一致性校验
  - [scripts/validator/cross-file.ts](scripts/validator/cross-file.ts) - 跨文件校验
  - [scripts/validator/document-type.ts](scripts/validator/document-type.ts) - 文档类型识别

## 注意事项

### 编写原则
1. **简洁性**：避免过度嵌套，保持结构清晰
2. **一致性**：统一使用标题层级、列表格式、代码块风格
3. **可读性**：合理使用空行分隔段落，代码块添加语言标识
4. **完整性**：链接必须有效，图片路径正确，目录与标题一致
5. **模板优先**：根据文档类型选择对应模板，确保结构规范

### 文档类型识别
校验工具会自动识别以下文档类型：

| 文档类型 | 识别模式 | 必选章节 | 适用场景 |
|:---------|:---------|:---------|:---------|
| README | readme.md 文件名 | 安装、使用、许可证 | 项目入口文档 |
| API 文档 | api 关键字 | 接口列表、认证、错误码 | API 参考文档 |
| 技术指南 | guide/tutorial 关键字 | 无（灵活结构） | 教程和指南 |
| FAQ | faq 关键字 | 无 | 常见问题解答 |
| 变更日志 | changelog 关键字 | 无（可选版本历史） | 版本更新记录 |
| 贡献指南 | contributing 关键字 | 如何贡献 | 开源项目贡献 |
| 设计文档 | design/rfc/需求/架构 | 背景、目标、方案设计 | 系统设计文档 |
| 流程文档 | 交互流程/流程/workflow | 描述、流程 | 交互流程说明 |
| 规范文档 | 规范/spec 关键字 | 概述、规范说明 | 技术规范标准 |
| Man Page | _*.md 格式 | 无 | Unix 风格手册页 |
| 用户文档 | user-doc 关键字 | 概述、功能说明 | 用户手册 |
| 快速开始 | quickstart 关键字 | 概述 | 入门指南 |

识别后会自动检查：
- 必选章节是否存在
- 推荐章节是否完整
- 文档结构是否规范
- 整体质量评分（满分 100 分）

### 代码块规范
1. **必须标注语言类型**：启用语法高亮和校验
2. **语法正确**：确保代码示例可运行
3. **拼写正确**：文本内容无拼写错误
4. **格式统一**：缩进风格一致

### 图表选择建议

| 场景 | 推荐工具 | 原因 |
|:-----|:---------|:-----|
| GitHub 文档 | Mermaid | 原生支持，无需插件 |
| 复杂 UML 建模 | PlantUML | 完整的 UML 2.5 支持 |
| 快速流程图 | Mermaid | 语法简单，即时渲染 |
| 架构设计文档 | PlantUML | 支持详细的系统建模 |

### 工作流图表完整性
1. **流程图**：必须有起点和终点，分支必须完整
2. **时序图**：所有参与者必须参与交互，alt 块必须闭合
3. **用例图**：必须有 Actor 和用例，关系必须完整
4. **状态图**：必须有初始状态，状态转换必须完整

### 跨文件项目
1. **文件引用**：使用相对路径，定期检查有效性
2. **实体定义**：统一命名规范，保持一致性
3. **逻辑描述**：同一流程在不同文件中描述一致

### 双重校验原则

所有校验都采用**脚本 + 智能体**双重模式：

1. **脚本校验（自动化 + 兜底）**
   - 精确的模式匹配
   - 自动化批量处理
   - 防止遗漏和错误
   - 标准化输出报告
   - 覆盖所有校验规则

2. **智能体校验（语义理解）**
   - 理解上下文和业务含义
   - 处理模糊和边界情况
   - 提供修正建议和示例
   - 确认修正结果

**校验流程：** 脚本先行 → 智能体深度分析 → 脚本确认修正

### 校验时机
- 初稿完成后：运行校验脚本，检查基本语法和结构
- 内容修改后：验证链接、目录和引用
- 发布前：完整校验，确保专业性
- 多文件项目：运行跨文件校验

## 使用示例

### 示例 1：创建项目 README
```
用户请求："为我的 Python 项目创建一个 README"

执行步骤：
1. 询问项目基本信息（名称、功能、安装方式）
2. 选择 README 模板：[references/document-templates/readme.md](references/document-templates/readme.md)
3. 设计 README 结构（标题、描述、安装、使用、许可证）
4. 编写内容，插入代码示例
5. 运行校验脚本检查格式和链接
6. 输出完整 README
```

### 示例 2：编写 API 文档
```
用户请求："为我的 API 编写文档"

执行步骤：
1. 收集 API 信息（接口列表、参数、响应格式）
2. 选择 API 文档模板：[references/document-templates/api-documentation.md](references/document-templates/api-documentation.md)
3. 编写认证说明、接口列表、参数表格
4. 添加请求/响应示例
5. 编写错误码说明
6. 运行校验检查完整性
7. 输出 API 文档
```

### 示例 3：校验并修正文档
```
用户请求："检查这个 Markdown 文档有没有问题"

执行步骤：
1. 运行校验脚本：npx ts-node scripts/markdown-validator.ts <file>
2. 分析错误和警告
3. 查看文档类型识别结果和标准检查
4. 按优先级修正问题
5. 重新校验确认修复
6. 返回优化后的文档
```

### 示例 4：校验多文件项目
```
用户请求："检查我的文档项目的一致性"

执行步骤：
1. 运行多文件校验：npx ts-node scripts/markdown-validator.ts --cross-file docs/
2. 查看单文件校验结果
3. 查看跨文件校验结果（实体一致性、逻辑一致性）
4. 分析问题并修正
5. 重新校验确认修复
```

### 示例 5：校验工作流图表
```
用户请求："检查流程图是否完整"

执行步骤：
1. 运行校验脚本
2. 查看流程图完整性检查结果
3. 检查：起点、终点、分支完整性、节点可达性
4. 补充缺失部分
5. 重新校验确认完整性
```

## 智能体职责说明

本 Skill 采用混合实现方式：

### 自然语言指导（主要方式）
智能体负责：
- **语言理解**：理解用户需求和文档类型
- **内容创作**：编写符合规范的 Markdown 内容
- **结构化思维**：规划文档结构和层级
- **模板选择**：根据场景选择合适模板
- **校验建议**：根据规则提供修正方案
- **语义分析**：深度分析文档逻辑和一致性

### 脚本工具（全面兜底）
校验脚本提供：
- **全面检查**：覆盖所有校验规则，无遗漏
- **自动化处理**：快速扫描大量文档
- **精确错误定位**：准确报告问题位置
- **标准化规则**：一致的校验标准
- **跨文件能力**：检查多文件项目一致性
- **文档类型识别**：自动识别并校验文档规范
- **模块化架构**：9 个独立模块，易于维护和扩展

两种方式配合使用，提升效率和准确性。
