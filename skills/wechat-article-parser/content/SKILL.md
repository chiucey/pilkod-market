---
name: wechat-article-parser
description: 解析微信公众号文章链接，提取正文并以 Markdown 形式保存到本地。识别 mp.weixin.qq.com 链接 → 多级 fallback 抓取（web_fetch 优先 / curl 兜底）→ 清洗 HTML 噪音 → 转换为干净 Markdown → 保存为 .md 文件。触发词：公众号解析、提取公众号文章、公众号链接、公众号文章提取保存、wechat article、parse wechat、mp.weixin.qq.com、保存公众号文章。
---

# 公众号文章提取保存技能 (wechat-article-parser)

识别用户输入中的微信公众号文章链接，提取正文并保存为 Markdown 文件到本地 workspace。

## 触发场景

任何包含 `https://mp.weixin.qq.com/s/...` 链接的消息都应自动触发本技能。

**典型触发语**：
- 「用公众号解析助手处理这个链接：https://mp.weixin.qq.com/s/xxx」
- 「帮我提取这篇公众号文章：https://mp.weixin.qq.com/s/xxx」
- 「公众号文章提取保存：https://mp.weixin.qq.com/s/xxx」
- 「解析并保存这篇文章 https://mp.weixin.qq.com/s/xxx」
- 直接粘贴链接本身（Agent 应主动识别）

## 工作流程

### Step 1：识别链接
- 正则匹配 `https?://mp\.weixin\.qq\.com/s/[A-Za-z0-9_-]+`
- 非公众号链接 → 不调用本技能，礼貌告知用户

### Step 2：抓取（多级 fallback）

**第一优先**：`web_fetch` 工具（Mavis 平台级抓取，渲染能力强）
```
web_fetch(url=<链接>, prompt="返回该文章页面的完整原始 HTML（不要总结）")
```

**第二兜底**：本地 `wechat_extract.py` 脚本（curl 模式，模拟微信内置浏览器 UA）
```bash
python3 /workspace/wechat-extract/wechat_extract.py "<URL>" --save
```

**第三兜底**：直接调 curl（最末备用）
```bash
curl -sL \
  -H "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/20H75 MicroMessenger/8.0.45(0x18002e31) NetType/WIFI Language/zh_CN" \
  -H "Referer: https://mp.weixin.qq.com/" \
  --max-time 30 \
  "<URL>" > /tmp/wx.html
```

### Step 3：解析与清洗
- 提取标题（`og:title` → `<title>`）、作者、发布时间
- 定位正文节点 `#js_content`（或 `.rich_media_content`）
- 删除噪音：`<script>` / `<style>` / `<iframe>` / 公众号二维码 / 赞赏码 / 分享区
- **不保留图片**（按用户偏好）
- 标题自动清理 `_xxx_微信公众平台` 后缀
- 用 `html2text` 转为 Markdown

### Step 4：保存到本地

调用 `save_to_file(article)`，文件落地到：
```
/workspace/wechat-extract/output/<标题>.md
```

文件名规则：基于文章标题，过滤 `\\/:*?"<>|\n\r` 等非法字符，截断到 80 字符。

### Step 5：返回给用户

```
[✓] 解析并保存成功
📄 文件: /workspace/wechat-extract/output/标题.md
📏 大小: 7.0 KB
🎯 字数: 3479
✍️ 作者: 熊心依旧
📅 发布时间: 2026-08-25

[用 <deliver-assets> 块附上文件]
```

**完整 Markdown 内容**也直接展示给用户（首屏预览 + 完整正文），用户不用打开文件也能看到。

## 输出文件格式

```markdown
# {文章标题}

> **作者**: {作者}  
> **发布时间**: {ISO 时间}  
> **原文链接**: [点击查看]({URL})  
> **正文字数**: {N}

---

{Markdown 正文}
```

## 失败处理

| 情况 | 识别关键字 | 处理建议 |
|---|---|---|
| 文章已删除 | `该内容已被发布者删除` | 告知用户文章不可用，附原始链接 |
| 公众号被封 | `该公众号被屏蔽` | 告知用户并附链接 |
| 反爬挑战 | `参数错误` / `访问频次过高` / `环境异常` | 建议稍后重试，或在微信内重新复制完整链接 |
| 链接无效 | HTTP 404 / HTML < 5KB | 检查链接是否完整，提示用户重新复制 |
| 未找到正文 | 解析时找不到 `#js_content` | 自动切换到下一种抓取方案；都失败则报错并附 HTML 头部 |

**错误信息必须包含**：
1. 失败的具体环节（抓取 / 解析 / 内容不可用）
2. 原始链接（方便用户自查）
3. 下一步建议（重试 / 微信内复制 / 手动粘贴）

**禁止**：静默失败、编造内容、只说「失败了」不给原因。

## 高级用法

### 批量处理
用户一次发多个链接，循环走完整流程，每个文件独立保存。

### 自定义输出目录
```bash
python3 /workspace/wechat-extract/wechat_extract.py "<URL>" --save
# 脚本默认保存到 /workspace/wechat-extract/output/
# 如需修改，编辑脚本里的 output_dir 默认值
```

### 仅解析不保存
```bash
python3 /workspace/wechat-extract/wechat_extract.py "<URL>"
# 不加 --save 则只在终端打印 Markdown
```

## 依赖说明

- Python 3.11+ + `beautifulsoup4` + `html2text`（已预装）
- `curl`（系统自带）
- 可选：`web_fetch` 工具（Mavis 平台 Agent 内置）

## 文件位置

| 文件 | 路径 | 作用 |
|---|---|---|
| 技能定义 | `/workspace/.skills/wechat-article-parser/SKILL.md` | 自动同步到平台 |
| 解析脚本 | `/workspace/wechat-extract/wechat_extract.py` | 核心抓取+解析+保存 |
| 边界测试 | `/workspace/wechat-extract/test_edge_cases.py` | 单元测试 |
| 输出目录 | `/workspace/wechat-extract/output/` | Markdown 文件落地 |

## 调用示例

**最简调用**（直接发链接）：
> https://mp.weixin.qq.com/s/paIFjTLKi54t9nfv2CigvQ

**明确指令**：
> 帮我用公众号文章提取保存技能处理这个链接
> https://mp.weixin.qq.com/s/paIFjTLKi54t9nfv2CigvQ

**批量调用**：
> 把这几个公众号文章都解析保存：
> - https://mp.weixin.qq.com/s/abc1
> - https://mp.weixin.qq.com/s/abc2
> - https://mp.weixin.qq.com/s/abc3

Agent 会自动识别触发，按上述流程走完。
