"""
TikTok Developer API - Review Monitor
TikTok开发者API - 审核监控模块

监控应用审核状态、自动提交审核、处理审核反馈
"""

import time
import logging
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from api_client import TikTokAPIClient, APIResponse, APIError

# 配置日志
logger = logging.getLogger('TikTokReviewMonitor')


class ReviewStatus(Enum):
    """审核状态"""
    PENDING = "pending"           # 待提交
    IN_REVIEW = "in_review"       # 审核中
    APPROVED = "approved"         # 已通过
    REJECTED = "rejected"         # 已驳回
    RESUBMITTED = "resubmitted"     # 重新提交


@dataclass
class ReviewInfo:
    """审核信息"""
    app_id: str = ""
    status: str = ""
    submit_time: str = ""
    review_time: str = ""
    reviewer_comment: str = ""
    rejection_reasons: List[str] = field(default_factory=list)
    estimated_finish_time: str = ""


@dataclass
class AdSlotInfo:
    """广告位信息"""
    ad_slot_id: str = ""
    ad_slot_type: str = ""  # rewarded, interstitial, banner
    status: str = ""
    created_time: str = ""


class ReviewMonitorError(Exception):
    """审核监控错误"""
    pass


class TikTokReviewMonitor:
    """TikTok审核监控器"""

    # 审核状态映射
    STATUS_MAP = {
        "pending": "待提交",
        "in_review": "审核中",
        "approved": "已通过",
        "rejected": "已驳回",
        "resubmitted": "重新提交"
    }

    # 审核时间预估（小时）
    REVIEW_TIME_ESTIMATE = {
        "first_review": 48,   # 首次审核
        "update_review": 24,  # 更新审核
        "re_review": 12       # 复审
    }

    def __init__(self, api_client: TikTokAPIClient):
        """
        初始化审核监控器

        Args:
            api_client: TikTok API客户端
        """
        self.client = api_client

        # 状态回调
        self._status_callback: Optional[Callable] = None

        # 审核历史
        self._review_history: Dict[str, List[ReviewInfo]] = {}

    def set_status_callback(self, callback: Callable[[str, ReviewInfo], None]):
        """
        设置状态回调

        Args:
            callback: 回调函数(app_id, review_info)
        """
        self._status_callback = callback

    def _notify_status_change(self, app_id: str, review_info: ReviewInfo):
        """通知状态变更"""
        if self._status_callback:
            self._status_callback(app_id, review_info)

    def submit_for_review(
        self,
        app_id: str,
        package_version: str,
        changelog: str = "",
        contact_info: str = ""
    ) -> ReviewInfo:
        """
        提交审核

        Args:
            app_id: 应用ID
            package_version: 包版本号
            changelog: 变更日志
            contact_info: 联系方式

        Returns:
            审核信息

        Raises:
            ReviewMonitorError: 提交失败
        """
        logger.info(f"提交审核: {app_id} v{package_version}")

        response = self.client.submit_review(
            app_id=app_id,
            package_version=package_version,
            changelog=changelog,
            contact_info=contact_info
        )

        if not response.is_success():
            raise ReviewMonitorError(f"提交审核失败: {response.error_message}")

        review_data = response.get_data("review", {})
        review_info = ReviewInfo(
            app_id=app_id,
            status="in_review",
            submit_time=datetime.now().isoformat()
        )

        # 记录历史
        if app_id not in self._review_history:
            self._review_history[app_id] = []
        self._review_history[app_id].append(review_info)

        self._notify_status_change(app_id, review_info)

        logger.info(f"审核已提交，等待审核...")
        return review_info

    def get_review_status(self, app_id: str) -> ReviewInfo:
        """
        获取审核状态

        Args:
            app_id: 应用ID

        Returns:
            审核信息
        """
        logger.info(f"查询审核状态: {app_id}")

        response = self.client.get_review_status(app_id)

        if not response.is_success():
            raise ReviewMonitorError(f"获取审核状态失败: {response.error_message}")

        review_data = response.get_data("review", {})
        review_info = ReviewInfo(
            app_id=app_id,
            status=review_data.get("status", ""),
            submit_time=review_data.get("submit_time", ""),
            review_time=review_data.get("review_time", ""),
            reviewer_comment=review_data.get("comment", ""),
            rejection_reasons=review_data.get("rejection_reasons", []),
            estimated_finish_time=review_data.get("estimated_finish_time", "")
        )

        return review_info

    def wait_for_review(
        self,
        app_id: str,
        check_interval: int = 300,  # 5分钟
        max_wait_time: int = 7200,  # 2小时
        on_status_change: Callable[[str, ReviewInfo], None] = None
    ) -> ReviewInfo:
        """
        等待审核完成

        Args:
            app_id: 应用ID
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒）
            on_status_change: 状态变更回调

        Returns:
            最终审核信息

        Raises:
            ReviewMonitorError: 等待超时或失败
        """
        logger.info(f"开始等待审核完成: {app_id}")

        start_time = time.time()
        last_status = ""

        while time.time() - start_time < max_wait_time:
            review_info = self.get_review_status(app_id)

            # 状态变更通知
            if review_info.status != last_status:
                logger.info(f"审核状态变更: {review_info.status}")
                last_status = review_info.status

                if on_status_change:
                    on_status_change(app_id, review_info)

                self._notify_status_change(app_id, review_info)

            # 审核完成
            if review_info.status in ["approved", "rejected"]:
                logger.info(f"审核完成: {review_info.status}")
                return review_info

            # 等待下次检查
            logger.debug(f"等待 {check_interval} 秒后再次检查...")
            time.sleep(check_interval)

        raise ReviewMonitorError(f"等待审核超时（{max_wait_time}秒）")

    def handle_rejection(
        self,
        app_id: str,
        auto_fix: bool = False,
        fix_rules: Dict = None
    ) -> Dict[str, Any]:
        """
        处理审核被拒

        Args:
            app_id: 应用ID
            auto_fix: 是否自动修复
            fix_rules: 修复规则

        Returns:
            处理结果

        Raises:
            ReviewMonitorError: 处理失败
        """
        logger.info(f"处理审核被拒: {app_id}")

        # 获取驳回原因
        review_info = self.get_review_status(app_id)

        if review_info.status != "rejected":
            raise ReviewMonitorError("应用未被驳回")

        rejection_info = {
            "app_id": app_id,
            "reasons": review_info.rejection_reasons,
            "comment": review_info.reviewer_comment,
            "handled": False,
            "actions": []
        }

        # 分析驳回原因
        common_issues = self._analyze_rejection_reasons(review_info.rejection_reasons)

        if auto_fix and fix_rules:
            # 自动修复
            fixed_issues = []
            for issue in common_issues:
                if issue in fix_rules:
                    logger.info(f"自动修复: {issue}")
                    # 调用相应修复逻辑
                    fixed_issues.append({
                        "issue": issue,
                        "fixed": True,
                        "action": fix_rules[issue]
                    })

            rejection_info["actions"] = fixed_issues
            rejection_info["handled"] = True

        return rejection_info

    def _analyze_rejection_reasons(self, reasons: List[str]) -> List[str]:
        """分析驳回原因"""
        issues = []

        reason_keywords = {
            "icon": ["icon", "图标"],
            "screenshot": ["screenshot", "截图"],
            "description": ["description", "描述"],
            "crash": ["crash", "崩溃"],
            "permission": ["permission", "权限"],
            "content": ["content", "内容", "违规"]
        }

        for reason in reasons:
            reason_lower = reason.lower()
            for issue, keywords in reason_keywords.items():
                if any(kw.lower() in reason_lower for kw in keywords):
                    if issue not in issues:
                        issues.append(issue)

        return issues

    def apply_for_ad_slots(
        self,
        app_id: str,
        ad_slot_types: List[str] = None
    ) -> List[AdSlotInfo]:
        """
        申请广告位

        Args:
            app_id: 应用ID
            ad_slot_types: 广告位类型列表

        Returns:
            广告位信息列表

        Raises:
            ReviewMonitorError: 申请失败
        """
        if ad_slot_types is None:
            ad_slot_types = ["rewarded", "interstitial"]

        logger.info(f"申请广告位: {app_id} - {ad_slot_types}")

        ad_slots = []

        for slot_type in ad_slot_types:
            response = self.client.create_ad_slot(app_id, slot_type)

            if response.is_success():
                slot_data = response.get_data("ad_slot", {})
                ad_slots.append(AdSlotInfo(
                    ad_slot_id=slot_data.get("ad_slot_id", ""),
                    ad_slot_type=slot_type,
                    status=slot_data.get("status", "created"),
                    created_time=datetime.now().isoformat()
                ))
                logger.info(f"广告位创建成功: {slot_type}")
            else:
                logger.warning(f"广告位创建失败: {slot_type} - {response.error_message}")

        return ad_slots

    def get_ad_slots(self, app_id: str) -> List[AdSlotInfo]:
        """
        获取应用广告位

        Args:
            app_id: 应用ID

        Returns:
            广告位信息列表
        """
        logger.info(f"获取广告位: {app_id}")

        response = self.client.get_ad_slots(app_id)

        if not response.is_success():
            raise ReviewMonitorError(f"获取广告位失败: {response.error_message}")

        slots_data = response.get_data("ad_slots", [])
        return [AdSlotInfo(
            ad_slot_id=slot.get("ad_slot_id", ""),
            ad_slot_type=slot.get("ad_slot_type", ""),
            status=slot.get("status", ""),
            created_time=slot.get("created_time", "")
        ) for slot in slots_data]

    def estimate_review_time(self, app_id: str, is_first_review: bool = True) -> Dict[str, Any]:
        """
        预估审核时间

        Args:
            app_id: 应用ID
            is_first_review: 是否首次审核

        Returns:
            预估信息
        """
        review_type = "first_review" if is_first_review else "update_review"
        hours = self.REVIEW_TIME_ESTIMATE.get(review_type, 48)

        estimated_finish = datetime.now() + timedelta(hours=hours)

        return {
            "app_id": app_id,
            "review_type": review_type,
            "estimated_hours": hours,
            "estimated_finish_time": estimated_finish.isoformat(),
            "estimated_finish_cn": estimated_finish.strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_review_history(self, app_id: str) -> List[ReviewInfo]:
        """
        获取审核历史

        Args:
            app_id: 应用ID

        Returns:
            审核历史列表
        """
        return self._review_history.get(app_id, [])

    def generate_review_report(self, app_id: str) -> Dict[str, Any]:
        """
        生成审核报告

        Args:
            app_id: 应用ID

        Returns:
            审核报告
        """
        review_info = self.get_review_status(app_id)
        history = self.get_review_history(app_id)

        report = {
            "app_id": app_id,
            "current_status": review_info.status,
            "status_display": self.STATUS_MAP.get(review_info.status, review_info.status),
            "submit_time": review_info.submit_time,
            "review_time": review_info.review_time,
            "reviewer_comment": review_info.reviewer_comment,
            "rejection_reasons": review_info.rejection_reasons,
            "history_count": len(history),
            "history": [
                {
                    "status": h.status,
                    "submit_time": h.submit_time,
                    "review_time": h.review_time
                }
                for h in history
            ],
            "generated_at": datetime.now().isoformat()
        }

        return report


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok Review Monitor Test")
    print("TikTok审核监控器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from api_client import TikTokAPIClient
    from review_monitor import TikTokReviewMonitor, ReviewStatus

    # 初始化
    client = TikTokAPIClient(oauth)
    monitor = TikTokReviewMonitor(client)

    # 提交审核
    review_info = monitor.submit_for_review(
        app_id='your_app_id',
        package_version='1.0.0',
        changelog='First release',
        contact_info='email@example.com'
    )

    # 状态变更回调
    def on_status_change(app_id, review_info):
        print(f"状态变更: {app_id} -> {review_info.status}")

    # 等待审核完成
    result = monitor.wait_for_review(
        app_id='your_app_id',
        check_interval=300,  # 5分钟
        max_wait_time=7200,  # 2小时
        on_status_change=on_status_change
    )

    if result.status == 'approved':
        print("审核通过！")
    else:
        print(f"审核驳回: {result.rejection_reasons}")

    # 申请广告位
    ad_slots = monitor.apply_for_ad_slots(
        app_id='your_app_id',
        ad_slot_types=['rewarded', 'interstitial']
    )

    for slot in ad_slots:
        print(f"广告位: {slot.ad_slot_type} - {slot.ad_slot_id}")

    # 生成审核报告
    report = monitor.generate_review_report('your_app_id')
    print(report)
    """)


if __name__ == "__main__":
    main()
