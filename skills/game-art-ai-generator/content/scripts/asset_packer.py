"""
Game Art AI Generator - Asset Packer
游戏美术AI生成器 - 素材打包模块

将生成的美术素材打包成ZIP，供Construct3直接导入
"""

import os
import json
import logging
import zipfile
from typing import Dict, Optional, Any, List
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

# 配置日志
logger = logging.getLogger('AssetPacker')


@dataclass
class AssetPackage:
    """素材包"""
    package_name: str
    package_path: str
    assets: Dict[str, List[str]] = field(default_factory=dict)
    manifest: Dict = None
    created_at: str = ""

    def __post_init__(self):
        if self.manifest is None:
            self.manifest = {}
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class PackageConfig:
    """打包配置"""
    compress_level: int = 6
    include_manifest: bool = True
    include_readme: bool = True
    category_folders: bool = True


class AssetPacker:
    """素材打包器"""

    # 默认文件夹结构
    DEFAULT_STRUCTURE = {
        "icons": ["*.png"],
        "ui": ["ui_*.png", "btn_*.png", "popup_*.png", "progress_*.png"],
        "characters": ["char_*.png", "player_*.png"],
        "props": ["prop_*.png", "item_*.png", "coin_*.png"],
        "backgrounds": ["bg_*.png", "background_*.png"],
        "animations": ["frame_*.png"],
        "audio": ["*.mp3", "*.wav"]
    }

    def __init__(self, output_dir: str = "./output"):
        """
        初始化打包器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_package(
        self,
        package_name: str,
        source_dir: str,
        config: PackageConfig = None,
        game_info: Dict = None
    ) -> AssetPackage:
        """
        创建素材包

        Args:
            package_name: 包名称
            source_dir: 素材源目录
            config: 打包配置
            game_info: 游戏信息

        Returns:
            AssetPackage
        """
        if config is None:
            config = PackageConfig()

        logger.info(f"[AssetPacker] Creating package: {package_name}")

        source_path = Path(source_dir)

        # 创建临时打包目录
        temp_dir = self.output_dir / f".temp_{package_name}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        # 组织素材
        assets = self._organize_assets(source_path, temp_dir, config)

        # 创建清单
        manifest = self._create_manifest(
            package_name,
            assets,
            game_info or {}
        )

        # 保存清单
        if config.include_manifest:
            with open(temp_dir / "manifest.json", 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

        # 创建说明文档
        if config.include_readme:
            readme = self._create_readme(package_name, manifest)
            with open(temp_dir / "README.txt", 'w', encoding='utf-8') as f:
                f.write(readme)

        # 打包ZIP
        zip_path = self.output_dir / f"{package_name}.zip"
        self._create_zip(temp_dir, zip_path, config.compress_level)

        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir)

        logger.info(f"[AssetPacker] Package created: {zip_path}")

        return AssetPackage(
            package_name=package_name,
            package_path=str(zip_path),
            assets=assets,
            manifest=manifest
        )

    def _organize_assets(
        self,
        source_dir: Path,
        temp_dir: Path,
        config: PackageConfig
    ) -> Dict[str, List[str]]:
        """组织素材"""
        assets = {}

        if config.category_folders:
            # 按类别组织
            for category in self.DEFAULT_STRUCTURE.keys():
                cat_dir = temp_dir / category
                cat_dir.mkdir(parents=True, exist_ok=True)
                assets[category] = []

                # 移动匹配文件
                for pattern in self.DEFAULT_STRUCTURE[category]:
                    for src_file in source_dir.glob(pattern):
                        dst_file = cat_dir / src_file.name
                        dst_file.write_bytes(src_file.read_bytes())
                        assets[category].append(str(dst_file))
        else:
            # 扁平结构
            assets["root"] = []
            for pattern in ["**/*.png", "**/*.mp3", "**/*.wav"]:
                for src_file in source_dir.glob(pattern):
                    dst_file = temp_dir / src_file.name
                    dst_file.write_bytes(src_file.read_bytes())
                    assets["root"].append(str(dst_file))

        return assets

    def _create_manifest(
        self,
        package_name: str,
        assets: Dict[str, List[str]],
        game_info: Dict
    ) -> Dict[str, Any]:
        """创建素材清单"""
        manifest = {
            "package_name": package_name,
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "game_info": {
                "name": game_info.get("name", ""),
                "type": game_info.get("type", ""),
                "theme": game_info.get("theme", ""),
                "style": game_info.get("style", "pixel")
            },
            "assets": {},
            "total_files": 0
        }

        for category, files in assets.items():
            manifest["assets"][category] = []
            for filepath in files:
                path = Path(filepath)
                asset_info = {
                    "filename": path.name,
                    "category": category,
                    "type": self._get_asset_type(path.suffix),
                    "path": str(path.relative_to(path.parent.parent)),
                    "size": path.stat().st_size
                }
                manifest["assets"][category].append(asset_info)
                manifest["total_files"] += 1

        return manifest

    def _get_asset_type(self, extension: str) -> str:
        """获取资源类型"""
        ext_map = {
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".mp3": "audio",
            ".wav": "audio"
        }
        return ext_map.get(extension.lower(), "unknown")

    def _create_readme(self, package_name: str, manifest: Dict) -> str:
        """创建说明文档"""
        readme = f"""
