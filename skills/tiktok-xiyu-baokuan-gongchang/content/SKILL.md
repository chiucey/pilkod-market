---
name: tiktok-xiyu-baokuan-gongchang
description: >
  Full pipeline for producing TikTok Spanish viral videos: extract copy from links,
  AI rewrite with scoring and polishing, translate to Latin American Spanish, format
  for voice-over line-by-line, guide ElevenLabs TTS, give FFmpeg/PR editing advice.
  Activates when user says "做西语解说", "TikTok西语", "足球解说西语",
  "电影解说西语", "西语爆款", "帮我做西语视频", or provides a Douyin/TikTok/web
  link asking to make a Spanish version. Supports football commentary, movie narration,
  drama commentary, and sports highlights. Output language: Latam Spanish.
license: CC-BY-4.0
metadata:
  version: "1.0"
  category: content-creation
  sources:
    - https://elevenlabs.io
    - https://github.com/yt-dlp/yt-dlp
    - https://ffmpeg.org
---

# TikTok西语爆款工厂

> 适用类型：足球解说、电影解说、剧情解说、体育集锦  
> 输出语言：拉丁美洲西班牙语（Latam Spanish）  
> 核心工具：yt-dlp + ElevenLabs + FFmpeg/PR

---

## 触发条件

当用户说以下任意关键词时加载本技能：
- "做西语解说"
- "TikTok西语"
- "足球解说西语"
- "电影解说西语"
- "西语爆款"
- "帮我做西语视频"
- 直接提供抖音/TikTok/网页链接并要求制作西语版本

---

## 工作流程总览


Step 1 → 文案提取（链接/文件/文本）
Step 2 → AI洗稿 + 评分 + 润色（满分中文文案）
Step 3 → 中译拉丁美洲西班牙语
Step 4 → 格式化分行（配音专用）
Step 5 → ElevenLabs配音指引
Step 6 → FFmpeg/PR剪辑 + 合规建议


复制

---

## Step 1：文案提取

**规则：按优先级选择提取方式**

**优先级 1 - 抖音/TikTok 链接：**

工具：mcp_batch_web_search 或自行用 yt-dlp 下载
命令：python3 -m yt_dlp --cookies /path/to/cookies.txt [URL]
注：抖音需完整Cookie（从Chrome DevTools Network标签提取），单独sessionid不够


复制

**优先级 2 - 普通网页/文章链接：**

工具：extract_content_from_websites


复制

**优先级 3 - 本地文件：**

工具：read_file


复制

**优先级 4 - 用户直接粘贴文字：**
直接使用，无需工具。

**提取后保存为 `original_text`，并告知用户：**
> "已提取文案，共 XXX 字。现在进入 Step 2 洗稿润色环节。"

---

## Step 2：AI 洗稿 · 评分 · 润色

对 `original_text` 执行以下三步：

**任务 A - 洗稿规则：**
- 每句话 15-25 字
- 悬念钩子开头（前3秒抓人）
- 删除冗余过渡句
- 保留核心转折点

**任务 B - 五维评分（满分100）：**
| 维度 | 满分 |
|------|------|
| 悬念感 | 20分 |
| 节奏感 | 20分 |
| 情感共鸣 | 20分 |
| 语言精炼度 | 20分 |
| 口语化程度 | 20分 |

**任务 C - 润色输出"满分文案"：**
- 加入语气词（Mira... Increíble... ¿Sabías que...?）
- 增强感叹句感染力
- 确保每段结尾有自然停顿

**输出格式：**

洗稿文案
[内容]
评分结果
总分：XX/100
悬念感：XX/20 | 节奏感：XX/20 | 情感共鸣：XX/20 | 语言精炼度：XX/20 | 口语化程度：XX/20
[评语]
满分文案
[润色后版本]


复制

保存润色结果为 `polished_text`。

---

## Step 3：中译拉丁美洲西班牙语

**翻译核心原则：**
- 使用 **tú**（不用 usted/vos）
- 拉美本地词汇优先：
  - móvil → celular
  - ordenador → computadora
  - autobús → colectivo
  - 足球场 → la cancha / el estadio
  - 射门 → disparar / rematar
  - 帽子戏法 → hat-trick（直接借用，已被拉美接受）
- 解说固定句式：
  - "接下来..." → "Lo que viene después..."
  - "你绝对想不到..." → "No te imaginas lo que pasa..."
  - "真相是..." → "La verdad es que..."
  - "这就是..." → "Eso es..."
  - "直到最后..." → "Hasta el final..."

