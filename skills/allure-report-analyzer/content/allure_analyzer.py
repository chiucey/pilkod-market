#!/usr/bin/env python3
"""
Allure 测试报告分析器 - 核心解析模块

功能：
- 解析 Allure JSON 报告格式
- 提取测试执行统计数据
- 分析失败原因并分类
- 生成分析报告（文本/JSON）
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class TestStatus(Enum):
    """测试状态枚举"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BROKEN = "broken"


@dataclass
class TestCase:
    """测试用例数据模型"""
    name: str
    status: str
    time: float  # 毫秒
    story: Optional[str] = None
    feature: Optional[str] = None
    severity: Optional[str] = None
    message: Optional[str] = None
    trace: Optional[str] = None
    links: List[Dict] = None

    def __post_init__(self):
        if self.links is None:
            self.links = []


@dataclass
class CategoryInfo:
    """失败分类信息"""
    name: str
    test_count: int
    description: Optional[str] = None


@dataclass
class AnalysisResult:
    """分析结果数据模型"""
    generated_at: str
    report_path: str
    summary: Dict[str, Any]
    failures: Dict[str, Any]
    slowest_tests: List[Dict]
    recommendations: List[str]

    def to_dict(self) -> Dict:
        return asdict(self)


class AllureReportAnalyzer:
    """Allure 报告分析器主类"""

    def __init__(self, report_path: str):
        """
        初始化分析器

        Args:
            report_path: Allure 报告目录路径
        """
        self.report_path = Path(report_path)
        self.data_path = self.report_path / "data"
        self._validate_report_path()

    def _validate_report_path(self):
        """验证报告路径有效性"""
        if not self.report_path.exists():
            raise FileNotFoundError(f"报告路径不存在: {self.report_path}")

        if not self.data_path.exists():
            raise FileNotFoundError(f"报告数据目录不存在: {self.data_path}")

    def _load_json(self, filename: str) -> Any:
        """加载 JSON 文件"""
        file_path = self.data_path / filename
        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def parse_summary(self) -> Dict[str, Any]:
        """解析执行摘要"""
        summary_data = self._load_json("summary.json")

        if summary_data:
            return {
                "total": summary_data.get("statistic", {}).get("total", 0),
                "passed": summary_data.get("statistic", {}).get("passed", 0),
                "failed": summary_data.get("statistic", {}).get("failed", 0),
                "skipped": summary_data.get("statistic", {}).get("skipped", 0),
                "broken": summary_data.get("statistic", {}).get("broken", 0),
                "unknown": summary_data.get("statistic", {}).get("unknown", 0),
            }

        # 如果没有 summary.json，从 test-cases.json 计算
        test_cases = self._load_json("test-cases.json") or []
        return self._calculate_summary_from_cases(test_cases)

    def _calculate_summary_from_cases(self, test_cases: List[Dict]) -> Dict[str, Any]:
        """从测试用例计算摘要"""
        summary = {
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "broken": 0,
            "unknown": 0
        }

        for case in test_cases:
            status = case.get("status", "unknown")
            if status in summary:
                summary[status] += 1

        return summary

    def parse_test_cases(self) -> List[TestCase]:
        """解析测试用例列表"""
        cases_data = self._load_json("test-cases.json") or []

        test_cases = []
        for case_data in cases_data:
            case = TestCase(
                name=case_data.get("name", "Unknown"),
                status=case_data.get("status", "unknown"),
                time=case_data.get("time", {}).get("duration", 0),
                story=case_data.get("story"),
                feature=case_data.get("feature"),
                severity=case_data.get("severity"),
                message=case_data.get("message"),
                trace=case_data.get("trace"),
                links=case_data.get("links", [])
            )
            test_cases.append(case)

        return test_cases

    def parse_categories(self) -> List[CategoryInfo]:
        """解析失败分类"""
        categories_data = self._load_json("categories.json") or []

        categories = []
        for cat in categories_data:
            category = CategoryInfo(
                name=cat.get("name", "Unknown"),
                test_count=cat.get("testCount", 0),
                description=cat.get("description")
            )
            categories.append(category)

        return categories

    def analyze_failures(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """分析失败测试"""
        failed_tests = [tc for tc in test_cases if tc.status in ["failed", "broken"]]

        failure_analysis = {
            "total_failures": len(failed_tests),
            "by_type": {
                "assertion": 0,
                "exception": 0,
                "timeout": 0,
                "assumption": 0,
                "other": 0
            },
            "details": []
        }

        for test in failed_tests:
            failure_type = self._classify_failure(test)
            failure_analysis["by_type"][failure_type] += 1

            failure_analysis["details"].append({
                "name": test.name,
                "status": test.status,
                "type": failure_type,
                "message": test.message,
                "trace": test.trace,
                "feature": test.feature,
                "story": test.story
            })

        return failure_analysis

    def _classify_failure(self, test: TestCase) -> str:
        """分类失败类型"""
        message = (test.message or "").lower()
        trace = (test.trace or "").lower()
        combined = message + " " + trace

        if any(x in combined for x in ["assert", "expected", "assertion"]):
            return "assertion"
        elif any(x in combined for x in ["timeout", "timed out", "connection"]):
            return "timeout"
        elif any(x in combined for x in ["assumption", "precondition"]):
            return "assumption"
        elif any(x in combined for x in ["exception", "error", "null", "none", "index"]):
            return "exception"
        else:
            return "other"

    def find_slowest_tests(self, test_cases: List[TestCase], limit: int = 10) -> List[Dict]:
        """查找最慢的测试"""
        sorted_cases = sorted(test_cases, key=lambda x: x.time, reverse=True)

        return [
            {
                "name": tc.name,
                "time_ms": tc.time,
                "time_formatted": self._format_duration(tc.time),
                "feature": tc.feature
            }
            for tc in sorted_cases[:limit]
        ]

    def _format_duration(self, ms: float) -> str:
        """格式化时长"""
        seconds = ms / 1000
        if seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            secs = seconds % 60
            return f"{minutes}m {secs:.2f}s"

    def generate_recommendations(self, summary: Dict, failures: Dict) -> List[str]:
        """生成改进建议"""
        recommendations = []

        total = summary.get("total", 0)
        failed = summary.get("failed", 0)
        broken = summary.get("broken", 0)
        pass_rate = ((total - failed - broken) / total * 100) if total > 0 else 0

        # 基于通过率的建议
        if pass_rate < 80:
            recommendations.append("⚠️ 测试通过率偏低，建议优先关注核心功能测试")

        # 基于失败类型的建议
        failure_types = failures.get("by_type", {})

        if failure_types.get("timeout", 0) > 0:
            recommendations.append("🔧 检测到超时失败，建议增加超时重试机制或优化被测系统性能")

        if failure_types.get("assertion", 0) > 0:
            recommendations.append("✅ 存在断言失败，请检查预期值与实际值的差异")

        if failure_types.get("exception", 0) > 0:
            recommendations.append("🐛 检测到异常错误，建议检查日志定位具体问题")

        if failure_types.get("assumption", 0) > 0:
            recommendations.append("📋 存在前置条件失败的测试，请检查测试环境配置")

        if not recommendations:
            recommendations.append("🎉 测试执行情况良好，继续保持！")

        return recommendations

    def analyze(self) -> AnalysisResult:
        """执行完整分析"""
        print(f"📂 正在分析报告: {self.report_path}")

        # 解析数据
        summary = self.parse_summary()
        test_cases = self.parse_test_cases()
        categories = self.parse_categories()

        # 分析失败
        failures = self.analyze_failures(test_cases)

        # 查找慢测试
        slowest = self.find_slowest_tests(test_cases)

        # 生成建议
        recommendations = self.generate_recommendations(summary, failures)

        return AnalysisResult(
            generated_at=datetime.now().isoformat(),
            report_path=str(self.report_path),
            summary={
                **summary,
                "pass_rate": round((summary.get("passed", 0) / summary.get("total", 1)) * 100, 2)
            },
            failures=failures,
            slowest_tests=slowest,
            recommendations=recommendations
        )

    def print_report(self, result: AnalysisResult, verbose: bool = False):
        """打印报告到终端"""
        print("\n" + "=" * 50)
        print("     Allure 测试报告分析结果")
        print("=" * 50)

        # 执行摘要
        print("\n📊 执行摘要")
        print(f"   总测试数: {result.summary['total']}")
        print(f"   通过: {result.summary['passed']} ({result.summary.get('pass_rate', 0)}%)")
        print(f"   失败: {result.summary['failed']}")
        print(f"   跳过: {result.summary['skipped']}")
        print(f"   损坏: {result.summary['broken']}")

        # 执行时间
        if result.slowest_tests:
            total_time = sum(t["time_ms"] for t in result.slowest_tests[:5])
            avg_time = total_time / min(len(result.slowest_tests), 5)
            print(f"\n⏱️ 执行时间")
            print(f"   平均: {self._format_duration(avg_time)}/测试")
            if result.slowest_tests:
                print(f"   最慢: {result.slowest_tests[0]['name']} ({result.slowest_tests[0]['time_formatted']})")

        # 失败详情
        if result.failures["total_failures"] > 0:
            print(f"\n❌ 失败测试 ({result.failures['total_failures']})")

            by_type = result.failures["by_type"]
            type_names = {
                "assertion": "断言失败",
                "exception": "异常错误",
                "timeout": "超时",
                "assumption": "前置条件失败",
                "other": "其他"
            }

            for ftype, count in by_type.items():
                if count > 0:
                    print(f"   {type_names.get(ftype, ftype)}: {count}")

            if verbose:
                print("\n   失败详情:")
                for i, detail in enumerate(result.failures["details"][:5], 1):
                    print(f"   {i}. {detail['name']} [{detail['type']}]")
                    if detail.get("message"):
                        print(f"      原因: {detail['message'][:80]}...")

        # 建议
        print("\n💡 建议改进")
        for rec in result.recommendations:
            print(f"   {rec}")

        print("\n" + "=" * 50)
        print(f"分析完成时间: {result.generated_at}")
        print("=" * 50 + "\n")

    def save_json_report(self, result: AnalysisResult, output_path: str):
        """保存 JSON 格式报告"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"✅ JSON 报告已保存: {output_file}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Allure 测试报告分析器")
    parser.add_argument("--path", "-p", default="./allure-report", help="报告路径")
    parser.add_argument("--output", "-o", help="JSON 输出路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")

    args = parser.parse_args()

    try:
        analyzer = AllureReportAnalyzer(args.path)
        result = analyzer.analyze()
        analyzer.print_report(result, verbose=args.verbose)

        if args.output:
            analyzer.save_json_report(result, args.output)

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
