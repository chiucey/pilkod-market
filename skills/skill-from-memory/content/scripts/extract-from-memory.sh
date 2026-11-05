#!/bin/bash
# extract-from-memory.sh
# Parse memory markdown files and extract reusable skill patterns

set -e

MEMORY_FILE="$1"
OUTPUT_DIR="$2"

if [ -z "$MEMORY_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <memory.md> <output-dir>"
    exit 1
fi

if [ ! -f "$MEMORY_FILE" ]; then
    echo "Error: Memory file not found: $MEMORY_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Extracting skill patterns from: $MEMORY_FILE"
echo "Output directory: $OUTPUT_DIR"

# Extract patterns: look for headers, code blocks, decision points
# Focus on: ## headers (tasks/patterns), ```code blocks``` (scripts), **bold** (decisions)

# Extract all ## headers as potential skill names
grep -E "^##?\s+" "$MEMORY_FILE" | head -20 > "$OUTPUT_DIR/patterns_header.txt" 2>/dev/null || true

# Extract code blocks as potential scripts
awk '/^```/{p=!p; if(p)print; next} p' "$MEMORY_FILE" > "$OUTPUT_DIR/patterns_code.txt" 2>/dev/null || true

# Extract bold text as key decisions
grep -oE "\*\*[^*]+\*\*" "$MEMORY_FILE" | sed 's/\*\*//g' > "$OUTPUT_DIR/patterns_decisions.txt" 2>/dev/null || true

# Extract lists as potential steps
awk '/^-\s+/{print}' "$MEMORY_FILE" > "$OUTPUT_DIR/patterns_steps.txt" 2>/dev/null || true

echo ""
echo "=== Extraction Summary ==="
[ -f "$OUTPUT_DIR/patterns_header.txt" ] && echo "Headers: $(wc -l < "$OUTPUT_DIR/patterns_header.txt") lines"
[ -f "$OUTPUT_DIR/patterns_code.txt" ] && echo "Code blocks: $(wc -l < "$OUTPUT_DIR/patterns_code.txt") lines"
[ -f "$OUTPUT_DIR/patterns_decisions.txt" ] && echo "Decisions: $(wc -l < "$OUTPUT_DIR/patterns_decisions.txt") lines"
[ -f "$OUTPUT_DIR/patterns_steps.txt" ] && echo "Steps: $(wc -l < "$OUTPUT_DIR/patterns_steps.txt") lines"

echo ""
echo "Extraction complete. Files saved to: $OUTPUT_DIR"
echo "Next step: Review extracted patterns and create skill structure"
