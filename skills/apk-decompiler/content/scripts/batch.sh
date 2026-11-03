#!/usr/bin/env bash
# batch.sh — Decompile (and optionally scan) a directory of APKs.
#
# Usage:
#   batch.sh --in DIR  --out DIR  [--with-scan] [--with-cfr] [--no-baksmali]
#
# Each APK's decompile lands in <out>/<apk-stem>/. A combined summary
# BATCH_REPORT.md and BATCH_REPORT.csv is written at the end.
set -uo pipefail

IN=""; OUT=""
WITH_SCAN=0; WITH_CFR=0; WITH_BAKSMALI=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --in)           IN="$2"; shift 2;;
    --out)          OUT="$2"; shift 2;;
    --with-scan)    WITH_SCAN=1; shift;;
    --with-cfr)     WITH_CFR=1; shift;;
    --no-baksmali)  WITH_BAKSMALI=0; shift;;
    -h|--help)      sed -n '2,8p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$IN" ] || { echo "--in is required" >&2; exit 2; }
[ -n "$OUT" ] || { echo "--out is required" >&2; exit 2; }
[ -d "$IN" ] || { echo "Not a directory: $IN" >&2; exit 2; }

mkdir -p "$OUT"

# Find all APKs (case-insensitive).
shopt -s nullglob nocaseglob
APKS=("$IN"/*.apk "$IN"/*.APK)
shopt -u nullglob nocaseglob
[ ${#APKS[@]} -gt 0 ] || { echo "No APKs found in $IN" >&2; exit 1; }

# Skip already-processed APKs unless FORCE=1
[ "${FORCE:-0}" = 1 ] && SKIP_EXISTING=0 || SKIP_EXISTING=1

SUMMARY="$OUT/BATCH_SUMMARY.csv"
echo "apk,stem,size,jadx_java,baksmali_smali,apktool_smali,scan_severity,scan_urls,scan_aws,scan_google,scan_perms" > "$SUMMARY"

# Per-APK run, sequential. Parallel is risky in 2 GB sandbox.
TOTAL=${#APKS[@]}
COUNT=0
for apk in "${APKS[@]}"; do
  COUNT=$((COUNT+1))
  name=$(basename "$apk")
  stem="${name%.apk}"
  apk_out="$OUT/$stem"

  echo
  echo "═══════════════════════════════════════════════"
  echo "  [$COUNT/$TOTAL] $name"
  echo "═══════════════════════════════════════════════"

  if [ "$SKIP_EXISTING" = 1 ] && [ -f "$apk_out/DECOMPILE_REPORT.md" ]; then
    echo "[batch] skip (already decompiled; use FORCE=1 to re-run)"
  else
    DECOMPILE_ARGS=(--apk "$apk" --out "$apk_out")
    [ "$WITH_CFR" = 1 ] && DECOMPILE_ARGS+=(--with-cfr)
    [ "$WITH_BAKSMALI" = 0 ] && DECOMPILE_ARGS+=(--no-baksmali)
    if ! bash "$(dirname "$0")/decompile.sh" "${DECOMPILE_ARGS[@]}"; then
      echo "[batch] decompile FAILED for $name" >&2
      continue
    fi
  fi

  # Optional scan.
  SEV=""; URLS=0; AWS=0; GOOGLE=0; PERMS=0
  if [ "$WITH_SCAN" = 1 ]; then
    if bash "$(dirname "$0")/scan.sh" --in "$apk_out" > /dev/null 2>&1; then
      SEV=$(grep -oE 'Severity\*\*: [^ ]+' "$apk_out/SCAN_REPORT.md" 2>/dev/null | sed 's/Severity\*\*: //')
      URLS=$(grep -oE 'Total unique URLs\*\*: [0-9]+' "$apk_out/SCAN_REPORT.md" 2>/dev/null \
             | grep -oE '[0-9]+' | head -1)
      AWS=$(grep -oE 'AWS Access Key .* \| [0-9]+' "$apk_out/SCAN_REPORT.md" 2>/dev/null \
            | grep -oE '[0-9]+$' | head -1)
      GOOGLE=$(grep -oE 'Google API Key .* \| [0-9]+' "$apk_out/SCAN_REPORT.md" 2>/dev/null \
               | grep -oE '[0-9]+$' | head -1)
      PERMS=$(grep -oE 'Total dangerous perms requested\*\*: [0-9]+' "$apk_out/SCAN_REPORT.md" 2>/dev/null \
              | grep -oE '[0-9]+$' | head -1)
    else
      SEV="scan-failed"
    fi
  fi

  JADX_JAVA=$(find "$apk_out/jadx" -name "*.java" 2>/dev/null | wc -l)
  BAKSMALI_FILES=$(find "$apk_out/smali" -name "*.smali" 2>/dev/null | wc -l)
  APKTOOL_FILES=$(find "$apk_out/apktool" -name "*.smali" 2>/dev/null | wc -l)
  SIZE=$(du -h "$apk" | cut -f1)

  printf "%s,%s,%s,%d,%d,%d,%s,%s,%s,%s,%s\n" \
    "$name" "$stem" "$SIZE" "$JADX_JAVA" "$BAKSMALI_FILES" "$APKTOOL_FILES" \
    "${SEV:-n/a}" "${URLS:-0}" "${AWS:-0}" "${GOOGLE:-0}" "${PERMS:-0}" >> "$SUMMARY"
done

# Combined BATCH_REPORT.md
{
echo "# Batch Decompile Report"
echo
echo "- **Input dir**: $IN"
echo "- **Output dir**: $OUT"
echo "- **APKs processed**: $TOTAL"
echo "- **Scan enabled**: $([ "$WITH_SCAN" = 1 ] && echo yes || echo no)"
echo
echo "## Per-APK summary"
echo
echo "| APK | Size | jadx .java | baksmali .smali | apktool .smali | Severity |"
echo "|-----|------|----------:|----------------:|---------------:|:--------:|"
if [ -f "$SUMMARY" ]; then
  # skip header
  tail -n +2 "$SUMMARY" \
    | awk -F, '{printf "| %s | %s | %d | %d | %d | %s |\n", $1, $3, $4, $5, $6, $7}'
fi
echo
echo "Full machine-readable summary: \`$SUMMARY\`"
} > "$OUT/BATCH_REPORT.md"

echo
echo "═══════════════════════════════════════════════"
echo "  Batch complete"
echo "═══════════════════════════════════════════════"
echo "  Processed: $TOTAL APK(s)"
echo "  Output:    $OUT"
echo "  Summary:   $SUMMARY"
echo "  Report:    $OUT/BATCH_REPORT.md"
