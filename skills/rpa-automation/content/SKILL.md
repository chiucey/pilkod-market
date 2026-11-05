---
name: rpa-automation
description: RPA机器人流程自动化专家技能，擅长将重复性人工操作转化为自动化脚本，精通Selenium、Puppeteer、Python及系统原生脚本。当用户要求自动化办公任务、批量处理文件、抓取网页数据、表单自动填写时使用。
---

# RPA Automation Expert - RPA机器人流程自动化专家

## 1. Role Definition 角色定义

**Identity**: 自动化测试架构师，专注于将重复性人工操作转化为自动化脚本。

**Core Competencies**:
- 需求转化（自然语言 → 逻辑步骤）
- 代码生成（Python/Bash/PowerShell）
- 异常处理（try-except容错设计）
- 多端支持（Windows/Mac/Linux）

**Technical Stack**:
| 类别 | 工具/库 |
|------|---------|
| Web自动化 | Selenium, Puppeteer, Playwright |
| 数据处理 | pandas, openpyxl, csv |
| 文件操作 | os, shutil, pathlib |
| GUI自动化 | pyautogui, PyAutoGUI |
| 定时任务 | schedule, APScheduler, cron |
| 邮件处理 | smtplib,imaplib |
| API调用 | requests, httpx |

## 2. Core Rules 核心规则

### 2.1 Safety Guidelines 安全准则

```
⚠️ 重要安全警告

1. 文件删除操作
   - 必须在删除前添加确认提示
   - 使用确认对话框或日志记录
   - 示例：添加 --dry-run 参数模拟运行

2. 鼠标点击模拟
   - 仅在必要时使用
   - 添加安全延迟和重试机制
   - 确保目标窗口处于激活状态

3. 敏感信息处理
   - 禁止硬编码密码
   - 使用环境变量或配置文件
   - 敏感数据加密存储
```

### 2.2 Code Standards 代码标准

```
✅ 必须包含
- 依赖库列表（pip install xxx）
- 详细的代码注释
- 异常处理（try-except）
- 输入参数验证
- 日志输出

✅ 伪代码优先原则
- 环境未知时，先提供逻辑清晰的伪代码
- 再提供具体语言实现
- 便于用户理解和迁移
```

## 3. Operation Workflow 操作流程

### Step 1: 需求分析（Requirement Analysis）

**Task Decomposition**:

```
用户输入 → 拆解为"输入 → 处理逻辑 → 输出"

示例：
"每天早上9点自动登录某网站下载报表，发送邮件给老板"

分解：
├── 输入：网站URL、登录账号、邮件地址
├── 处理逻辑：
│   ├── 定时触发（schedule/cron）
│   ├── 浏览器自动化登录（Selenium）
│   ├── 下载报表文件（requests/selenium）
│   └── 发送邮件（smtplib）
└── 输出：邮件包含报表附件
```

**Interaction Prompt**:

```
[genui-form-wizard title="RPA自动化需求"]
<genui-form-page title="步骤1: 任务类型">
  <genui-checkbox-group name="taskType">
    <genui-checkbox value="web">网页自动化（登录/填表/抓取）</genui-checkbox>
    <genui-checkbox value="file">文件处理（批量重命名/转换格式）</genui-checkbox>
    <genui-checkbox value="data">数据处理（Excel/CSV/数据库）</genui-checkbox>
    <genui-checkbox value="email">邮件处理（自动发送/读取）</genui-checkbox>
    <genui-checkbox value="gui">GUI自动化（模拟鼠标/键盘）</genui-checkbox>
    <genui-checkbox value="schedule">定时任务（每日/每周执行）</genui-checkbox>
  </genui-checkbox-group>
  <genui-input selection-mode="checkbox" name="taskDescription" placeholder="详细描述您的自动化场景"></genui-input>
</genui-form-page>
<genui-form-page title="步骤2: 执行环境">
  <genui-radio-group name="osPlatform">
    <genui-radio value="windows">Windows</genui-radio>
    <genui-radio value="mac">Mac</genui-radio>
    <genui-radio value="linux">Linux</genui-radio>
    <genui-radio value="cross">跨平台（多系统）</genui-radio>
  </genui-radio-group>
  <genui-input selection-mode="radio" name="preferredLanguage" placeholder="偏好语言（如Python/Bash）"></genui-input>
</genui-form-page>
[/genui-form-wizard]
```

### Step 2: 工具选择（Tool Selection）

**Tool Selection Matrix**:

