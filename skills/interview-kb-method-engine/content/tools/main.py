#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
面经知识库工具包 — 统一入口

⚠️ 命令从**包根目录**执行，写成 `python tools/main.py <子命令>`
   （本文件在 tools/ 下；直接写 `python main.py` 会 File not found）。

═══ 日常最常用的三条 ═══
    report   — 出《求职总报》（默认视角；`--view` 切换其他视角）
    record   — 建档：`record new` 建一场 / `record ask` 逐题追加 / `record fix` 补真值
    web      — 起本地图形界面（看卡片/报告/待办/趋势 + 与 agent 对话）

═══ 全部子命令 ═══
  建档与回填
    new      新建卡片骨架            (build_card.py)
    record   建档：new / ask / fix   (record.py)
    result   回填本轮结果（旧入口）  (build_card.py --id --outcome)
    merge    去重/冲突/把 _inbox 转正 (merge.py)
    remind   找"记录日+7 仍未回填真值"的场 (remind.py)

  报告与分析
    report   唯一报告入口（默认总报；旧名 report2/pulse/decision 均为 --view 别名）
    analyze  跨场统计                (cross_analysis.py)
    insights 痛点/优势体检            (insights.py)
    diagnosis 求职自我诊断            (diagnosis.py)
    strategy 求职定位/该投什么        (strategy.py)
    job      针对某份 JD 做 1-4 分析   (analyzer.py)
    answer   应答框架+缺口清单（复用你真过了的回答，不编造）(answer.py)
    evaluate 评估一场新面经           (predict.py)
    apply    下场决策：给 JD/公司 → 投/慎投 + 卡点 + 最佳高含金问答
    export   导出 CSV                (export_table.py)
    backtest 对定位/apply 做留一法回归基线

  赛道与质检
    tracks   赛道：define 定义 / show 查看 / set 逐卡指定 (tracks.py)
    validate 校验全部卡 + 跑 **7 组模块自检**（自检失败退出码非 0）
    selftest 全模块自检（Boss 相关）
    web      本地图形界面            (webserve.py)
    setup    首次向导：生成 profile.yaml + 提示建档 + 询问是否启用找岗模块

  简历
    resumecheck  校验结构化简历源    (resume_check.py)
    resumeedit   采纳/回退/diff 简历源 (resume_edit.py)
    resumerender 简历源 → 单栏 HTML/MD 终稿 (resume_render.py)
    resumeselftest 简历模块自检

  找岗（可选，需 Node.js 18+ 与 Chrome/Edge）
    boss        岗位池：解码 PUA 薪资 + 关键词分级筛选 (boss.py)
    bossmerge   合并多轮抓取，突破单次查询上限
    bosstojob   批量把抓到的 JD 喂给 job 做备战分析

═══ 用法示例 ═══
JD 分析：
    python tools/main.py job --jd "岗位JD文本" [--report markdown路径]
    python tools/main.py job --file jd.txt

应答框架（不生成漂亮答案，只复用你真过了的回答 + 标缺口）：
    python tools/main.py answer --jd-file jd.txt --report 应答框架.md
    python tools/main.py answer --q "你的缺点是什么" --q "讲个从0到1的项目"

回填真值：
    python tools/main.py record fix I007 --offer no
    python tools/main.py record fix I007 --why-ended "横向对比"

评估新面经：
    python tools/main.py evaluate "新面经文本"
    python tools/main.py evaluate --file new.txt

