#!/usr/bin/env node
/**
 * Douyin Browser Automation with QR Login
 *
 * This script provides browser-based Douyin access with QR code login.
 *
 * Usage:
 *   node douyin-browser.js [command] [args]
 *
 * Commands:
 *   login        - Open browser, get QR code, wait for login
 *   search       - Search for videos (requires login first)
 *   browse       - Browse video page and extract info
 *   trending     - Get trending videos
 *   user         - Get user profile info
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const { URL } = require('url');

// Configuration
const CONFIG = {
    douyinUrl: 'https://www.douyin.com',
    loginUrl: 'https://www.douyin.com/login',
    userDataDir: path.join(__dirname, '../data'),
    qrCodeDir: path.join(__dirname, '../data/qrcodes'),
    sessionFile: path.join(__dirname, '../data/session.json'),
    timeout: 120000, // 2 minutes for QR scan
    headless: false // Must be false for QR code visibility
};

// Ensure directories exist
function ensureDirs() {
    [CONFIG.userDataDir, CONFIG.qrCodeDir].forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
    });
}

/**
 * Download image from URL and save to file
 */
async function downloadImage(url, filePath) {
    return new Promise((resolve, reject) => {
        const protocol = url.startsWith('https') ? https : http;
        protocol.get(url, (response) => {
            if (response.statusCode === 301 || response.statusCode === 302) {
                return downloadImage(response.headers.location, filePath).then(resolve).catch(reject);
            }
            const file = fs.createWriteStream(filePath);
            response.pipe(file);
            file.on('finish', () => {
                file.close();
                resolve(filePath);
            });
        }).on('error', reject);
    });
}

/**
 * Convert QR code URL to base64 image data
 */
async function getQRCodeBase64(page, selector) {
    try {
        // Wait for QR code to appear
        await page.waitForSelector(selector, { timeout: 10000 });

        // Get QR code image
        const qrCode = await page.locator(selector).first();
        const imgSrc = await qrCode.getAttribute('src');

        if (!imgSrc) {
            throw new Error('QR code image not found');
        }

        // If it's a data URL, return as is
        if (imgSrc.startsWith('data:')) {
            return imgSrc;
        }

        // Download and convert to base64
        const qrPath = path.join(CONFIG.qrCodeDir, `qr_${Date.now()}.png`);
        await downloadImage(imgSrc, qrPath);
        const imgBuffer = fs.readFileSync(qrPath);
        return imgBuffer.toString('base64');
    } catch (error) {
        throw new Error(`Failed to get QR code: ${error.message}`);
    }
}

/**
 * Check if login is successful by looking for user elements
 */
async function checkLoginSuccess(page) {
    try {
        // Look for common logged-in elements
        const indicators = [
            'a[href*="/user/"]',
            '[class*="avatar"]',
            '[class*="profile"]',
            '[class*="nickname"]',
            'img[class*="author"]'
        ];

        for (const selector of indicators) {
            const element = await page.$(selector);
            if (element) {
                return true;
            }
        }

        // Check URL for login redirect
        const url = page.url();
        if (!url.includes('/login')) {
            return true;
        }

        return false;
    } catch {
        return false;
    }
}

/**
 * Launch browser and perform QR login
 */
