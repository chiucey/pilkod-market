---
name: ontology
description: 类型化知识图谱技能：为MaxClaw提供结构化智能体记忆与可组合技能数据支撑。当用户要求创建/查询/管理知识图谱实体（Person/Project/Task等）、定义实体关系、进行约束校验、实现跨技能数据共享、执行图谱遍历查询时使用。支持知识结构化管理与高效复用。
---

# Ontology - 类型化知识图谱技能

## 核心能力概览

本技能为 MaxClaw 提供类型化知识图谱能力，支持：
- **12大核心实体类型**的创建、查询、更新、删除
- **实体关系定义**与关联管理（含类型限制、cardinality、无环性约束）
- **约束规则校验**（必填属性、枚举值、关系合法性）
- **Append-only 存储模式**保留数据历史
- **跨技能数据共享**与规划式图谱转换

---

## 1. 核心实体类型体系

### 1.1 12大核心实体类型

```yaml
Person:
  description: 人物实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: role
      type: enum
      values: [developer, designer, manager, stakeholder, other]
      required: true
    - name: email
      type: string
      required: false
    - name: skills
      type: array[string]
      required: false
    - name: metadata
      type: object
      required: false

Organization:
  description: 组织实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: type
      type: enum
      values: [company, department, team, community, other]
      required: true
    - name: parent_id
      type: string
      required: false
      description: 父组织ID，支持层级结构
    - name: metadata
      type: object
      required: false

Project:
  description: 项目实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: status
      type: enum
      values: [planning, active, paused, completed, cancelled]
      required: true
      default: planning
    - name: owner_id
      type: string
      required: true
      ref_type: Person
    - name: start_date
      type: string
      required: false
    - name: end_date
      type: string
      required: false
    - name: description
      type: string
      required: false
    - name: metadata
      type: object
      required: false

Task:
  description: 任务实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: title
      type: string
      required: true
    - name: status
      type: enum
      values: [todo, in_progress, review, done, blocked]
      required: true
      default: todo
    - name: priority
      type: enum
      values: [low, medium, high, critical]
      required: false
      default: medium
    - name: assignee_id
      type: string
      required: false
      ref_type: Person
    - name: project_id
      type: string
      required: false
      ref_type: Project
    - name: due_date
      type: string
      required: false
    - name: dependencies
      type: array[string]
      required: false
      description: 依赖任务ID列表
    - name: metadata
      type: object
      required: false

Concept:
  description: 概念实体（用于抽象知识表示）
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: category
      type: string
      required: false
    - name: description
      type: string
      required: false
    - name: synonyms
      type: array[string]
      required: false
    - name: metadata
      type: object
      required: false

Document:
  description: 文档实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: title
      type: string
      required: true
    - name: type
      type: enum
      values: [spec, report, guide, note, api_doc, other]
      required: true
    - name: content
      type: string
      required: false
    - name: author_id
      type: string
      required: false
      ref_type: Person
    - name: project_id
      type: string
      required: false
      ref_type: Project
    - name: tags
      type: array[string]
      required: false
    - name: metadata
      type: object
      required: false

Event:
  description: 事件实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: type
      type: enum
      values: [meeting, deadline, milestone, review, release, other]
      required: true
    - name: start_time
      type: string
      required: true
    - name: end_time
      type: string
      required: false
    - name: location
      type: string
      required: false
    - name: participants
      type: array[string]
      required: false
      description: 参与者Person ID列表
    - name: project_id
      type: string
      required: false
      ref_type: Project
    - name: metadata
      type: object
      required: false
  constraints:
    - rule: end_time >= start_time
      message: "Event end_time must be greater than or equal to start_time"

Asset:
  description: 资产实体（代码、数据、文件等）
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: type
      type: enum
      values: [code, data, file, model, image, video, document, other]
      required: true
    - name: path
      type: string
      required: false
    - name: version
      type: string
      required: false
    - name: owner_id
      type: string
      required: false
      ref_type: Person
    - name: project_id
      type: string
      required: false
      ref_type: Project
    - name: tags
      type: array[string]
      required: false
    - name: metadata
      type: object
      required: false

Skill:
  description: 技能实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: category
      type: enum
      values: [technical, domain, soft, tool, language]
      required: false
    - name: level
      type: enum
      values: [beginner, intermediate, advanced, expert]
      required: false
    - name: owner_id
      type: string
      required: false
      ref_type: Person
    - name: description
      type: string
      required: false
    - name: metadata
      type: object
      required: false

Goal:
  description: 目标实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: description
      type: string
      required: false
    - name: status
      type: enum
      values: [defined, in_progress, achieved, abandoned]
      required: true
      default: defined
    - name: owner_id
      type: string
      required: false
      ref_type: Person
    - name: parent_goal_id
      type: string
      required: false
      ref_type: Goal
      description: 父目标ID，支持目标层级分解
    - name: metrics
      type: object
      required: false
    - name: metadata
      type: object
      required: false

Resource:
  description: 资源实体（计算、存储、人力等）
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: type
      type: enum
      values: [compute, storage, budget,人力, time, other]
      required: true
    - name: capacity
      type: object
      required: false
    - name: allocated_to
      type: array[string]
      required: false
      description: 已分配到的项目/任务ID
    - name: metadata
      type: object
      required: false

Conversation:
  description: 对话记录实体
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: participants
      type: array[string]
      required: true
      description: 参与者ID列表
    - name: topic
      type: string
      required: false
    - name: start_time
      type: string
      required: true
    - name: end_time
      type: string
      required: false
    - name: summary
      type: string
      required: false
    - name: metadata
      type: object
      required: false

Artifact:
  description: 产物实体（生成的文件、报告等）
  attributes:
    - name: id
      type: string
      required: true
      unique: true
    - name: name
      type: string
      required: true
    - name: type
      type: enum
      values: [report, presentation, code, config, data, model, other]
      required: true
    - name: format
      type: string
      required: false
    - name: path
      type: string
      required: false
    - name: generated_by
      type: string
      required: false
      ref_type: Skill
    - name: purpose
      type: string
      required: false
    - name: related_entities
      type: array[string]
      required: false
      description: 关联实体ID列表
    - name: metadata
      type: object
      required: false
```