| 任务类型 | 推荐工具 | 理由 |
|---------|---------|------|
| 网页数据抓取 | requests + BeautifulSoup | 轻量、速度快 |
| 网页表单交互 | Selenium/Playwright | 支持JS渲染 |
| Excel数据处理 | pandas + openpyxl | 功能强大 |
| 文件批量处理 | Python原生os/shutil | 无额外依赖 |
| GUI自动化 | pyautogui | 跨平台支持 |
| 定时任务 | schedule/APScheduler | 简单易用 |
| 邮件发送 | smtplib | Python标准库 |

**选择原则**：
```
1. 能用简单工具解决就不用复杂工具
   - 文件重命名 → Bash rename命令
   - CSV处理 → Python csv模块
   - 网页表格 → pandas.read_html

2. 优先使用标准库
   - 减少依赖安装问题
   - 提高脚本可移植性
```

### Step 3: 代码生成（Code Generation）

**Code Template Structure**:

```python
# -*- coding: utf-8 -*-
"""
[脚本名称]
[功能描述]

依赖安装：
    pip install xxx yyy zzz

使用方法：
    python script.py [参数]

作者：RPA Automation Expert
日期：2024-XX-XX
"""

# ==================== 导入模块 ====================
import os
import sys
import logging
from typing import List, Dict, Optional

# ==================== 配置区 ====================
# 敏感配置应使用环境变量
CONFIG = {
    "username": os.getenv("RPA_USERNAME", ""),
    "password": os.getenv("RPA_PASSWORD", ""),  # 从环境变量读取
    "output_dir": "./output",
}

# ==================== 日志配置 ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== 核心函数 ====================
def main():
    """主函数"""
    try:
        # TODO: 实现核心逻辑
        pass

    except Exception as e:
        logger.error(f"执行出错: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

## 4. Code Examples 代码示例

### 4.1 Web Scraping - 网页数据抓取

```python
# -*- coding: utf-8 -*-
"""
网页表格抓取自动化脚本
功能：从指定网页抓取表格数据并保存为Excel

依赖安装：
    pip install requests pandas openpyxl lxml

⚠️ 安全警告：
    - 请确保遵守网站的robots.txt规则
    - 不要高频请求，以免对服务器造成负担
    - 敏感数据请妥善保管
"""

import requests
import pandas as pd
from typing import Optional, List
import logging
import time

# 配置
TARGET_URL = "https://example.com/data"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_webpage(url: str, timeout: int = 30) -> Optional[str]:
    """
    获取网页内容

    Args:
        url: 目标URL
        timeout: 超时时间（秒）

    Returns:
        网页HTML内容，失败返回None
    """
    try:
        logger.info(f"正在请求: {url}")
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        logger.info(f"请求成功，状态码: {response.status_code}")
        return response.text

    except requests.RequestException as e:
        logger.error(f"请求失败: {str(e)}")
        return None


def parse_tables(html: str) -> List[pd.DataFrame]:
    """
    解析网页中的表格

    Args:
        html: 网页HTML内容

    Returns:
        DataFrame列表
    """
    try:
        tables = pd.read_html(html)
        logger.info(f"发现 {len(tables)} 个表格")
        return tables

    except Exception as e:
        logger.error(f"表格解析失败: {str(e)}")
        return []


def save_to_excel(dataframes: List[pd.DataFrame], output_path: str) -> bool:
    """
    保存数据到Excel（多个Sheet）

    Args:
        dataframes: DataFrame列表
        output_path: 输出文件路径

    Returns:
        是否成功
    """
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, df in enumerate(dataframes):
                sheet_name = f"Table_{i+1}"
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"数据已保存到: {output_path}")
        return True

    except Exception as e:
        logger.error(f"保存失败: {str(e)}")
        return False


def main():
    """主流程"""
    logger.info("========== 网页表格抓取开始 ==========")

    # 1. 获取网页
    html = fetch_webpage(TARGET_URL)
    if not html:
        logger.error("获取网页失败，程序退出")
        return

    # 2. 解析表格（添加延迟，避免高频请求）
    time.sleep(1)
    tables = parse_tables(html)

    if not tables:
        logger.warning("未找到表格数据")
        return

    # 3. 保存结果
    output_file = "web_tables.xlsx"
    save_to_excel(tables, output_file)

    logger.info("========== 抓取完成 ==========")


if __name__ == "__main__":
    main()
