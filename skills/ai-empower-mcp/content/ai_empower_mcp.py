"""
AI Empower MCP Skill
An intelligent co-pilot skill that observes, analyzes, and enhances AI agent workflows
by providing real-time insights, quality checks, and optimization suggestions.

Author: MiniMax Agent
Version: 1.0.0
"""

import json
import time
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


# ===================== Enums and Data Structures =====================
class EmpowerMode(str, Enum):
    """Empowerment modes"""
    THINK = "think"
    WORK = "work"
    DELIVER = "deliver"


class QualityLevel(str, Enum):
    """Quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEEDS_IMPROVEMENT = "needs_improvement"
    POOR = "poor"


@dataclass
class Observation:
    """Observation record"""
    timestamp: float
    mode: EmpowerMode
    content: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Insight:
    """Insight analysis"""
    category: str
    finding: str
    severity: str
    suggestion: str
    confidence: float = 0.8


@dataclass
class EmpowerResult:
    """Empowerment result"""
    success: bool
    mode: EmpowerMode
    insights: List[Insight]
    summary: str
    improvements: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


# ===================== Core Analysis Engines =====================
class ThinkingAnalyzer:
    """Thinking analyzer"""

    @staticmethod
    def analyze(thought_content: str, context: Optional[Dict] = None) -> EmpowerResult:
        """Analyze thinking process"""
        insights = []
        warnings = []
        improvements = []

        # Check logical coherence
        coherence_score = ThinkingAnalyzer._check_coherence(thought_content)
        if coherence_score < 0.7:
            insights.append(Insight(
                category="Logical Coherence",
                finding=f"Logic coherence score: {coherence_score:.0%}",
                severity="warning",
                suggestion="Consider breaking down complex logic into smaller steps"
            ))
            warnings.append("Logic coherence needs improvement")

        # Detect blind spots
        blindspots = ThinkingAnalyzer._detect_blindspots(thought_content)
        for spot in blindspots:
            insights.append(Insight(
                category="Blind Spot Detection",
                finding=spot["finding"],
                severity=spot["severity"],
                suggestion=spot["suggestion"]
            ))

        # Suggest deepening
        depth_suggestions = ThinkingAnalyzer._suggest_deepening(thought_content)
        if depth_suggestions:
            improvements.extend(depth_suggestions)

        # Generate summary
        summary = ThinkingAnalyzer._generate_think_summary(thought_content, insights)

        return EmpowerResult(
            success=True,
            mode=EmpowerMode.THINK,
            insights=insights,
            summary=summary,
            improvements=improvements,
            warnings=warnings
        )

    @staticmethod
    def _check_coherence(content: str) -> float:
        """Check logical coherence"""
        connectors = ['because', 'so', 'however', 'therefore', 'if', 'then', 'and', 'or',
                      'thus', 'hence', 'consequently', 'moreover', 'furthermore']
        connector_count = sum(1 for c in connectors if c.lower() in content.lower())

        sentences = re.split(r'[.!?]', content)
        sentence_count = len([s for s in sentences if s.strip()])

        if sentence_count == 0:
            return 0.0
        expected_connectors = sentence_count - 1
        if expected_connectors == 0:
            return 1.0
        return min(connector_count / expected_connectors * 0.5 + 0.5, 1.0)

    @staticmethod
    def _detect_blindspots(content: str) -> List[Dict]:
        """Detect thinking blind spots"""
        blindspots = []

        counter_patterns = [r'however', r'but', r'although', r'whereas', r'despite', r'oppose']
        if not any(re.search(p, content, re.IGNORECASE) for p in counter_patterns):
            blindspots.append({
                "finding": "No counterarguments or alternative perspectives considered",
                "severity": "warning",
                "suggestion": "Add consideration of opposing views or alternative approaches"
            })

        evidence_patterns = [r'\d+%', r'\d+ times', r'research', r'data', r'study', r'evidence']
        if not any(re.search(p, content, re.IGNORECASE) for p in evidence_patterns):
            blindspots.append({
                "finding": "Limited evidence or data supporting the analysis",
                "severity": "info",
                "suggestion": "Consider adding supporting data or research findings"
            })

        assumption_patterns = [r'assume', r'assumption', r'suppose', r'given that', r'if we assume']
        if not any(re.search(p, content, re.IGNORECASE) for p in assumption_patterns):
            blindspots.append({
                "finding": "No explicit assumptions stated",
                "severity": "info",
                "suggestion": "List key assumptions underlying the analysis"
            })

        return blindspots

    @staticmethod
    def _suggest_deepening(content: str) -> List[str]:
        """Suggest deeper analysis areas"""
        suggestions = []

        if len(content) < 200:
            suggestions.append("Thinking content is brief - consider expanding with more details and reasoning")

        if not re.search(r'for example|such as|e\.g\.|instance', content, re.IGNORECASE):
            suggestions.append("Consider adding concrete examples to support your points")

        return suggestions

    @staticmethod
    def _generate_think_summary(content: str, insights: List[Insight]) -> str:
        """Generate thinking analysis summary"""
        critical = [i for i in insights if i.severity == "critical"]
        warning_list = [i for i in insights if i.severity == "warning"]

        summary_parts = []
        if critical:
            summary_parts.append(f"Critical issues found: {len(critical)}")
        if warning_list:
            summary_parts.append(f"Warnings: {len(warning_list)}")
        if not insights:
            summary_parts.append("Thinking process appears well-structured")

        return " | ".join(summary_parts) if summary_parts else "Analysis complete"


class WorkAnalyzer:
    """Work analyzer"""

    @staticmethod
    def analyze(
        work_content: str,
        task_description: str,
        current_step: int = 1,
        total_steps: int = 1
    ) -> EmpowerResult:
        """Analyze work progress"""
        insights = []
        warnings = []
        improvements = []

        # Assess quality
        quality_score = WorkAnalyzer._assess_quality(work_content)
        quality_level = QualityLevel.GOOD if quality_score >= 0.7 else QualityLevel.NEEDS_IMPROVEMENT

        insights.append(Insight(
            category="Quality Assessment",
            finding=f"Quality score: {quality_score:.0%} ({quality_level.value})",
            severity="info",
            suggestion="Continue maintaining this quality level"
        ))

        # Detect issues
        issues = WorkAnalyzer._detect_issues(work_content, task_description)
        for issue in issues:
            insights.append(Insight(
                category="Issue Detection",
                finding=issue["finding"],
                severity=issue["severity"],
                suggestion=issue["suggestion"]
            ))
            if issue["severity"] in ["critical", "warning"]:
                warnings.append(issue["finding"])

        # Suggest optimizations
        optimizations = WorkAnalyzer._suggest_optimizations(work_content, task_description)
        improvements.extend(optimizations)

        # Check efficiency
        efficiency_tips = WorkAnalyzer._check_efficiency(work_content, current_step, total_steps)
        for tip in efficiency_tips:
            insights.append(Insight(
                category="Efficiency",
                finding=tip,
                severity="info",
                suggestion="Consider applying this efficiency tip"
            ))

        summary = f"Work quality: {quality_level.value} | Issues: {len(issues)} | Recommendations: {len(improvements)}"

        return EmpowerResult(
            success=True,
            mode=EmpowerMode.WORK,
            insights=insights,
            summary=summary,
            improvements=improvements,
            warnings=warnings
        )

    @staticmethod
    def _assess_quality(content: str) -> float:
        """Assess work quality"""
        score = 0.5

        if re.search(r'^\d+[\.、]|\n\d+[\.、]', content, re.MULTILINE):
            score += 0.15

        complete_markers = ['finished', 'complete', 'done', 'achieved', 'completed', 'implemented']
        if any(marker in content.lower() for marker in complete_markers):
            score += 0.15

        if len(content) > 500:
            score += 0.1

        error_markers = ['error', 'bug', 'issue', 'failed', 'failure', 'problem', 'mistake']
        error_count = sum(1 for m in error_markers if m in content.lower())
        score -= error_count * 0.05

        return min(max(score, 0), 1)

    @staticmethod
    def _detect_issues(content: str, task: str) -> List[Dict]:
        """Detect work issues"""
        issues = []

        task_keywords = WorkAnalyzer._extract_keywords(task)
        content_keywords = WorkAnalyzer._extract_keywords(content)
        overlap = len(set(task_keywords) & set(content_keywords))

        if task_keywords and overlap < len(task_keywords) * 0.3:
            issues.append({
                "finding": "Content may not fully address the task requirements",
                "severity": "warning",
                "suggestion": "Review task requirements and ensure all aspects are covered"
            })

        contradiction_patterns = [
            (r'not.*but', 'Self-contradictory statements detected'),
            (r'cannot.*but.*can', 'Conflicting claims detected'),
        ]
        for pattern, message in contradiction_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    "finding": message,
                    "severity": "critical",
                    "suggestion": "Resolve contradictions before proceeding"
                })

        incomplete_markers = ['TODO', 'pending', 'incomplete', 'in progress', 'WIP', 'TBD']
        if any(marker in content for marker in incomplete_markers):
            issues.append({
                "finding": "Work contains incomplete items",
                "severity": "warning",
                "suggestion": "Complete all items before delivery"
            })

        return issues

    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract keywords"""
        words = re.findall(r'[a-zA-Z]{3,}', text.lower())
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'has', 'her', 'was', 'one', 'our'}
        return [w for w in words if w not in stopwords]

    @staticmethod
    def _suggest_optimizations(content: str, task: str) -> List[str]:
        """Suggest optimizations"""
        suggestions = []

        if any(marker in content for marker in ['function', 'class', 'def ', 'import', 'async']):
            if 'error handling' not in content.lower() and 'except' not in content:
                suggestions.append("Add proper error handling")
            if 'logging' not in content.lower() and 'logger' not in content.lower():
                suggestions.append("Consider adding logging for debugging")

        if len(content) > 1000 and not re.search(r'#|\n\n|documentation|comment', content):
            suggestions.append("Consider adding documentation or comments")

        return suggestions

    @staticmethod
    def _check_efficiency(content: str, current_step: int, total_steps: int) -> List[str]:
        """Check efficiency"""
        tips = []

        progress = current_step / total_steps if total_steps > 0 else 0
        if progress > 0.8 and current_step < total_steps:
            tips.append("Approaching deadline, consider prioritizing critical items")

        if len(content) < 100 and total_steps > 5:
            tips.append("This step seems brief, consider adding more detail")

        return tips


