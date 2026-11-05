#!/usr/bin/env python3
"""
Memory Index Manager
记忆索引管理器 - 用于管理和维护记忆系统的索引

功能:
1. 自动扫描 /memories 目录下的所有记忆文件
2. 生成和维护索引数据库
3. 支持多维度检索
4. 定期清理过期记忆
5. 生成记忆统计报告
"""

import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class MemoryIndex:
    """记忆索引数据类"""
    memory_id: str
    memory_path: str
    memory_type: str  # session, file, qa, preference, persistent
    title: str
    summary: str
    keywords: List[str]
    created_time: str
    updated_time: str
    file_size: int
    access_count: int
    last_access: str
    related_memories: List[str]
    tags: List[str]
    content_hash: str


class MemoryIndexManager:
    """记忆索引管理器"""

    def __init__(self, memories_path: str = "/memories"):
        """
        初始化记忆索引管理器

        Args:
            memories_path: 记忆存储根目录
        """
        self.memories_path = Path(memories_path)
        self.index_file = self.memories_path / ".memory_index.json"
        self.index: Dict[str, MemoryIndex] = {}
        self.load_index()

    def load_index(self) -> None:
        """从文件加载索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.index = {
                        k: MemoryIndex(**v) for k, v in data.items()
                    }
            except Exception as e:
                print(f"加载索引失败: {e}")
                self.index = {}

    def save_index(self) -> None:
        """保存索引到文件"""
        try:
            self.memories_path.mkdir(parents=True, exist_ok=True)
            with open(self.index_file, 'w', encoding='utf-8') as f:
                data = {k: asdict(v) for k, v in self.index.items()}
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存索引失败: {e}")

    def generate_memory_id(self, content: str, memory_type: str) -> str:
        """生成记忆唯一ID"""
        hash_input = f"{content}{datetime.now().isoformat()}{memory_type}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    def extract_memory_type(self, file_path: Path) -> str:
        """从文件路径提取记忆类型"""
        path_str = str(file_path)
        if '/sessions/' in path_str:
            return 'session'
        elif '/files/' in path_str:
            return 'file'
        elif '/qa/' in path_str:
            return 'qa'
        elif '/persistent/' in path_str:
            return 'preference'
        else:
            return 'other'

    def extract_metadata(self, content: str) -> Tuple[str, str, List[str]]:
        """
        从记忆内容中提取元数据

        Returns:
            (title, summary, keywords)
        """
        lines = content.split('\n')
        title = ""
        summary = ""
        keywords = []

        # 提取标题 (通常是第一个 # 开头的行)
        for line in lines[:20]:
            if line.startswith('# ') and not title:
                title = line[2:].strip()
                break

        # 提取关键词 (搜索常见的关键词模式)
        keyword_patterns = [
            r'标签[：:]\s*([^\n]+)',
            r'关键词[：:]\s*([^\n]+)',
            r'tags[：:]\s*([^\n]+)',
            r'keywords[：:]\s*([^\n]+)',
        ]

        for pattern in keyword_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                keyword_str = match.group(1)
                keywords = [k.strip() for k in keyword_str.replace('、', ',').split(',')]
                break

        # 生成摘要 (取前200个字符)
        content_lines = [l for l in lines if l.strip() and not l.startswith('#')]
        summary = ' '.join(content_lines)[:200].strip()

        return title, summary, keywords

    def scan_memories(self) -> int:
        """
        扫描记忆目录并更新索引

        Returns:
            新增或更新的记忆数量
        """
        count = 0
        current_time = datetime.now().isoformat()

        for file_path in self.memories_path.rglob("*.md"):
            # 跳过索引文件本身
            if file_path.name.startswith('.'):
                continue

            try:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 生成内容哈希
                content_hash = hashlib.md5(content.encode()).hex8()

                # 检查是否需要更新
                memory_id = self.generate_memory_id(str(file_path), 'path')
                should_update = True

                if memory_id in self.index:
                    existing = self.index[memory_id]
                    if existing.content_hash == content_hash:
                        # 内容未变，更新访问时间
                        existing.last_access = current_time
                        existing.access_count += 1
                        should_update = False

                if should_update:
                    # 提取元数据
                    title, summary, keywords = self.extract_metadata(content)
                    memory_type = self.extract_memory_type(file_path)

                    # 获取文件大小
                    file_size = file_path.stat().st_size

                    # 获取时间信息
                    stat = file_path.stat()
                    created_time = datetime.fromtimestamp(stat.st_ctime).isoformat()
                    updated_time = datetime.fromtimestamp(stat.st_mtime).isoformat()

                    # 创建或更新索引
                    memory_index = MemoryIndex(
                        memory_id=memory_id,
                        memory_path=str(file_path),
                        memory_type=memory_type,
                        title=title,
                        summary=summary,
                        keywords=keywords,
                        created_time=created_time,
                        updated_time=updated_time,
                        file_size=file_size,
                        access_count=1,
                        last_access=current_time,
                        related_memories=[],
                        tags=keywords
                    )

                    self.index[memory_id] = memory_index
                    count += 1

            except Exception as e:
                print(f"处理文件 {file_path} 失败: {e}")
                continue

        if count > 0:
            self.save_index()

        return count

    def search(self, query: str, memory_type: Optional[str] = None,
               limit: int = 10) -> List[MemoryIndex]:
        """
        搜索记忆

        Args:
            query: 搜索关键词
            memory_type: 记忆类型过滤
            limit: 返回结果数量限制

        Returns:
            匹配的 MemoryIndex 列表
        """
        results = []
        query_lower = query.lower()

        for memory_index in self.index.values():
            # 类型过滤
            if memory_type and memory_index.memory_type != memory_type:
                continue

            # 计算相关度
            relevance = 0

            # 标题匹配
            if query_lower in memory_index.title.lower():
                relevance += 10

            # 关键词匹配
            for keyword in memory_index.keywords:
                if query_lower in keyword.lower():
                    relevance += 5

            # 摘要匹配
            if query_lower in memory_index.summary.lower():
                relevance += 3

            # 标签匹配
            for tag in memory_index.tags:
                if query_lower in tag.lower():
                    relevance += 2

            if relevance > 0:
                memory_index.relevance = relevance
                results.append(memory_index)

        # 按相关度排序
        results.sort(key=lambda x: getattr(x, 'relevance', 0), reverse=True)

        return results[:limit]

    def get_statistics(self) -> Dict:
        """
        获取记忆统计信息

        Returns:
            统计信息字典
        """
        stats = {
            'total_memories': len(self.index),
            'by_type': defaultdict(int),
            'total_size': 0,
            'recent_memories': [],
            'most_accessed': [],
            'oldest_memory': None,
            'newest_memory': None,
        }

        for memory_index in self.index.values():
            stats['by_type'][memory_index.memory_type] += 1
            stats['total_size'] += memory_index.file_size

        # 最近访问的记忆
        sorted_by_access = sorted(
            self.index.values(),
            key=lambda x: x.last_access,
            reverse=True
        )
        stats['recent_memories'] = [
            {'id': m.memory_id, 'title': m.title, 'last_access': m.last_access}
            for m in sorted_by_access[:5]
        ]

        # 访问最多的记忆
        sorted_by_count = sorted(
            self.index.values(),
            key=lambda x: x.access_count,
            reverse=True
        )
        stats['most_accessed'] = [
            {'id': m.memory_id, 'title': m.title, 'access_count': m.access_count}
            for m in sorted_by_count[:5]
        ]

        # 最早和最新的记忆
        sorted_by_created = sorted(
            self.index.values(),
            key=lambda x: x.created_time
        )
        if sorted_by_created:
            stats['oldest_memory'] = {
                'id': sorted_by_created[0].memory_id,
                'title': sorted_by_created[0].title,
                'created': sorted_by_created[0].created_time
            }
            stats['newest_memory'] = {
                'id': sorted_by_created[-1].memory_id,
                'title': sorted_by_created[-1].title,
                'created': sorted_by_created[-1].created_time
            }

        # 转换 defaultdict 为普通 dict
        stats['by_type'] = dict(stats['by_type'])

        return stats

    def cleanup_old_memories(self, days: int = 90) -> int:
        """
        清理过期记忆

        Args:
            days: 超过多少天未访问的记忆将被标记

        Returns:
            清理的记忆数量
        """
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()
        count = 0

        for memory_id, memory_index in list(self.index.items()):
            if memory_index.last_access < cutoff_time:
                # 添加过期标记到文件内容
                try:
                    file_path = Path(memory_index.memory_path)
                    if file_path.exists():
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # 添加过期标记
                        expiry_mark = f"\n\n<!-- 过期标记: {datetime.now().isoformat()} -->\n"
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content + expiry_mark)

                        count += 1
                except Exception as e:
                    print(f"处理过期记忆 {memory_id} 失败: {e}")

        return count

    def generate_report(self) -> str:
        """
        生成记忆系统报告

        Returns:
            报告文本
        """
        stats = self.get_statistics()

        report = f"""