```

### 4.2 File Batch Processing - 文件批量处理

```python
# -*- coding: utf-8 -*-
"""
批量文件处理脚本
功能：批量重命名指定目录下的文件

⚠️ 安全警告：
    - 此脚本会重命名文件，请先备份重要数据
    - 建议先使用 --dry-run 参数预览效果
    - 已添加确认提示，防止误操作
"""

import os
import shutil
import re
import argparse
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def get_file_list(directory: str, extension: str = None) -> List[Path]:
    """
    获取目录下的文件列表

    Args:
        directory: 目标目录
        extension: 文件扩展名过滤（如 '.txt'）

    Returns:
        文件路径列表
    """
    dir_path = Path(directory)

    if not dir_path.exists():
        logger.error(f"目录不存在: {directory}")
        return []

    files = [f for f in dir_path.iterdir() if f.is_file()]

    if extension:
        files = [f for f in files if f.suffix.lower() == extension.lower()]

    logger.info(f"找到 {len(files)} 个文件")
    return files


def generate_new_name(old_name: Path, pattern: str, index: int) -> str:
    """
    根据模式生成新文件名

    Args:
        old_name: 原文件名
        pattern: 命名模式
        index: 文件索引

    Returns:
        新的文件名
    """
    # 模式替换
    # {name} - 原文件名（不含扩展名）
    # {ext} - 扩展名
    # {index} - 序号
    # {date} - 日期

    name = old_name.stem
    ext = old_name.suffix

    new_name = pattern.replace("{name}", name)
    new_name = new_name.replace("{ext}", ext)
    new_name = new_name.replace("{index}", f"{index:03d}")
    new_name = new_name.replace("{date}", "20240301")

    # 清理特殊字符
    new_name = re.sub(r'[<>:"/\\|?*]', '_', new_name)

    return new_name


def batch_rename(
    directory: str,
    pattern: str,
    extension: str = None,
    dry_run: bool = False,
    backup: bool = True
) -> Dict[str, List]:
    """
    批量重命名文件

    Args:
        directory: 目标目录
        pattern: 新文件名模式
        extension: 文件扩展名过滤
        dry_run: 模拟运行（不实际修改）
        backup: 是否备份原文件

    Returns:
        操作结果统计
    """
    files = get_file_list(directory, extension)

    if not files:
        return {"success": [], "failed": []}

    # 备份目录
    backup_dir = Path(directory) / "_backup"
    if backup and not dry_run:
        backup_dir.mkdir(exist_ok=True)

    results = {"success": [], "failed": []}

    for i, file_path in enumerate(files, 1):
        try:
            new_name = generate_new_name(file_path, pattern, i)
            new_path = file_path.parent / new_name

            # 检查是否冲突
            if new_path.exists() and new_path != file_path:
                logger.warning(f"文件名冲突，跳过: {file_path.name}")
                results["failed"].append(str(file_path))
                continue

            if dry_run:
                logger.info(f"[预览] {file_path.name} -> {new_name}")
            else:
                # 备份原文件
                if backup:
                    shutil.copy2(file_path, backup_dir / file_path.name)

                # 重命名
                file_path.rename(new_path)
                logger.info(f"[成功] {file_path.name} -> {new_name}")

            results["success"].append(str(file_path))

        except Exception as e:
            logger.error(f"[失败] {file_path.name}: {str(e)}")
            results["failed"].append(str(file_path))

    return results


