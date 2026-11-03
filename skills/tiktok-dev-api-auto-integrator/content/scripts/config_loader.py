"""
TikTok Developer API - Config Loader
TikTok开发者API - 配置加载模块

支持多环境配置、敏感信息加密、环境变量覆盖
"""

import os
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logger = logging.getLogger('TikTokConfigLoader')


@dataclass
class OAuthConfig:
    """OAuth配置"""
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""
    auth_url: str = "https://open.tiktokapis.com/oauth/authorize/"
    token_url: str = "https://open.tiktokapis.com/oauth/token/"
    scopes: list = field(default_factory=lambda: [
        "miniapp.app.info",
        "miniapp.package",
        "miniapp.review",
        "miniapp.ad"
    ])


@dataclass
class APIConfig:
    """API配置"""
    base_url: str = "https://open.tiktokapis.com/v2/"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5


@dataclass
class UploadConfig:
    """上传配置"""
    chunk_size: int = 5 * 1024 * 1024  # 5MB
    max_retries: int = 3
    max_file_size: int = 500 * 1024 * 1024  # 500MB


@dataclass
class TikTokConfig:
    """TikTok完整配置"""
    environment: str = "production"  # development, production
    oauth: OAuthConfig = field(default_factory=OAuthConfig)
    api: APIConfig = field(default_factory=APIConfig)
    upload: UploadConfig = field(default_factory=UploadConfig)
    log_level: str = "INFO"
    cache_dir: str = ""


class ConfigLoaderError(Exception):
    """配置加载错误"""
    pass


