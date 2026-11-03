"""
Heywhale Dataset Assistant - Interactive dataset discovery and download tool
Requires: Python 3.9+, playwright, requests, chardet
Usage: python main.py
"""

import asyncio
import os
import re
import sys
import subprocess
import shutil
import requests
import chardet
from playwright.async_api import async_playwright


HEYWHALE_API = "https://www.heywhale.com/api/datasets"
HEYWHALE_AUTH = "https://www.heywhale.com/api/auth/login"


def detect_python():
    candidates = []
    if sys.platform == "win32":
        for ver in ["314", "313", "312", "311"]:
            candidates.append(
                os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", f"Python{ver}", "python.exe")
            )
        candidates.extend([r"C:\Python314\python.exe", r"C:\Python313\python.exe"])
        for p in os.environ.get("PATH", "").split(os.pathsep):
            for name in ["python.exe", "python3.exe"]:
                exe = os.path.join(p, name)
                if os.path.isfile(exe) and exe not in candidates:
                    candidates.append(exe)
    else:
        for name in ["python3", "python"]:
            path = shutil.which(name)
            if path and path not in candidates:
                candidates.append(path)
    for py_path in candidates:
        try:
            result = subprocess.run(
                [py_path, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                return {"path": py_path, "version": version}
        except Exception:
            continue
    return None


def detect_nodejs():
    candidates = []
    if sys.platform == "win32":
        common_paths = [
            r"D:\dev\nodejs\node.exe",
            os.path.join(os.environ.get("ProgramFiles", ""), "nodejs", "node.exe"),
            os.path.join(os.environ.get("ProgramFiles(x86)", ""), "nodejs", "node.exe"),
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "nodejs", "node.exe"),
        ]
        for p in os.environ.get("PATH", "").split(os.pathsep):
            node_exe = os.path.join(p, "node.exe")
            if os.path.isfile(node_exe) and node_exe not in candidates:
                candidates.append(node_exe)
    else:
        node_path = shutil.which("node")
        if node_path:
            candidates.append(node_path)
    for node_path in candidates:
        try:
            result = subprocess.run(
                [node_path, "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return {"path": node_path, "version": result.stdout.strip()}
        except Exception:
            continue
    return None


def auto_install_python():
    print("\n  Downloading Python 3.14.3 installer...")
    installer_url = "https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe"
    installer_path = os.path.join(os.environ.get("TEMP", "."), "python_installer.exe")
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"Invoke-WebRequest -Uri '{installer_url}' -OutFile '{installer_path}'"],
            timeout=300, check=True
        )
        print("  Installing Python (silent mode with PATH)...")
        subprocess.run(
            [installer_path, "/quiet", "InstallAllUsers=1", "PrependPath=1", "Include_pip=1"],
            timeout=600, check=True
        )
        print("  Python installed successfully!")
        return True
    except Exception as e:
        print(f"  Auto-install failed: {e}")
        print("  Please install manually from https://www.python.org/downloads/")
        return False


def auto_install_nodejs():
    print("\n  Downloading Node.js 24.15.0 LTS installer...")
    installer_url = "https://nodejs.org/dist/v24.15.0/node-v24.15.0-x64.msi"
    installer_path = os.path.join(os.environ.get("TEMP", "."), "node_installer.msi")
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"Invoke-WebRequest -Uri '{installer_url}' -OutFile '{installer_path}'"],
            timeout=300, check=True
        )
        print("  Installing Node.js (silent mode)...")
        subprocess.run(
            ["msiexec", "/i", installer_path, "/quiet", "/norestart"],
            timeout=600, check=True
        )
        print("  Node.js installed successfully!")
        return True
    except Exception as e:
        print(f"  Auto-install failed: {e}")
        print("  Please install manually from https://nodejs.org/")
        return False


