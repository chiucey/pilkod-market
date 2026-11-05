# Browser Server Automation Skill

Control a headless Chrome browser on the server using Playwright + Node.js.

## Installation (Already Done on This Server)

Google Chrome 146 is installed at: `/usr/bin/google-chrome`
Playwright is installed at: `/workspace/node_modules/playwright`

## Key Setup Required (Discovered 2026-03-24)

Before using Playwright with the system Chrome, create these symlinks:

```bash
mkdir -p /root/.cache/ms-playwright/chromium-1208/chrome-linux64
ln -sf /usr/bin/google-chrome /root/.cache/ms-playwright/chromium-1208/chrome-linux64/chrome

mkdir -p /root/.cache/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-linux64
ln -sf /usr/bin/google-chrome /root/.cache/ms-playwright/chromium_headless_shell-1208/chrome-headless-shell-linux64/chrome-headless-shell
```

Then Playwright auto-detects the browser without specifying `executablePath`.

## Basic Browser Test

```javascript
const {chromium} = require('playwright');
chromium.launch({headless:true, args:['--no-sandbox','--disable-setuid-sandbox']}).then(async b => {
  const p = await b.newPage();
  await p.setViewportSize({width:1440, height:900});
  await p.goto('https://example.com', {waitUntil:'domcontentloaded', timeout:15000});
  await p.screenshot({path: '/workspace/screenshot.png', fullPage:true});
  console.log('URL:', p.url(), 'Title:', await p.title());
  await b.close();
}).catch(e => console.error('Error:', e.message));
```

## Complete Login Script Template

```javascript
const {chromium} = require('playwright');

(async () => {
  const browser = await chromium.launch({ 
    headless: true, 
    args: ['--no-sandbox','--disable-setuid-sandbox','--disable-dev-shm-usage'] 
  });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1440, height: 900 });

  // Step 1: Navigate
  await page.goto('https://target-site.com/', { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.screenshot({ path: '/workspace/step1.png', fullPage: true });
  console.log('URL:', page.url(), 'Title:', await page.title());

  // Step 2: Click login button (find by text)
  await page.evaluate(() => {
    const all = document.querySelectorAll('*');
    for(const el of all) {
      if(el.children.length===0 && el.innerText && 
         (el.innerText.trim()==='登录'||el.innerText.trim()==='登陆')){
        el.click(); return;
      }
    }
  });
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/workspace/step2.png', fullPage: true });

  // Step 3: Fill inputs using native JS (for React/Vue custom inputs)
  await page.evaluate(() => {
    const inputs = document.querySelectorAll('input');
    for(const i of inputs) {
      if(i.placeholder && i.placeholder.includes('邮箱')) {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        setter.call(i, 'your@email.com');
        i.dispatchEvent(new Event('input',{bubbles:true}));
        i.dispatchEvent(new Event('change',{bubbles:true}));
      }
      if(i.placeholder && i.placeholder.includes('密码')) {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;
        setter.call(i, 'your-password');
        i.dispatchEvent(new Event('input',{bubbles:true}));
        i.dispatchEvent(new Event('change',{bubbles:true}));
      }
    }
  });
  await page.waitForTimeout(500);
  await page.screenshot({ path: '/workspace/step3.png', fullPage: true });

  // Step 4: Submit
  await page.evaluate(() => {
    const forms = document.querySelectorAll('form');
    for(const f of forms) {
      if(f.querySelector('input[name="email"]') || f.querySelector('input[placeholder*="邮箱"]')) {
        f.submit(); return;
      }
    }
    const btns = document.querySelectorAll('button');
    for(const b of btns) {
      if(b.type==='submit' || b.innerText.includes('登录')) { b.click(); return; }
    }
  });
  
  await page.waitForTimeout(5000);
  await page.screenshot({ path: '/workspace/step4_result.png', fullPage: true });
  console.log('Final URL:', page.url(), 'Title:', await page.title());
  
  await browser.close();
  console.log('Done');
})().catch(e => console.error('Fatal:', e.message));
```

## Known Issues & Solutions

### "Executable doesn't exist" error
**Cause**: Playwright can't find Chrome.  
**Fix**: Create symlinks as shown in Installation section above.

### IP-based 401 on login  
**Cause**: Target site rejects login requests from server IP (geo/IP restriction).  
**Solutions**:
1. Use Cookie import from logged-in browser session
2. Ask user to provide session cookies instead of credentials
3. Try alternative login methods (SMS, QR code)

### Form fill doesn't work for React/Vue inputs
**Cause**: React/Vue use controlled inputs that don't respond to direct `.fill()`.  
**Fix**: Use the `Object.getOwnPropertyDescriptor` approach shown above to bypass React's input handling.

### Page loads but content is empty
**Cause**: Page requires JavaScript to render (SPA).  
**Fix**: Use `waitUntil: 'networkidle'` or add `await page.waitForTimeout(2000)` after navigation.

## Platform Constraints
- No GUI available — use headless mode (`headless: true`)
- `--no-sandbox` and `--disable-setuid-sandbox` flags required
- `--disable-dev-shm-usage` helps prevent crashes in containerized environments
- Server has no graphics card — all rendering is software-based (slow but functional)

## File Paths
- Chrome binary: `/usr/bin/google-chrome`
- Playwright module: `/workspace/node_modules/playwright`
- Python PIL: `/usr/bin/python3` with `python3-pil` package installed
