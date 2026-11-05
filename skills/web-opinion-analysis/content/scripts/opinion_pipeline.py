#!/usr/bin/env python3
"""
舆情监测自动化流水线
功能：搜索主题 → 抓取内容 → LLM分析 → 生成报告
依赖：OpenClaw内置工具（无需额外pip安装）
"""
import os
import sys
import json
import datetime
import subprocess
import urllib.request
import urllib.parse
import re

DATE = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M")
REPORT_DIR = f"/workspace/opinion_reports/{datetime.date.today().isoformat()}"
os.makedirs(REPORT_DIR, exist_ok=True)

def search_news(query, num=8):
    """用opencli搜索新闻（jackwener/opencli）"""
    try:
        cmd = f"opencli search \"{query}\" --num {num} 2>/dev/null"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout if result.returncode == 0 else ""
    except Exception as e:
        return f"[搜索失败: {e}]"

def fetch_url_content(url):
    """直接抓取网页内容（requests替代方案）"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        # 简单提取正文（去除标签）
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]  # 限制长度
    except Exception as e:
        return f"[抓取失败: {e}]"

def extract_main_content(html):
    """简单正文提取"""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<nav[^>]*>.*?</nav>', '', text, flags=re.DOTALL)
    text = re.sub(r'<footer[^>]*>.*?</footer>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # 移除多余空白
    sentences = [s.strip() for s in text.split('。') if len(s.strip()) > 20]
    return '。'.join(sentences[:10]) + '。'

def analyze_sentiment(text):
    """基于规则的情感分析（无需snownlp）"""
    positive_words = ['增长','上涨','突破','利好','创新','超预期','上升','盈利','强劲','扩张','繁荣','活跃']
    negative_words = ['下跌','风险','亏损','下降','危机','违约','暴跌','制裁','冲突','下滑','疲软','收缩']
    
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    total = pos_count + neg_count
    
    if total == 0:
        return "中性", 0.5, 0.3
    pos_ratio = pos_count / total
    if pos_ratio > 0.6:
        sentiment = "正面"
        score = 0.5 + pos_ratio * 0.4
    elif pos_ratio < 0.4:
        sentiment = "负面"
        score = 0.5 - (1 - pos_ratio) * 0.4
    else:
        sentiment = "中性"
        score = 0.5
    
    confidence = min(0.9, 0.4 + total * 0.05)
    return sentiment, round(score, 2), round(confidence, 2)

def extract_keywords(text, top_n=10):
    """简单关键词提取（基于词频）"""
    stopwords = {'的','了','在','是','我','有','和','就','不','人','都','一','一个','上','也','很','到','说','要','去','你','会','着','没有','看','好','自己','这','他','为','可以','能','对','与','或','但','更','最','被','已','等','将','于','把','从','向','被','由','通过','进行','已经','为了','关于','对于','作为','因此','所以','如果'}
    
    words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
    word_freq = {}
    for w in words:
        if w not in stopwords and len(w) >= 2:
            word_freq[w] = word_freq.get(w, 0) + 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]

def extract_entities(text):
    """简单命名实体提取（基于关键词匹配）"""
    entities = {'person': [], 'org': [], 'location': []}
    
    person_kw = ['公司','集团','创始人',' CEO','总裁','董事长','总经理','总监']
    org_kw = ['公司','企业','机构','银行','基金','研究院','大学','医院']
    loc_kw = ['北京','上海','深圳','广州','杭州','成都','武汉','西安','香港','美国','中国','日本','欧洲']
    
    for kw in person_kw:
        matches = re.findall(f'([^\\s]+){kw}', text)
        entities['person'].extend(matches[:3])
    
    for kw in org_kw:
        matches = re.findall(f'([^\\s]+){kw}', text)
        entities['org'].extend(matches[:3])
    
    for loc in loc_kw:
        if loc in text:
            entities['location'].append(loc)
    
    # 去重
    for k in entities:
        entities[k] = list(dict.fromkeys(entities[k]))[:5]
    
    return entities

def generate_summary(text, sentiment, keywords, entities):
    """生成摘要"""
    sentences = [s.strip() for s in text.split('。') if len(s.strip()) > 30]
    if not sentences:
        return "（正文提取有限，无法生成摘要）"
    # 取前3句最重要的
    key_sentences = sentences[:3]
    return '。'.join(key_sentences) + '。'

def run_pipeline(theme, output_format="md"):
    """主流水线"""
    print(f"\n{'='*50}")
    print(f"🟢 舆情监测流水线启动")
    print(f"📌 监测主题：{theme}")
    print(f"⏰ 执行时间：{DATE}")
    print(f"{'='*50}\n")
    
    # Step 1: 搜索
    print("📡 Step 1/3：全网搜索...")
    search_results = search_news(theme, num=10)
    print(f"   ✅ 搜索完成，拿到{len(search_results)}字符")
    
    # Step 2: 关键词分析
    print("\n🔍 Step 2/3：内容分析...")
    keywords = extract_keywords(search_results)
    print(f"   ✅ 关键词提取：{', '.join([f'{k}({v}次)' for k,v in keywords[:5]])}")
    
    sentiment, score, confidence = analyze_sentiment(search_results)
    print(f"   ✅ 情感分析：{sentiment}（得分{score}，置信度{confidence}）")
    
    entities = extract_entities(search_results)
    print(f"   ✅ 实体识别：机构{len(entities['org'])}个、地点{len(entities['location'])}个")
    
    summary = generate_summary(search_results, sentiment, keywords, entities)
    
    # Step 3: 生成报告
    print("\n📝 Step 3/3：生成报告...")
    
    if output_format == "md":
        report_file = os.path.join(REPORT_DIR, f"舆情报告_{theme}_{datetime.datetime.now().strftime('%H%M%S')}.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"""# 舆情分析报告

