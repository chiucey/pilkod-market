"""
Construct3 C3P Parser
Construct3 .c3p项目文件解析器

解析、提取、重构Construct3的.c3p项目文件
.c3p文件本质为加密ZIP压缩包
"""

import os
import sys
import json
import zipfile
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('C3PParser')


@dataclass
class C3PFileInfo:
    """C3P文件信息"""
    original_path: str = ""
    original_size: int = 0
    extracted_path: str = ""
    project_name: str = ""
    project_version: str = ""
    layout_count: int = 0
    event_sheet_count: int = 0
    resource_count: int = 0
    extracted_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "original_path": self.original_path,
            "original_size": self.original_size,
            "extracted_path": self.extracted_path,
            "project_name": self.project_name,
            "project_version": self.project_version,
            "layout_count": self.layout_count,
            "event_sheet_count": self.event_sheet_count,
            "resource_count": self.resource_count,
            "extracted_at": self.extracted_at
        }


@dataclass
class C3PProjectStructure:
    """C3P项目结构"""
    root_path: str = ""
    project_file: str = ""  # project.c3proj
    ui_state_file: str = ""  # project.uistate.json
    layouts: List[str] = field(default_factory=list)
    event_sheets: List[str] = field(default_factory=list)
    object_types: List[str] = field(default_factory=list)
    animations: List[str] = field(default_factory=list)
    media_path: str = ""
    icons_path: str = ""
    files_tree: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "root_path": self.root_path,
            "project_file": self.project_file,
            "ui_state_file": self.ui_state_file,
            "layouts": self.layouts,
            "event_sheets": self.event_sheets,
            "object_types": self.object_types,
            "animations": self.animations,
            "media_path": self.media_path,
            "icons_path": self.icons_path,
            "files_tree": self.files_tree
        }


class C3PParseError(Exception):
    """C3P解析错误"""
    pass


class C3PNotFoundError(Exception):
    """C3P文件未找到错误"""
    pass


class InvalidC3PFormatError(Exception):
    """无效C3P格式错误"""
    pass


