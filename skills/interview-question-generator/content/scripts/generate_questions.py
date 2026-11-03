#!/usr/bin/env python3
"""
智能面试题生成器 - 基于岗位信息生成结构化面试题
支持命令行参数和交互式输入
"""

import json
import argparse
import sys
from typing import Optional, Dict, List, Any


# 岗位类型识别
JOB_TYPE_PATTERNS = {
    "技术/研发": ["工程师", "开发", "前端", "后端", "全栈", "Java", "Python", "Go", "C++", "算法", "测试", "运维", "DBA", "架构师", "技术总监", "CTO"],
    "产品": ["产品经理", "产品助理", "产品总监", "需求分析", "BA"],
    "运营": ["运营", "策划", "内容运营", "用户运营", "活动运营", "社群运营", "电商运营"],
    "市场/营销": ["市场", "营销", "推广", "品牌", "公关", "BD", "商务"],
    "销售": ["销售", "客户经理", "Account", "Sales", "招商"],
    "管理": ["经理", "总监", "主管", "Leader", "负责人", "VP", "COO", "CFO", "CHO"],
    "财务": ["财务", "会计", "审计", "投融资", "风控", "税务"],
    "行政": ["行政", "文员", "助理", "秘书", "前台", "后勤"],
    "HR": ["HR", "人力", "招聘", "培训", "薪酬", "绩效", "HRBP"],
    "管培生/校招": ["管培", "应届", "实习", "intern", "校招"]
}

# 核心技能关键词库
SKILL_KEYWORDS = {
    "编程语言": ["Python", "Java", "JavaScript", "C++", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "TypeScript"],
    "数据处理": ["SQL", "数据分析", "Python", "R", "Excel", "SPSS", "ETL", "Hive"],
    "框架技术": ["React", "Vue", "Angular", "Spring", "Django", "Flask", "Node.js", "Express"],
    "云与DevOps": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "K8s", "Jenkins", "CI/CD", "Git"],
    "机器学习": ["机器学习", "深度学习", "TensorFlow", "PyTorch", "NLP", "CV", "AI"],
    "产品设计": ["产品设计", "PRD", "需求分析", "Axure", "Figma", "Sketch", "UI", "UX", "用户体验"],
    "项目管理": ["项目管理", "敏捷", "Scrum", "Kanban", "Jira", "Confluence", "PM", "PMP"],
    "营销技能": ["SEO", "SEM", "信息流", "私域", "社群", "直播", "内容营销", "品牌营销"],
    "销售技能": ["客户管理", "CRM", "谈判", "销售技巧", "大客户", "渠道管理"],
    "软技能": ["沟通", "协调", "领导力", "团队管理", "演讲", "汇报", "跨部门"]
}


def identify_job_type(job_title: str, responsibilities: str = "") -> str:
    """识别岗位类型"""
    text = (job_title + " " + responsibilities).lower()

    for job_type, keywords in JOB_TYPE_PATTERNS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return job_type
    return "通用岗位"


def extract_skills(qualifications: str, responsibilities: str) -> Dict[str, List[str]]:
    """从文本中提取技能关键词"""
    text = (qualifications + " " + responsibilities)

    found_skills = {}
    for skill_category, keywords in SKILL_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in text]
        if matched:
            found_skills[skill_category] = matched

    return found_skills


def detect_leadership(responsibilities: str) -> bool:
    """检测是否需要领导力相关题目"""
    leadership_keywords = ["管理", "带领", "负责", "协调", "团队", "下属", "汇报", "团队规模"]
    return any(kw in responsibilities for kw in leadership_keywords)


def detect_client_facing(responsibilities: str) -> bool:
    """检测是否需要对客相关题目"""
    client_keywords = ["客户", "销售", "对接", "服务", "商务", "BD", "渠道"]
    return any(kw in responsibilities for kw in client_keywords)


def detect_data_focus(responsibilities: str, qualifications: str) -> bool:
    """检测是否需要数据分析相关题目"""
    text = responsibilities + " " + qualifications
    data_keywords = ["数据", "分析", "报表", "指标", "监控", "BI", "Dashboard"]
    return any(kw in text for kw in data_keywords)


