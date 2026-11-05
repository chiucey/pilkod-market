# -*- coding: utf-8 -*-
"""打包脚本：按 .gitignore 规则排除，避免把运行产物打进分发包。

═══ 为什么需要它（真实事故）═══
v3.5.0 第一次打包时漏进了 `求职诊断报告.md` —— 那是我在模板目录里
跑测试时生成的产物。内容恰好是空的（0 场面经），但**性质是错的**：
报告类文件会包含使用者的真实面试数据，一旦混入分发包就是数据泄露。

根因：旧打包命令（robocopy + 手写 /XD /XF）**不读 .gitignore**，
只排除了 .git/__pycache__/.pyc/.zip。而 .gitignore 里恰恰挡着
`求职总报.md` / `求职诊断*.md` / `cards/` / `config.yaml` 等一切个人产物。

现在：**以 .gitignore 为准**排除，并额外做一次"产物特征"兜底扫描。
用法（⚠️ 本文件在 `scripts/`，不是 `tools/`）::

    python scripts/pack.py <输出zip路径>

包内根目录名由下面的 `PKG_DIRNAME` 决定（必须是 kebab-case，
且等于 SKILL.md frontmatter 的 `name`，否则 skill 校验器会 FAIL）。
"""
import os
import re
import sys
import zipfile

PKG = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(PKG)

# ⚠️ 包内根目录名 —— 必须与 SKILL.md frontmatter 的 `name` 完全一致，且是 kebab-case。
#
# 为什么：skill 校验器（validate_skill.py）会把**文件夹名**和 frontmatter `name`
# 对比，规则是
#     · 文件夹名必须匹配 ^[a-z0-9]+(-[a-z0-9]+)*$   → 否则 ERROR（直接 FAIL）
#     · name 必须与文件夹名一致                      → 否则 WARNING
# 实测：本包的工作目录叫 `mianjing_skill_template`（下划线），
# 打出来的 zip 内层也就叫这个 → 校验 **FAIL: 1 error**，装不进标准 skill 流程。
#
# 所以：**工作目录名可以随便叫**（这里仍是 mianjing_skill_template，不必改），
# 但**包内名字必须是 kebab-case 且等于 frontmatter 的 name**。
# 改这个常量时，务必同步 SKILL.md 的 `name:`，否则会退回 WARNING。
PKG_DIRNAME = "interview-kb-method-engine"

# 无条件排除（与 .gitignore 无关的构建垃圾）
ALWAYS_SKIP_DIRS = {".git", "__pycache__", ".vscode", ".idea"}
ALWAYS_SKIP_EXT = {".pyc", ".pyo", ".zip", ".log"}

# 产物特征兜底 —— 即使 .gitignore 被改坏，这些也绝不进包
ARTIFACT_PATTERNS = [
    r"求职总报", r"求职定位", r"求职诊断", r"求职动态洞察", r"痛点优势",
    r"跨场分析", r"pulse", r"_v2\.md$", r"应答框架", r"面试详解",
    r"面试点评", r"JD分析", r"卡片表", r"^诊断",
]

# ⚠️ 显式「再放行」清单：这些被 .gitignore 挡着，但**必须**进包。
#
# 为什么需要：.gitignore 里 `cards/` 是整目录忽略（对 git 正确 ——
# 卡片是个人数据）。但**分发包需要空脚手架**，否则新用户打开
# cards/ 是空的、不知道卡长什么样，`merge formalize` 也无模板可依。
# 实测：第一版包脚本因此把这两个文件排除了（打包后自检才发现）。
REINCLUDE = {
    "cards/_template.yaml",
    "cards/_inbox/.gitkeep",
}

# ⚠️ 整文件排除：CHANGELOG 记录了整个开发过程，含真实公司名/卡号/使用者原话
#    （实测扫描出 143 处个人数据）。对外分发必须整份去掉。
#    使用者已确认："CHANGELOG 整个不放进包"。
EXCLUDE_FILES = {"CHANGELOG.md"}

# ⚠️ 整目录排除：装的是使用者自己的数据，绝不能进分发包。
#    chat/ = 网页「对话」页写的记录（含原话与求职细节），与 cards/ 同级敏感。
#
#    注意 cards/ **不在**这里：分发包需要那份空脚手架
#    （_template.yaml + _inbox/.gitkeep），已由 REINCLUDE 放行；
#    真实卡片（I*.yaml）与 _bak/ 由 .gitignore + ARTIFACT 规则挡掉。
EXCLUDE_DIRS = {"chat"}


def load_gitignore(root):
    """把 .gitignore 读成一组正则（支持常见的简单语法）。"""
    pats = []
    gi = os.path.join(root, ".gitignore")
    if not os.path.exists(gi):
        return pats
    with open(gi, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            neg = line.startswith("!")
            if neg:
                line = line[1:]
            # 转成正则
            r = re.escape(line)
            r = r.replace(r"\*", ".*").replace(r"\?", ".")
            if line.endswith("/"):
                r = r.rstrip("/") + r"(/.*)?$"
            else:
                r = r + r"$"
            pats.append((re.compile("^" + r), neg))
    return pats


def is_ignored(rel, name, pats):
    """rel 是相对包根的路径（用 / 分隔）。"""
    ignored = False
    for rx, neg in pats:
        if rx.search(rel) or rx.search(name):
            ignored = not neg
    return ignored


def is_artifact(name):
    return any(re.search(p, name) for p in ARTIFACT_PATTERNS)


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/pack.py <输出zip路径>   # 注意是 scripts/，不是 tools/")
        return 2
    out = os.path.abspath(sys.argv[1])
    pats = load_gitignore(ROOT)

    added, skipped = [], []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames
                           if d not in ALWAYS_SKIP_DIRS
                           and d not in EXCLUDE_DIRS
                           and not d.startswith("_zip")]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, ROOT).replace("\\", "/")
                ext = os.path.splitext(fn)[1].lower()

                if ext in ALWAYS_SKIP_EXT:
                    skipped.append((rel, "扩展名")); continue
                if fn in EXCLUDE_FILES:
                    skipped.append((rel, "整文件排除")); continue
                # 显式放行优先于 .gitignore
                if rel in REINCLUDE:
                    arc = PKG_DIRNAME + "/" + rel
                    z.write(full, arc)
                    added.append(rel)
                    continue
                if is_ignored(rel, fn, pats):
                    skipped.append((rel, ".gitignore")); continue
                if is_artifact(fn):
                    skipped.append((rel, "产物特征")); continue

                arc = PKG_DIRNAME + "/" + rel
                z.write(full, arc)
                added.append(rel)

    print("已打包 %d 个文件 -> %s" % (len(added), out))
    print("排除 %d 个：" % len(skipped))
    for rel, why in skipped:
        print("   [%s] %s" % (why, rel))

    # 自检：包里绝不能有个人数据 / 产物
    bad = [a for a in added if is_artifact(os.path.basename(a))
           or a.startswith("cards/I") or a.startswith("cards/_bak")
           or os.path.basename(a) in ("config.yaml", "resume.md", "profile.yaml")]
    if bad:
        print("\n[❌] 打包后自检发现不该进包的文件：")
        for b in bad:
            print("   " + b)
        return 1
    print("\n[OK] 打包自检通过：无产物、无真实卡、无个人配置。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
