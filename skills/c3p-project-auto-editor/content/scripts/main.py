"""
Construct3 C3P Auto Editor - Main Orchestrator
Construct3 C3P项目自动编辑器 - 主协调脚本

整合所有模块，实现全自动编辑.c3p项目文件
"""

import os
import sys
import json
import shutil
import logging
import zipfile
import tempfile
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from c3p_parser import C3PParser, C3PFileInfo, C3PProjectStructure
from xml_editor import C3PXMLEditor
from resource_manager import C3PResourceManager
from event_editor import C3PEventEditor, GameBalanceConfig
from config_loader import C3PConfigLoader, EditorConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('C3PAutoEditor')


@dataclass
class EditResult:
    """编辑结果"""
    success: bool
    output_path: str
    modifications_count: int
    warnings: List[str]
    errors: List[str]
    log_path: str

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "output_path": self.output_path,
            "modifications_count": self.modifications_count,
            "warnings": self.warnings,
            "errors": self.errors,
            "log_path": self.log_path
        }


@dataclass
class ModificationLog:
    """修改日志"""
    start_time: str
    end_time: str
    template_file: str
    output_file: str
    config_applied: Dict
    xml_modifications: List[Dict]
    resource_replacements: List[Dict]
    event_modifications: List[Dict]
    warnings: List[str]
    errors: List[str]

    def to_dict(self) -> Dict:
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "template_file": self.template_file,
            "output_file": self.output_file,
            "config_applied": self.config_applied,
            "xml_modifications": self.xml_modifications,
            "resource_replacements": self.resource_replacements,
            "event_modifications": self.event_modifications,
            "warnings": self.warnings,
            "errors": self.errors
        }


class C3PAutoEditorError(Exception):
    """编辑器错误"""
    pass


