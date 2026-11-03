---
name: tiktok-video-scraper
skill_id: "1711436041753624576"
description: |
  使用yt-dlp工具采集TikTok视频和内容数据。当用户需要以下场景时使用此技能：
  - 下载TikTok视频（单个视频、用户主页、话题标签）
  - 批量采集TikTok创作者内容
  - 提取TikTok视频元数据（播放量、点赞数、评论等）
  - 分析TikTok账号数据或竞品监控
  - 按时间/热度/内容过滤TikTok内容
  - 提取TikTok音乐/原声相关视频
  - 定时抓取TikTok数据用于长期监测
  触发关键词：TikTok下载、TikTok爬虫、TikTok采集、抖音下载、视频抓取、tiktok video download、scrape tiktok、分析TikTok数据、tiktok scraper
---

# TikTok 视频采集工具 (yt-dlp)

yt-dlp 是一款强大的命令行工具，支持从 TikTok（抖音国际版）及[众多网站](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)下载视频和音频。

## 安装配置

```bash
# macOS 系统
brew install yt-dlp ffmpeg

# Windows 系统（使用 winget）
winget install yt-dlp

# Linux 系统（使用 pip）
pip install yt-dlp
# Linux 还需要单独安装 ffmpeg
sudo apt install ffmpeg  # Debian/Ubuntu
sudo dnf install ffmpeg   # Fedora

# 验证安装
yt-dlp --version
```

---

## 核心使用场景

### 场景一：下载单个视频

**适用场景**：用户想要保存某条具体的TikTok视频

```bash
# 基础下载（最高质量）
yt-dlp "https://www.tiktok.com/@用户名/video/1234567890"

# 下载特定格式（推荐用于避免水印）
yt-dlp -f "best" "https://www.tiktok.com/@用户名/video/1234567890"

# 只下载音频（适合音乐类视频）
yt-dlp -x --audio-format mp3 "https://www.tiktok.com/@用户名/video/1234567890"

# 自定义输出文件名
yt-dlp -o "我的视频.%(ext)s" "https://www.tiktok.com/@用户名/video/1234567890"
```

**实战示例**：
```
用户说："帮我下载这个视频 https://www.tiktok.com/@cookwithmika/video/7321567890123"

执行：
yt-dlp "https://www.tiktok.com/@cookwithmika/video/7321567890123"

结果：视频保存为当前目录下的 7321567890123.mp4
```

---

### 场景二：下载整个用户主页

**适用场景**：采集某个创作者的所有或部分视频内容

```bash
# 基础抓取（下载所有视频）
yt-dlp "https://www.tiktok.com/@用户名" \
  -P "./tiktok/data" \
  -o "%(uploader)s/%(upload_date)s-%(id)s/video.%(ext)s" \
  --write-info-json

# 只下载最近30天的视频（用于增量更新）
yt-dlp "https://www.tiktok.com/@用户名" \
  -P "./tiktok/data" \
  -o "%(uploader)s/%(upload_date)s-%(id)s/video.%(ext)s" \
  --write-info-json \
  --dateafter "$(date -u -d '30 days ago' +%Y%m%d)"

# 限制下载数量（测试用，先看能抓多少）
yt-dlp "https://www.tiktok.com/@用户名" \
  --playlist-end 50 \
  --simulate
```

**输出目录结构**：
```
tiktok/data/
  cookwithmika/
    20260220-7321567890123/
      video.mp4          # 视频文件
      video.info.json     # 元数据（标题、播放量、发布时间等）
    20260218-7321234567890/
      video.mp4
      video.info.json
```

---

### 场景三：批量下载多个用户

**适用场景**：竞品分析、跨账号数据采集

```bash
# 方法1：循环下载（适合少量账号）
for handle in cookwithmika bakingqueen烘焙达人 foodie_flix; do
  yt-dlp "https://www.tiktok.com/@$handle" \
    -P "./tiktok/data" \
    -o "%(uploader)s/%(upload_date)s-%(id)s/video.%(ext)s" \
    --write-info-json \
    --download-archive "./tiktok/downloaded.txt"
done

# 方法2：并行下载（加快速度）
(yt-dlp "https://www.tiktok.com/@cookwithmika" -P "./tiktok/data" -o "%(uploader)s/%(id)s.%(ext)s" --download-archive "./tiktok/archive.txt") &
(yt-dlp "https://www.tiktok.com/@bakingqueen" -P "./tiktok/data" -o "%(uploader)s/%(id)s.%(ext)s" --download-archive "./tiktok/archive.txt") &
wait
```

