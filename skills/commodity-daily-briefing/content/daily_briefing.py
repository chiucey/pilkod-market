# -*- coding: utf-8 -*-
"""
大宗商品每日媒体简报系统 - 增强版
================================
专注于大宗商品行业的媒体信息采集与分析

功能特点：
1. 多数据源爬虫：财经媒体、期货交易所、行业门户
2. 智能分类：宏观、行业、产业、品种
3. 重点品种优先排序
4. Word + HTML 双格式输出
5. 邮件自动发送
"""

import os
import sys
import json
import time
import random
import logging
import hashlib
import re
import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from collections import defaultdict

import requests
from bs4 import BeautifulSoup
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement


# ============================================================
# 全局常量
# ============================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_CN = datetime.now().strftime("%Y年%m月%d日")
WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
TODAY_WEEKDAY = WEEKDAYS[datetime.now().weekday()]

# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# ============================================================
# 大宗商品品种关键词映射（增强版）
# ============================================================

COMMODITY_KEYWORDS = {
    # 有色金属
    "铜": ["铜", "copper", "Cu", "铜精矿", "阴极铜", "电解铜", "废铜", "铜矿", "铜价"],
    "铝": ["铝", "aluminum", "Al", "氧化铝", "电解铝", "铝锭", "铝价", "铝土矿"],
    "锌": ["锌", "zinc", "Zn", "锌锭", "锌价", "镀锌"],
    "镍": ["镍", "nickel", "Ni", "镍铁", "不锈钢", "镍价"],
    "锡": ["锡", "tin", "Sn", "锡锭", "锡价"],
    "铅": ["铅", "lead", "Pb", "铅锭", "铅价"],
    "贵金属": ["黄金", "gold", "Au", "金价", "金条", "白银", "silver", "Ag", "银价", "铂金", "钯金"],
    # 黑色金属
    "螺纹钢": ["螺纹", "rebar", "螺纹钢", "建材", "钢材", "钢价"],
    "铁矿石": ["铁矿", "iron ore", "铁矿石", "铁矿", "钢坯"],
    "焦煤": ["焦煤", "coking coal", "焦炭", "煤炭"],
    "热卷": ["热卷", "hot rolled", "热轧"],
    # 能源化工
    "原油": ["原油", "crude", "WTI", "Brent", "布伦特", "油价", "石油", "OPEC"],
    "天然气": ["天然气", "LNG", "natural gas", "管道气"],
    "燃料油": ["燃料油", "fuel oil", "船燃"],
    "橡胶": ["橡胶", "rubber", "天胶", "天然橡胶", "合成橡胶", "轮胎"],
    "塑料": ["塑料", "PE", "PP", "PVC", "聚乙烯", "聚丙烯"],
    "甲醇": ["甲醇", "MEOH", "Methanol"],
    "尿素": ["尿素", "urea", "氮肥"],
    "苯乙烯": ["苯乙烯", "SM", "Styrene"],
    # 农产品
    "大豆": ["大豆", "soybean", "豆粕", "豆油", "豆一", "豆二"],
    "玉米": ["玉米", "corn", "玉米期货", "小麦", "稻谷"],
    "棉花": ["棉花", "cotton", "棉纱"],
    "白糖": ["白糖", "sugar", "蔗糖"],
    "棕榈油": ["棕榈油", "palm oil", "油脂"],
    "苹果": ["苹果", "apple"],
    # 其他
    "黄金": ["黄金", "gold", "Au", "金价", "金条"],
    "白银": ["白银", "silver", "Ag", "银价"],
}

# 重点关注品种（可配置）
FOCUS_COMMODITIES = ["铜", "铝", "原油", "黄金", "螺纹钢", "铁矿石", "橡胶", "天然气", "镍", "白糖"]

# 行业子分类
SUBCATEGORIES = {
    "有色金属": ["铜", "铝", "锌", "镍", "锡", "铅"],
    "黑色金属": ["螺纹钢", "铁矿石", "焦煤", "热卷"],
    "贵金属": ["黄金", "白银"],
    "能源化工": ["原油", "天然气", "燃料油", "橡胶", "塑料", "甲醇", "尿素", "苯乙烯"],
    "农产品": ["大豆", "玉米", "棉花", "白糖", "棕榈油", "苹果"],
}

# 新闻分类关键词 —— 宏观
MACRO_KEYWORDS = [
    "GDP", "CPI", "PPI", "PMI", "利率", "央行", "人民银行", "美联储", "Fed",
    "FOMC", "货币政策", "财政政策", "汇率", "人民币", "美元", "降准", "降息",
    "加息", "MLF", "LPR", "逆回购", "就业", "非农", "失业率", "通胀",
    "经济数据", "零售销售", "工业增加值", "固定资产投资", "社融", "M2",
    "IMF", "世界银行", "达沃斯", "贸易战", "关税", "制裁",
]

