# Plain-language user communication

Apply this file to every user-facing message in every stage. Internal files, state keys, code, selectors, and reviewer instructions may retain precise professional terms.

## Contents

1. [Default communication mode](#default-communication-mode)
2. [Separate internal and user-facing language](#separate-internal-and-user-facing-language)
3. [Translate decisions, not only words](#translate-decisions-not-only-words)
4. [Preferred user-facing vocabulary](#preferred-user-facing-vocabulary)
5. [Questions and choices](#questions-and-choices)
6. [Stage summaries and commands](#stage-summaries-and-commands)
7. [Allowed professional mode](#allowed-professional-mode)
8. [Before-send check](#before-send-check)

## Default communication mode

Assume the user has no design or development experience unless they explicitly demonstrate or request professional terminology.

- Reply in the user's conversation language.
- For Simplified Chinese users, use natural Simplified Chinese and familiar website examples.
- Do not make the user learn English or design vocabulary to continue.
- Keep questions short and group only related decisions.
- Lead with what the user will see, choose, or gain.
- Recommend a practical option when the user is unsure, and explain the visible consequence.

Do not use unexplained professional terms as headings, bold labels, option names, progress messages, or approval requests.

## Separate internal and user-facing language

Maintain two layers:

1. **Internal precision**: use stable stage IDs, English schema keys, filenames, rule IDs, library names, and technical terms in project state, code, specifications, and reviewer instructions.
2. **User clarity**: translate the internal decision into ordinary language before sending a message.

Never paste an internal checklist directly into chat. Rewrite it for the current user.

Do not expose an internal term merely because it appears frequently in a loaded Reference. Frequency does not make it user-friendly.

Exact commands such as `next:content` and filenames such as `docs/spec.md` may
remain unchanged. Explain what each does in ordinary language. Do not ask the
user to open or approve the internal Markdown.

## Translate decisions, not only words

Do not perform literal word replacement when the underlying choice is still too technical.

Instead of asking the user to choose a mechanism:

- describe two or three visible outcomes;
- show examples or Browser previews when useful;
- explain the main tradeoff;
- recommend one;
- let the user approve the outcome;
- let the Agent choose the implementation mechanism unless it materially affects cost, rights, performance, maintenance, or future development.

Mention a technical name only when:

- the user asks for it;
- the user supplied it;
- it affects a decision the user must make;
- it is needed in a development handoff.

When needed, explain the effect first and put the technical term in parentheses once. Continue with the plain-language expression afterward.

## Preferred user-facing vocabulary

Use the right-hand expression or a more natural project-specific sentence.

| Internal term | User-facing expression |
|---|---|
| Requirements | 了解你要做什么网站 |
| Reference | 研究同行网站和你喜欢的网站样式 |
| Sitemap | 确认网站有哪些页面以及如何进入 |
| Content | 填写网站文字和图片 |
| Layout | 确认每个页面怎么排、从上到下怎么看 |
| Visual | 确认网站整体风格和配色 |
| Hero | 首页最上方的首屏 |
| Animation | 页面动态效果 |
| Review / QA | 全站检查 |
| Handoff | 给后续开发人员的说明 |
| copy voice / voice direction | 网站文字读起来是什么感觉；网站用什么方式说话 |
| copy | 网站文字 |
| copy meaning | 文字表达的事实和意思 |
| tone | 说话感觉；文字给人的感受 |
| Section | 页面里的一个内容区块 |
| CTA | 最希望访客点击的按钮；希望访客执行的动作 |
| Site Map / information architecture | 网站页面目录和访问关系 |
| Page Template | 共用同一种结构的页面类型 |
| Listing / Detail | 列表页 / 详情页 |
| Container | 内容在屏幕中的显示宽度 |
| Grid | 分栏排列 |
| Card | 带底色、边框、圆角或阴影的独立内容块 |
| Bento | 大小不一的模块拼接排版 |
| Design Token | 全站共用的颜色、字号和间距规则 |
| visual direction | 网站整体看起来的风格 |
| Palette | 网站配色 |
| generated still mockup | 静态效果图 |
| HTML concept preview | 可以直接在浏览器查看和点击的网页方案 |
| design-system preview | 集中比较配色、字体和按钮等样式的展示页 |
| Placeholder | 临时占位图；临时占位文字 |
| focal point | 画面中最重要、最吸引视线的位置 |
| crop | 图片在不同屏幕上的裁切范围 |
| responsive | 自动适配电脑、平板和手机 |
| Breakpoint | 屏幕变窄或变宽时改变排版的位置 |
| reduced motion | 用户开启“减少动画”后显示的简化效果 |
| fallback | 图片、动画或程序失败时显示的替代内容 |
| loading state | 内容加载时先显示的画面 |
| Gate | 进入下一步前需要确认的内容 |
| Reviewer | 独立检查角色；第二次检查 |
| Git Checkpoint | 可以恢复到这里的保存点 |
| Media ID | 图片编号 |
| generation batch | 这一组要生成的图片 |
| dependency | 为实现某个效果需要加入的工具 |

Do not translate brand names, exact commands, filenames, code, CSS selectors, library names, or technical values when precision is required. Surround them with a plain-language explanation.

## Questions and choices

Ask about the user's desired result, not the internal category.

Avoid:

> 请选择 Copy Voice。

Use:

> 你希望网站文字读起来更接近哪一种感觉？我会用同一段内容展示几种写法，并推荐最适合你客户的一种。

Avoid:

> 请确认 Hero CTA、Focal Point 和 Mobile Crop。

Use:

> 请确认首页最上方的标题、主要按钮，以及手机上背景图片应该保留画面的哪一部分。

Avoid:

> Content Gate 已通过。

Use:

> 网站文字和图片已经填入页面，电脑和手机上的显示也检查完成，可以准备进入风格和配色阶段。

Do not bold an unexplained term such as **copy voice**, **CTA**, **Container**, or **Gate**.

## Stage summaries and commands

At every stage boundary:

1. describe what the user can now see;
2. list only decisions that still need the user's attention;
3. link the project review page and actual website pages;
4. describe what will stop changing after approval;
5. give the exact command in a code block;
6. explain the command in one ordinary sentence.

Do not show internal verdict names, state enums, rule IDs, or reviewer role names unless a problem requires them. Translate:

- `must-fix` as “进入下一步前必须修正”;
- `unable-to-verify` as “当前环境无法确认”;
- `skipped-by-user` as “你选择不添加这类效果”.

## Allowed professional mode

Use professional terminology more freely only when the user explicitly asks for technical detail, identifies as a designer/developer, or is reviewing the development handoff.

Even in professional mode:

- define uncommon abbreviations once;
- keep user choices outcome-oriented;
- do not use jargon to hide uncertainty.

Return to plain language when the user says they do not understand.

## Before-send check

Before every user-facing message, silently check:

- Is the response in the user's language?
- Does any English or professional term appear without a need?
- Can a non-designer understand every option without searching?
- Did I explain visible results before implementation details?
- Did I accidentally paste internal stage, reviewer, or QA wording?
- Are exact commands and filenames explained?
- Can one sentence be made simpler without losing an important decision?

Rewrite the message before sending when any answer is unsatisfactory.
