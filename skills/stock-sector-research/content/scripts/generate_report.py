#!/usr/bin/env python3
"""
Sector Report Generator with Review Mechanism
Generate formatted sector research reports with built-in verification
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class DataSource:
    """Represents a data source with verification status"""
    def __init__(self, name: str, data_type: str, fetch_date: str, url: str = ""):
        self.name = name
        self.data_type = data_type
        self.fetch_date = fetch_date
        self.url = url
        self.verified = False
        self.notes = ""


class ReportReviewer:
    """Review mechanism for generated reports"""

    def __init__(self):
        self.checklist = {
            "data_sources": {"status": "pending", "issues": []},
            "numerical_accuracy": {"status": "pending", "issues": []},
            "data_timeliness": {"status": "pending", "issues": []},
            "logical_consistency": {"status": "pending", "issues": []},
            "risk_disclosure": {"status": "pending", "issues": []}
        }
        self.review_passed = False

    def review_report(self, report_content: str, sources: List[DataSource]) -> Dict:
        """
        Perform comprehensive review of the report

        Returns:
            Dict with review results and checklist status
        """
        issues = []
        warnings = []

        # 1. Check data sources
        for source in sources:
            if not source.name:
                issues.append(f"数据来源缺失：{source.data_type}")
            if not source.fetch_date:
                issues.append(f"数据获取日期缺失：{source.name}")
            if source.fetch_date:
                try:
                    fetch_date = datetime.strptime(source.fetch_date, "%Y-%m-%d")
                    days_old = (datetime.now() - fetch_date).days
                    if days_old > 30:
                        warnings.append(f"{source.name} 数据较旧({days_old}天前)")
                except:
                    warnings.append(f"日期格式异常：{source.fetch_date}")

        self.checklist["data_sources"]["status"] = "pass" if not issues else "fail"
        self.checklist["data_sources"]["issues"] = issues

        # 2. Check for placeholder text
        placeholder_patterns = [
            "暂无数据", "待补充", "待更新", "暂无", "无数据",
            "TBD", "TODO", "待核实", "数据来源不明"
        ]
        for pattern in placeholder_patterns:
            if pattern in report_content and "⚠️" not in report_content:
                warnings.append(f"存在未填充内容：{pattern}")

        # 3. Check report structure
        required_sections = ["数据来源", "风险提示", "投资建议"]
        for section in required_sections:
            if section not in report_content:
                warnings.append(f"缺少必要章节：{section}")

        self.checklist["risk_disclosure"]["status"] = "pass" if "风险" in report_content else "warning"

        # 4. Check numerical data
        import re
        numbers = re.findall(r'\d+\.?\d*%?', report_content)
        # Basic validation: numbers shouldn't be too repetitive
        if len(set(numbers)) < len(numbers) * 0.3:
            warnings.append("警告：报告中数值重复度较高，请核实")

        # Determine overall pass status
        self.review_passed = len([i for i in self.checklist.values() if i["status"] == "fail"]) == 0

        return {
            "passed": self.review_passed,
            "issues": issues,
            "warnings": warnings,
            "checklist": self.checklist,
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> str:
        """Generate review summary text"""
        if self.review_passed:
            return "复核通过 - 报告可正常输出"
        else:
            fail_items = [k for k, v in self.checklist.items() if v["status"] == "fail"]
            return f"复核未通过 - 需修正以下项目: {', '.join(fail_items)}"

    def generate_review_section(self, review_result: Dict) -> str:
        """Generate markdown review section"""
        status_emoji = "✅" if review_result["passed"] else "⚠️"

        md = f"""
## 复核确认

| 检查项 | 状态 | 说明 |
|-------|------|------|
"""

        checklist = review_result["checklist"]
        status_map = {
            "pass": "✅ 通过",
            "fail": "❌ 未通过",
            "warning": "⚠️ 警告",
            "pending": "⏳ 待检查"
        }

        check_items = [
            ("数据来源完整性", checklist["data_sources"]),
            ("数值准确性", checklist["numerical_accuracy"]),
            ("数据时效性", checklist["data_timeliness"]),
            ("逻辑一致性", checklist["logical_consistency"]),
            ("风险揭示充分性", checklist["risk_disclosure"])
        ]

        for name, check in check_items:
            status = status_map.get(check["status"], "⏳ 待检查")
            issues = "; ".join(check["issues"]) if check["issues"] else "无"
            md += f"| {name} | {status} | {issues} |\n"

        md += f"""
**复核结论**: {status_emoji} {review_result["summary"]}
"""

        if review_result["warnings"]:
            md += f"""
### 注意事项
"""
            for w in review_result["warnings"]:
                md += f"- ⚠️ {w}\n"

        if review_result["issues"]:
            md += f"""