---

## 2. 关系类型规范

### 2.1 预定义关系类型

```yaml
relationships:
  # 人与组织关系
  belongs_to:
    description: 人员属于组织
    from_types: [Person]
    to_types: [Organization]
    cardinality: many-to-one
    acyclic: true

  leads:
    description: 人员领导组织/项目
    from_types: [Person]
    to_types: [Organization, Project]
    cardinality: many-to-many
    acyclic: false

  # 项目关系
  owns:
    description: 人员拥有/负责项目
    from_types: [Person]
    to_types: [Project]
    cardinality: many-to-many
    acyclic: false

  contains:
    description: 组织包含子组织/项目
    from_types: [Organization, Project]
    to_types: [Organization, Project, Task]
    cardinality: one-to-many
    acyclic: true

  # 任务关系
  assigned_to:
    description: 任务分配给人员
    from_types: [Task]
    to_types: [Person]
    cardinality: many-to-one
    acyclic: false

  depends_on:
    description: 任务依赖关系
    from_types: [Task]
    to_types: [Task]
    cardinality: many-to-many
    acyclic: true
    inverse: blocks

  blocks:
    description: 任务阻塞关系（depends_on的反向）
    from_types: [Task]
    to_types: [Task]
    cardinality: many-to-many
    acyclic: true
    inverse: depends_on

  part_of:
    description: 任务属于项目
    from_types: [Task]
    to_types: [Project]
    cardinality: many-to-one
    acyclic: true

  # 文档关系
  authored_by:
    description: 文档由人员编写
    from_types: [Document]
    to_types: [Person]
    cardinality: many-to-one
    acyclic: false

  documents:
    description: 文档关联项目
    from_types: [Document]
    to_types: [Project, Task, Concept]
    cardinality: many-to-many
    acyclic: false

  # 技能关系
  has_skill:
    description: 人员拥有技能
    from_types: [Person]
    to_types: [Skill]
    cardinality: many-to-many
    acyclic: false

  implements:
    description: 技能实现概念
    from_types: [Skill]
    to_types: [Concept]
    cardinality: many-to-many
    acyclic: false

  # 目标关系
  achieves:
    description: 任务/项目达成目标
    from_types: [Task, Project]
    to_types: [Goal]
    cardinality: many-to-many
    acyclic: false

  decomposes_to:
    description: 目标分解为子目标/任务
    from_types: [Goal]
    to_types: [Goal, Task]
    cardinality: one-to-many
    acyclic: true

  # 资源关系
  allocates:
    description: 资源分配给项目/任务
    from_types: [Resource]
    to_types: [Project, Task]
    cardinality: many-to-many
    acyclic: false

  # 资产关系
  owns_asset:
    description: 人员拥有资产
    from_types: [Person]
    to_types: [Asset]
    cardinality: many-to-many
    acyclic: false

  contains_asset:
    description: 项目包含资产
    from_types: [Project]
    to_types: [Asset]
    cardinality: one-to-many
    acyclic: true

  # 事件关系
  has_event:
    description: 项目有事件
    from_types: [Project]
    to_types: [Event]
    cardinality: one-to-many
    acyclic: true

  participates_in:
    description: 人员参与事件
    from_types: [Person]
    to_types: [Event]
    cardinality: many-to-many
    acyclic: false

  # 对话关系
  involved_in:
    description: 人员参与对话
    from_types: [Person]
    to_types: [Conversation]
    cardinality: many-to-many
    acyclic: false

  # 产物关系
  produces:
    description: 技能/任务产生产物
    from_types: [Skill, Task]
    to_types: [Artifact]
    cardinality: many-to-many
    acyclic: false

  related_to:
    description: 通用关联关系
    from_types: ["*"]
    to_types: ["*"]
    cardinality: many-to-many
    acyclic: false
    description: 用于临时关联任意实体
```

