"""
连锁茶饮企业多部门协作Agent系统 - 集成模板
Tea Enterprise Multi-Agent Collaboration System - Integration Templates

本文件提供常用的协作模板，方便快速构建特定场景的协作流程。

Author: MiniMax Agent
Version: 1.0.0
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from agent_system import (
    TeaEnterpriseCollaborationSystem,
    TaskType,
    Department,
    Task,
    AgentResponse
)


@dataclass
class CollaborationTemplate:
    """协作模板基类"""
    name: str
    description: str
    task_type: TaskType
    lead_department: Department
    collaborating_departments: List[Department]
    required_fields: List[str]


class TemplateRegistry:
    """模板注册器"""

    def __init__(self, system: TeaEnterpriseCollaborationSystem):
        self.system = system
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, CollaborationTemplate]:
        """加载所有预定义模板"""
        return {
            "新品上市": CollaborationTemplate(
                name="新品上市协作模板",
                description="适用于新品研发、上市准备、配方确认等场景",
                task_type=TaskType.NEW_PRODUCT_LAUNCH,
                lead_department=Department.RND,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.SUPPLY_CHAIN,
                    Department.MARKETING,
                    Department.FINANCE,
                    Department.DATA_ANALYTICS
                ],
                required_fields=["产品名称", "上市时间", "目标市场"]
            ),
            "营销活动": CollaborationTemplate(
                name="营销活动协作模板",
                description="适用于促销活动、品牌推广、活动策划等场景",
                task_type=TaskType.MARKETING_CAMPAIGN,
                lead_department=Department.MARKETING,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.CUSTOMER_SERVICE,
                    Department.DATA_ANALYTICS,
                    Department.FINANCE
                ],
                required_fields=["活动名称", "活动时间", "活动预算"]
            ),
            "成本优化": CollaborationTemplate(
                name="成本优化协作模板",
                description="适用于采购优化、效率提升、成本控制等场景",
                task_type=TaskType.COST_OPTIMIZATION,
                lead_department=Department.SUPPLY_CHAIN,
                collaborating_departments=[
                    Department.FINANCE,
                    Department.OPERATIONS,
                    Department.DATA_ANALYTICS
                ],
                required_fields=["优化目标", "预期节省比例", "影响范围"]
            ),
            "人员扩张": CollaborationTemplate(
                name="人员扩张协作模板",
                description="适用于招聘扩张、培训计划、人员配置等场景",
                task_type=TaskType.STAFFING_EXPANSION,
                lead_department=Department.HR,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.FINANCE,
                    Department.RND
                ],
                required_fields=["扩张规模", "岗位类型", "时间计划"]
            ),
            "危机处理": CollaborationTemplate(
                name="危机处理协作模板",
                description="适用于突发事件、舆情危机、质量问题等场景",
                task_type=TaskType.CRISIS_MANAGEMENT,
                lead_department=Department.CEO,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.CUSTOMER_SERVICE,
                    Department.MARKETING,
                    Department.FINANCE,
                    Department.DATA_ANALYTICS
                ],
                required_fields=["危机类型", "影响程度", "发生时间"]
            ),
            "战略规划": CollaborationTemplate(
                name="战略规划协作模板",
                description="适用于年度规划、业务拓展、投资决策等场景",
                task_type=TaskType.STRATEGIC_PLANNING,
                lead_department=Department.CEO,
                collaborating_departments=[
                    Department.FINANCE,
                    Department.DATA_ANALYTICS,
                    Department.MARKETING,
                    Department.OPERATIONS,
                    Department.RND
                ],
                required_fields=["规划周期", "战略目标", "关键指标"]
            ),
            "数据分析": CollaborationTemplate(
                name="数据分析协作模板",
                description="适用于经营分析、市场研究、效果评估等场景",
                task_type=TaskType.DATA_ANALYSIS,
                lead_department=Department.DATA_ANALYTICS,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.MARKETING,
                    Department.FINANCE
                ],
                required_fields=["分析目标", "数据范围", "报告用途"]
            ),
            "客户服务": CollaborationTemplate(
                name="客户服务协作模板",
                description="适用于投诉处理、服务优化、满意度提升等场景",
                task_type=TaskType.CUSTOMER_SERVICE,
                lead_department=Department.CUSTOMER_SERVICE,
                collaborating_departments=[
                    Department.OPERATIONS,
                    Department.MARKETING,
                    Department.DATA_ANALYTICS
                ],
                required_fields=["客户诉求", "问题类型", "期望结果"]
            )
        }

    def execute_with_template(
        self,
        template_name: str,
        context: Dict
    ) -> Dict:
        """使用模板执行协作"""
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"未找到模板: {template_name}")

        # 构建任务描述
        task_description = self._build_task_description(template, context)

        # 执行协作
        result = self.system.process_user_request(
            task_description,
            task_type=template.task_type
        )

        # 添加模板元数据
        result['template_info'] = {
            "template_name": template.name,
            "execution_time": "立即"
        }

        return result

    def _build_task_description(
        self,
        template: CollaborationTemplate,
        context: Dict
    ) -> str:
        """根据模板和上下文构建任务描述"""
        desc_parts = [template.description]

        for field in template.required_fields:
            if field in context:
                desc_parts.append(f"{field}: {context[field]}")

        return "\n".join(desc_parts)


class GuidedCollaboration:
    """引导式协作流程"""

    def __init__(self, system: TeaEnterpriseCollaborationSystem):
        self.system = system
        self.template_registry = TemplateRegistry(system)

    def step_1_identify_task(self, user_input: str) -> Dict:
        """步骤1: 识别任务"""
        result = self.system.process_user_request(user_input)
        return {
            "step": 1,
            "action": "任务识别",
            "inferred_type": result['task_overview']['inferred_type'],
            "confidence": "高",
            "suggestion": "请确认任务类型是否正确，或选择以下模板之一："
        }

    def step_2_select_template(self, task_type: str) -> Dict:
        """步骤2: 选择模板"""
        matching_templates = []
        for name, template in self.template_registry.templates.items():
            if template.task_type.value == task_type:
                matching_templates.append({
                    "name": name,
                    "description": template.description,
                    "required_fields": template.required_fields
                })

        return {
            "step": 2,
            "action": "选择模板",
            "available_templates": matching_templates
        }

    def step_3_provide_context(self, template_name: str) -> List[str]:
        """步骤3: 提供上下文"""
        template = self.template_registry.templates.get(template_name)
        if template:
            return template.required_fields
        return []

    def step_4_execute(self, template_name: str, context: Dict) -> Dict:
        """步骤4: 执行协作"""
        return self.template_registry.execute_with_template(template_name, context)


class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        pass

    def generate_executive_summary(
        self,
        collaboration_result: Dict
    ) -> str:
        """生成高管摘要"""
        lines = [
            "=" * 60,
            "【高管摘要报告】",
            "=" * 60,
            "",
            f"任务类型: {collaboration_result['task_overview']['inferred_type']}",
            f"任务ID: {collaboration_result['report_header']['task_id']}",
            f"生成时间: {collaboration_result['report_header']['generated_at']}",
            "",
            "-" * 60,
            "执行摘要:",
            "-" * 60,
        ]

        # 添加综合方案摘要
        if 'integrated_solution' in collaboration_result:
            solution = collaboration_result['integrated_solution']
            if 'summary' in solution:
                lines.append(solution['summary'])

        lines.extend(["", "-" * 60, "关键行动项:"])
        if 'next_steps' in collaboration_result:
            for i, step in enumerate(collaboration_result['next_steps'], 1):
                lines.append(f"  {i}. {step}")

        lines.extend(["", "-" * 60, "风险提示:"])
        if 'integrated_solution' in collaboration_result:
            for risk in collaboration_result['integrated_solution'].get('risks', []):
                lines.append(f"  ⚠️ {risk}")

        lines.extend(["", "=" * 60])
        return "\n".join(lines)

    def generate_department_brief(
        self,
        collaboration_result: Dict,
        department: str
    ) -> str:
        """生成部门简报"""
        if department not in collaboration_result['department_contributions']:
            return f"未找到部门 {department} 的贡献信息"

        content = collaboration_result['department_contributions'][department]
        lines = [
            "=" * 60,
            f"【{department} 简报】",
            "=" * 60,
            ""
        ]

        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, dict):
                    lines.append(f"\n{key}:")
                    for k, v in value.items():
                        lines.append(f"  • {k}: {v}")
                elif isinstance(value, list):
                    lines.append(f"\n{key}:")
                    for item in value:
                        lines.append(f"  • {item}")
                else:
                    lines.append(f"{key}: {value}")

        return "\n".join(lines)


class QuickStart:
    """快速启动助手"""

    @staticmethod
    def new_product_launch(
        product_name: str,
        launch_date: str,
        target_market: str
    ) -> Dict:
        """快速启动新品上市协作"""
        system = TeaEnterpriseCollaborationSystem()
        registry = TemplateRegistry(system)

        context = {
            "产品名称": product_name,
            "上市时间": launch_date,
            "目标市场": target_market
        }

        return registry.execute_with_template("新品上市", context)

    @staticmethod
    def marketing_campaign(
        campaign_name: str,
        campaign_date: str,
        budget: str
    ) -> Dict:
        """快速启动营销活动协作"""
        system = TeaEnterpriseCollaborationSystem()
        registry = TemplateRegistry(system)

        context = {
            "活动名称": campaign_name,
            "活动时间": campaign_date,
            "活动预算": budget
        }

        return registry.execute_with_template("营销活动", context)

    @staticmethod
    def cost_optimization(
        optimization_target: str,
        savings_ratio: str,
        scope: str
    ) -> Dict:
        """快速启动成本优化协作"""
        system = TeaEnterpriseCollaborationSystem()
        registry = TemplateRegistry(system)

        context = {
            "优化目标": optimization_target,
            "预期节省比例": savings_ratio,
            "影响范围": scope
        }

        return registry.execute_with_template("成本优化", context)


# 使用示例
if __name__ == "__main__":
    # 初始化
    system = TeaEnterpriseCollaborationSystem()

    # 示例1: 使用模板执行
    print("\n" + "=" * 60)
    print("示例1: 使用模板执行协作")
    print("=" * 60)

    registry = TemplateRegistry(system)
    result = registry.execute_with_template("新品上市", {
        "产品名称": "春季限定系列",
        "上市时间": "2026年4月1日",
        "目标市场": "华东地区"
    })

    print(f"任务类型: {result['task_overview']['inferred_type']}")
    print(f"模板: {result['template_info']['template_name']}")

    # 示例2: 使用快速启动
    print("\n" + "=" * 60)
    print("示例2: 使用快速启动助手")
    print("=" * 60)

    result = QuickStart.marketing_campaign(
        campaign_name="五一促销活动",
        campaign_date="2026年5月1日-5月5日",
        budget="100万"
    )

    print(f"任务类型: {result['task_overview']['inferred_type']}")
    print(f"主导部门: {result['ceo_analysis']['lead_department']}")

    # 示例3: 生成报告
    print("\n" + "=" * 60)
    print("示例3: 生成高管摘要报告")
    print("=" * 60)

    # 先执行一个协作
    system = TeaEnterpriseCollaborationSystem()
    result = system.process_user_request("公司计划推出春季新品")

    # 生成报告
    generator = ReportGenerator()
    executive_summary = generator.generate_executive_summary(result)
    print(executive_summary)
