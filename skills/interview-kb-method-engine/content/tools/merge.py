#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# merge.py — 卡片去重 / 冲突标记 / 转正式(把 _inbox pending 正式成 I###)
# 用法:
#   python main.py merge            # scan: 报告(company,date,round 指纹)重复/冲突
#   python main.py merge formalize  # 把 cards/_inbox 的 P### 转正为 cards/I###_….yaml(无冲突才转)
#   python main.py merge --dry      # 只显示不动
import os, re, glob, sys
try:
    import yaml
except Exception:
    yaml=None
sys.stdout.reconfigure(encoding="utf-8",errors="replace") if hasattr(sys.stdout,'reconfigure') else None
BASE=os.path.dirname(os.path.abspath(__file__))
CARDS=os.path.join(BASE,"..","cards")
INBOX=os.path.join(CARDS,"_inbox")

def fp(d):
    iv=d.get("interview") or {}
    return (str(iv.get("company","")).strip(), str(iv.get("date","")).strip(), str(iv.get("round","")).strip(), str(iv.get("position","")).strip()[:12])

def load_cards(folder):
    out=[]
    if not os.path.isdir(folder): return out
    for p in sorted(glob.glob(os.path.join(folder,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        if isinstance(c,dict): out.append((os.path.basename(p), c))
    return out

def max_id(cards):
    m=0
    for name,_ in cards:
        mm=re.search(r'I(\d+)', name); m=max(m, int(mm.group(1)) if mm else 0)
    # also inbox P don't count
    return m

def scan():
    cards=load_cards(CARDS)
    seen={}
    dup=[]
    for name,c in cards:
        key=fp(c)
        if key in seen: dup.append((seen[key], name))
        else: seen[key]=name
    L=[]
    L.append(f"cards 正式卡 {len(cards)} 张。")
    if dup:
        L.append("重复(疑似同场)：")
        for a,b in dup: L.append(f"  {a}  vs  {b}  (同公司+日期+轮次+岗位前12字)")
    else:
        L.append("无重复。")
    # check inbox pending formalize conflicts
    if os.path.isdir(INBOX):
        pend=[]
        for name in sorted(glob.glob(os.path.join(INBOX,"P*.yaml"))): pend.append(os.path.basename(name))
        L.append(f"_inbox 有 {len(pend)} 张 pending 卡待转正。")
    print("\n".join(L))

def formalize(dry=False):
    if not os.path.isdir(INBOX):
        print("无 _inbox。"); return
    cards=load_cards(CARDS); maxi=max_id(cards)
    made=0; skipped_conflict=0; skipped_done=0
    for p in sorted(glob.glob(os.path.join(INBOX,"P*.yaml"))):
        name=os.path.basename(p)
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except Exception: continue
        key=fp(c)  # (company,date,round,pos12)
        # locate existing formal with same fingerprint
        exist=[ (n,cc) for n,cc in cards if fp(cc)==key ]
        if exist:
            print(f"[冲突/已存在] 跳过 {name} → 已匹配 {exist[0][0]}"); skipped_conflict+=1
            continue
        # 只需公司名非空即可转正；日期是可选字段（未填不阻断，仅提示）
        if not key[0]:
            print(f"[跳过·信息不足] {name} 缺公司名，先补 record new 或填 interview.company"); skipped_done+=1; continue
        if not key[1]:
            print(f"  [提示] {name} 未填面试日期(date)，仍可转正；建议补上以便去重更准。")
        maxi+=1
        new_id = f"I{maxi:03d}"
        newname=new_id+"_"+ re.sub(r'[\\/:*?"<>|\s]+','_', str(key[0]))[:40] +".yaml"
        dst=os.path.join(CARDS,newname)
        if dry:
            print(f"[DRY] 会转正 {name} -> {newname}"); made+=1; continue
        # 转正：补写正式 id（并把 pending 标记去掉），保证 validate 能过
        try:
            c["id"] = new_id
            _m = c.get("meta")
            if isinstance(_m, dict):
                _m.pop("pending", None)
                _m.pop("proposed_id", None)
            with open(p, "w", encoding="utf-8") as _f:
                yaml.safe_dump(c, _f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        except Exception as _e:
            print(f"[WARN] {name} 写入 id 失败（仍会转正）：{_e}")
        import shutil; shutil.move(p,dst); cards.append((newname,c)); made+=1
        print(f"[OK] 转正 {name} -> {newname}")
        # ⚠️ 把 config.card_track 里的旧卡号（P###）迁移到新卡号（I###）。
        #
        # 为什么必须做：建卡时 record new 会问赛道并写进 card_track（按当时的 P 号），
        # 而转正后卡号变成 I### —— 不迁移的话，**用户指定的赛道会在转正那一刻丢掉**，
        # 报表退回词表判断。实测确认过这个丢失（P1「策略运营」转正后变回词表判的「内容运营」）。
        # 这与"pending 卡填不了结果"是同一类问题：P/I 两套编号没打通。
        _old_cid = str(c.get("id") or "").strip()
        _old_pid = name.split("_")[0]          # 例如 P1
        _migrate_card_track(_old_pid, new_id)
    print(f"完成：转正 {made}，冲突/跳过 {skipped_conflict+skipped_done}。")


def _migrate_card_track(old_id, new_id):
    """把 config.yaml 里 card_track 的 old_id 键改成 new_id（保留赛道值）。"""
    try:
        cfgp = os.path.join(BASE, "config.yaml")
        if not os.path.exists(cfgp):
            return
        cfg = yaml.safe_load(open(cfgp, encoding="utf-8")) or {}
        ct = cfg.get("card_track") or {}
        old_up = str(old_id).strip().upper()
        if old_up not in ct:
            return
        track = ct.pop(old_up)
        ct[str(new_id).strip().upper()] = track
        cfg["card_track"] = ct
        with open(cfgp, "w", encoding="utf-8") as f:
            f.write("# config.yaml —— 你的个性化配置（由 setup / record / merge 自动维护）\n\n")
            yaml.safe_dump(cfg, f, allow_unicode=True, sort_keys=False,
                           default_flow_style=False, width=200)
        print(f"     ↳ 赛道指定已随卡号迁移：{old_up} -> {new_id}（{track}）")
    except Exception as _e:
        print(f"     [WARN] card_track 迁移失败（赛道指定可能丢）：{_e}")

def main():
    args=sys.argv[1:]
    dry = "--dry" in args
    sub = "formalize" if "formalize" in args else "scan"
    if sub=="scan": scan()
    else: formalize(dry=dry)

if __name__=="__main__":
    main()