---

## 3. 约束校验规则

### 3.1 属性约束

```yaml
attribute_constraints:
  # ID 唯一性
  unique_id:
    check: entity.id 不存在
    severity: error
    message: "Entity with id '{id}' already exists"

  # 必填属性
  required_attribute:
    check: 所有 required: true 的属性必须有值
    severity: error
    message: "Required attribute '{attribute}' is missing in {entity_type}"

  # 枚举值
  enum_value:
    check: 枚举属性值必须在允许列表内
    severity: error
    message: "Invalid value '{value}' for attribute '{attribute}'. Allowed: {allowed}"

  # 类型引用
  reference_integrity:
    check: ref_type 引用必须指向存在的实体
    severity: error
    message: "Reference '{attribute}' points to non-existent {ref_type} with id '{value}'"

  # 自定义逻辑约束
  custom_logic:
    # Event: end_time >= start_time
    - entity_type: Event
      rule: end_time is null OR end_time >= start_time
      message: "Event end_time must be >= start_time"
```

### 3.2 关系约束

```yaml
relationship_constraints:
  # 类型匹配
  type_match:
    check: 关系 from/to 类型必须在允许列表内
    severity: error
    message: "Cannot create '{relationship}' from {from_type} to {to_type}"

  # Cardinality 限制
  cardinality:
    # one-to-one: 两端各最多1条关系
    one-to-one:
      check: 每个实体的关联数量 <= 1
      severity: error
    # one-to-many: 一端1条，另一端多条
    one-to-many:
      check: 一端最多1条，另一端不限
      severity: error
    # many-to-many: 两端都不限
    many-to-many:
      check: 无限制
      severity: warning

  # 无环性检查
  acyclic_check:
    check: acyclic: true 的关系不能形成环
    severity: error
    message: "Relationship '{relationship}' cannot create cycles. Path found: {path}"
```

