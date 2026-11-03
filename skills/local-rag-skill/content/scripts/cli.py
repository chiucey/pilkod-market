"""
Local RAG Skill - 命令行工具
提供交互式命令行接口
"""

import os
import sys
import argparse
import json
from pathlib import Path
from typing import Optional

# 添加脚本目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from knowledge_base import LocalKnowledgeBase


def create_parser() -> argparse.ArgumentParser:
    """创建命令行解析器"""
    parser = argparse.ArgumentParser(
        prog='local_rag',
        description='Local RAG - 本地知识库管理工具'
    )

    # 全局参数
    parser.add_argument(
        '--db-path',
        default='./vector_db',
        help='数据库存储路径 (默认: ./vector_db)'
    )
    parser.add_argument(
        '--config',
        type=Path,
        help='配置文件路径'
    )

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # init - 初始化知识库
    init_parser = subparsers.add_parser('init', help='初始化知识库')
    init_parser.add_argument(
        '--db-path',
        default='./vector_db',
        help='数据库存储路径'
    )
    init_parser.add_argument(
        '--embedding-model',
        default='sentence-transformers/all-MiniLM-L6-v2',
        help='Embedding模型'
    )

    # add - 添加文档
    add_parser = subparsers.add_parser('add', help='添加文档到知识库')
    add_parser.add_argument('files', nargs='+', help='文件路径或文件夹')
    add_parser.add_argument(
        '--chunk-size',
        type=int,
        default=500,
        help='文本分块大小'
    )
    add_parser.add_argument(
        '--recursive',
        action='store_true',
        help='递归处理文件夹'
    )

    # add-text - 添加文本
    add_text_parser = subparsers.add_parser('add-text', help='添加文本到知识库')
    add_text_parser.add_argument('text', help='要添加的文本内容')
    add_text_parser.add_argument('--title', default='Untitled', help='文档标题')

    # search - 搜索
    search_parser = subparsers.add_parser('search', help='搜索知识库')
    search_parser.add_argument('query', help='查询文本')
    search_parser.add_argument(
        '--top-k',
        type=int,
        default=4,
        help='返回结果数量'
    )
    search_parser.add_argument(
        '--threshold',
        type=float,
        default=0.5,
        help='相似度阈值'
    )
    search_parser.add_argument(
        '--json',
        action='store_true',
        help='输出JSON格式'
    )

    # list - 列出文档
    list_parser = subparsers.add_parser('list', help='列出知识库中的文档')
    list_parser.add_argument(
        '--json',
        action='store_true',
        help='输出JSON格式'
    )

    # get - 获取文档
    get_parser = subparsers.add_parser('get', help='获取文档内容')
    get_parser.add_argument('doc_id', help='文档ID')
    get_parser.add_argument(
        '--chunks',
        action='store_true',
        help='包含所有块'
    )

    # delete - 删除文档
    delete_parser = subparsers.add_parser('delete', help='删除文档')
    delete_parser.add_argument('doc_id', help='文档ID')

    # update - 更新文档
    update_parser = subparsers.add_parser('update', help='更新文档')
    update_parser.add_argument('doc_id', help='文档ID')
    update_parser.add_argument('--file', help='新文件路径')
    update_parser.add_argument('--text', help='新文本内容')
    update_parser.add_argument('--title', help='新标题')

    # stats - 统计信息
    stats_parser = subparsers.add_parser('stats', help='显示统计信息')
    stats_parser.add_argument(
        '--json',
        action='store_true',
        help='输出JSON格式'
    )

    # clear - 清空知识库
    clear_parser = subparsers.add_parser('clear', help='清空知识库')
    clear_parser.add_argument(
        '--force',
        action='store_true',
        help='强制清空，不提示确认'
    )

    return parser


def cmd_init(args, kb: LocalKnowledgeBase):
    """初始化命令"""
    print(f"知识库初始化完成")
    print(f"数据库路径: {args.db_path}")
    print(f"使用前请确保已安装依赖: pip install -r requirements.txt")


def cmd_add(args, kb: LocalKnowledgeBase):
    """添加文档命令"""
    added_ids = []

    for file_path in args.files:
        path = Path(file_path)

        if not path.exists():
            print(f"文件不存在: {file_path}")
            continue

        if path.is_dir():
            try:
                ids = kb.add_folder(str(path), recursive=args.recursive)
                added_ids.extend(ids)
                print(f"从文件夹 {path} 添加了 {len(ids)} 个文档")
            except Exception as e:
                print(f"处理文件夹失败 {path}: {e}")
        else:
            try:
                doc_id = kb.add_document(str(path))
                added_ids.append(doc_id)
                print(f"添加文档成功: {path.name} (ID: {doc_id})")
            except Exception as e:
                print(f"处理文件失败 {path}: {e}")

    print(f"\n共添加 {len(added_ids)} 个文档")


