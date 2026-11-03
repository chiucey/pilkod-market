"""
Construct3 Resource Manager
Construct3资源文件替换管理器

自动化匹配并替换.c3p项目中的图片、音效、图标等资源
保留原文件层级与命名规范，适配游戏加载逻辑
"""

import os
import shutil
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from PIL import Image

# 配置日志
logger = logging.getLogger('C3PResourceManager')


@dataclass
class ResourceInfo:
    """资源信息"""
    original_path: str = ""
    original_name: str = ""
    original_size: int = 0
    original_md5: str = ""
    resource_type: str = ""  # image/audio/font/icon
    file_format: str = ""
    dimensions: Tuple[int, int] = (0, 0)

    def to_dict(self) -> Dict:
        return {
            "path": self.original_path,
            "name": self.original_name,
            "size": self.original_size,
            "md5": self.original_md5,
            "type": self.resource_type,
            "format": self.file_format,
            "dimensions": self.dimensions
        }


@dataclass
class ReplacementRecord:
    """替换记录"""
    original_file: str
    new_file: str
    original_md5: str = ""
    new_md5: str = ""
    replacement_type: str = ""  # direct/referenced/both
    replaced_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "original": self.original_file,
            "new": self.new_file,
            "original_md5": self.original_md5,
            "new_md5": self.new_md5,
            "type": self.replacement_type,
            "replaced_at": self.replaced_at
        }


class ResourceManagerError(Exception):
    """资源管理错误"""
    pass


