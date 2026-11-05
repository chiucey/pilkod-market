#!/usr/bin/env bash
# env-setup.sh — Install the Android decompiler toolchain under /opt.
# Idempotent. Re-run with FORCE=1 to force a fresh install.
#
# Tools installed:
#   - apktool 2.9.3            (APK → smali + resources + AndroidManifest)
#   - jadx 1.4.7               (Dex → Java; bundle ships its own bin/jadx)
#   - dex2jar 2.4              (Dex → JAR)
#   - cfr 0.152                (JAR → Java fallback decompiler)
#   - baksmali (shim)          (uses jadx's bundled baksmali-2.5.2.jar)
# Plus: reuses /opt/android-sdk/build-tools/{d8,dexdump,aapt,apksigner}
#       if android-apk-builder's env-setup.sh has been run already.
#
# Customise:
#   GH_MIRROR=https://gh-proxy.com bash env-setup.sh     # GitHub mirror
set -euo pipefail

PREFIX="${PREFIX:-/opt}"
TOOLS_DIR="$PREFIX/decompilers"
LOG_DIR="${LOG_DIR:-/workspace/.decompile-logs}"
GH_MIRROR="${GH_MIRROR:-}"  # e.g. https://gh-proxy.com (no trailing slash needed)

APKTOOL_VERSION="${APKTOOL_VERSION:-2.9.3}"
JADX_VERSION="${JADX_VERSION:-1.4.7}"
DEX2JAR_VERSION="${DEX2JAR_VERSION:-2.4}"
CFR_VERSION="${CFR_VERSION:-0.152}"

mkdir -p "$TOOLS_DIR/bin" "$TOOLS_DIR/lib" "$LOG_DIR"

# Colors
if [ -t 1 ]; then
  C_OK="\033[32m"; C_ERR="\033[31m"; C_DIM="\033[2m"; C_RST="\033[0m"
else
  C_OK=""; C_ERR=""; C_DIM=""; C_RST=""
fi
log()  { echo -e "${C_DIM}[env-setup]${C_RST} $*" >&2; }
ok()   { echo -e "${C_OK}[env-setup] ✓${C_RST} $*"; }
die()  { echo -e "${C_ERR}[env-setup] ✗ $*${C_RST}" >&2; exit 1; }

[ "$(id -u)" = 0 ] || die "Re-run as root. Tip: sudo -E bash env-setup.sh"

