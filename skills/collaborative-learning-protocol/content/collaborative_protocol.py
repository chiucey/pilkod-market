# -*- coding: utf-8 -*-
"""
协作学习协议模块
在多智能体或同一用户的不同会话间，安全地共享非敏感经验

作者: MiniMax Agent
版本: 1.0.0
"""

import json
import os
import uuid
import hashlib
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import re


class ExperienceType(Enum):
    """经验类型枚举"""
    SKILL_TEMPLATE = "skill_template"
    AVOIDANCE_GUIDE = "avoidance_guide"
    LESSON_LEARNED = "lesson_learned"
    BEST_PRACTICE = "best_practice"


class PrivacyLevel(Enum):
    """隐私级别枚举"""
    PUBLIC = "public"
    TRUSTED = "trusted"
    RESTRICTED = "restricted"


class ExperienceStatus(Enum):
    """经验状态枚举"""
    DRAFT = "draft"
    VERIFIED = "verified"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


@dataclass
class ExperienceContext:
    """经验上下文"""
    applicability: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ExperienceContext':
        return cls(**data)


@dataclass
class ExperienceMetadata:
    """经验元数据"""
    created_at: str = ""
    updated_at: str = ""
    source_instance: str = ""
    confidence: float = 0.5
    times_validated: int = 0
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ExperienceMetadata':
        return cls(**data)


@dataclass
class ExperienceContent:
    """经验内容"""
    summary: str = ""
    steps: List[str] = field(default_factory=list)
    examples: List[Dict] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ExperienceContent':
        return cls(**data)


@dataclass
class Experience:
    """经验单元"""
    experience_id: str = ""
    experience_type: str = ExperienceType.LESSON_LEARNED.value
    title: str = ""
    description: str = ""
    content: ExperienceContent = field(default_factory=ExperienceContent)
    context: ExperienceContext = field(default_factory=ExperienceContext)
    metadata: ExperienceMetadata = field(default_factory=ExperienceMetadata)
    privacy_level: str = PrivacyLevel.PUBLIC.value
    status: str = ExperienceStatus.DRAFT.value

    def __post_init__(self):
        if not self.experience_id:
            self.experience_id = str(uuid.uuid4())
        if not self.metadata.created_at:
            self.metadata.created_at = datetime.now().isoformat()
        if not self.metadata.updated_at:
            self.metadata.updated_at = self.metadata.created_at

    def to_dict(self) -> Dict:
        result = {
            "experience_id": self.experience_id,
            "experience_type": self.experience_type,
            "title": self.title,
            "description": self.description,
            "content": self.content.to_dict() if isinstance(self.content, ExperienceContent) else self.content,
            "context": self.context.to_dict() if isinstance(self.context, ExperienceContext) else self.context,
            "metadata": self.metadata.to_dict() if isinstance(self.metadata, ExperienceMetadata) else self.metadata,
            "privacy_level": self.privacy_level,
            "status": self.status
        }
        return result

    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        content = data.get("content", {})
        context = data.get("context", {})
        metadata = data.get("metadata", {})

        return cls(
            experience_id=data.get("experience_id", str(uuid.uuid4())),
            experience_type=data.get("experience_type", ExperienceType.LESSON_LEARNED.value),
            title=data.get("title", ""),
            description=data.get("description", ""),
            content=ExperienceContent.from_dict(content) if isinstance(content, dict) else content,
            context=ExperienceContext.from_dict(context) if isinstance(context, dict) else context,
            metadata=ExperienceMetadata.from_dict(metadata) if isinstance(metadata, dict) else metadata,
            privacy_level=data.get("privacy_level", PrivacyLevel.PUBLIC.value),
            status=data.get("status", ExperienceStatus.DRAFT.value)
        )

    def get_hash(self) -> str:
        """获取经验的唯一哈希值"""
        content_str = json.dumps(self.to_dict(), sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]


