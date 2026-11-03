---
name: 服装换色
description: 服装换色AI执行工具。根据用户上传的图片和目标颜色，分析材质与视觉特征，自动调用 @AI绘图 生成换色后的图片并返回。支持三种批量模式：单图多色、多图单色、多图多色全量。触发场景：用户上传服装图片并要求换色。
---

# 服装换色

分析服装图片，生成换色提示词，并通过 LinkFoxAgent `@AI绘图` 直接执行，将生成图片发送给用户。**所有提示词均为中文。**

---

## 第一步：模式识别

收到请求后，**优先判断模式**：

| 模式 | 判断条件 | 输出数量 |
|------|---------|---------|
| **单图单色** | 1张图 + 1个目标色 | 1张 |
| **单图多色** | 1张图 + 多个目标色 | N张 |
| **多图单色** | 多张图 + 1个目标色 | N张 |
| **多图多色** | 多张图 + 多个目标色 | N×M张 |

**颜色解析：**
- Hex 值直接使用：`#ff0000`
- 颜色名称转换为近似 Hex：枣红色→`#8B1A1A`，雾霾蓝→`#8FA3B1`，米白色→`#F5F0E8`
- 混合输入均支持

告知用户将生成的图片数量，然后开始执行。

---

## 第二步：图片分析（四维度）

对每张图片执行一次分析，提取以下信息（批量模式下同一张图只分析一次）：

### 维度1：服装识别 + 当前颜色
- 识别服装名称（如：黑色高腰抽绳运动短裙）
- 用 Hex 色值描述当前颜色，不确定时标注 `[待确认]`
- 注明需保持原色的配件（缝线、纽扣、内搭等）

### 维度2：材质/质感
仅描述图片中**可识别**的特征，不臆测：
- ⚠️ 光泽感 ≠ 皮革（优先判断为缎面/丝绸）
- ⚠️ 粗糙肌理 ≠ 亚麻
- ⚠️ 透明/半透 ≠ 必定是纱

### 维度3：保留边界
列出不可改变的项目：
- 版型/剪裁/裙长/袖长
- 松紧带/抽绳/拉链/纽扣
- 口袋/领口/袖口/下摆造型
- 面料肌理/织法特征
- 人物姿势/手部位置（模特图）
- 内搭/搭配单品（保持原色）

### 维度4：光线/阴影
描述基础光线，并判断是否需要氛围协调：

| 原图风格 | 目标色类型 | 协调策略 |
|---------|-----------|---------|
| 灰暗/暗调 | 高饱和鲜艳色 | 提亮环境光，降低明暗对比，增加漫反射 |
| 明亮/高调 | 深沉暗色 | 适当加深阴影，保持主体清晰 |
| 戏剧光影 | 任何颜色 | 保持原有光影，让新颜色融入 |
| 柔和均匀光 | 任何颜色 | 无需调整 |

---

## 第三步：换色选区确认（画廊页面）

图片分析完成后，**在构建提示词和执行换色前**，调用画廊生成脚本，将分析结果渲染为可视化确认页面并嵌入对话框。

### 3.1 准备 JSON 数据

将第二步的分析结果整理为以下 JSON，写入 `/tmp/fuzhuang-confirm-data.json`：

```json
{
  "images": ["/abs/path/img1.jpg"],
  "change_items": [
    {
      "name": "黑色高腰运动短裙",
      "current_hex": "#1a1a1a",
      "current_name": "黑色",
      "warning": null
    },
    {
      "name": "腰带",
      "current_hex": "#1a1a1a",
      "current_name": "黑色",
      "warning": "与短裙同色系，建议一起换色"
    }
  ],
  "target_colors": [
    {"hex": "#228B22", "name": "森林绿"},
    {"hex": "#8B1A1A", "name": "枣红色"}
  ],
  "preserve_items": ["版型/裙长", "松紧带/抽绳", "模特姿势/手部位置", "背景"]
}
```

字段说明：
- `images`：原图**绝对路径**列表（用户上传的本地文件路径）
- `change_items`：将换色的项目；`warning` 为 `null` 或同色系/配套提示文字
- `target_colors`：用户指定的目标颜色列表
- `preserve_items`：保留不变的项目，每项一个简短字符串

### 3.2 生成确认图片（全渠道通用）

