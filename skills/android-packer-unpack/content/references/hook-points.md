# Hook 点详解

加固壳再严密, 解密的 dex 必然要交给 ART runtime, 这一步有固定的 API 调用点。我们就在这里截胡。

## Hook 点优先级

按**通用性 / 成功率**排序, 优先用前面的:

### 1. dalvik.system.InMemoryDexClassLoader (API 28+, 推荐)

**触发时机**: dex 解密到内存后, 准备装载进 ClassLoader 时
**成功率**: 90%
**适配**: Android 9 (Pie) 及以上, 360 v4+ 默认走这个
**优势**: Java 层 hook, 不需要管 native 符号名, 不会因 Android 版本变符号名而失效

**构造器重载**:
```java
// API 28+
public InMemoryDexClassLoader(ByteBuffer buffer, ClassLoader parent)
// API 28+
public InMemoryDexClassLoader(ByteBuffer[] buffers, ClassLoader parent)
// API 28+ (Android 14)
public InMemoryDexClassLoader(ByteBuffer buffer, String libraryPath, ClassLoader parent)
```

**完整 hook 模板**: 见 `scripts/frida_hook_360.js` 的 `hookInMemoryDexClassLoader`

**注意事项**:
- `ByteBuffer.capacity()` 拿到大小
- 用 `get(i)` 一个一个读 (Frida 中 ByteBuffer 不能直接当 byte[] 用)
- 检查 magic 防止把空 buffer 当成 dex 写盘

### 2. art::DexFile::OpenMemory (libart.so, Android 7-14)

**触发时机**: native 层把 byte 数组构造成 DexFile 对象时
**成功率**: 95%
**适配**: Android 7.0 - 14

**符号名** (C++ Name Mangling, 不同版本不同):
```
Android 7-9  : _ZN3art7DexFile10OpenMemoryEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEEjPNS_6MemMapEPKNS_10OatDexFileEPS9_
Android 10-13: 移到 libdexfile.so, 符号名同
Android 14+  : 同上
```

**简化做法**: 用 `Module.enumerateExports('libart.so')` 模糊匹配:
```javascript
const exports = Module.enumerateExports('libart.so');
for (const exp of exports) {
    if (exp.name.indexOf('DexFile') >= 0 && exp.name.indexOf('OpenMemory') >= 0) {
        Interceptor.attach(exp.address, { ... });
    }
}
```

**参数解析** (OpenMemory):
- `arg[0]`: const uint8_t* base — dex 字节流起始地址
- `arg[1]`: size_t size — dex 字节流大小

**优势**: 90% 加固 (360 v3-v5 / 乐固 / 梆梆 / 爱加密) 都走这个, 是兜底
**劣势**: 不同 Android 版本符号名不一样, 需要模糊匹配

### 3. art::DexFile::OpenCommon (libdexfile.so, Android 10+)

**触发时机**: OpenCommon 是 OpenMemory 的替代接口
**成功率**: 90%
**适配**: Android 10+

**符号**:
```
_ZN3art13DexFileLoader10OpenCommonEPKhmRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEES8_jPNS_6MemMapEPS9_
```

**用法**: 同 OpenMemory, 模糊匹配即可

### 4. art::DexFile::Create (Android 12+)

**触发时机**: ART 7.0+ 引入的统一构造器
**成功率**: 85%

**符号**:
```
_ZN3art7DexFile6CreateEPKhjRKNSt3__112basic_stringIcNS3_11char_traitsIcEENS3_9allocatorIcEEEES8_jPNS_6MemMapEPKNS_10OatDexFileEPNS_13DexFileLoaderEPS9_
```

**注意**: 不是所有 Android 12 设备都走 Create, OpenCommon 仍是主流

### 5. BaseDexClassLoader.findClass (兜底, 慎用)

**触发时机**: 类查找时
**成功率**: 60%
**问题**:
- 易触发加固反 hook (有些加固会重写 findClass, 加检测)
- 一次只能拿到一个类, 不是完整 dex
- 拿到的 dex 字节流可能不完整

