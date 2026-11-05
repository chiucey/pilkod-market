# 视频后处理：去水印 + 修花字乱码

视频生成完**必须**走这两步检查。AI 视频工具的两个通病：
1. **右下角/角落自动打水印**（平台侧行为，重新生成去不掉，只能后处理裁掉）。
2. **屏幕花字渲染乱码**——尤其越南语/泰语/法语/西班牙语等带声调或特殊符号的文字，AI 经常把声调、字符渲染错（例如 "Bị mốc phấn" 渲染成 "Bi móc phần"）。VO 念的内容不受影响，但屏幕字会露馅。

## 目录

- [一、水印检查与去除](#一水印检查与去除)
- [二、花字乱码检查](#二花字乱码检查)
- [三、花字修正（局部模糊 + drawtext 重写）](#三花字修正局部模糊--drawtext-重写)
- [踩坑记录](#踩坑记录)

---

## 一、水印检查与去除

### 检查
下载视频后，抽 2-3 帧（开头/中间/结尾）看右下角：
```bash
ffmpeg -ss 14 -i input.mp4 -vframes 1 check_last.png
```
打开 check_last.png，放大右下角。常见豆包/即梦水印是小 logo，在最右下角距边 10-40px 内。

### 去除：放大裁剪法（推荐）
把画面整体放大 ~10% 再裁回原尺寸，让角落水印被推出画外。对主体（人脸居中、产品居中）影响最小。

以 720×1280 为例：
```bash
ffmpeg -i input.mp4 -vf "scale=792:1408,crop=720:1280:36:64" -c:a copy output_nowm.mp4
```
- `scale=792:1408`：宽高各放大 10%（720×1.1=792，1280×1.1=1408）
- `crop=720:1280:36:64`：居中裁回原尺寸，x偏移=(792-720)/2=36，y偏移=(1408-1280)/2=64
- 如果水印在左下角/左上角/右下角，偏移量方向相应调整；不确定就先居中裁。
- 其他分辨率按比例换算：新尺寸 = 原尺寸 × 1.1，裁剪偏移 = (新尺寸-原尺寸)/2。

**代价**：四周各裁掉一圈（左右36px、上下64px），主体在安全区内不受影响。

---

## 二、花字乱码检查

抽每个镜头时段中间的帧：
```bash
# 15秒视频分3镜，抽 2s / 7s / 13s
for t in 2 7 13; do ffmpeg -ss $t -i input.mp4 -vframes 1 "sub_${t}.png"; done
```
逐帧看屏幕花字。**判断标准**：
- 字母/声调符号是否和分镜里写的一致（越南语的 Ă Â Ê Ô Ơ Ư Đ + 五个声调符号；泰语的元音声调符号）。
- 常见乱码：声调符号错位、"ă/â"写成"a"、"ơ/ư"写成"o/u"、出现不存在的字符。
- 只要屏幕字和你分镜里写的不一致，就算乱码，必须修。

---

## 三、花字修正（局部模糊 + drawtext 重写）

### 思路
1. 把花字所在的底部横条模糊掉（盖住旧乱码字）。
2. 用 drawtext 在模糊条上重写正确文字。

### 字体
用系统自带的 **Noto Sans Bold**（支持越南语/泰语等扩展拉丁字符）：
```
/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf
```
先 `fc-list | grep "NotoSans-Bold"` 确认路径存在。

### 完整命令模板（以 720×1280、3 段花字为例）

```bash
ffmpeg -i input.mp4 -filter_complex "
[0:v]split=2[bg][fg];
[fg]crop=720:230:0:985,boxblur=14:2[blurred];
[bg][blurred]overlay=0:985[base];
[base]drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf:textfile=s1.txt:fontsize=28:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=1075:enable='between(t,0.3,5)',
drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf:textfile=s2.txt:fontsize=25:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=1080:enable='between(t,5.3,10)',
drawtext=fontfile=/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf:textfile=s3.txt:fontsize=27:fontcolor=white:borderw=2:bordercolor=black:x=(w-text_w)/2:y=1075:enable='between(t,10.3,15)'
" -c:a copy output_fixed.mp4
```

### 参数说明
- **模糊条位置**：`crop=720:230:0:985` 意思是从 y=985 开始裁 230px 高（覆盖 985–1215），`overlay=0:985` 放回。**先抽帧确认旧花字实际 y 坐标**，模糊条必须完整覆盖旧花字（上下各多留 20-30px 余量）。本次实战第一次模糊条放低了 40px 没盖住旧字，教训：宁高勿低、宁大勿小。
- **新花字 y**：放在模糊条中间（y≈1075），白色字 `fontcolor=white` + 黑描边 `borderw=2:bordercolor=black`，和 TikTok 原生花字风格一致。
- **时间段**：`enable='between(t,起,止)'`，比镜头分界早 0.3s、晚一点切，避免跳变。
- **字号**：720×1280 下 25-28 合适；花字超过一行宽度就降到 24。
- **文字内容**：长文本写进 `.txt` 文件用 `textfile=`；短文本直接 `text='...'`。

### 写文字文件
```bash
cat > s1.txt <<'EOF'
Bị mốc phấn rồi
EOF
```
UTF-8 保存，不要有 BOM。

### 验证
处理完再抽 3 帧确认：
```bash
for t in 2 7 13; do ffmpeg -ss $t -i output_fixed.mp4 -vframes 1 "check_${t}.png"; done
```
检查：①旧乱码字是否被模糊盖住 ②新字是否正确、居中、不挡产品和人脸 ③模糊条是否太突兀。

---

## 踩坑记录

- **不要在花字里用 `%` 符号**：ffmpeg drawtext 把 `%` 当格式串开头，会报 "Stray %" 警告并导致整段文字不渲染。越南语 "100% tự nhiên" 改成 "hoàn toàn tự nhiên"（完全天然）或 "tự nhiên" 即可，意思不变。
- **emoji 用不了**：drawtext 默认字体不渲染彩色 emoji（😩✨⭐）。花字里直接去掉 emoji，或换成简单符号（`!`、`*`）。要 emoji 需装 Noto Color Emoji 字体并额外配置，不值得。
- **模糊条是全程显示的**：因为不知道旧花字哪帧出现，模糊条会在视频底部全程显示。这是必要妥协，选在底部 18% 高度内，不挡人脸和产品。
- **VO 不受影响**：屏幕花字乱码只改屏幕字，VO 念的内容是 AI 视频模型生成的音轨，已经是对的，不要重录。
- **一次最多处理 2 个视频**：和生成阶段一致。
