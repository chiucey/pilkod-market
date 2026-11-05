"""
Construct3 High-Addictive Game Generator
Construct3高成瘾性游戏生成器 - 主执行脚本

全自动生成高质量休闲游戏，包含策划、制作、导出全流程
"""

import json
import random
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class GameProject:
    """游戏项目数据模型"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: str = ""
    description: str = ""
    canvas_width: int = 540
    canvas_height: int = 960
    target_fps: int = 60
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # 成瘾机制配置
    addiction_config: Dict = field(default_factory=dict)

    # 场景配置
    scenes: List[str] = field(default_factory=list)

    # 素材配置
    assets: List[Dict] = field(default_factory=list)

    # 事件逻辑
    event_sheets: List[Dict] = field(default_factory=list)


class Construct3GameGenerator:
    """Construct3游戏生成器主类"""

    def __init__(self):
        self.current_project: Optional[GameProject] = None
        self.game_templates = self._load_game_templates()

    def _load_game_templates(self) -> Dict[str, Dict]:
        """加载内置游戏模板"""
        return {
            "flappy_bird": {
                "name": "Flappy Bird类跑酷游戏",
                "category": "敏捷挑战",
                "description": "单指操作，即时反馈，无限重复，高分挑战",
                "core_mechanics": [
                    "玩家持续下落",
                    "点击/触摸向上飞跃",
                    "穿越管道障碍",
                    "碰撞检测",
                    "分数累积"
                ],
                "addiction_hooks": [
                    "即时反馈：每穿过管道有音效+分数变化",
                    "排行榜竞争：好友排名PK",
                    "目标递进：每次尝试都在突破自我",
                    "简短回合：每局30秒，随时开始"
                ],
                "ui_elements": [
                    "分数显示(顶部居中)",
                    "最高分显示",
                    "开始按钮",
                    "重新开始按钮",
                    "暂停按钮"
                ],
                "recommended_colors": {
                    "primary": "#4EC0CA",
                    "secondary": "#F5A623",
                    "accent": "#FFFFFF",
                    "background": "#70C5CE"
                }
            },
            "merge_2048": {
                "name": "2048类合成游戏",
                "category": "合成养成",
                "description": "滑动合并，数值积累，无限合成，策略思考",
                "core_mechanics": [
                    "4x4/5x5网格布局",
                    "滑动方向控制所有方块",
                    "相同数字方块合并",
                    "新方块随机生成",
                    "游戏结束判定"
                ],
                "addiction_hooks": [
                    "数值积累快感：数字越来越大",
                    "全合成成就：挑战2048/4096/8192",
                    "排名竞争：全球玩家排名",
                    "策略深度：看似简单实则需要思考"
                ],
                "ui_elements": [
                    "当前分数",
                    "最高分记录",
                    "游戏网格(4x4)",
                    "重新开始按钮",
                    "撤销按钮"
                ],
                "recommended_colors": {
                    "primary": "#EDF1F5",
                    "secondary": "#3C3A32",
                    "accent": "#EDC22E",
                    "background": "#FAF8EF"
                }
            },
            "candy_crush": {
                "name": "Candy Crush类消除游戏",
                "category": "解谜消除",
                "description": "交换匹配，连锁反应，关卡目标，道具辅助",
                "core_mechanics": [
                    "6x6/8x8糖果网格",
                    "相邻糖果交换",
                    "3个以上相同消除",
                    "连锁反应加分",
                    "关卡目标达成"
                ],
                "addiction_hooks": [
                    "连锁反应：一次消除多组爽快感",
                    "关卡进度：逐关推进有成就感",
                    "星数评价：追求完美三星",
                    "道具辅助：特殊糖果带来惊喜"
                ],
                "ui_elements": [
                    "当前关卡",
                    "目标分数/目标数量",
                    "剩余步数",
                    "糖果网格",
                    "特殊糖果提示"
                ],
                "recommended_colors": {
                    "primary": "#FF6B6B",
                    "secondary": "#4ECDC4",
                    "accent": "#FFE66D",
                    "background": "#2C3E50"
                }
            },
            "tetris": {
                "name": "俄罗斯方块类益智游戏",
                "category": "益智挑战",
                "description": "空间布局，速度挑战，高分追求，经典再现",
                "core_mechanics": [
                    "7种方块下落",
                    "左右移动旋转",
                    "行消除计分",
                    "速度逐渐加快",
                    "游戏结束判定"
                ],
                "addiction_hooks": [
                    "无尽模式：永远想再玩一局",
                    "高分追求：不断刷新个人记录",
                    "速度挑战：越来越刺激",
                    "简单上手：规则易懂但难精通"
                ],
                "ui_elements": [
                    "当前分数",
                    "消行数统计",
                    "下一个方块预览",
                    "等级/速度显示",
                    "最高分记录"
                ],
                "recommended_colors": {
                    "primary": "#E74C3C",
                    "secondary": "#3498DB",
                    "accent": "#2ECC71",
                    "background": "#1A1A2E"
                }
            },
            "idle_clicker": {
                "name": "放置挂机类收集游戏",
                "category": "放置收集",
                "description": "离线收益，数值成长，自动运行，长期目标",
                "core_mechanics": [
                    "点击获取资源",
                    "升级强化系统",
                    "离线收益计算",
                    "自动产出机制",
                    "多阶段目标"
                ],
                "addiction_hooks": [
                    "数值成长：看着数字不断增长",
                    "离线收益：睡觉也在赚钱",
                    "长期目标：永远有下一个目标",
                    "每日登录：积累奖励"
                ],
                "ui_elements": [
                    "主资源显示",
                    "点击区域",
                    "升级商店",
                    "成就进度",
                    "离线收益提示"
                ],
                "recommended_colors": {
                    "primary": "#9B59B6",
                    "secondary": "#F39C12",
                    "accent": "#1ABC9C",
                    "background": "#2C3E50"
                }
            }
        }

    def generate_game(self, template_type: str = None, custom_requirements: Dict = None) -> GameProject:
        """生成游戏项目"""
        # 选择模板
        if template_type and template_type in self.game_templates:
            template = self.game_templates[template_type]
        else:
            template = random.choice(list(self.game_templates.values()))

        # 创建项目
        project = GameProject()
        project.name = custom_requirements.get("name", f"Game_{project.id}") if custom_requirements else template["name"]
        project.category = template["category"]
        project.description = template["description"]

        # 配置成瘾机制
        project.addiction_config = {
            "instant_feedback": True,
            "progressive_difficulty": True,
            "random_rewards": True,
            "achievement_system": True,
            "replay_triggers": True,
            "goal_progression": True
        }

        # 生成场景
        project.scenes = self._generate_scenes(template)

        # 生成素材配置
        project.assets = self._generate_assets(template)

        # 生成事件逻辑
        project.event_sheets = self._generate_event_sheets(template)

        self.current_project = project
        return project

    def _generate_scenes(self, template: Dict) -> List[Dict]:
        """生成场景配置"""
        scenes = []

        # 主菜单场景
        scenes.append({
            "name": "Menu",
            "layout": {
                "background_color": template["recommended_colors"]["background"],
                "parallax_layers": 0
            },
            "layers": [
                {"name": "Background", "parallax": 0},
                {"name": "Game", "parallax": 1},
                {"name": "UI", "parallax": 1},
                {"name": "Text", "parallax": 1}
            ],
            "objects": [
                {"type": "Sprite", "name": "TitleLogo", "x": 270, "y": 300},
                {"type": "Button", "name": "StartButton", "x": 270, "y": 500},
                {"type": "Button", "name": "SettingsButton", "x": 270, "y": 600}
            ]
        })

        # 游戏场景
        scenes.append({
            "name": "Game",
            "layout": {
                "background_color": template["recommended_colors"]["background"],
                "unbounded_scrolling": False
            },
            "layers": [
                {"name": "Background", "parallax": 0},
                {"name": "Gameplay", "parallax": 1},
                {"name": "Effects", "parallax": 1},
                {"name": "UI", "parallax": 1},
                {"name": "Text", "parallax": 1}
            ],
            "objects": [
                {"type": "Sprite", "name": "Player", "x": 270, "y": 500},
                {"type": "Sprite", "name": "Ground", "x": 270, "y": 900},
                {"type": "Text", "name": "ScoreText", "x": 270, "y": 50}
            ]
        })

        # 结果场景
        scenes.append({
            "name": "GameOver",
            "layout": {
                "background_color": "#1A1A2E"
            },
            "layers": [
                {"name": "Background", "parallax": 0},
                {"name": "UI", "parallax": 1},
                {"name": "Text", "parallax": 1}
            ],
            "objects": [
                {"type": "Text", "name": "GameOverText", "x": 270, "y": 300},
                {"type": "Text", "name": "FinalScoreText", "x": 270, "y": 400},
                {"type": "Button", "name": "RestartButton", "x": 270, "y": 550},
                {"type": "Button", "name": "MenuButton", "x": 270, "y": 650}
            ]
        })

        return scenes

    def _generate_assets(self, template: Dict) -> List[Dict]:
        """生成素材配置"""
        assets = []

        # 基础游戏素材
        if "flappy" in template.get("name", "").lower():
            assets.extend([
                {"type": "sprite", "name": "Bird", "size": [50, 35], "animation_frames": 3},
                {"type": "sprite", "name": "Pipe", "size": [80, 400]},
                {"type": "sprite", "name": "Background", "size": [540, 960]},
                {"type": "sprite", "name": "Ground", "size": [600, 100]}
            ])
        elif "merge" in template.get("name", "").lower() or "2048" in template.get("name", "").lower():
            assets.extend([
                {"type": "sprite", "name": "Tile_2", "size": [100, 100], "color": "#EEE4DA"},
                {"type": "sprite", "name": "Tile_4", "size": [100, 100], "color": "#EDE0C8"},
                {"type": "sprite", "name": "Tile_8", "size": [100, 100], "color": "#F2B179"},
                {"type": "sprite", "name": "Tile_16", "size": [100, 100], "color": "#F59563"},
                {"type": "sprite", "name": "Tile_32", "size": [100, 100], "color": "#F67C5F"},
                {"type": "sprite", "name": "Tile_64", "size": [100, 100], "color": "#F65E3B"},
                {"type": "sprite", "name": "Grid", "size": [440, 440], "color": "#BBADA0"}
            ])
        elif "candy" in template.get("name", "").lower():
            colors = ["#FF6B6B", "#4ECDC4", "#FFE66D", "#95E1D3", "#F38181", "#AA96DA"]
            for i, color in enumerate(colors):
                assets.append({"type": "sprite", "name": f"Candy_{i+1}", "size": [60, 60], "color": color})
        else:
            assets.extend([
                {"type": "sprite", "name": "Player", "size": [50, 50]},
                {"type": "sprite", "name": "Obstacle", "size": [50, 100]},
                {"type": "sprite", "name": "Background", "size": [540, 960]}
            ])

        # UI素材
        assets.extend([
            {"type": "sprite", "name": "Button_Normal", "size": [200, 60]},
            {"type": "sprite", "name": "Button_Hover", "size": [200, 60]},
            {"type": "sprite", "name": "Button_Pressed", "size": [200, 60]}
        ])

        # 音效配置
        assets.extend([
            {"type": "audio", "name": "BGM", "format": "ogg"},
            {"type": "audio", "name": "Click", "format": "ogg"},
            {"type": "audio", "name": "Success", "format": "ogg"},
            {"type": "audio", "name": "GameOver", "format": "ogg"}
        ])

        return assets

    def _generate_event_sheets(self, template: Dict) -> List[Dict]:
        """生成事件逻辑表"""
        event_sheets = []

        # 主菜单事件表
        event_sheets.append({
            "name": "Menu_Events",
            "events": [
                {
                    "name": "Start Game",
                    "conditions": [
                        {"object": "StartButton", "condition": "On clicked"}
                    ],
                    "actions": [
                        {"action": "Go to scene", "target": "Game"},
                        {"action": "Play sound", "sound": "Click"}
                    ]
                },
                {
                    "name": "Open Settings",
                    "conditions": [
                        {"object": "SettingsButton", "condition": "On clicked"}
                    ],
                    "actions": [
                        {"action": "Set visible", "object": "SettingsPanel", "value": True}
                    ]
                }
            ]
        })

        # 游戏主事件表
        event_sheets.append({
            "name": "Game_Events",
            "events": [
                {
                    "name": "Player Input - Jump",
                    "conditions": [
                        {"object": "Touch/Click", "condition": "On touched"},
                        {"object": "Game", "condition": "Is running"}
                    ],
                    "actions": [
                        {"action": "Set velocity Y", "object": "Player", "value": -500},
                        {"action": "Play animation", "object": "Player", "value": "Fly"}
                    ]
                },
                {
                    "name": "Score Point",
                    "conditions": [
                        {"object": "Player", "condition": "On collision with", "target": "ScoreZone"}
                    ],
                    "actions": [
                        {"action": "Add to variable", "variable": "Score", "value": 1},
                        {"action": "Play sound", "sound": "Success"},
                        {"action": "Spawn effect", "effect": "ScorePopup"}
                    ]
                },
                {
                    "name": "Game Over - Collision",
                    "conditions": [
                        {"object": "Player", "condition": "On collision with", "target": "Obstacle"}
                    ],
                    "actions": [
                        {"action": "Set game state", "value": "GameOver"},
                        {"action": "Go to scene", "target": "GameOver"},
                        {"action": "Play sound", "sound": "GameOver"}
                    ]
                }
            ]
        })

        # 游戏结束事件表
        event_sheets.append({
            "name": "GameOver_Events",
            "events": [
                {
                    "name": "Restart Game",
                    "conditions": [
                        {"object": "RestartButton", "condition": "On clicked"}
                    ],
                    "actions": [
                        {"action": "Reset global variables"},
                        {"action": "Go to scene", "target": "Game"},
                        {"action": "Play sound", "sound": "Click"}
                    ]
                },
                {
                    "name": "Back to Menu",
                    "conditions": [
                        {"object": "MenuButton", "condition": "On clicked"}
                    ],
                    "actions": [
                        {"action": "Go to scene", "target": "Menu"},
                        {"action": "Play sound", "sound": "Click"}
                    ]
                }
            ]
        })

        return event_sheets

    def export_project_config(self) -> Dict:
        """导出项目配置（用于Construct3导入）"""
        if not self.current_project:
            return {"error": "No project loaded"}

        return {
            "project": {
                "name": self.current_project.name,
                "description": self.current_project.description,
                "canvas": {
                    "width": self.current_project.canvas_width,
                    "height": self.current_project.canvas_height
                },
                "fps": self.current_project.target_fps
            },
            "scenes": self.current_project.scenes,
            "assets": self.current_project.assets,
            "event_sheets": self.current_project.event_sheets,
            "addiction_config": self.current_project.addiction_config
        }

    def generate_complete_game_code(self) -> str:
        """生成完整的游戏代码（可直接在Construct3中使用的JSON配置）"""
        config = self.export_project_config()

        code = f'''// Construct3 Game Project Configuration
// Generated by Construct3 Addictive Game Generator
// Project: {config["project"]["name"]}
// Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

const GAME_CONFIG = {json.dumps(config["project"], indent=2, ensure_ascii=False)};

const SCENES = {json.dumps(config["scenes"], indent=2, ensure_ascii=False)};

const ASSETS = {json.dumps(config["assets"], indent=2, ensure_ascii=False)};

const EVENT_SHEETS = {json.dumps(config["event_sheets"], indent=2, ensure_ascii=False)};

const ADDICTION_CONFIG = {json.dumps(config["addiction_config"], indent=2, ensure_ascii=False)};

// ============================================
// Construct3 Project Setup Instructions:
// ============================================
// 1. Open Construct 3 (https://editor.construct.net)
// 2. Create new project
// 3. Set canvas size: {config["project"]["canvas"]["width"]}x{config["project"]["canvas"]["height"]}
// 4. Set FPS: {config["project"]["fps"]}
// 5. Import assets from ASSETS config
// 6. Create scenes from SCENES config
// 7. Create event sheets from EVENT_SHEETS config
// 8. Test and export!

export {{ GAME_CONFIG, SCENES, ASSETS, EVENT_SHEETS, ADDICTION_CONFIG }};
'''

        return code


def main():
    """主函数入口"""
    print("=" * 60)
    print("Construct3 High-Addictive Game Generator")
    print("Construct3高成瘾性游戏生成器")
    print("=" * 60)
    print()

    generator = Construct3GameGenerator()

    # 生成示例游戏
    print("Available Game Templates:")
    for key in generator.game_templates.keys():
        template = generator.game_templates[key]
        print(f"  - {key}: {template['name']}")
    print()

    # 生成Flappy Bird类型游戏
    print("Generating Flappy Bird template...")
    project = generator.generate_game("flappy_bird")
    print(f"Project Created: {project.name}")
    print(f"Category: {project.category}")
    print(f"Scenes: {[s['name'] for s in project.scenes]}")
    print(f"Assets: {len(project.assets)} items")
    print(f"Event Sheets: {len(project.event_sheets)} sheets")
    print()

    # 导出配置
    print("Exporting project configuration...")
    config = generator.export_project_config()
    print(json.dumps(config, indent=2, ensure_ascii=False)[:500] + "...")


if __name__ == "__main__":
    main()