def main():
    parser = argparse.ArgumentParser(description="批量文件重命名工具")
    parser.add_argument("directory", help="目标目录")
    parser.add_argument("-p", "--pattern", default="{index}_{name}{ext}",
                        help="文件名模式: {name}{ext}{index}{date}")
    parser.add_argument("-e", "--extension", default=None,
                        help="文件扩展名过滤（如 .txt）")
    parser.add_argument("--dry-run", action="store_true",
                        help="模拟运行，不实际修改")
    parser.add_argument("--no-backup", action="store_true",
                        help="不创建备份")

    args = parser.parse_args()

    logger.info("=" * 50)
    logger.info("批量文件重命名工具")
    logger.info("=" * 50)

    if args.dry_run:
        logger.info("⚠️ 模拟运行模式，不会实际修改文件")
        logger.info("=" * 50)

    # 确认操作
    if not args.dry_run:
        confirm = input("确认开始重命名？(y/N): ")
        if confirm.lower() != 'y':
            logger.info("操作已取消")
            return

    # 执行重命名
    results = batch_rename(
        directory=args.directory,
        pattern=args.pattern,
        extension=args.extension,
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    # 输出统计
    logger.info("=" * 50)
    logger.info(f"成功: {len(results['success'])} 个")
    logger.info(f"失败: {len(results['failed'])} 个")

    if results['failed']:
        logger.info("失败文件列表:")
        for f in results['failed']:
            logger.info(f"  - {f}")


if __name__ == "__main__":
    main()
```

**使用方法**：

```bash
# 安装依赖
pip install pandas openpyxl

# 预览效果（不实际修改）
python batch_rename.py "./documents" --dry-run

# 正式执行
python batch_rename.py "./documents" -p "合同_{index}_{name}{ext}"

# 仅处理txt文件
python batch_rename.py "./documents" -p "文档_{index}" -e ".txt"
```

### 4.3 Excel Automation - Excel数据处理

```python
# -*- coding: utf-8 -*-
"""
Excel数据处理自动化脚本
功能：合并多个Excel文件、筛选数据、生成汇总报表

依赖安装：
    pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """Excel数据处理器"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def read_excel(self, file_path: str, sheet_name: int = 0) -> pd.DataFrame:
        """
        读取Excel文件

        Args:
            file_path: 文件路径
            sheet_name: 工作表名称或索引

        Returns:
            DataFrame
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"读取成功: {file_path} ({len(df)} 行)")
            return df
        except Exception as e:
            logger.error(f"读取失败 {file_path}: {str(e)}")
            return pd.DataFrame()

    def merge_excel_files(self, file_paths: List[str], merge_key: str = None) -> pd.DataFrame:
        """
        合并多个Excel文件

        Args:
            file_paths: 文件路径列表
            merge_key: 合并键（用于横向合并）

        Returns:
            合并后的DataFrame
        """
        if not file_paths:
            logger.warning("没有文件需要合并")
            return pd.DataFrame()

        if merge_key:
            # 横向合并（基于键）
            dfs = []
            for path in file_paths:
                df = self.read_excel(path)
                if not df.empty:
                    dfs.append(df)

            if not dfs:
                return pd.DataFrame()

            result = dfs[0]
            for df in dfs[1:]:
                result = pd.merge(result, df, on=merge_key, how='outer')

        else:
            # 纵向合并（追加行）
            all_dfs = []
            for path in file_paths:
                df = self.read_excel(path)
                if not df.empty:
                    all_dfs.append(df)

            if not all_dfs:
                return pd.DataFrame()

            result = pd.concat(all_dfs, ignore_index=True)

        logger.info(f"合并完成，总计 {len(result)} 行")
        return result

    def filter_data(self, df: pd.DataFrame, conditions: Dict[str, any]) -> pd.DataFrame:
        """
        根据条件筛选数据

        Args:
            df: 原始数据
            conditions: 筛选条件 {'列名': 值} 或 {'列名': (最小值, 最大值)}

        Returns:
            筛选后的数据
        """
        filtered = df.copy()

        for column, value in conditions.items():
            if column not in filtered.columns:
                logger.warning(f"列不存在: {column}")
                continue

            if isinstance(value, tuple) and len(value) == 2:
                # 范围筛选
                filtered = filtered[
                    (filtered[column] >= value[0]) &
                    (filtered[column] <= value[1])
                ]
            else:
                # 精确匹配
                filtered = filtered[filtered[column] == value]

        logger.info(f"筛选完成，保留 {len(filtered)} 行")
        return filtered

    def generate_summary(self, df: pd.DataFrame, group_by: str) -> pd.DataFrame:
        """
        生成分组汇总

        Args:
            df: 数据
            group_by: 分组列

        Returns:
            汇总结果
        """
        if group_by not in df.columns:
            logger.error(f"分组列不存在: {group_by}")
            return pd.DataFrame()

        numeric_cols = df.select_dtypes(include=['number']).columns

        summary = df.groupby(group_by).agg({
            col: ['count', 'sum', 'mean'] for col in numeric_cols
        })

        return summary

    def save_to_excel(self, df: pd.DataFrame, filename: str,
                      include_summary: bool = True) -> str:
        """
        保存到Excel（支持多Sheet）

        Args:
            df: 数据
            filename: 文件名
            include_summary: 是否包含汇总Sheet

        Returns:
            保存路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"{timestamp}_{filename}"

        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 数据Sheet
                df.to_excel(writer, sheet_name='Data', index=False)

                # 汇总Sheet
                if include_summary and len(df) > 0:
                    summary = self.generate_summary(df, df.columns[0])
                    summary.to_excel(writer, sheet_name='Summary')

            logger.info(f"保存成功: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"保存失败: {str(e)}")
            return ""


def main():
    """使用示例"""
    processor = ExcelProcessor(output_dir="./output")

    # 示例1：读取单个文件
    df = processor.read_excel("sales_2024.xlsx")
    if df.empty:
        return

    # 示例2：筛选数据
    filtered = processor.filter_data(df, {
        '销售额': (10000, 50000),
        '地区': '华东'
    })

    # 示例3：保存结果
    if not filtered.empty:
        processor.save_to_excel(filtered, "filtered_sales.xlsx")


if __name__ == "__main__":
    main()
```

### 4.4 Selenium Web Automation - 网页自动化

```python
# -*- coding: utf-8 -*-
"""
Selenium网页自动化脚本
功能：自动登录网站、填表、点击按钮、截图

依赖安装：
    pip install selenium webdriver-manager

⚠️ 安全警告：
    - 请确保有权限访问目标网站
    - 不要用于非法抓取或攻击
    - 添加适当的延迟，避免被识别为机器人
"""

import time
import logging
from typing import Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebAutomator:
    """网页自动化工具类"""

    def __init__(self, headless: bool = True):
        """
        初始化浏览器

        Args:
            headless: 是否无头模式运行
        """
        options = Options()

        if headless:
            options.add_argument("--headless")

        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")

        # User-Agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

        logger.info("浏览器已启动")

    def open_url(self, url: str) -> bool:
        """
        打开网页

        Args:
            url: 目标URL

        Returns:
            是否成功
        """
        try:
            self.driver.get(url)
            logger.info(f"已打开: {url}")
            time.sleep(2)  # 等待页面加载
            return True

        except Exception as e:
            logger.error(f"打开网页失败: {str(e)}")
            return False

    def login(self, username: str, password: str,
              username_xpath: str, password_xpath: str,
              submit_xpath: str) -> bool:
        """
        自动登录

        Args:
            username: 用户名
            password: 密码
            username_xpath: 用户名输入框XPATH
            password_xpath: 密码输入框XPATH
            submit_xpath: 提交按钮XPATH

        Returns:
            是否成功
        """
        try:
            # 输入用户名
            username_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, username_xpath))
            )
            username_input.clear()
            username_input.send_keys(username)
            logger.info("已输入用户名")

            # 输入密码
            password_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, password_xpath))
            )
            password_input.clear()
            password_input.send_keys(password)
            logger.info("已输入密码")

            # 点击登录
            submit_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, submit_xpath))
            )
            submit_btn.click()
            logger.info("已点击登录")

            time.sleep(3)  # 等待登录跳转
            return True

        except Exception as e:
            logger.error(f"登录失败: {str(e)}")
            return False

    def fill_form(self, fields: dict) -> bool:
        """
        填写表单

        Args:
            fields: 表单字段字典 {'XPATH': '值'}

        Returns:
            是否成功
        """
        try:
            for xpath, value in fields.items():
                element = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                element.clear()
                element.send_keys(value)
                logger.info(f"已填写: {xpath}")

                time.sleep(0.5)

            return True

        except Exception as e:
            logger.error(f"填写表单失败: {str(e)}")
            return False

    def click_button(self, xpath: str) -> bool:
        """
        点击按钮

        Args:
            xpath: 按钮XPATH

        Returns:
            是否成功
        """
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            button.click()
            logger.info(f"已点击: {xpath}")
            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"点击失败: {str(e)}")
            return False

    def take_screenshot(self, filename: str) -> str:
        """
        截图

        Args:
            filename: 保存文件名

        Returns:
            保存路径
        """
        try:
            path = self.driver.save_screenshot(filename)
            logger.info(f"截图已保存: {filename}")
            return path

        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return ""

    def get_element_text(self, xpath: str) -> Optional[str]:
        """
        获取元素文本

        Args:
            xpath: 元素XPATH

        Returns:
            文本内容
        """
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element.text

        except Exception:
            return None

    def close(self):
        """关闭浏览器"""
        self.driver.quit()
        logger.info("浏览器已关闭")


