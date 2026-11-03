#!/bin/bash
# pandoc-export.sh - Resume export script using pandoc + wkhtmltopdf
# Usage: ./pandoc-export.sh <input.md> <output.format>

INPUT="$1"
OUTPUT="$2"

if [ -z "$INPUT" ] || [ -z "$OUTPUT" ]; then
  echo "Usage: pandoc-export.sh <input.md> <output.format>"
  echo "Formats: html, pdf, docx, tex"
  exit 1
fi

BASENAME="${INPUT%.md}"
case "$OUTPUT" in
  html)
    pandoc "$INPUT" -o "${BASENAME}.html" --standalone --css="https://cdn.jsdelivr.net/npm/water.css@2/out/water.css"
    ;;
  pdf)
    pandoc "$INPUT" -o "${BASENAME}.html" --standalone
    wkhtmltopdf "${BASENAME}.html" "${BASENAME}.pdf"
    ;;
  docx)
    pandoc "$INPUT" -o "${BASENAME}.docx"
    ;;
  tex)
    pandoc "$INPUT" -o "${BASENAME}.tex"
    ;;
  *)
    echo "Unknown format: $OUTPUT"
    exit 1
    ;;
esac

echo "Exported: ${BASENAME}.${OUTPUT}"
