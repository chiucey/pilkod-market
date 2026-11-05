---
name: "heywhale-dataset-assistant"
displayName: "和鲸数据助手"
description: "Interactive Heywhale dataset search, analysis and download assistant with Playwright automation, dynamic quota detection, registration guidance, and dual Python/Node.js support"
author: "李昊哲"
version: "1.2.0"
---

# Heywhale Dataset Assistant

Interactive dataset discovery, evaluation, and download assistant for the Heywhale (和鲸数据) platform.

## Overview

This skill helps users who are starting with an empty project and are unsure about which datasets to use. It provides an interactive workflow to discover, evaluate, and download datasets from the Heywhale platform using Python + Playwright automation.

## Environment Check

Before execution, detect all available tools using multi-path scanning. If any required tool is missing, offer the user choices: (A) 自动安装, (B) 手动安装, (C) 配置已安装路径.

### Latest Stable Versions (as of 2026-04)
- **Python**: 3.14.3 — https://www.python.org/downloads/
- **Node.js**: 24.15.0 LTS — https://nodejs.org/

### Python Detection & Installation

Multi-path scan for Python:

```python
def detect_python():
    candidates = []
    if sys.platform == "win32":
        for ver in ["314", "313", "312", "311"]:
            candidates.append(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", f"Python{ver}", "python.exe"))
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
            result = subprocess.run([py_path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"path": py_path, "version": result.stdout.strip().split()[-1]}
        except Exception:
            continue
    return None
```

**Python 未检测到时的提示：**
> Python 未检测到。请选择：
> A) 自动安装 Python 3.14.3（推荐）
> B) 手动安装（将打开 https://www.python.org/downloads/ ）
> C) 配置已安装的 Python 路径

自动安装命令 (Windows):
```powershell
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.14.3/python-3.14.3-amd64.exe" -OutFile "$env:TEMP\python_installer.exe"
Start-Process -Wait -FilePath "$env:TEMP\python_installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1"
```

### Node.js Detection & Installation

Multi-path scan for Node.js:

```python
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
            result = subprocess.run([node_path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return {"path": node_path, "version": result.stdout.strip()}
        except Exception:
            continue
    return None
```

**Node.js 未检测到时的提示：**
> Node.js 未检测到。请选择：
> A) 自动安装 Node.js 24.15.0 LTS（推荐）
> B) 手动安装（将打开 https://nodejs.org/ ）
> C) 配置已安装的 Node.js 路径
> D) 跳过（仅使用 Python）

自动安装命令 (Windows):
```powershell
Invoke-WebRequest -Uri "https://nodejs.org/dist/v24.15.0/node-v24.15.0-x64.msi" -OutFile "$env:TEMP\node_installer.msi"
Start-Process -Wait -FilePath "msiexec.exe" -ArgumentList "/i $env:TEMP\node_installer.msi /quiet /norestart"
```

### Python Dependencies
```bash
pip install playwright requests chardet
playwright install chromium
```

### Dual Script Support

本 Skill 同时提供 Python 和 Node.js 两种实现：
- **Python** (主要): `python main.py` — 完整交互模式
- **Node.js** (替代): `node download.js` — 等效功能
- 自动检测可用运行时并选择对应脚本

## Workflow

### Phase 1: Interactive Requirements Gathering

Ask the user these questions to understand their needs:

**Question 1 — Task Type:**
> 您的项目是什么类型的机器学习任务？
> - 回归预测 (Regression)
> - 分类 (Classification)
> - 聚类 (Clustering)
> - 自然语言处理 (NLP)
> - 时间序列 (Time Series)
> - 关联规则 (Association Rules)
> - 其他

**Question 2 — Domain:**
> 您的数据属于哪个领域？
> - 医疗健康
> - 金融经济
> - 电商消费
> - 教育考试
> - 体育运动
> - 餐饮美食
> - 其他

