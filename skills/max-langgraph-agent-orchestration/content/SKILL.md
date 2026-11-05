---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 8aac7011842b394bf6a5da7f1cf8903b
    PropagateID: 8aac7011842b394bf6a5da7f1cf8903b
    ReservedCode1: 3046022100abaa1a8521e35411435ddea335033313054b437362cab91c3dbe4915b04e0652022100a052c14557bed377e44d51167433dd5aa71db7a6b756f34b40174f36d3abafbd
    ReservedCode2: 3046022100eaacf9c64310d22c732de676fc395c4375a04efbf2d795f7d85b08e8e7dd04a8022100c204c5ff0d03008ca69066ba2948df98ac07a88dcc8476245ac7d8348618746b
description: Max-LangGraph 多 Agent 编排框架技能。当用户要求使用 LangGraph 构建多 Agent 编排系统、设计复杂工作流、实现条件分支和并行执行、或构建工程咨询自动化工作流时使用。
name: max-langgraph-agent-orchestration
---

# Max-LangGraph 多 Agent 编排框架

本技能提供使用 LangGraph 构建工程化多 Agent 编排系统的完整指南，涵盖从基础概念到生产级实现的全流程。

## 核心概念

### 1. 什么是 LangGraph？

LangGraph 是基于有向图的多 Agent 编排框架，核心特点包括：

| 特性 | 说明 |
|------|------|
| **图结构** | 使用有向图定义 Agent 协作关系 |
| **节点** | 每个节点代表一个 Agent 或工具 |
| **边** | 定义节点间的执行流程和条件 |
| **状态管理** | 跨节点共享和传递状态 |
| **条件分支** | 支持基于状态的动态路由 |
| **并行执行** | 支持同步和异步节点执行 |

### 2. LangGraph vs LangChain Agents

```
LangChain Agents          LangGraph
├── 单链式执行           ├── 有向图结构
├── 简单工具调用         ├── 复杂协作关系
├── 线性流程            ├── 条件分支
└── 有限状态            └── 丰富状态机
```

## 工作流设计模式

### 模式一：顺序执行

最简单的编排模式，Agent 依次执行：

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class WorkflowState(TypedDict):
    input: str
    analysis: str
    output: str

def create_sequential_workflow():
    builder = StateGraph(WorkflowState)

    # 添加节点
    builder.add_node("input_handler", input_handler_node)
    builder.add_node("analyzer", analyzer_node)
    builder.add_node("output_generator", output_generator_node)

    # 定义顺序边
    builder.add_edge("input_handler", "analyzer")
    builder.add_edge("analyzer", "output_generator")
    builder.add_edge("output_generator", END)

    return builder.compile()
```

### 模式二：条件分支

基于状态动态选择执行路径：

```python
def create_conditional_workflow():
    builder = StateGraph(WorkflowState)

    builder.add_node("router", router_node)
    builder.add_node("path_a", path_a_node)
    builder.add_node("path_b", path_b_node)
    builder.add_node("merger", merger_node)

    builder.add_edge("router", "path_a", condition=lambda s: s["route"] == "A")
    builder.add_edge("router", "path_b", condition=lambda s: s["route"] == "B")
    builder.add_edge("path_a", "merger")
    builder.add_edge("path_b", "merger")
    builder.add_edge("merger", END)

    return builder.compile()
```

### 模式三：并行执行

多个 Agent 同时处理不同任务：

```python
from langgraph.graph import parallel

def create_parallel_workflow():
    builder = StateGraph(WorkflowState)

    builder.add_node("dispatcher", dispatcher_node)
    builder.add_node("task_1", task_1_node)
    builder.add_node("task_2", task_2_node)
    builder.add_node("task_3", task_3_node)
    builder.add_node("aggregator", aggregator_node)

    # 并行执行多个任务
    builder.add_edge(
        "dispatcher",
        parallel("task_1", "task_2", "task_3")
    )
    builder.add_edge(
        parallel("task_1", "task_2", "task_3"),
        "aggregator"
    )
    builder.add_edge("aggregator", END)

    return builder.compile()
```

## 工程咨询场景实现

### 场景：工程项目评审工作流

```python
"""
工程项目评审多 Agent 系统
├── 需求分析 Agent - 分析项目需求
├── 成本估算 Agent - 计算工程成本
├── 风险评估 Agent - 识别风险因素
├── 合规检查 Agent - 验证合规性
└── 报告生成 Agent - 生成评审报告
"""

class ProjectReviewState(TypedDict):
    project_id: str
    requirements: dict
    cost_estimate: dict
    risk_assessment: dict
    compliance_result: dict
    final_report: str
    is_high_risk: bool

