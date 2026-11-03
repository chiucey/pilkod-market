import argparse
import json
import os
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="清理已审核的奖学金申请表PDF文件"
    )
    parser.add_argument(
        "--dir",
        default=".",
        help="扫描目录路径，默认为当前目录",
    )
    parser.add_argument(
        "--reviewed-list",
        default="reviewed_files.txt",
        help="已审核文件列表路径，每行一个文件名",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="试运行模式，只输出将要删除的文件而不实际删除",
    )
    parser.add_argument(
        "--older-than",
        type=int,
        default=0,
        help="删除超过N天未修改的PDF文件（与reviewed-list条件取并集）",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        result = {
            "status": "error",
            "message": f"目录不存在: {args.dir}",
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    # 读取已审核文件列表
    reviewed = set()
    list_path = os.path.join(args.dir, args.reviewed_list)
    if os.path.exists(list_path):
        with open(list_path, "r", encoding="utf-8") as f:
            reviewed = {line.strip() for line in f if line.strip()}

    deleted = []
    skipped = []
    now = datetime.now()

    for fname in os.listdir(args.dir):
        if not fname.lower().endswith(".pdf"):
            continue

        fpath = os.path.join(args.dir, fname)
        should_delete = False
        reason = ""

        # 条件1：在已审核列表中
        if fname in reviewed:
            should_delete = True
            reason = "in_reviewed_list"
        # 条件2：超过指定天数未修改
        elif args.older_than > 0:
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            days_old = (now - mtime).days
            if days_old >= args.older_than:
                should_delete = True
                reason = f"older_than_{args.older_than}_days"

        if should_delete:
            if not args.dry_run:
                try:
                    os.remove(fpath)
                except OSError as e:
                    skipped.append({"file": fname, "reason": str(e)})
                    continue
            deleted.append({"file": fname, "reason": reason})
        else:
            skipped.append({"file": fname, "reason": "not_reviewed"})

    result = {
        "status": "success",
        "timestamp": now.isoformat(),
        "directory": os.path.abspath(args.dir),
        "dry_run": args.dry_run,
        "deleted_count": len(deleted),
        "deleted_files": deleted,
        "skipped_count": len(skipped),
        "skipped_files": skipped,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
