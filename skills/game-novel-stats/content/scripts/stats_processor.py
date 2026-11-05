#!/usr/bin/env python3
"""
游戏小说数值处理脚本
功能：角色创建、数值计算、变更追踪、增长分析
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class StatChange:
    """数值变更记录"""
    chapter: int
    event: str
    stat: str
    change_type: str  # absolute, percentage, multiplier
    value: float
    old_value: float
    new_value: float

@dataclass
class Buff:
    """增益/减益状态"""
    name: str
    effect: str
    duration: str  # 章节数或永久
    stat_affected: str
    value: float

@dataclass
class Character:
    """角色数据模型"""
    character_id: str
    name: str
    role: str  # protagonist, antagonist, supporting, npc
    realm: str
    level: int
    exp: int
    exp_threshold: int
    base_stats: Dict[str, float]
    elements: Dict[str, float]
    special: Dict[str, float]
    buffs: List[Buff]
    debuffs: List[Buff]
    history: List[Dict]

    def to_dict(self) -> Dict:
        return {
            "character_id": self.character_id,
            "name": self.name,
            "role": self.role,
            "realm": self.realm,
            "level": self.level,
            "exp": self.exp,
            "exp_threshold": self.exp_threshold,
            "base_stats": self.base_stats,
            "elements": self.elements,
            "special": self.special,
            "buffs": [asdict(b) for b in self.buffs],
            "debuffs": [asdict(d) for d in self.debuffs],
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Character':
        return cls(
            character_id=data["character_id"],
            name=data["name"],
            role=data["role"],
            realm=data["realm"],
            level=data["level"],
            exp=data["exp"],
            exp_threshold=data["exp_threshold"],
            base_stats=data["base_stats"],
            elements=data.get("elements", {}),
            special=data.get("special", {}),
            buffs=[Buff(**b) for b in data.get("buffs", [])],
            debuffs=[Buff(**d) for d in data.get("debuffs", [])],
            history=data.get("history", [])
        )

class StatsProcessor:
    """数值处理器"""

    # 境界层级定义
    REALM_TIERS = [
        "炼气期", "筑基期", "金丹期", "元婴期",
        "化神期", "炼虚期", "合体期", "大乘期", "渡劫期", "真仙"
    ]

    # 默认属性模板
    DEFAULT_STATS = {
        "life": 1000,      # 生命值
        "mana": 500,       # 法力值
        "stamina": 800,    # 体力值
        "attack": 100,     # 攻击力
        "defense": 80,     # 防御力
        "speed": 90,       # 速度
        "crit_rate": 0.05, # 暴击率
        "crit_damage": 1.5 # 暴击伤害
    }

    DEFAULT_SPECIAL = {
        "luck": 10,
        "charisma": 10,
        "perception": 10,
        "comprehension": 10
    }

    # 境界加成倍率
    REALM_MULTIPLIERS = {
        "炼气期": 1.0,
        "筑基期": 1.5,
        "金丹期": 2.0,
        "元婴期": 3.0,
        "化神期": 4.5,
        "炼虚期": 6.0,
        "合体期": 8.0,
        "大乘期": 11.0,
        "渡劫期": 15.0,
        "真仙": 20.0
    }

    def __init__(self, data_dir: str = "./character_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.characters: Dict[str, Character] = {}
        self.load_all()

    def load_all(self):
        """加载所有角色数据"""
        for file in self.data_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    char = Character.from_dict(data)
                    self.characters[char.character_id] = char
            except Exception as e:
                print(f"加载失败 {file}: {e}")

    def save_character(self, char: Character):
        """保存角色数据"""
        file_path = self.data_dir / f"{char.character_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(char.to_dict(), f, ensure_ascii=False, indent=2)
        self.characters[char.character_id] = char

    def create_character(
        self,
        character_id: str,
        name: str,
        role: str = "protagonist",
        realm: str = "炼气期",
        level: int = 1,
        custom_stats: Optional[Dict[str, float]] = None,
        custom_special: Optional[Dict[str, float]] = None
    ) -> Character:
        """创建新角色"""
        base_stats = custom_stats or self.DEFAULT_STATS.copy()
        special = custom_special or self.DEFAULT_SPECIAL.copy()
        exp_threshold = self._calculate_exp_threshold(level)

        char = Character(
            character_id=character_id,
            name=name,
            role=role,
            realm=realm,
            level=level,
            exp=0,
            exp_threshold=exp_threshold,
            base_stats=base_stats,
            elements={},
            special=special,
            buffs=[],
            debuffs=[],
            history=[{
                "chapter": 0,
                "event": "角色创建",
                "description": f"创建{role}角色{name}"
            }]
        )
        self.save_character(char)
        return char

    def _calculate_exp_threshold(self, level: int) -> int:
        """计算升级所需经验值（指数增长）"""
        base_exp = 100
        return int(base_exp * (1.5 ** level))

    def _get_realm_index(self, realm: str) -> int:
        """获取境界索引（支持带小境界的名称如"筑基初期"）"""
        # 先精确匹配
        if realm in self.REALM_TIERS:
            return self.REALM_TIERS.index(realm)
        # 再模糊匹配（取前几个字符）
        for i, tier in enumerate(self.REALM_TIERS):
            if realm.startswith(tier) or tier.startswith(realm[:2]):
                return i
        # 默认返回最低境界
        return 0

    def _get_realm_multiplier(self, realm: str) -> float:
        """获取境界加成倍率"""
        return self.REALM_MULTIPLIERS.get(realm, 1.0)

    def get_effective_stats(self, char: Character) -> Dict[str, float]:
        """计算有效属性（含境界加成和buff/debuff）"""
        multiplier = self._get_realm_multiplier(char.realm)
        effective = {}

        # 基础属性（含境界加成）
        for stat, value in char.base_stats.items():
            effective[stat] = value * multiplier

        # 特殊属性（不含境界加成）
        for stat, value in char.special.items():
            effective[stat] = value

        # 应用buff
        for buff in char.buffs:
            if buff.stat_affected in effective:
                if '+' in buff.effect:
                    effective[buff.stat_affected] *= (1 + buff.value)
                elif '-' in buff.effect:
                    effective[buff.stat_affected] *= (1 - buff.value)

        # 应用debuff
        for debuff in char.debuffs:
            if debuff.stat_affected in effective:
                effective[debuff.stat_affected] *= (1 - debuff.value)

        return effective

    def calculate_damage(
        self,
        attacker: Character,
        defender: Character,
        base_damage: float
    ) -> Dict[str, Any]:
        """计算战斗伤害"""
        att_eff = self.get_effective_stats(attacker)
        def_eff = self.get_effective_stats(defender)

        attack = att_eff.get("attack", 100)
        defense = def_eff.get("defense", 80)

        # 伤害计算：(攻击力 - 防御力/2) × 技能倍率
        raw_damage = max(attack - defense / 2, attack * 0.1)

        # 暴击判定
        crit_rate = att_eff.get("crit_rate", 0.05)
        crit_damage = att_eff.get("crit_damage", 1.5)
        is_crit = __import__('random').random() < crit_rate
        final_damage = raw_damage * crit_damage if is_crit else raw_damage

        return {
            "raw_damage": round(raw_damage, 2),
            "final_damage": round(final_damage, 2),
            "is_critical": is_crit,
            "attacker": attacker.name,
            "defender": defender.name
        }

    def apply_stat_change(
        self,
        char: Character,
        chapter: int,
        event: str,
        stat: str,
        change_type: str,
        value: float,
        is_permanent: bool = True
    ) -> Dict[str, Any]:
        """应用数值变更"""
        stat_category = self._get_stat_category(stat)
        old_value = self._get_stat_value(char, stat)

        if change_type == "absolute":
            new_value = old_value + value
        elif change_type == "percentage":
            new_value = old_value * (1 + value)
        elif change_type == "multiplier":
            new_value = old_value * value
        else:
            raise ValueError(f"未知的变更类型: {change_type}")

        new_value = max(0, new_value)  # 不允许负值

        # 更新数值
        if stat_category == "base":
            char.base_stats[stat] = new_value
        elif stat_category == "special":
            char.special[stat] = new_value
        elif stat_category == "element":
            if stat not in char.elements:
                char.elements[stat] = 0
            char.elements[stat] = new_value

        # 记录历史
        history_entry = {
            "chapter": chapter,
            "event": event,
            "stat": stat,
            "change_type": change_type,
            "value": value,
            "old_value": old_value,
            "new_value": round(new_value, 2)
        }
        char.history.append(history_entry)

        self.save_character(char)

        return {
            "stat": stat,
            "old_value": old_value,
            "new_value": round(new_value, 2),
            "change": round(new_value - old_value, 2),
            "change_percent": round((new_value / old_value - 1) * 100, 2) if old_value != 0 else 0
        }

    def _get_stat_category(self, stat: str) -> str:
        """获取属性类别"""
        if stat in self.DEFAULT_STATS:
            return "base"
        elif stat in self.DEFAULT_SPECIAL:
            return "special"
        else:
            return "element"

    def _get_stat_value(self, char: Character, stat: str) -> float:
        """获取属性当前值"""
        if stat in char.base_stats:
            return char.base_stats[stat]
        elif stat in char.special:
            return char.special[stat]
        elif stat in char.elements:
            return char.elements[stat]
        return 0

    def add_exp(self, char: Character, chapter: int, exp_gained: int) -> Dict[str, Any]:
        """添加经验值并检查升级"""
        char.exp += exp_gained

        level_ups = 0
        while char.exp >= char.exp_threshold:
            char.exp -= char.exp_threshold
            char.level += 1
            char.exp_threshold = self._calculate_exp_threshold(char.level)
            level_ups += 1

        history_entry = {
            "chapter": chapter,
            "event": "获得经验",
            "exp_gained": exp_gained,
            "current_exp": char.exp,
            "level_ups": level_ups
        }
        char.history.append(history_entry)
        self.save_character(char)

        result = {
            "exp_gained": exp_gained,
            "current_exp": char.exp,
            "exp_threshold": char.exp_threshold,
            "level_ups": level_ups
        }

        if level_ups > 0:
            result["new_level"] = char.level
            result["message"] = f"恭喜！{char.name} 升到 {char.level} 级！"

        return result

    def realm_breakthrough(
        self,
        char: Character,
        chapter: int,
        new_realm: str
    ) -> Dict[str, Any]:
        """境界突破"""
        old_realm = char.realm
        old_index = self._get_realm_index(old_realm)
        new_index = self._get_realm_index(new_realm)

        if new_index <= old_index:
            return {"success": False, "message": "新境界不能低于或等于当前境界"}

        # 属性暴涨（突破时）
        growth_rate = 1.5  # 突破时属性增长50%
        for stat in char.base_stats:
            char.base_stats[stat] *= growth_rate

        char.realm = new_realm

        history_entry = {
            "chapter": chapter,
            "event": "境界突破",
            "old_realm": old_realm,
            "new_realm": new_realm,
            "growth_rate": f"+{(growth_rate-1)*100}%"
        }
        char.history.append(history_entry)
        self.save_character(char)

        return {
            "success": True,
            "old_realm": old_realm,
            "new_realm": new_realm,
            "growth_rate": f"+{(growth_rate-1)*100}%",
            "message": f"恭喜！{char.name} 从 {old_realm} 突破至 {new_realm}！"
        }

    def add_buff(
        self,
        char: Character,
        name: str,
        effect: str,
        duration: str,
        stat_affected: str,
        value: float,
        is_debuff: bool = False
    ) -> Dict[str, Any]:
        """添加buff/debuff"""
        buff = Buff(
            name=name,
            effect=effect,
            duration=duration,
            stat_affected=stat_affected,
            value=value
        )

        if is_debuff:
            char.debuffs.append(buff)
            target_list = char.debuffs
        else:
            char.buffs.append(buff)
            target_list = char.buffs

        self.save_character(char)
        buff_type = "debuff" if is_debuff else "buff"
        return {
            "success": True,
            "type": buff_type,
            "name": name,
            "stat_affected": stat_affected,
            "value": value,
            "duration": duration
        }

    def remove_buff(
        self,
        char: Character,
        buff_name: str,
        is_debuff: bool = False
    ) -> Dict[str, Any]:
        """移除buff/debuff"""
        target_list = char.debuffs if is_debuff else char.buffs
        original_length = len(target_list)
        char.debuffs = [b for b in char.debuffs if b.name != buff_name] if is_debuff else \
                       [b for b in char.buffs if b.name != buff_name]

        if len(target_list) == original_length:
            return {"success": False, "message": f"未找到 {buff_name}"}

        self.save_character(char)
        return {"success": True, "removed": buff_name}

    def get_character_summary(self, char: Character) -> Dict[str, Any]:
        """获取角色摘要"""
        effective = self.get_effective_stats(char)
        return {
            "id": char.character_id,
            "name": char.name,
            "role": char.role,
            "realm": char.realm,
            "level": char.level,
            "exp": f"{char.exp}/{char.exp_threshold}",
            "effective_stats": {k: round(v, 2) for k, v in effective.items()},
            "active_buffs": len(char.buffs),
            "active_debuffs": len(char.debuffs),
            "history_count": len(char.history)
        }

    def analyze_growth_curve(
        self,
        char: Character,
        target_chapters: int = 100
    ) -> Dict[str, Any]:
        """分析增长曲线"""
        # 基于历史计算平均增长率
        stat_growth = {}
        for entry in char.history:
            if "stat" in entry and entry.get("chapter", 0) > 0:
                stat = entry["stat"]
                if stat not in stat_growth:
                    stat_growth[stat] = []
                stat_growth[stat].append(entry.get("new_value", 0))

        growth_analysis = {}
        for stat, values in stat_growth.items():
            if len(values) >= 2:
                total_growth = (values[-1] / values[0] - 1) * 100
                growth_analysis[stat] = {
                    "start_value": values[0],
                    "current_value": values[-1],
                    "total_growth_percent": round(total_growth, 2),
                    "data_points": len(values)
                }

        # 预测目标章节数值
        predictions = {}
        if growth_analysis:
            for stat in char.base_stats:
                if stat in growth_analysis:
                    data_points = growth_analysis[stat]["data_points"]
                    growth_rate = growth_analysis[stat]["total_growth_percent"] / max(data_points - 1, 1)
                    predicted_value = char.base_stats[stat] * (1 + growth_rate / 100) ** target_chapters
                    predictions[stat] = round(predicted_value, 2)

        return {
            "current_stats": char.base_stats,
            "growth_analysis": growth_analysis,
            "target_chapters": target_chapters,
            "predicted_values": predictions,
            "recommendations": self._generate_growth_recommendations(char, growth_analysis)
        }

    def _generate_growth_recommendations(
        self,
        char: Character,
        growth_analysis: Dict
    ) -> List[str]:
        """生成增长建议"""
        recommendations = []

        if not growth_analysis:
            recommendations.append("当前数据不足，建议继续记录更多数值变化")
            return recommendations

        for stat, data in growth_analysis.items():
            if data["total_growth_percent"] < 50:
                recommendations.append(f"{stat}增长较慢(+{data['total_growth_percent']}%)，可考虑增加相关奇遇或修炼")
            elif data["total_growth_percent"] > 300:
                recommendations.append(f"{stat}增长过快(+{data['total_growth_percent']}%)，建议增加平衡机制")

        return recommendations

# 命令行接口
def main():
    import argparse
    parser = argparse.ArgumentParser(description="游戏小说数值处理工具")
    parser.add_argument("action", choices=["create", "show", "add-exp", "change-stat", "breakthrough", "analyze"])
    parser.add_argument("--id", help="角色ID")
    parser.add_argument("--name", help="角色名称")
    parser.add_argument("--role", default="protagonist", help="角色类型")
    parser.add_argument("--realm", default="炼气期", help="境界")
    parser.add_argument("--level", type=int, default=1, help="等级")
    parser.add_argument("--chapter", type=int, default=1, help="章节")
    parser.add_argument("--event", help="事件描述")
    parser.add_argument("--stat", help="属性名")
    parser.add_argument("--change-type", choices=["absolute", "percentage", "multiplier"], default="absolute")
    parser.add_argument("--value", type=float, help="变更值")
    parser.add_argument("--exp", type=int, help="经验值")
    parser.add_argument("--new-realm", help="新境界")
    parser.add_argument("--data-dir", default="./character_data", help="数据目录")

    args = parser.parse_args()
    processor = StatsProcessor(args.data_dir)

    if args.action == "create":
        if not args.id or not args.name:
            print("错误: create 需要 --id 和 --name")
            return
        char = processor.create_character(args.id, args.name, args.role, args.realm, args.level)
        print(f"角色 {char.name} 创建成功!")

    elif args.action == "show":
        if not args.id:
            print("错误: show 需要 --id")
            return
        char = processor.characters.get(args.id)
        if char:
            summary = processor.get_character_summary(char)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
        else:
            print(f"未找到角色 {args.id}")

    elif args.action == "add-exp":
        if not args.id or not args.exp:
            print("错误: add-exp 需要 --id 和 --exp")
            return
        char = processor.characters.get(args.id)
        if char:
            result = processor.add_exp(char, args.chapter, args.exp)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未找到角色 {args.id}")

    elif args.action == "change-stat":
        if not all([args.id, args.stat, args.value is not None]):
            print("错误: change-stat 需要 --id, --stat, --value")
            return
        char = processor.characters.get(args.id)
        if char:
            result = processor.apply_stat_change(
                char, args.chapter, args.event or "数值变更",
                args.stat, args.change_type, args.value
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未找到角色 {args.id}")

    elif args.action == "breakthrough":
        if not all([args.id, args.new_realm]):
            print("错误: breakthrough 需要 --id 和 --new-realm")
            return
        char = processor.characters.get(args.id)
        if char:
            result = processor.realm_breakthrough(char, args.chapter, args.new_realm)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未找到角色 {args.id}")

    elif args.action == "analyze":
        if not args.id:
            print("错误: analyze 需要 --id")
            return
        char = processor.characters.get(args.id)
        if char:
            result = processor.analyze_growth_curve(char)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"未找到角色 {args.id}")

if __name__ == "__main__":
    main()
