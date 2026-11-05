# 智能体大脑实现参考

## 核心实现示例

### 需求追踪器实现

```python
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class Requirement:
    id: str
    description: str
    created_at: datetime
    status: str = "active"
    parent_id: Optional[str] = None

@dataclass
class RequirementConflict:
    requirement_a: Requirement
    requirement_b: Requirement
    conflict_type: str
    description: str
    resolution_options: List[str]

class RequirementTracker:
    def __init__(self):
        self.requirements: Dict[str, Requirement] = {}
        self.history: List[Dict] = []

    def generate_id(self, content: str) -> str:
        """生成需求ID"""
        hash_obj = hashlib.md5(content.encode())
        return f"REQ-{hash_obj.hexdigest()[:8].upper()}"

    def record(self, requirement_text: str, parent_id: Optional[str] = None) -> Requirement:
        """记录新需求"""
        req_id = self.generate_id(requirement_text)
        requirement = Requirement(
            id=req_id,
            description=requirement_text,
            created_at=datetime.now(),
            parent_id=parent_id
        )
        self.requirements[req_id] = requirement
        self._log_change("created", requirement)
        return requirement

    def check_consistency(self, new_requirement_text: str) -> Dict:
        """
        检查新需求与现有需求的一致性
        返回结构:
        {
            'is_consistent': bool,
            'conflicts': List[RequirementConflict],
            'similarities': List[Dict],
            'suggestions': List[str]
        }
        """
        new_req_id = self.generate_id(new_requirement_text)

        # 检查是否重复
        if new_req_id in self.requirements:
            return {
                'is_consistent': True,
                'conflicts': [],
                'similarities': [{'id': new_req_id, 'similarity': 1.0}],
                'suggestions': ['This appears to be a duplicate requirement']
            }

        # 检测语义冲突
        conflicts = self._detect_semantic_conflicts(new_requirement_text)

        # 检测条件冲突
        conditional_conflicts = self._detect_conditional_conflicts(new_requirement_text)

        all_conflicts = conflicts + conditional_conflicts

        return {
            'is_consistent': len(all_conflicts) == 0,
            'conflicts': all_conflicts,
            'similarities': self._find_similar_requirements(new_requirement_text),
            'suggestions': self._generate_suggestions(all_conflicts)
        }

    def _detect_semantic_conflicts(self, new_text: str) -> List[RequirementConflict]:
        """检测语义冲突"""
        conflicts = []

        # 定义冲突关键词对
        conflict_pairs = [
            ('禁止', '允许'),
            ('必须', '可选'),
            ('一直', '偶尔'),
            ('全部', '部分'),
            ('新增', '删除'),
            ('扩展', '缩减')
        ]

        for req_id, existing_req in self.requirements.items():
            for keyword_a, keyword_b in conflict_pairs:
                if keyword_a in existing_req.description and keyword_b in new_text:
                    conflicts.append(RequirementConflict(
                        requirement_a=existing_req,
                        requirement_b=Requirement(id="NEW", description=new_text, created_at=datetime.now()),
                        conflict_type="semantic_contradiction",
                        description=f"'{existing_req.description}' 与新需求 '{new_text}' 存在语义冲突",
                        resolution_options=[
                            f"保留原需求 '{keyword_a}' 要求",
                            f"采用新需求 '{keyword_b}' 方式",
                            "重新定义需求范围"
                        ]
                    ))

        return conflicts

    def _detect_conditional_conflicts(self, new_text: str) -> List[RequirementConflict]:
        """检测条件冲突（如时间、条件等）"""
        conflicts = []

        for req_id, existing_req in self.requirements.items():
            # 检测时间冲突
            time_keywords = ['每天', '每周', '每月', '定时', '定期']
            for keyword in time_keywords:
                if keyword in existing_req.description and keyword in new_text:
                    if existing_req.description != new_text:
                        conflicts.append(RequirementConflict(
                            requirement_a=existing_req,
                            requirement_b=Requirement(id="NEW", description=new_text, created_at=datetime.now()),
                            conflict_type="time_condition_conflict",
                            description=f"时间相关的重复需求可能产生冲突",
                            resolution_options=[
                                "合并为一个统一的时间计划",
                                "明确两个需求的优先级",
                                "重新评估需求必要性"
                            ]
                        ))

        return conflicts

    def _find_similar_requirements(self, text: str) -> List[Dict]:
        """查找相似的现有需求"""
        similarities = []
        # 简单实现：检查关键词重叠
        words = set(text.replace(',', ' ').split())

        for req_id, existing_req in self.requirements.items():
            existing_words = set(existing_req.description.replace(',', ' ').split())
            overlap = words & existing_words
            if len(overlap) >= 3:  # 超过3个关键词重叠
                similarity = len(overlap) / max(len(words), len(existing_words))
                similarities.append({
                    'id': req_id,
                    'description': existing_req.description,
                    'similarity': similarity,
                    'common_keywords': list(overlap)
                })

        return sorted(similarities, key=lambda x: x['similarity'], reverse=True)

    def _generate_suggestions(self, conflicts: List[RequirementConflict]) -> List[str]:
        """生成解决建议"""
        suggestions = []

        if len(conflicts) == 0:
            suggestions.append("需求一致性检查通过")

        for conflict in conflicts:
            suggestions.extend(conflict.resolution_options)

        return suggestions

    def _log_change(self, action: str, requirement: Requirement):
        """记录变更历史"""
        self.history.append({
            'action': action,
            'requirement_id': requirement.id,
            'timestamp': datetime.now().isoformat(),
            'description': requirement.description
        })
```