**Question 3 — Data Size:**
> 您偏好什么规模的数据？
> - 小型 (<1MB，适合教学演示)
> - 中型 (1-100MB，适合实战练习)
> - 大型 (>100MB，适合深度分析)
> - 无偏好

**Question 4 — Target Variable:**
> 您是否有明确的目标变量？
> - 有，请描述
> - 没有，需要推荐

**Question 5 — Save Directory:**
> 数据集保存到哪个目录？(默认: 当前项目的 datasets/ 文件夹)

### Phase 2: Heywhale Account — Login or Register

**首先询问用户**: "您是否已有和鲸数据账号？"

#### 选项 A: 已有账号

1. 提示输入邮箱和密码
2. 尝试 API 登录:
   ```
   POST https://www.heywhale.com/api/auth/login
   Body: {"email": "...", "password": "..."}
   ```
3. 登录成功 (code=0) → 进入 Phase 3
4. 登录失败 → 提供重试或注册新账号选项

#### 选项 B: 没有账号 — 引导注册

逐步引导用户完成注册：

**第一步 — 选择注册方式：**

和鲸数据支持两种注册方式：

> **方式一：微信扫码注册（推荐，更快捷）**
> 1. 打开微信，搜索并关注公众号「和鲸社区」
> 2. 在公众号菜单中点击「登录/注册」
> 3. 扫描网页上的二维码完成注册
> 4. 注册后请在网页端绑定邮箱（设置 → 账号安全 → 绑定邮箱）
>
> **方式二：邮箱注册**
> 1. 访问注册页面：https://www.heywhale.com/auth/register
> 2. 填写以下信息：
>    - **邮箱地址**：用于登录和接收通知
>    - **用户名**：社区显示名称（2-20个字符）
>    - **密码**：至少8位，需包含字母和数字
>    - **确认密码**：再次输入密码
> 3. 勾选同意《用户协议》和《隐私保护指引》
> 4. 点击「注册」按钮
> 5. 前往邮箱查收验证邮件，点击验证链接
> 6. 验证完成后即可登录

**第二步 — 收集登录凭证：**

> 注册成功！请输入您的登录信息：
> - 邮箱：
> - 密码：

**第三步 — 验证登录：**

尝试 API 登录确认成功。如果失败，排查：
- 邮箱未验证？→ 提醒用户检查收件箱和垃圾邮件
- 密码错误？→ 提供密码重置链接：https://www.heywhale.com/auth/reset-password

**重要**:
- **绝不**将凭证写入文件或日志
- 登录成功后告知用户账号状态和额度

#### 动态额度检测 (Dynamic Quota Detection)

**重要**: 下载额度因账号类型和注册时间而异。新注册用户可能只有 3 个/天的下载额度，而非 20 个。**绝不假设固定额度数字。** 始终从页面动态检测实际额度：

1. 登录后，访问任意数据集页面并点击下载按钮
2. 确认弹窗会显示: "今日还剩 **X** 个下载额度，确认要下载吗？"
3. 用 JavaScript 提取数字 X：
```javascript
let modal = document.querySelector('.dataset-download-confirm-modal .confirm-title');
let match = modal ? modal.textContent.match(/还剩\s*(\d+)/) : null;
let remainingQuota = match ? parseInt(match[1]) : 0;
```
4. 部分数据集显示 "当前数据集不消耗下载额度" — 这些是免费的，不计入额度
5. 利用此信息：
   - 告知用户实际剩余额度
   - 优先下载推荐指数最高的数据集
   - 额度不足时发出警告
   - 建议将剩余下载推迟到次日

### Phase 3: Dataset Search

Use Heywhale API to search datasets:

```
GET https://www.heywhale.com/api/datasets?search={keyword}&page=1&pageSize=20
```

Search strategy:
- Combine task type + domain in Chinese: "糖尿病 分类", "房价 回归"
- Also try English: "diabetes classification", "house price regression"
- For each result, extract: ID, Title, Description, File list, Download/Like counts

