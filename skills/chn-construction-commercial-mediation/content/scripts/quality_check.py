#!/usr/bin/env python3
"""
严苛质量检查脚本 - 发布前必须通过
检查内容完整性、格式规范、专业术语一致性等
"""

import os
import re
import json
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent

class StrictQualityChecker:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.suggestions = []

    def run_strict_check(self):
        """执行严苛质量检查"""
        print("=" * 70)
        print("严苛质量检查 - 发布前审查")
        print("=" * 70)

        self.check_frontmatter_strict()
        self.check_content_completeness()
        self.check_terminology_consistency()
        self.check_citation_accuracy()
        self.check_cross_references()
        self.check_quality_standards()

        self.print_final_report()
        return len(self.errors) == 0

    def check_frontmatter_strict(self):
        """严苛检查frontmatter"""
        print("\n[1] Frontmatter 严苛检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            self.errors.append("Frontmatter格式错误")
            return

        fm = fm_match.group(1)

        # 检查name格式（必须小写+连字符）
        name_match = re.search(r'^name:\s*(.+)$', fm, re.MULTILINE)
        if name_match:
            name = name_match.group(1).strip()
            if re.match(r'^[a-z0-9\-]+$', name):
                self.passed.append(f"name格式正确: {name}")
            else:
                self.errors.append(f"name格式错误: {name} (应为小写+连字符)")
        else:
            self.errors.append("缺少name字段")

        # 检查description长度（应大于50字符）
        desc_match = re.search(r'^description:\s*(.+)$', fm, re.MULTILINE | re.DOTALL)
        if desc_match:
            desc = desc_match.group(1).strip()
            if len(desc) > 50:
                self.passed.append(f"description长度: {len(desc)}字符")
            else:
                self.errors.append(f"description过短: {len(desc)}字符 (应>50)")
        else:
            self.errors.append("缺少description字段")

        # 检查是否有触发场景描述
        if '触发' in fm or '适用' in fm or '场景' in fm:
            self.passed.append("包含触发场景描述")
        else:
            self.warnings.append("建议添加触发场景描述")

    def check_content_completeness(self):
        """检查内容完整性"""
        print("\n[2] 内容完整性检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        # 五大核心模块检查
        required_modules = [
            ("DEM", "争议证据图谱"),
            ("CMCR", "类案知识库"),
            ("MDEA", "多专业协同评估"),
            ("EIMP", "循证调解策略"),
            ("MOKMS", "效果评价")
        ]

        for abbr, name in required_modules:
            if abbr in content and name in content:
                self.passed.append(f"模块完整: {name} ({abbr})")
            elif abbr in content or name in content:
                self.warnings.append(f"模块部分存在: {abbr} 或 {name}")
            else:
                self.errors.append(f"缺少核心模块: {name}")

        # GRADE证据等级检查
        grade_levels = ["A级", "B级", "C级", "D级"]
        for level in grade_levels:
            if level in content:
                self.passed.append(f"证据等级: {level}")

        # 质量底线检查
        quality_lines = [
            "不可编造类案数据",
            "不可超出证据等级做结论",
            "失败分析"
        ]
        for line in quality_lines:
            if line in content:
                self.passed.append(f"包含质量要求: {line[:10]}...")

    def check_terminology_consistency(self):
        """检查术语一致性"""
        print("\n[3] 术语一致性检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查核心术语是否统一使用
        term_checks = {
            "调解": ["调解", "调解员", "调解协议"],
            "证据": ["证据", "证据等级", "证据链"],
            "类案": ["类案", "案例", "参照案例"],
            "商事调解": ["商事调解", "调解服务"]
        }

        for term_group, variations in term_checks.items():
            count = sum(content.count(v) for v in variations)
            if count > 5:
                self.passed.append(f"术语'{term_group}'使用充分: {count}处")

        # 检查英文缩写与中文对应
        abbr_checks = [
            ("DEM", "争议证据图谱"),
            ("CMCR", "类案知识库"),
            ("MDEA", "多专业协同"),
            ("EIMP", "循证调解策略"),
            ("MOKMS", "效果评价"),
            ("GRADE", "证据分级")
        ]

        for abbr, cn in abbr_checks:
            if abbr in content and cn in content:
                self.passed.append(f"缩写对照: {abbr}={cn}")
            elif abbr in content:
                self.warnings.append(f"缩写{abbr}缺少中文对照")

    def check_citation_accuracy(self):
        """检查引用准确性"""
        print("\n[4] 法律引用准确性检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查法律引用格式
        law_citations = [
            ("民法典第807条", "建设工程优先受偿权"),
            ("司法解释", "建设工程施工合同"),
            ("商事调解条例", "自愿原则")
        ]

        for law, topic in law_citations:
            if law in content:
                self.passed.append(f"法律引用: {law}")

        # 检查章节编号格式
        if re.search(r'#{1,3}\s+[一二三四五六七八九十]、|第[一二三四五六七八九十]条', content):
            self.warnings.append("存在中文编号格式，建议使用阿拉伯数字")

    def check_cross_references(self):
        """检查交叉引用"""
        print("\n[5] 交叉引用检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查references引用
        ref_patterns = [
            (r'references/mediator-guide', "调解员指南引用"),
            (r'references/agent-guide', "代理人指南引用"),
            (r'references/applicant-guide', "申请人指南引用"),
            (r'references/case-search-guide', "类案检索指南引用"),
            (r'references/legal-reference', "法律参考引用")
        ]

        for pattern, desc in ref_patterns:
            if re.search(pattern, content):
                self.passed.append(f"引用: {desc}")
            else:
                self.warnings.append(f"建议引用: {desc}")

        # 检查references文件是否存在
        ref_files = [
            "legal-reference.md",
            "case-search-guide.md",
            "mediator-guide.md",
            "agent-guide.md",
            "applicant-guide.md"
        ]

        for rf in ref_files:
            path = SKILL_ROOT / "references" / rf
            if path.exists():
                self.passed.append(f"文件存在: {rf}")
            else:
                self.errors.append(f"文件缺失: {rf}")

    def check_quality_standards(self):
        """检查质量标准"""
        print("\n[6] 质量标准检查...")

        with open(SKILL_ROOT / "SKILL.md", 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查度量标准
        metrics = [
            ("调解成功率", r'\d+%|≥\d+%'),
            ("协议履行率", r'\d+%|≥\d+%'),
            ("调解周期", r'\d+日|≤\d+日')
        ]

        for name, pattern in metrics:
            if re.search(pattern, content):
                self.passed.append(f"度量标准: {name}")

        # 检查CPD相关内容
        if 'CPD' in content or '持续专业发展' in content:
            self.passed.append("包含CPD持续专业发展内容")

        # 检查失败分析制度
        if 'M&M' in content or '发病率与死亡率' in content:
            self.passed.append("借鉴M&M讨论会制度")

    def print_final_report(self):
        """打印最终报告"""
        print("\n" + "=" * 70)
        print("质量检查最终报告")
        print("=" * 70)

        # 错误统计
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        passed_count = len(self.passed)

        print(f"\n✅ 通过: {passed_count} 项")
        print(f"⚠️ 警告: {warning_count} 项")
        print(f"❌ 错误: {error_count} 项")

        if error_count > 0:
            print("\n" + "-" * 70)
            print("❌ 必须修复的错误:")
            print("-" * 70)
            for i, err in enumerate(self.errors, 1):
                print(f"  {i}. {err}")

        if warning_count > 0:
            print("\n" + "-" * 70)
            print("⚠️ 建议改进项:")
            print("-" * 70)
            for i, warn in enumerate(self.warnings, 1):
                print(f"  {i}. {warn}")

        # 发布可行性判定
        print("\n" + "=" * 70)
        if error_count == 0:
            print("✅ 质量检查通过 - 可以发布")
            print("=" * 70)
        elif error_count <= 2:
            print("⚠️ 有少量错误 - 修复后可发布")
            print("=" * 70)
        else:
            print("❌ 错误过多 - 需要修复后重新检查")
            print("=" * 70)

if __name__ == "__main__":
    checker = StrictQualityChecker()
    success = checker.run_strict_check()
    exit(0 if success else 1)