class DeliverAnalyzer:
    """Delivery analyzer"""

    @staticmethod
    def analyze(deliverable_content: str, requirements: str) -> EmpowerResult:
        """Analyze deliverable"""
        insights = []
        warnings = []
        improvements = []

        # Check completeness
        completeness = DeliverAnalyzer._check_completeness(deliverable_content, requirements)
        if completeness < 0.8:
            warnings.append(f"Completeness score: {completeness:.0%} - Some requirements may not be met")
            insights.append(Insight(
                category="Completeness",
                finding=f"Completeness: {completeness:.0%}",
                severity="critical" if completeness < 0.6 else "warning",
                suggestion="Review requirements and add missing items"
            ))

        # Check accuracy
        accuracy = DeliverAnalyzer._check_accuracy(deliverable_content, requirements)
        if accuracy < 1.0:
            warnings.append("Potential inaccuracies detected")
            insights.append(Insight(
                category="Accuracy",
                finding="Some content may need verification",
                severity="warning",
                suggestion="Double-check facts, figures, and technical details"
            ))

        # Check quality standards
        quality_issues = DeliverAnalyzer._check_quality_standards(deliverable_content)
        for issue in quality_issues:
            insights.append(Insight(
                category="Quality Standards",
                finding=issue["finding"],
                severity=issue["severity"],
                suggestion=issue["suggestion"]
            ))

        # Suggest improvements
        suggested_improvements = DeliverAnalyzer._suggest_improvements(deliverable_content, requirements)
        improvements.extend(suggested_improvements)

        # Generate summary
        summary = DeliverAnalyzer._generate_summary(completeness, accuracy, quality_issues)

        return EmpowerResult(
            success=True,
            mode=EmpowerMode.DELIVER,
            insights=insights,
            summary=summary,
            improvements=improvements,
            warnings=warnings
        )

    @staticmethod
    def _check_completeness(content: str, requirements: str) -> float:
        """Check completeness"""
        if not requirements.strip():
            return 0.9

        req_keywords = DeliverAnalyzer._extract_requirements_keywords(requirements)
        content_keywords = DeliverAnalyzer._extract_keywords(content)

        matched = sum(1 for kw in req_keywords if kw.lower() in content.lower())
        coverage = matched / len(req_keywords) if req_keywords else 0.9

        structure_score = 0.5
        if re.search(r'introduction|overview|summary', content[:500], re.IGNORECASE):
            structure_score += 0.15
        if re.search(r'conclusion|final|end', content[-500:], re.IGNORECASE):
            structure_score += 0.15
        if re.search(r'detail|detail', content):
            structure_score += 0.2

        return (coverage + structure_score) / 2

    @staticmethod
    def _extract_requirements_keywords(requirements: str) -> List[str]:
        """Extract requirements keywords"""
        patterns = [
            r'\b(?:create|build|implement|design|develop|add|remove|fix|update|check)\b',
            r'[a-zA-Z]{4,}',
        ]
        keywords = []
        for p in patterns:
            keywords.extend(re.findall(p, requirements))
        return list(set(keywords))

    @staticmethod
    def _check_accuracy(content: str, requirements: str) -> float:
        """Check accuracy"""
        score = 1.0

        error_markers = ['???', 'TBD', '[TODO]', '[FIXME]', 'placeholder']
        for marker in error_markers:
            if marker in content:
                score -= 0.1

        placeholder_patterns = [r'xxx', r'XXX', r'\.\.\.', r'TBD']
        for pattern in placeholder_patterns:
            if re.search(pattern, content):
                score -= 0.05

        return max(score, 0)

    @staticmethod
    def _check_quality_standards(content: str) -> List[Dict]:
        """Check quality standards"""
        issues = []

        if content.count('```') % 2 != 0:
            issues.append({
                "finding": "Unbalanced code blocks",
                "severity": "warning",
                "suggestion": "Ensure all code blocks are properly closed"
            })

        links = re.findall(r'https?://[^\s\)>\]]+', content)
        if len(links) > 10:
            issues.append({
                "finding": f"Contains {len(links)} external links - verify they are accessible",
                "severity": "info",
                "suggestion": "Consider adding alt text for links"
            })

        avg_line_length = sum(len(line) for line in content.split('\n')) / max(len(content.split('\n')), 1)
        if avg_line_length > 120:
            issues.append({
                "finding": "Lines may be too long for readability",
                "severity": "info",
                "suggestion": "Consider breaking long lines for better readability"
            })

        return issues

    @staticmethod
    def _suggest_improvements(content: str, requirements: str) -> List[str]:
        """Suggest improvements"""
        suggestions = []

        if len(content) < 200:
            suggestions.append("Content seems brief - consider adding more detail")
        elif len(content) > 10000:
            suggestions.append("Content is extensive - consider adding a summary section")

        if '\n\n' not in content[:200]:
            suggestions.append("Add clear paragraph breaks for better readability")

        if '{' in content and '}' in content:
            if 'format' not in content.lower() and 'example' not in content.lower():
                suggestions.append("Consider adding usage examples if presenting code or templates")

        return suggestions

    @staticmethod
    def _generate_summary(completeness: float, accuracy: float, quality_issues: List[Dict]) -> str:
        """Generate summary"""
        parts = []
        parts.append(f"Completeness: {completeness:.0%}")
        parts.append(f"Accuracy: {accuracy:.0%}")
        parts.append(f"Quality issues: {len(quality_issues)}")

        overall = (completeness + accuracy) / 2
        if overall >= 0.9:
            status = "Excellent - Ready for delivery"
        elif overall >= 0.7:
            status = "Good - Minor improvements recommended"
        else:
            status = "Needs improvement before delivery"

        parts.append(status)
        return " | ".join(parts)


