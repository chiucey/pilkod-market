"""
小米 MiMo V2 TTS 客户端封装
"""

import os
import base64
from typing import Optional, Dict, Any


class MimoTTSClient:
    """MiMo V2 文本转语音客户端"""

    BASE_URL = "https://api.xiaomimimo.com/v1"
    MODEL = "mimo-v2-tts"

    # 可用音色映射
    VOICES = {
        "default": "mimo_default",
        "zh": "default_zh",
        "en": "default_en",
    }

    # 支持的风格
    STYLES = {
        "speed_up": "_Speed up",
        "slow_down": "_Slow down",
        "happy": "_Happy",
        "sad": "_Sad",
        "angry": "_Angry",
        "whisper": "_Whisper",
        "singing": "<|sing|>",
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            api_key: API 密钥，默认从环境变量 MIMO_API_KEY 获取
        """
        self.api_key = api_key or os.environ.get("MIMO_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required. Set MIMO_API_KEY environment variable or pass api_key parameter.")

    def _format_text(self, text: str, style: Optional[str] = None) -> str:
        """格式化文本，添加风格标签"""
        if style and style in self.STYLES:
            return f"<|style:{self.STYLES[style]}|>{text}"
        elif style:
            return f"<|style:{style}|>{text}"
        return text

    def synthesize(
        self,
        text: str,
        voice: str = "mimo_default",
        format: str = "wav",
        style: Optional[str] = None,
        user_message: Optional[str] = None,
    ) -> bytes:
        """
        合成语音

        Args:
            text: 要合成的文本（放在 assistant 角色中）
            voice: 音色选择
            format: 音频格式（wav, mp3 等）
            style: 语音风格
            user_message: 可选的 user 角色消息，用于调整语气

        Returns:
            bytes: 音频数据

        Raises:
            Exception: API 调用失败时抛出异常
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai package: pip install openai")

        client = OpenAI(api_key=self.api_key, base_url=self.BASE_URL)

        messages = []
        if user_message:
            messages.append({"role": "user", "content": user_message})
        messages.append({"role": "assistant", "content": self._format_text(text, style)})

        completion = client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            audio={"format": format, "voice": voice},
        )

        message = completion.choices[0].message
        audio_data = message.audio.data
        return base64.b64decode(audio_data)

    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        voice: str = "mimo_default",
        format: str = "wav",
        style: Optional[str] = None,
        user_message: Optional[str] = None,
    ) -> str:
        """
        合成语音并保存到文件

        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            voice: 音色选择
            format: 音频格式
            style: 语音风格
            user_message: 可选的 user 角色消息

        Returns:
            str: 保存的文件路径
        """
        audio_bytes = self.synthesize(text, voice, format, style, user_message)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        return output_path


# 命令行接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="小米 MiMo V2 TTS 客户端")
    parser.add_argument("--text", "-t", required=True, help="要合成的文本")
    parser.add_argument("--output", "-o", default="output.wav", help="输出文件路径")
    parser.add_argument("--voice", "-v", default="mimo_default", help="音色选择")
    parser.add_argument("--format", "-f", default="wav", help="音频格式")
    parser.add_argument("--style", "-s", help="语音风格")
    parser.add_argument("--api-key", "-k", help="API 密钥")

    args = parser.parse_args()

    client = MimoTTSClient(api_key=args.api_key)
    result = client.synthesize_to_file(
        text=args.text,
        output_path=args.output,
        voice=args.voice,
        format=args.format,
        style=args.style,
    )
    print(f"Audio saved to: {result}")
