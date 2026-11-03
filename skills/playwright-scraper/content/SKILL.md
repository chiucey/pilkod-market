---
name: Playwright Scraper
description: 基于 Playwright 的网页爬虫技能，支持反爬保护，可爬取复杂网站如小红书等。
---

# Playwright Scraper 🕷️

基于 Playwright 的网页爬虫，支持反爬保护，已验证成功爬取多种复杂网站。

## 功能特点

- 支持 JavaScript 渲染的动态页面
- 内置反爬虫保护（Stealth 模式）
- 支持登录后的页面爬取
- 支持截图和 HTML 保存
- 可模拟真实用户行为

## 使用方法

### 简单模式（适用于一般网站）

```bash
node /workspace/skills/playwright-scraper/scripts/playwright-simple.js <URL>
```

### Stealth 模式（适用于有反爬保护的网站）

```bash
node /workspace/skills/playwright-scraper/scripts/playwright-stealth.js <URL>
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| HEADLESS | 是否无头模式 | true |
| WAIT_TIME | 等待时间(毫秒) | 5000 |
| SCREENSHOT_PATH | 截图保存路径 | /tmp/screenshot.png |
| SAVE_HTML | 是否保存HTML | false |

## 示例

### 爬取小红书搜索结果

```bash
WAIT_TIME=10000 node /workspace/skills/playwright-scraper/scripts/playwright-stealth.js "https://www.xiaohongshu.com/search_result?keyword=待办工具"
```

### 爬取并保存截图

```bash
HEADLESS=false SCREENSHOT_PATH=/workspace/screenshot.png node /workspace/skills/playwright-scraper/scripts/playwright-stealth.js <URL>
```

## 注意事项

1. 爬取过程中请遵守网站的 robots.txt 规则
2. 不要过于频繁地请求同一网站
3. 对于需要登录的页面，可能需要配置 cookies 或手动登录
