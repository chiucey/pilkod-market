# LangGraph 核心概念详解

## 图结构基础

LangGraph 的核心是一个有向图（Directed Graph），由以下元素组成：

### 节点（Node）

节点是图中的基本执行单元，每个节点代表：
- 一个 LLM 调用
- 一个工具执行
- 一个状态转换
- 任意 Python 函数

```python
def my_node(state: AgentState) -> AgentState:
    """
    节点函数签名：
    - 输入：当前状态
    - 输出：更新后的状态
    """
    return {"result": "processed"}
```

### 边（Edge）

边定义了节点间的连接关系：

1. **普通边** - 无条件转移
2. **条件边** - 基于状态条件转移

```python
# 普通边
graph.add_edge("node_a", "node_b")

# 条件边
graph.add_conditional_edges(
    "router",
    lambda state: "path_a" if state["condition"] else "path_b",
    {
        "path_a": "node_a",
        "path_b": "node_b"
    }
)
```

## 状态管理

### 类型化状态

使用 TypeDict 或 Pydantic 定义状态：

```python
from typing import TypedDict
from pydantic import BaseModel, Field

# TypeDict 方式
class AgentState(TypedDict):
    messages: list
    context: dict

# Pydantic 方式（推荐）
class AgentState(BaseModel):
    messages: list = Field(default_factory=list)
    context: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
```

### 状态更新函数

```python
def update_state(state: AgentState, update: dict) -> AgentState:
    """状态更新必须返回完整状态"""
    return {**state, **update}
```

## 执行模型

### 同步执行

```python
result = graph.invoke({"input": "data"})
```

### 异步执行

```python
result = await graph.ainvoke({"input": "data"})
```

### 流式执行

```python
for chunk in graph.stream({"input": "data"}):
    print(chunk)
```
