"""
剧本解析器
解析规范格式的剧本文本，提取剧名、角色、场景、对话等信息
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Character:
    """角色信息"""
    name: str
    gender: str = ""
    identity: str = ""
    description: str = ""
    personality: str = ""
    abilities: List[str] = field(default_factory=list)
    hidden_identity: str = ""
    appearance: str = ""
    color: Tuple[int, int, int] = (100, 100, 100)  # 默认灰色

    def __post_init__(self):
        # 根据性别分配默认颜色
        if not self.color or self.color == (100, 100, 100):
            if "男" in self.gender:
                self.color = (70, 130, 180)  # 钢蓝色
            elif "女" in self.gender:
                self.color = (219, 112, 147)  # 粉紫色
            else:
                self.color = (128, 128, 128)  # 灰色


@dataclass
class Dialogue:
    """对话信息"""
    character: str
    content: str
    emotion: str = "normal"  # normal, happy, sad, angry, surprised
    action: str = ""  # 动作描述


@dataclass
class Scene:
    """场景信息"""
    number: int
    title: str
    camera_desc: str = ""  # 镜头描述
    dialogues: List[Dialogue] = field(default_factory=list)
    location: str = ""  # 场景地点
    time: str = ""  # 时间


@dataclass
class ScriptInfo:
    """剧本信息"""
    title: str
    duration: str = ""
    location: str = ""
    characters: List[Character] = field(default_factory=list)
    scenes: List[Scene] = field(default_factory=list)
    ending: str = ""


class ScriptParser:
    """剧本解析器"""

    def __init__(self):
        self.script_info: Optional[ScriptInfo] = None

    def parse(self, text: str) -> ScriptInfo:
        """
        解析剧本文本

        Args:
            text: 剧本文本内容

        Returns:
            ScriptInfo: 解析后的剧本信息对象
        """
        lines = text.strip().split('\n')

        # 初始化剧本信息
        self.script_info = ScriptInfo(title="")

        # 解析各部分
        current_section = ""
        current_character_name = ""

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # 判断章节
            if self._is_title_section(line):
                current_section = "title"
                self._parse_title(lines[i:i+3])
                i += 3
                continue

            elif self._is_character_section(line):
                current_section = "character"
                i += 1
                continue

            elif self._is_scene_section(line):
                current_section = "scene"
                scene = self._parse_scene_header(line)
                if scene:
                    self.script_info.scenes.append(scene)
                current_character_name = ""
                i += 1
                continue

            elif self._is_ending_section(line):
                current_section = "ending"
                self._parse_ending(lines[i:])
                break

            # 解析内容
            if current_section == "character":
                self._parse_character_line(line, lines, i)

            elif current_section == "scene" and self.script_info.scenes:
                self._parse_scene_content(line, self.script_info.scenes[-1])

            i += 1

        return self.script_info

    def _is_title_section(self, line: str) -> bool:
        """判断是否是剧名章节"""
        return "剧名" in line or line.startswith("一、") or "时长" in line

    def _is_character_section(self, line: str) -> bool:
        """判断是否是主角特征章节"""
        return "主角" in line or line.startswith("二、") or "角色" in line

    def _is_scene_section(self, line: str) -> bool:
        """判断是否是剧情脉络章节"""
        return "剧情" in line or line.startswith("三、") or re.match(r'^\d+\.', line)

    def _is_ending_section(self, line: str) -> bool:
        """判断是否是结局章节"""
        return "结局" in line or "结局" in line or line.startswith("四、")

    def _parse_title(self, lines: List[str]) -> None:
        """解析剧名部分"""
        for line in lines:
            line = line.strip()
            if "《" in line and "》" in line:
                match = re.search(r"《(.+?)》", line)
                if match:
                    self.script_info.title = match.group(1)
            if "时长" in line:
                match = re.search(r"时长[：:](.+)", line)
                if match:
                    self.script_info.duration = match.group(1).strip()
            if "场景" in line:
                match = re.search(r"场景[：:](.+)", line)
                if match:
                    self.script_info.location = match.group(1).strip()

    def _parse_character_line(self, line: str, all_lines: List[str], index: int) -> None:
        """解析角色行"""
        # 匹配角色名格式：角色名（性别，身份）
        match = re.match(r'^([^\s（]+)[:：]?\s*（(.+?)）', line)
        if not match:
            # 尝试匹配格式：角色名（男/女，...）
            match = re.match(r'^([^\s（]+)\s*[（(]([^）)]+)[）)]', line)

        if match:
            name = match.group(1).strip()
            details = match.group(2).strip()

            # 解析性别和身份
            gender = ""
            identity = ""

            if "男" in details:
                gender = "男"
            elif "女" in details:
                gender = "女"

            # 查找已存在的角色
            existing_char = None
            for char in self.script_info.characters:
                if char.name == name:
                    existing_char = char
                    break

            if not existing_char:
                char = Character(name=name, gender=gender, identity=identity)
                self.script_info.characters.append(char)

            # 继续解析描述
            j = index + 1
            while j < len(all_lines) and j < index + 5:
                desc_line = all_lines[j].strip()
                if not desc_line or desc_line.startswith("三") or re.match(r'^\d+\.', desc_line):
                    break
                if "人设" in desc_line:
                    match = re.search(r"人设[：:](.+)", desc_line)
                    if match:
                        if existing_char:
                            existing_char.personality = match.group(1).strip()
                        else:
                            char.personality = match.group(1).strip()
                elif "特殊能力" in desc_line:
                    match = re.search(r"特殊能力[：:](.+)", desc_line)
                    if match:
                        ability = match.group(1).strip()
                        if existing_char:
                            existing_char.abilities.append(ability)
                        else:
                            char.abilities.append(ability)
                elif "隐藏身份" in desc_line:
                    match = re.search(r"隐藏身份[：:](.+)", desc_line)
                    if match:
                        if existing_char:
                            existing_char.hidden_identity = match.group(1).strip()
                        else:
                            char.hidden_identity = match.group(1).strip()
                elif "外貌" in desc_line or "穿着" in desc_line:
                    match = re.search(r"[外貌穿着]+[：:](.+)", desc_line)
                    if match:
                        if existing_char:
                            existing_char.appearance += " " + match.group(1).strip()
                        else:
                            char.appearance += " " + match.group(1).strip()
                j += 1
        else:
            # 解析角色属性行
            for char in self.script_info.characters:
                if char.name in line:
                    if "人设" in line:
                        match = re.search(r"人设[：:](.+)", line)
                        if match:
                            char.personality = match.group(1).strip()
                    elif "外貌" in line or "穿着" in line:
                        match = re.search(r"[外貌穿着]+[：:](.+)", line)
                        if match:
                            char.appearance = match.group(1).strip()

    def _parse_scene_header(self, line: str) -> Optional[Scene]:
        """解析场景标题"""
        # 匹配格式：1. 开场：闯入者 或 开场：闯入者
        match = re.match(r'^(\d+)\.?\s*(.+?)[：:](.+)', line)
        if match:
            number = int(match.group(1))
            title = match.group(3).strip()
            return Scene(number=number, title=title)
        return None

    def _parse_scene_content(self, line: str, scene: Scene) -> None:
        """解析场景内容"""
        line = line.strip()
        if not line:
            return

        # 解析镜头描述：（镜头：...）
        if line.startswith("（") or line.startswith("("):
            if "镜头" in line or "画面" in line:
                # 简化匹配：提取冒号后的内容
                start = line.find("：")
                if start != -1:
                    scene.camera_desc = line[start+1:].strip().strip('""\u201c\u201d')
                else:
                    scene.camera_desc = line.strip("（）()")

        # 解析对话：角色名："内容" 或 角色名（动作）："内容"
        # 更通用的匹配模式，使用普通引号
        dialogue_match = re.match(r'^([^（(]+?)[（(]([^）)]+?)[）)]?[:：]?\s*["](.+?)["]?', line)
        if dialogue_match:
            char_name = dialogue_match.group(1).strip()
            action = dialogue_match.group(2).strip()
            content = dialogue_match.group(3).strip()
            content = content.strip('"\u201c\u201d')

            # 推断情感
            emotion = self._infer_emotion(action, content)

            dialogue = Dialogue(
                character=char_name,
                content=content,
                emotion=emotion,
                action=action
            )
            scene.dialogues.append(dialogue)
            return

        # 尝试匹配标准对话格式：角色名："内容"
        dialogue_match = re.match(r'^([^：:]+)[:：]\s*["""](.+)["""]?', line)
        if dialogue_match:
            char_name = dialogue_match.group(1).strip()
            content = dialogue_match.group(2).strip()
            content = content.strip('"\u201c\u201d')

            dialogue = Dialogue(
                character=char_name,
                content=content,
                emotion="normal",
                action=""
            )
            scene.dialogues.append(dialogue)

    def _infer_emotion(self, action: str, content: str) -> str:
        """根据动作和内容推断情感"""
        action_lower = action.lower()
        content_lower = content.lower()

        # 关键词匹配
        emotion_keywords = {
            "happy": ["笑", "开心", "高兴", "哈哈", "😊", "：）", ":)", "吐槽"],
            "sad": ["哭", "难过", "伤心", "叹息", "无奈"],
            "angry": ["怒", "气愤", "吼", "大声", "生气"],
            "surprised": ["惊讶", "吃惊", "震惊", "愣", "……", "..."]
        }

        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in action or keyword in content:
                    return emotion

        return "normal"

    def _parse_ending(self, lines: List[str]) -> None:
        """解析结局部分"""
        ending_lines = [line.strip() for line in lines if line.strip()]
        self.script_info.ending = " ".join(ending_lines)

    def get_character_color(self, name: str) -> Tuple[int, int, int]:
        """获取角色颜色"""
        for char in self.script_info.characters:
            if char.name == name:
                return char.color
        return (128, 128, 128)  # 默认灰色

    def get_character(self, name: str) -> Optional[Character]:
        """获取角色信息"""
        for char in self.script_info.characters:
            if char.name == name:
                return char
        return None


def parse_script_file(file_path: str) -> ScriptInfo:
    """
    解析剧本文件

    Args:
        file_path: 剧本文件路径

    Returns:
        ScriptInfo: 解析后的剧本信息
    """
    # 根据文件扩展名选择解析方式
    if file_path.endswith('.docx'):
        try:
            from docx import Document
            doc = Document(file_path)
            text = '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ImportError("请安装 python-docx 库以解析 .docx 文件")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

    parser = ScriptParser()
    return parser.parse(text)
