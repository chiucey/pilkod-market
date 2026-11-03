"""
连锁茶饮企业多部门协作Agent系统 - 测试套件
Tea Enterprise Multi-Agent Collaboration System - Test Suite

Author: MiniMax Agent
Version: 1.0.0
"""

import unittest
from agent_system import (
    TeaEnterpriseCollaborationSystem,
    TaskType,
    Department,
    Task,
    AgentResponse,
    BaseAgent,
    CEOAgent,
    OperationsAgent,
    SupplyChainAgent,
    MarketingAgent,
    RNDAgent,
    HRAgent,
    FinanceAgent,
    CustomerServiceAgent,
    DataAnalyticsAgent
)


class TestAgentSystem(unittest.TestCase):
    """Agent系统测试"""

    def setUp(self):
        """测试前准备"""
        self.system = TeaEnterpriseCollaborationSystem()

    def test_system_initialization(self):
        """测试系统初始化"""
        self.assertIsNotNone(self.system.ceo)
        self.assertIsNotNone(self.system.operations)
        self.assertIsNotNone(self.system.supply_chain)
        self.assertIsNotNone(self.system.marketing)
        self.assertIsNotNone(self.system.rnd)
        self.assertIsNotNone(self.system.hr)
        self.assertIsNotNone(self.system.finance)
        self.assertIsNotNone(self.system.customer_service)
        self.assertIsNotNone(self.system.data_analytics)

    def test_agent_registration(self):
        """测试Agent注册"""
        ceo = self.system.ceo
        # CEO注册了8个子Agent（不包括自己）
        self.assertEqual(len(ceo.agents_registry), 8)
        self.assertIn(Department.OPERATIONS, ceo.agents_registry)
        self.assertIn(Department.SUPPLY_CHAIN, ceo.agents_registry)
        self.assertIn(Department.MARKETING, ceo.agents_registry)


class TestTaskProcessing(unittest.TestCase):
    """任务处理测试"""

    def setUp(self):
        self.system = TeaEnterpriseCollaborationSystem()

    def test_new_product_launch_task(self):
        """测试新品上市任务"""
        result = self.system.process_user_request("公司计划推出春季新品")
        self.assertEqual(result['task_overview']['inferred_type'], '新品上市')
        self.assertEqual(result['ceo_analysis']['lead_department'], '产品研发部')
        self.assertIn('运营部', result['ceo_analysis']['collaborating_departments'])
        self.assertIn('供应链部', result['ceo_analysis']['collaborating_departments'])

    def test_marketing_campaign_task(self):
        """测试营销活动任务"""
        result = self.system.process_user_request("需要进行促销活动推广")
        self.assertEqual(result['ceo_analysis']['lead_department'], '市场营销部')

    def test_cost_optimization_task(self):
        """测试成本优化任务"""
        result = self.system.process_user_request("需要降低运营成本")
        self.assertIn(result['ceo_analysis']['lead_department'], ['供应链部', 'CEO办公室'])

    def test_crisis_management_task(self):
        """测试危机处理任务"""
        result = self.system.process_user_request("发生紧急危机事件")
        self.assertEqual(result['ceo_analysis']['lead_department'], 'CEO办公室')

    def test_data_analysis_task(self):
        """测试数据分析任务"""
        result = self.system.process_user_request("需要进行数据分析", task_type=TaskType.DATA_ANALYSIS)
        self.assertEqual(result['ceo_analysis']['lead_department'], '数据分析部')


class TestDepartmentAgents(unittest.TestCase):
    """各部门Agent测试"""

    def setUp(self):
        self.system = TeaEnterpriseCollaborationSystem()

    def test_operations_agent(self):
        """测试运营部Agent"""
        task = Task(
            task_id="test-001",
            task_type=TaskType.NEW_PRODUCT_LAUNCH,
            description="新品上市",
            requesting_dept=Department.CEO,
            lead_dept=Department.OPERATIONS
        )
        response = self.system.operations.process_task(task)
        self.assertEqual(response.department, Department.OPERATIONS)
        self.assertIn('store_readiness', response.content)

    def test_supply_chain_agent(self):
        """测试供应链部Agent"""
        task = Task(
            task_id="test-002",
            task_type=TaskType.COST_OPTIMIZATION,
            description="成本优化",
            requesting_dept=Department.CEO,
            lead_dept=Department.SUPPLY_CHAIN
        )
        response = self.system.supply_chain.process_task(task)
        self.assertEqual(response.department, Department.SUPPLY_CHAIN)
        self.assertIn('optimization_opportunities', response.content)

    def test_marketing_agent(self):
        """测试市场营销部Agent"""
        task = Task(
            task_id="test-003",
            task_type=TaskType.MARKETING_CAMPAIGN,
            description="营销活动",
            requesting_dept=Department.CEO,
            lead_dept=Department.MARKETING
        )
        response = self.system.marketing.process_task(task)
        self.assertEqual(response.department, Department.MARKETING)
        self.assertIn('campaign_plan', response.content)

    def test_rnd_agent(self):
        """测试产品研发部Agent"""
        task = Task(
            task_id="test-004",
            task_type=TaskType.NEW_PRODUCT_LAUNCH,
            description="新品研发",
            requesting_dept=Department.CEO,
            lead_dept=Department.RND
        )
        response = self.system.rnd.process_task(task)
        self.assertEqual(response.department, Department.RND)
        self.assertIn('development_status', response.content)


class TestCollaboration(unittest.TestCase):
    """协作机制测试"""

    def setUp(self):
        self.system = TeaEnterpriseCollaborationSystem()

    def test_cross_department_collaboration(self):
        """测试跨部门协作"""
        result = self.system.process_user_request("推出新品茶饮")
        # 验证多部门参与
        self.assertGreaterEqual(len(result['department_contributions']), 4)

    def test_department_capabilities(self):
        """测试部门能力"""
        caps = self.system.list_all_capabilities()
        self.assertEqual(len(caps), 9)
        for dept, cap_list in caps.items():
            self.assertGreater(len(cap_list), 0)

    def test_department_status(self):
        """测试部门状态查询"""
        status = self.system.get_department_status(Department.OPERATIONS)
        self.assertEqual(status['department'], '运营部')
        self.assertEqual(status['status'], 'active')


class TestOutputFormats(unittest.TestCase):
    """输出格式测试"""

    def setUp(self):
        self.system = TeaEnterpriseCollaborationSystem()

    def test_report_structure(self):
        """测试报告结构"""
        result = self.system.process_user_request("新品上市")
        self.assertIn('report_header', result)
        self.assertIn('task_overview', result)
        self.assertIn('ceo_analysis', result)
        self.assertIn('department_contributions', result)
        self.assertIn('integrated_solution', result)

    def test_report_header(self):
        """测试报告头"""
        result = self.system.process_user_request("新品上市")
        header = result['report_header']
        self.assertIn('task_id', header)
        self.assertIn('generated_at', header)
        self.assertIn('system', header)


def run_tests():
    """运行所有测试"""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()
