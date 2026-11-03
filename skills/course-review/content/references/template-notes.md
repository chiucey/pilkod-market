# review-template.html 定制说明

模板继承自用户上学期自己做的 `review.html`（AI 概论复习面板），保留原有骨架：
侧边栏 + 首页 + 概览 + 卡片 + 总结，localStorage 进度，导出/导入 markdown 进度报告。

## 占位符（build_panel.py 替换）

| 占位符 | 用途 |
|--------|------|
| `__TOPICS_JSON__` | 卡片数据，注入 `<script id="topics-data">` |
| `__PANEL_TITLE__` | 侧边栏标题 |
| `__PANEL_SUBTITLE__` | 侧边栏副标题 |
| `__COURSE_TITLE__` | 首页大标题 |
| `__PAGE_TITLE__` | 浏览器标签标题 |
| `__STATE_KEY__` | localStorage 键，换课必须换 |
| `__EXPORT_PREFIX__` | 导出的进度文件名前缀 |

## 相对原版新增的能力

1. **`fill` 填空型**（粉色）。`____` 自动渲染成醒目下划线空格；
   答案支持 `{answer, 常见错答, 记忆提示}` 三段式。
2. **`explain` 折叠讲解区**。答完题再点开看原理，默认收起，不干扰自测。
3. **`priority` 高频标记**。卡片头显示红色「高频」角标。
4. **答案对象支持**。原来 `answer` 只能是字符串，现在可以传对象分段渲染。
5. **自评状态回显**。切回上一张卡时，之前打的分会被高亮。
6. **导出进度新增「需要二刷的题」清单**，把评分 ≤2 的题单独列出来。
7. **公式改为构建期转换，零外部依赖**。原版引了 KaTeX CSS 却没引 JS，公式一直是裸的 LaTeX 源码；
   第一版修复时改成从 CDN 同步加载 KaTeX，结果**首屏被 265KB 远程请求阻塞**，
   实测国内网络 3~12 秒白屏。最终方案是 `latex_to_unicode.py` 在构建期把公式
   转成 Unicode + `<sub>`/`<sup>`，面板**不再有任何网络请求**。
8. **打印样式**。`Ctrl+P` 直接出纸质版（展开答案、隐藏按钮）。
9. **快捷键**：`空格` 显示答案 / `h` 提示 / `e` 展开讲解 / `1·2·3` 自评 / `←→` 翻页。

## 修掉的 bug（前两个继承自原版，第 3~6 个是工具链自伤）

### bug 1：以 `**粗体**` 开头的行被当成列表项吞掉

原版无序列表正则是 `/^[\s]*[•\-\*]\s*/`，`*` 也当项目符号，
所以 `**要点**：说明` 会被解析成列表项 `*要点**：说明`——**粗体整个丢失**。

原版内容恰好没有以 `**` 开头的行，所以一直没暴露。

**修法**：`•` 和 `-` 任意位置起行；`*` 必须后跟空格才当项目符号
（符合 CommonMark 规则）。

### bug 2：答案里有 `<` 会被 HTML 吞掉

`formatText` 原本对答案文本转义后再解析，但 `renderCard` 里
`card.answer` 为对象时（`knn-4` 那张卡）会直接把对象丢进 `formatText`，
导致渲染异常。现在统一在 `renderCard` 内先规范化 answer 类型再渲染。

### bug 3：`<sub>`/`<sup>` 被二次转义

`latex_to_unicode.py` 早期版本先插入 `<sub>` 标签、再做 HTML 转义，
结果下标变成字面量 `&lt;sub&gt;`。修法：**先转义、后生成标签**。
`formatText` 侧也加了对应的保护——转义前把 `<sub>`/`<sup>` 抽成占位符，转义后再还原。

### bug 4：转换器符号表只覆盖第3章 → 第4章 59% 的卡显示裸源码

`SYMBOLS` 缺 `∅ ⊕ Σ min max ≤ ≥ boxed frac bigl`。
eval 跑第4章时 58 张卡里 **34 张**会显示成 `\min{0.5,0.6}` 这种裸 LaTeX。
已补齐，并给 `build_panel.py` 加了硬拦截。

### bug 5：`
CF(E)` 被误认成 LaTeX 命令

课件里 `$\nCF(E)$` 的 `
` 是**真换行 + 函数名**，
通用剥离规则会把它砍成 `nCF(E)`。加了 `LOOKALIKE` 白名单。
⚠️ 排查这类问题时要**按真实字符串值统计**，不能对 `json.dumps()` 的结果 grep——
JSON 里的换行本身就序列化成 `\n`，会把整份文件误报成全是残留命令。

### bug 6：`igl` 里的 `\b` 是合法 JSON 转义

`"...1.05 \bigl["` 能过 `json.load`，但渲染成 `1.05 ␈igl[`（U+0008）。
`build_panel.py` 的 `validate()` 现在扫控制字符并直接报错。

**这三条的共同教训**：转换链上任何一步"成功返回"都不代表结果正确，
必须有独立断言。`verify_panel.js` 里 `no raw LaTeX command left in shipped data`
这类断言才是真正的防线。

## 手工修改注意

- **不要引入任何同步外部 `<script src="http...">`**。用户网络下 CDN 延迟 3~12 秒，
  会让面板白屏。要用外部库必须 `defer`，或更好——构建期转好。
- 改完 CSS/JS 后**务必重跑一遍渲染测试**，方法见 `../../../../../output/AI概论-复习包/第3章/` 的验收方式：
  用 node + 最小 DOM shim 加载 `TOPICS_JSON` 和 `<script>` 主体，断言 `formatText` 的 9 项行为 +
  自评/薄弱筛选逻辑。
- **不要引入外部 JS 依赖**，唯一允许的外部资源是 KaTeX CDN。
- **`__pycache__` 会让改过的脚本看起来没生效**。改完 `latex_to_unicode.py` 后
  先 `find . -name __pycache__ -exec rm -rf {} +`，或用 `python3 -B` 运行。
- 新增题型时同步改三处：`VALID_TYPES`（build_panel.py）、`TYPE_NAMES`/`TYPE_COLORS`（模板 JS）、
  `.type-badge.<type>` CSS 规则，以及 `references/card-schema.md`。