# 新闻分类关键词 —— 行业（期货市场）
INDUSTRY_KEYWORDS = [
    "期货", "交割", "库存", "仓单", "升贴水", "基差", "交易所", "结算价",
    "套保", "套利", "多头", "空头", "保证金", "涨停", "跌停", "主力合约",
    "成交量", "持仓量", "持仓", "平仓", "开仓", "爆仓", "穿仓",
]

# 新闻分类关键词 —— 产业（供需）
SUPPLY_KEYWORDS = [
    "产量", "开工率", "检修", "停产", "复产", "限产", "减产", "增产",
    "进出口", "出口", "进口", "矿山", "冶炼", "需求", "下游", "消费",
    "订单", "产能", "投产", "扩建", "环保", "供应", "短缺", "过剩",
    "库存", "库存变化", "去库", "累库", "采购", "销售",
]

# 需要排除的来源关键词（上市公司/股票相关）
EXCLUDE_SOURCES = ["东方财富", "同花顺", "雪球", "新浪财经", "网易财经", "凤凰网财经"]


# ============================================================
# 配置加载
# ============================================================

def load_config():
    """加载配置文件"""
    if not os.path.exists(CONFIG_PATH):
        default_config = {
            "email": {
                "smtp_server": "smtp.qq.com",
                "smtp_port": 465,
                "sender": "",
                "password": "",
                "receivers": []
            },
            "proxy": {"enabled": False, "proxy_list": []},
            "scraping": {
                "min_delay": 3,
                "max_delay": 8,
                "max_retries": 2,
                "timeout": 15
            },
            "focus_commodities": FOCUS_COMMODITIES,
            "output_dir": "output"
        }
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=4)
        print(f"[提示] 已生成默认配置文件: {CONFIG_PATH}")
        print("[提示] 请编辑 config.json 填写邮箱信息后重新运行。")
        return None
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 日志配置
# ============================================================

def setup_logging(output_dir):
    """配置日志系统"""
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{TODAY}.log")

    logger = logging.getLogger("briefing")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # 控制台输出
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)

    # 文件输出
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)

    return logger


# ============================================================
# HTTP 请求工具
# ============================================================

