---
name: image-to-web
description: >-
  输入一张图片（海报/插画/UI截图/照片/设计稿），生成美术风格与之"一脉相承"的网页：读图提取设计
  DNA（配色/字体/材质/氛围）→ 生成同款画风配图 → 截图与原图逐维验收。当用户说"照着这张图做网页/
  把图变成网站/风格要和图片一致/图生网页"时用。依赖读图+参考图生图+抠图+浏览器验收，纯文本 CLI 做不到。
---

# image-to-web — 图片 → 风格一脉相承的网页

> 一句话：**给一张图，产出一个"看起来是同一套美术语言"的网页。**
> 不是像素级复刻图片内容，而是继承它的**设计语言（配色 / 字体气质 / 材质 / 氛围 / 节奏）**，
> 把它铺展成一个真实、可用、干净的网页。

**适用输入**：海报 / 插画 / UI 截图 / 照片 / 设计稿 / 品牌视觉。**典型场景**：照着一张图做落地页、
把图变成网站、让网页风格和图片一致。

本 skill 融合了四套开源前端设计方法论的精华（image-to-code 的"图→分析→码"骨架、
design-taste 的三旋钮与反默认、imagegen 的反 AI-slop 清单、ui-ux-pro-max 的配色/字体库），
并在**首尾两端接上多模态视觉能力**：开头「读图拆 DNA」、结尾「截图验收相似度」；中间还用
**参考图生图 + 抠图**产出与原图同一画风的真实素材。

## 用到的 mcode 视觉工具（本 skill 的独占价值）
- **读图**：`images_understand`（多模态看图，第1步拆 DNA）——纯 CLI skill 做不到
- **生图**：`image_synthesize`（支持 `input_file_paths` 传参考图 → 生成同款画风的新图，第3步配图）
- **抠图**：`scripts/remove_bg.py`（本地 rembg，给网页做透明 PNG 素材）
- **验收**：内置 `browser`（截图成品与原图并排对比，第4步）

---

## 铁律（先读这条）

1. **读图在先，写码在后。** 没有把图片拆成设计 DNA 之前，禁止直接开写网页。图片是唯一的
   视觉真相来源，代码只是它的翻译层。
2. **继承语言，不搬内容。** 学的是配色/字体/材质/气质，不是把图里的文字、logo、具体画面
   照抄进网页。网页的文案/品牌/行业由用户或合理占位决定。
3. **🚫 绝不把原图/参考图直接放进网页。** 用户给的图 **只用于两件事**：① 第1步读图拆 DNA、
   ② 第4步验收对照。它**绝不能出现在成品里**——不许 `<img src="原图">`、不许当 CSS 背景、
   不许原样嵌入任何区块。把原图直接贴上去 = stub 偷懒 = 不合格，直接打回。网页里的每一张图，
   都必须是"读懂 DNA 后重新生成/设计"的产物。
4. **素材要设计感，不是塞整块插图。** 优先产出**可叠层的透明素材**（剪影、风格化描边图、
   图标、装饰图层、半透明纹理），让它们和背景/文字叠压出层次；**避免**每个区块甩一张塞满的
   矩形插图当占位——那是下策，显廉价。详见第 3.E。
5. **🎯 素材必须服务于它所在位置的语义（图要对题）。** 严禁"先按原图有啥生一篮子素材，再回头
   往文案栏位里硬塞"。必须**先定栏位语义、再按语义生对应素材**：文案写"灯火"就配暖光台灯，
   写"古本"就配书/书脊，写"茶"就配茶器。图不对题（灯火配了花、古本配了丝带）= 和"直贴原图"
   同级的偷懒，直接打回。素材继承的是原图的**画风**，不是原图的**物件清单**。详见第 3.E。
6. **必须截图验收。** 生成的网页一定要开内置浏览器截图，和原图并排逐维打分。"代码写完 ≠
   风格像"——不并排看过，不算完成。
