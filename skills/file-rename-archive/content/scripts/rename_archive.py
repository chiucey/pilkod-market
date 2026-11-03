"""
file-rename-archive: 国资资料库文件重命名与归档脚本
用法：
    uv run scripts/rename_archive.py --input result.json --archive-root "Z:\\国资档案库"
    uv run scripts/rename_archive.py --input result.json --archive-root "Z:\\国资档案库" --dry-run
"""

import argparse
import json
import os
import re
import shutil
import sys
import datetime
from pathlib import Path


# ──────────────────────────────────────────────
# subject 清洗
# ──────────────────────────────────────────────

def clean_subject(subject: str, max_len: int = 15) -> str:
    """清洗 subject 字段：去编号前缀、去特殊符号、截断至 max_len 字符。"""
    if not subject:
        return "未命名文件"

    # 去除编号前缀
    subject = re.sub(r'^附件[\d一二三四五六七八九十]+[：:]\s*', '', subject)
    subject = re.sub(r'^[（(][\d一二三四五六七八九十]+[）)]\s*', '', subject)
    subject = re.sub(r'^[\d\u4e00-\u9fa5]+[、]\s*', '', subject)
    subject = re.sub(r'^\d+[\.．]\s*', '', subject)

    # 去除特殊符号（引号、书名号、括号、标点）
    subject = re.sub(r'[""\'\'\"《》〈〉【】\[\]（）()]', '', subject)
    subject = re.sub(r'[！!？?#@&*%；;、……]', '', subject)
    subject = re.sub(r'\.{2,}', '', subject)  # 省略号

    # 截断
    subject = subject.strip()
    if len(subject) > max_len:
        subject = subject[:max_len]

    return subject.strip() or "未命名文件"


# ──────────────────────────────────────────────
# 日期生成
# ──────────────────────────────────────────────

def get_date_str(year: str, file_path: str) -> str:
    """优先使用 year 字段，月日从文件修改时间提取；year 为空则完全用修改时间。"""
    try:
        mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    except OSError:
        mtime = datetime.datetime.now()

    if year and len(year) == 4 and year.isdigit():
        return f"{year}{mtime.month:02d}{mtime.day:02d}"
    return mtime.strftime("%Y%m%d")


# ──────────────────────────────────────────────
# 新文件名生成
# ──────────────────────────────────────────────

def build_new_filename(record: dict, file_path: str) -> str:
    """根据分类记录生成规范化新文件名。"""
    date_str = get_date_str(record.get("year", ""), file_path)
    company = (record.get("company") or "").strip()
    subject = clean_subject(record.get("subject", ""))
    version = (record.get("version") or "").strip()
    ext = Path(file_path).suffix.lower()  # 保留原扩展名并小写

    # 拼接：YYYYMMDD_公司_主题_版本.ext
    # 公司为空时保留双下划线占位
    if company:
        base = f"{date_str}_{company}_{subject}"
    else:
        base = f"{date_str}__{subject}"

    if version:
        base = f"{base}_{version}"

    return f"{base}{ext}"


# ──────────────────────────────────────────────
# 目标目录构建
# ──────────────────────────────────────────────

def build_target_dir(archive_root: str, record: dict) -> str:
    """根据分类信息构建目标子目录路径。"""
    cat1 = record.get("category1", "").strip()
    cat1_name = record.get("category1_name", "").strip()
    cat2 = record.get("category2", "").strip()
    cat2_name = record.get("category2_name", "").strip()

    dir1 = f"{cat1}类_{cat1_name}"
    dir2 = f"{cat2}_{cat2_name}"
    return os.path.join(archive_root, dir1, dir2)


# ──────────────────────────────────────────────
# 重名冲突处理
# ──────────────────────────────────────────────

def resolve_conflict(target_dir: str, filename: str, max_tries: int = 99) -> str:
    """若目标文件已存在，追加 _1、_2 等序号。"""
    stem = Path(filename).stem
    ext = Path(filename).suffix
    candidate = os.path.join(target_dir, filename)

    if not os.path.exists(candidate):
        return filename

    for i in range(1, max_tries + 1):
        new_name = f"{stem}_{i}{ext}"
        candidate = os.path.join(target_dir, new_name)
        if not os.path.exists(candidate):
            return new_name

    raise FileExistsError(f"超过最大重试次数（{max_tries}），无法解决文件名冲突：{filename}")


# ──────────────────────────────────────────────
# Windows 长路径前缀
# ──────────────────────────────────────────────

def make_long_path(path: str) -> str:
    """为 Windows 长路径添加 \\?\ 或 \\?\UNC\ 前缀。"""
    if path.startswith("\\\\"):
        # UNC 路径
        return "\\\\?\\UNC\\" + path[2:]
    return "\\\\?\\" + os.path.abspath(path)


# ──────────────────────────────────────────────
# 索引更新（预留接口）
# ──────────────────────────────────────────────

