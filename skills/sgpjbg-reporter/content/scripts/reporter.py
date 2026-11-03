"""
三个皮匠报告自动化脚本
用于登录、搜索、下载和阅读报告
"""

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional


class SgpjbgReporter:
    """三个皮匠报告自动化处理类"""

    BASE_URL = "https://www.sgpjbg.com"
    DOWNLOAD_DIR = "/downloads/sgpjbg-reports"

    def __init__(self):
        self.session_data = {
            "logged_in": False,
            "username": None,
            "cookies": None,
            "downloads": []
        }

    def collect_credentials(self, username: str, password: str) -> Dict:
        """收集并验证用户凭证"""
        return {
            "username": username,
            "password": password,
            "valid": bool(username and password)
        }

    def prepare_login_steps(self) -> List[Dict]:
        """准备登录步骤用于interact_with_website"""
        return [
            {
                "action": "navigate",
                "url": self.BASE_URL,
                "description": "打开三个皮匠报告网站"
            },
            {
                "action": "wait",
                "seconds": 2,
                "description": "等待页面加载"
            },
            {
                "action": "find_element",
                "selector_type": "xpath",
                "selector": "//a[contains(text(),'登录')] | //button[contains(text(),'登录')] | //div[contains(@class,'login')]",
                "description": "查找登录入口"
            },
            {
                "action": "click",
                "description": "点击登录按钮"
            },
            {
                "action": "wait",
                "seconds": 1,
                "description": "等待登录弹窗"
            }
        ]

    def execute_login(self, username: str, password: str) -> str:
        """生成登录执行脚本"""
        return f'''
// 登录三个皮匠报告
// 用户名: {username}

// 1. 点击登录入口
const loginBtn = document.querySelector('a[href*="login"], button.login, .login-btn');
if (loginBtn) loginBtn.click();

// 2. 等待登录表单出现
await new Promise(r => setTimeout(r, 1000));

// 3. 填写用户名
const usernameInput = document.querySelector('input[name*="user"], input[name*="name"], #username, .username');
if (usernameInput) usernameInput.value = '{username}';

// 4. 填写密码
const passwordInput = document.querySelector('input[name*="pass"], input[type="password"], #password, .password');
if (passwordInput) passwordInput.value = '{password}';

// 5. 点击登录确认
const submitBtn = document.querySelector('button[type="submit"], .login-submit, .submit');
if (submitBtn) submitBtn.click();

// 6. 等待登录完成
await new Promise(r => setTimeout(r, 2000));

// 返回登录状态
return document.querySelector('.user-info, .username, [class*="logined"]') ? 'LOGIN_SUCCESS' : 'LOGIN_FAILED';
'''

    def prepare_search_steps(self, keyword: str) -> List[Dict]:
        """准备搜索步骤"""
        return [
            {
                "action": "find_element",
                "selector_type": "css",
                "selector": "input[type='search'], input[name*='search'], .search-input, #search",
                "description": "定位搜索框"
            },
            {
                "action": "fill",
                "value": keyword,
                "description": "输入搜索关键词"
            },
            {
                "action": "submit",
                "description": "提交搜索"
            }
        ]

    def execute_search(self, keyword: str) -> str:
        """生成搜索执行脚本"""
        return f'''
// 搜索报告: {keyword}

// 1. 找到搜索框
const searchInput = document.querySelector('input[type="search"], input[name*="search"], .search-input, input[id*="search"]');

// 2. 输入关键词
if (searchInput) {{
    searchInput.value = '{keyword}';
    searchInput.dispatchEvent(new Event('input'));
}}

// 3. 执行搜索
const searchBtn = document.querySelector('button[type="submit"], .search-btn, button:has-text("搜索")');
if (searchBtn) {{
    searchBtn.click();
}} else {{
    // 回车提交
    searchInput && searchInput.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Enter'}}));
}}

// 4. 等待结果加载
await new Promise(r => setTimeout(r, 2000));

// 5. 收集搜索结果
const results = [];
const items = document.querySelectorAll('.report-item, .doc-item, .list-item, article, [class*="report"]');
items.forEach((item, index) => {{
    const title = item.querySelector('h3, h4, .title, a')?.textContent?.trim() || '';
    const date = item.querySelector('.date, .time, span:last-child')?.textContent?.trim() || '';
    const link = item.querySelector('a[href]')?.href || '';
    if (title && link) {{
        results.push({{index: index + 1, title, date, link}});
    }}
}});

return JSON.stringify({{count: results.length, results: results.slice(0, 20)}});
'''

    def execute_download(self, report_link: str, filename: str) -> str:
        """生成下载执行脚本"""
        safe_filename = re.sub(r'[^\w\u4e00-\u9fff-]', '_', filename)[:100]
        return f'''
// 下载报告: {filename}

// 1. 导航到报告页面
window.open('{report_link}', '_blank');
await new Promise(r => setTimeout(r, 3000));

// 2. 查找下载按钮
const downloadBtn = document.querySelector('a[href*="download"], button[class*="download"], .download-btn');
if (downloadBtn) {{
    downloadBtn.click();
}}

// 3. 等待下载
await new Promise(r => setTimeout(r, 2000));

return 'DOWNLOAD_INITIATED: {safe_filename}';
'''

    def prepare_download_url_extraction(self) -> str:
        """提取真实下载链接的脚本"""
        return '''
// 提取PDF下载链接
const links = document.querySelectorAll('a[href*=".pdf"], a[href*="download"]');
const pdfLinks = [];

links.forEach(link => {
    const href = link.href;
    if (href && (href.includes('.pdf') || href.includes('download'))) {
        pdfLinks.push({
            text: link.textContent?.trim() || 'Download PDF',
            url: href
        });
    }
});

return JSON.stringify(pdfLinks);
'''

    def format_search_results(self, results_json: str) -> str:
        """格式化搜索结果用于展示"""
        try:
            data = json.loads(results_json)
            if not data.get('results'):
                return "未找到相关报告"

            output = [f"**找到 {data['count']} 篇相关报告：**\n"]
            output.append("| 序号 | 报告标题 | 日期 |")
            output.append("|------|----------|------|")

            for item in data['results']:
                title = item['title'][:50] + ('...' if len(item['title']) > 50 else '')
                output.append(f"| {item['index']} | {title} | {item['date']} |")

            return '\n'.join(output)
        except Exception as e:
            return f"结果解析失败: {str(e)}"

    def generate_download_script(self, report_title: str, report_url: str) -> str:
        """为单个报告生成下载脚本"""
        safe_title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', report_title)[:50]
        return f'''
// 下载: {safe_title}
window.location.href = '{report_url}';
await new Promise(r => setTimeout(r, 3000));

// 查找并点击下载按钮
const btn = document.querySelector('.download, [class*="down"]');
if (btn) btn.click();
'''

    def save_report_metadata(self, reports: List[Dict], output_file: str = "download_records.json") -> None:
        """保存下载记录到JSON文件"""
        download_dir = Path(self.DOWNLOAD_DIR)
        download_dir.mkdir(parents=True, exist_ok=True)

        record_file = download_dir / output_file
        with open(record_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_reports": len(reports),
                "reports": reports
            }, f, ensure_ascii=False, indent=2)

    def create_summary(self, reports: List[Dict]) -> str:
        """生成下载摘要"""
        if not reports:
            return "未下载任何报告"

        summary = ["**下载完成！**\n", f"共下载 {len(reports)} 篇报告：\n"]
        for i, report in enumerate(reports, 1):
            title = report.get('title', '未知标题')[:40]
            path = report.get('filepath', '未知路径')
            summary.append(f"{i}. **{title}**")
            summary.append(f"   📁 路径: `{path}`\n")

        summary.append("\n输入 `read [序号]` 可详细阅读某篇报告")
        return '\n'.join(summary)


def create_workflow_steps(action: str, params: Dict) -> List[Dict]:
    """根据操作类型创建工作流步骤"""
    workflows = {
        "login": [
            {"step": 1, "action": "navigate", "target": "https://www.sgpjbg.com"},
            {"step": 2, "action": "click", "target": "登录按钮"},
            {"step": 3, "action": "input", "target": "用户名", "value": params.get("username")},
            {"step": 4, "action": "input", "target": "密码", "value": "***"},
            {"step": 5, "action": "click", "target": "登录确认"}
        ],
        "search": [
            {"step": 1, "action": "click", "target": "搜索框"},
            {"step": 2, "action": "input", "target": "搜索关键词", "value": params.get("keyword")},
            {"step": 3, "action": "click", "target": "搜索按钮"}
        ],
        "download": [
            {"step": 1, "action": "click", "target": "报告链接"},
            {"step": 2, "action": "click", "target": "下载PDF按钮"},
            {"step": 3, "action": "wait", "duration": 3}
        ]
    }
    return workflows.get(action, [])


if __name__ == "__main__":
    # 测试脚本
    reporter = SgpjbgReporter()
    print("三个皮匠报告自动化助手已就绪")
    print(f"下载目录: {reporter.DOWNLOAD_DIR}")