def check_environment():
    print("=" * 60)
    print("Environment Check")
    print("=" * 60)
    print(f"  OS: {sys.platform}")

    python_info = detect_python()
    if python_info:
        print(f"  Python: {python_info['version']} ({python_info['path']})")
    else:
        print("  Python: Not found")
        print("\n  Python 未检测到。请选择：")
        print("    A) 自动安装 Python 3.14.3（推荐）")
        print("    B) 手动安装（将打开 https://www.python.org/downloads/ ）")
        print("    C) 配置已安装的 Python 路径")
        choice = input("  选择 (A/B/C): ").strip().upper()
        if choice == "A":
            if auto_install_python():
                python_info = detect_python()
        elif choice == "B":
            print("  请访问 https://www.python.org/downloads/ 下载安装")
            print("  安装时务必勾选 'Add Python to PATH'")
            input("  安装完成后按回车继续...")
            python_info = detect_python()
        elif choice == "C":
            custom_path = input("  请输入 Python 可执行文件路径: ").strip()
            if os.path.isfile(custom_path):
                try:
                    result = subprocess.run(
                        [custom_path, "--version"], capture_output=True, text=True, timeout=5
                    )
                    if result.returncode == 0:
                        python_info = {"path": custom_path, "version": result.stdout.strip().split()[-1]}
                        print(f"  Python: {python_info['version']} ({python_info['path']})")
                except Exception:
                    print("  Invalid Python path")
            else:
                print(f"  File not found: {custom_path}")

    if not python_info:
        print("  ERROR: Python is required. Exiting.")
        sys.exit(1)

    node_info = detect_nodejs()
    if node_info:
        print(f"  Node.js: {node_info['version']} ({node_info['path']})")
    else:
        print("  Node.js: Not found")
        print("\n  Node.js 未检测到。请选择：")
        print("    A) 自动安装 Node.js 24.15.0 LTS（推荐）")
        print("    B) 手动安装（将打开 https://nodejs.org/ ）")
        print("    C) 配置已安装的 Node.js 路径")
        print("    D) 跳过（仅使用 Python）")
        choice = input("  选择 (A/B/C/D): ").strip().upper()
        if choice == "A":
            auto_install_nodejs()
        elif choice == "B":
            print("  请访问 https://nodejs.org/ 下载安装")
            input("  安装完成后按回车继续...")
        elif choice == "C":
            custom_path = input("  请输入 Node.js 可执行文件路径: ").strip()
            if os.path.isfile(custom_path):
                print(f"  Node.js configured: {custom_path}")
            else:
                print(f"  File not found: {custom_path}")
        elif choice == "D":
            print("  Skipping Node.js (Python-only mode)")

    try:
        import playwright
        print(f"  Playwright: {playwright.__version__}")
    except ImportError:
        print("  Playwright: NOT INSTALLED")
        choice = input("  Install now? (y/n): ").strip().lower()
        if choice == "y":
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)

    try:
        import requests as r
        print(f"  Requests: {r.__version__}")
    except ImportError:
        print("  Requests: NOT INSTALLED")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)

    try:
        import chardet as c
        print(f"  Chardet: {c.__version__}")
    except ImportError:
        print("  Chardet: NOT INSTALLED")
        subprocess.run([sys.executable, "-m", "pip", "install", "chardet"], check=True)

    print()


def search_datasets(keyword, page=1, page_size=20):
    url = f"{HEYWHALE_API}?search={keyword}&page={page}&pageSize={page_size}"
    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", data.get("results", []))
    except Exception as e:
        print(f"  Search error: {e}")
    return []


def get_dataset_detail(ds_id, session=None):
    s = session or requests.Session()
    try:
        resp = s.get(f"{HEYWHALE_API}/{ds_id}", timeout=15)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def ensure_utf8(file_path):
    with open(file_path, "rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    encoding = result.get("encoding", "utf-8")
    if encoding and encoding.lower() not in ("utf-8", "ascii"):
        text = raw.decode(encoding, errors="replace")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)
        return True
    return False


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f}MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f}GB"


