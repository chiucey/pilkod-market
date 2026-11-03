#!/usr/bin/env python3
"""
MinerU Extractor — 通过 MinerU Online API 提取 PDF/文档文件文本内容

用法：
  python mineru_extractor.py check-config                          # 检测配置是否正确
  python mineru_extractor.py extract <URL>                         # 解析在线文件（默认）
  python mineru_extractor.py extract <本地文件> --source local     # 解析本地文件
  python mineru_extractor.py extract <源> --output result.txt      # 结果保存到文件
  python mineru_extractor.py --config D:/my/config.json extract <源>  # 指定配置路径
"""

import os
import re
import sys
import json
import time
import zipfile
import tempfile
import argparse
import requests
from pathlib import Path


# ══════════════════════════════════════════════════════════════
#  配置相关
# ══════════════════════════════════════════════════════════════

class ConfigError(Exception):
    """配置文件缺失或未正确填写时抛出。"""
    pass


_PLACEHOLDER_PATTERNS = [
    r"^your[-_]",
    r"^<.*>$",
    r"^x{6,}",
    r"^token[-_]?here",
    r"^test[-_]?token",
    r"^(none|null|undefined|todo)$",
]

def _is_placeholder(value: str) -> bool:
    v = value.strip().lower()
    return any(re.match(p, v) for p in _PLACEHOLDER_PATTERNS)


def validate_config(config_path: str = "config.json") -> dict:
    """
    检测 config.json 是否存在且已正确填写。
    通过返回配置字典，失败抛出 ConfigError。
    """
    path = Path(config_path)

    # ── 1. 文件是否存在 ──────────────────────────────────────
    if not path.exists():
        raise ConfigError(
            f"\n❌ 找不到配置文件：{path.resolve()}\n\n"
            "📋 请按以下步骤配置：\n"
            "  1. 将 config.json.template 复制并重命名为 config.json\n"
            "  2. 用文本编辑器打开 config.json\n"
            "  3. 填入您的真实参数后保存\n\n"
            "配置文件格式：\n"
            "  {\n"
            '    "MINERU_TOKEN": "你的真实 Token",\n'
            '    "MINERU_BASE_URL": "https://mineru.net/api/v4"\n'
            "  }\n\n"
            "🔑 MinerU Token 获取地址：https://mineru.net"
        )

    # ── 2. JSON 格式 ─────────────────────────────────────────
    try:
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"\n❌ config.json 格式错误：{e}\n\n"
            "请确保 JSON 语法正确，所有字符串用双引号包裹。"
        )

    # ── 3. 必填字段检测 ──────────────────────────────────────
    issues = []

    token = config.get("MINERU_TOKEN", "").strip()
    if not token:
        issues.append("  • MINERU_TOKEN：未填写")
    elif _is_placeholder(token):
        issues.append(f"  • MINERU_TOKEN：仍为占位值 ({token!r})，请替换为真实 Token")

    if not config.get("MINERU_BASE_URL", "").strip():
        issues.append("  • MINERU_BASE_URL：未填写")

    if issues:
        raise ConfigError(
            "\n❌ config.json 存在以下配置问题：\n\n"
            + "\n".join(issues)
            + "\n\n请打开 config.json 修正后重新运行。\n"
            "🔑 MinerU Token 获取地址：https://mineru.net"
        )

    return config


def load_config(config_path: str = "config.json") -> dict:
    """validate_config 的别名，兼容旧代码。"""
    return validate_config(config_path)


# ══════════════════════════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════════════════════════

def clean_text(text: str) -> str:
    """清洗提取文本：统一换行、去除多余空白。"""
    if text is None:
        return ""
    text = str(text)
    text = text.replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"\n+", "\n", text)
    text = re.sub(r"[ \xa0]+", " ", text)
    return text.strip()


# ══════════════════════════════════════════════════════════════
#  核心类
# ══════════════════════════════════════════════════════════════

