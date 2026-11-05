# 连锁茶饮企业多部门联动协作Agent系统

## 概述

这是一个专为连锁茶饮企业设计的多智能体（Multi-Agent）协作系统。系统模拟真实企业架构，包含9个专业化部门Agent，通过智能协作机制实现跨部门联动，解决复杂的商业问题。

### 核心特点

- **多Agent协作**：9个专业化部门Agent，各司其职
- **智能任务分配**：自动识别任务类型，分配主导和协作部门
- **协调机制**：完整的跨部门协作流程和冲突解决机制
- **综合报告**：整合各部门意见，生成可执行方案

## 系统架构

```
                    ┌─────────────────┐
                    │   CEO Agent     │
                    │   (主协调者)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────┴────┐         ┌────┴────┐          ┌────┴────┐
   │ 运营部  │         │ 供应链部 │          │ 市场部  │
   └────┬────┘         └────┬────┘          └────┬────┘
        │                    │                    │
   ┌────┴────┐         ┌────┴────┐          ┌────┴────┐
   │ 产品研发 │         │ 人力资源 │          │ 财务部  │
   └────┬────┘         └────┬────┘          └────┬────┘
        │                    │                    │
                    ┌────────┴────────┐
                    │   客服部 Agent  │
                    │   数据分析部    │
                    └─────────────────┘
```

## 快速开始

### 基本用法

```python
from agent_system import TeaEnterpriseCollaborationSystem

# 初始化系统
system = TeaEnterpriseCollaborationSystem()

# 处理用户请求
result = system.process_user_request("我们计划推出新品，需要各部门配合")

# 查看结果
print(result['task_overview']['inferred_type'])  # 任务类型
print(result['ceo_analysis']['lead_department'])  # 主导部门
print(result['ceo_analysis']['collaborating_departments'])  # 协作部门
```

### 查看所有能力

```python
# 列出所有部门能力
capabilities = system.list_all_capabilities()
for dept, caps in capabilities.items():
    print(f"{dept}: {caps}")
```

## 任务类型

| 任务类型 | 描述 | 主导部门 |
|---------|------|---------|
| `NEW_PRODUCT_LAUNCH` | 新品研发上市 | 产品研发部 |
| `MARKETING_CAMPAIGN` | 营销活动策划执行 | 市场营销部 |
| `COST_OPTIMIZATION` | 成本优化控制 | 供应链部 |
| `STAFFING_EXPANSION` | 人员招聘扩张 | 人力资源部 |
| `CRISIS_MANAGEMENT` | 危机事件处理 | CEO办公室 |
| `STRATEGIC_PLANNING` | 战略规划制定 | CEO办公室 |
| `DAILY_OPERATION` | 日常运营管理 | 运营部 |
| `CUSTOMER_SERVICE` | 客户服务支持 | 客服部 |
| `DATA_ANALYSIS` | 数据分析报告 | 数据分析部 |

## API参考

### TeaEnterpriseCollaborationSystem

主系统类，管理所有Agent和协作流程。

#### 方法

##### `process_user_request(user_input: str, task_type: TaskType = None) -> Dict`

处理用户请求并协调多部门协作。

**参数：**
- `user_input` (str): 用户请求描述
- `task_type` (TaskType, 可选): 指定任务类型

**返回：**
- `Dict`: 包含任务分析、各部门响应和综合方案的字典

**示例：**
```python
result = system.process_user_request(
    "公司计划推出春季新品茶饮",
    task_type=TaskType.NEW_PRODUCT_LAUNCH
)
```

##### `get_department_status(department: Department) -> Dict`

获取特定部门状态和能力。

**参数：**
- `department` (Department): 部门枚举

**返回：**
- `Dict`: 部门状态信息

##### `list_all_capabilities() -> Dict`

列出所有Agent的能力。

**返回：**
- `Dict`: 部门及其能力的映射

### TaskType 枚举

定义系统支持的任务类型：

```python
from agent_system import TaskType

TaskType.NEW_PRODUCT_LAUNCH    # 新品上市
TaskType.MARKETING_CAMPAIGN    # 营销活动
TaskType.COST_OPTIMIZATION     # 成本优化
TaskType.STAFFING_EXPANSION    # 人员扩张
TaskType.CRISIS_MANAGEMENT     # 危机处理
TaskType.DAILY_OPERATION       # 日常运营
TaskType.STRATEGIC_PLANNING   # 战略规划
TaskType.CUSTOMER_SERVICE     # 客户服务
TaskType.DATA_ANALYSIS        # 数据分析
TaskType.GENERAL              # 综合问题
```

### Department 枚举

定义系统中的部门：