# ===================== Main Empowerment Engine =====================
class EmpowerEngine:
    """Empowerment engine"""

    def __init__(self):
        self.thinking_analyzer = ThinkingAnalyzer()
        self.work_analyzer = WorkAnalyzer()
        self.deliver_analyzer = DeliverAnalyzer()
        self.observation_history: List[Observation] = []

    def empower(self, mode: str, **kwargs) -> Dict[str, Any]:
        """Main empowerment entry point"""
        try:
            empower_mode = EmpowerMode(mode.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid mode: {mode}. Use 'think', 'work', or 'deliver'"
            }

        try:
            if empower_mode == EmpowerMode.THINK:
                result = self._empower_thinking(**kwargs)
            elif empower_mode == EmpowerMode.WORK:
                result = self._empower_work(**kwargs)
            elif empower_mode == EmpowerMode.DELIVER:
                result = self._empower_delivery(**kwargs)
            else:
                return {"success": False, "error": "Unknown mode"}

            self._record_observation(empower_mode, kwargs, result)
            return result

        except Exception as e:
            return {
                "success": False,
                "error": f"Empower analysis failed: {str(e)}"
            }

    def _empower_thinking(self, **kwargs) -> Dict[str, Any]:
        """Empower thinking"""
        thought_content = kwargs.get("thought_content", "")
        context = kwargs.get("context", {})

        if not thought_content:
            return {"success": False, "error": "thought_content is required"}

        result = self.thinking_analyzer.analyze(thought_content, context)
        return self._format_result(result)

    def _empower_work(self, **kwargs) -> Dict[str, Any]:
        """Empower work"""
        work_content = kwargs.get("work_content", "")
        task_description = kwargs.get("task_description", "")
        current_step = kwargs.get("current_step", 1)
        total_steps = kwargs.get("total_steps", 1)

        if not work_content:
            return {"success": False, "error": "work_content is required"}

        result = self.work_analyzer.analyze(
            work_content, task_description, current_step, total_steps
        )
        return self._format_result(result)

    def _empower_delivery(self, **kwargs) -> Dict[str, Any]:
        """Empower delivery"""
        deliverable_content = kwargs.get("deliverable_content", "")
        requirements = kwargs.get("requirements", "")

        if not deliverable_content:
            return {"success": False, "error": "deliverable_content is required"}

        result = self.deliver_analyzer.analyze(deliverable_content, requirements)
        return self._format_result(result)

    def _format_result(self, result: EmpowerResult) -> Dict[str, Any]:
        """Format result"""
        return {
            "success": True,
            "mode": result.mode.value,
            "summary": result.summary,
            "insights": [
                {
                    "category": i.category,
                    "finding": i.finding,
                    "severity": i.severity,
                    "suggestion": i.suggestion,
                    "confidence": i.confidence
                }
                for i in result.insights
            ],
            "improvements": result.improvements,
            "warnings": result.warnings
        }

    def _record_observation(self, mode: EmpowerMode, params: Dict, result: Dict):
        """Record observation history"""
        observation = Observation(
            timestamp=time.time(),
            mode=mode,
            content=params.get("thought_content") or params.get("work_content") or params.get("deliverable_content", ""),
            context={"params": params, "result": result}
        )
        self.observation_history.append(observation)

        if len(self.observation_history) > 100:
            self.observation_history = self.observation_history[-100:]

    def get_history(self) -> List[Dict[str, Any]]:
        """Get empowerment history"""
        return [
            {
                "timestamp": o.timestamp,
                "mode": o.mode.value,
                "content_preview": o.content[:100] + "..." if len(o.content) > 100 else o.content
            }
            for o in self.observation_history[-10:]
        ]


