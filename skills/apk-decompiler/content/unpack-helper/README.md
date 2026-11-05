# Unpack / Defusion Helper

This directory contains Frida scripts and guides for unpacking packed/encrypted
APKs (加固应用). **You must run these on a real Android device** — the cloud
sandbox has no device, no adb, and no way to spawn the target app.

## Sandbox limitation

The Mavis sandbox is a Linux container with no Android device attached. It
can:

- ✅ Decompile ordinary APKs (already covered by `scripts/decompile.sh`).
- ✅ Take an *already-dumped* `.dex` and run jadx/baksmali/dex2jar on it.
- ❌ **Run a packed app to dump its in-memory DEX** — that needs `frida-server`
  on a USB-attached Android device with root.

## Workflow

1. **On your local machine (Mac/Linux with adb):**
   1. Install Frida tools: `pip install frida-tools`.
   2. Attach a rooted Android device (or emulator) over USB with USB debugging on.
   3. Push `frida-server` to the device (matching your device's arch):
      ```bash
      # Download from https://github.com/frida/frida/releases (pick your version)
      adb push frida-server /data/local/tmp/
      adb shell "chmod 755 /data/local/tmp/frida-server"
      adb shell "su -c /data/local/tmp/frida-server &"   # or: adb shell /data/local/tmp/frida-server &
      adb forward tcp:27042 tcp:27042
      ```
   4. Run the dump script against the target package:
      ```bash
      # Auto-detect: dump all dex loaded by ClassLoader
      frida -U -f com.target.package -l dump-dex.js --no-pause
      ```
   5. Pull the dumped `*.dex` files from the device:
      ```bash
      adb shell "find /data/data/com.target.package -name '*.dex' -exec cat {} \; > /sdcard/dump.bin"
      adb pull /sdcard/dump.bin ./dump.dex
      ```

2. **In the sandbox:**
   1. Upload `dump.dex` (or just the original APK) to your workspace.
   2. Treat the dumped dex as if it were the APK's dex:
      ```bash
      # Option A: just analyze the dumped dex directly
      bash scripts/decompile.sh --apk ./dump.dex --out /workspace/analysis

      # Option B: re-pack the dumped dex into the original APK and decompile
      # (preserves package context)
      # See: https://github.com/luoyesiqiu/DumpClass
      ```
   3. Then run the normal `scan.sh` + `package.sh` on the result.

## Files

| File | What it does |
|------|--------------|
| `dump-dex.js`  | Hooks `ClassLoader` to dump every loaded dex to a file. Works for most packers (Bangcle/Qihoo360/Tencent Leshu/Payegis/lianda/baidu/ijiami). |
| `dump-class.js` | Walks the loaded class list and forces each class to be initialised, which triggers packer-side decryption. |
| `frida-server-setup.sh` | One-shot helper to download the right frida-server binary for your device and push it via adb. |
