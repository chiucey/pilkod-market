#!/usr/bin/env bash
# new-project.sh — Generate a customized Android project from the base template.
# Usage:
#   new-project.sh --out DIR --name "MyApp" --package com.example.myapp \
#                  [--min 24] [--target 34] [--version-name 1.0] [--version-code 1]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates/base"

OUT=""; APP_NAME=""; PACKAGE=""
MIN_SDK=24; TARGET_SDK=34; COMPILE_SDK=34
VERSION_NAME="1.0"; VERSION_CODE=1
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)         OUT="$2"; shift 2;;
    --name)        APP_NAME="$2"; shift 2;;
    --package)     PACKAGE="$2"; shift 2;;
    --min)         MIN_SDK="$2"; shift 2;;
    --target)      TARGET_SDK="$2"; shift 2;;
    --compile)     COMPILE_SDK="$2"; shift 2;;
    --version-name) VERSION_NAME="$2"; shift 2;;
    --version-code) VERSION_CODE="$2"; shift 2;;
    --force)       FORCE=1; shift;;
    -h|--help)
      sed -n '2,9p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$OUT" ]      || { echo "--out is required" >&2; exit 2; }
[ -n "$APP_NAME" ] || { echo "--name is required" >&2; exit 2; }
[ -n "$PACKAGE" ]  || { echo "--package is required" >&2; exit 2; }
[[ "$PACKAGE" =~ ^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$ ]] || {
  echo "--package must be like com.example.myapp" >&2; exit 2; }

APP_NAME_SLUG=$(echo "$APP_NAME" | tr '[:upper:] ' '[:lower:]_')
PACKAGE_PATH=$(echo "$PACKAGE" | tr '.' '/')
FROM_PKG_PATH="com/mavis/template"

if [ -e "$OUT" ]; then
  if [ "$FORCE" = 1 ]; then
    echo "[new-project] --force: removing existing $OUT ..."
    rm -rf "$OUT" 2>/dev/null || true
  else
    echo "Output dir already exists: $OUT (use --force to overwrite)" >&2
    exit 2
  fi
fi

echo "[new-project] Scaffolding into $OUT ..."
mkdir -p "$OUT"
cp -r "$TEMPLATE_DIR/." "$OUT/"

# Move the template package dir to the target package dir.
if [ -d "$OUT/app/src/main/java/$FROM_PKG_PATH" ]; then
  mkdir -p "$OUT/app/src/main/java/$(dirname "$PACKAGE_PATH")"
  mv "$OUT/app/src/main/java/$FROM_PKG_PATH" "$OUT/app/src/main/java/$PACKAGE_PATH"
fi

# --- Pre-flight check: Kotlin nested-comment gotcha ----------------------
# Kotlin's /* ... */ comments are *nestable* (unlike Java). If a /** KDoc
# block contains a /* pattern (e.g. a filesystem path like /proc/* or /dev/*),
# the inner /* opens a nested comment that the next */ closes, leaving the
# outer KDoc open until EOF. The whole file is then parsed as a comment, and
# the build dies with a confusing "Unclosed comment" at the file's last line.
# This is the #1 way to silently break a freshly-pasted utility file.
# We scan every .kt file in the scaffolded tree and bail early with an
# actionable error if we find such a pattern.
PREFLIGHT_FAIL=0
while IFS= read -r -d '' f; do
  # awk state machine: 0=normal, 1=in /**...*/ KDoc, 2=in /*...*/ block
  awk '
    BEGIN { state = 0; lineno = 0 }
    { lineno++ }
    state == 0 {
      if (match($0, /\/\*\*/)) { state = 1; next }
      if (match($0, /\/\*/))  { state = 2; print FILENAME ":" lineno ": block /* without prior nesting: " $0; state = 0; next }
    }
    state == 1 {
      if (match($0, /\/\*/))  { print FILENAME ":" lineno ": NESTED /* inside /** KDoc block — Kotlin will treat the rest of the file as one giant comment. Offending line: " $0; state = 99; exit 1 }
      if (match($0, /\*\//)) { state = 0 }
    }
    state == 2 {
      if (match($0, /\*\//)) { state = 0 }
    }
    state == 99 { exit 1 }
  ' "$f" || PREFLIGHT_FAIL=1
done < <(find "$OUT" -type f -name '*.kt' -print0)

if [ "$PREFLIGHT_FAIL" -ne 0 ]; then
  cat >&2 <<'EOF'

[new-project] ABORT: Kotlin nested-comment hazard detected.

  Why:    Kotlin /* ... */ comments can be nested. A /** KDoc block that
          contains a "/*" sequence (very common with filesystem paths
          like /proc/*, /sys/*, /dev/*) opens a nested comment that
          Kotlin never closes, and the rest of the file is parsed as
          one big comment. The build then dies with a misleading
          "Unclosed comment" at end-of-file.

  Fix:    Either
            - escape the slash, e.g. write "/proc\u002F" or just rephrase
              the comment to avoid the path; or
            - move the path example outside the comment block.

  Files with the issue are listed above. Patch them, then re-run with
  --force to overwrite this scaffold.

EOF
  exit 3
fi

# Replace placeholders in all text files under the project.
find "$OUT" -type f \( -name "*.kt" -o -name "*.kts" -o -name "*.xml" -o -name "*.properties" -o -name "*.toml" -o -name "*.pro" \) -print0 \
  | xargs -0 sed -i \
      -e "s|@APP_NAME@|$APP_NAME|g" \
      -e "s|@APP_NAME_SLUG@|$APP_NAME_SLUG|g" \
      -e "s|@PACKAGE_NAME@|$PACKAGE|g" \
      -e "s|@PACKAGE_PATH@|$PACKAGE|g" \
      -e "s|@MIN_SDK@|$MIN_SDK|g" \
      -e "s|@TARGET_SDK@|$TARGET_SDK|g" \
      -e "s|@COMPILE_SDK@|$COMPILE_SDK|g" \
      -e "s|@VERSION_NAME@|$VERSION_NAME|g" \
      -e "s|@VERSION_CODE@|$VERSION_CODE|g"

# Sanity: no leftover placeholders.
LEFTOVERS=$(grep -rl '@[A-Z_]*@' "$OUT" 2>/dev/null || true)
if [ -n "$LEFTOVERS" ]; then
  echo "[new-project] WARNING: leftover placeholders in:" >&2
  echo "$LEFTOVERS" >&2
fi

echo "[new-project] ✓ Generated $OUT"
echo "  App:       $APP_NAME"
echo "  Package:   $PACKAGE"
echo "  minSdk:    $MIN_SDK"
echo "  targetSdk: $TARGET_SDK"
echo "  Version:   $VERSION_NAME ($VERSION_CODE)"
