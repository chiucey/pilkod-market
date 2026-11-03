#!/usr/bin/env node

/**
 * Playwright Stealth Scraper - 反爬虫保护版
 * 适用于有反爬保护的复杂网站
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const url = args[0];

if (!url) {
  console.error('Usage: node playwright-stealth.js <URL>');
  console.error('Example: node playwright-stealth.js "https://m.discuss.com.hk/#hot"');
  process.exit(1);
}

const WAIT_TIME = parseInt(process.env.WAIT_TIME || '10000');
const HEADLESS = process.env.HEADLESS !== 'false';

async function applyStealth(page) {
  // Hide webdriver
  await page.addInitScript(() => {
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    });
  });
  
  // Add common stealth properties
  await page.addInitScript(() => {
    // Mock permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
      parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    
    // Mock plugins
    Object.defineProperty(navigator, 'plugins', {
      get: () => [1, 2, 3, 4, 5]
    });
    
    // Mock languages
    Object.defineProperty(navigator, 'languages', {
      get: () => ['zh-CN', 'zh', 'en']
    });
  });
}

async function scrape() {
  console.log(`[Stealth] Starting stealth scrape for: ${url}`);
  console.log(`[Stealth] Headless mode: ${HEADLESS}`);
  
  const browser = await chromium.launch({
    headless: HEADLESS,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage'
    ]
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
    viewport: { width: 390, height: 844 },
    locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai',
    permissions: ['geolocation', 'notifications']
  });
  
  const page = await context.newPage();
  
  // Apply stealth modifications
  await applyStealth(page);
  
  // Enable console logging from page
  page.on('console', msg => {
    if (msg.type() === 'error') {
      console.log('[Page Error]', msg.text());
    }
  });
  
  try {
    console.log('[Stealth] Navigating to page...');
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
    
    // Wait for dynamic content
    console.log(`[Stealth] Waiting ${WAIT_TIME}ms for content...`);
    await page.waitForTimeout(WAIT_TIME);
    
    // Scroll to simulate user behavior
    console.log('[Stealth] Simulating user scroll...');
    await page.evaluate(async () => {
      await new Promise(resolve => {
        let totalHeight = 0;
        const distance = 100;
        const timer = setInterval(() => {
          const scrollHeight = document.body.scrollHeight;
          window.scrollBy(0, distance);
          totalHeight += distance;
          if (totalHeight >= scrollHeight) {
            clearInterval(timer);
            resolve();
          }
        }, 100);
      });
    });
    
    // Get page content
    const content = await page.content();
    const title = await page.title();
    
    console.log(`[Stealth] Page title: ${title}`);
    console.log(`[Stealth] Content length: ${content.length} characters`);
    
    // Save HTML if requested
    if (process.env.SAVE_HTML === 'true') {
      const filename = `page_${Date.now()}.html`;
      fs.writeFileSync(path.join('/workspace', filename), content);
      console.log(`[Stealth] HTML saved to: ${filename}`);
    }
    
    // Take screenshot if requested
    if (process.env.SCREENSHOT_PATH) {
      await page.screenshot({ path: process.env.SCREENSHOT_PATH, fullPage: true });
      console.log(`[Stealth] Screenshot saved to: ${process.env.SCREENSHOT_PATH}`);
    }
    
    console.log('[Stealth] Scrape completed successfully!');
    
    return content;
    
  } catch (error) {
    console.error('[Stealth] Error:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

scrape().catch(console.error);