# Mirror-aware URL: prepend $GH_MIRROR/ if set when host is github.com.
gh() {
  local url="$1"
  if [ -n "$GH_MIRROR" ] && [[ "$url" == https://github.com/* ]]; then
    echo "${GH_MIRROR}/${url}"
  else
    echo "$url"
  fi
}

fetch() {
  local url="$1"; local out="$2"
  log "Downloading $(basename "$out") from ${url} ..."
  curl -fsSL --retry 3 --max-time 600 -o "$out" "$url" \
    || die "Failed to download $url"
}

# -------- 1. apktool --------
install_apktool() {
  if [ -x "$TOOLS_DIR/bin/apktool" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "apktool already at $TOOLS_DIR/bin/apktool"
  else
    local jar="$TOOLS_DIR/lib/apktool-${APKTOOL_VERSION}.jar"
    local url; url=$(gh "https://github.com/iBotPeaches/Apktool/releases/download/v${APKTOOL_VERSION}/apktool_${APKTOOL_VERSION}.jar")
    fetch "$url" "$jar"
    cat > "$TOOLS_DIR/bin/apktool" <<EOF
#!/usr/bin/env bash
exec /opt/openjdk-17/bin/java -jar $jar "\$@"
EOF
    chmod +x "$TOOLS_DIR/bin/apktool"
  fi
  "$TOOLS_DIR/bin/apktool" --version 2>&1 | head -1
}

# -------- 2. jadx --------
install_jadx() {
  if [ -x "$TOOLS_DIR/bin/jadx" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "jadx already at $TOOLS_DIR/bin/jadx"
  else
    local zip="$LOG_DIR/jadx-${JADX_VERSION}.zip"
    local url; url=$(gh "https://github.com/skylot/jadx/releases/download/v${JADX_VERSION}/jadx-${JADX_VERSION}.zip")
    fetch "$url" "$zip"
    local extract="$TOOLS_DIR/jadx-${JADX_VERSION}"
    rm -rf "$extract"
    mkdir -p "$extract"
    unzip -q "$zip" -d "$extract"
    # jadx zip extracts to <extract>/{bin,lib,README,...} — no outer wrapper dir.
    if [ ! -x "$extract/bin/jadx" ]; then
      die "jadx unpacked but $extract/bin/jadx not found"
    fi
    ln -sf "$extract/bin/jadx" "$TOOLS_DIR/bin/jadx"
  fi
  "$TOOLS_DIR/bin/jadx" --version 2>&1 | head -1
}

# -------- 3. dex2jar --------
install_dex2jar() {
  if [ -x "$TOOLS_DIR/bin/d2j-dex2jar" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "dex2jar already at $TOOLS_DIR/bin/d2j-dex2jar"
  else
    local zip="$LOG_DIR/dex2jar-${DEX2JAR_VERSION}.zip"
    local url; url=$(gh "https://github.com/pxb1988/dex2jar/releases/download/v${DEX2JAR_VERSION}/dex-tools-v${DEX2JAR_VERSION}.zip")
    fetch "$url" "$zip"
    local extract="$TOOLS_DIR/dex2jar-${DEX2JAR_VERSION}"
    rm -rf "$extract"
    mkdir -p "$extract"
    unzip -q "$zip" -d "$extract"
    # dex-tools zip extracts to <extract>/dex-tools-vX.Y/{d2j-*.sh,bin/dex-tools,...}
    # Find the dex-tools-vX.Y subdir and symlink every d2j-*.sh (without the .sh).
    local subdir; subdir=$(find "$extract" -mindepth 1 -maxdepth 1 -type d | head -1)
    [ -n "$subdir" ] || die "dex2jar unpacked but no subdir found in $extract"
    # Make all d2j-*.sh executable (zip may not preserve +x).
    find "$subdir" -maxdepth 1 -name "d2j-*.sh" -exec chmod +x {} \;
    for f in "$subdir"/d2j-*.sh; do
      [ -e "$f" ] || continue
      local name; name=$(basename "$f" .sh)
      ln -sf "$f" "$TOOLS_DIR/bin/$name"
    done
  fi
  "$TOOLS_DIR/bin/d2j-dex2jar" --help 2>&1 | head -1 || true
}

# -------- 4. cfr --------
install_cfr() {
  if [ -x "$TOOLS_DIR/bin/cfr" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "cfr already at $TOOLS_DIR/bin/cfr"
  else
    local jar="$TOOLS_DIR/lib/cfr-${CFR_VERSION}.jar"
    local url; url=$(gh "https://github.com/leibnitz27/cfr/releases/download/${CFR_VERSION}/cfr-${CFR_VERSION}.jar")
    fetch "$url" "$jar"
    cat > "$TOOLS_DIR/bin/cfr" <<EOF
#!/usr/bin/env bash
exec /opt/openjdk-17/bin/java -jar $jar "\$@"
EOF
    chmod +x "$TOOLS_DIR/bin/cfr"
  fi
  "$TOOLS_DIR/bin/cfr" --version 2>&1 | head -3
}

# -------- 5. baksmali (dex2jar's d2j-dex2smali under the hood) --------
# The standalone baksmali 2.5.2 jar from jadx's lib is library-only (no main
# class) and Guava 30 modular, so direct `java -jar` is fragile. We use the
# dex2jar project's d2j-dex2smali script instead — same baksmali code, just
# packaged with the right classpath, and it ships with dex2jar already.
install_baksmali() {
  local d2j_script="$TOOLS_DIR/dex2jar-${DEX2JAR_VERSION}/dex-tools-v${DEX2JAR_VERSION}/d2j-dex2smali.sh"
  if [ ! -x "$d2j_script" ]; then
    die "d2j-dex2smali.sh not found; install_dex2jar must run first"
  fi
  cat > "$TOOLS_DIR/bin/baksmali" <<EOF
#!/usr/bin/env bash
# Shim: forward to dex2jar's d2j-dex2smali (uses baksmali under the hood).
exec "$d2j_script" "\$@"
EOF
  chmod +x "$TOOLS_DIR/bin/baksmali"
  ok "baksmali installed (delegates to d2j-dex2smali)"
}

# Make sure JDK 17 is on PATH.
if [ ! -x /opt/openjdk-17/bin/java ]; then
  log "JDK 17 not found at /opt/openjdk-17. Installing via apt..."
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    openjdk-17-jdk-headless unzip curl >"$LOG_DIR/apt.log" 2>&1 \
    || { tail -40 "$LOG_DIR/apt.log" >&2; die "apt install failed"; }
  rm -f /opt/openjdk-17
  ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" /opt/openjdk-17
fi
export JAVA_HOME=/opt/openjdk-17
export PATH="$JAVA_HOME/bin:$PATH"

install_apktool
install_jadx
install_dex2jar
install_cfr
install_baksmali

# Persist env
cat > /etc/profile.d/decompile-env.sh <<EOF
export JAVA_HOME=/opt/openjdk-17
export PATH=$JAVA_HOME/bin:$TOOLS_DIR/bin:\$PATH
alias d2j='d2j-dex2jar'
EOF
chmod +x /etc/profile.d/decompile-env.sh

echo
ok "Decompiler toolchain ready."
echo "  apktool:    $TOOLS_DIR/bin/apktool"
echo "  jadx:       $TOOLS_DIR/bin/jadx"
echo "  dex2jar:    $TOOLS_DIR/bin/d2j-dex2jar"
echo "  cfr:        $TOOLS_DIR/bin/cfr"
echo "  baksmali:   $TOOLS_DIR/bin/baksmali"
echo "  Java:       $JAVA_HOME"
echo "  Logs:       $LOG_DIR"
echo "  Reload:     source /etc/profile.d/decompile-env.sh"
echo
echo "Also available (from android-apk-builder SDK):"
ls /opt/android-sdk/build-tools/34.0.0/{d8,dexdump,aapt,apksigner,zipalign} 2>/dev/null | sed 's|^|  |'
