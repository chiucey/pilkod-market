---
name: ui-design-system
description: |
  Apply Refactoring UI (Adam Wathan & Steve Schoger) design tactics to decide a UI's visual
  system before markup gets written — personality, hierarchy, type scale, spacing scale,
  color shades, shadows, images, polish. Use this skill whenever an interface is about to be
  created, restyled, or audited and its look is undefined or feels wrong: "帮我设计这个页面",
  "配色方案", "设计一套 UI 规范", "design tokens", "这个界面太丑 / 太挤 / 没有层次",
  "换个主题色", "统一一下按钮和间距", "帮我看看这个设计有什么问题", "让它显得更专业 /
  更有质感", "按 refactoring UI 那套来", building a dashboard / landing page / form /
  app shell, or reviewing an existing UI. Produces a token sheet plus hierarchy decisions;
  rendering is handed off to visual-page or html-presentation-generator.
  Do NOT load for: writing markup when a visual system already exists, icon or illustration
  artwork, brand naming and copywriting, or CSS bugs unrelated to design.
---

# UI Design System

判断标准来自 **《Refactoring UI》**（Adam Wathan & Steve Schoger，即 Tailwind CSS 作者，
2018）。书的宣言是 *design with tactics, not talent*——设计不是天赋，是一组具体可执行的
动作。这套 skill 把那 9 章 50 节转成了可复用的判断顺序。

核心不是"好看的样式"，是一套顺序：**先定层级和个性，再建系统，最后调数值。**绝大多数
"界面很丑"都出在顺序反了——先挑了个好看的蓝色，然后发现没东西值得被强调。

## 和原书的对应关系

`references/` 下每个文件对应原书章节，引用建议直接带上 tactic 原名，方便用户回溯：

| 本 skill | 原书章节 | 代表 tactic |
|---|---|---|
| `design-process.md` | Ch.1 从零开始 / Ch.9 持续进阶 | Start with a feature, not a layout · Don't design too much · Choose a personality · Limit your choices |
| `hierarchy.md` | Ch.2 层级就是一切 | Not all elements are equal · Size isn't everything · Emphasize by de-emphasizing · Labels are a last resort · Semantics are secondary |
| `spacing-layout.md` | Ch.3 布局与间距 | Start with too much white space · Grids are overrated · Relative sizing doesn't scale · Avoid ambiguous spacing |
| `typography.md` | Ch.4 文字设计 | Establish a type scale · Keep your line length in check · Baseline, not center · Line-height is proportional · Not every link needs a color |
| `color.md` | Ch.5 色彩的运用 | Ditch hex for HSL · You need more colors than you think · Define your shades up front · Don't let lightness kill your saturation · Greys don't have to be grey · Don't rely on color alone |
| `elevation.md` | Ch.6 营造层次感 | Emulate a light source · Shadows can have two parts · Overlap elements to create layers · Use fewer borders |
| `images.md` | Ch.7 图片的运用 | Text needs consistent contrast · Everything has an intended size · Beware user-uploaded content |
| `finishing-touches.md` | Ch.8 收尾打磨 | Supercharge the defaults · Add color with accent borders · Don't overlook empty states · Think outside the box |

**书里还有大量组件级配色方案、200+ 组件样式库、图标和字体推荐**，属于素材而非判断标准，
这个 skill 不收录——需要具体视觉参考时去看 refactoringui.com 官网。

## Reference routing

只读这次用得上的文件，别一次性全读：

| 这次要做的事 | 读 |
|---|---|
| 从零开始一个界面、定个性、建系统 | `references/design-process.md` |
| 定层级、判断谁是主角、按钮分级 | `references/hierarchy.md` |
| 配色、色阶、对比度、图表色 | `references/color.md` |
| 字号、行高、行长、字距、中文排版 | `references/typography.md` |
| 间距、容器、栅格、密度 | `references/spacing-layout.md` |
| 阴影、圆角、层次感、z-index | `references/elevation.md` |
| 配图、图上文字、图标、用户上传内容 | `references/images.md` |
| 空状态、默认样式增强、细节打磨 | `references/finishing-touches.md` |

## Inputs to collect

- **Surface**：产出是什么、在哪渲染。dashboard / 落地页 / 移动端 / 幻灯片 / 邮件。同一套
  token 在这几种载体上的密度差 2 倍以上，直接影响后面所有 scale 决策。
- **既有规范**：用户有没有品牌色 / 设计系统 / 现成项目？**有就读它，用它的值。**不要在同一
  个项目里输出第二套竞争的调色板。用户没明说时，先翻项目里的 CSS 变量、tailwind config、
  已有页面样式。
- **个性**：正式还是亲和、锐利还是柔和、张扬还是克制。这一条会传导到字体、圆角、配色、
  留白的每一个决策——不定下来，后面所有选择都是随机的。详见 `design-process.md`。
- **那件最重要的事**：这块界面上，用户第一眼必须看到 / 唯一必须能完成的动作是什么。
  答不出来就问，这是层级判断的地基。
- **密度约束**：高频数据工具 vs 营销页。这比"风格"影响更大，比"好看"更重要。

能从上下文推断的就直接推断并说明假设（用户贴了文件、描述了产品），不要为了凑齐五项卡住用户。

## Procedure

1. **先做灰度线稿，不是配色稿。**
   不选颜色、不加阴影，先靠间距、留白、布局把结构立起来。这样做能逼出层级是否真的成立：
   去掉颜色还清楚，说明层级对了；一去掉就散架，说明一直在用颜色救场。细节留到后面。

2. **定层级，用最便宜的手段。**
   写出这个界面的 3–5 个信息层级。**突出靠弱化周围，而不是把主角搞得更响**——这条反直觉
   但有效。手段顺序：留白 → 字重 → 颜色深浅 → 字号。字号是最粗的手段，留到最后。靠颜色
   区分的层级最多两三级。具体规则见 `references/hierarchy.md`。

