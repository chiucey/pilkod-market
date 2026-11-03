#!/usr/bin/env python3
"""
复合SKILL生成器
基于高频模式自动生成复合Skill配置
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class SkillGenerator:
    """复合SKILL生成器"""

    # 预定义的组件映射
    SKILL_CATEGORIES = {
        "search": ["brave-search", "autoresearch", "deep-research", "in-depth-research"],
        "analyze": ["pattern-detection", "research-engine", "analyst"],
        "create": ["content-creation", "writing", "business-writing"],
        "code": ["code", "code-generator", "python"],
        "review": ["code-review", "ai-code-review", "security-auditor"],
        "test": ["backend-testing", "debugging"],
        "deploy": ["vercel-deploy", "github"],
        "store": ["cognitive-memory", "obsidian", "notion"],
        "notify": ["feishu-multi-agent-messaging", "slack", "discord"]
    }

    def __init__(self, patterns_file: Optional[str] = None):
        self.patterns_file = patterns_file
        self.patterns = []
        self.composite_skills = []

    def load_patterns(self, patterns: List[Dict]):
        """加载分析结果"""
        self.patterns = patterns

    def identify_composable_patterns(self) -> List[Dict]:
        """识别可组合的模式"""
        composable = []

        for pattern in self.patterns:
            pattern_str = pattern.get('pattern', '')
            frequency = pattern.get('frequency', 0)

            # 检查是否包含多个技能
            skills = pattern_str.split(' → ')
            if len(skills) >= 2 and frequency >= 3:
                composable.append({
                    'pattern': pattern_str,
                    'skills': skills,
                    'frequency': frequency,
                    'can_compose': True
                })

        return composable

    def generate_composite_skill(self, pattern_data: Dict) -> Dict:
        """生成复合Skill配置"""
        skills = pattern_data['skills']
        frequency = pattern_data['frequency']

        # 确定复合Skill类型
        skill_type = self._classify_composition(skills)

        composite = {
            "name": self._generate_name(skills),
            "version": "1.0.0",
            "description": self._generate_description(skills, skill_type),
            "components": [],
            "execution_flow": [],
            "evolution_enabled": True,
            "frequency": frequency,
            "efficiency_gain": f"+{min(80, frequency * 10)}%"
        }

        # 生成组件
        for i, skill in enumerate(skills):
            layer = self._assign_layer(i, len(skills))
            composite["components"].append({
                "skill": skill,
                "layer": layer,
                "weight": 1.0 - (i * 0.1)  # 早期组件权重更高
            })

            composite["execution_flow"].append({
                "step": i + 1,
                "action": layer,
                "skill": skill
            })

        return composite

    def _classify_composition(self, skills: List[str]) -> str:
        """分类组合类型"""
        skills_lower = [s.lower() for s in skills]

        if any(s in ['brave-search', 'autoresearch', 'deep-research'] for s in skills_lower):
            if any(s in ['writing', 'business-writing', 'content-creation'] for s in skills_lower):
                return "research-report"
            return "intelligence"
        elif any(s in ['code', 'code-generator', 'python'] for s in skills_lower):
            if any(s in ['code-review', 'ai-code-review'] for s in skills_lower):
                return "code-factory"
            return "code-generation"
        elif any(s in ['analyst', 'data-analyst', 'chart-image'] for s in skills_lower):
            return "data-analysis"
        elif any(s in ['content-creation', 'marketing-drafter'] for s in skills_lower):
            return "content-production"
        else:
            return "generic"

    def _generate_name(self, skills: List[str]) -> str:
        """生成复合Skill名称"""
        skill_type = self._classify_composition(skills)

        name_mapping = {
            "research-report": "auto-research-report",
            "intelligence": "smart-intelligence",
            "code-factory": "code-factory",
            "code-generation": "code-assistant",
            "data-analysis": "data-pipeline",
            "content-production": "content-engine",
            "generic": "workflow-automation"
        }

        return name_mapping.get(skill_type, f"composed-{skill_type}")

    def _generate_description(self, skills: List[str], skill_type: str) -> str:
        """生成描述"""
        chains = " → ".join(skills)
        return f"复合Skill: {chains}。自动化执行多步骤任务，提升效率。"

    def _assign_layer(self, index: int, total: int) -> str:
        """分配层次"""
        ratio = index / max(1, total - 1)

        if ratio == 0:
            return "trigger"
        elif ratio <= 0.25:
            return "search"
        elif ratio <= 0.5:
            return "analysis"
        elif ratio <= 0.75:
            return "processing"
        else:
            return "output"

    def generate_all(self) -> List[Dict]:
        """生成所有复合Skill"""
        composable = self.identify_composable_patterns()
        self.composite_skills = []

        for pattern_data in composable:
            composite = self.generate_composite_skill(pattern_data)
            self.composite_skills.append(composite)

        # 按频率排序
        self.composite_skills.sort(key=lambda x: x['frequency'], reverse=True)

        return self.composite_skills

    def save_composites(self, output_dir: str) -> List[str]:
        """保存生成的复合Skill"""
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []

        for composite in self.composite_skills:
            name = composite['name']
            filepath = os.path.join(output_dir, f"{name}.json")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(composite, f, ensure_ascii=False, indent=2)

            saved_files.append(filepath)

        return saved_files


def main():
    """主函数"""
    print("🛠️ 复合SKILL生成器")
    print("=" * 50)

    # 尝试加载分析报告
    report_path = "/workspace/temp-skills/skill-evolution-system/analysis_report.json"

    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
            patterns = report.get('top_20_patterns', [])
    else:
        print("⚠️ 未找到分析报告，使用示例数据")
        patterns = [
            {"pattern": "brave-search → summarize → cognitive-memory", "frequency": 45},
            {"pattern": "deep-research → writing → obsidian", "frequency": 38},
            {"pattern": "code → code-review → backend-testing", "frequency": 35},
        ]

    generator = SkillGenerator()
    generator.load_patterns(patterns)

    print(f"\n📊 分析了 {len(patterns)} 个高频模式")

    composites = generator.generate_all()

    print(f"\n🎯 生成了 {len(composites)} 个复合Skill")

    print("\n" + "=" * 50)
    print("📋 生成的复合Skill列表")
    print("=" * 50)

    for i, comp in enumerate(composites, 1):
        print(f"\n{i}. {comp['name']} (v{comp['version']})")
        print(f"   ⭐ 效率提升: {comp['efficiency_gain']}")
        print(f"   📝 组件数: {len(comp['components'])}")
        print(f"   🔗 {comp['description']}")

    # 保存
    output_dir = "/workspace/temp-skills/skill-evolution-system/generated-composites"
    saved_files = generator.save_composites(output_dir)

    print(f"\n✅ 已保存到: {output_dir}")

    return composites


if __name__ == "__main__":
    main()
