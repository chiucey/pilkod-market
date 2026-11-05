# Auth Guard（所有业务命令前必须执行）

## 触发与身份边界

用户明确要求登录/连接飞书项目，或请求飞书项目/Meegle 业务时执行。普通飞书任务由 lark-task 处理。Meegle 与 lark 的授权独立，不读取、输出、复制或手工修改 token、凭据文件、浏览器数据或系统钥匙串。只通过官方 CLI 管理本次授权。

CLI 缺失先读 [Pilkod CLI 准备说明](minimax-code-cli-setup.md)。用户交互授权由用户本人完成，不能代点同意；宿主权限检查始终有效。

## 1. 确定本次 profile 与目标 host

- 用户显式 profile 优先，否则沿用 CLI 当前 profile；不要为插件另行切换默认 profile。
- 以下 Bash 示例保存 `profile_args=(--profile "$profile")`；未指定时为 `profile_args=()`。PowerShell 对应 `$profileArgs = @('--profile', $profile)` 或 `@()`，调用 `meegle.cmd @profileArgs ...`。整轮认证与业务调用复用同一参数数组。
- 用户提供项目 URL 时，先用 `meegle "${profile_args[@]}" url decode --url "$url" --format json` 获取 `host`、`url_kind`、`simple_name`、`work_item_id`；不得自行截取路径段。保存返回的 host 为本轮 `$target_host`，处理分支见 [url-kinds.md](url-kinds.md)。
- 非 URL 请求：用户明确指定 host 时保存为 `$target_host`，否则为空；不继承前一请求的临时值。

## 2. 检查登录状态及退出码

```bash
meegle "${profile_args[@]}" auth status --format json
```

同时读取退出码和 JSON 的 `authenticated`、`host`、`reason`，不要因非零退出码丢弃输出。

- exit 0 且 `authenticated=true`：通过认证，仍先做下述 host 一致性检查。
- exit 1 且明确 `no local token` / `token rejected by server`：需要授权；两者分别表示没有本地 token / 服务端拒绝，报告真实原因。
- exit 2 / `server unreachable`：网络或服务异常，认证状态未获验证。停止业务调用，报告网络错误；不强迫重新登录、不退出登录、不删凭据、不把 `authenticated=false` 误当作 token 失效。
- 其他错误或无法解析输出：报告具体错误，不猜测状态，不循环登录。

比较前将目标和返回 host 转小写、去掉域名末尾的 `.`，端口必须一致：

- 目标 host 与状态返回的已有 host 均非空但不匹配：停止，说明两个站点，要求用户选择对应 profile 或明确切换。**不得静默用 `auth login --host` 覆盖已有 profile。**
- 有已有 host：复用已有 host，即使是 `meegle.com` 或自定义域名。
- 无已有 host 但有用户显式/URL 目标：复用目标。
- 两者均无：本国内插件默认 `project.feishu.cn`，无需询问国内/海外选择。

已认证且站点匹配则进入业务步骤；明确未认证则进入 device-code。

## 3. 非 TTY device-code 授权

不要使用默认浏览器回调登录，也不要要求用户运行交互式安装向导。使用实际 CLI 支持的两阶段流程：

```bash
meegle "${profile_args[@]}" auth login --host "$host" --device-code --phase init --format json
```

将返回的 `verification_uri_complete`（有则优先）或 `verification_uri` 与 `user_code` 展示给用户。`device_code` 和 `client_id` 仅保留作本次轮询参数，不向聊天展示或落盘；不读取任何已有凭据。告知用户自行打开链接授权。

保留 init 返回的原始值，按 `interval` 等待并在 `expires_in` 有效期内有限轮询；不要忙循环或重复 init：

```bash
meegle "${profile_args[@]}" auth login --host "$host" --device-code --phase poll \
  --device-code-value "$device_code" --client-id "$client_id" --once --format json
```

`--once` 可能 exit 0 但仍返回 pending，因此必须检查 JSON `status`：只有 `ok` 才表示完成；pending 等待后重试，slow_down 增加间隔，expired/denied/error 则停止。不得把初始化成功或轮询 exit 0 当作登录成功。用户拒绝或代码过期时说明原因，不自动重开授权。网络失败先报告，不强迫重新登录。

成功后再次执行同 profile 的 `auth status --format json` 并检查 host。验证通过后告知授权成功，继续原任务，不要求用户重述需求。

## 4. 执行业务

每条业务命令复用同一 profile。URL 为 `workitem_detail` 时，先 `project search` 将 `simple_name` 转为权威 `project_key`，再 `workitem get`；其他 URL kind 按 [url-kinds.md](url-kinds.md) 处理。业务权限不足不等同于未登录，不通过重登绕过空间权限。
