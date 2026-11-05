#!/usr/bin/env bash
# build.sh — Build a debug APK (auto-signs with debug keystore).
# Usage: build.sh --project DIR [--output DIR] [--variant debug|release]
#
# Why this script streams via tee (not `| tail`): pipe-through-tail buffers
# the entire gradle output and only shows it once the build finishes. A
# 6-minute first build with a silent network stall then looks identical to
# a hung JVM. tee-to-file-then-cat-tail lets you watch progress live AND
# jump to the end of the log if you only want the final result.
set -euo pipefail

PROJECT=""; OUTPUT=""; VARIANT="debug"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="$2"; shift 2;;
    --output)  OUTPUT="$2"; shift 2;;
    --variant) VARIANT="$2"; shift 2;;
    -h|--help) sed -n '2,5p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$PROJECT" ] || { echo "--project is required" >&2; exit 2; }
[ -d "$PROJECT" ] || { echo "Project not found: $PROJECT" >&2; exit 2; }

# Load env if present.
# shellcheck disable=SC1091
[ -f /etc/profile.d/android-build-env.sh ] && source /etc/profile.d/android-build-env.sh

# Ensure JDK 17 is on PATH.
if ! command -v java >/dev/null; then
  echo "[build] ERROR: java not on PATH. Run env-setup.sh first." >&2
  exit 1
fi
export JAVA_HOME="${JAVA_HOME:-$(dirname "$(dirname "$(readlink -f "$(which java)")")")}"
export ANDROID_HOME="${ANDROID_HOME:-/opt/android-sdk}"
export ANDROID_SDK_ROOT="${ANDROID_SDK_ROOT:-$ANDROID_HOME}"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

# Force Gradle's caches onto the local overlay filesystem. On NAS-mounted
# workspaces the daemon gets stuck on nfs lock files (.nfs*) that survive
# even after `rm -rf`, so we keep ~/.gradle off the network share.
export GRADLE_USER_HOME="${GRADLE_USER_HOME:-/root/.gradle}"

# Cleanup BEFORE the build, not after. Things that go wrong:
#   1. Project's .gradle/ on NFS holds .nfs* lock files that survive rm.
#   2. Kotlin compile daemon (KotlinCompileDaemon) auto-started by an
#      earlier build can outlive its parent Gradle process and refuse
#      new compile requests; or worse, hang on to file handles that
#      block re-compilation.
#   3. Stale Gradle daemons from a previous --no-daemon run are rare
#      but possible.
echo "[build] Pre-build cleanup..."
rm -rf "$PROJECT/.gradle" 2>/dev/null || true
# Stop *all* java processes that look like a Gradle daemon. Don't try
# to be surgical — the only thing that breaks is the current build, and
# we want a known-clean state.
pkill -9 -f "GradleDaemon\|KotlinCompileDaemon\|GradleMain" 2>/dev/null || true
sleep 1

# Pick the right Gradle version for this project.
WRAPPER_PROPS="$PROJECT/gradle/wrapper/gradle-wrapper.properties"
GRADLE_BIN="$(command -v gradle || true)"
if [ -f "$WRAPPER_PROPS" ]; then
  REQUESTED=$(grep -oE 'gradle-[0-9]+\.[0-9]+(\.[0-9]+)?' "$WRAPPER_PROPS" | head -1 | sed 's/^gradle-//')
  if [ -n "$REQUESTED" ] && [ -x "/opt/gradle-${REQUESTED}/bin/gradle" ]; then
    GRADLE_BIN="/opt/gradle-${REQUESTED}/bin/gradle"
    echo "[build] Project requests Gradle ${REQUESTED} → using ${GRADLE_BIN}"
  elif [ -n "$REQUESTED" ]; then
    echo "[build] Project requests Gradle ${REQUESTED} but it's not installed."
    echo "[build] Re-run env-setup.sh with GRADLE_VERSIONS including ${REQUESTED}, or set"
    echo "[build]   /opt/gradle-${REQUESTED}/bin/gradle manually before continuing."
    echo "[build] Falling back to: $(command -v gradle || echo 'none on PATH')"
  fi
