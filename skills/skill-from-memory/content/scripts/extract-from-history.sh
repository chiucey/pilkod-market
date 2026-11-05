#!/bin/bash
# extract-from-history.sh
# Parse conversation history JSONL for skill content

set -e

SESSION_FILE="$1"
OUTPUT_DIR="$2"
SINCE_DATE=""
PATTERN=""
TOOLS_ONLY=false

# Parse arguments
shift 2
while [ $# -gt 0 ]; do
    case "$1" in
        --since) SINCE_DATE="$2"; shift 2 ;;
        --pattern) PATTERN="$2"; shift 2 ;;
        --tools-only) TOOLS_ONLY=true; shift ;;
        *) echo "Unknown option: $1"; shift ;;
    esac
done

if [ -z "$SESSION_FILE" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <session.jsonl> <output-dir> [--since DATE] [--pattern REGEX] [--tools-only]"
    exit 1
fi

if [ ! -f "$SESSION_FILE" ]; then
    echo "Error: Session file not found: $SESSION_FILE"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Extracting skill patterns from: $SESSION_FILE"
[ -n "$SINCE_DATE" ] && echo "Since: $SINCE_DATE"
[ -n "$PATTERN" ] && echo "Pattern: $PATTERN"
echo "Output directory: $OUTPUT_DIR"

# Extract user messages (potential task patterns)
if [ -n "$PATTERN" ]; then
    grep -i "$PATTERN" "$SESSION_FILE" | grep '"role":"user"' | head -50 > "$OUTPUT_DIR/user_messages.txt" 2>/dev/null || true
else
    grep '"role":"user"' "$SESSION_FILE" | head -50 > "$OUTPUT_DIR/user_messages.txt" 2>/dev/null || true
fi

# Extract assistant responses (potential solutions)
grep '"role":"assistant"' "$SESSION_FILE" | head -50 > "$OUTPUT_DIR/assistant_messages.txt" 2>/dev/null || true

# Extract tool calls (potential scripts)
grep '"type":"tool_call"' "$SESSION_FILE" | head -100 > "$OUTPUT_DIR/tool_calls.txt" 2>/dev/null || true

# Extract code blocks from assistant messages
awk -F'"text":"' '/"role":"assistant"/{p=1; next} p{print; if(/```/)p=0}' "$SESSION_FILE" | \
    grep -oE '```[^*]*```' | head -50 > "$OUTPUT_DIR/code_blocks.txt" 2>/dev/null || true

echo ""
echo "=== Extraction Summary ==="
[ -f "$OUTPUT_DIR/user_messages.txt" ] && echo "User messages: $(wc -l < "$OUTPUT_DIR/user_messages.txt") lines"
[ -f "$OUTPUT_DIR/assistant_messages.txt" ] && echo "Assistant responses: $(wc -l < "$OUTPUT_DIR/assistant_messages.txt") lines"
[ -f "$OUTPUT_DIR/tool_calls.txt" ] && echo "Tool calls: $(wc -l < "$OUTPUT_DIR/tool_calls.txt") lines"
[ -f "$OUTPUT_DIR/code_blocks.txt" ] && echo "Code blocks: $(wc -l < "$OUTPUT_DIR/code_blocks.txt") lines"

echo ""
echo "Extraction complete. Files saved to: $OUTPUT_DIR"
echo "Next step: Review extracted patterns and create skill structure"
