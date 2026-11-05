---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: b1ccc2899606640dccab65f0f1f43914
    PropagateID: b1ccc2899606640dccab65f0f1f43914
    ReservedCode1: 30450221008ba454dc5b68eaf633cb5c260fc443109ed9ea1921e890748b1201d1f44800380220695090e2ed9e61ff6685d9bc97660e62e7b773d8fb2c2c7e699763b646705f1e
    ReservedCode2: 30430220207adc739310f2530f800ce98328958be560cf53a0adbab4bcb47c38ef147f6b021f1e1304ca7f762822d65fc41109b4fa70270d19c71fb17fccf8f98aa9b5d2a4
---

# Mermaid 图结构生成参考

## 基础图结构

### 1. 树状结构图 (graph TD)

```mermaid
graph TD
    ROOT[根目录]
    ROOT --> SRC[src/]
    ROOT --> TESTS[tests/]
    ROOT --> CONFIG[配置文件]

    SRC --> COMPONENTS[components/]
    SRC --> UTILS[utils/]
    SRC --> SERVICES[services/]

    COMPONENTS --> COMP1[Component1]
    COMPONENTS --> COMP2[Component2]
```

### 2. 依赖关系图 (graph LR)

```mermaid
graph LR
    A[入口文件] --> B[模块A]
    A --> C[模块B]
    B --> D[工具函数]
    C --> D
    C --> E[外部库]
```

### 3. 文件夹层级图

```mermaid
graph TD
    ROOT["📁 /"]
    ROOT --> SRC["📁 src/"]
    ROOT --> DOCS["📁 docs/"]
    ROOT --> CONFIG["📄 配置文件"]

    SRC --> COMPONENTS["📁 components/"]
    SRC --> HOOKS["📁 hooks/"]
    SRC --> UTILS["📁 utils/"]

    COMPONENTS --> BUTTON["📄 Button.tsx"]
    COMPONENTS --> MODAL["📄 Modal.tsx"]
```

## 进阶图结构

### 4. 带颜色的模块分组

```mermaid
graph TD
    subgraph Frontend["前端模块"]
        A[React App] --> B[Components]
        A --> C[Hooks]
        A --> D[Context]
    end

    subgraph Backend["后端模块"]
        E[API Server] --> F[Controllers]
        E --> G[Services]
        E --> H[Models]
    end

    A -->|HTTP| E
```

### 5. 依赖深度分析

```mermaid
graph TD
    L1[Level 1: 核心模块] --> L2[Level 2: 业务模块]
    L2 --> L3[Level 3: 工具模块]
    L3 --> L4[Level 4: 基础库]

    L1 -->|高频依赖| L3
    L2 -->|中频依赖| L3
    L3 -->|低频依赖| L4
```

## 特殊符号转义

Mermaid 中特殊字符需要转义：

| 特殊字符 | 转义写法 |
|---------|---------|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `"` | `&quot;` |
| `.` | 无需转义 |
| `#` | 无需转义 |
| 空格 | 使用 `[ ]` 包裹文本 |
