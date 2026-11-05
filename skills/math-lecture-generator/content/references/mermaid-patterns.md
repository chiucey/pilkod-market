---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3045022100ba0e417326931487054492dadb8643fd7877b94290e4a95b966d02854cfbb469022078332db5c2690db787cd42249d0f25188447509e4d07cd415856d7151cfa7785
    ReservedCode2: 304502207dc01db7c5c7e7cbcb208211b4b11b3444b2a6749cd4d04da9972fa4b53fdb18022100b704393894329a690e633691e2d254f80159522a72c1f85605f3927b8132c732
---

# Mermaid 图表模板参考

## 流程图 (Flowchart)

### 基本结构

```mermaid
graph TD
    A[开始] --> B{判断条件}
    B -->|条件满足| C[结果1]
    B -->|条件不满足| D[结果2]
    C --> E[结束]
    D --> E
```

### 方向控制

| 方向 | 语法 | 说明 |
|------|------|------|
| TD/TB | `graph TD` | 从上到下 |
| BT | `graph BT` | 从下到上 |
| LR | `graph LR` | 从左到右 |
| RL | `graph RL` | 从右到左 |

### 节点形状

| 形状 | 语法 | 用途 |
|------|------|------|
| 圆角矩形 | `[文字]` | 过程/步骤 |
| 矩形 | `[文字]` | 标准节点 |
| 菱形 | `{文字}` | 判断/决策 |
| 圆形 | `((文字))` | 开始/结束 |
| 六边形 | `{{文字}}` | 准备/操作 |
| 平行四边形 | `[\文字\]` | 输入/输出 |
| 梯形 | `[/文字\]` | 子程序 |

### 连线样式

```mermaid
graph LR
    A --> B
    A --- C
    B -.-> D
    C ==>|标注| E
    F -->|标注| G
```

| 语法 | 样式 |
|------|------|
| `-->` | 实线箭头 |
| `---` | 实线无箭头 |
| `-.->` | 虚线箭头 |
| `==>` | 粗箭头 |
| `-.--` | 虚线无箭头 |

## 数学推理流程图

### 证明逻辑链

```mermaid
graph TD
    A[已知条件] --> B[应用定理]
    B --> C{验证前提}
    C -->|满足| D[得出结论]
    C -->|不满足| E[寻找反例]
    D --> F[证明完成]
    E --> G[假设不成立]
```

### 分类讨论树

```mermaid
graph TD
    A[问题分类] --> B{情况1: x > 0}
    A --> C{情况2: x = 0}
    A --> D{情况3: x < 0}
    B --> B1[解集1]
    C --> C1[解集2]
    D --> D1[解集3]
    B1 --> E[综合解集]
    C1 --> E
    D1 --> E
```

### 解题步骤流程

```mermaid
graph LR
    A[读题审题] --> B[提取条件]
    B --> C[确定方法]
    C --> D[执行计算]
    D --> E{检验结果}
    E -->|合理| F[写出答案]
    E -->|不合理| G[检查过程]
    G --> D
```

## 思维导图 (Mindmap)

```mermaid
mindmap
  root((数学))
    代数
      函数
        一次函数
        二次函数
      方程
        一元方程
        多元方程
    几何
      平面几何
      立体几何
    概率统计
```

## 类图 (Class Diagram)

```mermaid
classDiagram
    class 三角形 {
        +边长a, b, c
        +求周长()
        +求面积()
        +判断类型()
    }
    class 等腰三角形 {
        +底边
        +腰长
        +判断等边()
    }
    三角形 <|-- 等腰三角形
```

## 序列图 (Sequence Diagram)

```mermaid
sequenceDiagram
    participant 学生
    participant 系统
    participant 教师
    学生->>系统: 提交作业
    系统->>系统: 检查格式
    系统->>教师: 通知批改
    教师->>系统: 批改完成
    系统->>学生: 发送成绩
```

## 状态图 (State Diagram)

```mermaid
stateDiagram-v2
    [*] --> 推导中
    推导中 --> 分类讨论
    分类讨论 --> 结果1: 情况A
    分类讨论 --> 结果2: 情况B
    结果1 --> [*]
    结果2 --> [*]
```

## 数学概念关系图

### 集合关系

```mermaid
graph LR
    A([实数R]) --> B([有理数Q])
    B --> C([整数Z])
    C --> D([自然数N])
```

### 运算性质

```mermaid
graph TD
    A[运算律] --> B[交换律]
    A --> C[结合律]
    A --> D[分配律]
    B --> E[a + b = b + a]
    C --> F[(a+b)+c = a+(b+c)]
    D --> G[a×(b+c) = a×b + a×c]
```

## 甘特图 (Gantt) - 教学进度

```mermaid
gantt
    title 数学课件制作计划
    dateFormat YYYY-MM-DD
    section 第一章
    知识点1        :a1, 2026-01-01, 3d
    知识点2        :a2, after a1, 2d
    例题讲解        :a3, after a2, 2d
    section 第二章
    知识点3        :b1, 2026-01-08, 3d
    知识点4        :b2, after b1, 2d
    综合练习        :b3, after b2, 2d
```

## 饼图 (Pie) - 课时分配

```mermaid
pie title 课程内容占比
    "基础概念" : 30
    "例题讲解" : 40
    "练习巩固" : 20
    "总结复习" : 10
```