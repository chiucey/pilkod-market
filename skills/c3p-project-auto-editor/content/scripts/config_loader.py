"""
Construct3 C3P Auto Editor - Configuration Loader
Construct3 C3P项目自动编辑器 - 配置加载器

支持JSON/YAML格式的配置文件加载与验证
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

# 配置日志
logger = logging.getLogger('C3PConfigLoader')


@dataclass
class EditorConfig:
    """编辑器配置"""
    # 基础信息
    game_name: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0.0"

    # 美术资源
    app_icon: str = ""
    background: str = ""
    sprites: Dict[str, str] = field(default_factory=dict)

    # 游戏平衡
    click_reward: int = 1
    upgrade_cost_base: int = 10
    difficulty: float = 1.0
    coin_rate: int = 1
    ad_frequency: int = 60

    # 广告配置
    tiktok_app_id: str = ""
    tiktok_rewarded_id: str = ""
    tiktok_interstitial_id: str = ""
    admob_app_id: str = ""
    admob_rewarded_id: str = ""

    # 导出配置
    package_name: str = ""
    bundle_id: str = ""
    orientation: str = "portrait"
    min_sdk: int = 21

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "basic_info": {
                "game_name": self.game_name,
                "description": self.description,
                "author": self.author,
                "version": self.version
            },
            "assets": {
                "app_icon": self.app_icon,
                "background": self.background,
                "sprites": self.sprites
            },
            "game_balance": {
                "click_reward": self.click_reward,
                "upgrade_cost_base": self.upgrade_cost_base,
                "difficulty": self.difficulty,
                "coin_rate": self.coin_rate,
                "ad_frequency": self.ad_frequency
            },
            "advertising": {
                "tiktok_app_id": self.tiktok_app_id,
                "tiktok_rewarded_id": self.tiktok_rewarded_id,
                "tiktok_interstitial_id": self.tiktok_interstitial_id,
                "admob_app_id": self.admob_app_id,
                "admob_rewarded_id": self.admob_rewarded_id
            },
            "export": {
                "package_name": self.package_name,
                "bundle_id": self.bundle_id,
                "orientation": self.orientation,
                "min_sdk": self.min_sdk
            }
        }


class ConfigLoaderError(Exception):
    """配置加载错误"""
    pass


class ConfigValidationError(Exception):
    """配置验证错误"""
    pass


class C3PConfigLoader:
    """C3P编辑器配置加载器"""

    # 配置默认值
    DEFAULTS = {
        "version": "1.0.0",
        "orientation": "portrait",
        "min_sdk": 21,
        "click_reward": 1,
        "upgrade_cost_base": 10,
        "difficulty": 1.0,
        "coin_rate": 1,
        "ad_frequency": 60
    }

    def __init__(self):
        self.config: Optional[EditorConfig] = None
        self.raw_config: Dict = {}

    def load_from_file(self, config_path: str) -> EditorConfig:
        """
        从文件加载配置

        Args:
            config_path: 配置文件路径

        Returns:
            EditorConfig对象

        Raises:
            ConfigLoaderError: 加载失败
            ConfigValidationError: 验证失败
        """
        if not os.path.exists(config_path):
            raise ConfigLoaderError(f"配置文件不存在: {config_path}")

        ext = os.path.splitext(config_path)[1].lower()

        try:
            if ext in ['.json', '.jsonc']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.raw_config = json.load(f)
            elif ext in ['.yaml', '.yml']:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.raw_config = yaml.safe_load(f)
            else:
                raise ConfigLoaderError(f"不支持的配置文件格式: {ext}")

            self.config = self._parse_config(self.raw_config)
            self._validate_config(self.config)

            logger.info(f"配置加载成功: {config_path}")
            return self.config

        except json.JSONDecodeError as e:
            raise ConfigLoaderError(f"JSON解析失败: {e}")
        except yaml.YAMLError as e:
            raise ConfigLoaderError(f"YAML解析失败: {e}")
        except Exception as e:
            raise ConfigLoaderError(f"配置加载失败: {e}")

    def load_from_dict(self, config_dict: Dict) -> EditorConfig:
        """
        从字典加载配置

        Args:
            config_dict: 配置字典

        Returns:
            EditorConfig对象
        """
        self.raw_config = config_dict
        self.config = self._parse_config(config_dict)
        self._validate_config(self.config)

        logger.info("配置加载成功（字典）")
        return self.config

    def _parse_config(self, raw: Dict) -> EditorConfig:
        """解析配置字典"""
        config = EditorConfig()

        # 基础信息
        basic = raw.get('basic_info', {})
        config.game_name = basic.get('game_name', self.DEFAULTS.get('game_name', ''))
        config.description = basic.get('description', '')
        config.author = basic.get('author', '')
        config.version = basic.get('version', self.DEFAULTS['version'])

        # 美术资源
        assets = raw.get('assets', {})
        config.app_icon = assets.get('app_icon', '')
        config.background = assets.get('background', '')
        config.sprites = assets.get('sprites', {})

        # 游戏平衡
        balance = raw.get('game_balance', {})
        config.click_reward = balance.get('click_reward', self.DEFAULTS['click_reward'])
        config.upgrade_cost_base = balance.get('upgrade_cost_base', self.DEFAULTS['upgrade_cost_base'])
        config.difficulty = balance.get('difficulty', self.DEFAULTS['difficulty'])
        config.coin_rate = balance.get('coin_rate', self.DEFAULTS['coin_rate'])
        config.ad_frequency = balance.get('ad_frequency', self.DEFAULTS['ad_frequency'])

        # 广告配置
        ads = raw.get('advertising', {})
        config.tiktok_app_id = ads.get('tiktok_app_id', '')
        config.tiktok_rewarded_id = ads.get('tiktok_rewarded_id', '')
        config.tiktok_interstitial_id = ads.get('tiktok_interstitial_id', '')
        config.admob_app_id = ads.get('admob_app_id', '')
        config.admob_rewarded_id = ads.get('admob_rewarded_id', '')

        # 导出配置
        export = raw.get('export', {})
        config.package_name = export.get('package_name', '')
        config.bundle_id = export.get('bundle_id', '')
        config.orientation = export.get('orientation', self.DEFAULTS['orientation'])
        config.min_sdk = export.get('min_sdk', self.DEFAULTS['min_sdk'])

        return config

    def _validate_config(self, config: EditorConfig) -> bool:
        """
        验证配置

        Args:
            config: EditorConfig对象

        Returns:
            bool: 验证是否通过

        Raises:
            ConfigValidationError: 验证失败
        """
        errors = []

        # 验证游戏名称
        if not config.game_name:
            errors.append("游戏名称不能为空")

        # 验证数值范围
        if config.click_reward < 1 or config.click_reward > 99999:
            errors.append("点击奖励范围: 1-99999")

        if config.upgrade_cost_base < 10 or config.upgrade_cost_base > 9999999:
            errors.append("升级价格范围: 10-9999999")

        if config.difficulty < 0.1 or config.difficulty > 10.0:
            errors.append("难度系数范围: 0.1-10.0")

        if config.coin_rate < 1 or config.coin_rate > 9999:
            errors.append("金币产出范围: 1-9999")

        if config.ad_frequency < 1 or config.ad_frequency > 999:
            errors.append("广告频次范围: 1-999")

        # 验证方向
        if config.orientation not in ['portrait', 'landscape', 'any']:
            errors.append("屏幕方向: portrait/landscape/any")

        # 验证SDK版本
        if config.min_sdk < 16 or config.min_sdk > 33:
            errors.append("最低SDK版本: 16-33")

        if errors:
            error_msg = "配置验证失败:\n" + "\n".join(f"  - {e}" for e in errors)
            raise ConfigValidationError(error_msg)

        return True

    def save_to_file(self, config: EditorConfig, output_path: str,
                   format: str = 'json') -> bool:
        """
        保存配置到文件

        Args:
            config: EditorConfig对象
            output_path: 输出路径
            format: 保存格式 (json/yaml)

        Returns:
            bool: 保存是否成功
        """
        try:
            data = config.to_dict()

            if format == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == 'yaml':
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
            else:
                raise ConfigLoaderError(f"不支持的格式: {format}")

            logger.info(f"配置已保存: {output_path}")
            return True

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def generate_template(self, output_path: str, format: str = 'json') -> bool:
        """
        生成配置模板

        Args:
            output_path: 输出路径
            format: 模板格式

        Returns:
            bool: 生成是否成功
        """
        template = {
            "basic_info": {
                "game_name": "My Awesome Game",
                "description": "A fun casual game",
                "author": "Your Name",
                "version": "1.0.0"
            },
            "assets": {
                "app_icon": "/path/to/icon.png",
                "background": "/path/to/background.png",
                "sprites": {
                    "player": "/path/to/player.png",
                    "enemy": "/path/to/enemy.png",
                    "coin": "/path/to/coin.png"
                }
            },
            "game_balance": {
                "click_reward": 10,
                "upgrade_cost_base": 50,
                "difficulty": 1.0,
                "coin_rate": 2,
                "ad_frequency": 60
            },
            "advertising": {
                "tiktok_app_id": "",
                "tiktok_rewarded_id": "",
                "tiktok_interstitial_id": "",
                "admob_app_id": "",
                "admob_rewarded_id": ""
            },
            "export": {
                "package_name": "com.gamestudio.myawesomesgame",
                "bundle_id": "com.gamestudio.myawesomesgame",
                "orientation": "portrait",
                "min_sdk": 21
            }
        }

        return self.save_to_file(self._dict_to_config(template), output_path, format)

    def _dict_to_config(self, data: Dict) -> EditorConfig:
        """将字典转换为EditorConfig"""
        config = EditorConfig()
        config.game_name = data.get('basic_info', {}).get('game_name', '')
        config.description = data.get('basic_info', {}).get('description', '')
        config.author = data.get('basic_info', {}).get('author', '')
        config.version = data.get('basic_info', {}).get('version', '1.0.0')
        config.app_icon = data.get('assets', {}).get('app_icon', '')
        config.background = data.get('assets', {}).get('background', '')
        config.sprites = data.get('assets', {}).get('sprites', {})
        config.click_reward = data.get('game_balance', {}).get('click_reward', 1)
        config.upgrade_cost_base = data.get('game_balance', {}).get('upgrade_cost_base', 10)
        config.difficulty = data.get('game_balance', {}).get('difficulty', 1.0)
        config.coin_rate = data.get('game_balance', {}).get('coin_rate', 1)
        config.ad_frequency = data.get('game_balance', {}).get('ad_frequency', 60)
        config.tiktok_app_id = data.get('advertising', {}).get('tiktok_app_id', '')
        config.tiktok_rewarded_id = data.get('advertising', {}).get('tiktok_rewarded_id', '')
        config.tiktok_interstitial_id = data.get('advertising', {}).get('tiktok_interstitial_id', '')
        config.admob_app_id = data.get('advertising', {}).get('admob_app_id', '')
        config.admob_rewarded_id = data.get('advertising', {}).get('admob_rewarded_id', '')
        config.package_name = data.get('export', {}).get('package_name', '')
        config.bundle_id = data.get('export', {}).get('bundle_id', '')
        config.orientation = data.get('export', {}).get('orientation', 'portrait')
        config.min_sdk = data.get('export', {}).get('min_sdk', 21)
        return config


def main():
    """主函数测试"""
    print("=" * 60)
    print("C3P Config Loader Test")
    print("C3P配置加载器测试")
    print("=" * 60)
    print()

    loader = C3PConfigLoader()

    # 生成配置模板
    print("生成配置模板:")
    template = loader.generate_template('config_template.json', 'json')
    print(f"模板已生成: config_template.json")

    # 加载配置示例
    print("""
    from config_loader import C3PConfigLoader

    loader = C3PConfigLoader()

    # 从文件加载
    config = loader.load_from_file('game_config.json')

    # 从字典加载
    config = loader.load_from_dict({
        "basic_info": {
            "game_name": "My Game",
            "version": "1.0.0"
        },
        "game_balance": {
            "click_reward": 10
        }
    })

    # 保存配置
    loader.save_to_file(config, 'output.json', 'json')
    """)


if __name__ == "__main__":
    main()
