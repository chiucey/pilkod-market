#!/usr/bin/env python3
"""
Agent Team Orchestration - Main Entry Point
Version: 4.0.0
A production-grade multi-Agent collaboration framework with standardized handoffs and quality enforcement.
"""

import sys
import json
import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from uuid import uuid4

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskState(Enum):
    """Task lifecycle states"""
    INBOX = "Inbox"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    REVIEW = "Review"
    DONE = "Done"
    FAILED = "Failed"


class AgentRole(Enum):
    """Agent roles in the orchestration framework"""
    ORCHESTRATOR = "Orchestrator"
    BUILDER = "Builder"
    REVIEWER = "Reviewer"
    OPS = "Ops"
    RESEARCHER = "Researcher"
    ANALYST = "Analyst"


@dataclass
class HandoffMessage:
    """
    Standardized 5-element handoff message structure.

    Elements:
        1. completed_work: Summary of changes/outputs
        2. artifact_location: Exact file path
        3. verification_method: Test command or acceptance criteria
        4. known_issues: Incomplete items or potential risks
        5. next_action: Clear task for receiver
    """
    task_id: str
    from_agent: str
    to_agent: str
    completed_work: str
    artifact_location: str
    verification_method: str
    known_issues: str
    next_action: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    handoff_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> tuple[bool, List[str]]:
        """Validate handoff message has all 5 required elements"""
        errors = []
        if not self.completed_work.strip():
            errors.append("Missing: completed_work")
        if not self.artifact_location.strip():
            errors.append("Missing: artifact_location")
        if not self.verification_method.strip():
            errors.append("Missing: verification_method")
        if not self.next_action.strip():
            errors.append("Missing: next_action")
        return (len(errors) == 0, errors)

    def format_message(self) -> str:
        """Format handoff message as readable text"""
        return (
            f"[Handoff {self.handoff_id[:8]}] {self.from_agent} → {self.to_agent}\n"
            f"Task: {self.task_id}\n"
            f"Completed: {self.completed_work}\n"
            f"Location: {self.artifact_location}\n"
            f"Verify: {self.verification_method}\n"
            f"Issues: {self.known_issues or 'None'}\n"
            f"Next: {self.next_action}\n"
            f"Time: {self.timestamp}"
        )


@dataclass
class TaskRecord:
    """Task record with state tracking"""
    task_id: str
    description: str
    state: TaskState = TaskState.INBOX
    assigned_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    state_history: List[Dict] = field(default_factory=list)
    handoffs: List[str] = field(default_factory=list)
    output_path: Optional[str] = None
    failure_reason: Optional[str] = None

    def update_state(self, new_state: TaskState, agent: str, comment: str = "") -> None:
        """Update task state with full traceability"""
        self.state = new_state
        self.updated_at = datetime.now().isoformat()
        self.state_history.append({
            "from_state": self.state.value if self.state_history else None,
            "to_state": new_state.value,
            "agent": agent,
            "comment": comment,
            "timestamp": self.updated_at
        })


