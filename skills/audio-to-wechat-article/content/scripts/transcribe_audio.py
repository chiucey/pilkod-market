#!/usr/bin/env python3
# 直播/访谈/播客内容转写脚本：支持中英文音频(mp3/wav等)和字幕文本文件(srt/txt)
# 用法: python3 transcribe_audio.py <输入文件> <输出前缀> [语言代码, 如 zh 或 en, 缺省自动检测]
# 产物: <前缀>_plain.txt 纯文本稿(无时间戳；中文统一为简体；英文保留原文)
import sys, os, re, subprocess

def ensure(pkg, import_name=None, index="https://pypi.tuna.tsinghua.edu.cn/simple"):
    try:
        __import__(import_name or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-i", index, "--quiet"])

ensure("opencc-python-reimplemented", "opencc")
import opencc

src, prefix = sys.argv[1], sys.argv[2]
lang = sys.argv[3] if len(sys.argv) > 3 else None
ext = os.path.splitext(src)[1].lower()

def clean_text(text):
    # 去除srt序号与时间戳行、常见字幕标签，合并为纯文本
    text = re.sub(r"\d{2}:\d{2}:\d{2}[,\.]\d{2,3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{2,3}.*", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    lines = [l.strip() for l in text.splitlines()]
    lines = [l for l in lines if l and not l.strip().isdigit()]
    text = "\n".join(lines)
    # 含中文则统一转简体
    if re.search(r"[一-鿿]", text):
        text = opencc.OpenCC("t2s").convert(text)
    return re.sub(r"\n{2,}", "\n", text).strip()

if ext in (".srt", ".txt", ".vtt"):
    raw = open(src, encoding="utf-8", errors="ignore").read()
    plain = clean_text(raw)
else:
    ensure("faster-whisper", "faster_whisper")
    # av 19.x 与 faster-whisper 不兼容(metadata_errors参数)，需固定为12.x；安装过程可能损坏，失败则强制重装
    try:
        import av
        broken = int(av.__version__.split(".")[0]) >= 19
    except Exception:
        broken = True
    if broken:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "av==12.3.0",
                               "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "--quiet",
                               "--force-reinstall", "--no-deps"])
        print("av已修复, 请重新运行本脚本"); sys.exit(0)
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")  # 国内镜像加速模型下载
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")             # 避免xet后端401报错
    from faster_whisper import WhisperModel
    # 沙箱内存约5GB: medium模型单进程cpu_threads=2, 多个文件务必逐个转写, 不要并行
    model = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=2)
    segments, info = model.transcribe(src, language=lang, vad_filter=True, beam_size=5)
    plain = clean_text("\n".join(s.text for s in segments))

with open(prefix + "_plain.txt", "w") as f:
    f.write(plain)
print(f"done, 文稿{len(plain)}字 -> {prefix}_plain.txt")
