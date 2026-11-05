#!/usr/bin/env python3
"""
岗位-候选人匹配引擎
根据候选人画像与岗位要求进行智能匹配
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class MatchResult:
    """匹配结果"""
    job: Dict
    match_rate: float
    skill_match: float
    experience_match: float
    salary_match: float
    education_match: float
    overall_score: float
    recommendation: str
    matching_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    gap_analysis: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class MatchEngine:
    """匹配引擎"""

    def __init__(self):
        self.skill_synonyms = {
            "Python": ["python", "Python", "django", "flask"],
            "Java": ["java", "Java", "spring", "springboot"],
            "JavaScript": ["javascript", "JS", "js", "前端"],
            "SQL": ["sql", "SQL", "mysql", "postgresql", "数据库"],
            "大数据": ["大数据", "big data", "hadoop", "spark", "flink"],
            "机器学习": ["机器学习", "ML", "机器学习", "machine learning", "AI", "人工智能"],
            "架构": ["架构", "架构师", "architecture", "系统设计"],
            "项目管理": ["项目管理", "PM", "project management", "敏捷", "scrum"],
            "数据分析": ["数据分析", "data analysis", "BI", "可视化"],
            "云计算": ["云计算", "cloud", "AWS", "Azure", "阿里云"],
            "DevOps": ["devops", "Docker", "K8s", "kubernetes", "CI/CD"],
        }

        self.job_title_mapping = {
            "工程师": ["engineer", "工程师", "开发"],
            "高级工程师": ["senior", "高级", "资深"],
            "架构师": ["architect", "架构师", "架构"],
            "经理": ["manager", "经理", "主管"],
            "总监": ["director", "总监", "VP"],
            "专家": ["expert", "专家", "specialist"],
            "产品经理": ["PM", "product manager", "产品"],
        }

    def match(
        self,
        candidate_skills: List[str],
        candidate_experience: List[Dict],
        candidate_education: str,
        candidate_salary: str,
        job_requirements: List[str],
        job_salary: str,
        job_experience: str,
        job_education: str
    ) -> Dict[str, Any]:
        """
        计算匹配度

        Args:
            candidate_skills: 候选人技能列表
            job_requirements: 岗位技能要求
            job_salary: 岗位薪资范围

        Returns:
            匹配结果
        """
        # 技能匹配
        skill_match = self._match_skills(candidate_skills, job_requirements)

        # 经验匹配
        experience_match = self._match_experience(
            candidate_experience, job_experience
        )

        # 学历匹配
        education_match = self._match_education(
            candidate_education, job_education
        )

        # 薪资匹配
        salary_match = self._match_salary(candidate_salary, job_salary)

        # 综合评分
        weights = {"skill": 0.35, "experience": 0.30, "education": 0.15, "salary": 0.20}
        overall = (
            skill_match * weights["skill"]
            + experience_match * weights["experience"]
            + education_match * weights["education"]
            + salary_match * weights["salary"]
        )

        # 推荐等级
        recommendation = self._get_recommendation(overall, skill_match)

        return {
            "skill_match": round(skill_match, 1),
            "experience_match": round(experience_match, 1),
            "education_match": round(education_match, 1),
            "salary_match": round(salary_match, 1),
            "overall_score": round(overall, 1),
            "recommendation": recommendation
        }

    def _match_skills(
        self,
        candidate_skills: List[str],
        job_requirements: List[str]
    ) -> float:
        """技能匹配"""
        if not job_requirements:
            return 100.0

        candidate_set = set(s.lower() for s in candidate_skills)
        matched = []
        missing = []

        for req in job_requirements:
            req_lower = req.lower()
            found = False

            # 直接匹配
            for skill in candidate_skills:
                if skill.lower() == req_lower or skill.lower() in req_lower:
                    matched.append(skill)
                    found = True
                    break

            # 同义词匹配
            if not found:
                for core_skill, synonyms in self.skill_synonyms.items():
                    if req_lower in [s.lower() for s in synonyms] or core_skill.lower() in req_lower:
                        if any(s.lower() in [c.lower() for c in candidate_skills] for s in synonyms):
                            matched.append(core_skill)
                            found = True
                            break

            if not found:
                missing.append(req)

        # 计算匹配率
        match_rate = (len(matched) / len(job_requirements)) * 100 if job_requirements else 100

        return min(match_rate, 100)

    def _match_experience(
        self,
        candidate_experience: List[Dict],
        job_experience_req: str
    ) -> float:
        """经验匹配"""
        if not job_experience_req:
            return 80.0

        # 提取要求年限
        years_req = 0
        patterns = [
            r'(\d+)年以上',
            r'(\d+)-(\d+)年',
            r'经验(\d+)年'
        ]
        for pattern in patterns:
            match = re.search(pattern, job_experience_req)
            if match:
                years_req = int(match.group(1))
                break

        # 计算候选人总年限
        total_years = len(candidate_experience) * 2  # 简化：每段计2年

        if years_req == 0:
            return 80.0

        if total_years >= years_req:
            # 超出或满足要求，得分高
            exceed_ratio = min((total_years - years_req) / years_req, 0.5)
            return 80 + exceed_ratio * 20
        else:
            # 不足，扣分
            gap = years_req - total_years
            penalty = min(gap * 10, 40)
            return max(40, 70 - penalty)

    def _match_education(
        self,
        candidate_education: str,
        job_education_req: str
    ) -> float:
        """学历匹配"""
        education_levels = {
            "博士": 5, "硕士": 4, "本科": 3, "大专": 2, "高中": 1, "未知": 0
        }
        job_levels = {
            "博士": 5, "PhD": 5,
            "硕士": 4, "研究生": 4, "MBA": 4,
            "本科": 3, "学士": 3,
            "大专": 2,
            "高中": 1,
            "不限": 0
        }

        cand_level = education_levels.get(candidate_education, 0)
        job_level = 0
        for key, level in job_levels.items():
            if key in job_education_req:
                job_level = max(job_level, level)

        if job_level == 0:
            return 85.0  # 不限则默认高分

        if cand_level >= job_level:
            return 100.0
        elif cand_level == job_level - 1:
            return 80.0
        else:
            return max(50, 70 - (job_level - cand_level) * 15)

    def _match_salary(
        self,
        candidate_salary: str,
        job_salary: str
    ) -> float:
        """薪资匹配"""
        if not candidate_salary or not job_salary:
            return 75.0

        # 提取薪资数值
        cand_nums = re.findall(r'\d+', candidate_salary)
        job_nums = re.findall(r'\d+', job_salary)

        if not cand_nums or not job_nums:
            return 75.0

        cand_max = int(cand_nums[-1]) if cand_nums else 0
        job_min = int(job_nums[0]) if job_nums else 0
        job_max = int(job_nums[-1]) if len(job_nums) > 1 else job_min

        # 候选人期望 > 岗位上限
        if cand_max > job_max:
            return max(60, 85 - (cand_max - job_max) * 2)
        # 候选人期望在岗位范围内
        elif job_min <= cand_max <= job_max:
            return 95.0
        # 候选人期望 < 岗位下限
        else:
            return 90.0  # 低于预期反而是优势

    def _get_recommendation(self, overall: float, skill_match: float) -> str:
        """获取推荐等级"""
        if overall >= 85 and skill_match >= 70:
            return "强烈推荐"
        elif overall >= 70 and skill_match >= 60:
            return "推荐"
        elif overall >= 55:
            return "考虑"
        else:
            return "不建议"


class BatchMatcher:
    """批量匹配器"""

    def __init__(self):
        self.engine = MatchEngine()

    def match_candidate_to_jobs(
        self,
        candidate_profile: Dict,
        jobs: List[Dict],
        top_n: int = 10
    ) -> List[Dict]:
        """
        将候选人匹配到多个岗位

        Args:
            candidate_profile: 候选人画像
            jobs: 岗位列表
            top_n: 返回前N个最佳匹配

        Returns:
            排序后的匹配结果列表
        """
        results = []

        for job in jobs:
            match_result = self.engine.match(
                candidate_skills=candidate_profile.get("hard_skills", []),
                candidate_experience=candidate_profile.get("work_experience", []),
                candidate_education=candidate_profile.get("highest_degree", ""),
                candidate_salary=candidate_profile.get("expected_salary", ""),
                job_requirements=job.get("requirements", []),
                job_salary=job.get("salary", ""),
                job_experience=job.get("experience", ""),
                job_education=job.get("education", "")
            )

            result = {
                "job_id": hashlib.md5(f"{job['company']}{job['position']}".encode()).hexdigest()[:8],
                "company": job.get("company", ""),
                "position": job.get("position", ""),
                "location": job.get("location", ""),
                "salary": job.get("salary", ""),
                "platform": job.get("platform", ""),
                "url": job.get("url", ""),
                "match_score": match_result["overall_score"],
                "skill_match": match_result["skill_match"],
                "experience_match": match_result["experience_match"],
                "education_match": match_result["education_match"],
                "salary_match": match_result["salary_match"],
                "recommendation": match_result["recommendation"]
            }
            results.append(result)

        # 按匹配度排序
        results.sort(key=lambda x: x["match_score"], reverse=True)

        return results[:top_n]

    def match_multiple_candidates(
        self,
        candidates: List[Dict],
        jobs: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """
        批量匹配多个候选人

        Args:
            candidates: 候选人列表
            jobs: 岗位列表

        Returns:
            每个候选人的匹配结果
        """
        results = {}
        for i, candidate in enumerate(candidates):
            name = candidate.get("name", f"候选人{i+1}")
            results[name] = self.match_candidate_to_jobs(candidate, jobs)
        return results


# 异步入口函数（供外部调用）
async def match_candidate_to_jobs(
    candidate_profile: Dict,
    jobs: List[Dict],
    top_n: int = 10
) -> List[Dict]:
    """
    候选人岗位匹配

    Args:
        candidate_profile: 候选人画像
        jobs: 岗位列表
        top_n: 返回前N个最佳匹配

    Returns:
        匹配结果列表
    """
    matcher = BatchMatcher()
    return matcher.match_candidate_to_jobs(candidate_profile, jobs, top_n)


async def batch_match(
    candidates: List[Dict],
    jobs: List[Dict]
) -> Dict[str, List[Dict]]:
    """
    批量匹配

    Args:
        candidates: 候选人列表
        jobs: 岗位列表

    Returns:
        每个候选人的匹配结果
    """
    matcher = BatchMatcher()
    return matcher.match_multiple_candidates(candidates, jobs)


# 主程序测试
if __name__ == "__main__":
    import asyncio

    async def test():
        # 模拟候选人
        candidate = {
            "name": "张三",
            "hard_skills": ["Python", "Java", "大数据", "机器学习", "架构设计"],
            "highest_degree": "硕士",
            "expected_salary": "40k-60k",
            "work_experience": [
                {"company": "阿里巴巴", "position": "高级工程师"},
                {"company": "腾讯", "position": "工程师"}
            ]
        }

        # 模拟岗位
        jobs = [
            {
                "company": "字节跳动",
                "position": "Python高级工程师",
                "salary": "35k-55k",
                "requirements": ["Python", "大数据", "机器学习"],
                "experience": "3-5年",
                "education": "本科及以上",
                "platform": "Boss直聘"
            },
            {
                "company": "美团",
                "position": "Java架构师",
                "salary": "40k-60k",
                "requirements": ["Java", "架构设计", "微服务"],
                "experience": "5年以上",
                "education": "本科及以上",
                "platform": "猎聘"
            }
        ]

        matcher = BatchMatcher()
        results = matcher.match_candidate_to_jobs(candidate, jobs)

        print("=== 匹配结果 ===")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['position']} @ {result['company']}")
            print(f"   综合匹配度: {result['match_score']}%")
            print(f"   推荐等级: {result['recommendation']}")
            print(f"   技能匹配: {result['skill_match']}%")
            print(f"   经验匹配: {result['experience_match']}%")

    asyncio.run(test())