def generate_interview_questions(
    job_title: str,
    responsibilities: str = "",
    qualifications: str = "",
    experience_years: int = 0,
    interview_duration: int = 45,
    output_format: str = "markdown"
) -> dict:
    """
    根据岗位信息生成结构化面试题

    Args:
        job_title: 岗位名称
        responsibilities: 岗位职责描述
        qualifications: 任职资格
        experience_years: 要求的经验年限
        interview_duration: 面试时长（分钟）
        output_format: 输出格式 (markdown/json)

    Returns:
        包含所有面试题的字典
    """

    # 基础信息提取
    job_type = identify_job_type(job_title, responsibilities)
    skills = extract_skills(qualifications, responsibilities)
    needs_leadership = detect_leadership(responsibilities)
    needs_client = detect_client_facing(responsibilities)
    needs_data = detect_data_focus(responsibilities, qualifications)

    # 生成各类题目
    questions = {
        "metadata": {
            "job_title": job_title,
            "job_type": job_type,
            "experience_years": experience_years,
            "interview_duration": interview_duration,
            "identified_skills": skills,
            "question_count": 0
        },
        "behavioral": generate_behavioral_questions(job_title, job_type, responsibilities, experience_years, needs_leadership),
        "situational": generate_situational_questions(job_title, job_type, responsibilities, needs_leadership, needs_client),
        "technical": generate_technical_questions(job_title, job_type, skills, needs_data),
        "cultural_fit": generate_cultural_questions(job_title, job_type, experience_years),
        "stress": generate_stress_questions(job_title, job_type),
        "evaluation_dimensions": generate_evaluation_dimensions(job_type, needs_leadership, needs_client)
    }

    # 统计题数
    for category in ["behavioral", "situational", "technical", "cultural_fit", "stress"]:
        questions["metadata"]["question_count"] += len(questions[category])

    return questions


