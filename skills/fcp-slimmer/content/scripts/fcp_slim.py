#!/usr/bin/env python3
"""
FCP X 工程文件瘦身工具
删除 .fcpbundle 中的渲染缓存、优化媒体、代理媒体，显著减小工程体积。
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime

# FCPX 资源库中可安全删除的目录（按大小排序，从大到小）
SLIM_TARGETS = [
    {"name": "Render Files", "desc": "渲染缓存文件", "safe": True},
    {"name": "Optimized Media", "desc": "优化媒体(ProRes转码)", "safe": True},
    {"name": "Proxy Media", "desc": "代理媒体(低分辨率副本)", "safe": True},
    {"name": "Audio Analysis Files", "desc": "音频分析缓存", "safe": True},
]

# 需要递归搜索的目录（这些目录在事件文件夹内部）
RECURSE_IN = ["Original Media", "Transcoded Media"]

# 输出模式
MODE_JSON = "json"
MODE_TEXT = "text"


def get_dir_size(path: Path) -> int:
    """计算目录总大小（字节）"""
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file() and not entry.is_symlink():
                try:
                    total += entry.stat().st_size
                except (OSError, PermissionError):
                    pass
    except Exception:
        pass
    return total


def format_size(size_bytes: int) -> str:
    """格式化字节数为人类可读格式"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def find_fcpbundles(base_path: str) -> list[Path]:
    """查找指定路径下的所有 .fcpbundle 文件"""
    base = Path(base_path)
    bundles = []
    
    # 直接是 .fcpbundle 文件
    if base.suffix == ".fcpbundle" or (base.is_dir() and base.suffixes and ".fcpbundle" in "".join(base.suffixes)):
        # 处理如 xxx.fcpbundle 的情况
        if base.exists():
            bundles.append(base)
        return bundles
    
    # 目录下查找所有 .fcpbundle
    if base.is_dir():
        for item in base.iterdir():
            name = item.name
            # .fcpbundle 可能表现为文件夹
            if name.endswith(".fcpbundle") and item.exists():
                bundles.append(item)
            # 也检查隐藏的 bundle（macOS 的一些变体）
    
    return bundles


def scan_bundle(bundle_path: Path, dry_run: bool = False, targets: list = None) -> dict:
    """
    扫描一个 fcpbundle 中的可清理内容
    返回扫描结果字典
    """
    if targets is None:
        targets = SLIM_TARGETS
    result = {
        "bundle_name": bundle_path.name,
        "bundle_path": str(bundle_path),
        "total_original_size": 0,
        "total_recoverable": 0,
        "targets": [],
        "errors": [],
        "timestamp": datetime.now().isoformat(),
    }
    
    if not bundle_path.exists():
        result["errors"].append(f"Bundle不存在: {bundle_path}")
        return result
    
    try:
        # 计算原始总大小
        result["total_original_size"] = get_dir_size(bundle_path)
        
        # 遍历 bundle 内部结构
        for target_info in targets:
            target_name = target_info["name"]
            
            # 在 bundle 根目录和子目录中搜索目标文件夹
            found_paths = list(bundle_path.rglob(target_name))
            
            for target_path in found_paths:
                if not target_path.is_dir():
                    continue
                    
                size = get_dir_size(target_path)
                if size == 0:
                    continue
                    
                target_result = {
                    "name": target_name,
                    "desc": target_info["desc"],
                    "path": str(target_path),
                    "size": size,
                    "size_human": format_size(size),
                    "safe": target_info["safe"],
                }
                
                # 如果不是 dry_run，执行删除
                if not dry_run:
                    try:
                        shutil.rmtree(target_path)
                        target_result["deleted"] = True
                        result["total_recoverable"] += size
                    except Exception as e:
                        target_result["deleted"] = False
                        target_result["error"] = str(e)
                        result["errors"].append(f"删除失败 {target_path}: {e}")
                else:
                    target_result["deleted"] = False
                    result["total_recoverable"] += size
                
                result["targets"].append(target_result)
        
        # 额外：清理 Shared Render Files 等特殊位置
        for special_name in ["Shared Render Files", "Shared Proxy Media", "Shared Optimized Media"]:
            special_path = bundle_path / special_name
            if special_path.is_dir():
                size = get_dir_size(special_path)
                if size > 0:
                    target_result = {
                        "name": special_name,
                        "desc": f"共享{special_name.replace('Shared ', '')}",
                        "path": str(special_path),
                        "size": size,
                        "size_human": format_size(size),
                        "safe": True,
                    }
                    if not dry_run:
                        try:
                            shutil.rmtree(special_path)
                            target_result["deleted"] = True
                            result["total_recoverable"] += size
                        except Exception as e:
                            target_result["deleted"] = False
                            target_result["error"] = str(e)
                    else:
                        result["total_recoverable"] += size
                    result["targets"].append(target_result)
                    
    except Exception as e:
        result["errors"].append(f"扫描异常: {e}")
    
    return result


