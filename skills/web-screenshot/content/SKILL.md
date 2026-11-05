---
name: web-screenshot
description: 使用 Playwright 对任意网址进行网页截图，支持全页面截图、等待动态内容加载、自定义视口大小。触发词：截图、截取网页、网页截图、screenshot、截屏。
---

# web-screenshot Skill

## 功能说明
对指定 URL 进行网页截图，截图结果保存至 `/workspace/screenshots/` 目录，并自动上传 CDN 返回链接。

## 工作流程

### 第一步：确认截图脚本存在
检查 `/workspace/screenshot.js` 是否存在。若不存在（Gateway 重启后可能被清除），需重新写入：

```javascript
// /workspace/screenshot.js
const { chromium } = require('playwright');

const EXECUTABLE_PATH = '/root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome';

async function screenshot(url, outputPath) {
  const browser = await chromium.launch({
    headless: true,
    executablePath: EXECUTABLE_PATH,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage({
    viewport: { width: 1280, height: 900, deviceScaleFactor: 1 }
  });

  try {
    console.log(`🌐 正在访问: ${url}`);
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    console.log('✅ 页面加载完成');

    await page.screenshot({
      path: outputPath,
      fullPage: false
    });
    console.log(`✅ 截图已保存: ${outputPath}`);

    const title = await page.title();
    console.log(`📄 页面标题: ${title}`);

  } finally {
    await browser.close();
  }
}

const url = process.argv[2];
const output = process.argv[3];
screenshot(url, output);
```

写入命令：
```
write 工具 → path: /workspace/screenshot.js → content: (上方代码)
```

### 第二步：确保 Playwright 环境可用
若 `/workspace/node_modules/playwright` 不存在，重新安装：
```bash
cd /workspace && npm init -y && npm install playwright
```

若 Chromium 可执行文件不存在，运行：
```bash
cd /workspace && node node_modules/playwright-core/cli.js install-deps chromium && node node_modules/playwright-core/cli.js install chromium
```

### 第三步：创建截图目录并执行截图
```bash
mkdir -p /workspace/screenshots
```

执行截图（使用 node exec 工具）：
```
command: cd /workspace && node screenshot.js "<URL>" "/workspace/screenshots/<文件名>.png"
```

**推荐视口参数：**
- PC 端：`viewport: { width: 1280, height: 900 }`
- 移动端：`viewport: { width: 375, height: 812 }`（iPhone 尺寸）

**等待策略（waitUntil）：**
- `domcontentloaded`：默认，适合静态页面
- `networkidle`：等待所有网络请求结束，适合 JS 动态渲染页面（ SPA）
- `load`：等待完整加载，适合含大量资源页面

### 第四步：上传至 CDN
使用 `upload_to_cdn` 工具上传截图：
```
file_path: /workspace/screenshots/<文件名>.png
```
返回 `cdn_url`，直接发送给用户。

## 目录规范
- 截图保存目录：`/workspace/screenshots/`
- 推荐文件命名：`<网站名>-<页面名>.png`（例：`baidu-home.png`、`wys-app-login.png`）

## 错误排查
| 错误信息 | 原因 | 解决方式 |
|---------|------|---------|
| `Executable doesn't exist` | Chromium 未下载 | 重新运行 `npx playwright install chromium` |
| `libnspr4.so: cannot open shared object` | 系统库缺失 | 运行 `node node_modules/playwright-core/cli.js install-deps chromium` |
| `Target page closed` | 浏览器异常崩溃 | 增加 `--no-sandbox` 参数或检查系统内存 |
| `timeout` | 页面加载太慢 | 增大 `timeout` 值或改用 `domcontentloaded` 策略 |

## 典型调用示例

**截取百度首页：**
```
exec: cd /workspace && node screenshot.js "https://www.baidu.com" "/workspace/screenshots/baidu-home.png"
→ upload_to_cdn: /workspace/screenshots/baidu-home.png
→ 回复用户 CDN 链接
```

**截取 SPA 应用（等待网络空闲）：**
```javascript
// 修改 screenshot.js 中的 waitUntil 为 'networkidle'
await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
```
