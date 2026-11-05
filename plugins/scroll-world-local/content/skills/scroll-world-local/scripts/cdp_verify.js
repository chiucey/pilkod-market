// Browser QA for scroll-world-local. Zero npm dependencies.
//
// Usage:
//   node cdp_verify.js <page_url> <out_dir> [debug_port]
//
// Requires Chrome running with --remote-debugging-port. Captures desktop chapter
// centres, real chapter boundaries, reverse/rapid scroll, mobile, and reduced motion.

const http = require('http');
const crypto = require('crypto');
const net = require('net');
const fs = require('fs');
const path = require('path');

const PAGE_URL = process.argv[2] || 'http://127.0.0.1:8766/index.html';
const OUT_DIR = process.argv[3] || path.resolve(process.cwd(), 'work', 'qa');
const PORT = parseInt(process.argv[4] || '9444', 10);
fs.mkdirSync(OUT_DIR, { recursive: true });

function getJSON(route) {
  return new Promise((resolve, reject) => {
    http.get({ host: '127.0.0.1', port: PORT, path: route }, response => {
      let data = '';
      response.on('data', chunk => data += chunk);
      response.on('end', () => {
        try { resolve(JSON.parse(data)); } catch (error) { reject(error); }
      });
    }).on('error', reject);
  });
}

function wsConnect(wsUrl) {
  return new Promise((resolve, reject) => {
    const url = new (require('url').URL)(wsUrl);
    const key = crypto.randomBytes(16).toString('base64');
    const socket = net.connect(url.port, url.hostname, () => {
      socket.write(
        `GET ${url.pathname}${url.search} HTTP/1.1\r\n` +
        `Host: ${url.host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n` +
        `Sec-WebSocket-Key: ${key}\r\nSec-WebSocket-Version: 13\r\n\r\n`
      );
    });
    let buffer = Buffer.alloc(0);
    let handshook = false;
    let id = 0;
    const pending = {};
    const eventListeners = [];

    function send(message) {
      const data = Buffer.from(JSON.stringify(message));
      const length = data.length;
      let header;
      if (length < 126) header = Buffer.from([0x81, 0x80 | length]);
      else if (length < 65536) {
        header = Buffer.alloc(4); header[0] = 0x81; header[1] = 0x80 | 126;
        header.writeUInt16BE(length, 2);
      } else {
        header = Buffer.alloc(10); header[0] = 0x81; header[1] = 0x80 | 127;
        header.writeBigUInt64BE(BigInt(length), 2);
      }
      const mask = crypto.randomBytes(4);
      const masked = Buffer.alloc(length);
      for (let i = 0; i < length; i++) masked[i] = data[i] ^ mask[i % 4];
      socket.write(Buffer.concat([header, mask, masked]));
    }

    const api = {
      cmd(method, params = {}) {
        return new Promise(done => {
          const requestId = ++id;
          pending[requestId] = done;
          send({ id: requestId, method, params });
        });
      },
      onEvent(listener) { eventListeners.push(listener); },
      close() { socket.end(); },
    };

    socket.on('data', chunk => {
      buffer = Buffer.concat([buffer, chunk]);
      if (!handshook) {
        const end = buffer.indexOf('\r\n\r\n');
        if (end === -1) return;
        handshook = true;
        buffer = buffer.slice(end + 4);
        resolve(api);
      }
      while (handshook) {
        if (buffer.length < 2) break;
        const lenCode = buffer[1] & 127;
        let offset = 2;
        let length = lenCode;
        if (lenCode === 126) {
          if (buffer.length < 4) break;
          length = buffer.readUInt16BE(2); offset = 4;
        } else if (lenCode === 127) {
          if (buffer.length < 10) break;
          length = Number(buffer.readBigUInt64BE(2)); offset = 10;
        }
        if (buffer.length < offset + length) break;
        const payload = buffer.slice(offset, offset + length).toString('utf8');
        buffer = buffer.slice(offset + length);
        const message = JSON.parse(payload);
        if (message.id && pending[message.id]) {
          pending[message.id](message); delete pending[message.id];
        } else {
          eventListeners.forEach(listener => listener(message));
        }
      }
    });
    socket.on('error', reject);
  });
}

const wait = ms => new Promise(resolve => setTimeout(resolve, ms));