def notify_index(record: dict, new_path: str, new_filename: str, index_url: str):
    """向 Skill 3 索引接口发送归档通知（预留，非阻塞）。"""
    try:
        import urllib.request
        payload = json.dumps({
            "action": "archive",
            "original_path": record.get("original_path", ""),
            "new_path": new_path,
            "new_filename": new_filename,
            "category1": record.get("category1", ""),
            "category2": record.get("category2", ""),
            "timestamp": datetime.datetime.now().isoformat(),
        }).encode("utf-8")
        req = urllib.request.Request(
            index_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status // 100 != 2:
                print(f"[WARN] 索引更新返回非 2xx：{resp.status}", file=sys.stderr)
    except Exception as e:
        print(f"[WARN] 索引更新失败（不影响归档）：{e}", file=sys.stderr)


# ──────────────────────────────────────────────
# 单文件归档
# ──────────────────────────────────────────────

def archive_file(record: dict, archive_root: str, backup_dir: str = None,
                 index_url: str = None, dry_run: bool = False) -> dict:
    """对单条记录执行重命名与归档，返回结果字典。"""
    original_path = record.get("original_path", "")
    result = {
        "original_path": original_path,
        "new_path": None,
        "new_filename": None,
        "status": "failed",
        "error": None,
    }

    # 检查原文件存在
    if not os.path.isfile(original_path):
        result["error"] = f"原文件不存在：{original_path}"
        return result

    try:
        # 构建目标目录
        target_dir = build_target_dir(archive_root, record)

        # 生成新文件名
        new_filename = build_new_filename(record, original_path)
        new_filename = resolve_conflict(target_dir, new_filename)

        new_path = os.path.join(target_dir, new_filename)

        result["new_filename"] = new_filename
        result["new_path"] = new_path

        if dry_run:
            print(f"[DRY-RUN] {original_path!r} → {new_path!r}")
            result["status"] = "success"
            return result

        # 创建目标目录
        try:
            os.makedirs(target_dir, exist_ok=True)
        except OSError:
            long_dir = make_long_path(target_dir)
            os.makedirs(long_dir, exist_ok=True)
            new_path = os.path.join(long_dir, new_filename)
            result["new_path"] = new_path

        # 可选：备份原文件
        if backup_dir:
            os.makedirs(backup_dir, exist_ok=True)
            shutil.copy2(original_path, os.path.join(backup_dir, Path(original_path).name))

        # 移动文件
        try:
            shutil.move(original_path, new_path)
        except OSError:
            # 尝试长路径
            long_src = make_long_path(original_path)
            long_dst = make_long_path(new_path)
            shutil.move(long_src, long_dst)
            result["new_path"] = new_path  # 记录规范路径

        result["status"] = "success"

        # 通知索引
        if index_url:
            notify_index(record, new_path, new_filename, index_url)

    except FileExistsError as e:
        result["error"] = str(e)
    except OSError as e:
        msg = str(e)
        if len(new_path) > 260:
            msg += f"（路径长度 {len(new_path)} 超过 260，建议缩短目录层级或映射盘符）"
        result["error"] = msg
    except Exception as e:
        result["error"] = f"未知错误：{e}"

    return result


# ──────────────────────────────────────────────
# 主流程
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="国资资料库文件重命名与归档")
    parser.add_argument("--input", required=True, help="分类结果 JSON 文件路径")
    parser.add_argument("--archive-root", required=True, help="归档根目录路径")
    parser.add_argument("--backup-dir", default=None, help="可选：备份原文件目录")
    parser.add_argument("--index-url", default=os.environ.get("INDEX_UPDATE_URL"), help="可选：索引更新接口 URL")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际移动文件")
    args = parser.parse_args()

    # 读取 JSON
    with open(args.input, encoding="utf-8") as f:
        data = json.load(f)

    # 兼容数组或单对象
    if isinstance(data, dict):
        records = data.get("results", [data])
    elif isinstance(data, list):
        records = data
    else:
        print("错误：输入 JSON 格式不支持，需为数组或对象。", file=sys.stderr)
        sys.exit(1)

    results = []
    for record in records:
        res = archive_file(
            record,
            archive_root=args.archive_root,
            backup_dir=args.backup_dir,
            index_url=args.index_url,
            dry_run=args.dry_run,
        )
        results.append(res)

        icon = "✅" if res["status"] == "success" else "❌"
        print(f"{icon} {res['original_path']}")
        if res["status"] == "success":
            print(f"   → {res['new_path']}")
        else:
            print(f"   错误：{res['error']}")

    # 汇总
    total = len(results)
    success = sum(1 for r in results if r["status"] == "success")
    failed = total - success

    output = {
        "summary": {"total": total, "success": success, "failed": failed},
        "results": results,
    }

    print("\n── 归档汇总 ──")
    print(f"总计：{total}  成功：{success}  失败：{failed}")
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
