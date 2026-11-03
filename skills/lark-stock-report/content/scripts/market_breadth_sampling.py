#!/usr/bin/env python3
"""
9:30 阶段涨跌家数降级方案 (2026-06-24 新增)
=========================================

**背景**: push2 涨/跌统计接口 (fs=m:0+s:3,m:1+s:2) 在 9:30 集合竞价阶段频繁 52 错误,
且没有专门的"全市场涨跌家数" endpoint. 实测 6/24 09:30 用 `fid=f3` 排序的 top 200 + bottom 200
采样可推断市场宽度.

**为什么用 top 200 + bottom 200 排序**:
- push2 的 fid=f3 排序接口相对稳定, 1-2 次重试就能拿到
- top 200 全数正收益 (sorted by f3 desc) → 上半市场强势信号
- bottom 200 全数负收益 (sorted by f3 asc) → 下半市场弱势信号
- 极端值 (涨停 / 跌停) 都在前 200 / 后 200 内, 不会漏

**使用方式**:
```bash
python3 scripts/market_breadth_sampling.py
```

**输出**:
- 涨停数 + 跌停数 (按代码前缀判定 10% / 20% / 30% 限制)
- 涨跌停比 + 涨停行业分布
- top 200 / bottom 200 采样区间
- "指数弱+个股中性" 等模式判定的关键依据

**限制**:
- 不能精确到 bearish_pct (需要全市场统计, 9:30 不可用)
- 涨停 / 跌停 计数可能因 9:30 阶段数据更新略有不一致, 建议 5 分钟后再跑一次
- 与 push2 涨停池 (f:!2 过滤) 计数有 1-3 只差异 (新股 / 退市 / ST 处理不同)
"""
import json
import os
import subprocess
import sys
import time
from collections import Counter