### 代码审查器实现

```python
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CodeIssue:
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str
    location: str
    description: str
    suggestion: str
    line_number: int

class CodeReviewer:
    def __init__(self):
        self.issues: List[CodeIssue] = []

        # 定义检查模式
        self.patterns = {
            'null_pointer': {
                'pattern': r'\.(\w+)\s*(?:\(|\.)(?!.*\.length)',
                'severity': 'HIGH',
                'description': '可能的空指针访问'
            },
            'resource_leak': {
                'patterns': [
                    (r'open\s*\([^)]+\)(?!\s*close)', '文件流未关闭'),
                    (r'new\s+Connection\s*(?!\s*close)', '数据库连接未关闭'),
                    (r'new\s+HttpClient\s*(?!\s*dispose)', 'HTTP客户端未释放')
                ],
                'severity': 'HIGH'
            },
            'infinite_loop': {
                'patterns': [
                    (r'while\s*\(\s*true\s*\)', '无限循环'),
                    (r'for\s*\(\s*;\s*;\s*\)', '死循环')
                ],
                'severity': 'CRITICAL'
            },
            'sql_injection': {
                'patterns': [
                    (r'executeQuery\s*\(\s*["\'].*\%s', 'SQL注入风险'),
                    (r'\$\{.*\}', '字符串格式化SQL')
                ],
                'severity': 'CRITICAL'
            },
            'hardcoded_secret': {
                'patterns': [
                    (r'password\s*=\s*["\'][^"\']+["\']', '硬编码密码'),
                    (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', '硬编码API密钥')
                ],
                'severity': 'CRITICAL'
            }
        }

    def analyze(self, code: str, language: str = 'python') -> Dict:
        """执行代码分析"""
        self.issues = []
        lines = code.split('\n')

        # 执行各项检查
        self._check_null_pointers(lines)
        self._check_resource_leaks(lines)
        self._check_infinite_loops(lines)
        self._check_security_issues(lines)
        self._check_code_style(lines, language)

        # 按严重程度分组
        grouped = self._group_by_severity()

        return {
            'total_issues': len(self.issues),
            'issues_by_severity': {
                'CRITICAL': len([i for i in self.issues if i.severity == 'CRITICAL']),
                'HIGH': len([i for i in self.issues if i.severity == 'HIGH']),
                'MEDIUM': len([i for i in self.issues if i.severity == 'MEDIUM']),
                'LOW': len([i for i in self.issues if i.severity == 'LOW'])
            },
            'issues': self.issues,
            'grouped_issues': grouped,
            'quality_score': self._calculate_quality_score()
        }

    def _check_null_pointers(self, lines: List[str]):
        """检查空指针风险"""
        for i, line in enumerate(lines, 1):
            # Python: list[index] without bounds check
            if re.search(r'\w+\[\w+\](?!\s*\.length)', line):
                if not any(x in line for x in ['if', 'try', 'len']):
                    self.issues.append(CodeIssue(
                        severity='HIGH',
                        category='null_check',
                        location=f'line {i}',
                        description='可能的索引越界访问',
                        suggestion='添加边界检查或使用安全的访问方式',
                        line_number=i
                    ))

    def _check_resource_leaks(self, lines: List[str]):
        """检查资源泄漏"""
        for i, line in enumerate(lines, 1):
            for category, patterns in self.patterns.items():
                if category == 'resource_leak':
                    for pattern, desc in patterns['patterns']:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 简单检查：后续是否有close
                            following_lines = '\n'.join(lines[i:i+10])
                            if 'close' not in following_lines.lower():
                                self.issues.append(CodeIssue(
                                    severity='HIGH',
                                    category='resource_leak',
                                    location=f'line {i}',
                                    description=desc,
                                    suggestion='确保在finally块或with语句中关闭资源',
                                    line_number=i
                                ))

    def _check_infinite_loops(self, lines: List[str]):
        """检查无限循环"""
        for i, line in enumerate(lines, 1):
            for pattern, desc in self.patterns['infinite_loop']['patterns']:
                if re.search(pattern, line):
                    self.issues.append(CodeIssue(
                        severity='CRITICAL',
                        category='infinite_loop',
                        location=f'line {i}',
                        description=desc,
                        suggestion='确保循环有终止条件或添加超时机制',
                        line_number=i
                    ))

    def _check_security_issues(self, lines: List[str]):
        """检查安全问题"""
        for i, line in enumerate(lines, 1):
            for category, patterns in self.patterns.items():
                if category in ['sql_injection', 'hardcoded_secret']:
                    for pattern, desc in patterns['patterns']:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.issues.append(CodeIssue(
                                severity='CRITICAL',
                                category='security',
                                location=f'line {i}',
                                description=desc,
                                suggestion='使用环境变量或配置中心存储敏感信息，使用参数化查询',
                                line_number=i
                            ))

    def _check_code_style(self, lines: List[str], language: str):
        """检查代码风格"""
        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # 检查过长的行
            if len(stripped) > 120:
                self.issues.append(CodeIssue(
                    severity='LOW',
                    category='style',
                    location=f'line {i}',
                    description=f'行长度超过120字符 ({len(stripped)}字符)',
                    suggestion='考虑拆分为多行或提取为函数',
                    line_number=i
                ))

            # 检查过长的函数名/变量名
            identifiers = re.findall(r'[a-z][a-zA-Z0-9_]{30,}', stripped)
            if identifiers:
                self.issues.append(CodeIssue(
                    severity='LOW',
                    category='naming',
                    location=f'line {i}',
                    description='标识符命名过长',
                    suggestion='使用更简洁的命名方式',
                    line_number=i
                ))

    def _group_by_severity(self) -> Dict:
        """按严重程度分组"""
        return {
            'CRITICAL': [i for i in self.issues if i.severity == 'CRITICAL'],
            'HIGH': [i for i in self.issues if i.severity == 'HIGH'],
            'MEDIUM': [i for i in self.issues if i.severity == 'MEDIUM'],
            'LOW': [i for i in self.issues if i.severity == 'LOW']
        }

    def _calculate_quality_score(self) -> int:
        """计算质量分数 (0-100)"""
        if not self.issues:
            return 100

        weights = {'CRITICAL': 30, 'HIGH': 15, 'MEDIUM': 5, 'LOW': 1}
        deductions = sum(weights[i.severity] for i in self.issues)

        return max(0, 100 - deductions)
```

