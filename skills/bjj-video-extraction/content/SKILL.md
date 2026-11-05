---
name: bjj-video-extraction
description: 柔术/ grappling 教学视频深度提炼——从 B 站/YouTube 拉取视频，ASR 转录音频，抽帧抓动作画面，交叉核对后产出带截图的 Markdown + 单文件 HTML 报告。当 Wayne 要求"提炼这集教学视频""把 Danaher 这套课整理出来""视频里讲的什么动作""做成带图的笔记"时使用。产出可点击的 CDN 链接，图片内嵌可离线阅读。
---

# 柔术视频教学提炼

## 核心纪律

1. **画面和口述必须交叉核对。** ASR 单独不可信——它会把 "shrimping" 听成 "shrimming"，会把 "pummeling" 听成 "pummeling"，也会把整段战术讲解漏掉。每一个要写进报告的技术断言，必须有一个对应的时间戳 + 一张抽帧图作为证据。反过来，抽帧图也不能单独下结论——你可能截到的是他示范的起始姿态而非结论姿态。
2. **Danaher 原话逐字引用。** 引用讲师的关键论断时，保留原词（"guard retention" 不是 "defense"，"pummeling" 不是 "foot movement"），不翻译后当原话用。可以中译，但要标 [译]。
3. **不编造动作名。** 如果不确定某个动作的标准英文名，就用讲师自己说的词 + 中文解释，标注"讲师原话/我的描述"。
4. **区分"讲师说的"和"我推断的"。** 报告里战术适配建议（尤其涉及伤病）必须单独成节并明确标注是我的推断，不是讲师教的。

## 已知环境

已验证可用，无需重装：

```
ffmpeg / ffprobe   /usr/bin/ffmpeg  (5.1.9)
yt-dlp              /usr/local/bin/yt-dlp
python3             markdown-it-py 4.0.0, Pygments, python-docx, requests
无 node（不要试 npm install）
```

工作目录默认 `/workspace`（不是 `/tmp`）——`/tmp` 在沙盒里，Wayne 本地看不到，成品必须走上传。

## 工作流

### 第一步：拿到视频源

优先 B 站（Wayne 的主要教学源）。B 站 API 对高播放视频会返回 412 风控，**yt-dlp 直接跑会拿不到页面**。解法是先用 curl 带浏览器 UA 访问首页拿 buvid3 cookie，再带 cookie 调 web 接口。

```bash
# 1) 拿 cookie
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
curl -s -A "$UA" -c /tmp/bili_cookies.txt https://www.bilibili.com/ -o /tmp/bili_home.html

# 2) 查分 P 信息（拿到各 P 的 cid）
curl -s -A "$UA" -b /tmp/bili_cookies.txt \
  "https://api.bilibili.com/x/web-interface/view?bvid=BVxxxx" | python3 -m json.tool

# 3) 拿播放地址
curl -s -A "$UA" -b /tmp/bili_cookies.txt \
  "https://api.bilibili.com/x/player/playurl?bvid=BVxxxx&cid=<CID>&qn=80&fnval=1" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['data']['durl'][0]['url'])"
```

**下载字幕前先确认有没有官方字幕轨**：

```bash
yt-dlp --list-subs "https://www.bilibili.com/video/BVxxxx"
```

Danaher 的 B 站转载通常**没有官方字幕**，那就必须走 ASR。不要假设有字幕。

### 第二步：抽音轨 + ASR 转录

```bash
ffmpeg -i input.mp4 -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k audio.mp3
```

用 `audios_understand`（matrix MCP）或 `listen_audio` 做转录。分片处理避免超长：按 10–15 分钟切，用 ffmpeg 的 `-ss`/`-t`。

**转录要带时间戳**，否则后面截图无法对齐。保留每条发言的起止秒数。

### 第三步：抽帧

分两层，不要一开始就抽几千张（用 `scripts/extract_frames.py`）：

```bash
# 概览层：每 2 分钟一帧，用来定位"这一集讲了哪几块"
python3 scripts/extract_frames.py overview input.mp4 overview/ --interval 120

# 接触印相：一张图看 20 帧，快速目视定位
python3 scripts/extract_frames.py contact input.mp4 sheet/ --interval 30 --tile 5x4

# 关键帧层：按 ASR 时间戳精确抽（自动抽 t-2/t/t+2 三帧）
python3 scripts/extract_frames.py keyframes input.mp4 key/ --times 300,430,520
```

从 contact sheet 里挑出关键时间点，再去抽高质量单帧。这一步省大量时间。

### 第四步：交叉核对

