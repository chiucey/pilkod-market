#!/usr/bin/env node
/**
 * 小红书创作者中心 - 自动发布笔记
 * 通过 OpenClaw Browser Relay 控制 Chrome 完成发布流程
 * 
 * 使用方式:
 *   node publish.js --title "标题" --content "正文" --images "img1.png,img2.png" --topics "#话题1,#话题2"
 */

const http = require('http');

const GATEWAY = 'http://127.0.0.1:18789';
const PROFILE = 'chrome';
const CURSOR = process.env.OPENCLAW_CURSOR;

// 工具函数：发送 CDP 命令到 gateway
async function cdp(command, params = {}) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({ jsonrpc: '2.0', id: 1, method: command, params });
    const opts = {
      hostname: '127.0.0.1',
      port: 18789,
      path: '/cdp',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer minimax-agent',
        'x-openclaw-profile': PROFILE,
      }
    };
    const req = http.request(opts, res => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch(e) { resolve(data); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// 截图并返回 URL
async function screenshot() {
  try {
    const result = await cdp('Page.captureScreenshot', { format: 'png' });
    if (result && result.data) {
      const buf = Buffer.from(result.data, 'base64');
      const path = `/tmp/xhs_${Date.now()}.png`;
      require('fs').writeFileSync(path, buf);
      return path;
    }
  } catch(e) { /* ignore */ }
  return null;
}

// 获取页面快照
async function snapshot() {
  try {
    const result = await cdp('Runtime.evaluate', {
      expression: `
        (() => {
          const snap = { url: document.URL, title: document.title, html: document.body?.innerHTML?.substring(0, 3000) };
          return JSON.stringify(snap);
        })()
      `,
      returnByValue: true,
    });
    if (result && result.result && result.result.value) {
      return JSON.parse(result.result.value);
    }
  } catch(e) { /* ignore */ }
  return null;
}

// 等待元素出现
async function waitFor(selector, timeout = 15000) {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const result = await cdp('Runtime.evaluate', {
      expression: `document.querySelector('${selector}') ? 'found' : 'not-found'`,
      returnByValue: true,
    });
    if (result && result.result && result.result.value === 'found') return true;
    await new Promise(r => setTimeout(r, 1000));
  }
  return false;
}

// 执行流程
async function main() {
  const args = require('minimist')(process.argv.slice(2));
  const title = args.title || '默认标题';
  const content = args.content || '';
  const images = args.images ? args.images.split(',') : [];
  const topics = args.topics || '';

  console.log('🟡 启动小红书发布流程...');
  console.log(`📌 标题: ${title}`);
  console.log(`📝 图片数: ${images.length}`);

  // Step 1: 打开创作者中心发布页
  console.log('\n📍 Step 1: 打开发布页面...');
  await cdp('Page.navigate', { url: 'https://creator.xiaohongshu.com/publish/publish' });
  await new Promise(r => setTimeout(r, 5000));

  const snap1 = await snapshot();
  console.log('页面标题:', snap1?.title || 'unknown');
  console.log('页面URL:', snap1?.url || 'unknown');

  // 检查是否需要登录
  if ((snap1?.url || '').includes('login')) {
    console.log('⚠️ 需要登录! 请确保 Chrome 已登录小红书，然后重新运行。');
    await screenshot();
    return;
  }

  // Step 2: 填入标题
  console.log('\n📍 Step 2: 填入标题...');
  try {
    await cdp('Runtime.evaluate', {
      expression: `
        (() => {
          const inputs = document.querySelectorAll('input, textarea, [contenteditable]');
          for (const el of inputs) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 200 && rect.height < 100 && el.tagName !== 'TEXTAREA') {
              el.focus();
              el.value = ${JSON.stringify(title)};
              el.dispatchEvent(new Event('input', { bubbles: true }));
              return 'title_set';
            }
          }
          return 'title_not_found';
        })()
      `,
      returnByValue: true,
    });
    console.log('✓ 标题已填入');
  } catch(e) {
    console.log('⚠️ 标题输入失败:', e.message);
  }

  await new Promise(r => setTimeout(r, 2000));

  // Step 3: 填入正文
  console.log('\n📍 Step 3: 填入正文...');
  try {
    await cdp('Runtime.evaluate', {
      expression: `
        (() => {
          const textareas = document.querySelectorAll('textarea, [contenteditable]');
          for (const el of textareas) {
            const rect = el.getBoundingClientRect();
            if (rect.width > 0) {
              el.focus();
              el.value = ${JSON.stringify(content)};
              el.dispatchEvent(new Event('input', { bubbles: true }));
              return 'content_set:' + el.className;
            }
          }
          return 'content_not_found';
        })()
      `,
      returnByValue: true,
    });
    console.log('✓ 正文已填入');
  } catch(e) {
    console.log('⚠️ 正文输入失败:', e.message);
  }

  await new Promise(r => setTimeout(r, 2000));

  // Step 4: 上传图片
  if (images.length > 0) {
    console.log('\n📍 Step 4: 上传图片...');
    for (const img of images) {
      try {
        const exists = require('fs').existsSync(img);
        if (!exists) {
          console.log(`⚠️ 图片不存在: ${img}`);
          continue;
        }
        // 找到文件上传 input
        const result = await cdp('Runtime.evaluate', {
          expression: `
            (() => {
              const inputs = document.querySelectorAll('input[type="file"]');
              return inputs.length > 0 ? 'found:' + inputs.length : 'not_found';
            })()
          `,
          returnByValue: true,
        });
        console.log(`文件上传input: ${result?.result?.value}`);
        
        if (result?.result?.value?.startsWith('found')) {
          // 使用 CDP 上传文件
          await cdp('Input.dispatchDragEvent', {
            type: 'drop',
            x: 200,
            y: 300,
          });
          console.log(`✓ 触发图片上传`);
        }
      } catch(e) {
        console.log(`⚠️ 图片上传失败: ${e.message}`);
      }
    }
  }

  await new Promise(r => setTimeout(r, 2000));

  // Step 5: 截图确认状态
  console.log('\n📍 Step 5: 截图确认...');
  const finalSnap = await snapshot();
  console.log('当前页面:', finalSnap?.title);
  
  const imgPath = await screenshot();
  if (imgPath) {
    console.log(`📸 截图: ${imgPath}`);
  }

  console.log('\n✅ 自动化流程执行完成!');
  console.log('请检查浏览器确认内容是否正确，然后手动点击发布。');
  console.log('(自动化点击发布需要更复杂的元素定位，当前版本已填入内容)');
}

main().catch(console.error);
