# -*- coding: utf-8 -*-
"""
资源预算监控模块
追踪 Token 消耗、API 调用次数、执行时间，设置阈值告警与限流

作者: MiniMax Agent
版本: 1.0.0
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import threading
import uuid


class AlertLevel(Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class OperationType(Enum):
    """操作类型枚举"""
    CODE_GENERATION = "code_generation"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    OPTIMIZATION = "optimization"
    SELF_IMPROVEMENT = "self_improvement"
    OTHER = "other"


@dataclass
class ResourceRecord:
    """资源记录数据类"""
    session_id: str
    timestamp: str
    operation_type: str
    token_input: int = 0
    token_output: int = 0
    token_total: int = 0
    api_calls: int = 1
    execution_time_ms: int = 0
    wait_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.token_total == 0:
            self.token_total = self.token_input + self.token_output


@dataclass
class ThresholdConfig:
    """阈值配置数据类"""
    # Token 阈值
    token_daily_soft: int = 30000
    token_daily_hard: int = 50000
    token_per_call_warning: int = 8000
    token_per_call_critical: int = 10000

    # API 调用阈值
    api_rpm_soft: int = 50
    api_rpm_hard: int = 60
    api_hourly_soft: int = 1500
    api_hourly_hard: int = 2000
    api_daily_soft: int = 8000
    api_daily_hard: int = 10000

    # 执行时间阈值（毫秒）
    execution_time_ms_soft: int = 30000
    execution_time_ms_hard: int = 60000
    execution_daily_total_ms_soft: int = 3600000
    execution_daily_total_ms_hard: int = 7200000

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'ThresholdConfig':
        return cls(**data)


class AlertManager:
    """告警管理器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.alert_history: List[Dict] = []
        self.listeners: List[callable] = []

    def add_listener(self, listener: callable):
        """添加告警监听器"""
        self.listeners.append(listener)

    def trigger_alert(self, level: AlertLevel, message: str, details: Dict):
        """触发告警"""
        alert = {
            "level": level.value,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "alert_id": str(uuid.uuid4())
        }
        self.alert_history.append(alert)

        # 通知所有监听器
        for listener in self.listeners:
            try:
                listener(alert)
            except Exception as e:
                print(f"告警监听器执行失败: {e}")

        return alert

    def get_recent_alerts(self, count: int = 10) -> List[Dict]:
        """获取最近的告警"""
        return self.alert_history[-count:]

    def get_alerts_by_level(self, level: AlertLevel) -> List[Dict]:
        """按级别获取告警"""
        return [a for a in self.alert_history if a["level"] == level.value]


