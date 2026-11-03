"""
词汇查询工具 - 用于在提示词生成时快速查找中英文标签

用法:
  python vocab_lookup.py 中文关键词          # 查找中文对应的英文标签
  python vocab_lookup.py --en 英文关键词      # 查找英文对应的中文
  python vocab_lookup.py --list              # 列出所有分类
  python vocab_lookup.py --cat 分类名         # 查看某个分类下的所有词汇
  python vocab_lookup.py --mother            # 列出母题模块
  python vocab_lookup.py --mother "脸部"      # 查看脸部模块的详情
"""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "references"


def load_vocab():
    path = BASE / "词汇数据库.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def load_mother():
    path = BASE / "母题数据库.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def list_categories(vocab):
    """列出所有分类"""
    print("\n📂 词汇分类：")
    for i, cat in enumerate(vocab.get("词汇", {}).keys(), 1):
        print(f"  {i:2d}. {cat}")


def view_category(vocab, cat_name):
    """查看某个分类下的词汇"""
    data = vocab.get("词汇", {})
    # 模糊匹配分类名
    matched = None
    for k in data:
        if cat_name in k:
            matched = k
            break
    if not matched:
        print(f"❌ 未找到分类: {cat_name}")
        print("可用分类：")
        list_categories(vocab)
        return

    print(f"\n📁 {matched}")
    entries = data[matched]
    if isinstance(entries, dict):
        # 检查是否有子分类
        has_sub = any(isinstance(v, dict) for v in entries.values())
        if has_sub:
            for sub_cat, items in entries.items():
                if isinstance(items, dict):
                    print(f"\n  🔸 {sub_cat}")
                    for cn, en in items.items():
                        print(f"    {cn} → {en}")
        else:
            for cn, en in entries.items():
                print(f"  {cn} → {en}")
    elif isinstance(entries, list):
        for item in entries:
            print(f"  {item}")


def search_cn(vocab, keyword):
    """按中文搜索"""
    print(f"\n🔍 搜索中文: \"{keyword}\"")
    found = False
    for cat, entries in vocab.get("词汇", {}).items():
        if isinstance(entries, dict):
            has_sub = any(isinstance(v, dict) for v in entries.values())
            if has_sub:
                for sub_cat, items in entries.items():
                    if isinstance(items, dict):
                        for cn, en in items.items():
                            if keyword in cn:
                                print(f"  [{cat} > {sub_cat}] {cn} → {en}")
                                found = True
            else:
                for cn, en in entries.items():
                    if keyword in cn:
                        print(f"  [{cat}] {cn} → {en}")
                        found = True
    if not found:
        print("  (无匹配)")


def search_en(vocab, keyword):
    """按英文搜索"""
    keyword = keyword.lower()
    print(f"\n🔍 搜索英文: \"{keyword}\"")
    found = False
    for cat, entries in vocab.get("词汇", {}).items():
        if isinstance(entries, dict):
            has_sub = any(isinstance(v, dict) for v in entries.values())
            if has_sub:
                for sub_cat, items in entries.items():
                    if isinstance(items, dict):
                        for cn, en in items.items():
                            if keyword in en.lower():
                                print(f"  [{cat} > {sub_cat}] {cn} → {en}")
                                found = True
            else:
                for cn, en in entries.items():
                    if keyword in en.lower():
                        print(f"  [{cat}] {cn} → {en}")
                        found = True
    if not found:
        print("  (无匹配)")


def list_mother_modules(mother):
    """列出母题模块"""
    modules = mother.get("模块", {})
    print("\n📂 母题模块：")
    for i, (name, info) in enumerate(modules.items(), 1):
        desc = info.get("description", "")
        detail_count = len(info.get("details", []))
        tag_count = len(info.get("sd_tags", []))
        print(f"  {i:2d}. {name}")
        if desc:
            print(f"      📝 {desc}")
        print(f"      📋 {detail_count} 个细节项, 🏷️ {tag_count} 个SD标签")


def view_mother_module(mother, keyword):
    """查看母题模块详情"""
    modules = mother.get("模块", {})
    matched = None
    for k in modules:
        if keyword in k:
            matched = k
            break
    if not matched:
        print(f"❌ 未找到模块: {keyword}")
        return

    info = modules[matched]
    print(f"\n📁 {matched}")
    if info.get("description"):
        print(f"  📝 {info['description']}")
    if info.get("details"):
        print(f"\n  📋 细节项:")
        for d in info["details"]:
            print(f"    • ({d})")
    if info.get("sd_tags"):
        print(f"\n  🏷️ SD 标签:")
        for t in info["sd_tags"]:
            print(f"    {t}")
    if info.get("mj_rule"):
        print(f"\n  🎨 MJ 描述:")
        print(f"    {info['mj_rule'][:200]}...")


def main():
    vocab = load_vocab()
    mother = load_mother()

    if not vocab:
        print("⚠️  词汇数据库.json 未找到，请先运行 convert_to_json.py")
        print(f"   期望路径: {BASE / '词汇数据库.json'}")
        return

    if len(sys.argv) < 2:
        print(__doc__)
        return

    arg = sys.argv[1]

    if arg == "--list":
        list_categories(vocab)
    elif arg == "--cat" and len(sys.argv) > 2:
        view_category(vocab, sys.argv[2])
    elif arg == "--en" and len(sys.argv) > 2:
        search_en(vocab, sys.argv[2])
    elif arg == "--mother":
        if mother:
            if len(sys.argv) > 2:
                view_mother_module(mother, sys.argv[2])
            else:
                list_mother_modules(mother)
        else:
            print("⚠️  母题数据库.json 未找到")
    else:
        search_cn(vocab, arg)


if __name__ == "__main__":
    main()
