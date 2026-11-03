#!/usr/bin/env python3
"""
技能安全扫描器 (Skill-Vetter-Scan)
自动扫描技能目录，进行安全审计、风险评分和安装建议
版本: 2.0.0 - 优化版（白名单 + 通俗报告）
"""

import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ============================================================
# 技能白名单 - 这些技能/目录不会被扫描
# ============================================================
SKILL_WHITELIST = [
    "skill-vetter-scan",      # 自身，跳过扫描
    "skill-blacklist",        # 黑名单管理
    "skill-install-confirm",  # 安装确认
]

# 文件白名单 - 这些文件不会被扫描
FILE_WHITELIST = [
    "_meta.json",             # 元数据文件
    "package.json",           # npm配置
    "requirements.txt",       # Python依赖
    "README.md",              # 说明文档
    "LICENSE",                # 许可证
    ".gitignore",             # Git忽略
]

# ============================================================
# 可疑关键词库（分级 + 通俗解释）
# ============================================================
SUSPICIOUS_KEYWORDS = {
    "严重": [
        # 危险操作 - 可能执行任意命令
        (r'eval\s*\(', -25, "危险代码执行",
         "🚨 能执行任意代码，可能是病毒或木马"),
        (r'exec\s*\(', -25, "危险代码执行",
         "🚨 能执行任意代码，可能是病毒或木马"),
        (r'os\.system\s*\(', -25, "执行系统命令",
         "🚨 能在你电脑上运行任何命令，如删除文件"),
        (r'subprocess\.call\s*\(', -25, "执行系统命令",
         "🚨 能在你电脑上运行任何命令"),
        (r'subprocess\.run\s*\(', -25, "执行系统命令",
         "🚨 能在你电脑上运行任何命令"),
        (r'subprocess\.Popen\s*\(', -25, "执行系统命令",
         "🚨 能在你电脑上运行任何命令"),
        # 动态加载 - 可能偷偷加载恶意代码
        (r'__import__\s*\(', -25, "动态加载代码",
         "🚨 可以偷偷加载未知代码，不知道会做什么"),
        (r'importlib', -25, "动态加载代码",
         "🚨 可以偷偷加载未知代码"),
        (r'pty\.spawn', -25, "创建虚拟终端",
         "🚨 可能用于提权攻击"),
    ],
    "高危": [
        # 网络请求 - 可能外传数据
        (r'requests\.get\s*\(', -20, "发起网络请求",
         "⚠️ 能访问网络，可能把你的数据发到外面"),
        (r'requests\.post\s*\(', -20, "发送网络数据",
         "⚠️ 能把你的数据发送到外部服务器"),
        (r'requests\.(put|delete|patch|head|options)\s*\(', -20, "网络数据操作",
         "⚠️ 能与外部服务器通信"),
        (r'urllib\.request', -20, "发起网络请求",
         "⚠️ 能访问网络"),
        (r'http\.client', -20, "HTTP客户端",
         "⚠️ 能进行网络通信"),
        (r'socket\.create_connection', -20, "建立网络连接",
         "⚠️ 能建立网络连接，可能是后门"),
        (r'socket\.connect', -20, "连接远程地址",
         "⚠️ 能连接外部服务器"),
        # 下载执行 - 可能下载恶意程序
        (r'\bcurl\s+', -20, "下载网络资源",
         "⚠️ 能从网上下载东西，可能是病毒"),
        (r'\bwget\s+', -20, "下载网络资源",
         "⚠️ 能从网上下载东西，可能是病毒"),
        (r'\bpip\s+install', -15, "安装Python包",
         "⚠️ 能安装软件包，可能是恶意程序"),
        (r'\bnpm\s+install', -15, "安装npm包",
         "⚠️ 能安装npm包，可能是恶意程序"),
    ],
    "中危": [
        # 权限操作 - 可能提权
        (r'\bchmod\s+', -15, "修改文件权限",
         "⚠️ 能改变文件访问权限，可能绕过安全限制"),
        (r'\bchown\s*\(', -15, "修改文件所有者",
         "⚠️ 能改变文件所有者，可能获取更高权限"),
        (r'\bsudo\s+', -15, "使用管理员权限",
         "⚠️ 尝试获取管理员权限"),
        (r'chattr', -15, "修改文件属性",
         "⚠️ 能锁定或解锁文件，可能保护恶意文件"),
        # 持久化 - 可能在系统启动时自动运行
        (r'\.bashrc', -15, "修改Shell配置",
         "⚠️ 能让恶意程序开机自动运行"),
        (r'\.bash_profile', -15, "修改Shell配置",
         "⚠️ 能让恶意程序开机自动运行"),
        (r'\.zshrc', -15, "修改Shell配置",
         "⚠️ 能让恶意程序开机自动运行"),
        (r'\.ssh/', -15, "访问SSH配置",
         "⚠️ 可能配置SSH后门或窃取SSH密钥"),
        # 系统信息收集
        (r'/etc/passwd', -15, "读取系统账户",
         "⚠️ 能获取系统用户列表"),
        (r'/etc/shadow', -15, "读取密码文件",
         "⚠️ 能获取用户密码哈希，有密码泄露风险"),
    ],
    "低危": [
        # 文件操作 - 可能是正当用途，也可能是数据窃取
        (r'open\s*\([^)]*[\'\"][wa][\'\"]', -5, "写入文件",
         "📝 能创建或修改文件，需要确认用途"),
        (r'\.write\s*\(', -5, "写入数据",
         "📝 能向文件写入数据"),
        (r'\.writelines\s*\(', -5, "批量写入",
         "📝 能批量写入文件"),
        # 编码压缩 - 可能是正当用途，也可能是混淆
        (r'base64', -3, "使用Base64编码",
         "📝 对数据进行编码，可能是正当用途"),
        (r'gzip', -3, "使用Gzip压缩",
         "📝 压缩数据，可能是正当用途"),
        (r'zlib', -3, "使用Zlib压缩",
         "📝 压缩数据，可能是正当用途"),
        # 文件操作
        (r'\bos\.remove\s*\(', -10, "删除文件",
         "🗑️ 能删除文件，请确认用途"),
        (r'\bos\.unlink\s*\(', -10, "删除文件",
         "🗑️ 能删除文件，请确认用途"),
        (r'\bos\.rmdir\s*\(', -10, "删除目录",
         "🗑️ 能删除目录，请确认用途"),
        (r'\bshutil\.rmtree\s*\(', -15, "删除目录树",
         "🗑️⚠️ 能删除整个目录，后果严重"),
    ]
}