**仅当其他 hook 点都失败时用**

### 6. 内存 dex 魔数扫描 (终极兜底)

**原理**: 加固再严密, dex 字节流总要短暂以明文形态落在某块内存里
**成功率**: 99% (只要 dex 在内存里, 就一定能找到)
**劣势**: 慢 (全内存扫一遍几秒到几十秒), 误报多 (可能有 .dex 缓存)

**扫描流程**:
```javascript
const ranges = Process.enumerateRanges('r--');  // 只读段
for (const range of ranges) {
    if (range.size > 200 * 1024 * 1024) continue;  // 跳过超大段
    const buf = Memory.readByteArray(range.base, range.size);
    // 在 buf 中搜 dex\n035\0
    // 命中后按 0x20 处的 file_size 切片
}
```

**完整代码**: 见 `scripts/frida_dex_scanner.js`

### 7. libjiagu.so 导出函数 (360 特定)

**适用**: 知道是 360 加固, 想直接抓 native 解密函数
**符号** (版本敏感, 不同 360 版本名不同):
- `Java_com_qihoo_util_DexHelper_decryptDex`
- `jiagu_decrypt`
- `decodeDex`
- `getOriginalDex`

**做法**: IDA 看 `libjiagu_*.so` 的 Exports, 反编译找关键函数, Frida `Interceptor.attach` 拦截

**劣势**: 符号版本敏感, 360 每次升级都换符号名, 需要每个版本单独适配

---

## 推荐组合策略

不同加固类型用不同 hook 组合:

| 加固类型 | Hook 组合 |
|---------|----------|
| 360 v3 | OpenMemory + 内存魔数扫描 |
| 360 v4 | InMemoryDexClassLoader + OpenMemory |
| 360 v5 | 内存魔数扫描 + libjiagu 导出函数 |
| 乐固 v2-v3 | OpenMemory + 内存魔数扫描 |
| 乐固 VMP | 内存魔数扫描 (全内存扫) |
| 梆梆 | InMemoryDexClassLoader + 内存魔数扫描 |
| 爱加密 | OpenMemory + 内存魔数扫描 |
| 百度 | OpenMemory |
| 自研 | 内存魔数扫描 (不知道 hook 点就扫) |

---

## 时机问题

Hook 时机比 hook 点更重要:

- ❌ **太早**: `libart.so` 还没加载, 符号解析不到
- ❌ **太晚**: dex 已经被 classLinker 处理过, hook 不到原始字节流
- ✅ **正确时机**: libart/libdexfile 加载完成 + 加固壳刚解密完 + classLinker 还没消费

**推荐触发方式**:
1. **`android_dlopen_ext` hook**: 监听到 `libart.so` 加载, 再挂 `OpenMemory`
2. **`Process.findModuleByName` 轮询**: 每 200ms 查一次, 找到就 hook
3. **用户手动触发**: 让 app 进主页面后, 再 attach frida

**示例** (frida_hook_360.js 中已用):
```javascript
const waitForLibart = setInterval(() => {
    if (Process.findModuleByName('libart.so') || Process.findModuleByName('libdexfile.so')) {
        clearInterval(waitForLibart);
        hookOpenMemory();
        hookOpenCommon();
        hookCreate();
    }
}, 200);
```

---

## 调试技巧

- **log 每个 hook 的命中**: 在 onLeave 里 console.log, 看到底是哪个 hook 点先触发
- **检查 hook 到的字节流前 8 字节**: 应该是 `64 65 78 0a 30 33 35 00` (dex\n035\0)
- **检查 0x20 处 file_size**: 0x70 以上 (最小 dex), 不超过 50MB (合理上限)
- **看 console 输出识别加固**: console 出现 `jiagu` / `tup` / `secexe` 关键字, 确认 hook 的是哪个
- **dump 多份去重**: 用 sha1 或 (size + 前 4 字节) 去重, 避免同一 dex 被 dump 多次