async function performLogin() {
    console.log('🚀 Launching browser for Douyin login...');

    ensureDirs();

    const browser = await chromium.launch({
        headless: CONFIG.headless,
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    });

    const page = await context.newPage();

    try {
        console.log('📱 Opening Douyin login page...');
        await page.goto(CONFIG.loginUrl, { waitUntil: 'networkidle', timeout: 30000 });

        // Wait for QR code to load
        await page.waitForTimeout(2000);

        // Try multiple QR code selectors (Douyin may change them)
        const qrSelectors = [
            '.login-qrcode img',
            'img[class*="qrcode"]',
            'img[class*="qr-code"]',
            '[class*="qrcode"] img',
            '[class*="qr-code"] img',
            '.qrcode-container img',
            'img[alt*="qr"]'
        ];

        let qrDataUrl = null;
        for (const selector of qrSelectors) {
            try {
                qrDataUrl = await getQRCodeBase64(page, selector);
                if (qrDataUrl) {
                    console.log(`✅ QR code found with selector: ${selector}`);
                    break;
                }
            } catch (e) {
                console.log(`  Trying selector: ${selector}`);
            }
        }

        if (!qrDataUrl) {
            // Try to get any image that might be the QR code
            const images = await page.$$eval('img', imgs =>
                imgs.map(img => ({ src: img.src, alt: img.alt, class: img.className }))
            );
            console.log('Available images:', JSON.stringify(images, null, 2));
            throw new Error('Could not find QR code image');
        }

        // Save QR code
        const qrFilePath = path.join(CONFIG.qrCodeDir, `douyin_qr_${Date.now()}.png`);
        const qrBuffer = Buffer.from(qrDataUrl.split(',')[1] || qrDataUrl, 'base64');
        fs.writeFileSync(qrFilePath, qrBuffer);

        console.log('='.repeat(60));
        console.log('📱 QR CODE GENERATED - PLEASE SCAN WITH DOUYIN APP');
        console.log('='.repeat(60));
        console.log(`QR Code saved to: ${qrFilePath}`);
        console.log('');
        console.log('Instructions:');
        console.log('1. Open Douyin app on your phone');
        console.log('2. Go to "Me" tab → Tap the scan icon');
        console.log('3. Scan the QR code above');
        console.log('');
        console.log('⏳ Waiting for login (timeout: 2 minutes)...');
        console.log('='.repeat(60));

        // Save QR code info
        const qrInfo = {
            qrFile: qrFilePath,
            generatedAt: new Date().toISOString(),
            status: 'pending'
        };
        fs.writeFileSync(
            path.join(CONFIG.qrCodeDir, 'qr_info.json'),
            JSON.stringify(qrInfo, null, 2)
        );

        // Wait for login with polling
        const startTime = Date.now();
        while (Date.now() - startTime < CONFIG.timeout) {
            await page.waitForTimeout(2000);

            if (await checkLoginSuccess(page)) {
                console.log('');
                console.log('🎉 LOGIN SUCCESSFUL!');

                // Save session cookies
                const cookies = await context.cookies();
                const sessionData = {
                    cookies: cookies,
                    loginTime: new Date().toISOString(),
                    userAgent: await context.options.userAgent
                };
                fs.writeFileSync(CONFIG.sessionFile, JSON.stringify(sessionData, null, 2));
                console.log(`Session saved to: ${CONFIG.sessionFile}`);

                qrInfo.status = 'success';
                fs.writeFileSync(
                    path.join(CONFIG.qrCodeDir, 'qr_info.json'),
                    JSON.stringify(qrInfo, null, 2)
                );

                await browser.close();
                return { success: true, message: 'Login successful' };
            }

            // Progress indicator
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            process.stdout.write(`\r⏳ Waiting... ${elapsed}s / ${CONFIG.timeout/1000}s `);
        }

        throw new Error('Login timeout - QR code expired');

    } catch (error) {
        console.error(`\n❌ Login failed: ${error.message}`);
        await browser.close();
        throw error;
    }
}

/**
 * Search for videos on Douyin
 */