def generate_behavioral_questions(job_title: str, job_type: str, responsibilities: str, years: int, needs_leadership: bool) -> List[Dict]:
    """生成行为面试题（STAR法则）"""
    questions = []

    # 核心STAR题 - 项目全流程
    questions.append({
        "question": f"请描述你过去在{job_type}岗位上独立完成的一个代表性项目，从立项到交付的全过程。请用STAR法则详细说明。",
        "考察要素": "自主性与执行力",
        "STAR提示": "Situation（背景）→ Task（任务）→ Action（行动）→ Result（结果+数据）",
        "评分标准": {
            "5分": "有清晰时间线、具体行动步骤和量化结果，能区分个人与团队贡献",
            "4分": "叙述完整，有具体行动但结果量化不足",
            "3分": "有完整叙述但缺乏数据支撑或细节",
            "2分": "叙述模糊，重点不突出",
            "1分": "无法描述具体项目或与岗位无关"
        },
        "追问提示": [
            "这个项目你面临的最大挑战是什么？",
            "结果有哪些可量化的指标？",
            "如果重新做一次，你会做哪些调整？"
        ]
    })

    # 成就导向题
    questions.append({
        "question": f"在过去{years or 3}年的{job_type}工作中，你最骄傲的一项成就是什么？请用STAR法则详细说明，重点说明你的个人贡献。",
        "考察要素": "职业成就与自我认知",
        "STAR提示": "背景→目标→你的核心行动→量化结果→个人成长",
        "评分标准": {
            "5分": "成就与岗位高度相关，有明确数据支撑，体现个人独特价值",
            "4分": "成就有数据支撑，但个人贡献与团队贡献边界模糊",
            "3分": "有成就叙述但与岗位关联性弱",
            "2分": "成就描述泛泛或缺乏说服力",
            "1分": "无法描述具体成就或明显夸大"
        },
        "追问提示": [
            "在这个成就中，你与团队成员的分工是怎样的？",
            "这个成就对业务产生了什么具体影响？",
            "你从中学到了什么，对现在的工作有什么帮助？"
        ]
    })

    # 领导力题（根据职责定制）
    if needs_leadership:
        questions.append({
            "question": "请描述一次你带领团队完成重要任务的经历。你是如何进行团队分工、目标设定和进度管理的？",
            "考察要素": "团队领导与分工协作",
            "STAR提示": "团队规模与构成→分工逻辑→协调机制→遇到的最大挑战→最终成果",
            "评分标准": {
                "5分": "能清晰描述团队分工逻辑、决策过程、协调机制和量化成果",
                "4分": "有完整叙述，分工和协调有亮点",
                "3分": "有叙述但分工细节和协调机制不清晰",
                "2分": "以执行为主，缺乏管理思维",
                "1分": "缺乏领导经验或描述空洞"
            },
            "追问提示": [
                "团队有多少人？你如何知人善任？",
                "过程中遇到的最大分歧是什么？如何解决的？",
                "你是如何做绩效追踪和反馈的？"
            ]
        })

    # 冲突管理题
    if "跨部门" in responsibilities or "合作" in responsibilities or "协调" in responsibilities:
        questions.append({
            "question": "请描述一次你在工作中与他人（同事/领导/客户）产生分歧或冲突的经历，你是如何处理的？最终结果如何？",
            "考察要素": "冲突管理与沟通能力",
            "STAR提示": "冲突背景→你的立场→你的行动→沟通策略→最终结果",
            "评分标准": {
                "5分": "展现同理心、有效沟通，找到双赢解决方案并维护关系",
                "4分": "能解决冲突，方法较得当",
                "3分": "能解决但方法较单一或被动",
                "2分": "回避冲突或激化矛盾",
                "1分": "无法描述处理冲突的经历"
            },
            "追问提示": [
                "对方的主要诉求是什么？你是如何回应的？",
                "有没有考虑过其他解决方案？",
                "事后你和对方的关系有什么变化？"
            ]
        })

    # 抗压题
    questions.append({
        "question": "请描述一次你在高压环境下（如紧迫的deadline、突发问题、高目标压力）按时完成任务的经历。你是如何应对的？",
        "考察要素": "时间管理与抗压能力",
        "STAR提示": "压力来源→你的应对策略→具体行动→时间管理方法→最终结果",
        "评分标准": {
            "5分": "有具体压力来源、系统的应对策略、有效的时间管理方法",
            "4分": "能抗压完成任务，有应对策略但不够系统",
            "3分": "能完成但过程描述不够具体",
            "2分": "依赖他人帮助或结果不理想",
            "1分": "在压力下放弃或无法完成任务"
        },
        "追问提示": [
            "压力主要来自哪里？你优先级判断的标准是什么？",
            "有没有什么方法帮你保持效率和冷静？",
            "这次经历对你后续工作有什么影响？"
        ]
    })

    return questions


