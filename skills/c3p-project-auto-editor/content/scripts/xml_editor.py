"""
Construct3 XML Editor
Construct3 XML配置文件编辑器

程序化修改.c3p项目中的XML配置文件
支持增删改查项目全局参数
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    import xml.etree.ElementTree as etree

try:
    import xml.etree.ElementTree as ET
except ImportError:
    pass

# 配置日志
logger = logging.getLogger('C3PXMLEditor')


@dataclass
class XMLModification:
    """XML修改记录"""
    file_path: str
    xpath: str
    old_value: str
    new_value: str
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "file": self.file_path,
            "xpath": self.xpath,
            "old_value": str(self.old_value),
            "new_value": str(self.new_value),
            "modified_at": self.modified_at
        }


class C3PXMLEditorError(Exception):
    """XML编辑错误"""
    pass


class C3PXMLValidationError(Exception):
    """XML验证错误"""
    pass


class C3PXMLEditor:
    """Construct3 XML配置文件编辑器"""

    # Construct3 XML命名空间
    C3P_NAMESPACES = {
        'c3p': 'https://www.construct.net',
        'c3': 'https://construct.net'
    }

    # 项目配置文件参数映射
    PROJECT_PARAMETERS = {
        'game_name': {
            'xpath': './/{*}name',
            'type': 'text',
            'required': True
        },
        'description': {
            'xpath': './/{*}description',
            'type': 'text'
        },
        'author': {
            'xpath': './/{*}author',
            'type': 'text'
        },
        'version': {
            'xpath': './/{*}version',
            'type': 'text'
        },
        'canvas_width': {
            'xpath': './/{*}window{*}width',
            'type': 'number'
        },
        'canvas_height': {
            'xpath': './/{*}window{*}height',
            'type': 'number'
        },
        'fps': {
            'xpath': './/{*}fps',
            'type': 'number'
        },
        'first_layout': {
            'xpath': './/{*}first-layout',
            'type': 'text'
        }
    }

    # 导出配置参数映射
    EXPORT_PARAMETERS = {
        'package_name': {
            'xpath': './/{*}android{*}package',
            'type': 'text'
        },
        'bundle_id': {
            'xpath': './/{*}ios{*}bundleIdentifier',
            'type': 'text'
        },
        'min_sdk': {
            'xpath': './/{*}android{*}minSdkVersion',
            'type': 'number'
        },
        'target_sdk': {
            'xpath': './/{*}android{*}targetSdkVersion',
            'type': 'number'
        }
    }

    def __init__(self, project_root: str):
        """
        初始化XML编辑器

        Args:
            project_root: C3P项目解压后的根目录
        """
        self.project_root = project_root
        self.modifications: List[XMLModification] = []
        self.backup_dir = os.path.join(project_root, '.backup')

        os.makedirs(self.backup_dir, exist_ok=True)

    def _get_parser(self):
        """获取XML解析器"""
        if HAS_LXML:
            return etree
        return etree

    def load_xml(self, file_path: str, create_backup: bool = True) -> Any:
        """
        加载XML文件

        Args:
            file_path: XML文件路径
            create_backup: 是否创建备份

        Returns:
            XML根元素
        """
        if not os.path.exists(file_path):
            raise C3PXMLEditorError(f"文件不存在: {file_path}")

        try:
            # 创建备份
            if create_backup:
                backup_path = os.path.join(
                    self.backup_dir,
                    f"{os.path.basename(file_path)}.bak"
                )
                if not os.path.exists(backup_path):
                    import shutil
                    shutil.copy2(file_path, backup_path)

            # 解析XML
            parser = self._get_parser()
            tree = parser.parse(file_path)
            return tree

        except Exception as e:
            logger.error(f"加载XML失败 {file_path}: {e}")
            raise C3PXMLEditorError(f"加载XML失败: {e}")

    def save_xml(self, tree: Any, file_path: str, pretty_print: bool = True) -> bool:
        """
        保存XML文件

        Args:
            tree: XML树或元素
            file_path: 保存路径
            pretty_print: 是否格式化输出

        Returns:
            bool: 保存是否成功
        """
        try:
            # 获取根元素
            root = tree if hasattr(tree, 'getroot') else tree

            # 格式化输出
            if pretty_print:
                self._prettify_xml(root)

            # 保存
            parser = self._get_parser()
            parser.dump(root, file_path) if hasattr(parser, 'dump') else None

            # 使用ElementTree保存
            ET = self._get_elementtree()
            tree_to_save = ET.ElementTree(root) if hasattr(tree, 'getroot') else tree
            tree_to_save.write(file_path, encoding='utf-8', xml_declaration=True)

            logger.info(f"XML保存成功: {file_path}")
            return True

        except Exception as e:
            logger.error(f"保存XML失败 {file_path}: {e}")
            raise C3PXMLEditorError(f"保存XML失败: {e}")

    def _get_elementtree(self):
        """获取ElementTree模块"""
        return etree

    def _prettify_xml(self, elem: Any):
        """格式化XML"""
        try:
            from lxml import etree as lxml_etree
            lxml_etree.indent(elem, space="  ")
        except:
            pass

    def find_element(self, root: Any, xpath: str) -> Optional[Any]:
        """
        查找XML元素

        Args:
            root: XML根元素
            xpath: XPath表达式

        Returns:
            找到的元素，未找到返回None
        """
        try:
            return root.find(xpath)
        except Exception as e:
            logger.warning(f"XPath查找失败 '{xpath}': {e}")
            return None

    def set_text_value(self, root: Any, xpath: str, value: str, create_path: bool = True) -> bool:
        """
        设置文本值

        Args:
            root: XML根元素
            xpath: XPath表达式
            value: 新值
            create_path: 是否自动创建路径

        Returns:
            bool: 设置是否成功
        """
        elem = self.find_element(root, xpath)

        if elem is None:
            if create_path:
                elem = self._create_path(root, xpath)
                if elem is None:
                    return False
            else:
                return False

        # 记录修改
        old_value = elem.text or ""
        elem.text = str(value)

        self.modifications.append(XMLModification(
            file_path="",
            xpath=xpath,
            old_value=old_value,
            new_value=value
        ))

        return True

    def set_attribute(self, elem: Any, attr_name: str, value: str) -> bool:
        """
        设置元素属性

        Args:
            elem: XML元素
            attr_name: 属性名
            value: 属性值

        Returns:
            bool: 设置是否成功
        """
        old_value = elem.get(attr_name, "")
        elem.set(attr_name, str(value))

        self.modifications.append(XMLModification(
            file_path="",
            xpath=f"@{attr_name}",
            old_value=old_value,
            new_value=value
        ))

        return True

    def _create_path(self, root: Any, xpath: str) -> Optional[Any]:
        """
        创建XPath路径

        Args:
            root: 根元素
            xpath: XPath表达式

        Returns:
            创建的元素
        """
        # 简化处理：只支持单层创建
        parts = xpath.strip('./').split('/')

        if len(parts) > 2:
            logger.warning("仅支持单层元素创建")
            return None

        parent = root
        for i, part in enumerate(parts):
            # 移除命名空间前缀
            tag = part.split('}')[-1] if '}' in part else part

            # 检查是否有属性选择器
            if '[' in tag:
                tag = tag.split('[')[0]

            # 查找或创建
            existing = parent.find(f".//{part}" if i > 0 else f".//{tag}")
            if existing is None:
                # 创建新元素
                new_elem = etree.SubElement(parent, f"{{{self.C3P_NAMESPACES['c3p'] if '{*}' in xpath else ''}}}{tag}")
                parent = new_elem
            else:
                parent = existing

        return parent

    def update_project_property(self, project_file: str, param_name: str, value: Any) -> bool:
        """
        更新项目属性

        Args:
            project_file: project.c3proj文件路径
            param_name: 参数名
            value: 新值

        Returns:
            bool: 更新是否成功
        """
        if param_name not in self.PROJECT_PARAMETERS:
            logger.warning(f"未知参数: {param_name}")
            return False

        param_config = self.PROJECT_PARAMETERS[param_name]
        xpath = param_config['xpath']

        try:
            tree = self.load_xml(project_file)
            root = tree.getroot() if hasattr(tree, 'getroot') else tree

            # 尝试多种命名空间
            for ns_prefix, ns_uri in [('c3p', 'https://www.construct.net'),
                                      ('c3', 'https://construct.net'),
                                      ('', '')]:
                if ns_prefix:
                    ns_xpath = xpath.replace('{*}', f'{{{ns_uri}}}')
                else:
                    ns_xpath = xpath.replace('{*}', '')

                elem = self.find_element(root, ns_xpath)

                if elem is not None:
                    # 类型转换
                    if param_config['type'] == 'number':
                        elem.text = str(int(value))
                    else:
                        elem.text = str(value)

                    # 记录修改
                    mod = XMLModification(
                        file_path=project_file,
                        xpath=xpath,
                        old_value=elem.text,
                        new_value=str(value)
                    )
                    self.modifications.append(mod)

                    # 保存
                    self.save_xml(tree, project_file)
                    logger.info(f"项目属性已更新: {param_name} = {value}")
                    return True

            logger.warning(f"未找到属性: {param_name}")
            return False

        except Exception as e:
            logger.error(f"更新项目属性失败: {e}")
            raise C3PXMLEditorError(f"更新项目属性失败: {e}")

    def batch_update_project(self, project_file: str, updates: Dict[str, Any]) -> Tuple[int, int]:
        """
        批量更新项目属性

        Args:
            project_file: project.c3proj文件路径
            updates: 更新参数字典

        Returns:
            Tuple[成功数量, 失败数量]
        """
        success = 0
        failed = 0

        for param, value in updates.items():
            if self.update_project_property(project_file, param, value):
                success += 1
            else:
                failed += 1

        return success, failed

    def update_export_config(self, project_file: str, config: Dict[str, Any]) -> bool:
        """
        更新导出配置

        Args:
            project_file: project.c3proj文件路径
            config: 导出配置字典

        Returns:
            bool: 更新是否成功
        """
        try:
            tree = self.load_xml(project_file)
            root = tree.getroot() if hasattr(tree, 'getroot') else tree

            # 查找或创建exportsettings节点
            export_settings = root.find('.//{*}export')
            if export_settings is None:
                export_settings = etree.SubElement(root, '{*}export')

            # 更新各项配置
            for key, value in config.items():
                if key in self.EXPORT_PARAMETERS:
                    param_config = self.EXPORT_PARAMETERS[key]
                    xpath = param_config['xpath'].split('{*}')[-1]

                    elem = export_settings.find(f'.//{xpath}')
                    if elem is None:
                        elem = etree.SubElement(export_settings, f'{{{self.C3P_NAMESPACES["c3p"]}}}{xpath}')

                    elem.text = str(value)

                    self.modifications.append(XMLModification(
                        file_path=project_file,
                        xpath=xpath,
                        old_value=elem.text or "",
                        new_value=str(value)
                    ))

            self.save_xml(tree, project_file)
            logger.info(f"导出配置已更新: {list(config.keys())}")
            return True

        except Exception as e:
            logger.error(f"更新导出配置失败: {e}")
            raise C3PXMLEditorError(f"更新导出配置失败: {e}")

    def get_modifications(self) -> List[Dict]:
        """获取修改记录"""
        return [mod.to_dict() for mod in self.modifications]

    def export_modifications_log(self, output_path: str) -> bool:
        """
        导出修改日志

        Args:
            output_path: 输出文件路径

        Returns:
            bool: 导出是否成功
        """
        import json

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.get_modifications(), f, indent=2, ensure_ascii=False)

            logger.info(f"修改日志已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出修改日志失败: {e}")
            return False


def main():
    """主函数测试"""
    print("=" * 60)
    print("Construct3 XML Editor Test")
    print("Construct3 XML编辑器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from xml_editor import C3PXMLEditor

    editor = C3PXMLEditor('/path/to/extracted/c3p')

    # 更新项目名称
    editor.update_project_property(
        'project.c3proj',
        'game_name',
        'My Awesome Game'
    )

    # 批量更新
    editor.batch_update_project('project.c3proj', {
        'game_name': 'New Game Name',
        'author': 'Game Studio',
        'version': '1.0.0'
    })

    # 更新导出配置
    editor.update_export_config('project.c3proj', {
        'package_name': 'com.gamestudio.newgame',
        'bundle_id': 'com.gamestudio.newgame'
    })

    # 导出修改日志
    editor.export_modifications_log('modifications.json')
    """)


if __name__ == "__main__":
    main()