class RateLimiter:
    """限流器"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self.gradual_recovery = self.config.get("gradual_recovery", True)
        self.recovery_rate = self.config.get("recovery_rate_per_minute", 0.1)

        self.is_limited = False
        self.limited_until: Optional[datetime] = None
        self.current_quota_ratio = 1.0  # 当前配额比例

        self._lock = threading.Lock()

    def should_rate_limit(self, current_rpm: int, threshold: int) -> bool:
        """检查是否需要限流"""
        if not self.enabled:
            return False

        with self._lock:
            if self.is_limited:
                if self.limited_until and datetime.now() < self.limited_until:
                    return True
                else:
                    self.is_limited = False
                    self.limited_until = None

            return current_rpm >= threshold

    def apply_limit(self, duration_seconds: int = 60):
        """应用限流"""
        with self._lock:
            self.is_limited = True
            self.limited_until = datetime.now() + timedelta(seconds=duration_seconds)
            self.current_quota_ratio = max(0.1, self.current_quota_ratio * 0.5)

    def apply_gradual_recovery(self):
        """应用渐进恢复"""
        if self.gradual_recovery and self.current_quota_ratio < 1.0:
            self.current_quota_ratio = min(1.0, self.current_quota_ratio + self.recovery_rate)

    def get_wait_time(self) -> int:
        """获取需要等待的时间（秒）"""
        if not self.is_limited or not self.limited_until:
            return 0

        remaining = self.limited_until - datetime.now()
        return max(0, int(remaining.total_seconds()))

    def reset(self):
        """重置限流状态"""
        with self._lock:
            self.is_limited = False
            self.limited_until = None
            self.current_quota_ratio = 1.0


class MonitoringSession:
    """监控会话"""

    def __init__(
        self,
        session_id: str,
        data_dir: str,
        thresholds: ThresholdConfig,
        alert_manager: AlertManager,
        rate_limiter: RateLimiter
    ):
        self.session_id = session_id
        self.data_dir = data_dir
        self.thresholds = thresholds
        self.alert_manager = alert_manager
        self.rate_limiter = rate_limiter

        self.records: deque = deque(maxlen=100)
        self.start_time = datetime.now()
        self.session_stats = {
            "total_token_input": 0,
            "total_token_output": 0,
            "total_token": 0,
            "total_api_calls": 0,
            "total_execution_time_ms": 0,
            "total_wait_time_ms": 0
        }

        # 滑动窗口计数器（用于频率统计）
        self.call_timestamps: deque = deque(maxlen=1000)

        self._lock = threading.Lock()
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)

    def record_api_call(
        self,
        operation_type: str,
        token_input: int = 0,
        token_output: int = 0,
        execution_time_ms: int = 0,
        wait_time_ms: int = 0,
        metadata: Optional[Dict] = None
    ) -> ResourceRecord:
        """记录 API 调用"""
        record = ResourceRecord(
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            operation_type=operation_type,
            token_input=token_input,
            token_output=token_output,
            token_total=token_input + token_output,
            api_calls=1,
            execution_time_ms=execution_time_ms,
            wait_time_ms=wait_time_ms,
            metadata=metadata or {}
        )

        with self._lock:
            self.records.append(record)
            self.call_timestamps.append(datetime.now())

            # 更新会话统计
            self.session_stats["total_token_input"] += token_input
            self.session_stats["total_token_output"] += token_output
            self.session_stats["total_token"] += record.token_total
            self.session_stats["total_api_calls"] += 1
            self.session_stats["total_execution_time_ms"] += execution_time_ms
            self.session_stats["total_wait_time_ms"] += wait_time_ms

        # 检查阈值
        self._check_thresholds(record)

        # 保存记录
        self._save_record(record)

        return record

    def record_batch(self, records_data: List[Dict]):
        """批量记录"""
        for data in records_data:
            self.record_api_call(**data)

    def _check_thresholds(self, record: ResourceRecord):
        """检查阈值并触发告警"""
        status = self.get_status()

        # Token 单次调用阈值检查
        if record.token_total >= self.thresholds.token_per_call_critical:
            self.alert_manager.trigger_alert(
                AlertLevel.CRITICAL,
                f"Token 消耗过高: {record.token_total}",
                {
                    "record": asdict(record),
                    "threshold": self.thresholds.token_per_call_critical,
                    "action": "hard_stop"
                }
            )
        elif record.token_total >= self.thresholds.token_per_call_warning:
            self.alert_manager.trigger_alert(
                AlertLevel.WARNING,
                f"Token 消耗警告: {record.token_total}",
                {
                    "record": asdict(record),
                    "threshold": self.thresholds.token_per_call_warning,
                    "action": "rate_limit"
                }
            )

        # 执行时间阈值检查
        if record.execution_time_ms >= self.thresholds.execution_time_ms_hard:
            self.alert_manager.trigger_alert(
                AlertLevel.CRITICAL,
                f"执行时间过长: {record.execution_time_ms}ms",
                {
                    "record": asdict(record),
                    "threshold": self.thresholds.execution_time_ms_hard
                }
            )
        elif record.execution_time_ms >= self.thresholds.execution_time_ms_soft:
            self.alert_manager.trigger_alert(
                AlertLevel.WARNING,
                f"执行时间警告: {record.execution_time_ms}ms",
                {
                    "record": asdict(record),
                    "threshold": self.thresholds.execution_time_ms_soft
                }
            )

        # 检查是否需要限流
        if self.should_rate_limit():
            self.rate_limiter.apply_limit()

    def should_rate_limit(self) -> bool:
        """检查是否应该限流"""
        status = self.get_status()
        return self.rate_limiter.should_rate_limit(
            status["current_rpm"],
            self.thresholds.api_rpm_hard
        )

    def get_rate_limit_wait(self) -> int:
        """获取限流等待时间"""
        return self.rate_limiter.get_wait_time()

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        with self._lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            hour_ago = now - timedelta(hours=1)
            day_ago = now - timedelta(days=1)

            # 计算滑动窗口内的调用次数
            recent_calls = [ts for ts in self.call_timestamps if ts >= minute_ago]
            hour_calls = [ts for ts in self.call_timestamps if ts >= hour_ago]

            return {
                "session_id": self.session_id,
                "uptime_seconds": (now - self.start_time).total_seconds(),
                "current_rpm": len(recent_calls),
                "current_rph": len(hour_calls),
                "daily_token_total": self.session_stats["total_token"],
                "daily_api_calls": self.session_stats["total_api_calls"],
                "daily_execution_time_ms": self.session_stats["total_execution_time_ms"],
                "total_records": len(self.records),
                "is_rate_limited": self.rate_limiter.is_limited,
                "quota_ratio": self.rate_limiter.current_quota_ratio,
                "thresholds": self.thresholds.to_dict()
            }

    def get_trend(self, metric: str, window_size: int = 10) -> Dict:
        """获取指标趋势"""
        records = list(self.records)[-window_size:]

        if not records:
            return {"values": [], "average": 0, "max": 0, "min": 0}

        values = []
        for record in records:
            if metric == "token_total":
                values.append(record.token_total)
            elif metric == "execution_time_ms":
                values.append(record.execution_time_ms)
            elif metric == "api_calls":
                values.append(record.api_calls)

        return {
            "values": values,
            "average": sum(values) / len(values) if values else 0,
            "max": max(values) if values else 0,
            "min": min(values) if values else 0
        }

    def _save_record(self, record: ResourceRecord):
        """保存记录到文件"""
        filepath = os.path.join(
            self.data_dir,
            f"session_{self.session_id}.jsonl"
        )

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + "\n")

    def end_session(self) -> Dict:
        """结束会话并返回统计"""
        with self._lock:
            stats = {
                "session_id": self.session_id,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
                **self.session_stats,
                "records_count": len(self.records),
                "alerts_count": len(self.alert_manager.alert_history)
            }

        # 保存会话摘要
        self._save_session_summary(stats)

        return stats

    def _save_session_summary(self, stats: Dict):
        """保存会话摘要"""
        filepath = os.path.join(
            self.data_dir,
            f"summary_{self.session_id}.json"
        )

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)


class BudgetMonitor:
    """资源预算监控主类"""

    def __init__(
        self,
        config_path: Optional[str] = None,
        data_dir: str = "data/budget_tracking",
        thresholds: Optional[ThresholdConfig] = None
    ):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化阈值配置
        self.thresholds = thresholds or ThresholdConfig.from_dict(
            self.config.get("thresholds", {})
        )

        # 初始化组件
        self.alert_manager = AlertManager(self.config.get("alerts", {}))
        self.rate_limiter = RateLimiter(self.config.get("rate_limiting", {}))

        self.current_session: Optional[MonitoringSession] = None
        self.sessions: Dict[str, MonitoringSession] = {}

        # 注册默认告警监听器
        self.alert_manager.add_listener(self._default_alert_handler)

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path and os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_config(self, config_path: str):
        """保存配置到文件"""
        config = {
            "thresholds": self.thresholds.to_dict(),
            "alerts": self.alert_manager.config,
            "rate_limiting": self.rate_limiter.config
        }

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

    def _default_alert_handler(self, alert: Dict):
        """默认告警处理器"""
        level = alert["level"]
        message = alert["message"]

        if level == "critical":
            print(f"[严重告警] {message}")
        elif level == "warning":
            print(f"[警告] {message}")
        else:
            print(f"[通知] {message}")

    def start_session(
        self,
        operation_name: str = "default"
    ) -> MonitoringSession:
        """开始新的监控会话"""
        session_id = f"{operation_name}_{int(time.time())}"

        session = MonitoringSession(
            session_id=session_id,
            data_dir=self.data_dir,
            thresholds=self.thresholds,
            alert_manager=self.alert_manager,
            rate_limiter=self.rate_limiter
        )

        self.current_session = session
        self.sessions[session_id] = session

        return session

    def end_session(self) -> Optional[Dict]:
        """结束当前会话"""
        if self.current_session:
            stats = self.current_session.end_session()
            self.current_session = None
            return stats
        return None

    def get_current_session(self) -> Optional[MonitoringSession]:
        """获取当前会话"""
        return self.current_session

    def generate_report(
        self,
        period: str = "daily",
        format: str = "markdown"
    ) -> str:
        """生成资源使用报告"""
        now = datetime.now()

        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(weeks=1)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:
            start_date = now - timedelta(days=1)

        # 收集所有会话记录
        all_records = []
        for session_id, session in self.sessions.items():
            for record in session.records:
                if datetime.fromisoformat(record.timestamp) >= start_date:
                    all_records.append(record)

        # 生成报告
        if format == "markdown":
            return self._generate_markdown_report(all_records, period, start_date, now)
        elif format == "json":
            return json.dumps({
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": now.isoformat(),
                "records": [asdict(r) for r in all_records]
            }, ensure_ascii=False, indent=2)
        else:
            return self._generate_markdown_report(all_records, period, start_date, now)

    def _generate_markdown_report(
        self,
        records: List[ResourceRecord],
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """生成 Markdown 格式报告"""
        total_tokens = sum(r.token_total for r in records)
        total_api_calls = sum(r.api_calls for r in records)
        total_execution_time = sum(r.execution_time_ms for r in records)

        avg_token = total_tokens / len(records) if records else 0
        avg_execution_time = total_execution_time / len(records) if records else 0

        period_name = {
            "daily": "日",
            "weekly": "周",
            "monthly": "月"
        }.get(period, "指定")

        report = f"""# 资源预算监控报告