def generate_situational_questions(job_title: str, job_type: str, responsibilities: str, needs_leadership: bool, needs_client: bool) -> List[Dict]:
    """生成情景模拟题"""
    scenarios = []

    # 适应能力题
    scenarios.append({
        "question": f"假设你入职后第一周，发现{job_type}的工作内容与你的预期有较大差距，你会怎么做？",
        "考察维度": "期望管理 & 适应能力",
        "参考答案": "①主动与直属上级沟通，明确工作预期和优先级；②主动学习业务知识，缩短适应期；③记录具体差异点，用数据支撑反馈；④保持开放心态，评估是认知偏差还是真实问题；⑤设定90天适应计划",
        "评分标准": {
            "5分": "主动沟通+制定适应计划+持续反馈的完整闭环",
            "4分": "主动沟通，有适应意识",
            "3分": "被动等待或私下抱怨",
            "2分": "消极对待或直接离职意向",
            "1分": "完全无法处理这种情况"
        }
    })

    # 多任务处理题
    scenarios.append({
        "question": f"假设你同时收到3个紧急任务，都需要在当天完成，但时间精力有限，你会如何处理？",
        "考察维度": "优先级判断 & 时间管理",
        "参考答案": "①识别3个任务的紧急程度、影响范围和deadline；②与相关方沟通调整预期，说明资源约束；③按重要紧急矩阵（ Eisenhower）排列优先级；④必要时寻求资源支持或延期低优先级任务；⑤及时汇报进展，管理各方期望",
        "评分标准": {
            "5分": "有系统方法论+沟通协调+资源争取的完整方案",
            "4分": "有基本的优先级判断方法",
            "3分": "有基本判断但方法较随意",
            "2分": "随意处理或只做一个忽略其他",
            "1分": "无法应对或陷入混乱"
        }
    })

    # 学习能力题
    scenarios.append({
        "question": f"假设你的直属领导安排了一项你不熟悉的任务，需要你在2天内交付，你会怎么做？",
        "考察维度": "学习能力 & 主动求助",
        "参考答案": "①快速评估任务难度和自身能力差距；②列出关键问题清单；③优先查阅内部文档/向有经验同事请教；④设定阶段性目标确保进度；⑤坦诚告知领导风险和预期，协商可行方案",
        "评分标准": {
            "5分": "主动出击+资源整合+预期管理的完整闭环",
            "4分": "主动学习，有求助意识",
            "3分": "闷头苦干，效率低下但不放弃",
            "2分": "遇到困难就停滞",
            "1分": "直接推脱或拒绝任务"
        }
    })

    # 客户/对客题
    if needs_client:
        scenarios.append({
            "question": "假设你对接的一位重要客户提出了一项合同外的需求，且时间紧迫，你会如何应对？",
            "考察维度": "客户管理 & 谈判能力",
            "参考答案": "①先倾听并确认需求的真实背景和优先级；②评估公司资源、可行性和影响；③提出替代方案或升级路径（如付费延期/简化版）；④平衡客户满意度与公司利益；⑤及时跟进承诺，建立信任",
            "评分标准": {
                "5分": "双赢思维+资源评估+方案协商的完整闭环",
                "4分": "有客户意识，能平衡双方利益",
                "3分": "单方面妥协或直接拒绝",
                "2分": "拖延或推诿",
                "1分": "不尊重客户或损害公司利益"
            }
        })

    # 团队管理题
    if needs_leadership:
        scenarios.append({
            "question": "假设你发现团队中有一名成员连续2周绩效不达标，你会如何处理？",
            "考察维度": "绩效管理 & 员工辅导",
            "参考答案": "①私下沟通，了解原因（能力问题/态度问题/外部因素）；②设定明确改进目标和期限；③提供支持和资源（如培训、导师）；④持续跟进并记录；⑤必要时启动正式绩效改进流程",
            "评分标准": {
                "5分": "有系统方法+辅导意识+公平公正的处理方式",
                "4分": "有辅导意识，能区分问题类型",
                "3分": "直接上级介入或简单批评",
                "2分": "放任不管或立即放弃",
                "1分": "公开批评或打击报复"
            }
        })

    return scenarios


