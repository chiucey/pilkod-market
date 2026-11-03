#!/usr/bin/env python3
"""
TikTok广告自动优化脚本
功能：定时检查广告表现，自动执行优化规则
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AdGroupMetrics:
    """广告组指标数据"""
    adgroup_id: str
    adgroup_name: str
    campaign_id: str
    spend: float
    impressions: int
    clicks: int
    conversions: int
    ctr: float
    cvr: float
    cpc: float
    cpa: float
    roas: float
    status: str


@dataclass
class OptimizationRule:
    """优化规则"""
    name: str
    condition_type: str
    threshold: float
    action: str
    action_value: float
    priority: int = 1


class TikTokAdOptimizer:
    """TikTok广告自动优化器"""

    # 默认优化规则库
    DEFAULT_RULES = [
        # 规则1：ROAS达标自动扩量
        OptimizationRule(
            name="roas_expand",
            condition_type="roas",
            threshold=1.3,
            action="increase_budget",
            action_value=0.2,
            priority=2
        ),
        # 规则2：超成本自动降价
        OptimizationRule(
            name="cpa_reduce",
            condition_type="cpa",
            threshold=1.5,
            action="decrease_bid",
            action_value=0.15,
            priority=1
        ),
        # 规则3：低效广告暂停
        OptimizationRule(
            name="low_performance_pause",
            condition_type="no_conversion_spend",
            threshold=500,
            action="pause",
            action_value=0,
            priority=1
        ),
        # 规则4：CTR过低淘汰
        OptimizationRule(
            name="low_ctr_pause",
            condition_type="ctr",
            threshold=0.5,
            action="pause",
            action_value=0,
            priority=1
        ),
    ]

    def __init__(self, config_path: Optional[str] = None):
        """初始化优化器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.rules = self._load_rules()
        self.execution_log = []

    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        """加载配置"""
        default_config = {
            "target_cpa": 50.0,
            "target_roas": 2.0,
            "min_conversions_for_optimization": 30,
            "min_spend_for_pause": 200,
            "min_ctr_threshold": 0.5,
            "max_budget_daily_increase": 0.5,  # 50%
            "auto_optimize_enabled": True,
            "notification_webhook": None,
        }

        if config_path:
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")

        return default_config

    def _load_rules(self) -> List[OptimizationRule]:
        """加载优化规则"""
        return self.DEFAULT_RULES.copy()

    def add_rule(self, rule: OptimizationRule) -> None:
        """添加优化规则"""
        self.rules.append(rule)
        self.rules.sort(key=lambda x: x.priority, reverse=True)
        logger.info(f"添加优化规则: {rule.name}")

    def remove_rule(self, rule_name: str) -> bool:
        """移除优化规则"""
        for i, rule in enumerate(self.rules):
            if rule.name == rule_name:
                self.rules.pop(i)
                logger.info(f"移除优化规则: {rule_name}")
                return True
        return False

    def analyze_adgroup(self, metrics: AdGroupMetrics) -> Dict:
        """分析单个广告组

        Args:
            metrics: 广告组指标数据

        Returns:
            分析结果和建议
        """
        result = {
            "adgroup_id": metrics.adgroup_id,
            "adgroup_name": metrics.adgroup_name,
            "current_metrics": asdict(metrics),
            "applicable_rules": [],
            "recommended_actions": [],
            "decision": "hold"  # hold / expand / reduce / pause
        }

        # 检查每条规则
        for rule in self.rules:
            is_triggered, action_details = self._check_rule(rule, metrics)
            if is_triggered:
                result["applicable_rules"].append({
                    "rule_name": rule.name,
                    "details": action_details
                })
                result["recommended_actions"].append(action_details)

        # 做出最终决策
        if any(a["action"] == "pause" for a in result["recommended_actions"]):
            result["decision"] = "pause"
        elif any(a["action"] == "decrease_bid" for a in result["recommended_actions"]):
            result["decision"] = "reduce"
        elif any(a["action"] == "increase_budget" for a in result["recommended_actions"]):
            result["decision"] = "expand"

        return result

    def _check_rule(self, rule: OptimizationRule, metrics: AdGroupMetrics) -> tuple:
        """检查规则是否触发

        Returns:
            (是否触发, 动作详情)
        """
        triggered = False
        details = {
            "rule": rule.name,
            "action": rule.action,
            "reason": ""
        }

        # 检查最小样本量
        if metrics.conversions < self.config["min_conversions_for_optimization"]:
            if rule.action in ["increase_budget", "decrease_bid"]:
                return False, {}

        if rule.condition_type == "roas":
            target_roas = self.config["target_roas"]
            if metrics.roas >= target_roas * rule.threshold:
                triggered = True
                details["reason"] = f"ROAS({metrics.roas:.2f}) >= 目标ROAS({target_roas}) × {rule.threshold}"

        elif rule.condition_type == "cpa":
            target_cpa = self.config["target_cpa"]
            if metrics.cpa >= target_cpa * rule.threshold:
                triggered = True
                details["reason"] = f"CPA({metrics.cpa:.2f}) >= 目标CPA({target_cpa}) × {rule.threshold}"

        elif rule.condition_type == "ctr":
            if metrics.ctr < rule.threshold:
                triggered = True
                details["reason"] = f"CTR({metrics.ctr:.2%}) < 阈值({rule.threshold:.2%})"

        elif rule.condition_type == "no_conversion_spend":
            if metrics.conversions == 0 and metrics.spend >= rule.threshold:
                triggered = True
                details["reason"] = f"花费({metrics.spend:.2f}) >= {rule.threshold} 但无转化"

        if triggered:
            details["value"] = rule.action_value
            details["priority"] = rule.priority

        return triggered, details

    def optimize_batch(self, adgroup_list: List[AdGroupMetrics]) -> Dict:
        """批量优化广告组

        Args:
            adgroup_list: 广告组列表

        Returns:
            优化报告
        """
        report = {
            "optimization_time": datetime.now().isoformat(),
            "total_adgroups": len(adgroup_list),
            "results": {
                "expand": [],
                "reduce": [],
                "pause": [],
                "hold": []
            },
            "summary": {
                "expand_count": 0,
                "reduce_count": 0,
                "pause_count": 0,
                "hold_count": 0,
                "total_suggestions": 0
            }
        }

        for metrics in adgroup_list:
            analysis = self.analyze_adgroup(metrics)

            # 分类结果
            decision = analysis["decision"]
            report["results"][decision].append({
                "adgroup_id": metrics.adgroup_id,
                "adgroup_name": metrics.adgroup_name,
                "analysis": analysis,
                "actions": analysis["recommended_actions"]
            })
            report["summary"][f"{decision}_count"] += 1
            report["summary"]["total_suggestions"] += len(analysis["recommended_actions"])

        # 记录执行日志
        self.execution_log.append(report)

        logger.info(f"优化完成: {len(adgroup_list)}个广告组")
        logger.info(f"扩量: {report['summary']['expand_count']}, "
                   f"缩量: {report['summary']['reduce_count']}, "
                   f"暂停: {report['summary']['pause_count']}, "
                   f"观望: {report['summary']['hold_count']}")

        return report

    def execute_optimization(self, optimization_report: Dict) -> Dict:
        """执行优化操作

        Args:
            optimization_report: 优化报告

        Returns:
            执行结果
        """
        execution_result = {
            "execution_time": datetime.now().isoformat(),
            "executed_actions": [],
            "failed_actions": [],
            "pending_actions": []
        }

        # 实际执行时需要调用TikTok API
        # 此处仅为模拟执行逻辑

        for decision_type, adgroups in optimization_report["results"].items():
            if decision_type == "pause":
                for ag in adgroups:
                    execution_result["executed_actions"].append({
                        "type": "pause_adgroup",
                        "adgroup_id": ag["adgroup_id"],
                        "reason": "低效广告自动暂停"
                    })

            elif decision_type == "expand":
                for ag in adgroups:
                    for action in ag["actions"]:
                        if action["action"] == "increase_budget":
                            execution_result["executed_actions"].append({
                                "type": "update_budget",
                                "adgroup_id": ag["adgroup_id"],
                                "increase_percent": action["value"] * 100
                            })

            elif decision_type == "reduce":
                for ag in adgroups:
                    for action in ag["actions"]:
                        if action["action"] == "decrease_bid":
                            execution_result["executed_actions"].append({
                                "type": "update_bid",
                                "adgroup_id": ag["adgroup_id"],
                                "decrease_percent": action["value"] * 100
                            })

        return execution_result

    def generate_optimization_report(self) -> str:
        """生成优化报告（Markdown格式）"""
        if not self.execution_log:
            return "暂无优化记录"

        latest = self.execution_log[-1]
        summary = latest["summary"]

        report = f"""# TikTok广告自动优化报告

📅 **生成时间**: {latest['optimization_time']}

## 优化概览

| 指标 | 数量 |
|------|------|
| 总广告组数 | {summary['total_adgroups']} |
| 建议扩量 | {summary['expand_count']} |
| 建议缩量 | {summary['reduce_count']} |
| 建议暂停 | {summary['pause_count']} |
| 建议观望 | {summary['hold_count']} |

## 扩量广告组

"""

        for ag in latest["results"]["expand"]:
            report += f"""### {ag['adgroup_name']}
- ID: `{ag['adgroup_id']}`
- 原因: {ag['analysis']['recommended_actions'][0]['reason']}

"""

        report += "## 缩量广告组\n\n"
        for ag in latest["results"]["reduce"]:
            report += f"""### {ag['adgroup_name']}
- ID: `{ag['adgroup_id']}`
- 原因: {ag['analysis']['recommended_actions'][0]['reason']}

"""

        report += "## 建议暂停广告组\n\n"
        for ag in latest["results"]["pause"]:
            report += f"""### {ag['adgroup_name']}
- ID: `{ag['adgroup_id']}`
- 原因: {ag['analysis']['recommended_actions'][0]['reason']}

"""

        return report

    def save_report(self, report: Dict, filepath: str) -> None:
        """保存报告到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        logger.info(f"报告已保存: {filepath}")

    def export_logs(self, filepath: str) -> None:
        """导出执行日志"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)
        logger.info(f"日志已导出: {filepath}")


