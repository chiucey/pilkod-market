"""
Unit Tests for Agent Team Orchestration Framework
Version: 4.0.0
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from main import (
    OrchestrationFramework,
    TaskState,
    AgentRole,
    HandoffMessage,
    TaskRecord,
    run
)


class TestHandoffMessage(unittest.TestCase):
    """Test handoff message validation and formatting"""

    def test_valid_handoff(self):
        """Test valid handoff message"""
        handoff = HandoffMessage(
            task_id="task-001",
            from_agent="agent-A",
            to_agent="agent-B",
            completed_work="Built authentication module",
            artifact_location="/shared/artifacts/auth/",
            verification_method="Run npm test auth",
            known_issues="Rate limiting not implemented",
            next_action="Review error handling"
        )
        is_valid, errors = handoff.validate()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)

    def test_invalid_handoff_missing_elements(self):
        """Test handoff with missing required elements"""
        handoff = HandoffMessage(
            task_id="task-001",
            from_agent="agent-A",
            to_agent="agent-B",
            completed_work="",  # Missing
            artifact_location="",  # Missing
            verification_method="",  # Missing
            known_issues="",
            next_action=""  # Missing
        )
        is_valid, errors = handoff.validate()
        self.assertFalse(is_valid)
        self.assertGreaterEqual(len(errors), 3)

    def test_handoff_format_message(self):
        """Test handoff message formatting"""
        handoff = HandoffMessage(
            task_id="task-001",
            from_agent="orchestrator",
            to_agent="builder",
            completed_work="Task completed",
            artifact_location="/shared/artifacts/output",
            verification_method="npm test",
            known_issues="None",
            next_action="Review output"
        )
        message = handoff.format_message()
        self.assertIn("Task completed", message)
        self.assertIn("/shared/artifacts/output", message)
        self.assertIn("npm test", message)


class TestTaskRecord(unittest.TestCase):
    """Test task record state management"""

    def test_task_creation(self):
        """Test task record creation"""
        task = TaskRecord(
            task_id="task-001",
            description="Test task"
        )
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.state, TaskState.INBOX)
        self.assertIsNone(task.assigned_agent)

    def test_state_update(self):
        """Test state update with history"""
        task = TaskRecord(
            task_id="task-001",
            description="Test task"
        )
        task.update_state(TaskState.ASSIGNED, "orchestrator", "Assigned to builder")
        self.assertEqual(task.state, TaskState.ASSIGNED)
        self.assertEqual(len(task.state_history), 1)
        self.assertEqual(task.state_history[0]["to_state"], "Assigned")


class TestOrchestrationFramework(unittest.TestCase):
    """Test orchestration framework operations"""

    def setUp(self):
        """Set up test framework"""
        self.framework = OrchestrationFramework()
        self.framework.register_agent("orchestrator", AgentRole.ORCHESTRATOR)
        self.framework.register_agent("builder", AgentRole.BUILDER)
        self.framework.register_agent("reviewer", AgentRole.REVIEWER)

    def test_agent_registration(self):
        """Test agent registration"""
        self.assertEqual(self.framework.agents["orchestrator"], AgentRole.ORCHESTRATOR)
        self.assertEqual(self.framework.agents["builder"], AgentRole.BUILDER)

    def test_task_creation(self):
        """Test task creation"""
        task = self.framework.create_task(
            task_id="task-001",
            description="Build authentication module"
        )
        self.assertIsNotNone(task)
        self.assertEqual(task.task_id, "task-001")
        self.assertEqual(task.state, TaskState.INBOX)

    def test_task_assignment(self):
        """Test task assignment by orchestrator"""
        self.framework.create_task("task-001", "Test task")
        success = self.framework.assign_task("task-001", "builder", "orchestrator")
        self.assertTrue(success)
        self.assertEqual(self.framework.tasks["task-001"].assigned_agent, "builder")

    def test_unauthorized_assignment(self):
        """Test unauthorized task assignment"""
        self.framework.create_task("task-001", "Test task")
        # Builder trying to assign (not orchestrator)
        success = self.framework.assign_task("task-001", "reviewer", "builder")
        self.assertFalse(success)

    def test_handoff_execution(self):
        """Test standardized handoff execution"""
        self.framework.create_task("task-001", "Test task")
        self.framework.assign_task("task-001", "builder", "orchestrator")

        handoff = HandoffMessage(
            task_id="task-001",
            from_agent="builder",
            to_agent="reviewer",
            completed_work="Built auth module",
            artifact_location="/shared/artifacts/auth/",
            verification_method="npm test auth",
            known_issues="None",
            next_action="Review code"
        )

        success = self.framework.execute_handoff(handoff, "orchestrator")
        self.assertTrue(success)
        self.assertEqual(len(self.framework.handoffs), 1)

    def test_invalid_handoff(self):
        """Test handoff validation"""
        self.framework.create_task("task-001", "Test task")

        handoff = HandoffMessage(
            task_id="task-001",
            from_agent="builder",
            to_agent="reviewer",
            completed_work="",  # Missing
            artifact_location="",
            verification_method="",
            known_issues="",
            next_action=""
        )

        success = self.framework.execute_handoff(handoff, "orchestrator")
        self.assertFalse(success)

    def test_task_state_flow(self):
        """Test complete task state flow"""
        self.framework.create_task("task-001", "Test task")

        # Assign
        self.framework.assign_task("task-001", "builder", "orchestrator")
        self.assertEqual(self.framework.tasks["task-001"].state, TaskState.ASSIGNED)

        # Start
        self.framework.start_task("task-001", "builder")
        self.assertEqual(self.framework.tasks["task-001"].state, TaskState.IN_PROGRESS)

        # Submit for review
        self.framework.submit_for_review("task-001", "builder")
        self.assertEqual(self.framework.tasks["task-001"].state, TaskState.REVIEW)

        # Complete
        self.framework.complete_task("task-001", "reviewer", "Approved")
        self.assertEqual(self.framework.tasks["task-001"].state, TaskState.DONE)

    def test_task_failure(self):
        """Test task failure handling"""
        self.framework.create_task("task-001", "Test task")
        self.framework.assign_task("task-001", "builder", "orchestrator")
        self.framework.start_task("task-001", "builder")

        success = self.framework.fail_task("task-001", "builder", "Implementation error")
        self.assertTrue(success)
        self.assertEqual(self.framework.tasks["task-001"].state, TaskState.FAILED)
        self.assertEqual(self.framework.tasks["task-001"].failure_reason, "Implementation error")

    def test_quality_rules_enforcement(self):
        """Test quality iron rules"""
        self.framework.create_task("task-001", "Test task")
        passed, issues = self.framework.enforce_quality_rules("task-001")
        self.assertFalse(passed)
        self.assertGreater(len(issues), 0)


class TestFrameworkEntryPoint(unittest.TestCase):
    """Test main entry point function"""

    def test_init_action(self):
        """Test init action"""
        result = run({"action": "init"})
        self.assertEqual(result["status"], "success")
        self.assertIn("version", result["data"])
        self.assertEqual(result["data"]["version"], "4.0.0")

    def test_create_task_action(self):
        """Test create_task action"""
        result = run({
            "action": "create_task",
            "task_id": "test-001",
            "description": "Test task"
        })
        self.assertEqual(result["status"], "success")
        self.assertIn("task", result["data"])

    def test_status_action(self):
        """Test status action"""
        result = run({"action": "status"})
        self.assertEqual(result["status"], "success")
        self.assertIn("tasks", result["data"])

    def test_unknown_action(self):
        """Test unknown action handling"""
        result = run({"action": "unknown"})
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
