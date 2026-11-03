// screenshot.js - 使用已安装的Chromium截图
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
      path: outputPath || '/workspace/screenshot.png',
      fullPage: false
    });
    console.log(`✅ 截图已保存: ${outputPath || '/workspace/screenshot.png'}`);

    const title = await page.title();
    console.log(`📄 页面标题: ${title}`);

  } catch (err) {
    console.error('❌ 截图失败:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
}

const url = process.argv[2] || 'https://test-api.depart.cn/wysapp/#/';
const output = process.argv[3] || '/workspace/screenshot.png';
screenshot(url, output);
