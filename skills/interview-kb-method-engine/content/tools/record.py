#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
record.py — 建档助手：一场面试可被完整记录（不设 questions 数量上限）。
两种用法（在 tools/ 目录下）：
  1) 新建一场（产生一张暂存卡到 cards/_inbox/，不占正式 I 号，避免覆盖）
     python record.py new --company 某公司 --position 岗位 --round 一面 --nature 正编 [--date 2026-05-01] [--review ""]
  2) 逐题追加（想记多少题都行）
     python record.py ask --file <存到 _inbox 的文件名，如 某公司_一面> --q "面试官问的完整题目" [--theme 主题] [--ans "我的回答/要点"] [--score 4]
  3) 从“口述/转写文本/笔记”一次性塞进一问多行是给 AI 做；本工具默认每题一条，防裁剪。
落 /cards/_inbox 是"待转正"，你看过后再正式归档(I 递增)。

说明：questions 是 list，长度无上限，逐条 --ask 累积即可把一场面试所有题都记下来。
"""
import os, re, sys, glob, argparse
from datetime import date as _date, timedelta as _td
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
try:
    import yaml
except Exception:
    yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
INBOX=os.path.join(BASE,"..","cards","_inbox")

def slug(s): return re.sub(r'[\\/:*?"<>|\s]+','_', s)[:40]

def next_pid():
    os.makedirs(INBOX, exist_ok=True)
    # find max numeric after f in current cards to estimate
    cur_max=0
    for p in glob.glob(os.path.join(BASE,"..","cards","I*.yaml")):
        m=re.search(r'I(\d+)', os.path.basename(p))
        cur_max=max(cur_max, int(m.group(1)) if m else 0)
    # also inbox
    for p in glob.glob(os.path.join(INBOX,"P*.yaml")):
        m=re.search(r'P(\d+)', os.path.basename(p))
        cur_max=max(cur_max, int(m.group(1)) if m else 0)
    return cur_max+1

def gen_card(company, position, round_, nature, date):
    from datetime import date as dt, timedelta as delta
    confirm_by=(dt.today()+delta(days=7)).isoformat()
    pid=next_pid()
    os.makedirs(INBOX, exist_ok=True)
    base=slug(f"{company}_{position or '岗位'}_{round_ or '一面'}")
    path=os.path.join(INBOX, f"P{pid}_{base}.yaml")
    c={
        'meta':{'create_date': date or '', 'review_date':'', 'confirm_by': confirm_by, 'pending':True, 'proposed_id':f'I{pid:03d}'},
        'interview':{'company':company,'position':position or '','level':'','date':date or '','round':round_ or '','interviewer_role':'','channel':'','base':'','nature':nature or ''},
        'context':{},
        'questions':[],
        'result':{'outcome':'unknown','reason':'','signal':''},
        'reflection':{'strength':'','weakness':'','improvement':''},
        'skills':[],
    }
    with open(path,'w',encoding='utf-8') as f: yaml.safe_dump(c,f,allow_unicode=True,sort_keys=False,default_flow_style=False)
    # convenient id only in filename; no top id to avoid collide (pending). print
    print(f"[OK] 已建暂存卡（未占用正式 I 号）{os.path.basename(path)}")
    print(f"     ⏰ 默认提醒你：第 {confirm_by} 前回填真实结果（python main.py remind 可催）。请届时以实际 outcome/offer 为准回填。")
    print("     转正时把它的 meta.proposed_id 改成正式 I###、或移入 cards/。")
    print("     下一步逐题追加：")
    print(f"     python record.py ask --file P{pid}_{base} --q \"…\" [--ans] [--theme 项目复盘] [--score 4]")
    return path

def add_q(fname, question, theme, ans, score):
    """往指定卡片追加一道题。

    --file 支持三种写法（此前只支持第 2 种，路径写全会拼出错误路径）：
      1. 绝对路径            /path/to/cards/_inbox/P1_x.yaml
      2. 纯文件名            P1_x.yaml 或 P1_x   （在 _inbox / cards 下查找）
      3. 相对路径            ../cards/_inbox/P1_x.yaml
    另支持通配符（如 P1_*），匹配唯一时自动采用。
    """
    raw = fname if fname.endswith('.yaml') else fname + ".yaml"

    cands = []
    if os.path.isabs(raw):
        cands.append(raw)
    else:
        # 相对路径：先按调用者给的相对路径解析（相对 cwd 与相对本脚本目录都试）
        cands.append(os.path.abspath(raw))
        cands.append(os.path.normpath(os.path.join(BASE, raw)))
        cands.append(os.path.normpath(os.path.join(os.getcwd(), raw)))
        # 纯文件名 / 通配符：在 _inbox 与 cards 下找
        cands.append(os.path.join(INBOX, os.path.basename(raw)))
        cands.append(os.path.join(os.path.dirname(INBOX), os.path.basename(raw)))

    path = None
    for c in cands:
        if os.path.exists(c):
            path = c
            break
    if path is None:
        # 退化为通配符匹配（对每个候选做 glob）
        for c in cands:
            hits = glob.glob(c)
            if len(hits) == 1:
                path = hits[0]
                break
            if len(hits) > 1:
                print("匹配多个，请用更精确的文件名：" +
                      ", ".join(os.path.basename(h) for h in hits))
                return 1
    if path is None:
        print(f"[ERR] 找不到卡片文件：{fname}")
        print("       --file 可以给：纯文件名（如 P1_某公司_一面）、"
              "相对路径（../cards/_inbox/P1_….yaml）或绝对路径。")
        try:
            avail = [os.path.basename(p) for p in glob.glob(os.path.join(INBOX, "P*.yaml"))]
            if avail:
                print("       _inbox 现有：" + ", ".join(avail))
        except Exception:
            pass
        return 1
    # ⚠️ 拒绝空题目。旧版会照样追加一条 `{'question': ''}` 并返回 0，
    #    而下游（answer.py / report 的题目统计）一律跳过没有 question 的条目，
    #    于是这条记录**写进去了却永远不显示** —— 用户以为记下了，其实没有。
    if not str(question or "").strip():
        print("[ERR] 题目不能为空（--q）。空题目会被下游统计静默忽略，等于没记。")
        return 2

    d=yaml.safe_load(open(path,encoding='utf-8'))
    qs=d.setdefault('questions',[])
    item={'question':question}
    if theme: item['theme']=theme
    if ans is not None: item['how_answered']=ans
    if score is not None:
        try: item['score']=int(score)
        except: pass
    qs.append(item)
    with open(path,'w',encoding='utf-8') as f: yaml.safe_dump(d,f,allow_unicode=True,sort_keys=False,default_flow_style=False)
    print(f"[OK] 已追加第 {len(qs)} 题：{question[:40]}")
    return 0

def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest='cmd')
    p1=sub.add_parser('new'); p1.add_argument('--company',required=True); p1.add_argument('--position'); p1.add_argument('--round'); p1.add_argument('--nature'); p1.add_argument('--date')
    # --track / --no-track：赛道是本工具最依赖业务判断的一环，所以建卡时**主动问**
    # （与 outcome/nature 同级）。不想被问就 --no-track（走词表判断）。
    p1.add_argument('--track', help='这场面试的赛道（给了就不问）')
    p1.add_argument('--no-track', action='store_true', help='不要问赛道，交给词表判')
    p2=sub.add_parser('ask'); p2.add_argument('--file',required=True); p2.add_argument('--q',required=True); p2.add_argument('--theme'); p2.add_argument('--ans'); p2.add_argument('--score')
    # `record fix` —— 一条命令补齐三个真值（remind 会直接给出可复制的用法）
    p3=sub.add_parser('fix', help='补齐三个真值：outcome / why_ended / offer（也可用来改）')
    p3.add_argument('id', help='卡号，如 I007 或 P1')
    p3.add_argument('--outcome', help='pass / fail / no_offer / unknown')
    p3.add_argument('--why-ended', dest='why_ended', help='没推进的真实原因')
    p3.add_argument('--offer', help='got / no / ongoing')
    p3.add_argument('--reason', help='你认为的原因（可写可不写）')
    a=ap.parse_args()
    if a.cmd=='new':
        gen_card(a.company,a.position,a.round,a.nature,a.date)
        # 建完卡再问赛道：这样能拿到刚生成的卡号，直接写进 config.card_track
        if not a.no_track:
            _ask_and_record_track(a.company, a.position, a.track)
        return 0
    if a.cmd=='ask':
        return add_q(a.file,a.q,a.theme,a.ans,a.score)
    if a.cmd=='fix':
        return fix_truths(a.id, a.outcome, a.why_ended, a.offer, a.reason)
    ap.print_help(); return 1


def fix_truths(cid, outcome=None, why_ended=None, offer=None, reason=None):
    """一条命令补齐/修改三个真值 —— 直接改写 result 下的字段。

    为什么单独做：实测使用者的真实卡里 outcome 填了 100%，
    但 offer 只有 28.9%、why_ended 只有 28.2% —— 因为补这两项在过去
    要手改 YAML 或用 `result` 命令（而那只认 outcome/reason/signal）。
    `remind` 现在会列出缺口并给一条可直接复制的本命令。

    复用 build_card 的字段写入（含**写前自动备份**与「未写入」告警）。
    """
    import build_card
    path = build_card.find_card(cid)
    if path is None:
        print(f"[错误] 未找到卡片 {cid}")
        return 1
    pairs = [("outcome", outcome), ("why_ended", why_ended),
             ("offer", offer), ("reason", reason)]
    pairs = [(k, v) for k, v in pairs if v]
    if not pairs:
        print("[错误] 至少给一个：--outcome / --why-ended / --offer / --reason")
        print("       例：python main.py record fix I007 --offer no")
        return 2

    bak = build_card.backup_before_write(path, why="补齐真值")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    applied, missing, changes = [], [], []
    for key, val in pairs:
        old = build_card._get_yaml_field(content, key)
        content, ok = build_card._set_yaml_field(content, key, val)
        if ok:
            applied.append(key)
            if old != val:
                changes.append(f"{key}: 「{old[:32]}」 → 「{val[:32]}」")
        else:
            missing.append(key)
            # 字段不存在就在 result 区块下补一行（比只报错更有用）
            if key in ("outcome", "why_ended", "offer", "reason"):
                content, added = _append_to_result(content, key, val)
                if added:
                    missing.remove(key)
                    applied.append(key + "(新增)")
                    changes.append(f"{key}: （新增）→ 「{val[:32]}」")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    name = os.path.basename(path).split(".")[0]
    if missing:
        print(f"[警告] {name}: 已写入 {', '.join(applied) or '无'}；"
              f"这些没写进去：{', '.join(missing)}")
    else:
        print(f"[OK] 已补齐 {name}: {', '.join(applied)}")
    for c in changes:
        print("       · " + c)
    if bak:
        print(f"     已备份原卡：{os.path.relpath(bak, os.path.dirname(build_card.CARDS_DIR))}")
    return 1 if missing else 0


def _append_to_result(content, key, val):
    """在 `result:` 区块末尾补一行字段（卡里没有这个字段时用）。"""
    import re as _re
    m = _re.search(r"^(result:)[ \t]*$", content, _re.M)
    if not m:
        return content, False
    # 找到 result 区块的结束（下一个顶层键或文件尾）
    rest = content[m.end():]
    nxt = _re.search(r"^\S", rest, _re.M)
    insert_at = m.end() + (nxt.start() if nxt else len(rest))
    line = f"  {key}: {val}\n"
    return content[:insert_at] + line + content[insert_at:], True


def _ask_and_record_track(company, position, given=None):
    """建卡后询问赛道，并写进 config.card_track（用刚生成的卡号）。

    为什么要问：赛道归类靠业务判断，引擎猜不准（实测被用户连续纠正 6 处）。
    它是"这场面试属于哪类"的事实，和"过没过""是不是外包"同级，
    所以应该在建档流程里直接问，而不是事后去改配置。
    """
    import glob as _glob
    import os as _os
    try:
        import tracks as _tracks
    except Exception:
        return
    # 找出刚建的那张卡（_inbox 里最新的 P*.yaml）
    inbox = _os.path.join(BASE, "..", "cards", "_inbox")
    cands = sorted(_glob.glob(_os.path.join(inbox, "P*.yaml")),
                   key=_os.path.getmtime)
    if not cands:
        return
    card_path = cands[-1]
    cid = _os.path.basename(card_path).split("_")[0]

    if given:
        track = given
    else:
        track = _tracks.ask_track_for(company or "", position or "")
    if track:
        _tracks.set_card_track(cid, track)
        print("     ✅ 已记为「%s」赛道（%s）" % (track, cid))
        print("        以后想改：python main.py tracks set %s 新赛道名" % cid)
    else:
        print("     ↳ 未指定赛道，report 时按词表判断")

if __name__=='__main__':
    sys.exit(main())
