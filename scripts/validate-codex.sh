#!/bin/sh
set -eu

repo_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
plugin_dir="${repo_dir}/plugins/codex/agix"
codex_home_dir=${CODEX_HOME:-"${HOME}/.codex"}
plugin_creator_dir="${codex_home_dir}/skills/.system/plugin-creator"
skill_creator_dir="${codex_home_dir}/skills/.system/skill-creator"

"${repo_dir}/scripts/build-dist.sh"
python3 "${plugin_creator_dir}/scripts/validate_plugin.py" "${plugin_dir}"

for skill_dir in "${plugin_dir}"/skills/*; do
  python3 "${skill_creator_dir}/scripts/quick_validate.py" "${skill_dir}"
done

python3 -m unittest discover -s "${repo_dir}/tests" -v
