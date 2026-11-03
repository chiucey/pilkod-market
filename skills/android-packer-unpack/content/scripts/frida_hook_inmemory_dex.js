// frida_hook_inmemory_dex.js — 通用兜底 hook (只挂 InMemoryDexClassLoader)
//
// 适合: 任何加固,只要解密的 dex 走 InMemoryDexClassLoader 加载
// 不依赖 so 符号,适合对加固内部结构不熟时的第一选择
//
// 用法:
//   frida -U -f <pkg> -l frida_hook_inmemory_dex.js --no-pause

'use strict';

const PKG = '{{PKG}}';
const OUT_DIR = '/data/data/' + PKG + '/files/';

let dumpedKeys = new Set();

function isValidDex(buf) {
    return buf && buf.length >= 8 &&
           buf[0] === 0x64 && buf[1] === 0x65 && buf[2] === 0x78 &&
           buf[3] === 0x0a && buf[4] === 0x30 && buf[5] === 0x33 &&
           buf[6] === 0x35 && buf[7] === 0x00;
}

function dumpDex(bytes, source) {
    if (!isValidDex(bytes)) return;
    const key = bytes.length + '_' + Array.from(bytes.slice(0, 4)).join(',');
    if (dumpedKeys.has(key)) return;
    dumpedKeys.add(key);
    const fname = OUT_DIR + 'dumped_' + Date.now() + '_' + dumpedKeys.size + '.dex';
    const f = new File(fname, 'wb');
    f.write(bytes);
    f.close();
    console.log('[+] ' + source + ' -> ' + fname + ' (' + bytes.length + ' bytes)');
}

Java.perform(function () {
    try {
        const IMCL = Java.use('dalvik.system.InMemoryDexClassLoader');
        IMCL.$init.overloads.forEach(function (ov) {
            ov.implementation = function () {
                const ret = ov.apply(this, arguments);
                for (let i = 0; i < arguments.length; i++) {
                    const a = arguments[i];
                    if (!a) continue;
                    const t = a.$className || '';
                    if (t === 'java.nio.ByteBuffer') {
                        // ByteBuffer
                        try {
                            const cap = a.capacity();
                            if (cap > 0x10000 && cap < 50 * 1024 * 1024) {
                                const arr = [];
                                for (let j = 0; j < cap; j++) arr.push(a.get(j));
                                dumpDex(arr, 'InMemoryDexClassLoader:ByteBuffer[' + i + ']');
                            }
                        } catch (e) { /* */ }
                    } else if (a.length !== undefined && typeof a.length === 'number' && a.length > 0x10000) {
                        // 可能是 byte[] — 但只有当它是 Java 数组才安全
                        // 用更严格判断: 在 Frida 中,Java byte[] 会被 proxy 为带 .length 的对象
                        try {
                            const sample = Java.array('byte', []);
                            if (a.$className === '[B' || (a.length > 0 && a[0] >= 0 && a[0] <= 255)) {
                                const arr = [];
                                for (let j = 0; j < a.length; j++) arr.push(a[j]);
                                dumpDex(arr, 'InMemoryDexClassLoader:byte[][' + i + ']');
                            }
                        } catch (e) { /* */ }
                    }
                }
                return ret;
            };
        });
        console.log('[+] Hooked InMemoryDexClassLoader (all overloads)');
    } catch (e) {
        console.log('[-] hook failed: ' + e.message);
    }
});
