/**
 * Heywhale Dataset Assistant - Node.js version
 * Requires: Node.js 18+, playwright, chardet (optional)
 * Usage: node download.js
 */

const { chromium } = require('playwright');
const readline = require('readline');
const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');
const { execSync } = require('child_process');

const HEYWHALE_API = 'https://www.heywhale.com/api/datasets';
const HEYWHALE_AUTH = 'https://www.heywhale.com/api/auth/login';

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

function question(prompt) {
    return new Promise(resolve => rl.question(prompt, resolve));
}

function detectPython() {
    const candidates = [];
    if (process.platform === 'win32') {
        const localAppData = process.env.LOCALAPPDATA || '';
        for (const ver of ['314', '313', '312', '311']) {
            candidates.push(path.join(localAppData, 'Programs', 'Python', `Python${ver}`, 'python.exe'));
        }
        candidates.push('C:\\Python314\\python.exe', 'C:\\Python313\\python.exe');
        const pathDirs = (process.env.PATH || '').split(path.delimiter);
        for (const p of pathDirs) {
            for (const name of ['python.exe', 'python3.exe']) {
                const exe = path.join(p, name);
                if (!candidates.includes(exe)) candidates.push(exe);
            }
        }
    } else {
        const paths = ['/usr/local/bin/python3', '/usr/bin/python3', '/opt/homebrew/bin/python3'];
        candidates.push(...paths);
    }
    for (const pyPath of candidates) {
        try {
            const result = execSync(`"${pyPath}" --version`, { encoding: 'utf-8', timeout: 5000 });
            const match = result.match(/Python (\d+\.\d+\.\d+)/);
            if (match) return { path: pyPath, version: match[1] };
        } catch (e) { continue; }
    }
    return null;
}

function detectNodeVersion() {
    return { path: process.execPath, version: process.version };
}

async function checkEnvironment() {
    console.log('='.repeat(60));
    console.log('Environment Check');
    console.log('='.repeat(60));
    console.log(`  OS: ${process.platform}`);
    console.log(`  Node.js: ${process.version} (${process.execPath})`);

    const pythonInfo = detectPython();
    if (pythonInfo) {
        console.log(`  Python: ${pythonInfo.version} (${pythonInfo.path})`);
    } else {
        console.log('  Python: Not found');
    }

    try {
        require('playwright');
        console.log('  Playwright: installed');
    } catch (e) {
        console.log('  Playwright: NOT INSTALLED (npm install playwright)');
    }

    console.log();
}

async function searchDatasets(keyword, page = 1, pageSize = 20) {
    const url = `${HEYWHALE_API}?search=${encodeURIComponent(keyword)}&page=${page}&pageSize=${pageSize}`;
    return new Promise((resolve) => {
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json.data || json.results || []);
                } catch (e) { resolve([]); }
            });
        }).on('error', () => resolve([]));
    });
}

function downloadFile(url, savePath) {
    return new Promise((resolve) => {
        const file = fs.createWriteStream(savePath);
        const protocol = url.startsWith('https') ? https : http;
        protocol.get(url, (res) => {
            if (res.statusCode === 200) {
                res.pipe(file);
                file.on('finish', () => {
                    file.close();
                    const size = fs.statSync(savePath).size;
                    resolve({ ok: true, size });
                });
            } else {
                file.close();
                if (fs.existsSync(savePath)) fs.unlinkSync(savePath);
                resolve({ ok: false, status: res.statusCode });
            }
        }).on('error', (e) => {
            file.close();
            if (fs.existsSync(savePath)) fs.unlinkSync(savePath);
            resolve({ ok: false, error: e.message });
        });
    });
}

function formatSize(bytes) {
    if (bytes < 1024) return `${bytes}B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)}MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)}GB`;
}