def get_session(config):
    """创建HTTP会话"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    })
    if config.get("proxy", {}).get("enabled") and config["proxy"].get("proxy_list"):
        proxy = random.choice(config["proxy"]["proxy_list"])
        session.proxies = {"http": proxy, "https": proxy}
    return session


def fetch_url(session, url, config, logger, source_name="",
              method="GET", data=None, headers=None, encoding=None):
    """带重试的URL获取"""
    scraping = config.get("scraping", {})
    max_retries = scraping.get("max_retries", 2)
    timeout = scraping.get("timeout", 15)
    min_delay = scraping.get("min_delay", 3)
    max_delay = scraping.get("max_delay", 8)

    for attempt in range(max_retries + 1):
        try:
            session.headers["User-Agent"] = random.choice(USER_AGENTS)
            if method.upper() == "POST":
                resp = session.post(url, data=data, headers=headers, timeout=timeout)
            else:
                resp = session.get(url, headers=headers, timeout=timeout)
            if encoding:
                resp.encoding = encoding
            elif resp.apparent_encoding:
                resp.encoding = resp.apparent_encoding
            resp.raise_for_status()
            delay = random.uniform(min_delay, max_delay)
            time.sleep(delay)
            return resp
        except Exception as e:
            if attempt < max_retries:
                logger.warning(f"[{source_name}] 请求失败({attempt+1}/{max_retries+1})，重试中... {e}")
                time.sleep(2)
            else:
                logger.error(f"[{source_name}] 请求最终失败: {e}")
                return None
    return None


# ============================================================
# 数据采集：大宗商品专业数据源
# ============================================================

def scrape_wallstreetcn(session, config, logger):
    """华尔街见闻：全球宏观+大宗商品"""
    logger.info("[P1] 华尔街见闻...")
    results = []
    url = "https://api-one-wscn.awtmt.com/apiv1/content/articles"
    params = {"category": "global", "limit": "30", "platform": "wscn"}
    try:
        full_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
        resp = fetch_url(session, full_url, config, logger, "华尔街见闻")
        if resp:
            raw_data = resp.json()
            items = raw_data.get("data", {}).get("items", [])
            for item in items[:15]:
                title = item.get("title", "")
                summary = item.get("content_short", "") or item.get("summary", "")
                pub_time = item.get("display_time", "")
                if pub_time:
                    try:
                        pub_time = datetime.fromtimestamp(int(pub_time)).strftime("%Y-%m-%d %H:%M")
                    except:
                        pub_time = TODAY
                if title and len(summary or title) > 30:
                    results.append({
                        "source": "华尔街见闻",
                        "type": "news",
                        "title": title,
                        "content": summary[:800] if summary else title,
                        "time": pub_time or TODAY,
                        "url": item.get("uri", ""),
                    })
            if results:
                logger.info(f"[P1] 华尔街见闻... 获取{len(results)}条")
                return results
    except Exception as e:
        logger.debug(f"[华尔街见闻] 采集失败: {e}")
    logger.warning("[P1] 华尔街见闻... 未获取到数据")
    return results


def scrape_cls_telegraph(session, config, logger):
    """财联社：深度报道"""
    logger.info("[P1] 财联社...")
    results = []
    url = "https://www.cls.cn/nodeapi/updateTelegraphList"
    params = {"app": "CailianpressWeb", "os": "web", "sv": "7.7.5", "rn": "30"}
    try:
        full_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
        resp = fetch_url(session, full_url, config, logger, "财联社")
        if resp:
            raw_data = resp.json()
            items = raw_data.get("data", {}).get("roll_data", [])
            for item in items[:20]:
                title = item.get("title", "") or item.get("brief", "")
                content = item.get("content", "") or item.get("brief", "")
                content = re.sub(r"<[^>]+>", "", content).strip()
                ctime = item.get("ctime", "")
                if ctime:
                    try:
                        pub_time = datetime.fromtimestamp(int(ctime)).strftime("%Y-%m-%d %H:%M")
                    except:
                        pub_time = TODAY
                else:
                    pub_time = TODAY
                if content and len(content) > 50:
                    results.append({
                        "source": "财联社",
                        "type": "news",
                        "title": title[:100] if title else content[:50],
                        "content": content[:800],
                        "time": pub_time,
                        "url": "",
                    })
            if results:
                logger.info(f"[P1] 财联社... 获取{len(results)}条")
                return results
    except Exception as e:
        logger.debug(f"[财联社] 采集失败: {e}")
    logger.warning("[P1] 财联社... 未获取到数据")
    return results


def scrape_jin10_report(session, config, logger):
    """金十数据：大宗商品专业数据"""
    logger.info("[P1] 金十数据...")
    results = []
    url = "https://www.jin10.com/"
    resp = fetch_url(session, url, config, logger, "金十数据")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.news-list a, div.article-list a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 15 and "javascript" not in href:
                    if not href.startswith("http"):
                        href = "https://www.jin10.com" + href
                    results.append({
                        "source": "金十数据",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P1] 金十数据... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[金十数据] 解析失败: {e}")
    logger.warning("[P1] 金十数据... 未获取到数据")
    return results


def scrape_smm_news(session, config, logger):
    """上海有色网：有色金属"""
    logger.info("[P2] SMM上海有色网...")
    results = []
    url = "https://news.smm.cn/news"
    resp = fetch_url(session, url, config, logger, "SMM")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.news-list a, div.article-list a, h3 a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 15:
                    if not any(ex in title for ex in ["股", "上市", "股价", "财报", "业绩"]):
                        if not href.startswith("http"):
                            href = "https://news.smm.cn" + href
                        results.append({
                            "source": "SMM有色",
                            "type": "news",
                            "title": title,
                            "content": title,
                            "time": TODAY,
                            "url": href,
                        })
            if results:
                logger.info(f"[P2] SMM上海有色网... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[SMM] 解析失败: {e}")
    logger.warning("[P2] SMM上海有色网... 未获取到数据")
    return results


def scrape_mysteel_news(session, config, logger):
    """我的钢铁网：黑色金属"""
    logger.info("[P2] 我的钢铁网...")
    results = []
    url = "https://www.mysteel.com/news/"
    resp = fetch_url(session, url, config, logger, "我的钢铁")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.news a, ul.newsList a, h3 a, li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 15:
                    if not href.startswith("http"):
                        href = "https://www.mysteel.com" + href
                    results.append({
                        "source": "我的钢铁",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P2] 我的钢铁网... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[我的钢铁] 解析失败: {e}")
    logger.warning("[P2] 我的钢铁网... 未获取到数据")
    return results


def scrape_oilchem_news(session, config, logger):
    """隆众资讯：能源化工"""
    logger.info("[P2] 隆众资讯...")
    results = []
    url = "https://www.oilchem.net/news/"
    resp = fetch_url(session, url, config, logger, "隆众资讯")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.news-list a, ul.list a, h3 a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 15:
                    if not href.startswith("http"):
                        href = "https://www.oilchem.net" + href
                    results.append({
                        "source": "隆众资讯",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P2] 隆众资讯... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[隆众资讯] 解析失败: {e}")
    logger.warning("[P2] 隆众资讯... 未获取到数据")
    return results


def scrape_cnfin_macro(session, config, logger):
    """中国证券报：宏观经济"""
    logger.info("[P2] 中国证券报...")
    results = []
    url = "https://www.cs.com.cn/xwzx/"
    resp = fetch_url(session, url, config, logger, "中国证券报")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.list a, div.text a, h3 a")
            seen = set()
            for a_tag in news_items:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if (title and len(title) > 10 and len(title) < 100
                        and title not in seen and "javascript" not in href):
                    seen.add(title)
                    if not href.startswith("http"):
                        href = "https://www.cs.com.cn" + href
                    results.append({
                        "source": "中国证券报",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
                    if len(results) >= 10:
                        break
            if results:
                logger.info(f"[P2] 中国证券报... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[中国证券报] 解析失败: {e}")
    logger.warning("[P2] 中国证券报... 未获取到数据")
    return results


def scrape_shfe_news(session, config, logger):
    """上海期货交易所：官方公告"""
    logger.info("[P3] 上期所...")
    results = []
    url = "https://www.shfe.com.cn/news/notice/"
    resp = fetch_url(session, url, config, logger, "上期所")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.news-list li a, div.list a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    if not href.startswith("http"):
                        href = "https://www.shfe.com.cn" + href
                    results.append({
                        "source": "上期所",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 上期所... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[上期所] 解析失败: {e}")
    logger.warning("[P3] 上期所... 未获取到数据")
    return results


def scrape_dce_news(session, config, logger):
    """大连商品交易所：官方公告"""
    logger.info("[P3] 大商所...")
    results = []
    url = "https://www.dce.com.cn/dcewzx/tzgg/index.html"
    resp = fetch_url(session, url, config, logger, "大商所")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.news-list li a, div.list a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    if not href.startswith("http"):
                        href = "https://www.dce.com.cn" + href
                    results.append({
                        "source": "大商所",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 大商所... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[大商所] 解析失败: {e}")
    logger.warning("[P3] 大商所... 未获取到数据")
    return results


def scrape_czce_news(session, config, logger):
    """郑州商品交易所：官方公告"""
    logger.info("[P3] 郑商所...")
    results = []
    url = "https://www.czce.com.cn/cn/xxgk/news/zxtz/index.html"
    resp = fetch_url(session, url, config, logger, "郑商所")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.news-list li a, div.list a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    if not href.startswith("http"):
                        href = "https://www.czce.com.cn" + href
                    results.append({
                        "source": "郑商所",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 郑商所... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[郑商所] 解析失败: {e}")
    logger.warning("[P3] 郑商所... 未获取到数据")
    return results


def scrape_ine_news(session, config, logger):
    """上海国际能源交易中心：原油期货"""
    logger.info("[P3] 上期能源...")
    results = []
    url = "https://www.ine.cn/news/notice/"
    resp = fetch_url(session, url, config, logger, "上期能源")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.news-list li a, div.list a, ul li a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    if not href.startswith("http"):
                        href = "https://www.ine.cn" + href
                    results.append({
                        "source": "上期能源",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 上期能源... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[上期能源] 解析失败: {e}")
    logger.warning("[P3] 上期能源... 未获取到数据")
    return results


def scrape_xinhua_finance(session, config, logger):
    """新华财经：宏观经济"""
    logger.info("[P3] 新华财经...")
    results = []
    url = "http://www.news.cn/fortune/"
    resp = fetch_url(session, url, config, logger, "新华财经", encoding="utf-8")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.tit a, h3 a, div.list a")
            for a_tag in news_items[:15]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    results.append({
                        "source": "新华财经",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 新华财经... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[新华财经] 解析失败: {e}")
    logger.warning("[P3] 新华财经... 未获取到数据")
    return results


def scrape_fed_news(session, config, logger):
    """美联储：官方新闻"""
    logger.info("[P3] 美联储...")
    results = []
    url = "https://www.federalreserve.gov/newsevents/pressreleases.htm"
    resp = fetch_url(session, url, config, logger, "美联储")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("div.row div.col-xs-9 a")
            for a_tag in news_items[:10]:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if title and len(title) > 10:
                    if not href.startswith("http"):
                        href = "https://www.federalreserve.gov" + href
                    results.append({
                        "source": "美联储",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
            if results:
                logger.info(f"[P3] 美联储... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[美联储] 解析失败: {e}")
    logger.warning("[P3] 美联储... 未获取到数据")
    return results


def scrape_pboc_news(session, config, logger):
    """人民银行：货币政策"""
    logger.info("[P3] 人民银行...")
    results = []
    url = "http://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
    resp = fetch_url(session, url, config, logger, "人民银行")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("font.newslist_style a, a")
            seen = set()
            for a_tag in news_items:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if (title and len(title) > 8 and len(title) < 100
                        and title not in seen and "javascript" not in href):
                    seen.add(title)
                    if not href.startswith("http"):
                        href = "http://www.pbc.gov.cn" + href
                    results.append({
                        "source": "人民银行",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
                    if len(results) >= 10:
                        break
            if results:
                logger.info(f"[P3] 人民银行... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[人民银行] 解析失败: {e}")
    logger.warning("[P3] 人民银行... 未获取到数据")
    return results


def scrape_stats_gov(session, config, logger):
    """国家统计局：数据发布"""
    logger.info("[P3] 国家统计局...")
    results = []
    url = "https://www.stats.gov.cn/sj/zxfb/"
    resp = fetch_url(session, url, config, logger, "国家统计局")
    if resp:
        try:
            soup = BeautifulSoup(resp.text, "lxml")
            news_items = soup.select("ul.list-content li a, div.list a, li a")
            seen = set()
            for a_tag in news_items:
                title = a_tag.get_text(strip=True)
                href = a_tag.get("href", "")
                if (title and len(title) > 8 and len(title) < 100
                        and title not in seen and "javascript" not in href):
                    seen.add(title)
                    if not href.startswith("http"):
                        href = "https://www.stats.gov.cn/sj/zxfb/" + href
                    results.append({
                        "source": "国家统计局",
                        "type": "news",
                        "title": title,
                        "content": title,
                        "time": TODAY,
                        "url": href,
                    })
                    if len(results) >= 10:
                        break
            if results:
                logger.info(f"[P3] 国家统计局... 获取{len(results)}条")
                return results
        except Exception as e:
            logger.debug(f"[国家统计局] 解析失败: {e}")
    logger.warning("[P3] 国家统计局... 未获取到数据")
    return results


# ============================================================
# 数据处理
# ============================================================

def classify_news(text):
    """将新闻分类为：宏观/行业/产业"""
    text_lower = text.lower()
    macro_score = sum(1 for kw in MACRO_KEYWORDS if kw.lower() in text_lower)
    industry_score = sum(1 for kw in INDUSTRY_KEYWORDS if kw.lower() in text_lower)
    supply_score = sum(1 for kw in SUPPLY_KEYWORDS if kw.lower() in text_lower)

    scores = {"宏观": macro_score, "行业": industry_score, "产业": supply_score}
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "行业"  # 默认归入行业
    return best


def match_commodities(text):
    """匹配新闻关联的品种"""
    matched = []
    text_lower = text.lower()
    for commodity, keywords in COMMODITY_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text_lower:
                matched.append(commodity)
                break
    return matched


def dedup_news(news_list):
    """基于标题相似度去重"""
    if not news_list:
        return []

    def similarity(s1, s2):
        if not s1 or not s2:
            return 0.0
        common = sum(1 for c1, c2 in zip(s1, s2) if c1 == c2)
        return common / max(len(s1), len(s2), 1)

    unique = []
    unique_titles = []
    for item in news_list:
        title = item.get("title", "")[:30]
        is_dup = False
        for prev_title in unique_titles:
            if similarity(title, prev_title) > 0.6:
                is_dup = True
                break
        if not is_dup:
            unique.append(item)
            unique_titles.append(title)
    return unique


def process_news(all_news, logger):
    """处理所有新闻"""
    logger.info("数据处理中...")

    # 过滤
    filtered = []
    for item in all_news:
        content = item.get("content", "") or item.get("title", "")
        source = item.get("source", "")
        if len(content) < 30:
            continue
        if any(ex in source for ex in EXCLUDE_SOURCES):
            continue
        if any(ex in content for ex in ["股吧", "股票代码", "股价", "涨停"]):
            continue
        filtered.append(item)
    logger.info(f"  过滤后剩余: {len(filtered)}条")

    # 去重
    filtered = dedup_news(filtered)
    logger.info(f"  去重后剩余: {len(filtered)}条")

    # 分类 + 品种关联
    for item in filtered:
        text = item.get("content", "") or item.get("title", "")
        item["category"] = classify_news(text)
        item["commodities"] = match_commodities(text)

    # 排序：重点品种优先
    def sort_key(item):
        focus_score = 0
        for c in item.get("commodities", []):
            if c in FOCUS_COMMODITIES:
                focus_score += 1
        return (-focus_score,)

    filtered.sort(key=sort_key)

    # 统计
    categories = defaultdict(int)
    for item in filtered:
        categories[item["category"]] += 1

    logger.info(f"  分类统计: {dict(categories)}")

    return filtered


# ============================================================
# Word文档生成
# ============================================================

def calculate_issue_number():
    """计算期号"""
    start_date = datetime(2024, 1, 1)
    days = (datetime.now() - start_date).days
    return 5000 + days


def create_word_report(news_items, output_dir, logger):
    """生成Word格式简报"""
    logger.info("生成Word文件...")
    doc = Document()

    # 页面设置
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    issue_number = calculate_issue_number()

    # 主标题
    title_para = doc.add_paragraph()
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_para.add_run("大宗商品媒体信息简报")
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.name = "黑体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

    # 副标题
    subtitle_para = doc.add_paragraph()
    subtitle_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run1 = subtitle_para.add_run(f"总第{issue_number}期  {TODAY_CN}  {TODAY_WEEKDAY}")
    run1.font.size = Pt(12)
    run1.font.color.rgb = RGBColor(80, 80, 80)
    run1.font.name = "宋体"
    run1._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    doc.add_paragraph()

    # 辅助函数
    def add_category_title(text):
        p = doc.add_paragraph()
        run = p.add_run(f"【{text}】")
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0, 51, 102)
        run.font.name = "黑体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        return p

    def add_news_item(item):
        title = item.get("title", "")
        content = item.get("content", "")
        source = item.get("source", "")
        time = item.get("time", "")
        commodities = item.get("commodities", [])

        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.left_indent = Cm(0.5)

        # 标题
        run1 = p.add_run(f"◆{title}")
        run1.font.size = Pt(11)
        run1.font.bold = True
        run1.font.name = "黑体"
        run1._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

        # 品种标签
        if commodities:
            p0 = doc.add_paragraph()
            p0.paragraph_format.first_line_indent = Cm(-0.5)
            p0.paragraph_format.left_indent = Cm(0.5)
            tag_text = "品种: " + " / ".join(commodities[:5])
            run0 = p0.add_run(tag_text)
            run0.font.size = Pt(9)
            run0.font.color.rgb = RGBColor(0, 102, 204)
            run0.font.name = "宋体"
            run0._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

        # 正文
        if content and content != title:
            p2 = doc.add_paragraph()
            p2.paragraph_format.first_line_indent = Cm(-0.5)
            p2.paragraph_format.left_indent = Cm(0.5)
            run2 = p2.add_run(content[:500])
            run2.font.size = Pt(10.5)
            run2.font.name = "宋体"
            run2._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

        # 来源
        p3 = doc.add_paragraph()
        p3.paragraph_format.first_line_indent = Cm(-0.5)
        p3.paragraph_format.left_indent = Cm(0.5)
        source_text = f"（{source}"
        if time:
            source_text += f" {time}"
        source_text += "）"
        run3 = p3.add_run(source_text)
        run3.font.size = Pt(9)
        run3.font.color.rgb = RGBColor(128, 128, 128)
        run3.font.name = "宋体"
        run3._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

        return p

    # 宏观
    add_category_title("宏观要闻")
    macro_news = [n for n in news_items if n.get("category") == "宏观"]
    if macro_news:
        for item in macro_news[:8]:
            add_news_item(item)
    else:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.5)
        run = p.add_run("今日暂无重要宏观新闻。")
        run.font.size = Pt(10.5)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    doc.add_paragraph()

    # 行业
    add_category_title("期货行业")
    industry_news = [n for n in news_items if n.get("category") == "行业"]
    if industry_news:
        for item in industry_news[:8]:
            add_news_item(item)
    else:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.5)
        run = p.add_run("今日暂无重要行业新闻。")
        run.font.size = Pt(10.5)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    doc.add_paragraph()

    # 产业
    add_category_title("产业动态")
    supply_news = [n for n in news_items if n.get("category") == "产业"]
    if supply_news:
        for item in supply_news[:8]:
            add_news_item(item)
    else:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.5)
        run = p.add_run("今日暂无重要产业新闻。")
        run.font.size = Pt(10.5)
        run.font.name = "宋体"
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    doc.add_paragraph()

    # 免责声明
    disclaimer_para = doc.add_paragraph()
    run = disclaimer_para.add_run(
        "【免责声明】本简报内容来源于公开信息，仅供内部参考，不构成任何投资建议。"
    )
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(150, 150, 150)
    run.font.name = "宋体"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    # 保存
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"大宗商品简报{issue_number}期.docx")
    doc.save(filepath)
    logger.info(f"Word文件已保存: {filepath}")
    return filepath


# ============================================================
# HTML邮件生成
# ============================================================

def create_html_report(news_items, output_dir, logger, issue_number):
    """生成HTML格式简报"""
    logger.info("生成HTML文件...")

    # 品种统计
    commodity_stats = defaultdict(int)
    for item in news_items:
        for c in item.get("commodities", []):
            commodity_stats[c] += 1

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body {{ font-family: '宋体', 'Microsoft YaHei', sans-serif; font-size: 14px; color: #333; max-width: 850px; margin: 0 auto; padding: 20px; }}
h1 {{ text-align: center; color: #003366; font-size: 24px; margin-bottom: 10px; }}
.subtitle {{ text-align: center; color: #666; font-size: 14px; margin-bottom: 20px; }}
.stats {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 25px; }}
.stats-title {{ font-weight: bold; color: #003366; margin-bottom: 10px; }}
.commodity-tag {{ display: inline-block; background: #e6f0ff; color: #0066cc; padding: 3px 8px; border-radius: 3px; margin: 3px; font-size: 12px; }}
h2 {{ color: #003366; border-bottom: 2px solid #003366; padding-bottom: 5px; font-size: 16px; margin-top: 25px; }}
.news-item {{ margin: 15px 0; padding-left: 10px; border-left: 3px solid #e6e6e6; }}
.news-title {{ font-weight: bold; font-size: 14px; margin-bottom: 5px; }}
.commodities {{ font-size: 11px; color: #0066cc; margin: 3px 0 5px 15px; }}
.news-content {{ font-size: 13px; color: #555; margin: 5px 0 5px 20px; }}
.news-source {{ font-size: 11px; color: #888; margin-left: 20px; }}
.disclaimer {{ font-size: 11px; color: #aaa; margin-top: 40px; border-top: 1px solid #eee; padding-top: 10px; }}
</style></head><body>
<h1>大宗商品媒体信息简报</h1>
<p class="subtitle">总第{issue_number}期  {TODAY_CN}  {TODAY_WEEKDAY}</p>
"""

    # 品种统计
    if commodity_stats:
        sorted_commodities = sorted(commodity_stats.items(), key=lambda x: -x[1])[:15]
        html += '<div class="stats"><div class="stats-title">今日涉及品种：</div>'
        for c, count in sorted_commodities:
            html += f'<span class="commodity-tag">{c}({count})</span>'
        html += '</div>'

    # 宏观
    html += "<h2>【宏观要闻】</h2>"
    macro_news = [n for n in news_items if n.get("category") == "宏观"]
    if macro_news:
        for item in macro_news[:8]:
            title = item.get("title", "")
            content = item.get("content", "")
            source = item.get("source", "")
            time = item.get("time", "")
            commodities = item.get("commodities", [])
            source_text = f"{source} {time}" if time else source
            html += f'<div class="news-item"><div class="news-title">◆{title}</div>'
            if commodities:
                html += f'<div class="commodities">品种: {" / ".join(commodities[:5])}</div>'
            if content and content != title:
                html += f'<div class="news-content">{content[:300]}</div>'
            html += f'<div class="news-source">（{source_text}）</div></div>'
    else:
        html += "<p>今日暂无重要宏观新闻。</p>"

    # 行业
    html += "<h2>【期货行业】</h2>"
    industry_news = [n for n in news_items if n.get("category") == "行业"]
    if industry_news:
        for item in industry_news[:8]:
            title = item.get("title", "")
            content = item.get("content", "")
            source = item.get("source", "")
            time = item.get("time", "")
            commodities = item.get("commodities", [])
            source_text = f"{source} {time}" if time else source
            html += f'<div class="news-item"><div class="news-title">◆{title}</div>'
            if commodities:
                html += f'<div class="commodities">品种: {" / ".join(commodities[:5])}</div>'
            if content and content != title:
                html += f'<div class="news-content">{content[:300]}</div>'
            html += f'<div class="news-source">（{source_text}）</div></div>'
    else:
        html += "<p>今日暂无重要行业新闻。</p>"

    # 产业
    html += "<h2>【产业动态】</h2>"
    supply_news = [n for n in news_items if n.get("category") == "产业"]
    if supply_news:
        for item in supply_news[:8]:
            title = item.get("title", "")
            content = item.get("content", "")
            source = item.get("source", "")
            time = item.get("time", "")
            commodities = item.get("commodities", [])
            source_text = f"{source} {time}" if time else source
            html += f'<div class="news-item"><div class="news-title">◆{title}</div>'
            if commodities:
                html += f'<div class="commodities">品种: {" / ".join(commodities[:5])}</div>'
            if content and content != title:
                html += f'<div class="news-content">{content[:300]}</div>'
            html += f'<div class="news-source">（{source_text}）</div></div>'
    else:
        html += "<p>今日暂无重要产业新闻。</p>"

    # 免责声明
    html += """<div class="disclaimer">
【免责声明】本简报内容来源于公开信息，仅供内部参考，不构成任何投资建议。
</div></body></html>"""

    # 保存HTML
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"大宗商品简报{issue_number}期.html")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"HTML文件已保存: {filepath}")
    return html, filepath


