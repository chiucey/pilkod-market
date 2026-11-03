#!/usr/bin/env python3
"""
remove_bg.py — 用本地 rembg 给图片抠图（去背景），输出带透明通道的 PNG。

为什么必须用脚本：rembg 自带的命令行入口（`rembg i ...`）在 Python 3.12 下会因
顶层 import gradio -> pkg_resources 而直接崩溃，无法使用。它的抠图核心其实在
Python API `rembg.remove()` 里，完全正常。所以这个脚本用 rembg 装在的那个
隔离解释器直接调 API，绕开坏掉的 CLI。这也是"skill 配脚本"的典型价值——
把一个装起来很折腾、CLI 又坏的工具，封装成一条稳定命令。

—— 环境初始化（换新机器 / 首次使用时）——
rembg 用 `uv tool` 装成一个隔离工具，不污染系统 python：
  1) 装 uv（若没有）：curl -LsSf https://astral.sh/uv/install.sh | sh
  2) 装 rembg：       uv tool install rembg
  3) 找解释器：       uv tool dir   # rembg 解释器在 <该目录>/rembg/bin/python
本机路径（macOS，供参考）：~/.local/share/uv/tools/rembg/bin/python
依赖：rembg 2.x + onnxruntime + Pillow（uv tool install 会一并装好）
模型：首次运行自动下载到 ~/.u2net/（u2net ~176M，一次性）

正确调用：
  <rembg-python> remove_bg.py in.png out.png
  例：~/.local/share/uv/tools/uv-tools/rembg/bin/python  ← 若上面路径不对，用 `uv tool dir` 查

速度参考：CPU 下约 9~10s/张（512px）；首次运行会下载模型（~176M，一次性）。

用法：
  <rembg-python> remove_bg.py <输入图> <输出.png> [--model u2net]
  自检：<任意 python3> remove_bg.py --check   # 检测 rembg 环境是否就绪并给出安装指令
"""
from __future__ import annotations  # 关键：让 `str | None` 等注解在 Python 3.7~3.9 也能跑
                                    # （rembg 隔离解释器常是 3.9.x，无此行直接用它跑本脚本会崩）
import os
import sys
import time


def find_rembg_python() -> str | None:
    """在常见位置找 rembg 的隔离解释器路径；找不到返回 None。"""
    candidates = [
        os.path.expanduser("~/.local/share/uv/tools/rembg/bin/python"),
        os.path.expanduser("~/.local/share/uv/tools/rembg/bin/python3"),
    ]
    # uv tool dir 动态查（跨平台最稳）
    try:
        import subprocess
        d = subprocess.run(["uv", "tool", "dir"], capture_output=True, text=True, timeout=10)
        if d.returncode == 0:
            base = d.stdout.strip()
            candidates.insert(0, os.path.join(base, "rembg", "bin", "python"))
            candidates.insert(1, os.path.join(base, "rembg", "Scripts", "python.exe"))  # windows
    except Exception:
        pass
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


INSTALL_HELP = """\
rembg 环境未就绪。按下面三步初始化（一次性）：
  1) 装 uv（若没有）：curl -LsSf https://astral.sh/uv/install.sh | sh
     装完刷新 PATH：  source "$HOME/.local/bin/env"   （否则下一步 uv 找不到）
  2) 装 rembg：       uv tool install rembg --with onnxruntime --with pillow
     ⚠️ 必须带 --with：裸装 rembg 不含 onnxruntime，会 import 崩
  3) 自检：           python3 remove_bg.py --check
说明：uv tool 装进隔离环境不动系统 python；首次抠图自动下模型到 ~/.u2net/（~176M，一次性）。"""


def pick_providers(accel: str):
    """跨端选 onnxruntime provider。返回 (providers列表, 人类可读说明)。

    accel:
      auto (默认) — 按平台 + 实际可用 provider 自动选：
        · Windows/Linux 有 NVIDIA(CUDA) 或 AMD/Intel(DirectML/ROCm) → 用 GPU
        · macOS → 一律 CPU（CoreML 加载大模型会初始化死锁，实测坑，主动跳过）
        · 其余 → CPU 兜底
      gpu  — 强制走可用的 GPU provider；没有则告警并降 CPU
      cpu  — 强制 CPU（最稳，跨端都能跑）
    """
    import platform
    try:
        import onnxruntime as ort
        avail = ort.get_available_providers()
    except Exception:
        return ["CPUExecutionProvider"], "CPU（onnxruntime 不可用，兜底）"

    is_mac = platform.system() == "Darwin"
    # 按优先级挑一个可用的 GPU provider（NVIDIA CUDA > AMD/Intel DirectML(win) > ROCm(linux)）
    gpu_order = ["CUDAExecutionProvider", "DmlExecutionProvider", "ROCMExecutionProvider"]
    gpu = next((g for g in gpu_order if g in avail), None)

    if accel == "cpu":
        return ["CPUExecutionProvider"], "CPU（强制）"
    if accel == "gpu":
        if gpu:
            return [gpu, "CPUExecutionProvider"], f"GPU：{gpu}（强制，CPU 兜底）"
        return ["CPUExecutionProvider"], "CPU（--accel gpu 但未检测到可用 GPU provider，已降级）"
    # auto
    if is_mac:
        return ["CPUExecutionProvider"], "CPU（macOS 自动降级，避开 CoreML 死锁）"
    if gpu:
        return [gpu, "CPUExecutionProvider"], f"GPU：{gpu}（自动，CPU 兜底）"
    return ["CPUExecutionProvider"], "CPU（自动，未检测到 GPU）"