class C3PParser:
    """Construct3 C3P文件解析器"""

    # C3P项目标准文件扩展名
    PROJECT_EXTENSIONS = {
        '.c3proj': 'project',
        '.uilayout': 'layout',
        '.uevents': 'event_sheet',
        '.uot': 'object_type',
        '.uanimations': 'animations',
        '.uscene': 'scene'
    }

    # 必须包含的核心文件
    REQUIRED_FILES = [
        'project.c3proj',
        'project.uistate.json'
    ]

    def __init__(self):
        self.file_info: Optional[C3PFileInfo] = None
        self.project_structure: Optional[C3PProjectStructure] = None
        self.temp_dir: Optional[str] = None
        self.is_extracted: bool = False

    def validate_c3p_file(self, file_path: str) -> bool:
        """
        验证.c3p文件有效性

        Args:
            file_path: C3P文件路径

        Returns:
            bool: 文件是否有效
        """
        path = Path(file_path)

        if not path.exists():
            logger.error(f"文件不存在: {file_path}")
            raise C3PNotFoundError(f"文件不存在: {file_path}")

        if not path.suffix.lower() == '.c3p':
            logger.warning(f"文件扩展名不是.c3p: {file_path}")

        if path.stat().st_size == 0:
            logger.error(f"文件为空: {file_path}")
            raise InvalidC3PFormatError(f"文件为空: {file_path}")

        # 尝试打开ZIP文件验证格式
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 检查是否包含核心文件
                file_list = zf.namelist()
                missing_files = [f for f in self.REQUIRED_FILES if f not in file_list]

                if missing_files:
                    logger.warning(f"缺少核心文件: {missing_files}")
                    # 不抛出错误，因为某些模板可能缺少某些文件

                return True
        except zipfile.BadZipFile:
            logger.error(f"无效的ZIP格式: {file_path}")
            raise InvalidC3PFormatError(f"无效的ZIP格式: {file_path}")
        except Exception as e:
            logger.error(f"验证失败: {e}")
            raise C3PParseError(f"验证失败: {e}")

    def extract(self, c3p_path: str, extract_dir: Optional[str] = None) -> Tuple[str, C3PFileInfo, C3PProjectStructure]:
        """
        解压.c3p文件

        Args:
            c3p_path: C3P文件路径
            extract_dir: 解压目录，None则使用临时目录

        Returns:
            Tuple[解压路径, 文件信息, 项目结构]
        """
        logger.info(f"开始解析C3P文件: {c3p_path}")

        # 验证文件
        self.validate_c3p_file(c3p_path)

        # 创建解压目录
        if extract_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix='c3p_')
            extract_path = self.temp_dir
        else:
            extract_path = extract_dir
            os.makedirs(extract_path, exist_ok=True)

        try:
            # 解压文件
            with zipfile.ZipFile(c3p_path, 'r') as zf:
                zf.extractall(extract_path)
                logger.info(f"解压完成: {extract_path}")

            # 解析项目信息
            self.file_info = self._parse_file_info(c3p_path, extract_path)
            self.project_structure = self._parse_project_structure(extract_path)
            self.is_extracted = True

            return extract_path, self.file_info, self.project_structure

        except Exception as e:
            logger.error(f"解压失败: {e}")
            # 清理临时目录
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise C3PParseError(f"解压失败: {e}")

    def _parse_file_info(self, c3p_path: str, extract_path: str) -> C3PFileInfo:
        """解析文件信息"""
        info = C3PFileInfo()
        info.original_path = os.path.abspath(c3p_path)
        info.original_size = os.path.getsize(c3p_path)
        info.extracted_path = extract_path
        info.extracted_at = datetime.now().isoformat()

        # 解析project.c3proj获取项目信息
        project_file = os.path.join(extract_path, 'project.c3proj')
        if os.path.exists(project_file):
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(project_file)
                root = tree.getroot()

                # 获取项目名称
                name_elem = root.find('.//{*}name')
                if name_elem is not None:
                    info.project_name = name_elem.text or ""

                # 获取版本信息
                version_elem = root.find('.//{*}version')
                if version_elem is not None:
                    info.project_version = version_elem.text or ""

                # 统计布局和事件表数量
                layouts_dir = os.path.join(extract_path, 'layouts')
                if os.path.exists(layouts_dir):
                    info.layout_count = len([f for f in os.listdir(layouts_dir)
                                            if f.endswith('.uilayout')])

                event_sheets_dir = os.path.join(extract_path, 'eventSheets')
                if os.path.exists(event_sheets_dir):
                    info.event_sheet_count = len([f for f in os.listdir(event_sheets_dir)
                                                 if f.endswith('.uevents')])

            except Exception as e:
                logger.warning(f"解析project.c3proj失败: {e}")

        # 统计资源数量
        media_path = os.path.join(extract_path, 'media')
        if os.path.exists(media_path):
            for root, dirs, files in os.walk(media_path):
                info.resource_count += len(files)

        logger.info(f"文件信息解析完成: {info.project_name} v{info.project_version}")
        return info

    def _parse_project_structure(self, root_path: str) -> C3PProjectStructure:
        """解析项目结构"""
        structure = C3PProjectStructure()
        structure.root_path = root_path

        # 构建文件树
        structure.files_tree = self._build_file_tree(root_path)

        # 定位核心文件
        structure.project_file = os.path.join(root_path, 'project.c3proj')
        structure.ui_state_file = os.path.join(root_path, 'project.uistate.json')

        # 收集布局文件
        layouts_dir = os.path.join(root_path, 'layouts')
        if os.path.exists(layouts_dir):
            structure.layouts = [
                os.path.join(layouts_dir, f)
                for f in os.listdir(layouts_dir)
                if f.endswith('.uilayout')
            ]

        # 收集事件表文件
        event_sheets_dir = os.path.join(root_path, 'eventSheets')
        if os.path.exists(event_sheets_dir):
            structure.event_sheets = [
                os.path.join(event_sheets_dir, f)
                for f in os.listdir(event_sheets_dir)
                if f.endswith('.uevents')
            ]

        # 收集对象类型文件
        object_types_dir = os.path.join(root_path, 'objectTypes')
        if os.path.exists(object_types_dir):
            structure.object_types = [
                os.path.join(object_types_dir, f)
                for f in os.listdir(object_types_dir)
                if f.endswith('.uot')
            ]

        # 收集动画配置
        animations_dir = os.path.join(root_path, 'animations')
        if os.path.exists(animations_dir):
            structure.animations = [
                os.path.join(animations_dir, f)
                for f in os.listdir(animations_dir)
            ]

        # 资源路径
        structure.media_path = os.path.join(root_path, 'media')
        structure.icons_path = os.path.join(root_path, 'icons')

        logger.info(f"项目结构解析完成: {len(structure.layouts)}布局, {len(structure.event_sheets)}事件表")
        return structure

    def _build_file_tree(self, root_path: str) -> Dict:
        """构建文件树"""
        tree = {}
        for root, dirs, files in os.walk(root_path):
            # 跳过临时隐藏目录
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            # 获取相对路径
            rel_path = os.path.relpath(root, root_path)
            if rel_path == '.':
                rel_path = '/'

            node = {'_files': []}
            for f in files:
                if not f.startswith('.'):
                    node['_files'].append(f)

            # 合并到树
            if rel_path == '/':
                tree.update(node)
            else:
                path_parts = rel_path.split(os.sep)
                current = tree
                for part in path_parts:
                    if part not in current:
                        current[part] = {'_files': []}
                    current = current[part]
                current['_files'].extend(node['_files'])

        return tree

    def get_resource_paths(self, resource_type: str = None) -> List[str]:
        """
        获取资源文件路径

        Args:
            resource_type: 资源类型 (images/audio/fonts/all)

        Returns:
            资源文件路径列表
        """
        if not self.is_extracted:
            raise C3PParseError("请先调用extract()方法")

        media_path = self.project_structure.media_path
        if not os.path.exists(media_path):
            return []

        resources = []
        extensions = {
            'images': ['.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp'],
            'audio': ['.ogg', '.mp3', '.wav', '.aac', '.m4a'],
            'fonts': ['.ttf', '.otf', '.woff', '.woff2']
        }

        target_exts = extensions.get(resource_type, extensions['images'] +
                                    extensions['audio'] + extensions['fonts']) if resource_type else []

        for root, dirs, files in os.walk(media_path):
            for f in files:
                if not f.startswith('.'):
                    ext = os.path.splitext(f)[1].lower()
                    if not target_exts or ext in target_exts:
                        resources.append(os.path.join(root, f))

        return resources

    def get_project_config(self) -> Dict[str, Any]:
        """获取项目配置"""
        if not self.is_extracted:
            raise C3PParseError("请先调用extract()方法")

        project_file = self.project_structure.project_file
        if not os.path.exists(project_file):
            return {}

        import xml.etree.ElementTree as ET
        tree = ET.parse(project_file)
        root = tree.getroot()

        config = {
            'name': '',
            'version': '',
            'description': '',
            'author': '',
            'canvas_width': 0,
            'canvas_height': 0,
            'fps': 60,
            'first_layout': '',
            'export_filters': []
        }

        # 解析项目属性
        props = root.find('.//{*}properties')
        if props is not None:
            for prop in props:
                tag = prop.tag.replace('{*}', '')
                config[tag] = prop.text or ""

        # 解析画布设置
        settings = root.find('.//{*}settings')
        if settings is not None:
            for setting in settings:
                tag = setting.tag.replace('{*}', '')
                if tag in ['width', 'height', 'fps']:
                    config[tag] = int(setting.text) if setting.text else 0

        return config

    def cleanup(self):
        """清理临时文件"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info(f"已清理临时目录: {self.temp_dir}")
            self.temp_dir = None
            self.is_extracted = False

    def get_summary(self) -> str:
        """获取解析摘要"""
        if not self.file_info:
            return "未解析任何C3P文件"

        return f"""
=== C3P文件解析摘要 ===
原始文件: {self.file_info.original_path}
文件大小: {self.file_info.original_size:,} bytes
解压路径: {self.file_info.extracted_path}
项目名称: {self.file_info.project_name}
项目版本: {self.file_info.project_version}
布局数量: {self.file_info.layout_count}
事件表: {self.file_info.event_sheet_count}
资源数量: {self.file_info.resource_count}
解析时间: {self.file_info.extracted_at}
"""


def main():
    """主函数测试"""
    print("=" * 60)
    print("Construct3 C3P Parser Test")
    print("Construct3 C3P解析器测试")
    print("=" * 60)
    print()

    parser = C3PParser()

    # 测试代码示例
    print("使用示例:")
    print("""
    from c3p_parser import C3PParser

    parser = C3PParser()

    # 解压C3P文件
    extract_path, file_info, structure = parser.extract('template.c3p')

    # 获取资源路径
    images = parser.get_resource_paths('images')
    print(f"图片资源: {len(images)}个")

    # 获取项目配置
    config = parser.get_project_config()
    print(f"项目配置: {config}")

    # 清理
    parser.cleanup()
    """)


if __name__ == "__main__":
    main()
