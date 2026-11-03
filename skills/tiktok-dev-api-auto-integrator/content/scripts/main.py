"""
TikTok Developer API - Main Integrator
TikTok开发者API - 主协调器

整合所有模块，提供完整的TikTok开发者API自动化操作
"""

import os
import sys
import logging
from typing import Dict, Optional, Any, Callable
from pathlib import Path

from config_loader import TikTokConfigLoader, TikTokConfig, OAuthConfig
from auth import TikTokOAuth, OAuthToken
from api_client import TikTokAPIClient, APIResponse
from app_manager import TikTokAppManager, AppCreationConfig, MiniAppInfo
from upload_manager import TikTokUploadManager, UploadConfig, UploadProgress
from review_monitor import TikTokReviewMonitor, ReviewInfo, AdSlotInfo

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TikTokIntegrator')


class TikTokIntegratorError(Exception):
    """TikTok集成器错误"""
    pass


class TikTokDevIntegrator:
    """TikTok开发者API集成器

    整合OAuth、应用管理、文件上传、审核监控，提供一键式自动化操作
    """

    def __init__(self, config_path: str = None):
        """
        初始化集成器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config_loader = TikTokConfigLoader()
        self.config = self.config_loader.load(config_path)

        # 验证配置
        validation = TikTokConfigLoader.validate_config(self.config)
        if not validation["valid"]:
            logger.warning(f"配置验证失败: {validation['errors']}")

        # 初始化各模块（暂不初始化client，待授权后设置）
        self.oauth: Optional[TikTokOAuth] = None
        self.client: Optional[TikTokAPIClient] = None
        self.app_manager: Optional[TikTokAppManager] = None
        self.upload_manager: Optional[TikTokUploadManager] = None
        self.review_monitor: Optional[TikTokReviewMonitor] = None

        # Token存储路径
        self.token_file = Path(self.config.cache_dir) / "oauth_token.json"
        self.token_file.parent.mkdir(parents=True, exist_ok=True)

        # 授权状态
        self._is_authenticated = False

    def initialize(self, oauth: TikTokOAuth = None):
        """
        初始化各模块

        Args:
            oauth: TikTokOAuth实例（如果已授权）
        """
        if oauth:
            self.oauth = oauth
            self._is_authenticated = True
        elif self.token_file.exists():
            # 从文件加载token
            self._load_token()

        # 创建API客户端
        if self._is_authenticated:
            self._create_clients()
        else:
            # 创建OAuth
            self.oauth = TikTokOAuth(
                client_id=self.config.oauth.client_id,
                client_secret=self.config.oauth.client_secret,
                redirect_uri=self.config.oauth.redirect_uri,
                auth_url=self.config.oauth.auth_url,
                token_url=self.config.oauth.token_url,
                scopes=self.config.oauth.scopes
            )

    def _create_clients(self):
        """创建各模块客户端"""
        if not self._is_authenticated:
            raise TikTokIntegratorError("未授权，请先完成OAuth授权")

        self.client = TikTokAPIClient(
            oauth=self.oauth,
            base_url=self.config.api.base_url,
            timeout=self.config.api.timeout,
            max_retries=self.config.api.max_retries
        )

        self.app_manager = TikTokAppManager(self.client)
        self.upload_manager = TikTokUploadManager(
            self.client,
            UploadConfig(
                chunk_size=self.config.upload.chunk_size,
                max_retries=self.config.upload.max_retries
            )
        )
        self.review_monitor = TikTokReviewMonitor(self.client)

    def _load_token(self):
        """从文件加载Token"""
        try:
            token = OAuthToken.load_from_file(str(self.token_file))

            # 检查token是否过期
            if token.is_expired():
                logger.info("Token已过期，需要刷新")
                self.oauth = TikTokOAuth(
                    client_id=self.config.oauth.client_id,
                    client_secret=self.config.oauth.client_secret,
                    redirect_uri=self.config.oauth.redirect_uri
                )
                self.oauth.set_token(token)
            else:
                self.oauth = TikTokOAuth(
                    client_id=self.config.oauth.client_id,
                    client_secret=self.config.oauth.client_secret,
                    redirect_uri=self.config.oauth.redirect_uri
                )
                self.oauth.set_token(token)
                self._is_authenticated = True

        except Exception as e:
            logger.warning(f"Token加载失败: {e}")
            self._is_authenticated = False

    def _save_token(self, token: OAuthToken):
        """保存Token"""
        token.save_to_file(str(self.token_file))
        self._is_authenticated = True

    # ==================== OAuth 授权 ====================

    def get_authorization_url(self) -> str:
        """
        获取授权URL

        Returns:
            授权URL
        """
        if not self.oauth:
            self.initialize()

        url, state = self.oauth.get_authorization_url()
        logger.info(f"授权URL: {url}")
        return url

    def handle_authorization_callback(self, code: str, state: str = None) -> OAuthToken:
        """
        处理授权回调

        Args:
            code: 授权码
            state: 状态码

        Returns:
            OAuthToken
        """
        if not self.oauth:
            raise TikTokIntegratorError("OAuth未初始化")

        token = self.oauth.exchange_code_for_token(code, state)
        self._save_token(token)
        self._create_clients()

        logger.info("授权成功")
        return token

    def refresh_token_if_needed(self) -> bool:
        """
        必要时刷新Token

        Returns:
            是否成功
        """
        if not self.oauth:
            return False

        if self.oauth.is_token_expired():
            logger.info("Token即将过期，刷新中...")
            success = self.oauth.refresh_access_token()
            if success:
                self._save_token(self.oauth.get_token())
            return success

        return True

    # ==================== 应用管理 ====================

    def create_app(
        self,
        title: str,
        description: str,
        category: str = "casual_game",
        language: str = "en"
    ) -> MiniAppInfo:
        """
        创建应用

        Args:
            title: 应用标题
            description: 应用描述
            category: 分类
            language: 语言

        Returns:
            MiniAppInfo
        """
        self._ensure_authenticated()

        config = AppCreationConfig(
            title=title,
            description=description,
            category=category,
            language=language
        )

        return self.app_manager.create_app(config)

    def get_app_info(self, app_id: str) -> MiniAppInfo:
        """获取应用信息"""
        self._ensure_authenticated()
        return self.app_manager.get_app_info(app_id)

    def get_all_apps(self) -> list:
        """获取所有应用"""
        self._ensure_authenticated()
        return self.app_manager.get_app_list()

    def find_app(self, title: str) -> Optional[MiniAppInfo]:
        """根据标题查找应用"""
        self._ensure_authenticated()
        return self.app_manager.find_app_by_title(title)

    # ==================== 文件上传 ====================

    def upload_game_package(
        self,
        app_id: str,
        file_path: str,
        version: str = None,
        on_progress: Callable[[UploadProgress], None] = None
    ) -> Dict[str, Any]:
        """
        上传游戏包

        Args:
            app_id: 应用ID
            file_path: 包文件路径
            version: 版本号
            on_progress: 进度回调

        Returns:
            上传结果
        """
        self._ensure_authenticated()
        return self.upload_manager.upload_game_package(
            app_id=app_id,
            file_path=file_path,
            version=version,
            on_progress=on_progress
        )

    def validate_package(self, file_path: str) -> Dict[str, Any]:
        """校验游戏包"""
        return self.upload_manager.validate_game_package(file_path)

    # ==================== 审核监控 ====================

    def submit_review(
        self,
        app_id: str,
        package_version: str,
        changelog: str = ""
    ) -> ReviewInfo:
        """
        提交审核

        Args:
            app_id: 应用ID
            package_version: 包版本
            changelog: 变更日志

        Returns:
            ReviewInfo
        """
        self._ensure_authenticated()
        return self.review_monitor.submit_for_review(
            app_id=app_id,
            package_version=package_version,
            changelog=changelog
        )

    def wait_for_review(
        self,
        app_id: str,
        check_interval: int = 300,
        max_wait_time: int = 7200
    ) -> ReviewInfo:
        """
        等待审核完成

        Args:
            app_id: 应用ID
            check_interval: 检查间隔（秒）
            max_wait_time: 最大等待时间（秒）

        Returns:
            ReviewInfo
        """
        self._ensure_authenticated()
        return self.review_monitor.wait_for_review(
            app_id=app_id,
            check_interval=check_interval,
            max_wait_time=max_wait_time
        )

    def get_review_status(self, app_id: str) -> ReviewInfo:
        """获取审核状态"""
        self._ensure_authenticated()
        return self.review_monitor.get_review_status(app_id)

    # ==================== 广告位 ====================

    def apply_ad_slots(self, app_id: str, slot_types: list = None) -> list:
        """
        申请广告位

        Args:
            app_id: 应用ID
            slot_types: 广告位类型列表

        Returns:
            AdSlotInfo列表
        """
        self._ensure_authenticated()
        return self.review_monitor.apply_for_ad_slots(
            app_id=app_id,
            ad_slot_types=slot_types
        )

    def get_ad_slots(self, app_id: str) -> list:
        """获取广告位"""
        self._ensure_authenticated()
        return self.review_monitor.get_ad_slots(app_id)

    # ==================== 一键发布 ====================

    def publish_game(
        self,
        title: str,
        description: str,
        category: str,
        package_path: str,
        version: str = "1.0.0",
        changelog: str = "Initial release",
        on_progress: Callable[[Dict], None] = None
    ) -> Dict[str, Any]:
        """
        一键发布游戏

        完整流程：创建应用 -> 上传包 -> 提交审核 -> 等待审核 -> 申请广告位

        Args:
            title: 游戏标题
            description: 游戏描述
            category: 游戏分类
            package_path: 游戏包路径
            version: 版本号
            changelog: 变更日志
            on_progress: 进度回调

        Returns:
            发布结果
        """
        self._ensure_authenticated()

        result = {
            "success": False,
            "steps": []
        }

        def report_progress(step: str, status: str, data: Any = None):
            logger.info(f"[{step}] {status}")
            if on_progress:
                on_progress({"step": step, "status": status, "data": data})
            result["steps"].append({"step": step, "status": status, "data": data})

        try:
            # Step 1: 检查或创建应用
            report_progress("app_check", "checking")
            app = self.find_app(title)

            if not app:
                report_progress("app_create", "creating")
                app = self.create_app(title, description, category)
                report_progress("app_create", "created", {"app_id": app.app_id})
            else:
                report_progress("app_check", "found", {"app_id": app.app_id})

            app_id = app.app_id

            # Step 2: 上传游戏包
            report_progress("upload", "uploading")

            def upload_progress(progress: UploadProgress):
                if on_progress:
                    on_progress({
                        "step": "upload",
                        "status": "uploading",
                        "progress": progress.progress_percent
                    })

            upload_result = self.upload_game_package(
                app_id=app_id,
                file_path=package_path,
                version=version,
                on_progress=upload_progress
            )
            report_progress("upload", "completed", upload_result)

            # Step 3: 提交审核
            report_progress("review_submit", "submitting")
            review_info = self.submit_review(
                app_id=app_id,
                package_version=version,
                changelog=changelog
            )
            report_progress("review_submit", "submitted")

            # Step 4: 等待审核
            report_progress("review_wait", "waiting")

            def review_callback(app_id: str, info: ReviewInfo):
                report_progress("review_status", info.status)

            final_review = self.wait_for_review(
                app_id=app_id,
                on_progress=review_callback
            )

            if final_review.status == "approved":
                report_progress("review", "approved")

                # Step 5: 申请广告位
                report_progress("ad_slots", "applying")
                ad_slots = self.apply_ad_slots(app_id)
                report_progress("ad_slots", "completed", {"count": len(ad_slots)})

                result["success"] = True
                result["app_id"] = app_id
                result["ad_slots"] = [
                    {"type": slot.ad_slot_type, "id": slot.ad_slot_id}
                    for slot in ad_slots
                ]
            else:
                report_progress("review", "rejected", {
                    "reasons": final_review.rejection_reasons
                })
                result["rejection_reasons"] = final_review.rejection_reasons

        except Exception as e:
            report_progress("error", str(e))
            result["error"] = str(e)

        return result

    # ==================== 辅助方法 ====================

    def _ensure_authenticated(self):
        """确保已授权"""
        if not self._is_authenticated:
            raise TikTokIntegratorError(
                "未授权，请先调用 get_authorization_url() 获取授权URL，"
                "然后调用 handle_authorization_callback() 完成授权"
            )

        # 刷新token
        self.refresh_token_if_needed()

    def is_authenticated(self) -> bool:
        """检查是否已授权"""
        return self._is_authenticated

    def get_review_report(self, app_id: str) -> Dict[str, Any]:
        """获取审核报告"""
        self._ensure_authenticated()
        return self.review_monitor.generate_review_report(app_id)

    def export_app_ids(self, output_path: str) -> bool:
        """导出AppID列表"""
        self._ensure_authenticated()
        return self.app_manager.export_app_ids(output_path)


def main():
    """主函数"""
    print("=" * 60)
    print("TikTok Developer API Integrator")
    print("TikTok开发者API集成器")
    print("=" * 60)
    print()

    integrator = TikTokDevIntegrator()

    # 检查是否已授权
    if not integrator.is_authenticated():
        print("尚未授权，请按以下步骤操作:")
        print()
        print("1. 获取授权URL:")
        auth_url = integrator.get_authorization_url()
        print(f"   {auth_url}")
        print()
        print("2. 在浏览器中打开URL并授权")
        print()
        print("3. 授权后，复制回调URL中的code参数")
        print()
        code = input("请输入授权码 (code): ")
        print()
        print("4. 完成授权...")
        integrator.handle_authorization_callback(code)
        print()
        print("授权成功!")
        print()

    # 显示菜单
    while True:
        print("请选择操作:")
        print("1. 创建应用")
        print("2. 获取应用列表")
        print("3. 上传游戏包")
        print("4. 提交审核")
        print("5. 申请广告位")
        print("6. 一键发布")
        print("7. 退出")
        print()

        choice = input("请输入选项 (1-7): ").strip()

        if choice == "7":
            break


if __name__ == "__main__":
    main()
