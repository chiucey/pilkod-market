"""
Construct3 Game Planner - 高成瘾性游戏策划生成器

自动生成完整游戏策划方案，包含玩法设计、关卡体系、奖励机制等
"""

import random
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GameConcept:
    """游戏概念设计"""
    title: str = ""
    elevator_pitch: str = ""  # 电梯演讲
    target_audience: str = ""
    core_loop: str = ""  # 核心循环
    emotional_hook: str = ""  # 情感钩子


@dataclass
class GameMechanic:
    """游戏机制"""
    name: str
    description: str
    implementation: str  # 在Construct3中的实现方式
    addiction_factor: str  # 对成瘾性的贡献


@dataclass
class LevelDesign:
    """关卡设计"""
    level_number: int
    difficulty: float  # 0-1
    objectives: List[str]
    rewards: List[str]
    time_estimate: str


@dataclass
class RewardSystem:
    """奖励系统"""
    reward_type: str
    trigger_condition: str
    rarity: str  # common/rare/epic/legendary
    addiction_impact: str


class GamePlanner:
    """游戏策划生成器"""

    def __init__(self):
        self.game_categories = {
            "解压闯关": {
                "description": "通过重复操作释放压力，配合即时反馈",
                "examples": ["Flappy Bird", "Doodle Jump", "Helix Jump"],
                "core_mechanics": ["单指操作", "即时反馈", "无限重复", "高分挑战"],
                "emotional_drivers": ["成就感", "掌控感", "释放感"]
            },
            "合成养成": {
                "description": "通过数值积累和合成满足收集欲望",
                "examples": ["2048", "Threes!", "Merge Dragons"],
                "core_mechanics": ["滑动操作", "相同合成", "数值积累", "升级强化"],
                "emotional_drivers": ["收集欲", "成长感", "完美主义"]
            },
            "敏捷挑战": {
                "description": "通过速度和精准度挑战激发竞争心理",
                "examples": ["Geometry Dash", "Crossy Road", "Slither.io"],
                "core_mechanics": ["反应速度", "精准操作", "排行榜", "对战竞技"],
                "emotional_drivers": ["竞争欲", "挑战欲", "表现欲"]
            },
            "趣味竞技": {
                "description": "通过社交互动和对战满足社交需求",
                "examples": ["Agar.io", "Among Us", "Stumble Guys"],
                "core_mechanics": ["多人对战", "社交互动", "随机性", "团队合作"],
                "emotional_drivers": ["社交欲", "表现欲", "归属感"]
            },
            "放置收集": {
                "description": "通过长期目标和离线收益保持玩家黏性",
                "examples": ["Adventure Capitalist", "Egg, Inc.", "Realm of the Mad God"],
                "core_mechanics": ["点击收集", "升级强化", "离线收益", "自动运行"],
                "emotional_drivers": ["期待感", "成长感", "积累欲"]
            }
        }

    def generate_game_concept(self, category: str = None) -> GameConcept:
        """生成游戏概念"""
        if not category or category not in self.game_categories:
            category = random.choice(list(self.game_categories.keys()))

        cat_info = self.game_categories[category]

        concept = GameConcept()
        concept.title = self._generate_title(category)
        concept.elevator_pitch = f"一款{category}游戏，{cat_info['description']}，让玩家在{cat_info['emotional_drivers'][0]}中获得满足感。"
        concept.target_audience = self._generate_target_audience(category)
        concept.core_loop = self._generate_core_loop(category)
        concept.emotional_hook = self._generate_emotional_hook(category)

        return concept

    def _generate_title(self, category: str) -> str:
        """生成游戏名称"""
        prefixes = {
            "解压闯关": ["疯狂", "跳跃", "飞翔", "冲刺", "弹跳"],
            "合成养成": ["超级", "魔法", "进化", "融合", "神秘"],
            "敏捷挑战": ["极速", "极限", "热血", "街头", "街头"],
            "趣味竞技": ["大乱斗", "派对", "王者", "全民", "疯狂"],
            "放置收集": ["无限", "永恒", "财富", "帝国", "世界"]
        }
        suffixes = {
            "解压闯关": ["大冒险", "闯关王", "跳跳跳", "挑战赛", "冲刺"],
            "合成养成": ["合成大师", "进化论", "养成记", "数字王", "合并乐园"],
            "敏捷挑战": ["摩托", "跑酷", "赛车", "冲刺", "对决"],
            "趣味竞技": ["大乱斗", "派对游戏", "挑战赛", "接龙", "躲避球"],
            "放置收集": ["Idle", "放置王国", "金币大师", "挂机传奇", "自动收集"]
        }

        prefix = random.choice(prefixes.get(category, [""]))
        suffix = random.choice(suffixes.get(category, [""]))
        return f"{prefix}{suffix}"

    def _generate_target_audience(self, category: str) -> str:
        """生成目标受众"""
        audiences = {
            "解压闯关": "15-35岁，追求碎片娱乐、压力释放的玩家",
            "合成养成": "25-45岁，喜欢动脑思考、追求完美的玩家",
            "敏捷挑战": "15-30岁，追求刺激、喜欢竞争排行榜的玩家",
            "趣味竞技": "18-35岁，喜欢社交、朋友聚会的玩家",
            "放置收集": "25-50岁，时间碎片化、喜欢长期养成的玩家"
        }
        return audiences.get(category, "18-35岁休闲游戏玩家")

    def _generate_core_loop(self, category: str) -> str:
        """生成核心循环"""
        loops = {
            "解压闯关": "操作 → 反馈 → 评分 → 重复",
            "合成养成": "滑动 → 合并 → 升级 → 再滑动",
            "敏捷挑战": "挑战 → 失误/成功 → 重试 → 突破",
            "趣味竞技": "匹配 → 对战 → 胜利/失败 → 再匹配",
            "放置收集": "点击 → 收集 → 升级 → 自动收集"
        }
        return loops.get(category, "操作 → 反馈 → 重复")

    def _generate_emotional_hook(self, category: str) -> str:
        """生成情感钩子"""
        hooks = {
            "解压闯关": "\"再来一局，只用30秒！\" - 每局都是新的开始",
            "合成养成": "\"差一点就合成了！\" - 永远追求更高的数字",
            "敏捷挑战": "\"我能超过那个分数吗？\" - 排行榜的诱惑",
            "趣味竞技": "\"和朋友一起玩！\" - 社交娱乐的乐趣",
            "放置收集": "\"睡一觉就能赚好多！\" - 离线收益的惊喜"
        }
        return hooks.get(category, "")

    def generate_game_mechanics(self, category: str) -> List[GameMechanic]:
        """生成游戏机制"""
        mechanics_map = {
            "解压闯关": [
                GameMechanic("即时反馈", "每次操作立即有视觉和音效反馈", "Play sound + Set animation", "让玩家感到操作被响应"),
                GameMechanic("单指操作", "简单的一指操作即可游戏", "On Touch/Click → Set velocity", "降低上手门槛"),
                GameMechanic("高分挑战", "永远有更高分数可以追求", "Score + HighScore variable", "持续复玩动力"),
                GameMechanic("简短回合", "每局30秒-2分钟", "Game over condition", "适合碎片时间")
            ],
            "合成养成": [
                GameMechanic("数值积累", "数字不断增大带来满足感", "Tile.Value * 2", "成长快感"),
                GameMechanic("空间策略", "有限空间内最大化利用", "Grid collision detection", "策略深度"),
                GameMechanic("随机生成", "新方块位置随机", "random() position", "不确定性刺激"),
                GameMechanic("合成惊喜", "合成时特效和音效", "Particle effect", "视觉满足")
            ],
            "敏捷挑战": [
                GameMechanic("速度递增", "游戏速度逐渐加快", "Set speed + delta time", "挑战升级"),
                GameMechanic("精准控制", "精确的时机把握", "Collision offset", "技术含量"),
                GameMechanic("死亡重置", "一失误就重来", "On collision → Game Over", "紧张刺激"),
                GameMechanic("排行榜", "与全球玩家竞争", "Leaderboard plugin", "竞争动力")
            ],
            "放置收集": [
                GameMechanic("点击收益", "每次点击获得资源", "On click → Add resource", "即时反馈"),
                GameMechanic("升级强化", "消耗资源提升效率", "Upgrade cost scaling", "成长系统"),
                GameMechanic("离线收益", "关闭游戏也继续产出", "timestamp calculation", "长期黏性"),
                GameMechanic("成就系统", "达成目标获得奖励", "Achievement trigger", "目标驱动")
            ]
        }
        return mechanics_map.get(category, [])

    def generate_level_design(self, category: str, level_count: int = 50) -> List[LevelDesign]:
        """生成关卡设计"""
        levels = []

        if category == "解压闯关":
            for i in range(1, level_count + 1):
                difficulty = min(0.3 + (i / level_count) * 0.7, 1.0)
                levels.append(LevelDesign(
                    level_number=i,
                    difficulty=difficulty,
                    objectives=[f"到达终点", f"收集{i*10}金币", f"不超过{i*2}次失误"],
                    rewards=[f"{i*10}金币", f"解锁皮肤" if i % 10 == 0 else None, f"成就进度"],
                    time_estimate=f"{30 + i*2}秒"
                ))

        elif category == "合成养成":
            for i in range(1, level_count + 1):
                difficulty = min(0.2 + (i / level_count) * 0.8, 1.0)
                target_score = int(2048 * (1.5 ** i))
                levels.append(LevelDesign(
                    level_number=i,
                    difficulty=difficulty,
                    objectives=[f"达到{self._format_number(target_score)}分", "合成更高级方块", "保持至少2个空位"],
                    rewards=[f"解锁新主题" if i % 5 == 0 else None, "成就进度"],
                    time_estimate="无限时间"
                ))

        else:
            for i in range(1, level_count + 1):
                difficulty = min(0.2 + (i / level_count) * 0.8, 1.0)
                levels.append(LevelDesign(
                    level_number=i,
                    difficulty=difficulty,
                    objectives=[f"完成关卡目标", f"获得{3-i%3}星评价"],
                    rewards=["关卡解锁", "成就进度"],
                    time_estimate=f"{60 + i*5}秒"
                ))

        return levels

    def _format_number(self, num: int) -> str:
        """格式化大数字"""
        if num >= 1000000000:
            return f"{num/1000000000:.1f}B"
        elif num >= 1000000:
            return f"{num/1000000:.1f}M"
        elif num >= 1000:
            return f"{num/1000:.1f}K"
        return str(num)

    def generate_reward_system(self, category: str) -> List[RewardSystem]:
        """生成奖励系统"""
        rewards = []

        # 通用奖励
        rewards.append(RewardSystem("新手礼包", "首次登录", "common", "降低初期难度"))
        rewards.append(RewardSystem("每日签到", "每天登录", "common", "培养登录习惯"))
        rewards.append(RewardSystem("观看广告", "主动观看", "common", "变现+留存双赢"))

        # 分类专属奖励
        if category == "解压闯关":
            rewards.extend([
                RewardSystem("无伤通关", "零失误完成关卡", "rare", "技术炫耀"),
                RewardSystem("连击奖励", "连续穿越障碍", "common", "操作奖励"),
                RewardSystem("皮肤碎片", "游戏内收集", "epic", "收集动力")
            ])
        elif category == "合成养成":
            rewards.extend([
                RewardSystem("全合成成就", "合成2048/4096/8192", "epic", "终极目标"),
                RewardSystem("高分奖励", "打破个人记录", "common", "持续进步"),
                RewardSystem("主题解锁", "收集足够方块", "rare", "收集动力")
            ])
        elif category == "放置收集":
            rewards.extend([
                RewardSystem("离线双倍", "回归游戏", "epic", "惊喜感"),
                RewardSystem("升级折扣", "限时活动", "rare", "紧迫感"),
                RewardSystem("稀有升级", "特殊升级项目", "legendary", "追求目标")
            ])

        return rewards

    def generate_addiction_loop(self, category: str) -> Dict:
        """生成成瘾循环设计"""
        loops = {
            "解压闯关": {
                "immediate": "操作→即时反馈（音效+分数）→继续操作",
                "short_term": "每局30秒→高分挑战→再来一局",
                "medium_term": "解锁新角色→收集皮肤→成就系统",
                "long_term": "排行榜竞争→好友对战→长期排名"
            },
            "合成养成": {
                "immediate": "滑动→合并→数字变大→满足感",
                "short_term": "追求更高数字→差一点就合成了",
                "medium_term": "解锁新主题→成就收集",
                "long_term": "全合成挑战→全球排名"
            },
            "放置收集": {
                "immediate": "点击→资源增加→数值增长",
                "short_term": "升级强化→效率提升",
                "medium_term": "解锁新项目→更多升级",
                "long_term": "离线收益→长期积累"
            }
        }
        return loops.get(category, loops["解压闯关"])

    def generate_complete_design_doc(self, category: str = None) -> str:
        """生成完整设计文档"""
        if not category:
            category = random.choice(list(self.game_categories.keys()))

        cat_info = self.game_categories[category]
        concept = self.generate_game_concept(category)
        mechanics = self.generate_game_mechanics(category)
        rewards = self.generate_reward_system(category)
        addiction_loops = self.generate_addiction_loop(category)

        levels = self.generate_level_design(category, 20)

        doc = f'''# {concept.title} - 游戏设计文档

## 1. 游戏概述

### 1.1 电梯演讲
{concept.elevator_pitch}

### 1.2 目标受众
{concept.target_audience}

### 1.3 核心循环
{concept.core_loop}

### 1.4 情感钩子
{concept.emotional_hook}

---

## 2. 品类定位

**品类**: {category}
**描述**: {cat_info['description']}

**核心机制**: {"、".join(cat_info['core_mechanics'])}

**情感驱动**: {"、".join(cat_info['emotional_drivers'])}

---

## 3. 游戏机制

'''

        for mechanic in mechanics:
            doc += f'''### 3.X {mechanic.name}
- **描述**: {mechanic.description}
- **实现方式**: {mechanic.implementation}
- **成瘾贡献**: {mechanic.addiction_factor}

'''

        doc += '''---

## 4. 成瘾循环设计

### 即时循环
''' + addiction_loops["immediate"] + '''

### 短期循环
''' + addiction_loops["short_term"] + '''

### 中期循环
''' + addiction_loops["medium_term"] + '''

### 长期循环
''' + addiction_loops["long_term"] + '''

---

## 5. 关卡设计（示例）

'''

        for level in levels[:10]:
            doc += f'''### 第{level.level_number}关
- **难度**: {level.difficulty:.0%}
- **目标**: {"、".join(level.objectives)}
- **奖励**: {"、".join(filter(None, level.rewards))}
- **预计时间**: {level.time_estimate}

'''

        doc += '''---

## 6. 奖励系统

| 奖励名称 | 触发条件 | 稀有度 | 成瘾影响 |
|---------|---------|--------|---------|
'''
        for reward in rewards:
            doc += f"| {reward.reward_type} | {reward.trigger_condition} | {reward.rarity} | {reward.addiction_impact} |\n"

        doc += '''

---

## 7. Construct3实现要点

### 7.1 项目设置
- 画布尺寸: 540x960 (竖屏)
- 帧率: 60 FPS
- 导出格式: HTML5

### 7.2 推荐插件
- Touch/Keyboard input
- Audio
- Particle
- Local Storage (存档)
- Platform behavior (物理)

### 7.3 性能优化
- 对象池复用
- 及时销毁不需要的对象
- 合理使用粒子效果
- 优化碰撞检测

---

## 8. 发布建议

### 目标平台
- TikTok小游戏
- Facebook Instant Games
- 独立HTML5发布

### 变现方式
- 激励视频广告（推荐）
- 插屏广告
- Banner广告

### 关键指标
- D1留存: >40%
- D7留存: >15%
- 平均游戏时长: >3分钟
- 人均广告观看: >3次

'''

        return doc


def main():
    """主函数"""
    print("=" * 60)
    print("Construct3 Game Planner - 游戏策划生成器")
    print("=" * 60)
    print()

    planner = GamePlanner()

    # 生成设计文档
    print("Generating game design document...")
    doc = planner.generate_complete_design_doc("解压闯关")

    print(doc[:2000])
    print("...")
    print()
    print(f"Total document length: {len(doc)} characters")


if __name__ == "__main__":
    main()