def build_project_review_graph():
    workflow = StateGraph(ProjectReviewState)

    # 节点定义
    workflow.add_node("requirement_analyzer", analyze_requirements)
    workflow.add_node("cost_estimator", estimate_costs)
    workflow.add_node("risk_assessor", assess_risks)
    workflow.add_node("compliance_checker", check_compliance)
    workflow.add_node("report_generator", generate_report)

    # 并行执行成本、风险和合规检查
    workflow.add_edge("requirement_analyzer", parallel(
        "cost_estimator",
        "risk_assessor",
        "compliance_checker"
    ))

    # 条件分支：基于风险等级
    workflow.add_conditional_edges(
        "risk_assessor",
        lambda s: "enhanced_review" if s["is_high_risk"] else "standard_review",
        {
            "enhanced_review": "enhanced_audit",
            "standard_review": "report_generator"
        }
    )

    workflow.add_node("enhanced_audit", enhanced_audit_node)
    workflow.add_edge("enhanced_audit", "report_generator")
    workflow.add_edge("report_generator", END)

    return workflow.compile()
```

## 状态管理最佳实践

### 1. 状态结构设计

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """统一状态模型"""
    # 会话级别状态
    session_id: str
    user_id: str
    created_at: datetime

    # 工作流级别状态
    workflow_id: str
    current_step: str
    step_history: List[dict] = Field(default_factory=list)

    # 业务级别状态
    business_data: dict = Field(default_factory=dict)

    # 元数据
    metadata: dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
```

### 2. 状态更新模式

```python
def update_state_with_validation(
    current_state: AgentState,
    updates: dict,
    validators: dict
) -> AgentState:
    """带验证的状态更新"""
    for key, value in updates.items():
        if key in validators:
            if not validators[key](value):
                raise ValueError(f"Validation failed for {key}")
        current_state.business_data[key] = value

    # 记录历史
    current_state.step_history.append({
        "step": current_state.current_step,
        "updates": updates,
        "timestamp": datetime.now().isoformat()
    })

    return current_state
```

## 错误处理与恢复

### 1. 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def resilient_agent_call(agent, input_data):
    """带指数退避的重试机制"""
    try:
        return await agent.ainvoke(input_data)
    except RateLimitError:
        raise
    except Exception as e:
        logging.error(f"Agent call failed: {e}")
        raise
```

### 2. 降级策略

```python
def create_fallback_workflow():
    """主流程失败时降级到简化流程"""
    builder = StateGraph(WorkflowState)

    builder.add_node("primary", primary_agent_node)
    builder.add_node("fallback", fallback_agent_node)
    builder.add_node("error_handler", error_handler_node)

    # 条件边：主流程失败时降级
    def route_on_success(state):
        if state.get("success"):
            return "primary"
        return "fallback"

    builder.add_conditional_edges(
        "initial",
        route_on_success,
        {
            "primary": "success_handler",
            "fallback": "fallback"
        }
    )

    return builder.compile()
```

## 监控与可观测性

### 1. 追踪执行流程

```python
from langgraph.callbacks import LangfuseCallbackHandler

def create_traced_workflow():
    """带分布式追踪的工作流"""
    workflow = StateGraph(WorkflowState)

    # 添加回调处理器
    callbacks = [
        LangfuseCallbackHandler(
            trace_id=session_id,
            metadata={"workflow": "project_review"}
        )
    ]

    # 所有节点共享追踪上下文
    workflow.add_node("analyzer", analyzer_node)
    workflow.add_edge("analyzer", END)

    return workflow.compile()
```

### 2. 性能指标

```python
class WorkflowMetrics:
    """工作流性能指标收集"""

    def __init__(self):
        self.step_durations: dict = {}
        self.error_counts: dict = {}
        self.retry_counts: dict = {}

    def record_step(self, step: str, duration: float, success: bool):
        self.step_durations[step] = duration
        if not success:
            self.error_counts[step] = self.error_counts.get(step, 0) + 1

    def get_metrics_summary(self) -> dict:
        return {
            "total_steps": len(self.step_durations),
            "avg_duration": np.mean(list(self.step_durations.values())),
            "error_rate": sum(self.error_counts.values()) /
                         max(1, sum(self.step_durations.values()))
        }
```

## 快速开始模板

### 基础模板

```python
# quick_start_template.py
"""
LangGraph 快速开始模板
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict
from pydantic import BaseModel

# 1. 定义状态
class AgentState(TypedDict):
    input: str
    intermediate_result: str
    output: str

# 2. 定义 Agent 函数
def agent_function(state: AgentState) -> AgentState:
    """Agent 实现"""
    return {"intermediate_result": f"Processed: {state['input']}"}

# 3. 构建图
def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_function)
    builder.add_edge("agent", END)
    return builder.compile()

# 4. 执行
if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({"input": "Hello LangGraph"})
    print(result)
```

## 参考资源

更多详细信息请参考：
- `references/langgraph-concepts.md` - 核心概念详解
- `references/workflow-patterns.md` - 工作流设计模式
- `references/engineering-consulting.md` - 工程咨询场景实现
- `scripts/` - 可复用脚本和工具