对每个准备写进报告的技术点：
1. 从 ASR 里找到讲师说的位置（时间戳 t）
2. 抽 t 附近的帧（t-2s, t, t+2s）
3. 确认画面里的动作和口述描述一致
4. 不一致 → 扩大抽帧范围再看；仍不一致 → 报告里标注"口述与画面有出入"

### 第五步：写 Markdown 报告

固定结构：

```markdown
# {讲师} — {系列名} {Pn} 提炼

## 一句话判断
## {P1标题} 内容概要
## 逐动作详解
### 动作名（含英文原名）
- 时间戳
- 动作要领
- 讲师原话（逐字，加引号）
- 画面证据（图片引用）
## 我认为最值得记的技术细节
## 速查表（表格）
## 战术适配（标注：我的推断，非讲师所授）
## 制作说明（源视频、字幕状况、提炼方法、局限）
```

规则：
- 讲师原话直接引，不加「他说」这种转述壳
- 速查表用 Markdown 表格，动作多的时候表格比列表好用
- 图片引用写相对路径，第六步会转 data URI
- 明确写出局限：无官方字幕、ASR 可能有误、抽帧只能覆盖讲师重点示范的瞬间

### 第六步：出图 + 上传交付

**图片内嵌成单文件 HTML**——Wayne 在手机上点开就能看，不依赖外部图片链接。

```python
import base64, os, re
from markdown_it import MarkdownIt

md = open("report.md", encoding="utf-8").read()
for f in sorted(os.listdir("imgs")):
    if not f.lower().endswith((".jpg", ".jpeg", ".png")):
        continue
    b64 = base64.b64encode(open(os.path.join("imgs", f), "rb").read()).decode()
    uri = f"data:image/jpeg;base64,{b64}"
    # 报告里的路径前缀千差万别，按「任意前缀 + 文件名」替换
    md = re.sub(r"\]\([^)]*?" + re.escape(f) + r"\)", f"]({uri})", md)
    md = md.replace(f"]({f})", f"]({uri})")

# 校验没有残留相对路径
left = [x for x in re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md) if not x.startswith("data:")]
assert not left, f"未替换的图片引用: {left}"

body = MarkdownIt("commonmark", {"html": True}).enable("table").render(md)
html = TEMPLATE.format(body=body)
open("report.html","w",encoding="utf-8").write(html)
print("真实字节数:", os.path.getsize("report.html"))
```

**上传用 mcp_matrix_get_upload_url + curl PUT**：

```python
# size_bytes 必须是 os.path.getsize 的真实字节数，不能用 len(str) 估算
size = os.path.getsize("/workspace/report.html")
```

```bash
# put_url 有效期 600s，拿到就立刻 PUT，别拖
curl -s -o /dev/null -w "%{http_code}" -X PUT \
  --data-binary @/workspace/report.html \
  -H "Content-Type: text/html" -H "Content-Length: <真实字节数>" "<put_url>"
```

**上传后必须验证**（这一步不能省）：

```bash
curl -s -o /tmp/v.html -w "%{http_code} %{size_download}" "<cdn_url>"
grep -c 'data:image/jpeg;base64' /tmp/v.html   # 图片数对不对
grep -o '<h1>[^<]*' /tmp/v.html | head -1      # 标题对不对
```

**同时提供 tar.gz 原始包**（Markdown + 独立 JPG），方便 Wayne 后续自己改：

```bash
cd /workspace && tar czf report.tar.gz report_dir/
```

`zip` 命令在此环境不存在，用 tar.gz。

## 附带脚本（已验证可用，直接调）

```
scripts/fetch_bilibili.sh   B 站取流（带 412 风控处理）+ 分P信息 + 字幕探测
scripts/extract_frames.py   抽帧三种模式：overview / contact / keyframes
scripts/build_report.py     Markdown + 图片目录 -> 单文件 HTML（含 --verify 自检）
scripts/check_delivery.py   交付前自检：图片引用、时间戳、引号、推断隔离、局限声明
scripts/selftest.py         技能包完整性自检（装完跑一次）
```

用法示例：

```bash
S=~/.hermes/skills/personal/bjj-video-extraction/scripts

bash $S/fetch_bilibili.sh BV1xx411c7mD /workspace/bjj_src

# 概览层：定位内容块
python3 $S/extract_frames.py overview video.mp4 ov/ --interval 120
# 接触印相：一张图看 20 帧
python3 $S/extract_frames.py contact video.mp4 ct/ --interval 30 --tile 5x4
# 关键帧：按 ASR 时间戳（每个点自动抽 t-2/t/t+2 三帧）
python3 $S/extract_frames.py keyframes video.mp4 key/ --times 300,430,520
# 片段模式：处理慢时用 --start/--dur 限制范围（33s vs 110s）
python3 $S/extract_frames.py contact video.mp4 ct/ --interval 60 --start 600 --dur 600

python3 $S/check_delivery.py report.md imgs_dir
python3 $S/build_report.py report.md imgs_dir report.html --title "标题"
python3 $S/build_report.py x x report.html --verify report.html
```

