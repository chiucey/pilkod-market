---
name: testbuddy-skill
description: 文本测试用例生成技能包。任何有关于文本测试用例生成、文本测试用例框架生成、脑图用例生成、召回、需求分析等文本测试用例生成的相关问题，都可以使用此技能。
---

# Design Agent Skill 测试设计技能包

## 核心定位

本 skill 是一个**轻量级的意图识别和工作流调度器**，负责：
1. 识别用户意图
2. 加载必要的会话参数
3. 调用对应的工作流

**工作流负责**：
- 自己的执行清单规划
- 具体的执行逻辑
- 任务状态管理

## 执行流程

### 🚨 重要：必须严格按照流程执行

**禁止跳过任何步骤！禁止直接执行操作！必须按照以下流程执行！**

### 步骤 0：识别意图类型（必须首先执行）

**必须首先判断用户意图是单一意图还是复合意图**：

#### 单一意图

用户只请求一个操作：

| 用户意图 | 触发关键词 | 意图关键词 |
|---------|-----------|-----------|
| 生成测试框架 | `生成测试框架`、`生成框架`、`创建测试框架` | `框架生成` |
| 生成测试模块 | `生成测试模块`、`生成功能模块`、`识别测试模块` | `模块生成` |
| 生成测试场景 | `生成测试场景`、`生成场景`、`创建测试场景` | `场景生成` |
| 生成测试点 | `生成测试点`、`创建测试点`、`根据模块生成测试点` | `测试点生成` |
| 生成测试用例 | `生成测试用例`、`生成用例`、`根据测试点生成用例` | `用例生成` |

#### 复合意图（可选，按需执行）

用户请求包含多个操作，**按顺序逐步执行**：

| 复合意图 | 执行顺序 | 说明 |
|---------|---------|------|
| 从TAPD获取需求并生成测试点 | 1. 获取需求 → 2. 生成测试点 | 先执行TAPD获取（可选），再执行测试点生成 |
| 从TAPD获取需求并生成测试用例 | 1. 获取需求 → 2. 生成测试用例 | 先执行TAPD获取（可选），再执行用例生成 |
| 从TAPD获取需求并生成测试框架 | 1. 获取需求 → 2. 生成测试框架 | 先执行TAPD获取（可选），再执行框架生成 |

**注意**：TAPD获取需求是**可选的**，用户也可以：
- 直接提供需求文档路径（如：`根据 @file:需求文档.md 生成测试点`）
- 直接提供需求内容（如：`根据以下需求生成测试点：...`）
- 从本地文件读取需求

### 步骤 1：加载会话参数（必须执行）

**无论单一意图还是复合意图，都必须执行此步骤！**

使用 `tools/load_session.md` 工具读取上下文信息。

### 步骤 2：获取需求内容（按需执行）

**根据用户提供的需求数据源，选择合适的获取方式**

**重要**：必须识别用户是否提供了"参考需求"或"参考用例"，如有则必须获取

#### 2.1 识别需求类型

- **主需求**：用户明确要求生成测试点/用例的需求
- **参考需求**：用户提供作为参考的其他需求（关键词：`参考需求`、`参考`、`类似需求`、`参照需求`）
- **参考用例**：用户提供作为参考的测试用例（关键词：`参考用例`、`参考测试用例`、`类似用例`）

#### 2.2 获取主需求内容

根据用户提供的需求数据源，选择合适的获取方式：

**方式1：从TAPD获取需求（可选）**

如果用户明确要求从TAPD获取需求，执行以下流程：

1. **读取TAPD工具文档**：使用 `read_file` 读取 `tools/fetch_tapd_issue.md`
2. **执行TAPD脚本**：使用 `run_command` 执行脚本获取需求
   ```bash
   python scripts/fetch_tapd_issue.py --issue-id <需求ID> --save --output markdown
   ```
