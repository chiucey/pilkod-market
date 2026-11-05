"""
视频导演任务分解器
Video Director Task Decomposer

将视频脚本自动分解为多agent分工任务，协调美术、剪辑、配乐等专业agent完成视频制作。
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


class TaskType(Enum):
    """任务类型枚举"""
    CHARACTER_ASSET = "character_asset"
    SCENE_BACKGROUND = "scene_background"
    STORYBOARD_FRAME = "storyboard_frame"
    VIDEO_CLIP = "video_clip"
    AUDIO_DESIGN = "audio_design"
    SUBTITLE_PACKAGE = "subtitle_package"
    VIDEO_SYNTHESIS = "video_synthesis"
    QUALITY_CHECK = "quality_check"


class EpisodeStatus(Enum):
    """制作状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CharacterCard:
    """人物设定卡"""
    role_name: str
    role_type: str  # monarch/minister/general/civilian
    appearance: str
    costume: str
    props: List[str]
    consistency: str
    episodes: List[int]
    mood: str

    def to_prompt(self) -> str:
        """生成人物生成提示词"""
        return f"""角色名称：{self.role_name}
角色类型：{self.role_type}
外貌特征：{self.appearance}
服饰配置：{self.costume}
标志性道具：{', '.join(self.props)}
角色气质：{self.mood}
一致性要求：{self.consistency}"""


@dataclass
class StoryboardFrame:
    """分镜画面"""
    episode: int
    time_start: str
    time_end: str
    duration: int
    scene_type: str
    visual_elements: Dict[str, Any]
    narration: str
    subtitle: Optional[str]
    effects: List[str]
    transition: Dict[str, str]

    def to_prompt(self, characters: List[str]) -> str:
        """生成分镜生成提示词"""
        char_list = ', '.join(characters) if characters else '待定'
        effects_list = ', '.join(self.effects) if self.effects else '无'
        return f"""集数：第{self.episode}集
时间码：{self.time_start} - {self.time_end}
场景类型：{self.scene_type}
画面描述：{self.visual_elements.get('description', '')}
出场人物：{char_list}
构图方式：{self.visual_elements.get('composition', '标准')}
色调指引：{self.visual_elements.get('tone', '待定')}
特效要求：{effects_list}
旁白：{self.narration}
字幕：{self.subtitle or '无'}"""


@dataclass
class AudioDesign:
    """音频设计"""
    episode: int
    time_start: str
    time_end: str
    music_style: str
    sfx_list: List[str]
    rhythm: str
    mood: str

    def to_prompt(self, narration: str = "") -> str:
        """生成音频设计提示词"""
        return f"""集数：第{self.episode}集
时间段：{self.time_start} - {self.time_end}
音乐风格：{self.music_style}
情绪氛围：{self.mood}
节奏类型：{self.rhythm}
音效列表：{', '.join(self.sfx_list)}
旁白内容：{narration}"""


@dataclass
class AgentTask:
    """Agent任务"""
    task_id: str
    task_type: TaskType
    priority: int
    episode: int
    status: EpisodeStatus
    inputs: Dict[str, Any]
    outputs: Dict[str, str]
    dependencies: List[str]
    agent_type: str
    prompt: str
    checkpoints: List[str]