### 效率审计器实现

```python
import re
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class EfficiencyIssue:
    category: str
    location: str
    current_complexity: str
    suggested_complexity: str
    impact: str
    suggestion: str

class EfficiencyAuditor:
    # 复杂度等级
    COMPLEXITY_LEVELS = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n²)', 'O(n³)', 'O(2^n)']

    def audit(self, code: str) -> Dict:
        """执行效率审计"""
        issues = []
        lines = code.split('\n')

        # 1. 检查嵌套循环
        nested_loop_issues = self._check_nested_loops(lines)
        issues.extend(nested_loop_issues)

        # 2. 检查数据库查询效率
        db_issues = self._check_database_efficiency(lines)
        issues.extend(db_issues)

        # 3. 检查API调用
        api_issues = self._check_api_calls(lines)
        issues.extend(api_issues)

        # 4. 检查算法复杂度
        algo_issues = self._check_algorithm_complexity(lines)
        issues.extend(algo_issues)

        return {
            'total_issues': len(issues),
            'issues': issues,
            'efficiency_score': self._calculate_efficiency_score(issues),
            'summary': self._generate_summary(issues)
        }

    def _check_nested_loops(self, lines: List[str]) -> List[EfficiencyIssue]:
        """检查嵌套循环"""
        issues = []

        for i, line in enumerate(lines):
            if 'for' in line or 'while' in line:
                # 统计后续行的缩进层级
                base_indent = len(line) - len(line.lstrip())
                loop_depth = 1

                for j in range(i+1, min(i+50, len(lines))):
                    next_line = lines[j]
                    if not next_line.strip():
                        continue

                    next_indent = len(next_line) - len(next_line.lstrip())

                    if next_indent > base_indent:
                        if 'for' in next_line or 'while' in next_line:
                            loop_depth += 1
                    elif next_indent <= base_indent:
                        break

                if loop_depth >= 3:
                    issues.append(EfficiencyIssue(
                        category='nested_loop',
                        location=f'line {i+1}',
                        current_complexity='O(n³)' if loop_depth == 3 else 'O(n^depth)',
                        suggested_complexity='O(n²) 或更低',
                        impact=f'发现{loop_depth}层嵌套循环，可能导致性能问题',
                        suggestion='考虑使用更高效的算法或数据结构，如哈希表'
                    ))

        return issues

    def _check_database_efficiency(self, lines: List[str]) -> List[EfficiencyIssue]:
        """检查数据库查询效率"""
        issues = []

        for i, line in enumerate(lines):
            # 检测N+1查询问题
            if re.search(r'for\s*\(.*\)\s*{.*\.(find|get|select|query)', line, re.DOTALL):
                issues.append(EfficiencyIssue(
                    category='n_plus_one',
                    location=f'line {i+1}',
                    current_complexity='O(n)',
                    suggested_complexity='O(1)',
                    impact='N+1查询问题，每次循环执行一次数据库查询',
                    suggestion='使用批量查询或JOIN操作'
                ))

            # 检测缺少索引的查询
            if re.search(r'where.*like.*%', line):
                issues.append(EfficiencyIssue(
                    category='full_scan',
                    location=f'line {i+1}',
                    current_complexity='O(n)',
                    suggested_complexity='O(log n)',
                    impact='前缀通配符查询无法使用索引',
                    suggestion='考虑使用后缀通配符或全文索引'
                ))

        return issues

    def _check_api_calls(self, lines: List[str]) -> List[EfficiencyIssue]:
        """检查API调用效率"""
        issues = []

        for i, line in enumerate(lines):
            # 检测同步阻塞调用
            if re.search(r'(requests\.|http\.client|fetch\()', line):
                # 检查是否在循环中
                for j in range(max(0, i-5), i):
                    if 'for' in lines[j] or 'while' in lines[j]:
                        issues.append(EfficiencyIssue(
                            category='blocking_api',
                            location=f'line {i+1}',
                            current_complexity='O(n * latency)',
                            suggested_complexity='O(1) 并行',
                            impact='循环中的同步API调用可能导致严重延迟',
                            suggestion='使用异步调用或批量API'
                        ))
                        break

        return issues

    def _check_algorithm_complexity(self, lines: List[str]) -> List[EfficiencyIssue]:
        """检查算法复杂度"""
        issues = []

        # 检测排序在循环中
        for i, line in enumerate(lines):
            if 'sort' in line.lower() or 'sorted(' in line:
                # 检查是否在循环中
                for j in range(max(0, i-10), i):
                    if 'for' in lines[j] or 'while' in lines[j]:
                        issues.append(EfficiencyIssue(
                            category='inefficient_sort',
                            location=f'line {i+1}',
                            current_complexity='O(n² log n)',
                            suggested_complexity='O(n log n)',
                            impact='循环中的排序操作导致时间复杂度增加',
                            suggestion='将排序移到循环外部'
                        ))
                        break

        return issues

    def _calculate_efficiency_score(self, issues: List[EfficiencyIssue]) -> int:
        """计算效率分数"""
        if not issues:
            return 100

        weights = {
            'nested_loop': 25,
            'n_plus_one': 30,
            'blocking_api': 20,
            'full_scan': 15,
            'inefficient_sort': 20
        }

        deductions = sum(weights.get(i.category, 10) for i in issues)
        return max(0, 100 - deductions)

    def _generate_summary(self, issues: List[EfficiencyIssue]) -> str:
        """生成摘要"""
        if not issues:
            return "代码效率良好，无明显性能问题"

        categories = {}
        for issue in issues:
            categories[issue.category] = categories.get(issue.category, 0) + 1

        summary = "发现以下效率问题：\n"
        for cat, count in categories.items():
            summary += f"- {cat}: {count}处\n"

        return summary
```

