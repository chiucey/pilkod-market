# 招聘智能匹配系统 - 使用参考

## 功能模块概览

### 1. 数据采集模块 (job_scraper.py)

**类结构：**
- `JobPosting`: 岗位数据结构
- `JobScraper`: 采集器基类
- `LiepinScraper`: 猎聘采集器
- `BossScraper`: Boss直聘采集器
- `Job51Scraper`: 51Job采集器
- `JobAggregator`: 聚合器

**主要函数：**
```python
# 单平台采集
scraper = LiepinScraper()
jobs = await scraper.scrape("Python", "上海")

# 多平台聚合
aggregator = JobAggregator(["猎聘", "Boss直聘", "51Job"])
results = await aggregator.scrape_all("数据分析", "上海")

# 带过滤采集
jobs = await aggregator.scrape_with_filter(
    keyword="算法",
    min_salary=30,  # 最低30k
    experience="3-5年",
    education="本科"
)
```

### 2. 简历解析模块 (resume_parser.py)

**类结构：**
- `CandidateProfile`: 候选人画像
- `ResumeParser`: 简历解析器
- `CandidateEvaluator`: 评估器
- `PotentialAnalyzer`: 潜力分析器

**主要函数：**
```python
# 解析简历
parser = ResumeParser()
profile = parser.parse(resume_text)

# 评估候选人
evaluator = CandidateEvaluator()
evaluation = evaluator.evaluate(profile)

# 潜力分析
analyzer = PotentialAnalyzer()
potential = analyzer.analyze(profile)

# 异步接口
profile = await parse_resume(resume_text)
evaluation = await evaluate_candidate(profile)
potential = await analyze_potential(profile)
```

**CandidateProfile 字段说明：**
| 字段 | 类型 | 说明 |
|------|------|------|
| name | str | 姓名 |
| highest_degree | str | 最高学历 (博士/硕士/本科/大专/未知) |
| total_years | float | 总工作年限 |
| hard_skills | List[str] | 硬技能 |
| soft_skills | List[str] | 软技能 |
| overseas_study | List[Dict] | 留学背景 |
| expected_salary | str | 期望薪资 |
| work_experience | List[Dict] | 工作经历 |

### 3. 匹配引擎 (match_engine.py)

**类结构：**
- `MatchEngine`: 匹配引擎
- `BatchMatcher`: 批量匹配器

**主要函数：**
```python
# 单次匹配
matcher = BatchMatcher()
results = matcher.match_candidate_to_jobs(
    candidate_profile,
    jobs,
    top_n=10  # 返回前10个最佳匹配
)

# 批量匹配
all_results = matcher.match_multiple_candidates(candidates, jobs)
```

**匹配结果字段：**
| 字段 | 说明 |
|------|------|
| match_score | 综合匹配度 (%) |
| skill_match | 技能匹配度 (%) |
| experience_match | 经验匹配度 (%) |
| education_match | 学历匹配度 (%) |
| salary_match | 薪资匹配度 (%) |
| recommendation | 推荐等级 (强烈推荐/推荐/考虑/不建议) |

### 4. 报告生成 (report_generator.py)

**类结构：**
- `ReportConfig`: 报告配置
- `ReportGenerator`: 单份报告生成器
- `BatchReportGenerator`: 批量报告生成器

**主要函数：**
```python
# 生成单份报告
generator = ReportGenerator()
html = generator.generate_html_report(
    profile, evaluation, potential, matched_jobs
)
generator.save_report(html, "report.html")

# 生成批量汇总
batch_gen = BatchReportGenerator()
summary = batch_gen.generate_summary_report(all_results)

# 异步接口
html = await generate_report(profile, evaluation, potential, jobs)
summary = await generate_batch_summary(all_results)
```

## 使用示例

### 完整评估流程

```python
import asyncio
from scripts.job_scraper import scrape_jobs
from scripts.resume_parser import parse_resume, evaluate_candidate, analyze_potential
from scripts.match_engine import match_candidate_to_jobs
from scripts.report_generator import generate_report

async def full_evaluation():
    # 1. 采集岗位数据
    print("📡 采集招聘数据...")
    jobs_data = await scrape_jobs("Python", ["猎聘", "Boss直聘"], "上海")
    all_jobs = [job for jobs in jobs_data.values() for job in jobs]

    # 2. 解析简历
    print("📄 解析候选人简历...")
    with open("resume.txt", "r") as f:
        resume_text = f.read()
    profile = await parse_resume(resume_text)

    # 3. 评估候选人
    print("📊 评估候选人...")
    evaluation = await evaluate_candidate(profile)

    # 4. 潜力分析
    print("🔮 分析潜力...")
    potential = await analyze_potential(profile)

    # 5. 匹配岗位
    print("🎯 匹配岗位...")
    matched_jobs = await match_candidate_to_jobs(
        profile.to_dict(),
        all_jobs,
        top_n=10
    )

    # 6. 生成报告
    print("📝 生成报告...")
    report = await generate_report(
        profile.to_dict(),
        evaluation,
        potential,
        matched_jobs,
        output_path="evaluation_report.html"
    )

    print("✅ 评估完成!")
    return report

# 运行
asyncio.run(full_evaluation())
```

### 批量处理

```python
async def batch_evaluation(candidate_files: List[str]):
    # 采集岗位
    jobs_data = await scrape_jobs("全栈工程师", ["猎聘"], "上海")
    all_jobs = [job for job in jobs_data.get("猎聘", [])]

    results = {}
    for file in candidate_files:
        name = file.split("/")[-1].replace(".txt", "")
        resume_text = open(file).read()

        profile = await parse_resume(resume_text)
        evaluation = await evaluate_candidate(profile)
        potential = await analyze_potential(profile)
        matched_jobs = await match_candidate_to_jobs(profile.to_dict(), all_jobs)

        results[name] = {
            "profile": profile.to_dict(),
            "evaluation": evaluation,
            "potential": potential,
            "matched_jobs": matched_jobs
        }

    # 生成汇总报告
    from scripts.report_generator import generate_batch_summary
    summary = await generate_batch_summary(results, "batch_summary.html")

    return results
```

## 评估权重配置

默认权重（可自定义）：
```python
weights = {
    "competency": 0.30,  # 胜任力
    "experience": 0.25,   # 经验
    "education": 0.15,    # 学历
    "salary_match": 0.15, # 薪资匹配
    "stability": 0.15     # 稳定性
}
```

匹配权重：
```python
match_weights = {
    "skill": 0.35,       # 技能匹配
    "experience": 0.30,  # 经验匹配
    "education": 0.15,   # 学历匹配
    "salary": 0.20       # 薪资匹配
}
```

## 评估等级

| 等级 | 综合得分 | 说明 |
|------|----------|------|
| A+ | ≥90 | 优秀，推荐优先 |
| A | 80-89 | 良好，重点考虑 |
| B+ | 70-79 | 中上，可以考虑 |
| B | 60-69 | 一般，备选 |
| C | <60 | 较弱，不建议 |

## 注意事项

1. **数据隐私**：简历仅用于本次评估，不做持久化存储
2. **OCR精度**：图片简历识别准确率约85-95%
3. **实时性**：招聘数据为实时抓取，可能存在延迟
4. **局限性**：评估仅供参考，最终决策需结合实际情况