---
name: apk-decompiler
description: Decompile, scan, and package any Android APK from one command. Produces Java source (jadx), smali (apktool + baksmali), resources, AndroidManifest, and an automated security report (hardcoded URLs, API keys, dangerous permissions, embedded SDKs, WebView/crypto issues). Includes Frida scripts for unpacking encrypted/packed APKs (加固). Use when the user wants to decompile, analyze, audit, or reverse-engineer an APK — whether their own, a competitor's, or a security review target. Do NOT use for iOS apps, web apps, or building APKs from source (use the android-apk-builder skill for that).
---

# Android APK Decompiler

Take an APK → get readable Java source, smali, resources, and a security
report. The skill owns the full chain: tool install → decompile → scan → package.

## Triggers

Activate when the user says any of:
- "反编译这个 APK / 看看这个 app 的代码"
- "Decompile / unpack / analyze this APK"
- "我看一下 / 看看 XXX 怎么实现的"
- "我要脱壳 / 解加固 / 解 360/梆梆/爱加密"
- "扫描硬编码的 URL/API key"
- "分析这个 APK 里有什么 SDK"

Do **not** activate for:
- Building APKs from source → `android-apk-builder` skill
- iOS apps (no IPA support in this sandbox)
- Web apps / websites
- Running the app — this skill produces static analysis, not a runnable build

## Required Inputs

| Input | Required? | Default |
|---|---|---|
| APK file path | yes | — |
| Output dir | yes | — |
| Run scan after? | no | yes |
| Output format | no | "store" zip (默认无压缩) |

If the user gives a single APK file, accept it directly. If they reference
"these 5 APKs in /workspace/apks", use batch mode.

## Pipeline

Run scripts in this order. First install is expensive (3-5 min, ~250 MB);
the rest are minutes per APK and idempotent.

```bash
# 1. Install the decompiler toolchain under /opt (idempotent).
#    First run: 3-5 min (downloads ~250 MB from GitHub via gh-proxy.com mirror).
#    Warm run:  <5 s.
GH_MIRROR=https://gh-proxy.com bash scripts/env-setup.sh

# 2. Decompile one APK.
#    First decompile: 2-5 min (jadx in 2 GB sandbox may OOM and produce
#    partial output — that's expected; apktool output is always complete).
bash scripts/decompile.sh \
  --apk /path/to/target.apk \
  --out /workspace/target_decompiled

# 3. (Optional) Run the security scan.
#    1-3 min on a medium APK; uses local-fs mirror to dodge NFS slow grep.
bash scripts/scan.sh --in /workspace/target_decompiled

# 4. Package the decompile tree.
#    Default: zip -0 store (无压缩, 仅存储模式).
bash scripts/package.sh --in /workspace/target_decompiled
# Add --deflate to compress; --pass PWD to encrypt.

# 5. Batch mode (many APKs at once).
bash scripts/batch.sh --in /workspace/apks --out /workspace/all_decompiled --with-scan
```

## Output Contract

After a single-APK run, deliver:

```
<deliver-assets>
<media type="file" src="<out>-store.zip" caption="Decompiled APK source (zip -0 仅存储模式)" />
<media type="file" src="<out>/SCAN_REPORT.md" caption="Security scan (markdown)" />
<media type="file" src="<out>/SCAN_REPORT.json" caption="Security scan (machine-readable)" />
<media type="file" src="<out>/DECOMPILE_REPORT.md" caption="Decompile summary" />
</deliver-assets>
```

`<out>` is whatever path the user asked for (typically `/workspace/<name>`).
The default zip output is `<out>-store.zip`.

For batch mode, point at `BATCH_REPORT.md` and the per-APK subdirs.

## What the scan catches

| Severity | Trigger |
|---|---|
| 🔴 HIGH | Any leaked AWS / Google / private key, JWT, weak crypto (DES/RC4/MD5), or >5 dangerous permissions |
| 🟡 MED | Any dangerous permission, WebView with `setJavaScriptEnabled` / `addJavascriptInterface`, >20 unique URLs, >3 third-party SDKs |
| 🟢 LOW | None of the above |