def send_email(config, html_content, word_filepath, logger):
    """发送邮件"""
    email_cfg = config.get("email", {})
    sender = email_cfg.get("sender", "")
    password = email_cfg.get("password", "")
    receivers = email_cfg.get("receivers", [])
    smtp_server = email_cfg.get("smtp_server", "smtp.qq.com")
    smtp_port = email_cfg.get("smtp_port", 465)

    if not sender or not password or not receivers:
        logger.warning("邮箱未配置，跳过邮件发送。")
        return False

    logger.info(f"发送邮件 → {len(receivers)}位收件人...")

    try:
        msg = MIMEMultipart("mixed")
        msg["From"] = sender
        msg["To"] = ", ".join(receivers)
        issue_number = calculate_issue_number()
        msg["Subject"] = f"【大宗商品简报】总第{issue_number}期 | {TODAY}"

        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(html_part)

        if word_filepath and os.path.exists(word_filepath):
            with open(word_filepath, "rb") as f:
                attachment = MIMEApplication(f.read())
                filename = os.path.basename(word_filepath)
                attachment.add_header("Content-Disposition", "attachment",
                                     filename=("utf-8", "", filename))
                msg.attach(attachment)

        context = ssl.create_default_context()
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
                server.login(sender, password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender, password)
                server.send_message(msg)

        logger.info(f"邮件发送成功 → {len(receivers)}位收件人")
        return True

    except Exception as e:
        logger.error(f"邮件发送失败: {e}")
        return False