7. **像不够就回炉。** 验收任一维度明显不像、或图不对题，回到对应步骤修，别糊弄过去。

---

## 四步工作流

```
第1步 读图拆 DNA   → 视觉模型深度看图，产出 style-dna（结构化）
第2步 风格库对齐   → 用 DNA 关键词查配色方案 + 字体对，补全专业设计选择
第3步 生成网页     → 按 DNA 设三旋钮，深度生成成品，全程守反 AI-slop 清单
第4步 截图验收     → 浏览器截图 → 与原图并排 → 逐维打分 → 不够像回炉
```

---

## 第 1 步：读图拆 DNA（本 skill 的独占开头）

用多模态视觉能力**深度**看用户给的图片。不要只说"这是一张蓝色的图"这种泛泛的话，
要拆到能据此写代码的颗粒度。产出下面这份 `style-dna`（写成 markdown 或 json 都行，
关键是每一项都填实）：

```yaml
style-dna:
  # —— 配色（最重要，直接决定像不像）——
  colors:
    background:  "#RRGGBB"      # 主背景色（取图里占面积最大的底色）
    surface:     "#RRGGBB"      # 卡片/面板色
    ink_primary: "#RRGGBB"      # 主文字色
    ink_muted:   "#RRGGBB"      # 次要文字色
    accent:      "#RRGGBB"      # 强调色（按钮/高亮，图里最跳的那个彩色）
    accent_2:    "#RRGGBB|none" # 第二强调色，没有就 none
    border:      "#RRGGBB"      # 描边/分隔线色
  theme: "light | dark"         # 整体明暗
  saturation: "muted | balanced | vivid"   # 饱和度基调

  # —— 字体气质 ——（不必猜出确切字体名，描述气质即可）
  type_feel: "几何无衬线 | 人文无衬线 | 现代衬线 | 复古衬线 | 圆体 | 等宽 | 手写 | 展示体"
  type_contrast: "标题与正文的字重/字号反差：弱 | 中 | 强"
  type_case: "标题是否常用全大写 / 首字母大写 / 正常"

  # —— 材质与深度 ——（决定"质感像不像"）
  radius: "sharp(0-2px) | soft(4-10px) | round(12-20px) | pill(999px)"
  shadow: "none | flat | subtle | soft-diffuse | dramatic"
  texture: "flat | grain-noise | gradient-mesh | glass-blur | paper | metal | 其它"
  border_style: "none | hairline | thick-black | 其它"

  # —— 氛围 & 构图 ——
  mood: "3-5 个形容词，如：干净/活泼/高级/野兽派/复古/温暖/冷峻/未来感"
  density: "1-10，1=极空(画廊) 10=极满(驾驶舱)"
  layout_energy: "对称规整 | 轻微错位 | 强烈非对称/编辑部"
  signature: "图里最有辨识度的一个视觉特征，如：黑粗描边+硬阴影 / 极光渐变 / 大留白衬线"
```

**读图要点**：
- **颜色一定要取具体 hex**，别写"蓝色"。这是像不像的第一决定因素。
- 抓 `signature`（招牌特征）——像不像，八成靠它。比如那张 SkillForge 卡片图的招牌
  就是"**粗黑描边 + 右下硬阴影（chunky shadow）+ 高饱和马卡龙色块 + 圆角**"，
  这套 Memphis/新野兽派语言抓住了，网页就一眼像。
- 拆完先用一句话概括：**"这张图的设计语言是 ___。"**
- 输入是照片/插画（无 UI 元素）时：只提配色+氛围+材质，radius/shadow/border 按氛围合理定，别硬编。

---

## 第 2 步：风格库对齐（补全专业设计选择）

拿第 1 步的 DNA 去参考表里找最贴的成熟方案，把"凭感觉"升级成"有依据"：
- 配色：`references/palettes.md` —— 按 mood/theme 找到贴近的成熟配色，微调到 DNA 的 hex 上。
- 字体：`references/font-pairs.md` —— 按 `type_feel` 找到匹配的字体对（标题+正文）。

