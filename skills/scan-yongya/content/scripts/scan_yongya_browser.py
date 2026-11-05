#!/usr/bin/env python3
"""
用 browser CLI（真实浏览器 + 无限滚动）扫描交易猫，找3件以上雍雅装备的账号。

关键改进：
  1. 真实浏览器渲染，绕过反爬
  2. 无限滚动：反复滚动直到卡片数稳定，加载全部账号
  3. 从列表卡片 DOM 的 data-goodsid / innerText 直接提取数据
  4. enforcePlat=2 安卓 / enforcePlat=3 苹果，两个平台都扫
"""
import subprocess, json, re, os, time, csv

# 每个平台的基础 URL（price/search 条件单独追加）
PLATFORMS = [
    ("安卓(灵犀)", "2",
     "https://www.jiaoyimao.com/lingxi/g1009207/"),
    ("苹果(iOS)",  "3",
     "https://www.jiaoyimao.com/lingxi/g1009207-3/"),
]

# 不同价格段逐一搜索（交易猫用价格桶，无法直接设最低价）
PRICE_TIERS = [
    ("50000+", '{"price":{"conditionList":["50000"],"groupName":"价格范围","statConditionList":["50000"]}}'),
    ("40000+", '{"price":{"conditionList":["40000"],"groupName":"价格范围","statConditionList":["40000"]}}'),
    ("30000+", '{"price":{"conditionList":["30000"],"groupName":"价格范围","statConditionList":["30000"]}}'),
    ("20000+", '{"price":{"conditionList":["20000"],"groupName":"价格范围","statConditionList":["20000"]}}'),
    ("10000+", '{"price":{"conditionList":["10000"],"groupName":"价格范围","statConditionList":["10000"]}}'),
    ("无限制",  None),
]

SEARCH_COND = '{"s3_equip_skill":{"selectType":1,"conditionList":["7018093469081410054@雍雅"],"conditionId":"7018093469081410054","statConditionList":["雍雅"],"conditionType":103}}'

RESULTS_CSV = "./outputs/found_3yongya_browser.csv"
MIN_YONGYA  = 3
MAX_SCROLL  = 80
STABLE_STOP = 4
SCROLL_WAIT = 2.0

# ── URL builder ─────────────────────────────────────────────────────────
def build_url(base: str, plat: str, price_cond: str | None) -> str:
    from urllib.parse import quote
    parts = [f"searchCondition={quote(SEARCH_COND)}",
             f"enforcePlat={plat}",
             "newPage=true"]
    if price_cond:
        parts.insert(0, f"priceCondition={quote(price_cond)}")
    return base + "?" + "&".join(parts)

# ── CLI wrapper ─────────────────────────────────────────────────────────
def cli(*args, timeout=30):
    r = subprocess.run(["browser"] + list(args),
                       capture_output=True, text=True, timeout=timeout)
    return (r.stdout or "") + (r.stderr or "")

def nav(url):      return cli("navigate", url, timeout=60)
def shot():        return cli("screenshot")
def exec_js(js):   return cli("console", "exec", js, timeout=30)

def parse_json(raw: str):
    """
    Extract JSON from browser console exec output.
    Format:
        Executed: <JS code>
        ---
        <actual result>
        ---
        ...
    """
    # 取第一对 --- 之间的内容（即实际返回值）
    parts = raw.split("---")
    # parts[0] = "Executed: <JS>"  parts[1] = actual result  parts[2] = rest
    candidates = parts[1:] if len(parts) > 1 else [raw]
    for chunk in candidates:
        chunk = chunk.strip()
        for pat in (r'\[[\s\S]*\]', r'\{[\s\S]*\}'):
            m = re.search(pat, chunk)
            if m:
                try:
                    return json.loads(m.group())
                except json.JSONDecodeError:
                    pass
    return None

# ── JS snippets ─────────────────────────────────────────────────────────
JS_SCROLL = """(function(){
  const cands=[document.querySelector('.list-container'),
               document.querySelector('.goods-list-dom')?.parentElement,
               document.scrollingElement,document.documentElement,document.body].filter(Boolean);
  for(const el of cands){el.scrollTop=el.scrollHeight;}
  window.scrollTo(0,document.body.scrollHeight);
  return cands.map(e=>({sh:e.scrollHeight,st:e.scrollTop}));
})()"""

JS_COUNT = """document.querySelectorAll('[data-goodsid]').length"""

JS_EXTRACT = r"""(function(){
  const cards=Array.from(document.querySelectorAll('[data-goodsid]'));
  // 只返回含雍雅的卡片，且裁剪文本，控制 JSON 大小
  const result=[];
  for(const c of cards){
    const text=(c.innerText||'').replace(/\s+/g,' ').trim();
    const yyM=text.match(/雍雅\*(\d+)/);
    const yy=yyM?Number(yyM[1]):0;
    if(yy===0) continue;   // 无雍雅跳过
    result.push({
      id:    c.getAttribute('data-goodsid'),
      os:    c.getAttribute('data-game_os')||'',
      price: c.getAttribute('data-price')||'',
      name:  (c.getAttribute('data-goods_name')||'').slice(0,40),
      yongya:yy,
    });
  }
  return JSON.stringify(result);
})()"""

