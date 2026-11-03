#!/usr/bin/env bash
# package-source.sh — Zip the project source for delivery.
# Usage: package-source.sh --project DIR --output FILE.zip
set -euo pipefail

PROJECT=""; OUTPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="$2"; shift 2;;
    --output)  OUTPUT="$2"; shift 2;;
    -h|--help) sed -n '2,4p' "$0"; exit 0;;
    *) echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

[ -n "$PROJECT" ] || { echo "--project is required" >&2; exit 2; }
[ -n "$OUTPUT" ]  || { echo "--output is required" >&2; exit 2; }
[ -d "$PROJECT" ] || { echo "Project not found: $PROJECT" >&2; exit 2; }

# Use a clean staging copy so we don't bundle build/, .gradle/, .idea/, etc.
STAGE=$(mktemp -d)
trap "rm -rf $STAGE" EXIT

PROJECT_NAME=$(basename "$PROJECT")
mkdir -p "$STAGE/$PROJECT_NAME"

# Copy with built-in exclusions (no rsync dependency).
tar -cf - \
  --exclude='build' --exclude='build/**' \
  --exclude='.gradle' --exclude='.gradle/**' \
  --exclude='.idea' --exclude='.idea/**' \
  --exclude='.kotlin' --exclude='.kotlin/**' \
  --exclude='local.properties' \
  --exclude='*.iml' \
  -C "$PROJECT" . \
  | tar -xf - -C "$STAGE/$PROJECT_NAME"

(cd "$STAGE" && zip -qr "$OUTPUT" "$PROJECT_NAME")
echo "[package-source] ✓ $OUTPUT ($(du -h "$OUTPUT" | cut -f1))"
