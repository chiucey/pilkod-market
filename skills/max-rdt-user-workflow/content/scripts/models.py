"""
Max-RDT 数据模型定义
定义Recipe、Data Flywheel、Taste Standard的核心数据结构
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
import uuid


class OutputFormat(Enum):
    """输出格式偏好"""
    MARKDOWN = "markdown"
    JSON = "json"
    PLAIN = "plain"
    STRUCTURED = "structured"


class CommunicationStyle(Enum):
    """沟通风格"""
    VERBOSE = "verbose"
    CONCISE = "concise"
    PROFESSIONAL = "professional"
    CASUAL = "casual"


class TaskComplexity(Enum):
    """任务复杂度"""
    SIMPLE = "simple"      # 1-2个步骤
    MODERATE = "moderate"  # 3-5个步骤
    COMPLEX = "complex"    # 5+个步骤


# ============== Recipe相关模型 ==============

@dataclass
class WorkflowNode:
    """工作流节点"""
    id: str
    type: str  # entry, action, parallel, merge
    action_type: Optional[str] = None
    tasks: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """工作流边"""
    from_id: str
    to_id: str
    condition: Optional[str] = None


@dataclass
class Workflow:
    """工作流结构"""
    nodes: List[WorkflowNode] = field(default_factory=list)
    edges: List[WorkflowEdge] = field(default_factory=list)


@dataclass
class UserPreferences:
    """用户偏好"""
    detail_level: str = "medium"
    communication_style: CommunicationStyle = CommunicationStyle.CONCISE
    output_format: OutputFormat = OutputFormat.MARKDOWN
    priority_order: List[str] = field(default_factory=lambda: ["accuracy", "speed"])
    response_length: str = "medium"
    creativity_level: float = 0.5  # 0-1


@dataclass
class TriggerCondition:
    """触发条件"""
    type: str  # keyword, complexity, domain
    values: List[str] = field(default_factory=list)
    min_value: Optional[float] = None


@dataclass
class Recipe:
    """用户专属工作流配方"""
    recipe_id: str
    user_id: str
    name: str
    description: str
    workflow: Workflow
    preferences: UserPreferences
    confidence: float = 0.5
    trigger_conditions: List[TriggerCondition] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.5
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "recipe_id": self.recipe_id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "workflow": {
                "nodes": [
                    {"id": n.id, "type": n.type, "action_type": n.action_type, "tasks": n.tasks}
                    for n in self.workflow.nodes
                ],
                "edges": [
                    {"from": e.from_id, "to": e.to_id}
                    for e in self.workflow.edges
                ]
            },
            "preferences": {
                "detail_level": self.preferences.detail_level,
                "communication_style": self.preferences.communication_style.value,
                "output_format": self.preferences.output_format.value,
                "priority_order": self.preferences.priority_order,
                "response_length": self.preferences.response_length,
                "creativity_level": self.preferences.creativity_level
            },
            "confidence": self.confidence,
            "trigger_conditions": [
                {"type": t.type, "values": t.values}
                for t in self.trigger_conditions
            ],
            "usage_count": self.usage_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


# ============== Data Flywheel相关模型 ==============

@dataclass
class BehaviorEvent:
    """行为事件"""
    event_id: str
    user_id: str
    timestamp: datetime
    event_type: str  # input, output, feedback, navigation
    content: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionPattern:
    """交互模式"""
    pattern_id: str
    user_id: str
    pattern_type: str
    frequency: int
    avg_duration: float
    success_indicator: float
    last_observed: datetime


@dataclass
class FlywheelMetrics:
    """飞轮指标"""
    behavior_count: int
    new_patterns: int
    quality_score: float
    evolution_triggered: bool
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class BehaviorData:
    """采集的行为数据"""
    user_id: str
    input_style: str
    frequency: str
    complexity_tolerance: float
    patience_level: str
    acceptance_rate: float
    refinement_count: int
    learning_velocity: float
    timestamp: datetime = field(default_factory=datetime.now)


# ============== Taste Standard相关模型 ==============

@dataclass
class QualityStandard:
    """质量标准"""
    dimension: str
    weight: float
    target: str  # high, medium, low, optimal
    benchmarks: List[str] = field(default_factory=list)


@dataclass
class StylePreference:
    """风格偏好"""
    naming_convention: str = "default"
    comment_style: str = "minimal"
    structure: str = "default"
    voice: str = "active"
    sentence_length: str = "varied"


@dataclass
class DomainTaste:
    """领域品味"""
    domain: str
    quality_standards: List[QualityStandard]
    style_preferences: StylePreference
    rejection_patterns: List[str] = field(default_factory=list)
    acceptance_patterns: List[str] = field(default_factory=list)
    confidence: float = 0.5
    sample_count: int = 0


@dataclass
class TasteProfile:
    """用户品味画像"""
    user_id: str
    domains: Dict[str, DomainTaste] = field(default_factory=dict)
    cross_domain_consistency: float = 0.5
    learning_confidence: str = "low"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationResult:
    """评估结果"""
    taste_score: float  # 0-1
    dimension_scores: Dict[str, float]
    suggestions: List[str] = field(default_factory=list)
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


# ============== 集成模型 ==============

@dataclass
class EnhancedTaskContext:
    """增强后的任务上下文"""
    original_task: Dict[str, Any]
    user_recipe: Optional[Dict] = None
    taste_standards: Optional[Dict] = None
    flywheel_state: Optional[Dict] = None
    enhancement_confidence: float = 0.0


@dataclass
class TaskOutcome:
    """任务执行结果"""
    task_id: str
    user_id: str
    recipe_id: Optional[str]
    execution_result: Any
    taste_evaluation: Optional[EvaluationResult]
    user_feedback: Optional[Dict]
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
