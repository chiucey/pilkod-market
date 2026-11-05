"""
TikTok Developer API - OAuth Authentication Module
TikTok开发者API - OAuth授权认证模块

支持OAuth2.0授权流程、Token自动刷新、权限管理
"""

import os
import time
import json
import logging
import secrets
import hashlib
import base64
from typing import Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path

import requests

# 配置日志
logger = logging.getLogger('TikTokAuth')


@dataclass
class OAuthTokens:
    """OAuth令牌数据结构"""
    access_token: str = ""
    refresh_token: str = ""
    expires_in: int = 0
    token_type: str = "Bearer"
    scope: str = ""
    open_id: str = ""
    expires_at: float = 0  # Unix时间戳

    def is_expired(self) -> bool:
        """检查令牌是否过期"""
        if self.expires_at == 0:
            return False
        return time.time() >= self.expires_at

    def is_refresh_needed(self) -> bool:
        """检查是否需要刷新令牌（提前5分钟）"""
        if self.expires_at == 0:
            return True
        return time.time() >= (self.expires_at - 300)

    def to_dict(self) -> Dict:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expires_in": self.expires_in,
            "token_type": self.token_type,
            "scope": self.scope,
            "open_id": self.open_id,
            "expires_at": self.expires_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'OAuthTokens':
        tokens = cls()
        tokens.access_token = data.get("access_token", "")
        tokens.refresh_token = data.get("refresh_token", "")
        tokens.expires_in = data.get("expires_in", 0)
        tokens.token_type = data.get("token_type", "Bearer")
        tokens.scope = data.get("scope", "")
        tokens.open_id = data.get("open_id", "")

        # 计算过期时间
        if "expires_at" in data:
            tokens.expires_at = data["expires_at"]
        elif tokens.expires_in > 0:
            tokens.expires_at = time.time() + tokens.expires_in

        return tokens


class AuthError(Exception):
    """认证错误"""
    pass


class TokenRefreshError(Exception):
    """令牌刷新错误"""
    pass


