#!/usr/bin/env python3
"""技能包完整性自检 —— 安装后运行一次，确认包可用。

用法:
  python3 scripts/selftest.py

在技能目录内直接运行即可（自动定位自身所在技能根目录）。
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "scripts")

EXPECTED = [
    "fetch_bilibili.sh",
    "extract_frames.py",
    "build_report.py",
    "check_delivery.py",
]

fail = 0


def ok(msg):
    print(f"OK   {msg}")


def bad(msg):
    global fail
    print(f"FAIL {msg}")
    fail += 1


def warn(msg):
    print(f"WARN {msg}")


# 1) SKILL.md + frontmatter
skill_md = os.path.join(ROOT, "SKILL.md")
if not os.path.isfile(skill_md):
    bad("SKILL.md 缺失")
else:
    txt = open(skill_md, encoding="utf-8").read()
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        fm = parts[1] if len(parts) > 1 else ""
        if "name:" in fm and "description:" in fm:
            ok("SKILL.md 存在且有 YAML frontmatter (name + description)")
        else:
            bad("SKILL.md frontmatter 缺少 name 或 description")
    else:
        bad("SKILL.md 没有 YAML frontmatter")

# 2) 脚本齐全
missing = [s for s in EXPECTED if not os.path.isfile(os.path.join(SCRIPTS, s))]
if missing:
    bad(f"缺少脚本: {missing}")
else:
    ok(f"{len(EXPECTED)} 个脚本存在")
    for s in EXPECTED:
        p = os.path.join(SCRIPTS, s)
        if not os.access(p, os.X_OK):
            warn(f"{s} 不可执行 —— 装完记得 chmod +x scripts/*")

# 3) 语法检查
for s in [x for x in EXPECTED if x.endswith(".py")]:
    p = os.path.join(SCRIPTS, s)
    if not os.path.isfile(p):
        continue
    r = subprocess.run([sys.executable, "-m", "py_compile", p],
                       capture_output=True, text=True)
    if r.returncode == 0:
        ok(f"{s} Python 语法通过")
    else:
        bad(f"{s} 语法错误: {r.stderr.strip()[-300:]}")

for s in [x for x in EXPECTED if x.endswith(".sh")]:
    p = os.path.join(SCRIPTS, s)
    if not os.path.isfile(p):
        continue
    r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
    if r.returncode == 0:
        ok(f"{s} bash 语法通过")
    else:
        bad(f"{s} bash 语法错误: {r.stderr.strip()[-300:]}")

# 4) 依赖检查
try:
    import markdown_it  # noqa: F401
    ok("依赖 markdown-it-py 可用")
except ImportError:
    bad("缺依赖 markdown-it-py —— pip3 install markdown-it-py")

for tool in ("ffmpeg", "ffprobe"):
    r = subprocess.run(["command", "-v", tool], shell=True,
                       capture_output=True, text=True)
    if r.returncode == 0:
        ok(f"依赖 {tool} 可用")
    else:
        bad(f"缺依赖 {tool} —— apt-get install -y ffmpeg")

r = subprocess.run(["command", "-v", "yt-dlp"], shell=True,
                   capture_output=True, text=True)
if r.returncode == 0:
    ok("依赖 yt-dlp 可用（可选，用于探测字幕轨）")
else:
    warn("缺 yt-dlp（可选）—— 仅影响字幕轨探测")

# 5) build_report.py 的 --verify 分支可用
p = os.path.join(SCRIPTS, "build_report.py")
if os.path.isfile(p):
    r = subprocess.run(
        [sys.executable, p, "x", "x", "/dev/null", "--verify", "/dev/null"],
        capture_output=True, text=True)
    if r.returncode in (0, 1):
        ok("build_report.py --verify 分支可执行")
    else:
        warn("build_report.py --verify 分支异常退出")

print()
print(f"{'FAIL' if fail else 'PASS'} — 失败项 {fail}")
sys.exit(1 if fail else 0)
