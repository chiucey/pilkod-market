#!/bin/bash
#========================================#
# OpenClaw Uninstaller Script
# Version: 1.0
# Description: 一键全自动卸载 OpenClaw 工具
#========================================#

set -e

echo "=========================================="
echo "  OpenClaw Uninstaller v1.0"
echo "=========================================="

# Color definitions
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#---------------------------------------
# Step 1: Detect installation status
#---------------------------------------
echo ""
log_info "Step 1: Detecting installation status..."

detected=""

if npm list -g --depth=0 2>/dev/null | grep -qi claw; then
    detected="${detected}npm "
    log_info "Found npm global installation"
fi

if pip list 2>/dev/null | grep -qi openclaw; then
    detected="${detected}pip "
    log_info "Found pip installation"
fi

if uv pip list 2>/dev/null | grep -qi openclaw; then
    detected="${detected}uv "
    log_info "Found uv pip installation"
fi

if [ -d "$HOME/.openclaw" ] || [ -d "$HOME/.config/openclaw" ]; then
    detected="${detected}config "
    log_info "Found configuration files"
fi

if [ -z "$detected" ]; then
    log_warn "No OpenClaw installation detected"
fi

#---------------------------------------
# Step 2: npm uninstall
#---------------------------------------
echo ""
log_info "Step 2: npm uninstall..."

npm uninstall -g openclaw 2>/dev/null && log_info "npm openclaw uninstalled" || log_warn "No npm openclaw"
npm uninstall -g clawd 2>/dev/null && log_info "npm clawd uninstalled" || log_warn "No npm clawd"
npm uninstall -g @openclaw/cli 2>/dev/null && log_info "npm @openclaw/cli uninstalled" || log_warn "No npm @openclaw/cli"

#---------------------------------------
# Step 3: pip uninstall
#---------------------------------------
echo ""
log_info "Step 3: pip uninstall..."

pip uninstall openclaw -y 2>/dev/null && log_info "pip openclaw uninstalled" || log_warn "No pip openclaw"
uv pip uninstall openclaw 2>/dev/null && log_info "uv pip openclaw uninstalled" || log_warn "No uv pip openclaw"

#---------------------------------------
# Step 4: Clean config files
#---------------------------------------
echo ""
log_info "Step 4: Cleaning configuration files..."

[ -d "$HOME/.openclaw" ] && rm -rf "$HOME/.openclaw" && log_info "Deleted ~/.openclaw"
[ -d "$HOME/.config/openclaw" ] && rm -rf "$HOME/.config/openclaw" && log_info "Deleted ~/.config/openclaw"
[ -d "$HOME/.clawd" ] && rm -rf "$HOME/.clawd" && log_info "Deleted ~/.clawd"
[ -d "$HOME/.openclaw-plugins" ] && rm -rf "$HOME/.openclaw-plugins" && log_info "Deleted ~/.openclaw-plugins"

#---------------------------------------
# Step 5: Clean npm residue
#---------------------------------------
echo ""
log_info "Step 5: Cleaning npm residue..."

rm -rf "$HOME/.npm/_npx"/*openclaw* 2>/dev/null && log_info "npm npx residue cleaned" || true
rm -rf "/tmp/.npm-global/lib/node_modules/openclaw"* 2>/dev/null && log_info "npm global residue cleaned" || true
rm -rf "/tmp/.npm-global/lib/node_modules/clawd"* 2>/dev/null && log_info "clawd residue cleaned" || true

#---------------------------------------
# Step 6: Verify uninstallation
#---------------------------------------
echo ""
log_info "Step 6: Verifying uninstallation..."

if which openclaw >/dev/null 2>&1; then
    log_error "OpenClaw still in PATH"
    exit 1
elif pip show openclaw >/dev/null 2>&1; then
    log_error "OpenClaw still installed via pip"
    exit 1
elif uv pip show openclaw >/dev/null 2>&1; then
    log_error "OpenClaw still installed via uv pip"
    exit 1
else
    echo ""
    echo "=========================================="
    echo -e "  ${GREEN}OpenClaw uninstall completed!${NC}"
    echo "=========================================="
fi