def cmd_add_text(args, kb: LocalKnowledgeBase):
    """添加文本命令"""
    try:
        doc_id = kb.add_text(args.text, args.title)
        print(f"添加文本成功 (ID: {doc_id})")
    except Exception as e:
        print(f"添加文本失败: {e}")


def cmd_search(args, kb: LocalKnowledgeBase):
    """搜索命令"""
    results = kb.search(args.query, top_k=args.top_k)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if not results:
            print("没有找到相关结果")
            return

        print(f"找到 {len(results)} 个相关结果:\n")

        for i, result in enumerate(results, 1):
            print(f"{'='*60}")
            print(f"[{i}] {result['title']}")
            print(f"    文档ID: {result['doc_id']}")
            print(f"    相似度: {result['score']:.4f}")
            print(f"    内容: {result['content'][:200]}...")
            print()


def cmd_list(args, kb: LocalKnowledgeBase):
    """列出文档命令"""
    docs = kb.list_documents()

    if args.json:
        print(json.dumps(docs, ensure_ascii=False, indent=2))
    else:
        if not docs:
            print("知识库为空")
            return

        print(f"知识库中共有 {len(docs)} 个文档:\n")

        for doc in docs:
            print(f"  - [{doc['doc_id']}] {doc['title']}")
            print(f"    块数: {doc['chunk_count']}")
            print(f"    添加时间: {doc['added_at']}")
            print()


def cmd_get(args, kb: LocalKnowledgeBase):
    """获取文档命令"""
    doc = kb.get_document(args.doc_id, include_chunks=args.chunks)

    if doc is None:
        print(f"文档不存在: {args.doc_id}")
        return

    if args.chunks:
        print(json.dumps(doc, ensure_ascii=False, indent=2))
    else:
        print(f"标题: {doc['title']}")
        print(f"文档ID: {doc['doc_id']}")
        print(f"源文件: {doc['source_path']}")
        print(f"块数: {doc['chunk_count']}")
        print(f"添加时间: {doc['added_at']}")
        print(f"\n{'='*60}")
        print(doc['content'])


def cmd_delete(args, kb: LocalKnowledgeBase):
    """删除文档命令"""
    if kb.delete_document(args.doc_id):
        print(f"文档已删除: {args.doc_id}")
    else:
        print(f"文档不存在: {args.doc_id}")


def cmd_update(args, kb: LocalKnowledgeBase):
    """更新文档命令"""
    success = kb.update_document(
        args.doc_id,
        new_file_path=args.file,
        new_text=args.text,
        new_title=args.title
    )

    if success:
        print(f"文档已更新: {args.doc_id}")
    else:
        print(f"更新失败，文档不存在: {args.doc_id}")


def cmd_stats(args, kb: LocalKnowledgeBase):
    """统计信息命令"""
    stats = kb.get_stats()

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print("=" * 40)
        print("Local RAG 知识库统计信息")
        print("=" * 40)
        print(f"总文档数: {stats['total_documents']}")
        print(f"总块数: {stats['total_chunks']}")
        print(f"数据库类型: {stats['vector_db_type']}")
        print(f"Embedding模型: {stats['embedding_model']}")
        print(f"数据库路径: {stats['db_path']}")

        if stats['documents']:
            print("\n文档列表:")
            for doc in stats['documents']:
                print(f"  - [{doc['doc_id']}] {doc['title']} ({doc['chunk_count']}块)")


def cmd_clear(args, kb: LocalKnowledgeBase):
    """清空知识库命令"""
    if not args.force:
        confirm = input("确定要清空知识库吗？此操作不可恢复 (y/N): ")
        if confirm.lower() != 'y':
            print("取消操作")
            return

    count = kb.clear()
    print(f"已清空 {count} 个文档")


def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    # 创建知识库实例
    try:
        kb = LocalKnowledgeBase(db_path=args.db_path)
    except Exception as e:
        print(f"初始化知识库失败: {e}")
        return

    # 执行命令
    commands = {
        'init': cmd_init,
        'add': cmd_add,
        'add-text': cmd_add_text,
        'search': cmd_search,
        'list': cmd_list,
        'get': cmd_get,
        'delete': cmd_delete,
        'update': cmd_update,
        'stats': cmd_stats,
        'clear': cmd_clear,
    }

    if args.command in commands:
        commands[args.command](args, kb)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