# 风险等级映射（中文友好）
RISK_LEVELS = [
    (81, 100, "安全", "🟢", "✅ 放心使用"),
    (61, 80, "注意", "🟡", "⚠️ 可以使用，但要注意观察"),
    (41, 60, "警告", "🟠", "⚠️⚠️ 建议先测试再使用"),
    (21, 40, "危险", "🔶", "🚫 不建议安装，请先查看代码"),
    (0, 20, "高危", "🔴", "🚫🚫 危险！强烈建议不要安装"),
]

# 扫描文件类型
SCAN_EXTENSIONS = ['.py', '.json', '.js', '.yaml', '.yml', '.sh', '.md']


def is_whitelisted(filepath: str) -> bool:
    """检查文件是否在白名单中"""
    basename = os.path.basename(filepath)

    # 检查文件白名单
    if basename in FILE_WHITELIST:
        return True

    # 检查技能白名单（通过目录路径判断）
    path_parts = filepath.split(os.sep)
    for skill_name in SKILL_WHITELIST:
        if skill_name in path_parts:
            return True

    return False


def find_skills_directory() -> Optional[str]:
    """查找技能目录"""
    default_dir = "/workspace/.minimax/skills/"
    if os.path.isdir(default_dir):
        return default_dir

    possible_dirs = [
        "/workspace/skills/",
        "/workspace/.skills/",
        "/workspace/temp-skills/",
    ]

    for d in possible_dirs:
        if os.path.isdir(d):
            return d

    return None


def get_file_type(filename: str) -> str:
    """获取文件类型中文描述"""
    ext = os.path.splitext(filename)[1].lower()
    type_map = {
        '.py': 'Python代码',
        '.json': '配置文件',
        '.js': 'JavaScript代码',
        '.yaml': '配置文件',
        '.yml': '配置文件',
        '.sh': 'Shell脚本',
        '.md': '说明文档',
    }
    return type_map.get(ext, '其他文件')