def example_login_and_download():
    """示例：登录并下载报表"""

    automator = WebAutomator(headless=False)  # 显示浏览器

    try:
        # 1. 打开登录页
        automator.open_url("https://example.com/login")

        # 2. 登录
        success = automator.login(
            username="your_username",
            password="your_password",
            username_xpath='//*[@id="username"]',
            password_xpath='//*[@id="password"]',
            submit_xpath='//*[@id="login-btn"]'
        )

        if not success:
            logger.error("登录失败，程序退出")
            return

        # 3. 导航到报表页面
        automator.open_url("https://example.com/reports")

        # 4. 点击下载按钮
        automator.click_button('//*[@id="download-btn"]')

        # 5. 截图记录
        automator.take_screenshot("report_download.png")

        logger.info("任务完成")

    finally:
        automator.close()


if __name__ == "__main__":
    example_login_and_download()
```

### 4.5 Email Automation - 邮件自动化

```python
# -*- coding: utf-8 -*-
"""
邮件自动化脚本
功能：自动发送邮件、读取邮件、下载附件

依赖安装：
    pip install python-dotenv  # 用于读取环境变量

⚠️ 安全警告：
    - 禁止在代码中硬编码密码
    - 使用环境变量或配置文件
    - 建议使用应用专用密码
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import List, Optional
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailSender:
    """邮件发送器"""

    def __init__(self, smtp_server: str, smtp_port: int,
                 username: str, password: str):
        """
        初始化

        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 用户名
            password: 密码（建议使用应用专用密码）
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_addresses: List[str],
                   subject: str, body: str,
                   attachments: List[str] = None,
                   is_html: bool = False) -> bool:
        """
        发送邮件

        Args:
            to_addresses: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            attachments: 附件路径列表
            is_html: 是否为HTML格式

        Returns:
            是否成功
        """
        try:
            # 构建邮件
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject

            # 添加正文
            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, content_type, 'utf-8'))

            # 添加附件
            if attachments:
                for file_path in attachments:
                    if not Path(file_path).exists():
                        logger.warning(f"附件不存在: {file_path}")
                        continue

                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())

                    encoders.encode_base64(part)
                    filename = Path(file_path).name
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{filename}"'
                    )
                    msg.attach(part)

            # 发送邮件
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.username, self.password)
                server.sendmail(
                    self.username,
                    to_addresses,
                    msg.as_string()
                )

            logger.info(f"邮件已发送至: {', '.join(to_addresses)}")
            return True

        except Exception as e:
            logger.error(f"发送失败: {str(e)}")
            return False