def generate_technical_questions(job_title: str, job_type: str, skills: Dict[str, List[str]], needs_data: bool) -> List[Dict]:
    """生成专业知识题"""
    questions = []

    # 岗位认知题
    questions.append({
        "question": f"请谈谈你对{job_type}这个岗位核心能力模型的理解，你认为最重要的3项能力是什么？为什么？",
        "考察维度": "岗位认知 & 自我定位",
        "参考答案": "结合岗位特点回答，常见要素：①专业硬技能②沟通协作③业务理解④学习能力⑤责任心⑥目标导向。优秀回答应能说清每项能力的重要性及关联性。",
        "评分标准": {
            "5分": "认知清晰有深度，能结合业务场景说明，能力间有逻辑关联",
            "4分": "认知较清晰，与岗位匹配",
            "3分": "认知一般，缺乏深度思考",
            "2分": "认知模糊或与岗位不符",
            "1分": "无法回答"
        }
    })

    # 数据分析题
    if needs_data or "数据处理" in skills:
        questions.append({
            "question": "你在以往工作中是如何用数据驱动决策的？能举一个具体例子吗？",
            "考察维度": "数据思维 & 分析能力",
            "参考答案": "①明确业务问题；②确定分析指标；③数据获取与处理；④分析与建模；⑤结论与落地；⑥效果验证",
            "评分标准": {
                "5分": "有完整数据驱动案例，有量化结果，能说明数据局限性",
                "4分": "有数据使用经验，能举出例子",
                "3分": "有数据意识但不成体系",
                "2分": "不擅用数据，决策靠直觉",
                "1分": "抵触或不会使用数据"
            },
            "追问提示": [
                "你常用的数据指标有哪些？",
                "如何验证数据的准确性？",
                "如果数据与直觉冲突，你会怎么办？"
            ]
        })

    # 技术/专业深挖题（根据识别的技能定制）
    if "项目管理" in skills or "敏捷" in str(skills):
        questions.append({
            "question": "请描述你管理或参与的一个项目的完整流程，你使用了哪些项目管理方法？有什么心得？",
            "考察维度": "项目管理能力",
            "参考答案": "①项目启动（目标、干系人）→②规划（WBS、风险识别）→③执行→④监控（进度、质量）→⑤收尾复盘。方法论：敏捷/Scrum/瀑布/Kanban等。",
            "评分标准": {
                "5分": "方法论清晰+有工具实践+有数据复盘+持续改进",
                "4分": "有流程概念，有实践经验",
                "3分": "有参与但缺乏系统方法论",
                "2分": "缺乏方法论，过程混乱",
                "1分": "未参与过项目管理"
            }
        })

    # 团队管理题
    if "软技能" in skills and any(s in str(skills) for s in ["领导力", "团队管理"]):
        questions.append({
            "question": "作为团队负责人，你是如何帮助团队成员提升绩效的？请举例说明。",
            "考察维度": "团队管理与人才培养",
            "参考答案": "①设定清晰目标（SMART）；②及时反馈与辅导；③绩效追踪与面谈；④差异化激励；⑤个人发展规划；⑥授权与信任",
            "评分标准": {
                "5分": "有体系方法+有成功案例+有数据支撑",
                "4分": "有管理经验，方法得当",
                "3分": "有经验但不系统",
                "2分": "缺乏管理经验或方法不当",
                "1分": "未带过团队"
            }
        })

    # 营销/运营题
    if "营销技能" in skills:
        questions.append({
            "question": "请分享一个你策划的最成功的营销活动。从目标制定到执行落地，你是如何思考和决策的？",
            "考察维度": "营销策划能力",
            "参考答案": "①明确目标受众和KPI；②竞品分析和差异化定位；③创意策略；④渠道选择和预算分配；⑤执行和优化；⑥效果复盘",
            "评分标准": {
                "5分": "有完整案例+数据支撑+复盘反思",
                "4分": "有案例，思考较全面",
                "3分": "有参与但缺乏主导",
                "2分": "描述泛泛",
                "1分": "无法举例"
            }
        })

    return questions


