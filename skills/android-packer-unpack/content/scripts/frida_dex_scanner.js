// frida_dex_scanner.js — 内存 dex 魔数扫描 (兜底方案)
//
// 思路: 加固再严密, 解密的 dex 必然以 dex\n035\0 魔数出现在内存某处
// 扫所有可读内存段, 找到所有 dex 头, 切片写盘
//
// 优势: 不依赖任何 hook 点, 绕过一切 hook 检测
// 劣势: 慢(全内存扫一遍几秒到几十秒), 误报多(可能有其他 .dex 缓存)
//
// 用法:
//   frida -U -f <pkg> -l frida_dex_scanner.js --no-pause
//   触发 app 各页面加载, 等 5-10 秒看 console

'use strict';

const PKG = '{{PKG}}';
const OUT_DIR = '/data/data/' + PKG + '/files/';
const DEX_MAGIC = [0x64, 0x65, 0x78, 0x0a, 0x30, 0x33, 0x35, 0x00];

// 单段扫描: 在 buf 中找所有 dex 头, 按 dex header.file_size 切片
function scanBuffer(buf, baseAddr) {
    const hits = [];
    for (let i = 0; i < buf.length - 8; i++) {
        let match = true;
        for (let j = 0; j < 8; j++) {
            if (buf[i + j] !== DEX_MAGIC[j]) { match = false; break; }
        }
        if (!match) continue;

        // 读 dex header: file_size 在 0x20
        if (i + 0x24 > buf.length) continue;
        const view = new DataView(buf.buffer, buf.byteOffset + i);
        const fileSize = view.getUint32(0x20, true);
        const headerSize = view.getUint32(0x24, true);
        // 合理性校验
        if (fileSize < 0x70 || fileSize > 50 * 1024 * 1024) continue;
        if (headerSize !== 0x70) continue;
        // 切片
        const slice = buf.slice(i, i + fileSize);
        hits.push({ offset: i, addr: baseAddr.add(i), size: fileSize, bytes: slice });
    }
    return hits;
}

function dumpDex(bytes, source) {
    const fname = OUT_DIR + 'scanned_' + Date.now() + '_' + Math.floor(Math.random() * 10000) + '.dex';
    try {
        const f = new File(fname, 'wb');
        f.write(bytes);
        f.close();
        console.log('[+] ' + source + ' -> ' + fname + ' (' + bytes.length + ' bytes)');
        return true;
    } catch (e) {
        console.log('[-] dump failed: ' + e.message);
        return false;
    }
}

let dumped = new Set();
let totalScanned = 0;

function scanAll() {
    const ranges = Process.enumerateRanges('r--');  // 只读段
    // 也可以 r-x 可执行段, 但通常 dex 落在 rw- 堆里
    console.log('[*] scanning ' + ranges.length + ' readable ranges...');
    for (const range of ranges) {
        if (range.size > 200 * 1024 * 1024) continue;  // 跳过超大段
        try {
            const buf = Memory.readByteArray(range.base, range.size);
            const u8 = new Uint8Array(buf);
            const hits = scanBuffer(u8, range.base);
            for (const h of hits) {
                const key = h.size + '_' + h.addr.toString();
                if (dumped.has(key)) continue;
                dumped.add(key);
                dumpDex(h.bytes, 'scan@' + h.addr + '+' + h.offset);
            }
            totalScanned += range.size;
        } catch (e) { /* skip unreadable */ }
    }
    console.log('[*] scanned ' + (totalScanned / 1024 / 1024).toFixed(1) + ' MB total');
}

// 每 3 秒扫一次, 持续 30 秒
let scanCount = 0;
const maxScans = 10;
const interval = setInterval(() => {
    scanAll();
    scanCount++;
    if (scanCount >= maxScans) {
        clearInterval(interval);
        console.log('[*] scan done, total dumped: ' + dumped.size);
    }
}, 3000);
