#!/usr/bin/env bash
# frida-server-setup.sh — Helper to download & push frida-server to an
# Android device over USB. **Run this on your LOCAL machine**, not in the
# sandbox (the sandbox has no adb, no device).
#
# Usage:
#   ./frida-server-setup.sh [FRIDA_VERSION]   # default: detect from `frida --version`
set -euo pipefail

FRIDA_VERSION="${1:-}"
if [ -z "$FRIDA_VERSION" ]; then
  if command -v frida >/dev/null 2>&1; then
    FRIDA_VERSION=$(frida --version)
  else
    echo "frida not installed locally. Run: pip install frida-tools" >&2
    exit 1
  fi
fi

if ! command -v adb >/dev/null 2>&1; then
  echo "adb not in PATH. Install Android platform-tools." >&2
  exit 1
fi

# Detect device arch.
ARCH=$(adb shell getprop ro.product.cpu.abi)
case "$ARCH" in
  arm64-v8a)   FRIDA_ARCH="android-arm64";;
  armeabi-v7a) FRIDA_ARCH="android-arm";;
  x86_64)      FRIDA_ARCH="android-x86_64";;
  x86)         FRIDA_ARCH="android-x86";;
  *) echo "Unknown ABI: $ARCH" >&2; exit 1;;
esac

ASSET="frida-server-${FRIDA_VERSION}-${FRIDA_ARCH}.xz"
URL="https://github.com/frida/frida/releases/download/${FRIDA_VERSION}/${ASSET}"

TMP=$(mktemp -d)
cd "$TMP"
echo "[setup] downloading $URL ..."
curl -fsSL -o server.xz "$URL"

xz -d server.xz
chmod +x frida-server-${FRIDA_VERSION}-${FRIDA_ARCH}

echo "[setup] pushing frida-server to /data/local/tmp/ ..."
adb push frida-server-${FRIDA_VERSION}-${FRIDA_ARCH} /data/local/tmp/frida-server
adb shell "chmod 755 /data/local/tmp/frida-server"

echo "[setup] starting frida-server in background ..."
adb shell "/data/local/tmp/frida-server &"

echo "[setup] forwarding port 27042 ..."
adb forward tcp:27042 tcp:27042

echo
echo "✓ frida-server ${FRIDA_VERSION} is running on the device."
echo "Test it: frida-ps -U"
echo
echo "Now you can dump packed apps:"
echo "  frida -U -f com.target.package -l dump-dex.js --no-pause"
