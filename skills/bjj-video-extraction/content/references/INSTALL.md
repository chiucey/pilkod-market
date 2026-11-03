# 安装说明 — bjj-video-extraction（柔术视频教学提炼）

## 这是什么

一个 Hermes Agent 技能包。用于把 B 站 / YouTube 上的柔术（grappling）教学视频
深度提炼成带动作截图的教学笔记，输出单文件 HTML + Markdown。

包含 5 个已验证可用的脚本：
```
scripts/fetch_bilibili.sh   B站取流（412 风控处理）+ 分P信息 + 字幕轨探测
scripts/extract_frames.py   抽帧三模式：overview / contact / keyframes
scripts/build_report.py     Markdown + 图片目录 → 单文件 HTML（含 --verify 自检）
scripts/check_delivery.py   交付前自检：图片引用/时间戳/引号/推断隔离/局限声明
scripts/selftest.py         技能包完整性自检（装完跑一次）
```

## 安装

### 方式一：一键安装脚本（推荐）

```bash
unzip bjj-video-extraction.zip -d /tmp/
bash /tmp/bjj-video-extraction/install.sh
# 或指定目录：
bash /tmp/bjj-video-extraction/install.sh ~/.hermes/skills/personal
```

脚本会自动：复制技能 → 补上执行权限 → 跑自检 → 覆盖前先备份。
默认装到 `~/.hermes/skills/personal/`。

### 方式二：手动复制

```bash
unzip bjj-video-extraction.zip -d /tmp/
mkdir -p ~/.hermes/skills/personal
cp -r /tmp/bjj-video-extraction ~/.hermes/skills/personal/
chmod +x ~/.hermes/skills/personal/bjj-video-extraction/scripts/*
```

> 注意：用 Python 的 `zipfile` 解压会丢失执行位（`unzip` 命令则保留）。
> 无论如何装完都执行一次 `chmod +x scripts/*`。

### 方式三：用 Hermes 自带工具

```bash
# 在 Claude Code / Hermes 中：
skill_manage(action='create', name='bjj-video-extraction', ...)
# 或直接把本目录内容贴进去
```

### 分类说明

技能默认归入 `personal` 类。如果你有别的分类习惯，
放到 `~/.hermes/skills/<任意分类>/bjj-video-extraction/` 都能被识别。

## 依赖

```
必须：
  python3           3.8+
  ffmpeg / ffprobe  抽帧、抽音轨
  markdown-it-py    Markdown → HTML 渲染（pip install markdown-it-py）
  requests          HTTP 请求

可选：
  yt-dlp            探测字幕轨
  curl              B站取流
```

安装依赖：
```bash
apt-get install -y ffmpeg
pip3 install markdown-it-py requests
```

**不需要 node**（环境里没有，用 markdown-it-py 替代）。

## 验证安装

```bash
cd ~/.hermes/skills/personal/bjj-video-extraction
python3 scripts/selftest.py
```

期望输出：
```
OK   SKILL.md 存在且有 YAML frontmatter (name + description)
OK   4 个脚本存在
OK   ... Python/bash 语法通过
OK   依赖 markdown-it-py / ffmpeg / ffprobe 可用
PASS — 技能包完整可用
```

## 使用

装好后不需要记脚本名，直接自然语言触发：

> 「提炼一下这集 Danaher 教学视频」
> 「把 P2 做成带图的笔记」
> 「视频里讲的什么动作」

也可以手动调：

```bash
S=~/.hermes/skills/personal/bjj-video-extraction/scripts

bash $S/fetch_bilibili.sh BV1xx411c7mD /workspace/bjj_src

python3 $S/extract_frames.py overview video.mp4 ov/ --interval 120
python3 $S/extract_frames.py contact  video.mp4 ct/ --interval 30 --tile 5x4
python3 $S/extract_frames.py keyframes video.mp4 key/ --times 300,430,520

python3 $S/check_delivery.py report.md imgs_dir
python3 $S/build_report.py  report.md imgs_dir report.html --title "标题"
python3 $S/build_report.py  x x report.html --verify report.html
```

## 关键坑位（速查，详见 SKILL.md）

1. **上传 CDN 返回 403** —— `get_upload_url` 的 `size_bytes` 必须填
   `os.path.getsize()` 的真实字节数，不能用 `len(str)` 估算。
   OSS 签名覆盖 Content-Length，不一致直接拒。
2. **put_url 有效期 600 秒** —— 拿到就立刻 PUT。
3. **B站 412 风控** —— 先 curl 首页拿 buvid3 cookie，再带 cookie 调 API。
4. **成品必须放 `/workspace`** —— `/tmp` 在沙盒里，Wayne 本地看不到，
   需要走上传才能访问。
5. **报告图片路径前缀不固定** —— `build_report.py` 用正则匹配「任意前缀+文件名」，
   不要改成写死路径。
6. **contact sheet 慢** —— 35 分钟 180MB 视频全量约 110s/张，
   用 `--start/--dur` 分段。

## 已知环境前提

本技能假设运行时具备：ffmpeg、ffprobe、python3、markdown-it-py。
若缺少某项，`selftest.py` 会明确报出缺哪个。
