import os
import shutil
from datetime import datetime
from pathlib import Path

# 配置区域
TARGET_DIR = os.path.expanduser("~/Downloads")  # 下载文件夹路径

# 文件分类映射
FILE_CATEGORIES = {
    "📚 Books & Reading": [".pdf", ".epub", ".mobi", ".txt", ".doc", ".docx"],
    "🎬 Movies & Videos": [".mp4", ".mov", ".avi", ".mkv", ".mp3", ".wav", ".m4a"],
    "📖 Manga & Comics": [".cbz", ".cbr"],
    "📸 Photography - Presets": [".jpg", ".jpeg", ".png", ".gif", ".svg", ".raw", ".cr2", ".nef", ".heic"],
    "🗂 Misc & Personal": []  # 其他文件
}

# 需要保留的现有文件夹
EXISTING_FOLDERS = [
    "📚 Books & Reading",
    "🎬 Movies & Videos",
    "📖 Manga & Comics",
    "📸 Photography - Presets",
    "🗂 Misc & Personal",
    "📊 Work - PPT & Power BI"
]

# 需要忽略的文件
IGNORE_FILES = [".DS_Store", ".localized", "_Folder_Manifest.md"]


def get_category(file_ext):
    """根据文件扩展名返回分类文件夹名称"""
    file_ext = file_ext.lower()
    for category, extensions in FILE_CATEGORIES.items():
        if file_ext in extensions:
            return category
    return "🗂 Misc & Personal"


def get_unique_filename(dest_dir, filename):
    """生成不冲突的文件名"""
    file_path = Path(dest_dir) / filename
    if not file_path.exists():
        return filename

    # 分离文件名和扩展名
    name = Path(filename).stem
    ext = Path(filename).suffix

    counter = 1
    while True:
        new_filename = f"{name}_{counter}{ext}"
        if not (Path(dest_dir) / new_filename).exists():
            return new_filename
        counter += 1


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def organize_downloads():
    """主整理函数"""
    target_path = Path(TARGET_DIR)
    moved_files = []
    errors = []

    print(f"📂 开始整理文件夹: {TARGET_DIR}")
    print("=" * 50)

    # 遍历根目录下的所有文件
    for item in target_path.iterdir():
        # 跳过文件夹和忽略的文件
        if item.is_dir() or item.name in IGNORE_FILES:
            continue

        # 获取文件扩展名
        file_ext = item.suffix.lower()

        # 确定目标分类
        category = get_category(file_ext)
        dest_dir = target_path / category

        # 如果目标文件夹不存在，创建它
        dest_dir.mkdir(exist_ok=True)

        # 检查目标目录是否在保留列表中
        is_existing_folder = category in EXISTING_FOLDERS

        # 生成唯一文件名
        unique_filename = get_unique_filename(dest_dir, item.name)

        try:
            # 移动文件
            dest_path = dest_dir / unique_filename
            shutil.move(str(item), str(dest_path))

            moved_files.append({
                "filename": item.name,
                "destination": category,
                "new_name": unique_filename,
                "size": item.stat().st_size
            })

            action = "保留在" if is_existing_folder else "移动到"
            print(f"✅ {item.name} → {action} {category}/")

        except Exception as e:
            errors.append(f"错误: {item.name} - {str(e)}")
            print(f"❌ 处理失败: {item.name} - {str(e)}")

    # 生成清单文件
    generate_manifest(target_path, moved_files)

    # 打印摘要
    print("\n" + "=" * 50)
    print(f"📊 整理完成！")
    print(f"   处理文件数: {len(moved_files)}")
    print(f"   错误数量: {len(errors)}")
    print(f"   清单文件: _Folder_Manifest.md")

    return moved_files, errors


def generate_manifest(target_path, moved_files):
    """生成文件夹清单文件"""
    manifest_path = target_path / "_Folder_Manifest.md"

    # 统计各文件夹文件数
    folder_stats = {}
    for category in FILE_CATEGORIES.keys():
        category_path = target_path / category
        if category_path.exists():
            files = list(category_path.iterdir())
            folder_stats[category] = len([f for f in files if f.is_file() and f.name not in IGNORE_FILES])
        else:
            folder_stats[category] = 0

    # 生成 Markdown 内容
    content = f"""# 下载文件夹文件清单

**更新时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 统计概览

| 分类 | 文件数量 |
|------|---------|
"""

    for category, count in folder_stats.items():
        content += f"| {category} | {count} |\n"

    content += "\n## 详细文件列表\n\n"

    # 遍历各分类文件夹
    for category in FILE_CATEGORIES.keys():
        category_path = target_path / category
        if category_path.exists():
            content += f"### {category}\n\n"
            content += "| 文件名 | 大小 | 修改日期 |\n"
            content += "|--------|------|----------|\n"

            for file in sorted(category_path.iterdir()):
                if file.is_file() and file.name not in IGNORE_FILES:
                    size = format_size(file.stat().st_size)
                    mtime = datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d")
                    content += f"| {file.name} | {size} | {mtime} |\n"

            content += "\n"

    # 写入文件
    with open(manifest_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 清单文件已生成: {manifest_path}")


if __name__ == "__main__":
    organize_downloads()