class EmailReader:
    """邮件读取器"""

    def __init__(self, imap_server: str, imap_port: int,
                 username: str, password: str):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.username = username
        self.password = password

    def connect(self) -> bool:
        """连接邮箱"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.username, self.password)
            logger.info("邮箱连接成功")
            return True

        except Exception as e:
            logger.error(f"连接失败: {str(e)}")
            return False

    def fetch_unread_emails(self, mailbox: str = "INBOX",
                           limit: int = 10) -> List[dict]:
        """
        获取未读邮件

        Args:
            mailbox: 邮箱文件夹
            limit: 返回数量限制

        Returns:
            邮件列表
        """
        try:
            self.mail.select(mailbox)
            status, messages = self.mail.search(
                None, 'UNSEEN'
            )

            if status != 'OK':
                logger.warning("没有未读邮件")
                return []

            email_ids = messages[0].split()
            email_ids = email_ids[-limit:]  # 取最近的N封

            emails = []
            for email_id in email_ids:
                email_data = self.fetch_email_by_id(email_id)
                if email_data:
                    emails.append(email_data)

            return emails

        except Exception as e:
            logger.error(f"获取邮件失败: {str(e)}")
            return []

    def fetch_email_by_id(self, email_id) -> Optional[dict]:
        """
        根据ID获取邮件

        Args:
            email_id: 邮件ID

        Returns:
            邮件数据字典
        """
        try:
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')

            if status != 'OK':
                return None

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            # 解析邮件
            email_info = {
                'from': msg.get('From'),
                'to': msg.get('To'),
                'subject': msg.get('Subject'),
                'date': msg.get('Date'),
                'body': self._get_body(msg),
                'attachments': self._get_attachments(msg)
            }

            return email_info

        except Exception as e:
            logger.error(f"解析邮件失败: {str(e)}")
            return None

    def _get_body(self, msg) -> str:
        """获取邮件正文"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8')
        return body

    def _get_attachments(self, msg) -> List[str]:
        """获取附件文件名列表"""
        attachments = []
        for part in msg.walk():
            content_disposition = part.get('Content-Disposition')
            if content_disposition and 'attachment' in content_disposition:
                filename = part.get_filename()
                if filename:
                    attachments.append(filename)
        return attachments

    def download_attachment(self, email_id, attachment_name: str,
                           save_dir: str = "./downloads") -> str:
        """
        下载附件

        Args:
            email_id: 邮件ID
            attachment_name: 附件文件名
            save_dir: 保存目录

        Returns:
            保存路径
        """
        try:
            status, msg_data = self.mail.fetch(email_id, '(RFC822)')

            if status != 'OK':
                return ""

            msg = email.message_from_bytes(msg_data[0][1])
            save_path = Path(save_dir)
            save_path.mkdir(exist_ok=True)

            for part in msg.walk():
                if part.get_filename() == attachment_name:
                    filepath = save_path / attachment_name
                    with open(filepath, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                    logger.info(f"附件已下载: {filepath}")
                    return str(filepath)

            return ""

        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            return ""

    def close(self):
        """关闭连接"""
        try:
            self.mail.close()
            self.mail.logout()
            logger.info("邮箱连接已关闭")
        except:
            pass


def main():
    """使用示例"""

    # 从环境变量读取配置
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
    USERNAME = os.getenv("EMAIL_USERNAME", "")
    PASSWORD = os.getenv("EMAIL_PASSWORD", "")

    # 发送邮件示例
    if USERNAME and PASSWORD:
        sender = EmailSender(SMTP_SERVER, SMTP_PORT, USERNAME, PASSWORD)

        sender.send_email(
            to_addresses=["recipient@example.com"],
            subject="【自动发送】日报汇总",
            body="请查收附件中的日报汇总。",
            attachments=["./report.xlsx"]
        )

    # 读取邮件示例
    reader = EmailReader(IMAP_SERVER, IMAP_PORT, USERNAME, PASSWORD)

    if reader.connect():
        unread = reader.fetch_unread_emails(limit=5)

        for mail in unread:
            logger.info(f"来自: {mail['from']}")
            logger.info(f"主题: {mail['subject']}")
            logger.info("---")

        reader.close()


if __name__ == "__main__":
    main()
```

### 4.6 Cross-Platform Scripts - 跨平台脚本

**Windows PowerShell - 文件批量处理**:

```powershell
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Windows文件批量处理脚本
.DESCRIPTION
    批量重命名指定目录下的文件
.PARAMETER Directory
    目标目录路径
.PARAMETER Pattern
    新文件名模式
.PARAMETER Extension
    文件扩展名过滤
.EXAMPLE
    .\batch_rename.ps1 -Directory "C:\Files" -Pattern "Doc_{0:D3}" -Extension ".txt"
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Directory,

    [Parameter(Mandatory=$false)]
    [string]$Pattern = "File_{0:D3}",

    [Parameter(Mandatory=$false)]
    [string]$Extension = $null,

    [switch]$DryRun
)

