# pipeline.md — 完整管线

支持两条路径：已有完整视频和从零生成。以下内容使用虚构的 **Ember & Oak 精品咖啡**作为文本示例，不包含或依赖任何示例媒体。
所有路径示意用 `$W`（work）和 `$S`（site）代替，实际执行时解析到当前任务工作区内。

```
W=<workspace>/work
S=<workspace>/site
mkdir -p "$W" "$S/assets/vid" "$S/assets/img"
cp references/scrub-engine.js "$S/scrub-engine.js"
python3 scripts/media.py ffmpeg-path   # 确认 ffmpeg 可用
```

场景序列:`field`(咖啡园) → `roastery`(烘焙) → `cafe`(门店) → `bar`(吧台) → `cup`(hero+CTA)
调色板:espresso `#4A2C2A` / cream `#F3E9DA`(bg) / caramel `#C88A5A` / sage `#8FB98A` / plum `#3A2E48`

## A. 已有完整视频

### 1. 分析，不修改源文件

```bash
python3 scripts/media.py probe <input-video>
python3 scripts/media.py contact <input-video> "$W/analysis/contact.jpg" 16
python3 scripts/media.py scene-detect <input-video> "$W/analysis/scenes" 0.28
```

先看联系表和候选场景帧，再写 `storyboard.md`。自动检测只提供候选边界；章节名称、内容意义、阅读停顿和 CTA 仍由模型根据画面与品牌故事判断。

### 2. 配置时间窗口

同一个完整视频可以被多个 section 复用。默认不切割源文件：

```js
const master = 'assets/vid/master.mp4';
sections: [
  { id:'field', source:master, videoStart:0, videoEnd:5.88, still:'assets/img/still_field.jpg' },
  { id:'roastery', source:master, videoStart:5.88, videoEnd:11.76, still:'assets/img/still_roastery.jpg' },
]
```

重要画面需要停留时，增加：

```js
holdStart: 0.42, holdEnd: 0.58, holdAt: 0.5
```

只有文件过大、移动端需要独立版本或分章预加载明显更合适时，才物理切段：

```bash
python3 scripts/media.py split <input-video> 0 5.88 "$S/assets/vid/chapter_field.mp4"
python3 scripts/media.py encode <input-video> "$S/assets/vid/master_mobile.mp4" mobile
```

### 3. 提取章节 poster

```bash
python3 scripts/media.py frame <input-video> 0 "$S/assets/img/still_field.jpg"
python3 scripts/media.py frame <input-video> 5.88 "$S/assets/img/still_roastery.jpg"
```

---

## B. 从零生成

### 1. 场景静图（image_synthesize，一次可批量）

style preamble(逐字复用):
```
Clay diorama miniature world, tilt-shift macro photography, handcrafted polymer clay and
felt materials with visible fingerprint texture, warm soft studio lighting, shallow depth
of field. COLOR PALETTE STRICTLY: espresso brown #4A2C2A, cream #F3E9DA background,
caramel #C88A5A, sage green #8FB98A, deep plum #3A2E48 accents.
```

每场景 = preamble + `SCENE: <画面>` + 构图。5 张全用 `resolution:"2K"` `aspect_ratio:"3:2"`。
生成后逐张 `read` 校验 subject 对。

> 使用当前任务工作区内可解析的 `output_file_path`，生成后检查真实文件是否落盘。

### 2. 连续飞行帧锁串联（gen_videos，串行）

只有 still_field 进管线;之后每段首帧 = 上段真实末帧。

```
# leg0 = 咖啡园推进
gen_videos([{ input_image_path:"$W/still_field.png", reference_type:"first_frame",
  duration:6, resolution:"1080P", output_file_path:"$W/leg0.mp4",
  prompt:"Continuous forward camera flight through a clay diorama miniature world, tilt-shift
  macro aesthetic, warm cinematic lighting. The camera flies forward and dives down into the
  coffee plantation terraces, gliding low over the clay coffee bushes and tiny harvesters,
  pushing forward along the dirt path toward the drying racks. Steady dolly-forward motion,
  no cuts, seamless continuous push-in, no camera shake. Palette: espresso/cream/caramel/sage/plum." }])

python3 scripts/media.py last "$W/leg0.mp4" "$W/leg0_last.png"

# leg1 = 从晾豆架推进钻进发光烘焙滚筒(首帧 = leg0 末帧)
gen_videos([{ input_image_path:"$W/leg0_last.png", reference_type:"first_frame",
  duration:6, resolution:"1080P", output_file_path:"$W/leg1.mp4",
  prompt:"Continuous forward camera flight..., keeps gliding forward over the drying racks then
  dives toward a glowing clay drum roaster where roasted beans tumble, warm orange glow.
  Steady dolly-forward, no cuts, seamless push-in, no shake. Palette: ..." }])
python3 scripts/media.py last "$W/leg1.mp4" "$W/leg1_last.png"

# leg2 = 从滚筒内部拉出 → 门店(穿门过渡)
# leg3 = 穿过店门进室内 → 吧台咖啡师拉花
# leg4 = 过 espresso 机 → 减速落定在 hero 拿铁杯特写(CTA finale)
# …每段同理:input = 上段 _last.png,prompt 引导到下一场景,末帧抽出来喂下段
```

过渡手法参考:**穿门而入**、**钻进物体(烘焙滚筒)再拉出**、**减速落定**——都是"镜头只向前"的合法运动。

### 3. 验缝（每个接缝都验）

```
python3 scripts/media.py first "$W/leg1.mp4" "$W/leg1_first.png"
python3 scripts/media.py seamdiff "$W/leg0_last.png" "$W/leg1_first.png"
# 期望: mean < 5/255, pixels>24 < 2%  → SEAM OK
# 实测参考: mean 3.25, max 83, >24=0.3%
```

### 4. 编码 + poster

```
names=(field roastery cafe bar cup)
for i in 0 1 2 3 4; do
  n=${names[$i]}
  python3 scripts/media.py encode "$W/leg$i.mp4" "$S/assets/vid/dive_$n.mp4"
  python3 scripts/media.py first  "$S/assets/vid/dive_$n.mp4" "$S/assets/img/still_$n.jpg"
done
```

## C. 组装页面

照 `index-template.html` 填 5 个 section(field→cup),`connectors:[null,null,null,null]`,
`--sw-bg:#F3E9DA`。英文文案不用 em dash。

## D. 本地验证

```bash
python3 -m http.server 8766 --bind 127.0.0.1 --directory "$S" &
SERVER_PID=$!
```

优先使用宿主提供的浏览器能力检查章节中心、边界前后、反向滚动、快速滚动、移动端和 reduced motion。

如果环境已经有 `node`，并且 Chromium 已由宿主或用户开启远程调试端口，可以额外运行：

```bash
node scripts/cdp_verify.js http://127.0.0.1:8766/index.html "$W/qa" <debug-port>
```

检查 `$W/qa/qa.json` 和截图。Skill 不负责安装或启动平台专属浏览器二进制。

## E. 部署

```
# 告知用户"公开发布"并确认后:
website_deploy(path="$S", project_name="<Brand> — Scroll World")
# curl 抽查线上 200 + CDP 抓线上首屏终检
```

---

## 收尾清理

```
kill "$SERVER_PID"
```