---

## 4. 核心功能实现

### 4.1 实体管理

#### 创建实体
```
操作: create_entity
输入:
  - entity_type: string (12种类型之一)
  - attributes: object (属性键值对)
  - id: string (可选，自动生成UUID)
输出:
  - success: boolean
  - entity_id: string
  - errors: array (如有校验错误)
执行流程:
  1. 生成/验证实体ID唯一性
  2. 应用属性类型约束
  3. 执行枚举值校验
  4. 执行必填属性校验
  5. 执行引用完整性校验
  6. 验证通过后写入存储
```

#### 查询实体
```
操作: query_entities
输入:
  - entity_type: string (可选，筛选类型)
  - filters: object (属性条件)
  - limit: number (可选，默认100)
  - offset: number (可选，分页)
输出:
  - entities: array
  - total: number
  - has_more: boolean
```

#### 更新实体
```
操作: update_entity
输入:
  - entity_id: string
  - updates: object (要更新的属性)
输出:
  - success: boolean
  - errors: array
执行流程:
  1. 校验实体存在
  2. 验证更新属性的合法性
  3. 保持append-only：创建新版本，保留历史
```

#### 删除实体
```
操作: delete_entity
输入:
  - entity_id: string
  - cascade: boolean (可选，是否删除关联关系)
输出:
  - success: boolean
  - deleted_relations: number
```

### 4.2 关系管理

#### 创建关系
```
操作: create_relation
输入:
  - from_id: string
  - to_id: string
  - relation_type: string
  - properties: object (可选，关系属性)
输出:
  - success: boolean
  - relation_id: string
执行流程:
  1. 验证 from/to 实体存在
  2. 校验关系类型合法性
  3. 执行类型匹配校验
  4. 执行 cardinality 校验
  5. 执行无环性校验
  6. 验证通过后写入
```

#### 查询关系
```
操作: query_relations
输入:
  - from_id: string (可选)
  - to_id: string (可选)
  - relation_type: string (可选)
  - depth: number (可选，遍历深度)
输出:
  - relations: array
  - paths: array (遍历路径)
```

#### 删除关系
```
操作: delete_relation
输入:
  - from_id: string
  - to_id: string
  - relation_type: string
输出:
  - success: boolean
```

### 4.3 图谱遍历

#### 深度优先遍历
```
操作: traverse_dfs
输入:
  - start_id: string
  - relation_types: array (可选，限定关系类型)
  - max_depth: number (默认3)
  - filter: object (可选，节点属性过滤)
输出:
  - nodes: array
  - edges: array
  - paths: array
```

#### 广度优先遍历
```
操作: traverse_bfs
输入:
  - start_id: string
  - relation_types: array
  - max_depth: number
  - limit: number (每层最大节点数)
输出:
  - levels: array (按层级组织的节点)
  - paths: array
```

#### 依赖路径查询
```
操作: find_dependency_path
输入:
  - from_id: string
  - to_id: string
输出:
  - path: array (节点ID序列)
  - relations: array (关系类型序列)
  - exists: boolean
```

### 4.4 约束校验

#### 全量校验
```
操作: validate_graph
输入:
  - entity_ids: array (可选，指定实体)
  - check_types: array (可选，指定校验类型)
输出:
  - valid: boolean
  - errors: array
  - warnings: array
  - details: object
```

#### 实时校验
```
操作: validate_entity
输入:
  - entity_id: string
  - operation: string (create/update)
输出:
  - valid: boolean
  - errors: array
  - warnings: array
```

---

## 5. 存储结构

### 5.1 Append-only 存储模式