# ===================== Global Instance =====================
_empower_engine = EmpowerEngine()


# ===================== Skill Entry Point =====================
def ai_empower_mcp(
    mode: str,
    thought_content: str = None,
    work_content: str = None,
    deliverable_content: str = None,
    requirements: str = None,
    task_description: str = None,
    context: Dict[str, Any] = None,
    current_step: int = 1,
    total_steps: int = 1
) -> Dict[str, Any]:
    """
    AI Empower MCP Skill Entry Point

    An intelligent co-pilot skill that observes, analyzes, and enhances AI agent
    workflows by providing real-time insights, quality checks, and optimization.

    Modes:
    - "think": Analyze thinking process, identify blind spots, suggest deeper analysis
    - "work": Monitor work progress, detect issues, provide optimizations
    - "deliver": Check deliverable quality, verify completeness, suggest improvements

    Args:
        mode: Empowerment mode (think/work/deliver)
        thought_content: Content to analyze for thinking mode
        work_content: Work output to analyze for work mode
        deliverable_content: Deliverable to audit for deliver mode
        requirements: Original requirements for completeness check
        task_description: Task description for context
        context: Additional context information
        current_step: Current step number (for work mode)
        total_steps: Total steps (for work mode)

    Returns:
        Empowerment result with insights and suggestions
    """
    if mode.lower() == "think":
        content = thought_content
    elif mode.lower() == "work":
        content = work_content
    elif mode.lower() == "deliver":
        content = deliverable_content
    else:
        return {"success": False, "error": f"Unknown mode: {mode}"}

    if not content:
        return {"success": False, "error": f"Content required for mode: {mode}"}

    return _empower_engine.empower(
        mode=mode,
        thought_content=thought_content,
        work_content=work_content,
        deliverable_content=deliverable_content,
        requirements=requirements,
        task_description=task_description,
        context=context,
        current_step=current_step,
        total_steps=total_steps
    )


