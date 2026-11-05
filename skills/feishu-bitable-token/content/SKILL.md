---
name: feishu-bitable-token
description: 让AI助手自动获取并管理飞书用户授权Token，实现多维表格的读取、写入与数据管理。全程引导配置，Token自动续期，适配任何飞书多维表格场景，零门槛接入。
---

> 通用技能，适用于任何需要读写飞书多维表格（Bitable）的 OpenClaw AI 助手。
> 用于以用户身份调用飞书开放接口，实现多维表格的读取、写入、管理等操作。
> 全程引导配置，Token 自动续期，零门槛接入。

---

## 安装说明

1. 将本文件（SKILL.md）放入 `workspace/skills/feishu-bitable-token/SKILL.md`
2. 按下方步骤创建目录结构和脚本文件
3. 完成后告知 AI 助手配置完成

---

## 首次安装配置流程（共4步）

### Step 1️⃣ 创建目录结构

在 `workspace/skills/feishu-bitable-token/` 下新建以下文件：
- `config/app.json`（配置文件）
- `run_initial.js`（首次授权脚本）
- `run_refresh.js`（自动续期脚本）
- `scripts/setup_auth.js`（授权链接生成器）

下方 Step 2~5 给出了每个文件的内容，复制粘贴保存即可。

---

### Step 2️⃣ 创建配置文件 config/app.json