def generate_cultural_questions(job_title: str, job_type: str, years: int) -> List[Dict]:
    """生成文化匹配题"""
    return [
        {
            "question": "你为什么对我们公司和这个{job_type}岗位感兴趣？你期望在这里获得什么？".format(job_type=job_type),
            "考察维度": "动机 & 稳定性",
            "参考答案": "对公司业务有了解+对岗位有真实兴趣+有清晰的职业期待+与公司价值观契合",
            "评分标准": {
                "5分": "有真实兴趣，了解公司业务，职业规划清晰，价值观契合",
                "4分": "有一定了解，有真实兴趣",
                "3分": "有基本了解但较表面",
                "2分": "单纯追求薪资或稳定",
                "1分": "盲目投递，无法说明原因"
            }
        },
        {
            "question": "请描述你理想中的工作团队氛围是什么样的？你适合什么样的管理风格？过去的经历证明你如何适应不同风格的领导？",
            "考察维度": "文化匹配 & 自我认知",
            "参考答案": "能清晰描述偏好+举出过去适应不同环境的例子+说明自己的调整方式",
            "评分标准": {
                "5分": "自我认知清晰，有跨文化适应经验，成熟度高",
                "4分": "有一定自我认知",
                "3分": "描述模糊或过于理想化",
                "2分": "人际敏感度低",
                "1分": "抱怨过往管理风格"
            }
        },
        {
            "question": f"未来在{job_type}岗位上可能会遇到挫折或瓶颈，你通常如何应对职业低谷期？",
            "考察维度": "抗挫能力 & 成长性",
            "参考答案": "①正视问题而非逃避；②主动寻求反馈；③设定小目标重建信心；④保持学习；⑤必要时调整方向",
            "评分标准": {
                "5分": "有具体应对策略+积极心态+有成长思维",
                "4分": "有应对意识",
                "3分": "会迷茫但会调整",
                "2分": "回避问题或消极",
                "1分": "频繁离职逃避"
            }
        },
        {
            "question": "请描述一个你主动学习新技能或新知识的经历。是什么驱动你学习？你是如何保持持续学习的？",
            "考察维度": "学习意愿 & 成长型思维",
            "参考答案": "有具体学习案例+有学习方法和资源+有学习成果证明",
            "评分标准": {
                "5分": "有持续学习习惯+方法系统+有成果输出",
                "4分": "有学习意识",
                "3分": "被动学习",
                "2分": "抵触学习",
                "1分": "无学习意愿"
            }
        }
    ]


def generate_stress_questions(job_title: str, job_type: str) -> List[Dict]:
    """生成压力面试题（建议仅在必要时使用）"""
    return [
        {
            "question": "我注意到你的简历中有一段工作经历较长（超过3年），而最近换了两次工作，能具体说说原因吗？",
            "考察维度": "稳定性 & 自我反思",
            "⚠️注意": "建议仅在有充分理由时使用，提前告知候选人这是常规流程",
            "参考答案": "诚实说明原因+突出每次变化后的成长收获+说明对稳定的重视",
        },
        {
            "question": "如果最终我们录取了你，但岗位内容和今天谈的有较大出入，你能接受吗？你的底线是什么？",
            "考察维度": "灵活性 & 期望管理",
            "参考答案": "了解底线范围+询问具体出入范围+表达开放态度但有原则",
        },
        {
            "question": "你认为你最大的缺点是什么？这会如何影响你胜任这份工作？你有在做什么改进吗？",
            "考察维度": "自我认知 & 改进意愿",
            "参考答案": "真实缺点+有具体改进行动+避免说与岗位核心要求对立的缺点",
        },
        {
            "question": "你的简历中有一些经历与这个岗位的关联度不高，你怎么看这个问题？",
            "考察维度": "自我营销 & 应变能力",
            "参考答案": "说明关联性+转移可迁移能力+表达学习意愿",
        }
    ]


def generate_evaluation_dimensions(job_type: str, needs_leadership: bool, needs_client: bool) -> List[Dict]:
    """生成岗位评估维度"""
    dimensions = [
        {
            "维度": "专业知识",
            "权重": "高",
            "考察要点": "岗位所需的专业技能、知识储备和实践经验"
        },
        {
            "维度": "逻辑思维",
            "权重": "高",
            "考察要点": "分析问题的方式、思考的条理性和深度"
        },
        {
            "维度": "沟通表达",
            "权重": "中",
            "考察要点": "表达的清晰度、倾听能力和说服力"
        },
        {
            "维度": "学习能力",
            "权重": "中",
            "考察要点": "学习意愿、方法和速度"
        }
    ]

    if needs_leadership:
        dimensions.append({
            "维度": "领导力",
            "权重": "高",
            "考察要点": "团队管理、目标分解、绩效辅导和激励能力"
        })

    if needs_client:
        dimensions.append({
            "维度": "客户意识",
            "权重": "高",
            "考察要点": "客户导向、服务意识和关系维护能力"
        })

    dimensions.extend([
        {
            "维度": "抗压能力",
            "权重": "中",
            "考察要点": "高压环境下的表现、时间管理和情绪控制"
        },
        {
            "维度": "文化匹配",
            "权重": "中",
            "考察要点": "价值观契合、团队融入和职业稳定性"
        }
    ])

    return dimensions


