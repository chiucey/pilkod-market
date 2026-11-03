#!/usr/bin/env bash
# B 站视频取流（B 站 API 有 412 风控，必须先拿 cookie）
# 用法: ./fetch_bilibili.sh BVxxxxxxxx [输出目录]
set -euo pipefail

BVID="${1:?用法: fetch_bilibili.sh BVxxxxxxxx [输出目录]}"
OUT="${2:-/workspace/bjj_src}"
mkdir -p "$OUT"

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
COOKIES="/tmp/bili_cookies.txt"

echo "[1/4] 获取 cookie..."
if [ ! -s "$COOKIES" ]; then
  curl -s -A "$UA" -c "$COOKIES" https://www.bilibili.com/ -o /tmp/bili_home.html
fi
grep -q buvid3 "$COOKIES" || { echo "FAIL: 未拿到 buvid3 cookie"; exit 1; }

echo "[2/4] 查询分 P..."
curl -s -A "$UA" -b "$COOKIES" \
  "https://api.bilibili.com/x/web-interface/view?bvid=${BVID}" > "$OUT/view.json"

python3 - "$OUT/view.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1]))
if d.get("code")!=0:
    print("FAIL:", d.get("message")); sys.exit(1)
data=d["data"]
print(f"  标题: {data['title']}")
print(f"  时长: {data['duration']}s")
for p in data.get("pages",[]):
    print(f"  P{p['page']}  cid={p['cid']}  {p['part']}  ({p['duration']}s)")
PY

echo "[3/4] 检查官方字幕轨..."
yt-dlp --list-subs "https://www.bilibili.com/video/${BVID}" 2>&1 | grep -E "available|subtitles" || echo "  (无字幕轨，需走 ASR)"

echo "[4/4] 下载各 P..."
python3 - "$OUT/view.json" "$BVID" "$COOKIES" "$UA" <<'PY'
import json,sys,subprocess,urllib.request,urllib.parse,os
view,bvid,cookies,ua=sys.argv[1:5]
d=json.load(open(view))["data"]
outdir=os.path.dirname(view)
for p in d.get("pages",[]):
    cid,pname=p["cid"],f"p{p['page']}"
    q=urllib.parse.urlencode({"bvid":bvid,"cid":cid,"qn":80,"fnval":1})
    req=urllib.request.Request(
        f"https://api.bilibili.com/x/player/playurl?{q}",
        headers={"User-Agent":ua,"Cookie":open(cookies).read().replace("\t"," ").split("\n")[-1] and
                 "; ".join(l.split("\t")[-2]+"="+l.split("\t")[-1] for l in open(cookies).read().split("\n") if l and not l.startswith("#"))})
    try:
        r=json.load(urllib.request.urlopen(req,timeout=30))
        url=r["data"]["durl"][0]["url"]
    except Exception as e:
        print(f"  {pname} 取流失败: {e}"); continue
    fn=f"{outdir}/{pname}.mp4"
    if os.path.exists(fn) and os.path.getsize(fn)>1_000_000:
        print(f"  {pname} 已存在, 跳过"); continue
    print(f"  {pname} 下载中 ({p['part']})...")
    subprocess.run(["curl","-sL","-A",ua,"-o",fn,url],check=True)
    print(f"  {pname} OK {os.path.getsize(fn)//1024//1024}MB")
PY

echo "完成。输出目录: $OUT"
ls -la "$OUT"
