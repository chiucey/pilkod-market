#!/bin/bash
set -e

echo "=== Helios Skill Setup ==="

pip install -r requirements.txt
playwright install chromium

CONFIG_DIR="$HOME/.helios"
CONFIG_FILE="$CONFIG_DIR/config.json"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_FILE" ]; then
  cat > "$CONFIG_FILE" << 'JSONEOF'
{
  "session_dir": "~/.helios/session",
  "staging_dir": "~/helios-staging",
  "expense_cap": 115.00,
  "non_gc_dinner_attendees": [],
  "helios_url": "https://console.huilianyi.com/"
}
JSONEOF
  echo "Created default config at $CONFIG_FILE"
fi

mkdir -p "$HOME/helios-staging"

echo ""
echo "Setup complete!"
echo "Edit ~/.helios/config.json, then run: python scripts/helios_bot.py --login"
