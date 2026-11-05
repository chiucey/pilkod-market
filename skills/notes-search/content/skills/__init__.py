# -*- coding: utf-8 -*-
"""
智能笔记技能 - 使用OpenClaw生态的向量搜索能力

本技能使用OpenClaw内置的memory系统进行语义搜索，无需额外安装向量搜索库。
"""

import json
import os
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Optional

from .config import DATA_DIR, MAX_CONTENT_LENGTH, TOP_K

# 笔记存储文件路径
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")


def _ensure_data_dir():
    """确保数据目录存在"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_notes() -> List[Dict]:
    """加载笔记列表"""
    if not os.path.exists(NOTES_FILE):
        return []
    try:
        with open(NOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_notes(notes: List[Dict]):
    """保存笔记列表"""
    _ensure_data_dir()
    with open(NOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def _generate_id() -> str:
    """生成唯一ID"""
    import uuid
    return str(uuid.uuid4())


def _check_openclaw_available() -> bool:
    """检查OpenClaw是否可用"""
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class NotesSearchSkill:
    """智能笔记搜索技能"""

    def __init__(self):
        self.notes: List[Dict] = _load_notes()
        self.openclaw_available = _check_openclaw_available()

    def add_note(self, content: str) -> Dict:
        """
        添加新笔记

        Args:
            content: 笔记内容（不超过100字）

        Returns:
            操作结果

        Example:
            add_note("今天学到了一个新的算法")
        """
        # 长度检查
        if len(content) > MAX_CONTENT_LENGTH:
            return {
                "success": False,
                "error": f"笔记内容不能超过{MAX_CONTENT_LENGTH}字，当前{len(content)}字"
            }

        if not content or not content.strip():
            return {
                "success": False,
                "error": "笔记内容不能为空"
            }

        note_id = _generate_id()
        created_at = datetime.utcnow().isoformat() + "Z"

        note = {
            "note_id": note_id,
            "content": content.strip(),
            "created_at": created_at
        }

        self.notes.append(note)
        _save_notes(self.notes)

        # 如果OpenClaw可用，尝试索引到memory
        if self.openclaw_available:
            self._index_to_openclaw_memory(note)

        return {
            "success": True,
            "note_id": note_id,
            "content": content.strip(),
            "created_at": created_at
        }

    def _index_to_openclaw_memory(self, note: Dict):
        """将笔记索引到OpenClaw memory（可选功能）"""
        # OpenClaw memory用于Agent记忆，我们可以将笔记以特殊格式存储
        # 格式: [notes::note_id] content
        try:
            temp_notes_file = os.path.join(DATA_DIR, "temp_notes.md")
            with open(temp_notes_file, 'w', encoding='utf-8') as f:
                f.write(f"[notes::{note['note_id']}] {note['content']}\n")
        except Exception as e:
            print(f"准备索引文件时出错: {e}")

    def search_notes(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        搜索相关笔记

        支持两种搜索模式：
        1. OpenClaw memory search（如果可用）
        2. 本地关键词匹配（后备）

        Args:
            query: 搜索关键词（支持模糊语义搜索）
            top_k: 返回结果数量，默认5条

        Returns:
            相关笔记列表，按相关性排序

        Example:
            search_notes("会议要点")
            search_notes("学习相关的内容")
        """
        if not query or not query.strip():
            return []

        results = []

        # 尝试使用OpenClaw memory search
        if self.openclaw_available:
            results = self._search_via_openclaw_memory(query, top_k or TOP_K)

        # 如果OpenClaw搜索没有结果或不可用，使用本地搜索
        if not results:
            results = self._local_search(query, top_k or TOP_K)

        return results

    def _search_via_openclaw_memory(self, query: str, top_k: int) -> List[Dict]:
        """通过OpenClaw memory API搜索"""
        try:
            result = subprocess.run(
                ["openclaw", "memory", "search", "--query", query,
                 "--max-results", str(top_k), "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                try:
                    search_results = json.loads(result.stdout)
                    matched_notes = []

                    for item in search_results:
                        content = item.get('content', '')
                        # 从内容中提取note_id
                        match = re.search(r'\[notes::([^\]]+)\]', content)
                        if match:
                            note_id = match.group(1)
                            note = self._get_note_by_id(note_id)
                            if note:
                                note['relevance_score'] = item.get('score', 0)
                                matched_notes.append(note)

                    return matched_notes
                except json.JSONDecodeError:
                    pass

        except Exception as e:
            print(f"OpenClaw memory搜索出错: {e}")

        return []

    def _local_search(self, query: str, top_k: int) -> List[Dict]:
        """本地搜索：基于关键词匹配和TF-IDF"""
        query_words = set(query.lower().split())
        results = []

        for note in self.notes:
            content_lower = note['content'].lower()

            # 计算匹配分数
            content_words = set(content_lower.split())
            matched_words = query_words & content_words

            if matched_words:
                # 基础分数：匹配词数
                base_score = len(matched_words)

                # 加权分数：完整短语匹配
                if query.lower() in content_lower:
                    base_score += 5

                # 标题/关键词匹配
                if any(word in content_lower for word in query_words):
                    base_score += 2

                note_copy = note.copy()
                note_copy['relevance_score'] = base_score
                note_copy['matched_words'] = list(matched_words)
                results.append(note_copy)

        # 排序
        results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        return results[:top_k]

    def _get_note_by_id(self, note_id: str) -> Optional[Dict]:
        """根据ID获取笔记"""
        for note in self.notes:
            if note['note_id'] == note_id:
                return note.copy()
        return None

    def list_notes(self) -> List[Dict]:
        """
        查看所有已记录的笔记

        Returns:
            笔记列表（按时间倒序）

        Example:
            list_notes()
        """
        return sorted(
            self.notes,
            key=lambda x: x.get('created_at', ''),
            reverse=True
        )

    def delete_note(self, note_id: str) -> Dict:
        """
        删除指定笔记

        Args:
            note_id: 笔记ID（从搜索结果或列表中获取）

        Returns:
            操作结果

        Example:
            delete_note("abc123...")
        """
        if not note_id:
            return {"success": False, "error": "笔记ID不能为空"}

        original_count = len(self.notes)
        self.notes = [n for n in self.notes if n['note_id'] != note_id]

        if len(self.notes) < original_count:
            _save_notes(self.notes)
            return {
                "success": True,
                "note_id": note_id,
                "message": "删除成功"
            }
        else:
            return {
                "success": False,
                "note_id": note_id,
                "message": "笔记不存在"
            }

    def get_note(self, note_id: str) -> Optional[Dict]:
        """
        查看单条笔记详情

        Args:
            note_id: 笔记ID

        Returns:
            笔记详情

        Example:
            get_note("abc123...")
        """
        return self._get_note_by_id(note_id)

    def get_stats(self) -> Dict:
        """
        获取技能统计信息

        Returns:
            统计信息
        """
        return {
            "total_notes": len(self.notes),
            "max_content_length": MAX_CONTENT_LENGTH,
            "openclaw_available": self.openclaw_available,
            "search_mode": "hybrid" if self.openclaw_available else "local"
        }


# 全局技能实例
skill = NotesSearchSkill()


def add_note(content: str) -> Dict:
    """添加笔记快捷函数"""
    return skill.add_note(content)


def search_notes(query: str, top_k: Optional[int] = None) -> List[Dict]:
    """搜索笔记快捷函数"""
    return skill.search_notes(query, top_k)


def list_notes() -> List[Dict]:
    """列出所有笔记快捷函数"""
    return skill.list_notes()


def delete_note(note_id: str) -> Dict:
    """删除笔记快捷函数"""
    return skill.delete_note(note_id)


def get_note(note_id: str) -> Optional[Dict]:
    """获取单条笔记快捷函数"""
    return skill.get_note(note_id)


def get_stats() -> Dict:
    """获取统计信息快捷函数"""
    return skill.get_stats()