## 报告周期
- 开始时间: {start_date.strftime('%Y-%m-%d %H:%M:%S')}
- 结束时间: {end_date.strftime('%Y-%m-%d %H:%M:%S')}

## 资源消耗汇总

| 指标 | 数值 |
|------|------|
| 总 Token 消耗 | {total_tokens:,} |
| API 调用次数 | {total_api_calls:,} |
| 总执行时间 | {total_execution_time:,} ms |
| 平均 Token/次 | {avg_token:,.0f} |
| 平均执行时间 | {avg_execution_time:,.0f} ms |

## 操作类型分布

"""

        # 统计操作类型分布
        operation_stats = {}
        for record in records:
            op_type = record.operation_type
            if op_type not in operation_stats:
                operation_stats[op_type] = {
                    "count": 0,
                    "token_total": 0,
                    "execution_time_ms": 0
                }
            operation_stats[op_type]["count"] += 1
            operation_stats[op_type]["token_total"] += record.token_total
            operation_stats[op_type]["execution_time_ms"] += record.execution_time_ms

        for op_type, stats in sorted(
            operation_stats.items(),
            key=lambda x: x[1]["token_total"],
            reverse=True
        ):
            report += f"- **{op_type}**: {stats['count']} 次, {stats['token_total']:,} Token\n"

        # 添加告警信息
        recent_alerts = self.alert_manager.get_recent_alerts(10)
        if recent_alerts:
            report += "\n## 最近告警\n\n"
            for alert in recent_alerts:
                level_icon = {
                    "info": "ℹ️",
                    "warning": "⚠️",
                    "critical": "🚨"
                }.get(alert["level"], "")
                report += f"- {level_icon} [{alert['level'].upper()}] {alert['message']} ({alert['timestamp']})\n"

        # 添加优化建议
        report += "\n## 优化建议\n\n"

        if avg_token > self.thresholds.token_per_call_warning:
            report += f"- 当前平均 Token 消耗 ({avg_token:,.0f}) 接近警告阈值，考虑优化提示词长度\n"

        if avg_execution_time > self.thresholds.execution_time_ms_soft:
            report += f"- 当前平均执行时间 ({avg_execution_time:,.0f}ms) 较长，建议检查处理逻辑\n"

        if total_api_calls > self.thresholds.api_daily_soft:
            report += f"- API 调用次数较多，考虑合并请求或增加缓存机制\n"

        if not report.endswith("建议\n"):
            report += "- 资源消耗处于正常范围\n"

        report += f"\n---\n*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return report

    def save_report(self, report: str, output_path: str):
        """保存报告到文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)

    def update_thresholds(self, thresholds: ThresholdConfig):
        """更新阈值配置"""
        self.thresholds = thresholds


# 便捷函数
def create_monitor(
    config_path: Optional[str] = None,
    data_dir: str = "data/budget_tracking"
) -> BudgetMonitor:
    """创建监控器实例"""
    return BudgetMonitor(config_path=config_path, data_dir=data_dir)


# 导出公共接口
__all__ = [
    "BudgetMonitor",
    "MonitoringSession",
    "ResourceRecord",
    "ThresholdConfig",
    "AlertManager",
    "RateLimiter",
    "AlertLevel",
    "OperationType",
    "create_monitor"
]
