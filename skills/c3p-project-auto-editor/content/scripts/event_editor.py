"""
Construct3 Event Editor
Construct3事件表编辑器

精准定位并程序化修改事件表中的游戏逻辑参数
支持修改数值规则、触发条件，不破坏原有事件逻辑结构
"""

import os
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from xml.etree import ElementTree as ET

# 配置日志
logger = logging.getLogger('C3PEventEditor')


@dataclass
class EventModification:
    """事件修改记录"""
    file_path: str
    event_id: str
    description: str
    parameter: str
    old_value: Any
    new_value: Any
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "file": self.file_path,
            "event_id": self.event_id,
            "description": self.description,
            "parameter": self.parameter,
            "old_value": str(self.old_value),
            "new_value": str(self.new_value),
            "modified_at": self.modified_at
        }


@dataclass
class GameBalanceConfig:
    """游戏平衡配置"""
    click_reward: int = 1
    upgrade_cost_base: int = 10
    upgrade_cost_multiplier: float = 1.5
    difficulty: float = 1.0
    coin_rate: int = 1
    ad_frequency: int = 60
    reward_multiplier: float = 1.0
    enemy_speed: float = 100.0
    player_speed: float = 200.0
    gravity: float = 500.0
    jump_force: float = -400.0


class EventEditorError(Exception):
    """事件编辑错误"""
    pass


