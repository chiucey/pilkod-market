#!/usr/bin/env python3
"""
综合评估报告生成器
生成可视化的候选人评估报告
"""

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict


@dataclass
class ReportConfig:
    """报告配置"""
    title: str = "候选人综合评估报告"
    language: str = "zh-CN"
    include_charts: bool = True
    include_potential: bool = True
    company_logo: str = ""
    author: str = "招聘智能匹配系统"


class ReportGenerator:
    """报告生成器"""

    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()

    def generate_html_report(
        self,
        candidate_profile: Dict,
        evaluation: Dict,
        potential_analysis: Dict,
        matched_jobs: List[Dict]
    ) -> str:
        """
        生成HTML报告

        Args:
            candidate_profile: 候选人画像
            evaluation: 评估结果
            potential_analysis: 潜力分析
            matched_jobs: 匹配岗位列表

        Returns:
            HTML报告内容
        """
        scores = evaluation.get("scores", {})

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; }}
        .header h1 {{ font-size: 32px; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 14px; }}
        .card {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .card-title {{ font-size: 18px; font-weight: 600; color: #2c3e50; margin-bottom: 20px; border-left: 4px solid #667eea; padding-left: 12px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .info-item {{ margin-bottom: 15px; }}
        .info-label {{ color: #7f8c8d; font-size: 13px; margin-bottom: 5px; }}
        .info-value {{ font-size: 15px; font-weight: 500; }}
        .score-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; }}
        .score-card {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; }}
        .score-value {{ font-size: 36px; font-weight: 700; color: #667eea; }}
        .score-label {{ font-size: 12px; color: #7f8c8d; margin-top: 5px; }}
        .tag {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; margin: 3px; }}
        .tag-success {{ background: #d4edda; color: #155724; }}
        .tag-warning {{ background: #fff3cd; color: #856404; }}
        .tag-info {{ background: #d1ecf1; color: #0c5460; }}
        .job-list {{ display: flex; flex-direction: column; gap: 15px; }}
        .job-item {{ display: flex; justify-content: space-between; align-items: center; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }}
        .job-info {{ flex: 1; }}
        .job-title {{ font-size: 16px; font-weight: 600; margin-bottom: 5px; }}
        .job-company {{ font-size: 14px; color: #7f8c8d; }}
        .job-score {{ font-size: 24px; font-weight: 700; color: #667eea; margin-right: 20px; }}
        .recommendation {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-weight: 500; }}
        .rec-strong {{ background: #28a745; color: white; }}
        .rec-good {{ background: #17a2b8; color: white; }}
        .rec-consider {{ background: #ffc107; color: #333; }}
        .potential-section {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }}
        .footer {{ text-align: center; padding: 20px; color: #95a5a6; font-size: 12px; }}
        .badge {{ display: inline-flex; align-items: center; padding: 4px 12px; border-radius: 12px; font-size: 12px; margin-left: 8px; }}
        .badge-high {{ background: #d4edda; color: #155724; }}
        .badge-medium {{ background: #fff3cd; color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{candidate_profile.get('name', '候选人')} - 综合评估报告</h1>
            <div class="meta">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 报告编号: {self._generate_id()}</div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="card-title">基本信息</div>
                <div class="info-item">
                    <div class="info-label">最高学历</div>
                    <div class="info-value">{candidate_profile.get('highest_degree', '未知')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">工作年限</div>
                    <div class="info-value">{candidate_profile.get('total_years', 0):.1f} 年</div>
                </div>
                <div class="info-item">
                    <div class="info-label">当前公司</div>
                    <div class="info-value">{candidate_profile.get('current_company', '未知')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">期望薪资</div>
                    <div class="info-value">{candidate_profile.get('expected_salary', '未填写')}</div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">核心技能</div>
                <div>
                    {self._render_skills(candidate_profile.get('hard_skills', []), 'success')}
                    {self._render_skills(candidate_profile.get('soft_skills', []), 'info')}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">综合评分</div>
            <div class="score-grid">
                <div class="score-card">
                    <div class="score-value">{scores.get('competency_score', 0):.0f}</div>
                    <div class="score-label">胜任力</div>
                </div>
                <div class="score-card">
                    <div class="score-value">{scores.get('experience_score', 0):.0f}</div>
                    <div class="score-label">经验</div>
                </div>
                <div class="score-card">
                    <div class="score-value">{scores.get('education_score', 0):.0f}</div>
                    <div class="score-label">学历</div>
                </div>
                <div class="score-card">
                    <div class="score-value">{scores.get('salary_match_score', 0):.0f}</div>
                    <div class="score-label">薪资匹配</div>
                </div>
                <div class="score-card">
                    <div class="score-value">{evaluation.get('total_score', 0):.0f}</div>
                    <div class="score-label">综合等级</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <span class="badge badge-{'high' if evaluation.get('total_score', 0) >= 80 else 'medium'}">
                    {evaluation.get('grade', 'B')} 级候选人
                </span>
            </div>
        </div>

        <div class="card">
            <div class="card-title">优势与劣势</div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <div class="info-label">优势</div>
                    {self._render_list(evaluation.get('strengths', []), 'success')}
                </div>
                <div>
                    <div class="info-label">劣势</div>
                    {self._render_list(evaluation.get('weaknesses', []), 'warning')}
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-title">推荐岗位 TOP {len(matched_jobs)}</div>
            <div class="job-list">
                {self._render_jobs(matched_jobs)}
            </div>
        </div>

        {"".join([f'''
        <div class="card potential-section">
            <div class="card-title" style="border-color: white; color: white;">潜力分析</div>
            <div class="grid">
                <div>
                    <div class="info-label">家境评估</div>
                    <div class="info-value">{potential_analysis.get('family_background', {}).get('summary', '信息有限')}</div>
                    <div style="margin-top: 10px;">财务状况: <strong>{potential_analysis.get('family_background', {}).get('financial_indicator', '未知')}</strong></div>
                </div>
                <div>
                    <div class="info-label">职业潜力</div>
                    <div style="font-size: 28px; font-weight: 700;">{potential_analysis.get('career_potential', {}).get('level', '未知')}</div>
                    <div>评分: {potential_analysis.get('career_potential', {}).get('score', 0):.0f}/100</div>
                </div>
            </div>
            <div style="margin-top: 20px;">
                <div class="info-label">风险因素</div>
                {self._render_risks(potential_analysis.get('risk_factors', []))}
            </div>
            <div style="margin-top: 20px;">
                <div class="info-label">发展建议</div>
                {self._render_suggestions(potential_analysis.get('development_suggestions', []))}
            </div>
        </div>
        ''']) if self.config.include_potential else ""}

        <div class="footer">
            本报告由 {self.config.author} 自动生成 | 仅供参考，最终决策请结合实际情况
        </div>
    </div>
</body>
</html>"""
        return html

    def _render_skills(self, skills: List[str], tag_type: str) -> str:
        """渲染技能标签"""
        if not skills:
            return '<span class="tag tag-info">暂无</span>'
        color_map = {'success': 'tag-success', 'info': 'tag-info', 'warning': 'tag-warning'}
        return ''.join([f'<span class="tag {color_map.get(tag_type, "tag-info")}">{s}</span>' for s in skills])

    def _render_list(self, items: List[str], tag_type: str) -> str:
        """渲染列表"""
        if not items:
            return '<div class="info-value">暂无</div>'
        return ''.join([f'<div class="info-value">• {item}</div>' for item in items])

    def _render_jobs(self, jobs: List[Dict]) -> str:
        """渲染岗位列表"""
        if not jobs:
            return '<div class="info-value">暂无推荐</div>'

        rec_class_map = {'强烈推荐': 'rec-strong', '推荐': 'rec-good', '考虑': 'rec-consider'}
        html_parts = []
        for job in jobs:
            rec_class = rec_class_map.get(job.get('recommendation', ''), 'rec-consider')
            html_parts.append(f'''
            <div class="job-item">
                <div class="job-info">
                    <div class="job-title">{job.get('position', '')} @ {job.get('company', '')}</div>
                    <div class="job-company">{job.get('salary', '')} | {job.get('location', '')} | {job.get('platform', '')}</div>
                </div>
                <div class="job-score">{job.get('match_score', 0):.0f}%</div>
                <span class="recommendation {rec_class}">{job.get('recommendation', '')}</span>
            </div>
            ''')
        return ''.join(html_parts)

    def _render_risks(self, risks: List[str]) -> str:
        """渲染风险因素"""
        return ''.join([f'<div class="info-value" style="color: #fff3cd;">⚠️ {r}</div>' for r in risks])

    def _render_suggestions(self, suggestions: List[str]) -> str:
        """渲染建议"""
        return ''.join([f'<div class="info-value" style="color: #fff;">✓ {s}</div>' for s in suggestions])

    def _generate_id(self) -> str:
        """生成报告ID"""
        return datetime.now().strftime('%Y%m%d%H%M%S')

    def save_report(self, html: str, filepath: str):
        """保存报告到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)


class BatchReportGenerator:
    """批量报告生成器"""

    def __init__(self, config: ReportConfig = None):
        self.config = config or ReportConfig()
        self.generator = ReportGenerator(config)

    def generate_summary_report(
        self,
        results: Dict[str, Dict]
    ) -> str:
        """
        生成汇总报告

        Args:
            results: 批量匹配结果 {候选人: {profile, evaluation, potential, jobs}}

        Returns:
            HTML汇总报告
        """
        total = len(results)
        avg_score = sum(r.get('evaluation', {}).get('total_score', 0) for r in results.values()) / max(total, 1)
        strong_count = sum(1 for r in results.values() if r.get('evaluation', {}).get('total_score', 0) >= 80)

        rows = []
        for name, data in results.items():
            eval_data = data.get('evaluation', {})
            jobs = data.get('matched_jobs', [])[:3]  # 只显示前3
            score = eval_data.get('total_score', 0)
            grade = eval_data.get('grade', 'N/A')

            rows.append(f'''
            <tr>
                <td>{name}</td>
                <td><strong>{score:.0f}</strong></td>
                <td><span class="badge badge-{ 'high' if score >= 80 else 'medium'}">{grade}</span></td>
                <td>{', '.join([j.get('position', '') for j in jobs[:2]])}</td>
            </tr>
            ''')

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>批量评估汇总报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        th {{ background: #667eea; color: white; padding: 15px; text-align: left; }}
        td {{ padding: 15px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .stats {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ flex: 1; background: white; padding: 20px; border-radius: 8px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }}
        .stat-value {{ font-size: 32px; font-weight: 700; color: #667eea; }}
        .stat-label {{ color: #7f8c8d; font-size: 14px; margin-top: 5px; }}
        .badge-high {{ background: #d4edda; color: #155724; padding: 4px 12px; border-radius: 12px; font-size: 12px; }}
        .badge-medium {{ background: #fff3cd; color: #856404; padding: 4px 12px; border-radius: 12px; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>批量候选人评估汇总报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total}</div>
                <div class="stat-label">评估人数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{avg_score:.0f}</div>
                <div class="stat-label">平均得分</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{strong_count}</div>
                <div class="stat-label">优秀候选人</div>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>候选人</th>
                    <th>综合得分</th>
                    <th>等级</th>
                    <th>推荐岗位</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
</body>
</html>"""
        return html


# 异步入口函数
async def generate_report(
    candidate_profile: Dict,
    evaluation: Dict,
    potential_analysis: Dict,
    matched_jobs: List[Dict],
    output_path: str = None
) -> str:
    """
    生成评估报告

    Args:
        candidate_profile: 候选人画像
        evaluation: 评估结果
        potential_analysis: 潜力分析
        matched_jobs: 匹配岗位
        output_path: 输出路径（可选）

    Returns:
        HTML报告内容
    """
    generator = ReportGenerator()
    html = generator.generate_html_report(
        candidate_profile, evaluation, potential_analysis, matched_jobs
    )

    if output_path:
        generator.save_report(html, output_path)

    return html


async def generate_batch_summary(
    results: Dict[str, Dict],
    output_path: str = None
) -> str:
    """
    生成批量汇总报告

    Args:
        results: 批量结果
        output_path: 输出路径（可选）

    Returns:
        HTML报告内容
    """
    generator = BatchReportGenerator()
    html = generator.generate_summary_report(results)

    if output_path:
        generator.save_report(html, output_path)

    return html


# 主程序测试
if __name__ == "__main__":
    import asyncio

    async def test():
        # 模拟数据
        profile = {
            "name": "张三",
            "highest_degree": "硕士",
            "total_years": 5.0,
            "current_company": "阿里巴巴",
            "expected_salary": "40k-60k",
            "hard_skills": ["Python", "Java", "大数据", "机器学习", "架构设计"],
            "soft_skills": ["沟通能力", "团队协作"]
        }

        evaluation = {
            "total_score": 85.5,
            "grade": "A",
            "scores": {
                "competency_score": 88.0,
                "experience_score": 82.0,
                "education_score": 90.0,
                "salary_match_score": 85.0,
                "stability_score": 80.0
            },
            "strengths": ["学历优秀", "经验丰富", "技能突出"],
            "weaknesses": []
        }

        potential = {
            "family_background": {
                "summary": "具有海外学习背景，表明家庭经济条件较好",
                "financial_indicator": "良好"
            },
            "career_potential": {
                "level": "高",
                "score": 85.0
            },
            "risk_factors": ["薪资期望较高"],
            "development_suggestions": ["建议关注海外进修机会"]
        }

        jobs = [
            {"position": "Python高级工程师", "company": "字节跳动", "salary": "35k-55k", "match_score": 92, "recommendation": "强烈推荐", "location": "上海", "platform": "Boss直聘"},
            {"position": "架构师", "company": "美团", "salary": "40k-60k", "match_score": 88, "recommendation": "推荐", "location": "上海", "platform": "猎聘"}
        ]

        report = await generate_report(profile, evaluation, potential, jobs)
        print(f"报告已生成，共 {len(report)} 字符")

        # 保存测试
        with open("/tmp/test_report.html", "w", encoding="utf-8") as f:
            f.write(report)
        print("测试报告已保存到 /tmp/test_report.html")

    asyncio.run(test())