原则：**参考表是为了避免踩 AI 均值坑（Inter + 紫渐变），不是覆盖 DNA。**
DNA 的 hex 和气质是主，参考表是把它们锚定到经过验证的专业组合上。
- 8 档里没有贴近的（如赛博朋克/水墨/蒸汽波），直接用 DNA 自建配色字体，别硬套一档不像的。

---

## 第 3 步：生成网页（深度生成 + 反 AI-slop）

### 3.A 先设三旋钮（继承自 design-taste）
根据 DNA 的 mood/density 定三个值，后续所有布局/动效/密度决策都受它们约束：
- **DESIGN_VARIANCE**（1 对称规整 → 10 艺术化混乱）：由 `layout_energy` 定
- **MOTION_INTENSITY**（1 静态 → 10 电影级物理动效）：干净/B2B 取低，创意/活泼取高
- **VISUAL_DENSITY**（1 画廊留白 → 10 驾驶舱密集）：直接用 DNA 的 `density`

### 3.B 网页必须继承的 DNA 映射（像不像的关键）
| DNA 项 | 落到网页 |
|---|---|
| colors 全套 hex | 直接做成 CSS 变量，全站只用这套色，不许掺其它 |
| accent | 只用在按钮/高亮/焦点，别铺满 |
| radius | 全站圆角统一到这一档 |
| shadow | 阴影风格统一（如"硬阴影"就 `4px 4px 0 #000` 那种，不是柔和阴影） |
| texture | 背景质感照做（grain/mesh/glass/paper） |
| type_feel | 选气质一致的字体对 |
| signature | **重点复刻**——招牌特征在网页 hero 和卡片上明确体现 |

### 3.C 反 AI-slop 清单（五套 skill 的共识，硬规则）
生成时严禁以下"AI 一眼假"的默认，除非 DNA 明确就是这个方向：
- ❌ Inter / Roboto / 系统默认字体当主字体
- ❌ 紫色→蓝色 "AI 渐变"、霓虹外发光
- ❌ 白底居中 hero + 深色 mesh 背景的套路
- ❌ 三个等宽特性卡片一行排
- ❌ 卡片套卡片套卡片、每个 section 套巨型圆角容器
- ❌ 假 KPI（"99.99%"、"∞ scale"）、假品牌名（Acme/Nexus/NovaCore）
- ❌ AI 文案套话（Unleash/Elevate/Seamless/Next-Gen）
- ❌ emoji 当功能图标、"SECTION 01"廉价标签、隐形按钮文字
- ❌ 6 行不换行的巨型标题（H1 控制在 2-3 行）
- ❌ **把用户原图/参考图直接当成品配图贴上去**（stub 偷懒，见铁律3）
- ❌ **每个区块甩一张塞满的矩形插图**当默认——优先透明可叠层素材（剪影/图标/图层，见 3.E）
- ❌ **生图 prompt 里写 "transparent background"**——生图模型没 alpha，会画出假棋盘格像素；
  透明要生图纯色高对比底 + rembg 抠图两道工序（见 3.E）

### 3.D hero 纪律
hero 干净、留白、H1 短而有力（5-10 词），一个主 CTA。首屏在小笔记本上要完整可读。

### 3.E 素材：生图 + 抠图，做"可叠层的高级素材"，不是塞整块插图
网页里的图片素材是相似度的关键一环——光配色字体像、配图却是随便塞的整块插图，会显廉价。
**核心原则：优先做透明、可叠层的设计化素材，让它们和背景/文字叠压出层次。**

**🚫 两条禁止（对应用户踩过的坑）：**
- 禁止把用户原图 / 参考图直接放进网页（见铁律3）。原图只作生图参考 + 验收对照。
- 禁止"每个区块甩一张塞满的矩形插图"当默认做法——那是偷懒的下策。