## 集成使用示例

```python
class AgentBrain:
    def __init__(self):
        self.requirement_tracker = RequirementTracker()
        self.code_reviewer = CodeReviewer()
        self.efficiency_auditor = EfficiencyAuditor()

    def full_review(self, code: str, requirement: str) -> Dict:
        """执行完整审查"""
        # 1. 需求一致性检查
        req_check = self.requirement_tracker.check_consistency(requirement)

        # 2. 代码审查
        code_review = self.code_reviewer.analyze(code)

        # 3. 效率审计
        efficiency = self.efficiency_auditor.audit(code)

        # 综合评分
        overall_score = (
            code_review['quality_score'] * 0.5 +
            efficiency['efficiency_score'] * 0.3 +
            (100 if req_check['is_consistent'] else 50) * 0.2
        )

        return {
            'requirement_check': req_check,
            'code_review': code_review,
            'efficiency_audit': efficiency,
            'overall_score': round(overall_score, 2),
            'recommendations': self._generate_recommendations(
                req_check, code_review, efficiency
            )
        }

    def _generate_recommendations(self, req_check, code_review, efficiency) -> List[str]:
        """生成建议"""
        recommendations = []

        if not req_check['is_consistent']:
            recommendations.append("解决需求冲突后再继续")

        if code_review['issues_by_severity']['CRITICAL'] > 0:
            recommendations.append("修复CRITICAL级别的代码问题")

        if efficiency['efficiency_score'] < 70:
            recommendations.append("优化代码效率")

        if not recommendations:
            recommendations.append("质量检查通过，可以继续")

        return recommendations
```

