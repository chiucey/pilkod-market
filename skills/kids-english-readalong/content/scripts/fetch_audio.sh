#!/usr/bin/env bash
# Download TTS assets by node_id into a local directory.
# Usage: fetch_audio.sh <outdir> <node_id:filename> [<node_id:filename> ...]
set -euo pipefail

outdir="${1:?usage: fetch_audio.sh <outdir> <node_id:filename> [...]}"
shift

mkdir -p "$outdir"

for pair in "$@"; do
  node_id="${pair%%:*}"
  name="${pair##*:}"
  url="$(mcode-tools get_asset_url "$node_id" \
    | python3 -c 'import sys,json; print(json.load(sys.stdin)["download_url"])')"
  curl -sL "$url" -o "$outdir/$name"
  echo "$outdir/$name"
done
