# content.json 结构说明

`content.json` 是这本电子版的唯一内容源。改内容只改它，然后重新 build；不要手改生成的 `index.html`。

## 骨架

```json
{
  "meta": {
    "title": "书名",
    "subtitle": "副标题",
    "author": "作者",
    "kicker": "Electronic Edition",
    "lang": "zh-CN",
    "cover": "assets/cover.jpg",
    "coverAlt": "封面图描述",
    "coverCaption": "封面图注，可留空",
    "facts": [["类别", "经管 / 人工智能"], ["出版", "某出版社"]],
    "intro": "一到两段导言，<strong> 里是允许的 HTML",
    "styleKit": false,
    "labels": {},
    "footer": "© 出版社"
  },
  "chapters": [
    { "id": "ch1", "no": "Chapter 01", "title": "章标题", "lead": "导语", "blocks": [] }
  ],
  "colophon": ["书名：书名", "作者：作者", "版本：电子可视化版"]
}
```

### meta 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `title` | 是 | 书名，进 `<title>`、封面大标题（橙黄）、侧栏品牌 |
| `subtitle` | 否 | 副标题；素材里没有就整块留空，不要替作者编 |
| `author` | 否 | 填了会自动生成 byline `著 作者` |
| `kicker` | 否 | 封面右上小字，默认 `Electronic Edition` |
| `lang` | 否 | 默认 `zh-CN` |
| `cover` | 否 | 封面图相对路径；**没有封面图就删掉这个字段**，build 会输出一个封面占位框 |
| `coverAlt` | 否 | alt 文本，verify 会查空 alt |
| `facts` | 否 | 二元数组或 `{k,v}` 对象数组，最多 5 条 |
| `intro` | 否 | 导言段落，纯文本；需要行内 `<strong>`/`<em>` 时用 `introHtml` |
| `styleKit` | 否 | `true` 时页尾注入组件样式库区块，并自动加一条目录项 |
| `labels` | 否 | 覆盖界面文案：`cover`/`styleKit`/`toggle`/`progress`/`footer`/`print`/`fsKey` |
| `footer` | 否 | 侧栏底部版权行 |

### chapter 字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 否 | 章节锚点，默认 `ch1`、`ch2`…；导航锚点依赖它 |
| `no` | 否 | 章节序号标签，默认 `Chapter 01`。用中文序号（`第一章`）还是英文（`Chapter 01`）全书统一即可 |
| `title` | 是 | 章节大标题（橙黄） |
| `lead` | 否 | 导语，橙色竖线样式 |
| `blocks` | 是 | 正文块数组，见下 |

## blocks

所有块都有 `type`。文本字段默认 HTML 转义；需要行内标签时，同名加 `Html` 后缀（`text` → `textHtml`）
或在该块上写 `"html": true`。

| type | 字段 | 对应样式 |
|---|---|---|
| `prose` | `text`、`noIndent?` | `.prose` |
| `h3` / `h4` | `text` | `.h--3` / `.h--4` |
| `pull` | `text`、`cite?` | `.pull` 引文 |
| `cards` | `items: [{n,t,d}]` | `.cards` 要点卡片 |
| `list` | `items: []`、`variant: ordered\|dot\|check` | `.list` |
| `callout` | `label`、`text`、`tone: amber\|note` | `.callout` |
| `figure` | `src`、`alt`、`caption?` | `.figure` 配图（自动 lazy-load） |
| `slot` | `label?`、`hint?` | `.slot` 待补图位 |
| `bars` | `items: [{label,value,display?}]` | `.bars` 数据条，`value` 为 0–100 |
| `timeline` | `items: [{time,title,text}]` | `.timeline` 时间轴 |
| `table` | `head: []`、`rows: [[]]` | `.tablewrap > table` |
| `tags` | `items: [{t,accent?}]` 或 `["关键词"]` | `.tags` |
| `divider` | 无 | `.divider` 菱形分隔 |

约定：

- 连续的 `prose` 会被 build 自动合并成一个段落组，中间不用插空块。
- 原文里分开的段落，写成两块 `prose`——段与段的间距就是书的呼吸。
- 未知 `type` 不会中断构建：build 会告警并把它的 `text` 当正文渲染，随后请回 `content.json` 改对。
- `figure.src` 找不到文件时 build 只告警不中断，`verify.mjs` 会报错——先补图再交付。

## 完整示例（可直接跑）

```json
{
  "meta": {
    "title": "示例书名",
    "subtitle": "副标题",
    "author": "某作者",
    "cover": "assets/cover.jpg",
    "coverAlt": "示例书名封面",
    "facts": [["类别", "示例分类"], ["出版", "某出版社"]],
    "intro": "这是一段导言，用来说明这本书讲什么、为谁而写。",
    "footer": "© 某出版社"
  },
  "chapters": [
    {
      "title": "起点",
      "lead": "一句概括本章核心主张的话。",
      "blocks": [
        { "type": "h3", "text": "小标题" },
        { "type": "prose", "text": "第一段正文，首行缩进两字。" },
        { "type": "prose", "text": "第二段正文。" },
        { "type": "pull", "text": "可被单独摘出的判断句。", "cite": "作者" },
        { "type": "cards", "items": [
          { "n": "01", "t": "要点一", "d": "一句说明。" },
          { "n": "02", "t": "要点二", "d": "一句说明。" }
        ]},
        { "type": "figure", "src": "assets/img/p012.jpg", "alt": "示意图描述", "captionHtml": "<b>图 1　说明</b>　图注正文。" },
        { "type": "table", "head": ["项目", "数值"], "rows": [["甲", "10"], ["乙", "20"]] },
        { "type": "divider" }
      ]
    }
  ],
  "colophon": ["书名：示例书名", "版本：电子可视化版"]
}
```

跑通验证：

```bash
node scripts/build.mjs /path/to/work/content.json
node scripts/verify.mjs /path/to/work/index.html
```
