#!/usr/bin/env python3
"""
Skill 安全扫描器 - 快速验证脚本
检测 Skill 文件中的安全漏洞、信息泄露和恶意代码模式
"""

import os
import re
import json
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

# 风险等级
RiskLevel = {
    "critical": "[CRITICAL] Critical",
    "high": "[HIGH] High",
    "medium": "[MEDIUM] Medium",
    "low": "[LOW] Low"
}


@dataclass
class SecurityFinding:
    """安全发现"""
    level: str  # critical, high, medium, low
    category: str  # 信息泄露, 代码漏洞, 文件结构, 依赖安全
    file: str
    line: Optional[int] = None
    description: str = ""
    pattern: str = ""
    recommendation: str = ""

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "category": self.category,
            "file": self.file,
            "line": self.line,
            "description": self.description,
            "pattern": self.pattern,
            "recommendation": self.recommendation
        }


class SecurityScanner:
    """安全扫描器"""

    def __init__(self):
        self.findings: List[SecurityFinding] = []

        # 1. 信息泄露检测规则
        self.secret_patterns = [
            # API Keys
            (r'(?i)(api[_-]?key|apikey|secret[_-]?key)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]{20,}', "API Key 泄露", "critical"),
            (r'(?i)(password|passwd|pwd|token|auth_token|bearer)\s*[:=]\s*["\']?[^"\s]{8,}', "凭证泄露", "critical"),
            (r'(?i)sk-[a-zA-Z0-9]{48}', "OpenAI API Key 泄露", "critical"),
            (r'ghp_[a-zA-Z0-9]{36}', "GitHub Token 泄露", "critical"),
            (r'AKIA[A-Z0-9]{16}', "AWS Access Key 泄露", "critical"),
            (r'(?i)xox[baprs]-[0-9]{10,}', "Slack Token 泄露", "critical"),

            # 私钥
            (r'-----BEGIN (RSA |DSA |EC |OPENSSH |PGP )?PRIVATE KEY-----', "私钥泄露", "critical"),

            # 连接字符串
            (r'(?i)(mongodb|mysql|postgres|redis):\/\/[^\s]+:[^\s]+@[^\s]+', "数据库连接字符串泄露", "critical"),

            # 硬编码凭证
            (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9/+=]{40}', "AWS Secret Key 泄露", "critical"),

            # 环境变量名泄露
            (r'\$\{?[A-Z_][A-Z0-9_]*\}\$?', "环境变量引用泄露风险", "medium"),
        ]

        # 2. 代码漏洞检测规则
        self.vulnerability_patterns = [
            # 命令注入
            (r'\beval\s*\(', "使用 eval() 可能导致代码注入", "critical"),
            (r'\bexec\s*\(', "使用 exec() 可能导致代码注入", "critical"),
            (r'subprocess\.(run|call|Popen|check_output)\s*\([^)]*\b(?:shell|cmd)\s*=\s*True', "subprocess 使用 shell=True 可能导致命令注入", "critical"),
            (r'os\.system\s*\(', "os.system() 可能导致命令注入", "critical"),
            (r'os\.popen\s*\(', "os.popen() 可能导致命令注入", "high"),
            (r'\b__import__\s*\(', "动态导入可能存在代码注入风险", "high"),

            # 路径遍历
            (r'\.\.\/|[\\/]\.\.[\\/]', "检测到路径遍历模式 ../", "high"),
            (r'open\s*\([^)]*\+[^)]*\.\.[\\/]', "文件操作中的路径遍历风险", "high"),
            (r'Path\s*\([^)]*\+[^)]*\.parent', "Path 操作中的路径遍历风险", "medium"),

            # 不安全反序列化
            (r'pickle\.loads?\s*\(', "使用 pickle.loads() 不安全，可能导致代码执行", "critical"),
            (r'yaml\.load\s*\([^)]*(?!Loader=yaml\.SafeLoader\)', "yaml.load() 不安全，应使用 SafeLoader", "high"),
            (r'marshal\.loads\s*\(', "marshal.loads() 不安全", "high"),
            (r'\.from_json\s*\([^)]*\)\.parse\s*\(', "不安全的 JSON 解析", "medium"),

            # 危险的系统调用
            (r'os\.chmod\s*\([^)]*0o?7', "过于宽松的文件权限 chmod 777", "high"),
            (r'os\.chmod\s*\([^)]*0o?666', "过于宽松的文件权限 chmod 666", "medium"),
            (r'shutil\.rmtree\s*\([^)]*\+[^)]*\)', "递归删除存在路径遍历风险", "high"),
            (r'shutil\.copytree\s*\([^)]*\+[^)]*\)', "拷贝操作存在路径遍历风险", "medium"),

            # 网络请求风险
            (r'requests\.(get|post)\s*\([^)]*verify\s*=\s*False', "SSL 验证被禁用", "high"),
            (r'urllib3\.disable_warnings', "禁用安全警告", "medium"),
            (r'httpx|aiohttp.*verify\s*=\s*False', "HTTP 客户端禁用 SSL 验证", "high"),

            # 潜在的恶意代码模式
            (r'base64\.b64decode\s*\([^)]*\)\s*\.decode\s*\(\s*\)', "Base64 解码后执行可能为 shellcode", "critical"),
            (r'zlib\.decompress\s*\(', "压缩数据解码可能隐藏恶意代码", "medium"),
            (r'socket\.create_connection\s*\(', "创建网络连接可能用于远控", "medium"),
            (r'threading\.Thread\s*\([^)]*daemon\s*=\s*True', "守护线程可能用于隐藏后门", "high"),
        ]

        # 3. 上传/下载相关检测
        self.upload_patterns = [
            (r'(?i)(upload|write|save).*(?:file|path|content)', "文件上传操作 - 需验证路径安全性", "high"),
            (r'(?i)(download|fetch|get).*(?:file|content|remote)', "文件下载操作 - 需验证来源可靠性", "medium"),
            (r'Content-Disposition.*filename', "HTTP 文件名解析可能存在路径穿越", "high"),
            (r'multipart/form-data', "文件上传表单检测", "medium"),
            (r'Content-Type.*octet-stream', "二进制上传检测", "medium"),
            (r'glob\.glob\s*\([^)]*\*', "通配符文件操作可能访问意外文件", "medium"),
        ]

        # 4. 文件结构异常规则
        self.structure_patterns = [
            # 符号链接逃逸
            (r'symlink|is_symlink|link_to', "符号链接可能用于逃逸", "high"),
            # 隐藏文件
            (r'^\..*', "隐藏文件检测", "medium"),
            # 可执行脚本
            (r'\.sh$|\.bash$|\.zsh$', "Shell 脚本检测", "medium"),
            (r'#!/bin/(ba)?sh', "Shebang 检测到 shell 脚本", "medium"),
            (r'chmod\s*\+x', "动态修改执行权限", "medium"),
        ]

    def scan_file(self, file_path: str, content: str) -> List[SecurityFinding]:
        """扫描单个文件"""
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # 跳过注释行（但保留在 context 中）
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//'):
                continue

            # 检测秘密泄露
            for pattern, desc, level in self.secret_patterns:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        level=level,
                        category="信息泄露",
                        file=file_path,
                        line=line_num,
                        description=desc,
                        pattern=pattern,
                        recommendation="将敏感信息移至环境变量或安全的密钥管理服务"
                    ))

            # 检测代码漏洞
            for pattern, desc, level in self.vulnerability_patterns:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        level=level,
                        category="代码漏洞",
                        file=file_path,
                        line=line_num,
                        description=desc,
                        pattern=pattern,
                        recommendation=get_recommendation(desc)
                    ))

            # 检测上传/下载相关
            for pattern, desc, level in self.upload_patterns:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        level=level,
                        category="上传下载",
                        file=file_path,
                        line=line_num,
                        description=desc,
                        pattern=pattern,
                        recommendation="确保文件来源和目标路径经过严格验证"
                    ))

        return findings

    def scan_directory(self, base_path: str, exclude_patterns: List[str] = None) -> List[SecurityFinding]:
        """扫描目录"""
        if exclude_patterns is None:
            exclude_patterns = ['node_modules', '.git', '__pycache__', '.venv', 'venv', 'dist', 'build']

        findings = []
        base = Path(base_path)

        for path in base.rglob('*'):
            # 跳过排除目录
            if any(excl in str(path) for excl in exclude_patterns):
                continue

            # 检测文件结构问题
            rel_path = path.relative_to(base)

            # 符号链接检测
            if path.is_symlink():
                target = path.resolve()
                if not str(target).startswith(str(base.resolve())):
                    findings.append(SecurityFinding(
                        level="critical",
                        category="文件结构",
                        file=str(rel_path),
                        description="符号链接逃逸 - 链接指向工作目录之外",
                        recommendation="移除符号链接或确保链接指向安全路径"
                    ))

            # 隐藏文件检测
            if path.name.startswith('.') and path.is_file():
                findings.append(SecurityFinding(
                    level="medium",
                    category="文件结构",
                    file=str(rel_path),
                    description="隐藏文件检测",
                    recommendation="确保隐藏文件不包含敏感信息"
                ))

            # 扫描文件内容
            if path.is_file() and path.stat().st_size < 10 * 1024 * 1024:  # 跳过大于 10MB 的文件
                try:
                    content = path.read_text(encoding='utf-8', errors='ignore')
                    findings.extend(self.scan_file(str(rel_path), content))
                except Exception:
                    pass

        return findings

    def scan_skill_package(self, skill_path: str) -> Dict:
        """扫描 Skill 包文件"""
        findings = []
        skill_path = Path(skill_path)

        # 解压 .skill 文件
        if skill_path.suffix == '.skill' or skill_path.is_file():
            try:
                with zipfile.ZipFile(skill_path, 'r') as zf:
                    temp_dir = skill_path.with_suffix('.tmp')
                    zf.extractall(temp_dir)
                    findings.extend(self.scan_directory(str(temp_dir)))
                    # 清理临时目录
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except zipfile.BadZipFile:
                # 尝试作为目录处理
                findings.extend(self.scan_directory(str(skill_path)))
        else:
            # 直接扫描目录
            findings.extend(self.scan_directory(str(skill_path)))

        return self.format_report(findings)

    def format_report(self, findings: List[SecurityFinding]) -> Dict:
        """格式化报告"""
        # 按等级分组
        by_level = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        by_category = {
            "信息泄露": [],
            "代码漏洞": [],
            "文件结构": [],
            "上传下载": []
        }

        for f in findings:
            by_level[f.level].append(f)
            by_category[f.category].append(f)

        return {
            "summary": {
                "total": len(findings),
                "critical": len(by_level["critical"]),
                "high": len(by_level["high"]),
                "medium": len(by_level["medium"]),
                "low": len(by_level["low"])
            },
            "by_level": {k: [f.to_dict() for f in v] for k, v in by_level.items()},
            "by_category": {k: [f.to_dict() for f in v] for k, v in by_category.items()},
            "findings": [f.to_dict() for f in findings]
        }


