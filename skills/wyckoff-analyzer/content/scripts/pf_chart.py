#!/usr/bin/env python3
"""点数图生成器 - 支持任意A股股票"""
import subprocess, json, sys

def get_data(symbol):
    code = f"sh{symbol}" if symbol.startswith('6') else f"sz{symbol}"
    r = subprocess.run(['curl','-s','--max-time','8',
        f"http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={code}&scale=240&ma=no&datalen=60"],
        capture_output=True, text=True)
    return json.loads(r.stdout)

def pf_chart(data, box=0.2, rev=3):
    closes = [float(d['close']) for d in data]
    highs  = [float(d['high'])  for d in data]
    lows   = [float(d['low'])   for d in data]
    cur    = closes[-1]
    cur_date = data[-1]['day']
    dir = 'X' if closes[1] > closes[0] else 'O'
    ref = closes[0]; extreme = cur
    cols = []
    for i in range(1, len(data)-1):
        close = closes[i]; high = highs[i]; low = lows[i]
        if dir == 'X':
            if close > extreme: extreme = high
            if close < ref - box * rev:
                cols.append(('X', extreme, ref))
                dir = 'O'; ref = extreme - box; extreme = low
        else:
            if close < extreme: extreme = low
            if close > ref + box * rev:
                cols.append(('O', ref, extreme))
                dir = 'X'; ref = extreme + box; extreme = high
        if len(cols) > 60: break
    return cols, closes, cur, cur_date

def render(cols, closes, cur, cur_date, box=0.2, width=38):
    if not cols: return None
    dcols = cols[-width:] if len(cols)>width else cols
    all_p = [p for t,top,bot in dcols for p in [top,bot]]
    hi = (max(all_p)/box+1)*box; lo = (min(all_p)//box)*box
    n = min(int((hi-lo)/box)+1, 28)
    step = (hi-lo)/max(n-1,1)
    rows = [[' ']*len(dcols) for _ in range(n)]
    for ci,(ct,ctop,cbot) in enumerate(dcols):
        for ri in range(n):
            rp = hi - ri*step
            if rp <= ctop and rp >= cbot: rows[ri][ci] = ct
    lines = []
    lines.append(f"{'═'*len(dcols)} P&F 点数图 {'═'*len(dcols)}")
    for ri in range(n):
        rp = hi - ri*step
        line = ''.join(rows[ri])
        if line.strip(' '):
            lines.append(f"{rp:5.2f} │{line}│")
    if lo <= cur <= hi:
        ri = int((hi-cur)/step)
        if 0<=ri<n:
            line = ''.join(rows[ri])
            lines.append(f"{cur:5.2f} │{line}│ ←当前价")
    lines.append(f"{'─'*len(dcols)} {'─'*len(dcols)}")
    lines.append(f"X=上涨(买方)  O=下跌(卖方)  格=0.2元  反转=3格  现价:{cur:.2f}元  {cur_date}")
    return '\n'.join(lines)

if __name__ == '__main__':
    sym = sys.argv[1] if len(sys.argv)>1 else '002644'
    data = get_data(sym)
    cols,closes,cur,cur_date = pf_chart(data)
    chart = render(cols, closes, cur, cur_date)
    out = f"/tmp/pf_{sym}.txt"
    with open(out,'w') as f:
        f.write(f"[{sym}] P&F点数图\n")
        f.write(f"现价:{cur:.2f}元 ({cur_date})\n")
        f.write(f"X=买方  O=卖方  0.2元/格  3格反转\n")
        f.write(f"{'='*50}\n{chart}\n")
    print(chart)
    print(f"\nSaved: {out}")
