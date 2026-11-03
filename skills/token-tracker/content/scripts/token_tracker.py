#!/usr/bin/env python3
"""
Token 消耗追踪器
用法: python3 token_tracker.py [report|status]
"""

import json
import os
from datetime import datetime
from pathlib import Path

MEMORY_DIR = Path("/workspace/memory/token-usage")
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def get_today_file():
    """获取今日日志文件"""
    today = datetime.now().strftime("%Y-%m-%d")
    return MEMORY_DIR / f"{today}.md"

def format_size(tokens):
    """格式化 token 数量"""
    if tokens >= 1000:
        return f"{tokens/1000:.1f}K"
    return str(tokens)

def get_session_status():
    """获取当前会话状态"""
    # 这个需要在 OpenClaw 运行时通过 session_status 工具获取
    return {
        "in_tokens": 0,
        "out_tokens": 0,
        "total_tokens": 0,
        "cost": 0,
        "context_percent": 0
    }

def generate_report():
    """生成消耗报告"""
    today_file = get_today_file()
    
    report = f"""# Token 消耗报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 今日汇总

"""
    
    if today_file.exists():
        with open(today_file, 'r') as f:
            content = f.read()
            report += f"```\n{content}\n```\n"
    else:
        report += "暂无记录\n"
    
    # 列出所有历史文件
    files = sorted(MEMORY_DIR.glob("*.md"), reverse=True)[:7]
    
    report += f"""
## 最近 7 天

| 日期 | 文件 |
|------|------|
"""
    for f in files:
        report += f"| {f.stem} | {f.name} |\n"
    
    return report

def analyze_usage():
    """分析使用情况"""
    # 简单分析 - 后续可以扩展
    return """
## 消耗分析

### 低消耗操作 (推荐)
- 读取小文件
- 短搜索查询
- 简单计算

### 高消耗操作 (注意)
- 浏览器截屏/操作
- 生成长报告
- 大文件处理

### 优化建议
1. 减少不必要的长对话
2. 使用缓存避免重复搜索
3. 及时清理上下文
"""

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'report':
            print(generate_report())
        elif cmd == 'analyze':
            print(analyze_usage())
    else:
        # 显示当前状态
        print(f"📊 Token 追踪器")
        print(f"📁 日志目录: {MEMORY_DIR}")
        print(f"📅 今日文件: {get_today_file().name}")