3. **定个性，再定系统。**
   把配色、字号、间距、圆角、阴影全部定成**有限集合**（灰 8–10 档、主色 5–10 档、
   字号 8–12 档、间距 10–15 档、圆角 1 档、阴影 5 档），之后用排除法决策而不是每次重新想。
   决策速度提升来自有限集合，不来自审美。详见 `references/color.md` 的色阶推导。

4. **色彩只按 HSL 派生，临场不调色。**
   放弃 hex（`#03369E` 和 `#507DD7` 其实是同一族蓝），改 HSL 保证同一色相下改 S/L 就是
   一族色。中性色注入主色相 3–10% 饱和（"灰色不必是灰的"）。**调亮时同时提饱和度**，
   否则会调出粉扑扑的塑料感。验证方式是拿掉颜色看层级还成不成立。

5. **字号固定成阶梯，段落守住行长。**
   手刻 8–12 档，不用线性刻度（档位间视觉分不开）、不用模数比例（出小数）、不用 em
   （嵌套会累积）。行高与字号成反比，正文每行 45–75 字符——**即使容器很宽，段落也要单独
   限宽**，这是最常被忽略的一条。

6. **间距只从固定阶梯取值。**
   4px 起步，档位之间差异必须肉眼可辨（16 vs 20 是假档）。间距不够是分组不明确的唯一
   可靠解法。栅格被高估了——能用 flex/grid 的 gap 就别引入栅格系统。

7. **模拟光源，而不是加装饰。**
   亮边在上、暗影在下，凸起和凹陷是两套镜像。阴影按高度分 5 档，**低档叠两段**
   （大而弥散 + 小而锐利），最高层只留弥散那段。重叠元素制造层次通常比加阴影更有效。
   少用边框：加间距 > 换背景色 > 加阴影 > 画边框。

8. **收尾：默认样式和空状态是专业感的分水岭。**
   浏览器默认的列表、链接、引用、表格、复选框都值得改造一遍。**空状态别写"暂无数据"**，
   解释这里将来有什么 + 给一个行动入口，顺带承担新手引导。加载、错误、超长文本、深色模式
   这些非理想状态要在 token 阶段就规划，事后补成本翻好几倍。

9. **产出 token 表，落成 CSS 变量文件。**
   不要停在口头描述。这是输出契约，不是可选的附加项。

## Output contract

- **一段 CSS `:root {}` token 块**，颜色（含完整色阶）/ 字阶 / 间距 / 圆角 / 阴影 / z-index
  全部用自定义属性命名，命名要读起来像语义（`--color-accent`、`--text-secondary`），
  不要 `--blue-500`。色阶按 `50–900` 展开，因为"你需要的颜色比你以为的多"——真实界面
  需要 40–80 个预定义颜色。
- **一句层级说明**：哪个元素是主角，靠什么手段（留白 / 字重 / 颜色 / 字号）压过其他元素。
  用户需要知道 token 背后的判断，才能在改动时保住体系。
- **3–5 条针对本次界面的具体决策**，写清"因为什么所以这样"，而不是"我们用了主色蓝"。
- token 块落到一个 `.tokens.css` 文件（不要只贴在对话里，用户要能直接复制进项目）。

如果用户的请求暗示他最终想**看到**界面（"设计一个看板"、"做个页面给我看"），token 定了之后
继续用 `visual-page` 或 `html-presentation-generator` 渲染出来并交付预览图——停在 token 阶段
会让用户拿到一份没人替他落地的规范。纯规范咨询（"给我一套间距标准"、"这个配色怎么改"）
才只交 token。不要在这里自建 HTML 产出层，那两个 skill 已经覆盖了。

审阅已有界面时（"看看这个设计有什么问题"），不要重出一份 token 表——按上面 8 个文件的顺序
逐项扫，指出问题所在、为什么是问题、改成什么，并引用对应原则。

## Failure handling

- **用户已有品牌规范** → 一律以用户规范为准，本 skill 的默认阶梯让位；只在用户没定义的部分
  （比如没定次要文字的灰阶）补默认值，并说明这些是补的。
- **需求只有"好看"两个字** → 别问"你想要什么风格"，问"这块界面上最重要的一件事是什么"。
  从内容出发定层级，比从形容词出发靠谱。
- **token 落地后发现拥挤** → 回到第 2 步推层级，不要新增字号来补救。新增字号会破坏第 5 步
  建立的短字阶。
- **对比度实测不达标** → 多半是层级没拉开，不是色值选错。压深该深的、确认该浅的真的够浅，
  通常不必牺牲美观（"accessible doesn't have to mean ugly"）。
- **确实不适合套系统**（艺术化展示、实验性交互）→ 说明理由，按用户的设计走，本 skill 的
  约束在常规产品界面上才有价值，不要强套。

## Examples

Input: "帮我设计一个数据分析看板的配色和间距"
Output: 3 层层级（KPI 数字 / 图表区 / 筛选器背景），一套 `:root` token（主色取品牌蓝，
中性色注入该色相至 4% 饱和，完整色阶按 50–900 展开），5 档字阶 + 各档行高，8px 基准的
7 级间距阶梯，2 级阴影；层级说明写"KPI 靠 32px 字号 + 700 字重 + 最深文字压过图表，
图表靠 1px 边框和更浅的底色后退，主色只出现在当前选中的筛选 chip 上"。

Input: "这个按钮列表看着很乱，帮我改改"
Output: 不重出 token 表。按 hierarchy.md 分三级（主要 / 次要 / 三级操作），指出删除按钮
不该抢更多注意力而该靠确认弹窗承担风险，再给每级的具体样式。
