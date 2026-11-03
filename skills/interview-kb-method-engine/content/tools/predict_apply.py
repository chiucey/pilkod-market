#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict_apply.py — “下场决策”模块
给一个目标公司/JD → 判断:投/慎投/别投 + 卡点预警 + 引用你过去通过率好公司/该题材曾 pass 的最高含金问答，方便临场备战。

用法:
  python predict_apply.py --text "公司:某某公司 岗位:内容运营..."
  python predict_apply.py --jd 内容运营
说明: 纯提示+启发式，不构成结论；投不投最终结合职级/薪资/稳定性。
"""
import os, glob, re, sys, argparse
# 保证 UTF-8 终端/管道下中文输出可读
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
try: import yaml
except Exception: yaml=None
BASE=os.path.dirname(os.path.abspath(__file__))
try:
    from strategy import is_cross
except Exception:
    def is_cross(company, position='', note=''): return False
CARDS=os.path.join(BASE,"..","cards")

CONTRACT_WORDS=("外包","兼职","实习")

def load_cards():
    cs=[]
    if yaml is None: return cs
    for p in sorted(glob.glob(os.path.join(CARDS,"I*.yaml"))):
        try: c=yaml.safe_load(open(p,encoding="utf-8"))
        except: continue
        if isinstance(c,dict): c["_id"]=c.get("id"); cs.append(c)
    return cs

def out(c):
    s=str((c.get("result") or {}).get("outcome") or "")
    if "pass" in s.lower(): return "pass"
    if "fail" in s.lower() or "挂" in s: return "fail"
    return "?"

def comp_slug(c):
    try:return str(c.get("interview").get("company","")).split("·")[0]
    except:return "?"

def nature(c):
    blob=" ".join([str(c.get("interview",{}).get("position","")),comp_slug(c),
                   str((c.get("result") or {}).get("reason",""))])
    return "外包" if any(w in blob for w in CONTRACT_WORDS) else "正编"



def best_pass(cards, tokens, exclude_contract=True, topn=5):
    cand=[]
    for c in cards:
        if out(c)!="pass": continue
        if exclude_contract and nature(c)=="外包": continue
        scor=max([q.get("score",0) for q in (c.get("questions") or [])],default=0)
        hay=(comp_slug(c)+c.get("interview",{}).get("position",""))
        rel=sum(1 for t in tokens if t in hay)
        # 题材辅助:从 questions 找与 token 相近的高分回答
        qs=(c.get("questions") or [])
        hot=[q for q in qs if any(t in (q.get("question","")+q.get("how_answered","")) for t in tokens)]
        cand.append((rel,scor,c["_id"],comp_slug(c),(c.get("interview") or {}).get("position",""),hot))
    cand.sort(key=lambda x:(x[0],x[1]),reverse=True)
    return cand[:topn]

# 目标公司历史淘汰弱信号词
def company_weak(cards, comp):
    fs=[c for c in cards if comp_slug(c)==comp and out(c)=="fail"]
    ws=[]
    for c in fs:
        w=(c.get("reflection") or {}).get("weakness","")
        for kw in ["gap","外包","商业化","行业跨界","口径","简历","稳定性","base","职级","技术","AI"]:
            if kw in w: ws.append(kw)
    from collections import Counter
    return dict(Counter(ws))

def verdict(hist_rate, is_cross, match_hit):
    # hist_rate: tuple(pass,fail)
    p,f=hist_rate; tot=p+f
    rate=(p/tot*100) if tot else None
    if is_cross: return "慎投/别投（跨界/降维，历史上通过率低）"
    if rate is None: return "投（数据少，但属匹配赛道，观察卡点）"
    if rate>=60: return "投（高置信：你的主战场）"
    if rate>=40: return "可投（命中匹配赛道，但需处理卡点）"
    return "慎投"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--text"); ap.add_argument("--jd")
    ap.add_argument("--company")
    a=ap.parse_args()
    buf=(a.text or "")+ " " +(a.jd or "")+" "+(a.company or "")
    if not buf.strip():
        print("用法: python predict_apply.py --text '公司:某公司 岗位:内容运营...' 或 --jd 内容运营 --company 某公司"); return
    cards=load_cards()
    # 粗识别公司与其他 token
    comp_candidates=sorted({comp_slug(c) for c in cards},key=len,reverse=True)
    comp=next((x for x in comp_candidates if x and x in buf), "")
    low_buf = buf
    stop = {"公司","岗位","运营","内容","负责人","求职","招聘"}
    tokens = [w for w in re.findall(r'[\u4e00-\u9fffA-Za-z][\u4e00-\u9fffA-Za-z0-9]*', buf)
              if w not in stop and len(w) >= 2]
    # 确保核心方向词也在 tokens
    for extra in ("美食","垂类","社区","创作者","UGC","商业化","用户增长","求职","数码"):
        if extra in buf:
            tokens.append(extra)
    tokens = list(dict.fromkeys(tokens))
    print("="*50); print("【下场决策】JD:", (a.text or a.jd or a.company)[:80]); print("="*50)
    # 行业历史
    def hist(comp):
        sub=[c for c in cards if comp_slug(c)==comp]
        ok=[c for c in sub if out(c)=="pass"]; ng=[c for c in sub if out(c)=="fail"]
        return (len(ok), len(ng), sub)
    if comp:
        p,f,sub=hist(comp)
        print(f"\n目标公司: {comp}  你面过 {len(sub)} 场(正编口径通过 {p}/{p+f})")
        cross = is_cross(comp, "")
        print("判定:", verdict((p,f),cross,False))
        wc=company_weak(cards,comp)
        if wc: print("在该公司的历史卡点:", ", ".join(f"{k}×{v}" for k,v in wc.items()))
        # 曾 pass 的公司问答
    else:
        print("(未能锁定公司，按通用匹配赛道粗判)\n")
    # 命中题材(通用): 用 tokens 找最佳 pass 卡
    hits=best_pass(cards, [t for t in tokens if len(t)>1][:6])
    print("\n同类题材你曾 pass 的高分场（可复用打法/话术）:")
    if hits:
        for rel,sc,id,cp,pos,hot in hits[:4]:
            print(f"\n- [{id}] {cp}·{str(pos)[:36]}   <rel={rel},topQ={sc}>")
            for q in hot[:2]:
                print(f"    Q: {str(q.get('question',''))[:50]}")
                print(f"    A: {str(q.get('how_answered',''))[:90]}...")
    else:
        print("  (该题材过往 pass 样本不足；建议参考你自己先跑 `insights` 找出的最强卡话术)")
    print("\n投前请核实: 职级 / 薪资 / 正编or外包 / gap 与稳定性叙事 / 返聘冲突 ")

if __name__=="__main__":
    main()
