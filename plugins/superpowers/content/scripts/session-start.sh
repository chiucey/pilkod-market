#!/bin/sh
# SessionStart: inject the using-superpowers Skill so the Superpowers workflow
# applies from the first turn (ported from upstream obra/superpowers hooks).
# Read-only: no network, no writes. awk is the only external dependency;
# Node/Python/jq/bash are intentionally not required.
set -eu

plugin_root=${PLUGIN_ROOT:-${MINIMAX_PLUGIN_ROOT:-}}
if [ -z "$plugin_root" ]; then
  exit 0
fi

skill_md=$plugin_root/skills/using-superpowers/SKILL.md
if [ ! -f "$skill_md" ] || [ ! -r "$skill_md" ]; then
  exit 0
fi

# Prefer the system awk so a reduced Hook PATH still works; fail open without it.
if [ -x /usr/bin/awk ]; then
  awk_bin=/usr/bin/awk
else
  awk_bin=$(command -v awk 2>/dev/null || :)
fi
if [ -z "$awk_bin" ]; then
  exit 0
fi

# Emit one SessionStart JSON object and escape every JSON control character.
exec "$awk_bin" '
  BEGIN {
    ORS = ""
    for (i = 1; i < 32; i++) control[sprintf("%c", i)] = sprintf("\\u%04x", i)
    printf "%s", "{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\""
    printf "%s", "<EXTREMELY_IMPORTANT>\\nYou have superpowers.\\n\\n**Below is the full content of your superpowers:using-superpowers skill - your introduction to using skills. For all other skills, load them with the skill tool (for example superpowers:brainstorming):**\\n\\n"
  }
  {
    if (NR > 1) printf "%s", "\\n"
    line = $0
    for (i = 1; i <= length(line); i++) {
      c = substr(line, i, 1)
      if (c == "\\") printf "%s", "\\\\"
      else if (c == "\"") printf "%s", "\\\""
      else if (c in control) printf "%s", control[c]
      else printf "%s", c
    }
  }
  END {
    printf "%s", "\\n</EXTREMELY_IMPORTANT>\"}}\n"
  }
' "$skill_md"