(async () => {
  const targets = await getJSON('/json');
  const page = targets.find(target => target.type === 'page' && target.webSocketDebuggerUrl);
  if (!page) throw new Error('No Chrome page target. Check the debug port.');
  const client = await wsConnect(page.webSocketDebuggerUrl);
  const issues = [];
  client.onEvent(message => {
    if (message.method === 'Runtime.exceptionThrown') issues.push({ type: 'exception', data: message.params });
    if (message.method === 'Log.entryAdded' && message.params?.entry?.level === 'error') {
      issues.push({ type: 'console-error', data: message.params.entry.text });
    }
  });

  await client.cmd('Page.enable');
  await client.cmd('Runtime.enable');
  await client.cmd('Log.enable');
  await client.cmd('Network.enable');
  await client.cmd('Network.setCacheDisabled', { cacheDisabled: true });
  await client.cmd('Network.clearBrowserCache');
  await client.cmd('Page.navigate', { url: PAGE_URL });
  await wait(4500);

  async function evaluate(expression) {
    const result = await client.cmd('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.result?.exceptionDetails) throw new Error(result.result.exceptionDetails.text);
    return result.result?.result?.value;
  }

  async function capture(name) {
    const screenshot = await client.cmd('Page.captureScreenshot', { format: 'png' });
    const output = path.join(OUT_DIR, `${name}.png`);
    fs.writeFileSync(output, Buffer.from(screenshot.result.data, 'base64'));
    console.log('shot', output);
  }

  async function scrollToY(y, delay = 1300) {
    await evaluate(`scrollTo(0, ${Math.max(0, Math.round(y))})`);
    await wait(delay);
  }

  async function scrollToFrac(fraction, delay = 1300) {
    const y = await evaluate(`(() => {
      const max = document.documentElement.scrollHeight - innerHeight;
      const y = max * ${fraction}; scrollTo(0, y); return y;
    })()`);
    await wait(delay);
    return y;
  }

  await capture('desktop_top');

  const chapterCentres = [];
  const chapterCount = await evaluate(`document.querySelectorAll('.sw-route__dot').length`);
  for (let index = 0; index < chapterCount; index++) {
    const y = await evaluate(`(() => {
      const dot = document.querySelectorAll('.sw-route__dot')[${index}];
      if (!dot) return null; dot.click(); return true;
    })()`);
    if (y == null) continue;
    await wait(1600);
    const actualY = await evaluate('scrollY');
    chapterCentres.push(actualY);
    await capture(`desktop_chapter_${String(index + 1).padStart(2, '0')}`);
  }

  for (let index = 0; index < chapterCentres.length - 1; index++) {
    const boundary = (chapterCentres[index] + chapterCentres[index + 1]) / 2;
    await scrollToY(boundary - 18, 900);
    await capture(`boundary_${String(index + 1).padStart(2, '0')}_before`);
    await scrollToY(boundary + 18, 900);
    await capture(`boundary_${String(index + 1).padStart(2, '0')}_after`);
  }

  await scrollToFrac(0.98, 1000);
  await capture('reverse_start_finale');
  await scrollToFrac(0.02, 1200);
  await capture('reverse_end_top');

  await evaluate(`(() => {
    const max = document.documentElement.scrollHeight - innerHeight;
    [0.1, 0.85, 0.3, 0.95, 0.55].forEach((f, i) => setTimeout(() => scrollTo(0, max * f), i * 45));
  })()`);
  await wait(1100);
  await capture('rapid_scroll_settled');

  await client.cmd('Emulation.setDeviceMetricsOverride', {
    width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
    screenWidth: 390, screenHeight: 844,
  });
  await client.cmd('Page.reload', { ignoreCache: true });
  await wait(4500);
  await scrollToFrac(0, 800); await capture('mobile_top');
  await scrollToFrac(0.5, 1200); await capture('mobile_middle');
  await scrollToFrac(0.98, 1200); await capture('mobile_finale');

  await client.cmd('Emulation.setEmulatedMedia', {
    media: '', features: [{ name: 'prefers-reduced-motion', value: 'reduce' }],
  });
  await client.cmd('Page.reload', { ignoreCache: true });
  await wait(2500);
  await scrollToFrac(0.5, 700);
  await capture('reduced_motion_middle');

  const manifest = {
    page: PAGE_URL,
    chapter_count: chapterCount,
    chapter_centres: chapterCentres,
    issues,
    completed_at: new Date().toISOString(),
  };
  fs.writeFileSync(path.join(OUT_DIR, 'qa.json'), JSON.stringify(manifest, null, 2));
  client.close();
  console.log('done', OUT_DIR, `issues=${issues.length}`);
})().catch(error => { console.error('ERR', error); process.exit(1); });