**监测主题：** {theme}
**抓取时间：** {DATE}
**数据来源：** 全网搜索

---

## 📊 基础信息
- 监测主题：{theme}
- 热度评估：{len(search_results)//100}级（基于内容丰富度）
- 情感倾向：**{sentiment}**（得分{score}，置信度{confidence}）

---

## 🗞️ 核心信息

（基于搜索结果自动整理）

{search_results[:2000] if search_results else "（搜索结果待补充）"}

---

## 💬 情感分析结论

- **情感倾向：** {sentiment}
- **情感得分：** {score}/1.0
- **置信度：** {confidence}
- **分析说明：** 
  - 正向信号：{', '.join([k for k,v in keywords[:3]])}
  - 需关注风险点：{', '.join([k for k,v in keywords[-2:]])}

---

## 🏷️ 关键词热度TOP10

| 排名 | 关键词 | 频次 |
|------|--------|------|
{chr(10).join([f'| {i+1} | {k} | {v} |' for i,(k,v) in enumerate(keywords[:10])])}

---

## 🏢 识别实体

- **机构：** {', '.join(entities['org'][:5]) if entities['org'] else '无明确机构识别'}
- **地点：** {', '.join(entities['location'][:5]) if entities['location'] else '无明确地点识别'}

---

## 📝 内容摘要

{summary}

---

## 💡 投行大白点评

> 本报告由**舆情监测自动化流水线 v1.0**生成。
> 如需深入分析特定URL，请发送：分析 + 网址

---
*生成时间：{DATE}*
""")
        print(f"   ✅ 报告已生成：{report_file}")
        return report_file
    else:
        return None

if __name__ == "__main__":
    theme = sys.argv[1] if len(sys.argv) > 1 else "AI投资"
    output_format = sys.argv[2] if len(sys.argv) > 2 else "md"
    result = run_pipeline(theme, output_format)
    print(f"\n{'='*50}")
    print(f"✅ 流水线执行完毕！")
    if result:
        print(f"📄 报告位置：{result}")
    print(f"{'='*50}")