class ScriptParser:
    """剧本解析器"""

    def __init__(self):
        self.characters: List[CharacterCard] = []
        self.storyboards: List[StoryboardFrame] = []
        self.audio_designs: List[AudioDesign] = []
        self.series_info: Dict[str, Any] = {}

    def parse_script(self, script_text: str) -> Dict[str, Any]:
        """解析剧本文本"""
        result = {
            "characters": [],
            "storyboards": [],
            "audio_designs": [],
            "series_info": {}
        }

        # 解析人物设定卡
        self._parse_character_cards(script_text)
        result["characters"] = [asdict(c) for c in self.characters]

        # 解析分镜时间轴
        self._parse_storyboard_frames(script_text)
        result["storyboards"] = [asdict(s) for s in self.storyboards]

        # 解析音频设计
        self._parse_audio_designs(script_text)
        result["audio_designs"] = [asdict(a) for a in self.audio_designs]

        # 提取系列信息
        self._extract_series_info(script_text)
        result["series_info"] = self.series_info

        return result

    def _parse_character_cards(self, text: str) -> None:
        """解析人物设定卡"""
        # 简化的解析逻辑，实际使用时需要更复杂的NLP处理
        patterns = [
            r'([^\s]+)身份/关系：([^\n]+)',
            r'出现集数：第(\d+)集',
            r'外貌识别点：([^\n]+)',
            r'穿戴/服饰：([^\n]+)',
            r'打扮/仪态：([^\n]+)',
            r'一致性提示：([^\n]+)'
        ]

        # 示例：从文本中提取人物（简化版）
        # 实际实现需要更复杂的文本分析
        pass

    def _parse_storyboard_frames(self, text: str) -> None:
        """解析分镜时间轴"""
        # 简化的解析逻辑
        pass

    def _parse_audio_designs(self, text: str) -> None:
        """解析音频设计"""
        # 简化的解析逻辑
        pass

    def _extract_series_info(self, text: str) -> None:
        """提取系列信息"""
        title_match = re.search(r'《([^》]+)》', text)
        if title_match:
            self.series_info["title"] = title_match.group(1)

        theme_match = re.search(r'核心主题句：([^\n]+)', text)
        if theme_match:
            self.series_info["theme"] = theme_match.group(1)