```python
from agent_system import Department

Department.CEO               # CEO办公室
Department.OPERATIONS        # 运营部
Department.SUPPLY_CHAIN     # 供应链部
Department.MARKETING         # 市场营销部
Department.RND               # 产品研发部
Department.HR                # 人力资源部
Department.FINANCE           # 财务部
Department.CUSTOMER_SERVICE # 客服部
Department.DATA_ANALYTICS   # 数据分析部
```

## 协作场景示例

### 场景1: 新品上市

```python
user_request = """
公司计划在4月推出三款春季新品：
- 茉莉花茶鲜奶茶
- 樱花乌龙茶
- 青梅绿茶

需要协调研发部确认配方，供应链部准备原料，
运营部进行门店准备，市场部制定推广策略，
财务部审批预算。
"""

result = system.process_user_request(user_request)
```

**自动识别：**
- 任务类型：新品上市
- 主导部门：产品研发部
- 协作部门：运营部、供应链部、市场营销部、财务部

### 场景2: 营销活动

```python
user_request = """
五一假期计划推出会员专享促销活动：
- 全场饮品第二杯半价
- 会员积分翻倍
- 邀请好友得优惠券

需要市场部策划活动细则，运营部执行推广，
客服部准备FAQ，数据分析部监控效果。
"""

result = system.process_user_request(user_request)
```

### 场景3: 成本优化

```python
user_request = """
公司要求降低运营成本15%，重点优化：
- 原材料采购成本
- 物流配送效率
- 门店人力成本

供应链部负责采购议价，财务部分析成本结构，
运营部优化排班，数据分析部提供决策支持。
"""

result = system.process_user_request(user_request)
```

### 场景4: 危机处理

```python
user_request = """
【紧急】某门店发生食品安全投诉事件，
顾客在社交媒体发布负面信息。

需要CEO协调全部门联动处理：
- 运营部现场调查
- 客服部联系顾客
- 市场部舆情应对
- 财务部准备赔偿预算
"""

result = system.process_user_request(user_request)
```

## 输出格式

### 完整报告结构

```python
{
    "report_header": {
        "task_id": "task-20260321XXXXXX",
        "generated_at": "2026-03-21TXX:XX:XX",
        "system": "连锁茶饮企业多部门联动协作系统"
    },
    "task_overview": {
        "description": "用户请求描述",
        "inferred_type": "任务类型",
        "status": "任务状态"
    },
    "ceo_analysis": {
        "task_analysis": {...},
        "lead_department": "主导部门",
        "collaborating_departments": ["协作部门列表"],
        "recommended_actions": ["推荐行动"]
    },
    "department_contributions": {
        "部门名称": {部门响应内容},
        ...
    },
    "integrated_solution": {
        "summary": "综合摘要",
        "departments_input": {...},
        "consensus": ["共识点"],
        "action_items": ["行动项"],
        "risks": ["风险提示"],
        "recommendations": ["建议"]
    },
    "next_steps": ["后续步骤"]
}
```

## 运行示例

### 交互式演示

```bash
python examples.py
```

将展示8个完整的协作场景示例：

1. 新品上市全部门联动
2. 营销活动跨部门协作
3. 成本优化专项协作
4. 人员扩张招聘协作
5. 危机处理全部门联动
6. 系统能力查询
7. 引导式协作流程
8. 指定任务类型协作

### 单个示例测试

```python
from examples import example_1_new_product_launch

example_1_new_product_launch()
```

## 扩展系统

### 添加新部门Agent

```python
class NewDepartmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(Department.NEW_DEPT, "newdept-001")

    def process_task(self, task: Task) -> AgentResponse:
        return AgentResponse(...)

    def get_capabilities(self) -> List[str]:
        return ["能力1", "能力2"]

# 注册到系统
system = TeaEnterpriseCollaborationSystem()
system.ceo.register_agent(Department.NEW_DEPT, NewDepartmentAgent())
```

### 自定义协作规则

```python
# 在CEOAgent中修改 _determine_collaborating_departments 方法
# 添加新的协作映射规则
```

## 最佳实践

1. **明确任务描述**：提供清晰、具体的任务描述有助于准确识别任务类型
2. **指定任务类型**：对于复杂任务，建议显式指定`task_type`参数
3. **查看完整报告**：检查返回的完整报告以获取所有部门的详细意见
4. **关注协作要点**：注意报告中各部门的协调要点和风险提示

## 故障排除

### 问题：任务类型识别不准确

**解决方案**：显式指定`task_type`参数

```python
result = system.process_user_request(
    user_input,
    task_type=TaskType.NEW_PRODUCT_LAUNCH
)
```

### 问题：需要特定部门的详细分析

**解决方案**：直接调用特定Agent

```python
system.operations.process_task(task)
system.supply_chain.process_task(task)
```

## 版本历史

- **v1.0.0** (2026-03-21)
  - 初始版本发布
  - 9个部门Agent完整实现
  - 多Agent协作机制
  - 完整示例和文档

## 许可证

MIT License

## 作者

MiniMax Agent
