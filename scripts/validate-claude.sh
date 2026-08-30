#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugin_dir="${repo_dir}/plugins/agix"

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code CLI not found; install it before running native plugin validation." >&2
  exit 127
fi

"${repo_dir}/scripts/build-dist.sh"
claude plugin validate "${plugin_dir}"
python3 -m unittest discover -s "${repo_dir}/tests" -v