The report lists:
- Top 50 unique URLs (filtering out well-known schema URLs)
- AWS Access Keys (`AKIA[0-9A-Z]{16}`) and Google API Keys (`AIza[35]`)
- Private-key PEM blocks, JWT tokens, generic `secret=/api_key=/token=…` lines
- 18 named dangerous Android permissions
- 30+ third-party SDK fingerprints (Tencent, Alibaba, ByteDance, Firebase, ...)
- WebView with JavaScript bridges
- Weak crypto primitives
- Files that opt into cleartext HTTP

## Output Layout (single APK)

```
target_decompiled/
├── apktool/                    # 资源 + Manifest + apktool smali (always complete)
│   ├── AndroidManifest.xml
│   ├── res/
│   └── smali/                  # + smali_classes2/, smali_classes3/ for multidex
├── jadx/                       # Java source (may be partial if OOM)
│   └── sources/
├── smali/                      # baksmali smali (deepest layer)
│   └── classes/                # + classes2/, classes3/ for multidex
├── jar/                        # dex2jar JAR (intermediate, for CFR or diffing)
│   ├── classes.jar
│   └── classes2.jar
├── cfr/                        # CFR fallback Java (only if --with-cfr)
├── DECOMPILE_REPORT.md         # decompile summary
├── SCAN_REPORT.md              # security scan (after scan.sh)
└── SCAN_REPORT.json            # machine-readable scan
```

## Failure Handling

- **Jadx hits Java heap OOM** in 2 GB sandboxes on large APKs (>5k classes).
  The script keeps partial output. To recover, drop `--with-baksmali` (you
  already have apktool smali) and re-run with `JADX_HEAP=600m` (lower) or
  `JADX_HEAP=1500m` if you have a bigger sandbox.
- **`zip error: Invalid command arguments (bad split size: 'tore')`** —
  this is fixed in current script. If it ever returns, your `zip` is
  ancient; `apt install zip` to refresh.
- **APK is packed/encrypted (加固)** — apktool will give you a stub
  AndroidManifest and ~10 small smali files. That's the *packer*'s code.
  The real DEX is decrypted in memory at runtime. Use `unpack-helper/`:
  see `unpack-helper/README.md` for the workflow.
- **Sandbox can't reach dl.google.com / github.com** — set
  `GH_MIRROR=https://gh-proxy.com` before `env-setup.sh`.
- **`apktool` shows "permission denied" mid-run** — kill any zombie
  `apktool` / `jadx` / `java` processes (`pkill -9 -f java`) and retry.
  This is the same NFS-lock issue `android-apk-builder` documents; the
  workaround is identical.

## Memory Limits (2 GB sandbox)

Tools peak at these memory levels; never run jadx + CFR simultaneously
in a 2 GB sandbox:

| Tool | Peak RAM |
|---|---|
| apktool 2.9.3 | ~300 MB |
| jadx 1.4.7    | 1.0–1.5 GB (configurable via `JADX_HEAP`) |
| dex2jar 2.4   | ~600 MB |
| baksmali 2.5.2| ~400 MB |
| CFR 0.152     | ~1.0 GB (off by default — pass `--with-cfr` to enable) |

If you need CFR output, run decompile twice: once without, once with
`--with-cfr --no-jadx --no-apktool --no-baksmali`.

## Scope Boundaries (MVP)

The skill does **static** analysis well. **Dynamic** (running the app,
intercepting network, dumping in-memory state) requires a real device
with frida-server — see `unpack-helper/README.md` for the bridge.

Out of scope for v1 (escalate to the user before adding):
- Frida server install in-sandbox (no device attached)
- Automatic packer identification (currently requires the user to look
  at the apktool output and pick the right unpacker)
- DEX deobfuscation (string encryption, control-flow flattening,
  identifier renaming) — use [DexGuard](https://github.com/xxkfqz/dexguard)
  or [simplify](https://github.com/CalebFenton/simplify) externally.
- Native (`.so`) library analysis — use Ghidra / IDA locally.

## When the user wants to "解加固"

1. Tell them: this requires a real Android device with USB debugging on,
   which the sandbox doesn't have.
2. Give them `unpack-helper/frida-server-setup.sh` (run on their local
   machine with the device attached).
3. Give them `unpack-helper/dump-dex.js` (Frida script to run after).
4. After they pull the dumped `*.dex` files, take the dump as if it were
   the original APK and run the normal `decompile.sh` + `scan.sh` flow.
