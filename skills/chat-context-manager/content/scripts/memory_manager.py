#!/usr/bin/env python3
"""
聊天上下文管理器 - 核心记忆管理脚本
自动记录、分类、更新聊天中的关键信息
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib

# 配置
MEMORY_DIR = Path("/workspace/chat-memory")
MEMORY_FILES = {
    "identity": "user_identity.md",
    "preferences": "user_preferences.md",
    "agreements": "agreements.md",
    "facts": "facts.md",
    "summary": "conversation_summary.md"
}

@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: str
    created_at: str
    updated_at: str
    status: str = "active"  # active, updated, archived
    source_hint: str = ""   # 原始语句提示

    def to_markdown(self) -> str:
        return f"""- **{self.key}**: {self.value}
  - 创建时间: {self.created_at}
  - 更新时间: {self.updated_at}
  - 状态: {self.status}"""

class MemoryManager:
    """记忆管理器"""

    def __init__(self, memory_dir: str = None):
        self.memory_dir = Path(memory_dir) if memory_dir else MEMORY_DIR
        self._ensure_memory_dir()

    def _ensure_memory_dir(self):
        """确保记忆目录存在"""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        for filename in MEMORY_FILES.values():
            filepath = self.memory_dir / filename
            if not filepath.exists():
                filepath.write_text(self._get_empty_template(filename))

    def _get_empty_template(self, filename: str) -> str:
        """获取空模板"""
        templates = {
            "user_identity.md": "# 用户身份信息\n\n记录用户的名字、头像、形象描述等身份信息。\n\n## 基本信息\n\n---\n\n## 头像描述\n\n---\n\n## 其他身份特征\n\n---\n",
            "user_preferences.md": "# 用户偏好设置\n\n记录用户的偏好、交流风格、喜欢的话题等。\n\n## 称呼偏好\n\n---\n\n## 交流风格\n\n---\n\n## 主题偏好\n\n---\n",
            "agreements.md": "# 约定与规则\n\n记录用户与AI之间的约定、规则和协议。\n\n## 行为约定\n\n---\n\n## 对话规则\n\n---\n",
            "facts.md": "# 重要事实记录\n\n记录重要的事实、日期、事件和关键信息。\n\n## 重要日期\n\n---\n\n## 关键事实\n\n---\n",
            "conversation_summary.md": "# 对话摘要\n\n记录重要对话的摘要，便于回顾。\n\n## 最近对话\n\n---\n"
        }
        return templates.get(filename, "")

    def _normalize_key(self, text: str) -> str:
        """规范化键名"""
        # 移除特殊字符，转小写
        key = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
        key = key.strip().lower()
        return key

    def _extract_value(self, text: str) -> str:
        """提取值内容"""
        # 移除常见前缀
        patterns = [
            r'(?:叫|是|为| named?| called?| is)\s*["\']?([^"\'\n]+)["\']?',
            r'(?:头像|形象|样子| avatar| image)\s*[:：]?\s*["\']?([^"\'\n]+)["\']?',
            r'["\']([^"\']+)["\']',
            r'[:：]\s*(.+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return text.strip()

    def _generate_entry_id(self, key: str, category: str) -> str:
        """生成条目唯一ID"""
        raw = f"{category}:{key}:{datetime.now().isoformat()}"
        return hashlib.md5(raw.encode()).hexdigest()[:8]

    # ============ 信息识别 ============

    def identify_identity_info(self, text: str) -> Optional[Dict[str, str]]:
        """识别身份信息"""
        patterns = [
            # 中文模式 - 名字识别（优先匹配，确保不会误匹配其他内容）
            (r'^我叫\s*([^\s,，]+)', 'name'),
            (r'叫(?:我做|我)\s*([^\s,，]+)', 'name'),
            (r'^(?:我的)?名字(?:是|叫)?\s*([^\s,，]+)', 'name'),
            (r'名字(?:是|叫)\s*([^\s,，]+)', 'name'),
            (r'(?:以后|以后)?(?:叫我|称呼我)\s*([^\s,，。]+)', 'nickname'),
            # 头像识别（更精确的模式，避免贪婪）
            (r'头像(?:是|为|:|：)?\s*["\']?([^"\'，。]+)["\']?', 'avatar'),
            (r'形象(?:是|为|:|：)?\s*["\']?([^"\'，。]+)["\']?', 'avatar'),
            (r'外观(?:是|为|:|：)?\s*["\']?([^"\'，。]+)["\']?', 'avatar'),
            # 性别识别（需要完整的性别词汇）
            (r'性别(?:\s*(?:是|:|：)\s*)?(["\']?(?:男|女)["\']?)', 'gender'),
            # 英文模式 - 名字（需要更精确的匹配）
            (r'(?:my name is|call me|named)\s+["\']?([A-Za-z][^\s"\'\n,]*)["\']?', 'name'),
            # 英文头像
            (r'(?:avatar|profile image)\s*(?:is|:)?\s*["\']?([^"\'\n。]+)["\']?', 'avatar'),
        ]

        results = {}
        for pattern, key in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().rstrip('"\'')
                # 过滤掉太短的或明显错误的值
                if len(value) >= 1 and value not in ['是', '为', ':', '：', 'is']:
                    results[key] = value

        # 如果已有name键，不要被nickname覆盖
        if 'name' in results and 'nickname' in results:
            del results['nickname']

        return results if results else None

    def identify_preference_info(self, text: str) -> Optional[Dict[str, str]]:
        """识别偏好信息"""
        patterns = [
            (r'(?:叫我|称呼我)\s*["\']?([^\s"\'，。]+)["\']?', 'nickname'),
            (r'(?:以后|以后)?(?:叫我|称呼我)\s*["\']?([^\s"\'，。]+)["\']?', 'nickname'),
            (r'(?:喜欢|love)\s*([^\s"\'，。]+)', 'likes'),
            (r'(?:讨厌|hate|不喜欢)\s*([^\s"\'，。]+)', 'dislikes'),
            (r'(?:希望|想要|want|prefer)[，,\s]*(.{2,30})', 'preference'),  # 2-30字符的偏好描述
        ]

        results = {}
        for pattern, key in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).strip().rstrip('"\'')
                # 过滤无效值
                if len(value) >= 2 and value not in ['是', '为', ':', '：']:
                    results[key] = value

        # nickname 应该优先于其他类型
        if 'nickname' in results:
            # 清除其他可能导致混淆的结果
            for key in ['preference', 'likes', 'dislikes']:
                if key in results:
                    del results[key]

        return results if results else None

    def identify_agreement(self, text: str) -> Optional[str]:
        """识别约定内容"""
        patterns = [
            (r'(?:说好了|约定|答应|agreed?|记住)\s*[:：]?\s*["\']?([^"\'\n。]+)["\']?', 1),
            (r'(?:以后|下次|从现在起)\s*["\']?([^"\'\n。]+)["\']?', 1),
            (r'(?:不要|禁止|别)\s*["\']?([^"\'\n。]+)["\']?', 1),
        ]

        for pattern, group_idx in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(group_idx).strip()
        return None

    # ============ 存储操作 ============

    def save_identity(self, key: str, value: str, source_hint: str = "") -> bool:
        """保存身份信息"""
        return self._save_entry("identity", key, value, source_hint)

    def save_preference(self, key: str, value: str, source_hint: str = "") -> bool:
        """保存偏好信息"""
        return self._save_entry("preferences", key, value, source_hint)

    def save_agreement(self, key: str, value: str, source_hint: str = "") -> bool:
        """保存约定"""
        return self._save_entry("agreements", key, value, source_hint)

    def save_fact(self, key: str, value: str, source_hint: str = "") -> bool:
        """保存事实"""
        return self._save_entry("facts", key, value, source_hint)

    def _save_entry(self, category: str, key: str, value: str, source_hint: str = "") -> bool:
        """通用保存方法"""
        filepath = self.memory_dir / MEMORY_FILES.get(category, f"{category}.md")

        try:
            content = filepath.read_text(encoding='utf-8')
            now = datetime.now().strftime("%Y-%m-%d %H:%M")

            # 检查是否已存在该键
            existing_pattern = rf'- \*\*{re.escape(key)}\*\*:.*?(?=\n\s*- \*\*|\n\s*---|\n\s*## |\Z)'
            existing_match = re.search(existing_pattern, content, re.DOTALL)

            if existing_match:
                # 更新现有条目
                old_entry = existing_match.group(0)
                new_entry = f"- **{key}**: {value}\n  - 创建时间: {self._extract_created_time(old_entry) or now}\n  - 更新时间: {now}\n  - 状态: updated"
                content = content.replace(old_entry, new_entry)
            else:
                # 添加新条目
                entry = MemoryEntry(
                    key=key,
                    value=value,
                    created_at=now,
                    updated_at=now,
                    source_hint=source_hint
                )

                # 直接追加到文件末尾
                content += entry.to_markdown() + "\n\n---\n\n"

            filepath.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False

    def _extract_created_time(self, entry_text: str) -> Optional[str]:
        """从条目中提取创建时间"""
        match = re.search(r'创建时间:\s*([\d-]+\s+[\d:]+)', entry_text)
        return match.group(1) if match else None

    def _find_section(self, content: str, key: str) -> Optional[str]:
        """根据键名找到合适的章节"""
        key_lower = key.lower()
        section_map = {
            'name': '基本信息',
            'nickname': '基本信息',
            'avatar': '头像描述',
            'description': '其他身份特征',
            'gender': '基本信息',
            'likes': '主题偏好',
            'dislikes': '主题偏好',
            'preference': '主题偏好',
        }
        return section_map.get(key_lower)

    # ============ 读取操作 ============

    def load_all_memories(self) -> Dict[str, str]:
        """加载所有记忆"""
        memories = {}
        for category, filename in MEMORY_FILES.items():
            filepath = self.memory_dir / filename
            if filepath.exists():
                memories[category] = filepath.read_text(encoding='utf-8')
        return memories

    def load_identity(self) -> str:
        """加载身份信息"""
        filepath = self.memory_dir / MEMORY_FILES["identity"]
        return filepath.read_text(encoding='utf-8') if filepath.exists() else ""

    def load_preferences(self) -> str:
        """加载偏好信息"""
        filepath = self.memory_dir / MEMORY_FILES["preferences"]
        return filepath.read_text(encoding='utf-8') if filepath.exists() else ""

    def load_agreements(self) -> str:
        """加载约定"""
        filepath = self.memory_dir / MEMORY_FILES["agreements"]
        return filepath.read_text(encoding='utf-8') if filepath.exists() else ""

    def get_compact_context(self) -> str:
        """获取紧凑的上下文（用于加载到AI上下文）"""
        memories = self.load_all_memories()
        lines = ["## 已记忆的关键信息\n"]

        for category, content in memories.items():
            if content.strip() and "## " in content:
                lines.append(f"\n### {category.upper()}")
                # 提取要点
                entries = re.findall(r'- \*\*(.+?)\*\*: (.+)', content)
                for key, value in entries:
                    lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    # ============ 处理用户消息 ============

    def process_message(self, message: str) -> List[Tuple[str, str, str]]:
        """
        处理用户消息，提取并保存关键信息
        返回: [(category, key, value), ...]
        """
        results = []

        # 识别身份信息
        identity = self.identify_identity_info(message)
        if identity:
            for key, value in identity.items():
                self.save_identity(key, value, message)
                results.append(("identity", key, value))

        # 识别偏好信息
        preference = self.identify_preference_info(message)
        if preference:
            for key, value in preference.items():
                self.save_preference(key, value, message)
                results.append(("preferences", key, value))

        # 识别约定
        agreement = self.identify_agreement(message)
        if agreement:
            self.save_agreement(f"agreement_{len(results)}", agreement, message)
            results.append(("agreements", "agreement", agreement))

        return results

    # ============ 对话摘要 ============

    def add_conversation_summary(self, summary: str) -> bool:
        """添加对话摘要"""
        filepath = self.memory_dir / MEMORY_FILES["summary"]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            content = filepath.read_text(encoding='utf-8')
            new_entry = f"### {now}\n\n{summary}\n\n---\n\n"

            # 在 "## 最近对话" 后插入
            if "## 最近对话" in content:
                parts = content.split("## 最近对话")
                content = parts[0] + "## 最近对话\n" + new_entry + parts[1]
            else:
                content += new_entry

            filepath.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            print(f"保存摘要失败: {e}")
            return False

    # ============ 工具方法 ============

    def clear_all_memories(self) -> bool:
        """清除所有记忆（谨慎使用）"""
        try:
            for filename in MEMORY_FILES.values():
                filepath = self.memory_dir / filename
                if filepath.exists():
                    filepath.unlink()
            self._ensure_memory_dir()
            return True
        except Exception as e:
            print(f"清除记忆失败: {e}")
            return False

    def export_memories_json(self) -> str:
        """导出为JSON格式"""
        memories = self.load_all_memories()
        export_data = {}

        for category, content in memories.items():
            entries = re.findall(r'- \*\*(.+?)\*\*: (.+)', content)
            export_data[category] = {k: v for k, v in entries}

        return json.dumps(export_data, ensure_ascii=False, indent=2)


# CLI 入口
if __name__ == "__main__":
    import sys

    manager = MemoryManager()

    if len(sys.argv) < 2:
        print("用法: python memory_manager.py <命令> [参数]")
        print("命令:")
        print("  init          - 初始化记忆目录")
        print("  process <文本> - 处理文本并提取信息")
        print("  load          - 加载所有记忆")
        print("  compact       - 获取紧凑上下文")
        print("  export        - 导出为JSON")
        print("  clear         - 清除所有记忆")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        manager._ensure_memory_dir()
        print("记忆目录已初始化")

    elif cmd == "process":
        if len(sys.argv) < 3:
            print("请提供要处理的文本")
            sys.exit(1)
        results = manager.process_message(sys.argv[2])
        for cat, key, value in results:
            print(f"[{cat}] {key}: {value}")

    elif cmd == "load":
        print(manager.load_all_memories().get("identity", "无"))

    elif cmd == "compact":
        print(manager.get_compact_context())

    elif cmd == "export":
        print(manager.export_memories_json())

    elif cmd == "clear":
        confirm = input("确定要清除所有记忆吗？(y/N): ")
        if confirm.lower() == 'y':
            manager.clear_all_memories()
            print("记忆已清除")
        else:
            print("取消操作")

    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)
