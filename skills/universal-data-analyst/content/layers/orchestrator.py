#!/usr/bin/env python3
"""
Data Analysis Orchestrator - 数据分析流程编排器

管理完整的数据分析流程：
1. 数据加载
2. 本体识别
3. 质量校验
4. 方案规划
5. 脚本生成
6. 执行分析
7. 综合报告
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

import pandas as pd
import numpy as np

from .data_loader import DataLoader, DataFormat
from .data_validator import DataValidator, ValidationReport


class FlowHealthMonitor:
    """流程健康状态监控器"""

    def __init__(self):
        self.steps = {
            'load': {'status': 'pending', 'importance': 'critical'},
            'ontology': {'status': 'pending', 'importance': 'optional'},
            'validation': {'status': 'pending', 'importance': 'optional'},
            'planning': {'status': 'pending', 'importance': 'critical'},
            'script': {'status': 'pending', 'importance': 'critical'},
            'execution': {'status': 'pending', 'importance': 'critical'},
            'report': {'status': 'pending', 'importance': 'critical'},
        }
        self.current_step = None
        self.step_results = {}

    def can_proceed(self, step_name: str) -> bool:
        """检查是否可以执行某步骤"""
        if step_name not in self.steps:
            return True

        step = self.steps[step_name]
        if step['status'] in ['success', 'pending']:
            return True

        # 检查前置依赖
        dependencies = {
            'ontology': ['load'],
            'validation': ['load'],
            'planning': ['load'],
            'script': ['load', 'planning'],
            'execution': ['load', 'script'],
            'report': ['load'],
        }

        deps = dependencies.get(step_name, [])
        for dep in deps:
            if self.steps.get(dep, {}).get('status') == 'failed':
                return False

        return True

    def record_step_start(self, step_name: str) -> bool:
        """记录步骤开始"""
        if not self.can_proceed(step_name):
            return False
        self.steps[step_name]['status'] = 'running'
        self.current_step = step_name
        return True

    def record_step_success(self, step_name: str, message: str = "", details: Dict = None):
        """记录步骤成功"""
        self.steps[step_name]['status'] = 'success'
        self.step_results[step_name] = {
            'status': 'success',
            'message': message,
            'details': details or {}
        }

    def record_step_failure(self, step_name: str, error: str, suggestions: List[str] = None):
        """记录步骤失败"""
        self.steps[step_name]['status'] = 'failed'
        self.step_results[step_name] = {
            'status': 'failed',
            'error': error,
            'suggestions': suggestions or []
        }

    def get_health_score(self) -> float:
        """计算健康评分"""
        total = len(self.steps)
        success = sum(1 for s in self.steps.values() if s['status'] == 'success')

        critical_steps = ['load', 'planning', 'execution']
        critical_success = sum(1 for s in critical_steps if self.steps.get(s, {}).get('status') == 'success')

        # 关键步骤权重更高
        score = (success / total) * 50 + (critical_success / len(critical_steps)) * 50
        return score

    def is_flow_interrupted(self) -> bool:
        """检查流程是否被中断"""
        critical = ['load', 'execution']
        return any(self.steps.get(s, {}).get('status') == 'failed' for s in critical)


class DataAnalysisOrchestrator:
    """数据分析流程编排器"""

    def __init__(self, output_dir: str = "./analysis_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # 初始化组件
        self.loader = DataLoader()
        self.validator = DataValidator()
        self.health_monitor = FlowHealthMonitor()

        # 会话状态
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.output_dir / f"session_{self.session_id}"
        self.session_dir.mkdir(exist_ok=True)

        # 数据缓存
        self.df: Optional[pd.DataFrame] = None
        self.validation_report: Optional[ValidationReport] = None
        self.data_profile: Optional[Dict] = None

    def load_data(self, file_path: str, **kwargs) -> bool:
        """
        步骤1: 加载数据

        Args:
            file_path: 数据文件路径
            **kwargs: 额外参数

        Returns:
            bool: 是否成功
        """
        print("\n" + "=" * 60)
        print("【步骤1/7】数据加载")
        print("=" * 60)

        if not self.health_monitor.record_step_start('load'):
            print("⛔ 步骤被阻塞")
            return False

        result = self.loader.execute({'file_path': file_path, **kwargs})

        if result.success:
            self.df = result.data
            msg = f"✅ 加载成功: {result.rows:,} 行 × {result.columns} 列"
            print(msg)

            if result.warnings:
                print(f"\n⚠️ 警告:")
                for w in result.warnings:
                    print(f"   - {w}")

            self.health_monitor.record_step_success(
                'load',
                message=msg,
                details={
                    'rows': result.rows,
                    'columns': result.columns,
                    'encoding': result.encoding
                }
            )

            # 保存数据信息
            self._save_json("step1_data_info.json", {
                'file_path': file_path,
                'file_name': Path(file_path).name,
                'rows': result.rows,
                'columns': result.columns,
                'encoding': result.encoding,
                'report_title': f"{Path(file_path).stem} 数据分析报告"
            })

            return True
        else:
            msg = f"❌ 加载失败: {result.errors}"
            print(msg)

            suggestions = [
                "检查文件编码（尝试 gbk、utf-8）",
                "确认文件格式是否为支持的格式",
                "检查文件路径是否正确"
            ]

            self.health_monitor.record_step_failure(
                'load',
                error=result.errors[0] if result.errors else "Unknown error",
                suggestions=suggestions
            )
            return False

    def validate_data(self) -> Optional[ValidationReport]:
        """
        步骤2: 数据质量校验

        Returns:
            ValidationReport 或 None
        """
        print("\n" + "=" * 60)
        print("【步骤2/7】数据质量校验")
        print("=" * 60)

        if not self.health_monitor.record_step_start('validation'):
            print("⛔ 步骤被阻塞")
            return None

        if self.df is None:
            print("❌ 请先加载数据")
            self.health_monitor.record_step_failure('validation', error="数据未加载")
            return None

        try:
            report = self.validator.execute(self.df)
            self.validation_report = report

            print(f"\n📊 质量评分: {report.overall_score:.1f}/100")

            if report.issues:
                critical = sum(1 for i in report.issues if i.severity.value == 'critical')
                warning = sum(1 for i in report.issues if i.severity.value == 'warning')
                print(f"📋 发现问题: {len(report.issues)} 个 (Critical: {critical}, Warning: {warning})")

                if critical > 0:
                    print("\n⚠️ 发现严重数据质量问题，建议处理后再分析")
            else:
                print("✅ 未发现明显的数据质量问题")

            # 保存报告
            self._save_json("step2_validation_report.json", report.to_dict())

            # 生成清洗建议
            cleaning_report = report.generate_cleaning_report()
            (self.session_dir / "step2_cleaning_report.txt").write_text(cleaning_report, encoding='utf-8')

            self.health_monitor.record_step_success(
                'validation',
                message=f"质量评分 {report.overall_score:.1f}/100",
                details={'issues_count': len(report.issues)}
            )

            return report

        except Exception as e:
            print(f"❌ 校验失败: {e}")
            self.health_monitor.record_step_failure('validation', error=str(e))
            return None

    def generate_ontology_prompt(self) -> str:
        """
        步骤3: 生成数据本体识别提示词

        Returns:
            str: 提示词文本
        """
        print("\n" + "=" * 60)
        print("【步骤3/7】数据本体识别")
        print("=" * 60)

        if self.df is None:
            print("❌ 请先加载数据")
            return ""

        # 生成数据画像
        self.data_profile = self._generate_data_profile(self.df)

        # 生成提示词
        prompt = self._build_ontology_prompt()

        # 保存提示词
        (self.session_dir / "step3_ontology_prompt.txt").write_text(prompt, encoding='utf-8')
        print("💾 本体识别提示词已保存")

        return prompt

    def generate_planning_prompt(self, user_intent: str) -> str:
        """
        步骤4: 生成分析方案提示词

        Args:
            user_intent: 用户分析意图

        Returns:
            str: 提示词文本
        """
        print("\n" + "=" * 60)
        print("【步骤4/7】分析方案规划")
        print("=" * 60)
        print(f"📝 用户诉求: {user_intent}")

        if self.df is None:
            print("❌ 请先加载数据")
            return ""

        prompt = self._build_planning_prompt(user_intent)

        # 保存提示词
        (self.session_dir / "step4_planning_prompt.txt").write_text(prompt, encoding='utf-8')
        print("💾 分析方案提示词已保存")

        return prompt

    def generate_script_prompt(self, analysis_plan: Dict = None) -> str:
        """
        步骤5: 生成脚本生成提示词

        Args:
            analysis_plan: 分析方案（可选）

        Returns:
            str: 提示词文本
        """
        print("\n" + "=" * 60)
        print("【步骤5/7】生成分析脚本")
        print("=" * 60)

        if self.df is None:
            print("❌ 请先加载数据")
            return ""

        prompt = self._build_script_prompt(analysis_plan)

        # 保存提示词
        (self.session_dir / "step5_script_prompt.txt").write_text(prompt, encoding='utf-8')
        print("💾 脚本生成提示词已保存")

        return prompt

    def run_full_analysis(self, file_path: str, user_intent: str = "探索性数据分析") -> Dict[str, Any]:
        """
        运行完整分析流程

        Args:
            file_path: 数据文件路径
            user_intent: 用户分析意图

        Returns:
            Dict: 分析结果
        """
        print("\n" + "=" * 60)
        print("🚀 启动通用数据分析流程")
        print(f"📁 数据文件: {file_path}")
        print(f"🎯 分析目标: {user_intent}")
        print("=" * 60)

        # 步骤1: 加载数据
        if not self.load_data(file_path):
            return self._finalize_flow(error="数据加载失败")

        # 步骤2: 质量校验
        self.validate_data()

        # 步骤3: 本体识别
        self.generate_ontology_prompt()

        # 步骤4: 方案规划
        self.generate_planning_prompt(user_intent)

        # 步骤5: 脚本生成
        self.generate_script_prompt()

        return self._finalize_flow()

    def _generate_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成数据画像"""
        profile = {
            'shape': df.shape,
            'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
            'columns': []
        }

        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'null_count': df[col].isnull().sum(),
                'null_pct': df[col].isnull().sum() / len(df) * 100,
                'unique_count': df[col].nunique(),
            }

            if pd.api.types.is_numeric_dtype(df[col]):
                col_info['type'] = 'numeric'
                col_info['min'] = float(df[col].min()) if df[col].notna().any() else None
                col_info['max'] = float(df[col].max()) if df[col].notna().any() else None
                col_info['mean'] = float(df[col].mean()) if df[col].notna().any() else None
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_info['type'] = 'datetime'
            else:
                col_info['type'] = 'categorical' if df[col].nunique() < 100 else 'text'
                col_info['sample_values'] = df[col].dropna().head(3).tolist()

            profile['columns'].append(col_info)

        # 检测潜在维度
        col_names_lower = [c.lower() for c in df.columns]

        profile['potential_time_cols'] = [
            c for c in df.columns
            if any(k in c.lower() for k in ['time', 'date', 'timestamp', 'created'])
        ]

        profile['potential_price_cols'] = [
            c for c in df.columns
            if any(k in c.lower() for k in ['price', 'cost', 'amount', 'revenue', 'profit'])
            and pd.api.types.is_numeric_dtype(df[c])
        ]

        profile['potential_id_cols'] = [
            c for c in df.columns
            if any(k in c.lower() for k in ['id', 'user', 'customer', 'product', 'order'])
        ]

        return profile

    def _build_ontology_prompt(self) -> str:
        """构建本体识别提示词"""
        p = self.data_profile

        prompt = f"""# 数据本体识别

## 数据概况
- 数据形状: {p['shape'][0]:,} 行 × {p['shape'][1]} 列
- 内存占用: {p['memory_mb']:.2f} MB

## 字段详情
"""

        for col in p['columns'][:15]:
            prompt += f"\n- **{col['name']}** ({col['type']}, {col['dtype']})"
            prompt += f"\n  - 唯一值: {col['unique_count']:,}, 缺失率: {col['null_pct']:.1f}%"
            if col.get('mean') is not None:
                prompt += f"\n  - 范围: [{col['min']:.2f}, {col['max']:.2f}], 均值: {col['mean']:.2f}"
            if col.get('sample_values'):
                prompt += f"\n  - 示例值: {col['sample_values'][:3]}"

        if p.get('potential_time_cols'):
            prompt += f"\n\n## 潜在时间列\n{', '.join(p['potential_time_cols'])}"
        if p.get('potential_price_cols'):
            prompt += f"\n\n## 潜在价格/货币列\n{', '.join(p['potential_price_cols'])}"
        if p.get('potential_id_cols'):
            prompt += f"\n\n## 潜在ID/实体列\n{', '.join(p['potential_id_cols'])}"

        prompt += """

## 请思考并回答

1. **实体类型**: 交易/事件型？状态/存量型？关系/网络型？特征/属性型？时序/轨迹型？
2. **数据生成机制**: 观测型？实验型？模拟型？测量型？报告型？
3. **核心维度**: 时间？地理？分类？网络关系？
4. **是否经济型数据？** 如果是，属于零售/订阅/金融/其他？
5. **关键词标签**: 3-5个关键词
6. **适合回答的问题**: 描述/诊断/预测/规范/因果？
7. **数据局限性**: 样本量、时间跨度、潜在偏差？

请以 JSON 格式输出分析结果。
"""

        return prompt

    def _build_planning_prompt(self, user_intent: str) -> str:
        """构建方案规划提示词"""
        if self.data_profile is None:
            return ""

        p = self.data_profile

        prompt = f"""# 分析方案规划

## 用户诉求
"{user_intent}"

## 数据画像
- 实体类型: {p.get('entity_type', '待识别')}
- 数据规模: {p['shape'][0]:,} 行 × {p['shape'][1]} 列

## 字段详情
"""
        for col in p['columns'][:15]:
            prompt += f"- {col['name']}: {col['type']}, 唯一值{col['unique_count']:,}, 缺失{col['null_pct']:.1f}%\n"

        if self.validation_report:
            prompt += f"\n## 数据质量\n"
            prompt += f"- 质量评分: {self.validation_report.overall_score:.1f}/100\n"
            prompt += f"- 问题数: {len(self.validation_report.issues)}\n"

        prompt += """

## 请规划分析方案

1. **问题类型判定**: 描述/诊断/预测/规范/因果？
2. **推荐框架**: 该领域公认的分析方法？
3. **分析步骤**: 具体分步骤路径？
4. **预期输出**: 数字/图表/报告？
5. **风险提示**: 结论可能不可靠的情况？

请以 JSON 格式输出分析方案。
"""

        return prompt

    def _build_script_prompt(self, analysis_plan: Dict = None) -> str:
        """构建脚本生成提示词"""
        prompt = """# 分析脚本生成

## 生成要求

请生成一个完整的 Python 分析脚本，要求：

1. **标准依赖**
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
```

2. **输出目录**: `./output/`
3. **结果保存**: 图表保存为 PNG，数值保存为 JSON
4. **错误处理**: 所有计算都要有 try-except
5. **注释完整**: 每个步骤说明目的

## 数据信息
"""

        if self.data_profile:
            prompt += f"- 行数: {self.data_profile['shape'][0]:,}\n"
            prompt += f"- 列数: {self.data_profile['shape'][1]}\n"
            prompt += f"- 列名: {', '.join(self.data_profile['columns'][:10])}\n"

        prompt += """

请输出完整的 Python 脚本代码。
"""

        return prompt

    def _finalize_flow(self, error: str = None) -> Dict[str, Any]:
        """结束流程"""
        health_score = self.health_monitor.get_health_score()
        is_interrupted = self.health_monitor.is_flow_interrupted()

        # 保存健康报告
        health_report = {
            'session_id': self.session_id,
            'health_score': health_score,
            'is_interrupted': is_interrupted,
            'steps': self.health_monitor.steps,
            'results': self.health_monitor.step_results
        }
        self._save_json("FLOW_HEALTH_REPORT.json", health_report)

        print("\n" + "=" * 60)
        if error:
            print(f"❌ 流程中断: {error}")
        elif is_interrupted:
            print("⚠️ 流程部分完成，关键步骤失败")
        else:
            print("✅ 流程执行成功")

        print(f"\n📂 输出目录: {self.session_dir}")
        print(f"📊 健康评分: {health_score:.1f}")
        print("=" * 60)

        return {
            'session_dir': str(self.session_dir),
            'health_score': health_score,
            'is_interrupted': is_interrupted,
            'error': error
        }

    def _save_json(self, filename: str, data: Dict):
        """保存 JSON 文件"""
        filepath = self.session_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Universal Data Analyst')
    parser.add_argument('file', help='数据文件路径')
    parser.add_argument('--intent', '-i', default='探索性数据分析',
                       help='分析意图')
    parser.add_argument('--output', '-o', default='./analysis_output',
                       help='输出目录')

    args = parser.parse_args()

    orchestrator = DataAnalysisOrchestrator(output_dir=args.output)
    results = orchestrator.run_full_analysis(args.file, args.intent)

    sys.exit(0 if not results.get('is_interrupted') else 1)


if __name__ == '__main__':
    main()
