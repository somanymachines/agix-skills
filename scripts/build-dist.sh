#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
build_dir=$(mktemp -d)

cleanup() {
  rm -rf -- "${build_dir}"
}
trap cleanup EXIT HUP INT TERM

plugin_build="${build_dir}/agix"
mkdir -p "${plugin_build}"

cp "${repo_dir}/.mcp.json" "${plugin_build}/.mcp.json"
cp -R "${repo_dir}/skills" "${plugin_build}/skills"
cp -R "${repo_dir}/assets" "${plugin_build}/assets"

cp -R "${repo_dir}/.codex-plugin" "${plugin_build}/.codex-plugin"
mkdir -p "${plugin_build}/.claude-plugin"
cp "${repo_dir}/.claude-plugin/plugin.json" \
  "${plugin_build}/.claude-plugin/plugin.json"

rm -rf -- "${repo_dir}/plugins/agix"
mkdir -p "${repo_dir}/plugins"
mv "${plugin_build}" "${repo_dir}/plugins/agix"

echo "Built ${repo_dir}/plugins/agix"