async function heywhaleDownload(datasets, email, password, baseDir) {
    const loginResp = await new Promise((resolve) => {
        const url = new URL(HEYWHALE_AUTH);
        const data = JSON.stringify({ email, password });
        const req = https.request({
            hostname: url.hostname, path: url.pathname, method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Content-Length': data.length }
        }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => { try { resolve(JSON.parse(body)); } catch (e) { resolve({ code: -1 }); } });
        });
        req.on('error', () => resolve({ code: -1 }));
        req.write(data);
        req.end();
    });

    if (loginResp.code !== 0) {
        console.log('Login failed!');
        return false;
    }
    console.log('Login successful!');

    const browser = await chromium.launch({ headless: false, slowMo: 300 });
    const context = await browser.newContext({ viewport: { width: 1280, height: 900 } });
    const page = await context.newPage();
    await page.goto('https://www.heywhale.com/', { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(3000);

    let remainingQuota = null;
    if (datasets.length > 0) {
        const firstDs = datasets[0];
        console.log('\nDetecting download quota...');
        try {
            await page.goto(`https://www.heywhale.com/home/dataset/${firstDs.id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
            await page.waitForTimeout(8000);
            const downloadBtn = page.locator('button.ivu-btn-icon-only:has(.icon-download)');
            if (await downloadBtn.count() > 0) {
                await downloadBtn.first.click();
                await page.waitForTimeout(3000);
                const quotaText = await page.evaluate(() => {
                    const modals = document.querySelectorAll('.dataset-download-confirm-modal');
                    for (const m of modals) {
                        const title = m.querySelector('.confirm-title');
                        if (title) return title.textContent;
                    }
                    return '';
                });
                if (quotaText) {
                    const match = quotaText.match(/还剩\s*(\d+)/);
                    if (match) {
                        remainingQuota = parseInt(match[1]);
                        console.log(`  Detected quota: ${remainingQuota} remaining today`);
                    }
                }
                for (const sel of ['.dataset-download-confirm-modal .ivu-modal-close', '.dataset-download-modal .ivu-modal-close']) {
                    try {
                        const close = page.locator(sel).first;
                        if (await close.isVisible()) { await close.click(); await page.waitForTimeout(1000); }
                    } catch (e) {}
                }
            }
        } catch (e) {
            console.log(`  Quota detection error: ${e.message}`);
        }
    }

    if (remainingQuota === null) {
        console.log('  WARNING: Could not detect quota. Defaulting to conservative estimate (3).');
        remainingQuota = 3;
    }

    console.log(`\n  Your daily download quota: ${remainingQuota}`);

    let quotaUsed = 0;
    for (let i = 0; i < datasets.length; i++) {
        const ds = datasets[i];
        const saveDir = path.join(baseDir, ds.case_dir || ds.id);
        fs.mkdirSync(saveDir, { recursive: true });

        if (quotaUsed >= remainingQuota) {
            console.log(`\n  QUOTA EXCEEDED: ${quotaUsed}/${remainingQuota} used.`);
            console.log(`  Remaining ${datasets.length - i} datasets need to be downloaded tomorrow.`);
            break;
        }

        console.log(`\n[${i + 1}/${datasets.length}] ${ds.title} (quota: ${quotaUsed}/${remainingQuota})`);
        try {
            await page.goto(`https://www.heywhale.com/home/dataset/${ds.id}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
        } catch (e) {
            console.log('  Page timeout, skipping');
            continue;
        }
        await page.waitForTimeout(10000);

        const downloadBtn = page.locator('button.ivu-btn-icon-only:has(.icon-download)');
        if (await downloadBtn.count() === 0) {
            console.log('  No download button found');
            continue;
        }
        await downloadBtn.first.click();
        await page.waitForTimeout(3000);

        let isFreeDs = false;
        const confirmVisible = await page.evaluate(() => {
            const modals = document.querySelectorAll('.dataset-download-confirm-modal .ivu-modal-wrap');
            for (const m of modals) {
                if (!m.classList.contains('ivu-modal-hidden') && getComputedStyle(m).display !== 'none') return true;
            }
            return false;
        });
        if (confirmVisible) {
            const quotaText = await page.evaluate(() => {
                const modals = document.querySelectorAll('.dataset-download-confirm-modal');
                for (const m of modals) {
                    const title = m.querySelector('.confirm-title');
                    if (title) return title.textContent;
                }
                return '';
            });
            if (quotaText) {
                const match = quotaText.match(/还剩\s*(\d+)/);
                if (match) remainingQuota = parseInt(match[1]);
            }
            await page.evaluate(() => {
                const modals = document.querySelectorAll('.dataset-download-confirm-modal .ivu-modal-wrap');
                for (const m of modals) {
                    if (!m.classList.contains('ivu-modal-hidden')) {
                        const btn = m.querySelector('.ivu-btn-primary');
                        if (btn) btn.click();
                    }
                }
            });
            await page.waitForTimeout(5000);
        }

        isFreeDs = (await page.evaluate(() => {
            const modals = document.querySelectorAll('.dataset-download-modal');
            for (const m of modals) {
                const wrap = m.querySelector('.ivu-modal-wrap');
                if (wrap && !wrap.classList.contains('ivu-modal-hidden') && getComputedStyle(wrap).display !== 'none') return m.textContent;
            }
            return '';
        }) || '').includes('不消耗');

        const signedUrls = await page.evaluate(() => {
            const results = [];
            const modals = document.querySelectorAll('.dataset-download-modal .ivu-modal-wrap');
            for (const m of modals) {
                if (!m.classList.contains('ivu-modal-hidden') && getComputedStyle(m).display !== 'none') {
                    const links = m.querySelectorAll('a[href*="myqcloud.com"]');
                    links.forEach(a => {
                        const href = a.getAttribute('href');
                        let filename = '';
                        const match = href.match(/filename[^&]*=([^&]+)/);
                        if (match) filename = decodeURIComponent(match[1]);
                        if (!filename) {
                            const pm = href.match(/\/([^?/]+\.csv)\?/);
                            if (pm) filename = decodeURIComponent(pm[1]);
                        }
                        results.push({ url: href, filename });
                    });
                    break;
                }
            }
            return results;
        });

        const closeBtn = page.locator('.dataset-download-modal .ivu-modal-close');
        if (await closeBtn.count() > 0) {
            try { await closeBtn.first.click(); } catch (e) {}
        }
        await page.waitForTimeout(1000);

        let csvCount = 0;
        for (const su of signedUrls) {
            if (!su.filename.endsWith('.csv')) continue;
            csvCount++;
            const savePath = path.join(saveDir, su.filename);
            const result = await downloadFile(su.url, savePath);
            if (result.ok) {
                console.log(`  ${su.filename}: OK (${formatSize(result.size)})`);
            } else {
                console.log(`  ${su.filename}: FAIL ${result.status || result.error}`);
            }
        }

        if (!isFreeDs && csvCount > 0) {
            quotaUsed += csvCount;
            console.log(`  Quota: ${quotaUsed}/${remainingQuota} used`);
        } else if (isFreeDs) {
            console.log('  FREE dataset (no quota consumed)');
        }
    }

    console.log('\nClosing browser...');
    await page.waitForTimeout(3000);
    await browser.close();
    return true;
}

async function interactiveMode() {
    await checkEnvironment();

    console.log('='.repeat(60));
    console.log('Heywhale Dataset Assistant - Interactive Mode (Node.js)');
    console.log('='.repeat(60));

    console.log('\nStep 1: Do you have a Heywhale account?');
    console.log('  1. Yes (已有账号)');
    console.log('  2. No (没有账号，需要注册)');
    const hasAccount = await question('  Select (1/2): ');

    let email, password;

    if (hasAccount.trim() === '1') {
        email = (await question('  Email: ')).trim();
        password = (await question('  Password: ')).trim();
    } else {
        console.log('\n  和鲸数据注册引导：');
        console.log('  ─────────────────────────────────────');
        console.log('  方式一：微信扫码注册（推荐）');
        console.log('    1. 打开微信，搜索公众号「和鲸社区」并关注');
        console.log('    2. 在公众号菜单中点击「登录/注册」');
        console.log('    3. 扫描二维码完成注册');
        console.log('    4. 注册后在网页端绑定邮箱（设置→账号安全）');
        console.log();
        console.log('  方式二：邮箱注册');
        console.log('    1. 访问 https://www.heywhale.com/auth/register');
        console.log('    2. 填写：邮箱地址、用户名(2-20字符)、密码(8位+字母数字)');
        console.log('    3. 勾选同意《用户协议》和《隐私保护指引》');
        console.log('    4. 点击注册 → 查收验证邮件 → 点击验证链接');
        console.log('  ─────────────────────────────────────');
        console.log();
        console.log('  注册完成后请输入登录信息：');
        email = (await question('  Email: ')).trim();
        password = (await question('  Password: ')).trim();
    }

    if (!email || !password) {
        console.log('  Credentials required. Exiting.');
        rl.close();
        return;
    }

    console.log('\nStep 2: What type of ML task?');
    console.log('  1. Regression  2. Classification  3. Clustering');
    console.log('  4. NLP  5. Time Series  6. Association Rules  7. Other');
    const taskType = (await question('  Select (1-7): ')).trim();

    const taskKeywords = {
        '1': '回归 预测', '2': '分类 预测', '3': '聚类 无监督',
        '4': '文本 NLP', '5': '时间序列', '6': '关联规则', '7': ''
    };

    console.log('\nStep 3: What domain?');
    console.log('  1. Healthcare  2. Finance  3. E-commerce');
    console.log('  4. Education  5. Sports  6. Food  7. Other');
    const domain = (await question('  Select (1-7): ')).trim();

    const domainKeywords = {
        '1': '医疗 健康', '2': '金融 贷款', '3': '电商 消费',
        '4': '教育 学生', '5': '体育 运动', '6': '餐饮 美食', '7': ''
    };

    let searchKw = `${taskKeywords[taskType] || ''} ${domainKeywords[domain] || ''}`.trim();
    if (!searchKw) searchKw = (await question('  Enter search keywords: ')).trim();
    if (!searchKw) searchKw = '机器学习 数据集';

    console.log(`\nStep 4: Searching Heywhale for '${searchKw}'...`);
    const results = await searchDatasets(searchKw);

    if (!results.length) {
        console.log('  No datasets found. Try different keywords.');
        rl.close();
        return;
    }

    console.log(`\n  Found ${results.length} datasets:\n`);
    for (let i = 0; i < results.length; i++) {
        const ds = results[i];
        const title = ds.Title || ds.title || 'Unknown';
        const dsId = ds._id || ds.id || '';
        const downloads = ds.DownloadCount || ds.downloadCount || 0;
        console.log(`  [${i + 1}] ${title}`);
        console.log(`      ID: ${dsId}`);
        console.log(`      Downloads: ${downloads}`);
    }

    console.log('\nStep 5: Save directory');
    const baseDir = (await question('  Directory (default: ./datasets): ')).trim() || './datasets';

    console.log('\nStep 6: Select datasets to download');
    console.log('  Enter numbers (e.g., 1,3,5) or "all":');
    const selection = (await question('  Selection: ')).trim();

    let selected;
    if (selection.toLowerCase() === 'all') {
        selected = results.map((_, i) => i);
    } else {
        selected = selection.split(',').map(x => parseInt(x.trim()) - 1).filter(x => !isNaN(x) && x >= 0);
    }

    const datasetsToDownload = selected
        .filter(idx => idx >= 0 && idx < results.length)
        .map(idx => ({
            id: results[idx]._id || results[idx].id || '',
            title: results[idx].Title || results[idx].title || 'Unknown',
            case_dir: (results[idx].Title || results[idx].title || 'unknown').replace(/ /g, '_').substring(0, 50),
        }));

    if (!datasetsToDownload.length) {
        console.log('  No datasets selected. Exiting.');
        rl.close();
        return;
    }

    console.log(`\n  Will download ${datasetsToDownload.length} datasets:`);
    datasetsToDownload.forEach(ds => console.log(`    - ${ds.title}`));

    console.log('\n  NOTE: Download quota will be detected automatically.');

    const confirm = (await question('\n  Confirm download? (y/n): ')).trim().toLowerCase();
    if (confirm !== 'y') {
        console.log('  Cancelled.');
        rl.close();
        return;
    }

    await heywhaleDownload(datasetsToDownload, email, password, baseDir);

    console.log('\n' + '='.repeat(60));
    console.log('Download Complete!');
    console.log('='.repeat(60));

    rl.close();
}

interactiveMode().catch(console.error);
