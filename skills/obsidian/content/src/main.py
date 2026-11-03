#!/usr/bin/env python3
"""
Obsidian 技能主逻辑。
通过文件系统操作直接管理 Obsidian 库（纯 Markdown 文件）。
无外部依赖，仅使用 Python 标准库。
"""

import os
import re
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全局变量：Obsidian 库根目录，从环境变量读取
VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH")
if not VAULT_PATH:
    # 运行时若未设置，可尝试从传入参数获取，或报错
    logger.warning("环境变量 OBSIDIAN_VAULT_PATH 未设置，将尝试从输入参数获取。")


def _get_vault_path(input_data: Dict) -> Optional[Path]:
    """获取库路径：优先从环境变量，其次从输入参数 vault_path"""
    path_str = VAULT_PATH or input_data.get("vault_path")
    if path_str:
        return Path(path_str).expanduser().resolve()
    return None


def _is_within_vault(file_path: Path, vault_path: Path) -> bool:
    """检查文件是否在库目录内"""
    try:
        file_path.resolve().relative_to(vault_path.resolve())
        return True
    except ValueError:
        return False


def search_notes(vault_path: Path, query: str, search_content: bool = False) -> List[Dict]:
    """搜索笔记：按标题或内容"""
    results = []
    for md_file in vault_path.rglob("*.md"):
        rel_path = md_file.relative_to(vault_path)
        # 标题匹配
        if query.lower() in rel_path.stem.lower():
            results.append({
                "path": str(rel_path),
                "title": rel_path.stem,
                "match_type": "title"
            })
            continue
        # 内容匹配
        if search_content:
            try:
                content = md_file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    # 简单取第一行作为摘要
                    first_line = content.split('\n')[0][:100]
                    results.append({
                        "path": str(rel_path),
                        "title": rel_path.stem,
                        "match_type": "content",
                        "snippet": first_line
                    })
            except Exception as e:
                logger.error(f"读取文件 {md_file} 失败: {e}")
    return results


def create_note(vault_path: Path, path: str, content: str = "", open_after: bool = False) -> Dict:
    """创建笔记"""
    note_path = vault_path / path
    if not note_path.suffix == ".md":
        note_path = note_path.with_suffix(".md")
    # 确保父目录存在
    note_path.parent.mkdir(parents=True, exist_ok=True)
    if note_path.exists():
        return {"status": "error", "message": f"笔记已存在: {note_path}"}
    try:
        note_path.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "message": f"笔记创建成功: {note_path.relative_to(vault_path)}",
            "path": str(note_path.relative_to(vault_path))
        }
    except Exception as e:
        return {"status": "error", "message": f"创建失败: {e}"}


def move_note(vault_path: Path, old_path: str, new_path: str) -> Dict:
    """移动/重命名笔记，并尝试更新其他笔记中的 wikilink"""
    old_full = vault_path / old_path
    if not old_full.suffix == ".md":
        old_full = old_full.with_suffix(".md")
    if not old_full.exists():
        return {"status": "error", "message": f"源笔记不存在: {old_full}"}

    new_full = vault_path / new_path
    if not new_full.suffix == ".md":
        new_full = new_full.with_suffix(".md")
    if new_full.exists():
        return {"status": "error", "message": f"目标位置已存在: {new_full}"}

    # 确保目标目录存在
    new_full.parent.mkdir(parents=True, exist_ok=True)

    # 记录旧标题（不含扩展名）和新标题
    old_title = old_full.stem
    new_title = new_full.stem

    # 移动文件
    try:
        shutil.move(str(old_full), str(new_full))
    except Exception as e:
        return {"status": "error", "message": f"移动文件失败: {e}"}

    # 更新其他笔记中的 wikilink (简单替换，不处理别名等复杂情况)
    updated_count = 0
    # 匹配 [[旧标题]] 或 [[旧标题|别名]] 等，只替换标题部分
    # 简单替换：将 [[旧标题 替换为 [[新标题
    # 更精细的：用正则捕获 [[旧标题(\]|\|)，替换为新标题+捕获组
    pattern = re.compile(rf"\[\[{re.escape(old_title)}(\]\]|\|)")
    for md_file in vault_path.rglob("*.md"):
        if md_file == new_full:  # 跳过刚移动的文件本身
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            new_content, count = pattern.subn(rf"[[{new_title}\1", content)
            if count:
                md_file.write_text(new_content, encoding="utf-8")
                updated_count += count
        except Exception as e:
            logger.error(f"更新链接时处理文件 {md_file} 失败: {e}")

    return {
        "status": "success",
        "message": f"笔记已从 {old_path} 移动到 {new_path}，更新了 {updated_count} 处 wikilink。",
        "updated_links": updated_count
    }