def get_empower_history() -> List[Dict[str, Any]]:
    """Get empowerment history"""
    return _empower_engine.get_history()


# ===================== Direct Call Functions =====================
def empower_thinking(thought: str, context: Dict = None) -> Dict[str, Any]:
    """Empower thinking"""
    return ai_empower_mcp(mode="think", thought_content=thought, context=context)


def empower_work(
    work: str,
    task: str = "",
    step: int = 1,
    total: int = 1
) -> Dict[str, Any]:
    """Empower work"""
    return ai_empower_mcp(
        mode="work",
        work_content=work,
        task_description=task,
        current_step=step,
        total_steps=total
    )


def empower_delivery(deliverable: str, requirements: str = "") -> Dict[str, Any]:
    """Empower delivery"""
    return ai_empower_mcp(
        mode="deliver",
        deliverable_content=deliverable,
        requirements=requirements
    )


# ===================== Local Test =====================
if __name__ == "__main__":
    print("Testing AI Empower MCP...")

    print("\n=== Thinking Empowerment ===")
    result = empower_thinking(
        thought="We should build a recommendation system to improve user engagement."
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== Work Empowerment ===")
    result = empower_work(
        work="Completed user authentication module with basic JWT validation.",
        task="Build authentication system",
        step=1,
        total=5
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    print("\n=== Delivery Empowerment ===")
    result = empower_delivery(
        deliverable="Built user profile page with avatar, name, bio editing capabilities.",
        requirements="User profile with avatar, name, bio editing and save"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