### Phase 4: Dataset Analysis & Recommendation

For each candidate dataset, analyze and present:

```
┌─────────────────────────────────────────────────────────────┐
│ 数据集: {title}                                               │
├─────────────────────────────────────────────────────────────┤
│ ID: {id}                                                     │
│ 描述: {description}                                          │
│ 文件: {file1} ({size1}), {file2} ({size2})                   │
│ 下载量: {downloads} | 点赞: {likes}                           │
│ 适合任务: {recommended_tasks}                                 │
│ 推荐指数: ★★★★☆                                              │
│ 适合章节: {chapter_suggestions}                               │
└─────────────────────────────────────────────────────────────┘
```

Summary table:

| # | Dataset | Files | Size | Rating | Tasks | Chapter |
|---|---------|-------|------|--------|-------|---------|
| 1 | ...     | 2 csv | 1.7M | ★★★★☆  | Regression | 01_regression |

### Phase 5: Download Planning

Help user plan:

1. **动态额度检查**: 先通过访问数据集页面读取确认弹窗来检测用户实际剩余额度。不要假设 20/天。
   - 如果剩余额度 < 需要的文件总数，按推荐指数排序优先下载
   - 单独标记免费数据集（不消耗额度）— 它们不计入额度
   - 额度不足时，建议分多天批次下载
2. **Batch grouping**: Group by topic/chapter
3. **Size estimate**: Show total download size
4. **Directory structure**:
   ```
   datasets/
   ├── 01_regression/
   │   ├── case01_XXX/
   │   │   └── data.csv
   │   └── case02_YYY/
   ├── 02_classification/
   ├── 03_decision_tree/
   └── ...
   ```
5. **额度感知的批次策略**:
   ```
   批次 1 (今天, 额度: 3):
     [免费] 数据集 A (不消耗额度)
     [免费] 数据集 B (不消耗额度)
     [1/3]  数据集 C (最高优先级)
     [2/3]  数据集 D (高优先级)
     [3/3]  数据集 E (中优先级)
   
   批次 2 (明天):
     [1/?]  数据集 F
     [2/?]  数据集 G
   ```

### Phase 6: Selective Download Confirmation

Present options:
- **A**: Download all recommended datasets
- **B**: Select specific datasets by number
- **C**: Download by priority (highest rating first)
- **D**: Preview data structure before deciding

For option D, show:
- Column names and types
- First 3 rows of data
- Missing value statistics
- Basic statistical summary

Wait for user confirmation before downloading.

### Phase 7: Execute Download

#### Download Script (Python + Playwright)

The download mechanism follows this flow:
1. API login → get session cookies
2. Launch Playwright browser → inject cookies
3. Navigate to dataset page → click download button
4. Handle confirmation modal → extract COS signed URLs
5. Download files via signed URLs using requests
6. Verify and convert encoding to UTF-8

