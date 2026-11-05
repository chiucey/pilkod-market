#!/usr/bin/env bash
# Wrapper for quark-drive CLI: ensures MAVIS_AGENT=mavis is set so the
# CLI recognizes the Mavis Agent runtime environment.
#
# Usage:
#   bash scripts/quark-drive.sh <command> [args...]
# or equivalently:
#   ./scripts/quark-drive.sh <command> [args...]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

export MAVIS_AGENT="${MAVIS_AGENT:-mavis}"

exec node "$SCRIPT_DIR/quark-drive.cjs" "$@"