3. **验证获取结果**：确认需求文件已保存到 `.testbuddy/md/` 目录
4. **读取需求内容**：使用 `read_file` 读取生成的需求文件

**方式2：从本地文件读取需求（可选）**

如果用户提供了本地需求文档路径（如：`@file:需求文档.md`），直接读取文件内容。

**支持的文件格式**：
- **文本格式**：`.md`、`.json`、`.yaml`、`.yml`、`.txt` - 直接读取文件内容
- **Excel格式**：`.xlsx`、`.xls` - 需要调用解析脚本提取内容
- **XMind格式**：`.xmind` - 需要调用解析脚本提取内容

**Excel和XMind文件处理流程**：

1. **识别文件类型**：根据文件扩展名判断
2. **调用解析脚本并保存**：
   - Excel文件：执行 `python scripts/parse_excel.py <文件路径> --output-file ".testbuddy/md/excel_reference.json"`
   - XMind文件：执行 `python scripts/parse_xmind.py <文件路径> --output-file ".testbuddy/md/xmind_reference.json"`
3. **保存解析结果**：将解析结果保存到 `.testbuddy/md/` 目录
4. **读取解析内容**：使用 `read_file` 读取保存的JSON文件
5. **使用解析内容**：将解析结果作为需求内容使用

**方式3：直接使用用户提供的需求内容（可选）**

如果用户直接提供了需求内容，直接使用该内容。

#### 2.3 获取参考需求内容（如有）

**重要**：必须主动识别用户是否提供了参考需求，如有则必须获取

**识别方式**：
- 关键词识别：`参考需求`、`参考`、`类似需求`、`参照需求`
- TAPD需求ID识别：用户提到其他需求ID
- 文件路径识别：用户提供了其他需求文档路径

**获取方式**：

**方式1：从TAPD获取参考需求**
1. 执行TAPD脚本：`python scripts/fetch_tapd_issue.py --issue-id <需求ID> --save --output markdown`
2. 读取保存的文件内容作为参考需求

**方式2：从本地文件读取参考需求**
- 文本文件：直接读取内容
- Excel文件：使用 `parse_excel.py` 解析
- XMind文件：使用 `parse_xmind.py` 解析

**示例**：
```
用户: 生成需求ID为123的测试点，参考需求：需求ID是456
识别: 主需求ID=123，参考需求ID=456
执行: 
  1. 获取主需求: python scripts/fetch_tapd_issue.py --issue-id 123 --save --output markdown
  2. 获取参考需求: python scripts/fetch_tapd_issue.py --issue-id 456 --save --output markdown
```

#### 2.4 获取参考用例内容（如有）

**重要**：必须主动识别用户是否提供了参考用例，如有则必须获取

**识别方式**：
- 关键词识别：`参考用例`、`参考测试用例`、`类似用例`
- 文件路径识别：用户提供了用例文档路径

**获取方式**：
- Excel文件：使用 `parse_excel.py` 解析
- XMind文件：使用 `parse_xmind.py` 解析

**示例**：
```
用户: 参考用例：C:\Users\XXXX.xls
识别: 参考用例文件路径
执行: python scripts/parse_excel.py "C:\Users\XXXX.xls" --output-file ".testbuddy/md/excel_cases.json"
```

#### 2.5 输出结果

- **主需求信息**：需求ID、需求名称、需求内容
- **参考需求列表**：`reference_requirements`（如有）
- **参考用例列表**：`reference_cases`（如有）

**注意**：以上方式是**并列关系**，根据用户的实际请求选择其中一种即可。**参考需求和参考用例不是强制的**，仅当用户意图明确需要参考时才获取。

### 步骤 3：选择并调用工作流（必须执行）

**禁止跳过此步骤！必须通过select_workflow选择工作流！**

1. **使用 select_workflow 工具**：
   - 调用 `tools/select_workflow.md` 工具
   - 传入识别的意图关键词（如"测试点生成"、"用例生成"）

