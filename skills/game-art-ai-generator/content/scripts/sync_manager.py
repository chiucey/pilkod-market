"""
Game Art AI Generator - Sync Manager
游戏美术AI生成器 - 协同同步模块

与c3p-project-auto-editor和tiktok-dev-api-auto-integrator无缝协同
"""

import os
import sys
import logging
import json
import shutil
from typing import Dict, Optional, Any, List, Callable
from dataclasses import dataclass
from pathlib import Path

# 配置日志
logger = logging.getLogger('SyncManager')


@dataclass
class SyncResult:
    """同步结果"""
    success: bool
    target: str = ""
    message: str = ""
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class C3PConfig:
    """C3P项目配置"""
    project_path: str = ""
    auto_inject: bool = True
    backup_original: bool = True


@dataclass
class TikTokConfig:
    """TikTok配置"""
    app_title: str = ""
    app_description: str = ""
    category: str = "casual_game"


class SyncManager:
    """同步管理器"""

    # Construct3素材类型映射
    C3P_ASSET_MAPPING = {
        "icons": "ProjectFiles/icons",
        "ui": "ProjectFiles/sprites/ui",
        "characters": "ProjectFiles/sprites/characters",
        "props": "ProjectFiles/sprites/objects",
        "backgrounds": "ProjectFiles backgrounds",
        "animations": "ProjectFiles/animations",
        "audio": "ProjectFiles/audio"
    }

    def __init__(
        self,
        asset_package_path: str = None,
        workspace_dir: str = "./workspace"
    ):
        """
        初始化同步管理器

        Args:
            asset_package_path: 素材包路径
            workspace_dir: 工作区目录
        """
        self.asset_package_path = asset_package_path
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.c3p_config = C3PConfig()
        self.tiktok_config = TikTokConfig()

        # 同步状态
        self._sync_history: List[SyncResult] = []

    def set_asset_package(self, package_path: str):
        """设置素材包路径"""
        self.asset_package_path = package_path
        logger.info(f"[SyncManager] Asset package set: {package_path}")

    def sync_to_c3p(
        self,
        package_path: str = None,
        c3p_project_path: str = None,
        asset_mapping: Dict = None
    ) -> SyncResult:
        """
        同步素材到Construct3项目

        Args:
            package_path: 素材包路径
            c3p_project_path: C3P项目路径
            asset_mapping: 素材映射配置

        Returns:
            SyncResult
        """
        package_path = package_path or self.asset_package_path
        c3p_project_path = c3p_project_path or self.c3p_config.project_path

        if not package_path:
            return SyncResult(
                success=False,
                target="c3p",
                message="No asset package specified"
            )

        logger.info(f"[SyncManager] Syncing to C3P: {c3p_project_path}")

        try:
            # 解压素材包
            from asset_packer import AssetPacker
            packer = AssetPacker(str(self.workspace_dir))

            if package_path.endswith('.zip'):
                extract_dir = packer.extract_package(
                    package_path,
                    str(self.workspace_dir / "assets")
                )
            else:
                extract_dir = package_path

            # 如果提供了C3P项目路径，执行注入
            if c3p_project_path and Path(c3p_project_path).exists():
                self._inject_to_c3p(
                    extract_dir,
                    c3p_project_path,
                    asset_mapping or self.C3P_ASSET_MAPPING
                )

                # 备份原项目
                if self.c3p_config.backup_original:
                    self._backup_project(c3p_project_path)

            result = SyncResult(
                success=True,
                target="c3p",
                message=f"Assets synced to C3P project",
                details={
                    "source": extract_dir,
                    "target": c3p_project_path,
                    "extracted_files": len(list(Path(extract_dir).rglob('*.*')))
                }
            )

            self._sync_history.append(result)
            return result

        except Exception as e:
            logger.error(f"[SyncManager] C3P sync failed: {e}")
            result = SyncResult(
                success=False,
                target="c3p",
                message=str(e)
            )
            self._sync_history.append(result)
            return result

    def _inject_to_c3p(
        self,
        assets_dir: str,
        c3p_path: str,
        asset_mapping: Dict
    ):
        """注入素材到C3P项目"""
        logger.info(f"[SyncManager] Injecting assets to C3P")

        assets_path = Path(assets_dir)

        # 构建c3p-editor调用命令
        # 这里假设c3p-project-auto-editor插件可用
        c3p_script = self.workspace_dir / "c3p_inject.py"

        # 生成注入脚本
        inject_config = {
            "c3p_path": c3p_path,
            "assets_mapping": {}
        }

        for category, c3p_folder in asset_mapping.items():
            category_dir = assets_path / category
            if category_dir.exists():
                inject_config["assets_mapping"][category] = {
                    "source_dir": str(category_dir),
                    "target_folder": c3p_folder,
                    "files": [f.name for f in category_dir.glob('*')]
                }

        # 保存配置
        config_path = self.workspace_dir / "c3p_inject_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(inject_config, f, indent=2, ensure_ascii=False)

        logger.info(f"[SyncManager] C3P injection config saved: {config_path}")

        return str(config_path)

    def _backup_project(self, project_path: str):
        """备份原项目"""
        project_path = Path(project_path)
        backup_path = project_path.with_suffix('.c3p.backup')

        if not backup_path.exists():
            shutil.copy2(project_path, backup_path)
            logger.info(f"[SyncManager] Project backed up: {backup_path}")

    def prepare_for_tiktok(
        self,
        asset_package_path: str = None,
        game_title: str = "",
        game_description: str = ""
    ) -> Dict[str, Any]:
        """
        准备TikTok上线所需素材

        Args:
            asset_package_path: 素材包路径
            game_title: 游戏标题
            game_description: 游戏描述

        Returns:
            TikTok上线配置
        """
        package_path = asset_package_path or self.asset_package_path

        logger.info(f"[SyncManager] Preparing for TikTok")

        # 提取并检查素材
        from asset_packer import AssetPacker
        packer = AssetPacker(str(self.workspace_dir))

        extract_dir = packer.extract_package(
            package_path,
            str(self.workspace_dir / "tiktok_ready")
        )

        # 验证素材完整性
        extract_path = Path(extract_dir)
        validation = self._validate_for_tiktok(extract_path)

        # 生成TikTok配置
        tiktok_config = {
            "game_title": game_title or self.tiktok_config.app_title,
            "game_description": game_description or self.tiktok_config.app_description,
            "assets_path": extract_dir,
            "validation": validation,
            "required_files": {
                "icon": "icons/icon_1.png",
                "package": self._create_game_package(extract_path)
            }
        }

        # 保存配置
        config_path = self.workspace_dir / "tiktok_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(tiktok_config, f, indent=2, ensure_ascii=False)

        return tiktok_config

    def _validate_for_tiktok(self, assets_dir: Path) -> Dict[str, Any]:
        """验证TikTok素材"""
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "checks": {}
        }

        # 检查图标
        icons_dir = assets_dir / "icons"
        if icons_dir.exists():
            icons = list(icons_dir.glob("*.png"))
            validation["checks"]["icon"] = {
                "found": len(icons) > 0,
                "count": len(icons)
            }
            if len(icons) == 0:
                validation["warnings"].append("No icon found in icons/")
        else:
            validation["checks"]["icon"] = {"found": False}
            validation["errors"].append("Missing icons/ folder")

        # 检查UI
        ui_dir = assets_dir / "ui"
        validation["checks"]["ui"] = {
            "found": ui_dir.exists(),
            "has_buttons": len(list(ui_dir.glob("btn_*.png"))) > 0 if ui_dir.exists() else False
        }

        # 检查音效
        audio_dir = assets_dir / "audio"
        validation["checks"]["audio"] = {
            "found": audio_dir.exists(),
            "has_bgm": len(list(audio_dir.glob("bgm_*.mp3"))) > 0 if audio_dir.exists() else False
        }

        return validation

    def _create_game_package(self, assets_dir: Path) -> str:
        """创建TikTok可用的游戏包"""
        import zipfile

        package_path = assets_dir.parent / "tiktok_game.zip"

        # 创建包含所有游戏素材的ZIP
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 确保包含index.html
            if (assets_dir / "index.html").exists():
                zf.write(assets_dir / "index.html", "index.html")
            else:
                # 创建默认index.html
                default_html = self._generate_default_html(assets_dir)
                zf.writestr("index.html", default_html)

            # 添加所有素材
            for ext in ['*.png', '*.jpg', '*.mp3', '*.wav']:
                for file in assets_dir.rglob(ext):
                    arcname = file.relative_to(assets_dir)
                    zf.write(file, arcname)

        logger.info(f"[SyncManager] TikTok package created: {package_path}")
        return str(package_path)

    def _generate_default_html(self, assets_dir: Path) -> str:
        """生成默认HTML入口文件"""
        icons = list((assets_dir / "icons").glob("*.png")) if (assets_dir / "icons").exists() else []
        icon_path = f"icons/{icons[0].name}" if icons else ""

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Game</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #1A1A2E;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: Arial, sans-serif;
        }}
        #game-container {{
            width: 100%;
            max-width: 500px;
            text-align: center;
            color: #fff;
        }}
        h1 {{ margin-bottom: 20px; font-size: 24px; }}
        p {{ margin-bottom: 30px; opacity: 0.8; }}
    </style>