def format_markdown(questions: dict) -> str:
    """格式化为 Markdown 输出"""
    meta = questions["metadata"]
    md = f"# 面试题库：{meta['job_title']}\n\n"
    md += f"> AI生成 · {meta['question_count']}道面试题 · 约{meta['interview_duration']}分钟\n\n"

    md += f"**岗位类型**: {meta['job_type']} | "
    md += f"**经验要求**: {meta['experience_years']}年+ | "
    md += f"**识别技能**: {', '.join([s for skills in meta['identified_skills'].values() for s in skills][:5]) if meta['identified_skills'] else '通用能力'}\n\n"

    sections = [
        ("行为面试题（STAR法则）", "behavioral", "🟡"),
        ("情景模拟题", "situational", "🔵"),
        ("专业知识题", "technical", "🟢"),
        ("文化匹配题", "cultural_fit", "🟣"),
        ("压力面试题", "stress", "🔴"),
    ]

    for title, key, emoji in sections:
        md += f"\n## {emoji} {title}（{len(questions[key])}题）\n\n"
        for i, q in enumerate(questions[key], 1):
            md += f"### {i}. {q['question']}\n\n"
            for field, value in q.items():
                if field == "question":
                    continue
                elif field in ["评分标准", "STAR提示", "参考答案"]:
                    md += f"| **{field}** |\n|------|\n"
                    if isinstance(value, dict):
                        for score, desc in value.items():
                            md += f"| {score} | {desc} |\n"
                    else:
                        md += f"| {value} |\n"
                    md += "\n"
                elif field == "追问提示":
                    md += f"| **追问提示** |\n|------|\n"
                    for tip in value:
                        md += f"| • {tip} |\n"
                    md += "\n"
                elif field == "⚠️注意":
                    md += f"> ⚠️ {value}\n\n"
                else:
                    md += f"**{field}**: {value}\n\n"

    # 评估维度
    md += f"\n---\n\n## 📊 评估维度（{len(questions['evaluation_dimensions'])}项）\n\n"
    md += "| 维度 | 权重 | 考察要点 |\n|------|------|----------|\n"
    for dim in questions["evaluation_dimensions"]:
        md += f"| {dim['维度']} | {dim['权重']} | {dim['考察要点']} |\n"

    return md


def main():
    parser = argparse.ArgumentParser(description="智能面试题生成器")
    parser.add_argument("--job-title", "-t", default="", help="岗位名称")
    parser.add_argument("--responsibilities", "-r", default="", help="岗位职责（多行或逗号分隔）")
    parser.add_argument("--qualifications", "-q", default="", help="任职资格")
    parser.add_argument("--experience", "-e", type=int, default=0, help="要求的工作年限")
    parser.add_argument("--duration", "-d", type=int, default=45, help="面试时长（分钟）")
    parser.add_argument("--output", "-o", choices=["markdown", "json"], default="markdown", help="输出格式")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式输入模式")

    args = parser.parse_args()

    if args.interactive or not args.job_title:
        print("=" * 50)
        print("智能面试题生成器 - 交互模式")
        print("=" * 50)
        args.job_title = input("\n请输入岗位名称：").strip() or "通用岗位"
        args.responsibilities = input("请输入岗位职责（可选，直接回车跳过）：\n").strip()
        args.qualifications = input("请输入任职资格（可选，直接回车跳过）：\n").strip()
        try:
            args.experience = int(input("要求工作年限（可选，直接回车为0）：").strip() or "0")
        except ValueError:
            args.experience = 0
        try:
            args.duration = int(input("面试时长分钟数（可选，直接回车为45）：").strip() or "45")
        except ValueError:
            args.duration = 45

    if not args.job_title:
        print("错误：岗位名称不能为空", file=sys.stderr)
        sys.exit(1)

    result = generate_interview_questions(
        job_title=args.job_title,
        responsibilities=args.responsibilities,
        qualifications=args.qualifications,
        experience_years=args.experience,
        interview_duration=args.duration,
        output_format=args.output
    )

    if args.output == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(result))


if __name__ == "__main__":
    main()
