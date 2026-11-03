// frida_hook_360.js — 360 加固 脱壳 hook 脚本
//
// 适配: 360 Jiagu v3.x - v5.x
// 策略: 三路 hook 兜底,任一触发即 dump
//   1) dalvik.system.InMemoryDexClassLoader.<init>  (API 28+)
//   2) art::DexFile::OpenMemory  (libart.so, Android 7-14 通用)
//   3) art::DexFile::OpenCommon  (libdexfile.so, Android 10+ 替代)
//
// 用法:
//   frida -U -f <pkg> -l frida_hook_360.js -l frida_anti_anti.js --no-pause
//
// 输出:
//   /data/data/<pkg>/files/<pkg>_<timestamp>_<idx>.dex

'use strict';

const PKG = '{{PKG}}';  // 替换为目标包名
const OUT_DIR = '/data/data/' + PKG + '/files/';

// 防止重复 hook
let dumpedKeys = new Set();

// dex 头校验
function isValidDex(buf) {
    if (!buf || buf.length < 8) return false;
    // dex\n035\0  (0x64 0x65 0x78 0x0a 0x30 0x33 0x35 0x00)
    return buf[0] === 0x64 && buf[1] === 0x65 && buf[2] === 0x78 &&
           buf[3] === 0x0a && buf[4] === 0x30 && buf[5] === 0x33 &&
           buf[6] === 0x35 && buf[7] === 0x00;
}

function dumpDex(bytes, source) {
    if (!isValidDex(bytes)) {
        console.log('[-] ' + source + ' got non-dex bytes, len=' + bytes.length);
        return;
    }
    // 用 dex 大小 + 首 4 字节当去重 key
    const key = bytes.length + '_' + bytes.slice(0, 4).join(',');
    if (dumpedKeys.has(key)) {
        console.log('[=] ' + source + ' dedup, len=' + bytes.length);
        return;
    }
    dumpedKeys.add(key);

    const ts = Date.now();
    const fname = OUT_DIR + 'dumped_' + ts + '_' + dumpedKeys.size + '.dex';
    const f = new File(fname, 'wb');
    f.write(bytes);
    f.close();
    console.log('[+] ' + source + ' dumped ' + bytes.length + ' bytes -> ' + fname);
}

// === Hook 1: InMemoryDexClassLoader (API 28+ 360 走这个) ===
function hookInMemoryDexClassLoader() {
    try {
        const IMCL = Java.use('dalvik.system.InMemoryDexClassLoader');
        // 多种构造器重载
        const overloads = IMCL.$init.overloads;
        for (const ov of overloads) {
            ov.implementation = function () {
                // 调用原始方法
                const ret = ov.apply(this, arguments);
                // 参数里找 byte[] / ByteBuffer
                for (let i = 0; i < arguments.length; i++) {
                    const a = arguments[i];
                    if (a === null || a === undefined) continue;
                    const t = a.constructor?.class?.getName?.() || '';
                    if (t === '[B' || t.endsWith('ByteBuffer')) {
                        let bytes;
                        try {
                            if (t === '[B') {
                                bytes = a;  // Java.array(byte)
                            } else {
                                // ByteBuffer
                                const cap = a.capacity();
                                bytes = new Array(cap);
                                for (let j = 0; j < cap; j++) bytes[j] = a.get(j);
                            }
                        } catch (e) { continue; }
                        dumpDex(bytes, 'InMemoryDexClassLoader[' + i + ']');
                    }
                }
                return ret;
            };
        }
        console.log('[+] Hooked InMemoryDexClassLoader');
    } catch (e) {
        console.log('[-] InMemoryDexClassLoader hook failed: ' + e.message);
    }
}

// === Hook 2: art::DexFile::OpenMemory (Android 7-14 通用) ===
function hookOpenMemory() {
    try {
        const exports = Module.enumerateExports('libart.so');
        for (const exp of exports) {
            if (exp.name.indexOf('DexFile') >= 0 && exp.name.indexOf('OpenMemory') >= 0) {
                Interceptor.attach(exp.address, {
                    onEnter(args) {
                        // OpenMemory(const uint8_t* base, size_t size, ...)
                        this.base = args[0];
                        this.size = args[1]?.toInt32?.() || 0;
                    },
                    onLeave() {
                        if (this.base && this.size > 0) {
                            try {
                                const bytes = Memory.readByteArray(this.base, this.size);
                                dumpDex(bytes, 'libart.so:OpenMemory');
                            } catch (e) { /* ignore */ }
                        }
                    }
                });
                console.log('[+] Hooked libart.so ' + exp.name);
            }
        }
    } catch (e) {
        console.log('[-] OpenMemory hook failed: ' + e.message);
    }
}

// === Hook 3: art::DexFile::OpenCommon (libdexfile.so Android 10+) ===
function hookOpenCommon() {
    try {
        const exports = Module.enumerateExports('libdexfile.so');
        for (const exp of exports) {
            if (exp.name.indexOf('DexFile') >= 0 && exp.name.indexOf('OpenCommon') >= 0) {
                Interceptor.attach(exp.address, {
                    onEnter(args) {
                        this.base = args[0];
                        this.size = args[1]?.toInt32?.() || 0;
                    },
                    onLeave() {
                        if (this.base && this.size > 0) {
                            try {
                                const bytes = Memory.readByteArray(this.base, this.size);
                                dumpDex(bytes, 'libdexfile.so:OpenCommon');
                            } catch (e) { /* ignore */ }
                        }
                    }
                });
                console.log('[+] Hooked libdexfile.so ' + exp.name);
            }
        }
    } catch (e) {
        console.log('[-] OpenCommon hook failed: ' + e.message);
    }
}

// === Hook 4: art::DexFile::Create (Android 12+) ===
function hookCreate() {
    try {
        const exports = Module.enumerateExports('libdexfile.so');
        for (const exp of exports) {
            if (exp.name.indexOf('DexFile') >= 0 && exp.name.indexOf('Create') >= 0
                && exp.name.indexOf('Open') < 0) {
                Interceptor.attach(exp.address, {
                    onEnter(args) {
                        // 第一个参数通常就是 const uint8_t* base
                        this.base = args[0];
                    },
                    onLeave() {
                        if (this.base) {
                            try {
                                // 读 dex 头拿到 size
                                const fileSize = Memory.readU32(this.base.add(0x20));
                                if (fileSize > 0 && fileSize < 100 * 1024 * 1024) {
                                    const bytes = Memory.readByteArray(this.base, fileSize);
                                    dumpDex(bytes, 'libdexfile.so:Create');
                                }
                            } catch (e) { /* ignore */ }
                        }
                    }
                });
                console.log('[+] Hooked libdexfile.so ' + exp.name);
            }
        }
    } catch (e) {
        console.log('[-] Create hook failed: ' + e.message);
    }
}

Java.perform(function () {
    console.log('[*] 360 hook init, pkg=' + PKG);
    // 1. 等 libart / libdexfile 加载后再 hook
    const waitForLibart = setInterval(() => {
        if (Process.findModuleByName('libart.so') || Process.findModuleByName('libdexfile.so')) {
            clearInterval(waitForLibart);
            console.log('[*] libart/libdexfile loaded');
            hookOpenMemory();
            hookOpenCommon();
            hookCreate();
        }
    }, 200);

    // 2. Java 层 hook 不依赖 so 加载,直接挂
    hookInMemoryDexClassLoader();
});
