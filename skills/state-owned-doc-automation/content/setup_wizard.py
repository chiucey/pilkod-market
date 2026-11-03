"""首次配置向导：通过图形界面写入 config.py 路径配置。"""

from __future__ import annotations

import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.py")
DEFAULT_BACKUP = r".\backup"
EXAMPLE_TEXT = r"示例：\\192.168.1.100\国资资料库 或 Z:\归档库"


def _escape_py_raw(value: str) -> str:
    """转义双引号，输出可写入 r"..." 的字符串内容。"""
    return (value or "").replace('"', '\\"')


def _update_config_paths(shared_path: str, watch_path: str, processed_path: str) -> None:
    """覆盖 config.py 中的三个路径变量。"""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    replacements = {
        "SHARED_BASE_PATH": shared_path,
        "WATCH_DIR": watch_path,
        "PROCESSED_DIR": processed_path or DEFAULT_BACKUP,
    }

    for key, value in replacements.items():
        pattern = rf"^{key}\s*=\s*r?\".*?\""
        new_line = f'{key} = r"{_escape_py_raw(value)}"'
        content, count = re.subn(pattern, new_line, content, count=1, flags=re.MULTILINE)
        if count == 0:
            raise RuntimeError(f"未在 config.py 中找到变量：{key}")

    with open(CONFIG_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def _pick_dir(entry: tk.Entry) -> None:
    """弹出目录选择器并回填输入框。"""
    current = entry.get().strip() or PROJECT_ROOT
    selected = filedialog.askdirectory(initialdir=current, title="请选择目录")
    if selected:
        entry.delete(0, tk.END)
        entry.insert(0, selected)


def _build_row(parent: tk.Widget, row: int, title: str, default_value: str) -> tk.Entry:
    """构建单行输入区域（标题 + 输入框 + 浏览按钮 + 示例）。"""
    label = tk.Label(parent, text=title, anchor="w")
    label.grid(row=row, column=0, columnspan=3, sticky="w", pady=(8, 2))

    entry = tk.Entry(parent, width=70)
    entry.grid(row=row + 1, column=0, columnspan=2, sticky="we", padx=(0, 8))
    entry.insert(0, default_value)

    browse_btn = tk.Button(parent, text="浏览", width=10, command=lambda: _pick_dir(entry))
    browse_btn.grid(row=row + 1, column=2, sticky="e")

    hint = tk.Label(parent, text=EXAMPLE_TEXT, fg="#808080", anchor="w")
    hint.grid(row=row + 2, column=0, columnspan=3, sticky="w")
    return entry


def main() -> None:
    root = tk.Tk()
    root.title("国资资料库 - 首次配置向导")
    root.geometry("760x380")
    root.resizable(False, False)

    frame = tk.Frame(root, padx=20, pady=16)
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    shared_entry = _build_row(frame, 0, "资料库根目录（SHARED_BASE_PATH）", "")
    watch_entry = _build_row(frame, 3, "待归档目录（WATCH_DIR）", "")
    processed_entry = _build_row(frame, 6, "已处理备份目录（PROCESSED_DIR，可选）", DEFAULT_BACKUP)

    def save_and_exit() -> None:
        shared_path = shared_entry.get().strip()
        watch_path = watch_entry.get().strip()
        processed_path = processed_entry.get().strip() or DEFAULT_BACKUP

        if not shared_path:
            messagebox.showerror("配置错误", "请填写资料库根目录（SHARED_BASE_PATH）。")
            return
        if not watch_path:
            messagebox.showerror("配置错误", "请填写待归档目录（WATCH_DIR）。")
            return

        try:
            _update_config_paths(shared_path, watch_path, processed_path)
            print(f"[OK] 配置已保存到: {CONFIG_PATH}")
            print(f"[OK] SHARED_BASE_PATH = {shared_path}")
            print(f"[OK] WATCH_DIR = {watch_path}")
            print(f"[OK] PROCESSED_DIR = {processed_path}")
            messagebox.showinfo("保存成功", "配置已保存，程序即将退出。")
            root.destroy()
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("保存失败", f"写入 config.py 失败：{exc}")

    save_btn = tk.Button(frame, text="保存配置并退出", command=save_and_exit, height=2)
    save_btn.grid(row=9, column=0, columnspan=3, sticky="we", pady=(18, 0))

    root.mainloop()


if __name__ == "__main__":
    main()
