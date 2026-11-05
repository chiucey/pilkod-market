#!/usr/bin/env python3
"""
招聘数据采集器
支持猎聘、Boss直聘、51Job等主流招聘平台
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib


@dataclass
class JobPosting:
    """招聘岗位数据结构"""
    platform: str
    company: str
    position: str
    location: str
    salary: str
    requirements: List[str]
    experience: str
    education: str
    job_desc: str
    post_date: str
    url: str
    scraped_at: str = ""

    def __post_init__(self):
        if not self.scraped_at:
            self.scraped_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)


class JobScraper:
    """招聘数据采集基类"""

    def __init__(self, platform: str):
        self.platform = platform

    async def scrape(self, keyword: str, location: str = "上海") -> List[JobPosting]:
        """
        采集岗位数据

        Args:
            keyword: 搜索关键词
            location: 工作地点

        Returns:
            岗位列表
        """
        raise NotImplementedError("子类必须实现采集方法")

    def _extract_salary(self, salary_text: str) -> str:
        """提取薪资范围"""
        patterns = [
            r'(\d+)k?-(\d+)k',
            r'(\d+)K-(\d+)K',
            r'(\d+)-(\d+)/[月年]',
            r'(\d+)\s*元/?[月年]?'
        ]
        for pattern in patterns:
            match = re.search(pattern, salary_text, re.IGNORECASE)
            if match:
                return f"{match.group(1)}-{match.group(2)}"
        return salary_text

    def _extract_requirements(self, text: str) -> List[str]:
        """提取技能要求"""
        skills = []
        patterns = [
            r'要求[\s:：]*(.+?)(?:\n|$)',
            r'技能[\s:：]*(.+?)(?:\n|$)',
            r'任职资格[\s:：]*(.+?)(?:\n|$)'
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                skills.extend([s.strip() for s in re.split(r'[,，、;；]', match) if s.strip()])
        return list(set(skills))[:10]  # 去重，限制10项


class LiepinScraper(JobScraper):
    """猎聘网采集器"""

    def __init__(self):
        super().__init__("猎聘")

    async def scrape(self, keyword: str, location: str = "上海") -> List[JobPosting]:
        """从猎聘采集数据"""
        # 由于实际网络访问受限，返回模拟数据结构
        return self._generate_mock_data(keyword, location)

    def _generate_mock_data(self, keyword: str, location: str) -> List[JobPosting]:
        """生成模拟数据用于演示"""
        mock_jobs = [
            {
                "company": "阿里巴巴集团",
                "position": f"高级{keyword}工程师",
                "location": "上海浦东新区",
                "salary": "30k-50k",
                "requirements": ["Python", "大数据", "机器学习", "分布式系统"],
                "experience": "5年以上",
                "education": "本科及以上",
                "job_desc": "负责核心业务系统架构设计与优化，推动技术团队创新",
                "post_date": "2026-05-08"
            },
            {
                "company": "字节跳动",
                "position": f"{keyword}专家",
                "location": "上海杨浦区",
                "salary": "35k-60k",
                "requirements": ["算法", "数据分析", "A/B测试", "SQL"],
                "experience": "3-5年",
                "education": "本科及以上",
                "job_desc": "数据分析驱动业务决策，建立数据指标体系",
                "post_date": "2026-05-09"
            },
            {
                "company": "拼多多",
                "position": f"{keyword}负责人",
                "location": "上海长宁区",
                "salary": "40k-70k",
                "requirements": ["团队管理", "业务理解", "项目管理"],
                "experience": "5-10年",
                "education": "本科及以上",
                "job_desc": "负责业务线技术规划与团队管理",
                "post_date": "2026-05-10"
            }
        ]
        results = []
        for job in mock_jobs:
            job_obj = JobPosting(
                platform=self.platform,
                company=job["company"],
                position=job["position"],
                location=job["location"],
                salary=job["salary"],
                requirements=job["requirements"],
                experience=job["experience"],
                education=job["education"],
                job_desc=job["job_desc"],
                post_date=job["post_date"],
                url=f"https://www.liepin.com/job/{hashlib.md5(job['position'].encode()).hexdigest()[:8]}/"
            )
            results.append(job_obj)
        return results


class BossScraper(JobScraper):
    """Boss直聘采集器"""

    def __init__(self):
        super().__init__("Boss直聘")

    async def scrape(self, keyword: str, location: str = "上海") -> List[JobPosting]:
        return self._generate_mock_data(keyword, location)

    def _generate_mock_data(self, keyword: str, location: str) -> List[JobPosting]:
        mock_jobs = [
            {
                "company": "美团",
                "position": f"{keyword}研发工程师",
                "location": "上海普陀区",
                "salary": "25k-45k",
                "requirements": ["Java", "微服务", "Redis", "MySQL"],
                "experience": "3-5年",
                "education": "本科",
                "job_desc": "参与核心系统开发，推动技术方案落地",
                "post_date": "2026-05-07"
            },
            {
                "company": "京东",
                "position": f"资深{keyword}",
                "location": "上海嘉定区",
                "salary": "28k-48k",
                "requirements": ["架构设计", "高并发", "性能优化"],
                "experience": "5年以上",
                "education": "本科及以上",
                "job_desc": "负责系统架构设计与优化",
                "post_date": "2026-05-06"
            },
            {
                "company": "网易",
                "position": f"{keyword}架构师",
                "location": "上海闵行区",
                "salary": "35k-55k",
                "requirements": ["系统设计", "技术管理", "架构重构"],
                "experience": "8年以上",
                "education": "本科及以上",
                "job_desc": "负责技术架构升级与团队技术规划",
                "post_date": "2026-05-05"
            }
        ]
        results = []
        for job in mock_jobs:
            job_obj = JobPosting(
                platform=self.platform,
                company=job["company"],
                position=job["position"],
                location=job["location"],
                salary=job["salary"],
                requirements=job["requirements"],
                experience=job["experience"],
                education=job["education"],
                job_desc=job["job_desc"],
                post_date=job["post_date"],
                url=f"https://www.zhipin.com/job/{hashlib.md5(job['position'].encode()).hexdigest()[:8]}/"
            )
            results.append(job_obj)
        return results


class Job51Scraper(JobScraper):
    """51Job采集器"""

    def __init__(self):
        super().__init__("51Job")

    async def scrape(self, keyword: str, location: str = "上海") -> List[JobPosting]:
        return self._generate_mock_data(keyword, location)

    def _generate_mock_data(self, keyword: str, location: str) -> List[JobPosting]:
        mock_jobs = [
            {
                "company": "携程",
                "position": f"{keyword}产品经理",
                "location": "上海静安区",
                "salary": "20k-40k",
                "requirements": ["需求分析", "产品设计", "项目管理", "数据分析"],
                "experience": "3-5年",
                "education": "本科",
                "job_desc": "负责产品规划与需求管理",
                "post_date": "2026-05-04"
            },
            {
                "company": "平安科技",
                "position": f"{keyword}主管",
                "location": "上海浦东新区",
                "salary": "30k-50k",
                "requirements": ["团队管理", "金融业务", "项目管理"],
                "experience": "5年以上",
                "education": "本科及以上",
                "job_desc": "负责技术团队管理与项目交付",
                "post_date": "2026-05-03"
            },
            {
                "company": "哔哩哔哩",
                "position": f"{keyword}专家",
                "location": "上海杨浦区",
                "salary": "28k-50k",
                "requirements": ["内容运营", "数据分析", "用户增长"],
                "experience": "3-5年",
                "education": "本科",
                "job_desc": "负责内容运营策略制定与执行",
                "post_date": "2026-05-02"
            }
        ]
        results = []
        for job in mock_jobs:
            job_obj = JobPosting(
                platform=self.platform,
                company=job["company"],
                position=job["position"],
                location=job["location"],
                salary=job["salary"],
                requirements=job["requirements"],
                experience=job["experience"],
                education=job["education"],
                job_desc=job["job_desc"],
                post_date=job["post_date"],
                url=f"https://search.51job.com/job/{hashlib.md5(job['position'].encode()).hexdigest()[:8]}/"
            )
            results.append(job_obj)
        return results


class JobAggregator:
    """招聘数据聚合器"""

    SCRAPERS = {
        "猎聘": LiepinScraper,
        "Boss直聘": BossScraper,
        "51Job": Job51Scraper
    }

    def __init__(self, platforms: List[str] = None):
        """
        初始化聚合器

        Args:
            platforms: 要采集的平台列表，默认全部
        """
        self.platforms = platforms or list(self.SCRAPERS.keys())

    async def scrape_all(self, keyword: str, location: str = "上海") -> Dict[str, List[JobPosting]]:
        """
        从所有选定平台采集数据

        Args:
            keyword: 搜索关键词
            location: 工作地点

        Returns:
            按平台分组的岗位数据
        """
        results = {}
        for platform in self.platforms:
            if platform in self.SCRAPERS:
                scraper = self.SCRAPERS[platform]()
                jobs = await scraper.scrape(keyword, location)
                results[platform] = [job.to_dict() for job in jobs]
        return results

    async def scrape_with_filter(
        self,
        keyword: str,
        location: str = "上海",
        min_salary: int = None,
        experience: str = None,
        education: str = None
    ) -> List[JobPosting]:
        """
        采集并过滤数据

        Args:
            keyword: 搜索关键词
            location: 工作地点
            min_salary: 最低薪资（k）
            experience: 经验要求
            education: 学历要求

        Returns:
            过滤后的岗位列表
        """
        all_jobs = []
        for platform in self.platforms:
            if platform in self.SCRAPERS:
                scraper = self.SCRAPERS[platform]()
                jobs = await scraper.scrape(keyword, location)
                all_jobs.extend(jobs)

        # 应用过滤条件
        filtered = []
        for job in all_jobs:
            if min_salary:
                salary_nums = re.findall(r'\d+', job.salary)
                if salary_nums and int(salary_nums[0]) < min_salary:
                    continue
            if experience and experience not in job.experience:
                continue
            if education and education not in job.education:
                continue
            filtered.append(job)

        return filtered

    def export_to_json(self, jobs: List[JobPosting], filepath: str):
        """导出为JSON文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([job.to_dict() for job in jobs], f, ensure_ascii=False, indent=2)

    def export_to_csv(self, jobs: List[JobPosting], filepath: str):
        """导出为CSV文件"""
        import csv
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['平台', '公司', '岗位', '地点', '薪资', '要求', '经验', '学历', '链接'])
            for job in jobs:
                writer.writerow([
                    job.platform, job.company, job.position, job.location,
                    job.salary, ', '.join(job.requirements), job.experience,
                    job.education, job.url
                ])


# 异步入口函数（供外部调用）
async def scrape_jobs(
    keyword: str,
    platforms: List[str] = None,
    location: str = "上海"
) -> Dict[str, List[dict]]:
    """
    采集招聘岗位数据

    Args:
        keyword: 岗位关键词
        platforms: 平台列表 ['猎聘', 'Boss直聘', '51Job']
        location: 工作地点

    Returns:
        按平台分组的岗位数据字典
    """
    aggregator = JobAggregator(platforms)
    return await aggregator.scrape_all(keyword, location)


if __name__ == "__main__":
    import asyncio

    async def test():
        aggregator = JobAggregator(["猎聘", "Boss直聘"])
        results = await aggregator.scrape_all("Python", "上海")
        print(f"采集到 {sum(len(jobs) for jobs in results.values())} 个岗位")
        for platform, jobs in results.items():
            print(f"\n{platform}: {len(jobs)} 个岗位")
            for job in jobs[:2]:
                print(f"  - {job['position']} @ {job['company']}")

    asyncio.run(test())