```bash
IMG_PATH=$(python3 ~/.openclaw/skills/fuzhuang-huanse/scripts/gen_confirm_image.py \
  < /tmp/fuzhuang-confirm-data.json)
echo "IMG_PATH=$IMG_PATH"
```

脚本会自动：
1. 将原图缩略图嵌入画面
2. 绘制换色项目（当前色块 → 目标色块）、同色系警告徽章
3. 绘制目标颜色大色卡
4. 绘制保留项标签云
5. 输出 PNG 绝对路径（如 `/tmp/fuzhuang-confirm-1746000000.png`）

### 3.3 发送图片 + 可选 embed

**必做（所有渠道）：** 用 `linkfox_upload_file` 发送图片，并附上确认提示：

```python
linkfox_upload_file(paths=[IMG_PATH])
# 同时回复文字：
# 以上换色范围是否正确？如需调整（增加或减少换色项目），请直接告知，确认后立即执行。
```

**可选（仅 webchat）：** 同时生成 HTML 画廊并嵌入：

```bash
CANVAS_ID=$(python3 ~/.openclaw/skills/fuzhuang-huanse/scripts/gen_confirm_gallery.py \
  < /tmp/fuzhuang-confirm-data.json)
```

```
[embed ref="<CANVAS_ID>" title="换色选区确认" height="520" /]
```


### 同色系 / 配套单品自动标记规则

| 情况 | `warning` 字段内容 |
|------|-------------------|
| 多件单品颜色相近（视觉上属同色系） | `"与XX同色系，建议一起换色"` |
| 明显配套单品（裙+手套、上衣+披肩/围巾/领巾） | `"与XX为配套单品，建议一起换色"` |
| 颜色差异明显的独立单品 | `warning: null`，列入 `preserve_items` |

### 重复款式跳过确认

如果当前 session 中已经对**相同款式**（相同服装名称 + 相同当前颜色）做过确认，本次分析完成后**直接进入第四步**，无需再次等待用户确认。主 agent 应在 session 上下文中记住已确认的款式信息。

### 用户确认后的处理

- **确认无误** → 进入第四步，按确认后的选区构建提示词
- **增加换色项** → 将新增项加入 `change_items`，从 `preserve_items` 移除，**重新执行 3.1–3.3** 生成新画廊，再次等待确认
- **减少换色项** → 将移除项加入 `preserve_items`，**重新执行 3.1–3.3**，再次等待确认
- **修改目标颜色** → 更新 `target_colors` 后**重新执行 3.1–3.3**，再次等待确认

## 第四步：构建 @AI绘图 提示词

每个颜色生成一条紧凑提示词，**严格控制在 1000 字符以内**：

**格式模板：**
```
将图中的[服装名称]颜色替换为[目标色Hex]（[颜色名]），保持版型/材质/光线不变。材质：[简短材质描述]。保留：[关键保留项，逗号分隔]。[氛围协调说明（仅在需要时添加）]禁止改变构图、版型、材质纹理、图片宽高比例，禁止模糊变形失真。
```

---

## 第五步：执行换色（sessions_spawn）

### 5.1 上传原图 + 调用 @AI绘图 + 下载图片

将图片上传、@AI绘图 调用、下载合并在同一个子 agent 中执行：

⚠️ **每个颜色必须单独提交一个任务，禁止将多个颜色打包进同一条 @AI绘图 消息。**
多色打包会导致 AI 将多次生成的视觉元素互相融合，产生"两件衣服合并"的错误结果。

**子 agent 任务模板（每色独立提交 + 异步轮询）：**

