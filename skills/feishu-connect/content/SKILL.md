---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1acf91a77a51c6bebb17f6b0c5205edd
    PropagateID: 1acf91a77a51c6bebb17f6b0c5205edd
    ReservedCode1: 3045022100867220cfe352bdc031ace86eac322da45732a9c3a07679dd8eff19a2b940f4130220545a57d00ded6a6f8835ab744dfdc09a7292fc87234deefb0b567795bd45107c
    ReservedCode2: 3044022072d15f5766639cd098564a46b4b3d190e662689dc07135e01d7e7a31e17d006b02202011ead111bc854843c1bf279bcdfca6e47c36187a8a2e8b13adecfc7dbbbe11
description: Connect Feishu bot via direct API. Replace step 1 of feisu.md, get the link (must append from=maxclaw), poll for client_id/client_secret after user completes configuration, then proceed with step 2 and 3. Use when users ask to connect Feishu, integrate Feishu, bind Feishu bot, create Feishu bot, OpenClaw + Feishu, or similar.
name: feishu-connect
---

# Feishu Connect Skill

## 适用场景

用户要求连接飞书、绑定飞书机器人、创建飞书机器人、OpenClaw 接飞书时触发。

## 版本说明

- 本 skill 适用于云端 MaxClaw（当前版本 2026.3.11）。
- 当 OpenClaw 版本 < 2026.3.22 时，飞书插件（`@larksuite/openclaw-lark`）将自动安装 2026.3.18 版本。
- 云端 MaxClaw 默认使用 2026.3.18 版本的飞书插件。

## 最高优先级规则（必须遵守，违反即失败）

1. 给用户的链接必须拼接 `&from=maxclaw`，没有这个参数的链接是错误的。
2. 这个 skill 只替换 `feisu.md` 的第 1 步；用户回复"ok"或"配置好了"之后，不要再重复执行 `feisu.md` 的第 1 步，直接继续走 `feisu.md` 的第 2 步和第 3 步。
3. 用户回复"ok"或"配置好了"之后，禁止输出任何关于"配置权限"、"开启机器人能力"、"配置事件订阅"、"发布应用"、"管理员审批"、"权限管理"、"批量导入"的内容。

## 核心原则

- 直接走接口直连模式，不要先跑官方安装器（`npx -y @larksuite/openclaw-lark install`）。
- 这个 skill 仅用于替换 `feisu.md` 的第 1 步；拿到凭证后，后续配置和配对继续按 `feisu.md` 的第 2 步和第 3 步执行。
- 链接必须裸露返回，不要用反引号、代码块包裹，用户必须能直接点击。
- 不要自动开轮询，给链接后等用户确认再继续。
- 不要生成二维码图片。
- 不要手动卸载/禁用/删除插件，不要手动改写配置文件。

## 执行流程

### 第 1 步：接口直连，一次拿到链接

```bash
COOKIE_JAR=/tmp/feishu_cookies.txt
rm -f "$COOKIE_JAR"

# init
INIT_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST "https://accounts.feishu.cn/oauth/v1/app/registration" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=init")
echo "=== INIT ==="
echo "$INIT_RESP"

# begin
BEGIN_RESP=$(curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST "https://accounts.feishu.cn/oauth/v1/app/registration" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=begin&archetype=PersonalAgent&auth_method=client_secret&request_user_info=open_id")
echo "=== BEGIN ==="
echo "$BEGIN_RESP"
```

从 begin 返回值中提取：
- `verification_uri_complete` — 原始链接
- `device_code` — 保存下来，用户确认后 poll 用
- `user_code` — 从链接参数中提取

### 第 2 步：拼接 from=maxclaw，生成最终链接

拿到 `verification_uri_complete` 后，必须在末尾拼接 `&from=maxclaw`。

示例：
- 原始：https://open.feishu.cn/page/openclaw?user_code=XXXX-XXXX
- 最终：https://open.feishu.cn/page/openclaw?user_code=XXXX-XXXX&from=maxclaw

没有 `&from=maxclaw` 的链接是错误的，不要发给用户。

### 第 3 步：把链接直接发给用户

链接裸露返回。正确输出：

---

请在浏览器中直接打开这个链接完成飞书配置：

https://open.feishu.cn/page/openclaw?user_code=XXXX-XXXX&from=maxclaw

用户码：XXXX-XXXX

配置完成之后回来和我说一声"ok"或者"配置好了"就行。

---

禁止把链接放在反引号或代码块里。

### 第 4 步：用户回复"ok"或"配置好了"之后

先执行一次 poll：

```bash
curl -s -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
  -X POST "https://accounts.feishu.cn/oauth/v1/app/registration" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "action=poll&device_code=<之前保存的 device_code>"
```

返回 `client_id` + `client_secret` → 成功。
返回 `authorization_pending` → 告诉用户飞书侧似乎还没完成，让用户再确认。

poll 成功后：

---

说明这里已经完成了 `feisu.md` 的第 1 步替换，并拿到了后续要用的凭证：

- `client_id` 作为 `App ID`
- `client_secret` 作为 `App Secret`

然后不要回到 `feisu.md` 的第 1 步，直接继续执行：

- `feisu.md` 的第 2 步：Configure OpenClaw
- `feisu.md` 的第 3 步：Start + test

也就是说，后面继续按 `feisu.md` 去配置 OpenClaw、启动 gateway、给机器人发消息，并用配对码执行 `openclaw pairing approve feishu <CODE>`。

---

不要再输出飞书开放平台里的建应用、配权限、开事件订阅、发布应用这类第 1 步指引。

### 第 5 步：提示批量授权（可选）

机器人创建并配对完成后，提示用户可以在飞书对话中发送 `/feishu auth` 完成批量授权，便于后续 OpenClaw 通过用户身份完成消息、文档、多维表格、日历等任务。

## 禁止事项

- 给用户的链接不拼 `&from=maxclaw`
- 在用户确认后又重新执行 `feisu.md` 的第 1 步
- 输出"配置权限/开启机器人能力/配置事件订阅/发布应用/管理员审批/批量导入/权限JSON"等内容
- 先跑官方安装器（`npx -y @larksuite/openclaw-lark install`）再切直连
- 手动卸载/禁用插件
- 自动开轮询
- 生成二维码图片
- 用反引号/代码块包裹链接
- 把 `authorization_pending` 当失败

## 一句话总结

用这个 skill 替换 `feisu.md` 的第 1 步：curl 拿链接 → 拼 `&from=maxclaw` → 裸链接给用户 → 等用户说 ok → poll 拿到 `client_id/client_secret` → 继续走 `feisu.md` 的第 2 步和第 3 步 → 提示 `/feishu auth` 批量授权。
