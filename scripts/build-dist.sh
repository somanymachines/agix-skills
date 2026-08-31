#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir=$(mktemp -d)

cleanup() {
  rm -rf -- "${build_dir}"
}
trap cleanup EXIT HUP INT TERM

codex_build="${build_dir}/codex/agix"
claude_build="${build_dir}/claude/agix"
mkdir -p "${codex_build}/skills" "${claude_build}/skills"

for plugin_build in "${codex_build}" "${claude_build}"; do
  cp "${repo_dir}/.mcp.json" "${plugin_build}/.mcp.json"
  cp -R "${repo_dir}/assets" "${plugin_build}/assets"
  cp -R "${repo_dir}/skills/shared/agix-hello" \
    "${plugin_build}/skills/agix-hello"
done

cp -R "${repo_dir}/skills/codex/agix-hello/." \
  "${codex_build}/skills/agix-hello/"
cp -R "${repo_dir}/skills/codex/agix-listen" \
  "${codex_build}/skills/agix-listen"
cp -R "${repo_dir}/.codex-plugin" "${codex_build}/.codex-plugin"

mkdir -p "${claude_build}/.claude-plugin"
cp "${repo_dir}/.claude-plugin/plugin.json" \
  "${claude_build}/.claude-plugin/plugin.json"

rm -rf -- "${repo_dir}/plugins/agix" "${repo_dir}/plugins/codex" \
  "${repo_dir}/plugins/claude"
mkdir -p "${repo_dir}/plugins"
mv "${build_dir}/codex" "${repo_dir}/plugins/codex"
mv "${build_dir}/claude" "${repo_dir}/plugins/claude"

echo "Built ${repo_dir}/plugins/codex/agix"
echo "Built ${repo_dir}/plugins/claude/agix"
