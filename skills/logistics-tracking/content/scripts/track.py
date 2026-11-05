#!/usr/bin/env python3
"""
物流轨迹查询 - 快递100 API
支持所有主流快递，自动识别公司
"""

import sys, json, os, re, time, hashlib, urllib.request, urllib.parse

def get_config():
    path = os.path.join(os.path.dirname(__file__), "apikey.txt")
    if os.path.exists(path):
        lines = [l.strip() for l in open(path) if l.strip() and not l.startswith("#")]
        return (lines[0], lines[1]) if len(lines) >= 2 else (lines[0] if lines else "", "")
    return "", ""

def detect(n):
    n = re.sub(r'[^A-Za-z0-9]', '', n.upper())
    if n.startswith("SF") and len(n) in (12,15,18,20,22): return ("shunfeng","顺丰速运")
    if n.startswith("JDV") or (n.startswith("JD") and len(n)>=10): return ("jd","京东物流")
    if n.startswith("YT"): return ("yto","圆通速递")
    if n.startswith("ZTO") or (len(n)==12 and n.startswith("7")): return ("zto","中通快递")
    if len(n)==13 and n.startswith("1"): return ("yunda","韵达速递")
    if len(n)==12 and n.startswith("3"): return ("shentong","申通快递")
    if n.startswith("JTSD") or (n.startswith("JT") and len(n)>=10): return ("jtexpress","极兔速递")
    if n.startswith("EMS") or (len(n)==13 and n.startswith("E")): return ("ems","中国邮政EMS")
    if n.startswith("YZ") or n.startswith("PB"): return ("youzhengguonei","中国邮政")
    if n.startswith("DB") or n.startswith("DP"): return ("debang","德邦快递")
    if n.startswith("HT"): return ("huitongkuaidi","百世快递")
    if n.startswith("TT"): return ("tiantian","天天快递")
    if n.startswith("ANE"): return ("anneng","安能物流")
    if n.startswith("ZJS"): return ("zhaijisong","宅急送")
    if n.upper().startswith("DHL"): return ("dhl","DHL")
    if n.upper().startswith("FEDEX"): return ("fedex","FedEx")
    if n.upper().startswith("UPS"): return ("ups","UPS")
    return ("","未知快递")

STATE = {"0":"在途","1":"揽收","2":"运输中","3":"派送中","4":"已签收","5":"异常","6":"退件中","7":"退件完成"}
EMOJI = {"已签收":"✅","在途":"🚚","揽收":"📬","运输中":"🚚","派送中":"📦","异常":"⚠️","退件中":"↩️","退件完成":"↩️"}

def call(url):
    req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)","Referer":"https://www.kuaidi100.com/"})
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))

def has_traces(data):
    ts = data.get("data",[]) or []
    if not ts: return False
    if len(ts)==1 and "查无结果" in str(ts[0].get("context","")): return False
    return True

def query(track_num):
    ctype, cname = detect(track_num)
    if not ctype:
        return {"code":404,"error":f"无法识别快递公司：{track_num}","number":track_num}
    customer, api_key = get_config()
    ts = str(int(time.time()*1000))

    # 优先非签名（更稳定，返回真实数据）
    p1 = urllib.parse.urlencode({"type":ctype,"postid":track_num,"temp":"0.5","show":"0","muti":"1","order":"desc"})
    d1 = call(f"https://www.kuaidi100.com/query?{p1}")
    if has_traces(d1):
        traces = [{"time":t.get("ftime",""),"location":t.get("location",""),"message":t.get("context","")} for t in d1.get("data",[]) or []]
        return {"code":200,"number":track_num,"carrier":cname,"status":STATE.get(d1.get("state","0"),d1.get("state","在途")),"traces":traces}

    # 签名兜底（数据可能更完整）
    sig = hashlib.md5(f"{customer}{api_key}{ts}".encode()).hexdigest().upper()
    p2 = urllib.parse.urlencode({"type":ctype,"postid":track_num,"temp":ts,"customer":customer,"sign":sig,"show":"0","muti":"1","order":"desc"})
    d2 = call(f"https://www.kuaidi100.com/query?{p2}")
    if has_traces(d2):
        traces = [{"time":t.get("ftime",""),"location":t.get("location",""),"message":t.get("context","")} for t in d2.get("data",[]) or []]
        return {"code":200,"number":track_num,"carrier":cname,"status":STATE.get(d2.get("state","0"),d2.get("state","在途")),"traces":traces}

    return {"code":500,"error":"查询失败，请稍后重试","number":track_num,"carrier":cname}

def fmt(r):
    if r.get("code")!=200:
        return f"❌ 查询失败\n\n{r.get('error','未知错误')}\n\n单号：{r.get('number','')}\n快递：{r.get('carrier','')}"
    s, e = r.get("status","未知"), EMOJI.get(r.get("status",""),"📋")
    lines = [f"📦 物流查询结果","",f"单号：`{r['number']}`",f"快递：{r['carrier']}",f"状态：{s} {e}","","━━━━━━━━━━━━━━"]
    for t in r.get("traces",[]):
        if t.get("time"): lines.append(f"📍 {t['time']}{'  📍 '+t['location'] if t['location'] else ''}")
        if t.get("message"): lines.append(f"   {t['message']}")
        lines.append("")
    return "\n".join(lines+["━━━━━━━━━━━━━━","🔗 官网查询：https://www.kuaidi100.com"])

if __name__=="__main__":
    for num in sum([[n.strip() for n in re.split(r"[,，\s]+",a) if n.strip()] for a in sys.argv[1:]],[]):
        r = query(num)
        print(f"\n{'='*42}\n  单号: {num}\n{'='*42}")
        print(json.dumps(r,ensure_ascii=False,indent=2))
        print("\n--- 飞书 ---\n"+fmt(r))