def get_recommendation(desc: str) -> str:
    """获取修复建议"""
    recommendations = {
        "使用 eval()": "避免使用 eval()，使用 ast.literal_eval() 或其他安全方式",
        "使用 exec()": "避免使用 exec()，考虑重构代码逻辑",
        "shell=True": "避免使用 shell=True，使用列表形式传递命令参数",
        "os.system()": "使用 subprocess.run() 配合列表参数",
        "pickle.loads()": "使用安全的序列化格式如 JSON，或使用 restricted unpickler",
        "yaml.load()": "使用 yaml.safe_load() 替代",
        "路径遍历": "使用 os.path.join() 和 pathlib 安全地处理路径",
        "API Key": "使用环境变量或密钥管理服务存储敏感信息",
        "私钥": "使用安全的密钥存储解决方案",
        "文件上传": "验证文件类型、大小和内容，禁止执行上传的文件",
        "网络连接": "验证连接目标，使用 HTTPS，确保 SSL 验证开启",
        "守护线程": "确保后台任务有适当的生命周期管理"
    }

    for key, rec in recommendations.items():
        if key in desc:
            return rec

    return "请检查代码逻辑，确保安全操作"


def main():
    """主函数 - CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Skill 安全扫描器')
    parser.add_argument('path', help='Skill 文件路径或目录')
    parser.add_argument('-o', '--output', help='输出 JSON 报告文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--no-colors', action='store_true', help='禁用颜色输出')

    args = parser.parse_args()

    scanner = SecurityScanner()
    report = scanner.scan_skill_package(args.path)

    # 输出报告
    output_report(report, args.output, args.verbose, args.no_colors)

    # 返回状态码
    return 0 if report['summary']['critical'] == 0 else 1


def output_report(report: Dict, output_file: str = None, verbose: bool = False, no_colors: bool = False):
    """输出报告"""
    # 输出到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"报告已保存至: {output_file}")

    # 控制台输出
    summary = report['summary']

    print("\n" + "=" * 50)
    print("[SCAN] Security Scan Report")
    print("=" * 50)

    # 风险摘要
    print(f"\n[STAT] Risk Summary:")
    print(f"   [CRITICAL] Critical: {summary['critical']}")
    print(f"   [HIGH] High: {summary['high']}")
    print(f"   [MEDIUM] Medium: {summary['medium']}")
    print(f"   [LOW] Low: {summary['low']}")
    print(f"   --------------------------------")
    print(f"   Total: {summary['total']}")

    # 详细发现
    if report['findings']:
        print(f"\n[LIST] Detailed Findings:")

        # 按等级排序输出
        for level in ['critical', 'high', 'medium', 'low']:
            findings = report['by_level'].get(level, [])
            if not findings:
                continue

            level_name = {
                'critical': 'Critical',
                'high': 'High',
                'medium': 'Medium',
                'low': 'Low'
            }.get(level, level)

            print(f"\n[{level.upper()}] {level_name} ({len(findings)} items):")

            for f in findings:
                loc = f"Line {f['line']}" if f['line'] else ""
                print(f"   - {f['file']} {loc}")
                print(f"     {f['description']}")
                if verbose:
                    print(f"     Recommendation: {f['recommendation']}")

    # 结论
    print("\n" + "-" * 50)
    if summary['critical'] > 0:
        print("[WARNING] Critical security issues detected. Please fix before installation.")
    elif summary['high'] > 0:
        print("[WARNING] Medium security issues detected. Please review and fix.")
    elif summary['total'] > 0:
        print("[OK] Scan complete. Low-risk issues found.")
    else:
        print("[OK] No obvious security issues detected.")


if __name__ == '__main__':
    exit(main())