class TikTokOAuth:
    """TikTok OAuth认证管理器"""

    # TikTok OAuth端点
    AUTH_URL = "https://www.tiktok.com/v2/auth/authorize/"
    TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
    REFRESH_URL = "https://open.tiktokapis.com/v2/oauth/token/refresh/"

    # 权限范围
    SCOPES = {
        "miniapp.read": "读取MiniApp信息",
        "miniapp.write": "写入MiniApp信息",
        "miniapp.upload": "上传游戏包",
        "ad.read": "读取广告信息",
        "ad.write": "写入广告配置"
    }

    def __init__(self, client_key: str, client_secret: str,
                 redirect_uri: str, config_dir: str = None):
        """
        初始化OAuth管理器

        Args:
            client_key: TikTok应用Client Key
            client_secret: TikTok应用Client Secret
            redirect_uri: OAuth回调地址
            config_dir: 配置存储目录
        """
        self.client_key = client_key
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        # 配置目录
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".tiktok_auth"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Token文件路径
        self.token_file = self.config_dir / "tokens.json"
        self.state_file = self.config_dir / "state.txt"

        # 当前令牌
        self.tokens: Optional[OAuthTokens] = None

        # 加载已有令牌
        self._load_tokens()

    def _generate_state(self) -> str:
        """生成随机state参数"""
        return secrets.token_urlsafe(32)

    def _generate_code_verifier(self) -> str:
        """生成PKCE code_verifier"""
        return base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        ).rstrip(b'=').decode('ascii')

    def _generate_code_challenge(self, code_verifier: str) -> str:
        """生成PKCE code_challenge"""
        digest = hashlib.sha256(code_verifier.encode('ascii')).digest()
        return base64.urlsafe_b64encode(
            digest
        ).rstrip(b'=').decode('ascii')

    def get_authorization_url(self, scopes: list = None,
                             state: str = None,
                             code_challenge: bool = True) -> Tuple[str, str, str]:
        """
        获取授权URL

        Args:
            scopes: 权限列表
            state: 状态参数
            code_challenge: 是否使用PKCE

        Returns:
            Tuple[授权URL, state, code_verifier]
        """
        # 生成参数
        if state is None:
            state = self._generate_state()

        code_verifier = None
        code_challenge_method = None

        if code_challenge:
            code_verifier = self._generate_code_verifier()
            code_challenge_value = self._generate_code_challenge(code_verifier)
            code_challenge_method = "S256"
        else:
            code_challenge_value = None

        # 默认权限
        if scopes is None:
            scopes = ["miniapp.read", "miniapp.write", "miniapp.upload"]

        # 构建URL参数
        params = {
            "client_key": self.client_key,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state
        }

        if code_challenge and code_challenge_value:
            params["code_challenge"] = code_challenge_value
            params["code_challenge_method"] = code_challenge_method

        # 构建URL
        from urllib.parse import urlencode
        auth_url = self.AUTH_URL + "?" + urlencode(params)

        # 保存state和code_verifier
        self._save_state(state, code_verifier)

        return auth_url, state, code_verifier

    def _save_state(self, state: str, code_verifier: str = None):
        """保存state和code_verifier"""
        with open(self.state_file, 'w') as f:
            json.dump({
                "state": state,
                "code_verifier": code_verifier,
                "created_at": time.time()
            }, f)

    def _load_state(self) -> Dict:
        """加载state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {}

    def exchange_code_for_token(self, code: str, state: str = None) -> OAuthTokens:
        """
        用授权码交换访问令牌

        Args:
            code: 授权码
            state: 状态参数（用于验证）

        Returns:
            OAuthTokens令牌对象
        """
        # 加载保存的state和code_verifier
        saved_state = self._load_state()
        code_verifier = saved_state.get("code_verifier")

        # 验证state
        if state and saved_state.get("state") != state:
            logger.warning("State不匹配，可能存在安全风险")

        # 构建请求
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }

        if code_verifier:
            data["code_verifier"] = code_verifier

        try:
            response = requests.post(self.TOKEN_URL, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            logger.info("Token获取成功")

            # 解析令牌
            self.tokens = OAuthTokens.from_dict(token_data)
            self._save_tokens()

            return self.tokens

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            logger.error(f"Token获取失败: {error_data}")
            raise AuthError(f"Token获取失败: {error_data.get('error_description', str(e))}")
        except Exception as e:
            logger.error(f"Token获取异常: {e}")
            raise AuthError(f"Token获取异常: {e}")

    def refresh_access_token(self) -> OAuthTokens:
        """
        刷新访问令牌

        Returns:
            OAuthTokens新令牌对象
        """
        if not self.tokens or not self.tokens.refresh_token:
            raise TokenRefreshError("无可用的refresh_token")

        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.tokens.refresh_token
        }

        try:
            response = requests.post(self.TOKEN_URL, data=data, timeout=30)
            response.raise_for_status()
            token_data = response.json()

            logger.info("Token刷新成功")

            # 解析新令牌
            self.tokens = OAuthTokens.from_dict(token_data)
            self._save_tokens()

            return self.tokens

        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            logger.error(f"Token刷新失败: {error_data}")
            raise TokenRefreshError(f"Token刷新失败: {error_data.get('error_description', str(e))}")
        except Exception as e:
            logger.error(f"Token刷新异常: {e}")
            raise TokenRefreshError(f"Token刷新异常: {e}")

    def ensure_valid_token(self) -> str:
        """
        确保获取有效的访问令牌

        Returns:
            有效的access_token
        """
        # 检查是否已有令牌
        if not self.tokens:
            self._load_tokens()

        # 检查是否需要刷新
        if self.tokens and self.tokens.is_refresh_needed():
            try:
                self.refresh_access_token()
            except TokenRefreshError as e:
                logger.error(f"自动刷新Token失败: {e}")
                raise AuthError(f"需要重新授权: {e}")

        # 检查令牌是否过期
        if self.tokens and self.tokens.is_expired():
            raise AuthError("Token已过期，需要重新授权")

        if not self.tokens or not self.tokens.access_token:
            raise AuthError("未授权，请先进行OAuth授权")

        return self.tokens.access_token

    def set_tokens(self, tokens: OAuthTokens):
        """
        设置令牌（用于从外部加载）

        Args:
            tokens: OAuthTokens对象
        """
        self.tokens = tokens
        self._save_tokens()

    def revoke_authorization(self) -> bool:
        """
        撤销授权

        Returns:
            是否成功
        """
        if not self.tokens or not self.tokens.access_token:
            return True

        # 注意：TikTok API可能不支持此端点
        url = "https://open.tiktokapis.com/v2/oauth/token/revoke/"
        data = {
            "client_key": self.client_key,
            "client_secret": self.client_secret,
            "token": self.tokens.access_token
        }

        try:
            response = requests.post(url, data=data, timeout=30)
            self._clear_tokens()
            logger.info("授权已撤销")
            return True
        except Exception as e:
            logger.error(f"撤销授权失败: {e}")
            return False

    def _save_tokens(self):
        """保存令牌到文件"""
        if self.tokens:
            with open(self.token_file, 'w') as f:
                json.dump(self.tokens.to_dict(), f, indent=2)
            logger.debug("Token已保存")

    def _load_tokens(self):
        """从文件加载令牌"""
        if self.token_file.exists():
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                self.tokens = OAuthTokens.from_dict(data)
                logger.debug("Token已加载")
            except Exception as e:
                logger.warning(f"加载Token失败: {e}")
                self.tokens = None

    def _clear_tokens(self):
        """清除令牌"""
        self.tokens = None
        if self.token_file.exists():
            self.token_file.unlink()
        if self.state_file.exists():
            self.state_file.unlink()

    def get_account_info(self) -> Dict:
        """
        获取账号信息

        Returns:
            账号信息字典
        """
        access_token = self.ensure_valid_token()

        url = "https://open.tiktokapis.com/v2/user/info/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def is_authorized(self) -> bool:
        """检查是否已授权"""
        if not self.tokens or not self.tokens.access_token:
            return False
        if self.tokens.is_expired():
            return False
        return True


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok OAuth Authentication Module Test")
    print("TikTok OAuth认证模块测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from auth import TikTokOAuth

    # 初始化
    oauth = TikTokOAuth(
        client_key="your_client_key",
        client_secret="your_client_secret",
        redirect_uri="https://yourapp.com/callback"
    )

    # 获取授权URL
    auth_url, state, code_verifier = oauth.get_authorization_url()
    print(f"请访问以下URL进行授权: {auth_url}")

    # 用户授权后，用返回的code交换token
    tokens = oauth.exchange_code_for_token(code)

    # 获取有效token（自动刷新）
    access_token = oauth.ensure_valid_token()

    # 获取账号信息
    account_info = oauth.get_account_info()
    """)


if __name__ == "__main__":
    main()
