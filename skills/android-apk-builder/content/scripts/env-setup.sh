#!/usr/bin/env bash
# env-setup.sh — Install JDK 17, Android SDK, and one or more Gradle versions
# under /opt. Idempotent. Re-run with FORCE=1 to force-reinstall any component.
#
# Customise versions:
#   GRADLE_VERSIONS="8.9 8.7 8.4 7.6.4" bash env-setup.sh
#   BUILD_TOOLS_VER=35.0.0 PLATFORM_VER=android-35 bash env-setup.sh
#   APT_MIRROR=https://your-mirror/debian bash env-setup.sh
#   GRADLE_MIRROR=https://your-mirror/gradle bash env-setup.sh
set -euo pipefail

PREFIX="${PREFIX:-/opt}"
JDK_DIR="${JDK_DIR:-$PREFIX/openjdk-17}"
ANDROID_SDK_DIR="${ANDROID_SDK_DIR:-$PREFIX/android-sdk}"
LOG_DIR="${LOG_DIR:-/workspace/.android-build-logs}"
BUILD_TOOLS_VER="${BUILD_TOOLS_VER:-34.0.0}"
PLATFORM_VER="${PLATFORM_VER:-android-34}"
# Default set covers AGP 7.x → 8.5+ projects.
GRADLE_VERSIONS="${GRADLE_VERSIONS:-8.9 8.7 8.4 7.6.4}"

mkdir -p "$LOG_DIR"

# Colors (degrade gracefully if not a TTY)
if [ -t 1 ]; then
  C_OK="\033[32m"; C_ERR="\033[31m"; C_DIM="\033[2m"; C_RST="\033[0m"
else
  C_OK=""; C_ERR=""; C_DIM=""; C_RST=""
fi
log()  { echo -e "${C_DIM}[env-setup]${C_RST} $*" >&2; }
ok()   { echo -e "${C_OK}[env-setup] ✓${C_RST} $*"; }
die()  { echo -e "${C_ERR}[env-setup] ✗ $*${C_RST}" >&2; exit 1; }

[ "$(id -u)" = 0 ] || die "Re-run as root. Tip: sudo -E bash env-setup.sh"

# -------- 0. APT sources (auto-fallback) --------
ensure_apt_sources() {
  if [ -f /etc/os-release ] && grep -q 'ID=debian' /etc/os-release; then
    if apt-get update -qq 2>&1 | grep -q "Failed to fetch\|Could not connect"; then
      local mirror="${APT_MIRROR:-https://mirrors.tuna.tsinghua.edu.cn/debian}"
      log "Default APT sources unreachable. Falling back to $mirror ..."
      cat > /etc/apt/sources.list.d/debian.sources <<EOF
Types: deb
URIs: $mirror
Suites: bookworm bookworm-updates
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg

Types: deb
URIs: $mirror-security
Suites: bookworm-security
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
      apt-get update -qq || true
    fi
  fi
}