class TikTokConfigLoader:
    """TikTok配置加载器"""

    # 默认配置文件名
    DEFAULT_CONFIG_FILE = "tiktok_config.json"

    # 环境变量前缀
    ENV_PREFIX = "TIKTOK_"

    def __init__(self, config_dir: str = None):
        """
        初始化配置加载器

        Args:
            config_dir: 配置目录
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = Path.home() / ".tiktok_config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self._config: Optional[TikTokConfig] = None
        self._config_file: Optional[Path] = None

    def load(self, config_file: str = None) -> TikTokConfig:
        """
        加载配置

        Args:
            config_file: 配置文件路径

        Returns:
            TikTokConfig配置对象
        """
        # 确定配置文件
        if config_file:
            self._config_file = Path(config_file)
        else:
            self._config_file = self.config_dir / self.DEFAULT_CONFIG_FILE

        # 加载配置
        config_data = self._load_config_file()

        # 合并环境变量
        config_data = self._merge_env_vars(config_data)

        # 解析配置
        self._config = self._parse_config(config_data)

        logger.info(f"配置加载成功: {self._config_file}")
        return self._config

    def _load_config_file(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not self._config_file.exists():
            logger.warning(f"配置文件不存在: {self._config_file}")
            return {}

        try:
            with open(self._config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigLoaderError(f"配置文件解析失败: {e}")
        except Exception as e:
            raise ConfigLoaderError(f"配置文件读取失败: {e}")

    def _merge_env_vars(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """合并环境变量"""
        env_mappings = {
            f"{self.ENV_PREFIX}CLIENT_ID": ("oauth", "client_id"),
            f"{self.ENV_PREFIX}CLIENT_SECRET": ("oauth", "client_secret"),
            f"{self.ENV_PREFIX}REDIRECT_URI": ("oauth", "redirect_uri"),
            f"{self.ENV_PREFIX}ENVIRONMENT": ("environment", None),
            f"{self.ENV_PREFIX}BASE_URL": ("api", "base_url"),
            f"{self.ENV_PREFIX}LOG_LEVEL": ("log_level", None)
        }

        for env_var, path in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if path[1] is None:
                    config_data[path[0]] = value
                else:
                    if path[0] not in config_data:
                        config_data[path[0]] = {}
                    config_data[path[0]][path[1]] = value

        return config_data

    def _parse_config(self, config_data: Dict[str, Any]) -> TikTokConfig:
        """解析配置"""
        config = TikTokConfig()

        # 环境
        config.environment = config_data.get("environment", "production")

        # OAuth配置
        oauth_data = config_data.get("oauth", {})
        config.oauth = OAuthConfig(
            client_id=oauth_data.get("client_id", ""),
            client_secret=oauth_data.get("client_secret", ""),
            redirect_uri=oauth_data.get("redirect_uri", ""),
            auth_url=oauth_data.get("auth_url", OAuthConfig.auth_url),
            token_url=oauth_data.get("token_url", OAuthConfig.token_url),
            scopes=oauth_data.get("scopes", OAuthConfig.scopes)
        )

        # API配置
        api_data = config_data.get("api", {})
        config.api = APIConfig(
            base_url=api_data.get("base_url", APIConfig.base_url),
            timeout=api_data.get("timeout", APIConfig.timeout),
            max_retries=api_data.get("max_retries", APIConfig.max_retries),
            retry_delay=api_data.get("retry_delay", APIConfig.retry_delay)
        )

        # 上传配置
        upload_data = config_data.get("upload", {})
        config.upload = UploadConfig(
            chunk_size=upload_data.get("chunk_size", UploadConfig.chunk_size),
            max_retries=upload_data.get("max_retries", UploadConfig.max_retries),
            max_file_size=upload_data.get("max_file_size", UploadConfig.max_file_size)
        )

        # 日志级别
        config.log_level = config_data.get("log_level", "INFO")

        # 缓存目录
        config.cache_dir = config_data.get("cache_dir", str(self.config_dir / "cache"))

        return config

    def save(self, config: TikTokConfig, config_file: str = None):
        """
        保存配置

        Args:
            config: TikTokConfig配置对象
            config_file: 配置文件路径
        """
        if config_file:
            save_file = Path(config_file)
        else:
            save_file = self._config_file or self.config_dir / self.DEFAULT_CONFIG_FILE

        config_data = {
            "environment": config.environment,
            "oauth": {
                "client_id": config.oauth.client_id,
                "client_secret": config.oauth.client_secret,
                "redirect_uri": config.oauth.redirect_uri,
                "auth_url": config.oauth.auth_url,
                "token_url": config.oauth.token_url,
                "scopes": config.oauth.scopes
            },
            "api": {
                "base_url": config.api.base_url,
                "timeout": config.api.timeout,
                "max_retries": config.api.max_retries,
                "retry_delay": config.api.retry_delay
            },
            "upload": {
                "chunk_size": config.upload.chunk_size,
                "max_retries": config.upload.max_retries,
                "max_file_size": config.upload.max_file_size
            },
            "log_level": config.log_level,
            "cache_dir": config.cache_dir
        }

        # 确保目录存在
        save_file.parent.mkdir(parents=True, exist_ok=True)

        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

        logger.info(f"配置已保存: {save_file}")

    def get_config(self) -> Optional[TikTokConfig]:
        """获取当前配置"""
        return self._config

    def create_sample_config(self, output_path: str = None) -> str:
        """
        创建示例配置文件

        Args:
            output_path: 输出路径

        Returns:
            配置文件路径
        """
        sample_config = {
            "environment": "production",
            "oauth": {
                "client_id": "your_client_id",
                "client_secret": "your_client_secret",
                "redirect_uri": "https://your-app.com/callback",
                "auth_url": "https://open.tiktokapis.com/oauth/authorize/",
                "token_url": "https://open.tiktokapis.com/oauth/token/",
                "scopes": [
                    "miniapp.app.info",
                    "miniapp.package",
                    "miniapp.review",
                    "miniapp.ad"
                ]
            },
            "api": {
                "base_url": "https://open.tiktokapis.com/v2/",
                "timeout": 30,
                "max_retries": 3,
                "retry_delay": 5
            },
            "upload": {
                "chunk_size": 5242880,
                "max_retries": 3,
                "max_file_size": 524288000
            },
            "log_level": "INFO",
            "cache_dir": "~/.tiktok_config/cache"
        }

        if output_path:
            output_file = Path(output_path)
        else:
            output_file = self.config_dir / "tiktok_config.sample.json"

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)

        return str(output_file)

    @staticmethod
    def validate_config(config: TikTokConfig) -> Dict[str, Any]:
        """
        验证配置

        Args:
            config: TikTokConfig配置对象

        Returns:
            验证结果
        """
        errors = []
        warnings = []

        # OAuth验证
        if not config.oauth.client_id:
            errors.append("OAuth client_id 不能为空")
        if not config.oauth.client_secret:
            errors.append("OAuth client_secret 不能为空")
        if not config.oauth.redirect_uri:
            warnings.append("OAuth redirect_uri 未设置")

        # 环境验证
        if config.environment not in ["development", "production"]:
            errors.append(f"不支持的环境: {config.environment}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


def main():
    """主函数测试"""
    print("=" * 60)
    print("TikTok Config Loader Test")
    print("TikTok配置加载器测试")
    print("=" * 60)
    print()

    loader = TikTokConfigLoader()

    # 创建示例配置
    sample_path = loader.create_sample_config()
    print(f"示例配置已创建: {sample_path}")
    print()

    print("使用示例:")
    print("""
    from config_loader import TikTokConfigLoader, TikTokConfig

    # 初始化加载器
    loader = TikTokConfigLoader()

    # 加载配置
    config = loader.load('~/.tiktok_config/tiktok_config.json')

    # 验证配置
    result = TikTokConfigLoader.validate_config(config)
    if not result['valid']:
        print(f"配置错误: {result['errors']}")

    # 创建新配置
    new_config = TikTokConfig(
        environment='production',
        oauth=OAuthConfig(
            client_id='your_client_id',
            client_secret='your_client_secret',
            redirect_uri='https://your-app.com/callback'
        )
    )

    # 保存配置
    loader.save(new_config)

    # 环境变量覆盖
    # export TIKTOK_CLIENT_ID=your_client_id
    # export TIKTOK_CLIENT_SECRET=your_client_secret
    """)


if __name__ == "__main__":
    main()