class MineruOnlineExtractor:
    """
    使用 MinerU Online API 提取文档文本内容。

    推荐用法：
        config = validate_config("config.json")
        extractor = MineruOnlineExtractor(config)

        # 解析在线 URL
        text = extractor.extract_file("https://example.com/notice.pdf", source_method="online")

        # 解析本地文件
        text = extractor.extract_file("/path/to/file.pdf", source_method="local")

        if text:
            print(text)
        else:
            print("提取失败")
    """

    def __init__(self, config: dict, poll_attempts: int = 60, poll_interval: int = 5):
        """
        参数:
            config         (dict): validate_config() 返回的配置字典
            poll_attempts  (int) : 轮询最大次数，默认 60
            poll_interval  (int) : 轮询间隔秒数，默认 5（最多等待约 5 分钟）
        """
        self.token = config["MINERU_TOKEN"]
        self.base_url = config["MINERU_BASE_URL"].rstrip("/")
        self.poll_attempts = poll_attempts
        self.poll_interval = poll_interval
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    # ── 内部：下载 zip 并读取 full.md ────────────────────────

    def _download_and_read_full_md(self, zip_url: str) -> str:
        """下载结果 zip 包，提取其中的 full.md 并返回清洗后的文本。"""
        if not zip_url:
            return ""
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "result.zip")
            resp = requests.get(zip_url, timeout=60)
            resp.raise_for_status()
            with open(zip_path, "wb") as fh:
                fh.write(resp.content)

            extract_dir = os.path.join(tmpdir, "extracted")
            with zipfile.ZipFile(zip_path, "r") as zh:
                zh.extractall(extract_dir)

            full_md_path = None
            for root, _, files in os.walk(extract_dir):
                if "full.md" in files:
                    full_md_path = os.path.join(root, "full.md")
                    break

            if not full_md_path:
                raise Exception("zip 包中未找到 full.md")

            with open(full_md_path, "r", encoding="utf-8") as fh:
                return clean_text(fh.read())

    # ── 在线 URL 解析 ─────────────────────────────────────────

    def extract_from_online(self, file_path: str) -> str:
        """
        提交在线 URL 到 MinerU 解析任务，轮询完成后返回文本。

        参数:
            file_path (str): 在线文件 URL

        返回:
            str: 清洗后的 Markdown 文本，失败返回空字符串
        """
        if not file_path or not isinstance(file_path, str):
            raise Exception("file_path 为空或格式非法")

        payload = {
            "url": file_path,
            "enable_formula": True,
            "language": "ch",
            "enable_table": True,
            "layout_model": "doclayout_yolo",
        }
        res = requests.post(
            f"{self.base_url}/extract/task",
            json=payload,
            headers=self.headers,
            timeout=60,
        )
        res.raise_for_status()
        data = res.json()
        if data.get("code") != 0:
            raise Exception(f"提交任务失败: {data}")

        task_id = data.get("data", {}).get("task_id")
        if not task_id:
            raise Exception("提交任务后未获取到 task_id")

        # 轮询任务状态
        zip_url = ""
        for attempt in range(self.poll_attempts):
            time.sleep(self.poll_interval)
            poll_res = requests.get(
                f"{self.base_url}/extract/task/{task_id}",
                headers=self.headers,
                timeout=30,
            )
            poll_res.raise_for_status()
            poll_data = poll_res.json()
            if poll_data.get("code") != 0:
                continue
            state = poll_data.get("data", {}).get("state", "")
            if state == "done":
                zip_url = poll_data.get("data", {}).get("full_zip_url", "")
                break
            if state == "failed":
                err = poll_data.get("data", {}).get("err_msg", "未知失败")
                print(f"⚠️  在线解析失败: {err}")
                return ""

        if not zip_url:
            print(f"⚠️  轮询超时（{self.poll_attempts} 次），未获取到结果: {file_path}")
            return ""

        return self._download_and_read_full_md(zip_url)

    # ── 本地文件解析 ──────────────────────────────────────────

    def extract_from_local(self, file_path: str) -> str:
        """
        上传本地 PDF 到 MinerU，轮询完成后返回文本。

        参数:
            file_path (str): 本地文件路径

        返回:
            str: 清洗后的 Markdown 文本，失败返回空字符串
        """
        if not file_path or not os.path.exists(file_path):
            raise Exception(f"本地文件不存在: {file_path}")

        file_name = os.path.basename(file_path)

        # 申请上传 URL
        payload = {
            "enable_formula": True,
            "language": "ch",
            "enable_table": True,
            "layout_model": "doclayout_yolo",
            "enable_ocr": True,
            "files": [{"name": file_name, "is_ocr": True}],
        }
        apply_res = requests.post(
            f"{self.base_url}/file-urls/batch",
            json=payload,
            headers=self.headers,
            timeout=30,
        )
        apply_res.raise_for_status()
        apply_data = apply_res.json()
        if apply_data.get("code") != 0:
            raise Exception(f"申请上传 URL 失败: {apply_data}")

        data = apply_data.get("data", {})
        batch_id = data.get("batch_id")
        file_urls = data.get("file_urls", [])
        upload_url = file_urls[0] if file_urls else ""
        if not batch_id or not upload_url:
            raise Exception("申请上传 URL 成功但未获取到 batch_id 或 upload_url")

        # 上传文件
        with open(file_path, "rb") as fh:
            put_res = requests.put(upload_url, data=fh, timeout=120)
            put_res.raise_for_status()

        # 轮询解析结果
        zip_url = ""
        for attempt in range(self.poll_attempts):
            time.sleep(self.poll_interval)
            poll_res = requests.get(
                f"{self.base_url}/extract-results/batch/{batch_id}",
                headers=self.headers,
                timeout=30,
            )
            poll_res.raise_for_status()
            poll_data = poll_res.json()
            if poll_data.get("code") != 0:
                continue

            extract_result = poll_data.get("data", {}).get("extract_result", [])
            if not extract_result:
                continue

            state = extract_result[0].get("state", "")
            if state == "done":
                zip_url = extract_result[0].get("full_zip_url", "")
                break
            if state == "failed":
                err = extract_result[0].get("err_msg", "未知失败")
                print(f"⚠️  本地解析失败: {err}")
                return ""

        if not zip_url:
            print(f"⚠️  轮询超时（{self.poll_attempts} 次），未获取到结果: {file_path}")
            return ""

        return self._download_and_read_full_md(zip_url)

    # ── 统一入口 ──────────────────────────────────────────────

    def extract_file(self, file_path: str, source_method: str = "online") -> str:
        """
        统一入口：根据 source_method 选择在线或本地解析。

        参数:
            file_path     (str): 文件路径或在线 URL
            source_method (str): 'online'（默认）或 'local'

        返回:
            str: 清洗后的文本，失败返回空字符串
        """
        if source_method == "online":
            return self.extract_from_online(file_path)
        elif source_method == "local":
            return self.extract_from_local(file_path)
        else:
            raise Exception(
                f"参数错误：source_method 必须为 'online' 或 'local'，当前为 '{source_method}'"
            )


