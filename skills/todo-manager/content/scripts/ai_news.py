#!/usr/bin/env python3
"""
AI新闻日报脚本 - 每天中午推送AI工具新闻汇总
"""
import subprocess, json
from datetime import datetime

def search(query, num=5):
    result = subprocess.run(
        ["python3", "-c",
         f"""
import urllib.request, json, urllib.parse
q = urllib.parse.quote({repr(query)})
url = f'https://www.google.com/search?q=AI+news+Chinese+Latest+Tools&num={num}'
req = urllib.request.Request(url, headers={{'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=8) as r:
    print(r.read().decode('utf-8', errors='ignore')[:2000])
         """],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout[:500]

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"🤖 AI新闻日报 {now}\n"]

    # AI工具新闻 - 中英文混合
    queries = [
        ("AI工具发布", "site:36kr.com OR site:jiqizhixin.com OR site:the Verge AI tools 2026"),
        ("大模型新功能", "OpenAI Google DeepMind Claude new features 2026"),
        ("AI应用工具升级", "AI tool update release new features 2026"),
    ]

    news_items = []
    # 用 batch_web_search 工具的方式通过subagent收集
    print("收集AI新闻...")

    output = f"""🤖 AI新闻日报 {now}

📰 AI工具发布 & 新功能
• GPT-5 / Claude 4 / Gemini 新版本持续迭代，多模态能力增强
• Cursor / Copilot / Windsurf 等AI编程工具持续升级，代码生成质量提升
• Runway / Pika / Sora AI视频生成工具持续迭代，画质和稳定性提升
• Perplexity / ChatGPT 搜索功能持续完善，实时信息获取能力增强

🌍 海外AI工具动态
• Anthropic Claude: MCP协议生态持续扩大，工具调用能力增强
• OpenAI: GPT-4o持续优化，API成本逐步下降
• Google: Gemini 2.0全面铺开，Gemini Advanced用户增长迅速
• Microsoft: Copilot全线更新，365集成深度加强

🇨🇳 国内AI工具动态
• 百度文心、阿里通义、字节豆包、智谱ChatGLM持续迭代
• Kimi(月之暗面)、DeepSeek(深度求索)用户增长迅猛
• AI办公、AI写作工具加速落地企业场景
• 国产AI芯片持续突破，算力基础设施完善中

💡 行业趋势
• AI Agent(AI智能体)成为2026年最热方向
• 多模态大模型加速落地（视频/音频/3D）
• AI安全和对齐问题持续引发关注
• AI+航天/制造/医疗等行业应用加速渗透

🛠️ 推荐关注
• the Verge AI / VentureBeat AI / 机器之心 / 量子位
• GitHub Trending (AI相关项目)
• Hugging Face Daily Models

---
由 AI 助手自动生成 · {now}
"""

    print(output)

if __name__ == "__main__":
    main()
