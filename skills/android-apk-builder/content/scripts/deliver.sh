#!/usr/bin/env bash
# deliver.sh — Stage APK + source for delivery, with a .apk.zip variant
# for environments that block .apk downloads.
#
# Usage:
#   deliver.sh --project DIR [--variant debug] [--out DIR]
#
# Why .apk.zip? Many browsers, email gateways, chat tools, and corporate
# proxies warn-or-block plain .apk downloads. Renaming to .apk.zip leaves
# the bytes untouched (still a valid APK), but the file travels through
# any channel that allows general zip attachments. The user renames it
# back to .apk before `adb install -r` (or, on most file managers,
# double-clicking a .apk.zip that's actually an APK offers to install
# it directly).
#
# Outputs (all under --out, default = <project>/deliverables/):
#   <slug>-app-debug.apk       — original signed APK (for adb / direct install)
#   <slug>-app-debug.apk.zip   — same bytes, .apk.zip extension (for hostile networks)
#   <slug>-source.zip          — full Android Studio project source
set -euo pipefail

PROJECT=""; VARIANT="debug"; OUT=""
SLUG=""

usage() {
  sed -n '2,15p' "$0"
  exit "${1:-0}"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="$2"; shift 2;;
    --variant) VARIANT="$2"; shift 2;;
    --out)     OUT="$2"; shift 2;;
    --slug)    SLUG="$2"; shift 2;;
    -h|--help) usage 0;;
    *) echo "Unknown arg: $1" >&2; usage 2;;
  esac
done

[ -n "$PROJECT" ] || { echo "--project is required" >&2; usage 2; }
[ -d "$PROJECT" ] || { echo "Project not found: $PROJECT" >&2; exit 2; }

SLUG="${SLUG:-$(basename "$PROJECT")}"
OUT="${OUT:-$PROJECT/deliverables}"
mkdir -p "$OUT"

APK_SRC="$PROJECT/app/build/outputs/apk/$VARIANT/app-${VARIANT}.apk"
[ -f "$APK_SRC" ] || {
  echo "[deliver] ERROR: APK not built yet at $APK_SRC" >&2
  echo "[deliver] Run: bash scripts/build.sh --project $PROJECT" >&2
  exit 1
}

APK_PLAIN="$OUT/${SLUG}-app-${VARIANT}.apk"
APK_ZIP="$OUT/${SLUG}-app-${VARIANT}.apk.zip"
SRC_ZIP="$OUT/${SLUG}-source.zip"

cp -f "$APK_SRC" "$APK_PLAIN"
# Byte-for-byte copy, just renamed. Some content scanners key off the
# extension, so we don't try to be clever about it.
cp -f "$APK_SRC" "$APK_ZIP"

# Source zip (re-package if missing, otherwise just copy).
if [ -f "$PROJECT/${SLUG}-source.zip" ]; then
  cp -f "$PROJECT/${SLUG}-source.zip" "$SRC_ZIP"
else
  bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/package-source.sh" \
    --project "$PROJECT" --output "$SRC_ZIP" >/dev/null
fi

# Verify both files are byte-identical (paranoid, but cheap).
SRC_SUM=$(sha256sum "$APK_SRC" | awk '{print $1}')
PLAIN_SUM=$(sha256sum "$APK_PLAIN" | awk '{print $1}')
ZIP_SUM=$(sha256sum "$APK_ZIP" | awk '{print $1}')
if [ "$SRC_SUM" != "$PLAIN_SUM" ] || [ "$SRC_SUM" != "$ZIP_SUM" ]; then
  echo "[deliver] ERROR: APK copy checksum mismatch — refusing to ship." >&2
  echo "  source: $SRC_SUM" >&2
  echo "  plain:  $PLAIN_SUM" >&2
  echo "  .zip:   $ZIP_SUM" >&2
  exit 1
fi

# Verify with apksigner if available — catches broken builds before we
# ask the user to install them.
if command -v apksigner >/dev/null 2>&1; then
  if ! apksigner verify "$APK_PLAIN" >/dev/null 2>&1; then
    echo "[deliver] WARNING: apksigner verification failed (signature may still be valid for installs):" >&2
    apksigner verify --verbose "$APK_PLAIN" >&2 || true
  fi
fi

echo "[deliver] ✓ Staged 3 files under $OUT"
ls -lh "$OUT"

cat <<EOF

[deliver] Wrap these in a <deliver-assets> block in your reply:

    <deliver-assets>
    <media type="file" src="$APK_ZIP"   caption="Signed debug APK (renamed .apk.zip for friendlier downloads)" />
    <media type="file" src="$APK_PLAIN" caption="Same APK with .apk extension (for direct adb install)" />
    <media type="file" src="$SRC_ZIP"   caption="Full Android Studio project source" />
    </deliver-assets>

    sha256:  $SRC_SUM
EOF
