"""
连锁茶饮企业多部门联动协作Agent系统
Tea Enterprise Multi-Department Collaboration Agent System

该模块实现了连锁茶饮企业的多Agent协作系统，包括：
- CEO协调Agent（主控中心）
- 运营部Agent
- 供应链部Agent
- 市场营销部Agent
- 产品研发部Agent
- 人力资源部Agent
- 财务部Agent
- 客服部Agent
- 数据分析部Agent

Author: MiniMax Agent
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class TaskType(Enum):
    """任务类型枚举"""
    NEW_PRODUCT_LAUNCH = "新品上市"
    MARKETING_CAMPAIGN = "营销活动"
    COST_OPTIMIZATION = "成本优化"
    STAFFING_EXPANSION = "人员扩张"
    CRISIS_MANAGEMENT = "危机处理"
    DAILY_OPERATION = "日常运营"
    STRATEGIC_PLANNING = "战略规划"
    CUSTOMER_SERVICE = "客户服务"
    DATA_ANALYSIS = "数据分析"
    GENERAL = "综合问题"


class Department(Enum):
    """部门枚举"""
    CEO = "CEO办公室"
    OPERATIONS = "运营部"
    SUPPLY_CHAIN = "供应链部"
    MARKETING = "市场营销部"
    RND = "产品研发部"
    HR = "人力资源部"
    FINANCE = "财务部"
    CUSTOMER_SERVICE = "客服部"
    DATA_ANALYTICS = "数据分析部"


@dataclass
class Task:
    """任务数据类"""
    task_id: str
    task_type: TaskType
    description: str
    requesting_dept: Department
    lead_dept: Department
    collaborating_depts: List[Department] = field(default_factory=list)
    priority: int = 1  # 1-5, 1为最高优先级
    deadline: Optional[str] = None
    status: str = "pending"
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResponse:
    """Agent响应数据类"""
    agent_id: str
    department: Department
    response_type: str  # "opinion", "support", "decision", "data"
    content: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = 0.9


class BaseAgent(ABC):
    """Agent基类"""

    def __init__(self, department: Department, agent_id: str):
        self.department = department
        self.agent_id = agent_id
        self.task_history: List[Task] = []
        self.knowledge_base: Dict[str, Any] = {}

    @abstractmethod
    def process_task(self, task: Task) -> AgentResponse:
        """处理任务的核心方法"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """获取Agent能力列表"""
        pass

    def can_handle_task(self, task: Task) -> bool:
        """判断是否能处理该任务"""
        return True

    def collaborate(self, other_agent: 'BaseAgent', request: Dict) -> Dict:
        """与其他Agent协作"""
        return {
            "from": self.department.value,
            "to": other_agent.department.value,
            "request": request,
            "status": "forwarded"
        }


class CEOAgent(BaseAgent):
    """
    CEO协调Agent - 主控中心
    负责任务分配、部门协调、结果整合
    """

    def __init__(self):
        super().__init__(Department.CEO, "ceo-main")
        self.agents_registry: Dict[Department, BaseAgent] = {}
        self.pending_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []

    def register_agent(self, department: Department, agent: BaseAgent):
        """注册部门Agent"""
        self.agents_registry[department] = agent

    def process_task(self, task: Task) -> AgentResponse:
        """CEO处理任务 - 分析并分配"""
        # 任务分析
        task_analysis = self._analyze_task(task)

        # 分配主导和协作部门
        lead_dept = self._determine_lead_department(task)
        collaborating_depts = self._determine_collaborating_departments(task)

        task.lead_dept = lead_dept
        task.collaborating_depts = collaborating_depts
        task.status = "assigned"

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="task_assignment",
            content={
                "task_analysis": task_analysis,
                "lead_department": lead_dept.value,
                "collaborating_departments": [d.value for d in collaborating_depts],
                "recommended_actions": self._generate_action_plan(task)
            }
        )

    def _analyze_task(self, task: Task) -> Dict:
        """分析任务类型和复杂度"""
        keywords = {
            TaskType.NEW_PRODUCT_LAUNCH: ["新品", "研发", "推出", "上市"],
            TaskType.MARKETING_CAMPAIGN: ["营销", "推广", "活动", "宣传"],
            TaskType.COST_OPTIMIZATION: ["成本", "预算", "优化", "节约"],
            TaskType.STAFFING_EXPANSION: ["招聘", "人员", "扩张", "团队"],
            TaskType.CRISIS_MANAGEMENT: ["危机", "紧急", "问题", "投诉"],
            TaskType.STRATEGIC_PLANNING: ["战略", "规划", "长期", "目标"]
        }

        matched_types = []
        for task_type, kw_list in keywords.items():
            if any(kw in task.description for kw in kw_list):
                matched_types.append(task_type.value)

        return {
            "detected_types": matched_types,
            "complexity": "high" if len(matched_types) > 2 else "medium" if matched_types else "low",
            "requires_cross_department": len(matched_types) > 1 or task.task_type in [
                TaskType.NEW_PRODUCT_LAUNCH,
                TaskType.MARKETING_CAMPAIGN,
                TaskType.CRISIS_MANAGEMENT
            ]
        }

    def _determine_lead_department(self, task: Task) -> Department:
        """确定主导部门"""
        task_lead_mapping = {
            TaskType.NEW_PRODUCT_LAUNCH: Department.RND,
            TaskType.MARKETING_CAMPAIGN: Department.MARKETING,
            TaskType.COST_OPTIMIZATION: Department.SUPPLY_CHAIN,
            TaskType.STAFFING_EXPANSION: Department.HR,
            TaskType.CRISIS_MANAGEMENT: Department.CEO,
            TaskType.DAILY_OPERATION: Department.OPERATIONS,
            TaskType.STRATEGIC_PLANNING: Department.CEO,
            TaskType.CUSTOMER_SERVICE: Department.CUSTOMER_SERVICE,
            TaskType.DATA_ANALYSIS: Department.DATA_ANALYTICS,
            TaskType.GENERAL: Department.CEO
        }
        return task_lead_mapping.get(task.task_type, Department.CEO)

    def _determine_collaborating_departments(self, task: Task) -> List[Department]:
        """确定协作部门"""
        collaboration_map = {
            TaskType.NEW_PRODUCT_LAUNCH: [
                Department.OPERATIONS, Department.SUPPLY_CHAIN,
                Department.MARKETING, Department.FINANCE
            ],
            TaskType.MARKETING_CAMPAIGN: [
                Department.OPERATIONS, Department.CUSTOMER_SERVICE,
                Department.DATA_ANALYTICS, Department.FINANCE
            ],
            TaskType.COST_OPTIMIZATION: [
                Department.FINANCE, Department.OPERATIONS,
                Department.DATA_ANALYTICS
            ],
            TaskType.STAFFING_EXPANSION: [
                Department.OPERATIONS, Department.FINANCE, Department.RND
            ],
            TaskType.CRISIS_MANAGEMENT: [
                Department.OPERATIONS, Department.CUSTOMER_SERVICE,
                Department.MARKETING, Department.FINANCE
            ],
            TaskType.STRATEGIC_PLANNING: [
                Department.FINANCE, Department.DATA_ANALYTICS,
                Department.MARKETING, Department.OPERATIONS
            ]
        }
        return collaboration_map.get(task.task_type, [])

    def _generate_action_plan(self, task: Task) -> List[str]:
        """生成行动方案"""
        return [
            f"1. {task.lead_dept.value}主导处理核心问题",
            f"2. 各协作部门在24小时内反馈意见",
            "3. CEO办公室整合各部门意见",
            "4. 生成最终执行方案"
        ]

    def coordinate_collaboration(self, task: Task) -> Dict[str, AgentResponse]:
        """协调跨部门协作"""
        responses = {}

        # 通知主导部门
        lead_agent = self.agents_registry.get(task.lead_dept)
        if lead_agent:
            responses[task.lead_dept] = lead_agent.process_task(task)

        # 通知协作部门
        for dept in task.collaborating_depts:
            agent = self.agents_registry.get(dept)
            if agent:
                responses[dept] = agent.process_task(task)

        return responses

    def integrate_responses(self, responses: Dict[Department, AgentResponse]) -> Dict:
        """整合各Agent响应"""
        integrated = {
            "summary": "综合各部门意见",
            "departments_input": {},
            "consensus": [],
            "action_items": [],
            "risks": [],
            "recommendations": []
        }

        for dept, response in responses.items():
            integrated["departments_input"][dept.value] = response.content

        # 识别共识点
        if len(responses) >= 2:
            integrated["consensus"].append("各部门已达成初步共识，需进一步细化执行方案")

        # 识别风险
        integrated["risks"].append("注意部门间资源协调")
        integrated["risks"].append("关注时间节点控制")

        return integrated

    def get_capabilities(self) -> List[str]:
        return [
            "任务分配与协调",
            "跨部门协作管理",
            "战略规划支持",
            "危机处理指挥",
            "资源整合优化"
        ]


class OperationsAgent(BaseAgent):
    """运营部Agent - 门店运营管理"""

    def __init__(self):
        super().__init__(Department.OPERATIONS, "ops-001")
        self.store_data = {
            "total_stores": 200,
            "stores_by_region": {"华东": 60, "华南": 50, "华北": 40, "西南": 30, "华中": 20},
            "avg_daily_customers_per_store": 300,
            "peak_hours": ["11:00-13:00", "17:00-19:00"]
        }

    def process_task(self, task: Task) -> AgentResponse:
        """处理运营相关任务"""
        if task.task_type == TaskType.NEW_PRODUCT_LAUNCH:
            content = self._handle_new_product_launch(task)
        elif task.task_type == TaskType.MARKETING_CAMPAIGN:
            content = self._handle_marketing_campaign(task)
        elif task.task_type == TaskType.CRISIS_MANAGEMENT:
            content = self._handle_crisis(task)
        else:
            content = self._handle_general_operations(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="operations_feedback",
            content=content
        )

    def _handle_new_product_launch(self, task: Task) -> Dict:
        """处理新品上市"""
        return {
            "store_readiness": {
                "estimated_stores_prepared": 200,
                "preparation_time_needed": "7-10天",
                "staff_training_required": True,
                "training_duration": "3天",
                "equipment_check": "需要检查200家门店的设备"
            },
            "inventory_requirements": {
                "cups_needed": "200万+",
                "ingredients_needed": "根据配方定",
                "packaging_materials": "已与供应链确认"
            },
            "implementation_steps": [
                "1. 接收总部培训材料",
                "2. 组织区域培训",
                "3. 门店设备检查",
                "4. 试运营测试",
                "5. 正式上线"
            ],
            "potential_issues": [
                "员工学习新配方需要时间",
                "高峰期可能影响出杯速度"
            ]
        }

    def _handle_marketing_campaign(self, task: Task) -> Dict:
        """处理营销活动"""
        return {
            "execution_capability": {
                "can_execute_in_all_stores": True,
                "stores_involved": 200,
                "execution_time": "活动开始前3天准备"
            },
            "point_of_sale_materials": [
                "海报(已确认数量)",
                "宣传单页",
                "收银系统更新"
            ],
            "customer_communication": {
                "in_store_announcement": True,
                "staff_briefing_required": True
            },
            "coordination_needed": [
                "市场部提供活动细则",
                "IT部门更新POS系统"
            ]
        }

    def _handle_crisis(self, task: Task) -> Dict:
        """处理危机事件"""
        return {
            "immediate_actions": [
                "启动门店应急响应",
                "收集现场情况",
                "安抚顾客",
                "上报总部"
            ],
            "coordination": {
                "need_customer_service": True,
                "need_marketing": True,
                "need_legal": True
            },
            "response_timeline": "30分钟内响应"
        }

    def _handle_general_operations(self, task: Task) -> Dict:
        """处理日常运营"""
        return {
            "task_received": task.description,
            "operational_impact": "中",
            "resource_requirements": "待评估",
            "timeline": "按需执行"
        }

    def get_capabilities(self) -> List[str]:
        return [
            "门店运营管理",
            "库存管理优化",
            "人员排班调度",
            "质量控制执行",
            "客户体验提升"
        ]


class SupplyChainAgent(BaseAgent):
    """供应链部Agent - 采购与物流管理"""

    def __init__(self):
        super().__init__(Department.SUPPLY_CHAIN, "supply-001")
        self.suppliers = {
            "茶叶": ["福建茶园A", "云南茶园B", "浙江茶园C"],
            "奶制品": ["蒙牛乳业", "伊利乳业", "光明乳业"],
            "糖浆": ["可口可乐糖浆", "国产优质糖浆"],
            "杯子包材": ["华东包材厂", "华南包材厂"]
        }

    def process_task(self, task: Task) -> AgentResponse:
        """处理供应链相关任务"""
        if task.task_type == TaskType.NEW_PRODUCT_LAUNCH:
            content = self._handle_new_product_supply(task)
        elif task.task_type == TaskType.COST_OPTIMIZATION:
            content = self._handle_cost_optimization(task)
        else:
            content = self._handle_general_supply(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="supply_chain_feedback",
            content=content
        )

    def _handle_new_product_supply(self, task: Task) -> Dict:
        """处理新品供应"""
        return {
            "supplier_capacity": {
                "can_meet_demand": True,
                "lead_time": "14-21天",
                "minimum_order_quantity": "按需求"
            },
            "cost_implications": {
                "estimated_material_cost": "待产品研发部确认配方",
                "supplier_quote_needed": True
            },
            "logistics": {
                "distribution_centers": 5,
                "can_deliver_to_all_stores": True,
                "delivery_frequency": "每周2-3次"
            },
            "quality_assurance": [
                "原料入库检验",
                "供应商资质审核",
                "存储条件监控"
            ],
            "risk_factors": [
                "季节性原料供应可能受影响",
                "进口原料有汇率风险"
            ]
        }

    def _handle_cost_optimization(self, task: Task) -> Dict:
        """处理成本优化"""
        return {
            "current_cost_structure": {
                "原料成本占比": "35%",
                "物流成本占比": "8%",
                "仓储成本占比": "5%"
            },
            "optimization_opportunities": [
                "批量采购议价",
                "物流路线优化",
                "仓储集中化",
                "供应商整合"
            ],
            "potential_savings": {
                "原料成本": "3-5%",
                "物流成本": "2-4%",
                "整体": "4-6%"
            },
            "implementation_timeline": "3-6个月",
            "risks": [
                "可能影响原料质量",
                "供应商关系维护"
            ]
        }

    def _handle_general_supply(self, task: Task) -> Dict:
        """处理一般供应链任务"""
        return {
            "supply_status": "正常",
            "inventory_level": "安全库存以上",
            "lead_time": "标准时间"
        }

    def get_capabilities(self) -> List[str]:
        return [
            "原材料采购管理",
            "供应商关系维护",
            "物流配送协调",
            "库存预警管理",
            "成本控制优化"
        ]


class MarketingAgent(BaseAgent):
    """市场营销部Agent - 品牌与推广"""

    def __init__(self):
        super().__init__(Department.MARKETING, "mkt-001")
        self.channels = ["微信公众号", "小红书", "抖音", "美团", "大众点评", "线下门店"]

    def process_task(self, task: Task) -> AgentResponse:
        """处理营销相关任务"""
        if task.task_type == TaskType.MARKETING_CAMPAIGN:
            content = self._handle_campaign(task)
        elif task.task_type == TaskType.NEW_PRODUCT_LAUNCH:
            content = self._handle_new_product_marketing(task)
        else:
            content = self._handle_general_marketing(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="marketing_feedback",
            content=content
        )

    def _handle_campaign(self, task: Task) -> Dict:
        """处理营销活动"""
        return {
            "campaign_plan": {
                "suggested_duration": "2-4周",
                "budget_range": "50-200万",
                "channels": self.channels,
                "key_messages": ["品质", "新鲜", "健康"]
            },
            "social_media_strategy": {
                "content_calendar": "提前2周准备",
                "influencer_collaboration": "可安排",
                "user_generated_content": "鼓励"
            },
            "promotional_materials": [
                "海报设计",
                "视频素材",
                "文案内容",
                "社交媒体素材"
            ],
            "expected_outcomes": {
                "sales_increase": "15-25%",
                "new_customers": "10,000+",
                "engagement_rate": "3-5%"
            },
            "coordination_requirements": [
                "运营部配合执行",
                "客服部准备FAQ",
                "数据分析部监控效果"
            ]
        }

    def _handle_new_product_marketing(self, task: Task) -> Dict:
        """处理新品营销"""
        return {
            "launch_strategy": {
                "phased_rollout": True,
                "initial_region": "华东地区",
                "full_launch": "2周后全国"
            },
            "marketing_channels": {
                "online": ["抖音", "小红书", "微信"],
                "offline": ["门店", "户外广告"]
            },
            "key_messages": [
                "季节限定",
                "精选原料",
                "匠心工艺"
            ],
            "timeline": {
                "teaser_phase": "上市前1周",
                "launch_phase": "上市当周",
                "sustain_phase": "上市后2周"
            }
        }

    def _handle_general_marketing(self, task: Task) -> Dict:
        """处理一般营销任务"""
        return {
            "marketing_plan": "根据任务需求制定",
            "timeline": "待确认",
            "budget": "待财务部审批"
        }

    def get_capabilities(self) -> List[str]:
        return [
            "品牌推广策略制定",
            "活动策划执行",
            "社交媒体运营",
            "客户关系管理",
            "市场份额分析"
        ]


class RNDAgent(BaseAgent):
    """产品研发部Agent - 新品研发"""

    def __init__(self):
        super().__init__(Department.RND, "rnd-001")
        self.current_products = ["经典奶茶", "水果茶", "芝士茶", "冷萃茶"]

    def process_task(self, task: Task) -> AgentResponse:
        """处理研发相关任务"""
        if task.task_type == TaskType.NEW_PRODUCT_LAUNCH:
            content = self._handle_new_product_dev(task)
        else:
            content = self._handle_general_rd(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="rd_feedback",
            content=content
        )

    def _handle_new_product_dev(self, task: Task) -> Dict:
        """处理新品研发"""
        return {
            "development_status": {
                "current_stage": "配方确定阶段",
                "estimated_completion": "2-3周",
                "testing_required": True
            },
            "recipe_specifications": {
                "base_ingredients": ["茶叶", "奶", "糖"],
                "unique_selling_points": ["季节限定", "健康配方"],
                "shelf_life": "4小时(现制)"
            },
            "quality_standards": [
                "口感一致性",
                "外观标准",
                "操作流程标准化"
            ],
            "cost_implications": {
                "material_cost_per_cup": "待测算",
                "pricing_recommendation": "待财务部分析"
            },
            "collaboration_needed": [
                "供应链部确认原料供应",
                "运营部确认操作可行性",
                "市场部确认定位"
            ]
        }

    def _handle_general_rd(self, task: Task) -> Dict:
        """处理一般研发任务"""
        return {
            "rd_project_status": "进行中",
            "timeline": "待确认",
            "resource_requirements": ["研发人员", "实验室", "测试原料"]
        }

    def get_capabilities(self) -> List[str]:
        return [
            "新品研发测试",
            "配方优化改进",
            "季节性产品规划",
            "竞品分析",
            "品质标准制定"
        ]


class HRAgent(BaseAgent):
    """人力资源部Agent"""

    def __init__(self):
        super().__init__(Department.HR, "hr-001")
        self.current_headcount = 3000

    def process_task(self, task: Task) -> AgentResponse:
        """处理人力资源任务"""
        if task.task_type == TaskType.STAFFING_EXPANSION:
            content = self._handle_staffing(task)
        else:
            content = self._handle_general_hr(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="hr_feedback",
            content=content
        )

    def _handle_staffing(self, task: Task) -> Dict:
        """处理人员扩张"""
        return {
            "recruitment_plan": {
                "positions_needed": ["店长", "调茶师", "值班主管"],
                "total_headcount_needed": "待各部门确认",
                "timeline": "提前1-2个月启动"
            },
            "training_program": {
                "basic_training": "1周",
                "on_job_training": "2周",
                "certification_required": True
            },
            "cost_implications": {
                "recruitment_cost_per_person": "500-1000元",
                "training_cost_per_person": "2000-3000元"
            },
            "challenges": [
                "招聘竞争激烈",
                "培训周期较长",
                "人员留存率"
            ]
        }

    def _handle_general_hr(self, task: Task) -> Dict:
        """处理一般HR任务"""
        return {
            "hr_initiative": "根据任务需求",
            "timeline": "待确认",
            "stakeholders": ["各部门负责人", "门店店长"]
        }

    def get_capabilities(self) -> List[str]:
        return [
            "招聘与培训管理",
            "员工绩效评估",
            "薪酬福利设计",
            "企业文化建设",
            "劳动法规合规"
        ]


class FinanceAgent(BaseAgent):
    """财务部Agent"""

    def __init__(self):
        super().__init__(Department.FINANCE, "fin-001")

    def process_task(self, task: Task) -> AgentResponse:
        """处理财务任务"""
        if task.task_type == TaskType.COST_OPTIMIZATION:
            content = self._handle_cost_analysis(task)
        elif task.task_type == TaskType.NEW_PRODUCT_LAUNCH:
            content = self._handle_new_product_finance(task)
        else:
            content = self._handle_general_finance(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="finance_feedback",
            content=content
        )

    def _handle_cost_analysis(self, task: Task) -> Dict:
        """处理成本分析"""
        return {
            "current_financial_status": {
                "revenue": "稳步增长",
                "cost_structure": "原料35%, 人工25%, 租金20%, 其他20%"
            },
            "optimization_recommendations": [
                "原料采购议价",
                "人工效率提升",
                "租金成本控制"
            ],
            "roi_analysis": "待具体方案"
        }

    def _handle_new_product_finance(self, task: Task) -> Dict:
        """处理新品财务分析"""
        return {
            "budget_requirements": {
                "marketing_budget": "待市场部确认",
                "training_budget": "待HR确认",
                "total_budget": "待汇总"
            },
            "cost_pricing": {
                "material_cost": "待研发部提供",
                "suggested_retail_price": "18-28元",
                "target_margin": "60%+"
            },
            "financial_metrics": {
                "payback_period": "预计3-6个月",
                "npv": "待测算"
            }
        }

    def _handle_general_finance(self, task: Task) -> Dict:
        """处理一般财务任务"""
        return {
            "financial_impact": "待分析",
            "budget_required": "待确认",
            "approval_required": True
        }

    def get_capabilities(self) -> List[str]:
        return [
            "预算管理控制",
            "成本核算分析",
            "财务报表编制",
            "投资决策支持",
            "风险管理审计"
        ]


class CustomerServiceAgent(BaseAgent):
    """客服部Agent"""

    def __init__(self):
        super().__init__(Department.CUSTOMER_SERVICE, "cs-001")

    def process_task(self, task: Task) -> AgentResponse:
        """处理客服任务"""
        if task.task_type == TaskType.CRISIS_MANAGEMENT:
            content = self._handle_crisis(task)
        else:
            content = self._handle_general_cs(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="customer_service_feedback",
            content=content
        )

    def _handle_crisis(self, task: Task) -> Dict:
        """处理危机"""
        return {
            "immediate_actions": [
                "记录客户反馈",
                "安抚客户情绪",
                "协调门店处理",
                "升级上报"
            ],
            "response_templates": {
                "complaint": "已收到您的反馈，我们非常重视...",
                "refund": "理解您的心情，我们将尽快处理..."
            }
        }

    def _handle_general_cs(self, task: Task) -> Dict:
        """处理一般客服任务"""
        return {
            "customer_impact": "需要评估",
            "communication_plan": "待制定",
            "follow_up_required": True
        }

    def get_capabilities(self) -> List[str]:
        return [
            "客户咨询响应",
            "投诉处理跟进",
            "满意度追踪",
            "服务质量监督",
            "反馈分析"
        ]


class DataAnalyticsAgent(BaseAgent):
    """数据分析部Agent"""

    def __init__(self):
        super().__init__(Department.DATA_ANALYTICS, "data-001")

    def process_task(self, task: Task) -> AgentResponse:
        """处理数据分析任务"""
        content = self._handle_analysis_request(task)

        return AgentResponse(
            agent_id=self.agent_id,
            department=self.department,
            response_type="data_analytics_feedback",
            content=content
        )

    def _handle_analysis_request(self, task: Task) -> Dict:
        """处理分析请求"""
        return {
            "data_availability": {
                "sales_data": True,
                "customer_data": True,
                "inventory_data": True,
                "feedback_data": True
            },
            "analysis_capabilities": [
                "趋势分析",
                "预测模型",
                "关联分析",
                "异常检测"
            ],
            "delivery_timeline": {
                "preliminary_report": "1-2天",
                "detailed_analysis": "3-5天",
                "dashboard_update": "1周"
            },
            "key_metrics_to_track": [
                "销售额",
                "客单价",
                "复购率",
                "客户满意度"
            ]
        }

    def get_capabilities(self) -> List[str]:
        return [
            "经营数据分析",
            "市场趋势研究",
            "预测模型构建",
            "KPI监控",
            "数据驱动决策"
        ]


class TeaEnterpriseCollaborationSystem:
    """茶饮企业协作系统 - 主系统类"""

    def __init__(self):
        # 初始化所有Agent
        self.ceo = CEOAgent()
        self.operations = OperationsAgent()
        self.supply_chain = SupplyChainAgent()
        self.marketing = MarketingAgent()
        self.rnd = RNDAgent()
        self.hr = HRAgent()
        self.finance = FinanceAgent()
        self.customer_service = CustomerServiceAgent()
        self.data_analytics = DataAnalyticsAgent()

        # 注册所有Agent到CEO
        self.ceo.register_agent(Department.OPERATIONS, self.operations)
        self.ceo.register_agent(Department.SUPPLY_CHAIN, self.supply_chain)
        self.ceo.register_agent(Department.MARKETING, self.marketing)
        self.ceo.register_agent(Department.RND, self.rnd)
        self.ceo.register_agent(Department.HR, self.hr)
        self.ceo.register_agent(Department.FINANCE, self.finance)
        self.ceo.register_agent(Department.CUSTOMER_SERVICE, self.customer_service)
        self.ceo.register_agent(Department.DATA_ANALYTICS, self.data_analytics)

        self.all_agents = {
            Department.CEO: self.ceo,
            Department.OPERATIONS: self.operations,
            Department.SUPPLY_CHAIN: self.supply_chain,
            Department.MARKETING: self.marketing,
            Department.RND: self.rnd,
            Department.HR: self.hr,
            Department.FINANCE: self.finance,
            Department.CUSTOMER_SERVICE: self.customer_service,
            Department.DATA_ANALYTICS: self.data_analytics
        }

    def process_user_request(self, user_input: str, task_type: Optional[TaskType] = None) -> Dict:
        """
        处理用户请求的主要入口

        Args:
            user_input: 用户输入描述
            task_type: 可选的任务类型

        Returns:
            综合协作结果
        """
        # 1. 创建任务
        task = self._create_task(user_input, task_type)

        # 2. CEO分析并分配任务
        ceo_response = self.ceo.process_task(task)

        # 3. 协调跨部门协作
        department_responses = self.ceo.coordinate_collaboration(task)

        # 4. 整合各Agent响应
        integrated_result = self.ceo.integrate_responses(department_responses)

        # 5. 生成最终报告
        final_report = self._generate_report(task, ceo_response, department_responses, integrated_result)

        return final_report

    def _create_task(self, description: str, task_type: Optional[TaskType] = None) -> Task:
        """创建任务"""
        if task_type is None:
            task_type = self._infer_task_type(description)

        return Task(
            task_id=f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_type=task_type,
            description=description,
            requesting_dept=Department.CEO,
            lead_dept=Department.CEO,
            collaborating_depts=[]
        )

    def _infer_task_type(self, description: str) -> TaskType:
        """从描述推断任务类型"""
        keywords_map = {
            "新品": TaskType.NEW_PRODUCT_LAUNCH,
            "研发": TaskType.NEW_PRODUCT_LAUNCH,
            "营销": TaskType.MARKETING_CAMPAIGN,
            "推广": TaskType.MARKETING_CAMPAIGN,
            "成本": TaskType.COST_OPTIMIZATION,
            "预算": TaskType.COST_OPTIMIZATION,
            "招聘": TaskType.STAFFING_EXPANSION,
            "人员": TaskType.STAFFING_EXPANSION,
            "危机": TaskType.CRISIS_MANAGEMENT,
            "紧急": TaskType.CRISIS_MANAGEMENT,
            "战略": TaskType.STRATEGIC_PLANNING,
            "规划": TaskType.STRATEGIC_PLANNING,
            "分析": TaskType.DATA_ANALYSIS,
            "数据": TaskType.DATA_ANALYSIS
        }

        for keyword, task_type in keywords_map.items():
            if keyword in description:
                return task_type

        return TaskType.GENERAL

    def _generate_report(self, task: Task, ceo_response: AgentResponse,
                        department_responses: Dict[Department, AgentResponse],
                        integrated_result: Dict) -> Dict:
        """生成最终报告"""
        return {
            "report_header": {
                "task_id": task.task_id,
                "generated_at": datetime.now().isoformat(),
                "system": "连锁茶饮企业多部门联动协作系统"
            },
            "task_overview": {
                "description": task.description,
                "inferred_type": task.task_type.value,
                "status": task.status
            },
            "ceo_analysis": ceo_response.content,
            "department_contributions": {
                dept.value: response.content
                for dept, response in department_responses.items()
            },
            "integrated_solution": integrated_result,
            "next_steps": [
                "各部门按分工执行",
                "定期汇报进展",
                "必要时召开协调会议"
            ]
        }

    def get_department_status(self, department: Department) -> Dict:
        """获取部门状态"""
        agent = self.all_agents.get(department)
        if agent:
            return {
                "department": department.value,
                "agent_id": agent.agent_id,
                "capabilities": agent.get_capabilities(),
                "status": "active"
            }
        return {"status": "not_found"}

    def list_all_capabilities(self) -> Dict:
        """列出所有Agent的能力"""
        return {
            dept.value: agent.get_capabilities()
            for dept, agent in self.all_agents.items()
        }


# 使用示例和测试
if __name__ == "__main__":
    # 初始化系统
    system = TeaEnterpriseCollaborationSystem()

    # 示例1: 新品上市协作
    print("=" * 60)
    print("示例1: 新品上市多部门协作")
    print("=" * 60)
    result1 = system.process_user_request(
        "我们计划下个月推出春季新品茶饮，需要各部门配合准备"
    )
    print(f"任务类型: {result1['task_overview']['inferred_type']}")
    print(f"主导部门: {result1['ceo_analysis']['lead_department']}")
    print(f"协作部门: {result1['ceo_analysis']['collaborating_departments']}")

    # 示例2: 营销活动协作
    print("\n" + "=" * 60)
    print("示例2: 营销活动多部门协作")
    print("=" * 60)
    result2 = system.process_user_request(
        "我们计划在五一假期进行促销活动，需要各部门配合"
    )
    print(f"任务类型: {result2['task_overview']['inferred_type']}")
    print(f"主导部门: {result2['ceo_analysis']['lead_department']}")

    # 示例3: 成本优化协作
    print("\n" + "=" * 60)
    print("示例3: 成本优化多部门协作")
    print("=" * 60)
    result3 = system.process_user_request(
        "公司要求降低运营成本10%，需要各部门提出优化方案"
    )
    print(f"任务类型: {result3['task_overview']['inferred_type']}")
    print(f"主导部门: {result3['ceo_analysis']['lead_department']}")

    # 示例4: 列出所有能力
    print("\n" + "=" * 60)
    print("示例4: 各部门能力列表")
    print("=" * 60)
    capabilities = system.list_all_capabilities()
    for dept, caps in capabilities.items():
        print(f"\n{dept}:")
        for cap in caps:
            print(f"  - {cap}")