2. **调用工作流**：
   - 根据 `select_workflow` 返回的路径类型选择读取方式：
     - 如果路径以 `.codebuddy/rules/` 开头（自定义工作流）：使用 `read_rules` 读取
     - 如果路径以 `workflows/` 开头（默认工作流）：使用 `read_file` 读取
   - 交由工作流执行具体逻辑
   - **禁止不执行select_workflow流程直接读取文件/工作流**

### 🚨 常见错误及纠正

| 错误行为 | 正确行为 |
|---------|---------|
| 强制要求必须从TAPD获取需求 | 根据用户实际请求选择需求来源，支持TAPD、本地文件、直接提供内容三种方式 |
| 跳过select_workflow直接读取工作流文件 | 必须通过select_workflow选择工作流，不能直接读取 |
| 跳过load_session直接执行操作 | 必须先加载会话参数，再执行后续操作 |
| 复合意图只执行其中一个步骤 | 必须按顺序执行所有步骤 |


## 工作流能力矩阵（供参考）

| 生成目标 | 触发关键词 | 输入节点类型 | 输出节点类型 |
|---------|-----------|-------------|-------------|
| 测试框架 | `framework`/`框架` | STORY/BUG | FEATURE/SCENE/TEST_POINT |
| 测试模块 | `feature`/`模块` | STORY/BUG | FEATURE |
| 测试场景 | `scene`/`场景` | FEATURE/STORY/BUG | SCENE |
| 测试点 | `tpoint`/`testpoint`/`测试点` | FEATURE/SCENE/STORY/BUG | TEST_POINT |
| 测试用例 | `case`/`用例` | STORY/BUG/FEATURE/TEST_POINT/SCENE | CASE |

## 工具能力矩阵（供参考）

| 工具 | 功能 | 文档路径 |
|-----|------|----------|
| select_workflow | 智能选择工作流 | `tools/select_workflow.md` |
| select_rule | 智能选择规则 | `tools/select_rule.md` |
| load_session | 加载会话参数 | `tools/load_session.md` |
| add_nodes | 添加节点到脑图 | `tools/add_nodes.md` |
| update_nodes | 修改脑图节点 | `tools/update_nodes.md` |
| delete_nodes | 删除脑图节点 | `tools/delete_nodes.md` |
| search_nodes | 查询脑图节点 | `tools/search_nodes.md` |
| rag_search | 知识库检索 | `tools/rag_search.md` |
| fetch_tapd_issue | 从TAPD获取需求 | `tools/fetch_tapd_issue.md` |

## TAPD需求获取功能

### 功能说明

本技能支持从TAPD获取需求内容，用于测试点和测试用例生成。

### 使用方法

1. **配置TAPD参数**：在 `.testbuddy/env/session.json` 中配置TAPD相关参数
2. **获取需求**：使用命令获取需求并保存为Markdown文件
3. **引用需求**：在对话中引用生成的Markdown文件进行测试生成

### 配置示例

```json
{
  "tapd": {
    "base_url": "https://www.tapd.cn",
    "cookie": "your_cookie_string",
    "workspace_id": "your_workspace_id"
  }
}
```

### 执行示例

```bash
# 获取需求并保存
python scripts/fetch_tapd_issue.py --issue-id 1167410840001329364 --save --output markdown

# 在对话中引用
# 用户: 根据 @file:.testbuddy/md/STORY-1167410840001329364.md 生成测试点
```

### 注意事项

- **需求ID格式**：使用完整的需求ID，如 `1167410840001329364`（15-18位数字）
- **Cookie配置**：需要在浏览器中获取有效的TAPD Cookie
- **权限要求**：Cookie需要有查看对应需求的权限
- **响应完整性**：脚本会完整获取需求的所有字段，包括描述、状态、优先级等
- **格式转换**：自动将HTML格式的需求描述转换为Markdown格式

---