前往 [飞书开放平台](https://open.feishu.cn/app) 创建企业自建应用，获取 App ID、App Secret，填入下方文件：

```json
{
  "APP_ID": "cli_你的AppID",
  "APP_SECRET": "你的AppSecret",
  "REDIRECT_URI": "https://httpbin.org/get"
}
```

> ⚠️ APP_ID、APP_SECRET、REDIRECT_URI 必须全部填写。Redirect URI 建议填 `https://httpbin.org/get`，并在飞书开放平台应用安全设置中添加一致地址。

---

### Step 3️⃣ 创建脚本：scripts/setup_auth.js

授权链接生成器，运行后输出授权地址：

```javascript
/**
 * 飞书多维表格 Token 管理 - 授权链接生成器
 * 使用方式：node scripts/setup_auth.js
 */
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '../config/app.json');
const SCOPE_DEFAULT = [
  'bitable:app:readonly',
  'base:app:read',
  'base:table:read',
  'base:record:retrieve',
  'base:record:create',
  'base:record:update',
].join(' ');

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    console.error('[错误] 配置文件不存在:', CONFIG_FILE);
    console.error('请先创建 config/app.json');
    process.exit(1);
  }
  const cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  if (!cfg.APP_ID || !cfg.REDIRECT_URI) {
    console.error('[错误] config/app.json 中缺少 APP_ID 或 REDIRECT_URI');
    process.exit(1);
  }
  return cfg;
}

function main() {
  const cfg = loadConfig();
  const params = new URLSearchParams({
    client_id: cfg.APP_ID,
    response_type: 'code',
    redirect_uri: cfg.REDIRECT_URI,
    scope: cfg.SCOPE || SCOPE_DEFAULT,
    prompt: 'consent',
  });
  const authUrl = 'https://accounts.feishu.cn/open-apis/authen/v1/authorize?' + params.toString();
  console.log('飞书授权链接生成器\n');
  console.log('App ID:', cfg.APP_ID);
  console.log('Redirect URI:', cfg.REDIRECT_URI);
  console.log('\n请在浏览器中打开以下链接，扫码登录飞书授权。');
  console.log('授权成功后，将浏览器地址栏 URL 中的 code= 后面的字符串发给女仆酱。\n');
  console.log(authUrl);
}
main();
```

---

### Step 4️⃣ 创建脚本：run_initial.js

首次授权脚本，用 code 换取 Token（只需运行一次）：

```javascript
/**
 * 飞书多维表格 Token 管理 - 首次授权脚本
 * 使用方式：node run_initial.js <code>
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '../config/app.json');
const CREDFILE = '/root/.openclaw/credentials/feishu-bitable-token.json';

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    console.error('[错误] 配置文件不存在:', CONFIG_FILE);
    process.exit(1);
  }
  const cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  if (!cfg.APP_ID || !cfg.APP_SECRET || !cfg.REDIRECT_URI) {
    console.error('[错误] config/app.json 缺少必要配置');
    process.exit(1);
  }
  return cfg;
}

function getAppToken(appId, appSecret) {
  return new Promise((ok, fail) => {
    const data = JSON.stringify({ app_id: appId, app_secret: appSecret });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/auth/v3/app_access_token/internal',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) }
    }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { ok(JSON.parse(d).app_access_token); } catch (e) { fail(e); } });
    });
    req.on('error', fail);
    req.write(data); req.end();
  });
}

function exchangeCode(appToken, code) {
  return new Promise((ok, fail) => {
    const body = JSON.stringify({ grant_type: 'authorization_code', code });
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/authen/v1/access_token',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + appToken, 'Content-Length': Buffer.byteLength(body) }
    }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { ok(JSON.parse(d)); } catch (e) { fail(e); } });
    });
    req.on('error', fail);
    req.write(body); req.end();
  });
}

async function main() {
  const cfg = loadConfig();
  const code = process.argv[2];
  if (!code) {
    console.error('用法: node run_initial.js <code>');
    console.error('1. 先运行: node scripts/setup_auth.js 获取授权链接');
    console.error('2. 浏览器授权后，把 code 发给女仆酱运行本脚本');
    process.exit(1);
  }
  const appToken = await getAppToken(cfg.APP_ID, cfg.APP_SECRET);
  const resp = await exchangeCode(appToken, code);
  if (resp.code !== 0) { console.error('[授权失败]', resp.msg); process.exit(1); }
  const cred = {
    user_access_token: resp.data.access_token,
    refresh_token: resp.data.refresh_token,
    updated_at: new Date().toISOString(),
    expires_in: resp.data.expires_in || 6900,
    app_id: cfg.APP_ID,
    app_secret: cfg.APP_SECRET,
  };
  const dir = path.dirname(CREDFILE);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(CREDFILE, JSON.stringify(cred, null, 2));
  console.log('[授权成功] Token已保存至:', CREDFILE);
}
main().catch(e => { console.error('[异常]', e.message); process.exit(1); });
```

---

### Step 5️⃣ 创建脚本：run_refresh.js

自动续期脚本，每次调飞书多维表格前自动运行：

```javascript
/**
 * 飞书多维表格 Token 管理 - 自动续期脚本
 * 使用方式：node run_refresh.js
 * 退出码：0=成功，1=需要重新授权
 */
const https = require('https');
const fs = require('fs');
const path = require('path');

const CONFIG_FILE = path.join(__dirname, '../config/app.json');
const CREDFILE = '/root/.openclaw/credentials/feishu-bitable-token.json';

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    console.error('[错误] 配置文件不存在:', CONFIG_FILE);
    process.exit(1);
  }
  const cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  if (!cfg.APP_ID || !cfg.APP_SECRET) { console.error('[错误] 配置缺失'); process.exit(1); }
  return cfg;
}

function api(hostname, pathname, method, headers, body) {
  return new Promise((ok, fail) => {
    const req = https.request({ hostname, path: pathname, method, headers }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { ok(JSON.parse(d)); } catch (e) { ok({}); } });
    });
    req.on('error', fail);
    if (body) req.write(body);
    req.end();
  });
}

async function main() {
  if (!fs.existsSync(CREDFILE)) {
    console.error('[错误] 凭证文件不存在，请先完成首次授权（run_initial.js）');
    process.exit(1);
  }
  const cfg = loadConfig();
  const cred = JSON.parse(fs.readFileSync(CREDFILE, 'utf8'));
  const elapsed = (Date.now() - new Date(cred.updated_at).getTime()) / 1000;
  const expiresIn = cred.expires_in || 6900;
  if (elapsed < expiresIn - 300) { console.log('[Token有效] 无需刷新'); return; }
  console.log('[Token过期] 正在刷新...');
  const appBody = JSON.stringify({ app_id: cfg.APP_ID, app_secret: cfg.APP_SECRET });
  const appR = await api('open.feishu.cn', '/open-apis/auth/v3/app_access_token/internal', 'POST',
    { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(appBody) }, appBody);
  const refreshBody = JSON.stringify({ grant_type: 'refresh_token', refresh_token: cred.refresh_token });
  const r = await api('open.feishu.cn', '/open-apis/authen/v1/refresh_access_token', 'POST',
    { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + appR.app_access_token, 'Content-Length': Buffer.byteLength(refreshBody) }, refreshBody);
  if (r.code !== 0) { console.error('[刷新失败]', r.msg, '\n请重新执行 Step 3~4 获取授权'); process.exit(1); }
  cred.user_access_token = r.data.access_token;
  cred.refresh_token = r.data.refresh_token;
  cred.updated_at = new Date().toISOString();
  cred.expires_in = r.data.expires_in;
  fs.writeFileSync(CREDFILE, JSON.stringify(cred, null, 2));
  console.log('[刷新成功] 凭证已更新');
}
main().catch(e => { console.error('[异常]', e.message); process.exit(1); });
```

---

## 日常使用

**首次授权后，告知女仆酱："飞书多维表格Token配置完成"**，之后所有操作均可直接说"帮我读/写飞书多维表格"。

手动续期：
```bash
node run_refresh.js   # 退出码0=成功，1=需重新授权
```

Token 有效期：
| 凭证 | 有效期 |
|------|--------|
| user_access_token | 约2小时 |
| refresh_token | 30天（每次续期自动轮换）|

---

## 常见问题

| 症状 | 解决 |
|------|------|
| 授权页面打不开 | 确认 APP_ID 与飞书开放平台一致 |
| redirect_uri 不匹配 | 确认 REDIRECT_URI 与飞书开放平台配置一致 |
| code 失效 | 重新运行 `node scripts/setup_auth.js` 获取新 code |
| Token 刷新失败 | 重新执行 Step 3~4 首次授权流程 |