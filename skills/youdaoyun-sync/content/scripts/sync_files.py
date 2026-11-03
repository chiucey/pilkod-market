#!/usr/bin/env python3
"""
有道云笔记同步脚本
支持通过 Token 或分享链接同步文件
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("请安装 requests: pip install requests")
    sys.exit(1)


@dataclass
class FileInfo:
    """文件信息数据结构"""
    id: str
    name: str
    path: str
    size: int
    modified_time: str
    is_dir: bool
    hash: Optional[str] = None


@dataclass
class SyncResult:
    """同步结果"""
    sync_time: str
    total_files: int
    downloaded: int
    skipped: int
    failed: int
    total_size: str
    changes: dict


class YoudaoSync:
    """有道云笔记同步器"""

    BASE_API = "https://note.youdao.com/yws/api/v1"
    SHARE_API = "https://note.youdao.com/yws/api/v1/share"

    def __init__(self, output_dir: str, log_level: int = logging.INFO):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.sync_state_file = self.output_dir / ".sync_state.json"
        self.setup_logging(log_level)

    def setup_logging(self, level: int):
        """设置日志"""
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(self.output_dir / "sync.log", encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_share_link(self, share_link: str) -> dict:
        """解析分享链接获取分享 ID"""
        # 支持格式: https://note.youdao.com/sharing/embed?id=xxx
        # 或: https://note.youdao.com/share/?id=xxx
        patterns = [
            r'id=([a-zA-Z0-9_-]+)',
            r'/sharing/embed\?id=([a-zA-Z0-9_-]+)',
            r'/share/\?id=([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, share_link)
            if match:
                return {"share_id": match.group(1)}

        raise ValueError(f"无法解析分享链接: {share_link}")

    def get_share_info(self, share_id: str) -> dict:
        """获取分享信息"""
        url = f"{self.SHARE_API}/{share_id}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"获取分享信息失败: {e}")
            raise

    def get_files_via_token(self, token: str) -> list:
        """通过 Token 获取文件列表"""
        self.session.headers["Authorization"] = f"Bearer {token}"
        url = f"{self.BASE_API}/files"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get("files", [])
        except requests.RequestException as e:
            self.logger.error(f"获取文件列表失败: {e}")
            raise

    def get_files_via_share(self, share_link: str) -> list:
        """通过分享链接获取文件列表"""
        parsed = self.parse_share_link(share_link)
        share_info = self.get_share_info(parsed["share_id"])

        # 获取文件列表
        url = f"{self.SHARE_API}/{parsed['share_id']}/files"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json().get("files", [])
        except requests.RequestException as e:
            self.logger.error(f"获取分享文件列表失败: {e}")
            raise

    def download_file(self, file_id: str, output_path: Path, token: str = None) -> bool:
        """下载单个文件"""
        url = f"{self.BASE_API}/file/{file_id}"

        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        for attempt in range(3):
            try:
                response = self.session.get(url, headers=headers, timeout=60, stream=True)
                response.raise_for_status()

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True

            except requests.RequestException as e:
                self.logger.warning(f"下载失败 (尝试 {attempt + 1}/3): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    self.logger.error(f"文件下载失败: {output_path}")
                    return False

    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件 MD5 哈希"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                md5.update(chunk)
        return md5.hexdigest()

    def load_sync_state(self) -> dict:
        """加载同步状态"""
        if self.sync_state_file.exists():
            try:
                with open(self.sync_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_sync_state(self, state: dict):
        """保存同步状态"""
        with open(self.sync_state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def list_files(self, source_type: str, auth: str) -> list:
        """列出所有文件"""
        if source_type == "token":
            files = self.get_files_via_token(auth)
        else:  # share
            files = self.get_files_via_share(auth)

        return [FileInfo(
            id=f.get("id", ""),
            name=f.get("name", "unknown"),
            path=f.get("path", "/"),
            size=f.get("size", 0),
            modified_time=f.get("modified", ""),
            is_dir=f.get("dir", False)
        ) for f in files]

    def sync_files(self, source_type: str, auth: str, mode: str = "full",
                   paths: list = None, exclude: str = None) -> SyncResult:
        """同步文件"""

        # 解析排除模式
        exclude_patterns = []
        if exclude:
            exclude_patterns = [p.strip() for p in exclude.split(',')]

        # 获取文件列表
        files = self.list_files(source_type, auth)
        state = self.load_sync_state()

        downloaded = 0
        skipped = 0
        failed = 0
        total_size = 0
        changes = {"added": 0, "modified": 0, "deleted": 0}

        for file_info in files:
            # 跳过目录
            if file_info.is_dir:
                continue

            # 选择性同步
            if mode == "selective" and paths:
                if file_info.path not in paths:
                    skipped += 1
                    continue

            # 检查排除模式
            skip = False
            for pattern in exclude_patterns:
                if pattern in file_info.name or re.match(pattern, file_info.name):
                    skip = True
                    break
            if skip:
                skipped += 1
                continue

            # 构建本地路径
            relative_path = file_info.path.lstrip('/')
            local_path = self.output_dir / relative_path

            # 检查是否需要下载
            should_download = True

            if mode == "incremental":
                file_key = f"{file_info.id}_{file_info.name}"
                if file_key in state:
                    old_hash = state[file_key].get("hash")
                    # 比较修改时间
                    if file_info.modified_time <= state[file_key].get("modified"):
                        should_download = False
                        skipped += 1

            if not should_download:
                continue

            # 下载文件
            if self.download_file(file_info.id, local_path, auth if source_type == "token" else None):
                downloaded += 1
                total_size += file_info.size
                file_hash = self.calculate_file_hash(local_path)

                # 更新状态
                state[f"{file_info.id}_{file_info.name}"] = {
                    "hash": file_hash,
                    "modified": file_info.modified_time,
                    "size": file_info.size,
                    "path": str(local_path)
                }

                # 判断变化类型
                file_key = f"{file_info.id}_{file_info.name}"
                if file_key not in state or file_key not in [f"{f.id}_{f.name}" for f in files]:
                    changes["added"] += 1
                else:
                    changes["modified"] += 1
            else:
                failed += 1

        # 保存同步状态
        self.save_sync_state(state)

        return SyncResult(
            sync_time=datetime.now().isoformat(),
            total_files=len(files),
            downloaded=downloaded,
            skipped=skipped,
            failed=failed,
            total_size=self._format_size(total_size),
            changes=changes
        )

    def check_updates(self, source_type: str, auth: str) -> dict:
        """检查更新"""
        files = self.list_files(source_type, auth)
        state = self.load_sync_state()

        updates = {"new": [], "modified": [], "deleted": []}

        for file_info in files:
            file_key = f"{file_info.id}_{file_info.name}"
            if file_key not in state:
                updates["new"].append(asdict(file_info))
            elif file_info.modified_time > state[file_key].get("modified", ""):
                updates["modified"].append(asdict(file_info))

        # 检查删除
        for key in state:
            found = False
            for f in files:
                if f"{f.id}_{f.name}" == key:
                    found = True
                    break
            if not found:
                updates["deleted"].append(key)

        return updates

    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}TB"


def main():
    parser = argparse.ArgumentParser(description="有道云笔记同步工具")
    parser.add_argument("--action", choices=["list", "sync", "check"], required=True,
                        help="操作: list=列出文件, sync=同步文件, check=检查更新")
    parser.add_argument("--source", choices=["token", "share"], required=True,
                        help="认证来源: token=Token, share=分享链接")
    parser.add_argument("--auth", required=True, help="认证信息 (Token 或分享链接)")
    parser.add_argument("--mode", choices=["full", "selective", "incremental"], default="full",
                        help="同步模式")
    parser.add_argument("--paths", help="选择性同步的路径 (逗号分隔)")
    parser.add_argument("--output", default="./youdaoyun", help="输出目录")
    parser.add_argument("--exclude", help="排除的文件模式 (如 *.tmp,*.log)")
    parser.add_argument("--log-file", help="日志文件路径")

    args = parser.parse_args()

    # 创建同步器
    sync = YoudaoSync(args.output)

    try:
        if args.action == "list":
            files = sync.list_files(args.source, args.auth)
            print("\n📁 文件列表:")
            print("-" * 60)
            for f in files:
                icon = "📁" if f.is_dir else "📄"
                size_str = "" if f.is_dir else f" ({sync._format_size(f.size)})"
                print(f"{icon} {f.path}/{f.name}{size_str}")
            print("-" * 60)
            print(f"总计: {len(files)} 个项目")

        elif args.action == "sync":
            paths = args.paths.split(',') if args.paths else None
            result = sync.sync_files(
                args.source, args.auth, args.mode, paths, args.exclude
            )
            print("\n✅ 同步完成!")
            print("-" * 40)
            print(f"📊 同步统计:")
            print(f"   - 总文件数: {result.total_files}")
            print(f"   - 已下载: {result.downloaded}")
            print(f"   - 跳过: {result.skipped}")
            print(f"   - 失败: {result.failed}")
            print(f"   - 总大小: {result.total_size}")
            if result.changes:
                print(f"\n📝 变更:")
                print(f"   - 新增: {result.changes.get('added', 0)}")
                print(f"   - 修改: {result.changes.get('modified', 0)}")
                print(f"   - 删除: {result.changes.get('deleted', 0)}")
            print("-" * 40)
            print(f"📁 输出目录: {args.output}")

        elif args.action == "check":
            updates = sync.check_updates(args.source, args.auth)
            print("\n🔍 更新检查结果:")
            print("-" * 40)
            print(f"🆕 新增: {len(updates['new'])}")
            print(f"✏️ 修改: {len(updates['modified'])}")
            print(f"🗑️ 删除: {len(updates['deleted'])}")

            if updates['new']:
                print("\n新增文件:")
                for f in updates['new'][:5]:
                    print(f"   - {f['name']}")
                if len(updates['new']) > 5:
                    print(f"   ... 还有 {len(updates['new']) - 5} 个")

        sys.exit(0 if result.failed == 0 else 5)

    except Exception as e:
        sync.logger.error(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
