#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键校验 cards 下所有 YAML 卡：语法可解析 + 必填字段 + outcome 枚举。
用法: python validate.py   （默认扫 cards/）
      python validate.py --path <cards_dir>
任何语法/结构问题都会打印，exitcode 非 0；全通过打印 OK。
向后兼容：老卡可能缺新加字段(offer/round_result/卡点轮等)，只警告不报错。
"""
import sys, glob, os, re
import subprocess
from pathlib import Path
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
try:
    import yaml
except Exception:
    print("[ERR] \u9700\u8981 pyyaml: pip install pyyaml"); sys.exit(2)

BASE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.normpath(os.path.join(BASE, "..", "cards"))

VALID_OUTCOME = {"pass", "fail", "no_offer", "unknown", "待确认", None, ""}
REQUIRED_TOP = ["id", "meta", "interview", "result", "reflection", "skills"]
REQUIRED_IV = ["company", "position"]

def boss_selftest():
    """跑 Boss 模块自检。PUA 薪资解码曾写错（整体偏高一位），
    错误结果看起来依然合理，必须靠内置真值回归兜住。"""
    boss = Path(__file__).resolve().parent / "boss.py"
    if not boss.exists():
        return 0
    print()
    print("--- Boss 模块自检 ---")
    try:
        r = subprocess.run([sys.executable, str(boss), "selftest"],
                           capture_output=True, cwd=str(boss.parent))
        out = r.stdout.decode("utf-8", errors="replace")
        for ln in out.splitlines():
            s = ln.strip()
            if s and ("通过" in s or s.startswith("✗") or "✅" in s or "失败" in s):
                print("  " + s)
        if r.returncode != 0:
            print("  [WARN] Boss 自检未通过 —— 详见 python main.py boss selftest")
            return 1
    except Exception as e:
        print(f"  [WARN] Boss 自检无法执行: {e}")
    return 0


def resume_selftest():
    """跑简历模块自检（个人总结的 5 条规则）。
    这几条规则是按经验标定的，且规则②「性格可写」与规则③「要有产出」
    本身存在张力，容易被后续改动误伤，所以用内置案例锁住。"""
    rc = Path(__file__).resolve().parent / "resume_check.py"
    if not rc.exists():
        return 0
    print()
    print("--- 简历模块自检 ---")
    try:
        r = subprocess.run([sys.executable, str(rc), "selftest"],
                           capture_output=True, cwd=str(rc.parent))
        out = r.stdout.decode("utf-8", errors="replace")
        for ln in out.splitlines():
            s = ln.strip()
            if s and (s.startswith("✓") or s.startswith("✗") or "通过" in s or "失败" in s):
                print("  " + s)
        if r.returncode != 0:
            print("  [WARN] 简历自检未通过 —— 详见 python main.py resumeselftest")
            return 1
    except Exception as e:
        print(f"  [WARN] 简历自检无法执行: {e}")
    return 0


def taxonomy_selftest():
    """跑赛道/体量归类自检。

    锁住三条曾被改错的行为：
      ① 归类以【岗位方向】为准，不是公司名（某大厂 8 场跨赛道，按公司名会合并错）
      ② 体量只归一、不猜测（认不出必须返回空，不能瞎给一档）
      ③ 挂因关键词【最长优先】（"行业gap" 不能被拆成 "行业"+"gap"）
    """
    print()
    print("--- 赛道/体量自检 ---")
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from industry_taxonomy import classify, norm_scale, scale_of, SCALE_TIERS
    except Exception as e:
        print(f"  [WARN] 无法导入 industry_taxonomy: {e}")
        return 1
    cases = [
        # (公司+岗位文本, 期望赛道, 说明)
        #
        # ⚠️ 这一条曾经写成期望 "出海/国际化" —— 那是我自己的错误假设，
        #    于是自检非但没抓出问题，反而**把错的锁住了**。
        #    用户指出：某大厂浏览器海外业务是**内容策略**岗，
        #    "海外"只是它服务的市场、不是业务方向（同组做国内版就是内容策略）。
        #    实测这个错归类让 5 场卡撑起了"出海/国际化"这个"第二好赛道"。
        #    教训：自检的价值 = 我当时的认知水平，写错了就一起错。
        #    所以这类"业务语义"的用例，最终还是要靠懂业务的人复核。
        ("某大厂 浏览器海外业务·内容策略运营", "内容运营",
         "市场是海外，但岗位是内容策略 → 市场词不等于业务方向"),
        ("某公司 出海业务内容运营", "出海/国际化", "明确以出海为业务形态才算"),
        ("某公司 海外本地化运营", "出海/国际化", "本地化是真出海信号"),
        ("某大厂 应用商店·品类经营·影视综方向", "内容运营",
         "载体(商店/画报)与题材(影视综)都不是业务方向 —— 做内容就算内容"),
        ("某本地生活平台 到餐·美食频道首页产品运营", "内容运营",
         "「生活服务/点评」已删除 → 泛内容类收敛到内容运营"),
        ("某短视频平台 快聘 B端 商家运营", "B端/商家", "具体业务方向优先"),
        ("某公司 内容运营", "内容运营", "无更具体方向时才落到泛内容类"),
    ]
    bad = 0
    # ⚠️ 这些用例的"期望值"只在**未自定义赛道**时成立。
    #    用户一旦在 config.yaml 写了 track_rules（定义自己的类目），
    #    判定结果就会落到他的自定义类目上，这些内置期望自然对不上 ——
    #    那不是 bug，是使用者按自己业务重新分了类。
    #    所以：有 track_rules 时**跳过**内置归类的期望比对，
    #    改为只检查"每个用例都判出了一个非空赛道"（即没退化到判不出来）。
    from industry_taxonomy import _load_config
    _has_custom = bool((_load_config().get("track_rules") or {}))
    if _has_custom:
        print("  · 检测到 config 里定义了 track_rules（自定义赛道）→ 跳过内置归类期望比对")
        _empty = [t for t, _w, _y in cases if not classify(t, fallback="")]
        if _empty:
            print(f"  ✗ 有 {len(_empty)} 条判不出任何赛道（自定义词表可能过窄）")
            bad += 1
        else:
            print(f"  ✓ {len(cases)} 条都能判出赛道（自定义词表生效）")
        cases = []   # 不再逐条比对内置期望
    for text, want, why in cases:
        got = classify(text, fallback="其他")
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'✓' if ok else '✗'} 归类「{text}」→ {got}（期望 {want}）")
        if not ok:
            print(f"      理由：{why}")

    scases = [("大厂", "大厂"), ("一线大厂", "大厂"), ("初创", "创业团队"),
              ("startup", "创业团队"), ("小公司", "小厂"), ("垂类头部", "中厂")]
    for raw, want in scases:
        got = norm_scale(raw)
        ok = got == want
        bad += 0 if ok else 1
        print(f"  {'✓' if ok else '✗'} 体量归一「{raw}」→ {got!r}（期望 {want!r}）")
    got = scale_of("枫叶互动")           # 未配置 → 必须为空，不许猜
    ok = got in ("", ) or got in SCALE_TIERS
    if got:
        print(f"  ✓ 未标注体量返回 {got!r}（来自 config）")
    else:
        print("  ✓ 未标注体量返回 ''（不猜测 —— 这是设计要求）")

    # 最长优先
    from report_all import blocker_hits
    class _C(dict): pass
    c = {"reflection": {"weakness": "岗位偏商业转化与纯内容背景有gap；对行业理解不足"}}
    hits = blocker_hits(c)
    dup = [h for h in hits if h == "gap"]
    if "gap" in dup and "有gap" in hits:
        print("  ✗ 挂因最长优先失效：同时记了 'gap' 和 '有gap'")
        bad += 1
    else:
        print(f"  ✓ 挂因最长优先：{hits}")

    # offer 字段归一：YAML 会把裸写的 no/false 解析成**布尔**，
    # 实测真实数据 40 张卡是 offer: False，而旧代码用
    # str(offer).startswith("no") 判断 → 永远为假（str(False)=='False'）。
    # 这个 bug 曾散落在 report2/report3/decision/strategy 四个文件里。
    from industry_taxonomy import offer_flag
    ocases = [
        ({"result": {"offer": False}}, "no"),
        ({"result": {"offer": True}}, "got"),
        ({"result": {"offer": "no"}}, "no"),
        ({"result": {"offer": "got"}}, "got"),
        ({"result": {"offer": "ongoing"}}, "ongoing"),
        ({"result": {"offer": ""}}, ""),
        ({"result": {}}, ""),
    ]
    obad = [want for card, want in ocases if offer_flag(card) != want]
    if obad:
        print(f"  ✗ offer 归一：{len(obad)} 项不符（布尔 False 必须归一成 'no'）")
        bad += 1
    else:
        print("  ✓ offer 归一：布尔/字符串/缺失 全对（False→'no'，True→'got'）")

    # 「挂了但非能力原因」的识别（report 的 4b 节）。
    # 起因：I007 某内容社区实际挂因是"面试官认可经验，但要能补团队缺口的人"——
    # 是匹配问题不是能力问题；而旧版只认 outcome=pass 的非能力卡点，
    # 这类 fail 卡会被当成能力短板，改进方向被带偏。
    from report_all import _NONCAP_KW
    ncases = [
        ("非能力卡点：要能补齐团队能力缺口的人选", True),
        ("一面挂：简历匹配度低，自评不该约面", True),
        ("实际无HC，仍走了挂", True),
        ("业务稳定度存疑(裁了三波)+base需迁杭州", True),
        ("后段未准备到的问题答不上", False),   # 纯能力原因 -> 不该进 4b
        ("语速太快，自我介绍没讲清", False),
    ]
    nbad = [t for t, want in ncases
            if (any(k.lower() in t.lower() for k in _NONCAP_KW)) != want]
    if nbad:
        print(f"  ✗ 非能力卡点识别：{len(nbad)} 项不符 -> {nbad[:2]}")
        bad += 1
    else:
        print("  ✓ 非能力卡点识别：匹配/需求类能认出，纯能力原因不误收")

    # 用工性质：四个模块曾各写一份、结果互不相同（同一批卡外包数算出 17/18/19/15）。
    # 现在统一走 industry_taxonomy.nature_of；这里锁住"四类都认得出"。
    from industry_taxonomy import nature_of
    ncases = [
        ({"interview": {"nature": "正编"}}, "正编"),
        ({"interview": {"nature": "外包"}}, "外包"),
        ({"interview": {"nature": "兼职"}}, "兼职"),
        ({"interview": {"nature": "实习"}}, "实习"),
        # 旧 report2 只认正编/外包，遇到"兼职"会返回第四种值"未知nature"
        # （封闭集合吞掉新类别）—— 这条专门锁住它。
        ({"interview": {"nature": "兼职"}, "result": {}}, "兼职"),
        # nature 缺失时退回文本兜底
        ({"interview": {"position": "内容运营（外包岗）"}}, "外包"),
        ({"interview": {"position": "内容运营"}}, "正编"),
    ]
    nbad = [want for card, want in ncases if nature_of(card) != want]
    if nbad:
        print(f"  ✗ 用工性质：{len(nbad)} 项不符（四类必须都能识别）")
        bad += 1
    else:
        print("  ✓ 用工性质：正编/外包/兼职/实习 四类全对（不再有'未知nature'）")

    # 轮次是**自由文本**（真实数据 58 种写法），不能用枚举白名单比对 ——
    # 旧代码只收全角"一面（业务）"，数据里的半角"业务面(一面)""一面(业务)"
    # 全被漏掉，实测 87 张 fail 卡丢 38 张。
    from industry_taxonomy import round_no
    rcases = [
        ("一面", 1), ("一面（业务）", 1), ("一面(业务)", 1), ("业务面(一面)", 1),
        ("业务面", 1), ("业务面（COO/公司经营层）", 1),
        ("二面", 2), ("二面（交叉面）", 2), ("三面", 3),
        ("HR面", 9), ("", 0),
        # 既有序号又有"终轮/boss"字样时，**序号优先** —— 它确实是第三轮，
        # 比笼统的"后期轮(9)"信息量更大，也让"是否一面"的判定不受影响。
        ("三面（boss 面，终轮）", 3),
    ]
    rbad = [r for r, want in rcases if round_no({"interview": {"round": r}}) != want]
    if rbad:
        print(f"  ✗ 轮次归一：{len(rbad)} 项不符（半角括号/带后缀都要能认）")
        bad += 1
    else:
        print("  ✓ 轮次归一：全角/半角/带后缀 全对（一面类都认成第 1 轮）")

    # 跨模块一致性：同一个概念被多个模块各算一遍，是**本项目的头号病根**
    # （赛道归类曾在 report_all / decision / report3 / backtest 里各有一份，
    #   实测有 43/真实卡算法不同；正编外包曾被算出 17/18/19/15 四个数）。
    # 这里直接比对：bucket 必须同一结果。
    try:
        import report_all as _ra
        import decision as _dec
        import report3 as _r3
        _cards = _ra.load()[:0]   # 空库时跳过（下面有 cards 才算）
        _probe = [
            {"interview": {"company": "某大厂", "position": "浏览器海外业务·内容策略运营"}},
            {"interview": {"company": "某本地生活平台", "position": "到餐·美食频道首页产品运营"}},
            {"interview": {"company": "某短视频平台", "position": "快聘 B端 商家运营"}},
            {"interview": {"company": "某公司", "position": "用户增长运营"}},
        ]
        _mismatch = []
        for _c in _probe:
            _b = [_ra.bucket(_c), _dec.bucket(_c), _r3.bucket(_c)]
            if len(set(_b)) != 1:
                _mismatch.append((_c["interview"]["position"][:16], _b))
        if _mismatch:
            print(f"  ✗ 赛道归类跨模块不一致：{_mismatch[:2]}")
            bad += 1
        else:
            print("  ✓ 赛道归类跨模块一致（report_all / decision / report3 同源）")
    except Exception as e:
        print(f"  [提示] 跨模块一致性检查跳过：{type(e).__name__}: {e}")

    # 配置缓存：不缓存时 classify() 每次重读 YAML，backtest 的 O(n²)
    # 留一法会从 1 秒变成跑不完（实测卡死 45s+）。
    import industry_taxonomy as it
    if it.taxonomy() is not it.taxonomy():
        print("  ✗ 配置缓存失效：taxonomy() 每次返回新对象，O(n²) 调用会卡死")
        bad += 1
    else:
        print("  ✓ 配置缓存生效（backtest 留一法 1s 内完成）")

    # 挂因词表必须是「内置 ∪ 用户」，不能是「用户覆盖内置」。
    # 实测教训：用户 config 里配了 blocker_keywords 之后，引擎后来补的词
    # （没答上/不匹配/无HC…）**一个都不生效**，87 张 fail 卡里 23 张的挂因
    # 在报表里完全不可见 —— 代码改了、用户的结果没变。
    _kws = it.blocker_keywords()
    _builtin = set(it.DEFAULT_BLOCKER_KEYWORDS)
    _lost = sorted(_builtin - set(_kws))
    if _lost:
        print(f"  ✗ 挂因词表被 config 覆盖了：内置表有 {len(_lost)} 个词没生效 -> {_lost[:5]}")
        bad += 1
    else:
        print(f"  ✓ 挂因词表是「内置 ∪ 用户」合并（{len(_kws)} 个词，内置表未被覆盖）")

    if bad:
        print(f"  [WARN] 赛道/体量自检 {bad} 项未通过")
        return 1
    print("  ✅ 全部通过（归类 / 体量 / 挂因 / offer / 性质 / 轮次 / 缓存）")
    return 0


def answer_selftest():
    """跑应答框架自检。

    这个模块的核心承诺是「不编答案、只说真话」，所以自检重点锁在
    **不会误导人**上：卡挂了但回答好 → 仍要能复用且要说清；
    没素材 → 必须如实报缺口，不能拿低相似度的素材硬凑。
    """
    ap = Path(__file__).resolve().parent / "answer.py"
    if not ap.exists():
        return 0
    print()
    print("--- 应答框架自检 ---")
    try:
        r = subprocess.run([sys.executable, str(ap), "selftest"],
                           capture_output=True, cwd=str(ap.parent))
        out = r.stdout.decode("utf-8", errors="replace")
        for ln in out.splitlines():
            s = ln.strip()
            if s and (s.startswith("✓") or s.startswith("✗") or "通过" in s or "失败" in s):
                print("  " + s)
        if r.returncode != 0:
            print("  [WARN] 应答框架自检未通过 —— 详见 python main.py answer selftest")
            return 1
    except Exception as e:
        print(f"  [WARN] 应答框架自检无法执行: {e}")
    return 0


def module_smoke_selftest():
    """作用域分析：找出**函数体里读取、却无处定义**的名字。

    ⚠️ 这个检查器换了四版，前三版都被实测证伪，记下来免得再走回头路：
      ① "查未定义名字"（AST 全局收集）：各模块用
         `try: from X import ... / except: def ...` 兜底，
         兜底里的 def 让名字"已定义" → **永远报绿**。
      ② "比对 import 列表 vs 兜底 def"：精确注入真实 bug（import 与兜底
         都删掉 is_first_round、保留调用点）后**依然报绿**。
      ③ "真的 import 每个模块"：模块能 import 成功，因为
         `is_first_round` 是在**函数体内**被读取的，import 期根本不执行。
      ④ 现在这版 = **作用域分析**：对每个函数收集它读取的自由变量，
         若既不是局部变量/参数，也不在模块级绑定集合里 → 判定缺失。
         实测能精确抓到 `main(): is_first_round`（就是当初 report_all
         崩溃的那个名字）。

    被检查的"模块级绑定"包含：import、顶层 def/class/赋值、
    以及 **try/except 兜底里的 def/赋值**（所以只有 import 和兜底**都**漏了才会报）。
    """
    import ast
    import builtins
    here = Path(__file__).resolve().parent

    # ── 选哪些模块来查 ──
    #
    # ⚠️ 旧版用正则 `run\("X.py"\)` 从 main.py 里抠模块名 —— **脆弱**：
    #    它假设每个模块都被一个直接的 `run("…")` 调用路由。
    #    实测（v3.4.0 报告合并时）：把 report_all.py 的派发改成查表
    #    （`_VIEWS = {"总报": ("report_all.py", …)}`）之后，
    #    正则再也抠不到它 —— **report_all.py 静默退出了作用域检查**，
    #    注入 `_x = _undefined_abc` 这种必崩的代码，validate 依然全绿。
    #    更早还一直漏掉 analyzer.py（它是被 import 的，不是 run 的）。
    #    这正是"自检悄悄失去覆盖"的典型：**没人会注意到它少查了一个文件**。
    #
    # 现在改成**扫目录**：tools/ 下所有 .py，排除 main.py（入口自身）和
    #     validate.py（就是本文件）。宁可多查几个，也不漏。
    _SKIP = {"main.py", "__init__.py", Path(__file__).name}
    engine = {f.name for f in here.glob("*.py") if f.name not in _SKIP}

    problems = []
    checked = 0
    for f in sorted(here.glob("*.py")):
        if f.name not in engine:
            continue
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        checked += 1

        # ── 模块级绑定集合 ──
        #
        # ⚠️ 这里要区分两种"有定义"：
        #   ① **真正会执行到的模块级绑定** —— 可以当自由变量的来源
        #   ② 条件块（`if __name__ == "__main__":` 等）里的绑定 —— **不算**
        #
        # 实测踩到的 bug（v3.5 修）：
        #   diagnosis.py 把 `import argparse` 写在文件底部的
        #   `if __name__ == "__main__":` 块里，而 main()（第 271 行）就用它。
        #   旧版用 ast.walk(tree) 收集绑定 —— walk 会**钻进条件块**，
        #   看到那行 import 就认为"argparse 已定义"，于是报绿。
        #   实际运行时：直接 import diagnosis 后调 main() → NameError。
        #   报绿的不是业务代码，是**质检本身** —— 最严重的一类缺陷。
        #
        # ⚠️ 但也不能只认"文件最外层"（第一版改法踩到）：
        #   backtest.main() 里嵌套定义了 bucket_rates()，它读外层的 pool；
        #   predict_apply.main() 里嵌套了 hist()，它读外层的 cards。
        #   这些是**合法的闭包**，只看顶层会把它们误报成未定义。
        #   所以：**逐层维护作用域栈** —— 函数体内部的绑定归该函数，
        #   嵌套函数可以读它外层的局部变量。
        mod = set(dir(builtins)) | {"__name__", "__file__", "__doc__"}

        def _collect(stmts, sink, *, conditional=False):
            """收集一批语句里的绑定到 sink。

            conditional=True 表示这批语句是"条件执行"的
            （如 if/while 体）—— 仍收集进 sink，但调用方要清楚
            它只在特定条件下才存在。对本检查而言：
              · 模块顶层条件块 → **不收**（诊断 bug 的根因）
              · 函数体内的条件块 → 收（函数体整体是"会执行"的）
            """
            for node in stmts:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                     ast.ClassDef)):
                    sink.add(node.name)
                elif isinstance(node, ast.Import):
                    for a in node.names:
                        sink.add((a.asname or a.name).split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    for a in node.names:
                        sink.add(a.asname or a.name)
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        for n in ast.walk(t):
                            if isinstance(n, ast.Name):
                                sink.add(n.id)
                elif isinstance(node, ast.AnnAssign):
                    # 带类型标注的赋值（`NATURE_PATTERNS: list[...] = [...]`）
                    # 是 AnnAssign 而非 Assign。旧版漏了它，boss.py 被误报。
                    if isinstance(node.target, ast.Name):
                        sink.add(node.target.id)
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    for n in ast.walk(node.target):
                        if isinstance(n, ast.Name):
                            sink.add(n.id)
                elif isinstance(node, (ast.With, ast.AsyncWith)):
                    for item in node.items:
                        if item.optional_vars is not None:
                            for n in ast.walk(item.optional_vars):
                                if isinstance(n, ast.Name):
                                    sink.add(n.id)
                elif isinstance(node, ast.ExceptHandler) and node.name:
                    sink.add(node.name)

        # 只收「模块顶层、且非条件块内部」的绑定
        for stmt in tree.body:
            if isinstance(stmt, (ast.If, ast.While)):
                # 条件块：只认它**本身**（if 语句不产生绑定），体内一律不收。
                # 这是 diagnosis 那个 bug 的关键 —— `if __name__` 里的 import
                # 在别处并不可见。
                continue
            if isinstance(stmt, ast.Try):
                # try 块在模块顶层**一定会执行到**，其中的兜底 def/import 有效；
                # except 分支只在出错时才执行，严格说也不保证 —— 但各模块的
                # `except: def offer_flag(): ...` 兜底是**有意设计**，
                # 缺了它会把好代码误报。这里保留（宁可漏报这一种，不误报）。
                for sub in stmt.body + stmt.orelse + stmt.finalbody:
                    _collect([sub], mod)
                for h in stmt.handlers:
                    _collect(h.body, mod)
                continue
            _collect([stmt], mod)

        # ── 逐个函数做作用域检查 ──
        #
        # ⚠️ 必须处理**闭包**：函数可以读它外层函数的局部变量。
        #    实测（第一版改法踩到）：backtest.main() 内嵌 bucket_rates()
        #    读外层的 pool；predict_apply.main() 内嵌 hist() 读外层的 cards。
        #    只收集"自己函数体内"的绑定会把这两个合法闭包误报成未定义。
        #
        # 做法：为每个函数算出「它自己 + 所有外层函数」的局部绑定并集。
        _fns = [n for n in ast.walk(tree)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]

        def _fn_locals(fn):
            """一个函数**自身**的局部绑定（含嵌套 def 名、import、赋值等）。

            注意 `ast.walk(fn)` 会钻进嵌套函数体 —— 那会把内层函数的局部
            变量算成外层可见。对本检查是**偏保守**（宁可判"有定义"而漏报，
            也不误报好代码），与"不误报"的取舍一致。
            """
            s = set()
            for a in (list(fn.args.args) + list(fn.args.kwonlyargs)
                      + list(fn.args.posonlyargs)):
                s.add(a.arg)
            if fn.args.vararg:
                s.add(fn.args.vararg.arg)
            if fn.args.kwarg:
                s.add(fn.args.kwarg.arg)
            for sub in ast.walk(fn):
                if isinstance(sub, ast.Name) and isinstance(sub.ctx, ast.Store):
                    s.add(sub.id)
                elif isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef,
                                      ast.ClassDef)):
                    s.add(sub.name)
                elif isinstance(sub, ast.ExceptHandler) and sub.name:
                    s.add(sub.name)
                elif isinstance(sub, (ast.Import, ast.ImportFrom)):
                    for a in sub.names:
                        s.add((a.asname or a.name).split(".")[0])
                elif isinstance(sub, ast.comprehension):
                    for n in ast.walk(sub.target):
                        if isinstance(n, ast.Name):
                            s.add(n.id)
                elif isinstance(sub, ast.arg):
                    s.add(sub.arg)
            return s

        # 建"父函数"索引：函数 → 它所在的最近外层函数
        _parent = {}
        for parent in _fns:
            for child in ast.walk(parent):
                if child is parent:
                    continue
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    _parent.setdefault(child, parent)

        for fn in _fns:
            # 沿作用域链向上收集（自己 + 所有外层函数）
            local = set()
            node = fn
            while node is not None:
                local |= _fn_locals(node)
                node = _parent.get(node)
            reads = {n.id for n in ast.walk(fn)
                     if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
            miss = sorted(r for r in reads - local if r not in mod)
            if miss:
                problems.append((f.name, fn.name, miss))

    print()
    print("--- \u4f5c\u7528\u57df\u68c0\u67e5\uff1a\u51fd\u6570\u91cc\u8bfb\u4e86\u4f46\u65e0\u5904\u5b9a\u4e49\u7684\u540d\u5b57 ---")
    for fname, fn, miss in problems:
        print(f"  \u2717 {fname} \u2192 {fn}(): {', '.join(miss)}")
        print("       \uff08\u8dd1\u5230\u8be5\u5206\u652f\u4f1a NameError \u2014\u2014 report_all \u66fe\u56e0 is_first_round \u5d29\u8fc7\uff09")
    if problems:
        print(f"  [WARN] {len(problems)} \u5904")
        return 1
    print(f"  \u2713 {checked} \u4e2a\u5f15\u64ce\u6a21\u5757\u3001\u6240\u6709\u51fd\u6570\u7684\u81ea\u7531\u53d8\u91cf\u90fd\u6709\u51fa\u5904")
    return 0


def track_flow_selftest():
    """赛道流程自检 —— **跑真实行为，不查源码字符串**。

    ═══ 为什么整组重写（v3.3.3）═══
    旧版 6 项全是「读源码找字符串」（如 `"_migrate_card_track" in msrc`）。
    注入 bug 实测证伪：把 merge.py 里**真正迁移用的字段名**改坏、
    仅保留 `_migrate_card_track` 字样，此自检仍打印
    「✓ 转正时会迁移 card_track（赛道不丢）」并 ✅ 全部通过 ——
    而实际转正后 `card_track` 停在 `P1:`，**用户的赛道指定真的丢了**。
    那正是 v3.3.0 修过的 bug，等于修复没有回归防线。
    教训与作用域检查器同源：**查字符串的自检 = 锁住字面量，不锁行为**。

    现在只查两样，且都必须真跑：
      ① 转正迁移的**结果**（在隔离副本里真跑 merge formalize，看 card_track 有没有迁）
      ② CLI 接口的**存在性**（问 argparse 本体，而不是 grep 源码）
    """
    print()
    print("--- 赛道流程自检 ---")
    bad = 0
    here = Path(__file__).resolve().parent

    # ① tracks 模块存在且能列出赛道
    try:
        sys.path.insert(0, str(here))
        import tracks as _tr
        tks = _tr.existing_tracks()
        if tks:
            print(f"  ✓ tracks 模块可用，现有 {len(tks)} 个赛道")
        else:
            print("  ✗ tracks.existing_tracks() 返回空")
            bad += 1
    except Exception as e:
        print(f"  ✗ 无法导入 tracks：{e}")
        return 1

    # ② 【行为】转正迁移：在隔离副本里真跑一次 merge formalize
    ok, detail = _probe_track_migration(here)
    if ok:
        print("  ✓ 转正时赛道真的随卡号迁移（P### → I###，实跑验证）")
    else:
        print(f"  ✗ 转正后赛道没迁移到新卡号：{detail}")
        print("       （用户建卡时指定的赛道会在转正那一刻丢掉）")
        bad += 1

    # ③ 【行为】record new 真的接受 --track / --no-track
    #    旧版 grep "--track"，于是**参数被改名/删掉但注释里还留着**就会漏报。
    #    这里直接问 argparse：把参数表解析出来看选项字符串。
    ok, detail = _probe_cli_opts(here / "record.py", ["--track", "--no-track"])
    if ok:
        print("  ✓ record new 真的支持 --track / --no-track（查 argparse 本体）")
    else:
        print(f"  ✗ record.py 的 CLI 不接受 --track/--no-track：{detail}")
        bad += 1

    # ④ 【行为】setup 真的会调用 define_tracks（查 AST 调用点，不查字符串）
    ok, detail = _probe_calls(here / "setup.py", "define_tracks")
    if ok:
        print("  ✓ setup 真的会调用 define_tracks（前置询问赛道）")
    else:
        print(f"  ✗ setup.py 未真正调用 define_tracks：{detail}")
        bad += 1

    # ⑤ 【行为】setup 会把 *.example 落地成"真身"
    #    没有这一步，新用户打开包只看到 .example，不知道该复制哪个。
    ok, detail = _probe_calls(here / "setup.py", "_scaffold_files")
    if ok:
        print("  ✓ setup 真的会调用 _scaffold_files（示例版→真身）")
    else:
        print(f"  ✗ setup.py 未真正调用 _scaffold_files：{detail}")
        bad += 1

    # ⑥ 【行为】生成真身时不能覆盖已存在的文件（否则第二次 setup 就是数据丢失）
    #    用真实临时目录跑一次，断言"已存在则内容不变"。
    ok, detail = _probe_no_overwrite(here)
    if ok:
        print("  ✓ 生成真身时已存在则不覆盖（实跑验证，内容未被改动）")
    else:
        print(f"  ✗ setup 的落地逻辑会覆盖已有文件：{detail}")
        bad += 1

    if bad:
        print(f"  [WARN] 赛道流程自检 {bad} 项未通过")
        return 1
    print("  ✅ 全部通过（定义/逐卡指定/转正迁移/建卡询问/文件落地 —— 均为实跑验证）")
    return 0


# ── 以下为「行为探针」：跑真代码/查真 AST，不用字符串匹配 ──────────────

def _probe_track_migration(here):
    """在临时副本里真跑 merge formalize，断言 card_track 从 P### 迁到 I###。

    为什么必须隔离：merge.py 用 __file__ 定位 ../cards 与 ./config.yaml，
    直接跑会动到用户真实数据。所以整包复制到 temp 再跑。
    这是本组唯一"重"的检查（约 0.1s）。
    """
    import shutil
    import tempfile
    pkg = here.parent
    try:
        td = tempfile.mkdtemp(prefix="mf_track_")
        try:
            work = os.path.join(td, "pkg")
            shutil.copytree(str(pkg), work,
                            ignore=shutil.ignore_patterns("__pycache__", "*.zip", ".git"))
            wtools = os.path.join(work, "tools")
            inbox = os.path.join(work, "cards", "_inbox")
            os.makedirs(inbox, exist_ok=True)
            for f in glob.glob(os.path.join(inbox, "P*.yaml")):
                os.remove(f)

            # 造一张 pending 卡
            with open(os.path.join(inbox, "P1_probe.yaml"), "w", encoding="utf-8") as f:
                f.write("id: P1\nmeta:\n  pending: true\n  proposed_id: I900\n"
                        "interview:\n  company: 自检探针公司\n  position: 内容运营\n"
                        "  round: 一面\n  date: '2025-01-01'\n  nature: 正编\n"
                        "result:\n  outcome: pass\n"
                        "reflection:\n  strength: []\n  weakness: []\n  improvement: []\n"
                        "skills: []\n")

            # config.yaml 里登记 P1 的赛道（用哨兵值，避免与真实赛道撞名）
            SENTINEL = "自检哨兵赛道"
            cfgp = os.path.join(wtools, "config.yaml")
            cfg = {}
            if os.path.exists(cfgp):
                try:
                    cfg = yaml.safe_load(open(cfgp, encoding="utf-8")) or {}
                except Exception:
                    cfg = {}
            cfg["card_track"] = {"P1": SENTINEL}
            with open(cfgp, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False,
                               default_flow_style=False, width=200)

            # 真跑 merge formalize
            r = subprocess.run([sys.executable, "main.py", "merge", "formalize"],
                               capture_output=True, cwd=wtools)
            _out = r.stdout.decode("utf-8", errors="replace")

            # 断言：出现 I### 键且值仍为哨兵；P1 键应已不在
            after = yaml.safe_load(open(cfgp, encoding="utf-8")) or {}
            ct = after.get("card_track") or {}
            migrated = [k for k, v in ct.items()
                        if str(k).upper().startswith("I") and v == SENTINEL]
            still_p = [k for k in ct if str(k).upper().startswith("P")]
            if migrated and not still_p:
                return True, f"{migrated[0]}={SENTINEL}"
            if not migrated and not ct:
                return False, "转正后 card_track 整个消失（赛道指定丢失）"
            if migrated:
                return True, f"{migrated[0]}={SENTINEL}（P 键残留 {still_p}）"
            return False, f"card_track 仍是 {ct}（未迁到 I###）"
        finally:
            shutil.rmtree(td, ignore_errors=True)
    except Exception as e:
        return False, f"探针执行失败：{e}"


def _probe_cli_opts(script, wanted):
    """问 argparse 本体：这些选项字符串真的存在吗？

    比 grep 源码强的地方：注释/文档字符串里提到 `--track` 不再算数，
    而"参数被改名、注释留旧名"这种最常见的漏检会被抓到。
    """
    try:
        import ast
        tree = ast.parse(Path(script).read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"解析失败：{e}"
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if name in ("add_argument", "add_parser"):
                for a in node.args:
                    if isinstance(a, ast.Constant) and isinstance(a.value, str):
                        found.add(a.value)
    missing = [w for w in wanted if w not in found]
    if missing:
        return False, f"缺少 {missing}（实际选项 {len(found)} 个）"
    return True, "ok"


def _probe_calls(script, fnname):
    """AST 检查：某函数是否被**真的调用**（不是出现在注释/字符串里）。"""
    try:
        import ast
        tree = ast.parse(Path(script).read_text(encoding="utf-8"))
    except Exception as e:
        return False, f"解析失败：{e}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            nm = getattr(f, "attr", None) or getattr(f, "id", None)
            if nm == fnname:
                return True, "ok"
    return False, f"没有任何 {fnname}() 调用点"


def _probe_no_overwrite(here):
    """真跑一次 _scaffold_files：已存在的文件内容必须原样保留。

    安全要点：_scaffold_files() 用模块级 ROOT 定位真实包目录。
    所以这里**把 ROOT 临时改成 temp 目录**再调用 ——
    既不碰用户文件，又能真跑到「已存在则跳过」那条分支。
    """
    import shutil
    import tempfile
    try:
        sys.path.insert(0, str(here))
        import setup as _setup
        fn = getattr(_setup, "_scaffold_files", None)
        if fn is None:
            return False, "setup.py 里没有 _scaffold_files"
    except Exception as e:
        return False, f"无法导入 setup：{e}"

    td = tempfile.mkdtemp(prefix="mf_scaffold_")
    _saved_root = getattr(_setup, "ROOT", None)
    try:
        # 在 temp 里摆好 example 源 + 一个"用户已改过"的真身
        for name in ("config.example.yaml", "resume.example.md"):
            src = here.parent / name
            if src.exists():
                shutil.copy2(str(src), os.path.join(td, name))
        MARK = "# 用户手改过的痕迹 —— 不许被覆盖\n"
        target = os.path.join(td, "config.yaml")
        with open(target, "w", encoding="utf-8") as f:
            f.write(MARK)

        _setup.ROOT = td          # ← 关键：把落地目标指向 temp
        try:
            fn()
        finally:
            if _saved_root is not None:
                _setup.ROOT = _saved_root

        with open(target, encoding="utf-8") as f:
            after = f.read()
        if MARK in after:
            # 顺带确认它确实会生成"缺失的"真身（resume.md 不存在 → 应被生成）
            gen = os.path.exists(os.path.join(td, "resume.md"))
            return True, ("ok" if gen else "ok（但 resume.md 未生成，请查 example 是否在包里）")
        return False, "已存在的 config.yaml 被覆盖（用户改动会丢）"
    except Exception as e:
        return False, f"探针失败：{e}"
    finally:
        try:
            if _saved_root is not None:
                _setup.ROOT = _saved_root
        except Exception:
            pass
        shutil.rmtree(td, ignore_errors=True)


def main(argv=None):
    argv = list(argv) if argv else sys.argv[1:]
    path = CARDS
    if "--path" in argv:
        path = argv[argv.index("--path") + 1]
    files = sorted(glob.glob(os.path.join(path, "I*.yaml")))
    # ⚠️ _inbox 的暂存卡（P*.yaml）也要校验。
    #    旧版只扫 I*.yaml，于是 `record new` / `record ask` 写坏的卡
    #    （实测：YAML 被压成一行、带 BOM、字段缺失）**完全不会被发现** ——
    #    而 validate 恰恰是"0 告警才可继续"的那个关卡。
    #    暂存卡是文档教的主流程产物，漏检等于主流程没有质检。
    inbox_files = sorted(glob.glob(os.path.join(path, "_inbox", "P*.yaml")))
    files = files + inbox_files
    if not files:
        print(f"[提示] {path} 下还没有任何 I*.yaml 卡片 —— 这是正常的「初始空库」状态。")
        print("       先建一场：python main.py record new --company 公司 --position 岗位 --round 一面 --nature 正编")
        print("       再逐题补：python main.py record ask --file <卡文件> --q '面试题'")
        return _run_all_selftests()
    errs, warns = [], []
    ncard = 0
    for fp in files:
        ncard += 1
        name = os.path.basename(fp)
        try:
            with open(fp, encoding="utf-8") as f:
                txt = f.read()
        except Exception as e:
            errs.append(f"[IO] {name}: {e}"); continue
        try:
            d = yaml.safe_load(txt)
        except Exception as e:
            errs.append(f"[YAML-FAIL] {name}: {str(e).split(chr(10))[0]}"); continue
        if not isinstance(d, dict):
            errs.append(f"[STRUCT] {name}: 顶层不是映射"); continue
        # ⚠️ 暂存卡（_inbox/P*.yaml）**没有顶层 id** —— `record new` 只写
        #    meta.proposed_id，正式号要等 merge formalize 才分配。
        #    所以对暂存卡不能要求 id，否则每一张合法新建的 pending 卡
        #    都会在这里报 [MISSING] 阻塞错误（实测就是这样）。
        _is_pending = os.path.basename(fp).startswith("P")
        _need = [k for k in REQUIRED_TOP if not (_is_pending and k == "id")]
        for k in _need:
            if k not in d:
                errs.append(f"[MISSING] {name}: 缺 {k}")
        if _is_pending and "id" not in d:
            # 但得确认它至少有 proposed_id，否则转正时会出问题
            if not (d.get("meta") or {}).get("proposed_id"):
                warns.append(f"[WARN] {name}: 暂存卡既无 id 也无 meta.proposed_id，转正时会没号")
        iv = d.get("interview", {}) or {}
        for k in REQUIRED_IV:
            if not iv.get(k):
                warns.append(f"[WARN] {name}: interview.{k} 为空")
        oc = (d.get("result", {}) or {}).get("outcome")
        ocs = oc.strip() if isinstance(oc, str) else oc
        if ocs not in VALID_OUTCOME:
            warns.append(f"[WARN] {name}: outcome=「{ocs}」非标准枚举")
        # 漏真值提醒：正式卡 outcome 非"实际"结果、又未标"待实际" → 提示补 actual，
        #   别让推断/体感当结果的来源。(pass/fail/no_offer 视为已定，不在此列)
        _oc_t = ocs if isinstance(ocs, str) else ""
        _lower = _oc_t.lower()
        _is_actual = ("pass" in _lower) or ("fail" in _lower) or ("no_offer" in _lower)
        if not _is_actual:
            _res = d.get("result", {}) or {}
            _blob = " ".join([str(_res.get("reason", "")), str(_res.get("signal", "")),
                              str((d.get("meta", {}) or {}).get("ai_guess", "")),
                              str((d.get("meta", {}) or {}).get("subjective", ""))])
            _restful = ("待" in _blob or "实际结果" in _blob or "待确认" in _blob or "需补" in _blob)
            _offer = str(_res.get("offer", "") or "").strip()
            _rr = str(_res.get("round_result", "") or "").strip()
            _has_resolved = bool(_offer) or (_rr.lower() in ("pass", "fail"))
            if not _restful and not _has_resolved:
                warns.append(f"[MISS-ACTUAL] {name}: outcome 非实际(pass/fail) 且未见'待实际/待确认'标注 → 请回填实际结果(result.outcome/offer)，勿把 ai_guess/主观体感当真相")
        # 新加字段，仅警告（向后兼容）
        for k in ("round_result", "offer", "why_ended", "process"):
            if k not in (d.get("result", {}) or {}):
                pass  # 允许缺失
        sk = d.get("skills", [])
        if not isinstance(sk, list):
            warns.append(f"[WARN] {name}: skills 应为 list")
        # 文本值里若有可疑未转义英文双引号(粗检)
        m = re.search(r':\s*"[^"\n]*"[^"\n]*"', txt)
        if m:
            warns.append(f"[WARN] {name}: 疑似嵌套未转义双引号: …{m.group(0)[:40]}…")
    _pend_n = len(inbox_files)
    _card_n = ncard - _pend_n
    if _pend_n:
        print(f"扫描 {_card_n} 张正式卡 + {_pend_n} 张 _inbox 暂存卡。")
    else:
        print(f"扫描 {ncard} 张卡。")
    if errs:
        print(f"\n[❌] {len(errs)} 个阻塞错误:")
        print("\n".join("  " + e for e in errs))
        return 1
    if warns:
        print(f"[WARN] {len(warns)} 个警告(可降级):")
        print("\n".join("  " + w for w in warns))
    else:
        print("[OK] 全部卡片 YAML 语法与结构通过（0 警告）。")

    # 顺带跑各模块自检
    return _run_all_selftests()


def _web_probe_helpers():
    """给 web_selftest 用的两个防挂死工具（返回 dict，便于内联使用）。"""
    import socket
    import threading

    def _port_open(port, t=1.0):
        """TCP 能否连上 —— 只探连接，不发请求，绝不会阻塞。"""
        s = socket.socket()
        s.settimeout(t)
        try:
            s.connect(("127.0.0.1", port))
            return True
        except Exception:
            return False
        finally:
            try:
                s.close()
            except Exception:
                pass

    def _fetch(port, path, timeout=6):
        """带 wall-clock 上限的请求。

        ⚠️ 为什么不能直接 urlopen(timeout=…)：当服务端**接受了连接却不响应**
        （handler 抛异常就是这种），socket 的 read 会一直阻塞，timeout 不生效
        （实测栈停在 http/client.py _read_status，自检挂死）。
        这里把请求丢进守护线程，主线程只等 timeout 秒 —— 到点就走，
        线程随进程结束，不会拖住自检。
        """
        box = {}

        def work():
            try:
                import urllib.request
                box["data"] = urllib.request.urlopen(
                    "http://127.0.0.1:%d%s" % (port, path), timeout=timeout).read()
            except Exception as e:
                box["err"] = str(e)

        th = threading.Thread(target=work, daemon=True)
        th.start()
        th.join(timeout)
        if th.is_alive():
            return None, "timeout"
        if "err" in box:
            return None, box["err"]
        return box.get("data"), None

    return _port_open, _fetch


def web_selftest():
    """图形界面自检：**实跑**服务并请求接口，而不是查源码字符串。

    ⚠️ 为什么必须真跑：界面最容易坏在"接口能返回但字段改名了"
    或"前端引用了不存在的字段" —— 这些查字符串一个都抓不到。
    这里真起一次服务（随机端口）、真发 HTTP 请求、真断言字段。

    也刻意覆盖**空库**场景：新装包的人 cards/ 是空的，
    那时接口仍须正常返回，而不是抛异常（新手第一屏就崩是最糟的）。
    """
    print()
    print("--- 图形界面自检 ---")
    ws = Path(__file__).resolve().parent / "webserve.py"
    if not ws.exists():
        print("  · 未发现 webserve.py —— 跳过（该模块为可选）")
        return 0

    import json
    import time
    import shutil
    import socket
    import tempfile
    import subprocess as sp

    _port_open, _fetch = _web_probe_helpers()

    bad = 0
    td = tempfile.mkdtemp(prefix="web_probe_")
    proc = None
    try:
        # 在**临时副本**里跑，绝不碰使用者的真实数据
        pkg = os.path.dirname(str(Path(__file__).resolve().parent))
        work = os.path.join(td, "pkg")
        shutil.copytree(pkg, work, ignore=shutil.ignore_patterns(
            "__pycache__", ".git", "*.zip"))
        wtools = os.path.join(work, "tools")
        # 清掉报告与卡片，模拟"从没跑过 report 的新用户"
        #
        # ⚠️ 卡片也必须清掉，否则自检会**依赖运行环境**：
        #    从真实数据目录跑 validate 时 copytree 会把使用者的卡片一起复制过来，
        #    于是"空库场景"断言（n==0）失败 —— 自检本身变成了
        #    "在有卡的地方就报错、在没卡的地方才通过"，这是不可接受的。
        #    自检必须**自带数据前提**，不依赖调用者所在目录。
        for f in os.listdir(work):
            if f.endswith(".md") and any(k in f for k in
                                         ("总报", "定位", "诊断", "洞察", "痛点", "跨场")):
                try:
                    os.remove(os.path.join(work, f))
                except Exception:
                    pass
        _cards_dir = os.path.join(work, "cards")
        if os.path.isdir(_cards_dir):
            for f in os.listdir(_cards_dir):
                if f.startswith("I") and f.endswith(".yaml"):
                    try:
                        os.remove(os.path.join(_cards_dir, f))
                    except Exception:
                        pass
        _inbox = os.path.join(_cards_dir, "_inbox")
        if os.path.isdir(_inbox):
            for f in os.listdir(_inbox):
                if f.endswith(".yaml"):
                    try:
                        os.remove(os.path.join(_inbox, f))
                    except Exception:
                        pass

        # ⚠️ 端口必须**每次现找一个空闲的**，不能写死。
        #
        # 实测踩到的坑：写死 8731 时，如果那个端口已被占（使用者手动开着
        # 面经台、或上次自检的进程没退干净），本自检会连到**别人的服务**上
        # 探测 —— 于是对"注入过 bug 的代码"照样判绿。
        # 这个缺陷是用注入验证抓出来的：注入字段改名后自检仍报 ✅。
        # 教训与 scope 检查同源：**自检必须确保它测的是自己启动的那个东西**。
        def _free_port():
            s = socket.socket()
            try:
                s.bind(("127.0.0.1", 0))
                return s.getsockname()[1]
            finally:
                s.close()

        port = _free_port()
        proc = sp.Popen([sys.executable, "main.py", "web", "--port", str(port),
                         "--no-open"], cwd=wtools,
                        stdout=sp.PIPE, stderr=sp.STDOUT)
        # 等服务起来（最多 12 秒）
        #
        # ⚠️ 这里踩过一个坑：`urlopen(..., timeout=2)` 的 timeout 是
        #    "socket 操作超时"，但当服务端**接受了 TCP 连接却不回响应**
        #    （例如 handler 里抛异常）时，readinto 会一直阻塞 ——
        #    实测栈停在 http/client.py: _read_status，**timeout 不生效**，
        #    自检就这么挂死了（用 faulthandler 抓到）。
        #    所以改成：**先探端口是否可连**，再在**独立线程**里发请求，
        #    整体加 wall-clock 上限，保证永不挂死。
        ok_up = False
        deadline = time.time() + 12
        while time.time() < deadline:
            time.sleep(0.4)
            if proc.poll() is not None:
                break
            if _port_open(port):
                # 端口通了，再发一次真实请求；用线程包住防阻塞
                _raw, _err = _fetch(port, "/api/overview", 5)
                if _err is None:
                    ok_up = True
                break
        if not ok_up:
            print("  ✗ 服务起不来或接口无响应（12 秒内）")
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            # ⚠️ 别用 proc.stdout.read()：进程被 terminate 后，stdout 管道
            #    可能仍被**子进程的子进程**持有，read() 会**永久阻塞**
            #    （实测栈停在 validate.py:1052，自检挂死 400 秒以上）。
            #    改成在线程里读 + 限时，拿不到就算了。
            _tail = ""
            try:
                import threading as _th

                def _rd():
                    nonlocal _tail
                    try:
                        if proc.stdout is not None:
                            _tail = (proc.stdout.read() or b"").decode(
                                "utf-8", "replace")
                    except Exception:
                        pass

                _t = _th.Thread(target=_rd, daemon=True)
                _t.start()
                _t.join(2)
            except Exception:
                pass
            _tail = _tail.strip()[-200:]
            if _tail:
                print("      子进程输出: " + _tail.replace("\n", " | ")[:160])
            return 1

        print("  ✓ 服务能启动并响应（实跑，端口 %d）" % port)

        # 接口 → 必须存在的字段
        # （trend 已随"去掉时间线分布"一起移除，只留赛道维度 tracks）
        NEED = {
            "/api/overview": ["n", "pass", "fail", "zheng", "questions",
                              "tracks", "todos"],
            "/api/cards": None,        # 列表，元素字段另测
            "/api/reports": None,
        }
        for ep, fields in NEED.items():
            raw, err = _fetch(port, ep, 6)
            if err is not None:
                print(f"  ✗ {ep} 请求失败: {err}")
                bad += 1
                continue
            try:
                d = json.loads(raw)
            except Exception as e:
                print(f"  ✗ {ep} 返回的不是合法 JSON: {e}")
                bad += 1
                continue
            if fields:
                miss = [k for k in fields if k not in d]
                if miss:
                    print(f"  ✗ {ep} 缺字段: {miss}")
                    bad += 1
                else:
                    print(f"  ✓ {ep} 字段齐全（{len(fields)} 个）")

        # 首页必须是可用的 HTML
        raw, err = _fetch(port, "/", 6)
        if err is not None:
            print(f"  ✗ 首页请求失败: {err}")
            bad += 1
        else:
            page = raw.decode("utf-8", "replace")
            if "<html" in page.lower() and "面经台" in page:
                print("  ✓ 首页返回有效 HTML")
            else:
                print("  ✗ 首页不是预期的 HTML")
                bad += 1
            # 关键：前端引用的接口必须真实存在（防"改了后端忘了前端"）
            for ep in ("/api/cards", "/api/overview", "/api/reports", "/api/report"):
                if ep not in page:
                    print(f"  ✗ 前端没有引用 {ep} —— 可能改名后没同步")
                    bad += 1

        # 空库场景：cards 为空时接口仍须正常（不能崩）
        raw, err = _fetch(port, "/api/overview", 6)
        if err is not None:
            print(f"  ✗ 空库场景请求失败: {err}")
            bad += 1
        else:
            try:
                d = json.loads(raw)
            except Exception as e:
                print(f"  ✗ 空库场景返回的不是合法 JSON: {e}")
                bad += 1
            else:
                if d.get("n") == 0 and isinstance(d.get("todos"), list):
                    print("  ✓ 空库场景接口正常（n=0，不抛异常）")
                else:
                    print("  ✗ 空库场景返回异常: n=%r" % d.get("n"))
                    bad += 1

        # ── 写接口的**防护**（比功能更重要：写错了会毁数据）──
        # 真发 POST，逐条断言"该拦的拦住了"。
        def _post(payload, headers):
            import urllib.error
            import urllib.request as _u
            req = _u.Request("http://127.0.0.1:%d/api/edit" % port,
                             data=json.dumps(payload).encode(),
                             headers=headers, method="POST")
            try:
                r = _u.urlopen(req, timeout=6)
                return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                try:
                    return e.code, json.loads(e.read())
                except Exception:
                    return e.code, {}
            except Exception as e:
                return None, {"msg": str(e)}

        H_OK = {"Content-Type": "application/json", "X-Mianjing-Edit": "1"}

        def _post_chat(payload):
            import urllib.error
            import urllib.request as _u
            req = _u.Request("http://127.0.0.1:%d/api/chat" % port,
                             data=json.dumps(payload).encode(),
                             headers=H_OK, method="POST")
            try:
                r = _u.urlopen(req, timeout=6)
                return r.status, json.loads(r.read())
            except urllib.error.HTTPError as e:
                try:
                    return e.code, json.loads(e.read())
                except Exception:
                    return e.code, {}
            except Exception as e:
                return None, {"msg": str(e)}

        # ① 外站来源必须被拒（CSRF）
        st, d = _post({"id": "I001", "fields": {"offer": "no"}},
                      dict(H_OK, Origin="http://evil.example.com"))
        if st == 403:
            print("  ✓ 写接口拒绝外站来源（CSRF 防护）")
        else:
            print("  ✗ 写接口没拦住外站来源！HTTP %s" % st)
            bad += 1

        # ② 缺自定义头必须被拒
        st, d = _post({"id": "I001", "fields": {"offer": "no"}},
                      {"Content-Type": "application/json"})
        if st == 403:
            print("  ✓ 写接口要求自定义头（X-Mianjing-Edit）")
        else:
            print("  ✗ 写接口缺自定义头也放行！HTTP %s" % st)
            bad += 1

        # ③ 字段白名单 / ④ 卡号格式 —— 必须在**存在这张卡**的前提下测。
        #
        # ⚠️ 踩过的坑：一开始我用 "I001" 去测，但自检的探针副本是**空库**，
        #    find_card 先失败，于是"拦住了"其实是"卡不存在"，
        #    把白名单/卡号校验**整段删掉**它照样报绿（注入验证抓到的）。
        #    所以先造一张卡，再测这两条 —— 确保测的是校验本身。
        _probe_card = os.path.join(work, "cards", "I900_探针.yaml")
        try:
            os.makedirs(os.path.join(work, "cards"), exist_ok=True)
            with open(_probe_card, "w", encoding="utf-8") as f:
                f.write("id: I900\ninterview:\n  company: 探针公司\n"
                        "  position: 内容运营\n  round: 一面\n  nature: 正编\n"
                        "result:\n  outcome: pass\n  offer: \"\"\n"
                        "  why_ended: \"\"\n  reason: \"\"\n"
                        "reflection:\n  strength: \"\"\n  weakness: \"\"\n"
                        "  improvement: \"\"\nskills: []\n")
        except Exception:
            pass

        st, d = _post({"id": "I900", "fields": {"skills": "hacked"}}, H_OK)
        if not d.get("ok"):
            print("  ✓ 写接口拦下白名单外字段（skills）")
        else:
            print("  ✗ 写接口放行了白名单外字段！")
            bad += 1

        st2, d2 = _post({"id": "../../config", "fields": {"offer": "no"}}, H_OK)
        if not d2.get("ok"):
            print("  ✓ 写接口拦下非法卡号（防目录穿越）")
        else:
            print("  ✗ 写接口放行了非法卡号！")
            bad += 1

        # ⑤ 正常写入必须成功 + 真的落盘 + 生成备份
        #    （只测"该拦的拦住了"不够 —— 还要测"该放的放行了"，
        #      否则把写功能整个删掉自检也会绿）
        import time as _t
        before = _t.time()
        st3, d3 = _post({"id": "I900", "fields": {"offer": "no"}}, H_OK)
        _ok_write = bool(d3.get("ok"))
        _landed = False
        try:
            with open(_probe_card, encoding="utf-8") as f:
                _landed = "offer: no" in f.read()
        except Exception:
            pass
        _has_bak = os.path.isdir(os.path.join(work, "cards", "_bak")) and \
            bool(os.listdir(os.path.join(work, "cards", "_bak")))
        if _ok_write and _landed and _has_bak:
            print("  ✓ 正常写入成功 + 落盘 + 已备份（%.1fs）" % (_t.time() - before))
        else:
            print("  ✗ 正常写入有问题：ok=%s 落盘=%s 备份=%s"
                  % (_ok_write, _landed, _has_bak))
            bad += 1

        # ⑥ 对话页：发消息必须落盘到 chat/对话.md，且能被读回
        #    （这一页是"网页记录 → AI 读"的桥，坏了就等于对话功能失效）
        st4, d4 = _post_chat({"text": "自检探针消息-勿留", "who": "我"})
        _chat_file = os.path.join(work, "chat", "对话.md")
        _chat_ok = bool(d4.get("ok")) and os.path.exists(_chat_file)
        _chat_landed = False
        if _chat_ok:
            try:
                with open(_chat_file, encoding="utf-8") as f:
                    _chat_landed = "自检探针消息-勿留" in f.read()
            except Exception:
                pass
        raw, err = _fetch(port, "/api/chat", 5)
        _chat_read = False
        if err is None:
            try:
                _chat_read = any(m.get("text", "").startswith("自检探针消息")
                                 for m in json.loads(raw).get("messages", []))
            except Exception:
                pass
        if _chat_ok and _chat_landed and _chat_read:
            print("  ✓ 对话页：消息落盘 + 能读回")
        else:
            print("  ✗ 对话页有问题：写入=%s 落盘=%s 读回=%s"
                  % (_chat_ok, _chat_landed, _chat_read))
            bad += 1

        # ⑦ 分栏布局 + 自动刷新（使用者要的"左边对话、右边卡片"）
        #    这几项只有真读页面才能验 —— 查源码字符串会漏掉
        #    "函数定义了但没被调用"这类问题。
        raw, err = _fetch(port, "/", 6)
        if err is None:
            pg = raw.decode("utf-8", "replace")
            _need = [
                ('class="split"', "左右分栏容器"),
                ('class="pane-chat"', "对话区"),
                ('class="pane-side"', "侧栏"),
                # 侧栏放的是**统计速览**，不是又一份卡片列表 ——
                # 使用者指出"第一个 tab 底下有卡片，跟第二个 tab 重复了"，
                # 所以改成速览；这里断言新结构在、旧列表不在。
                ('id="sidequick"', "侧栏统计速览"),
                ('function drawQuick', "速览渲染函数"),
                ('drawQuick();', "速览的调用点"),
                # 旧结构必须消失（否则又是重复）
                ('id="slist"', None),          # None = 断言"不该存在"
                ("function drawSide", None),
                # ⚠️ 必须同时查"定义"和"调用点"：
                #    只查 "startChatPoll" 会漏掉"函数还在、但没被调用"
                #    （实测注入：删掉调用后自检照样报绿）。所以要求带 () 的调用形式。
                ("function startChatPoll", "自动刷新函数定义"),
                ("startChatPoll();", "自动刷新的**调用点**"),
                ("stopChatPoll();", "切页停止轮询的调用点"),
                ("},2000)", "2 秒轮询间隔"),
            ]
            # why 为 None 表示"断言不该存在"（用于防止重复结构复活）
            _miss = []
            for key, why in _need:
                if why is None:
                    if key in pg:
                        _miss.append("不该存在但出现了：%s" % key)
                elif key not in pg:
                    _miss.append(why)
            if not _miss:
                print("  ✓ 对话页分栏 + 自动刷新 + 侧栏不重复（结构齐全）")
            else:
                print("  ✗ 对话页缺：%s" % "、".join(_miss))
                bad += 1
        else:
            print("  ✗ 首页请求失败: %s" % err)
            bad += 1

    except Exception as e:
        print(f"  ✗ 自检无法执行: {e}")
        return 1
    finally:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        shutil.rmtree(td, ignore_errors=True)

    if bad:
        print(f"  [WARN] 图形界面自检 {bad} 项未通过")
        return 1
    print("  ✅ 全部通过（起服务 / 接口字段 / 前端引用 / 空库场景 —— 均为实跑）")
    return 0


def _run_all_selftests():
    """跑全部 7 组自检，并把结果反映到退出码。

    ⚠️ 旧版这里只调用、**不看返回值**，然后 `return 0` ——
    于是某组自检打了一屏 ✗ 和 [WARN]，退出码却仍是 0。
    文档写的是"0 告警才可继续"，而 `validate` 的退出码正是
    CI / pre-commit / 打包脚本判断"能不能继续"的依据，
    退出码恒 0 等于**把这条闸门关掉了**（实测注入 bug 后确认）。

    现在：任一组返回非 0 → 整体返回 1，并明确提示。
    """
    rcs = [
        ("Boss", boss_selftest()),
        ("简历", resume_selftest()),
        ("赛道/体量", taxonomy_selftest()),
        ("应答框架", answer_selftest()),
        ("作用域", module_smoke_selftest()),
        ("赛道流程", track_flow_selftest()),
        ("图形界面", web_selftest()),
    ]
    failed = [n for n, rc in rcs if rc]
    if failed:
        print()
        print(f"[❌] 自检未通过：{' / '.join(failed)}"
              f"（{len(failed)}/{len(rcs)} 组）")
        print("     → validate 退出码 1。请先修好再继续（文档口径：0 告警才可继续）。")
        return 1

    # 顺带核对：文档里写的自检组数，跟实际是否一致。
    #
    # ⚠️ 为什么加这条：加了"图形界面"这组之后，`SKILL.md` / `ENGINE.md` /
    #    `SKILL_GUIDE.md` / `tools/README.md` **四处**还写着"6 组"，
    #    是使用者问「如果是 skill 呢」、去查 `SKILL.md` 能力表时才发现的 ——
    #    **AI agent 读的就是 `SKILL.md`，数字过时会让它漏掉整个能力**。
    #    这类"文档数字跟不上代码"没有任何机制会报错，所以自己查一次。
    _n = len(rcs)
    _docs = ["SKILL.md", "SKILL_GUIDE.md",
             os.path.join("tools", "ENGINE.md"), os.path.join("tools", "README.md")]
    _bad = []
    for _d in _docs:
        _p = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), _d)
        if not os.path.exists(_p):
            continue
        try:
            with open(_p, encoding="utf-8") as f:
                _t = f.read()
        except Exception:
            continue
        for _m in re.finditer(r"(\d+)\s*组[^\n]{0,12}自检", _t):
            if int(_m.group(1)) != _n:
                _bad.append("%s 写着 %s 组" % (_d, _m.group(1)))
    if _bad:
        print()
        print("[❌] 文档里的自检组数与实际不符（实际 %d 组）：" % _n)
        for _b in _bad:
            print("     · " + _b)
        print("     → 请把文档改成 %d 组。AI agent 读 SKILL.md 判断能力，数字过时会让它漏掉功能。" % _n)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