async function searchVideos(query, limit = 10) {
    console.log(`🔍 Searching for: "${query}"`);

    // Load session if exists
    if (!fs.existsSync(CONFIG.sessionFile)) {
        throw new Error('Not logged in. Run "login" command first.');
    }

    const sessionData = JSON.parse(fs.readFileSync(CONFIG.sessionFile, 'utf-8'));

    const browser = await chromium.launch({
        headless: true,
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 900 },
        userAgent: sessionData.userAgent || 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    await context.addCookies(sessionData.cookies);
    const page = await context.newPage();

    try {
        const searchUrl = `https://www.douyin.com/search/${encodeURIComponent(query)}`;
        console.log(`📍 Opening: ${searchUrl}`);

        await page.goto(searchUrl, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);

        // Scroll to load more content
        for (let i = 0; i < 3; i++) {
            await page.evaluate(() => window.scrollBy(0, 500));
            await page.waitForTimeout(1000);
        }

        // Extract video data
        const videos = await page.evaluate(() => {
            const results = [];
            const items = document.querySelectorAll('[class*="video-card"], [class*="feed-list"] > div');

            items.forEach((item, index) => {
                if (index >= 20) return; // Limit results

                const titleEl = item.querySelector('[class*="title"], [class*="desc"], a[class*="title"]');
                const authorEl = item.querySelector('[class*="author"], [class*="nickname"], [class*="name"]');
                const linkEl = item.querySelector('a[href*="/video/"]');
                const statsEl = item.querySelector('[class*="like"], [class*="play"]');

                if (titleEl || linkEl) {
                    results.push({
                        title: titleEl?.textContent?.trim() || 'Untitled',
                        author: authorEl?.textContent?.trim() || 'Unknown',
                        url: linkEl?.href || '',
                        stats: statsEl?.textContent?.trim() || ''
                    });
                }
            });

            return results;
        });

        console.log(`\n✅ Found ${videos.length} videos:`);
        videos.slice(0, limit).forEach((video, i) => {
            console.log(`${i + 1}. ${video.title}`);
            console.log(`   Author: ${video.author}`);
            if (video.url) console.log(`   URL: ${video.url}`);
            console.log('');
        });

        await browser.close();
        return videos;

    } catch (error) {
        console.error(`Search failed: ${error.message}`);
        await browser.close();
        throw error;
    }
}

/**
 * Get detailed video information
 */
async function getVideoInfo(videoUrl) {
    console.log(`📹 Extracting video info from: ${videoUrl}`);

    if (!fs.existsSync(CONFIG.sessionFile)) {
        throw new Error('Not logged in. Run "login" command first.');
    }

    const sessionData = JSON.parse(fs.readFileSync(CONFIG.sessionFile, 'utf-8'));

    const browser = await chromium.launch({
        headless: true,
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 900 },
        userAgent: sessionData.userAgent
    });

    await context.addCookies(sessionData.cookies);
    const page = await context.newPage();

    try {
        await page.goto(videoUrl, { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);

        // Extract video details
        const videoInfo = await page.evaluate(() => {
            return {
                title: document.querySelector('h1[class*="title"], [class*="video-title"]')?.textContent?.trim() || '',
                author: document.querySelector('[class*="author-name"], [class*="nickname"]')?.textContent?.trim() || '',
                description: document.querySelector('[class*="desc"], [class*="description"]')?.textContent?.trim() || '',
                likes: document.querySelector('[class*="like"] span, [class*="like-count"]')?.textContent?.trim() || '',
                comments: document.querySelector('[class*="comment"] span, [class*="comment-count"]')?.textContent?.trim() || '',
                shares: document.querySelector('[class*="share"] span, [class*="share-count"]')?.textContent?.trim() || '',
                plays: document.querySelector('[class*="play-count"], [class*="playCount"]')?.textContent?.trim() || '',
                hashtags: Array.from(document.querySelectorAll('[class*="tag"], [class*="hashtag"] a'))
                    .map(el => el.textContent?.trim())
                    .filter(Boolean)
            };
        });

        console.log('\n📊 Video Information:');
        console.log(JSON.stringify(videoInfo, null, 2));

        await browser.close();
        return videoInfo;

    } catch (error) {
        console.error(`Failed to get video info: ${error.message}`);
        await browser.close();
        throw error;
    }
}

/**
 * Get trending videos
 */
async function getTrending(limit = 20) {
    console.log('🔥 Fetching trending videos...');

    if (!fs.existsSync(CONFIG.sessionFile)) {
        throw new Error('Not logged in. Run "login" command first.');
    }

    const sessionData = JSON.parse(fs.readFileSync(CONFIG.sessionFile, 'utf-8'));

    const browser = await chromium.launch({
        headless: true,
        args: ['--disable-blink-features=AutomationControlled']
    });

    const context = await browser.newContext({
        viewport: { width: 1280, height: 900 },
        userAgent: sessionData.userAgent
    });

    await context.addCookies(sessionData.cookies);
    const page = await context.newPage();

    try {
        await page.goto('https://www.douyin.com', { waitUntil: 'networkidle', timeout: 30000 });
        await page.waitForTimeout(3000);

        // Scroll to load trending content
        for (let i = 0; i < 5; i++) {
            await page.evaluate(() => window.scrollBy(0, 800));
            await page.waitForTimeout(1000);
        }

        const trending = await page.evaluate(() => {
            const results = [];
            const items = document.querySelectorAll('[class*="video-card"], [class*="item"]');

            items.forEach((item, i) => {
                if (i >= 30) return;

                const title = item.querySelector('[class*="title"]')?.textContent?.trim();
                const author = item.querySelector('[class*="author"]')?.textContent?.trim();
                const link = item.querySelector('a[href*="/video/"]')?.href;

                if (title || link) {
                    results.push({ title: title || 'Untitled', author: author || 'Unknown', url: link || '' });
                }
            });

            return results;
        });

        console.log(`\n🔥 Top ${Math.min(limit, trending.length)} Trending Videos:`);
        trending.slice(0, limit).forEach((v, i) => {
            console.log(`${i + 1}. ${v.title} - @${v.author}`);
        });

        await browser.close();
        return trending;

    } catch (error) {
        console.error(`Failed to get trending: ${error.message}`);
        await browser.close();
        throw error;
    }
}

/**
 * Check login status
 */
async function checkStatus() {
    if (!fs.existsSync(CONFIG.sessionFile)) {
        console.log('❌ Not logged in');
        return { loggedIn: false };
    }

    const sessionData = JSON.parse(fs.readFileSync(CONFIG.sessionFile, 'utf-8'));
    const loginDate = new Date(sessionData.loginTime);
    const hoursSinceLogin = (Date.now() - loginDate.getTime()) / (1000 * 60 * 60);

    console.log(`✅ Logged in since: ${loginDate.toLocaleString()}`);
    console.log(`   Session age: ${Math.floor(hoursSinceLogin)} hours`);

    if (hoursSinceLogin > 24) {
        console.log('⚠️ Session is older than 24 hours, consider re-logging in');
    }

    return { loggedIn: true, loginTime: sessionData.loginTime, hoursSinceLogin };
}

// Main CLI handler
async function main() {
    const args = process.argv.slice(2);
    const command = args[0] || 'help';

    console.log('🎬 Douyin Browser Automation Tool');
    console.log('='.repeat(40));

    try {
        switch (command) {
            case 'login':
                await performLogin();
                break;

            case 'search':
                const query = args.slice(1).join(' ') || '热门视频';
                await searchVideos(query);
                break;

            case 'video':
                const videoUrl = args[1];
                if (!videoUrl) {
                    console.error('Usage: node douyin-browser.js video <video-url>');
                    process.exit(1);
                }
                await getVideoInfo(videoUrl);
                break;

            case 'trending':
                await getTrending();
                break;

            case 'status':
                await checkStatus();
                break;

            case 'help':
            default:
                console.log(`
Available Commands:
  node douyin-browser.js login      - Open browser and get QR code for login
  node douyin-browser.js search [q] - Search for videos (default: 热门视频)
  node douyin-browser.js video <url> - Get detailed video info
  node douyin-browser.js trending   - Get trending videos
  node douyin-browser.js status     - Check login status

Examples:
  node douyin-browser.js login
  node douyin-browser.js search 美食教程
  node douyin-browser.js video https://www.douyin.com/video/123456
  node douyin-browser.js trending
`);
                break;
        }
    } catch (error) {
        console.error(`\n❌ Error: ${error.message}`);
        process.exit(1);
    }

    process.exit(0);
}

main();