---

### 场景四：搜索、话题标签和音乐

**适用场景**：按主题收集内容、追踪热点话题

```bash
# 按关键词搜索
yt-dlp "tiktoksearch:空气炸锅食谱" --playlist-end 30

# 按话题标签采集（#booktok #foodtok）
yt-dlp "https://www.tiktok.com/tag/booktok" --playlist-end 100

# 采集使用特定音乐/原声的所有视频
yt-dlp "https://www.tiktok.com/music/original-sound-7123456789012345678" --playlist-end 50

# 采集音乐创作者主页的所有视频
yt-dlp "https://www.tiktok.com/@musiccreator" --playlist-end 200
```

**实战示例**：
```
用户说："帮我收集#AI创业 这个话题下播放量超过10万的视频"

执行：
yt-dlp "https://www.tiktok.com/tag/AI创业" \
  --playlist-end 100 \
  --match-filters "view_count >= 100000" \
  --write-info-json

结果：只下载匹配条件的高热度视频
```

---

## 高级过滤功能

### 按时间过滤

```bash
# 只下载2026年2月1日之后的视频
--dateafter 20260201

# 只下载2026年2月1日之前的视频
--datebefore 20260201

# 指定日期范围
--dateafter 20260201 --datebefore 20260228

# 动态日期（最近7天）
--dateafter "$(date -u -d '7 days ago' +%Y%m%d)"      # Linux
--dateafter "$(date -u -v-7d +%Y%m%d)"                 # macOS

# 动态日期（本月内）
--dateafter "$(date -u -d 'first day of month' +%Y%m%d)"

# 动态日期（最近24小时）
--dateafter "$(date -u -d 'yesterday' +%Y%m%d)"
```

### 按数据指标过滤

```bash
# 播放量 >= 100万
--match-filters "view_count >= 1000000"

# 点赞数 >= 10万
--match-filters "like_count >= 100000"

# 时长 30-60秒（适合短视频分析）
--match-filters "duration >= 30 & duration <= 60"

# 时长 >= 3分钟（适合长内容）
--match-filters "duration >= 180"

# 标题包含关键词（不区分大小写）
--match-filters "title ~= (?i)美食"

# 组合过滤：10万播放 + 2月发布
yt-dlp "https://www.tiktok.com/@用户名" \
  --match-filters "view_count >= 100000" \
  --dateafter 20260201

# 组合过滤：点赞率 > 5%
--match-filters "like_count / view_count > 0.05"
```

**实战示例**：
```
用户说："找出@foodie这个账号里，播放量超过50万的最火视频"

执行：
yt-dlp "https://www.tiktok.com/@foodie" \
  --simulate \
  --match-filters "view_count >= 500000" \
  --print "%(view_count)s | %(like_count)s likes | %(title)s | %(webpage_url)s" \
  | sort -rn

结果：预览筛选出的高热度视频列表
```

---

## 仅获取元数据（不下载视频）

### 预览下载内容

```bash
# 预览模式下查看视频列表
yt-dlp "https://www.tiktok.com/@用户名" \
  --simulate \
  --print "%(upload_date)s | %(view_count)s views | %(title)s"

# 查看详细信息
yt-dlp "https://www.tiktok.com/@用户名" --simulate -J | jq .
```

### 导出为 JSON 文件

```bash
# 单个 JSON 数组格式
yt-dlp "https://www.tiktok.com/@用户名" --simulate --dump-json > videos.json

# JSONL 格式（每行一个对象，推荐用于大数据量）
yt-dlp "https://www.tiktok.com/@用户名" --simulate -j > videos.jsonl

# 包含所有可用元数据
yt-dlp "https://www.tiktok.com/@用户名" \
  --skip-download \
  --write-info-json \
  -o "%(id)s.%(ext)s"
```

### 导出为 CSV 文件

```bash
# 标准 CSV 导出
yt-dlp "https://www.tiktok.com/@用户名" \
  --simulate \
  --print-to-file "%(uploader)s,%(id)s,%(upload_date)s,%(view_count)s,%(like_count)s,%(comment_count)s,%(share_count)s,%(webpage_url)s" \
  "./tiktok/analysis/metadata.csv"

# 添加表头
echo "用户名,视频ID,发布日期,播放量,点赞数,评论数,分享数,链接" > metadata.csv
yt-dlp "https://www.tiktok.com/@用户名" \
  --simulate \
  --print-to-file "%(uploader)s,%(id)s,%(upload_date)s,%(view_count)s,%(like_count)s,%(comment_count)s,%(share_count)s,%(webpage_url)s" \
  -a metadata.csv
```

