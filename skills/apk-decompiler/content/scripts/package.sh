#!/usr/bin/env bash
# package.sh — Zip a decompile output directory for delivery.
# Default mode: zip -0 (store only, no compression) — faster on already-compressed
# text/dex, easier diff/grep, and matches the user's "仅存储模式" requirement.
#
# Usage:
#   package.sh --in DIR [--out FILE.zip] [--deflate] [--pass PASSWORD]
set -uo pipefail

IN=""; OUT=""; COMPRESS=0; PASS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in)       IN="$2"; shift 2;;
    --out)      OUT="$2"; shift 2;;
    --deflate)  COMPRESS=1; shift;;
    --pass)     PASS="$2"; shift 2;;
    -h|--help)  sed -n '2,11p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$IN" ] || { echo "--in is required" >&2; exit 2; }
[ -d "$IN" ] || { echo "Not a directory: $IN" >&2; exit 2; }

# zip flag: -0 = store, -9 = max deflate
if [ "$COMPRESS" = 1 ]; then
  ZIP_FLAG="-9"
  MODE_LABEL="deflate (compressed)"
else
  ZIP_FLAG="-0"
  MODE_LABEL="store (no compression, 仅存储模式)"
fi
SUFFIX=$([[ "$COMPRESS" == 1 ]] && echo ".zip" || echo "-store.zip")
[ -n "$OUT" ] || OUT="$IN${SUFFIX}"

rm -f "$OUT"

# Stage on local fs first (zip is much faster on local than NAS), then
# move/copy the resulting zip to OUT.
STAGE=$(mktemp -d -p /opt/decompile-work)
trap "rm -rf $STAGE" EXIT

NAME=$(basename "$IN")
STAGED="$STAGE/$NAME"
mkdir -p "$STAGED"
# Hardlink-copy where possible, fall back to tar pipe.
(cd "$IN" && tar -cf - .) | (cd "$STAGED" && tar -xf -)

ZIP_ARGS=(-rq "$ZIP_FLAG")
if [ -n "$PASS" ]; then
  ZIP_ARGS+=(-P "$PASS")
fi

(cd "$STAGE" && zip "${ZIP_ARGS[@]}" "$OUT" "$NAME")
RC=$?

if [ $RC -ne 0 ]; then
  echo "[package] ✗ zip failed (rc=$RC)" >&2
  exit 1
fi

echo
echo "═══════════════════════════════════════════════"
echo "  Package complete"
echo "═══════════════════════════════════════════════"
echo "  Source:    $IN"
echo "  Output:    $OUT"
echo "  Size:      $(du -h "$OUT" | cut -f1)"
echo "  Mode:      $MODE_LABEL"
[ -n "$PASS" ] && echo "  Encrypted: yes (use --pass to set)"
ls -lh "$OUT"
