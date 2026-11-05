"""
Game Art AI Generator - Sound Generator
游戏美术AI生成器 - 音效匹配模块

根据游戏主题自动匹配生成音效
"""

import os
import logging
import hashlib
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

# 配置日志
logger = logging.getLogger('SoundGenerator')


class SoundType(Enum):
    """音效类型"""
    BGM = "bgm"
    SFX_BUTTON = "sfx_button"
    SFX_COIN = "sfx_coin"
    SFX_SUCCESS = "sfx_success"
    SFX_FAIL = "sfx_fail"
    SFX_TRANSITION = "sfx_transition"
    SFX_AD_TRIGGER = "sfx_ad_trigger"


@dataclass
class SoundAsset:
    """音效资源"""
    sound_type: SoundType
    name: str
    file_path: str
    duration: float = 0.0
    format: str = "mp3"
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class SoundConfig:
    """音效配置"""
    bgm_tempo: int = 120  # BPM
    bgm_style: str = "casual"
    sfx_volume: float = 0.8
    bgm_volume: float = 0.5
    loop_bgm: bool = True


class SoundMatcher:
    """音效匹配生成器"""

    # 主题音效映射
    THEME_SOUND_PROFILES = {
        "太空": {
            "bgm_tempo": 110,
            "bgm_style": "electronic",
            "sfx_tone": "sci-fi"
        },
        "复古": {
            "bgm_tempo": 130,
            "bgm_style": "chiptune",
            "sfx_tone": "retro"
        },
        "可爱": {
            "bgm_tempo": 140,
            "bgm_style": "cute",
            "sfx_tone": "kawaii"
        },
        "竞技": {
            "bgm_tempo": 160,
            "bgm_style": "energetic",
            "sfx_tone": "impact"
        },
        "治愈": {
            "bgm_tempo": 90,
            "bgm_style": "calm",
            "sfx_tone": "soft"
        },
        "恐怖": {
            "bgm_tempo": 80,
            "bgm_style": "dark",
            "sfx_tone": "scary"
        },
        "美食": {
            "bgm_tempo": 120,
            "bgm_style": "warm",
            "sfx_tone": "bubbly"
        },
        "自然": {
            "bgm_tempo": 100,
            "bgm_style": "ambient",
            "sfx_tone": "natural"
        }
    }

    # 音效关键词映射
    SFX_KEYWORDS = {
        "button": SoundType.SFX_BUTTON,
        "coin": SoundType.SFX_COIN,
        "success": SoundType.SFX_SUCCESS,
        "fail": SoundType.SFX_FAIL,
        "transition": SoundType.SFX_TRANSITION,
        "ad": SoundType.SFX_AD_TRIGGER
    }

    def __init__(
        self,
        theme_keywords: str = "",
        game_type: str = "",
        output_dir: str = "./sounds"
    ):
        """
        初始化音效匹配器

        Args:
            theme_keywords: 主题关键词
            game_type: 游戏类型
            output_dir: 输出目录
        """
        self.theme_keywords = theme_keywords
        self.game_type = game_type
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config = self._match_config()

    def _match_config(self) -> SoundConfig:
        """根据主题匹配音效配置"""
        config = SoundConfig()

        # 分析关键词
        keywords_lower = self.theme_keywords.lower()

        for theme, profile in self.THEME_SOUND_PROFILES.items():
            if theme in keywords_lower:
                config.bgm_tempo = profile["bgm_tempo"]
                config.bgm_style = profile["bgm_style"]
                break
        else:
            # 默认配置
            if self.game_type == "competitive":
                config.bgm_tempo = 150
                config.bgm_style = "energetic"
            elif self.game_type == "relaxing":
                config.bgm_tempo = 95
                config.bgm_style = "calm"

        return config

    def get_bgm_prompt(self, bgm_index: int = 0) -> str:
        """
        获取BGM生成提示词

        Args:
            bgm_index: BGM编号(0或1)

        Returns:
            生成提示词
        """
        style = self.config.bgm_style
        tempo = self.config.bgm_tempo

        prompts = {
            "chiptune": f"{tempo}bpm pixel game music loop, 8-bit retro style, cheerful",
            "cute": f"{tempo}bpm kawaii background music, cute playful loop, soft",
            "electronic": f"{tempo}bpm space ambient electronic, futuristic loop",
            "energetic": f"{tempo}bpm energetic game music, action loop, intense",
            "calm": f"{tempo}bpm calm relaxing loop, gentle melody, zen",
            "dark": f"{tempo}bpm dark ambient, mysterious atmosphere, suspenseful",
            "warm": f"{tempo}bpm warm cozy music, friendly loop, inviting",
            "ambient": f"{tempo}bpm nature ambient, peaceful loop, serene"
        }

        return prompts.get(style, prompts["chiptune"])

    def get_sfx_prompt(self, sound_type: SoundType) -> str:
        """
        获取音效生成提示词

        Args:
            sound_type: 音效类型

        Returns:
            生成提示词
        """
        tone = self._get_sfx_tone()
        style = self.config.bgm_style

        sfx_prompts = {
            SoundType.SFX_BUTTON: f"game button click sound, {tone}, crisp, short 0.2s",
            SoundType.SFX_COIN: f"collect coin sound, {tone}, satisfying, 0.3s",
            SoundType.SFX_SUCCESS: f"success fanfare, {tone}, triumphant, 0.5s",
            SoundType.SFX_FAIL: f"failure sound, {tone}, sad, 0.4s",
            SoundType.SFX_TRANSITION: f"whoosh transition sound, {tone}, smooth, 0.3s",
            SoundType.SFX_AD_TRIGGER: f"reward ad notification sound, {tone}, inviting, 0.5s"
        }

        return sfx_prompts.get(sound_type, sfx_prompts[SoundType.SFX_BUTTON])

    def _get_sfx_tone(self) -> str:
        """获取音效音色"""
        style = self.config.bgm_style

        tone_map = {
            "chiptune": "8-bit retro chip sound",
            "cute": "cute kawaii bubble sound",
            "electronic": "sci-fi electronic blip",
            "energetic": "impact punchy sound",
            "calm": "soft gentle chime",
            "dark": "deep ominous tone",
            "warm": "soft rounded sound",
            "ambient": "natural soft tone"
        }

        return tone_map.get(style, "crisp game sound")

    def generate_sound_metadata(self) -> Dict[str, Any]:
        """
        生成音效元数据（供后续API调用使用）

        Returns:
            音效生成配置
        """
        metadata = {
            "theme_keywords": self.theme_keywords,
            "game_type": self.game_type,
            "config": {
                "bgm_tempo": self.config.bgm_tempo,
                "bgm_style": self.config.bgm_style,
                "sfx_volume": self.config.sfx_volume,
                "bgm_volume": self.config.bgm_volume,
                "loop_bgm": self.config.loop_bgm
            },
            "assets_to_generate": []
        }

        # BGM
        for i in range(2):
            metadata["assets_to_generate"].append({
                "type": "bgm",
                "index": i,
                "prompt": self.get_bgm_prompt(i),
                "filename": f"bgm_{i+1}.mp3",
                "duration": 60.0,
                "loop": True
            })

        # SFX
        for sfx_type in [SoundType.SFX_BUTTON, SoundType.SFX_COIN,
                         SoundType.SFX_SUCCESS, SoundType.SFX_FAIL,
                         SoundType.SFX_AD_TRIGGER]:
            metadata["assets_to_generate"].append({
                "type": sfx_type.value,
                "prompt": self.get_sfx_prompt(sfx_type),
                "filename": f"{sfx_type.value}.mp3",
                "duration": 0.5,
                "loop": False
            })

        return metadata

    def save_metadata(self, output_path: str = None) -> str:
        """保存音效元数据"""
        if output_path is None:
            output_path = self.output_dir / "sound_metadata.json"
        else:
            output_path = Path(output_path)

        metadata = self.generate_sound_metadata()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"[SoundGenerator] Metadata saved to: {output_path}")
        return str(output_path)

    def create_sound_manifest(self) -> Dict[str, Any]:
        """
        创建音效清单（用于Construct3导入）

        Returns:
            音效清单
        """
        manifest = {
            "game_name": self.theme_keywords,
            "generated_at": self._get_timestamp(),
            "audio_files": [
                {
                    "name": "bgm_1",
                    "filename": "bgm_1.mp3",
                    "type": "bgm",
                    "loop": True,
                    "volume": self.config.bgm_volume
                },
                {
                    "name": "bgm_2",
                    "filename": "bgm_2.mp3",
                    "type": "bgm",
                    "loop": True,
                    "volume": self.config.bgm_volume
                },
                {
                    "name": "btn_click",
                    "filename": "sfx_button.mp3",
                    "type": "sfx",
                    "loop": False,
                    "volume": self.config.sfx_volume
                },
                {
                    "name": "coin_collect",
                    "filename": "sfx_coin.mp3",
                    "type": "sfx",
                    "loop": False,
                    "volume": self.config.sfx_volume
                },
                {
                    "name": "level_complete",
                    "filename": "sfx_success.mp3",
                    "type": "sfx",
                    "loop": False,
                    "volume": self.config.sfx_volume
                },
                {
                    "name": "game_over",
                    "filename": "sfx_fail.mp3",
                    "type": "sfx",
                    "loop": False,
                    "volume": self.config.sfx_volume
                },
                {
                    "name": "ad_available",
                    "filename": "sfx_ad_trigger.mp3",
                    "type": "sfx",
                    "loop": False,
                    "volume": self.config.sfx_volume
                }
            ]
        }

        return manifest

    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class SoundPlaceholder:
    """音效占位符（当没有TTS服务时）"""

    # 默认短音效（base64编码的静音/简单音效）
    PLACEHOLDER_SFX = {
        SoundType.SFX_BUTTON: "placeholder_button.mp3",
        SoundType.SFX_COIN: "placeholder_coin.mp3",
        SoundType.SFX_SUCCESS: "placeholder_success.mp3",
        SoundType.SFX_FAIL: "placeholder_fail.mp3",
        SoundType.SFX_AD_TRIGGER: "placeholder_ad.mp3"
    }

    def __init__(self, output_dir: str = "./sounds"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_placeholder(self, sound_type: SoundType) -> SoundAsset:
        """创建占位音效"""
        logger.warning(f"[SoundPlaceholder] Creating placeholder for {sound_type.value}")

        filename = self.PLACEHOLDER_SFX.get(sound_type, "placeholder.mp3")
        filepath = self.output_dir / filename

        # 创建简单占位文件
        with open(filepath, 'wb') as f:
            # 写入简单的WAV文件头（静音）
            import struct
            # WAV header
            f.write(b'RIFF')
            f.write(struct.pack('<I', 36 + 16000))  # File size
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write(struct.pack('<I', 16))  # Subchunk size
            f.write(struct.pack('<H', 1))   # Audio format (PCM)
            f.write(struct.pack('<H', 1))   # Num channels
            f.write(struct.pack('<I', 16000))  # Sample rate
            f.write(struct.pack('<I', 32000))  # Byte rate
            f.write(struct.pack('<H', 2))   # Block align
            f.write(struct.pack('<H', 16))  # Bits per sample
            f.write(b'data')
            f.write(struct.pack('<I', 16000))  # Data size

        return SoundAsset(
            sound_type=sound_type,
            name=sound_type.value,
            file_path=str(filepath),
            duration=0.3,
            format="wav",
            metadata={"placeholder": True}
        )


def main():
    """测试"""
    print("=" * 60)
    print("Sound Generator Test")
    print("音效生成器测试")
    print("=" * 60)

    matcher = SoundMatcher(
        theme_keywords="复古像素 太空闯关",
        game_type="skill"
    )

    metadata = matcher.generate_sound_metadata()
    print("BGM Prompt:", matcher.get_bgm_prompt())
    print("\nSFX Prompts:")
    for st in SoundType:
        if st.value.startswith("sfx"):
            print(f"  {st.value}: {matcher.get_sfx_prompt(st)}")

    print("\nManifest:")
    print(json.dumps(matcher.create_sound_manifest(), indent=2))


if __name__ == "__main__":
    main()