def get_action_type(risk_points: List[Dict]) -> Tuple[str, str]:
    """
    根据风险点判断操作类型
    返回: (操作类型描述, 警告级别)
    """
    has_execution = False      # 是否有执行命令
    has_permission = False     # 是否有权限操作
    has_file_change = False    # 是否有文件修改/删除
    has_network = False        # 是否有网络操作
    has_readonly = False       # 是否只是读取

    for point in risk_points:
        desc = point.get("description", "")
        if "执行" in desc or "代码" in desc:
            has_execution = True
        if "权限" in desc or "sudo" in desc or "chmod" in desc:
            has_permission = True
        if "删除" in desc or "写入" in desc or "修改" in desc:
            has_file_change = True
        if "网络" in desc or "请求" in desc or "发送" in desc:
            has_network = True
        if "读取" in desc:
            has_readonly = True

    if has_file_change:
        return "🔴 文件操作", "会修改或删除文件，请特别注意"
    elif has_execution:
        return "🟠 程序执行", "会运行程序或命令，请注意"
    elif has_permission:
        return "🟠 权限操作", "会修改系统权限，请注意"
    elif has_network:
        return "🟡 网络通信", "会访问网络，确认用途后再使用"
    else:
        return "📖 读取操作", "只是读取文件，安全"


def scan_file(filepath: str) -> Tuple[int, List[Dict], str]:
    """
    扫描单个文件
    返回: (风险评分, 风险点列表, 文件内容)
    """
    # 检查白名单
    if is_whitelisted(filepath):
        return 100, [], "（白名单文件，已跳过详细扫描）"

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return 100, [], ""

    score = 100
    risk_points = []

    # 关键词检查
    for level in ["严重", "高危", "中危", "低危"]:
        for item in SUSPICIOUS_KEYWORDS.get(level, []):
            if len(item) == 4:
                pattern, penalty, keyword, human_desc = item
            else:
                pattern, penalty, human_desc = item
                keyword = pattern

            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                score += penalty * len(matches)
                for match in matches[:3]:  # 最多显示3个匹配
                    risk_points.append({
                        "level": level,
                        "keyword": keyword,
                        "description": human_desc,
                        "technical": str(item[2]) if len(item) > 2 else "",
                        "penalty": penalty
                    })

    # 确保分数在0-100范围内
    score = max(0, min(100, score))

    return score, risk_points, content


def get_risk_level(score: int) -> Tuple[str, str, str]:
    """获取风险等级信息"""
    for min_score, max_score, level_name, icon, suggestion in RISK_LEVELS:
        if min_score <= score <= max_score:
            return level_name, icon, suggestion
    return "未知", "⚪", "无法判断"


def generate_report(
    scan_dir: str,
    results: List[Dict],
    total_files: int,
    skipped_files: int = 0
) -> str:
    """生成通俗易懂的Markdown报告"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 统计各风险等级数量
    stats = {"安全": 0, "注意": 0, "警告": 0, "危险": 0, "高危": 0}
    action_stats = {"文件操作": 0, "程序执行": 0, "权限操作": 0, "网络通信": 0, "读取操作": 0}

    for r in results:
        level = r["level_name"]
        if level in stats:
            stats[level] += 1

        action_type, _ = get_action_type(r["risk_points"])
        if action_type in action_stats:
            action_stats[action_type] += 1

    # 总体建议
    if stats["高危"] > 0 or stats["危险"] > 0:
        overall_suggestion = "🚫 存在危险技能，不建议安装"
        overall_level = "danger"
    elif stats["警告"] > 0:
        overall_suggestion = "⚠️ 存在风险技能，请谨慎操作"
        overall_level = "warning"
    elif stats["注意"] > 0:
        overall_suggestion = "⚠️ 基本安全，但需注意观察"
        overall_level = "caution"
    else:
        overall_suggestion = "✅ 所有技能安全，可以放心使用"
        overall_level = "safe"

    # 生成报告
    report = f"""# 🛡️ 技能安全检查报告

**扫描时间:** {now}
**扫描目录:** `{scan_dir}`
**扫描文件:** {total_files} 个 | **跳过文件:** {skipped_files} 个（白名单）

---

## 📊 安全概览

"""

    # 图标展示
    if overall_level == "danger":
        report += "### 🚫 整体评估：不安全\n\n"
    elif overall_level == "warning":
        report += "### ⚠️ 整体评估：需注意\n\n"
    elif overall_level == "caution":
        report += "### ⚡ 整体评估：基本安全\n\n"
    else:
        report += "### ✅ 整体评估：安全可靠\n\n"

    report += f"**总体建议:** {overall_suggestion}\n\n"

    # 风险分布
    report += """### 风险分布