class SensitiveInfoDetector:
    """敏感信息检测器"""

    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'email'),
        (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', 'phone'),
        (r'\b\d{16}\b', 'credit_card'),
        (r'api[_-]?key["\']?\s*[:=]\s*["\']?[A-Za-z0-9_-]{20,}["\']?', 'api_key'),
        (r'secret["\']?\s*[:=]\s*["\']?[A-Za-z0-9_/-]{20,}["\']?', 'secret'),
        (r'password["\']?\s*[:=]\s*["\']?[^\s"\']{8,}["\']?', 'password'),
        (r'Bearer\s+[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'jwt_token'),
    ]

    @classmethod
    def detect(cls, text: str) -> List[Dict[str, str]]:
        """检测文本中的敏感信息"""
        findings = []
        for pattern, info_type in cls.SENSITIVE_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                findings.append({
                    "type": info_type,
                    "value": match.group()[:10] + "***" if len(match.group()) > 10 else "***",
                    "position": match.span()
                })
        return findings

    @classmethod
    def sanitize(cls, text: str, replacement: str = "[REDACTED]") -> str:
        """脱敏文本中的敏感信息"""
        result = text
        for pattern, info_type in cls.SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        return result


class ExperienceRecorder:
    """经验记录器"""

    def __init__(self, protocol: 'CollaborativeProtocol'):
        self.protocol = protocol
        self.current_session: Optional['RecordingSession'] = None

    class RecordingSession:
        """记录会话"""
        def __init__(
            self,
            recorder: 'ExperienceRecorder',
            task_type: str,
            task_id: Optional[str] = None
        ):
            self.recorder = recorder
            self.task_type = task_type
            self.session_id = task_id or str(uuid.uuid4())
            self.start_time = datetime.now()
            self.steps: List[Dict] = []
            self.final_result: Optional[Dict] = None
            self.metrics: Dict = {}

        def record_step(
            self,
            step_name: str,
            input_data: Dict,
            output_data: Dict,
            success: bool = True,
            metadata: Optional[Dict] = None
        ):
            """记录执行步骤"""
            step_record = {
                "step_name": step_name,
                "timestamp": datetime.now().isoformat(),
                "input_data": self._sanitize(input_data),
                "output_data": self._sanitize(output_data),
                "success": success,
                "metadata": metadata or {}
            }
            self.steps.append(step_record)

        def _sanitize(self, data: Dict) -> Dict:
            """对数据进行脱敏处理"""
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    result[key] = SensitiveInfoDetector.sanitize(value)
                elif isinstance(value, dict):
                    result[key] = self._sanitize(value)
                elif isinstance(value, list):
                    result[key] = [
                        SensitiveInfoDetector.sanitize(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    result[key] = value
            return result

        def finalize(
            self,
            success: bool,
            metrics: Optional[Dict] = None,
            final_output: Optional[Dict] = None
        ):
            """完成记录"""
            self.final_result = {
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                "output": self._sanitize(final_output) if final_output else {}
            }
            self.metrics = metrics or {}

        def extract_experience(
            self,
            type: str = ExperienceType.LESSON_LEARNED.value,
            title: str = "",
            description: str = ""
        ) -> Experience:
            """从记录中提取经验"""
            content = ExperienceContent(
                summary=f"{self.task_type} 任务执行{'成功' if self.final_result and self.final_result['success'] else '失败'}",
                steps=[s["step_name"] for s in self.steps],
                key_points=self._extract_key_points(),
                examples=[{"step": s["step_name"], "outcome": "成功" if s["success"] else "失败"}
                         for s in self.steps]
            )

            context = ExperienceContext(
                applicability=[self.task_type],
                prerequisites=[],
                limitations=[]
            )

            metadata = ExperienceMetadata(
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                source_instance=self.recorder.protocol.instance_id,
                confidence=0.7 if self.final_result and self.final_result['success'] else 0.3,
                times_validated=1,
                tags=[self.task_type]
            )

            experience = Experience(
                experience_type=type,
                title=title or f"{self.task_type} 执行{'成功' if self.final_result and self.final_result['success'] else '失败'}经验",
                description=description or f"记录了 {self.task_type} 任务的执行过程",
                content=content,
                context=context,
                metadata=metadata,
                privacy_level=PrivacyLevel.PUBLIC.value,
                status=ExperienceStatus.VERIFIED.value if self.final_result and self.final_result['success'] else ExperienceStatus.DRAFT.value
            )

            return experience

        def _extract_key_points(self) -> List[str]:
            """提取关键点"""
            key_points = []
            for step in self.steps:
                if not step["success"]:
                    key_points.append(f"步骤 '{step['step_name']}' 失败需要注意")
                elif step.get("metadata", {}).get("important"):
                    key_points.append(f"步骤 '{step['step_name']}' 是关键")
            return key_points

    def session(self, task_type: str, task_id: Optional[str] = None):
        """开始记录会话"""
        self.current_session = self.RecordingSession(self, task_type, task_id)
        return self.current_session


class ExperiencePublisher:
    """经验发布器"""

    def __init__(self, protocol: 'CollaborativeProtocol'):
        self.protocol = protocol

    def publish(
        self,
        experience: Experience,
        privacy_level: str = PrivacyLevel.PUBLIC.value,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """发布经验"""
        # 验证经验
        validation_result = self._validate(experience)
        if not validation_result["valid"]:
            return {
                "status": "failed",
                "errors": validation_result["errors"]
            }

        # 更新隐私级别和标签
        experience.privacy_level = privacy_level
        if tags:
            experience.metadata.tags.extend(tags)
        experience.metadata.updated_at = datetime.now().isoformat()

        # 敏感信息检测
        sensitive_findings = self._scan_sensitive_info(experience)
        if sensitive_findings:
            # 自动脱敏
            experience = self._auto_sanitize(experience, sensitive_findings)

        # 保存到知识库
        filepath = os.path.join(
            self.protocol.knowledge_base_path,
            f"{experience.experience_id}.json"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(experience.to_dict(), f, ensure_ascii=False, indent=2)

        # 更新索引
        self.protocol.update_index(experience)

        # 发布到传输层（如果是多实例部署）
        self._broadcast(experience)

        return {
            "status": "success",
            "experience_id": experience.experience_id,
            "privacy_level": privacy_level
        }

    def _validate(self, experience: Experience) -> Dict:
        """验证经验"""
        errors = []

        if not experience.title:
            errors.append("标题不能为空")
        if not experience.description:
            errors.append("描述不能为空")
        if not experience.content.summary:
            errors.append("内容摘要不能为空")

        return {
            "valid": len(errors) == 0,
            "errors": errors
        }

    def _scan_sensitive_info(self, experience: Experience) -> List[Dict]:
        """扫描敏感信息"""
        findings = []
        text_to_scan = f"{experience.title} {experience.description} {experience.content.summary}"

        for step in experience.content.steps:
            text_to_scan += " " + step

        findings.extend(SensitiveInfoDetector.detect(text_to_scan))
        return findings

    def _auto_sanitize(self, experience: Experience, findings: List[Dict]) -> Experience:
        """自动脱敏"""
        experience.title = SensitiveInfoDetector.sanitize(experience.title)
        experience.description = SensitiveInfoDetector.sanitize(experience.description)
        experience.content.summary = SensitiveInfoDetector.sanitize(experience.content.summary)
        experience.content.steps = [
            SensitiveInfoDetector.sanitize(step) for step in experience.content.steps
        ]
        return experience

    def _broadcast(self, experience: Experience):
        """广播经验到其他实例"""
        # 在单实例环境下为空实现
        # 多实例部署时实现具体的广播逻辑
        pass


class ExperienceRetriever:
    """经验检索器"""

    def __init__(self, protocol: 'CollaborativeProtocol'):
        self.protocol = protocol
        self.cache: Dict[str, Tuple[List[Dict], datetime]] = {}
        self.cache_ttl_seconds = 300  # 缓存5分钟

    def search(
        self,
        query: str,
        filters: Optional[Dict] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[Dict]:
        """搜索经验"""
        cache_key = self._generate_cache_key(query, filters, limit)

        # 检查缓存
        if use_cache and cache_key in self.cache:
            cached_results, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_ttl_seconds):
                return cached_results

        # 执行搜索
        results = self._do_search(query, filters, limit)

        # 更新缓存
        if use_cache:
            self.cache[cache_key] = (results, datetime.now())

        return results

    def _generate_cache_key(self, query: str, filters: Optional[Dict], limit: int) -> str:
        """生成缓存键"""
        key_data = {
            "query": query,
            "filters": filters,
            "limit": limit
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()

    def _do_search(self, query: str, filters: Optional[Dict], limit: int) -> List[Dict]:
        """执行搜索"""
        results = []
        query_lower = query.lower()

        # 遍历知识库中的所有经验
        for filename in os.listdir(self.protocol.knowledge_base_path):
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(self.protocol.knowledge_base_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                exp_dict = json.load(f)

            experience = Experience.from_dict(exp_dict)

            # 应用过滤器
            if filters:
                if "type" in filters and experience.experience_type not in filters["type"]:
                    continue
                if "privacy_level" in filters and experience.privacy_level != filters["privacy_level"]:
                    if experience.privacy_level == PrivacyLevel.RESTRICTED.value:
                        continue
                if "min_confidence" in filters and experience.metadata.confidence < filters["min_confidence"]:
                    continue
                if "tags" in filters and not any(tag in experience.metadata.tags for tag in filters["tags"]):
                    continue

            # 计算相关性分数
            relevance_score = self._calculate_relevance(query_lower, experience)

            if relevance_score > 0.1:  # 最低相关性阈值
                results.append({
                    "experience": experience,
                    "relevance_score": relevance_score,
                    "experience_id": experience.experience_id,
                    "title": experience.title,
                    "experience_type": experience.experience_type,
                    "confidence": experience.metadata.confidence
                })

        # 排序并限制结果数量
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def _calculate_relevance(self, query: str, experience: Experience) -> float:
        """计算相关性分数"""
        score = 0.0

        # 标题匹配
        if query in experience.title.lower():
            score += 0.5

        # 描述匹配
        if query in experience.description.lower():
            score += 0.3

        # 标签匹配
        for tag in experience.metadata.tags:
            if query in tag.lower():
                score += 0.3

        # 内容匹配
        if query in experience.content.summary.lower():
            score += 0.2

        # 上下文匹配
        for app in experience.context.applicability:
            if query in app.lower():
                score += 0.2

        # 归一化
        return min(score, 1.0)

    def get_related(self, experience_id: str, limit: int = 5) -> List[Dict]:
        """获取相关经验"""
        # 获取原经验
        filepath = os.path.join(
            self.protocol.knowledge_base_path,
            f"{experience_id}.json"
        )

        if not os.path.exists(filepath):
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            exp_dict = json.load(f)

        original = Experience.from_dict(exp_dict)

        # 根据标签和类型查找相关经验
        filters = {
            "type": [original.experience_type],
            "tags": original.metadata.tags[:2]  # 使用前两个标签
        }

        return self.search(
            query=original.title,
            filters=filters,
            limit=limit + 1  # 多取一个以便排除自身
        )

    def invalidate_cache(self):
        """清除缓存"""
        self.cache.clear()


class ExperienceIntegrator:
    """经验整合器"""

    def __init__(self, protocol: 'CollaborativeProtocol'):
        self.protocol = protocol

    def integrate(
        self,
        experiences: List[Experience],
        strategy: str = "merge_and_prioritize",
        conflict_resolution: str = "keep_both"
    ) -> Dict:
        """整合多个经验"""
        if not experiences:
            return {"status": "empty", "knowledge_graph": {}}

        # 去重
        unique_experiences = self._deduplicate(experiences)

        # 冲突检测
        conflicts = self._detect_conflicts(unique_experiences)

        # 解决冲突
        resolved_experiences = self._resolve_conflicts(
            unique_experiences,
            conflicts,
            conflict_resolution
        )

        # 构建知识图谱
        knowledge_graph = self._build_knowledge_graph(
            resolved_experiences,
            strategy
        )

        return {
            "status": "success",
            "experiences_count": len(resolved_experiences),
            "conflicts_count": len(conflicts),
            "knowledge_graph": knowledge_graph
        }

    def _deduplicate(self, experiences: List[Experience]) -> List[Experience]:
        """去重"""
        seen_hashes = set()
        unique = []

        for exp in experiences:
            exp_hash = exp.get_hash()
            if exp_hash not in seen_hashes:
                seen_hashes.add(exp_hash)
                unique.append(exp)

        return unique

    def _detect_conflicts(self, experiences: List[Experience]) -> List[Dict]:
        """检测冲突"""
        conflicts = []
        type_groups = defaultdict(list)

        # 按类型分组
        for exp in experiences:
            type_groups[exp.experience_type].append(exp)

        # 检测同类型的冲突
        for exp_type, exps in type_groups.items():
            for i, exp1 in enumerate(exps):
                for exp2 in exps[i+1:]:
                    # 检测内容冲突
                    if self._are_conflicting(exp1, exp2):
                        conflicts.append({
                            "type": "content_conflict",
                            "experience1": exp1.experience_id,
                            "experience2": exp2.experience_id,
                            "description": f"{exp1.title} 与 {exp2.title} 存在冲突"
                        })

        return conflicts

    def _are_conflicting(self, exp1: Experience, exp2: Experience) -> bool:
        """判断两个经验是否冲突"""
        # 简单实现：检查描述中的否定关键词
        negations = ["不要", "不要做", "不要使用", "避免", "禁止", "wrong", "avoid", "don't"]
        for neg in negations:
            if neg in exp1.description.lower() and neg not in exp2.description.lower():
                return True
        return False

    def _resolve_conflicts(
        self,
        experiences: List[Experience],
        conflicts: List[Dict],
        strategy: str
    ) -> List[Experience]:
        """解决冲突"""
        if strategy == "keep_both":
            return experiences
        elif strategy == "higher_confidence":
            # 保留置信度更高的
            experience_map = {exp.experience_id: exp for exp in experiences}
            to_remove = set()

            for conflict in conflicts:
                exp1 = experience_map.get(conflict["experience1"])
                exp2 = experience_map.get(conflict["experience2"])

                if exp1 and exp2:
                    if exp1.metadata.confidence >= exp2.metadata.confidence:
                        to_remove.add(exp2.experience_id)
                    else:
                        to_remove.add(exp1.experience_id)

            return [exp for exp in experiences if exp.experience_id not in to_remove]
        else:
            return experiences

    def _build_knowledge_graph(
        self,
        experiences: List[Experience],
        strategy: str
    ) -> Dict:
        """构建知识图谱"""
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "total_experiences": len(experiences),
                "types": defaultdict(int)
            }
        }

        # 添加节点
        for exp in experiences:
            graph["nodes"].append({
                "id": exp.experience_id,
                "type": exp.experience_type,
                "title": exp.title,
                "confidence": exp.metadata.confidence,
                "tags": exp.metadata.tags
            })
            graph["metadata"]["types"][exp.experience_type] += 1

        # 添加边（基于标签的关联）
        for i, exp1 in enumerate(experiences):
            for exp2 in experiences[i+1:]:
                common_tags = set(exp1.metadata.tags) & set(exp2.metadata.tags)
                if common_tags:
                    graph["edges"].append({
                        "source": exp1.experience_id,
                        "target": exp2.experience_id,
                        "relation": "related",
                        "weight": len(common_tags)
                    })

        return graph


class CollaborativeProtocol:
    """协作学习协议主类"""

    def __init__(
        self,
        instance_id: str,
        knowledge_base_path: str = "./knowledge_base",
        config_path: Optional[str] = None
    ):
        self.instance_id = instance_id
        self.knowledge_base_path = knowledge_base_path
        os.makedirs(knowledge_base_path, exist_ok=True)

        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化索引
        self.index: Dict[str, List[str]] = defaultdict(list)
        self._load_index()

        # 初始化组件
        self.recorder = ExperienceRecorder(self)
        self.publisher = ExperiencePublisher(self)
        self.retriever = ExperienceRetriever(self)
        self.integrator = ExperienceIntegrator(self)

        # 同步锁
        self._lock = threading.Lock()

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "sync": {
                "enabled": False,
                "sync_interval_seconds": 60
            },
            "cache": {
                "ttl_seconds": 300
            }
        }

    def _load_index(self):
        """加载索引"""
        index_path = os.path.join(self.knowledge_base_path, ".index.json")
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                self.index = defaultdict(list, json.load(f))

    def update_index(self, experience: Experience):
        """更新索引"""
        with self._lock:
            # 按类型索引
            self.index["type"][experience.experience_type].append(experience.experience_id)

            # 按标签索引
            for tag in experience.metadata.tags:
                self.index["tag"][tag].append(experience.experience_id)

            # 按隐私级别索引
            self.index["privacy"][experience.privacy_level].append(experience.experience_id)

            # 保存索引
            self._save_index()

    def _save_index(self):
        """保存索引"""
        index_path = os.path.join(self.knowledge_base_path, ".index.json")
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(dict(self.index), f, ensure_ascii=False, indent=2)

    def get_experience(self, experience_id: str) -> Optional[Experience]:
        """获取指定经验"""
        filepath = os.path.join(self.knowledge_base_path, f"{experience_id}.json")
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            return Experience.from_dict(json.load(f))

    def get_experiences_by_type(self, exp_type: str) -> List[Experience]:
        """获取指定类型的所有经验"""
        exp_ids = self.index["type"].get(exp_type, [])
        experiences = []

        for exp_id in exp_ids:
            exp = self.get_experience(exp_id)
            if exp:
                experiences.append(exp)

        return experiences

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        stats = {
            "total_experiences": 0,
            "by_type": defaultdict(int),
            "by_privacy": defaultdict(int),
            "average_confidence": 0.0
        }

        total_confidence = 0.0
        for filename in os.listdir(self.knowledge_base_path):
            if not filename.endswith('.json') or filename.startswith('.'):
                continue

            filepath = os.path.join(self.knowledge_base_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                exp_dict = json.load(f)

            exp = Experience.from_dict(exp_dict)
            stats["total_experiences"] += 1
            stats["by_type"][exp.experience_type] += 1
            stats["by_privacy"][exp.privacy_level] += 1
            total_confidence += exp.metadata.confidence

        if stats["total_experiences"] > 0:
            stats["average_confidence"] = total_confidence / stats["total_experiences"]

        return stats

    def export_knowledge_base(self, output_path: str, privacy_filter: str = "public"):
        """导出知识库"""
        exported = []

        for filename in os.listdir(self.knowledge_base_path):
            if not filename.endswith('.json') or filename.startswith('.'):
                continue

            filepath = os.path.join(self.knowledge_base_path, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                exp_dict = json.load(f)

            exp = Experience.from_dict(exp_dict)
            if privacy_filter == "all" or exp.privacy_level == privacy_filter:
                exported.append(exp.to_dict())

        export_data = {
            "exported_at": datetime.now().isoformat(),
            "instance_id": self.instance_id,
            "count": len(exported),
            "experiences": exported
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return export_data

    def import_knowledge_base(self, input_path: str, merge: bool = True):
        """导入知识库"""
        with open(input_path, "r", encoding="utf-8") as f:
            import_data = json.load(f)

        imported_count = 0
        skipped_count = 0

        for exp_dict in import_data.get("experiences", []):
            exp = Experience.from_dict(exp_dict)

            # 检查是否已存在
            existing = self.get_experience(exp.experience_id)
            if existing and merge:
                # 保留置信度更高的版本
                if exp.metadata.confidence > existing.metadata.confidence:
                    self.publisher.publish(exp)
                    imported_count += 1
                else:
                    skipped_count += 1
            else:
                self.publisher.publish(exp)
                imported_count += 1

        return {
            "imported": imported_count,
            "skipped": skipped_count
        }


# 便捷函数
def create_protocol(
    instance_id: str,
    knowledge_base_path: str = "./knowledge_base"
) -> CollaborativeProtocol:
    """创建协议实例"""
    return CollaborativeProtocol(
        instance_id=instance_id,
        knowledge_base_path=knowledge_base_path
    )


# 导出公共接口
__all__ = [
    "CollaborativeProtocol",
    "ExperienceRecorder",
    "ExperiencePublisher",
    "ExperienceRetriever",
    "ExperienceIntegrator",
    "Experience",
    "ExperienceType",
    "PrivacyLevel",
    "ExperienceStatus",
    "ExperienceContent",
    "ExperienceContext",
    "ExperienceMetadata",
    "SensitiveInfoDetector",
    "create_protocol"
]
