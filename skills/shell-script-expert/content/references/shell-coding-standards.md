---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 304402200281e5bced75c5da73ec9041a52db750bd58dba09f5149bafd73a6663fe9538602206ed93d249e223410aa55d7769f8b43495894f1de2400758912108458a9f5a29b
    ReservedCode2: 3046022100ecfdc1f0049356ca1ee1de72450d14643f300323b460071dc743459b0bc7624f022100c119484f70674b9973fc90b5ce9fb74bd85b491fa4dfb7a5a9483eee75979134
---

# Shell Script Coding Standards Reference

## 1. Script Header Template

```bash
#!/usr/bin/env bash
#
# Script Name: script-name.sh
# Description: Brief description of what the script does
# Author: Your Name <email@example.com>
# Created: YYYY-MM-DD
# Last Modified: YYYY-MM-DD
# Version: 1.0.0
#
# Usage: ./script-name.sh [OPTIONS] ARGUMENTS
#
# Options:
#   -h, --help        Show this help message
#   -v, --verbose     Enable verbose output
#   -f, --force       Force operation
#   -o, --output      Specify output file
#
# Examples:
#   ./script-name.sh -v -o result.txt input.txt
#   ./script-name.sh --force /path/to/directory
#
# Exit Codes:
#   0   Success
#   1   General error
#   2   Invalid arguments
#   3   File not found
#   4   Permission denied
#
```

## 2. Usage Function Template

```bash
usage() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS] ARGUMENTS

Description: Brief description of the script's purpose.

OPTIONS:
    -h, --help              Show this help message and exit
    -v, --verbose           Enable verbose output (default: disabled)
    -f, --force             Force operation without confirmation
    -o, --output FILE       Specify output file (required)
    -c, --config FILE       Specify configuration file (default: ~/.config/script.conf)
    -n, --dry-run           Show what would be done without executing
    -q, --quiet             Suppress non-error messages

ARGUMENTS:
    INPUT_FILE              Input file to process (required)

EXAMPLES:
    # Basic usage with required output
    $(basename "$0") -o result.txt input.txt

    # Verbose mode with force
    $(basename "$0") -vf -o output.log data.csv

    # Using long options
    $(basename "$0") --verbose --force --output results.txt input.txt

    # Dry run mode
    $(basename "$0") -n -o test.txt sample.dat

NOTES:
    - INPUT_FILE must exist and be readable
    - Output will overwrite existing files unless --force is specified

Report bugs to: your.email@example.com
EOF
}
```

## 3. Error Handling Functions

```bash
# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Error handling
set -eE -o pipefail
trap 'error_handling $? $LINENO $BASH_LINENO' ERR

error_handling() {
    local exit_code=$1
    local line_no=$2
    local bash_line=$3
    log_error "Error occurred in script '$0' at line $line_no (command: ${BASH_COMMAND})"
    log_error "Exit code: $exit_code"
    exit "$exit_code"
}

# Cleanup function
cleanup() {
    local exit_code=$?
    # Add cleanup code here (temp files, locks, etc.)
    if [[ -n "${TMPDIR:-}" ]] && [[ -d "$TMPDIR" ]]; then
        rm -rf "$TMPDIR" 2>/dev/null || true
    fi
    exit "$exit_code"
}
trap cleanup EXIT
```

## 4. Argument Parsing Template

```bash
#!/usr/bin/env bash

# Default values
VERBOSE=false
FORCE=false
DRY_RUN=false
QUIET=false
OUTPUT_FILE=""
CONFIG_FILE="$HOME/.config/script.conf"
INPUT_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            usage
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -q|--quiet)
            QUIET=true
            shift
            ;;
        -*)
            log_error "Unknown option: $1"
            echo "Try '$(basename "$0") --help' for more information." >&2
            exit 2
            ;;
        *)
            INPUT_FILE="$1"
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$INPUT_FILE" ]]; then
    log_error "Missing required argument: INPUT_FILE"
    echo "Try '$(basename "$0") --help' for more information." >&2
    exit 2
fi

if [[ -z "$OUTPUT_FILE" ]]; then
    log_error "Missing required option: -o, --output OUTPUT_FILE"
    echo "Try '$(basename "$0") --help' for more information." >&2
    exit 2
fi
```

## 5. Common Functions Library

```bash
# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
is_root() {
    [[ $EUID -eq 0 ]]
}

# Require root privileges
require_root() {
    if ! is_root; then
        log_error "This operation requires root privileges"
        log_info "Please run with sudo or as root"
        exit 4
    fi
}

# Check file exists and is readable
validate_file() {
    local file="$1"
    if [[ ! -e "$file" ]]; then
        log_error "File not found: $file"
        exit 3
    fi
    if [[ ! -r "$file" ]]; then
        log_error "File not readable: $file"
        exit 4
    fi
}

# Check directory exists and is writable
validate_directory() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        log_error "Directory not found: $dir"
        exit 3
    fi
    if [[ ! -w "$dir" ]]; then
        log_error "Directory not writable: $dir"
        exit 4
    fi
}

# Confirm action with user
confirm() {
    local prompt="${1:-Are you sure?}"
    local default="${2:-n}"

    if [[ "$FORCE" == "true" ]]; then
        return 0
    fi

    local yn
    case "$default" in
        y) yn="Y/n"; default="y" ;;
        n) yn="y/N"; default="n" ;;
        *) yn="y/n"; default="y" ;;
    esac

    read -rp "$prompt [$yn]: " yn
    [[ -z "$yn" ]] && yn="$default"

    case "$yn" in
        [yY]*) return 0 ;;
        *) return 1 ;;
    esac
}

# Create temporary directory
create_temp_dir() {
    local tmpdir
    tmpdir=$(mktemp -d)
    if [[ ! -d "$tmpdir" ]]; then
        log_error "Failed to create temporary directory"
        exit 1
    fi
    echo "$tmpdir"
}

# Safe delete with confirmation
safe_delete() {
    local file="$1"
    if [[ -e "$file" ]]; then
        if ! confirm "Delete '$file'?"; then
            log_info "Skipped: $file"
            return 1
        fi
        rm -rf "$file"
    fi
}
```

## 6. POSIX Compliance Guidelines

```bash
# Use #!/usr/bin/env bash for portability
# Avoid bash-specific features when targeting POSIX
# Use [[ ]] only if bash-specific features are needed

# Portable alternatives:
# [[ $var ]]          -> [ -n "$var" ]
# [[ -z $var ]]       -> [ -z "$var" ]
# [[ -f $file ]]      -> [ -f "$file" ]
# [[ $a == $b ]]      -> [ "$a" = "$b" ]
# [[ $a != $b ]]      -> [ "$a" != "$b" ]
# [[ $a -gt $b ]]     -> [ "$a" -gt "$b" ]

# For strict POSIX, use:
#!/bin/sh
# instead of #!/usr/bin/env bash
```

## 7. Best Practices Checklist

- [ ] Use `set -e` to exit on error
- [ ] Use `set -u` to exit on undefined variable
- [ ] Use `set -o pipefail` for proper pipeline error handling
- [ ] Always quote variables containing spaces or special characters
- [ ] Use `$(command)` instead of backticks for command substitution
- [ ] Use `basename "$0"` instead of hardcoded script name
- [ ] Use meaningful variable names in UPPER_SNAKE_CASE
- [ ] Add comments for complex logic
- [ ] Use functions to organize code
- [ ] Define constants at the top of the script
- [ ] Validate all user input
- [ ] Use proper exit codes
- [ ] Clean up temporary files
- [ ] Handle signals appropriately