**✅ 素材要往这些"高级、可叠层"的方向做**（优先级从高到低；透明底都靠第②道抠图产生，不靠生图）：
1. **剪影 / 风格化描边图**：主体轮廓或线描，抠成透明后能压在色块/文字上，克制又有设计感。
2. **图标 / 符号系统**：同一画风的一组图标，统一描边/圆角，做特性区、导航、装饰。
3. **装饰图层 / 抽象元素**：从原图 DNA 提炼的几何块、纹路、光斑、笔触，半透明叠加造氛围。
4. **主视觉（hero）**：需要主图时，做成"主体抠透明 + 可与排版叠压"，而不是满屏死图。
5. **纹理 / 背景**：grain/mesh/paper 等，低透明度铺底，别喧宾夺主（整幅背景不必抠）。

**做法（透明素材 = 生图 + 抠图两道工序，缺一不可）：**

**⓪ 生图前，先列「素材清单表」——清单没过不许开生图（防止图不对题）：**
先把网页里每个要放素材的栏位/区块列出来，逐个写清"这个位置的**语义**要什么"，再据此写生图
prompt。**顺序必须是"先定语义 → 再生素材"，不是"先生一篮子 → 再硬塞"**（见铁律5）。

| 栏位/区块 | 语义要什么 | 生图 prompt 主体（带 DNA 画风） | 要透明? |
|---|---|---|---|
| 例：灯火 | 暖光台灯 | brass desk lamp, warm glow, <DNA画风> | 是 |
| 例：古本 | 古书/书脊 | stacked antique books, <DNA画风> | 是 |
| 例：茶 | 茶器 | teapot and cup, <DNA画风> | 是 |
| 例：hero 背景 | 氛围底图 | <场景>, <DNA画风> | 否 |

清单里每一行的 prompt 主体，**必须对得上该栏位的文字语义**。列完自检一遍："如果只看这张图，
能猜到它配的是哪个词吗？"猜不出 = prompt 跑偏，改了再生。

> ⚠️ **关键技术事实（必读，否则必翻车）**：`image_synthesize` **没有 alpha 通道输出能力，
> 生不出真透明背景**。若在生图 prompt 里写 "transparent background / isolated on transparent"，
> 模型只会**把灰白棋盘格当成一种图案画进像素里**——那是"画出来的假透明"，是实打实的像素，
> 不是真透明区。拿这种假棋盘格图去 rembg 抠图 = 抠一张"画着棋盘格的白底图"，结果边缘留白雾、
> 一团乱，纯属给伪命题擦屁股。
>
> **透明是 rembg 抠出来的，不是生图生出来的。** 两道工序：

- **第①道 生图 → 纯色底、干净主体**：`image_synthesize` 的 `input_file_paths` 传原图当参考，
  prompt 里：
  - ✅ 写 **"clean solid <颜色> background"（纯色底）**，主体清晰、边缘干净、居中留边距。
    **底色必须与主体拉开对比**（rembg 靠对比找边缘）：浅色/白色主体 → 配深色底（如深灰/黑）；
    深色主体 → 配浅色底（如白/浅灰）。核心是"纯色 + 高对比 + 干净边缘"，**不是死认白底**——
    白色物品配白底会糊在一起，抠不出边。
  - 🚫 **绝不写** "transparent / transparent background / isolated on transparent / PNG with alpha"
    —— 生图模型不认，只会画出假棋盘格。
  - 继承 DNA 的画风配色，只学画风不抄画面（合规 + 不山寨）。