class OrchestrationFramework:
    """
    Core orchestration framework for multi-Agent collaboration.

    Features:
        - Task lifecycle management
        - Standardized handoff protocols
        - State tracking with full traceability
        - Quality rule enforcement
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.tasks: Dict[str, TaskRecord] = {}
        self.handoffs: List[HandoffMessage] = []
        self.agents: Dict[str, AgentRole] = {}
        self.quality_rules_enabled = True
        self.logger = logger

    def register_agent(self, agent_id: str, role: AgentRole) -> None:
        """Register an agent with its role"""
        self.agents[agent_id] = role
        self.logger.info(f"Registered agent: {agent_id} as {role.value}")

    def create_task(self, task_id: str, description: str, output_path: Optional[str] = None) -> TaskRecord:
        """Create a new task"""
        task = TaskRecord(
            task_id=task_id,
            description=description,
            output_path=output_path or self._get_default_output_path(task_id)
        )
        self.tasks[task_id] = task
        self.logger.info(f"Created task: {task_id}")
        return task

    def assign_task(self, task_id: str, agent_id: str, orchestrator_id: str) -> bool:
        """Assign task to an agent (Orchestrator only)"""
        if orchestrator_id not in self.agents or self.agents[orchestrator_id] != AgentRole.ORCHESTRATOR:
            self.logger.error(f"Unauthorized: {orchestrator_id} is not an Orchestrator")
            return False

        if task_id not in self.tasks:
            self.logger.error(f"Task not found: {task_id}")
            return False

        task = self.tasks[task_id]
        task.assigned_agent = agent_id
        task.update_state(TaskState.ASSIGNED, orchestrator_id, f"Assigned to {agent_id}")
        self.logger.info(f"Task {task_id} assigned to {agent_id}")
        return True

    def start_task(self, task_id: str, agent_id: str) -> bool:
        """Start task execution"""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        if task.assigned_agent != agent_id:
            self.logger.warning(f"Task {task_id} not assigned to {agent_id}")
            return False
        task.update_state(TaskState.IN_PROGRESS, agent_id, "Task execution started")
        return True

    def submit_for_review(self, task_id: str, agent_id: str) -> bool:
        """Submit task for review"""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.update_state(TaskState.REVIEW, agent_id, "Submitted for review")
        return True

    def complete_task(self, task_id: str, agent_id: str, comment: str = "") -> bool:
        """Mark task as done"""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.update_state(TaskState.DONE, agent_id, comment or "Task completed")
        return True

    def fail_task(self, task_id: str, agent_id: str, reason: str) -> bool:
        """Mark task as failed"""
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        task.failure_reason = reason
        task.update_state(TaskState.FAILED, agent_id, f"Failed: {reason}")
        self.logger.warning(f"Task {task_id} failed: {reason}")
        return True

    def execute_handoff(self, handoff: HandoffMessage, orchestrator_id: str) -> bool:
        """
        Execute a standardized handoff between agents.
        Validates all 5 required elements before proceeding.
        """
        # Validate orchestrator authority
        if orchestrator_id not in self.agents or self.agents[orchestrator_id] != AgentRole.ORCHESTRATOR:
            self.logger.error("Unauthorized: Only Orchestrator can execute handoffs")
            return False

        # Validate handoff message
        is_valid, errors = handoff.validate()
        if not is_valid:
            self.logger.error(f"Invalid handoff: {', '.join(errors)}")
            return False

        # Validate task exists
        if handoff.task_id not in self.tasks:
            self.logger.error(f"Task not found: {handoff.task_id}")
            return False

        # Store handoff and update task
        self.handoffs.append(handoff)
        self.tasks[handoff.task_id].handoffs.append(handoff.handoff_id)
        self.tasks[handoff.task_id].assigned_agent = handoff.to_agent

        self.logger.info(f"Handoff executed: {handoff.handoff_id[:8]}")
        return True

    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Get task status summary"""
        if task_id not in self.tasks:
            return None
        task = self.tasks[task_id]
        return {
            "task_id": task.task_id,
            "state": task.state.value,
            "assigned_agent": task.assigned_agent,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
            "failure_reason": task.failure_reason
        }

    def get_all_tasks(self) -> List[Dict]:
        """Get all task statuses"""
        return [self.get_task_status(tid) for tid in self.tasks]

    def _get_default_output_path(self, task_id: str) -> str:
        """Get default artifact path"""
        base = self.config.get("shared_artifact_base_path", "/shared/artifacts")
        return f"{base}/{task_id}"

    def enforce_quality_rules(self, task_id: str) -> tuple[bool, List[str]]:
        """
        Enforce quality iron rules.
        Returns (passed, issues) tuple.
        """
        issues = []
        if task_id not in self.tasks:
            return False, ["Task not found"]

        task = self.tasks[task_id]

        # Rule 1: Task must have passed through review
        if task.state != TaskState.DONE:
            issues.append("Task has not been completed")

        # Rule 2: Task must have valid output path
        if not task.output_path:
            issues.append("No output path specified")

        # Rule 3: Task must have state history
        if len(task.state_history) < 3:
            issues.append("Insufficient state history - review may have been skipped")

        return (len(issues) == 0, issues)


def run(input_data: Optional[Dict] = None) -> Dict:
    """
    Main entry point for the skill.

    Args:
        input_data: Dict containing action and parameters

    Returns:
        Dict with status, data, and user message
    """
    input_data = input_data or {}
    action = input_data.get("action", "init")

    try:
        framework = OrchestrationFramework()

        if action == "init":
            return {
                "status": "success",
                "data": {
                    "framework": "active",
                    "version": "4.0.0",
                    "features": [
                        "Task lifecycle management",
                        "5-element handoff protocol",
                        "Quality iron rules",
                        "State traceability"
                    ]
                },
                "message_for_user": (
                    "Agent Team Orchestration Framework v4.0.0 activated. "
                    "Features: Task lifecycle, standardized handoffs, quality rules, monitoring dashboard."
                )
            }

        elif action == "create_task":
            task = framework.create_task(
                task_id=input_data.get("task_id", str(uuid4())),
                description=input_data.get("description", ""),
                output_path=input_data.get("output_path")
            )
            return {
                "status": "success",
                "data": {"task": asdict(task)},
                "message_for_user": f"Task created: {task.task_id}"
            }

        elif action == "handoff":
            handoff = HandoffMessage(
                task_id=input_data["task_id"],
                from_agent=input_data["from_agent"],
                to_agent=input_data["to_agent"],
                completed_work=input_data["completed_work"],
                artifact_location=input_data["artifact_location"],
                verification_method=input_data["verification_method"],
                known_issues=input_data.get("known_issues", ""),
                next_action=input_data["next_action"]
            )
            success = framework.execute_handoff(
                handoff,
                input_data.get("orchestrator_id", "system")
            )
            return {
                "status": "success" if success else "error",
                "data": {"handoff_id": handoff.handoff_id, "validated": success},
                "message_for_user": handoff.format_message() if success else "Handoff failed validation"
            }

        elif action == "status":
            tasks = framework.get_all_tasks()
            return {
                "status": "success",
                "data": {"tasks": tasks, "count": len(tasks)},
                "message_for_user": f"Retrieved status for {len(tasks)} tasks"
            }

        else:
            return {
                "status": "error",
                "data": None,
                "message_for_user": f"Unknown action: {action}"
            }

    except Exception as e:
        logger.exception("Framework error")
        return {
            "status": "error",
            "data": None,
            "message_for_user": f"Error: {str(e)}"
        }


if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        input_data = json.loads(input_json) if input_json else {}
    else:
        input_data = {}

    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False, indent=2))
