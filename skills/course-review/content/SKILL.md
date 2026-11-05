---
name: course-review
description: |
  Turn a course's slides/notes into a three-piece exam-crash kit: a lecture handout
  (Markdown), a one-page cheat sheet (Markdown), and an interactive self-test panel
  (single-file HTML with hint/reveal/self-rating/weak-item replay). Use when the user
  says "突击" / "考前复习" / "复习资料" / "期末速成" / "刷题" about a course whose
  slides, PDF, or textbook chapters they provide — especially for courses they call
  水课, want to score well on for GPA without deep study, or need condensed before an
  exam. Triggers: "这门课要突击了", "帮我整理第3章复习资料", "生成考前复习面板",
  "make a review panel from these slides". Do NOT use for: solving a specific
  homework/exam problem the user is stuck on (answer that directly), deep research,
  or summarizing a paper the user authored.
---

# Course Review Kit

把一门课的课件变成「讲义 + 速记卡 + 自测面板」三件套。

## Inputs to collect

**开跑前必须问清，问不到的直接问用户，不要猜：**

1. **考试信息**——闭卷还是开卷？题型大致有哪些（填空/选择/简答/计算/证明/编程）？
   是否明确不划重点？占比多少？
   原因：题型直接决定卡片 schema。开卷考要重"检索"，闭卷要重"默写精度"。
2. **时间盒**——距离考试几天、每天能投入多久。
   原因：决定讲义的详略和路径分层。问不到就给三档预设并标注是预设。
3. **用户底子**——专业背景、相关前置课（离散数学？概率论？）、哪几章最虚。
   原因：决定"新概念要不要从零解释"。用户说过"这课里所有知识对新概念"
   时，讲义禁止出现"显然""容易验证"这类跳步表达。
4. **目标分数**——及格就行，还是冲高分。
   原因：及格档可以砍掉边缘知识点冲高分必须全考覆盖且细节到关键词。
5. **课件文件**——全部读完再动手，不要边读边写。
   原因：漏掉的章节会直接变成漏掉的考点。

**如果 `references/courses/<课程>.md` 存在，先读它**——那是上一轮沉淀的考点地图，
不要重新分析一遍课件。改模板前读 `references/template-notes.md`（记录了模板的全部定制点和已修 bug）。

## Procedure

### 1. 抽考点地图（先建索引，不写内容）

用 `pdftotext -layout` 逐个课件转文本，再抽取每页首行得到「页码 → 标题」索引。
先通读这个索引判断章节结构，**再回去读细节页**。

理由：255 页的 PPT 直接读会漏；先建索引能看清哪些页是"章节封面/目录"（可跳过）、
哪些是"例题"（要出计算卡）、哪些是"定义"（要出填空+概念卡）。

产出：一份 `考点地图.md`，列出每章的节号、页码范围、题型预判、高频点标记。

### 2. 判题型 → 切卡片

对每个考点问一句：**它最可能以什么形式考？** 然后按 `references/card-schema.md`
选 type。判错题型的代价是卡片白做——比如把"1975 年肖特里菲提出 C-F 模型"
做成概念题，学生读懂但填空照样写错年份。

**写卡片时守住三条**：
- 题面不泄漏答案（写完自检：只读题面能答上来吗）
- 填空卡必须写 `常见错答`——写错在哪比写对更值钱
- 新概念在 `explain` 里先大白话再术语，不假设任何前置知识

### 3. 写讲义和速记卡

结构固定，照 `references/lecture-spec.md` 走。要点：
- 讲义 = 输入。讲清"为什么长这样"，不是复述定义。
- 速记卡 = 兜底。每章末尾必须有「如果只能背 10 条」。
- 讲义开头写时间盒路径，**落到具体节号**，不许写"重点看前三节"。

### 4. 构建 HTML 面板

**一条命令搞定**——`build_panel.py` 内部会先跑公式转换再注入，
所以不存在"忘了转换"这种静默失败：

```bash
python3 .skills/course-review/scripts/build_panel.py topics.json -o 复习面板.html \
  --title "AI 概论" --subtitle "第3章 · 确定性推理" --course "人工智能概论 · 第3章 确定性推理方法" \
  --state-key ai-intro-ch3-v1 --export-prefix "AI概论第3章复习进度_"
```

**为什么不挂 KaTeX CDN**：实测国内到 jsdelivr 是 2.8~12 秒，同步 `<script src>` 会
**阻塞首屏**，用户看到的是白屏不是慢。正确解法是构建期转 Unicode，面板**零外部依赖**。

**卡片里直接写 Unicode 优先于写 LaTeX**（`→ ¬ ∧ ∨ ∅ ⊕ ≤ ≥ Σ`，算子写 `min`/`max`）。
写 LaTeX 也能过，但每多一个命令就多一次翻车——eval 跑第 4 章时 58 张卡里
**34 张（59%）因为转换器不认 `\varnothing \max \sum \boxed \frac` 而显示成裸源码**。
`build_panel.py` 现在会拦住这类情况：残留 LaTeX 命令、残留 `$`、或控制字符（`\bigl` 里的
`\b` 是合法 JSON 转义，会变成 U+0008 显示成 `1.05 igl[`）都会直接报错。

