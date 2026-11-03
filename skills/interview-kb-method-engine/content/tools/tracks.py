#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tracks.py — 「赛道」的交互式定义与逐卡指定。

═══ 为什么要有这个模块 ═══
赛道归类是本工具里**最依赖业务判断**的一环，而引擎猜不准 ——
实测被使用者连续纠正 6 处（按JD映射 / 海外≠出海 / 商店画报也是内容策略 /
某体育社区影视是垂类 / 某小说社区是社区运营 / 到餐那三个都是产品运营）。

所以「赛道」不该是一段藏在 config.yaml 里的词表，而应该像
「这场过没过」「是不是外包」一样 —— **在使用流程里直接被问到**。

本模块提供两件事：
  ① define_tracks()  —— 首次 setup 时问"你面过哪些方向"，写进 config.track_rules
  ② ask_track_for()  —— 新建一场面经时问"这场归哪类"，写进 config.card_track

═══ 与其它机制的关系（优先级从高到低）═══
  ① config.card_track   逐卡指定   ← 本模块的 ask_track_for 写这里（最准）
  ② config.track_rules  关键词规则 ← 本模块的 define_tracks 写这里
  ③ 引擎内置词表         兜底
"""
import io
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(BASE, "config.yaml")

# 常见方向：给用户一个起点，而不是让他从空白开始想
COMMON_TRACKS = [
    ("内容运营", "写内容、做内容供给/生态"),
    ("策略运营", "定策略/机制/分发/推荐"),
    ("产品运营", "偏产品侧的运营（产运）"),
    ("垂类", "某个垂类的内容运营（美食/数码/影视…）"),
    ("社区运营", "社区/社群/圈子"),
    ("创作者运营", "创作者/作者/UP主/达人"),
    ("活动运营", "活动策划/赛事"),
    ("达人营销", "KOC/KOL/达人商业化"),
    ("生态运营", "标签/模型/治理/风控"),
    ("用户增长", "拉新/促活/留存"),
]


def _load_cfg():
    try:
        import yaml
        if os.path.exists(CONFIG):
            with io.open(CONFIG, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        pass
    return {}


def _save_cfg(cfg):
    """写回 config.yaml（保留可读格式；无 config 时从 example 复制一份）。"""
    import yaml
    if not os.path.exists(CONFIG):
        ex = os.path.join(BASE, "config.example.yaml")
        if os.path.exists(ex):
            io.open(CONFIG, "w", encoding="utf-8", newline="\n").write(
                io.open(ex, encoding="utf-8").read())
    with io.open(CONFIG, "w", encoding="utf-8", newline="\n") as f:
        f.write("# config.yaml —— 你的个性化配置（由 setup / record 自动维护）\n")
        f.write("# 赛道相关：track_rules 定义你分哪几类；card_track 逐卡指定（最准）\n\n")
        yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False,
                       default_flow_style=False, width=200)


def existing_tracks():
    """当前已定义的赛道名（用户自定义优先，其次内置）。"""
    cfg = _load_cfg()
    out = list((cfg.get("track_rules") or {}).keys())
    try:
        sys.path.insert(0, BASE)
        from industry_taxonomy import taxonomy
        for k in taxonomy().keys():
            if k not in out:
                out.append(k)
    except Exception:
        pass
    return out


def _ask(prompt, default=""):
    try:
        if default:
            a = input("%s [%s]: " % (prompt, default)).strip()
            return a if a else default
        return input("%s: " % prompt).strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print("[提示] 检测不到交互式输入，已跳过。非交互请用命令行参数。")
        return default or ""


def define_tracks(noninteractive=False):
    """首次定义赛道：问用户"你面过哪些方向"。

    写入 config.track_rules。已定义过则跳过（除非用户要求重定义）。
    """
    cfg = _load_cfg()
    if (cfg.get("track_rules") or {}) and not noninteractive:
        cur = list(cfg["track_rules"].keys())
        print()
        print("  你已定义过 %d 个赛道：%s" % (len(cur), "、".join(cur)))
        a = _ask("  要重新定义吗？(y/n)", "n").lower()
        if a not in ("y", "yes", "是", "1"):
            return cur

    print()
    print("=" * 68)
    print("  定义你的【赛道】—— 这个必须你自己定")
    print("=" * 68)
    print()
    print("  为什么要问你：赛道归类靠业务判断，引擎猜不准。")
    print("  实测被纠正过多次，例如：")
    print("    · 「浏览器海外业务」其实是内容策略，不是出海（海外只是市场）")
    print("    · 「应用商店/画报的内容运营」也是内容岗（载体不是方向）")
    print("    · 「某体育社区影视评分运营」算垂类、「某小说社区」算社区运营")
    print()
    print("  【怎么定】按你**实际在做什么**分，不按公司、不按平台、不按题材。")
    print("  下面这些是常见的，你挑要用的（回车采用默认全选）：")
    print()
    for i, (name, desc) in enumerate(COMMON_TRACKS, 1):
        print("    %2d. %-10s %s" % (i, name, desc))
    print()
    if noninteractive:
        chosen = [n for n, _ in COMMON_TRACKS]
    else:
        raw = _ask("  保留哪些？(回车=全部 / 输入序号如 1,2,5 / 或直接写你自己的，逗号分隔)", "")
        if not raw:
            chosen = [n for n, _ in COMMON_TRACKS]
        else:
            chosen = []
            for part in raw.replace("，", ",").split(","):
                part = part.strip()
                if not part:
                    continue
                if part.isdigit() and 1 <= int(part) <= len(COMMON_TRACKS):
                    chosen.append(COMMON_TRACKS[int(part) - 1][0])
                else:
                    chosen.append(part)      # 用户自己起的名字
    # 去重保序
    seen, tracks = set(), []
    for t in chosen:
        if t and t not in seen:
            seen.add(t)
            tracks.append(t)

    # 写进 track_rules（用赛道名本身做关键词，保证至少能被同名岗位命中）
    cfg.setdefault("track_rules", {})
    for t in tracks:
        cfg["track_rules"].setdefault(t, [t])
    _save_cfg(cfg)
    print()
    print("  ✅ 已记录 %d 个赛道：%s" % (len(tracks), "、".join(tracks)))
    print("     （存在 tools/config.yaml，随时可改）")
    return tracks


def ask_track_for(company="", position="", noninteractive=False, default=""):
    """为**一场面试**指定赛道。写入 config.card_track。

    返回赛道名；跳过则返回 ""（表示交给词表判）。
    """
    tracks = existing_tracks()
    # 先猜一个（用词表），作为默认值 —— 用户只要回车或改一下即可
    guess = default
    if not guess:
        try:
            sys.path.insert(0, BASE)
            from industry_taxonomy import classify_position
            guess = classify_position(company, position, fallback="")
        except Exception:
            guess = ""

    print()
    print("  这场面试归哪类赛道？")
    print("    %s · %s" % (company or "(公司未填)", (position or "(岗位未填)")[:40]))
    print("    已有赛道：%s" % "、".join(tracks[:12]) + ("…" if len(tracks) > 12 else ""))
    if guess:
        print("    （我按词表猜是「%s」，回车即可；也可以直接写别的）" % guess)
    if noninteractive:
        return guess
    ans = _ask("  赛道", guess or (tracks[0] if tracks else ""))
    ans = (ans or "").strip()
    if ans in ("-", "跳过", "skip", "不填"):
        return ""
    return ans


def set_card_track(card_id, track):
    """把「卡号 → 赛道」写进 config.card_track。"""
    cfg = _load_cfg()
    cfg.setdefault("card_track", {})
    cfg["card_track"][str(card_id).upper()] = str(track)
    _save_cfg(cfg)
    return True


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "show"
    if cmd == "define":
        define_tracks()
    elif cmd == "show":
        print("已定义赛道：")
        for t in existing_tracks():
            print("  " + t)
    elif cmd == "set" and len(sys.argv) > 3:
        set_card_track(sys.argv[2], sys.argv[3])
        print("[OK] %s -> %s" % (sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