# ══════════════════════════════════════════════════════════════
#  CLI 命令实现
# ══════════════════════════════════════════════════════════════

def cmd_check_config(args):
    """check-config 子命令：检测配置是否正确填写。"""
    try:
        config = validate_config(args.config)
        token = config["MINERU_TOKEN"]
        masked = "*" * 8 + token[-6:] if len(token) > 6 else "******"
        print("✅ 配置检测通过！")
        print(f"   MINERU_TOKEN   : {masked}")
        print(f"   MINERU_BASE_URL: {config['MINERU_BASE_URL']}")
    except ConfigError as e:
        print(e)
        sys.exit(1)


def cmd_extract(args):
    """extract 子命令：解析在线 URL 或本地文件。"""
    # ── 配置检测 ─────────────────────────────────────────────
    try:
        config = validate_config(args.config)
    except ConfigError as e:
        print(e)
        sys.exit(1)

    source = args.source
    is_url = source.startswith("http://") or source.startswith("https://")

    # 自动推断 source_method（用户未显式指定时）
    source_method = args.source_method
    if source_method is None:
        source_method = "online" if is_url else "local"

    # 本地文件：检查是否存在
    if source_method == "local" and not Path(source).exists():
        print(f"❌ 找不到文件：{Path(source).resolve()}")
        sys.exit(1)

    extractor = MineruOnlineExtractor(config)

    if source_method == "online":
        print(f"🌐 正在提交在线解析任务：{source}")
        print(f"   （最多等待约 {extractor.poll_attempts * extractor.poll_interval // 60} 分钟，请稍候...）")
    else:
        print(f"📄 正在上传并解析本地文件：{Path(source).resolve()}")
        print(f"   （最多等待约 {extractor.poll_attempts * extractor.poll_interval // 60} 分钟，请稍候...）")

    text = extractor.extract_file(source, source_method=source_method)

    # ── 处理结果 ──────────────────────────────────────────────
    if not text:
        print("\n❌ 提取失败或结果为空")
        sys.exit(1)

    char_count = len(text)
    print(f"✅ 提取成功，共 {char_count} 个字符\n")

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"💾 结果已保存至：{out_path.resolve()}")
    else:
        if char_count > 2000 and not args.full:
            print(text[:2000])
            print(f"\n... （内容过长，仅显示前 2000 字符，共 {char_count} 字符）")
            print("提示：使用 --output <文件名> 保存完整内容，或 --full 显示全部。")
        else:
            print(text)