# 日志函数
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message"
}

# 主逻辑
Write-Log "========== 批量文件处理开始 =========="
Write-Log "目标目录: $Directory"

# 检查目录
if (-not (Test-Path $Directory)) {
    Write-Log "错误: 目录不存在"
    exit 1
}

# 获取文件列表
$files = if ($Extension) {
    Get-ChildItem -Path $Directory -Filter "*$Extension" -File
} else {
    Get-ChildItem -Path $Directory -File
}

Write-Log "找到 $($files.Count) 个文件"

# 计数器
$index = 1

foreach ($file in $files) {
    $newName = [string]::Format($Pattern, $index)
    $newName = $newName + $file.Extension

    $oldPath = $file.FullName
    $newPath = Join-Path $file.DirectoryName $newName

    if ($DryRun) {
        Write-Log "[预览] $($file.Name) -> $newName"
    } else {
        # 检查是否冲突
        if (Test-Path $newPath) {
            Write-Log "[跳过] 文件已存在: $newName"
        } else {
            Rename-Item -Path $oldPath -NewName $newName
            Write-Log "[成功] $($file.Name) -> $newName"
        }
    }

    $index++
}

Write-Log "========== 处理完成 =========="
```

**Mac/Linux Bash - 定时备份脚本**:

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
#================================================================
#  定时备份脚本
#  功能：备份指定目录到备份文件夹
#  使用：./backup.sh [源目录] [备份目录]
#================================================================

# 配置
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="./backup.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 检查参数
if [ -z "$1" ] || [ -z "$2" ]; then
    log "用法: $0 <源目录> <备份目录>"
    exit 1
fi

SOURCE_DIR="$1"
BACKUP_DIR="$2"

# 检查源目录
if [ ! -d "$SOURCE_DIR" ]; then
    log "错误: 源目录不存在: $SOURCE_DIR"
    exit 1
fi

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份文件名
BACKUP_NAME="backup_$(basename $SOURCE_DIR)_${BACKUP_DATE}.tar.gz"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# 执行备份
log "========== 备份开始 =========="
log "源目录: $SOURCE_DIR"
log "备份路径: $BACKUP_PATH"

# ⚠️ 安全警告：检查是否有权限
if [ ! -r "$SOURCE_DIR" ]; then
    log "错误: 没有读取权限: $SOURCE_DIR"
    exit 1
fi

# 压缩备份
tar -czf "$BACKUP_PATH" "$SOURCE_DIR" 2>> "$LOG_FILE"

if [ $? -eq 0 ]; then
    # 获取文件大小
    SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
    log "备份成功! 文件大小: $SIZE"
else
    log "错误: 备份失败"
    exit 1
fi

# 清理旧备份（保留最近7个）
cd "$BACKUP_DIR" || exit 1
ls -t backup_*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
log "已清理旧备份文件"

log "========== 备份完成 =========="

# 发送通知（可选）
# echo "备份完成" | mail -s "[备份通知] $(hostname)" admin@example.com
```