# ============================================================
# 主程序
# ============================================================

def collect_all_data(session, config, logger):
    """采集所有新闻数据"""
    all_news = []

    # P1: 高优先级
    logger.info("=" * 50)
    logger.info("开始采集 [P1] 高优先级新闻...")
    logger.info("=" * 50)

    scrapers_p1 = [
        scrape_wallstreetcn,
        scrape_cls_telegraph,
        scrape_jin10_report,
    ]
    for scraper in scrapers_p1:
        try:
            result = scraper(session, config, logger)
            if result:
                all_news.extend(result)
        except Exception as e:
            logger.error(f"采集器异常: {scraper.__name__} - {e}")

    # P2: 行业新闻
    logger.info("=" * 50)
    logger.info("开始采集 [P2] 行业新闻...")
    logger.info("=" * 50)

    scrapers_p2 = [
        scrape_smm_news,
        scrape_mysteel_news,
        scrape_oilchem_news,
        scrape_cnfin_macro,
    ]
    for scraper in scrapers_p2:
        try:
            result = scraper(session, config, logger)
            if result:
                all_news.extend(result)
        except Exception as e:
            logger.error(f"采集器异常: {scraper.__name__} - {e}")

    # P3: 交易所+宏观
    logger.info("=" * 50)
    logger.info("开始采集 [P3] 交易所公告 & 宏观数据...")
    logger.info("=" * 50)

    scrapers_p3 = [
        scrape_shfe_news,
        scrape_dce_news,
        scrape_czce_news,
        scrape_ine_news,
        scrape_xinhua_finance,
        scrape_fed_news,
        scrape_pboc_news,
        scrape_stats_gov,
    ]
    for scraper in scrapers_p3:
        try:
            result = scraper(session, config, logger)
            if result:
                all_news.extend(result)
        except Exception as e:
            logger.error(f"采集器异常: {scraper.__name__} - {e}")

    return all_news


