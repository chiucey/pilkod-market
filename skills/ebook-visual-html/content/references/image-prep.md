# 图片准备

扫描页原图动辄几 MB，整本直塞会让页面在手机和低端设备上卡死。缩图是这一步唯一的主要目的。

## 目录与命名

```
<work>/
├── assets/
│   ├── cover.jpg        封面，建议长边 ≤2400
│   └── img/
│       ├── p001.jpg     正文配图，长边 ≤1600
│       ├── p002.jpg
│       └── …
```

`pNNN` 的编号必须等于页序（从 1 起、零填充 3 位）。写 `content.json` 时按编号引用，
后面某页要重切，只要覆盖同名文件再 rebuild，不用改内容。

## 一条命令搞定

```bash
node scripts/prepare-images.mjs <扫描目录或文件…> --out <work>/assets/img --max 1600
```

脚本按 `sips` → `magick` → `ffmpeg` → `python3 + Pillow` 顺序探测可用工具，逐张缩放，
跳过已存在且更新的目标文件（`--force` 强制重做），最后打印成功/失败清单。
封面单独来一次：`--out <work>/assets --max 2400 --name cover`。

## 工具探测与手工等价命令

| 工具 | 命令 | 平台 |
|---|---|---|
| sips | `sips -s format jpeg -s formatOptions 82 --resampleWidth 1600 in.jpg --out out.jpg` | macOS 自带 |
| ImageMagick | `magick in.jpg -resize "1600x>" -quality 82 out.jpg` | 跨平台 |
| ffmpeg | `ffmpeg -y -i in.jpg -vf "scale='min(1600,iw)':-2" -q:v 4 out.jpg` | 跨平台 |
| Pillow | `python3 -c "from PIL import Image; im=Image.open('in.jpg'); im.thumbnail((1600,1600)); im.convert('RGB').save('out.jpg','JPEG',quality=82)"` | 跨平台 |

Windows（PowerShell）同样用 `magick` 或 Pillow，路径加引号即可：

```powershell
magick "in.jpg" -resize "1600x>" -quality 82 "out.jpg"
```

## 沙箱注意：sips 会“报成功但不产出文件”

受限运行环境里 sips 可能无法写入系统临时目录，命令返回成功但目标文件根本不存在。
**必须校验产物**：脚本已经这么做了，你手工跑时也要 `ls -la` 确认一次。
文件不在就换下一个工具，不要把同一个失败命令反复重跑。

## 顺手能做的处理

- **扫描质量差**：先用 ffmpeg 提对比度再看图，比硬读强很多：
  `ffmpeg -y -i p003.jpg -vf "eq=contrast=1.25:brightness=0.02,format=gray" p003-hi.png`
- **书脊、页边黑边**：先裁掉再识别，能显著降低误读。用 ffmpeg：
  `ffmpeg -y -i in.jpg -vf "crop=iw*0.94:ih*0.96:iw*0.03:ih*0.02" out.jpg`
- **整页只有一张插图**：直接当 `figure` 用；需要切图再走上面的裁剪。
- **图太糊不适合上网页**（原图分辨率低于 1200px）：保留 `slot` 占位，别硬塞一张糊图毁版面。

## 封面

封面图按图片处理，不从图上提取文字。封面区里的书名、作者、副标题、简介是另写的文案，
写在 `content.json` 的 `meta` 里，和图上的内容互不依赖——换一版封面图不需要重写文案。
书衣展开图（一张里含书脊与封底）很宽，直接用作封面横幅效果最好；想只取正面书封，
用 `crop` 按比例裁一次，裁完命名为 `cover.jpg`。
没有封面图时不要造一张假的，`content.json` 里省掉 `meta.cover`，build 会输出一个封面占位框。