def demo():
    """演示函数"""
    # 创建示例数据
    sample_adgroups = [
        AdGroupMetrics(
            adgroup_id="ag001",
            adgroup_name="夏季新品-女裙-测试组1",
            campaign_id="camp001",
            spend=1500.0,
            impressions=50000,
            clicks=800,
            conversions=45,
            ctr=1.6,
            cvr=5.6,
            cpc=1.88,
            cpa=33.33,
            roas=3.5,
            status="ENABLE"
        ),
        AdGroupMetrics(
            adgroup_id="ag002",
            adgroup_name="夏季新品-女裙-测试组2",
            campaign_id="camp001",
            spend=2000.0,
            impressions=60000,
            clicks=600,
            conversions=20,
            ctr=1.0,
            cvr=3.3,
            cpc=3.33,
            cpa=100.0,
            roas=1.2,
            status="ENABLE"
        ),
        AdGroupMetrics(
            adgroup_id="ag003",
            adgroup_name="清仓特卖-测试组",
            campaign_id="camp002",
            spend=800.0,
            impressions=30000,
            clicks=150,
            conversions=0,
            ctr=0.5,
            cvr=0.0,
            cpc=5.33,
            cpa=0,
            roas=0,
            status="ENABLE"
        ),
    ]

    # 创建优化器
    optimizer = TikTokAdOptimizer()

    # 设置优化目标
    optimizer.config["target_cpa"] = 50.0
    optimizer.config["target_roas"] = 2.0

    # 执行优化
    report = optimizer.optimize_batch(sample_adgroups)

    # 输出报告
    print(optimizer.generate_optimization_report())

    # 保存报告
    optimizer.save_report(report, "/tmp/optimization_report.json")


if __name__ == "__main__":
    demo()