class TaskDecomposer:
    """任务分解器"""

    def __init__(self):
        self.agent_mapping = {
            TaskType.CHARACTER_ASSET: "art-director",
            TaskType.SCENE_BACKGROUND: "art-director",
            TaskType.STORYBOARD_FRAME: "image-gen",
            TaskType.VIDEO_CLIP: "video-gen",
            TaskType.AUDIO_DESIGN: "audio-director",
            TaskType.SUBTITLE_PACKAGE: "subtitle-gen",
            TaskType.VIDEO_SYNTHESIS: "editor",
            TaskType.QUALITY_CHECK: "quality-reviewer"
        }

    def decompose(
        self,
        characters: List[Dict],
        storyboards: List[Dict],
        audio_designs: List[Dict],
        series_info: Dict
    ) -> List[AgentTask]:
        """分解任务"""
        tasks = []

        # 1. 人物资产生成任务
        tasks.extend(self._create_character_tasks(characters))

        # 2. 场景背景生成任务
        tasks.extend(self._create_scene_tasks(storyboards))

        # 3. 分镜画面生成任务
        tasks.extend(self._create_storyboard_tasks(storyboards, characters))

        # 4. 音频设计任务
        tasks.extend(self._create_audio_tasks(audio_designs, storyboards))

        # 5. 视频合成任务
        tasks.extend(self._create_synthesis_tasks(storyboards, series_info))

        # 6. 质量检查任务
        tasks.extend(self._create_quality_tasks(tasks))

        return tasks

    def _create_character_tasks(self, characters: List[Dict]) -> List[AgentTask]:
        """创建人物资产任务"""
        tasks = []
        for i, char in enumerate(characters):
            char_card = CharacterCard(
                role_name=char.get("role_name", "Unknown"),
                role_type=char.get("role_type", "civilian"),
                appearance=char.get("appearance", ""),
                costume=char.get("costume", ""),
                props=char.get("props", []),
                consistency=char.get("consistency", ""),
                episodes=char.get("episodes", []),
                mood=char.get("mood", "")
            )

            task = AgentTask(
                task_id=f"char_asset_{i+1}",
                task_type=TaskType.CHARACTER_ASSET,
                priority=1,
                episode=char.get("episodes", [1])[0] if char.get("episodes") else 1,
                status=EpisodeStatus.PENDING,
                inputs={
                    "character_card": asdict(char_card)
                },
                outputs={
                    "character_image": f"{char_card.role_name}_全身立绘.png",
                    "character_face": f"{char_card.role_name}_面部特写.png",
                    "costume_details": f"{char_card.role_name}_服饰细节.png"
                },
                dependencies=[],
                agent_type=self.agent_mapping[TaskType.CHARACTER_ASSET],
                prompt=char_card.to_prompt(),
                checkpoints=[
                    "面部特征与设定一致",
                    "服饰颜色符合配色方案",
                    "道具与角色身份匹配"
                ]
            )
            tasks.append(task)

        return tasks

    def _create_scene_tasks(self, storyboards: List[Dict]) -> List[AgentTask]:
        """创建场景背景任务"""
        tasks = []
        scenes = {}

        for i, sb in enumerate(storyboards):
            scene_desc = sb.get("visual_elements", {}).get("setting", "")
            if scene_desc and scene_desc not in scenes:
                scenes[scene_desc] = {
                    "task_id": f"scene_bg_{len(scenes)+1}",
                    "scene_name": scene_desc,
                    "episodes": [sb.get("episode", 1)]
                }
            elif scene_desc:
                scenes[scene_desc]["episodes"].append(sb.get("episode", 1))

        for scene_name, scene_info in scenes.items():
            task = AgentTask(
                task_id=scene_info["task_id"],
                task_type=TaskType.SCENE_BACKGROUND,
                priority=2,
                episode=scene_info["episodes"][0],
                status=EpisodeStatus.PENDING,
                inputs={
                    "scene_name": scene_name,
                    "episodes": scene_info["episodes"]
                },
                outputs={
                    "scene_image": f"scene_{scene_name}.png",
                    "scene_elements": f"scene_{scene_name}_elements.png"
                },
                dependencies=[],
                agent_type=self.agent_mapping[TaskType.SCENE_BACKGROUND],
                prompt=f"场景名称：{scene_name}\n集数：{', '.join(map(str, scene_info['episodes']))}",
                checkpoints=[
                    "场景风格与时代背景一致",
                    "细节丰富可再利用"
                ]
            )
            tasks.append(task)

        return tasks

    def _create_storyboard_tasks(
        self,
        storyboards: List[Dict],
        characters: List[Dict]
    ) -> List[AgentTask]:
        """创建分镜画面任务"""
        tasks = []
        char_map = {c.get("role_name", ""): c for c in characters}

        for i, sb in enumerate(storyboards):
            episode = sb.get("episode", 1)
            time_start = sb.get("time_start", "00:00:00")

            # 提取画面中的人物
            frame_chars = sb.get("visual_elements", {}).get("characters", [])

            frame = StoryboardFrame(
                episode=episode,
                time_start=time_start,
                time_end=sb.get("time_end", time_start),
                duration=sb.get("duration", 5),
                scene_type=sb.get("scene_type", "dialogue"),
                visual_elements=sb.get("visual_elements", {}),
                narration=sb.get("narration", ""),
                subtitle=sb.get("subtitle"),
                effects=sb.get("effects", []),
                transition=sb.get("transition", {})
            )

            task = AgentTask(
                task_id=f"storyboard_ep{episode}_{i+1}",
                task_type=TaskType.STORYBOARD_FRAME,
                priority=3,
                episode=episode,
                status=EpisodeStatus.PENDING,
                inputs={
                    "frame_data": asdict(frame),
                    "referenced_characters": frame_chars
                },
                outputs={
                    "frame_image": f"ep{episode}_{time_start.replace(':', '_')}_frame.png",
                    "effect_layers": f"ep{episode}_{time_start.replace(':', '_')}_effects.png"
                },
                dependencies=[f"char_asset_{j+1}" for j, c in enumerate(characters) if c.get("role_name") in frame_chars],
                agent_type=self.agent_mapping[TaskType.STORYBOARD_FRAME],
                prompt=frame.to_prompt(frame_chars),
                checkpoints=[
                    "人物形象与设定一致",
                    "色调符合指引",
                    "特效清晰可叠加"
                ]
            )
            tasks.append(task)

        return tasks

    def _create_audio_tasks(
        self,
        audio_designs: List[Dict],
        storyboards: List[Dict]
    ) -> List[AgentTask]:
        """创建音频设计任务"""
        tasks = []

        # 按集数分组
        episodes_audio = {}
        for ad in audio_designs:
            ep = ad.get("episode", 1)
            if ep not in episodes_audio:
                episodes_audio[ep] = []
            episodes_audio[ep].append(ad)

        # 为每集创建主音频任务
        for ep, audio_list in episodes_audio.items():
            # 获取该集的旁白用于音频节奏设计
            ep_narations = [sb.get("narration", "") for sb in storyboards if sb.get("episode") == ep]
            combined_narration = " ".join(ep_narations[:3])  # 取前3段旁白

            for i, ad in enumerate(audio_list):
                audio_design = AudioDesign(
                    episode=ep,
                    time_start=ad.get("time_start", "00:00:00"),
                    time_end=ad.get("time_end", "00:00:00"),
                    music_style=ad.get("music_style", "待定"),
                    sfx_list=ad.get("sfx_list", []),
                    rhythm=ad.get("rhythm", "中等"),
                    mood=ad.get("mood", "")
                )

                task = AgentTask(
                    task_id=f"audio_ep{ep}_{i+1}",
                    task_type=TaskType.AUDIO_DESIGN,
                    priority=4,
                    episode=ep,
                    status=EpisodeStatus.PENDING,
                    inputs={
                        "audio_design": asdict(audio_design)
                    },
                    outputs={
                        "bgm_segment": f"ep{ep}_audio_{i+1}.mp3",
                        "sfx_package": f"ep{ep}_sfx_{i+1}.zip"
                    },
                    dependencies=[],
                    agent_type=self.agent_mapping[TaskType.AUDIO_DESIGN],
                    prompt=audio_design.to_prompt(combined_narration),
                    checkpoints=[
                        "音乐情绪与画面匹配",
                        "音效与动作同步",
                        "节奏流畅无突兀"
                    ]
                )
                tasks.append(task)

        return tasks

    def _create_synthesis_tasks(
        self,
        storyboards: List[Dict],
        series_info: Dict
    ) -> List[AgentTask]:
        """创建视频合成任务"""
        tasks = []

        # 按集数分组
        episodes = set(sb.get("episode", 1) for sb in storyboards)

        for ep in sorted(episodes):
            ep_storyboards = [sb for sb in storyboards if sb.get("episode") == ep]

            task = AgentTask(
                task_id=f"synthesis_ep{ep}",
                task_type=TaskType.VIDEO_SYNTHESIS,
                priority=5,
                episode=ep,
                status=EpisodeStatus.PENDING,
                inputs={
                    "episode": ep,
                    "frame_count": len(ep_storyboards),
                    "series_title": series_info.get("title", ""),
                    "episode_title": f"第{ep}集"
                },
                outputs={
                    "video_file": f"ep{ep}_final.mp4",
                    "report": f"ep{ep}_制作报告.md"
                },
                dependencies=[f"storyboard_ep{ep}_{i+1}" for i in range(len(ep_storyboards))],
                agent_type=self.agent_mapping[TaskType.VIDEO_SYNTHESIS],
                prompt=f"集数：第{ep}集\n总画面数：{len(ep_storyboards)}\n系列标题：{series_info.get('title', '')}",
                checkpoints=[
                    "画面衔接流畅",
                    "音画同步正确",
                    "字幕位置准确",
                    "格式符合规范"
                ]
            )
            tasks.append(task)

        return tasks

    def _create_quality_tasks(self, all_tasks: List[AgentTask]) -> List[AgentTask]:
        """创建质量检查任务"""
        tasks = []

        # 人物一致性检查
        char_tasks = [t for t in all_tasks if t.task_type == TaskType.CHARACTER_ASSET]
        if char_tasks:
            task = AgentTask(
                task_id="quality_character_consistency",
                task_type=TaskType.QUALITY_CHECK,
                priority=6,
                episode=0,
                status=EpisodeStatus.PENDING,
                inputs={
                    "task_ids": [t.task_id for t in char_tasks]
                },
                outputs={
                    "report": "character_consistency_report.md"
                },
                dependencies=[t.task_id for t in char_tasks],
                agent_type=self.agent_mapping[TaskType.QUALITY_CHECK],
                prompt="检查人物设定的一致性：面部特征、服装配色、标志性道具",
                checkpoints=[
                    "所有人物形象一致",
                    "无明显风格偏差"
                ]
            )
            tasks.append(task)

        return tasks

    def generate_task_report(self, tasks: List[AgentTask]) -> str:
        """生成任务报告"""
        report = "# 视频制作任务分解报告\n\n"

        # 按类型分组
        by_type = {}
        for task in tasks:
            if task.task_type.value not in by_type:
                by_type[task.task_type.value] = []
            by_type[task.task_type.value].append(task)

        report += "## 任务概览\n\n"
        report += f"| 任务类型 | 任务数量 | 负责人Agent |\n"
        report += f"|----------|----------|-------------|\n"

        for task_type, task_list in by_type.items():
            agent = task_list[0].agent_type if task_list else ""
            report += f"| {task_type} | {len(task_list)} | {agent} |\n"

        report += "\n## 详细任务列表\n\n"

        for task_type, task_list in by_type.items():
            report += f"### {task_type}\n\n"
            for task in task_list:
                report += f"#### {task.task_id}\n"
                report += f"- **集数**：第{task.episode}集\n"
                report += f"- **优先级**：{task.priority}\n"
                report += f"- **状态**：{task.status.value}\n"
                report += f"- **依赖任务**：{', '.join(task.dependencies) if task.dependencies else '无'}\n"
                report += f"- **输出文件**：\n"
                for name, path in task.outputs.items():
                    report += f"  - {name}: {path}\n"
                report += f"- **质量检查点**：\n"
                for cp in task.checkpoints:
                    report += f"  - [ ] {cp}\n"
                report += "\n"

        return report