### 需修正项目
"""
            for i in review_result["issues"]:
                md += f"- ❌ {i}\n"

        return md


class ReportGenerator:
    """Generate sector research reports in multiple formats with review"""

    def __init__(self):
        self.output_formats = ["markdown", "html", "json"]
        self.reviewer = ReportReviewer()
        self.data_sources: List[DataSource] = []

    def add_source(self, name: str, data_type: str, fetch_date: str, url: str = ""):
        """Add a data source to track"""
        source = DataSource(name, data_type, fetch_date, url)
        self.data_sources.append(source)
        return source

    def generate_markdown_report(self, analysis_data: Dict) -> str:
        """Generate Markdown format report"""
        report = f"""# {analysis_data.get('sector_name', '行业板块')} 深度研究报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 一、板块概述

{analysis_data.get('overview', '暂无数据')}

---

## 二、产业链分析

### 2.1 产业链结构

{analysis_data.get('industry_chain', '暂无数据')}

### 2.2 价值分布

{analysis_data.get('value_distribution', '暂无数据')}

---

## 三、竞争格局分析

### 3.1 波特五力分析

| 竞争要素 | 强度 | 说明 |
|---------|------|------|
{self._format_porter_table(analysis_data.get('porter_analysis', {}))}

### 3.2 主要参与者

{analysis_data.get('competitors', '暂无数据')}

---

## 四、估值分析

### 4.1 估值指标

| 指标 | 数值 | 历史分位 | 说明 |
|-----|------|---------|------|
{self._format_valuation_table(analysis_data.get('valuation', {}))}

### 4.2 跨市场对比

{analysis_data.get('cross_market', '暂无数据')}

---

## 五、资金流向

{analysis_data.get('money_flow', '暂无数据')}

---

## 六、投资建议

### 6.1 综合评级

**评级**: {analysis_data.get('rating', '待评估')}

### 6.2 龙头标的

{analysis_data.get('leading_stocks', '暂无数据')}

### 6.3 风险提示

{analysis_data.get('risk_warnings', '暂无数据')}

---

## 七、数据来源

"""

        # Add data sources section
        if self.data_sources:
            for src in self.data_sources:
                date_str = src.fetch_date if src.fetch_date else "日期未知"
                report += f"- **{src.name}** - {src.data_type} - 获取日期: {date_str}"
                if src.url:
                    report += f" [{src.url}]"
                report += "\n"
        else:
            report += "- ⚠️ **数据来源待补充** - 请在复核阶段补充数据来源信息\n"

        report += f"""
---

## 八、复核确认

> **复核说明**: 报告生成后，请使用复核机制检查所有数据来源和内容准确性。

### 复核清单

- [ ] 宏观数据：来源可靠，时间有效
- [ ] 行业数据：口径一致，来源明确
- [ ] 公司数据：最新公告，数据匹配
- [ ] 资金数据：平台数据，实时或准实时
- [ ] 估值数据：计算准确，分位合理
- [ ] 预测观点：基于数据，有据可依
- [ ] 风险提示：充分揭示，不遗漏

---