- **第②道 抠图 → 真透明 PNG**（产生真 alpha 的唯一环节）——先自检环境（换机器/首次必做）：
  ```bash
  # ① 自检：任何 python3 都能跑，自动定位 rembg 解释器并报状态；没装会打印安装三步
  python3 scripts/remove_bg.py --check
  # ② 抠图：把上一道生成的【纯色底图】抠成透明；用它报出的 rembg 解释器路径（不是系统 python）
  <上一步报出的路径> scripts/remove_bg.py 纯色底图.png 透明.png [--model <见下表>] [--accel auto|gpu|cpu]
  ```
  **选模型**（默认 u2net 够用，特殊形状才换）：

  | --model | 定位 |
  |---|---|
  | `u2net`（默认） | 通用最快(~10s)，90% 素材够用 |
  | `isnet-general-use` | 边缘略精细的通用备选 |
  | `birefnet-general-lite` | **环/洞/C形/月牙/戒指/字母孔洞等镂空专用**(~17s)。u2net/isnet 是显著性检测，会把镂空**补全成实心**（弦月被填成满月盘），只有 birefnet 懂镂空拓扑 |

  首次抠图自动下载模型到 `~/.u2net/`（u2net~168M/birefnet-lite~224M，一次性）。rembg 的 CLI 在
  py3.12 会崩，脚本直接调 Python API 绕开。**环境/下载见文末「环境初始化」。**
  - **抠完必须验一下抠干净没有**，两种方式按能力选：
    - **① 有视觉能力（如 M3）→ 直接看抠出的透明 PNG**：弦月是不是干净 C 形？环/洞有没有被填实？
      边缘有没有留白雾？这是最准的验收，能看就看图。
    - **② 没视觉能力 / 或缩略图肉眼看不真切 → 看脚本打印的「不透明占比」兜底**：
      - 环/洞/月牙类抠出 **≥30%** = 多半被补成实心（弦月本该 ~9~13%），脚本会提示换 `birefnet-general-lite`
      - 占比 **≥85%** ≈ 几乎没抠掉背景（主体/底色对比不够，回第①道换底色）
      - "被补成实心"这种在网页缩略图上常看不出，**占比就是给这种情况兜底告警的**
  - 纯色底 + 主体与底高对比时抠得最干净；底越花、边缘越糊，抠得越差——所以第①道一定要纯色高对比底。
- **不需要透明的素材**（如整幅背景纹理、hero 底图）：直接用第①道生图产物即可，不必抠。
- **一套素材保持一致**：所有素材用同一批参考 + 同一套 prompt 基调，别一张一个风格。
- **落盘纪律（否则裂图）**：`image_synthesize` 产物常落在默认 workspace 目录，用之前先 `mv`
  回项目目录，网页里用**相对路径**引用；交付前确认图片真在项目目录、能打开。
- **兜底**：确实不需要定制素材的位置，才用 `picsum.photos/seed/<关键词>/宽/高` 占位，别留裂图。

### 3.F 技术落地
- 默认单文件静态 HTML（内联 CSS，字体走 Google Fonts / 系统字体栈），零构建、能直接开。
- 除非用户要 React/框架，否则不引入构建链。
- 生成的图片素材放项目目录、用相对路径引；实在不需要定制配图才用 picsum 占位（见 3.E）。
- 必须响应式：移动端单列、不横向滚动、`min-h-dvh` 别用 `100vh`。
- 文字/背景对比度不足（如浅灰配白）时，微调 ink 色保证可读，别死抄原图 hex 牺牲可读性。

---

## 第 4 步：截图验收相似度（本 skill 的独占结尾）

**这一步不能省。** 代码写完只是一半，必须眼见为实：

1. 本地起个静态 server（`python3 -m http.server <端口>`），或直接用内置浏览器打开文件。
2. 用**内置浏览器**打开网页，截图（首屏 + 关键 section）。
3. 把原图和网页截图**并排**看，逐维打分（每项 ✅/⚠️/❌）：
   - 配色是否一脉相承（主色调、强调色）
   - 字体气质是否一致
   - 材质/圆角/阴影是否延续
   - 招牌特征（signature）有没有体现
   - 整体氛围/密度像不像
   - **图文是否对题**：逐个素材问"它配的文字是什么？图对得上吗？"（灯火配的是台灯不是花、
     古本配的是书不是丝带）——对不上就回炉重生这张，不是换位置糊弄
4. 任一项 ❌ 或多项 ⚠️ → 回第 3 步（甚至第 1 步重新读图）修，再截图，直到过关。
5. 交付时给用户一张"原图 vs 网页"的并排对比，让用户自己验。