def get_slim_targets():
    """获取当前有效的瘦身目标列表"""
    return SLIM_TARGETS


def get_all_target_names():
    """获取所有可能的目录名（用于命令行选项）"""
    base = [t["name"] for t in SLIM_TARGETS]
    extra = ["Shared Render Files", "Shared Proxy Media", "Shared Optimized Media", "Audio Analysis Files"]
    return base + extra


def filter_targets(allowed_names: set) -> list:
    """根据允许的名称过滤瘦身目标"""
    filtered = [t for t in SLIM_TARGETS if t["name"] in allowed_names]
    for n in {"Shared Render Files", "Shared Proxy Media", "Shared Optimized Media", "Audio Analysis Files"} & allowed_names:
        filtered.append({"name": n, "desc": f"共享{n.replace('Shared ', '').replace('Files', '文件').replace('Media', '')}", "safe": True})
    return filtered


def main():
    import argparse
    
    all_names = get_all_target_names()
    
    parser = argparse.ArgumentParser(description="FCP X 工程文件瘦身工具")
    parser.add_argument("path", help="FCPX资源库路径(.fcpbundle)或包含.fcpbundle的目录")
    parser.add_argument("--dry-run", "-n", action="store_true", default=False,
                       help="仅扫描不删除，预览可释放空间")
    parser.add_argument("--json", action="store_true", default=False,
                       help="以JSON格式输出结果")
    parser.add_argument("--targets", nargs="+", choices=all_names,
                       help="仅清理指定类型，默认全部清理")
    
    args = parser.parse_args()
    
    mode = MODE_JSON if args.json else MODE_TEXT
    dry_run = args.dry_run
    
    # 如果指定了 targets 过滤器
    if args.targets:
        active_targets = filter_targets(set(args.targets))
    else:
        active_targets = SLIM_TARGETS
    
    path = os.path.expanduser(args.path)
    
    # 判断是单个 bundle 还是目录
    base = Path(path)
    if base.suffix == ".fcpbundle" or (base.is_dir() and ".fcpbundle" in base.name):
        bundles = [base]
    else:
        bundles = find_fcpbundles(path)
    
    if not bundles:
        output = {"error": f"未找到任何.fcpbundle文件: {path}"} if mode == MODE_JSON else f"[ERROR] 未找到任何.fcpbundle文件: {path}"
        print(output if isinstance(output, str) else json.dumps(output, ensure_ascii=False, indent=2))
        sys.exit(1)
    
    results = []
    grand_total_original = 0
    grand_total_recoverable = 0
    
    for bundle in bundles:
        r = scan_bundle(bundle, dry_run=dry_run, targets=active_targets)
        results.append(r)
        grand_total_original += r.get("total_original_size", 0)
        grand_total_recoverable += r.get("total_recoverable", 0)
    
    # 输出结果
    summary = {
        "mode": "预览(dry-run)" if dry_run else "执行清理",
        "bundles_scanned": len(results),
        "grand_total_original": grand_total_original,
        "grand_total_original_human": format_size(grand_total_original),
        "grand_total_recoverable": grand_total_recoverable,
        "grand_total_recoverable_human": format_size(grand_total_recoverable),
        "recovery_percent": (
            f"{grand_total_recoverable / grand_total_original * 100:.1f}%"
            if grand_total_original > 0 else "0%"
        ),
        "details": results,
        "timestamp": datetime.now().isoformat(),
    }
    
    if mode == MODE_JSON:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"[FCPX] 工程文件瘦身 {'预览' if dry_run else '报告'}")
        print(f"{'='*60}")
        print(f"[INFO] 扫描资源库数: {len(results)}")
        print(f"[INFO] 原始总大小: {format_size(grand_total_original)}")
        print(f"[INFO] 可释放空间: {format_size(grand_total_recoverable)} ({summary['recovery_percent']})")
        print(f"{'='*60}\n")

        for r in results:
            print(f"[BUNDLE] {r['bundle_name']}")
            print(f"   原始大小: {format_size(r['total_original_size'])}")
            if r['targets']:
                for t in r['targets']:
                    status = "[OK] 已删除" if t.get('deleted') else ("[PENDING] 待删除" if dry_run else f"[ERROR] {t.get('error', '失败')}")
                    print(f"   [DELETE] [{status}] {t['name']} ({t['desc']}): {t['size_human']}")
            else:
                print("   [SKIP] 无需清理")

            if r.get('errors'):
                for err in r['errors']:
                    print(f"   [WARNING] {err}")
            print()

        if not dry_run:
            print(f"[OK] 瘦身完成！共释放 {format_size(grand_total_recoverable)} 空间。")
            print(f"[HINT] 下次打开 FCPX 时会自动重新生成必要的缓存。")
        else:
            print(f"[HINT] 这是预览模式，使用不带 --dry-run 的命令执行实际清理")


if __name__ == "__main__":
    main()