> 命令的**参数、口径、边界**以 `tools/ENGINE.md` 为唯一权威来源。
> 你也可直接把 JD 或新面经发给 AI，AI 会在会话内基于卡片做分析。
"""

import sys
import os
import subprocess

# Windows 控制台默认 GBK，直接 print 中文报告会乱码或被替换成 '?'。
# 统一在入口把 stdout/stderr 切到 UTF-8，子进程通过环境变量继承。
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))


def run(script, args):
    return subprocess.call([sys.executable, os.path.join(BASE, script)] + args)


def run_job():
    """在会话内执行 JD 的 1-4 分析并输出报告。"""
    args = sys.argv[2:]
    jd = None
    report = None
    i = 0
    while i < len(args):
        if args[i] == "--jd" and i + 1 < len(args):
            jd = args[i + 1]; i += 2
        elif args[i] == "--file" and i + 1 < len(args):
            try:
                with open(args[i + 1], "r", encoding="utf-8") as f:
                    jd = f.read()
            except Exception as e:
                print("读取失败:", e); return 1
            i += 2
        elif args[i] == "--report" and i + 1 < len(args):
            report = args[i + 1]; i += 2
        else:
            i += 1

    if not jd:
        print("job 需要 --jd '文本' 或 --file jd.txt")
        return 1

    import analyzer
    a = analyzer.Analyzer(jd)
    parts = [
        "# JD 分析报告\n",
        "## 1) 岗位职责画像\n", _f(a.analyze_job()),
        "\n## 2) 简历匹配度\n", _f(a.match_resume()),
        "\n## 3) 最匹配的面经/问题/最佳回答\n", _f(a.most_relevant()),
        "\n## 4) 预判会遇到的问题\n", _f(a.predict_questions()),
    ]
    report_text = "\n".join(parts)
    if report:
        with open(report, "w", encoding="utf-8") as f:
            f.write(report_text)
        print("[OK] 已生成:", report)
    else:
        print(report_text)
    return 0


def _f(obj):
    # 简易 dict → 文本（含嵌套 dict 用 yaml 展示更清晰）
    try:
        import yaml
        return yaml.dump(obj, allow_unicode=True, sort_keys=False, default_flow_style=False)
    except Exception:
        return str(obj)


# ── 报告视角：多个报告命令合并到 report --view ───────────────────────
#
# ═══ 为什么要合并（v3.4.0）═══
# 此前有 7 个报告命令（report/report2/pulse/decision/diagnosis/strategy/insights），
# 实测它们**重复输出同一批核心章节**：
#   轮次通过率总览 / 正编vs外包 / 主场赛道 / 业务过但offer=no —— 5 个命令各算一遍。
# 更糟的是同一口径在多处各写一份实现，历史上因此出过
# 「四个模块算出四个不同的正编外包拆分」。全部 7 个模块共享 industry_taxonomy 内核，
# 却没有单一出口。
#
# 现在的约定：
#   · `report`   —— 默认视角，=《求职总报》（唯一总报，章节最全）
#   · `--view 轮次|脉搏|决策|诊断|定位|痛点` —— 切到对应视角
#   · 老命令名（report2/pulse/decision/…）**全部保留为别名**，行为不变
#     —— 不破坏任何已有用法与脚本。
# 合并方式是**委托**：转到对应模块执行，逻辑一行没动，输出与旧版逐字节一致。

_VIEWS = {
    "总报":   ("report_all.py", "唯一《求职总报》—— 章节最全，日常默认看这个"),
    "轮次":   ("report2.py",    "轮次口径 + 正编/外包拆分（旧 report2）"),
    "脉搏":   ("report3.py",    "动态洞察：趋势 + 跨界告警（旧 pulse）"),
    "决策":   ("decision.py",   "浓缩决策：定位_v2 + pulse_v2 两份（旧 decision）"),
    "诊断":   ("diagnosis.py",  "4 问自我诊断（旧 diagnosis）"),
    "定位":   ("strategy.py",   "求职定位：匹配 vs 跨界（旧 strategy）"),
    "痛点":   ("insights.py",   "痛点/优势体检（旧 insights）"),
}

# 旧命令名 → 视角名
_ALIASES = {
    "report2": "轮次", "pulse": "脉搏", "decision": "决策",
    "diagnosis": "诊断", "strategy": "定位", "insights": "痛点",
}


def _view(name, rest=None):
    """跑某个报告视角。"""
    mod = _VIEWS[name][0]
    return run(mod, rest or [])


def _report(args):
    """`report [--view <视角>] [其他参数]` 的统一入口。"""
    args = list(args)
    view = "总报"
    if "--view" in args:
        i = args.index("--view")
        if i + 1 >= len(args):
            print("[错误] --view 后面要跟视角名。可选：" + " / ".join(_VIEWS))
            return 2
        view = args[i + 1]
        del args[i:i + 2]
    # 也支持 `--view=轮次` 写法
    for a in list(args):
        if a.startswith("--view="):
            view = a.split("=", 1)[1]
            args.remove(a)

    if view in ("list", "?", "help"):
        print("可用视角（report --view <名>）：")
        for k, (mod, desc) in _VIEWS.items():
            print(f"  {k:<4} {desc}")
        print("\n不加 --view 就是「总报」（默认，章节最全）。")
        return 0

    if view not in _VIEWS:
        print(f"[错误] 未知视角：{view}")
        print("       可选：" + " / ".join(_VIEWS))
        print("       看说明：python tools/main.py report --view list")
        return 2
    return _view(view, args)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "new":
        return run("build_card.py", rest)
    if cmd == "result":
        return run("build_card.py", rest)
    if cmd == "analyze":
        return run("cross_analysis.py", rest)
    if cmd == "job":
        return run_job()
    if cmd == "evaluate":
        return run("predict.py", rest)
    if cmd == "answer":   # 应答框架+缺口：只复用你真过了的回答，没素材的直接标缺口
        return run("answer.py", rest)
    if cmd == "strategy":
        return run("strategy.py", rest)
    if cmd == "insights":
        return run("insights.py", rest)
    if cmd == "diagnosis":
        return run("diagnosis.py", rest)
    if cmd == "apply":   # 下场决策：给 JD/公司 → 投/慎投 + 卡点 + 最佳高含金问答
        return run("predict_apply.py", rest)
    if cmd == "report2": # 旧名 → 等价于 report --view 轮次
        return _view("轮次", rest)
    if cmd == "pulse":  # 旧名 → 等价于 report --view 脉搏
        return _view("脉搏", rest)
    if cmd == "decision":  # 旧名 → 等价于 report --view 决策（生成两份浓缩报告）
        return _view("决策", rest)
    if cmd == "report":   # ⭐ 主入口：默认《求职总报》；--view 切换其他视角
        return _report(rest)
    if cmd == "record":   # 建档：record new 建一场 / record ask 随时逐题追加(不限题目数)
        return run("record.py", rest)
    if cmd == "backtest": # 对定位/apply 做留一法回归基线
        return run("backtest.py", rest)
    if cmd == "tracks":   # 赛道：define 定义你的类目 / show 查看 / set 逐卡指定
        return run("tracks.py", rest)
    if cmd == "setup":   # 首次运行向导：生成 profile.yaml + 提示建档
        return run("setup.py", rest)
    if cmd == "merge":   # 去重/冲突/把 _inbox 转正 (scan/formailize/--dry)
        return run("merge.py", rest)
    if cmd in ("contract", "fill"):  # 最小契约：每场只回填这 3 样
        print("每场面试后，你只需回填 3 样：")
        print("① outcome  = pass / fail   —— 这轮过没过")
        print("② why_ended= 横向 / 审批不通过 / 简历背调 / 卡薪资 / base / 外包无转正（若①=pass但③=no也填）")
        print("③ offer    = got / no / ongoing —— 最终有没有拿到")
        print("填完即可 python tools/main.py report 刷新唯一总报。CONTRACT.md 有填空模板。")
        return 0
    if cmd == "export":
        return run("export_table.py", rest)
    if cmd == "web":   # 面经台：本地图形界面（看板/报告/待办/趋势/同类题）
        return run("webserve.py", rest)
    if cmd == "remind":  # 回填真值闹钟：找记录+7 天仍未回填实际结果的场
        return run("remind.py", rest)
    if cmd == "resumecheck":  # skill v3「简历修改」阶段：校验结构化简历源（≥2成果点/数据对比）
        return run("resume_check.py", rest)
    if cmd == "resumeedit":  # 采纳/回退/diff 编辑简历源（人主辅机，保留 baseline）
        return run("resume_edit.py", rest)
    if cmd == "resumerender":  # 简历源 → 单栏 HTML/Markdown 终稿
        return run("resume_render.py", rest)
    if cmd == "validate":   # 校验全部卡：YAML 语法 + 必填字段 + outcome 枚举（并顺带跑 Boss 自检）
        return run("validate.py", rest)
    if cmd == "boss":   # Boss直聘岗位：解码PUA薪资 + 关键词分级筛选
        return run("boss.py", rest)
    if cmd == "bossmerge":   # 合并多轮抓取，突破单次查询上限
        return run("boss.py", ["merge"] + rest)
    if cmd == "bosstojob":   # 批量：把抓到的 JD 逐条喂给 job 做备战分析
        return run("boss.py", ["tojob"] + rest)
    if cmd == "resumeselftest":   # 简历模块自检（个人总结 5 条规则）
        return run("resume_check.py", ["selftest"] + rest)
    if cmd == "selftest":   # 全模块自检（PUA解码/薪资解析/分级），失败退出码非0
        rc = run("boss.py", ["selftest"] + rest)
        return rc
    print("未知子命令:", cmd)
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
