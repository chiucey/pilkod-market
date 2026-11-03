#!/usr/bin/env bash
# decompile.sh — Full decompile pipeline for a single APK.
#   1. apktool    →  resources + AndroidManifest + smali
#   2. jadx       →  Java source (primary decompiler)
#   3. baksmali   →  smali (deepest layer; via d2j-dex2smali)
#   4. dex2jar    →  JAR (intermediate)
#   5. CFR        →  fallback Java source (off by default — heavy)
#
# Memory note: the sandbox is ~2 GB. jadx peaks at 1.5 GB, CFR peaks at 1 GB.
# Default options keep total under 2 GB. Use --with-cfr to add it.
#
# Usage:
#   decompile.sh --apk FILE --out DIR [--with-cfr] [--no-baksmali] [--no-apktool]
set -uo pipefail

APK=""; OUT=""
WITH_CFR=0
WITH_BAKSMALI=1
WITH_APKTOOL=1
JADX_HEAP="${JADX_HEAP:-1024m}"  # jadx Xmx; tune with JADX_HEAP=2048m

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apk)          APK="$2"; shift 2;;
    --out)          OUT="$2"; shift 2;;
    --with-cfr)     WITH_CFR=1; shift;;
    --no-cfr)       WITH_CFR=0; shift;;
    --no-baksmali)  WITH_BAKSMALI=0; shift;;
    --no-apktool)   WITH_APKTOOL=0; shift;;
    -h|--help)      sed -n '2,16p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$APK" ] || { echo "--apk is required" >&2; exit 2; }
[ -n "$OUT" ] || { echo "--out is required" >&2; exit 2; }
[ -f "$APK" ] || { echo "APK not found: $APK" >&2; exit 2; }

# Load env if present
[ -f /etc/profile.d/decompile-env.sh ] && source /etc/profile.d/decompile-env.sh
[ -f /etc/profile.d/android-build-env.sh ] && source /etc/profile.d/android-build-env.sh

APK_NAME=$(basename "$APK")
APK_STEM="${APK_NAME%.apk}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Pre-kill any leftover decompile processes from a previous aborted run.
# jadx/cfr/dex2jar hold files open; killing them lets `rm -rf` succeed.
pkill -9 -f jadx.cli 2>/dev/null || true
pkill -9 -f cfr-0     2>/dev/null || true
pkill -9 -f d2j-      2>/dev/null || true
pkill -9 -f apktool   2>/dev/null || true
sleep 1

# Best-effort clean; ignore errors (lock files from NFS-mounted dirs are common).
rm -rf "$OUT" 2>/dev/null || true
mkdir -p "$OUT"

# All temp work happens on local overlay fs (/opt/decompile-work) to dodge
# NFS lock issues, then we mv the final tree to $OUT. The user-facing $OUT
# stays on whatever fs the user passed (e.g. NAS /workspace).
WORK="/opt/decompile-work/$(date +%s)-$$"
mkdir -p "$WORK"
trap "rm -rf $WORK" EXIT

APKTOOL_DIR="$WORK/apktool"
JADX_DIR="$WORK/jadx"
BAKSMALI_DIR="$WORK/smali"
JAR_DIR="$WORK/jar"
CFR_DIR="$WORK/cfr"

echo "[decompile] APK:   $APK_NAME ($(du -h "$APK" | cut -f1))"
echo "[decompile] Out:   $OUT"
echo

# -------- 1. apktool --------
if [ "$WITH_APKTOOL" = 1 ]; then
  echo "[1/5] apktool ..."
  mkdir -p "$APKTOOL_DIR"
  if apktool d -f -o "$APKTOOL_DIR" "$APK" >"$WORK/apktool.log" 2>&1; then
    APKTOOL_SMALI_FILES=$(find "$APKTOOL_DIR" -name "*.smali" 2>/dev/null | wc -l)
    echo "      → $APKTOOL_SMALI_FILES smali files, AndroidManifest + res/"
  else
    echo "      ✗ apktool failed; see $WORK/apktool.log"
    tail -10 "$WORK/apktool.log" >&2
    APKTOOL_SMALI_FILES=0
  fi
else
  echo "[1/5] apktool skipped (--no-apktool)"
  APKTOOL_SMALI_FILES=0
fi
echo