## 测试用例

```python
# 测试需求追踪器
def test_requirement_tracker():
    tracker = RequirementTracker()

    # 测试1: 记录新需求
    req1 = tracker.record("系统需要支持用户登录")
    assert req1.id.startswith("REQ-")

    # 测试2: 检测重复需求
    result = tracker.check_consistency("系统需要支持用户登录")
    assert result['is_consistent'] == True
    assert len(result['similarities']) > 0

    # 测试3: 检测冲突需求
    result = tracker.check_consistency("禁止用户登录")
    assert result['is_consistent'] == False
    assert len(result['conflicts']) > 0

# 测试代码审查器
def test_code_reviewer():
    reviewer = CodeReviewer()

    code = """
    password = "hardcoded123"
    for item in items:
        result = executeQuery(f"SELECT * FROM users WHERE id = {item}")
    """

    result = reviewer.analyze(code)

    assert result['total_issues'] >= 2
    assert any(i['severity'] == 'CRITICAL' for i in result['grouped_issues']['CRITICAL'])

# 测试效率审计器
def test_efficiency_auditor():
    auditor = EfficiencyAuditor()

    code = """
    for i in range(n):
        for j in range(n):
            for k in range(n):
                process(data[i][j][k])
    """

    result = auditor.audit(code)

    assert result['total_issues'] >= 1
    assert any('nested_loop' in i['category'] for i in result['issues'])
```