PUSH2_URL = "https://82.push2.eastmoney.com/api/qt/clist/get"
PARAMS = {
    "fid": "f3",
    "pz": "200",
    "pn": "1",
    "np": "1",
    "fltt": "2",
    "invt": "2",
    "fs": "m:1+t:2,m:0+t:6",
    "fields": "f12,f14,f3,f4",
    "_": str(int(time.time() * 1000)),
}
HEADERS = {
    "Referer": "https://quote.eastmoney.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}


def is_limit_up(code, pct):
    """判定是否涨停. 主板 10% / 创业/科创 20% / 北交所 30%."""
    if pct is None:
        return False
    if code.startswith(("688", "300")):
        return pct >= 19.5
    if code.startswith(("8", "4")):
        return pct >= 29.5
    return pct >= 9.5


def is_limit_down(code, pct):
    """判定是否跌停. 主板 10% / 创业/科创 20% / 北交所 30%."""
    if pct is None:
        return False
    if code.startswith(("688", "300")):
        return pct <= -19.5
    if code.startswith(("8", "4")):
        return pct <= -29.5
    return pct <= -9.5


def fetch_with_retry(po, pz=200, max_attempts=3):
    """带重试的 push2 抓取. po=1 升序(底部), po=0 降序(顶部)."""
    params = dict(PARAMS)
    params["po"] = str(po)
    params["pz"] = str(pz)

    url = PUSH2_URL + "?" + "&".join(f"{k}={v}" for k, v in params.items())

    for attempt in range(1, max_attempts + 1):
        try:
            cmd = ["curl", "-sL", "-H", f"Referer: {HEADERS['Referer']}",
                   "-H", f"User-Agent: {HEADERS['User-Agent']}",
                   "--max-time", "10", url, "-o", "/tmp/push2_resp.json"]
            result = subprocess.run(cmd, capture_output=True, timeout=15)
            if result.returncode != 0:
                print(f"[WARN] curl 退出码 {result.returncode}, 重试 {attempt}/{max_attempts}",
                      file=sys.stderr)
                time.sleep(attempt * 2)
                continue

            if not os.path.exists("/tmp/push2_resp.json") or os.path.getsize("/tmp/push2_resp.json") < 100:
                print(f"[WARN] 响应为空 (尝试 {attempt}/{max_attempts}), 重试",
                      file=sys.stderr)
                time.sleep(attempt * 2)
                continue

            with open("/tmp/push2_resp.json") as f:
                data = json.load(f)
            diff = data.get("data", {}).get("diff", [])
            if not diff:
                print(f"[WARN] diff 为空 (尝试 {attempt}/{max_attempts}), 重试",
                      file=sys.stderr)
                time.sleep(attempt * 2)
                continue
            return diff, data.get("data", {}).get("total", 0)
        except Exception as e:
            print(f"[WARN] 异常 {e} (尝试 {attempt}/{max_attempts}), 重试",
                  file=sys.stderr)
            time.sleep(attempt * 2)

    raise RuntimeError(f"push2 抓取失败 (重试 {max_attempts} 次)")


def classify_industry(name):
    """简易行业分类 (基于关键词)."""
    keywords = {
        "纺织/消费": ["兴业", "孚日", "海欣", "梦洁", "纺织", "服装", "服饰", "鞋", "帽", "床上用品"],
        "食品/饮料": ["食品", "饮料", "酒", "奶", "米", "肉", "茶", "调味", "天味"],
        "化工/材料": ["材料", "玻纤", "膜", "化学", "新材", "化工", "聚酯", "纤维", "胶", "涂"],
        "PCB/电子": ["PCB", "光模块", "电路", "通信", "电子", "光电", "集成", "微", "芯", "存"],
        "新能源/锂电": ["锂电", "电池", "光伏", "储能", "风电", "新能源", "太阳能", "锂", "铜箔"],
        "医药/生物": ["医药", "生物", "医疗", "制药", "健康", "诊断", "基因", "蛋白", "药", "医"],
        "汽车/零部件": ["汽车", "零部件", "智能驾驶", "汽配", "驾驶", "车", "轮", "胎"],
        "机械/装备": ["机械", "装备", "制造", "工业", "智能", "机器人", "机床", "泵", "阀", "仪表"],
        "军工": ["军工", "航空", "航天", "兵装", "船舶", "导弹", "雷达", "防务", "武器"],
        "金融": ["银行", "保险", "证券", "金融", "信托", "租赁"],
        "地产/建筑": ["地产", "建筑", "装饰", "家居", "物业", "建材", "城", "建", "装"],
        "钢铁/煤炭": ["钢铁", "煤炭", "焦炭", "铁矿", "有色", "黄金", "铝", "铜", "稀土"],
        "数字/AI": ["数字", "网络", "软件", "信息", "数据", "云", "AI", "智能", "算法"],
    }
    for ind, kws in keywords.items():
        if any(kw in name for kw in kws):
            return ind
    return "其他"


def main():
    print("=" * 60)
    print("市场宽度采样 (top 200 + bottom 200)")
    print("=" * 60)

    print("\n[1/2] 抓取 top 200 (涨停端)...")
    top_items, total = fetch_with_retry(po=1, pz=200)
    print(f"  抓取到 {len(top_items)} 只, 全市场 {total} 只")

    print("\n[2/2] 抓取 bottom 200 (跌停端)...")
    bot_items, _ = fetch_with_retry(po=0, pz=200)
    print(f"  抓取到 {len(bot_items)} 只")

    limit_up = [x for x in top_items if is_limit_up(x.get("f12", ""), x.get("f3"))]
    limit_down = [x for x in bot_items if is_limit_down(x.get("f12", ""), x.get("f3"))]

    print("\n" + "=" * 60)
    print("涨跌停统计")
    print("=" * 60)
    print(f"涨停: {len(limit_up)} (来自 top {len(top_items)} 中)")
    for x in limit_up[:15]:
        print(f"  {x['f12']} {x['f14']} {x.get('f3', 0):.2f}%")
    if len(limit_up) > 15:
        print(f"  ...还有 {len(limit_up) - 15} 只")

    print(f"\n跌停: {len(limit_down)} (来自 bottom {len(bot_items)} 中)")
    for x in limit_down[:15]:
        print(f"  {x['f12']} {x['f14']} {x.get('f3', 0):.2f}%")
    if len(limit_down) > 15:
        print(f"  ...还有 {len(limit_down) - 15} 只")

    if limit_down:
        ratio = len(limit_up) / len(limit_down)
        print(f"\n涨跌停比: {len(limit_up)}:{len(limit_down)} = {ratio:.2f}")
    else:
        print(f"\n涨跌停比: {len(limit_up)}:0 (无跌停)")

    print("\n" + "=" * 60)
    print("涨停行业分布")
    print("=" * 60)
    ind_count = Counter()
    for x in limit_up:
        name = x.get("f14", "")
        ind_count[classify_industry(name)] += 1
    for ind, cnt in ind_count.most_common():
        pct = cnt / len(limit_up) * 100 if limit_up else 0
        print(f"  {ind}: {cnt} ({pct:.1f}%)")

    print("\n" + "=" * 60)
    print("Top 200 / Bottom 200 边界")
    print("=" * 60)
    if top_items:
        last = top_items[-1]
        print(f"Top 200 末位: {last['f12']} {last['f14']} {last.get('f3', 0):.2f}%")
    if bot_items:
        last = bot_items[-1]
        print(f"Bottom 200 末位: {last['f12']} {last['f14']} {last.get('f3', 0):.2f}%")

    print("\n" + "=" * 60)
    print("模式判定提示 (按 5 指标打分)")
    print("=" * 60)
    if len(limit_up) >= 100 and not limit_down:
        print("  -> [SUGGEST] S24 普涨确认 (涨停 100+, 跌停 0)")
    elif len(limit_up) >= 30 and len(limit_up) < 100 and len(limit_down) <= 1:
        print("  -> [SUGGEST] S29 强普涨+主线集中 (涨停 30-100, 跌停 <= 1)")
    elif len(limit_up) >= 100 and 1 <= len(limit_down) <= 10:
        print("  -> [SUGGEST] S27 题材普涨+权重分化 (涨停 100+, 跌停 1-10)")
    elif len(limit_up) < 20 and not limit_down:
        print("  -> [SUGGEST] S34 指数弱+个股中性 (涨停 < 20, 跌停 0) - 5 指标打分就是最终判据")
    elif len(limit_up) >= 20 and len(limit_up) < 70 and not limit_down:
        print("  -> [SUGGEST] S33 指数弱+个股强 (涨停 20-50, 跌停 0) - 需配合 6 指数全数收阴 + V 中等")
    else:
        print(f"  -> [SUGGEST] 按 5 指标打分判定 (涨停 {len(limit_up)}, 跌停 {len(limit_down)})")


if __name__ == "__main__":
    main()
