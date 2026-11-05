#!/usr/bin/env python3
"""
HermesAgent 测试脚本

此脚本包含对 HermesAgent 核心功能的单元测试和集成测试。
"""

import asyncio
import json
import os
import sys
import time
import unittest
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum


# ============================================================================
# 核心组件模拟
# ============================================================================

class CallStatus(Enum):
    """调用状态枚举"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class FunctionCall:
    """函数调用请求"""
    call_id: str
    function_name: str
    arguments: Dict[str, Any]
    timeout: int = 30
    retry_policy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "function_name": self.function_name,
            "arguments": self.arguments,
            "timeout": self.timeout,
            "retry_policy": self.retry_policy
        }


@dataclass
class FunctionResponse:
    """函数调用响应"""
    call_id: str
    status: CallStatus
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }


@dataclass
class Session:
    """会话对象"""
    session_id: str
    user_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    status: str = "active"
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "context": self.context
        }


@dataclass
class Skill:
    """技能对象"""
    skill_id: str
    name: str
    version: str
    description: str
    trigger_phrases: List[str]
    implementation: str
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "trigger_phrases": self.trigger_phrases,
            "implementation": self.implementation,
            "dependencies": self.dependencies,
            "metadata": self.metadata
        }


# ============================================================================
# 核心组件实现
# ============================================================================

class FunctionCallingProtocol:
    """函数调用协议实现"""

    def __init__(self):
        self.registered_functions: Dict[str, callable] = {}

    def register(self, name: str, func: callable) -> None:
        """注册函数"""
        self.registered_functions[name] = func

    async def execute(self, call: FunctionCall) -> FunctionResponse:
        """执行函数调用"""
        start_time = time.time()

        try:
            if call.function_name not in self.registered_functions:
                return FunctionResponse(
                    call_id=call.call_id,
                    status=CallStatus.ERROR,
                    error=f"函数未注册: {call.function_name}",
                    metadata={"execution_time": time.time() - start_time}
                )

            func = self.registered_functions[call.function_name]

            # 检查是否为异步函数
            if asyncio.iscoroutinefunction(func):
                result = await func(**call.arguments)
            else:
                result = func(**call.arguments)

            return FunctionResponse(
                call_id=call.call_id,
                status=CallStatus.SUCCESS,
                result=result,
                metadata={"execution_time": time.time() - start_time}
            )

        except Exception as e:
            return FunctionResponse(
                call_id=call.call_id,
                status=CallStatus.ERROR,
                error=str(e),
                metadata={"execution_time": time.time() - start_time}
            )


class SessionManager:
    """会话管理器"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, session_id: str, user_id: str = None) -> Session:
        """创建新会话"""
        session = Session(session_id=session_id, user_id=user_id)
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话"""
        return self.sessions.get(session_id)

    def update_session(self, session_id: str, context: Dict[str, Any]) -> bool:
        """更新会话上下文"""
        session = self.get_session(session_id)
        if session:
            session.context.update(context)
            session.updated_at = datetime.now()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False


class SkillRegistry:
    """技能注册表"""

    def __init__(self):
        self.skills: Dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """注册技能"""
        self.skills[skill.skill_id] = skill

    def get(self, skill_id: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(skill_id)

    def find_by_trigger(self, trigger: str) -> List[Skill]:
        """根据触发短语查找技能"""
        matches = []
        for skill in self.skills.values():
            # 检查请求中是否包含技能的触发短语
            if any(phrase.lower() in trigger.lower() for phrase in skill.trigger_phrases):
                matches.append(skill)
        return matches

    def list_all(self) -> List[Skill]:
        """列出所有技能"""
        return list(self.skills.values())


class IncrementalLearningEngine:
    """增量学习引擎"""

    def __init__(self):
        self.learning_records: List[Dict[str, Any]] = []
        self.knowledge_base: Dict[str, Any] = {}

    def learn(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """学习新的交互数据"""
        # 提取知识
        knowledge = self._extract_knowledge(interaction_data)

        # 融合到知识库
        self._merge_knowledge(knowledge)

        # 记录学习
        record = {
            "timestamp": datetime.now().isoformat(),
            "data": interaction_data,
            "knowledge": knowledge
        }
        self.learning_records.append(record)

        return {"status": "success", "knowledge_extracted": len(knowledge)}

    def _extract_knowledge(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从数据中提取知识"""
        # 简化的知识提取
        return {
            "patterns": data.get("patterns", []),
            "rules": data.get("rules", []),
            "examples": data.get("examples", [])
        }

    def _merge_knowledge(self, new_knowledge: Dict[str, Any]) -> None:
        """将新知识融合到知识库"""
        for key, value in new_knowledge.items():
            if key not in self.knowledge_base:
                self.knowledge_base[key] = []
            self.knowledge_base[key].extend(value)


class DynamicBinder:
    """动态绑定器"""

    def __init__(self, skill_registry: SkillRegistry):
        self.skill_registry = skill_registry

    def bind(self, request: str, available_skills: List[Skill]) -> Optional[Skill]:
        """将请求绑定到最合适的技能"""
        if not available_skills:
            return None

        # 简单的相似度匹配
        best_match = None
        highest_score = 0

        for skill in available_skills:
            score = self._calculate_similarity(request, skill)
            if score > highest_score:
                highest_score = score
                best_match = skill

        return best_match

    def _calculate_similarity(self, request: str, skill: Skill) -> float:
        """计算请求与技能的相似度"""
        request_lower = request.lower()
        score = 0.0

        # 检查触发短语匹配
        for phrase in skill.trigger_phrases:
            if phrase.lower() in request_lower:
                score += 1.0

        # 检查描述关键词
        desc_words = skill.description.lower().split()
        request_words = request_lower.split()
        score += len(set(desc_words) & set(request_words)) / len(desc_words)

        return score


