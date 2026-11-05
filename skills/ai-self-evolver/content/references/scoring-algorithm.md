# 评分算法详解

## 评分公式

```
最终评分 = 相关性分 × 0.4 + 实用性分 × 0.3 + 新颖度分 × 0.2 + 质量分 × 0.1
```

## 各维度详细计算

### 1. 相关性评分 (40%)

#### GitHub项目相关性

```python
def calculate_relevance(project) -> float:
    score = 0

    # 名称匹配 (最高20分)
    name_matches = count_keyword_matches(project.name, AI_KEYWORDS)
    score += min(name_matches * 7, 20)

    # 描述匹配 (最高25分)
    desc_matches = count_keyword_matches(project.description, AI_KEYWORDS)
    score += min(desc_matches * 5, 25)

    # Readme匹配 (最高25分)
    readme_matches = count_keyword_matches(project.readme, AI_KEYWORDS)
    score += min(readme_matches * 3, 25)

    # Topics/Tags匹配 (最高20分)
    topic_matches = count_keyword_matches(project.topics, AI_KEYWORDS)
    score += min(topic_matches * 5, 20)

    # 语言相关性 (最高10分)
    if project.language in ["Python", "JavaScript", "TypeScript"]:
        score += 10
    elif project.language in ["Rust", "Go", "C++"]:
        score += 7

    return min(score, 100)
```

#### 关键词匹配算法

```python
AI_KEYWORDS = {
    # 核心AI概念
    "high": ["llm", "gpt", "agent", "chatbot", "langchain", "rag"],
    # 工具和框架
    "medium": ["ai", "ml", "nlp", "cv", "neural", "transformer", "embedding"],
    # 相关技术
    "low": ["api", "cloud", "deployment", "docker", "kubernetes"]
}

def count_keyword_matches(text, keywords) -> int:
    text_lower = text.lower()
    matches = 0

    for priority, words in keywords.items():
        for word in words:
            if word in text_lower:
                weight = {"high": 3, "medium": 2, "low": 1}[priority]
                matches += weight * text_lower.count(word)

    return matches
```

### 2. 实用性评分 (30%)

```python
def calculate_utility(project) -> float:
    score = 0

    # 安装便利性 (最高30分)
    if project.package_manager:
        score += 15
    if project.setup_instructions:
        score += 10
    if project.demo_example:
        score += 5

    # 功能完整性 (最高25分)
    if project.has_tests:
        score += 10
    if project.has_docs:
        score += 10
    if project.has_license:
        score += 5

    # 活跃度 (最高25分)
    commits_recent = project.commits_last_month
    if commits_recent > 50:
        score += 25
    elif commits_recent > 20:
        score += 20
    elif commits_recent > 10:
        score += 15
    elif commits_recent > 0:
        score += 10

    # 社区接受度 (最高20分)
    if project.stars > 10000:
        score += 20
    elif project.stars > 1000:
        score += 15
    elif project.stars > 100:
        score += 10
    elif project.stars > 10:
        score += 5

    return min(score, 100)
```

### 3. 新颖度评分 (20%)

```python
def calculate_novelty(project) -> float:
    score = 0

    # 发布时间 (最高40分)
    age_days = (today - project.created_at).days
    if age_days < 7:
        score += 40
    elif age_days < 30:
        score += 30
    elif age_days < 90:
        score += 20
    elif age_days < 180:
        score += 10
    else:
        score += 0

    # Star增长率 (最高30分)
    star_rate = project.stars / max(age_days, 1) * 7  # weekly rate
    if star_rate > 1000:
        score += 30
    elif star_rate > 500:
        score += 25
    elif star_rate > 100:
        score += 20
    elif star_rate > 50:
        score += 15
    elif star_rate > 10:
        score += 10

    # 类别新颖度 (最高30分)
    if project.category == "first_of_kind":
        score += 30
    elif project.category == "significant_improvement":
        score += 20
    elif project.category == "new_implementation":
        score += 15
    elif project.category == "feature_addition":
        score += 10

    return min(score, 100)
```

### 4. 质量评分 (10%)

```python
def calculate_quality(project) -> float:
    score = 0

    # 代码质量指标 (最高40分)
    if project.lgtm_grade == "A":
        score += 20
    elif project.lgtm_grade in ["B", "C"]:
        score += 15
    elif project.has_lgtm:
        score += 10

    if project.code_coverage > 80:
        score += 10
    elif project.code_coverage > 50:
        score += 5

    # 安全评分 (最高30分)
    if project.security_score > 90:
        score += 30
    elif project.security_score > 70:
        score += 20
    elif project.security_score > 50:
        score += 10

    # 许可证 (最高20分)
    if project.license in ["MIT", "Apache-2.0", "BSD-3-Clause"]:
        score += 20
    elif project.license in ["GPL-3.0", "LGPL"]:
        score += 10
    elif project.license == "Unknown":
        score -= 10  # 扣分

    # 问题响应 (最高10分)
    if project.issue_response_time < 24:
        score += 10
    elif project.issue_response_time < 72:
        score += 5

    return min(max(score, 0), 100)
```

## 用户偏好调整

```python
def adjust_by_user_preference(base_score, user_profile, project) -> float:
    adjusted = base_score

    # 用户擅长领域加成
    for skill in user_profile.expertise:
        if skill in project.keywords:
            adjusted *= 1.1

    # 用户兴趣领域加成
    for interest in user_profile.interests:
        if interest in project.description:
            adjusted *= 1.15

    # 用户避免领域扣分
    for avoid in user_profile.avoid:
        if avoid in project.description:
            adjusted *= 0.7

    # 历史偏好加权
    similar = find_similar_installed(project)
    if similar:
        user_rating = user_profile.get_rating(similar)
        adjusted *= (0.8 + user_rating * 0.4)  # 0.8-1.2

    return min(adjusted, 100)
```

## 阈值设置

```python
THRESHOLDS = {
    "auto_install": 85,   # 自动安装阈值
    "recommend": 70,      # 推荐安装阈值
    "notify": 50,          # 通知用户阈值
    "ignore": 0           # 忽略阈值
}
```

## 评分示例

```python
example_project = {
    "name": "auto-gpt",
    "description": "An autonomous GPT-4 experiment",
    "stars": 140000,
    "language": "Python",
    "created_days_ago": 180,
    "has_docs": True,
    "has_tests": True,
    "license": "MIT"
}

# 计算得分
relevance = calculate_relevance(example_project)  # ~75
utility = calculate_utility(example_project)      # ~70
novelty = calculate_novelty(example_project)      # ~40
quality = calculate_quality(example_project)        # ~80

final_score = (
    relevance * 0.4 +
    utility * 0.3 +
    novelty * 0.2 +
    quality * 0.1
)

# final_score ≈ 68
```
