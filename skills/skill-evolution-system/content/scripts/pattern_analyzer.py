#!/usr/bin/env python3
"""
SKILL使用模式分析器
分析对话历史中的SKILL调用模式，识别高频操作组合
"""

import json
import os
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple


class PatternAnalyzer:
    """SKILL使用模式分析器"""

    def __init__(self, logs_dir: str = "/workspace/.minimax/conversation_logs"):
        self.logs_dir = Path(logs_dir)
        self.patterns = defaultdict(int)
        self.skill_sequences = []
        self.skill_frequency = Counter()

    def scan_logs(self) -> List[str]:
        """扫描所有对话日志文件"""
        log_files = []
        if self.logs_dir.exists():
            log_files = list(self.logs_dir.glob("*.json")) + list(self.logs_dir.glob("*.log"))
        return log_files

    def extract_skill_calls(self, content: str) -> List[str]:
        """从内容中提取SKILL调用"""
        # 匹配 Skill(...) 模式
        skill_pattern = r'Skill\s*\(\s*["\']?([^"\')]+)["\']?\s*\)'
        skills = re.findall(skill_pattern, content, re.IGNORECASE)
        return skills

    def extract_skill_chains(self, content: str) -> List[List[str]]:
        """提取SKILL调用链"""
        skills = self.extract_skill_calls(content)
        # 如果多个SKILL在短时间/上下文中连续调用，视为一个链
        chains = []
        current_chain = []

        for skill in skills:
            current_chain.append(skill)
            # 简单策略：每5个skill作为一个链
            if len(current_chain) >= 3:
                chains.append(current_chain.copy())
                current_chain = current_chain[2:]  # 保留最后2个作为下一个链的开始

        if len(current_chain) >= 2:
            chains.append(current_chain)

        return chains

    def analyze_patterns(self) -> Dict:
        """分析使用模式"""
        log_files = self.scan_logs()

        all_chains = []

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    chains = self.extract_skill_chains(content)
                    all_chains.extend(chains)

                    # 统计单技能频率
                    skills = self.extract_skill_calls(content)
                    self.skill_frequency.update(skills)
            except Exception as e:
                print(f"Error reading {log_file}: {e}")

        # 分析高频组合
        for chain in all_chains:
            chain_key = " → ".join(chain)
            self.patterns[chain_key] += 1

        return self.get_top_patterns(n=20)

    def get_top_patterns(self, n: int = 20) -> List[Tuple[str, int]]:
        """获取Top N高频模式"""
        return self.patterns.most_common(n)

    def get_skill_frequency(self) -> List[Tuple[str, int]]:
        """获取技能使用频率"""
        return self.skill_frequency.most_common(50)

    def generate_report(self) -> Dict:
        """生成分析报告"""
        top_patterns = self.get_top_patterns(20)
        top_skills = self.get_skill_frequency()

        return {
            "total_patterns_found": len(self.patterns),
            "total_skills_found": len(self.skill_frequency),
            "top_20_patterns": [
                {"pattern": p, "frequency": f, "weight": "⭐" * min(5, f // 3 + 1)}
                for p, f in top_patterns
            ],
            "top_50_skills": [
                {"skill": s, "frequency": f}
                for s, f in top_skills
            ]
        }


def main():
    """主函数"""
    print("🔍 SKILL使用模式分析器")
    print("=" * 50)

    analyzer = PatternAnalyzer()

    print("\n📊 正在分析对话历史...")
    report = analyzer.analyze_patterns()

    print(f"\n发现 {report['total_patterns_found']} 个操作模式")
    print(f"发现 {report['total_skills_found']} 个不同SKILL")

    print("\n" + "=" * 50)
    print("🏆 Top 20 高频操作模式")
    print("=" * 50)

    for i, item in enumerate(report['top_20_patterns'], 1):
        print(f"\n{i}. {item['weight']} ({item['frequency']}次)")
        print(f"   {item['pattern']}")

    print("\n" + "=" * 50)
    print("📦 Top 50 高频SKILL")
    print("=" * 50)

    for i, item in enumerate(report['top_50_skills'][:50], 1):
        print(f"{i:2}. {item['skill']:<40} (使用{item['frequency']}次)")

    # 保存报告
    report_path = "/workspace/temp-skills/skill-evolution-system/analysis_report.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 分析报告已保存到: {report_path}")

    return report


if __name__ == "__main__":
    main()