| 等级 | 数量 | 状态 |
|------|------|------|
"""
    for level, icon_suggest in [
        ("🟢 安全", "✅ 放心使用"),
        ("🟡 注意", "⚠️ 注意观察"),
        ("🟠 警告", "⚠️⚠️ 先测试"),
        ("🔶 危险", "🚫 不建议"),
        ("🔴 高危", "🚫🚫 危险")
    ]:
        level_key = level.split()[1]  # 提取"安全"、"注意"等
        count = stats.get(level_key, 0)
        status = "✅ 无" if count == 0 else f"⚠️ {count}个"
        report += f"| {level} | {status} | {icon_suggest} |\n"

    # 操作类型统计
    report += """
### 操作类型分析

"""

    has_dangerous = False
    for action_type, desc in action_stats.items():
        if desc > 0:
            if "文件" in action_type or "执行" in action_type:
                has_dangerous = True
                report += f"- {action_type}: **{desc} 个文件** ⚠️ 需要关注\n"
            elif "权限" in action_type:
                has_dangerous = True
                report += f"- {action_type}: **{desc} 个文件** ⚠️ 需要关注\n"
            else:
                report += f"- {action_type}: {desc} 个文件\n"

    if has_dangerous:
        report += "\n> 💡 **提示**: 含有文件操作或程序执行的技能，请仔细确认用途后再安装。\n"

    report += """
---

## 📋 详细结果

"""

    # 按风险等级排序（从高到低）
    sorted_results = sorted(results, key=lambda x: x["score"])

    for result in sorted_results:
        level_name = result["level_name"]
        score = result["score"]

        # 选择合适的图标
        if score >= 81:
            icon = "🟢"
        elif score >= 61:
            icon = "🟡"
        elif score >= 41:
            icon = "🟠"
        elif score >= 21:
            icon = "🔶"
        else:
            icon = "🔴"

        action_type, action_desc = get_action_type(result["risk_points"])

        report += f"""### {icon} {os.path.basename(result['file'])} ({score}/100分)

| 项目 | 内容 |
|------|------|
| **安全等级** | {level_name} |
| **文件类型** | {result['file_type']} |
| **操作类型** | {action_type} |
| **安装建议** | {result['suggestion']} |

"""

        if result['risk_points']:
            report += f"**⚠️ 发现 {len(result['risk_points'])} 个需要注意的地方:**\n\n"
            for i, point in enumerate(result['risk_points'], 1):
                # 根据等级选择颜色
                if point['level'] == '严重':
                    level_icon = "🔴"
                elif point['level'] == '高危':
                    level_icon = "🟠"
                elif point['level'] == '中危':
                    level_icon = "🟡"
                else:
                    level_icon = "📝"

                report += f"{i}. {level_icon} **{point['description']}**\n"
                report += f"   └─ 具体问题: `{point['keyword']}`\n\n"
        else:
            report += "**✅ 未发现可疑内容**\n"

        report += "---\n\n"

    # 简洁汇总表
    report += """## 📊 一目了然

| 文件名 | 类型 | 安全 | 操作 | 建议 |
|--------|------|------|------|------|
"""

    for result in sorted_results:
        filename = os.path.basename(result['file'])
        file_type = result['file_type']
        score = result['score']

        if score >= 81:
            level_icon = "🟢安全"
        elif score >= 61:
            level_icon = "🟡注意"
        elif score >= 41:
            level_icon = "🟠警告"
        elif score >= 21:
            level_icon = "🔶危险"
        else:
            level_icon = "🔴高危"

        action_type, _ = get_action_type(result["risk_points"])
        suggestion = result['suggestion'].replace("✅", "").replace("⚠️", "").replace("🚫", "").strip()

        report += f"| {filename} | {file_type} | {score} | {action_type} | {suggestion} |\n"

    report += f"""

---

## 💡 安全小贴士

1. **🟢 绿色(安全)**: 可以直接安装使用
2. **🟡 黄色(注意)**: 可以安装，但留意使用过程中的异常
3. **🟠 橙色(警告)**: 建议先在测试环境运行，确认无误后再正式使用
4. **🔴 红色(危险)**: 不建议安装，请先查看源码或联系开发者确认

---

