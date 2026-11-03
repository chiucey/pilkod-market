#!/usr/bin/env python3
"""按文件管理器视觉顺序（或用户手动指定的顺序），把目标文件夹根目录下的所有文件
重命名为 EP{ep:02d}-C{n:02d}-T{t:02d}.{ext} 格式。

三种模式:
  1) 默认（有 GUI）: 读取 macOS Finder / Windows Explorer 当前窗口的视觉显示顺序
  2) --list: 只列出文件并加编号，不改名。用于无 GUI 环境里让用户先看到列表
  3) --order "3,1,2,4": 用户给出索引顺序（对应 --list 的编号），按这个顺序重命名

典型用法:
  python rename.py                    # 本地 macOS/Windows 有 GUI：读 Finder/Explorer
  python rename.py --dry-run          # 同上，只预览
  python rename.py --list             # 列出文件 + 编号（适合无 GUI 环境）
  python rename.py --order "3,1,2,4"  # 手动指定顺序
  python rename.py --ep 2 --t 1       # 自定义 EP/T
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys


def list_root_files(folder: str) -> list[str]:
    """返回文件夹根目录下所有文件的绝对路径，按字母序排序（确定性）。"""
    entries = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if os.path.isfile(p) and not name.startswith("."):
            entries.append(p)
    entries.sort(key=lambda p: os.path.basename(p))
    return entries


# ---------------- macOS: Finder via AppleScript ----------------

def _mac_visual_order(folder_path: str) -> list[str]:
    applescript = f'''
    tell application "Finder"
        activate
        set targetFolder to POSIX file "{folder_path}" as alias
        open targetFolder
        delay 0.4
        set targetWindow to front Finder window
        set theItems to items of targetWindow
        set output to ""
        repeat with anItem in theItems
            set output to output & (POSIX path of (anItem as alias)) & linefeed
        end repeat
        return output
    end tell
    '''
    result = subprocess.run(
        ["osascript", "-e", applescript], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"AppleScript 失败: {result.stderr.strip()}")
    paths = [line.rstrip("/") for line in result.stdout.split("\n") if line.strip()]
    return [p for p in paths if os.path.isfile(p)]


# ---------------- Windows: Explorer via PowerShell ----------------

def _win_visual_order(folder_path: str) -> list[str]:
    folder_path = os.path.abspath(folder_path)
    target_escaped = folder_path.replace('"', '`"')
    ps_script = f'''
$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$target = "{target_escaped}"
$shell = New-Object -ComObject Shell.Application

function Find-Win($shell, $target) {{
    foreach ($w in $shell.Windows()) {{
        try {{
            $p = $w.Document.Folder.Self.Path
            if ($p -ieq $target) {{ return $w }}
        }} catch {{}}
    }}
    return $null
}}

$win = Find-Win $shell $target
if (-not $win) {{
    Start-Process explorer.exe -ArgumentList "`"$target`""
    for ($i = 0; $i -lt 25; $i++) {{
        Start-Sleep -Milliseconds 300
        $win = Find-Win $shell $target
        if ($win) {{ break }}
    }}
}}
if (-not $win) {{ Write-Error "找不到 Explorer 窗口: $target"; exit 1 }}

foreach ($item in $win.Document.Folder.Items()) {{
    Write-Output $item.Path
}}
'''
    result = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise RuntimeError(f"PowerShell 失败: {result.stderr.strip()}")
    paths = [line.strip() for line in result.stdout.split("\n") if line.strip()]
    return [p for p in paths if os.path.isfile(p)]


def try_gui_order(folder_path: str) -> list[str] | None:
    """尝试读 GUI 文件管理器顺序；失败时返回 None（不抛错）。"""
    system = platform.system()
    try:
        if system == "Darwin":
            return _mac_visual_order(folder_path)
        if system == "Windows":
            return _win_visual_order(folder_path)
        return None
    except Exception:
        return None


# ---------------- 重命名逻辑 ----------------

def plan(files: list[str], ep: int, t: int) -> list[tuple[str, str]]:
    out = []
    for i, src in enumerate(files, start=1):
        ext = os.path.splitext(src)[1]
        new_name = f"EP{ep:02d}-C{i:02d}-T{t:02d}{ext}"
        out.append((src, new_name))
    return out


def execute(plan_list: list[tuple[str, str]]) -> None:
    if not plan_list:
        return
    folder = os.path.dirname(plan_list[0][0])
    temp_paths = []
    for i, (src, _) in enumerate(plan_list):
        ext = os.path.splitext(src)[1]
        tmp = os.path.join(folder, f".__rename_tmp_{i:04d}__{ext}")
        os.rename(src, tmp)
        temp_paths.append(tmp)
    for tmp, (_, new_name) in zip(temp_paths, plan_list):
        os.rename(tmp, os.path.join(folder, new_name))


# ---------------- main ----------------

def print_list(folder: str, files: list[str]) -> None:
    print(f"{folder} 里共 {len(files)} 个文件（按字母序编号）:\n")
    for i, f in enumerate(files, 1):
        print(f"  [{i:2d}] {os.path.basename(f)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--folder", default="~/Desktop/downloads", help="目标文件夹（默认 ~/Desktop/downloads）")
    parser.add_argument("--ep", type=int, default=1, help="EP 编号，默认 1")
    parser.add_argument("--t", type=int, default=1, help="T 编号，默认 1")
    parser.add_argument("--dry-run", action="store_true", help="只预览，不实际改名")
    parser.add_argument("--list", action="store_true", help="只列出文件 + 编号，不改名（无 GUI 环境用）")
    parser.add_argument("--order", help='手动指定顺序，索引来自 --list 的编号，例如 "3,1,2,4"')
    args = parser.parse_args()

    folder = os.path.abspath(os.path.expanduser(args.folder))
    if not os.path.isdir(folder):
        sys.exit(f"文件夹不存在: {folder}")

    # 模式 2: --list
    if args.list:
        files = list_root_files(folder)
        if not files:
            print(f"{folder} 里没有文件")
            return
        print_list(folder, files)
        print("\n下一步：请用户给出视频的实际顺序，再调用脚本并加 --order 参数。")
        print('例如: --order "3,1,2,4" 表示第一集是原 [3]、第二集是原 [1]，依此类推')
        return

    # 确定文件顺序
    files: list[str] | None = None

    if args.order:
        # 模式 3: 用户显式给的顺序
        all_files = list_root_files(folder)
        try:
            indices = [int(x.strip()) for x in args.order.split(",") if x.strip()]
        except ValueError:
            sys.exit(f'--order 必须是逗号分隔的整数，例如 "3,1,2,4"；收到: {args.order!r}')
        if len(indices) != len(all_files):
            sys.exit(
                f"--order 给了 {len(indices)} 个索引，但文件夹里有 {len(all_files)} 个文件；"
                "必须覆盖全部文件"
            )
        if sorted(indices) != list(range(1, len(all_files) + 1)):
            sys.exit(f"--order 索引必须是 1..{len(all_files)} 的一个排列，不能重复或越界")
        files = [all_files[i - 1] for i in indices]
    else:
        # 模式 1: 读 GUI 视觉顺序
        files = try_gui_order(folder)
        if not files:
            # 读不到 → 退回列表 + 指引
            all_files = list_root_files(folder)
            if not all_files:
                print(f"{folder} 里没有文件")
                return
            print("【无法读取 Finder / Explorer 视觉顺序】")
            print("可能当前环境没有 GUI（如云端沙盒），或文件管理器窗口未打开。\n")
            print_list(folder, all_files)
            print("\n下一步：请用户给出视频的实际播放顺序，然后用 --order 指定，例如：")
            print(f'  python {sys.argv[0]} --order "3,1,2,4,..." --ep {args.ep} --t {args.t}')
            sys.exit(2)

    # 预览 / 执行
    plan_list = plan(files, args.ep, args.t)
    print(f"目标文件夹: {folder}")
    print(f"共 {len(plan_list)} 个文件:\n")
    for i, (src, new_name) in enumerate(plan_list, 1):
        print(f"  {i:2d}. {os.path.basename(src)}  →  {new_name}")

    if args.dry_run:
        print("\n[dry-run] 未做任何改动")
        return

    execute(plan_list)
    print(f"\n完成，重命名 {len(plan_list)} 个文件")


if __name__ == "__main__":
    main()