### 使用 jq 分析数据

```bash
# 播放量前10的视频
jq -s 'sort_by(.view_count) | reverse | .[:10] | .[] | {title, view_count, like_count: .like_count, url: .webpage_url}' \
  tiktok/data/*/*.info.json

# 总播放量统计
jq -s 'map(.view_count) | add' tiktok/data/*/*.info.json

# 按发布日期分组统计
jq -s 'group_by(.upload_date) | map({date: .[0].upload_date, count: length, avg_views: (map(.view_count) | add / length)})' \
  tiktok/data/*/*.info.json

# 互动率计算（点赞+评论+分享/播放量）
jq -s '.[] | {title, engagement_rate: ((.like_count + .comment_count + .share_count) / .view_count * 100)}' \
  tiktok/data/*/*.info.json

# 导出为新 CSV
jq -r '[.title, .view_count, .like_count, .comment_count, .upload_date] | @csv' \
  tiktok/data/*/*.info.json > analysis.csv
```

> **提示**：将 JSONL/CSV 文件导入 Python 的 pandas 库，可以进行更深入的分析和可视化，如散点图、发布时间热力图、跨创作者对比等。

---

## 持续采集与定时任务

### 增量更新（跳过已下载）

```bash
# 使用归档文件追踪已下载内容
yt-dlp "https://www.tiktok.com/@用户名" \
  -P "./tiktok/data" \
  -o "%(uploader)s/%(upload_date)s-%(id)s/video.%(ext)s" \
  --write-info-json \
  --download-archive "./tiktok/downloaded.txt"

# 多次运行时自动跳过已有视频
# 适合每日定时任务，持续追踪新内容
```

### 认证访问（私密/受限制内容）

```bash
# 使用浏览器 Cookie（推荐，用于访问私密账号）
yt-dlp --cookies-from-browser chrome "https://www.tiktok.com/@用户名"

# 使用 Cookie 文件
yt-dlp --cookies ./tiktok_cookies.txt "https://www.tiktok.com/@用户名"

# 导出 Cookie 方法（Chrome 扩展）：
# 1. 安装 "Get cookies.txt LOCALLY" 扩展
# 2. 登录 TikTok 后导出 Cookie 文件
```

### 定时自动采集

**创建采集脚本** `scripts/scrape-tiktok.sh`：

```bash
#!/bin/bash
set -e

# 配置参数
ACCOUNTS="cookwithmika bakingqueen烘焙达人 foodie_flix"
DATA_DIR="./tiktok/data"
ARCHIVE="./tiktok/downloaded.txt"
LOG_DIR="./tiktok/logs"

# 创建日志目录
mkdir -p "$LOG_DIR"

for handle in $ACCOUNTS; do
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始采集 @$handle"
  yt-dlp "https://www.tiktok.com/@$handle" \
    -P "$DATA_DIR" \
    -o "%(uploader)s/%(upload_date)s-%(id)s/video.%(ext)s" \
    --write-info-json \
    --download-archive "$ARCHIVE" \
    --cookies-from-browser chrome \
    --dateafter "$(date -u -d '7 days ago' +%Y%m%d)" \
    --sleep-interval 3 \
    --max-sleep-interval 8 \
    2>&1 | tee -a "$LOG_DIR/scrape_$(date '+%Y%m%d').log"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] @$handle 采集完成"
done

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 本次采集任务全部完成"
```

**设置定时任务**（crontab）：

```bash
# 编辑定时任务
crontab -e

# 每天早上8点执行
0 8 * * * cd /path/to/project && ./scripts/scrape-tiktok.sh >> ./tiktok/logs/cron.log 2>&1

# 每6小时执行一次
0 */6 * * * cd /path/to/project && ./scripts/scrape-tiktok.sh >> ./tiktok/logs/cron.log 2>&1

# 每周一早上9点执行
0 9 * * 1 cd /path/to/project && ./scripts/scrape-tiktok.sh >> ./tiktok/logs/cron.log 2>&1
```

