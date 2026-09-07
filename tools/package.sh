#!/usr/bin/env bash
# Build the installable .plugin file.
#
# The repository root IS the plugin, so packaging is a zip of the root with the
# repository's own scaffolding excluded — .github, tools and .git are ours, not the
# plugin's, and shipping them would put CI config inside every officer's install.
set -euo pipefail

cd "$(dirname "$0")/.."
NAME=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['name'])")
VER=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")
mkdir -p dist
OUT="dist/${NAME}.plugin"
rm -f "$OUT"

zip -rq "$OUT" . \
  -x '.git/*' -x '.github/*' -x 'tools/*' -x 'dist/*' \
  -x '*.DS_Store' -x '*__pycache__*' -x '*.pyc' -x '*.plugin'

echo "built $OUT  (${NAME} v${VER}, $(unzip -l "$OUT" | tail -1 | awk '{print $2}') files)"