# 记忆系统统计报告

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 总体概况

- **记忆总数**: {stats['total_memories']}
- **存储总大小**: {stats['total_size'] / 1024:.2f} KB

## 按类型分布

| 类型 | 数量 | 占比 |
|------|------|------|
"""

        total = stats['total_memories']
        for memory_type, count in stats['by_type'].items():
            percentage = (count / total * 100) if total > 0 else 0
            report += f"| {memory_type} | {count} | {percentage:.1f}% |\n"

        report += f"""
## 最近访问

"""
        for item in stats['recent_memories']:
            report += f"- {item['title']} - {item['last_access']}\n"

        report += f"""
## 高频访问

"""
        for item in stats['most_accessed']:
            report += f"- {item['title']} - 访问 {item['access_count']} 次\n"

        if stats['oldest_memory']:
            report += f"""
## 时间跨度

- **最早记忆**: {stats['oldest_memory']['title']} ({stats['oldest_memory']['created']})
- **最新记忆**: {stats['newest_memory']['title']} ({stats['newest_memory']['created']})

"""

        return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='记忆索引管理器')
    parser.add_argument('command', choices=['scan', 'search', 'stats', 'cleanup', 'report'],
                       help='要执行的命令')
    parser.add_argument('--query', '-q', help='搜索关键词')
    parser.add_argument('--type', '-t', help='记忆类型过滤')
    parser.add_argument('--limit', '-l', type=int, default=10, help='结果数量限制')
    parser.add_argument('--days', '-d', type=int, default=90, help='清理过期天数')
    parser.add_argument('--path', '-p', default='/memories', help='记忆目录路径')

    args = parser.parse_args()

    manager = MemoryIndexManager(args.path)

    if args.command == 'scan':
        count = manager.scan_memories()
        print(f"扫描完成，新增/更新 {count} 条记忆")

    elif args.command == 'search':
        if not args.query:
            print("错误: 搜索命令需要 --query 参数")
            return

        results = manager.search(args.query, args.type, args.limit)
        print(f"找到 {len(results)} 条相关记忆:\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.title}")
            print(f"   路径: {result.memory_path}")
            print(f"   摘要: {result.summary[:100]}...")
            print()

    elif args.command == 'stats':
        stats = manager.get_statistics()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.command == 'cleanup':
        count = manager.cleanup_old_memories(args.days)
        print(f"已标记 {count} 条过期记忆")

    elif args.command == 'report':
        report = manager.generate_report()
        print(report)


if __name__ == '__main__':
    main()
