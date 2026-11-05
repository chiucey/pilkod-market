#!/usr/bin/env python3
"""
Edge-TTS 文字转语音工具
使用 Microsoft Edge TTS 将文本转换为高质量音频

依赖安装:
    pip install edge-tts ffmpeg-python

使用方法:
    python tts_tool.py "文本内容" [声音ID] [输出文件]

示例:
    python tts_tool.py "Hello world" aria output.mp3
    python tts_tool.py "这是一段中文" xiaoxiao chinese.mp3
"""

import asyncio
import edge_tts
import ffmpeg
import sys
import os

# 声音映射表：短名称 -> 完整语音ID
VOICE_MAP = {
    # 英文女声
    "aria": "en-US-AriaNeural",
    "michelle": "en-US-MichelleNeural",
    "emma": "en-US-EmmaNeural",
    "ava": "en-US-AvaNeural",

    # 英文男声
    "christopher": "en-US-ChristopherNeural",
    "guy": "en-US-GuyNeural",
    "andrew": "en-US-AndrewNeural",
    "benjamin": "en-US-BenjaminNeural",

    # 中文女声
    "xiaoxiao": "zh-CN-XiaoxiaoNeural",
    "xiaoyi": "zh-CN-XiaoyiNeural",
    "lili": "zh-CN-LiliNeural",

    # 中文男声
    "yunyang": "zh-CN-YunyangNeural",
    "yunxi": "zh-CN-YunxiNeural",
    "yunye": "zh-CN-YunyeNeural",

    # 粤语
    "xiaoxiao_zh_hk": "zh-CN-XiaoxiaoNeural",
}


def get_voice_id(voice: str) -> str:
    """获取完整的语音ID"""
    return VOICE_MAP.get(voice.lower(), voice)


async def generate_tts(
    text: str,
    voice: str = "aria",
    output_file: str = "output.mp3"
) -> str:
    """
    生成高质量 TTS 音频

    Args:
        text: 要转换的文本内容
        voice: 声音ID（支持快捷键或完整语音ID）
        output_file: 输出文件路径

    Returns:
        输出文件路径
    """
    voice_id = get_voice_id(voice)

    print(f"正在生成音频...")
    print(f"  文本长度: {len(text)} 字符")
    print(f"  声音: {voice_id}")
    print(f"  输出: {output_file}")

    # 生成 ogg 格式临时文件
    temp_file = "temp_audio.ogg"

    try:
        # 使用 edge-tts 生成语音
        communicate = edge_tts.Communicate(text, voice=voice_id)
        await communicate.save(temp_file)
        print("  TTS 生成完成")

        # 检查临时文件是否生成
        if not os.path.exists(temp_file):
            raise FileNotFoundError("TTS 生成失败：临时文件未创建")

        # 使用 ffmpeg 转换为高质量 MP3
        print("  正在转换为高清 MP3...")
        ffmpeg.input(temp_file).output(
            output_file,
            codec="libmp3lame",
            bitrate="192k",
            ar=48000,
            ac=2
        ).overwrite_output().run(capture_stdout=True, capture_stderr=True)

        # 清理临时文件
        if os.path.exists(temp_file):
            os.remove(temp_file)

        # 获取输出文件大小
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"\n音频生成成功!")
        print(f"  文件: {output_file}")
        print(f"  大小: {file_size:.1f} KB")
        print(f"  规格: 192kbps / 48kHz / 立体声")

        return output_file

    except ffmpeg.Error as e:
        print(f"FFmpeg 转换失败: {e.stderr.decode() if e.stderr else str(e)}")
        raise
    except Exception as e:
        print(f"生成失败: {str(e)}")
        raise
    finally:
        # 确保清理临时文件
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass


def list_available_voices():
    """列出所有可用的声音（需要网络连接）"""
    print("正在获取可用声音列表...")
    try:
        voices = asyncio.run(edge_tts.list_voices())
        print(f"\n共 {len(voices)} 种声音可用:\n")

        # 按语言分组
        by_lang = {}
        for voice in voices:
            lang = voice Locale.split("-")[0]
            if lang not in by_lang:
                by_lang[lang] = []
            by_lang[lang].append(voice)

        for lang, voices_list in sorted(by_lang.items()):
            print(f"=== {lang.upper()} ===")
            for v in voices_list[:5]:  # 每种语言只显示前5个
                gender = "女" if "Female" in v["Gender"] else "男"
                print(f"  {v['ShortName']} - {gender} - {v['FriendlyName']}")
            if len(voices_list) > 5:
                print(f"  ... 还有 {len(voices_list) - 5} 种声音")
            print()

    except Exception as e:
        print(f"获取声音列表失败: {str(e)}")
        print("请检查网络连接")


def main():
    """主入口"""
    if len(sys.argv) < 2:
        print("Edge-TTS 文字转语音工具")
        print("=" * 40)
        print("使用方法:")
        print("  python tts_tool.py \"文本内容\" [声音ID] [输出文件]")
        print()
        print("声音快捷键:")
        print("  英文女声: aria, michelle, emma, ava")
        print("  英文男声: christopher, guy")
        print("  中文女声: xiaoxiao")
        print("  中文男声: yunyang, yunxi")
        print()
        print("示例:")
        print('  python tts_tool.py "Hello world" aria hello.mp3')
        print('  python tts_tool.py "这是一段中文" xiaoxiao chinese.mp3')
        print()
        print("输入 --list 可查看所有可用声音")
        sys.exit(0)

    if sys.argv[1] == "--list":
        list_available_voices()
        sys.exit(0)

    text = sys.argv[1]
    voice = sys.argv[2] if len(sys.argv) > 2 else "aria"
    output = sys.argv[3] if len(sys.argv) > 3 else "output.mp3"

    try:
        asyncio.run(generate_tts(text, voice, output))
    except Exception as e:
        print(f"\n错误: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
