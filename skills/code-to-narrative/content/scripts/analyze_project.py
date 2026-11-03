#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_project.py — 分析项目结构，生成自然语言框架描述
"""
import os
import sys
import json
import subprocess
from pathlib import Path

def get_tree(root_path: str, max_depth: int = 4, exclude_dirs=None) -> str:
    """返回项目目录树"""
    if exclude_dirs is None:
        exclude_dirs = {"node_modules", ".git", "__pycache__", ".venv", "venv",
                        "dist", "build", ".next", ".nuxt", "target", "vendor",
                        ".idea", ".vscode", ".DS_Store"}
    lines = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        depth = dirpath[len(root_path):].count(os.sep)
        if depth >= max_depth:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        indent = "  " * depth
        folder_name = os.path.basename(dirpath) or os.path.dirname(dirpath)
        if depth > 0:
            lines.append(f"{indent}📁 {folder_name}/")
        for fname in sorted(filenames):
            if fname.startswith("."):
                continue
            ext = os.path.splitext(fname)[1]
            icon = "🐍" if ext == ".py" else ("📄" if ext in [".js",".ts",".jsx",".tsx"] else ("⚙️" if ext == ".json" else "📃"))
            lines.append(f"{indent}  {icon} {fname}")
    return "\n".join(lines)

def detect_language(root_path: str) -> str:
    """检测项目主语言"""
    exts = {}
    for dirpath, _, filenames in os.walk(root_path):
        if "node_modules" in dirpath or ".git" in dirpath:
            continue
        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext:
                exts[ext] = exts.get(ext, 0) + 1
    if not exts:
        return "unknown"
    top = sorted(exts.items(), key=lambda x: -x[1])[0][0]
    lang_map = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                 ".jsx": "React/JSX", ".tsx": "React/TSX", ".go": "Go",
                 ".java": "Java", ".rs": "Rust", ".rb": "Ruby",
                 ".php": "PHP", ".cs": "C#", ".cpp": "C++", ".c": "C"}
    return lang_map.get(top, top)

def find_entry_points(root_path: str, lang: str) -> dict:
    """查找入口文件"""
    entries = {}
    entry_names = {
        "Python": ["main.py", "app.py", "server.py", "api.py", "run.py", "cli.py", "__main__.py", "manage.py"],
        "JavaScript": ["index.js", "main.js", "server.js", "app.js", "cli.js"],
        "TypeScript": ["index.ts", "main.ts", "server.ts", "app.ts"],
        "Go": ["main.go"],
        "Java": ["Main.java", "Application.java"],
    }
    names = entry_names.get(lang, [])
    for fname in os.listdir(root_path):
        if fname in names:
            entries[fname] = os.path.join(root_path, fname)
    # 查找配置
    for fname in ["package.json", "requirements.txt", "Pipfile", "pyproject.toml",
                  "go.mod", "Cargo.toml", "pom.xml", "build.gradle",
                  ".env", ".env.example", "settings.py", "config.py", "config.ts"]:
        path = os.path.join(root_path, fname)
        if os.path.exists(path):
            entries[fname] = path
    return entries

def read_file_content(path: str, max_lines: int = 60) -> str:
    """读取文件内容（限制行数）"""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[:max_lines])
    except Exception:
        return ""

def summarize_file(path: str) -> str:
    """生成单个文件的自然语言摘要"""
    fname = os.path.basename(path)
    ext = os.path.splitext(fname)[1]
    content = read_file_content(path, 80)
    if not content:
        return f"{fname}: 文件存在但无法读取"

    lines = [l.strip() for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]
    comments = [l for l in content.split("\n") if l.strip().startswith("#")]
    summary_parts = []

    # 从注释推断用途
    if comments:
        doc_comments = [l.strip().lstrip("#").strip() for l in comments[:5] if l.strip().startswith("#")]
        if doc_comments:
            summary_parts.append("用途：" + " ".join(doc_comments[:2]))

    # 检测 import/require
    imports = []
    for l in lines[:30]:
        if l.startswith("import ") or l.startswith("from ") or l.startswith("require("):
            imports.append(l.strip()[:60])
    if imports:
        deps = []
        for i in imports[:8]:
            parts = i.split()
            if len(parts) >= 2:
                dep = parts[1].split(".")[0].split("(")[0].strip()
                deps.append(dep)
        summary_parts.append(f"依赖：{', '.join(set(deps))}")

    # 函数/类检测
    if ext in [".py"]:
        classes = [l.strip() for l in lines if l.strip().startswith("class ") and ":" in l]
        funcs = [l.strip() for l in lines if l.strip().startswith("def ") and ":" in l]
        if classes:
            summary_parts.append(f"类：{', '.join([c.split('class ')[1].split('(')[0] for c in classes[:5]])}")
        if funcs:
            summary_parts.append(f"函数：{', '.join([f.split('def ')[1].split('(')[0] for f in funcs[:8]])}")
    elif ext in [".js", ".ts", ".jsx", ".tsx"]:
        funcs = [l.strip() for l in lines if ("function " in l or "const " in l or "async " in l) and "=" in l]
        exports = [l.strip() for l in lines if "export" in l]
        if exports:
            summary_parts.append(f"导出：{', '.join([e.split()[-1].rstrip('{;').strip() for e in exports[:5] if e.split()])}")
    elif ext in [".go"]:
        funcs = [l.strip() for l in lines if l.strip().startswith("func ")]
        if funcs:
            summary_parts.append(f"函数：{', '.join([f.split('(')[0].split('func ')[1] for f in funcs[:6]])}")

    return fname + ":\n    " + "\n    ".join(summary_parts) if summary_parts else fname

def analyze_project(root_path: str) -> dict:
    """生成完整项目分析"""
    root_path = os.path.abspath(root_path)
    project_name = os.path.basename(root_path)
    lang = detect_language(root_path)
    tree = get_tree(root_path)
    entries = find_entry_points(root_path, lang)

    # 读入口文件和主要模块
    modules = {}
    dirs_to_scan = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in {"node_modules",".git","__pycache__",".venv","venv","dist","build",".next",".nuxt","vendor",".idea",".vscode"}]
        for d in dirnames:
            if d not in {"tests","test","__pycache__","static","public","docs"}:
                dirs_to_scan.append(os.path.join(dirpath, d))
        if len(dirs_to_scan) > 20:
            break

    # 找主要源文件目录
    src_dirs = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in {"node_modules",".git","__pycache__",".venv","venv","dist","build",".next",".nuxt","vendor",".idea",".vscode",".github","tests","test","docs","assets","static","public","bin","lib"}]
        if dirpath.count(os.sep) - root_path.count(os.sep) >= 2:
            continue
        for f in filenames:
            ext = os.path.splitext(f)[1]
            if ext in [".py",".js",".ts",".jsx",".tsx",".go",".java",".rs"]:
                rel = os.path.relpath(dirpath, root_path)
                if rel == ".":
                    rel = "根目录"
                src_dirs.append((rel, dirpath))
                break

    modules_info = {}
    seen_dirs = set()
    for label, dirpath in src_dirs[:8]:
        if label in seen_dirs:
            continue
        seen_dirs.add(label)
        files = [f for f in os.listdir(dirpath) if not f.startswith(".") and os.path.isfile(os.path.join(dirpath, f))]
        key_files = files[:5]  # 最多5个关键文件
        summaries = []
        for f in key_files:
            fp = os.path.join(dirpath, f)
            summaries.append(summarize_file(fp))
        modules_info[label] = summaries

    return {
        "project_name": project_name,
        "language": lang,
        "tree": tree,
        "entry_points": entries,
        "modules": modules_info,
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 analyze_project.py <项目路径>")
        sys.exit(1)
    result = analyze_project(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