> viewport 注意：内置浏览器宽度由用户面板物理宽度决定，AI 改不了缩放。若截图偏窄
> （<1000px 或出现移动端单列布局），提示用户把面板拉宽后重截，别拿手机版截图验收桌面站。

---

## 完成标准（Definition of Done）
- [ ] 产出了填实的 style-dna（含具体 hex + signature）
- [ ] 网页只用 DNA 那套配色，圆角/阴影/字体气质统一
- [ ] 招牌特征在网页上明确体现
- [ ] **生图前列过「素材清单表」**（先定栏位语义→再生素材，不是先生一篮子再硬塞）
- [ ] **每张素材图文对题**（灯火=台灯不是花、古本=书不是丝带），验收时逐个核过
- [ ] **网页里没有任何一张是用户原图/参考图直贴的**（原图只作参考+验收对照）
- [ ] 素材以透明可叠层元素为主（剪影/图标/图层），不是每块塞整张矩形插图
- [ ] 透明素材走"生图纯色高对比底 → rembg 抠图"两道工序（生图 prompt 没写 transparent，无假棋盘格；底色与主体拉开对比）
- [ ] 配图用参考图生图、同款画风；需去背的已抠成透明 PNG
- [ ] 生成的素材在项目目录、相对路径引用、无裂图
- [ ] 全程无反 AI-slop 清单里的东西
- [ ] 开浏览器截图，并排对比过，逐维打分通过
- [ ] 交付时附"原图 vs 网页"对比

---

## 一个完整示范（以 SkillForge 卡片图为例）

**输入**：一张 Memphis 风格卡片列表截图（粗黑描边、右下硬阴影、马卡龙色块、圆角）。

**第1步 DNA**（节选）：
```
colors: bg #F8F6F6 / surface #FFFFFF / ink #1A1A1A / accent #FF6B35(橙) /
        accent_2 #FFD84D(黄)、#B8E4D0(薄荷)、#FFB4C6(粉) / border #000000
theme: light  saturation: vivid
type_feel: 几何无衬线 + 超粗字重  type_contrast: 强  type_case: 标题正常/标签全大写
radius: round(16px)  shadow: dramatic(硬阴影 4px 4px 0 #000)  texture: flat
mood: 活泼/大胆/复古 Memphis/高辨识  density: 5  layout_energy: 轻微错位
signature: 粗黑描边 + 右下硬阴影 + 高饱和马卡龙色块胶囊标签
```
**一句话**：这张图的设计语言是 **"新孟菲斯 / 硬阴影野兽派"**。

**第3步**：VARIANCE 8 / MOTION 5 / DENSITY 5；全站 3px 黑描边 + `4px 4px 0 #000` 硬阴影 +
16px 圆角 + 马卡龙强调色轮换；标题超粗几何无衬线；hero 一句大标题 + 一个橙色硬阴影按钮。

**第4步**：截图并排 → 配色✅ 描边阴影✅ 圆角✅ 招牌特征✅ 氛围✅ → 通过。

---

## 环境初始化（依赖与配置，换机器/首次使用看这里）

本 skill 主体是纯文本规则，**唯一的外部依赖是抠图用的 rembg**（第 3.E 用）。读图/生图/截图
都走 mcode 内置工具，无需额外装。

**rembg 一次性安装（用 uv tool，隔离环境不污染系统 python）。**