def main():
    """主入口函数"""
    print("=" * 60)
    print(f"  大宗商品每日媒体简报系统")
    print(f"  {TODAY_CN} {TODAY_WEEKDAY}")
    print("=" * 60)
    print()

    # 1. 加载配置
    config = load_config()
    if config is None:
        return

    # 2. 设置输出目录和日志
    output_dir = os.path.join(SCRIPT_DIR, config.get("output_dir", "output"))
    os.makedirs(output_dir, exist_ok=True)
    logger = setup_logging(output_dir)
    logger.info("开始采集...")

    # 3. 创建HTTP会话
    session = get_session(config)

    # 4. 采集数据
    all_news = collect_all_data(session, config, logger)
    logger.info(f"采集完成，共获取新闻{len(all_news)}条")

    # 5. 数据处理
    if not all_news:
        logger.warning("今日所有数据源均未获取到数据！")
        all_news = [{
            "source": "系统",
            "type": "news",
            "title": "今日数据采集异常",
            "content": "今日所有数据源均未能成功采集，可能原因：网络问题、非交易日、网站改版。请检查日志文件。",
            "time": TODAY,
            "url": "",
        }]

    processed_news = process_news(all_news, logger)
    issue_number = calculate_issue_number()

    # 6. 生成Word报告
    word_path = create_word_report(processed_news, output_dir, logger)

    # 7. 生成HTML + 发送邮件
    html_content, html_path = create_html_report(processed_news, output_dir, logger, issue_number)
    send_email(config, html_content, word_path, logger)

    # 8. 完成
    logger.info("=" * 50)
    logger.info("全部完成！")
    logger.info(f"  Word: {word_path}")
    logger.info(f"  HTML: {html_path}")
    print()
    print("简报生成完成！请查看 output/ 目录。")


if __name__ == "__main__":
    main()