</head>
<body>
    <div id="game-container">
        <h1>Game</h1>
        <p>Loading...</p>
    </div>
</body>
</html>
"""

    def generate_pipeline_script(
        self,
        c3p_project_path: str = None,
        tiktok_app_info: Dict = None
    ) -> str:
        """
        生成完整流水线脚本

        Args:
            c3p_project_path: C3P项目路径
            tiktok_app_info: TikTok应用信息

        Returns:
            脚本路径
        """
        logger.info(f"[SyncManager] Generating pipeline script")

        pipeline_config = {
            "step_1_art_generation": {
                "status": "completed" if self.asset_package_path else "pending",
                "input": {
                    "game_type": "skill",
                    "theme_keywords": "..."
                }
            },
            "step_2_c3p_injection": {
                "status": "pending",
                "c3p_project": c3p_project_path or "",
                "asset_package": self.asset_package_path or ""
            },
            "step_3_tiktok_publish": {
                "status": "pending",
                "app_title": tiktok_app_info.get("title") if tiktok_app_info else "",
                "app_description": tiktok_app_info.get("description") if tiktok_app_info else ""
            }
        }

        config_path = self.workspace_dir / "pipeline_config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(pipeline_config, f, indent=2, ensure_ascii=False)

        return str(config_path)

    def get_sync_history(self) -> List[SyncResult]:
        """获取同步历史"""
        return self._sync_history


def main():
    """测试"""
    print("=" * 60)
    print("Sync Manager Test")
    print("协同同步管理器测试")
    print("=" * 60)

    manager = SyncManager()

    # 示例：准备TikTok上线
    config = manager.prepare_for_tiktok(
        asset_package_path="./output/game_assets.zip",
        game_title="My Awesome Game",
        game_description="A fun casual game"
    )

    print("\nTikTok Config:")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()
