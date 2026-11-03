#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
strategy.py — 求职定位与策略洞察（定位分析模块）

从已存档的面经卡片，自动产出"定位洞察"型结论（区别于 cross_analysis 的数据统计、
insights 的痛/优点聚合）。它回答的是方向性问题：

1. 我的优势赛道是什么（按公司/岗位类型统计通过率）
2. 我应该投 / 慎投 / 别投哪些岗位（识别匹配 vs 跨界/降维/错配）
3. 我反复挂的真实卡点是哪些（跨界/职级/稳定性/外包/回流/评价高但黄了）
4. 给我定位建议（往哪条主线倾斜）

核心思想（结合 40 场实证）：
- 你不是能力问题，是"投错地方"——分赛道看通过率差异巨大。
- 你偏"策略/数据/内容方法论"，而非"垂类执行/头部作者深度运营"。
- 你反复"评价高但 offer 黄"多因非业务因素（职级/稳定性/回流/外包）而非表现。

用法（复用 tools/ 下卡片）：
    python strategy.py                 # 生成《求职定位报告.md》
    python strategy.py --plain         # 终端直接打印
"""

import os
import re
import glob
import argparse
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    yaml = None

try:
    from industry_taxonomy import offer_flag, nature_of
except Exception:
    def offer_flag(card): return ''
    def nature_of(card, default="正编"): return default

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(BASE, "..", "cards")
OUT = os.path.join(BASE, "..", "求职定位报告.md")

# ---- 岗位/行业分类规则（把 position 归类，识别跨界/匹配）----
# 关键强项信号词（你最有竞争力、最该讲的方向）
STRENGTH_KEYWORDS = [
    "内容策略", "策略运营", "产运", "数据", "推荐", "标签", "分发",
    "创作者策略", "中台", "内容运营", "垂类运营", "社区运营", "内容产运",
]
# 跨界/弱信号词（这些方向方法论难复制，通过率通常低）
# 注：此处只放【通用品类词】，你自己的具体公司名请写进 config.yaml 的 cross_industry 里。
CROSS_INDUSTRY_KEYWORDS = [
    "硬件", "电子书", "墨水屏", "汽车", "财经", "股票",
    "民宿", "AI数字人", "AIGC", "本地生活", "泛生活", "外包", "招聘", "快聘",
    "播客", "数字人",
]


def _load_user_config():
    """读取可选的 config.yaml（用户自建，见 config.example.yaml）。找不到就用空配置。"""
    for name in ("config.yaml", "config.yml"):
        p = os.path.join(BASE, name)
        if os.path.exists(p):
            try:
                import yaml as _yaml
                with open(p, encoding="utf-8") as f:
                    return _yaml.safe_load(f) or {}
            except Exception:
                return {}
    return {}


def _industry_rules():
    """行业识别规则：内置【通用品类词】+ 用户在 config.yaml 里自定义的 company→industry 映射。

    这样引擎本身不含任何个人公司名；用户把自己面过的公司填进 config 即可。
    """
    base = [
        (["智能硬件", "墨水屏", "电子书"], "智能硬件/硬件"),
        (["民宿"], "民宿/本地生活"),
        (["AI数字人", "数字人"], "AI/数字人"),
        (["汽车", "车企"], "汽车"),
        (["财经", "股票", "证券"], "财经/金融"),
        (["播客"], "播客/音频"),
        (["招聘", "快聘"], "招聘/蓝领"),
    ]
    user = _load_user_config()
    for comp, ind in (user.get("industry_map") or {}).items():
        base.insert(0, ([str(comp)], str(ind)))
    return base


def industry_of(company, position):
    t = (company or "") + "|" + (position or "")
    for kws, ind in _industry_rules():
        if any(k in t for k in kws):
            return ind
    return "其他"


def is_cross(company, position):
    t = (company or "") + "|" + (position or "")
    user = _load_user_config()
    extra = user.get("cross_industry") or []
    kws = list(CROSS_INDUSTRY_KEYWORDS) + [str(x) for x in extra]
    return any(k in t for k in kws)




def normalize_outcome(out):
    out = str(out or "")
    if "pass" in out.lower():
        return "pass"
    if "fail" in out.lower() or "挂" in out:
        return "fail"
    return "unknown"


class StrategyAnalyzer:
    def __init__(self):
        self.cards = self.load_cards()

    def load_cards(self):
        cards = []
        if yaml is None:
            return cards
        for p in sorted(glob.glob(os.path.join(CARDS, "I*.yaml"))):
            try:
                c = yaml.safe_load(open(p, encoding="utf-8"))
            except Exception:
                continue
            if c:
                c["_id"] = c.get("id") or os.path.basename(p).split("_")[0]
                cards.append(c)
        return cards

    def analyze(self):
        # 分行业通过率
        ind = defaultdict(lambda: {"pass": 0, "fail": 0, "cards": []})
        # 跨界 vs 匹配
        cross_stat = {"pass": 0, "fail": 0, "cards": []}
        match_stat = {"pass": 0, "fail": 0, "cards": []}
        # 外包
        contract_stat = {"pass": 0, "fail": 0, "cards": []}
        # 评价高但黄(fail)的场(供"非业务卡点"分析近证据可能不足,靠用户补)
        highpraise_fail = []
        # 用于识别的样本
        for c in self.cards:
            inter = c.get("interview", {}) or {}
            res = c.get("result", {}) or {}
            comp = str(inter.get("company", ""))
            pos = str(inter.get("position", ""))
            date = str(inter.get("date", ""))
            out = normalize_outcome(res.get("outcome"))
            if out == "unknown":
                continue
            indus = industry_of(comp, pos)
            ind[indus]["pass" if out == "pass" else "fail"] += 1
            ind[indus]["cards"].append((c["_id"], pos, date, out))

            if is_cross(comp, pos):
                cross_stat["pass" if out == "pass" else "fail"] += 1
                cross_stat["cards"].append((c["_id"], comp.split("·")[0][:10], pos[:18], out))
            else:
                match_stat["pass" if out == "pass" else "fail"] += 1
                match_stat["cards"].append((c["_id"], comp.split("·")[0][:10], pos[:18], out))

            # 用卡的显式 nature（最可信），文本兜底只在 nature 为空时生效 ——
            # 见 industry_taxonomy.nature_of 的说明。
            if nature_of(c, default="") in ("外包", "兼职", "实习"):
                contract_stat["pass" if out == "pass" else "fail"] += 1
                contract_stat["cards"].append((c["_id"], comp.split("·")[0][:10], pos[:18], out))

        # 组装报告
        L = []
        L.append("# 求职定位与策略洞察报告\n")
        L.append(f"> 基于 {len(self.cards)} 场面经自动生成（定位分析模块 strategy.py）。\n")

        # 0) 总体
        total_p = sum(v["pass"] for v in ind.values())
        total_f = sum(v["fail"] for v in ind.values())
        total = total_p + total_f
        L.append(f"## 0) 总览\n- 已标记结果 {total} 场 ｜ 通过 {total_p} ｜ 未通过 {total_f} ｜ 业务面通过率 "
                 f"**{round(total_p/max(total,1)*100,1)}%**\n")

        # 1) 分行业通过率
        L.append("## 1) 我的优势赛道（按公司分：通过率高的才是你的主战场）\n")
        L.append("| 公司/行业 | 通过 | 未过 | 通过率 |")
        L.append("|---|---|---|---|")
        for indus, st in sorted(ind.items(), key=lambda x: -self._rate(x[1])):
            p, f = st["pass"], st["fail"]
            L.append(f"| {indus} | {p} | {f} | {self._rate(st)}% |")
        L.append("")

        # 2) 跨界 vs 匹配
        L.append("## 2) 定位判断：跨界 vs 匹配赛道\n")
        cm = self._rate(cross_stat)
        mm = self._rate(match_stat)
        L.append(f"- **匹配赛道（内容/社区/垂类主流大厂）**：通过 {match_stat['pass']} / 挂 {match_stat['fail']} → 通过率 **{mm}%**")
        L.append(f"- **跨界/新行业/降维（硬件/财经/汽车/本地生活/外包...）**：通过 {cross_stat['pass']} / 挂 {cross_stat['fail']} → 通过率 **{cm}%**")
        L.append("")
        L.append("> 若跨界通过率明显低于匹配赛道，强烈建议把火力集中在匹配赛道，而不是再造网跨行业。\n")

        L.append("### 匹配赛道明细\n")
        for cid, comp, pos, out in match_stat["cards"]:
            L.append(f"- [{'通过' if out=='pass' else '挂'}] {cid} {comp} · {pos}")
        L.append("\n### 跨界/降维赛道明细\n")
        for cid, comp, pos, out in cross_stat["cards"]:
            L.append(f"- [{'通过' if out=='pass' else '挂'}] {cid} {comp} · {pos}")
        L.append("")

        # 3) 卡点识别
        L.append("## 3) 真实卡点（为什么有的黄了）\n")
        # 外包
        if contract_stat["pass"] or contract_stat["fail"]:
            L.append(f"**外包岗**：通过 {contract_stat['pass']} / 挂 {contract_stat['fail']}"
                     f"（若非正编岗，注意降维/职级错配；即使通过也考虑是否想去）")
            for cid, comp, pos, out in contract_stat["cards"]:
                L.append(f"  - [{'通过' if out=='pass' else '挂'}] {cid} {comp} · {pos}")
            L.append("")
        # 用户补充信息（通过但不入职 / 高评价但挂）
        L.append("**'非业务卡点'（面试通过/评价高但未拿 offer）——需用户确认才准**：")
        _nbo = []
        for c in self.cards:
            _r = (c.get("result", {}) or {})
            # ⚠️ 这里曾经写成 in ("no","False","false") —— 那是在给一个
            #    类型 bug 打补丁：YAML 把裸写的 no/false 解析成布尔 False，
            #    于是有人看到值变成 "False" 就把它硬塞进白名单。
            #    现在统一走 offer_flag()，布尔/字符串/中文写法都能认。
            if str(_r.get("outcome", "")).strip() == "pass" and offer_flag(c) == "no":
                _nbo.append(c)
        if _nbo:
            _comp = "、".join(sorted({str((c.get("interview", {}) or {}).get("company", "")) for c in _nbo} - {""})) or "（见下方明细）"
            L.append(f"从数据看，{_comp} 等出现「通过轮次却最终没拿 offer」——通常说明能力展示没问题；")
        else:
            L.append("从数据看，暂无「通过轮次却最终没拿 offer」的明显样本；")
        L.append("但最终落空多为 职级/薪资/回流/外包/家庭gap 等非业务因素，而非面试表现。建议在 result.reason 标注。\n")

        # 4) 定位建议
        L.append("## 4) 定位建议\n")
        best_ind = max(ind.items(), key=lambda x: self._rate(x[1]))[0] if ind else ""
        L.append(f"- **主攻赛道**：{best_ind or '（数据不足）'} 等你历史通过率较高的方向、正编岗优先。")
        L.append("- 反复被认可的多是你的**通用方法论**（内容/社区/创作者/数据策略），"
                 "建议投能复用这些方法论的岗，避免与完全陌生的执行向岗位硬拼。")
        L.append("- 跨界新行业（与你过往经历行业不同、外包岗等）历史上通过率低，除非职级到或极大匹配，否则慎投。")
        L.append("- 处理软信号：职级预期、稳定性、家庭gap、外包/降维态度——这些常决定成败。\n")
        return "\n".join(L)

    @staticmethod
    def _rate(st):
        p, f = st.get("pass", 0), st.get("fail", 0)
        total = p + f
        return round(p / total * 100, 1) if total else 0


def main():
    ap = argparse.ArgumentParser(description="求职定位分析")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--plain", action="store_true")
    args = ap.parse_args()

    a = StrategyAnalyzer()
    rep = a.analyze()
    if args.plain:
        print(rep)
        return 0
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(rep)
    print(f"[OK] 已生成求职定位报告 -> {args.out}")
    return 0


if __name__ == "__main__":
    exit(main())
