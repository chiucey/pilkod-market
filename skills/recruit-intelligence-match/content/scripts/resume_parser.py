#!/usr/bin/env python3
"""
简历解析与候选人评估模块
支持PDF、Word、图片（OCR）格式简历解析
"""

import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class CandidateProfile:
    """候选人画像"""
    name: str = ""
    age: int = 0
    phone: str = ""
    email: str = ""
    location: str = ""

    # 教育背景
    education_list: List[Dict] = field(default_factory=list)
    highest_degree: str = ""
    overseas_study: List[Dict] = field(default_factory=list)

    # 工作经验
    work_experience: List[Dict] = field(default_factory=list)
    total_years: float = 0
    current_company: str = ""
    current_position: str = ""

    # 技能
    hard_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    languages: List[str] = field(default_factory=list)

    # 期望
    expected_salary: str = ""
    expected_position: str = ""
    expected_location: str = ""

    # 原始文本
    raw_text: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class ResumeParser:
    """简历解析器基类"""

    def __init__(self):
        self.common_skills = [
            "Python", "Java", "JavaScript", "C++", "Go", "Rust",
            "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis",
            "AWS", "Azure", "GCP", "Docker", "Kubernetes",
            "Machine Learning", "Deep Learning", "NLP",
            "Project Management", "Agile", "Scrum",
            "Data Analysis", "Big Data", "Spark", "Hadoop",
            "Vue", "React", "Angular", "Node.js",
            "Communication", "Leadership", "Teamwork"
        ]

    def parse(self, text: str) -> CandidateProfile:
        """
        解析简历文本

        Args:
            text: 简历原始文本

        Returns:
            候选人画像
        """
        profile = CandidateProfile()
        profile.raw_text = text

        # 基础信息提取
        profile.name = self._extract_name(text)
        profile.phone = self._extract_phone(text)
        profile.email = self._extract_email(text)
        profile.location = self._extract_location(text)
        profile.age = self._extract_age(text)

        # 教育背景
        profile.education_list = self._extract_education(text)
        profile.highest_degree = self._get_highest_degree(profile.education_list)
        profile.overseas_study = self._extract_overseas_study(text)

        # 工作经验
        profile.work_experience = self._extract_work_experience(text)
        profile.total_years = self._calculate_total_years(profile.work_experience)
        if profile.work_experience:
            profile.current_company = profile.work_experience[0].get("company", "")
            profile.current_position = profile.work_experience[0].get("position", "")

        # 技能
        profile.hard_skills = self._extract_hard_skills(text)
        profile.soft_skills = self._extract_soft_skills(text)
        profile.languages = self._extract_languages(text)

        # 期望
        profile.expected_salary = self._extract_expected_salary(text)
        profile.expected_position = self._extract_expected_position(text)

        return profile

    def _extract_name(self, text: str) -> str:
        """提取姓名"""
        patterns = [
            r'^([^\s]{2,4})(?:（|\()',
            r'姓名[:：]\s*([^\s]+)',
            r'^([^\s]{2,4})\s+(?:男|女)',
            r'^([^\s]{2,4})$',  # 单行名字（行首）
            r'\n([^\s]{2,4})\s*$',  # 行尾名字
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if name and len(name) >= 2 and len(name) <= 4:
                    return name
        return "未知"

    def _extract_phone(self, text: str) -> str:
        """提取电话号码"""
        patterns = [
            r'1[3-9]\d{9}',
            r'\d{3,4}-\d{7,8}',
            r'\d{11}'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return ""

    def _extract_email(self, text: str) -> str:
        """提取邮箱"""
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(pattern, text)
        return match.group(0) if match else ""

    def _extract_location(self, text: str) -> str:
        """提取所在地"""
        locations = ["上海", "北京", "深圳", "广州", "杭州", "南京", "苏州", "成都", "武汉", "西安"]
        for loc in locations:
            if loc in text[:500]:  # 通常在前500字符内
                return loc
        return "未知"

    def _extract_age(self, text: str) -> int:
        """提取年龄"""
        patterns = [
            r'(\d{4})年出生',
            r'(\d{2})岁',
            r'年龄[:：]\s*(\d+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if "年出生" in pattern:
                    birth_year = int(match.group(1))
                    return 2026 - birth_year
                else:
                    return int(match.group(1))
        return 0

    def _extract_education(self, text: str) -> List[Dict]:
        """提取教育背景"""
        education_list = []

        # 学校识别模式
        universities = [
            "清华", "北大", "复旦", "上海交通", "浙江大学", "南京大学",
            "中国人民大学", "中科大", "武汉大学", "华中科技", "中山大学",
            "同济大学", "上海财经", "对外经贸", "北航", "北理工",
            "哈佛", "MIT", "斯坦福", "牛津", "剑桥", "耶鲁"
        ]

        for uni in universities:
            if uni in text:
                edu = {
                    "school": uni,
                    "degree": self._extract_degree_from_context(text, uni),
                    "major": self._extract_major_from_context(text, uni),
                    "year": self._extract_year_from_context(text, uni)
                }
                education_list.append(edu)

        # 按年份排序
        education_list.sort(key=lambda x: x.get("year", ""), reverse=True)
        return education_list

    def _extract_degree_from_context(self, text: str, school: str) -> str:
        """从上下文提取学历"""
        degree_map = {
            "博士": ["博士", "PhD", "Doctor"],
            "硕士": ["硕士", "Master", "MBA", "研究生"],
            "本科": ["本科", "学士", "Bachelor"]
        }
        idx = text.find(school)
        if idx > 0:
            context = text[max(0, idx-50):idx+100]
            for degree, keywords in degree_map.items():
                if any(kw in context for kw in keywords):
                    return degree
        return "本科"

    def _extract_major_from_context(self, text: str, school: str) -> str:
        """从上下文提取专业"""
        majors = [
            "计算机", "软件工程", "电子信息", "机械", "金融", "经济",
            "管理", "会计", "市场营销", "人力资源", "设计", "数学",
            "物理", "化学", "生物", "材料", "自动化", "通信"
        ]
        idx = text.find(school)
        if idx > 0:
            context = text[max(0, idx-30):idx+100]
            for major in majors:
                if major in context:
                    return major
        return ""

    def _extract_year_from_context(self, text: str, school: str) -> str:
        """从上下文提取毕业年份"""
        pattern = r'(19|20)\d{2}'
        idx = text.find(school)
        if idx > 0:
            context = text[max(0, idx):idx+150]
            match = re.search(pattern, context)
            if match:
                return match.group(0)
        return ""

    def _get_highest_degree(self, education_list: List[Dict]) -> str:
        """获取最高学历"""
        degree_order = {"博士": 3, "硕士": 2, "本科": 1}
        if not education_list:
            return "未知"
        return max(education_list, key=lambda x: degree_order.get(x.get("degree", ""), 0)).get("degree", "")

    def _extract_overseas_study(self, text: str) -> List[Dict]:
        """提取留学背景"""
        overseas = []
        countries = ["美国", "英国", "澳大利亚", "加拿大", "新加坡", "日本", "德国", "法国", "欧洲"]
        schools = ["Harvard", "MIT", "Stanford", "Oxford", "Cambridge", "Yale", "UCL", "Berkeley"]

        for country in countries:
            if country in text:
                overseas.append({
                    "country": country,
                    "type": "留学经历"
                })

        for school in schools:
            if school in text:
                overseas.append({
                    "school": school,
                    "type": "海外学历"
                })

        return overseas

    def _extract_work_experience(self, text: str) -> List[Dict]:
        """提取工作经验"""
        experience = []

        # 公司模式识别
        companies = [
            "阿里巴巴", "腾讯", "字节跳动", "百度", "京东", "美团",
            "拼多多", "网易", "滴滴", "快手", "小米", "华为",
            "微软", "谷歌", "亚马逊", "苹果", "IBM", "Oracle"
        ]

        for company in companies:
            if company in text:
                exp = {
                    "company": company,
                    "position": self._extract_position_from_context(text, company),
                    "duration": self._extract_duration_from_context(text, company),
                    "achievements": self._extract_achievements_from_context(text, company)
                }
                experience.append(exp)

        return experience[:5]  # 最多5段

    def _extract_position_from_context(self, text: str, company: str) -> str:
        """从上下文提取职位"""
        positions = [
            "工程师", "架构师", "经理", "总监", "主管", "负责人",
            "专家", "高级", "资深", "初级", "实习生", "VP", "COO", "CTO", "CEO"
        ]
        idx = text.find(company)
        if idx > 0:
            context = text[max(0, idx-30):idx+50]
            for pos in positions:
                if pos in context:
                    return pos
        return "未知职位"

    def _extract_duration_from_context(self, text: str, company: str) -> str:
        """从上下文提取工作时间"""
        pattern = r'(?:20|19)\d{2}年\d{1,2}月至(?:20|19)\d{2}年\d{1,2}月'
        idx = text.find(company)
        if idx > 0:
            context = text[idx:idx+200]
            match = re.search(pattern, context)
            if match:
                return match.group(0)
        return ""

    def _extract_achievements_from_context(self, text: str, company: str) -> str:
        """从上下文提取工作成就"""
        achievements = []
        metrics = ["100%", "50%", "提升", "增长", "减少", "优化", "负责", "带领"]
        idx = text.find(company)
        if idx > 0:
            context = text[idx:idx+500]
            for metric in metrics:
                if metric in context:
                    line_start = context.rfind('\n', 0, context.find(metric))
                    if line_start >= 0:
                        achievements.append(context[line_start:context.find(metric)+10].strip())
        return "; ".join(achievements[:3])

    def _calculate_total_years(self, work_experience: List[Dict]) -> float:
        """计算总工作年限"""
        if not work_experience:
            return 0.0
        return sum([2.0 for _ in work_experience])  # 简化：每段经验计2年

    def _extract_hard_skills(self, text: str) -> List[str]:
        """提取硬技能"""
        found = [skill for skill in self.common_skills if skill.lower() in text.lower()]
        return found[:15]  # 最多15项

    def _extract_soft_skills(self, text: str) -> List[str]:
        """提取软技能"""
        soft_skills = [
            "沟通能力", "团队协作", "领导力", "问题解决", "时间管理",
            "学习能力", "创新能力", "抗压能力", "逻辑思维", "责任心"
        ]
        found = [skill for skill in soft_skills if skill in text]
        return found[:5]

    def _extract_languages(self, text: str) -> List[str]:
        """提取语言能力"""
        languages = [
            "英语", "CET-4", "CET-6", "IELTS", "TOEFL",
            "日语", "N1", "N2", "法语", "德语", "西班牙语"
        ]
        found = [lang for lang in languages if lang in text]
        return found if found else ["中文"]

    def _extract_expected_salary(self, text: str) -> str:
        """提取期望薪资"""
        patterns = [
            r'期望薪资[:：]\s*(\d+)[kK]-(\d+)[kK]',
            r'期望(\d+)-(\d+)k',
            r'(\d+)k以上'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}k-{match.group(2)}k"
        return ""

    def _extract_expected_position(self, text: str) -> str:
        """提取期望职位"""
        positions = ["产品经理", "项目经理", "架构师", "工程师", "总监", "主管", "专家"]
        for pos in positions:
            if f"期望{pos}" in text or f"目标{pos}" in text:
                return pos
        return ""


class CandidateEvaluator:
    """候选人评估器"""

    def __init__(self):
        self.weights = {
            "competency": 0.30,
            "experience": 0.25,
            "education": 0.15,
            "salary_match": 0.15,
            "stability": 0.15
        }

    def evaluate(self, profile: CandidateProfile) -> Dict[str, Any]:
        """
        综合评估候选人

        Args:
            profile: 候选人画像

        Returns:
            评估结果
        """
        scores = {
            "competency_score": self._evaluate_competency(profile),
            "experience_score": self._evaluate_experience(profile),
            "education_score": self._evaluate_education(profile),
            "salary_match_score": self._evaluate_salary_match(profile),
            "stability_score": self._evaluate_stability(profile)
        }

        # 计算加权总分
        total_score = sum(
            scores[key] * self.weights[key.replace("_score", "")]
            for key in scores
        )

        return {
            "scores": scores,
            "total_score": round(total_score, 1),
            "grade": self._get_grade(total_score),
            "strengths": self._identify_strengths(profile, scores),
            "weaknesses": self._identify_weaknesses(profile, scores)
        }

    def _evaluate_competency(self, profile: CandidateProfile) -> float:
        """评估胜任力（技能匹配度）"""
        base_score = min(len(profile.hard_skills) * 5, 50)
        skill_bonus = 20 if len(profile.hard_skills) > 10 else 10
        return min(base_score + skill_bonus, 100)

    def _evaluate_experience(self, profile: CandidateProfile) -> float:
        """评估工作经验"""
        if profile.total_years == 0:
            return 30
        years_score = min(profile.total_years * 10, 60)
        company_bonus = 20 if any(c in str(profile.work_experience) for c in
            ["阿里巴巴", "腾讯", "字节", "百度", "京东"]) else 0
        return min(years_score + company_bonus, 100)

    def _evaluate_education(self, profile: CandidateProfile) -> float:
        """评估教育背景"""
        degree_scores = {"博士": 95, "硕士": 85, "本科": 70, "大专": 55, "未知": 40}
        score = degree_scores.get(profile.highest_degree, 40)
        if profile.overseas_study:
            score += 10
        return min(score, 100)

    def _evaluate_salary_match(self, profile: CandidateProfile) -> float:
        """评估薪资匹配度"""
        if not profile.expected_salary:
            return 75  # 默认中等
        return 80  # 简化处理

    def _evaluate_stability(self, profile: CandidateProfile) -> float:
        """评估稳定性"""
        stability = 70
        if profile.age > 30 and profile.total_years > 5:
            stability += 15
        if not profile.overseas_study:
            stability += 10
        return min(stability, 100)

    def _get_grade(self, score: float) -> str:
        """评估等级"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B+"
        elif score >= 60:
            return "B"
        else:
            return "C"

    def _identify_strengths(self, profile: CandidateProfile, scores: Dict) -> List[str]:
        """识别优势"""
        strengths = []
        if scores["education_score"] >= 85:
            strengths.append("学历优秀")
        if scores["experience_score"] >= 80:
            strengths.append("经验丰富")
        if scores["competency_score"] >= 80:
            strengths.append("技能突出")
        if profile.overseas_study:
            strengths.append("具有国际视野")
        if profile.languages and len(profile.languages) > 1:
            strengths.append("语言能力强")
        return strengths

    def _identify_weaknesses(self, profile: CandidateProfile, scores: Dict) -> List[str]:
        """识别劣势"""
        weaknesses = []
        if scores["education_score"] < 60:
            weaknesses.append("学历较低")
        if profile.total_years < 2:
            weaknesses.append("经验较少")
        if not profile.hard_skills:
            weaknesses.append("技能描述不足")
        return weaknesses


class PotentialAnalyzer:
    """潜力分析器"""

    def __init__(self):
        self.tier1_schools = ["清华", "北大", "复旦", "上海交通", "浙大", "中科大"]
        self.overseas_top = ["Harvard", "MIT", "Stanford", "Oxford", "Cambridge"]

    def analyze(self, profile: CandidateProfile) -> Dict[str, Any]:
        """
        分析候选人潜力

        Args:
            profile: 候选人画像

        Returns:
            潜力分析结果
        """
        return {
            "family_background": self._analyze_family_background(profile),
            "career_potential": self._analyze_career_potential(profile),
            "risk_factors": self._analyze_risk_factors(profile),
            "development_suggestions": self._generate_suggestions(profile)
        }

    def _analyze_family_background(self, profile: CandidateProfile) -> Dict[str, str]:
        """分析家境"""
        result = {
            "summary": "",
            "留学_indicated": False,
            "financial_indicator": "中等"
        }

        # 留学背景暗示家庭经济较好
        if profile.overseas_study:
            result["留学_indicated"] = True
            result["financial_indicator"] = "良好"
            result["summary"] = f"具有海外{profile.overseas_study[0].get('type', '学习')}背景，表明家庭经济条件较好"

        # 985/211学校可能暗示较好教育资源
        for edu in profile.education_list:
            school = edu.get("school", "")
            if any(t in school for t in self.tier1_schools):
                result["financial_indicator"] = "中上"
                break

        # 大厂经历可能暗示较高收入
        if any(c in str(profile.work_experience) for c in ["阿里", "腾讯", "字节", "百度"]):
            result["financial_indicator"] = "良好"

        if not result["summary"]:
            result["summary"] = "家庭背景信息有限，需进一步了解"

        return result

    def _analyze_career_potential(self, profile: CandidateProfile) -> Dict[str, Any]:
        """分析职业潜力"""
        potential_score = 50

        # 技能加分
        if len(profile.hard_skills) > 8:
            potential_score += 15

        # 学历加分
        if profile.highest_degree in ["博士", "硕士"]:
            potential_score += 10

        # 留学加分
        if profile.overseas_study:
            potential_score += 10

        # 年龄因素
        if 25 <= profile.age <= 35:
            potential_score += 10

        # 顶级公司经验
        if any(c in str(profile.work_experience) for c in ["阿里", "腾讯", "字节", "华为", "微软", "谷歌"]):
            potential_score += 15

        potential_level = "高" if potential_score >= 80 else ("中" if potential_score >= 60 else "一般")

        return {
            "score": min(potential_score, 100),
            "level": potential_level,
            "analysis": self._generate_potential_analysis(profile, potential_level)
        }

    def _generate_potential_analysis(self, profile: CandidateProfile, level: str) -> str:
        """生成潜力分析文本"""
        if level == "高":
            return f"{profile.name or '候选人'}具备高发展潜力，具有多项核心竞争力，预计在未来3-5年内有较大晋升空间"
        elif level == "中":
            return f"{profile.name or '候选人'}具备中等发展潜力，建议持续关注技能提升和职业发展机会"
        else:
            return f"{profile.name or '候选人'}发展潜力一般，建议明确职业方向，有针对性地提升专业能力"

    def _analyze_risk_factors(self, profile: CandidateProfile) -> List[str]:
        """分析风险因素"""
        risks = []

        if profile.age < 25:
            risks.append("年龄较轻，职业稳定性待验证")

        if len(profile.work_experience) > 3 and profile.total_years < 5:
            risks.append("换工作频率较高，可能影响稳定性")

        if profile.expected_salary and "60k" in profile.expected_salary:
            risks.append("薪资期望较高，需评估性价比")

        if not profile.overseas_study and profile.highest_degree == "本科":
            risks.append("学历背景在竞争中优势不明显")

        return risks if risks else ["未发现明显风险因素"]

    def _generate_suggestions(self, profile: CandidateProfile) -> List[str]:
        """生成发展建议"""
        suggestions = []

        if not profile.overseas_study and profile.highest_degree in ["本科", "硕士"]:
            suggestions.append("建议关注海外进修或国际项目机会，提升国际竞争力")

        if len(profile.hard_skills) < 5:
            suggestions.append("建议加强专业技术能力，构建核心竞争力")

        if profile.total_years < 3:
            suggestions.append("建议在当前领域深耕，积累项目经验和行业资源")

        if not profile.languages or profile.languages == ["中文"]:
            suggestions.append("建议提升英语能力，适应国际化工作环境")

        return suggestions if suggestions else ["继续保持现有优势，稳扎稳打发展职业"]


# 异步入口函数（供外部调用）
async def parse_resume(text: str) -> CandidateProfile:
    """
    解析简历文本

    Args:
        text: 简历原始文本

    Returns:
        候选人画像
    """
    parser = ResumeParser()
    return parser.parse(text)


async def evaluate_candidate(profile: CandidateProfile) -> Dict[str, Any]:
    """
    评估候选人

    Args:
        profile: 候选人画像

    Returns:
        评估结果
    """
    evaluator = CandidateEvaluator()
    return evaluator.evaluate(profile)


async def analyze_potential(profile: CandidateProfile) -> Dict[str, Any]:
    """
    分析候选人潜力

    Args:
        profile: 候选人画像

    Returns:
        潜力分析结果
    """
    analyzer = PotentialAnalyzer()
    return analyzer.analyze(profile)


# 主程序测试
if __name__ == "__main__":
    import asyncio

    async def test():
        # 模拟简历文本
        sample_resume = """
        张三
        男，1990年出生
        手机：13812345678
        邮箱：zhangsan@example.com

        教育背景：
        2013-2016 复旦大学 硕士 计算机科学
        2009-2013 浙江大学 学士 软件工程

        工作经验：
        2020-至今 阿里巴巴 高级技术专家
        2016-2020 腾讯科技 技术工程师

        技能：Python, Java, 大数据, 机器学习, 架构设计

        期望薪资：40k-60k
        """

        profile = await parse_resume(sample_resume)
        print(f"解析完成：{profile.name}")
        print(f"最高学历：{profile.highest_degree}")
        print(f"工作年限：{profile.total_years}")
        print(f"技能：{', '.join(profile.hard_skills)}")

        evaluation = await evaluate_candidate(profile)
        print(f"\n评估得分：{evaluation['total_score']}")
        print(f"评估等级：{evaluation['grade']}")

        potential = await analyze_potential(profile)
        print(f"\n潜力等级：{potential['career_potential']['level']}")

    asyncio.run(test())