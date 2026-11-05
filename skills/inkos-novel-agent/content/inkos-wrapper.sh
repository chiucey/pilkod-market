#!/bin/bash
# InkOS Novel Agent Wrapper Script
# This script provides a convenient interface to InkOS CLI

INKOS_CMD="/tmp/.npm-global/bin/inkos"
PROJECT_DIR="${HOME}/inkos-projects"

# Ensure project directory exists
mkdir -p "$PROJECT_DIR"

# Change to project directory
cd "$PROJECT_DIR" || exit 1

# Function to display help
show_help() {
    cat << EOF
InkOS Novel Agent - CLI Wrapper

Usage: ./inkos-wrapper.sh [command] [options]

Commands:
    init [name]              Initialize a new InkOS project
    create --title TITLE     Create a new book
    write [book-id]          Write next chapter
    write [book-id] -c N     Write N chapters continuously
    audit [book-id] [n]      Audit chapter N
    revise [book-id] [n]     Revise chapter N
    export [book-id]         Export to TXT
    export [book-id] --format epub  Export to EPUB
    style-analyze [file]     Analyze style from file
    style-import [file] [book-id]  Import style to book
    detect [book-id] [n]     Run AIGC detection
    agent [instruction]      Natural language agent mode
    list                    List all books
    status [book-id]         Show project status
    help                    Show this help message

Examples:
    ./inkos-wrapper.sh init my-novel
    ./inkos-wrapper.sh create --title "逆天改命" --genre xianxia
    ./inkos-wrapper.sh write my-novel
    ./inkos-wrapper.sh write my-novel -c 5
    ./inkos-wrapper.sh style-analyze reference.txt
    ./inkos-wrapper.sh agent "帮我写一个都市修仙故事"

For more commands, see: inkos --help
EOF
}

# Check if InkOS is installed
if ! command -v "$INKOS_CMD" &> /dev/null; then
    echo "Error: InkOS not found. Installing..."
    npm install -g @actalk/inkos
fi

# Parse command line arguments
case "$1" in
    init)
        shift
        "$INKOS_CMD" init "$@"
        ;;
    create)
        shift
        "$INKOS_CMD" book create "$@"
        ;;
    write)
        shift
        "$INKOS_CMD" write next "$@"
        ;;
    audit)
        shift
        "$INKOS_CMD" audit "$@"
        ;;
    revise)
        shift
        "$INKOS_CMD" revise "$@"
        ;;
    export)
        shift
        "$INKOS_CMD" export "$@"
        ;;
    style-analyze)
        shift
        "$INKOS_CMD" style analyze "$@"
        ;;
    style-import)
        shift
        "$INKOS_CMD" style import "$@"
        ;;
    detect)
        shift
        "$INKOS_CMD" detect "$@"
        ;;
    agent)
        shift
        "$INKOS_CMD" agent "$@"
        ;;
    list)
        "$INKOS_CMD" book list
        ;;
    status)
        shift
        "$INKOS_CMD" status "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        if [ -z "$1" ]; then
            show_help
        else
            "$INKOS_CMD" "$@"
        fi
        ;;
esac
