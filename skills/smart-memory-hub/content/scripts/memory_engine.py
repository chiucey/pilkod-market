"""
Smart Memory Hub - 智能记忆管家核心模块

特点：
- 可靠的长期记忆（自动 + 手动）
- 严格的防膨胀机制（上限 + 淘汰 + 压缩 + 降级）
- 轻量级实现（单 JSON 文件）
"""

import json
import os
import re
import time
import uuid
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import threading

# ============== 配置常量 ==============

MAX_ENTRIES = 200
MAX_CHARS_PER_ENTRY = 200
INJECT_LIMIT = 5
CLEANUP_THRESHOLD = 180
TIMEOUT_MS = 1000
CLEANUP_INTERVAL = 10
COMPRESS_BATCH_SIZE = 10


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    content: str
    keywords: List[str]
    last_used: str
    importance: int
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'MemoryEntry':
        return MemoryEntry(**data)

    def truncate_content(self, max_chars: int = MAX_CHARS_PER_ENTRY) -> bool:
        """截断超长内容，返回是否被截断"""
        if len(self.content) > max_chars:
            self.content = self.content[:max_chars - 20] + "...[已压缩]"
            return True
        return False


class MemoryDatabase:
    """记忆数据库管理器"""

    def __init__(self, storage_path: str = None):
        if storage_path is None:
            home = Path.home()
            self.storage_dir = home / ".openclaw" / "smart_memory"
        else:
            self.storage_dir = Path(storage_path)

        self.memory_file = self.storage_dir / "memory.json"
        self.backup_file = self.storage_dir / "memory_backup.json"
        self.log_file = self.storage_dir / "memory.log"

        self._lock = threading.Lock()
        self._conversation_count = 0  # 对话轮次计数
        self._ensure_storage()
        self._data = self._load()

    def _ensure_storage(self):
        """确保存储目录存在"""
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        if not self.memory_file.exists():
            self._init_empty()

    def _init_empty(self):
        """初始化空数据库"""
        self._data = {
            "max_entries": MAX_ENTRIES,
            "version": "1.0.0",
            "last_cleanup": datetime.now().isoformat() + "Z",
            "degraded_mode": False,
            "entries": [],
            "compressed_cache": ""
        }
        self._save()

    def _load(self) -> dict:
        """加载数据库"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证并设置默认值
            data.setdefault("max_entries", MAX_ENTRIES)
            data.setdefault("version", "1.0.0")
            data.setdefault("last_cleanup", datetime.now().isoformat() + "Z")
            data.setdefault("degraded_mode", False)
            data.setdefault("entries", [])
            data.setdefault("compressed_cache", "")

            return data

        except (json.JSONDecodeError, FileNotFoundError) as e:
            self._log(f"加载失败: {e}，初始化新数据库")
            self._init_empty()
            return self._data

    def _save(self):
        """保存数据库"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self._log(f"保存失败: {e}")

    def _log(self, message: str):
        """记录日志"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"

            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            pass

    @property
    def entries(self) -> List[MemoryEntry]:
        """获取所有记忆条目"""
        return [MemoryEntry.from_dict(e) for e in self._data.get("entries", [])]

    @property
    def count(self) -> int:
        """获取条目数量"""
        return len(self._data.get("entries", []))

    @property
    def degraded_mode(self) -> bool:
        """检查是否处于降级模式"""
        return self._data.get("degraded_mode", False)

    @degraded_mode.setter
    def degraded_mode(self, value: bool):
        """设置降级模式"""
        self._data["degraded_mode"] = value
        self._save()

    def add_entry(self, content: str, keywords: List[str] = None,
                  importance: int = 50, source: str = "auto") -> Tuple[bool, str]:
        """
        添加新记忆条目
        返回: (是否成功, 消息)
        """
        if self.degraded_mode:
            return False, "记忆系统暂不可用"

        if self.count >= MAX_ENTRIES:
            # 触发强制合并
            self._force_compress()
            if self.count >= MAX_ENTRIES:
                return False, "记忆库已满，已触发压缩但仍满，请使用 /clear_memory 清理"

        # 截断超长内容
        if len(content) > MAX_CHARS_PER_ENTRY:
            content = content[:MAX_CHARS_PER_ENTRY - 20] + "...[已压缩]"

        # 提取关键词
        if keywords is None:
            keywords = self._extract_keywords(content)

        entry = MemoryEntry(
            id=f"mem_{uuid.uuid4().hex[:8]}",
            content=content,
            keywords=keywords,
            last_used=datetime.now().isoformat() + "Z",
            importance=min(importance, 100),
            created_at=datetime.now().isoformat() + "Z"
        )

        self._data["entries"].append(entry.to_dict())
        self._save()

        self._log(f"添加记忆: {entry.id} - {content[:50]}")

        return True, f"已记住: {content[:50]}..."

    def update_last_used(self, entry_id: str):
        """更新记忆的最后使用时间"""
        for entry in self._data["entries"]:
            if entry["id"] == entry_id:
                entry["last_used"] = datetime.now().isoformat() + "Z"
                break
        self._save()

    def search(self, query: str, limit: int = INJECT_LIMIT) -> List[MemoryEntry]:
        """
        搜索相关记忆
        返回最多 limit 条最相关记忆
        """
        if self.degraded_mode:
            return []

        start_time = time.time()

        try:
            query_lower = query.lower()
            query_words = set(query_lower.split())

            scored = []

            for entry_dict in self._data["entries"]:
                entry = MemoryEntry.from_dict(entry_dict)

                # 计算相关性分数
                score = 0

                # 关键词匹配
                for kw in entry.keywords:
                    if kw.lower() in query_lower:
                        score += 10
                    if any(w in kw.lower() for w in query_words):
                        score += 5

                # 内容匹配
                if query_lower in entry.content.lower():
                    score += 15

                # 重要性加成
                score += entry.importance / 10

                # 频率加成（last_used 越近越高）
                try:
                    last_used = datetime.fromisoformat(entry.last_used.replace("Z", "+00:00"))
                    days_ago = (datetime.now() - last_used.replace(tzinfo=None)).days
                    score += max(0, 10 - days_ago)
                except:
                    pass

                if score > 0:
                    scored.append((score, entry))

            # 按分数排序
            scored.sort(key=lambda x: x[0], reverse=True)

            # 更新 last_used 并返回
            results = []
            for score, entry in scored[:limit]:
                self.update_last_used(entry.id)
                results.append(entry)

            elapsed = (time.time() - start_time) * 1000

            if elapsed > TIMEOUT_MS:
                self._log(f"检索超时: {elapsed:.0f}ms，启用降级模式")
                self.degraded_mode = True
                return []

            return results

        except Exception as e:
            self._log(f"检索失败: {e}")
            return []

    def delete_by_id(self, entry_id: str) -> bool:
        """删除指定记忆"""
        original_count = len(self._data["entries"])
        self._data["entries"] = [
            e for e in self._data["entries"]
            if e["id"] != entry_id
        ]

        deleted = len(self._data["entries"]) < original_count
        if deleted:
            self._save()
            self._log(f"删除记忆: {entry_id}")

        return deleted

    def delete_by_keyword(self, keyword: str) -> int:
        """根据关键词删除记忆"""
        original_count = len(self._data["entries"])
        keyword_lower = keyword.lower()

        self._data["entries"] = [
            e for e in self._data["entries"]
            if keyword_lower not in e["content"].lower()
            and not any(keyword_lower in kw.lower() for kw in e.get("keywords", []))
        ]

        deleted = original_count - len(self._data["entries"])
        if deleted > 0:
            self._save()
            self._log(f"关键词删除: {keyword}, 删除了 {deleted} 条")

        return deleted

    def _extract_keywords(self, content: str) -> List[str]:
        """从内容中提取关键词"""
        # 简单实现：提取 2-6 个字符的词组
        keywords = []

        # 提取引号内的内容
        quotes = re.findall(r'["\']([^"\']+)["\']', content)
        keywords.extend(quotes[:3])

        # 提取数字/编码
        codes = re.findall(r'[A-Z]{2,}[0-9]*|[0-9]{4,}', content)
        keywords.extend(codes[:2])

        # 提取关键词模式
        patterns = [
            r'我叫\s*(\S+)',
            r'项目[是为]?\s*["\']?(\S+)["\']?',
            r'喜欢\s*(.+)',
            r'叫\s*(.+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                keywords.append(match.group(1)[:10])

        return list(set(keywords))[:5]

    def calculate_importance(self, content: str, appeared_count: int = 1,
                            explicit_remember: bool = False) -> int:
        """计算记忆重要性分数"""
        score = 50  # 基础分数

        # 明确要求记住
        if explicit_remember:
            score += 30

        # 出现次数加成
        score += min(appeared_count - 1, 3) * 10

        # 关键信息检测
        key_patterns = [
            (r'我叫|我是|名字', 25),  # 姓名
            (r'项目|代号|计划', 20),   # 项目
            (r'邮箱|电话|微信|QQ', 15),  # 联系方式
            (r'需要|必须|截止|deadline', 20),  # 待办
            (r'喜欢|不喜欢|偏好|讨厌', 15),  # 偏好
        ]

        for pattern, bonus in key_patterns:
            if re.search(pattern, content):
                score += bonus

        return min(score, 100)

    def auto_cleanup(self) -> Dict:
        """自动清理：淘汰低重要性/久未使用的记忆"""
        if self.count < CLEANUP_THRESHOLD:
            return {"action": "skip", "reason": "below_threshold"}

        self._log(f"触发自动清理，当前条目: {self.count}")

        original_count = self.count
        kept = []

        # 按重要性和时间排序
        entries = sorted(
            self._data["entries"],
            key=lambda e: (e.get("importance", 0), e.get("last_used", "")),
            reverse=True
        )

        # 保留重要记忆
        for entry in entries:
            if entry.get("importance", 0) > 90:
                kept.append(entry)
            else:
                # 检查是否太旧
                try:
                    last_used = datetime.fromisoformat(entry["last_used"].replace("Z", "+00:00"))
                    days_ago = (datetime.now() - last_used.replace(tzinfo=None)).days
                    if days_ago < 7:  # 7 天内保留
                        kept.append(entry)
                except:
                    kept.append(entry)

        # 如果还是太多，只保留最新的 180 条
        if len(kept) > CLEANUP_THRESHOLD:
            kept = kept[:CLEANUP_THRESHOLD]

        removed = original_count - len(kept)
        self._data["entries"] = kept
        self._data["last_cleanup"] = datetime.now().isoformat() + "Z"
        self._save()

        self._log(f"清理完成，删除: {removed} 条，保留: {len(kept)} 条")

        return {
            "action": "cleanup",
            "removed": removed,
            "remaining": len(kept)
        }

    def _force_compress(self) -> bool:
        """强制压缩：合并最旧的 10 条为 1 条摘要"""
        if self.count < COMPRESS_BATCH_SIZE:
            return False

        # 创建备份
        try:
            shutil.copy(self.memory_file, self.backup_file)
        except Exception as e:
            self._log(f"备份失败: {e}")

        # 获取最旧的条目
        entries = sorted(
            self._data["entries"],
            key=lambda e: e.get("created_at", "")
        )

        oldest_batch = entries[:COMPRESS_BATCH_SIZE]

        # 生成压缩摘要
        summary = " | ".join([
            e["content"][:50] for e in oldest_batch
        ])

        if len(summary) > MAX_CHARS_PER_ENTRY:
            summary = summary[:MAX_CHARS_PER_ENTRY - 20] + "..."

        # 压缩后的条目
        compressed_entry = {
            "id": f"mem_{uuid.uuid4().hex[:8]}",
            "content": f"[压缩摘要] {summary}",
            "keywords": ["compressed", "archive"],
            "last_used": datetime.now().isoformat() + "Z",
            "importance": 30,  # 压缩后降低重要性
            "created_at": datetime.now().isoformat() + "Z"
        }

        # 更新条目列表
        self._data["entries"] = [compressed_entry] + entries[COMPRESS_BATCH_SIZE:]

        # 更新压缩缓存
        old_cache = self._data.get("compressed_cache", "")
        new_cache = f"{old_cache}\n[{datetime.now().strftime('%Y-%m-%d')}] {summary}"
        self._data["compressed_cache"] = new_cache[-5000:]  # 保留最后 5000 字符

        self._data["last_cleanup"] = datetime.now().isoformat() + "Z"
        self._save()

        self._log(f"压缩完成: 合并 {COMPRESS_BATCH_SIZE} 条为 1 条")

        return True

    def manual_compact(self) -> Tuple[int, int]:
        """手动压缩合并
        返回: (合并条数, 剩余条数)
        """
        if self.count < COMPRESS_BATCH_SIZE:
            return 0, self.count

        original_count = self.count
        self._force_compress()
        return COMPRESS_BATCH_SIZE, self.count

    def reset_all(self) -> bool:
        """清空所有记忆"""
        self._data["entries"] = []
        self._data["compressed_cache"] = ""
        self._data["degraded_mode"] = False
        self._data["last_cleanup"] = datetime.now().isoformat() + "Z"
        self._save()
        self._log("重置所有记忆")
        return True

    def get_stats(self) -> Dict:
        """获取统计信息"""
        entries = self._data.get("entries", [])

        total_chars = sum(len(e.get("content", "")) for e in entries)

        # 按重要性分布
        importance_dist = {"high": 0, "medium": 0, "low": 0}
        for e in entries:
            imp = e.get("importance", 0)
            if imp > 70:
                importance_dist["high"] += 1
            elif imp > 40:
                importance_dist["medium"] += 1
            else:
                importance_dist["low"] += 1

        # 按类型统计关键词
        all_keywords = []
        for e in entries:
            all_keywords.extend(e.get("keywords", []))
        keyword_counts = {}
        for kw in all_keywords:
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        top_keywords = sorted(
            keyword_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]

        return {
            "total_entries": len(entries),
            "max_entries": self._data.get("max_entries", MAX_ENTRIES),
            "total_chars": total_chars,
            "avg_chars_per_entry": total_chars // len(entries) if entries else 0,
            "importance_distribution": importance_dist,
            "degraded_mode": self._data.get("degraded_mode", False),
            "last_cleanup": self._data.get("last_cleanup", "从未"),
            "compressed_cache_size": len(self._data.get("compressed_cache", "")),
            "top_keywords": top_keywords
        }

    def increment_conversation_count(self) -> int:
        """增加对话轮次，返回当前轮次"""
        self._conversation_count += 1

        # 每 CLEANUP_INTERVAL 轮检查一次
        if self._conversation_count % CLEANUP_INTERVAL == 0:
            self.auto_cleanup()

        return self._conversation_count


class SmartMemoryHub:
    """智能记忆管家主类"""

    def __init__(self, storage_path: str = None):
        self.db = MemoryDatabase(storage_path)
        self._current_session_entries = []  # 当前会话中使用的记忆

    def process_user_input(self, message: str) -> Tuple[str, bool]:
        """
        处理用户输入
        返回: (记忆注入文本, 是否为管理命令)
        """
        # 检查是否是管理命令
        if message.startswith('/'):
            return self._handle_command(message), True

        # 增加对话轮次
        self.db.increment_conversation_count()

        # 提取可能的新信息并自动记忆
        self._auto_capture(message)

        # 检索相关记忆
        if self.db.degraded_mode:
            return "[记忆系统暂不可用]", False

        memories = self.db.search(message, limit=INJECT_LIMIT)

        # 格式化为注入文本
        if not memories:
            return "", False

        self._current_session_entries = memories

        lines = []
        for mem in memories:
            lines.append(f"[记忆] {mem.content} (importance: {mem.importance})")

        return "\n".join(lines), False

    def _auto_capture(self, message: str):
        """自动捕获可能需要记忆的信息"""
        # 检测明确的记忆指令
        if '/remember' in message or '记住' in message:
            # 提取记忆内容
            content = message.replace('记住', '').replace('/remember', '').strip()
            if content:
                importance = self.db.calculate_importance(
                    content,
                    appeared_count=1,
                    explicit_remember=True
                )
                self.db.add_entry(content, importance=importance, source="explicit")

        # 检测重复出现的信息
        words = message.split()
        for word in words:
            if len(word) >= 2:
                # 简单检查是否重复
                existing = self.db.search(word, limit=1)
                if existing:
                    # 更新重要性
                    for entry_dict in self.db._data["entries"]:
                        if entry_dict["content"] == existing[0].content:
                            entry_dict["importance"] = min(100, entry_dict.get("importance", 50) + 5)
                    self.db._save()

    def _handle_command(self, command: str) -> str:
        """处理管理命令"""
        cmd = command.strip()

        if cmd.startswith('/remember '):
            content = cmd[10:].strip()
            if not content:
                return "❌ 请提供要记忆的内容，例如：/remember 我喜欢喝咖啡"

            importance = self.db.calculate_importance(content, explicit_remember=True)
            success, msg = self.db.add_entry(content, importance=min(100, importance + 30))
            return f"✅ {msg}"

        elif cmd.startswith('/recall '):
            keyword = cmd[8:].strip()
            if not keyword:
                return "❌ 请提供搜索关键词，例如：/recall 项目名称"

            memories = self.db.search(keyword, limit=10)
            if not memories:
                return f"🔍 没有找到关于「{keyword}」的记忆"

            lines = [f"🔍 关于「{keyword}」的记忆："]
            for mem in memories:
                lines.append(f"\n• {mem.content}")
                lines.append(f"  重要性: {mem.importance} | 最后使用: {mem.last_used[:10]}")
            return "\n".join(lines)

        elif cmd == '/memory_stats':
            stats = self.db.get_stats()
            lines = ["📊 记忆统计：", ""]
            lines.append(f"• 当前条目: {stats['total_entries']} / {stats['max_entries']}")
            lines.append(f"• 总字符数: {stats['total_chars']}")
            lines.append(f"• 平均每条: {stats['avg_chars_per_entry']} 字符")
            lines.append("")
            lines.append("重要性分布：")
            lines.append(f"  - 高 (>70): {stats['importance_distribution']['high']}")
            lines.append(f"  - 中 (40-70): {stats['importance_distribution']['medium']}")
            lines.append(f"  - 低 (<40): {stats['importance_distribution']['low']}")
            lines.append("")
            lines.append(f"• 降级模式: {'是 ⚠️' if stats['degraded_mode'] else '否 ✅'}")
            lines.append(f"• 最后清理: {stats['last_cleanup'][:10]}")
            if stats['top_keywords']:
                lines.append("")
                lines.append("高频关键词：")
                for kw, count in stats['top_keywords'][:5]:
                    lines.append(f"  - {kw}: {count}次")
            return "\n".join(lines)

        elif cmd == '/clear_memory':
            return "⚠️ 确定要清空所有记忆吗？此操作不可恢复。\n请再次输入 `/clear_memory confirm` 确认。"

        elif cmd == '/clear_memory confirm':
            self.db.reset_all()
            return "🗑️ 已清空所有记忆"

        elif cmd == '/compact_memory':
            merged, remaining = self.db.manual_compact()
            if merged > 0:
                return f"✅ 压缩完成：合并了 {merged} 条，剩余 {remaining} 条"
            else:
                return "📭 当前记忆数量不足以压缩"

        return ""

    def get_response_context(self, query: str) -> str:
        """获取用于增强回复的记忆上下文"""
        if self.db.degraded_mode:
            return ""

        memories = self.db.search(query, limit=3)

        if not memories:
            return ""

        # 使用可选的前缀格式
        return f"根据记忆中你曾说过 {memories[0].content}，因此"


# ============== OpenClaw 集成接口 ==============

class SmartMemoryHubPlugin:
    """OpenClaw 插件接口"""

    def __init__(self):
        self.hub = SmartMemoryHub()

    def on_user_message(self, message: str) -> str:
        """用户消息钩子"""
        memory_inject, is_command = self.hub.process_user_input(message)
        return memory_inject

    def on_bot_reply(self, message: str) -> None:
        """机器人回复钩子（可用于从回复中捕获新记忆）"""
        pass

    def get_memory_context(self, query: str) -> str:
        """获取记忆上下文"""
        return self.hub.get_response_context(query)

    def add_memory(self, content: str, importance: int = 50) -> bool:
        """手动添加记忆"""
        success, _ = self.hub.db.add_entry(content, importance=importance)
        return success


# 导出
__all__ = ['MemoryEntry', 'MemoryDatabase', 'SmartMemoryHub', 'SmartMemoryHubPlugin']
