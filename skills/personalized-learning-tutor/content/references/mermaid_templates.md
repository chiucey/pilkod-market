# Mermaid 图表模板库

## 流程图模板

### 基础流程图
```mermaid
graph LR
    A[开始] --> B[步骤1]
    B --> C{判断}
    C -->|是| D[结果1]
    C -->|否| E[结果2]
    D --> F[结束]
    E --> F
```

### 横向流程图
```mermaid
graph LR
    A[输入] --> B[处理]
    B --> C[处理2]
    C --> D[输出]
```

### 下向上流程图
```mermaid
graph BT
    A[底层] --> B[中层]
    B --> C[顶层]
```

## 架构图模板

### 层级架构图
```mermaid
graph TB
    A[顶层模块] --> B[模块1]
    A --> C[模块2]
    A --> D[模块3]
    B --> B1[子模块1.1]
    B --> B2[子模块1.2]
    C --> C1[子模块2.1]
    D --> D1[子模块3.1]
    D --> D2[子模块3.2]
```

### 组件架构图
```mermaid
graph LR
    subgraph 前端
        A[用户界面]
    end
    subgraph 后端
        B[API服务]
        C[数据库]
    end
    A --> B
    B --> C
```

## 循环流程图
```mermaid
graph LR
    A[开始] --> B[执行]
    B --> C{检查}
    C -->|继续| B
    C -->|完成| D[结束]
```

## 序列图模板

### 简单交互流程
```mermaid
sequenceDiagram
    participant 用户
    participant 系统
    participant 数据库
    用户->>系统: 请求
    系统->>数据库: 查询
    数据库-->>系统: 返回结果
    系统-->>用户: 响应
```

### 详细交互流程
```mermaid
sequenceDiagram
    participant U as 用户
    participant A as 应用
    participant S as 服务
    participant D as 数据

    U->>A: 发起请求
    A->>S: 转发请求
    S->>D: 数据操作
    D-->>S: 返回数据
    S-->>A: 处理结果
    A-->>U: 展示结果
```

## 状态图模板

### 状态转换图
```mermaid
stateDiagram-v2
    [*] --> 初始状态
    初始状态 --> 运行中: 启动
    运行中 --> 暂停: 暂停
    暂停 --> 运行中: 继续
    运行中 --> 结束: 完成
    结束 --> [*]
```

## 甘特图模板

### 学习计划甘特图
```mermaid
gantt
    title 学习计划时间线
    dateFormat  YYYY-MM-DD
    section 第一周
    基础概念           :a1, 2024-01-01, 3d
    核心原理           :a2, after a1, 4d
    section 第二周
    进阶应用           :b1, 2024-01-08, 5d
    实践项目           :b2, after b1, 2d
    section 第三周
    综合项目           :c1, 2024-01-15, 7d
```

## ER图模板

### 实体关系图
```mermaid
erDiagram
    用户 {
        int id PK
        string name
        string email
    }
    课程 {
        int id PK
        string title
        int user_id FK
    }
    用户 ||--o{ 课程 : 创建
```

## 思维导图模板

### 主题发散图
```mermaid
mindmap
  root((核心主题))
    概念A
      要点1
      要点2
    概念B
      要点3
      要点4
    概念C
      要点5
      要点6
```

## 类图模板

### 简单类图
```mermaid
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()
    }
    class Dog {
        +String breed
        +bark()
    }
    class Cat {
        +String color
        +meow()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

## 使用场景对照表

| 内容类型 | 推荐图表 | Mermaid类型 |
|----------|----------|-------------|
| 操作步骤 | 流程图 | graph LR/TB |
| 系统架构 | 架构图 | graph TB |
| 交互流程 | 序列图 | sequenceDiagram |
| 状态变化 | 状态图 | stateDiagram |
| 时间安排 | 甘特图 | gantt |
| 数据关系 | ER图 | erDiagram |
| 概念发散 | 思维导图 | mindmap |
| 类结构 | 类图 | classDiagram |

## 样式配置建议

### 颜色主题
- 基础概念：蓝色系 (#4A90E2)
- 重要内容：橙色系 (#F5A623)
- 关键节点：绿色系 (#7ED321)
- 警示/注意：红色系 (#D0021B)

### 字体大小
- 标题：18-20px
- 节点文字：14-16px
- 注释说明：12px

### 布局建议
- 横向流程：使用 LR
- 纵向层级：使用 TB
- 复杂关系：适当使用缩进和分组