*📅 报告生成时间: {now}*
*🔒 扫描工具: Skill-Vetter-Scan v2.0.0*
"""

    return report


def scan_directory(target_dir: Optional[str] = None) -> Dict:
    """
    扫描技能目录
    返回扫描结果字典
    """
    if target_dir is None:
        target_dir = find_skills_directory()

    if target_dir is None:
        return {
            "success": False,
            "error": "❌ 未找到技能目录，请确认技能已安装或目录路径正确",
            "scan_dir": None,
            "results": [],
            "total_files": 0,
            "skipped_files": 0
        }

    if not os.path.isdir(target_dir):
        return {
            "success": False,
            "error": f"❌ 指定的目录不存在: {target_dir}",
            "scan_dir": target_dir,
            "results": [],
            "total_files": 0,
            "skipped_files": 0
        }

    results = []
    scanned_files = 0
    skipped_files = 0

    # 遍历目录
    for root, dirs, files in os.walk(target_dir):
        # 跳过隐藏目录
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for filename in files:
            filepath = os.path.join(root, filename)

            # 只扫描指定类型的文件
            ext = os.path.splitext(filename)[1].lower()
            if ext not in SCAN_EXTENSIONS:
                continue

            # 跳过白名单
            if is_whitelisted(filepath):
                skipped_files += 1
                continue

            scanned_files += 1
            score, risk_points, _ = scan_file(filepath)
            level_name, icon, suggestion = get_risk_level(score)

            results.append({
                "file": filepath,
                "file_type": get_file_type(filename),
                "score": score,
                "level_name": level_name,
                "icon": icon,
                "suggestion": suggestion,
                "risk_points": risk_points
            })

    # 生成报告
    report = generate_report(target_dir, results, scanned_files, skipped_files)

    # 保存报告
    report_dir = "/workspace/.minimax"
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "技能安全检查报告.md")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    return {
        "success": True,
        "scan_dir": target_dir,
        "report_path": report_path,
        "results": results,
        "total_files": scanned_files,
        "skipped_files": skipped_files,
        "report": report
    }


def print_summary(result: Dict):
    """打印摘要到控制台"""
    if not result["success"]:
        print(f"\n{result['error']}")
        return

    print(f"\n{'='*60}")
    print(f"🛡️ 技能安全扫描完成")
    print(f"{'='*60}")
    print(f"📂 扫描目录: {result['scan_dir']}")
    print(f"📄 扫描文件: {result['total_files']} 个")
    print(f"⏭️  跳过文件: {result['skipped_files']} 个（白名单）")
    print(f"📋 报告已保存: {result['report_path']}")
    print(f"{'='*60}\n")

    # 统计
    stats = {}
    for r in result["results"]:
        level = r["level_name"]
        stats[level] = stats.get(level, 0) + 1

    # 快速判断
    if stats.get("高危", 0) > 0 or stats.get("危险", 0) > 0:
        print("🚫 状态: 存在危险技能，不建议安装\n")
    elif stats.get("警告", 0) > 0:
        print("⚠️ 状态: 存在风险技能，请谨慎\n")
    elif stats.get("注意", 0) > 0:
        print("⚡ 状态: 基本安全，但需注意\n")
    else:
        print("✅ 状态: 所有技能安全可靠\n")

    # 高风险文件
    critical = [r for r in result["results"] if r["score"] < 40]
    if critical:
        print(f"🚨 需要关注的文件 ({len(critical)} 个):")
        for r in critical:
            action_type, _ = get_action_type(r["risk_points"])
            print(f"  - {os.path.basename(r['file'])} {action_type}")
        print()

    print(f"📖 详细报告请查看: {result['report_path']}")


def main():
    """主函数"""
    target_dir = sys.argv[1] if len(sys.argv) > 1 else None

    if target_dir == "--help" or target_dir == "-h":
        print("""
🛡️ 技能安全扫描器 (Skill-Vetter-Scan v2.0.0)

用法:
  python scan_skills.py [目标目录]

功能:
  • 自动跳过白名单文件（如自身skill-vetter-scan）
  • 生成通俗易懂的安全报告
  • 风险分级：安全/注意/警告/危险/高危

示例:
  python scan_skills.py                              # 扫描默认目录
  python scan_skills.py /workspace/.minimax/skills/  # 扫描指定目录
        """)
        sys.exit(0)

    print(f"\n🔍 正在扫描技能目录...")

    if target_dir:
        print(f"📂 目标目录: {target_dir}")

    result = scan_directory(target_dir)
    print_summary(result)

    if result["success"]:
        print("\n" + "="*60)
        print("📋 完整报告:")
        print("="*60)
        print(result["report"])


if __name__ == "__main__":
    main()