```
Execute the following steps and report all results back.

Step 1: Upload image
Run: python3 ~/.openclaw/skills/linkfoxagent/scripts/upload_image.py "<本地图片绝对路径>"
Capture the returned URL as IMAGE_URL. If this fails, report error and stop.

Step 2: Submit EACH color as a SEPARATE independent task (one task per color)
CRITICAL: Each @AI绘图 request must be its own linkfox.py call.
NEVER put multiple colors in one message — it causes visual blending/fusion.

  Color 1:
  Write /tmp/fuzhuang-<suffix>-c1.txt: "1、@AI绘图 参考图片：<IMAGE_URL>，提示词：<颜色1的紧凑提示词>"
  Run: python3 ~/.openclaw/skills/linkfoxagent/scripts/linkfox.py --stdin < /tmp/fuzhuang-<suffix>-c1.txt
  Capture messageId_1 from JSON output: {"messageId": "xxx"}

  Color 2:
  Write /tmp/fuzhuang-<suffix>-c2.txt: "1、@AI绘图 参考图片：<IMAGE_URL>，提示词：<颜色2的紧凑提示词>"
  Run: python3 ~/.openclaw/skills/linkfoxagent/scripts/linkfox.py --stdin < /tmp/fuzhuang-<suffix>-c2.txt
  Capture messageId_2 from JSON output

  （以此类推，每个颜色一个独立文件 + 独立提交）

Print: "已提交 N 个独立任务：messageId_1=xxx, messageId_2=xxx, ..."
If any submission fails → report error for that color, continue with others.

Step 3: Round-robin poll ALL messageIds until all complete

Write /tmp/fuzhuang-poll-<timestamp>.py，填入 Step 2 获取的实际 messageId 后运行：

```python
import subprocess, os, re, time

LINKFOX = os.path.expanduser('~/.openclaw/skills/linkfoxagent/scripts/linkfox.py')

# 填入 Step 2 获取的实际 messageId
pending = {
    '颜色1名称': 'MESSAGEID_1',
    '颜色2名称': 'MESSAGEID_2',
    # 按实际颜色数量添加
}
results = {}

for round_num in range(40):  # 最多约 20 分钟
    for color in list(pending.keys()):
        r = subprocess.run(
            ['python3', LINKFOX, '--poll', pending[color], '--timeout', '10', '--interval', '5'],
            capture_output=True, text=True, timeout=30
        )
        out = r.stdout + r.stderr
        if 'Status: finished' in out:
            urls = re.findall(r'https://agent-files\.linkfox\.com/[^\s"<>]+\.(?:png|jpg|jpeg|webp)', out)
            if urls:
                results[color] = urls[0]
                del pending[color]
                print(f'DONE {color}: {urls[0]}')
        elif 'Status: error' in out:
            print(f'ERROR {color}')
            del pending[color]
    if not pending:
        print('ALL_COMPLETE')
        break
    print(f'WAITING round={round_num+1} pending={list(pending.keys())}')
    time.sleep(3)

for color, url in results.items():
    print(f'RESULT {color} {url}')
```

Run: python3 /tmp/fuzhuang-poll-<timestamp>.py
解析输出：
- "DONE 颜色: URL" → 记录该颜色的结果 URL
- "ALL_COMPLETE" → 全部完成，进入 Step 4
- "ERROR 颜色" → 该颜色失败，跳过
- 脚本结束后仍有颜色未完成 → 报告超时，附 messageId 供手动恢复
Step 4: Download generated images and fix aspect ratio
For each completed color:
- mkdir -p /tmp/fuzhuang-huanse
- curl -s -o "/tmp/fuzhuang-huanse/颜色名_Hex.png" "<图片URL>"
- python3 ~/.openclaw/skills/fuzhuang-huanse/scripts/fix_aspect_ratio.py "<原始图片本地路径>" "/tmp/fuzhuang-huanse/颜色名_Hex.png"
  （原始图片本地路径 = Step 1 中传给 upload_image.py 的路径）
- Report local path and original URL

Rules:
- NEVER batch multiple colors in one @AI绘图 message — one color = one task
- upload_image.py fails → report error and stop
- Each poll exec is at most 30s; never use --wait or background long-running processes
- Extract image URL from HTML output for each color's result
- If ShareURL present → include it in report
- messageIds are recovery keys: if sub-agent restarts, resume polling from Step 3
```

**派发前告知用户：**
> 「正在上传图片并提交换色任务，共 N 张图片 × M 个颜色 = NM 套，预计 1-5 分钟...」

### 5.2 多图场景

每张图片单独上传，并行派发多个子 agent（每个子 agent 处理一张图的全部颜色，每色独立提交）。

⚠️ **所有执行子 agent 必须在同一轮消息中一次性全部派出**，不得分批等待用户消息后再逐个派发。每次 `sessions_spawn` 调用之间不要等待，连续调用直到所有图片的子 agent 全部启动。

### 5.3 颜色数量较多时

