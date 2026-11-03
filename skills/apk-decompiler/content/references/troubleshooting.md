# Troubleshooting

## Install / Environment

### `Failure writing output to destination` during env-setup
Sandbox ran out of `/opt` space, or the target directory was missing.
Check:
```bash
df -h /opt
ls -la /opt/decompilers  # should exist with bin/ and lib/ subdirs
```
Re-run with `FORCE=1` to retry any component.

### GitHub raw download times out (no progress)
Set `GH_MIRROR=https://gh-proxy.com bash env-setup.sh` — the script
auto-prepends this for any URL starting with `https://github.com/`.

### `baksmali: no main manifest attribute`
Means the script's `baksmali` shim is pointing at the baksmali 2.5.2
*library* jar (no main class) instead of `d2j-dex2smali.sh`. The
`env-setup.sh` install function should set this up correctly; if you
see this error, re-run:
```bash
bash /workspace/.skills/apk-decompiler/scripts/env-setup.sh
```

## Decompile

### `Java heap space` / `OutOfMemoryError` in jadx
The sandbox is 2 GB and jadx peak is 1.5 GB. Try:
```bash
# Lower heap (faster, fewer classes decompiled before OOM)
JADX_HEAP=600m bash scripts/decompile.sh --apk X --out Y

# Higher heap (only if your sandbox has >3 GB RAM)
JADX_HEAP=2000m bash scripts/decompile.sh --apk X --out Y
```
Partial output is still useful — apktool always completes.

### jadx finishes but only 5k java files when you expected 30k
That's the partial-output case. The script keeps what jadx produced.
To get the rest, run jadx again with more heap on a beefier machine
or wait — jadx's progress log shows `progress: N of M` so you can see
how far it got.

### `apktool` hangs forever
The `apktool` Java process is being held open by a zombie parent or an
NFS file lock. Kill it:
```bash
pkill -9 -f apktool
pkill -9 -f java
sleep 2
rm -rf <out>     # if rm fails, retry after a longer sleep
```

## Scan

### Scan finds 0 of everything on a clearly active app
Either the decompile tree is too small (jadx OOM'd) or your grep can't
follow NFS symlinks. The skill uses a `tar | tar` mirror to local fs
specifically to dodge that — but if you invoke `scan.sh` on a directory
that's *not* the standard `<out>/`, double-check the source path.

To re-scan on a fresh APK:
```bash
# Remove stale SCAN_REPORT.*
rm <out>/SCAN_REPORT.*
bash scripts/scan.sh --in <out>
```

### `Severity: 🔴 HIGH` for a perfectly innocent app
Check what triggered it. Common false positives:
- Compose / AndroidX string-table URLs (`https://youtrack.jetbrains.com/...`,
  `https://goo.gle/compose-feedback`)
- AWS-like hex strings inside the dex that aren't actually AWS keys
- `setJavaScriptEnabled` in WebView library code, not your app

Open the report and confirm the matches are in *your* package, not in
a vendored library.

## Package

### `zip error: Invalid command arguments (bad split size: 'tore')`
Your local `zip` is too old. Refresh:
```bash
apt-get install -y zip
```

### Output zip is huge (no compression)
You're using default `store` mode. Add `--deflate` if you want gzip-like
compression — but for already-compressed dex/jar content it's only
marginally smaller and takes much longer.

## Sandbox-specific

### `Cannot delete file: .../test-counter/.gradle/.../buildOutputCleanup/.nfs...`
Same as the `android-apk-builder` skill: stale Gradle daemon holds NFS
lock files. Fix:
```bash
pkill -9 -f GradleDaemon
sleep 2
rm -rf <stale-dir>
```

### Output directory accumulates `__MACOSX/` files
You're zipping on macOS. Switch to Linux or pass `-MM` to `zip` (not
exposed via this script — re-zip manually if needed).

## Frida / Unpacking

### `frida-server` version mismatch
The local `frida` Python tool and the on-device `frida-server` must be
the same version. `frida-server-setup.sh` reads `frida --version` and
downloads the matching binary; if you upgrade frida-tools, re-run it.

### `Failed to spawn: unable to connect to remote frida-server`
```bash
adb shell "su -c pkill frida-server" 2>/dev/null || adb shell pkill frida-server
adb shell "/data/local/tmp/frida-server &"
adb forward tcp:27042 tcp:27042
```

### Dumped `dump_*.dex` are all `classes.dex`-shaped but the apktool output is tiny
The packer is using *class-level* encryption. After dumping, also run
`unpack-helper/dump-class.js` which forces every loaded class to be
initialised, triggering the packer's class-by-class decryption path.