class C3PAutoEditor:
    """Construct3 C3P项目自动编辑器主类"""

    def __init__(self, config: Optional[EditorConfig] = None):
        """
        初始化编辑器

        Args:
            config: 编辑器配置
        """
        self.config = config
        self.parser: Optional[C3PParser] = None
        self.xml_editor: Optional[C3PXMLEditor] = None
        self.resource_manager: Optional[C3PResourceManager] = None
        self.event_editor: Optional[C3PEventEditor] = None
        self.config_loader: Optional[C3PConfigLoader] = None

        self.work_dir: Optional[str] = None
        self.output_path: Optional[str] = None

        self.modification_log: List[Dict] = []
        self.warnings: List[str] = []
        self.errors: List[str] = []

    def load_config(self, config_path: str) -> EditorConfig:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            EditorConfig对象
        """
        self.config_loader = C3PConfigLoader()
        self.config = self.config_loader.load_from_file(config_path)
        return self.config

    def load_config_from_dict(self, config_dict: Dict) -> EditorConfig:
        """
        从字典加载配置

        Args:
            config_dict: 配置字典

        Returns:
            EditorConfig对象
        """
        self.config_loader = C3PConfigLoader()
        self.config = self.config_loader.load_from_dict(config_dict)
        return self.config

    def edit(self, template_c3p: str, output_c3p: str) -> EditResult:
        """
        编辑C3P项目

        Args:
            template_c3p: 模板文件路径
            output_c3p: 输出文件路径

        Returns:
            EditResult编辑结果
        """
        start_time = datetime.now()
        self.output_path = output_c3p

        logger.info(f"开始编辑C3P项目: {template_c3p}")

        try:
            # 阶段1: 解压模板
            self._extract_template(template_c3p)

            # 阶段2: 初始化各模块
            self._initialize_modules()

            # 阶段3: 修改项目配置
            self._update_project_config()

            # 阶段4: 替换资源
            self._replace_resources()

            # 阶段5: 更新游戏平衡
            self._update_game_balance()

            # 阶段6: 更新广告配置
            self._update_advertising()

            # 阶段7: 重新打包
            self._repack_project(output_c3p)

            end_time = datetime.now()

            # 生成修改日志
            log = ModificationLog(
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                template_file=template_c3p,
                output_file=output_c3p,
                config_applied=self.config.to_dict() if self.config else {},
                xml_modifications=self.xml_editor.get_modifications() if self.xml_editor else [],
                resource_replacements=self.resource_manager.get_replacements() if self.resource_manager else [],
                event_modifications=self.event_editor.get_modifications() if self.event_editor else [],
                warnings=self.warnings,
                errors=self.errors
            )

            log_path = output_c3p + '.log.json'
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(log.to_dict(), f, indent=2, ensure_ascii=False)

            # 清理临时文件
            self._cleanup()

            result = EditResult(
                success=True,
                output_path=output_c3p,
                modifications_count=len(log.xml_modifications) + len(log.resource_replacements) + len(log.event_modifications),
                warnings=self.warnings,
                errors=self.errors,
                log_path=log_path
            )

            logger.info(f"编辑完成: {output_c3p}")
            return result

        except Exception as e:
            logger.error(f"编辑失败: {e}")
            self.errors.append(str(e))
            self._cleanup()

            return EditResult(
                success=False,
                output_path=output_c3p,
                modifications_count=0,
                warnings=self.warnings,
                errors=self.errors,
                log_path=""
            )

    def _extract_template(self, template_c3p: str):
        """解压模板"""
        logger.info("阶段1: 解压模板...")

        self.parser = C3PParser()

        try:
            extract_path, file_info, structure = self.parser.extract(template_c3p)
            self.work_dir = extract_path

            logger.info(f"解压成功: {file_info.project_name}")

        except Exception as e:
            raise C3PAutoEditorError(f"解压模板失败: {e}")

    def _initialize_modules(self):
        """初始化各模块"""
        logger.info("阶段2: 初始化模块...")

        if not self.work_dir:
            raise C3PAutoEditorError("工作目录未初始化")

        self.xml_editor = C3PXMLEditor(self.work_dir)
        self.resource_manager = C3PResourceManager(self.work_dir)
        self.event_editor = C3PEventEditor(self.work_dir)

        logger.info("模块初始化完成")

    def _update_project_config(self):
        """更新项目配置"""
        logger.info("阶段3: 更新项目配置...")

        if not self.config:
            logger.warning("未提供配置，跳过项目配置更新")
            return

        project_file = os.path.join(self.work_dir, 'project.c3proj')

        if not os.path.exists(project_file):
            self.warnings.append("project.c3proj文件不存在")
            return

        updates = {}

        if self.config.game_name:
            updates['game_name'] = self.config.game_name
        if self.config.description:
            updates['description'] = self.config.description
        if self.config.author:
            updates['author'] = self.config.author
        if self.config.version:
            updates['version'] = self.config.version

        if updates:
            success, failed = self.xml_editor.batch_update_project(project_file, updates)
            logger.info(f"项目配置更新: {success}成功, {failed}失败")

        # 更新导出配置
        export_config = {}
        if self.config.package_name:
            export_config['package_name'] = self.config.package_name
        if self.config.bundle_id:
            export_config['bundle_id'] = self.config.bundle_id

        if export_config:
            self.xml_editor.update_export_config(project_file, export_config)
            logger.info(f"导出配置更新: {list(export_config.keys())}")

    def _replace_resources(self):
        """替换资源"""
        logger.info("阶段4: 替换资源...")

        if not self.config:
            logger.warning("未提供配置，跳过资源替换")
            return

        replaced_count = 0

        # 替换应用图标
        if self.config.app_icon and os.path.exists(self.config.app_icon):
            if self.resource_manager.replace_app_icon(self.config.app_icon):
                replaced_count += 1

        # 替换背景
        if self.config.background:
            bg_matches = self.resource_manager.find_resource_by_name(self.config.background)
            if bg_matches:
                self.resource_manager.replace_resource(bg_matches[0].original_name, self.config.background)
                replaced_count += 1
            elif os.path.exists(self.config.background):
                # 尝试替换任意背景图
                bg_resources = self.resource_manager.find_resource_by_type('background')
                if bg_resources:
                    self.resource_manager.replace_resource(bg_resources[0].original_name, self.config.background)
                    replaced_count += 1

        # 替换精灵图
        for name, path in self.config.sprites.items():
            if path and os.path.exists(path):
                if self.resource_manager.replace_resource(name, path):
                    replaced_count += 1

        logger.info(f"资源替换完成: {replaced_count}个")

    def _update_game_balance(self):
        """更新游戏平衡"""
        logger.info("阶段5: 更新游戏平衡...")

        if not self.config:
            logger.warning("未提供配置，跳过游戏平衡更新")
            return

        config = GameBalanceConfig(
            click_reward=self.config.click_reward,
            upgrade_cost_base=self.config.upgrade_cost_base,
            difficulty=self.config.difficulty,
            coin_rate=self.config.coin_rate,
            ad_frequency=self.config.ad_frequency
        )

        modified_count = self.event_editor.update_game_balance(config)
        logger.info(f"游戏平衡更新: {modified_count}个事件表")

    def _update_advertising(self):
        """更新广告配置"""
        logger.info("阶段6: 更新广告配置...")

        if not self.config:
            logger.warning("未提供配置，跳过广告配置更新")
            return

        ad_config = {}

        if self.config.tiktok_app_id:
            ad_config['tiktok_app_id'] = self.config.tiktok_app_id
        if self.config.tiktok_rewarded_id:
            ad_config['tiktok_rewarded_id'] = self.config.tiktok_rewarded_id
        if self.config.tiktok_interstitial_id:
            ad_config['tiktok_interstitial_id'] = self.config.tiktok_interstitial_id
        if self.config.admob_app_id:
            ad_config['admob_app_id'] = self.config.admob_app_id
        if self.config.admob_rewarded_id:
            ad_config['admob_rewarded_id'] = self.config.admob_rewarded_id

        if ad_config:
            modified_count = self.event_editor.update_ad_config(ad_config)
            logger.info(f"广告配置更新: {modified_count}个事件表")

    def _repack_project(self, output_path: str):
        """重新打包项目"""
        logger.info("阶段7: 重新打包项目...")

        if not self.work_dir:
            raise C3PAutoEditorError("工作目录未初始化")

        try:
            # 创建ZIP文件
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(self.work_dir):
                    # 跳过备份目录
                    dirs[:] = [d for d in dirs if not d.startswith('.')]

                    for file in files:
                        # 跳过备份和临时文件
                        if file.startswith('.') or file.endswith('.bak'):
                            continue

                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.work_dir)
                        zf.write(file_path, arcname)

            logger.info(f"打包完成: {output_path}")

        except Exception as e:
            raise C3PAutoEditorError(f"打包失败: {e}")

    def _cleanup(self):
        """清理临时文件"""
        if self.parser:
            self.parser.cleanup()

        if self.work_dir and os.path.exists(self.work_dir):
            try:
                shutil.rmtree(self.work_dir)
                logger.info(f"已清理工作目录: {self.work_dir}")
            except:
                pass


def main():
    """主函数入口"""
    import argparse

    parser_cli = argparse.ArgumentParser(description='Construct3 C3P Auto Editor')
    parser_cli.add_argument('template', help='模板C3P文件路径')
    parser_cli.add_argument('output', help='输出C3P文件路径')
    parser_cli.add_argument('--config', '-c', required=True, help='配置文件路径')

    args = parser_cli.parse_args()

    print("=" * 60)
    print("Construct3 C3P Project Auto Editor")
    print("Construct3 C3P项目自动编辑器")
    print("=" * 60)
    print()

    # 创建编辑器
    editor = C3PAutoEditor()

    # 加载配置
    print(f"加载配置文件: {args.config}")
    config = editor.load_config(args.config)
    print(f"配置: {config.game_name}")

    # 执行编辑
    print(f"\n开始编辑...")
    result = editor.edit(args.template, args.output)

    # 输出结果
    print("\n" + "=" * 60)
    print("编辑结果:")
    print("=" * 60)
    print(f"状态: {'成功' if result.success else '失败'}")
    print(f"输出文件: {result.output_path}")
    print(f"修改数量: {result.modifications_count}")
    print(f"日志文件: {result.log_path}")

    if result.warnings:
        print(f"\n警告 ({len(result.warnings)}):")
        for w in result.warnings:
            print(f"  - {w}")

    if result.errors:
        print(f"\n错误 ({len(result.errors)}):")
        for e in result.errors:
            print(f"  - {e}")

    print()


if __name__ == "__main__":
    main()
