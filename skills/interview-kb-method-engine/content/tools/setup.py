#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setup.py — 首次运行向导。两件事：
  ① 分流：告诉用户"找岗模块（Boss 抓岗位）"的存在，让他选装不装
  ② 建档：生成 profile.yaml，给出下一步命令

用法:
  python main.py setup                 # 交互式（会问你要不要装找岗模块）
  python main.py setup --quick         # 非交互，默认＝只要复盘引擎
  python main.py setup --with-boss     # 非交互，明确要装找岗模块
  python main.py setup --no-boss       # 非交互，明确不要
  python main.py setup --name 张三 --city 北京 --gap '…'
"""
import os
import shutil
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(BASE, "..")
PROFILE = os.path.join(ROOT, "profile.yaml")
CARDS = os.path.join(ROOT, "cards")
BOSS_FLAG = os.path.join(ROOT, ".boss_enabled")   # 用户的选择记录在这


def ask(prompt, default=""):
    """交互式提问。

    ⚠️ 没有 TTY 时（管道、CI、被别的脚本 spawn、stdin 关闭）input() 会抛
    EOFError 并打出裸 traceback。这里兜住，退回默认值并提示用 --quick /
    --name 等参数非交互运行 —— 否则用户只会看到一段看不懂的异常。
    """
    try:
        if default:
            a = input(f"{prompt} [{default}]: ").strip()
            return a if a else default
        return input(f"{prompt}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        print("[提示] 检测不到交互式输入（stdin 已关闭）。已跳过该问题。")
        print("       非交互请用：python main.py setup --quick")
        print("       或直接指定：--name 张三 --city 北京 --gap '…'")
        return default or ""


def ask_yes_no(prompt, default="n"):
    """问一个是非题。认 y/yes/是/1 与 n/no/否/0；认不出就再问一次。"""
    while True:
        a = ask(prompt + "（y/n）", default).strip().lower()
        if a in ("y", "yes", "是", "1", "要", "装"):
            return True
        if a in ("n", "no", "否", "0", "不要", "不装"):
            return False
        print("  ↳ 没看懂，回 y 或 n 就行。")


def boss_deps():
    """探测找岗模块的依赖是否就绪。返回 (node_ok, browser_ok, detail)。"""
    node = shutil.which("node")
    node_ok = False
    node_ver = ""
    if node:
        try:
            import subprocess
            r = subprocess.run([node, "--version"], capture_output=True, timeout=10)
            node_ver = r.stdout.decode("utf-8", "replace").strip()
            # Node 18+ 才有内置 fetch / WebSocket
            maj = int("".join(c for c in node_ver.lstrip("v").split(".")[0] if c.isdigit()) or 0)
            node_ok = maj >= 18
        except Exception:
            node_ok = False

    browser_ok = False
    browser_name = ""
    try:
        sys.path.insert(0, BASE)
        from boss import __file__ as _bf  # noqa: F401  只为确认模块在
        # 直接复用 boss.mjs 的探测逻辑不现实（JS），这里做等价的最小检查
        import os as _os
        cands = [
            (r"C:\Program Files\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe", "Chrome"),
            (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "Edge"),
            (r"C:\Program Files\Microsoft\Edge\Application\msedge.exe", "Edge"),
            ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "Chrome"),
            ("/usr/bin/google-chrome", "Chrome"),
            ("/usr/bin/chromium", "Chromium"),
        ]
        for p, n in cands:
            if _os.path.exists(p):
                browser_ok, browser_name = True, n
                break
        else:
            # 交给 boss.mjs 自己找（它还会查 PATH），这里不武断说"没有"
            if shutil.which("chrome") or shutil.which("chromium") or shutil.which("msedge"):
                browser_ok, browser_name = True, "PATH 中的浏览器"
    except Exception:
        pass

    detail = []
    detail.append(f"Node.js：{'✅ ' + node_ver if node_ok else ('找到 ' + node_ver + '，但需要 18+' if node else '❌ 未安装')}")
    detail.append(f"浏览器：{'✅ ' + browser_name if browser_ok else '❌ 未检测到 Chrome/Edge（也可能在非标准路径，运行时脚本会再找一次）'}")
    return node_ok, browser_ok, detail


def banner():
    print()
    print("=" * 68)
    print("  面试知识库 & 求职策略引擎 —— 首次设置")
    print("=" * 68)


def explain_boss():
    """把找岗模块讲清楚：它能干什么、要什么、不装会缺什么。"""
    print()
    print("─" * 68)
    print("  这个工具包含【两个部分】，第二部分是可选的：")
    print("─" * 68)
    print()
    print("  ① 面试复盘引擎（核心，默认就有）")
    print("     把每场面试记成一张卡 → 自动生成《求职总报》：")
    print("     轮次通过率 / 正编vs外包 / 反复挂的根源 / 该投慎投别投")
    print("     还有：对着 JD 备战、基于你自己真实回答的应答框架")
    print("     依赖：只要 Python + pyyaml")
    print()
    print("  ② 找岗模块（可选）—— 直接从 Boss直聘 抓岗位")
    print("     输入一个关键词（如「内容运营」），自动打开浏览器抓回")
    print("     约 150 条岗位池 + JD 正文，再按你的能力和用工性质分成 A/B/C 级。")
    print("     适合：还没定投哪些、想批量看市场的人。")
    print()
    print("     ⚠️ 它需要额外两样东西（下面会帮你检测）：")
    print("        · Node.js 18+      （抓取脚本是 Node 写的）")
    print("        · Chrome 或 Edge   （要真实浏览器扫码登录 Boss）")
    print()
    print("     登录态只存在你自己电脑上，不会上传任何地方。")
    print("     不装也能用 ①，只是要自己在招聘网站上翻岗位。")
    print()


def _scaffold_files():
    """把 *.example 模板落地成可用的「真身」文件。

    做三件事（已存在的**绝不覆盖** —— 用户可能已经填过内容）：
      config.example.yaml  -> config.yaml      （赛道/体量/主场/挂因词等可配置项）
      resume.example.md    -> resume.md        （简历；用户自己填）
      config.yaml 里顺带写好赛道骨架（若用户刚在向导里定义过）

    返回生成的清单，供调用方打印。
    """
    made = []
    pairs = [
        ("config.example.yaml", "config.yaml"),
        ("resume.example.md", "resume.md"),
    ]
    for src, dst in pairs:
        s = os.path.join(ROOT, src)
        d = os.path.join(ROOT, dst)
        if os.path.exists(d):
            continue
        if not os.path.exists(s):
            continue
        try:
            with open(s, "r", encoding="utf-8") as f:
                content = f.read()
            # 给头部加一行说明，让用户知道这是自动生成的、可以改
            content = (f"# 本文件由 setup 从 {src} 自动生成 —— 放心改，改坏了"
                       f"删掉重跑 setup 即可。\n" + content)
            with open(d, "w", encoding="utf-8") as f:
                f.write(content)
            made.append(dst)
        except Exception as e:
            print(f"  [WARN] 生成 {dst} 失败：{e}")
    return made


def main():
    quick = "--quick" in sys.argv
    force_yes = "--with-boss" in sys.argv
    force_no = "--no-boss" in sys.argv

    def arg(k):
        if f"--{k}" in sys.argv:
            i = sys.argv.index(f"--{k}")
            return sys.argv[i + 1] if i + 1 < len(sys.argv) else ""
        return None

    banner()
    os.makedirs(CARDS, exist_ok=True)

    # ── 第一步：找岗模块要不要装 ──────────────────────────────
    # 依赖探测只做**一次**，结果留给下面复用 —— 否则选了 y 之后会再打印
    # 一遍同样的检测结果，看起来像重复执行（实测踩到）。
    node_ok, browser_ok, dep_detail = boss_deps()
    if force_yes:
        want_boss = True
    elif force_no or quick:
        want_boss = False
    else:
        explain_boss()
        print("  你这台机器的检测结果：")
        for d in dep_detail:
            print("    " + d)
        print()
        if node_ok and browser_ok:
            print("  ✅ 两个依赖都在 —— 装上就能直接用。")
        else:
            print("  ⚠️ 上面标 ❌ 的还没就绪，装完需要先补上才能抓取。")
            print("     （不强求现在装：核心的复盘功能跟它无关）")
        print()
        want_boss = ask_yes_no("  要不要现在启用【找岗模块】？",
                               "y" if (node_ok and browser_ok) else "n")

    # 记录选择（不装也写下来，免得每次问；想改直接删这个文件或重跑 setup）
    try:
        with open(BOSS_FLAG, "w", encoding="utf-8") as f:
            f.write("yes\n" if want_boss else "no\n")
    except Exception:
        pass

    print()
    if want_boss:
        print("  ✅ 已选择【启用找岗模块】。")
        if not (node_ok and browser_ok):
            print("     但依赖还没齐，先补上这两样：")
            for d in dep_detail:
                if "❌" in d:
                    print("       " + d)
            print("     Node.js: https://nodejs.org  （装 LTS 版即可）")
            print("     浏览器 : 装 Chrome 或 Edge 任一个")
            print("     （装完重跑 setup 会自动认出来）")
        print()
        print("     用法示例：")
        print("       node tools/boss.mjs harvest --query 内容运营 --city 北京")
        print("       python main.py boss filter --file boss_jobs.json")
        print("       python main.py bossmerge --files boss_*.json")
        print("     详细见 tools/BOSS.md")
    else:
        print("  ✅ 已选择【只用复盘引擎】。找岗那部分不需要装任何东西。")
        print("     以后想启用：重跑 python main.py setup --with-boss")
        print("     （或直接按 tools/BOSS.md 用，装个 Node 就行）")

    # ── 第二步：赛道定义（**前置询问** —— 与"是否通过/是否外包"同级的基本信息）
    #
    # 为什么必须问：赛道归类靠业务判断，引擎猜不准 ——
    # 实测被使用者连续纠正 6 处。而"你面的是哪类岗"只有本人知道，
    # 所以它应该像 outcome / nature 一样在流程里直接问，而不是藏在配置注释里。
    print()
    if quick:
        print("[--quick] 跳过赛道定义（可稍后跑：python main.py tracks define）")
    else:
        try:
            import tracks as _tracks
            _tracks.define_tracks()
        except Exception as e:
            print("[提示] 赛道定义向导跳过：%s" % e)
            print("       可稍后跑：python main.py tracks define")

    # ── 第三步：profile.yaml ────────────────────────────────
    print()
    profile_path = PROFILE
    if os.path.exists(profile_path):
        print("[已存在 profile.yaml] 直接使用；改口径请自行编辑。")
    else:
        name = arg("name") or ("" if quick else ask("名字(可空)", ""))
        city = arg("city") or ("" if quick else ask("常驻城市", ""))
        gap = arg("gap") or ("" if quick else ask(
            "统一 GAP 说法（一句话，会用于自介/动机，避免每场乱讲）",
            "（按自己情况填：如空窗期在做什么/已稳定可投入）"))
        doc = (
            "# profile.yaml（候选人主档案）——改一次全局生效\n"
            "# 字段见 tools/schema 与 example；此处为 setup 生成初稿，请自行校对行业/每段经历。\n"
            "profile:\n"
            f"  candidate:\n    name: {name or ''}\n    base: {city or ''}\n    edu: ''\n"
            "  timeline: []\n"
            f"  gaps:\n    - when: ''\n      length: ''\n      why: {gap or ''}\n      status: 已稳定可投入\n"
            f"  ready_made:\n    self_intro_short: ''\n    why_look_motive: ''\n    gap_story: {gap or ''}\n"
            "  notes: []\n"
        )
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(doc)
        print(f"[OK] 已生成 {profile_path}")

    # ── 第四步：把其余的"示例版"落地成"真身" ────────────────────
    #
    # ⚠️ 为什么必须自动做这一步（实测发现的问题）：
    #   包里给的是 *.example 模板，而文档从头到尾让用户用 config.yaml /
    #   resume.md / profile.yaml —— 这三个「真身」原本**不自动生成**，
    #   得用户自己猜到"要复制一份改名"。
    #   新用户打开包看到 4 个 .example，无从下手；而引用了这些名字的文档
    #   在包里根本找不到对应文件（实测：文档提到 13 个文件名，4 个找不到）。
    #   「告诉用户做 3 步」永远不如「帮他做掉」—— 所以这里直接生成。
    _made = _scaffold_files()
    if _made:
        print(f"[OK] 已生成 {len(_made)} 个可编辑文件：" + "、".join(_made))
        print("     （都是从对应 .example 复制的空模板，填你自己的内容即可）")

    # ── 第五步：下一步 ──────────────────────────────────────
    print()
    print("─" * 68)
    print("  接下来：把第一场面试记进来")
    print("─" * 68)
    print("  python main.py record new --company X --position Y --round 一面 --nature 正编")
    print("  python main.py record ask --file <上面给的文件名> --q '面试题' "
          "[--ans '…' --theme 项目复盘 --score 4]")
    print("      ↳ 想记多少题就加多少遍；面完记得回填 outcome/why_ended/offer")
    print("  python main.py report      # 生成《求职总报》")
    print()
    print("  想偷懒：把整场面试的逐字稿直接发给 AI，让它按 tools/digest_guide.md 建档。")
    print()
    print("  校验一切正常： python main.py validate")
    print()
    if not want_boss:
        print("  （找岗模块当前未启用；python main.py setup --with-boss 可随时开）")
        print()


if __name__ == '__main__':
    main()
