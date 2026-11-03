"""
Taste Standard - 品味标准引擎

构建用户的主观评价体系，让AI输出更符合用户审美
核心思想: 用户对"好"的定义不是固定的，而是通过交互逐渐清晰和强化
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict
from dataclasses import asdict, field

from models import (
    TasteProfile, DomainTaste, QualityStandard, StylePreference,
    EvaluationResult
)


class DomainClassifier:
    """领域分类器"""

    DOMAIN_PATTERNS = {
        'code_generation': {
            'keywords': ['代码', '函数', '类', '实现', '编程', '开发', 'code', 'function', 'class'],
            'indicators': ['import', 'def ', 'class ', '=>', '->']
        },
        'writing': {
            'keywords': ['写作', '文章', '报告', '文档', '写', '内容', 'write', 'article', 'report'],
            'indicators': ['。', '，', '！', '？', 'Paragraph']
        },
        'analysis': {
            'keywords': ['分析', '研究', '评估', '比较', '研究', 'analyze', 'research', 'evaluate'],
            'indicators': ['分析', '结论', '结果', '数据']
        },
        'creative': {
            'keywords': ['创作', '创意', '故事', '诗歌', '设计', 'create', 'story', 'poem', 'design'],
            'indicators': ['创意', '灵感', '想象']
        },
        'data_processing': {
            'keywords': ['数据', '处理', '转换', '清洗', 'data', 'process', 'transform'],
            'indicators': ['csv', 'json', '表格', 'dataframe']
        },
        'general': {
            'keywords': [],
            'indicators': []
        }
    }

    def identify(self, feedback_history: List[Dict]) -> List[str]:
        """
        从反馈历史中识别相关领域

        Returns:
            List[str]: 识别出的领域列表
        """
        domain_scores = defaultdict(float)

        for feedback in feedback_history:
            content = str(feedback.get('content', ''))
            domain = self.classify_text(content)

            # 基于置信度加权
            confidence = feedback.get('confidence', 1.0)
            domain_scores[domain] += confidence

        # 排序并返回top领域
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        return [d[0] for d in sorted_domains[:3]] if sorted_domains else ['general']

    def classify_text(self, text: str) -> str:
        """
        分类文本所属领域

        Args:
            text: 待分类文本

        Returns:
            str: 领域名称
        """
        text_lower = text.lower()
        scores = {}

        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = 0

            # 关键词匹配
            for keyword in patterns['keywords']:
                if keyword.lower() in text_lower:
                    score += 2

            # 指标匹配
            for indicator in patterns['indicators']:
                if indicator in text:
                    score += 1

            scores[domain] = score

        # 返回最高分领域
        if scores:
            best_domain = max(scores.items(), key=lambda x: x[1])
            if best_domain[1] > 0:
                return best_domain[0]

        return 'general'


class QualityEvaluator:
    """质量评估器"""

    def evaluate_relevance(self, output: Any, context: Dict, domain_taste: DomainTaste) -> float:
        """
        评估输出相关性

        Args:
            output: 待评估输出
            context: 上下文信息
            domain_taste: 领域品味标准

        Returns:
            float: 相关性分数 (0-1)
        """
        # 获取相关质量标准
        relevance_standard = None
        for standard in domain_taste.quality_standards:
            if standard.dimension == 'relevance':
                relevance_standard = standard
                break

        if not relevance_standard:
            return 0.7  # 默认值

        # 简化实现：基于关键词匹配
        score = 0.7

        output_text = str(output).lower()
        context_text = context.get('task', '').lower()

        # 检查核心关键词是否出现在输出中
        if context_text:
            keywords = self._extract_keywords(context_text)
            matched = sum(1 for kw in keywords if kw in output_text)
            score = 0.5 + (matched / max(len(keywords), 1)) * 0.3

        return min(1.0, max(0.0, score))

    def evaluate_quality_perception(
        self,
        output: Any,
        quality_standards: List[QualityStandard]
    ) -> float:
        """
        评估质量感知

        Args:
            output: 待评估输出
            quality_standards: 质量标准列表

        Returns:
            float: 质量感知分数 (0-1)
        """
        scores = []

        for standard in quality_standards:
            dimension_score = self._evaluate_dimension(output, standard)
            # 加权
            weighted_score = dimension_score * standard.weight
            scores.append(weighted_score)

        return sum(scores) if scores else 0.7

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取长度>2的词
        words = re.findall(r'[\w\u4e00-\u9fff]{3,}', text)
        return list(set(words))[:10]

    def _evaluate_dimension(self, output: Any, standard: QualityStandard) -> float:
        """评估单个维度"""
        output_text = str(output)

        if standard.dimension == 'clarity':
            # 清晰度：检查是否包含过多复杂句式
            sentences = re.split(r'[。!?\n]', output_text)
            avg_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
            if avg_length < 50:
                return 0.9
            elif avg_length < 100:
                return 0.7
            else:
                return 0.5

        elif standard.dimension == 'readability':
            # 可读性：检查结构化程度
            has_structure = any(marker in output_text for marker in ['#', '1.', '2.', '-', '*', '•'])
            return 0.9 if has_structure else 0.6

        elif standard.dimension == 'efficiency':
            # 效率：检查冗余度
            if len(output_text) < 500:
                return 0.9
            elif len(output_text) < 2000:
                return 0.7
            else:
                return 0.5

        return 0.7  # 默认


class StyleMatcher:
    """风格匹配器"""

    STYLE_PATTERNS = {
        'modern_pythonic': {
            'naming': [r'^[a-z][a-z0-9_]*$', r'^[a-z][a-z0-9_]*s?$'],
            'structure': ['def ', 'class ', 'return'],
            'indicators': ['snake_case', 'list comprehension', 'with statement']
        },
        'formal': {
            'naming': [r'^[A-Z][a-zA-Z]+$'],
            'structure': ['# ', '## ', '### '],
            'indicators': ['正式', '请', '本']
        },
        'casual': {
            'naming': [],
            'structure': [],
            'indicators': ['简单', 'ok', '好的', '随便']
        }
    }

    def match(self, output: Any, target_style: StylePreference) -> float:
        """
        匹配目标风格

        Args:
            output: 待匹配输出
            target_style: 目标风格偏好

        Returns:
            float: 风格匹配分数 (0-1)
        """
        output_text = str(output)
        style_score = 0.0
        match_count = 0

        # 检查命名约定
        if target_style.naming_convention == 'snake_case':
            if re.search(r'[a-z][a-z0-9_]*[a-z0-9]', output_text):
                style_score += 0.3
                match_count += 1

        # 检查注释风格
        if target_style.comment_style == 'minimal':
            comment_count = output_text.count('#') + output_text.count('//')
            if comment_count < 5:
                style_score += 0.2
                match_count += 1

        # 检查结构风格
        if target_style.structure == 'functional':
            if 'def ' in output_text and 'return' in output_text:
                style_score += 0.3
                match_count += 1

        # 检查voice
        if target_style.voice == 'active':
            passive_count = output_text.lower().count('被') + output_text.lower().count('by ')
            if passive_count < 3:
                style_score += 0.2
                match_count += 1

        return style_score if match_count > 0 else 0.5

    def detect_style(self, output: Any) -> str:
        """检测输出风格"""
        output_text = str(output)

        for style_name, patterns in self.STYLE_PATTERNS.items():
            match_score = 0

            for indicator in patterns['indicators']:
                if indicator.lower() in output_text.lower():
                    match_score += 1

            if match_score >= 2:
                return style_name

        return 'default'


class StandardCalibrator:
    """标准校准器"""

    def __init__(self):
        self.calibration_history: Dict[str, List[float]] = defaultdict(list)

    def calibrate(self, taste_profile: TasteProfile) -> TasteProfile:
        """
        跨领域一致性校准

        Args:
            taste_profile: 待校准的品味画像

        Returns:
            TasteProfile: 校准后的品味画像
        """
        # 计算跨领域一致性
        consistency = self._calculate_consistency(taste_profile)
        taste_profile.cross_domain_consistency = consistency

        # 调整学习置信度
        total_samples = sum(
            dt.sample_count for dt in taste_profile.domains.values()
        )
        if total_samples > 50:
            taste_profile.learning_confidence = 'high'
        elif total_samples > 10:
            taste_profile.learning_confidence = 'medium'
        else:
            taste_profile.learning_confidence = 'low'

        # 校准权重
        self._calibrate_weights(taste_profile)

        return taste_profile

    def _calculate_consistency(self, profile: TasteProfile) -> float:
        """计算一致性分数"""
        if len(profile.domains) < 2:
            return 1.0

        # 提取共同维度
        common_dimensions = set()
        for domain_taste in profile.domains.values():
            for standard in domain_taste.quality_standards:
                common_dimensions.add(standard.dimension)

        # 计算维度权重的一致性
        dimension_weights = {}
        for dim in common_dimensions:
            weights = []
            for domain_taste in profile.domains.values():
                for standard in domain_taste.quality_standards:
                    if standard.dimension == dim:
                        weights.append(standard.weight)
            if weights:
                dimension_weights[dim] = weights

        # 计算权重的方差（方差越小一致性越高）
        if not dimension_weights:
            return 0.7

        variances = []
        for dim, weights in dimension_weights.items():
            if len(weights) > 1:
                mean = sum(weights) / len(weights)
                variance = sum((w - mean) ** 2 for w in weights) / len(weights)
                variances.append(variance)

        avg_variance = sum(variances) / len(variances) if variances else 0
        consistency = max(0, 1 - avg_variance * 5)

        return consistency

    def _calibrate_weights(self, profile: TasteProfile) -> None:
        """校准各领域权重"""
        for domain, taste in profile.domains.items():
            # 确保权重和为1
            total_weight = sum(s.weight for s in taste.quality_standards)
            if total_weight > 0:
                for standard in taste.quality_standards:
                    standard.weight /= total_weight


class TasteStandard:
    """品味标准主引擎"""

    def __init__(self):
        self.domain_classifier = DomainClassifier()
        self.quality_evaluator = QualityEvaluator()
        self.style_matcher = StyleMatcher()
        self.calibrator = StandardCalibrator()
        self.taste_profiles: Dict[str, TasteProfile] = {}

    async def establish_taste(self, user_id: str, feedback_history: List[Dict]) -> TasteProfile:
        """
        建立用户品味标准

        Args:
            user_id: 用户标识
            feedback_history: 历史反馈数据

        Returns:
            TasteProfile: 完整的品味画像
        """
        # 领域识别
        domains = self.domain_classifier.identify(feedback_history)

        # 每个领域建立独立标准
        taste_profile = TasteProfile(user_id=user_id)

        for domain in domains:
            domain_taste = await self._build_domain_taste(domain, feedback_history)
            taste_profile.add_domain(domain, domain_taste)

        # 跨域一致性校准
        taste_profile = self.calibrator.calibrate(taste_profile)

        # 存储
        self.taste_profiles[user_id] = taste_profile

        return taste_profile

    async def _build_domain_taste(self, domain: str,
                                   feedback_history: List[Dict]) -> DomainTaste:
        """为特定领域构建品味标准"""
        # 获取该领域的反馈
        domain_feedback = [
            f for f in feedback_history
            if f.get('domain') == domain
        ]

        # 如果没有该领域的反馈，使用默认标准
        if not domain_feedback:
            return self._default_domain_taste(domain)

        # 分析反馈，提取质量标准和风格偏好
        quality_standards = self._extract_quality_standards(domain_feedback)
        style_preferences = self._extract_style_preferences(domain_feedback)
        rejection_patterns = self._extract_rejection_patterns(domain_feedback)
        acceptance_patterns = self._extract_acceptance_patterns(domain_feedback)

        # 计算置信度
        confidence = min(1.0, len(domain_feedback) / 20)

        return DomainTaste(
            domain=domain,
            quality_standards=quality_standards,
            style_preferences=style_preferences,
            rejection_patterns=rejection_patterns,
            acceptance_patterns=acceptance_patterns,
            confidence=confidence,
            sample_count=len(domain_feedback)
        )

    def _default_domain_taste(self, domain: str) -> DomainTaste:
        """返回默认领域品味"""
        if domain == 'code_generation':
            return DomainTaste(
                domain=domain,
                quality_standards=[
                    QualityStandard(dimension='readability', weight=0.3, target='high'),
                    QualityStandard(dimension='efficiency', weight=0.3, target='optimal'),
                    QualityStandard(dimension='documentation', weight=0.2, target='minimal')
                ],
                style_preferences=StylePreference(
                    naming_convention='snake_case',
                    comment_style='sparse',
                    structure='functional'
                ),
                rejection_patterns=['over_engineered', 'unnecessary_abstraction'],
                acceptance_patterns=['clean', 'efficient', 'readable'],
                confidence=0.5,
                sample_count=0
            )
        elif domain == 'writing':
            return DomainTaste(
                domain=domain,
                quality_standards=[
                    QualityStandard(dimension='clarity', weight=0.4, target='high'),
                    QualityStandard(dimension='conciseness', weight=0.3, target='moderate'),
                    QualityStandard(dimension='depth', weight=0.3, target='balanced')
                ],
                style_preferences=StylePreference(
                    voice='active',
                    sentence_length='varied',
                    structure='hierarchical'
                ),
                rejection_patterns=['verbose', 'redundant'],
                acceptance_patterns=['clear', 'concise', 'well-structured'],
                confidence=0.5,
                sample_count=0
            )
        else:
            return DomainTaste(
                domain=domain,
                quality_standards=[
                    QualityStandard(dimension='relevance', weight=0.5, target='high'),
                    QualityStandard(dimension='accuracy', weight=0.5, target='high')
                ],
                style_preferences=StylePreference(),
                confidence=0.5,
                sample_count=0
            )

    def _extract_quality_standards(self, feedback: List[Dict]) -> List[QualityStandard]:
        """从反馈中提取质量标准"""
        # 简化实现：基于反馈类型推断
        standards = []

        # 统计反馈中的维度提及
        dimension_mentions = defaultdict(int)
        for f in feedback:
            content = str(f.get('content', ''))
            for dim in ['clarity', 'accuracy', 'relevance', 'efficiency', 'readability']:
                if dim in content.lower():
                    dimension_mentions[dim] += 1

        # 将提及转换为标准
        total_mentions = sum(dimension_mentions.values()) or 1
        for dim, count in dimension_mentions.items():
            standards.append(QualityStandard(
                dimension=dim,
                weight=count / total_mentions,
                target='high'
            ))

        # 确保至少有默认标准
        if not standards:
            standards.append(QualityStandard(
                dimension='relevance',
                weight=1.0,
                target='high'
            ))

        return standards

    def _extract_style_preferences(self, feedback: List[Dict]) -> StylePreference:
        """从反馈中提取风格偏好"""
        # 简化实现：基于反馈推断
        style = StylePreference()

        for f in feedback:
            content = str(f.get('content', ''))

            if 'snake_case' in content or 'python' in content:
                style.naming_convention = 'snake_case'
            elif 'camelCase' in content:
                style.naming_convention = 'camelCase'

            if 'minimal' in content or 'less comments' in content:
                style.comment_style = 'minimal'
            elif 'documented' in content:
                style.comment_style = 'detailed'

        return style

    def _extract_rejection_patterns(self, feedback: List[Dict]) -> List[str]:
        """提取拒绝模式"""
        patterns = []
        for f in feedback:
            if f.get('accepted') == False:
                patterns.extend(f.get('reasons', []))
        return list(set(patterns))

    def _extract_acceptance_patterns(self, feedback: List[Dict]) -> List[str]:
        """提取接受模式"""
        patterns = []
        for f in feedback:
            if f.get('accepted') == True:
                patterns.extend(f.get('reasons', []))
        return list(set(patterns))

    async def evaluate_output(
        self,
        output: Any,
        context: Dict,
        taste_profile: Optional[TasteProfile] = None,
        user_id: Optional[str] = None
    ) -> EvaluationResult:
        """
        使用品味标准评估输出

        Args:
            output: 待评估输出
            context: 上下文信息
            taste_profile: 品味画像（可选）
            user_id: 用户ID（如果profile未提供）

        Returns:
            EvaluationResult: 评估结果
        """
        # 获取品味画像
        if not taste_profile and user_id:
            taste_profile = self.taste_profiles.get(user_id)

        if not taste_profile:
            # 返回默认评估
            return EvaluationResult(
                taste_score=0.7,
                dimension_scores={'default': 0.7},
                suggestions=['Please establish taste profile first'],
                confidence=0.0
            )

        # 获取相关领域
        domain = context.get('domain', self.domain_classifier.classify_text(str(output)))
        domain_taste = taste_profile.get_domain_taste(domain)

        if not domain_taste:
            domain_taste = self._default_domain_taste(domain)

        # 多维度评估
        relevance_score = self.quality_evaluator.evaluate_relevance(
            output, context, domain_taste
        )
        style_score = self.style_matcher.match(output, domain_taste.style_preferences)
        quality_score = self.quality_evaluator.evaluate_quality_perception(
            output, domain_taste.quality_standards
        )

        scores = {
            'relevance': relevance_score,
            'style_match': style_score,
            'quality_perception': quality_score
        }

        # 获取权重
        weights = {}
        for standard in domain_taste.quality_standards:
            weights[standard.dimension] = standard.weight

        # 添加style权重（如果没有）
        if 'style_match' not in weights:
            weights['style_match'] = 0.2

        # 计算综合评分
        taste_score = sum(scores[k] * weights.get(k, 1/len(scores))
                          for k in scores)

        # 生成改进建议
        suggestions = self._generate_suggestions(scores, domain_taste)

        return EvaluationResult(
            taste_score=taste_score,
            dimension_scores=scores,
            suggestions=suggestions,
            confidence=domain_taste.confidence
        )

    def _generate_suggestions(self, scores: Dict[str, float],
                             domain_taste: DomainTaste) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for dim, score in scores.items():
            if score < 0.6:
                if dim == 'relevance':
                    suggestions.append('Ensure output directly addresses the request')
                elif dim == 'style_match':
                    suggestions.append('Adjust formatting to match user preferences')
                elif dim == 'quality_perception':
                    suggestions.append('Improve clarity and structure')

        return suggestions

    async def update_from_feedback(
        self,
        output: Any,
        user_feedback: Dict,
        context: Dict
    ) -> None:
        """
        从用户反馈中更新品味标准

        Args:
            output: 系统输出
            user_feedback: 用户反馈
            context: 上下文信息
        """
        user_id = user_feedback.get('user_id')
        if not user_id or user_id not in self.taste_profiles:
            return

        taste_profile = self.taste_profiles[user_id]
        domain = context.get('domain', 'general')

        # 获取领域品味
        domain_taste = taste_profile.get_domain_taste(domain)
        if not domain_taste:
            domain_taste = self._default_domain_taste(domain)
            taste_profile.add_domain(domain, domain_taste)

        # 解析反馈
        if user_feedback.get('accepted'):
            # 更新接受模式
            for pattern in self.style_matcher.detect_style(output):
                if pattern not in domain_taste.acceptance_patterns:
                    domain_taste.acceptance_patterns.append(pattern)
        elif user_feedback.get('rejected'):
            # 更新拒绝模式
            for pattern in self.style_matcher.detect_style(output):
                if pattern not in domain_taste.rejection_patterns:
                    domain_taste.rejection_patterns.append(pattern)

        # 更新样本数
        domain_taste.sample_count += 1
        taste_profile.updated_at = datetime.now()

        # 重新校准
        taste_profile = self.calibrator.calibrate(taste_profile)

    def get_taste_profile(self, user_id: str) -> Optional[TasteProfile]:
        """获取用户品味画像"""
        return self.taste_profiles.get(user_id)

    def add_taste_profile(self, profile: TasteProfile) -> None:
        """添加品味画像"""
        self.taste_profiles[profile.user_id] = profile