# ══════════════════════════════════════════════════════════════
#  CLI 入口
# ══════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mineru_extractor",
        description="MinerU Extractor — 使用 MinerU Online API 提取 PDF/文档文件文本内容",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python mineru_extractor.py check-config
  python mineru_extractor.py check-config --config D:/project/config.json

  python mineru_extractor.py extract https://example.com/notice.pdf
  python mineru_extractor.py extract https://example.com/notice.pdf --output result.txt

  python mineru_extractor.py extract 公告.pdf --source local
  python mineru_extractor.py extract 公告.pdf --source local --output result.txt

  python mineru_extractor.py --config D:/project/config.json extract 公告.pdf --source local
        """,
    )

    parser.add_argument(
        "--config", default="config.json", metavar="路径",
        help="config.json 路径（默认：当前目录下的 config.json）",
    )

    subparsers = parser.add_subparsers(dest="command", metavar="命令")
    subparsers.required = True

    # ── check-config ──────────────────────────────────────────
    subparsers.add_parser(
        "check-config",
        help="检测 config.json 是否存在且已正确填写",
    )

    # ── extract ───────────────────────────────────────────────
    p_extract = subparsers.add_parser(
        "extract",
        help="提取在线 URL 或本地文件的文本内容",
    )
    p_extract.add_argument(
        "source", metavar="文件路径或URL",
        help="本地文件路径 或 https:// 开头的在线链接",
    )
    p_extract.add_argument(
        "--source-method", "--source", dest="source_method",
        choices=["online", "local"], default=None, metavar="online|local",
        help="解析方式：online（在线URL）或 local（本地文件）。不指定时根据输入自动判断",
    )
    p_extract.add_argument(
        "--output", "-o", metavar="路径",
        help="将提取结果保存到指定文件（不指定则打印到终端）",
    )
    p_extract.add_argument(
        "--full", action="store_true",
        help="终端输出时显示完整内容（默认超过 2000 字符时截断预览）",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "check-config":
        cmd_check_config(args)
    elif args.command == "extract":
        cmd_extract(args)


if __name__ == "__main__":
    main()