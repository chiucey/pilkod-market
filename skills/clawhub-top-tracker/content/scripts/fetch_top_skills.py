#!/usr/bin/env python3
"""
ClawHub Top Skills Fetcher
通过 ClawHub 公开 Convex API 获取 Skill 榜单数据
API: POST https://wry-manatee-359.convex.cloud/api/query
     Body: {"path": "skills:listPublicPageV4", "args": {...}}
响应: {"value": {"page": [...], "hasMore": true, "nextCursor": "..."}}

注意：args 中绝对不要传 cursor: None，服务器会报 Server Error。
      首次请求不传 cursor 键，从第二次开始用上一次的 nextCursor 值。
"""

import json, argparse, sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: pip install requests"); sys.exit(1)

CONVEX_BASE = "https://wry-manatee-359.convex.cloud"
QUERY_ENDPOINT = f"{CONVEX_BASE}/api/query"


def fetch_skills(num: int = 25, sort: str = "downloads"):
    all_skills, page_size = [], min(25, num)
    headers = {"Content-Type": "application/json", "User-Agent": "clawhub-top-tracker/1.0"}

    # 首次请求：不传 cursor 键（传 cursor: None 会导致 Server Error）
    args = {"numItems": page_size, "sort": sort, "dir": "desc", "nonSuspiciousOnly": True}

    while len(all_skills) < num:
        payload = {"path": "skills:listPublicPageV4", "args": args}
        print(f"[{len(all_skills)}] 请求中 (cursor={'有' if 'cursor' in args else '无'})...", file=sys.stderr)

        try:
            r = requests.post(QUERY_ENDPOINT, json=payload, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"❌ 请求失败: {e}", file=sys.stderr)
            break

        if data.get("status") == "error":
            print(f"❌ API错误: {data.get('errorMessage','')}", file=sys.stderr)
            break

        value = data.get("value", {})
        entries = value.get("page", [])
        next_cursor = value.get("nextCursor")
        has_more = value.get("hasMore", False)

        if not entries:
            print("⚠️ 无更多数据", file=sys.stderr)
            break

        for e in entries:
            skill_data = e.get("skill", {})
            stats = skill_data.get("stats", {}) or {}
            all_skills.append({
                "name":        skill_data.get("displayName", "").strip(),
                "slug":        skill_data.get("slug", ""),
                "author":      e.get("ownerHandle", ""),
                "downloads":   int(stats.get("downloads", 0)),
                "installs":    int(stats.get("installsCurrent", 0)),
                "stars":       int(stats.get("stars", 0)),
                "description": clean(skill_data.get("summary", "")),
                "tags":        list(skill_data.get("capabilityTags", [])),
                "skillUrl":    f"https://clawhub.ai/{e.get('ownerHandle','')}/{skill_data.get('slug','')}",
                "createdAt":   skill_data.get("createdAt"),
                "version":     (e.get("latestVersion") or {}).get("version", ""),
            })

        if not has_more or not next_cursor:
            break

        # 下一页：加入 nextCursor（注意不要加 cursor: None，保持键不存在）
        args = {
            "numItems": page_size,
            "sort": sort,
            "dir": "desc",
            "nonSuspiciousOnly": True,
            "cursor": next_cursor,
        }

    return all_skills[:num]


def clean(text):
    if not text: return ""
    return " ".join(l.strip() for l in text.splitlines() if l.strip())[:300]


def save(data, path):
    result = {
        "fetchedAt": datetime.utcnow().isoformat() + "Z",
        "total": len(data),
        "skills": data,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存 {len(data)} 条到 {path}", file=sys.stderr)


def main():
    a = argparse.ArgumentParser(description="ClawHub Top Skills Fetcher")
    a.add_argument("--num",   type=int, default=25,   help="获取数量（默认25，最大100）")
    a.add_argument("--sort",  default="downloads", choices=["downloads","stars","latest"], help="排序方式")
    a.add_argument("--output",default="clawhub_top.json", help="输出文件路径")
    args = a.parse_args()

    num = min(args.num, 100)
    print(f"📡 获取 ClawHub Top{num} (sort={args.sort})...", file=sys.stderr)

    try:
        skills = fetch_skills(num=num, sort=args.sort)
    except Exception as e:
        print(f"❌ 失败: {e}"); sys.exit(1)

    if not skills:
        print("⚠️ 未获取到数据"); sys.exit(1)

    save(skills, args.output)

    print("\n📊 榜单摘要：", file=sys.stderr)
    for i, s in enumerate(skills[:10], 1):
        print(f"  {i:2}. {s['name']:32s} | ⬇️{s['downloads']:>6} | ⭐{s['stars']:>5} | {s['author']}", file=sys.stderr)


if __name__ == "__main__":
    main()