def main():
    """主函数：演示任务分解流程"""
    # 示例数据
    sample_characters = [
        {
            "role_name": "商鞅",
            "role_type": "minister",
            "appearance": "瘦高身形，面容冷峻，鹰钩鼻，眼神锐利如刀",
            "costume": "深色法家深衣（黑/深灰），腰悬法尺",
            "props": ["法尺", "竹简", "法冠"],
            "consistency": "必须保持冷峻威严的法律化身形象",
            "episodes": [2, 3],
            "mood": "冷酷决绝"
        }
    ]

    sample_storyboards = [
        {
            "episode": 2,
            "time_start": "00:00:00",
            "time_end": "00:00:12",
            "duration": 12,
            "scene_type": "action",
            "visual_elements": {
                "description": "刑场特写，公子虔被按在木桩上，商鞅手持法尺站在一旁",
                "characters": ["商鞅", "公子虔"],
                "composition": "特写",
                "tone": "血红"
            },
            "narration": "太子犯法，师傅受刑。",
            "subtitle": "法不阿贵",
            "effects": ["慢镜头", "血液飞溅"],
            "transition": {"type": "fade_in"}
        }
    ]

    sample_series = {
        "title": "秦朝的兴起",
        "theme": "从西陲边陲到统一帝国"
    }

    # 分解任务
    decomposer = TaskDecomposer()
    tasks = decomposer.decompose(
        characters=sample_characters,
        storyboards=sample_storyboards,
        audio_designs=[],
        series_info=sample_series
    )

    # 生成报告
    report = decomposer.generate_task_report(tasks)
    print(report)

    # 保存任务列表
    task_list = [asdict(t) for t in tasks]
    print("\n\n任务JSON:")
    print(json.dumps(task_list, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