# ============================================================================
# 测试用例
# ============================================================================

class TestFunctionCallingProtocol(unittest.TestCase):
    """函数调用协议测试"""

    def setUp(self):
        self.protocol = FunctionCallingProtocol()

        # 注册测试函数
        def add(a: int, b: int) -> int:
            return a + b

        self.protocol.register("add", add)

    def test_sync_function_call(self):
        """测试同步函数调用"""
        call = FunctionCall(
            call_id="test-1",
            function_name="add",
            arguments={"a": 5, "b": 3}
        )

        response = asyncio.run(self.protocol.execute(call))

        self.assertEqual(response.status, CallStatus.SUCCESS)
        self.assertEqual(response.result, 8)

    def test_async_function_call(self):
        """测试异步函数调用"""
        async def async_add(a: int, b: int) -> int:
            await asyncio.sleep(0.01)
            return a + b

        self.protocol.register("async_add", async_add)

        call = FunctionCall(
            call_id="test-2",
            function_name="async_add",
            arguments={"a": 10, "b": 20}
        )

        response = asyncio.run(self.protocol.execute(call))

        self.assertEqual(response.status, CallStatus.SUCCESS)
        self.assertEqual(response.result, 30)

    def test_unregistered_function(self):
        """测试调用未注册函数"""
        call = FunctionCall(
            call_id="test-3",
            function_name="nonexistent",
            arguments={}
        )

        response = asyncio.run(self.protocol.execute(call))

        self.assertEqual(response.status, CallStatus.ERROR)
        self.assertIn("未注册", response.error)


class TestSessionManager(unittest.TestCase):
    """会话管理器测试"""

    def setUp(self):
        self.manager = SessionManager()

    def test_create_session(self):
        """测试创建会话"""
        session = self.manager.create_session("sess-1", "user-1")

        self.assertEqual(session.session_id, "sess-1")
        self.assertEqual(session.user_id, "user-1")
        self.assertEqual(session.status, "active")

    def test_get_session(self):
        """测试获取会话"""
        self.manager.create_session("sess-2")
        session = self.manager.get_session("sess-2")

        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "sess-2")

    def test_update_session(self):
        """测试更新会话"""
        self.manager.create_session("sess-3")
        result = self.manager.update_session("sess-3", {"key": "value"})

        self.assertTrue(result)
        session = self.manager.get_session("sess-3")
        self.assertEqual(session.context["key"], "value")

    def test_delete_session(self):
        """测试删除会话"""
        self.manager.create_session("sess-4")
        result = self.manager.delete_session("sess-4")

        self.assertTrue(result)
        self.assertIsNone(self.manager.get_session("sess-4"))


class TestSkillRegistry(unittest.TestCase):
    """技能注册表测试"""

    def setUp(self):
        self.registry = SkillRegistry()
        self.test_skill = Skill(
            skill_id="skill-1",
            name="test-skill",
            version="1.0.0",
            description="测试技能",
            trigger_phrases=["测试", "test"],
            implementation="def execute(): pass"
        )

    def test_register_skill(self):
        """测试注册技能"""
        self.registry.register(self.test_skill)

        skill = self.registry.get("skill-1")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.name, "test-skill")

    def test_find_by_trigger(self):
        """测试根据触发短语查找"""
        self.registry.register(self.test_skill)

        matches = self.registry.find_by_trigger("需要测试")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].skill_id, "skill-1")

    def test_list_all_skills(self):
        """测试列出所有技能"""
        self.registry.register(self.test_skill)
        self.registry.register(Skill(
            skill_id="skill-2",
            name="another-skill",
            version="1.0.0",
            description="另一个技能",
            trigger_phrases=["其他"],
            implementation=""
        ))

        all_skills = self.registry.list_all()
        self.assertEqual(len(all_skills), 2)


class TestIncrementalLearning(unittest.TestCase):
    """增量学习引擎测试"""

    def setUp(self):
        self.engine = IncrementalLearningEngine()

    def test_learn(self):
        """测试学习功能"""
        data = {
            "patterns": ["pattern1", "pattern2"],
            "rules": ["rule1"],
            "examples": ["example1"]
        }

        result = self.engine.learn(data)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(self.engine.learning_records), 1)
        self.assertIn("patterns", self.engine.knowledge_base)


class TestDynamicBinder(unittest.TestCase):
    """动态绑定器测试"""

    def setUp(self):
        self.registry = SkillRegistry()
        self.binder = DynamicBinder(self.registry)

        self.registry.register(Skill(
            skill_id="code-skill",
            name="code-generator",
            version="1.0.0",
            description="生成代码",
            trigger_phrases=["写代码", "生成代码"],
            implementation=""
        ))

    def test_bind_to_skill(self):
        """测试绑定到技能"""
        skills = self.registry.list_all()
        bound = self.binder.bind("请帮我写代码", skills)

        self.assertIsNotNone(bound)
        self.assertEqual(bound.skill_id, "code-skill")


# ============================================================================
# 主程序
# ============================================================================

def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestFunctionCallingProtocol))
    suite.addTests(loader.loadTestsFromTestCase(TestSessionManager))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestIncrementalLearning))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicBinder))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