```json
{
  "graph": {
    "entities": {
      "{entity_id}": {
        "version": 1,
        "created_at": "ISO8601",
        "updated_at": "ISO8601",
        "type": "Person",
        "data": { ... },
        "history": [
          {
            "version": 0,
            "timestamp": "ISO8601",
            "operation": "create",
            "data": { ... }
          }
        ]
      }
    },
    "relations": {
      "{relation_id}": {
        "created_at": "ISO8601",
        "from": "{entity_id}",
        "to": "{entity_id}",
        "type": "belongs_to",
        "properties": {}
      }
    },
    "indexes": {
      "by_type": {
        "Person": ["entity_id_1", "entity_id_2"],
        "Project": ["entity_id_3"]
      },
      "by_attribute": {
        "Person.name": {
          "John": ["entity_id_1"],
          "Jane": ["entity_id_2"]
        }
      }
    }
  },
  "metadata": {
    "version": "1.0.0",
    "created_at": "ISO8601",
    "last_updated": "ISO8601",
    "stats": {
      "total_entities": 100,
      "total_relations": 250,
      "by_type": { ... }
    }
  }
}
```

---

## 6. 跨技能数据共享

### 6.1 Skill Contract 规范

```yaml
skill_contract:
  skill_name: ontology
  permissions:
    read:
      - entities: ["*"]
        conditions: ["属主验证"]
      - relations: ["*"]
    write:
      - entities: ["*"]
        conditions: ["append-only保留历史"]
      - relations: ["*"]
  preconditions:
    - 输入实体类型必须是12种核心类型之一
    - ID必须唯一或为自动生成
    - 属性必须符合类型定义
  postconditions:
    - 操作结果已持久化
    - 索引已更新
    - 历史版本已保留
  error_handling:
    - 校验失败返回详细错误信息
    - 支持部分成功（可选）
```

---

## 7. 规划式图谱转换

### 7.1 任务规划流程

```
输入: 多步骤任务描述
输出: 图谱操作序列

Step 1: 解析任务
  - 识别涉及的实体类型
  - 识别实体间关系
  - 识别操作顺序依赖

Step 2: 生成操作序列
  - 创建实体 (按依赖排序)
  - 创建关系 (前置实体已存在)
  - 更新状态 (最后执行)

Step 3: 执行与回滚
  - 按序执行每个操作
  - 失败时回滚已完成操作
  - 返回执行结果
```

---

## 8. 使用示例

### 示例1: 创建人员并关联项目
```
用户: 创建开发者张三，负责"AI助手"项目
执行:
  1. create_entity(type: Person, attributes: {name: 张三, role: developer})
  2. create_entity(type: Project, attributes: {name: AI助手, status: planning})
  3. create_relation(from: 张三.id, to: AI助手.id, type: owns)
结果: 成功创建两个实体及关联关系
```

### 示例2: 查询项目依赖
```
用户: 查询"AI助手"项目的所有任务及依赖
执行:
  1. query_entities(entity_type: Task, filters: {project_id: AI助手.id})
  2. 遍历每个Task的depends_on关系
结果: 返回项目任务树及依赖路径
```

### 示例3: 约束校验
```
用户: 检查图谱数据完整性
执行:
  1. validate_graph()
  2. 检查所有引用的实体是否存在
  3. 检查关系类型合法性
结果: 返回校验报告，包含错误和警告列表
```

---

## 9. 错误码与消息

| 错误码 | 含义 | 处理建议 |
|--------|------|----------|
| E001 | 实体ID已存在 | 使用新ID或查询现有实体 |
| E002 | 必填属性缺失 | 补充缺失属性 |
| E003 | 枚举值无效 | 使用允许的值之一 |
| E004 | 引用实体不存在 | 先创建被引用实体 |
| E005 | 关系类型不匹配 | 检查from/to实体类型 |
| E006 | Cardinality冲突 | 删除现有关系或调整 |
| E007 | 循环依赖检测 | 移除环中的关系 |
| W001 | 建议使用唯一ID | 可忽略或使用UUID |
| W002 | 孤立实体检测 | 考虑添加关联关系 |