def do_check() -> int:
    """自检：报告 rembg 环境状态 + 该用哪个解释器。"""
    p = find_rembg_python()
    if not p:
        print("❌ 没找到 rembg 隔离解释器。\n" + INSTALL_HELP)
        return 1
    print(f"✅ rembg 解释器：{p}")
    import subprocess
    probe = (
        "import rembg,PIL,onnxruntime,platform;"
        "av=onnxruntime.get_available_providers();"
        "print('rembg',getattr(rembg,'__version__','?'),'| onnxruntime',onnxruntime.__version__);"
        "print('平台',platform.system(),platform.machine(),'| 可用 providers:',av);"
        "gpu=next((g for g in ['CUDAExecutionProvider','DmlExecutionProvider','ROCMExecutionProvider'] if g in av),None);"
        "print('auto 将使用:', 'CPU(mac 避 CoreML 死锁)' if platform.system()=='Darwin' else ('GPU '+gpu if gpu else 'CPU(未检测到 GPU)'))"
    )
    r = subprocess.run([p, "-c", probe], capture_output=True, text=True)
    if r.returncode == 0:
        print("✅ 依赖就绪：" + r.stdout.strip())
        print(f"➡️  调用方式：{p} remove_bg.py in.png out.png [--accel auto|gpu|cpu]")
        return 0
    print("⚠️ 解释器在但依赖有问题：\n" + (r.stderr or r.stdout).strip() + "\n" + INSTALL_HELP)
    return 1


def main() -> int:
    import argparse
    p = argparse.ArgumentParser(description="rembg 抠图（去背景）")
    p.add_argument("inp", nargs="?", help="输入图片路径")
    p.add_argument("out", nargs="?", help="输出 PNG 路径（带透明通道）")
    p.add_argument("--model", default="u2net",
                   help="u2net(默认,通用最快~10s,90%%素材够用) / isnet-general-use(边缘略精细) / "
                        "birefnet-general-lite(环/洞/C形/月牙/镂空专用,~17s)")
    p.add_argument("--check", action="store_true", help="仅检测 rembg 环境是否就绪")
    p.add_argument("--accel", default="auto", choices=["auto", "gpu", "cpu"],
                   help="加速方式：auto(默认,按平台+可用硬件自动选;mac一律CPU) / gpu(强制GPU,无则降CPU) / cpu(强制CPU)")
    a = p.parse_args()

    if a.check:
        return do_check()
    if not a.inp or not a.out:
        p.error("需要 <输入图> <输出.png>，或用 --check 自检环境")

    try:
        from rembg import remove, new_session
        from PIL import Image
    except ModuleNotFoundError as e:
        print(f"缺少依赖 {e.name}。本脚本必须用 rembg 所在解释器运行。\n" + INSTALL_HELP,
              file=sys.stderr)
        return 2

    t = time.time()
    providers, accel_desc = pick_providers(a.accel)
    try:
        # 跨端 provider 选择见 pick_providers()：
        # Windows/Linux 有显卡走 GPU(CUDA/DirectML/ROCm)，mac 及无卡走 CPU。
        # 注意：macOS 的 CoreML 加载 isnet/birefnet 大计算图会初始化死锁（睡眠、%CPU=0、卡十几分钟
        # 不报错），所以 auto 在 mac 上一律用 CPU 绕开。CPU 下 u2net~10s/isnet~4s/birefnet-lite~17s。
        print(f"⚙️  加速：{accel_desc}", file=sys.stderr)
        session = new_session(a.model, providers=providers)
        img = Image.open(a.inp)
        out = remove(img, session=session)
        # 确保是 RGBA 再存
        if out.mode != "RGBA":
            out = out.convert("RGBA")
        out.save(a.out)
    except FileNotFoundError:
        print(f"找不到输入文件: {a.inp}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"抠图失败: {e}", file=sys.stderr)
        return 1

    # 抠图干净度自检：算 alpha>10 的不透明像素占比（opaque ratio）。
    # 用途：判断"环/洞/C形/镂空"素材是否被显著性模型补全成实心。
    # 例：弦月本该 ~9~13%，若抠出来 30%+ 多半被 u2net 补成圆盘了 → 换 birefnet-general-lite 重来。
    opaque_pct = None
    try:
        alpha = out.split()[-1]
        hist = alpha.histogram()
        total = out.size[0] * out.size[1]
        opaque = sum(hist[11:])  # alpha 11~255 视为不透明
        opaque_pct = 100.0 * opaque / total if total else 0.0
    except Exception:
        pass

    msg = f"✅ 抠图完成 {out.size} RGBA -> {a.out} | 模型 {a.model} | 耗时 {time.time()-t:.1f}s"
    if opaque_pct is not None:
        msg += f" | 不透明占比 {opaque_pct:.1f}%"
        if opaque_pct >= 85:
            msg += "  ⚠️ 占比极高：几乎没抠掉背景，检查主体/底色对比或换模型"
        elif opaque_pct >= 30 and a.model in ("u2net", "u2netp", "isnet-general-use"):
            msg += "  ⚠️ 占比偏高：若这是环/洞/月牙/镂空素材，可能被补全成实心，建议 --model birefnet-general-lite 重试"
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