---

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 空结果 / 找不到视频 | 添加 `--cookies-from-browser chrome`，TikTok 对匿名请求限流 |
| 403 Forbidden 错误 | 被限流，等待10-15分钟，或使用Cookie/更换IP |
| "视频不可用" | 区域限制，尝试 `--geo-bypass` 或使用VPN |
| 下载的是带水印视频 | 使用 `-F` 查看可用格式，有些格式可能无水印 |
| 下载速度慢 | 添加 `--concurrent-fragments 4` 加快下载 |
| 主页显示视频数少于预期 | TikTok API限制，使用 `--playlist-end N` 明确指定数量，尝试加Cookie |

### 调试模式

```bash
# 详细输出诊断问题
yt-dlp -v "https://www.tiktok.com/@用户名" 2>&1 | tee debug.log

# 查看完整的请求头和响应
yt-dlp -v --dump-headers "https://www.tiktok.com/@用户名" 2>&1

# 测试模式（不下载）
yt-dlp --simulate -v "https://www.tiktok.com/@用户名" 2>&1
```

---

## 参数速查表

### 常用选项

| 参数 | 说明 | 示例 |
|------|------|------|
| `-o 模板` | 输出文件名模板 | `-o "%(uploader)s/%(id)s.%(ext)s"` |
| `-P 路径` | 下载目录 | `-P "./tiktok/data"` |
| `--dateafter 日期` | 限定发布日期之后 | `--dateafter 20260201` |
| `--datebefore 日期` | 限定发布日期之前 | `--datebefore 20260228` |
| `--playlist-end N` | 最多下载N个视频 | `--playlist-end 50` |
| `--match-filters 表达式` | 按元数据过滤 | `--match-filters "view_count >= 100000"` |
| `--write-info-json` | 保存元数据JSON | `--write-info-json` |
| `--download-archive 文件` | 归档已下载，跳过重复 | `--download-archive archive.txt` |
| `--simulate` / `-s` | 模拟运行，不下载 | `--simulate` |
| `-j` / `--dump-json` | 输出元数据为JSON | `-j` |
| `--cookies-from-browser 浏览器` | 使用浏览器Cookie | `--cookies-from-browser chrome` |
| `--sleep-interval 秒` | 下载间隔（秒） | `--sleep-interval 3` |
| `-x` | 仅下载音频 | `-x --audio-format mp3` |

### 输出模板变量

| 变量 | 说明 | 示例输出 |
|------|------|---------|
| `%(id)s` | 视频ID | `7321567890123` |
| `%(uploader)s` | 上传者/用户名 | `cookwithmika` |
| `%(upload_date)s` | 上传日期 | `20260220` |
| `%(title).50s` | 标题（前50字符） | `空气炸锅鸡翅做法...` |
| `%(view_count)s` | 播放量 | `1500000` |
| `%(like_count)s` | 点赞数 | `250000` |
| `%(comment_count)s` | 评论数 | `12000` |
| `%(share_count)s` | 分享数 | `5000` |
| `%(duration)s` | 时长（秒） | `45` |
| `%(ext)s` | 文件扩展名 | `mp4` |
| `%(webpage_url)s` | 视频链接 | `https://www.tiktok.com/...` |

[完整模板参考 →](https://github.com/yt-dlp/yt-dlp#output-template)

---

## 常见使用流程示例

### 流程一：竞品账号分析

```bash
# 1. 采集目标账号视频元数据（不下载视频）
yt-dlp "https://www.tiktok.com/@竞品账号" \
  --simulate -j > competitor_videos.jsonl

# 2. 分析数据
jq -s '[.[] | {views: .view_count, likes: .like_count, date: .upload_date}]' \
  competitor_videos.jsonl

# 3. 下载高价值视频
yt-dlp "https://www.tiktok.com/@竞品账号" \
  --match-filters "view_count >= 100000" \
  -P "./competitor/top_videos/" \
  --download-archive "./competitor/archive.txt"
```

### 流程二：话题追踪

```bash
# 1. 收集话题下的热门视频
yt-dlp "https://www.tiktok.com/tag/你的话题" \
  --playlist-end 200 \
  --match-filters "view_count >= 50000" \
  --write-info-json \
  -P "./trending/topic_data/"

# 2. 定时更新
# crontab: 0 */6 * * * 上述命令
```

### 流程三：音乐/原声分析

```bash
# 1. 获取使用某音乐的所有视频
yt-dlp "https://www.tiktok.com/music/原声名-7123456789" \
  --simulate -j > trending_sounds.jsonl

# 2. 统计使用该音乐的视频数量和平均播放量
jq -s '[length, (map(.view_count) | add / length)]' trending_sounds.jsonl
```
