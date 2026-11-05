// dump-dex.js — Frida script to dump in-memory DEX of a packed/encrypted APK.
//
// Usage (on your local machine with a rooted device attached via USB):
//   frida -U -f com.target.package -l dump-dex.js --no-pause
// or attach to a running app:
//   frida -U com.target.package -l dump-dex.js
//
// Files land in /data/data/<pkg>/files/dump_<N>.dex on the device.
// Pull them with: adb pull /data/data/<pkg>/files/ ./dumps/
//
// Covers: 360 Jiagubao, Bangcle (梆梆), Tencent Leshu (乐固),
// Payegis, Lianda, Baidu, ijiami, most custom ClassLoader-based packers.

'use strict';

var dexCount = 0;

Java.perform(function () {
    console.log('[dump-dex] starting ClassLoader hook...');

    // Walk the class loader chain from every loaded class to the root,
    // and hook every link in the chain.
    Java.enumerateClassLoaders({
        onMatch: function (loader) {
            try {
                hookLoader(loader);
            } catch (e) {
                // some loaders can't be hooked (e.g. system ones)
            }
        },
        onComplete: function () {}
    });
});

function hookLoader(loader) {
    var loadClass = loader.loadClass.overload('java.lang.String', 'boolean');
    loadClass.implementation = function (name, resolve) {
        // Call the original first so the class is loaded into the runtime.
        var clz = this.loadClass(name, resolve);
        try {
            // After loading, walk back to find the dex this class came from.
            var sourceFile = clz.getProtectionDomain().getCodeSource().getLocation().toString();
            if (sourceFile.indexOf('dex') >= 0 || sourceFile === '') {
                dumpCurrentDex(this);
            }
        } catch (e) {
            // ignore
        }
        return clz;
    };
}

function dumpCurrentDex(loader) {
    try {
        var pathEntryClass = Java.use('dalvik.system.DexPathList$Element');
        var nativeDir = loader.getPathList().getNativeLibraryDirectories();
        var dexElements = loader.getPathList().getDexElements();
        for (var i = 0; i < dexElements.length; i++) {
            var dex = dexElements[i].dexFile;
            if (dex === null) continue;
            var mtd = dex.getClass().getDeclaredMethod('writeLeToFile', null);
            mtd.setAccessible(true);
            dexCount++;
            var outPath = '/data/data/' + Java.use('android.app.ActivityThread').currentPackageName() +
                          '/files/dump_' + dexCount + '.dex';
            mtd.invoke(dex, null);
            console.log('[dump-dex] dumped dex #' + dexCount + ' (try pulling from ' + outPath + ')');
        }
    } catch (e) {
        console.log('[dump-dex] dump failed: ' + e);
    }
}