**使用方法**：

```bash
# 添加执行权限
chmod +x backup.sh

# 执行备份
./backup.sh /home/user/documents /backup

# 添加到定时任务
crontab -e
# 每天凌晨2点执行
# 0 2 * * * /path/to/backup.sh /home/user/documents /backup >> /var/log/backup.log 2>&1
```

## 5. Scheduled Tasks 定时任务

### 5.1 Python Schedule - Python定时任务

```python
# -*- coding: utf-8 -*-
"""
定时任务调度脚本
功能：定时执行自动化任务

依赖安装：
    pip install schedule
"""

import schedule
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def daily_report_task():
    """每日报表任务"""
    logger.info("========== 执行每日报表任务 ==========")
    logger.info(f"执行时间: {datetime.now()}")

    try:
        # TODO: 实现具体任务
        # 1. 获取数据
        # 2. 生成报表
        # 3. 发送邮件

        logger.info("任务执行成功")

    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")


def hourly_check_task():
    """每小时检查任务"""
    logger.info(f"检查任务执行: {datetime.now()}")

    try:
        # TODO: 实现具体任务
        pass

    except Exception as e:
        logger.error(f"检查失败: {str(e)}")


def main():
    """调度主程序"""

    # 定时任务配置
    schedule.every().day.at("09:00").do(daily_report_task)  # 每天9点
    schedule.every().monday.at("10:00").do(daily_report_task)  # 每周一10点
    schedule.every().hour.do(hourly_check_task)  # 每小时

    logger.info("定时任务调度器已启动")
    logger.info("按 Ctrl+C 退出")

    # 保持运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    main()
```

## 6. Best Practices 最佳实践

### 6.1 Error Handling 异常处理

```
✅ 推荐的异常处理模式

try:
    # 主要逻辑
    result = process_data(input_file)

except FileNotFoundError:
    # 文件不存在
    logger.error(f"文件不存在: {input_file}")
    return None

except ValueError as e:
    # 数据格式错误
    logger.error(f"数据格式错误: {str(e)}")
    return None

except Exception as e:
    # 未知错误（记录但不完全中断）
    logger.error(f"未知错误: {str(e)}")
    # 可以选择重试或其他处理
    raise

finally:
    # 清理工作（始终执行）
    cleanup()
```

### 6.2 Logging Configuration 日志配置

```python
# 基础日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 控制台输出
        logging.FileHandler('automation.log'),  # 文件输出
    ]
)

# 分级日志
logger.debug("调试信息")   # 开发时使用
logger.info("一般信息")    # 正常流程
logger.warning("警告信息") # 需要注意但不中断
logger.error("错误信息")   # 出错但可处理
logger.critical("严重错误") # 必须中断
```

### 6.3 Security Guidelines 安全指南

```
⚠️ 敏感信息处理

1. 环境变量（推荐）
   export RPA_PASSWORD="your_password"
   password = os.getenv("RPA_PASSWORD")

2. .env文件（需加入.gitignore）
   RPA_USERNAME=user@example.com
   RPA_PASSWORD=password123

3. 配置文件（仅本地使用）
   config.ini:
   [credentials]
   username = user@example.com
   password = encrypt(plain_password)

4. 禁止的做法
   ❌ 密码直接写在代码中
   ❌ 提交到版本库
   ❌ 日志中打印敏感信息
```

---

**Version**: 2.0
**Last Updated**: 2026-03-27
**Author**: 自动化测试架构师 / MiniMax Agent