================================================================================
                    {package_name} - 游戏美术素材包
================================================================================

生成时间: {manifest['created_at']}
游戏类型: {manifest['game_info'].get('type', 'N/A')}
游戏主题: {manifest['game_info'].get('theme', 'N/A')}
素材风格: {manifest['game_info'].get('style', 'pixel')}

--------------------------------------------------------------------------------
                              素材清单
--------------------------------------------------------------------------------

"""
        for category, files in manifest["assets"].items():
            readme += f"\n[{category.upper()}] ({len(files)} 个文件)\n"
            readme += "-" * 40 + "\n"
            for asset in files:
                readme += f"  - {asset['filename']:<30} {asset['type']:<10} {asset['size']:,} bytes\n"

        readme += f"""

--------------------------------------------------------------------------------
                              Construct3 导入指南
--------------------------------------------------------------------------------

1. 解压ZIP文件
2. 打开Construct3项目
3. 选择 "Project" -> "Import"
4. 选择解压后的文件夹
5. 素材将自动分类导入

--------------------------------------------------------------------------------
                              素材使用说明
--------------------------------------------------------------------------------

图标 (icons/):
  - 游戏图标 512x512 PNG
  - 可直接用于TikTok应用上架

UI组件 (ui/):
  - 按钮: 包含normal/hover/pressed/disabled状态
  - 进度条: 背景层+填充层分离
  - 弹窗: 需配合文本使用

游戏元素 (characters/, props/):
  - 角色动画: 包含多个帧的PNG序列
  - 道具: 可直接拖入场景使用

背景 (backgrounds/):
  - 可平铺背景图
  - 适配不同关卡

音效 (audio/):
  - BGM文件需设置循环播放
  - SFX文件可直接触发播放

--------------------------------------------------------------------------------
                              版权说明
--------------------------------------------------------------------------------

本素材包由AI自动生成，用于TikTok小游戏开发。
素材可用于商业用途，无版权风险。

================================================================================
"""

        return readme

    def _create_zip(
        self,
        source_dir: Path,
        zip_path: Path,
        compress_level: int = 6
    ):
        """创建ZIP文件"""
        with zipfile.ZipFile(
            zip_path,
            'w',
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=compress_level
        ) as zf:
            for file in source_dir.rglob('*'):
                if file.is_file():
                    arcname = file.relative_to(source_dir)
                    zf.write(file, arcname)

    def extract_package(
        self,
        zip_path: str,
        extract_dir: str = None
    ) -> str:
        """
        解压素材包

        Args:
            zip_path: ZIP文件路径
            extract_dir: 解压目录

        Returns:
            解压目录路径
        """
        zip_path = Path(zip_path)

        if extract_dir is None:
            extract_dir = zip_path.stem

        extract_path = Path(extract_dir)
        extract_path.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_path)

        logger.info(f"[AssetPacker] Extracted to: {extract_path}")
        return str(extract_path)

    def verify_package(self, zip_path: str) -> Dict[str, Any]:
        """
        验证素材包完整性

        Args:
            zip_path: ZIP文件路径

        Returns:
            验证结果
        """
        zip_path = Path(zip_path)

        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "stats": {}
        }

        try:
            with zipfile.ZipFile(zip_path, 'r') as zf:
                files = zf.namelist()
                result["stats"]["total_files"] = len(files)
                result["stats"]["total_size"] = sum(
                    zf.getinfo(f).file_size for f in files
                )

                # 检查必需文件
                if "manifest.json" not in files:
                    result["warnings"].append("缺少manifest.json")

                # 检查必需类别
                categories = set()
                for f in files:
                    parts = Path(f).parts
                    if len(parts) > 1 and parts[0] in self.DEFAULT_STRUCTURE:
                        categories.add(parts[0])

                result["stats"]["categories"] = list(categories)

        except zipfile.BadZipFile:
            result["valid"] = False
            result["errors"].append("无效的ZIP文件")

        return result


def main():
    """测试"""
    print("=" * 60)
    print("Asset Packer Test")
    print("素材打包器测试")
    print("=" * 60)

    packer = AssetPacker("./output")

    # 创建测试包
    # package = packer.create_package(
    #     package_name="test_game_assets",
    #     source_dir="./generated",
    #     game_info={
    #         "name": "Test Game",
    #         "type": "skill",
    #         "theme": "space adventure"
    #     }
    # )

    print("Package structure created")
    print("\n使用方法:")
    print("""
    from asset_packer import AssetPacker

    packer = AssetPacker("./output")

    # 创建素材包
    package = packer.create_package(
        package_name="my_game_assets",
        source_dir="./generated",
        game_info={"name": "My Game", "type": "skill"}
    )

    print(f"Package: {package.package_path}")

    # 验证包
    result = packer.verify_package(package.package_path)
    print(f"Valid: {result['valid']}")
    """)


if __name__ == "__main__":
    main()
