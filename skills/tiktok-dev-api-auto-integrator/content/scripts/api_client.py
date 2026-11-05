"""
TikTok Developer API - API Client
TikTok开发者API客户端

封装TikTok OpenAPI所有接口调用
支持自动Token管理、错误处理、重试机制
"""

import os
import time
import json
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from auth import TikTokOAuth, OAuthTokens, AuthError

# 配置日志
logger = logging.getLogger('TikTokAPIClient')


@dataclass
class APIResponse:
    """API响应封装"""
    success: bool
    data: Dict = field(default_factory=dict)
    error_code: str = ""
    error_message: str = ""
    http_status: int = 0

    def is_success(self) -> bool:
        return self.success and self.http_status == 200

    def get_data(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


class APIError(Exception):
    """API错误"""
    def __init__(self, message: str, error_code: str = "", response: Dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response or {}


class RateLimitError(Exception):
    """限流错误"""
    pass


class TikTokAPIClient:
    """TikTok OpenAPI客户端"""

    # API基础URL
    BASE_URL = "https://open.tiktokapis.com/v2"

    # 默认请求头
    DEFAULT_HEADERS = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    def __init__(self, oauth: TikTokOAuth = None,
                 client_key: str = None,
                 client_secret: str = None,
                 redirect_uri: str = None,
                 config_dir: str = None,
                 access_token: str = None):
        """
        初始化API客户端

        Args:
            oauth: OAuth管理器实例（优先使用）
            client_key: Client Key（无oauth时使用）
            client_secret: Client Secret
            redirect_uri: 回调地址
            config_dir: 配置目录
            access_token: 直接传入Access Token
        """
        # 优先使用传入的OAuth实例
        if oauth:
            self.oauth = oauth
        elif access_token:
            # 创建简单的OAuth实例用于token管理
            self.oauth = None
            self._access_token = access_token
        else:
            # 创建新的OAuth实例
            if not all([client_key, client_secret, redirect_uri]):
                raise ValueError("需要提供oauth实例或client_key/client_secret/redirect_uri")
            self.oauth = TikTokOAuth(client_key, client_secret, redirect_uri, config_dir)
            self._access_token = None

        # 请求会话
        self.session = self._create_session()

        # 请求计数
        self.request_count = 0
        self.last_request_time = 0

        # 速率限制配置
        self.rate_limit = 100  # 每分钟请求数
        self.rate_window = 60   # 时间窗口（秒）

    def _create_session(self) -> requests.Session:
        """创建带重试机制的请求会话"""
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _get_access_token(self) -> str:
        """获取访问令牌"""
        if self.oauth:
            return self.oauth.ensure_valid_token()
        elif hasattr(self, '_access_token') and self._access_token:
            return self._access_token
        else:
            raise AuthError("未授权，请先进行OAuth授权")

    def _build_headers(self, additional_headers: Dict = None) -> Dict:
        """构建请求头"""
        headers = self.DEFAULT_HEADERS.copy()

        # 添加访问令牌
        access_token = self._get_access_token()
        headers["Authorization"] = f"Bearer {access_token}"

        # 合并额外头
        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _rate_limit_wait(self):
        """速率限制等待"""
        current_time = time.time()

        # 重置计数器
        if current_time - self.last_request_time >= self.rate_window:
            self.request_count = 0
            self.last_request_time = current_time

        # 检查是否超限
        if self.request_count >= self.rate_limit:
            wait_time = self.rate_window - (current_time - self.last_request_time)
            if wait_time > 0:
                logger.info(f"触发速率限制，等待{wait_time:.1f}秒")
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()

        self.request_count += 1

    def _make_request(self, method: str, endpoint: str,
                     data: Dict = None,
                     params: Dict = None,
                     headers: Dict = None,
                     retry_count: int = 0) -> APIResponse:
        """
        发起API请求

        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            params: URL参数
            headers: 请求头
            retry_count: 重试次数

        Returns:
            APIResponse响应对象
        """
        # 速率限制
        self._rate_limit_wait()

        # 构建URL
        url = f"{self.BASE_URL}{endpoint}"

        # 构建请求头
        request_headers = self._build_headers(headers)

        try:
            logger.debug(f"API请求: {method} {url}")

            if method.upper() == "GET":
                response = self.session.get(url, headers=request_headers,
                                           params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=request_headers,
                                           json=data, params=params, timeout=60)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=request_headers,
                                           json=data, params=params, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=request_headers,
                                                params=params, timeout=30)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")

            # 解析响应
            return self._parse_response(response)

        except requests.exceptions.Timeout:
            if retry_count < 3:
                logger.warning(f"请求超时，重试第{retry_count + 1}次")
                return self._make_request(method, endpoint, data, params,
                                        headers, retry_count + 1)
            return APIResponse(False, {}, "TIMEOUT", "请求超时", 0)

        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {e}")
            return APIResponse(False, {}, "REQUEST_ERROR", str(e), 0)

    def _parse_response(self, response: requests.Response) -> APIResponse:
        """解析API响应"""
        try:
            response_data = response.json()
        except:
            response_data = {}

        http_status = response.status_code

        # 检查HTTP状态码
        if http_status == 200:
            return APIResponse(True, response_data, "", "", http_status)

        elif http_status == 401:
            return APIResponse(False, response_data, "UNAUTHORIZED",
                             response_data.get("error_description", "未授权"), http_status)

        elif http_status == 403:
            return APIResponse(False, response_data, "FORBIDDEN",
                             response_data.get("error_description", "权限不足"), http_status)

        elif http_status == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            logger.warning(f"触发速率限制，等待{retry_after}秒")
            time.sleep(retry_after)
            raise RateLimitError("API速率限制")

        elif http_status >= 500:
            return APIResponse(False, response_data, "SERVER_ERROR",
                             response_data.get("error_description", "服务器错误"), http_status)

        else:
            error_code = response_data.get("error_code", "")
            error_msg = response_data.get("error_description", "")
            return APIResponse(False, response_data, error_code, error_msg, http_status)

    # ==================== MiniApp API ====================

    def create_miniapp(self, title: str, category: str = None,
                       description: str = None,
                       language: str = "en") -> APIResponse:
        """
        创建MiniApp应用

        Args:
            title: 应用标题
            category: 应用分类
            description: 应用描述
            language: 应用语言

        Returns:
            APIResponse
        """
        data = {
            "title": title,
            "category": category or "casual_game",
            "description": description or title,
            "language": language
        }

        return self._make_request("POST", "/miniapp/v2/app/create/", data=data)

    def get_app_list(self, page_size: int = 20,
                    page_token: str = None) -> APIResponse:
        """
        获取应用列表

        Args:
            page_size: 每页数量
            page_token: 分页令牌

        Returns:
            APIResponse
        """
        params = {"max_results": page_size}
        if page_token:
            params["page_token"] = page_token

        return self._make_request("GET", "/miniapp/v2/app/list/", params=params)

    def get_app_info(self, app_id: str) -> APIResponse:
        """
        获取应用详情

        Args:
            app_id: 应用ID

        Returns:
            APIResponse
        """
        return self._make_request("GET", f"/miniapp/v2/app/info/",
                                 params={"app_id": app_id})

    def update_app_info(self, app_id: str, title: str = None,
                       description: str = None,
                       category: str = None,
                       screenshots: List[str] = None,
                       icon_url: str = None) -> APIResponse:
        """
        更新应用信息

        Args:
            app_id: 应用ID
            title: 应用标题
            description: 应用描述
            category: 应用分类
            screenshots: 截图URL列表
            icon_url: 图标URL

        Returns:
            APIResponse
        """
        data = {"app_id": app_id}

        if title:
            data["title"] = title
        if description:
            data["description"] = description
        if category:
            data["category"] = category
        if screenshots:
            data["screenshots"] = screenshots
        if icon_url:
            data["icon_url"] = icon_url

        return self._make_request("POST", "/miniapp/v2/app/update/", data=data)

    def upload_package(self, app_id: str, package_url: str,
                      version: str = None,
                      changelog: str = None) -> APIResponse:
        """
        上传游戏包

        Args:
            app_id: 应用ID
            package_url: 包URL
            version: 版本号
            changelog: 更新日志

        Returns:
            APIResponse
        """
        data = {
            "app_id": app_id,
            "package_url": package_url,
            "version": version or "1.0.0",
            "changelog": changelog or "Initial release"
        }

        return self._make_request("POST", "/miniapp/v2/app/package/upload/",
                                 data=data)

    def submit_for_review(self, app_id: str,
                         package_version: str = None) -> APIResponse:
        """
        提交审核

        Args:
            app_id: 应用ID
            package_version: 包版本

        Returns:
            APIResponse
        """
        data = {"app_id": app_id}
        if package_version:
            data["package_version"] = package_version

        return self._make_request("POST", "/miniapp/v2/app/package/submit/",
                                 data=data)

    def get_review_status(self, app_id: str) -> APIResponse:
        """
        获取审核状态

        Args:
            app_id: 应用ID

        Returns:
            APIResponse
        """
        return self._make_request("GET", "/miniapp/v2/app/review/status/",
                                 params={"app_id": app_id})

    # ==================== Ad Unit API ====================

    def create_ad_unit(self, app_id: str, ad_type: str,
                      name: str = None,
                      reward_amount: int = None) -> APIResponse:
        """
        创建广告位

        Args:
            app_id: 应用ID
            ad_type: 广告类型 (rewarded_video/interstitial)
            name: 广告位名称
            reward_amount: 激励奖励数量

        Returns:
            APIResponse
        """
        data = {
            "app_id": app_id,
            "ad_type": ad_type
        }

        if name:
            data["name"] = name
        if reward_amount:
            data["reward_amount"] = reward_amount

        return self._make_request("POST", "/miniapp/v2/app/ad/create/", data=data)

    def get_ad_unit_list(self, app_id: str) -> APIResponse:
        """
        获取广告位列表

        Args:
            app_id: 应用ID

        Returns:
            APIResponse
        """
        return self._make_request("GET", "/miniapp/v2/app/ad/list/",
                                 params={"app_id": app_id})

    def get_ad_unit_info(self, app_id: str, ad_unit_id: str) -> APIResponse:
        """
        获取广告位详情

        Args:
            app_id: 应用ID
            ad_unit_id: 广告位ID

        Returns:
            APIResponse
        """
        params = {
            "app_id": app_id,
            "ad_unit_id": ad_unit_id
        }
        return self._make_request("GET", "/miniapp/v2/app/ad/info/", params=params)

    # ==================== Media Upload API ====================

    def upload_media(self, file_path: str, media_type: str = "image") -> APIResponse:
        """
        上传媒体文件（图片、图标等）

        Args:
            file_path: 文件路径
            media_type: 媒体类型 (image/audio)

        Returns:
            APIResponse
        """
        url = f"{self.BASE_URL}/media/upload/"

        headers = self._build_headers()
        headers["Content-Type"] = "multipart/form-data"

        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'media_type': media_type}

            response = self.session.post(
                url, headers=headers, files=files, data=data, timeout=120
            )

        return self._parse_response(response)


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok API Client Test")
    print("TikTok API客户端测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from auth import TikTokOAuth
    from api_client import TikTokAPIClient

    # 初始化OAuth
    oauth = TikTokOAuth(client_key, client_secret, redirect_uri)

    # 初始化API客户端
    client = TikTokAPIClient(oauth)

    # 创建应用
    result = client.create_miniapp("My Game", "casual_game")
    if result.is_success():
        app_id = result.get_data("app_id")
        print(f"应用创建成功: {app_id}")

    # 获取应用列表
    result = client.get_app_list()
    apps = result.get_data("apps", [])

    # 创建广告位
    result = client.create_ad_unit(app_id, "rewarded_video", "激励视频")
    if result.is_success():
        ad_unit_id = result.get_data("ad_unit_id")
        print(f"广告位创建成功: {ad_unit_id}")

    # 上传媒体
    result = client.upload_media("/path/to/icon.png", "image")
    icon_url = result.get_data("url")
    """)


if __name__ == "__main__":
    main()
