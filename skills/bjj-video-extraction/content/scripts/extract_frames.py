#!/usr/bin/env python3
"""抽帧工具：概览层 / 接触印相 / 按时间戳精确抽帧

用法:
  # 概览层：每 N 秒一帧，用于定位内容块
  python3 extract_frames.py overview video.mp4 out_dir --interval 120

  # 接触印相：一张图看 20 帧，快速目视定位
  python3 extract_frames.py contact video.mp4 out_dir --interval 30 --tile 5x4

  # 精确抽帧：按 ASR 时间戳
  python3 extract_frames.py keyframes video.mp4 out_dir --times 300,430,520
"""
import argparse, os, subprocess, sys


def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FFMPEG 失败:\n{r.stderr[-1500:]}", file=sys.stderr)
        sys.exit(1)


def duration(path):
    out = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","csv=p=0",path], capture_output=True, text=True)
    try: return float(out.stdout.strip())
    except: return 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["overview","contact","keyframes"])
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--interval", type=int, default=120, help="概览/印相的抽帧间隔(秒)")
    ap.add_argument("--tile", default="5x4", help="接触印相排布,如 5x4")
    ap.add_argument("--times", default="", help="关键帧时间戳,逗号分隔(秒)")
    ap.add_argument("--width", type=int, default=640, help="单帧宽度")
    ap.add_argument("--q", type=int, default=3, help="JPEG 质量 2=高 5=低")
    ap.add_argument("--start", type=float, default=None, help="起始秒(只处理片段)")
    ap.add_argument("--dur", type=float, default=None, help="时长秒(只处理片段)")
    a = ap.parse_args()

    os.makedirs(a.outdir, exist_ok=True)

    # 片段模式：-ss/-t 前置能大幅缩短处理时间（35 分钟视频全量 contact sheet 约 2 分钟/张）
    win = ""
    if a.start is not None:
        win += f" -ss {a.start:.2f}"
    if a.dur is not None:
        win += f" -t {a.dur:.2f}"

    if a.mode == "overview":
        dur = duration(a.video)
        if a.dur is not None:
            dur = min(dur - (a.start or 0), a.dur)
        print(f"处理时长 {dur:.0f}s, 每 {a.interval}s 一帧, 约 {int(dur//a.interval)} 帧")
        run(f'ffmpeg -y{win} -i "{a.video}" -vf "fps=1/{a.interval},scale={a.width}:-1" '
            f'-q:v {a.q} "{a.outdir}/f_%04d.jpg"')
        print(f"完成 -> {a.outdir}")

    elif a.mode == "contact":
        w, h = [int(x) for x in a.tile.lower().split("x")]
        dur = duration(a.video)
        if a.dur is not None:
            dur = min(dur - (a.start or 0), a.dur)
        n = int(dur // a.interval)
        print(f"{n} 帧, 排成 {w}x{h}, 每张印相 {w*h} 帧")
        run(f'ffmpeg -y{win} -i "{a.video}" -vf "fps=1/{a.interval},scale=320:-1,tile={w}x{h}" '
            f'-q:v {a.q} "{a.outdir}/sheet_%02d.png"')
        print(f"完成 -> {a.outdir}")

    elif a.mode == "keyframes":
        times = [float(t) for t in a.times.split(",") if t.strip()]
        dur = duration(a.video)
        for i, t in enumerate(times, 1):
            # 每个时间点抽 3 帧(t-2, t, t+2)，避免只截到动作中间态
            for j, off in enumerate((-2, 0, 2), 1):
                tt = max(0, min(t + off, dur - 0.5))
                out = f"{a.outdir}/k{i:02d}_{'abc'[j-1]}.jpg"
                run(f'ffmpeg -y -ss {tt:.2f} -i "{a.video}" -frames:v 1 '
                    f'-vf "scale={a.width}:-1" -q:v {a.q} "{out}"')
            print(f"  k{i:02d} @ {t:.0f}s -> k{i:02d}_a/b/c.jpg")
        print(f"完成 -> {a.outdir}")


if __name__ == "__main__":
    main()
