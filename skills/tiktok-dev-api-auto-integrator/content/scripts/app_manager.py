"""
TikTok Developer API - App Manager
TikTok开发者API - 应用管理器

封装应用创建、配置、更新等完整流程
"""

import os
import json
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from api_client import TikTokAPIClient, APIResponse, APIError

# 配置日志
logger = logging.getLogger('TikTokAppManager')


@dataclass
class MiniAppInfo:
    """MiniApp信息"""
    app_id: str = ""
    title: str = ""
    description: str = ""
    category: str = ""
    language: str = "en"
    status: str = ""
    icon_url: str = ""
    screenshots: List[str] = field(default_factory=list)
    package_url: str = ""
    package_version: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "app_id": self.app_id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "language": self.language,
            "status": self.status,
            "icon_url": self.icon_url,
            "screenshots": self.screenshots,
            "package_url": self.package_url,
            "package_version": self.package_version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MiniAppInfo':
        info = cls()
        info.app_id = data.get("app_id", "")
        info.title = data.get("title", "")
        info.description = data.get("description", "")
        info.category = data.get("category", "")
        info.language = data.get("language", "en")
        info.status = data.get("status", "")
        info.icon_url = data.get("icon_url", "")
        info.screenshots = data.get("screenshots", [])
        info.package_url = data.get("package_url", "")
        info.package_version = data.get("package_version", "")
        info.created_at = data.get("created_at", "")
        info.updated_at = data.get("updated_at", "")
        return info


@dataclass
class AppCreationConfig:
    """应用创建配置"""
    title: str = ""
    description: str = ""
    category: str = "casual_game"
    language: str = "en"
    icon_path: str = ""
    screenshots_paths: List[str] = field(default_factory=list)


class AppManagerError(Exception):
    """应用管理错误"""
    pass