# -------- 2. jadx: Java source (primary) --------
echo "[2/5] jadx (Java source, heap=$JADX_HEAP) ..."
mkdir -p "$JADX_DIR"
# JADX_OPTS env var is read by jadx's POSIX launcher; it sets -Xmx BEFORE
# the script's own DEFAULT_JVM_OPTS that uses MaxRAMPercentage=70. Without
# this override, jadx tries to use 70% of system RAM and OOMs in 2 GB sandboxes.
export JADX_OPTS="-Xmx$JADX_HEAP -Dfile.encoding=UTF-8 -XX:+UseG1GC"
# --no-res: skip resource decode (apktool did that)
# --no-imports: skip import generation (saves a lot of time on big APKs)
# --no-debug-info: skip .local/.param/.line directives
# --no-replace-consts: keep literal values verbatim (faster, slightly noisier)
# --escape-unicode: avoid mojibake in identifiers
# --show-bad-code: keep methods jadx couldn't fully recover
# --threads-count 2: gentle on a 2-core / 2 GB sandbox
timeout 240 jadx -d "$JADX_DIR" \
  --no-res --no-imports --no-debug-info --no-replace-consts \
  --escape-unicode --show-bad-code --threads-count 2 \
  "$APK" >"$WORK/jadx.log" 2>&1
JADX_RC=$?
if [ $JADX_RC -eq 0 ] || [ $JADX_RC -eq 124 ]; then
  # 124 = timeout — partial output is still useful
  JADX_JAVA_FILES=$(find "$JADX_DIR" -name "*.java" 2>/dev/null | wc -l)
  [ $JADX_RC -eq 124 ] && echo "      ⚠ jadx hit 240s timeout, keeping partial output"
else
  echo "      ✗ jadx failed (rc=$JADX_RC); tail of log:"
  tail -10 "$WORK/jadx.log" >&2
  JADX_JAVA_FILES=0
fi
echo "      → $JADX_JAVA_FILES Java files"
echo

# -------- 3. baksmali (deepest smali) --------
if [ "$WITH_BAKSMALI" = 1 ]; then
  echo "[3/5] baksmali (smali, via d2j-dex2smali) ..."
  mkdir -p "$BAKSMALI_DIR"
  local_dex_dir="$WORK/.dex"
  mkdir -p "$local_dex_dir"
  unzip -o -q "$APK" 'classes*.dex' -d "$local_dex_dir"
  for dex in "$local_dex_dir"/classes*.dex; do
    [ -f "$dex" ] || continue
    name=$(basename "$dex" .dex)
    baksmali disassemble "$dex" -o "$BAKSMALI_DIR/$name" >/dev/null 2>&1
  done
  rm -rf "$local_dex_dir"
  BAKSMALI_FILES=$(find "$BAKSMALI_DIR" -name "*.smali" 2>/dev/null | wc -l)
  echo "      → $BAKSMALI_FILES smali files"
else
  echo "[3/5] baksmali skipped (--no-baksmali)"
  BAKSMALI_FILES=0
fi
echo

# -------- 4. dex2jar --------
echo "[4/5] dex2jar (Dex → JAR) ..."
mkdir -p "$JAR_DIR"
local_dex_dir="$WORK/.dex_jar"
mkdir -p "$local_dex_dir"
unzip -o -q "$APK" 'classes*.dex' -d "$local_dex_dir"
JAR_COUNT=0
for dex in "$local_dex_dir"/classes*.dex; do
  [ -f "$dex" ] || continue
  name=$(basename "$dex" .dex)
  d2j-dex2jar -f -o "$JAR_DIR/${name}.jar" "$dex" >/dev/null 2>&1 && JAR_COUNT=$((JAR_COUNT+1))
done
rm -rf "$local_dex_dir"
echo "      → $JAR_COUNT JAR file(s) at $JAR_DIR/"
echo