JS_EXTRACT_ALL_IDS = r"""(function(){
  // 只提取所有账号ID（用于去重），不含文本
  const cards=Array.from(document.querySelectorAll('[data-goodsid]'));
  return JSON.stringify(cards.map(c=>c.getAttribute('data-goodsid')));
})()"""

# ── Scroll until stable ──────────────────────────────────────────────────
def scroll_to_load_all(label=""):
    last, stable = 0, 0
    for i in range(MAX_SCROLL):
        exec_js(JS_SCROLL)
        time.sleep(SCROLL_WAIT)
        raw = exec_js(JS_COUNT)
        m = re.search(r'\d+', raw)
        count = int(m.group()) if m else 0
        print(f"  [{label}] 滚动{i+1:02d} 卡片={count}", end="")
        if count > last:
            stable = 0; last = count; print(" ↑新增")
        else:
            stable += 1; print(f" 稳定{stable}/{STABLE_STOP}")
            if stable >= STABLE_STOP:
                print(f"  卡片数稳定，停止")
                break
    return last

# ── Main ─────────────────────────────────────────────────────────────────
def main():
    os.makedirs("outputs", exist_ok=True)

    print("\n" + "="*65)
    print("  真实浏览器无限滚动扫描  —  寻找3件以上雍雅装备账号")
    print("="*65)

    all_seen = set()
    found    = []

    for plat_name, plat_id, base_url in PLATFORMS:
        print(f"\n{'━'*65}")
        print(f"  平台: {plat_name}")
        print(f"{'━'*65}")

        for tier_name, price_cond_str in PRICE_TIERS:
            url = build_url(base_url, plat_id, price_cond_str)
            print(f"\n  ── 价格段: {tier_name} ──")
            print(f"  导航: {url[:100]}...")

            nav(url)
            time.sleep(4)

            # Debug 确认页面状态
            debug_raw = exec_js("JSON.stringify({title:document.title,cards:document.querySelectorAll('[data-goodsid]').length})")
            dbg = parse_json(debug_raw)
            if dbg:
                print(f"  页面: {dbg.get('title','?')[:40]}  初始卡片:{dbg.get('cards',0)}")

            # 无限滚动
            label = f"{plat_name}/{tier_name}"
            final_count = scroll_to_load_all(label)
            print(f"  最终卡片数: {final_count}")

            # 先提取全部 ID（去重用）
            raw_ids = exec_js(JS_EXTRACT_ALL_IDS)
            all_ids = parse_json(raw_ids) or []
            new_ids = [i for i in all_ids if i and i not in all_seen]
            for i in new_ids:
                all_seen.add(i)
            print(f"  全部ID: {len(all_ids)}  新增: {len(new_ids)}")

            # 再提取含雍雅的卡片（JSON 小很多）
            raw = exec_js(JS_EXTRACT)
            cards = parse_json(raw)
            if cards is None:
                print(f"  [警告] 雍雅卡片提取失败，原始: {raw[:200]}")
                continue
            new_cards = [c for c in cards if c.get("id") and c["id"] in set(new_ids)]

            print(f"  含雍雅卡片: {len(cards)}  其中新账号: {len(new_cards)}")

            from collections import Counter
            dist = Counter(c.get("yongya",0) for c in new_cards)
            for k in sorted(dist.keys(), reverse=True):
                if k > 0:
                    print(f"    雍雅{k}件: {dist[k]}个")

            # 找 3+ 雍雅
            for c in new_cards:
                yy = c.get("yongya", 0)
                if yy >= MIN_YONGYA:
                    gid = c["id"]
                    entry = {
                        "item_id":   gid,
                        "platform":  plat_name,
                        "url":       f"https://www.jiaoyimao.com/lingxi/g1009207/{gid}.html",
                        "price":     c.get("price",""),
                        "yongya":    yy,
                        "name":      c.get("name",""),
                        "os_tag":    c.get("os",""),
                        "tier":      tier_name,
                        "text":      c.get("text","")[:200],
                    }
                    found.append(entry)
                    _save(found)
                    print(f"\n  ★★★ 找到! ★★★  ID={gid}  雍雅={yy}件  价格={c.get('price','')}元")
                    print(f"  链接: {entry['url']}\n")

            if not new_cards:
                print("  无新账号，此价格段已全部收录")

    # ── 关闭浏览器 ───────────────────────────────────────────────────────
    cli("close")

    # ── 最终报告 ─────────────────────────────────────────────────────────
    print("\n" + "="*65)
    print(f"扫描完成！检查 {len(all_seen)} 个不重复账号")
    print(f"找到 {len(found)} 个含3件以上雍雅装备的账号")
    print("="*65)

    from collections import Counter
    all_cards_dist = {}  # Would need to store, skip for now

    if found:
        print(f"\n结果已保存: {RESULTS_CSV}")
        for a in found:
            print(f"  {a['url']}  雍雅={a['yongya']}件  价格={a['price']}  平台={a['platform']}")
    else:
        print("\n当前交易猫暂无3件以上雍雅装备的账号在售（两个平台均已扫描）。")


def _save(rows):
    if not rows: return
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
