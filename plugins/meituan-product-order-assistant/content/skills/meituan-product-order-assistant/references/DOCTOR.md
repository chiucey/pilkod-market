# 美团商品导购下单 Skill 诊断手册

仅在用户明确说「导购诊断」「导购排查」或「meituan-product-order-assistant doctor」时执行。诊断过程不得展示完整 Token，不得自动领券、下单或清除凭证。

## 诊断顺序

严格按 A1 → A7 执行；某一步失败时记录结果，并继续执行仍然安全且可行的后续检查。

### A1 定位并校验脚本

将当前 skill 根目录记为 `SKILL_DIR`：

```bash
RUN_JS="$SKILL_DIR/scripts/run.js"
node --check "$RUN_JS"
node "$RUN_JS" init
```

从 `init` 返回 JSON 中记录：

- `skill_dir` → skill 根目录
- `data_dir` → Minimax 凭证和缓存目录
- `ok: true` → Node.js、Python 和内置 pt-passport 均已就绪
- `NPM_NOT_FOUND`、`TGZ_NOT_FOUND`、`INSTALL_FAILED` → 按错误名报告依赖问题

### A2 校验固定配置

确认以下三项完全一致：

- `scripts/config.json` 的 `aiScene`：`7838d76df26da10771f3406435dbaceb`
- 领券路径：`/fulishemini/couponActivity/sendCouponMinimax`
- `scripts/run.js` 中 `CLIENT_SOURCE`：`minimax`

还应确认二维码、领券、热词、搜索、近期位置、地址解析和下单请求都使用同一个 `CLIENT_SOURCE` 常量，并且没有其他宿主的路径、文案或来源标识。

### A3 检查登录状态

```bash
node "$RUN_JS" get-token
```

只向用户报告分类结果，不展示 `token` 字段：

- `ok: true` → Token 缓存有效
- `ok: false, error: NO_TOKEN` → 未登录或 Token 已过期，需要重新扫码登录
- `PT_PASSPORT_NOT_INSTALLED` → 重新执行 `init`

如用户明确要求重新登录，再按 SKILL.md 的 Step 1 执行 `auth-get-code` → `qrcode` → `auth-poll-token`。诊断本身不得擅自发起扫码会话。

### A4 检查设备标识

```bash
node "$RUN_JS" get-device-token
```

- `ok: true` 且有 `device_token` → 设备标识正常；报告时仅显示前 8 位加 `****`
- `DEVICE_TOKEN_FAILED` → 报告 `data_dir` 的可写性或 JSON 格式问题

凭证目录预期包含：

- `device.json`：设备标识
- `pt_passport_auth.json`：pt-passport 登录凭证
- `today_coupons_cache.json`：当天领券缓存，首次领券前可能不存在

### A5 检查接口连通性

仅做不会产生业务状态的 HEAD 检查：

```bash
curl -sS -o /dev/null -w "%{http_code}" -I --max-time 10 "https://media.meituan.com/fulishemini/couponActivity/sendCouponMinimax"
```

判断：

- `403` → 请求可能在网关或风控层被拦截
- `405` → 服务可达，HEAD 方法不被业务接口接受，属于预期现象
- `000` → DNS、TLS、代理或网络超时
- 其他状态 → 原样记录并结合日志判断

不得为了诊断调用 `node "$RUN_JS" issue`，因为该命令会实际领取优惠券。

### A6 检查发券日志

日志目录为系统临时目录下的 `meituan-product-order-assistant/issue.log`。

```bash
python3 "$SKILL_DIR/scripts/diag_issue_log.py"
```

重点检查：

- `request.url` 是否以 `sendCouponMinimax` 结尾
- `request.aiScene` 是否为指定埋点
- `response.http_status` 是否为 403、429、5xx
- `result.code` 是否为 200、401、509、50200、9999

不得把日志中的完整 Token 返回给用户。

### A7 静态适配审计

检查 skill 内文本和脚本：

```bash
grep -RniE "c[a]tpaw|c[a]tdesk|w[o]rkbuddy|coupon-fusion-w[o]rkbuddy|meituan-c[a]tpaw" "$SKILL_DIR" --exclude-dir=node_modules
```

预期无输出。若有输出，说明仍残留其他宿主的路径、文案或 client source。

## 诊断报告模板

```text
【美团商品导购下单 Skill 诊断报告】

- 环境：Node.js / Python / 内置 pt-passport [正常或异常]
- 固定配置：aiScene / sendCouponMinimax / clientSource=minimax [正常或异常]
- 登录：[有效 / 未登录 / 已过期 / 组件异常]
- 设备标识：[正常 / 异常]
- 网络：HEAD HTTP [状态码和判断]
- 发券日志：[无日志 / 最新状态摘要]
- 宿主残留：[无 / 列出文件与行号]

结论：[最可能原因]
建议：[下一步操作]
```

## 安全限制

- 不输出完整 user_token、device_token、登录链接中的授权码或 pt-passport 缓存内容。
- 不通过命令行参数传递 Token。
- 不因诊断自动领券、下单、退出登录或清除设备标识。
- 只有用户明确要求登录时才发起扫码登录会话。