颜色数量较多时，所有颜色仍各自独立提交，子 agent 内部顺序提交后并行轮询所有 messageId。

---

## 第六步：发送图片给用户

子 agent 完成后，主 agent 收到所有本地路径，执行以下交付流程：

> ⚠️ **`linkfox_upload_file` 是上下文绑定工具，必须由主 agent 直接调用，严禁在子 agent 中调用。**
> 子 agent 是隔离 session，没有 Linkfox 对话上下文，调用会静默返回"成功"但文件不会投递给用户。

### Step 6.1 打包为 ZIP（在子 agent 中执行，仅报告路径）

派发一个子 agent 完成打包，子 agent **只负责创建 ZIP 并报告路径，不调用 linkfox_upload_file**：

⚠️ 系统无 `zip` 命令，必须用 Python zipfile 模块打包：

```python
import zipfile, os
files = ["/tmp/fuzhuang-huanse/img1_xxx.png", ...]
out = "/tmp/fuzhuang-huanse/huanse_[颜色]_[N]pics.zip"
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f, os.path.basename(f))
print(f"ZIP_PATH={out}")
```

命名规则：`huanse_[颜色hex]_[总数]pics.zip`，例如 `huanse_228B22_2pics.zip`

子 agent 完成后，在结果中输出所有 ZIP 文件的绝对路径（格式：`ZIP_PATH=/tmp/...`），主 agent 从结果中提取路径。

### Step 6.2 主 agent 直接发送 ZIP（必须在主 session 执行）

⚠️ 此步骤由**主 agent 直接调用**，不得派发给子 agent：

```
linkfox_upload_file(paths=["/tmp/fuzhuang-huanse/huanse_xxx_Npics.zip", ...])
```

### Step 6.3 同时提供浏览器预览链接

在消息中列出每张图的公开 URL，供用户直接在浏览器中预览：

```
📦 换色结果已打包（共 N 张）

🔗 浏览器预览链接：
图1 🔵 #颜色：https://agent-files.linkfox.com/...
图2 🩷 #颜色：https://agent-files.linkfox.com/...
```

> **关于本地路径：** OpenClaw 运行在远程服务器上，无法直接写入用户本地路径（如 C:\Users\...）。
> 用户通过聊天窗口收到 ZIP 后，可解压到本地任意位置。

---

## 关键原则

- **图片只分析一次**：同一张图的固定信息复用，不重复分析
- **提示词紧凑**：控制在 1000 字符内
- **每色独立提交**：每个颜色单独调用一次 @AI绘图，禁止多色打包，避免视觉融合
- **Round-robin 轮询**：多色任务全部提交后，用 round-robin 方式并行轮询所有 messageId，总耗时 ≈ max(单色时间) 而非 sum
- **不臆测材质**：光泽感面料优先判断为缎面/丝绸而非皮革
- **氛围协调按需**：仅在目标色与原图色调冲突明显时添加
- **保持原图比例**：AI 生成时可能忽略比例约束，必须在下载后用 `fix_aspect_ratio.py` 做后处理裁剪（居中裁剪至原图宽高比）；提示词约束为辅助，后处理为保障
- **图片URL必须转发**：@AI绘图 返回 HTML，需提取其中图片 URL
- **换色前确认选区**：图片分析完成后必须先输出换色选区确认，等用户明确确认后再执行；自动标记同色系和配套单品，避免漏换
- **批次并行**：多图时并行派发多个子 agent，减少等待时间
- **同一轮派出**：所有执行子 agent 必须在同一轮消息中一次性全部 spawn，不得分批等待
- **重复款式免确认**：同一 session 中已确认过的款式（相同服装名+当前颜色），再次提交时跳过第三步确认直接执行
- **轮询间隔 3s**：polling 脚本 sleep 统一使用 3 秒，减少等待抖动
- **交付优先级**：linkfox_upload_file 发送 ZIP（主要）+ 浏览器公开链接（备用）
- **linkfox_upload_file 必须由主 agent 调用**：该工具绑定当前 Linkfox 对话上下文，在子 agent（隔离 session）中调用会静默失败。打包可在子 agent 中完成并报告路径，但上传必须由主 agent 直接执行。

## 参考资源

材质词库、光线词库：`references/materials.md`