```python
import asyncio
import os
import re
import requests
from playwright.async_api import async_playwright

async def heywhale_download(datasets, email, password, base_dir):
    session = requests.Session()
    resp = session.post("https://www.heywhale.com/api/auth/login", json={
        "email": email, "password": password
    }, timeout=15)
    if resp.json().get("code") != 0:
        print("Login failed")
        return False
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

        # Dynamic quota detection
        remaining_quota = None
        if datasets:
            first_ds = datasets[0]
            probe_url = f"https://www.heywhale.com/home/dataset/{first_ds['id']}"
            try:
                await page.goto(probe_url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(8)
                download_btn = page.locator('button.ivu-btn-icon-only:has(.icon-download)')
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
                            print(f"检测到额度: 今日还剩 {remaining_quota} 个下载")
                    for sel in ['.dataset-download-confirm-modal .ivu-modal-close', '.dataset-download-modal .ivu-modal-close']:
                        try:
                            close = page.locator(sel).first
                            if await close.is_visible():
                                await close.click()
                                await asyncio.sleep(1)
                        except Exception:
                            pass
            except Exception:
                pass

        quota_used = 0
        for ds in datasets:
            save_dir = os.path.join(base_dir, ds["case_dir"])
            os.makedirs(save_dir, exist_ok=True)

            csv_exists = all(
                os.path.exists(os.path.join(save_dir, f)) and os.path.getsize(os.path.join(save_dir, f)) > 100
                for f in ds.get("expected_csvs", [])
            )
            if csv_exists:
                print(f"SKIP: {ds['title']} (already exists)")
                continue

            if remaining_quota is not None and quota_used >= remaining_quota:
                print(f"额度已用完: {quota_used}/{remaining_quota}。剩余数据集请明天下载。")
                break

            url = f"https://www.heywhale.com/home/dataset/{ds['id']}"
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(10)

            download_btn = page.locator('button.ivu-btn-icon-only:has(.icon-download)')
            if await download_btn.count() == 0:
                print(f"ERR: No download button for {ds['title']}")
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

            close_btn = page.locator('.dataset-download-modal .ivu-modal-close')
            if await close_btn.count() > 0:
                try: await close_btn.first.click()
                except: pass
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
                        print(f"OK: {su['filename']} ({os.path.getsize(save_path)}B)")
                    else:
                        print(f"FAIL: {su['filename']} HTTP {r.status_code}")
                except Exception as e:
                    print(f"ERR: {su['filename']} - {e}")

            if not is_free_ds and csv_count > 0:
                quota_used += csv_count
                print(f"额度: {quota_used}/{remaining_quota} 已使用" if remaining_quota else f"已下载: {csv_count} 个文件")
            elif is_free_ds:
                print(f"免费数据集 (不消耗额度)")

        await browser.close()
    return True
```

#### Encoding Conversion

After download, ensure all CSV files are UTF-8:

```python
import chardet

def ensure_utf8(file_path):
    with open(file_path, 'rb') as f:
        raw = f.read()
    result = chardet.detect(raw)
    encoding = result.get('encoding', 'utf-8')
    if encoding and encoding.lower() not in ('utf-8', 'ascii'):
        text = raw.decode(encoding, errors='replace')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return True
    return False
```

### Phase 8: Post-Download Verification

Verify each downloaded file:
1. File exists and size > 100 bytes
2. CSV is parseable (not corrupted)
3. Encoding is UTF-8
4. Display summary:

```
╔══════════════════════════════════════════════════════════╗
║               Download Summary                           ║
╠══════════════════════════════════════════════════════════╣
║ [OK] 01_regression/case07_berry_yield/train.csv (1.7MB) ║
║ [OK] 01_regression/case07_berry_yield/test.csv (1.0MB)  ║
║ [OK] 02_classification/case12_diabetes/data.csv (23KB)  ║
║ ...                                                      ║
╠══════════════════════════════════════════════════════════╣
║ Total: 9 datasets, 13 files, 112.5MB                    ║
║ Status: All downloads successful                         ║
╚══════════════════════════════════════════════════════════╝
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| Login failed | Wrong credentials | Re-ask for email/password |
| No download button | Page not loaded | Increase wait, retry |
| Confirm modal missing | Some datasets skip it | Proceed to download modal |
| No signed URLs | Download modal issue | Retry click flow |
| HTTP 403 | Signed URL expired | Re-navigate for new URL |
| Quota exceeded | Downloads exceed actual quota (may be 3 for new users) | Inform user, show remaining, continue tomorrow |
| Quota detection failed | Modal text format changed | Default to conservative estimate (3), proceed cautiously |
| Encoding issue | Non-UTF-8 CSV | Auto-convert with chardet |
| Large file timeout | Slow connection | Increase timeout, show progress |
| Node.js not in PATH | Installed but not configured | Use multi-path scanning to locate node.exe |

## Security

- **Never** store credentials in files, logs, or environment variables
- **Never** commit credentials to version control
- Use credentials only in the current session memory
- Close browser immediately after download completes
