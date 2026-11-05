#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NSFC 结题报告下载器 (最终优化版)
- 协议适配：严格遵循 application/x-www-form-urlencoded
- 稳健性：处理 503 重试、SSL 忽略、断点续传
- 目录结构：/tmp/nsfc_download/{id}/{api,img,info.json}
"""

import os
import sys

# 自动获取 zip 包的绝对路径
zip_path = os.path.join(os.path.dirname(__file__), "libs")

# 把 zip 包加入搜索路径
if os.path.exists(zip_path):
    sys.path.insert(0, zip_path)


import json
import re
import subprocess
import time
from pathlib import Path

import requests
import urllib3

# 1. 环境安全配置：忽略 SSL 证书错误
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NSFCReportDownloader:
    def __init__(self, target_input, base_dir="/tmp/nsfc_download"):
        # 提取 ID：兼容完整 URL 或纯 ID
        self.report_id = self._extract_id(target_input)
        self.host = "https://kd.nsfc.cn"

        # 目录结构初始化
        self.base_path = Path(base_dir) / self.report_id
        self.api_dir = self.base_path / "api"
        self.img_dir = self.base_path / "img"
        self.info_cache = self.base_path / "info.json"

        for d in [self.api_dir, self.img_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.project_name = "nsfc_report"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }

    def _extract_id(self, text):
        """从链接或字符串中提取32位ID"""
        match = re.search(r"id=([a-f0-9]{32})", text)
        if match:
            return match.group(1)
        if re.fullmatch(r"[a-f0-9]{32}", text):
            return text
        raise ValueError(f"无法识别有效的 ID: {text}")

    def safe_request(self, method, url, **kwargs):
        """核心请求逻辑：处理 503 重试与 SSL 忽略"""
        kwargs.setdefault("verify", False)
        kwargs.setdefault("timeout", 30)
        kwargs.setdefault("headers", self.headers)

        while True:
            try:
                resp = self.session.request(method, url, **kwargs)
                if resp.status_code == 503:
                    print(f"服务器繁忙 (503)，10 秒后重试...")
                    time.sleep(10)
                    continue
                resp.raise_for_status()
                return resp
            except Exception as e:
                print(f"请求失败: {e}，3 秒后重试...")
                time.sleep(3)

    def fetch_project_info(self):
        """获取并缓存项目信息"""
        if self.info_cache.exists():
            try:
                with open(self.info_cache, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.project_name = data.get("data", {}).get(
                        "projectName", "nsfc_report"
                    )
                    return data
            except:
                pass

        url = f"{self.host}/api/baseQuery/conclusionProjectInfo/{self.report_id}"
        # 注意：此处必须使用 POST 且 body 为空，匹配原 TS 代码
        resp = self.safe_request(
            "POST",
            url,
            headers={
                **self.headers,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        data = resp.json()

        with open(self.info_cache, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        self.project_name = data.get("data", {}).get("projectName", "nsfc_report")
        return data

    def download_report(self):
        """单线程下载图片与 API"""
        index = 1
        while True:
            api_file = self.api_dir / f"{index}.json"
            img_file = self.img_dir / f"{index}.png"

            # 1. 接口数据获取（缓存优先）
            if api_file.exists():
                with open(api_file, "r", encoding="utf-8") as f:
                    api_data = json.load(f)
            else:
                api_url = f"{self.host}/api/baseQuery/completeProjectReport"
                # 适配 Content-Type: application/x-www-form-urlencoded
                resp = self.safe_request(
                    "POST", api_url, data={"id": self.report_id, "index": index}
                )
                api_data = resp.json()
                with open(api_file, "w", encoding="utf-8") as f:
                    json.dump(api_data, f, ensure_ascii=False, indent=4)

            # 2. 解析图片链接
            img_url_suffix = api_data.get("data", {}).get("url")
            if not img_url_suffix:
                print(f"第 {index} 页无 URL，下载流程结束。")
                break

            # 3. 下载图片（断点续传）
            if img_file.exists() and img_file.stat().st_size > 0:
                print(f"第 {index} 页已缓存，跳过。")
            else:
                img_url = self.host + img_url_suffix
                # 404 判定文档结束
                img_resp = self.session.get(img_url, verify=False, timeout=30)
                if img_resp.status_code == 404:
                    print(f"第 {index} 页 404，判定为文档终点。")
                    break
                elif img_resp.status_code == 503:
                    time.sleep(10)
                    continue

                with open(img_file, "wb") as f:
                    f.write(img_resp.content)
                print(f"已下载第 {index} 页。")
                time.sleep(1)  # 频率限制

            index += 1

    def finalize_pdf(self):
        """使用 img2pdf 无损合成"""
        import img2pdf

        img_paths = sorted(
            [str(p) for p in self.img_dir.glob("*.png")],
            key=lambda x: int(Path(x).stem),
        )

        if not img_paths:
            print("错误：未找到图片文件。")
            return

        # 强力清洗文件名
        clean_name = re.sub(r'[\/:*?"<>|]', "_", self.project_name).strip()
        pdf_path = Path.cwd() / f"{clean_name}.pdf"

        print(f"正在合成 PDF: {clean_name}.pdf ...")
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(img_paths))

        # 标准化日志埋点
        stats = pdf_path.stat()
        print(
            f"\nPDF_GENERATION_COMPLETE: {pdf_path.name} | Total Pages: {len(img_paths)} | File Size: {stats.st_size / 1024 / 1024:.2f} MB | Path: {pdf_path.absolute()}"
        )

    def run(self):
        self.fetch_project_info()
        self.download_report()
        self.finalize_pdf()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python nsfc_downloader.py <URL_OR_ID>")
        sys.exit(1)

    # 自动安装依赖
    for lib in ["requests", "img2pdf"]:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib, "-q"])

    downloader = NSFCReportDownloader(sys.argv[1])
    downloader.run()
