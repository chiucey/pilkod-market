#!/usr/bin/env python3
"""
技能回归测试 - 验证各模块功能正确性
"""

import sys
import asyncio
from pathlib import Path

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from job_scraper import JobAggregator, scrape_jobs
from resume_parser import ResumeParser, CandidateEvaluator, PotentialAnalyzer, parse_resume, evaluate_candidate, analyze_potential
from match_engine import MatchEngine, BatchMatcher, match_candidate_to_jobs


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def run(self, name: str, test_func):
        """运行单个测试"""
        print(f"\n📋 测试: {name}")
        try:
            result = test_func()
            if result:
                print(f"  ✅ 通过")
                self.passed += 1
            else:
                print(f"  ❌ 失败")
                self.failed += 1
        except Exception as e:
            print(f"  ❌ 异常: {e}")
            self.failed += 1

    def report(self):
        """打印测试报告"""
        total = self.passed + self.failed
        print("\n" + "=" * 50)
        print(f"📊 测试结果: {self.passed}/{total} 通过")
        if self.failed > 0:
            print(f"❌ 失败: {self.failed}")
        return self.failed == 0


def test_job_scraper():
    """测试招聘数据采集"""
    async def _test():
        aggregator = JobAggregator(["猎聘", "Boss直聘"])
        results = await aggregator.scrape_all("Python", "上海")
        return len(results) > 0 and sum(len(jobs) for jobs in results.values()) > 0

    return asyncio.run(_test())


def test_resume_parser():
    """测试简历解析"""
    async def _test():
        sample_resume = """
        李四
        男，1988年出生
        手机：13912345678

        教育背景：
        2010-2014 清华大学 硕士 计算机科学

        工作经验：
        2018-至今 腾讯 技术专家

        技能：Python, Java, 架构设计, 团队管理
        """

        parser = ResumeParser()
        profile = parser.parse(sample_resume)
        # 测试核心字段是否正确解析
        has_skills = len(profile.hard_skills) > 0
        has_degree = profile.highest_degree in ["博士", "硕士", "本科", "大专"]
        return has_skills and has_degree

    return asyncio.run(_test())


def test_candidate_evaluator():
    """测试候选人评估"""
    async def _test():
        parser = ResumeParser()
        profile = parser.parse("""
        王五
        博士
        技能：Python, AI, 大数据
        """)

        evaluator = CandidateEvaluator()
        result = evaluator.evaluate(profile)

        return result.get("total_score", 0) > 0 and result.get("grade") in ["A+", "A", "B+", "B", "C"]

    return asyncio.run(_test())


def test_potential_analyzer():
    """测试潜力分析"""
    async def _test():
        parser = ResumeParser()
        profile = parser.parse("""
        测试候选人
        硕士 留学
        技能：Python, 大数据
        """)

        analyzer = PotentialAnalyzer()
        result = analyzer.analyze(profile)

        return "family_background" in result and "career_potential" in result

    return asyncio.run(_test())


def test_match_engine():
    """测试匹配引擎"""
    async def _test():
        engine = MatchEngine()

        result = engine.match(
            candidate_skills=["Python", "Java", "大数据"],
            candidate_experience=[],
            candidate_education="硕士",
            candidate_salary="40k-60k",
            job_requirements=["Python", "大数据", "机器学习"],
            job_salary="35k-55k",
            job_experience="3-5年",
            job_education="本科及以上"
        )

        return result.get("overall_score", 0) > 0 and "recommendation" in result

    return asyncio.run(_test())


def test_batch_matcher():
    """测试批量匹配"""
    async def _test():
        matcher = BatchMatcher()

        candidate = {
            "name": "测试候选人",
            "hard_skills": ["Python", "Java", "架构设计"],
            "highest_degree": "硕士",
            "expected_salary": "40k-60k",
            "work_experience": []
        }

        jobs = [
            {
                "company": "字节跳动",
                "position": "Python工程师",
                "salary": "30k-50k",
                "requirements": ["Python", "大数据"],
                "experience": "3-5年",
                "education": "本科"
            }
        ]

        results = matcher.match_candidate_to_jobs(candidate, jobs, top_n=5)
        return len(results) > 0 and results[0].get("match_score", 0) > 0

    return asyncio.run(_test())


def main():
    print("🧪 招聘智能匹配系统 - 回归测试")
    print("=" * 50)

    runner = TestRunner()

    # 运行测试
    runner.run("招聘数据采集", test_job_scraper)
    runner.run("简历解析", test_resume_parser)
    runner.run("候选人评估", test_candidate_evaluator)
    runner.run("潜力分析", test_potential_analyzer)
    runner.run("匹配引擎", test_match_engine)
    runner.run("批量匹配", test_batch_matcher)

    # 打印报告
    success = runner.report()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()