class TikTokAppManager:
    """TikTok MiniApp管理器"""

    # 应用状态映射
    STATUS_MAP = {
        "pending": "待审核",
        "in_review": "审核中",
        "approved": "已通过",
        "rejected": "已驳回",
        "online": "已上线"
    }

    # 支持的分类
    CATEGORIES = [
        "casual_game",
        "puzzle_game",
        "action_game",
        "arcade_game",
        "strategy_game",
        "simulation_game",
        "sports_game",
        "music_game",
        "educational_game",
        "other"
    ]

    def __init__(self, api_client: TikTokAPIClient, config_dir: str = None):
        """
        初始化应用管理器

        Args:
            api_client: TikTok API客户端
            config_dir: 配置目录
        """
        self.client = api_client

        # 配置目录
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".tiktok_apps"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # 应用缓存
        self._app_cache: Dict[str, MiniAppInfo] = {}

    def create_app(self, config: AppCreationConfig) -> MiniAppInfo:
        """
        创建MiniApp应用

        Args:
            config: 应用创建配置

        Returns:
            MiniAppInfo应用信息

        Raises:
            AppManagerError: 创建失败
        """
        logger.info(f"创建MiniApp: {config.title}")

        # 调用API创建应用
        response = self.client.create_miniapp(
            title=config.title,
            category=config.category,
            description=config.description,
            language=config.language
        )

        if not response.is_success():
            raise AppManagerError(f"创建应用失败: {response.error_message}")

        # 解析响应
        app_data = response.get_data("app", {})
        app_info = MiniAppInfo.from_dict(app_data)

        # 保存到缓存
        self._app_cache[app_info.app_id] = app_info

        # 保存配置
        self._save_app_config(app_info, config)

        logger.info(f"应用创建成功: {app_info.app_id}")
        return app_info

    def get_app_info(self, app_id: str, use_cache: bool = True) -> MiniAppInfo:
        """
        获取应用信息

        Args:
            app_id: 应用ID
            use_cache: 是否使用缓存

        Returns:
            MiniAppInfo应用信息
        """
        # 检查缓存
        if use_cache and app_id in self._app_cache:
            return self._app_cache[app_id]

        logger.info(f"获取应用信息: {app_id}")

        response = self.client.get_app_info(app_id)

        if not response.is_success():
            raise AppManagerError(f"获取应用信息失败: {response.error_message}")

        app_data = response.get_data("app", {})
        app_info = MiniAppInfo.from_dict(app_data)

        # 更新缓存
        self._app_cache[app_id] = app_info

        return app_info

    def update_app_info(self, app_id: str,
                        title: str = None,
                        description: str = None,
                        category: str = None,
                        icon_url: str = None,
                        screenshots: List[str] = None) -> MiniAppInfo:
        """
        更新应用信息

        Args:
            app_id: 应用ID
            title: 应用标题
            description: 应用描述
            category: 应用分类
            icon_url: 图标URL
            screenshots: 截图URL列表

        Returns:
            MiniAppInfo更新后的应用信息
        """
        logger.info(f"更新应用信息: {app_id}")

        response = self.client.update_app_info(
            app_id=app_id,
            title=title,
            description=description,
            category=category,
            icon_url=icon_url,
            screenshots=screenshots
        )

        if not response.is_success():
            raise AppManagerError(f"更新应用信息失败: {response.error_message}")

        # 重新获取最新信息
        return self.get_app_info(app_id, use_cache=False)

    def upload_and_update_icon(self, app_id: str, icon_path: str) -> str:
        """
        上传图标并更新应用

        Args:
            app_id: 应用ID
            icon_path: 图标文件路径

        Returns:
            图标URL
        """
        if not os.path.exists(icon_path):
            raise AppManagerError(f"图标文件不存在: {icon_path}")

        logger.info(f"上传图标: {icon_path}")

        # 上传图标
        response = self.client.upload_media(icon_path, "image")

        if not response.is_success():
            raise AppManagerError(f"图标上传失败: {response.error_message}")

        icon_url = response.get_data("url", "")

        # 更新应用信息
        self.update_app_info(app_id, icon_url=icon_url)

        logger.info(f"图标更新成功: {icon_url}")
        return icon_url

    def upload_and_update_screenshots(self, app_id: str,
                                     screenshot_paths: List[str]) -> List[str]:
        """
        上传截图并更新应用

        Args:
            app_id: 应用ID
            screenshot_paths: 截图文件路径列表

        Returns:
            截图URL列表
        """
        screenshot_urls = []

        for path in screenshot_paths:
            if not os.path.exists(path):
                logger.warning(f"截图文件不存在: {path}")
                continue

            logger.info(f"上传截图: {path}")

            response = self.client.upload_media(path, "image")

            if response.is_success():
                url = response.get_data("url", "")
                screenshot_urls.append(url)

        if screenshot_urls:
            self.update_app_info(app_id, screenshots=screenshot_urls)

        logger.info(f"截图更新成功: {len(screenshot_urls)}张")
        return screenshot_urls

    def get_app_list(self, page_size: int = 50) -> List[MiniAppInfo]:
        """
        获取应用列表

        Args:
            page_size: 每页数量

        Returns:
            应用信息列表
        """
        logger.info("获取应用列表")

        response = self.client.get_app_list(page_size=page_size)

        if not response.is_success():
            raise AppManagerError(f"获取应用列表失败: {response.error_message}")

        apps_data = response.get_data("apps", [])
        apps = [MiniAppInfo.from_dict(app) for app in apps_data]

        # 更新缓存
        for app in apps:
            self._app_cache[app.app_id] = app

        return apps

    def find_app_by_title(self, title: str) -> Optional[MiniAppInfo]:
        """
        根据标题查找应用

        Args:
            title: 应用标题

        Returns:
            匹配的应用，未找到返回None
        """
        apps = self.get_app_list()
        for app in apps:
            if app.title.lower() == title.lower():
                return app
        return None

    def get_app_status_display(self, app_id: str) -> str:
        """
        获取应用状态（中文显示）

        Args:
            app_id: 应用ID

        Returns:
            状态中文描述
        """
        app_info = self.get_app_info(app_id)
        return self.STATUS_MAP.get(app_info.status, app_info.status)

    def _save_app_config(self, app_info: MiniAppInfo, config: AppCreationConfig):
        """保存应用配置"""
        config_file = self.config_dir / f"{app_info.app_id}.json"

        data = {
            "app_info": app_info.to_dict(),
            "creation_config": {
                "title": config.title,
                "description": config.description,
                "category": config.category,
                "language": config.language,
                "icon_path": config.icon_path,
                "screenshots_paths": config.screenshots_paths
            },
            "saved_at": datetime.now().isoformat()
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.debug(f"配置已保存: {config_file}")

    def load_app_config(self, app_id: str) -> Optional[Dict]:
        """加载应用配置"""
        config_file = self.config_dir / f"{app_id}.json"

        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None

    def export_app_ids(self, output_path: str) -> bool:
        """
        导出所有AppID

        Args:
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        apps = self.get_app_list()

        export_data = {
            "export_time": datetime.now().isoformat(),
            "total": len(apps),
            "apps": [app.to_dict() for app in apps]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        logger.info(f"AppID已导出: {output_path}")
        return True


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok App Manager Test")
    print("TikTok应用管理器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from api_client import TikTokAPIClient
    from app_manager import TikTokAppManager, AppCreationConfig

    # 初始化
    client = TikTokAPIClient(oauth)
    manager = TikTokAppManager(client)

    # 创建应用
    config = AppCreationConfig(
        title="My Awesome Game",
        description="A fun casual game",
        category="casual_game",
        language="en"
    )
    app = manager.create_app(config)
    print(f"应用创建成功: {app.app_id}")

    # 获取应用列表
    apps = manager.get_app_list()
    for app in apps:
        print(f"- {app.title} ({app.app_id}): {app.status}")

    # 更新应用信息
    app = manager.update_app_info(
        app_id,
        description="Updated description"
    )

    # 上传图标
    icon_url = manager.upload_and_update_icon(app_id, "/path/to/icon.png")

    # 根据标题查找
    app = manager.find_app_by_title("My Awesome Game")
    """)


if __name__ == "__main__":
    main()
