#!/usr/bin/env python3
"""
木偶剧视频生成器核心脚本
自动生成剧本、分镜、运镜方案
"""

import json
import re
from typing import Dict, List, Optional

class PuppetShowGenerator:
    """木偶剧视频生成器"""

    def __init__(self):
        self.durations = {
            "5s": {"scenes": 2, "shots_per_scene": 1},
            "10s": {"scenes": 3, "shots_per_scene": 2},
            "15s": {"scenes": 4, "shots_per_scene": 2},
            "1min": {"scenes": 6, "shots_per_scene": 3},
            "5min": {"scenes": 12, "shots_per_scene": 4},
            "15min": {"scenes": 25, "shots_per_scene": 5},
            "30min": {"scenes": 40, "shots_per_scene": 5}
        }

        self.color_schemes = {
            "温馨童趣": {"primary": "#FFD700", "secondary": "#87CEEB", "emotion": "温暖快乐"},
            "悬疑惊悚": {"primary": "#1C3144", "secondary": "#8B0000", "emotion": "紧张神秘"},
            "浪漫爱情": {"primary": "#FF69B4", "secondary": "#DDA0DD", "emotion": "浪漫温馨"},
            "历史传奇": {"primary": "#8B4513", "secondary": "#006400", "emotion": "厚重庄严"},
            "奇幻冒险": {"primary": "#9932CC", "secondary": "#00CED1", "emotion": "神秘刺激"}
        }

        self.shot_types = ["远景", "全景", "中景", "近景", "特写", "双人中景", "过肩镜头"]
        self.camera_moves = ["推镜头", "拉镜头", "摇镜头", "移镜头", "跟镜头", "固定镜头"]

    def parse_input(self, story_text: str, duration: str, style: str = "温馨童趣") -> Dict:
        """解析输入文本"""
        return {
            "story_text": story_text,
            "duration": duration,
            "style": style,
            "color_scheme": self.color_schemes.get(style, self.color_schemes["温馨童趣"])
        }

    def generate_script(self, story_text: str, duration: str, style: str) -> Dict:
        """生成完整剧本"""
        duration_config = self.durations.get(duration, self.durations["1min"])

        # 提取关键元素
        characters = self._extract_characters(story_text)
        scenes = self._extract_scenes(story_text, duration_config["scenes"])

        script = {
            "title": self._generate_title(story_text),
            "style": style,
            "duration": duration,
            "acts": [
                {"act": 1, "name": "开场设定", "description": "介绍角色与背景"},
                {"act": 2, "name": "冲突发展", "description": "推进故事情节"},
                {"act": 3, "name": "高潮转折", "description": "制造情感爆发点"},
                {"act": 4, "name": "结局收束", "description": "完美落幕"}
            ],
            "characters": characters,
            "scenes": scenes,
            "dialogues": self._generate_dialogues(story_text, characters),
            "color_scheme": self.color_schemes.get(style)
        }

        return script

    def generate_storyboard(self, script: Dict) -> List[Dict]:
        """生成分镜脚本"""
        storyboard = []
        scene_idx = 0

        for scene in script.get("scenes", []):
            for shot_num in range(1, 4):
                storyboard.append({
                    "shot_id": f"S{scene_idx + 1}_Shot{shot_num}",
                    "scene": scene.get("name", f"场景{scene_idx + 1}"),
                    "shot_type": self._random_shot_type(),
                    "camera_move": self._random_camera_move(),
                    "description": scene.get("description", ""),
                    "duration_seconds": 3,
                    "characters": scene.get("characters", []),
                    "dialogue": scene.get("dialogue", ""),
                    "action": scene.get("action", ""),
                    "color_notes": self._get_color_notes(script.get("color_scheme"))
                })
            scene_idx += 1

        return storyboard

    def generate_character_config(self, characters: List[str], style: str) -> List[Dict]:
        """生成角色固定配置"""
        character_configs = []

        character_types = {
            "主角": {"服装": "主角专属服装", "化妆": "精细主角妆容", "道具": "专属道具"},
            "配角": {"服装": "配角服装", "化妆": "基础妆容", "道具": "辅助道具"},
            "反派": {"服装": "反派服装", "化妆": "特殊妆容", "道具": "威胁道具"}
        }

        for idx, char_name in enumerate(characters[:5]):
            char_type = "主角" if idx == 0 else ("反派" if idx == len(characters) - 1 else "配角")
            config = character_types.get(char_type, character_types["配角"])

            character_configs.append({
                "name": char_name,
                "type": char_type,
                "appearance": self._describe_appearance(char_name, style),
                "costume": config["服装"],
                "makeup": config["化妆"],
                "props": [f"{char_name}专属道具"],
                "color_palette": self._get_character_colors(char_type, style)
            })

        return character_configs

    def _extract_characters(self, story_text: str) -> List[str]:
        """提取角色"""
        # 简单实现，实际可使用NLP
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', story_text)
        # 模拟角色提取
        return ["小木偶奇奇", "小木偶妮娜", "神秘魔法师", "森林精灵"]

    def _extract_scenes(self, story_text: str, num_scenes: int) -> List[Dict]:
        """提取场景"""
        scene_names = ["森林小屋", "神秘洞穴", "魔法花园", "高山之巅", "湖边小屋", "古老城堡"]
        scenes = []

        for i in range(num_scenes):
            scenes.append({
                "scene_id": i + 1,
                "name": scene_names[i % len(scene_names)],
                "description": f"场景{i + 1}的详细描述",
                "atmosphere": self._get_scene_atmosphere(i, num_scenes),
                "lighting": self._get_scene_lighting(i, num_scenes),
                "characters": [],
                "dialogue": "",
                "action": ""
            })

        return scenes

    def _generate_title(self, story_text: str) -> str:
        """生成标题"""
        return "木偶奇遇记 - 奇妙之旅"

    def _generate_dialogues(self, story_text: str, characters: List[str]) -> List[Dict]:
        """生成台词"""
        dialogues = []
        for char in characters:
            dialogues.append({
                "character": char,
                "text": f"你好，我是{char}！",
                "emotion": "开心"
            })
        return dialogues

    def _random_shot_type(self) -> str:
        """随机镜头类型"""
        import random
        return random.choice(self.shot_types)

    def _random_camera_move(self) -> str:
        """随机运镜方式"""
        import random
        return random.choice(self.camera_moves)

    def _describe_appearance(self, name: str, style: str) -> str:
        """描述外观"""
        return f"{name} - 木偶外观描述，采用{style}风格设计"

    def _get_scene_atmosphere(self, idx: int, total: int) -> str:
        """获取场景氛围"""
        if idx == 0:
            return "轻松愉快"
        elif idx == total - 1:
            return "震撼感人"
        else:
            return "紧张刺激"

    def _get_scene_lighting(self, idx: int, total: int) -> str:
        """获取灯光设计"""
        if idx == 0:
            return "明亮暖光"
        elif idx == total - 1:
            return "戏剧性侧光"
        else:
            return "自然光"

    def _get_color_notes(self, color_scheme: Dict) -> str:
        """获取色调注释"""
        if not color_scheme:
            return "标准色调"
        return f"主色:{color_scheme.get('primary', '#FFFFFF')}, 辅色:{color_scheme.get('secondary', '#CCCCCC')}"

    def _get_character_colors(self, char_type: str, style: str) -> Dict:
        """获取角色配色"""
        scheme = self.color_schemes.get(style, self.color_schemes["温馨童趣"])
        return {
            "outfit": scheme.get("primary", "#FFD700"),
            "accessory": scheme.get("secondary", "#87CEEB"),
            "highlight": "#FFFFFF"
        }


def main():
    """主函数"""
    generator = PuppetShowGenerator()

    # 测试生成
    story = "从前有一个小木偶，他叫做奇奇..."
    script = generator.generate_script(story, "1min", "温馨童趣")

    print(json.dumps(script, ensure_ascii=False, indent=2))

    storyboard = generator.generate_storyboard(script)
    print("\n=== 分镜脚本 ===")
    print(json.dumps(storyboard, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