class C3PResourceManager:
    """Construct3资源管理器"""

    # 支持的图片格式
    IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'}
    # 支持的音频格式
    AUDIO_FORMATS = {'.ogg', '.mp3', '.wav', '.aac', '.m4a'}
    # 支持的字体格式
    FONT_FORMATS = {'.ttf', '.otf', '.woff', '.woff2'}

    # 图片资源类型映射
    IMAGE_TYPE_MAPPING = {
        'icon': ['app_icon', 'icon', 'logo'],
        'background': ['background', 'bg', 'back'],
        'sprite': ['player', 'enemy', 'item', 'coin'],
        'ui': ['button', 'panel', 'dialog']
    }

    def __init__(self, project_root: str):
        """
        初始化资源管理器

        Args:
            project_root: C3P项目解压后的根目录
        """
        self.project_root = project_root
        self.media_path = os.path.join(project_root, 'media')
        self.icons_path = os.path.join(project_root, 'icons')
        self.backup_path = os.path.join(project_root, '.resource_backup')

        self.resources: Dict[str, ResourceInfo] = {}
        self.replacements: List[ReplacementRecord] = []

        os.makedirs(self.backup_path, exist_ok=True)

        # 扫描现有资源
        self._scan_resources()

    def _scan_resources(self):
        """扫描项目资源"""
        logger.info("开始扫描项目资源...")

        if not os.path.exists(self.media_path):
            logger.warning(f"媒体目录不存在: {self.media_path}")
            return

        for root, dirs, files in os.walk(self.media_path):
            for f in files:
                if f.startswith('.'):
                    continue

                ext = os.path.splitext(f)[1].lower()
                if ext not in self.IMAGE_FORMATS | self.AUDIO_FORMATS | self.FONT_FORMATS:
                    continue

                file_path = os.path.join(root, f)
                resource_info = self._get_resource_info(file_path)

                if resource_info:
                    self.resources[f] = resource_info

        logger.info(f"资源扫描完成: {len(self.resources)}个资源文件")

    def _get_resource_info(self, file_path: str) -> Optional[ResourceInfo]:
        """获取资源信息"""
        try:
            info = ResourceInfo()
            info.original_path = file_path
            info.original_name = os.path.basename(file_path)
            info.original_size = os.path.getsize(file_path)
            info.file_format = os.path.splitext(file_path)[1].lower()

            # 计算MD5
            info.original_md5 = self._calculate_md5(file_path)

            # 获取尺寸
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.IMAGE_FORMATS:
                try:
                    with Image.open(file_path) as img:
                        info.dimensions = img.size
                    info.resource_type = 'image'
                except:
                    info.resource_type = 'image'
            elif ext in self.AUDIO_FORMATS:
                info.resource_type = 'audio'
            elif ext in self.FONT_FORMATS:
                info.resource_type = 'font'

            return info

        except Exception as e:
            logger.warning(f"获取资源信息失败: {file_path} - {e}")
            return None

    def _calculate_md5(self, file_path: str) -> str:
        """计算文件MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def find_resource_by_name(self, name_pattern: str, resource_type: str = None) -> List[ResourceInfo]:
        """
        按名称模式查找资源

        Args:
            name_pattern: 名称模式（支持模糊匹配）
            resource_type: 资源类型过滤

        Returns:
            匹配的资源列表
        """
        results = []

        for resource in self.resources.values():
            if resource_type and resource.resource_type != resource_type:
                continue

            if name_pattern.lower() in resource.original_name.lower():
                results.append(resource)

        return results

    def find_resource_by_type(self, resource_type: str) -> List[ResourceInfo]:
        """
        按类型查找资源

        Args:
            resource_type: 资源类型 (icon/background/sprite/ui/audio)

        Returns:
            匹配的资源列表
        """
        results = []

        # 类型关键词映射
        type_keywords = self.IMAGE_TYPE_MAPPING.get(resource_type, [resource_type])

        for resource in self.resources.values():
            if resource.resource_type != 'image':
                continue

            name_lower = resource.original_name.lower()
            if any(kw in name_lower for kw in type_keywords):
                results.append(resource)

        return results

    def replace_resource(self, original_name: str, new_file_path: str,
                        create_backup: bool = True) -> bool:
        """
        替换资源文件

        Args:
            original_name: 原资源名称
            new_file_path: 新资源文件路径
            create_backup: 是否创建备份

        Returns:
            bool: 替换是否成功
        """
        # 查找原资源
        original_info = self.resources.get(original_name)
        if not original_info:
            # 尝试模糊匹配
            matches = self.find_resource_by_name(original_name)
            if matches:
                original_info = matches[0]
            else:
                logger.error(f"未找到资源: {original_name}")
                return False

        original_path = original_info.original_path

        # 验证新文件
        if not os.path.exists(new_file_path):
            logger.error(f"新资源文件不存在: {new_file_path}")
            return False

        # 验证格式
        new_ext = os.path.splitext(new_file_path)[1].lower()
        original_ext = os.path.splitext(original_path)[1].lower()

        if new_ext != original_ext:
            logger.warning(f"格式不一致: {original_ext} -> {new_ext}")

        # 创建备份
        if create_backup:
            backup_file = os.path.join(
                self.backup_path,
                f"{original_name}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
            )
            shutil.copy2(original_path, backup_file)
            logger.info(f"已备份: {backup_file}")

        try:
            # 替换文件
            shutil.copy2(new_file_path, original_path)

            # 记录替换
            new_md5 = self._calculate_md5(new_file_path)
            self.replacements.append(ReplacementRecord(
                original_file=original_path,
                new_file=new_file_path,
                original_md5=original_info.original_md5,
                new_md5=new_md5,
                replacement_type='direct'
            ))

            # 更新资源信息
            original_info.original_size = os.path.getsize(original_path)
            original_info.original_md5 = new_md5

            if new_ext in self.IMAGE_FORMATS:
                try:
                    with Image.open(original_path) as img:
                        original_info.dimensions = img.size
                except:
                    pass

            logger.info(f"资源替换成功: {original_name}")
            return True

        except Exception as e:
            logger.error(f"资源替换失败: {e}")
            return False

    def batch_replace(self, replacements: Dict[str, str]) -> Tuple[int, int]:
        """
        批量替换资源

        Args:
            replacements: {原名称: 新文件路径} 字典

        Returns:
            Tuple[成功数量, 失败数量]
        """
        success = 0
        failed = 0

        for original, new in replacements.items():
            if self.replace_resource(original, new):
                success += 1
            else:
                failed += 1

        return success, failed

    def replace_by_type(self, resource_type: str, new_file_path: str) -> bool:
        """
        按类型替换资源（替换该类型第一个资源）

        Args:
            resource_type: 资源类型
            new_file_path: 新资源文件路径

        Returns:
            bool: 替换是否成功
        """
        resources = self.find_resource_by_type(resource_type)

        if not resources:
            logger.error(f"未找到类型为{resource_type}的资源")
            return False

        return self.replace_resource(resources[0].original_name, new_file_path)

    def replace_app_icon(self, new_icon_path: str) -> bool:
        """
        替换应用图标

        Args:
            new_icon_path: 新图标文件路径

        Returns:
            bool: 替换是否成功
        """
        # 查找icons目录
        if not os.path.exists(self.icons_path):
            os.makedirs(self.icons_path, exist_ok=True)

        # 查找现有图标
        icon_files = []
        for f in os.listdir(self.icons_path):
            if f.startswith('icon') or f.endswith('.png'):
                icon_files.append(f)

        if icon_files:
            # 替换第一个图标
            icon_path = os.path.join(self.icons_path, icon_files[0])
            try:
                shutil.copy2(new_icon_path, icon_path)

                self.replacements.append(ReplacementRecord(
                    original_file=icon_path,
                    new_file=new_icon_path,
                    replacement_type='direct'
                ))

                logger.info(f"应用图标替换成功: {icon_path}")
                return True

            except Exception as e:
                logger.error(f"图标替换失败: {e}")
                return False
        else:
            # 创建新图标
            new_path = os.path.join(self.icons_path, 'icon.png')
            try:
                shutil.copy2(new_icon_path, new_path)

                self.replacements.append(ReplacementRecord(
                    original_file=new_path,
                    new_file=new_icon_path,
                    replacement_type='direct'
                ))

                logger.info(f"应用图标创建成功: {new_path}")
                return True

            except Exception as e:
                logger.error(f"图标创建失败: {e}")
                return False

    def optimize_image(self, file_path: str, max_width: int = None,
                      max_height: int = None, quality: int = 85) -> bool:
        """
        优化图片资源

        Args:
            file_path: 图片路径
            max_width: 最大宽度
            max_height: 最大高度
            quality: JPEG质量

        Returns:
            bool: 优化是否成功
        """
        try:
            with Image.open(file_path) as img:
                original_width, original_height = img.size

                # 计算新尺寸
                new_width = original_width
                new_height = original_height

                if max_width and original_width > max_width:
                    ratio = max_width / original_width
                    new_width = max_width
                    new_height = int(original_height * ratio)

                if max_height and new_height > max_height:
                    ratio = max_height / new_height
                    new_height = max_height
                    new_width = int(new_width * ratio)

                # 缩放
                if new_width != original_width or new_height != original_height:
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # 保存
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    img.save(file_path, 'JPEG', quality=quality, optimize=True)
                else:
                    img.save(file_path, optimize=True)

                logger.info(f"图片已优化: {file_path} ({original_width}x{original_height} -> {new_width}x{new_height})")
                return True

        except Exception as e:
            logger.error(f"图片优化失败: {e}")
            return False

    def get_replacements(self) -> List[Dict]:
        """获取替换记录"""
        return [r.to_dict() for r in self.replacements]

    def export_replacement_log(self, output_path: str) -> bool:
        """
        导出替换日志

        Args:
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        import json

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "total_replacements": len(self.replacements),
                    "replacements": self.get_replacements()
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"替换日志已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出替换日志失败: {e}")
            return False

    def get_resource_summary(self) -> str:
        """获取资源摘要"""
        summary = {
            'total': len(self.resources),
            'images': sum(1 for r in self.resources.values() if r.resource_type == 'image'),
            'audio': sum(1 for r in self.resources.values() if r.resource_type == 'audio'),
            'fonts': sum(1 for r in self.resources.values() if r.resource_type == 'font'),
            'replacements': len(self.replacements)
        }

        return f"""
=== 资源摘要 ===
总数: {summary['total']}
- 图片: {summary['images']}
- 音频: {summary['audio']}
- 字体: {summary['fonts']}
替换次数: {summary['replacements']}
"""


def main():
    """主函数测试"""
    print("=" * 60)
    print("Construct3 Resource Manager Test")
    print("Construct3资源管理器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from resource_manager import C3PResourceManager

    manager = C3PResourceManager('/path/to/extracted/c3p')

    # 按名称替换资源
    manager.replace_resource('background.png', '/path/to/new/background.png')

    # 按类型替换
    manager.replace_by_type('icon', '/path/to/new/icon.png')
    manager.replace_by_type('background', '/path/to/new/bg.png')

    # 批量替换
    manager.batch_replace({
        'player.png': '/path/to/new/player.png',
        'coin.png': '/path/to/new/coin.png'
    })

    # 替换应用图标
    manager.replace_app_icon('/path/to/new/icon.png')

    # 优化图片
    manager.optimize_image('/path/to/image.png', max_width=1024, max_height=1024)

    # 导出替换日志
    manager.export_replacement_log('replacements.json')
    """)


if __name__ == "__main__":
    main()
