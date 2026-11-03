#!/usr/bin/env node

/**
 * Playwright Simple Scraper - 简单版
 * 适用于没有反爬保护的动态网站
 */

const { chromium } = require('playwright');

const args = process.argv.slice(2);
const url = args[0];

if (!url) {
  console.error('Usage: node playwright-simple.js <URL>');
  console.error('Example: node playwright-simple.js https://example.com');
  process.exit(1);
}

const WAIT_TIME = parseInt(process.env.WAIT_TIME || '5000');

async function scrape() {
  console.log(`[Simple] Starting scrape for: ${url}`);
  
  const browser = await chromium.launch({
    headless: true
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    console.log('[Simple] Navigating to page...');
    await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Wait for dynamic content
    await page.waitForTimeout(WAIT_TIME);
    
    // Get page content
    const content = await page.content();
    const title = await page.title();
    
    console.log(`[Simple] Page title: ${title}`);
    console.log(`[Simple] Content length: ${content.length} characters`);
    
    // Save HTML if requested
    if (process.env.SAVE_HTML === 'true') {
      const fs = require('fs');
      const path = require('path');
      const filename = `page_${Date.now()}.html`;
      fs.writeFileSync(path.join('/workspace', filename), content);
      console.log(`[Simple] HTML saved to: ${filename}`);
    }
    
    // Take screenshot if requested
    if (process.env.SCREENSHOT_PATH) {
      await page.screenshot({ path: process.env.SCREENSHOT_PATH, fullPage: true });
      console.log(`[Simple] Screenshot saved to: ${process.env.SCREENSHOT_PATH}`);
    }
    
    console.log('[Simple] Scrape completed successfully!');
    
    // Return content for further processing
    return content;
    
  } catch (error) {
    console.error('[Simple] Error:', error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

scrape().catch(console.error);