**足球解说专用词汇：**
- 进球：gol, tantos, anotar
- 传球：pase, centrar, colgar el balón
- 防守：defensa, tapar, robar
- 逆转：remontada, dar vuelta al partido
- 角球：tiro de esquina / córner
- 越位：fuera de lugar / offside

保存翻译结果为 `spanish_text`。

---

## Step 4：格式化分行

**规则：**
- `.` `!` `?` 后必须换行
- `,` 在长句（>15词）中换行
- 每行 ≤15 词
- 语气词/感叹词独立成行
- 保留原始标点

**示例：**

原文：Minuto 77, Cristiano se para frente al balón, corre y dispara.
格式化：
Minuto 77,
Cristiano se para frente al balón,
corre y dispara.


复制

保存格式化结果为 `formatted_spanish`。

---

## Step 5：ElevenLabs 配音指引

**操作步骤：**

1. 打开 https://elevenlabs.io → 登录
2. 选择西语语音：
   - 男声推荐：Santiago、Diego、Gabriel
   - 女声推荐：Valentina、María、Camila
3. 复制 `formatted_spanish` 全文粘贴
4. 设置：Speed 0.95，Stability 0.6
5. 点击 Generate → 下载 MP3

**本地配音替代方案（如用户有其他TTS工具）：**
- MiniMax TTS（可用 batch_synthesize_speech 工具）
- Azure TTS 西语（latam-ES）
- 已克隆声音（Voice Cloning）

---

## Step 6：FFmpeg/PR 剪辑 + 合规建议

**FFmpeg 自动化剪辑（如视频在本地）：**

```bash
# 截取精彩片段（前60秒）
ffmpeg -i input.mp4 -ss 0 -t 60 -c:v libx264 -preset fast -crf 23 output_60s.mp4

# 竖屏裁切（16:9 → 9:16）
ffmpeg -i input.mp4 -vf "crop=ih*9/16:ih" -c:a copy output_vertical.mp4

# 添加字幕
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output_with_subs.mp4

# 压制到指定大小（<100MB）
ffmpeg -i input.mp4 -vf "scale=1280:720" -b:v 2000k -bufsize 2000k output_compressed.mp4

PR 剪辑合规检查清单：









































检查项
要求
画面比例
9:16 竖屏（1080×1920）
片头
前3秒字幕钩子
单片段时长
≤30秒
总使用时长
≤原片10%
B-roll频率
每15-20秒切换
人声:背景乐
7:3 音量比
字幕
西语，15-20字/行，白字描边
画面处理
镜像/变色/加速可降低版权识别
版权风险处理：
	•	
	•	单一来源片段 ≤30秒
	•	多个来源混合使用
	•	添加画面特效（色相偏移+5~+15、水平翻转）
	•	加速/减速 5-10%


成品汇总输出模板


复制
# TikTok西语爆款工厂 - 成品汇总

## 原始文案
[original_text]

## 满分中文文案
[polished_text]

## 拉丁美洲西班牙语
[spanish_text]

## 格式化分行（配音用）
[formatted_spanish]

## ElevenLabs 操作指引
[Step 5内容]

## 剪辑建议
[Step 6内容]

---
💡 文案已可直接用于 ElevenLabs。配音完成后将 MP3 导入剪映/PR，
按上方剪辑建议操作即可发布。


常见问题 & 避坑
Q: 抖音链接下载失败？
A: 需要完整Cookie。从Chrome DevTools → Network → 请求的 Request Headers → Cookie字段，复制全部内容，用--cookies参数传入。单独sessionid不够。
Q: 翻译腔太重？
A: 强制要求使用tú、celular等拉美词汇，避免西班牙特有表达。用语气词（¿Sabías que...? / Mira esto...）增加口语感。
Q: 文案太长？
A: TikTok配音建议总时长60-180秒。按每分钟150词的语速，总字数控制在1500-4500字。超长文案需截断或分段。
Q: 视频文件太大无法上传？
A: 用FFmpeg压缩：ffmpeg -i video.mp4 -vf "scale=1280:720" -b:v 2000k output.mp4
或截取精彩片段：ffmpeg -i video.mp4 -ss 30 -t 60 -c copy clip.mp4

更新日志
	•	
	•	v1.0.0 (2026-04-17): 初始版本，整合足球/电影解说全流程

