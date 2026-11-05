# -*- coding: utf-8 -*-
"""
配置加载模块
Configuration Loader Module

负责加载和管理配置文件
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器类"""
    
    DEFAULT_CONFIG = {
        'news_sources': [
            {
                'name': '新浪新闻',
                'url': 'https://rss.sina.com.cn/news/china/focus15.xml',
                'category': 'domestic',
                'enabled': True
            },
            {
                'name': '网易新闻',
                'url': 'https://news.163.com/rss/news.xml',
                'category': 'domestic',
                'enabled': True
            },
            {
                'name': '腾讯新闻',
                'url': 'https://news.qq.com/newsrss.php',
                'category': 'domestic',
                'enabled': True
            }
        ],
        'output': {
            'format': 'markdown',
            'include_weather': True,
            'include_quote': True,
            'include_history': True,
            'max_news_per_category': 10
        },
        'quotes': {
            'enabled': True,
            'source': 'local'
        },
        'weather': {
            'enabled': True,
            'location': '北京'
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为 config/settings.yaml
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # 默认配置文件路径
            base_dir = Path(__file__).parent.parent
            self.config_path = base_dir / 'config' / 'settings.yaml'
        
        self.config = None
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML解析错误
        """
        if not self.config_path.exists():
            # 如果配置文件不存在，创建默认配置
            self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            
            # 合并默认配置
            config = self.DEFAULT_CONFIG.copy()
            if self.config:
                self._deep_merge(config, self.config)
            
            self.config = config
            return self.config
            
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"配置文件解析错误: {e}")
        except Exception as e:
            raise Exception(f"加载配置文件失败: {e}")
    
    def _create_default_config(self) -> None:
        """创建默认配置文件"""
        # 确保目录存在
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入默认配置
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, allow_unicode=True, default_flow_style=False)
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """
        深度合并字典
        
        Args:
            base: 基础字典
            override: 覆盖字典
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置键，支持点号分隔的路径
            default: 默认值
            
        Returns:
            配置值
        """
        if self.config is None:
            self.load()
        
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典，默认为当前配置
        """
        if config is None:
            config = self.config
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)
