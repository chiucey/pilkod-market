#!/bin/sh
# SessionStart preflight: PATH and standalone install path; no network or auth.
set -eu

cli_path=$(command -v meegle 2>/dev/null || :)
if [ -n "$cli_path" ] && [ -f "$cli_path" ] && [ -x "$cli_path" ]; then
  exit 0
fi

plugin_root=${PLUGIN_ROOT:-${MINIMAX_PLUGIN_ROOT:-}}
if [ -z "$plugin_root" ]; then
  exit 0
fi

if [ -n "${HOME:-}" ] && [ -f "$HOME/.minimax/bin/meegle" ] && [ -x "$HOME/.minimax/bin/meegle" ]; then
  standalone_cli=$HOME/.minimax/bin/meegle
  reminder="Meegle plugin: meegle is already installed at this absolute path: $standalone_cli
Use that quoted absolute executable path for Feishu Project/Meegle commands, or prepend its directory to PATH in EACH terminal invocation. Verify --version before first use. Do not reinstall merely because the Hook PATH did not contain it. An executable path is not proof of Feishu Project authentication."
else
  setup_doc=$plugin_root/skills/meegle/references/minimax-code-cli-setup.md
  reminder="Meegle plugin dependency check: meegle was not found in the Hook PATH or the standalone installation directory.
Before the first Feishu Project/Meegle operation, read this plugin's installation reference: $setup_doc
The terminal tool may have a different PATH: if it already resolves meegle, reuse it. Otherwise use the normal terminal tool to install CLI version 1.0.26; with working Node/npm the CLI-only command is: npm install -g @lark-project/meegle@1.0.26
If Node/npm is absent or the global prefix is unwritable, follow the reference's official npm archive download and SHA-256 verification procedure (no Node required). This plugin already includes the upstream meegle Skill; do not install another global Skills copy or run the all-in-one installation wizard.
After installation, verify --version and use the discovered absolute CLI path or set PATH for each command, then resume the original request. Do not start a download for an unrelated task. Configuration and OAuth are separate and follow meegle."
fi

# /usr/bin/awk is provided by supported macOS/Linux hosts; Node/Python/jq are
# intentionally not dependencies of this preflight. Escape all JSON controls.
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"'
printf '%s' "$reminder" | /usr/bin/awk '
  BEGIN { ORS=""; for (i=1;i<32;i++) control[sprintf("%c",i)]=sprintf("\\u%04x",i) }
  { if (NR>1) printf "\\n";
    for (i=1;i<=length($0);i++) {
      c=substr($0,i,1);
      if (c=="\\") printf "\\\\";
      else if (c=="\"") printf "\\\"";
      else if (c in control) printf "%s",control[c];
      else printf "%s",c;
    }
  }'
printf '"}}\n'