async def heywhale_download(datasets, email, password, base_dir):
    session = requests.Session()
    resp = session.post(HEYWHALE_AUTH, json={
        "email": email, "password": password
    }, timeout=15)
    if resp.json().get("code") != 0:
        print("Login failed!")
        return False
    print("Login successful!")
    api_cookies = dict(session.cookies)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        await context.add_cookies([
            {"name": k, "value": v, "domain": ".heywhale.com", "path": "/"}
            for k, v in api_cookies.items()
        ])
        page = await context.new_page()
        await page.goto("https://www.heywhale.com/", wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)

        remaining_quota = None
        if datasets:
            first_ds = datasets[0]
            probe_url = f"https://www.heywhale.com/home/dataset/{first_ds['id']}"
            try:
                print("\nDetecting download quota...")
                await page.goto(probe_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(8)
                download_btn = page.locator("button.ivu-btn-icon-only:has(.icon-download)")
                if await download_btn.count() > 0:
                    await download_btn.first.click()
                    await asyncio.sleep(3)
                    quota_text = await page.evaluate("""() => {
                        let modals = document.querySelectorAll('.dataset-download-confirm-modal');
                        for (let m of modals) {
                            let title = m.querySelector('.confirm-title');
                            if (title) return title.textContent;
                        }
                        return '';
                    }""")
                    if quota_text:
                        match = re.search(r'还剩\s*(\d+)', quota_text)
                        if match:
                            remaining_quota = int(match.group(1))
                            print(f"  Detected quota: {remaining_quota} remaining today")
                        else:
                            print(f"  Could not parse quota from: {quota_text[:50]}")
                    else:
                        print("  No confirmation modal appeared (may be free dataset)")
                    for sel in ['.dataset-download-confirm-modal .ivu-modal-close',
                                '.dataset-download-modal .ivu-modal-close']:
                        try:
                            close = page.locator(sel).first
                            if await close.is_visible():
                                await close.click()
                                await asyncio.sleep(1)
                        except Exception:
                            pass
            except Exception as e:
                print(f"  Quota detection error: {e}")

        if remaining_quota is None:
            print("  WARNING: Could not detect quota. Defaulting to conservative estimate (3).")
            remaining_quota = 3

        print(f"\n  Your daily download quota: {remaining_quota}")
        total_csvs = sum(len(ds.get("expected_csvs", [])) or 1 for ds in datasets)
        print(f"  Datasets to download: {len(datasets)} (est. {total_csvs} files)")
        if total_csvs > remaining_quota:
            print(f"  WARNING: You need {total_csvs} downloads but only have {remaining_quota} quota!")
            print(f"  Will download as many as possible, then suggest continuing tomorrow.")

        quota_used = 0
        for i, ds in enumerate(datasets, 1):
            ds_id = ds["id"]
            save_dir = os.path.join(base_dir, ds.get("case_dir", ds_id))
            os.makedirs(save_dir, exist_ok=True)

            expected = ds.get("expected_csvs", [])
            csv_exists = all(
                os.path.exists(os.path.join(save_dir, f)) and os.path.getsize(os.path.join(save_dir, f)) > 100
                for f in expected
            )
            if csv_exists:
                print(f"\n[{i}/{len(datasets)}] {ds['title']} - SKIP (exists)")
                continue

            if quota_used >= remaining_quota:
                print(f"\n  QUOTA EXCEEDED: {quota_used}/{remaining_quota} used.")
                print(f"  Remaining {len(datasets) - i + 1} datasets need to be downloaded tomorrow.")
                break

            print(f"\n[{i}/{len(datasets)}] {ds['title']} (quota: {quota_used}/{remaining_quota})")
            url = f"https://www.heywhale.com/home/dataset/{ds_id}"
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except Exception:
                print(f"  Page timeout, skipping")
                continue
            await asyncio.sleep(10)

            download_btn = page.locator("button.ivu-btn-icon-only:has(.icon-download)")
            if await download_btn.count() == 0:
                print(f"  No download button found")
                continue
            await download_btn.first.click()
            await asyncio.sleep(3)

            is_free_ds = False
            confirm_visible = await page.evaluate("""() => {
                let modals = document.querySelectorAll('.dataset-download-confirm-modal .ivu-modal-wrap');
                for (let m of modals) {
                    if (!m.classList.contains('ivu-modal-hidden') && getComputedStyle(m).display !== 'none')
                        return true;
                }
                return false;
            }""")
            if confirm_visible:
                quota_text = await page.evaluate("""() => {
                    let modals = document.querySelectorAll('.dataset-download-confirm-modal');
                    for (let m of modals) {
                        let title = m.querySelector('.confirm-title');
                        if (title) return title.textContent;
                    }
                    return '';
                }""")
                if quota_text:
                    match = re.search(r'还剩\s*(\d+)', quota_text)
                    if match:
                        remaining_quota = int(match.group(1))

                await page.evaluate("""() => {
                    let modals = document.querySelectorAll('.dataset-download-confirm-modal .ivu-modal-wrap');
                    for (let m of modals) {
                        if (!m.classList.contains('ivu-modal-hidden')) {
                            let btn = m.querySelector('.ivu-btn-primary');
                            if (btn) btn.click();
                        }
                    }
                }""")
                await asyncio.sleep(5)

            is_free_ds = '不消耗' in (await page.evaluate("""() => {
                let modals = document.querySelectorAll('.dataset-download-modal');
                for (let m of modals) {
                    let wrap = m.querySelector('.ivu-modal-wrap');
                    if (wrap && !wrap.classList.contains('ivu-modal-hidden') && getComputedStyle(wrap).display !== 'none')
                        return m.textContent;
                }
                return '';
            }""") or "")

            signed_urls = await page.evaluate("""() => {
                let results = [];
                let modals = document.querySelectorAll('.dataset-download-modal .ivu-modal-wrap');
                for (let m of modals) {
                    if (!m.classList.contains('ivu-modal-hidden') && getComputedStyle(m).display !== 'none') {
                        let links = m.querySelectorAll('a[href*="myqcloud.com"]');
                        links.forEach(a => {
                            let href = a.getAttribute('href');
                            let match = href.match(/filename[^&]*=([^&]+)/);
                            let filename = match ? decodeURIComponent(match[1]) : '';
                            if (!filename) {
                                let pm = href.match(/\\/([^?/]+\\.csv)\\?/);
                                if (pm) filename = decodeURIComponent(pm[1]);
                            }
                            results.push({url: href, filename: filename});
                        });
                        break;
                    }
                }
                return results;
            }""")

            close_btn = page.locator(".dataset-download-modal .ivu-modal-close")
            if await close_btn.count() > 0:
                try:
                    await close_btn.first.click()
                except Exception:
                    pass
            await asyncio.sleep(1)

            csv_count = sum(1 for su in signed_urls if su["filename"].endswith(".csv"))
            for su in signed_urls:
                if not su["filename"].endswith(".csv"):
                    continue
                save_path = os.path.join(save_dir, su["filename"])
                try:
                    r = requests.get(su["url"], timeout=120, stream=True)
                    if r.status_code == 200 and int(r.headers.get("Content-Length", 0)) > 100:
                        with open(save_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                        converted = ensure_utf8(save_path)
                        size = os.path.getsize(save_path)
                        enc_note = " (converted to UTF-8)" if converted else ""
                        print(f"  {su['filename']}: OK ({format_size(size)}){enc_note}")
                    else:
                        print(f"  {su['filename']}: FAIL HTTP {r.status_code}")
                except Exception as e:
                    print(f"  {su['filename']}: ERR {e}")

            if not is_free_ds and csv_count > 0:
                quota_used += csv_count
                print(f"  Quota: {quota_used}/{remaining_quota} used")
            elif is_free_ds:
                print(f"  FREE dataset (no quota consumed)")

        print("\nClosing browser...")
        await asyncio.sleep(3)
        await browser.close()

    return True


def interactive_mode():
    check_environment()

    print("=" * 60)
    print("Heywhale Dataset Assistant - Interactive Mode")
    print("=" * 60)

    print("\nStep 1: What type of ML task?")
    print("  1. Regression")
    print("  2. Classification")
    print("  3. Clustering")
    print("  4. NLP")
    print("  5. Time Series")
    print("  6. Association Rules")
    print("  7. Other")
    task_type = input("  Select (1-7): ").strip()

    task_keywords = {
        "1": "回归 预测",
        "2": "分类 预测",
        "3": "聚类 无监督",
        "4": "文本 NLP 自然语言",
        "5": "时间序列 预测",
        "6": "关联规则 购物篮",
        "7": "",
    }
    keyword = task_keywords.get(task_type, "")

    print("\nStep 2: What domain?")
    print("  1. Healthcare")
    print("  2. Finance")
    print("  3. E-commerce")
    print("  4. Education")
    print("  5. Sports")
    print("  6. Food")
    print("  7. Other")
    domain = input("  Select (1-7): ").strip()

    domain_keywords = {
        "1": "医疗 健康 糖尿病 心脏",
        "2": "金融 贷款 信用卡",
        "3": "电商 消费 用户",
        "4": "教育 学生 考试",
        "5": "体育 奥运 运动",
        "6": "餐饮 美食 茶饮",
        "7": "",
    }
    domain_kw = domain_keywords.get(domain, "")

    search_kw = f"{keyword} {domain_kw}".strip()
    if not search_kw:
        search_kw = input("  Enter search keywords: ").strip()
    if not search_kw:
        search_kw = "机器学习 数据集"

    print(f"\nStep 3: Searching Heywhale for '{search_kw}'...")
    results = search_datasets(search_kw)

    if not results:
        print("  No datasets found. Try different keywords.")
        return

    print(f"\n  Found {len(results)} datasets:\n")
    for i, ds in enumerate(results, 1):
        title = ds.get("Title", ds.get("title", "Unknown"))
        desc = ds.get("Description", ds.get("description", ""))[:80]
        downloads = ds.get("DownloadCount", ds.get("downloadCount", 0))
        likes = ds.get("LikeCount", ds.get("likeCount", 0))
        ds_id = ds.get("_id", ds.get("id", ""))
        print(f"  [{i}] {title}")
        print(f"      ID: {ds_id}")
        print(f"      {desc}...")
        print(f"      Downloads: {downloads} | Likes: {likes}")
        print()

    print("Step 4: Heywhale Account")
    print("  您是否已有和鲸数据账号？")
    print("  1. Yes (已有账号)")
    print("  2. No (没有账号，需要注册)")
    has_account = input("  选择 (1/2): ").strip()

    if has_account == "1":
        email = input("  Email: ").strip()
        password = input("  Password: ").strip()
    else:
        print("\n  和鲸数据注册引导：")
        print("  " + "─" * 50)
        print("  方式一：微信扫码注册（推荐，更快捷）")
        print("    1. 打开微信，搜索公众号「和鲸社区」并关注")
        print("    2. 在公众号菜单中点击「登录/注册」")
        print("    3. 扫描二维码完成注册")
        print("    4. 注册后在网页端绑定邮箱（设置→账号安全→绑定邮箱）")
        print()
        print("  方式二：邮箱注册")
        print("    1. 访问 https://www.heywhale.com/auth/register")
        print("    2. 填写：邮箱地址、用户名(2-20字符)、密码(8位+字母数字)")
        print("    3. 勾选同意《用户协议》和《隐私保护指引》")
        print("    4. 点击注册 → 查收验证邮件 → 点击验证链接")
        print("  " + "─" * 50)
        print()
        print("  注册完成后请输入登录信息：")
        email = input("  Email: ").strip()
        password = input("  Password: ").strip()

    if not email or not password:
        print("  Credentials required. Exiting.")
        return

    print("\nStep 5: Save directory")
    base_dir = input(f"  Directory (default: ./datasets): ").strip() or "./datasets"

    print("\nStep 6: Select datasets to download")
    print("  Enter numbers (e.g., 1,3,5) or 'all': ")
    selection = input("  Selection: ").strip()

    if selection.lower() == "all":
        selected = list(range(len(results)))
    else:
        try:
            selected = [int(x.strip()) - 1 for x in selection.split(",") if x.strip().isdigit()]
        except Exception:
            print("  Invalid selection. Exiting.")
            return

    datasets_to_download = []
    for idx in selected:
        if 0 <= idx < len(results):
            ds = results[idx]
            ds_id = ds.get("_id", ds.get("id", ""))
            title = ds.get("Title", ds.get("title", "Unknown"))
            datasets_to_download.append({
                "id": ds_id,
                "title": title,
                "case_dir": title.replace(" ", "_")[:50],
            })

    if not datasets_to_download:
        print("  No datasets selected. Exiting.")
        return

    print(f"\n  Will download {len(datasets_to_download)} datasets:")
    for ds in datasets_to_download:
        print(f"    - {ds['title']}")

    print("\n  NOTE: Download quota will be detected automatically.")
    print("  If quota is insufficient, downloads will be batched across days.")

    confirm = input("\n  Confirm download? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Cancelled.")
        return

    asyncio.run(heywhale_download(datasets_to_download, email, password, base_dir))

    print("\n" + "=" * 60)
    print("Download Complete!")
    print("=" * 60)


if __name__ == "__main__":
    interactive_mode()
