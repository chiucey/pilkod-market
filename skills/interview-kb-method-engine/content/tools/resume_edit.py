#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill v3「简历修改」阶段 — 简历源编辑器（人主辅机：采纳 / 回退 / diff）。

配套 resume_check.py（负责校验）。本脚本负责"用户拍板后动手改"，并保留 baseline 可回退。

三个动作（子命令）:
  set    采纳一次修改：改某条 bullet 的字段，改完打印 diff
  revert 回退到最近一次备份（baseline 始终保留，不会被覆盖）
  diff   显示当前结构化源 vs 最近一次备份的差异（或 vs baseline）

基线策略:
  - 首次对文件执行 set 前，若 <file>.bak 不存在 → 自动创建（这是"原始版 baseline"，此后不再覆盖）。
  - 每次 set 前把当前内容另存为 <file>.last（可多次覆盖，作为"最近一次"回退点）。
  - revert 默认回退到 <file>.last；--baseline 则回退到最原始的 <file>.bak。

路径定位:
  experience[i].bullets[j].action|metric|goal
  experience[i].headline
  请用形如 "bullets[0].metric" 的相对键（前面可带 experience 索引，也可省略=第0块）。

用法:
  python resume_edit.py --file r.yaml set --key bullets[0].metric --value "社群 40 → 5000 人"
  python resume_edit.py --file r.yaml set --exp 0 --key bullets[0].metric --value "..."
  python resume_edit.py --file r.yaml diff
  python resume_edit.py --file r.yaml revert            # 回退到最近一次
  python resume_edit.py --file r.yaml revert --baseline # 回退到最原始基线
"""
import sys, os, copy, shutil

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except Exception:
    print("[ERR] 需要 pyyaml: pip install pyyaml"); sys.exit(2)


def load(fp):
    with open(fp, encoding="utf-8") as f:
        return yaml.safe_load(f.read())


def dump(data):
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)


def write(fp, data):
    with open(fp, "w", encoding="utf-8") as f:
        f.write(dump(data))


def backup_if_missing(fp):
    bak = fp + ".bak"
    if not os.path.exists(bak):
        shutil.copyfile(fp, bak)
        return True
    return False


def snapshot_last(fp):
    shutil.copyfile(fp, fp + ".last")


def re_match_bullets(key):
    import re
    return re.match(r"^bullets\[(\d+)\]\.(\w+)$", key.strip())


def apply_set(data, exp, key, value):
    exps = data.get("experiences")
    if not isinstance(exps, list):
        raise ValueError("顶层缺少 experiences[] 列表")
    exp = int(exp) if exp is not None else 0
    if exp < 0 or exp >= len(exps):
        raise ValueError(f"experience 索引 {exp} 越界（共 {len(exps)} 块）")
    blk = exps[exp]
    if not isinstance(blk, dict):
        raise ValueError(f"experience[{exp}] 不是映射")
    if key == "headline":
        blk["headline"] = value
        return f"experience[{exp}].headline"
    m = re_match_bullets(key)
    if not m:
        raise ValueError(f"不支持的键 {key}（支持 headline 或 bullets[i].action/metric/goal）")
    bi, field = int(m.group(1)), m.group(2)
    bullets = blk.get("bullets")
    if not isinstance(bullets, list) or bi >= len(bullets):
        raise ValueError(f"bullets[{bi}] 不存在")
    if field not in ("action", "metric", "goal"):
        raise ValueError(f"字段 {field} 不支持（action/metric/goal）")
    bullets[bi][field] = value
    return f"experience[{exp}].bullets[{bi}].{field}"


def show_diff(fp, against=".last"):
    ref = fp + against
    if not os.path.exists(ref):
        print(f"[提示] 无参考备份 {ref}；可先 set 一次生成。")
        return
    try:
        old = load(ref)
    except Exception as e:
        print(f"[ERR] 读参考 {ref} 失败: {e}"); return
    try:
        new = load(fp)
    except Exception as e:
        print(f"[ERR] 读 {fp} 失败: {e}"); return
    if old == new:
        print("（当前与参考备份无差异）")
        return
    print(f"diff（{os.path.basename(fp)} vs {os.path.basename(ref)}）:")
    print_diff_dict(old, new)


def print_diff_dict(a, b, prefix=""):
    if isinstance(a, dict) and isinstance(b, dict):
        keys = list(a.keys())
        for k in b.keys():
            if k not in a:
                keys.append(k)
        for k in keys:
            va, vb = a.get(k), b.get(k)
            if va != vb:
                print_diff_dict(va, vb, prefix + str(k) + ".")
    elif isinstance(a, list) and isinstance(b, list):
        for i in range(max(len(a), len(b))):
            va = a[i] if i < len(a) else None
            vb = b[i] if i < len(b) else None
            if va != vb:
                print_diff_dict(va, vb, prefix + f"[{i}].")
    else:
        print(f"  - {prefix.rstrip('.')}")
        print(f"      旧: {a}")
        print(f"      新: {b}")


def main(argv=None):
    argv = list(argv) if argv else sys.argv[1:]
    if "--file" not in argv:
        print(__doc__); return 2
    fp = argv[argv.index("--file") + 1]
    if not os.path.exists(fp):
        print(f"[ERR] 文件不存在: {fp}"); return 2
    rest = [a for a in argv if a != "--file" and a != fp]
    cmd = rest[0] if rest else ""

    if cmd == "set":
        # 解析 --exp / --key / --value
        exp = None
        key = value = None
        i = 1
        while i < len(rest):
            if rest[i] == "--exp" and i + 1 < len(rest):
                exp = rest[i + 1]; i += 2
            elif rest[i] == "--key" and i + 1 < len(rest):
                key = rest[i + 1]; i += 2
            elif rest[i] == "--value" and i + 1 < len(rest):
                value = rest[i + 1]; i += 2
            else:
                i += 1
        if not key or value is None:
            print("set 需 --key <bullets[i].field|headline> --value <值> [--exp 0]")
            return 2
        backup_if_missing(fp)
        snapshot_last(fp)
        try:
            data = load(fp)
            path = apply_set(data, exp, key, value)
            write(fp, data)
        except Exception as e:
            print(f"[ERR] 修改失败（未改动文件）: {e}"); return 1
        print(f"[OK] 已采纳: {path} = {value}")
        show_diff(fp, ".last")
        return 0

    if cmd == "revert":
        baseline = "--baseline" in rest
        ref = fp + (".bak" if baseline else ".last")
        if not os.path.exists(ref):
            print(f"[ERR] 无回退点 {ref}"); return 1
        # 回退：先显示差异，再覆盖
        print(f"回退到 {'基线' if baseline else '最近一次'}（{os.path.basename(ref)}）:")
        show_diff(fp, ".bak" if baseline else ".last")
        shutil.copyfile(ref, fp)
        print(f"[OK] 已回退 {os.path.basename(fp)} 到 {os.path.basename(ref)}")
        return 0

    if cmd == "diff":
        baseline = "--baseline" in rest
        show_diff(fp, ".bak" if baseline else ".last")
        return 0

    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main())
