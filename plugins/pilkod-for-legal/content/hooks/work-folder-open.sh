#!/bin/sh
# Pilkod For Legal UserPromptSubmit hook for macOS and other POSIX systems.
#
# Only a prompt that does nothing but open Pilkod For Legal receives entry
# guidance; every other prompt gets "{}". The Host's per-turn session id is the
# only page selector (ADR 0050): never infer ownership from cwd or history.
#
# Uses only sh, head, sed and grep from the operating system, so users never
# install Node or another runtime (ADR 0064). work-folder-open.ps1 is the
# Windows twin; both print the shared work-folder-open-context*.txt text.
LC_ALL=C
export LC_ALL
here=$(dirname -- "$0")
empty() { printf '{}\n'; exit 0; }

# The Host writes one line of JSON.stringify output. Oversized input is never
# an opening prompt.
input=$(head -c 256001)
[ "${#input}" -le 256000 ] || empty

# Fast path for ordinary prompts: no further processes are started.
case $input in
  *[Mm][Ii][Nn][Ii][Mm][Aa][Xx]-[Ff][Oo][Rr]-[Ll][Ee][Gg][Aa][Ll]*) ;;
  *[Mm][Ii][Nn][Ii][Mm][Aa][Xx]\ [Ff][Oo][Rr]\ [Ll][Ee][Gg][Aa][Ll]*) ;;
  *) empty ;;
esac
case $input in
  *'"hook_event_name":"UserPromptSubmit"'*) ;;
  *) empty ;;
esac

# JavaScript \s: ASCII whitespace plus these Unicode spaces, as UTF-8 bytes.
ws=$(printf '([[:space:]]|\302\240|\341\232\200|\342\200\200|\342\200\201|\342\200\202|\342\200\203|\342\200\204|'\
'\342\200\205|\342\200\206|\342\200\207|\342\200\210|\342\200\211|\342\200\212|\342\200\250|'\
'\342\200\251|\342\200\257|\342\201\237|\343\200\200|\357\273\277)')

# One sed pass takes the top-level "prompt" string: a key follows "{" or ","
# and every quote inside a JSON string is escaped, so a value cannot imitate a
# key (the Host's metadata has no nested prompt). JSON.stringify escapes only
# control characters; the whitespace ones (\t \n \v \f \r) act as spaces.
# Then trim like String.prototype.trim.
prompt=$(printf '%s\n' "$input" | sed -n -E \
  -e 's/^.*[{,]"prompt":"(([^"\\]|\\.)*)"[,}].*$/\1/' -e 't found' -e 'b' -e ':found' \
  -e 's/\\[tnfr]/ /g' -e 's/\\u000[bB]/ /g' -e "s/^$ws+//" -e "s/$ws+\$//" -e 'p')
# Any other escape, a quote or a backslash cannot belong to an opening prompt.
case $prompt in
  '' | *\\*) empty ;;
esac

name='(@?minimax-for-legal|pilkod for legal)'
opening="^($name|(请)?(打开|启动)$ws*$name($ws*(插件|工作台|首页))?|(please$ws+)?open$ws+$name)(。|[.!]|！)?\$"
printf '%s\n' "$prompt" | grep -E -i -q -- "$opening" || empty

session=$(printf '%s\n' "$input" | sed -n -E 's/^.*[{,]"session_id":"([A-Za-z0-9_-]{1,200})"[,}].*$/\1/p')
if [ -n "$session" ]; then
  sed "s/__SESSION_ID__/$session/" "$here/work-folder-open-context.txt"
else
  cat "$here/work-folder-open-context-no-session.txt"
fi
