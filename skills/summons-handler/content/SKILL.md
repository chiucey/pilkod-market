---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 45b8a2d334de1b9868f1c2541fcee16e
    PropagateID: 45b8a2d334de1b9868f1c2541fcee16e
    ReservedCode1: 3046022100846fd4be0cbc453d8732810d22720bac384f4f92d4c2e00d3b286f89572fab60022100b5047dcf7865ad8f3f2b805c054a6a7c1c4c600dda9b1912def59ec7d0ff42b4
    ReservedCode2: 304402200e59b392783673193f4eca453138a64261164a9f09ad1e4a30012874aab38c34022010d9cb6e86b77cc3139749166a21f7320fadd14de01aaa998e67e8d40117a014
description: 法院短信链接解析、PDF下载与提醒创建技能。当用户发送法院短信或链接时：(1)解析URL参数识别案件信息；(2)用browser工具携带sdsin Token下载PDF；(3)用pymupgr提取PDF文字；(4)识别文书类型；(5)提取关键信息（案号、时间、地点等）；(6)判断文书类型——传票/出庭通知书创建飞书日历+微信提醒（提前2天），其他文书存档不创建日历；(7)PDF文件发回给用户。触发场景：收到法院短信链接、"帮我处理这个链接"、"下载法院文书"。
name: summons-handler
---

# summons-handler — 法院文书处理技能

## 完整工作流程

### Step 1：接收并解析 URL

用户发送法院短信内容，提取其中的 URL 参数：

```
https://zxfw.court.gov.cn/zxfw/#/pagesAjkj/app/wssd/index?qdbh=XXX&sdbh=XXX&sdsin=XXX
```

解析出：
- `qdbh`：签收编号
- `sdbh`：送达编号
- `sdsin`：一次性认证 Token

### Step 2：下载 PDF

使用 OpenClaw 内置 `browser` 工具：

```
browser(action=open, url="<原始URL>")
```

在 browser 会话中导航到该 URL，法院系统会通过 sdsin Token 完成自动认证。

认证成功后，在页面中找到 PDF 下载按钮或直接获取 PDF 链接。

**PDF 保存路径**：`/workspace/court_docs/<案号>_<文书类型>.pdf`

### Step 3：提取 PDF 文字

使用 `exec` 调用 pymupdf：

```python
import fitz
doc = fitz.open("/workspace/court_docs/xxx.pdf")
text = "\n".join([page.get_text() for page in doc])
```

> ⚠️ 不要使用 images_understand（OCR）来读 PDF，模型会产生幻觉。
> 必须用 pymupdf 直接提取文字。

### Step 4：识别文书类型

根据 PDF 标题/关键词判断文书类型：

| 关键词 | 文书类型 | 是否创建日历 |
|---|---|---|
| 传票 | 传票 | ✅ |
| 出庭通知 | 出庭通知书 | ✅ |
| 开庭通知 | 开庭通知书 | ✅ |
| 保全情况告知书 | 财产保全告知 | ❌ 存档 |
| 民事裁定书 | 裁定书 | ❌ 存档 |
| 调解书 | 调解书 | ❌ 存档 |
| 判决书 | 判决书 | ❌ 存档 |

### Step 5：提取关键信息

无论何种文书，提取以下字段并展示给用户确认：

| 字段 | 说明 |
|---|---|
| 案号 | 如 (2026) 粤0606民初XXX号 |
| 案由 | 买卖合同/劳动争议/民间借贷等 |
| 开庭/应到时间 | 具体日期和时间 |
| 开庭/应到地点 | 法院名称+地址 |
| 审判员/书记员 | 姓名+电话（如有） |
| 签发日期 | 文书签发时间 |
| 联系法官 | 姓名+电话 |
| 答辩/异议期限 | 特别注意的期限 |

### Step 6：发送 PDF 给用户

将 PDF 文件通过 message 工具发送给用户（WeChat）：

```
message(action=send, media="/workspace/court_docs/xxx.pdf")
```

### Step 7：创建日历（如适用）

**仅限传票/出庭通知书/开庭通知书**，其他文书仅存档。

提醒时间 = 开庭/应到时间 - 2天

使用 `openclaw cron add` 创建微信提醒：

```bash
openclaw cron add \
  --name "<案件简称> 开庭提醒" \
  --at "<开庭日期-2天>T10:00:00+08:00" \
  --channel weixin \
  --account e02491421491-im-bot \
  --to "o9cq807ihQhM4WYZ8KPeJecysM2I@im.wechat" \
  --message "📢 开庭提醒（提前2天）\n\n案号：xxx\n..."
```

飞书日历创建（如已连接飞书）：
```
wecom_mcp call schedule createEvent '{"title":"开庭提醒","start_time":"...","end_time":"..."}'
```

### Step 8：汇报结果

告知用户：
- 文书类型识别结果
- 关键信息确认（请用户核对）
- 提醒创建结果
- 存档路径

---

## 存档规则

所有处理过的文书存入：
```
/workspace/court_docs/<案号>_<文书类型>_<日期>.pdf
```

同时更新案件记录文件：
```
/workspace/memory/case_<案号>.md
```

---

## 微信用户信息（固定值）

- WeChat ID：`o9cq807ihQhM4WYZ8KPeJecysM2I@im.wechat`
- Account ID：`e02491421491-im-bot`

## 当前已知案件

- (2026) 粤0606民初16046号 — 廖丽芳 诉 刘玉娟等 民间借贷 → 续封提醒2027-03-25
- 佛南劳人仲案字〔2026〕2896号 — 杨友良诉普强金属 → 开庭2026-04-14

---

## 注意事项

- sdsin Token 有效期短，处理要及时
- PDF 必须用 pymupdf 提取文字，不使用 OCR
- 任何无法读取的文件（如需要登录的页面），明确告知用户并提供手动下载指引
- 文书类型判断拿不准时，存档不创建日历，并向用户说明