**macOS / Linux 一键闭环**（可整段复制粘贴，装完直接自检）：
```bash
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh   # 没 uv 才装
source "$HOME/.local/bin/env" 2>/dev/null || export PATH="$HOME/.local/bin:$PATH"  # ⚠️ 关键：刷新 PATH，否则下一行 uv 找不到
uv tool install rembg --with onnxruntime --with pillow                         # ⚠️ 必须带 --with：rembg 默认不装 onnxruntime，裸装会 import 崩
python3 scripts/remove_bg.py --check                                           # 自检：报解释器/依赖/加速方案，全绿即就绪
```
> **① PATH 坑（新机器必踩）**：`curl | sh` 把 uv 装进 `~/.local/bin`，但**当前终端 PATH 还没加载它**，
> 不 `source`/不重开终端就直接 `uv tool install` 会报 `command not found`。上面第 2 行就是修这个。
> **② onnxruntime 坑（新机器必踩）**：`uv tool install rembg` **默认不装 onnxruntime**（rembg 列为可选），
> 裸装后 `import rembg` 直接崩 `No module named 'onnxruntime'`。必须 `--with onnxruntime --with pillow`
> 把它们装进同一隔离环境。实测漏了必崩。

**Windows（PowerShell）**：
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"   # 装 uv（装完重开一个 PowerShell 窗口刷新 PATH）
uv tool install rembg --with onnxruntime --with pillow       # 同样必须带 --with（GPU 机器换成 onnxruntime-gpu / onnxruntime-directml）
python scripts\remove_bg.py --check
```

**验证标准**：`--check` 打印出"✅ rembg 解释器 / ✅ 依赖就绪 / auto 将使用 ..."即初始化成功。
报错就照它打印的 `INSTALL_HELP` 三步走。

**配置说明：**
- 解释器路径由脚本自动定位（内部用 `uv tool dir` 动态查，跨 macOS/Linux/Windows）；
  本机为 `~/.local/share/uv/tools/rembg/bin/python`，不必手写死。
- 模型缓存：首次抠图自动下到 `~/.u2net/`（u2net~168M / birefnet-general-lite~224M，一次性）。
- **模型从 GitHub Releases 下载，国内直连极慢**（birefnet-general 973M 实测几十 kB/s 基本下不动）。
  慢/下不动时走 HF 镜像：`HF_ENDPOINT=https://hf-mirror.com <rembg-python> remove_bg.py ...`，
  或手动下 `.onnx` 丢进 `~/.u2net/`。
- **跨端加速（`--accel` 参数，默认 auto，无需手动指定）**：脚本按平台 + 实际硬件自动选加速：
  - **Windows / Linux 有独显** → 自动走 GPU：NVIDIA=CUDA、AMD/Intel=DirectML(win)、AMD=ROCm(linux)
    （装的时候把 `--with onnxruntime` 换成 `--with onnxruntime-gpu`(NVIDIA) 或 `--with onnxruntime-directml`(win)，
    二选一、别和 CPU 版 onnxruntime 混装）
  - **Windows / Linux 无独显** → 自动 CPU
  - **macOS** → **一律 CPU**（`auto` 主动跳过 CoreML——它加载重模型会初始化死锁，卡十几分钟不报错）
  - 想强制：`--accel gpu`（无 GPU 会告警并降 CPU，不崩）/ `--accel cpu`（最稳，跨端都能跑）
  - `--check` 会打印"本机 auto 将用什么"，一眼确认。CPU 下重模型慢（birefnet-lite ~17s/张），
    能用 u2net 就别上 birefnet。
- macOS 无 `timeout` 命令；若想给重模型加超时保护，注意跨平台（用 Python 侧超时，别依赖 shell timeout）。
- 不用抠图功能时，整个 rembg 可以不装——skill 其余部分照常工作。

---

## 出处（融合来源，仅记录，不必联网）
- image-to-code（@leonxlnx / taste-skill）：图→深度分析→码 的骨架
- design-taste-frontend（@leonxlnx）：三旋钮、设计读、反默认、诚实规则
- imagegen-frontend-web（@leonxlnx）：反 AI-slop 清单、构图/背景多样性
- ui-ux-pro-max（@nextlevelbuilder）：配色方案 / 字体对 参考库
- rembg 抠图脚本：复用自 frontend-assets skill
- mcode 独占补强：多模态读图（第1步）、参考图生图 + 抠图（第3步素材）、内置浏览器截图验收（第4步）