`build_panel.py` 会校验 schema（必填字段、type 枚举、id 唯一、difficulty 范围、
填空卡必须含 `____`），校验不过直接报错退出。**不要为了绕过校验去改卡片**——
校验失败说明卡片本身有问题。

### 5. 验证（不要跳过）

跑通构建 ≠ 能用。必须跑渲染测试：

```bash
node verify_panel.js                       # 面板行为（与面板同目录）
python3 -B .skills/course-review/scripts/test_pipeline.py   # 转换链 + 构建守卫
```

断言要覆盖四类：**渲染**（粗体/列表/转义/上下标）、**数据**（无残留 `$` 或 `\to`）、
**自包含**（零 `src="http"`）、**性能**（首屏渲染 < 50ms）。

`test_pipeline.py` 是**回归测试**，每个 case 都对应一个真实翻过车的地方
（`\nCF` 误判、`\bigl` 控制字符、嵌套 `\boxed`、全角逗号、填空被下标正则吃掉）。
**改转换器或校验器后必须跑它**——eval 证明这些坑会原样复现。

⚠️ 改完 `.py` 先清 `__pycache__`（或加 `-B`），否则会看到"改了没生效"的假象。

构建后自己再抽查 3 张卡的转换结果——转换器容易把 `LIKE(x,y)` 的逗号变全角、
或把 `<sub>` 二次转义成 `&lt;sub&gt;`，这类问题断言不一定能全兜住。

### 6. 交付前自查

- 三件套一致性（见 `lecture-spec.md` 第 4 节）：讲义小节 ↔ 卡片 ↔ 速记卡逐条对得上
- HTML **零外部请求**（`grep -c 'src="http'` 应为 0）
- 讲义开头的时间盒路径是三档预设且已标注「待确认」
- 报告里说清楚：**多少张卡、覆盖几章、哪几章最密、时间盒怎么分配**
- 有没有 skill 跑不动的环节（公式渲染失败、模板 bug）→ 补进 `references/courses/<课程>.md`

## Output contract

```
<课程名>-复习包/
├── 考点地图.md            # 章节索引 + 高频点标记
├── 讲义-<章节>.md         # 每章一份
├── 速记卡-<章节>.md       # 每章一份
├── 模拟卷-<章节>.md       # 按用户给的题型组卷 + 按点给分参考答案 ❗
├── topics.json            # 卡片源数据（构建用，保留以便改卡重出）
├── verify_panel.js        # 渲染测试（构建用）
└── 复习面板.html          # 自包含单文件，双击即用
```

**HTML 必须零外部依赖**：`grep -c 'src="http' 复习面板.html` 必须为 0。
任何同步远程 `<script>` 都会让面板在国内网络白屏 3~12 秒。

**模拟卷不可省**（eval 实测的最大缺口）：面板里的卡片是**单点自测**，
适合记忆保持，但它**不像一张卷子**。用户告诉过我们考试是填空/选择/大题/计算，
就必须给一份**按这些题型组卷、按点给分**的模拟卷——这是"冲绩点"最直接对应的产物。

**不要维护进度文件**——面板用 localStorage 自带，导出/导入走 markdown。

## Failure handling

- **面板打开慢/白屏**：先查有没有同步 `<script src="http...">`——
  远程 CDN 在用户网络下可能 3~12 秒，足够让人以为坏了。正确解法是构建期转 Unicode，
  不是换 CDN。
- **课件是扫描件/图片型 PDF**：`pdftotext` 抽不出文本 → 加载 `pdf` skill 做 OCR，
  别拿空文本硬编考点。
- **公式抽出来是乱码**（课件里公式是图片或特殊字体）：转成 Unicode 记法
  （`¬∧∨→⊆∧min/max`）而不是放弃该考点，这类考点通常正是计算题来源。
- **用户中途改需求**（比如突然说要开卷）：停下重判题型，别在旧 schema 上打补丁。
- **课件自己前后打架**（例：第4章 P34 写 $K=1-\sum$、P40 写 $K=\frac{1}{1-\sum}$，
  是两个不同的量）：**讲义/卡片/速记卡三处都并列写出两种写法并标注各自页码出处，
  不要替老师"改对"**。考卷按哪份给分不可预测，学生得自己认得出这是两种定义。
- **章节太多一次做不完**：先做最难的一章给用户验收风格，确认后再批量。
  理由：风格不对 × 4 章 = 4 份废稿，先花一章的成本换确定性。
- **知识点与用户给的资料对不上**（教材版本差异）：以用户课件为准，差异处在讲义里
  标注一句，不擅自用别的版本覆盖。

## Examples

**Input**：用户丢来 4 份 AI 导论 PDF，说"这门课要突击了，全考不划重点，题型有填空选择大题，
可能有点简单计算；期末冲高分；我AI专业在学离散但这门课符号不学；离考试还有两个月，
先把资料做出来"。

**关键动作**：
1. 问时间盒 → 用户说还没定 → 给三档预设并标注
2. `pdftotext` 四份课件，建页码索引，发现是"确定性推理"章最难且计算最密
3. 先做第 3 章：讲义（自然演绎→子句集→归结原理→归结反演 6 节）+ 速记卡 + 约 25 张卡
4. `build_panel.py` 生成 HTML，浏览器验证
5. 交付并说明"这章计算密度最高，建议先刷它"

**Output**：三件套 + 明确的复习顺序建议。