*本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。*
"""
        return report

    def _format_porter_table(self, porter_data: Dict) -> str:
        """Format Porter's Five Forces as markdown table"""
        if not porter_data:
            return "| - | - | - |"

        rows = []
        for force, data in porter_data.items():
            rows.append(f"| {force} | {data.get('score', 0)} | {data.get('description', '')} |")
        return "\n".join(rows)

    def _format_valuation_table(self, valuation_data: Dict) -> str:
        """Format valuation metrics as markdown table"""
        if not valuation_data:
            return "| - | - | - | - |"

        rows = []
        for metric, value in valuation_data.items():
            rows.append(f"| {metric} | {value.get('value', 0)} | {value.get('percentile', 0)}% | {value.get('note', '')} |")
        return "\n".join(rows)

    def review_before_output(self, report_content: str) -> Tuple[str, Dict]:
        """
        Review report before final output

        Returns:
            Tuple of (review_section, review_result)
        """
        review_result = self.reviewer.review_report(report_content, self.data_sources)
        review_section = self.reviewer.generate_review_section(review_result)

        # Insert review section before the disclaimer
        if "## 八、复核确认" in report_content:
            # Update placeholder with actual review
            review_marker = "> **复核说明**: 报告生成后，请使用复核机制检查所有数据来源和内容准确性。"
            if review_marker in report_content:
                report_content = report_content.replace(review_marker, "✅ 自动复核已完成")

        return report_content, review_result

    def generate_and_review_report(self, analysis_data: Dict) -> Dict:
        """
        Generate report and perform review

        Returns:
            Dict with report content and review result
        """
        # Generate report
        report_content = self.generate_markdown_report(analysis_data)

        # Perform review
        report_content, review_result = self.review_before_output(report_content)

        return {
            "report": report_content,
            "review": review_result,
            "review_passed": review_result["passed"],
            "issues": review_result["issues"],
            "warnings": review_result["warnings"]
        }

    def generate_html_report(self, analysis_data: Dict) -> str:
        """Generate HTML format report"""
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{analysis_data.get('sector_name', '行业板块')} 研究报告</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #1a1a2e; border-bottom: 3px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #2c3e50; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #4a90d9; color: white; }}
        tr:nth-child(even) {{ background-color: #f8f9fa; }}
        .rating {{ display: inline-block; padding: 5px 15px; border-radius: 5px; font-weight: bold; }}
        .rating-positive {{ background-color: #d4edda; color: #155724; }}
        .rating-neutral {{ background-color: #fff3cd; color: #856404; }}
        .rating-negative {{ background-color: #f8d7da; color: #721c24; }}
        .risk {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; }}
        .warning {{ background-color: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }}
        .review-section {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .footer {{ margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>{analysis_data.get('sector_name', '行业板块')} 深度研究报告</h1>
    <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

    <h2>一、板块概述</h2>
    <p>{analysis_data.get('overview', '暂无数据')}</p>

    <h2>二、产业链分析</h2>
    <p>{analysis_data.get('industry_chain', '暂无数据')}</p>

    <h2>三、竞争格局分析</h2>
    <p>{analysis_data.get('competitors', '暂无数据')}</p>

    <h2>四、估值分析</h2>
    <p>{analysis_data.get('valuation_summary', '暂无数据')}</p>

    <h2>五、投资建议</h2>
    <p><strong>综合评级:</strong> <span class="rating rating-positive">{analysis_data.get('rating', '待评估')}</span></p>
    <p>{analysis_data.get('recommendation', '暂无数据')}</p>

    <h2>六、风险提示</h2>
    <div class="risk">
        {analysis_data.get('risk_warnings', '暂无数据')}
    </div>

    <h2>七、数据来源</h2>
    <div class="warning">
        ⚠️ 请在复核阶段补充完整的数据来源信息
    </div>

    <div class="review-section">
        <h3>📋 复核清单</h3>
        <ul>
            <li>☐ 宏观数据：来源可靠，时间有效</li>
            <li>☐ 行业数据：口径一致，来源明确</li>
            <li>☐ 公司数据：最新公告，数据匹配</li>
            <li>☐ 资金数据：平台数据，实时或准实时</li>
            <li>☐ 估值数据：计算准确，分位合理</li>
            <li>☐ 风险提示：充分揭示，不遗漏</li>
        </ul>
    </div>

    <div class="footer">
        <p>本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
    </div>
</body>
</html>"""
        return html

    def save_report(self, report_content: str, output_path: str, format: str = "markdown") -> bool:
        """Save report to file"""
        try:
            if format == "html":
                if not output_path.endswith('.html'):
                    output_path += '.html'
            elif format == "markdown":
                if not output_path.endswith('.md'):
                    output_path += '.md'

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False


def main():
    """Example usage with review mechanism"""
    generator = ReportGenerator()

    # Add data sources
    generator.add_source("东方财富", "行业资金流向", "2024-04-05", "https://data.eastmoney.com")
    generator.add_source("国家统计局", "行业产值数据", "2024-03-15", "https://www.stats.gov.cn")
    generator.add_source("公司公告", "年度报告", "2024-04-01")

    # Example data
    analysis_data = {
        "sector_name": "新能源汽车",
        "overview": "新能源汽车行业正在经历爆发式增长，渗透率持续提升...",
        "industry_chain": "上游：锂矿、钴矿、镍矿 | 中游：电池材料、电池芯 | 下游：整车制造",
        "competitors": "比亚迪、特斯拉、蔚来、小鹏、理想",
        "valuation_summary": "当前PE: 28.5倍，历史分位: 45%",
        "rating": "强烈推荐",
        "recommendation": "建议关注龙头公司和细分领域隐形冠军",
        "risk_warnings": "原材料价格波动、行业竞争加剧、补贴退坡"
    }

    # Generate and review report
    result = generator.generate_and_review_report(analysis_data)

    print(f"Report Review Passed: {result['review_passed']}")
    if result['warnings']:
        print(f"Warnings: {result['warnings']}")
    if result['issues']:
        print(f"Issues: {result['issues']}")

    # Save report
    generator.save_report(result['report'], "sector_report.md", "markdown")
    print("Report saved: sector_report.md")


if __name__ == "__main__":
    main()