fi
if [ -z "$GRADLE_BIN" ]; then
  echo "[build] ERROR: no gradle on PATH. Run env-setup.sh first." >&2
  exit 1
fi

cd "$PROJECT"

# Ensure a debug keystore exists (Gradle uses ~/.android/debug.keystore by default).
DEBUG_KS="$HOME/.android/debug.keystore"
if [ ! -f "$DEBUG_KS" ]; then
  echo "[build] Generating debug keystore at $DEBUG_KS ..."
  mkdir -p "$(dirname "$DEBUG_KS")"
  "$JAVA_HOME/bin/keytool" -genkey -v \
    -keystore "$DEBUG_KS" -storepass android -keypass android \
    -alias androiddebugkey -dname "CN=Android Debug,O=Android,C=US" \
    -keyalg RSA -keysize 2048 -validity 10000 >/dev/null
fi

OUTPUT="${OUTPUT:-$PROJECT/build/outputs/apk/$VARIANT}"
mkdir -p "$OUTPUT"

# Allow user-defined extra Gradle args (e.g. --no-daemon for memory-tight sandboxes).
GRADLE_ARGS=${GRADLE_ARGS:-""}

TASK="assemble$(tr '[:lower:]' '[:upper:]' <<< "${VARIANT:0:1}")${VARIANT:1}"

# Stream output to a log file in real time so the caller can tail it.
# Also tee to stdout so progress is visible in the parent shell.
LOG_DIR="/workspace/.android-build-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/build-$(date +%Y%m%d-%H%M%S).log"
: > "$LOG_FILE"

echo "[build] Running $(basename "$(dirname "$GRADLE_BIN")")  $TASK ..."
echo "[build] Log: $LOG_FILE"
echo "[build] Tip: in another shell, run:  tail -f $LOG_FILE"
echo "[build] ------------------------------------------------------------"

# --info so task-level progress ("> Task :app:compileDebugKotlin") hits
# the log; --console=plain so it doesn't pretty-print (which would
# collide with our markers below).
set +e
"$GRADLE_BIN" --no-daemon "$TASK" --console=plain --warning-mode=summary \
  --info 2>&1 | tee "$LOG_FILE"
BUILD_RC=$?
set -e

echo "[build] ------------------------------------------------------------"
echo "[build] gradle exit code: $BUILD_RC"
echo "[build] Tail of log:"
tail -20 "$LOG_FILE" || true

APK_SRC="$PROJECT/app/build/outputs/apk/$VARIANT/app-${VARIANT}.apk"
if [ ! -f "$APK_SRC" ]; then
  echo "[build] ERROR: APK not found at $APK_SRC" >&2
  echo "[build] Last 50 lines of log:" >&2
  tail -50 "$LOG_FILE" >&2 || true
  echo "[build] Re-run with more detail: cd $PROJECT && gradle assembleDebug --info --stacktrace" >&2
  exit 1
fi
cp "$APK_SRC" "$OUTPUT/"

APK_SIZE=$(du -h "$OUTPUT/app-debug.apk" | cut -f1)
echo "[build] ✓ APK ready: $OUTPUT/app-debug.apk ($APK_SIZE)"

# Print a "where things went" line so the caller knows which phase
# dominated the wall-clock time. Helps diagnose network vs compile issues.
if grep -q "Downloading" "$LOG_FILE" 2>/dev/null; then
  DL_COUNT=$(grep -c "Downloading" "$LOG_FILE" || true)
  echo "[build] Note: $DL_COUNT download events in the log — first build is dependency-heavy."
fi
if grep -q "KotlinCompileDaemon" "$LOG_FILE" 2>/dev/null; then
  echo "[build] Note: KotlinCompileDaemon was used (faster incremental builds)."
fi