# -------- 1. JDK 17 --------
install_jdk() {
  if [ -x "$JDK_DIR/bin/java" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "JDK 17 already at $JDK_DIR"
  else
    log "Installing OpenJDK 17 via apt..."
    ensure_apt_sources
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      openjdk-17-jdk-headless unzip curl >"$LOG_DIR/apt.log" 2>&1 \
      || { tail -40 "$LOG_DIR/apt.log" >&2; die "apt install failed"; }
    rm -f "$JDK_DIR"
    ln -s "$(dirname "$(dirname "$(readlink -f "$(which java)")")")" "$JDK_DIR"
  fi
  "$JDK_DIR/bin/java" -version
}

# -------- 2. Android SDK --------
install_android_sdk() {
  if [ -d "$ANDROID_SDK_DIR/cmdline-tools/latest" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "Android SDK already at $ANDROID_SDK_DIR"
  else
    log "Downloading Android command-line tools..."
    local TMP; TMP=$(mktemp -d)
    cd "$TMP"
    curl -fsSL --retry 3 -o cmdline-tools.zip \
      "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" \
      || die "Failed to download cmdline-tools"
    mkdir -p "$ANDROID_SDK_DIR/cmdline-tools"
    unzip -q cmdline-tools.zip
    rm -rf "$ANDROID_SDK_DIR/cmdline-tools/latest"
    mv cmdline-tools "$ANDROID_SDK_DIR/cmdline-tools/latest"
    cd / && rm -rf "$TMP"
  fi

  export JAVA_HOME="$JDK_DIR"
  export ANDROID_HOME="$ANDROID_SDK_DIR"
  export PATH="$JDK_DIR/bin:$ANDROID_SDK_DIR/cmdline-tools/latest/bin:$ANDROID_SDK_DIR/platform-tools:$PATH"

  log "Accepting SDK licenses..."
  yes 2>/dev/null | sdkmanager --licenses >"$LOG_DIR/licenses.log" 2>&1 || true

  log "Installing platform-tools, build-tools;${BUILD_TOOLS_VER}, platforms;${PLATFORM_VER}..."
  sdkmanager --install \
    "platform-tools" \
    "build-tools;${BUILD_TOOLS_VER}" \
    "platforms;${PLATFORM_VER}" \
    >"$LOG_DIR/sdk-install.log" 2>&1 \
    || { tail -60 "$LOG_DIR/sdk-install.log" >&2; die "sdkmanager install failed"; }
  ok "Android SDK components installed"
}

# -------- 3. Gradle (multi-version) --------
GRADLE_MIRRORS=(
  "https://mirrors.cloud.tencent.com/gradle"
  "https://mirrors.huaweicloud.com/gradle"
  "https://mirrors.aliyun.com/macports/distfiles/gradle"
  "https://services.gradle.org/distributions"
)

pick_gradle_mirror() {
  local version="$1"
  if [ -n "${GRADLE_MIRROR:-}" ]; then
    echo "$GRADLE_MIRROR"; return
  fi
  local best="" best_time=999
  for m in "${GRADLE_MIRRORS[@]}"; do
    local url="$m/gradle-${version}-bin.zip"
    local t; t=$(curl -sI -o /dev/null -w "%{time_total}" --max-time 6 "$url" 2>/dev/null || echo "99")
    if [ "$(printf "%.0f" "$t")" -lt "$(printf "%.0f" "$best_time")" ]; then
      best_time=$t; best=$m
    fi
  done
  log "Chose Gradle mirror: $best (latency ${best_time}s)"
  echo "$best"
}

install_gradle_version() {
  local version="$1"
  local dir="$PREFIX/gradle-${version}"
  if [ -x "$dir/bin/gradle" ] && [ "${FORCE:-0}" != 1 ]; then
    ok "Gradle ${version} already at $dir"
  else
    local mirror; mirror=$(pick_gradle_mirror "$version")
    log "Downloading Gradle ${version} from $mirror ..."
    local TMP; TMP=$(mktemp -d)
    cd "$TMP"
    curl -fsSL --retry 3 --max-time 300 -L -o gradle.zip \
      "$mirror/gradle-${version}-bin.zip" \
      || die "Failed to download Gradle ${version} from $mirror"
    unzip -q gradle.zip
    rm -rf "$dir"
    mv "gradle-${version}" "$dir"
    cd / && rm -rf "$TMP"
  fi
  "$dir/bin/gradle" --version 2>&1 | grep "^Gradle" | head -1
}

install_gradle_all() {
  # Set the default symlink to the FIRST listed version (the freshest).
  local first="${GRADLE_VERSIONS%% *}"
  local default_dir="$PREFIX/gradle"

  for v in $GRADLE_VERSIONS; do
    install_gradle_version "$v"
  done

  # Maintain a /opt/gradle symlink that always points at the freshest version
  # installed — handy for `gradle` on PATH. build.sh overrides this when it
  # detects a different version in gradle-wrapper.properties.
  rm -f "$default_dir"
  ln -s "$PREFIX/gradle-${first}" "$default_dir"
  ok "Default 'gradle' on PATH → $default_dir → $(basename "$(readlink "$default_dir")")"
}

install_jdk
if [ "${SKIP_SDK:-0}" = 1 ]; then
  log "SKIP_SDK=1: skipping install_android_sdk (cmdline-tools / platform-tools / build-tools / platforms already provisioned manually)"
  [ -d "$ANDROID_SDK_DIR/cmdline-tools/latest" ] || die "SKIP_SDK=1 but $ANDROID_SDK_DIR/cmdline-tools/latest is missing"
  [ -d "$ANDROID_SDK_DIR/platform-tools" ] || die "SKIP_SDK=1 but $ANDROID_SDK_DIR/platform-tools is missing"
  [ -d "$ANDROID_SDK_DIR/build-tools" ] || die "SKIP_SDK=1 but $ANDROID_SDK_DIR/build-tools is missing"
  [ -d "$ANDROID_SDK_DIR/platforms" ] || die "SKIP_SDK=1 but $ANDROID_SDK_DIR/platforms is missing"
  ok "Android SDK already provisioned at $ANDROID_SDK_DIR"
else
  install_android_sdk
fi
install_gradle_all

# Persist env for future shells. Add EVERY installed Gradle to PATH so any
# version can be invoked by absolute path (/opt/gradle-X.Y/bin/gradle) even
# when the default symlink points elsewhere.
GRADLE_PATH=""
for v in $GRADLE_VERSIONS; do
  GRADLE_PATH="$GRADLE_PATH:$PREFIX/gradle-${v}/bin"
done
cat > /etc/profile.d/android-build-env.sh <<EOF
export JAVA_HOME=$JDK_DIR
export ANDROID_HOME=$ANDROID_SDK_DIR
export ANDROID_SDK_ROOT=$ANDROID_SDK_DIR
export PATH=$JDK_DIR/bin:$ANDROID_SDK_DIR/cmdline-tools/latest/bin:$ANDROID_SDK_DIR/platform-tools:$PREFIX/gradle/bin${GRADLE_PATH}:\$PATH
# Installed Gradle versions: $GRADLE_VERSIONS
EOF
chmod +x /etc/profile.d/android-build-env.sh

echo
ok "Environment ready."
echo "  JDK:               $JDK_DIR"
echo "  Android SDK:       $ANDROID_SDK_DIR"
echo "  Gradle (default):  $PREFIX/gradle -> $(basename "$(readlink "$PREFIX/gradle" 2>/dev/null || echo 'gradle-NONE')")"
echo "  Gradle (all):      $(echo $GRADLE_VERSIONS | tr ' ' '\n' | sed 's|^|  - /opt/gradle-|' | tr '\n' ' ')"
echo "  Logs:              $LOG_DIR"
echo "  Reload:            source /etc/profile.d/android-build-env.sh"
