"""
MaxHermes + MaxClaw + DeerFlow 复合体初始化脚本

快速初始化多智能体复合系统
"""

import asyncio
import json
from pathlib import Path

# 导入组件
from memory_manager import FiveLayerMemory, create_memory_system
from evolution_runner import EvolutionEngine, create_evolution_engine


class MaxHermes:
    """
    MaxHermes - 通信协调层
    负责用户交互与消息路由
    """

    def __init__(self, memory_system, evolution_engine):
        self.memory = memory_system
        self.evolution = evolution_engine
        self.dialogue_state = {}

    async def process_input(self, user_message: str) -> Dict:
        """处理用户输入"""
        # 1. 存储到L1短时记忆
        await self.memory.store(1, 'last_input', user_message)

        # 2. 意图识别
        intent = self.recognize_intent(user_message)

        # 3. 检索相关上下文
        context = await self.memory.retrieve(user_message, layers=[1, 2, 3])

        return {
            'intent': intent,
            'context': context,
            'message': user_message
        }

    def recognize_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()

        # 简单规则匹配
        patterns = {
            'complex_task': ['分析', '构建', '实现', '设计', '开发', 'build', 'create', 'implement', 'design'],
            'simple_query': ['什么是', '如何', '怎么', '查询', 'what', 'how', 'query'],
            'creative': ['创作', '写', '生成', '制作', 'write', 'create', 'generate', 'make'],
            'coding': ['代码', 'code', 'debug', '修复', 'fix'],
            'research': ['研究', '调研', 'research', 'investigate']
        }

        for intent, keywords in patterns.items():
            if any(kw in message_lower for kw in keywords):
                return intent

        return 'general'

    async def generate_response(self, result: Any) -> str:
        """生成响应"""
        # 简单响应生成
        return f"处理完成: {result}"


class MaxClaw:
    """
    MaxClaw - 执行工具层
    负责工具调用与代码执行
    """

    def __init__(self, available_tools: list = None):
        self.tools = available_tools or []
        self.execution_history = []

    async def execute(self, task_spec: Dict) -> Dict:
        """执行任务"""
        task_type = task_spec.get('intent', 'general')

        # 根据意图选择执行策略
        if task_type == 'complex_task':
            return await self._execute_complex(task_spec)
        elif task_type == 'coding':
            return await self._execute_coding(task_spec)
        else:
            return await self._execute_simple(task_spec)

    async def _execute_simple(self, task_spec: Dict) -> Dict:
        """简单任务执行"""
        return {
            'status': 'success',
            'result': f"处理简单任务: {task_spec.get('message', '')}",
            'steps': 1
        }

    async def _execute_coding(self, task_spec: Dict) -> Dict:
        """代码任务执行"""
        return {
            'status': 'success',
            'result': "代码任务已执行",
            'steps': ['解析需求', '生成代码', '验证语法']
        }

    async def _execute_complex(self, task_spec: Dict) -> Dict:
        """复杂任务执行"""
        return {
            'status': 'success',
            'result': "复杂任务分解执行",
            'steps': ['任务分解', '子任务执行', '结果整合']
        }


class DeerFlow:
    """
    DeerFlow - 流程编排层
    负责任务编排与状态管理
    """

    def __init__(self, hermes: MaxHermes, claw: MaxClaw, memory):
        self.hermes = hermes
        self.claw = claw
        self.memory = memory
        self.task_graph = {}

    async def orchestrate(self, goal: str) -> Dict:
        """编排任务执行"""
        # 1. 意图分析
        parsed = await self.hermes.process_input(goal)

        # 2. 存储到L2任务记忆
        await self.memory.store(2, 'current_task', goal, {
            'intent': parsed['intent'],
            'start_time': asyncio.get_event_loop().time()
        })

        # 3. 任务执行
        result = await self.claw.execute(parsed)

        # 4. 更新任务状态
        await self.memory.store(2, 'last_result', result)

        # 5. 记录执行结果用于进化
        await self.hermes.evolution.record_outcome(
            task=goal,
            approach=parsed['intent'],
            success=result.get('status') == 'success',
            metrics={'steps': result.get('steps', [])}
        )

        return result


class MaxHCDComposite:
    """
    MaxHermes + MaxClaw + DeerFlow 复合体
    """

    def __init__(self, project_name: str = 'default'):
        # 初始化5层记忆体
        self.memory = create_memory_system(project_name)

        # 初始化进化引擎
        self.evolution = create_evolution_engine(self.memory)

        # 初始化核心组件
        self.hermes = MaxHermes(self.memory, self.evolution)
        self.claw = MaxClaw()
        self.deerflow = DeerFlow(self.hermes, self.claw, self.memory)

    async def process(self, user_request: str) -> Dict:
        """处理用户请求"""
        # 使用DeerFlow编排整个流程
        result = await self.deerflow.orchestrate(user_request)

        # 生成响应
        response = await self.hermes.generate_response(result)

        return {
            'request': user_request,
            'result': result,
            'response': response,
            'memory_stats': self.memory.get_stats(),
            'evolution_stats': self.evolution.get_evolution_stats()
        }

    async def trigger_evolution(self) -> Dict:
        """触发进化"""
        return await self.evolution.evolve_capabilities()

    def status(self) -> str:
        """获取系统状态"""
        return f"""
╔═══════════════════════════════════════════════════╗
║         MAX-HCD COMPOSITE SYSTEM STATUS          ║
╠═══════════════════════════════════════════════════╣
{self.memory.summary()}
{self.evolution.summary()}
╚═══════════════════════════════════════════════════╝
        """


async def create_composite(project_name: str = 'default') -> MaxHCDComposite:
    """创建复合体实例"""
    composite = MaxHCDComposite(project_name)
    print(f"✓ MaxHCD Composite initialized: {project_name}")
    return composite


async def demo():
    """演示"""
    print("Initializing MaxHCD Composite...")

    # 创建复合体
    composite = await create_composite('demo')

    # 处理请求
    print("\nProcessing requests...")

    result1 = await composite.process("帮我分析销售数据")
    print(f"\n[1] Result: {result1['result']['result']}")

    result2 = await composite.process("构建一个Web应用")
    print(f"\n[2] Result: {result2['result']['result']}")

    result3 = await composite.process("写一段Python代码")
    print(f"\n[3] Result: {result3['result']['result']}")

    # 触发进化
    print("\nTriggering evolution...")
    evolution_result = await composite.trigger_evolution()
    print(f"Evolution: {evolution_result}")

    # 显示状态
    print(composite.status())


if __name__ == '__main__':
    asyncio.run(demo())