def delete_note(vault_path: Path, path: str) -> Dict:
    """删除笔记"""
    note_path = vault_path / path
    if not note_path.suffix == ".md":
        note_path = note_path.with_suffix(".md")
    if not note_path.exists():
        return {"status": "error", "message": f"笔记不存在: {note_path}"}
    try:
        note_path.unlink()
        return {
            "status": "success",
            "message": f"笔记已删除: {note_path.relative_to(vault_path)}"
        }
    except Exception as e:
        return {"status": "error", "message": f"删除失败: {e}"}


def run(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    主入口。
    输入参数格式:
    {
        "action": "search" | "create" | "move" | "delete",
        "query": "...",           # 用于 search
        "search_content": bool,   # search 是否搜索内容
        "path": "...",            # create/move/delete 的路径
        "new_path": "...",        # move 的目标路径
        "content": "...",         # create 的笔记内容
        "open_after": bool,       # create 是否创建后打开（本实现忽略）
        "vault_path": "..."       # 可选，覆盖环境变量设置的库路径
    }
    """
    try:
        vault_path = _get_vault_path(input_data)
        if not vault_path:
            return {
                "status": "error",
                "message_for_user": "未设置 Obsidian 库路径。请在 Agent 环境变量中设置 OBSIDIAN_VAULT_PATH，或在输入参数中提供 vault_path。"
            }
        if not vault_path.is_dir():
            return {
                "status": "error",
                "message_for_user": f"库路径不存在或不是目录: {vault_path}"
            }

        action = input_data.get("action")
        if not action:
            return {
                "status": "error",
                "message_for_user": "缺少必要参数: action"
            }

        if action == "search":
            query = input_data.get("query")
            if not query:
                return {"status": "error", "message_for_user": "搜索需要 query 参数"}
            search_content = input_data.get("search_content", False)
            results = search_notes(vault_path, query, search_content)
            if results:
                msg = f"找到 {len(results)} 个相关笔记：\n" + "\n".join(
                    f"- {r['title']} ({r['path']})" + (f" - 摘要: {r.get('snippet', '')}" if r.get('snippet') else "")
                    for r in results
                )
            else:
                msg = "未找到匹配的笔记。"
            return {"status": "success", "data": results, "message_for_user": msg}

        elif action == "create":
            path = input_data.get("path")
            if not path:
                return {"status": "error", "message_for_user": "创建需要 path 参数"}
            content = input_data.get("content", "")
            result = create_note(vault_path, path, content)
            return {"status": result["status"], "message_for_user": result["message"], "data": result}

        elif action == "move":
            old_path = input_data.get("path")
            new_path = input_data.get("new_path")
            if not old_path or not new_path:
                return {"status": "error", "message_for_user": "移动需要 path 和 new_path 参数"}
            result = move_note(vault_path, old_path, new_path)
            return {"status": result["status"], "message_for_user": result["message"], "data": result}

        elif action == "delete":
            path = input_data.get("path")
            if not path:
                return {"status": "error", "message_for_user": "删除需要 path 参数"}
            result = delete_note(vault_path, path)
            return {"status": result["status"], "message_for_user": result["message"], "data": result}

        else:
            return {
                "status": "error",
                "message_for_user": f"不支持的操作: {action}。支持的操作: search, create, move, delete"
            }

    except Exception as e:
        logger.exception("执行失败")
        return {
            "status": "error",
            "message_for_user": f"内部错误: {str(e)}"
        }


if __name__ == "__main__":
    import sys
    if not sys.stdin.isatty():
        input_json = sys.stdin.read()
        if input_json:
            input_data = json.loads(input_json)
        else:
            input_data = {}
    else:
        input_data = {}
    output = run(input_data)
    print(json.dumps(output, ensure_ascii=False))
