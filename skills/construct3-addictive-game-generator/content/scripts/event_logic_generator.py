"""
Construct3 Event Logic Generator
Construct3事件逻辑生成器

自动生成各类高成瘾游戏的完整事件表代码
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json


@dataclass
class EventCondition:
    """事件条件"""
    object_name: str
    condition: str
    comparison: str = None
    value: Any = None


@dataclass
class EventAction:
    """事件动作"""
    action: str
    target: str = None
    value: Any = None


@dataclass
class GameEvent:
    """游戏事件"""
    name: str
    description: str = ""
    conditions: List[EventCondition] = None
    actions: List[EventAction] = None
    group: str = "Main"


class EventLogicGenerator:
    """Construct3事件逻辑生成器"""

    def __init__(self):
        self.events: List[GameEvent] = []
        self.event_sheet_name = "Main Events"

    def add_event(self, event: GameEvent):
        """添加事件"""
        self.events.append(event)

    def generate_flappy_bird_events(self) -> List[GameEvent]:
        """生成Flappy Bird游戏事件"""
        events = []

        # 玩家输入 - 跳跃
        events.append(GameEvent(
            name="Player Jump - Touch/Click",
            description="玩家触摸/点击屏幕时小鸟向上飞跃",
            conditions=[
                EventCondition("Touch", "On touched object", "GameLayer"),
            ],
            actions=[
                EventAction("Set velocity Y", "Bird", -600),
                EventAction("Set animation", "Bird", "Flap"),
                EventAction("Play sound", "Flap"),
            ],
            group="Player Input"
        ))

        # 玩家输入 - 空格键
        events.append(GameEvent(
            name="Player Jump - Keyboard",
            description="玩家按空格键时小鸟向上飞跃",
            conditions=[
                EventCondition("Keyboard", "On key pressed", value="Space"),
            ],
            actions=[
                EventAction("Set velocity Y", "Bird", -600),
                EventAction("Set animation", "Bird", "Flap"),
            ],
            group="Player Input"
        ))

        # 重力影响
        events.append(GameEvent(
            name="Gravity Effect",
            description="持续应用重力使小鸟下落",
            conditions=[],
            actions=[
                EventAction("Add to velocity Y", "Bird", 15),
            ],
            group="Physics"
        ))

        # 管道生成
        events.append(GameEvent(
            name="Spawn Pipes",
            description="定时在右侧生成管道",
            conditions=[
                EventCondition("System", "Every X seconds", value=2.0),
            ],
            actions=[
                EventAction("Create object", "PipeTop", "PipesSpawner", 0, 0),
                EventAction("Create object", "PipeBottom", "PipesSpawner", 0, 0),
                EventAction("Set Y position", "PipeTop", "random(100,400)"),
                EventAction("Set Y position", "PipeBottom", "PipeTop.Y + 200"),
                EventAction("Start timer", "PipeMovement"),
            ],
            group="Obstacles"
        ))

        # 管道移动
        events.append(GameEvent(
            name="Move Pipes",
            description="管道持续向左移动",
            conditions=[
                EventCondition("Pipes", "On collision with", "PipesSpawner"),
            ],
            actions=[
                EventAction("Set velocity X", "Pipes", -200),
            ],
            group="Obstacles"
        ))

        # 碰撞检测 - 障碍物
        events.append(GameEvent(
            name="Collision - Obstacle",
            description="小鸟碰到管道时游戏结束",
            conditions=[
                EventCondition("Bird", "On collision with", "Pipes"),
            ],
            actions=[
                EventAction("Set game state", value="GameOver"),
                EventAction("Stop all movements"),
                EventAction("Play sound", "Hit"),
                EventAction("Set animation", "Bird", "Die"),
                EventAction("Wait", value=0.5),
                EventAction("Go to scene", "GameOver"),
            ],
            group="Collision"
        ))

        # 碰撞检测 - 边界
        events.append(GameEvent(
            name="Collision - Boundaries",
            description="小鸟超出屏幕边界时游戏结束",
            conditions=[
                EventCondition("Bird", "Y >", value="LayoutHeight"),
            ],
            actions=[
                EventAction("Set game state", value="GameOver"),
                EventAction("Go to scene", "GameOver"),
            ],
            group="Collision"
        ))

        # 小鸟碰到顶部
        events.append(GameEvent(
            name="Collision - Top Boundary",
            description="小鸟碰到屏幕顶部",
            conditions=[
                EventCondition("Bird", "Y <", value="0"),
            ],
            actions=[
                EventAction("Set Y position", "Bird", 0),
            ],
            group="Collision"
        ))

        # 计分
        events.append(GameEvent(
            name="Score Point",
            description="小鸟穿过管道间隙时增加分数",
            conditions=[
                EventCondition("Bird", "On collision with", "ScoreZone"),
            ],
            actions=[
                EventAction("Add to variable", "Score", 1),
                EventAction("Play sound", "Point"),
                EventAction("Create object", "ScorePopup", "ScoreZone.X", "ScoreZone.Y"),
                EventAction("Destroy", "ScoreZone"),
            ],
            group="Scoring"
        ))

        # 难度递增
        events.append(GameEvent(
            name="Increase Difficulty",
            description="分数达到一定值时增加难度",
            conditions=[
                EventCondition("Score", ">=", value=10),
                EventCondition("DifficultyLevel", "<", value=2),
            ],
            actions=[
                EventAction("Set variable", "DifficultyLevel", 2),
                EventAction("Set pipe speed", value=250),
            ],
            group="Difficulty"
        ))

        events.append(GameEvent(
            name="Increase Difficulty - Level 3",
            description="更高难度",
            conditions=[
                EventCondition("Score", ">=", value=25),
                EventCondition("DifficultyLevel", "<", value=3),
            ],
            actions=[
                EventAction("Set variable", "DifficultyLevel", 3),
                EventAction("Set pipe speed", value=300),
            ],
            group="Difficulty"
        ))

        return events

    def generate_2048_events(self) -> List[GameEvent]:
        """生成2048合成游戏事件"""
        events = []

        # 键盘输入 - 向左
        events.append(GameEvent(
            name="Input - Swipe Left",
            description="玩家向左滑动时所有方块左移并合并",
            conditions=[
                EventCondition("Touch", "On swipe gesture", value="Left"),
                EventCondition("GameState", "=", value="Playing"),
            ],
            actions=[
                EventAction("Call function", "MoveLeft"),
                EventAction("Wait", value=0.2),
                EventAction("Call function", "SpawnNewTile"),
            ],
            group="Input"
        ))

        # 键盘输入 - 向右
        events.append(GameEvent(
            name="Input - Swipe Right",
            description="玩家向右滑动时所有方块右移并合并",
            conditions=[
                EventCondition("Touch", "On swipe gesture", value="Right"),
                EventCondition("GameState", "=", value="Playing"),
            ],
            actions=[
                EventAction("Call function", "MoveRight"),
                EventAction("Wait", value=0.2),
                EventAction("Call function", "SpawnNewTile"),
            ],
            group="Input"
        ))

        # 键盘输入 - 向上
        events.append(GameEvent(
            name="Input - Swipe Up",
            description="玩家向上滑动时所有方块上移并合并",
            conditions=[
                EventCondition("Touch", "On swipe gesture", value="Up"),
                EventCondition("GameState", "=", value="Playing"),
            ],
            actions=[
                EventAction("Call function", "MoveUp"),
                EventAction("Wait", value=0.2),
                EventAction("Call function", "SpawnNewTile"),
            ],
            group="Input"
        ))

        # 键盘输入 - 向下
        events.append(GameEvent(
            name="Input - Swipe Down",
            description="玩家向下滑动时所有方块下移并合并",
            conditions=[
                EventCondition("Touch", "On swipe gesture", value="Down"),
                EventCondition("GameState", "=", value="Playing"),
            ],
            actions=[
                EventAction("Call function", "MoveDown"),
                EventAction("Wait", value=0.2),
                EventAction("Call function", "SpawnNewTile"),
            ],
            group="Input"
        ))

        # 方块合并检测
        events.append(GameEvent(
            name="Merge Detection",
            description="相同数字的方块合并",
            conditions=[
                EventCondition("Tiles", "Overlapping", "Tiles"),
                EventCondition("Tiles.Value", "=", "Tiles.Value"),
            ],
            actions=[
                EventAction("Destroy", "Tiles"),
                EventAction("Set value", "Tiles.Value", "Tiles.Value * 2"),
                EventAction("Add to Score", "Tiles.Value"),
                EventAction("Play sound", "Merge"),
            ],
            group="Game Logic"
        ))

        # 游戏结束检测
        events.append(GameEvent(
            name="Game Over Check",
            description="无法移动时游戏结束",
            conditions=[
                EventCondition("System", "Every X seconds", value=0.5),
            ],
            actions=[
                EventAction("Call function", "CheckGameOver"),
            ],
            group="Game Logic"
        ))

        # 胜利检测
        events.append(GameEvent(
            name="Victory Check",
            description="合成2048时触发胜利",
            conditions=[
                EventCondition("Tiles", "Value =", value=2048),
            ],
            actions=[
                EventAction("Set game state", value="Victory"),
                EventAction("Show victory popup"),
                EventAction("Play sound", "Victory"),
            ],
            group="Game Logic"
        ))

        return events

    def generate_candy_crush_events(self) -> List[GameEvent]:
        """生成Candy Crush消除游戏事件"""
        events = []

        # 选择糖果
        events.append(GameEvent(
            name="Select Candy",
            description="玩家点击选中糖果",
            conditions=[
                EventCondition("Candy", "On clicked"),
            ],
            actions=[
                EventAction("Set selected", "Candy", True),
                EventAction("Set animation", "Candy", "Selected"),
            ],
            group="Selection"
        ))

        # 交换糖果
        events.append(GameEvent(
            name="Swap Candies",
            description="点击相邻糖果进行交换",
            conditions=[
                EventCondition("Candy", "On clicked"),
                EventCondition("SelectedCandy", "Is not empty"),
            ],
            actions=[
                EventAction("Call function", "SwapCandies"),
            ],
            group="Selection"
        ))

        # 匹配检测
        events.append(GameEvent(
            name="Match Detection",
            description="检测3个或更多相同糖果相连",
            conditions=[
                EventCondition("Candy", "Is adjacent to", "Candy"),
                EventCondition("Candy.Type", "=", "Candy.Type"),
            ],
            actions=[
                EventAction("Call function", "CheckMatch"),
            ],
            group="Matching"
        ))

        # 消除糖果
        events.append(GameEvent(
            name="Eliminate Candies",
            description="符合条件的糖果被消除",
            conditions=[
                EventCondition("MatchCount", ">=", value=3),
            ],
            actions=[
                EventAction("Play animation", "Candy", "Explode"),
                EventAction("Wait", value=0.3),
                EventAction("Destroy", "Candy"),
                EventAction("Add to Score", "MatchCount * 10"),
                EventAction("Play sound", "Pop"),
            ],
            group="Matching"
        ))

        # 糖果下落
        events.append(GameEvent(
            name="Candy Fall",
            description="消除后上方糖果下落填充空位",
            conditions=[
                EventCondition("Candy", "Y <", value="Hole.Y"),
            ],
            actions=[
                EventAction("Set velocity Y", "Candy", 500),
            ],
            group="Physics"
        ))

        # 生成新糖果
        events.append(GameEvent(
            name="Spawn New Candies",
            description="从顶部生成新糖果",
            conditions=[
                EventCondition("System", "CandyCount <", value=64),
            ],
            actions=[
                EventAction("Create object", "Candy", "TopSpawner", 0, 0),
                EventAction("Set Y", "Candy", -50),
            ],
            group="Spawning"
        ))

        # 关卡目标检测
        events.append(GameEvent(
            name="Level Target Check",
            description="检查是否达成关卡目标",
            conditions=[
                EventCondition("Score", ">=", "LevelTarget"),
            ],
            actions=[
                EventAction("Set game state", value="LevelComplete"),
                EventAction("Show level complete popup"),
                EventAction("Play sound", "LevelComplete"),
            ],
            group="Level"
        ))

        # 步数耗尽
        events.append(GameEvent(
            name="Out of Moves",
            description="步数用尽但未达成目标",
            conditions=[
                EventCondition("Moves", "=", value=0),
                EventCondition("Score", "<", "LevelTarget"),
            ],
            actions=[
                EventAction("Set game state", value="LevelFailed"),
                EventAction("Show game over popup"),
            ],
            group="Level"
        ))

        return events

    def generate_idle_clicker_events(self) -> List[GameEvent]:
        """生成放置挂机游戏事件"""
        events = []

        # 点击主按钮
        events.append(GameEvent(
            name="Main Click",
            description="玩家点击主按钮获得资源",
            conditions=[
                EventCondition("ClickButton", "On clicked"),
            ],
            actions=[
                EventAction("Add to Resource", "ClickValue"),
                EventAction("Play sound", "Click"),
                EventAction("Create particle effect", "ClickButton"),
                EventAction("Set animation", "ClickButton", "Pressed"),
                EventAction("Wait", value=0.1),
                EventAction("Set animation", "ClickButton", "Normal"),
            ],
            group="Clicking"
        ))

        # 自动产出
        events.append(GameEvent(
            name="Auto Production",
            description="定时自动产出资源",
            conditions=[
                EventCondition("System", "Every X seconds", value=1.0),
            ],
            actions=[
                EventAction("Add to Resource", "AutoProductionRate"),
                EventAction("Update UI"),
            ],
            group="Auto"
        ))

        # 升级按钮
        events.append(GameEvent(
            name="Purchase Upgrade",
            description="购买升级项目",
            conditions=[
                EventCondition("UpgradeButton", "On clicked"),
                EventCondition("Resource", ">=", "UpgradeCost"),
            ],
            actions=[
                EventAction("Subtract from Resource", "UpgradeCost"),
                EventAction("Add to ClickValue", "UpgradeBonus"),
                EventAction("Add to AutoProductionRate", "UpgradeAutoBonus"),
                EventAction("Multiply UpgradeCost", 1.5),
                EventAction("Play sound", "Upgrade"),
            ],
            group="Upgrades"
        ))

        # 离线收益计算
        events.append(GameEvent(
            name="Offline Earnings",
            description="玩家返回时计算离线收益",
            conditions=[
                EventCondition("System", "On start of layout"),
            ],
            actions=[
                EventAction("Calculate offline time"),
                EventAction("Show offline earnings popup"),
                EventAction("Add to Resource", "OfflineEarnings"),
            ],
            group="Offline"
        ))

        # 成就解锁检测
        events.append(GameEvent(
            name="Achievement Check",
            description="检测成就解锁条件",
            conditions=[
                EventCondition("Resource", ">=", "AchievementTarget"),
            ],
            actions=[
                EventAction("Unlock achievement", "AchievementID"),
                EventAction("Show achievement popup"),
                EventAction("Add bonus reward"),
            ],
            group="Achievements"
        ))

        # 每日签到
        events.append(GameEvent(
            name="Daily Login",
            description="每日登录奖励",
            conditions=[
                EventCondition("System", "On start of layout"),
            ],
            actions=[
                EventAction("Check login streak"),
                EventAction("Show daily reward popup"),
                EventAction("Add to Resource", "DailyReward"),
            ],
            group="Daily"
        ))

        return events

    def generate_event_sheet_json(self, events: List[GameEvent]) -> str:
        """生成事件表JSON格式（用于导入Construct3）"""
        event_sheet = {
            "name": self.event_sheet_name,
            "events": []
        }

        current_group = None
        for event in events:
            if event.group != current_group:
                current_group = event.group
                event_sheet["events"].append({
                    "type": "comment",
                    "text": f"=== {current_group} ==="
                })

            event_entry = {
                "name": event.name,
                "description": event.description,
                "conditions": [
                    {
                        "object": c.object_name,
                        "condition": c.condition,
                        "comparison": c.comparison,
                        "value": c.value
                    } for c in (event.conditions or [])
                ],
                "actions": [
                    {
                        "action": a.action,
                        "target": a.target,
                        "value": a.value
                    } for a in (event.actions or [])
                ]
            }
            event_sheet["events"].append(event_entry)

        return json.dumps(event_sheet, indent=2, ensure_ascii=False)

    def generate_c3p_template(self) -> str:
        """生成Construct3项目模板（JSON格式）"""
        template = {
            "project": {
                "name": "Generated Game",
                "formatVersion": 1.2,
                "runtime": {
                    "canvasWidth": 540,
                    "canvasHeight": 960,
                    "pixelRounding": True,
                    "fps": 60,
                    "zPreset": "minimal"
                }
            },
            "layouts": [
                {
                    "name": "Menu",
                    "layers": ["Background", "UI"],
                    "objects": [
                        {"type": "Sprite", "name": "Title", "x": 270, "y": 200},
                        {"type": "Button", "name": "StartBtn", "x": 270, "y": 500}
                    ]
                },
                {
                    "name": "Game",
                    "layers": ["Background", "Gameplay", "UI"],
                    "objects": []
                },
                {
                    "name": "GameOver",
                    "layers": ["Background", "UI"],
                    "objects": [
                        {"type": "Text", "name": "ScoreText", "x": 270, "y": 300},
                        {"type": "Button", "name": "RestartBtn", "x": 270, "y": 500}
                    ]
                }
            ],
            "eventSheets": [
                {
                    "name": "Main",
                    "events": []
                }
            ]
        }
        return json.dumps(template, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    print("=" * 60)
    print("Construct3 Event Logic Generator")
    print("Construct3事件逻辑生成器")
    print("=" * 60)
    print()

    generator = EventLogicGenerator()

    # 生成Flappy Bird事件
    print("Generating Flappy Bird events...")
    flappy_events = generator.generate_flappy_bird_events()
    print(f"Generated {len(flappy_events)} events")
    for event in flappy_events:
        print(f"  - {event.name} [{event.group}]")
    print()

    # 生成事件表JSON
    print("Generating event sheet JSON...")
    json_output = generator.generate_event_sheet_json(flappy_events)
    print(json_output[:500] + "...")


if __name__ == "__main__":
    main()
