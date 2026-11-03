#!/opt/pylib/bin/python3
"""财经新闻搜索脚本"""
import sys
import json
import argparse
from typing import Optional

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("错误：缺少依赖，请运行 `uv pip install requests beautifulsoup4`")
    sys.exit(1)


SITES_CONFIG = {
    "cls": {
        "name": "财联社",
        "url": "https://www.cls.cn/search",
        "params": {"keyword": "{keyword}", "type": "telegraph"},
    },
    "stcn": {
        "name": "证券时报",
        "url": "https://www.stcn.com/search",
        "params": {"keyword": "{keyword}"},
    },
    "jiuyan": {
        "name": "韭研公社",
        "url": "https://www.jiuyangongshe.com/search",
        "params": {"keyword": "{keyword}"},
    },
    "investing": {
        "name": "英为财情",
        "url": "https://cn.investing.com/search",
        "params": {"q": "{keyword}"},
    },
    "eastmoney": {
        "name": "东方财富",
        "url": "https://so.eastmoney.com/search",
        "params": {"keyword": "{keyword}"},
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}


def search_site(site_id: str, keyword: str, limit: int = 5) -> dict:
    """搜索单个网站"""
    config = SITES_CONFIG.get(site_id)
    if not config:
        return {"site": site_id, "error": "未知网站"}

    try:
        url = config["url"]
        params = {k: v.format(keyword=keyword) for k, v in config["params"].items()}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        # 提取新闻标题和链接（通用提取逻辑，可根据网站调整）
        results = []
        for item in soup.find_all("a", limit=limit)[:limit]:
            title = item.get_text(strip=True)
            href = item.get("href", "")
            if title:
                results.append({"title": title, "url": href})
        return {
            "site": config["name"],
            "count": len(results),
            "results": results,
        }
    except Exception as e:
        return {"site": config["name"], "error": str(e)}


def search_all(keyword: str, sites: Optional[list], limit: int, content_type: str, output_json: bool):
    """搜索所有指定网站"""
    site_ids = sites if sites else list(SITES_CONFIG.keys())
    results = []
    for sid in site_ids:
        r = search_site(sid, keyword, limit)
        results.append(r)
        err = r.get('error')
        if err:
            print(f"[{r['site']}] 错误: {err}")
        else:
            print(f"[{r['site']}] 找到 {r['count']} 条")

    if output_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if "error" not in r:
                print(f"\n=== {r['site']} ===")
                for item in r["results"]:
                    print(f"  • {item['title']}")
                    if item["url"]:
                        print(f"    {item['url']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="财经新闻搜索")
    parser.add_argument("keyword", nargs="?", default="", help="搜索关键词")
    parser.add_argument("--sites", help="指定网站（逗号分隔）")
    parser.add_argument("--type", default="all", help="内容类型: all/telegraph/news/calendar/research")
    parser.add_argument("--limit", type=int, default=5, help="每站返回数量")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    site_list = args.sites.split(",") if args.sites else None
    search_all(args.keyword, site_list, args.limit, args.type, args.json)