**`build_report.py` 会打印真实字节数**，把这个数字填进 `get_upload_url` 的 `size_bytes`，否则 OSS 返回 403。

## 常见陷阱

- **412 风控**：B 站 API 拒绝无 cookie 请求。先 curl 首页拿 buvid3。
- **上传 403 有两个原因**：(1) put_url 过期（600s）；(2) `size_bytes` 与实际文件字节数不符——OSS 签名覆盖 Content-Length，不一致直接拒。**用 `os.path.getsize` 而不是 `len(text)`**。
- **图片路径前缀千差万别**：报告里可能是 `p1_final/x.jpg`、`imgs/x.jpg`、`./x.jpg`。写死 `imgsdir/filename` 替换会漏，必须按「任意前缀 + 文件名」正则替换。`build_report.py` 已处理。
- **不要把 base64 手动贴进工具参数**：太大会被截断导致损坏。写成文件，或直接用 Python 处理。
- **`/tmp` 不可见**：成品必须在 `/workspace` 并上传，否则 Wayne 看不到。
- **无 node**：用 markdown-it-py，别试 npm。
- **contact sheet 很慢**：35 分钟 180MB 视频全量 tile 约 110s/张。用 `--start/--dur` 分段。
- **接触印相尺寸**：tile 参数要和帧数匹配，否则末张拼不满留黑边。
- **抽帧要抽多个时间点**：单帧容易截到动作中间态，说服力弱。`keyframes` 模式自动抽 t-2/t/t+2。
- **报告里"我的建议"要隔离**：讲师原话和我对 Wayne 跟腱康复/技术适配的推断混在一起，会让 Wayne 误以为是 Danaher 的原话。
- **`check_delivery.py` 的孤儿图告警是有效的**：P1 首次运行就报出 3 张未被引用的图 + 多个缺时间戳小节，说明这个检查抓得住真问题。

## 打包分发（给别的机器装）

```bash
# 已验证的打包脚本逻辑（用 python zipfile，因为环境里没有 zip 命令）
# 逐文件写 ZipInfo 并设 external_attr 保留执行位
info.external_attr = (os.stat(full).st_mode & 0xFFFF) << 16
```

**坑位**：
- 环境里**没有 `zip` 命令**，用 Python `zipfile` 打。
- Python `zipfile.extractall()` **会丢执行位**（`unzip` 命令则保留）。所以包里的 `install.sh` 必须自己 `chmod +x scripts/*`。
- `install.sh` 放在 `scripts/` 下，`SRC_DIR` 要向上找一级找 `SKILL.md`：
  ```bash
  _here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  if [ -f "$_here/SKILL.md" ]; then SRC_DIR="$_here"
  elif [ -f "$_here/../SKILL.md" ]; then SRC_DIR="$(cd "$_here/.." && pwd)"
  else echo "FAIL: 找不到 SKILL.md"; exit 1; fi
  ```
- 上传前用 `os.path.getsize` 拿真实字节数填 `size_bytes`。
- **验证要闭环**：打包 → 上传 → 从 CDN 下载 → sha256 对比 → 用下载到的包做全新安装 → 跑 selftest → 再用装好的技能跑一遍真实任务。少了最后一步，脚本可能只是「能跑」但「装完不能用」。

**本技能已发布的包**：
- tar.gz: `/workspace/skills_packages/bjj-video-extraction.tar.gz`
- zip: `/workspace/skills_packages/bjj-video-extraction.zip`
- CDN: 见会话记录


## 已知偏好（来自 Wayne 档案）

- 母语中文，报告用中文；讲师原话保留英文原文
- 强烈求真务实、追求本质——报告要给判断，不要平铺直叙的摘要
- INTJ：必须给出「我不同意/我认为这里可以质疑」的部分
- 跟腱断裂术后康复中（2026年6月手术）：任何涉及跳跃、跑动、踝关节极度背屈的动作要标注风险
- 己训练马伽术/拳击/柔术，技术理解深，不需要解释基础术语
- 交付物在手机上看：HTML 要响应式，长段落别太长
- 喜欢表格化的速查

## 边界

- 书籍/长文逐章精读 → deep-reading-analyst
- 视频内容本身不深挖、只要摘要 → 直接用 web 搜索更快