# -------- 5. CFR (fallback) — off by default --------
if [ "$WITH_CFR" = 1 ]; then
  echo "[5/5] cfr (fallback Java source) ..."
  mkdir -p "$CFR_DIR"
  for jar in "$JAR_DIR"/*.jar; do
    [ -f "$jar" ] || continue
    name=$(basename "$jar" .jar)
    cfr "$jar" --outputdir "$CFR_DIR/$name" >/dev/null 2>&1 || true
  done
  CFR_FILES=$(find "$CFR_DIR" -name "*.java" 2>/dev/null | wc -l)
  echo "      → $CFR_FILES CFR fallback Java files"
else
  echo "[5/5] cfr skipped (use --with-cfr to enable; adds ~1 GB peak RAM)"
  CFR_FILES=0
fi
echo

# -------- Move to OUT --------
echo "[finalize] moving $WORK → $OUT ..."
# Move the subdirs we actually produced.
if [ "$WITH_APKTOOL" = 1 ] && [ -d "$APKTOOL_DIR" ]; then
  mv "$APKTOOL_DIR" "$OUT/apktool"
fi
if [ -d "$JADX_DIR" ]; then
  mv "$JADX_DIR" "$OUT/jadx"
fi
if [ "$WITH_BAKSMALI" = 1 ] && [ -d "$BAKSMALI_DIR" ]; then
  mv "$BAKSMALI_DIR" "$OUT/smali"
fi
if [ -d "$JAR_DIR" ]; then
  mv "$JAR_DIR" "$OUT/jar"
fi
if [ "$WITH_CFR" = 1 ] && [ -d "$CFR_DIR" ]; then
  mv "$CFR_DIR" "$OUT/cfr"
fi

# Pull package + version for the report header.
PKG=$(/opt/android-sdk/build-tools/34.0.0/aapt dump badging "$APK" 2>/dev/null \
      | head -1 | grep -oE "name='[^']+'" | head -1 | sed "s/name='//;s/'$//")
VER=$(/opt/android-sdk/build-tools/34.0.0/aapt dump badging "$APK" 2>/dev/null \
      | head -1 | grep -oE "versionName='[^']+'" | sed "s/versionName='//;s/'$//")
SDK_MIN=$(/opt/android-sdk/build-tools/34.0.0/aapt dump badging "$APK" 2>/dev/null \
          | grep -oE "sdkVersion:'[0-9]+'" | head -1 | grep -oE "[0-9]+")
SDK_TARGET=$(/opt/android-sdk/build-tools/34.0.0/aapt dump badging "$APK" 2>/dev/null \
             | grep -oE "targetSdkVersion:'[0-9]+'" | head -1 | grep -oE "[0-9]+")

cat > "$OUT/DECOMPILE_REPORT.md" <<EOF
# Decompile Report

- **APK**: $APK_NAME
- **Size**: $(du -h "$APK" | cut -f1)
- **Package**: $PKG
- **Version**: $VER
- **minSdk**: $SDK_MIN
- **targetSdk**: $SDK_TARGET
- **Decompiled at**: $TIMESTAMP

## Output Layout

| Path | Contents | Files |
|------|----------|------:|
| apktool/ | Resources + Manifest + apktool smali | $APKTOOL_SMALI_FILES |
| jadx/ | Java source (jadx, primary) | $JADX_JAVA_FILES |
| smali/ | baksmali smali (deepest) | $BAKSMALI_FILES |
| jar/ | dex2jar JAR (intermediate) | $JAR_COUNT |
| cfr/ | Fallback Java via CFR | $CFR_FILES |

## Tools used

- apktool 2.9.3
- jadx 1.4.7 (heap=$JADX_HEAP)
- baksmali (via dex2jar 2.4's d2j-dex2smali)
- dex2jar 2.4
- CFR 0.152 $([ "$WITH_CFR" = 1 ] && echo "(enabled)" || echo "(disabled)")

## Next steps

- \`bash scripts/scan.sh --in $OUT\` to surface URLs, API keys, dangerous permissions.
- \`bash scripts/package.sh --in $OUT --out /workspace/<name>.zip\` to ship.
- For packed/encrypted DEX (加固), see \`unpack-helper/\`.
EOF

echo
echo "═══════════════════════════════════════════════"
echo "  Decompile complete → $OUT"
echo "═══════════════════════════════════════════════"
echo "  apktool:    $APKTOOL_SMALI_FILES smali + resources + manifest"
echo "  jadx:       $JADX_JAVA_FILES Java files"
echo "  baksmali:   $BAKSMALI_FILES smali files"
echo "  dex2jar:    $JAR_COUNT JAR files"
echo "  cfr:        $CFR_FILES Java files"
echo "  Report:     $OUT/DECOMPILE_REPORT.md"