class C3PEventEditor:
    """Construct3事件表编辑器"""

    # 事件表命名空间
    EVENT_NAMESPACES = {
        'c3': 'https://construct.net',
        'event': 'https://construct.net/events'
    }

    # 已知的事件参数XPath模式
    EVENT_PARAM_PATTERNS = {
        'score': ['.//{*}score', './/{*}addScore', './/{*}SetScore'],
        'health': ['.//{*}health', './/{*}SetHealth', './/{*}subtractHealth'],
        'speed': ['.//{*}speed', './/{*}SetSpeed', './/{*}velocity'],
        'position': ['.//{*}X', './/{*}Y', './/{*}SetPosition'],
        'variable': ['.//{*}variable', './/{*}localvar', './/{*}globalvar'],
        'timer': ['.//{*}wait', './/{*}timer', './/{*}everyXseconds'],
        'audio': ['.//{*}Play', './/{*}Stop', './/{*}SetVolume']
    }

    def __init__(self, project_root: str):
        """
        初始化事件编辑器

        Args:
            project_root: C3P项目解压后的根目录
        """
        self.project_root = project_root
        self.event_sheets_dir = os.path.join(project_root, 'eventSheets')
        self.backup_dir = os.path.join(project_root, '.event_backup')
        self.modifications: List[EventModification] = []

        os.makedirs(self.backup_dir, exist_ok=True)

        # 扫描事件表
        self.event_sheets = self._scan_event_sheets()

    def _scan_event_sheets(self) -> List[str]:
        """扫描事件表文件"""
        event_sheets = []

        if not os.path.exists(self.event_sheets_dir):
            logger.warning(f"事件表目录不存在: {self.event_sheets_dir}")
            return event_sheets

        for f in os.listdir(self.event_sheets_dir):
            if f.endswith('.uevents'):
                event_sheets.append(os.path.join(self.event_sheets_dir, f))

        logger.info(f"发现{len(event_sheets)}个事件表")
        return event_sheets

    def _create_backup(self, file_path: str) -> str:
        """创建事件表备份"""
        import shutil

        backup_path = os.path.join(
            self.backup_dir,
            f"{os.path.basename(file_path)}.{datetime.now().strftime('%Y%m%d%H%M%S')}.bak"
        )
        shutil.copy2(file_path, backup_path)
        return backup_path

    def parse_event_sheet(self, event_sheet_path: str) -> ET.Element:
        """
        解析事件表XML

        Args:
            event_sheet_path: 事件表文件路径

        Returns:
            XML根元素
        """
        try:
            tree = ET.parse(event_sheet_path)
            return tree.getroot()
        except Exception as e:
            logger.error(f"解析事件表失败: {event_sheet_path} - {e}")
            raise EventEditorError(f"解析事件表失败: {e}")

    def find_event_by_description(self, root: ET.Element,
                                  description: str) -> List[ET.Element]:
        """
        按描述查找事件

        Args:
            root: XML根元素
            description: 事件描述关键词

        Returns:
            匹配的事件元素列表
        """
        events = []

        # 递归查找
        for elem in root.iter():
            # 检查元素的文本内容
            if description.lower() in (elem.text or '').lower():
                events.append(elem)

            # 检查元素属性
            for attr_value in elem.attrib.values():
                if description.lower() in attr_value.lower():
                    events.append(elem)

        return events

    def find_events_with_parameter(self, root: ET.Element,
                                   parameter_name: str) -> List[Tuple[ET.Element, str]]:
        """
        查找包含特定参数的事件

        Args:
            root: XML根元素
            parameter_name: 参数名

        Returns:
            List[Tuple[元素, 参数值]]
        """
        results = []

        for elem in root.iter():
            # 检查标签名
            if parameter_name.lower() in elem.tag.lower():
                results.append((elem, elem.text or ''))

            # 检查文本内容
            if elem.text and parameter_name.lower() in elem.text.lower():
                results.append((elem, elem.text))

            # 检查属性
            for attr, value in elem.attrib.items():
                if parameter_name.lower() in attr.lower():
                    results.append((elem, value))

        return results

    def modify_numeric_value(self, elem: ET.Element, new_value: Any) -> bool:
        """
        修改元素的数值

        Args:
            elem: XML元素
            new_value: 新值

        Returns:
            bool: 修改是否成功
        """
        try:
            old_value = elem.text

            # 尝试数值转换
            if isinstance(new_value, str):
                try:
                    new_value = float(new_value)
                except ValueError:
                    pass

            elem.text = str(new_value)

            logger.info(f"数值修改: {old_value} -> {new_value}")
            return True

        except Exception as e:
            logger.error(f"修改数值失败: {e}")
            return False

    def update_score_values(self, event_sheet_path: str,
                           score_multiplier: float = 1.0,
                           base_score_add: int = 0) -> Tuple[int, int]:
        """
        更新事件表中的分数相关数值

        Args:
            event_sheet_path: 事件表路径
            score_multiplier: 分数倍率
            base_score_add: 基础分数增加

        Returns:
            Tuple[修改数量, 失败数量]
        """
        try:
            root = self.parse_event_sheet(event_sheet_path)
            self._create_backup(event_sheet_path)

            success = 0
            failed = 0

            # 查找所有数值元素
            for elem in root.iter():
                if elem.text:
                    try:
                        value = float(elem.text)

                        # 检查是否像分数值
                        if value > 0 and value < 100000:
                            new_value = int(value * score_multiplier + base_score_add)
                            if new_value != int(value):
                                elem.text = str(new_value)
                                success += 1

                                self.modifications.append(EventModification(
                                    file_path=event_sheet_path,
                                    event_id="score_multiplier",
                                    description="分数倍率调整",
                                    parameter=elem.tag,
                                    old_value=value,
                                    new_value=new_value
                                ))

                    except (ValueError, TypeError):
                        pass

            # 保存
            tree = ET.ElementTree(root)
            tree.write(event_sheet_path, encoding='utf-8', xml_declaration=True)

            logger.info(f"分数更新完成: {success}处修改")
            return success, failed

        except Exception as e:
            logger.error(f"更新分数失败: {e}")
            return 0, 1

    def update_game_balance(self, config: GameBalanceConfig) -> int:
        """
        更新游戏平衡参数

        Args:
            config: 游戏平衡配置

        Returns:
            修改的事件表数量
        """
        modified_count = 0

        for event_sheet in self.event_sheets:
            try:
                root = self.parse_event_sheet(event_sheet)
                original_modified = len(self.modifications)

                # 更新各类型参数
                self._update_speed_parameters(root, config)
                self._update_reward_parameters(root, config)
                self._update_difficulty_parameters(root, config)
                self._update_ad_frequency(root, config)

                # 如果有修改
                if len(self.modifications) > original_modified:
                    self._create_backup(event_sheet)

                    # 保存
                    tree = ET.ElementTree(root)
                    tree.write(event_sheet, encoding='utf-8', xml_declaration=True)

                    modified_count += 1
                    logger.info(f"已更新事件表: {os.path.basename(event_sheet)}")

            except Exception as e:
                logger.error(f"更新事件表失败: {event_sheet} - {e}")

        return modified_count

    def _update_speed_parameters(self, root: ET.Element, config: GameBalanceConfig):
        """更新速度参数"""
        speed_patterns = ['speed', 'velocity', 'SetSpeed', 'SetX', 'SetY']

        for elem in root.iter():
            tag_lower = elem.tag.lower()

            for pattern in speed_patterns:
                if pattern in tag_lower and elem.text:
                    try:
                        value = float(elem.text)
                        if 'player' in str(elem.attrib).lower():
                            new_value = config.player_speed
                        elif 'enemy' in str(elem.attrib).lower():
                            new_value = config.enemy_speed * config.difficulty
                        else:
                            new_value = value * config.difficulty

                        if new_value != value:
                            elem.text = str(new_value)
                            self.modifications.append(EventModification(
                                file_path="",
                                event_id="speed_adjust",
                                description="速度参数调整",
                                parameter=elem.tag,
                                old_value=value,
                                new_value=new_value
                            ))

                    except (ValueError, TypeError):
                        pass

    def _update_reward_parameters(self, root: ET.Element, config: GameBalanceConfig):
        """更新奖励参数"""
        reward_patterns = ['reward', 'coin', 'score', 'point', '金币', '奖励']

        for elem in root.iter():
            tag_lower = elem.tag.lower()
            text_lower = (elem.text or '').lower()

            for pattern in reward_patterns:
                if pattern in tag_lower or pattern in text_lower:
                    if elem.text:
                        try:
                            value = float(elem.text)
                            new_value = int(value * config.reward_multiplier * config.coin_rate)

                            if new_value != int(value):
                                elem.text = str(new_value)
                                self.modifications.append(EventModification(
                                    file_path="",
                                    event_id="reward_adjust",
                                    description="奖励参数调整",
                                    parameter=elem.tag,
                                    old_value=value,
                                    new_value=new_value
                                ))

                        except (ValueError, TypeError):
                            pass

    def _update_difficulty_parameters(self, root: ET.Element, config: GameBalanceConfig):
        """更新难度参数"""
        # 难度调整通常涉及敌人数量、生成频率等
        difficulty_patterns = ['spawn', 'enemy', 'count', 'frequency', 'timer']

        for elem in root.iter():
            tag_lower = elem.tag.lower()

            for pattern in difficulty_patterns:
                if pattern in tag_lower and elem.text:
                    try:
                        value = float(elem.text)

                        # 某些值应该随难度增加
                        if value > 0:
                            new_value = value * (1 + (config.difficulty - 1) * 0.5)
                        else:
                            new_value = value

                        if abs(new_value - value) > 0.1:
                            elem.text = str(new_value)
                            self.modifications.append(EventModification(
                                file_path="",
                                event_id="difficulty_adjust",
                                description="难度参数调整",
                                parameter=elem.tag,
                                old_value=value,
                                new_value=new_value
                            ))

                    except (ValueError, TypeError):
                        pass

    def _update_ad_frequency(self, root: ET.Element, config: GameBalanceConfig):
        """更新广告触发频率"""
        ad_patterns = ['ad', 'advertisement', 'interstitial', 'rewardvideo']

        for elem in root.iter():
            tag_lower = elem.tag.lower()

            for pattern in ad_patterns:
                if pattern in tag_lower and elem.text:
                    try:
                        value = float(elem.text)

                        # 广告间隔应该随难度适当调整
                        if value > 0:
                            new_value = value / config.difficulty
                        else:
                            new_value = config.ad_frequency

                        if abs(new_value - value) > 1:
                            elem.text = str(int(new_value))
                            self.modifications.append(EventModification(
                                file_path="",
                                event_id="ad_frequency_adjust",
                                description="广告频率调整",
                                parameter=elem.tag,
                                old_value=value,
                                new_value=new_value
                            ))

                    except (ValueError, TypeError):
                        pass

    def add_variable(self, event_sheet_path: str, var_name: str,
                   var_type: str = "number", initial_value: Any = 0) -> bool:
        """
        在事件表中添加全局变量

        Args:
            event_sheet_path: 事件表路径
            var_name: 变量名
            var_type: 变量类型 (number/string/boolean)
            initial_value: 初始值

        Returns:
            bool: 添加是否成功
        """
        try:
            root = self.parse_event_sheet(event_sheet_path)

            # 查找或创建变量区域
            variables = root.find('.//{*}variables')
            if variables is None:
                variables = ET.SubElement(root, '{*}variables')

            # 创建新变量
            var_elem = ET.SubElement(variables, '{*}variable')
            var_elem.set('name', var_name)
            var_elem.set('type', var_type)
            var_elem.text = str(initial_value)

            self._create_backup(event_sheet_path)

            # 保存
            tree = ET.ElementTree(root)
            tree.write(event_sheet_path, encoding='utf-8', xml_declaration=True)

            self.modifications.append(EventModification(
                file_path=event_sheet_path,
                event_id="add_variable",
                description=f"添加变量{var_name}",
                parameter="variable",
                old_value=None,
                new_value={"name": var_name, "type": var_type, "value": initial_value}
            ))

            logger.info(f"已添加变量: {var_name} = {initial_value}")
            return True

        except Exception as e:
            logger.error(f"添加变量失败: {e}")
            return False

    def update_ad_config(self, ad_config: Dict[str, str]) -> int:
        """
        更新广告配置

        Args:
            ad_config: 广告配置字典

        Returns:
            修改的事件表数量
        """
        modified_count = 0

        for event_sheet in self.event_sheets:
            try:
                root = self.parse_event_sheet(event_sheet)
                original_modified = len(self.modifications)

                # 在变量或配置区域查找广告ID
                for elem in root.iter():
                    for attr, value in elem.attrib.items():
                        attr_lower = attr.lower()
                        value_lower = value.lower()

                        for ad_type, ad_id in ad_config.items():
                            if ad_type in attr_lower or ad_type in value_lower:
                                if ad_id and ad_id not in value:
                                    elem.set(attr, ad_id)
                                    self.modifications.append(EventModification(
                                        file_path=event_sheet,
                                        event_id="ad_config",
                                        description=f"更新{ad_type}配置",
                                        parameter=attr,
                                        old_value=value,
                                        new_value=ad_id
                                    ))

                if len(self.modifications) > original_modified:
                    self._create_backup(event_sheet)

                    tree = ET.ElementTree(root)
                    tree.write(event_sheet, encoding='utf-8', xml_declaration=True)

                    modified_count += 1

            except Exception as e:
                logger.error(f"更新广告配置失败: {event_sheet} - {e}")

        return modified_count

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
                json.dump({
                    "total_modifications": len(self.modifications),
                    "modifications": self.get_modifications()
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"修改日志已导出: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出修改日志失败: {e}")
            return False


def main():
    """主函数测试"""
    print("=" * 60)
    print("Construct3 Event Editor Test")
    print("Construct3事件表编辑器测试")
    print("=" * 60)
    print()

    print("使用示例:")
    print("""
    from event_editor import C3PEventEditor, GameBalanceConfig

    editor = C3PEventEditor('/path/to/extracted/c3p')

    # 创建游戏平衡配置
    config = GameBalanceConfig(
        click_reward=10,
        upgrade_cost_base=50,
        difficulty=1.5,
        coin_rate=2,
        ad_frequency=30
    )

    # 更新游戏平衡参数
    editor.update_game_balance(config)

    # 更新广告配置
    editor.update_ad_config({
        'tiktok_app_id': 'your_app_id',
        'tiktok_rewarded_id': 'your_rewarded_unit_id',
        'tiktok_interstitial_id': 'your_interstitial_unit_id'
    })

    # 添加自定义变量
    editor.add_variable('events1.uevents', 'CustomScore', 'number', 0)

    # 导出修改日志
    editor.export_modifications_log('event_modifications.json')
    """)


if __name__ == "__main__":
    main()
