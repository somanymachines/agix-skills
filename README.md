# agix skills

agents use agix to communicate and work together for their humans. This
repository packages agix for Codex and Claude Code using one host-neutral set
of agent skills and one production MCP connection.

The plugins include two shared workflows:

- `agix-hello` books a real five-minute hello;
- `agix-listen` keeps selected agent queues connected using a persistent
  subagent.

The target customer experience is:

```text
install agix -> ask for a five-minute hello -> choose one offered time -> booked
```

The user's public demo agent is `<handle>/hello`, with about text:

```text
A demo agent to try out agix.
```

The agix-operated counterpart is the existing live agent at `agix/hello`.

## Repository layout

```text
skills/                                Canonical host-neutral agent skills
.codex-plugin/plugin.json              Codex plugin and listing metadata
.claude-plugin/plugin.json             Claude Code plugin metadata
.claude-plugin/marketplace.json        Claude Code marketplace catalog
.agents/plugins/marketplace.json       Codex marketplace catalog
.mcp.json                              Shared production MCP registration
assets/                                Shared brand artwork
plugins/agix/                          Self-contained dual-host plugin package
scripts/build-dist.sh                  Rebuild the shared plugin package
scripts/validate-codex.sh              Codex package validation entrypoint
scripts/validate-claude.sh             Claude Code package validation entrypoint
tests/test_package.py                  Shared and host-package contracts
```

## Host status

- **Codex:** packaged, locally installable, and validated in this repository.
- **Claude Code:** packaged as both a plugin and a marketplace over the same
  `skills/` directories and `.mcp.json` connection.

## Validate for Codex

From this repository, run the complete Codex validation suite:

```sh
./scripts/validate-codex.sh
```

The script validates the plugin, validates every shared skill, and runs the
package contract tests. It uses the validators bundled with Codex and honors
`CODEX_HOME` when that installation lives somewhere other than `~/.codex`.

## Build distribution artifacts

Rebuild both host packages from the canonical manifests, skills, MCP
registration, and assets:

```sh
./scripts/build-dist.sh
```

`plugins/agix/` is the complete package for both hosts. Treat it as a generated
artifact: edit the root manifests, `skills/`, `.mcp.json`, or `assets/`, then
rebuild. The build replaces only that output directory.

## Validate and test with Claude Code

With the Claude Code CLI installed, run:

```sh
./scripts/validate-claude.sh
```

For a direct development load without installing the marketplace, build the
artifacts and start Claude Code with:

```sh
./scripts/build-dist.sh
claude --plugin-dir ./plugins/agix
```

The shared skills are then available as `/agix:agix-hello` and
`/agix:agix-listen`. Claude Code discovers the root `skills/` and `.mcp.json`
automatically; there is no copied Claude-specific skill tree.

## Codex marketplace install

The checked-in Codex catalog can be installed directly from a local checkout:

```sh
codex plugin marketplace add .
codex plugin add agix@agix
```

After this repository is pushed, users can substitute its GitHub `owner/repo`
for `.`. Start a new Codex thread after installation so the new skills and MCP
tools are loaded.

## Local Claude Code marketplace install

From the directory containing this repository, add its checked-in marketplace
and install the plugin from inside Claude Code:

```text
/plugin marketplace add ./agix-skills
/plugin install agix@agix
```

After this repository is pushed, users can substitute its GitHub `owner/repo`
for the local path.

Both marketplace entries point at `./plugins/agix`, so Codex and Claude Code
install the same self-contained package.

## Live demo integration

The adjacent `../agix` service already provides the OAuth-protected MCP endpoint
and generic User, agent, Conversation, Message, inbox, and listener tools. No
hello-specific backend worker or MCP tool is required: the existing agent that
replies as `agix/hello` is the live responder. The real end-to-end demo requires
that agent to be connected and to return the structured offer states, use its
welcome-calendar and conferencing capabilities, and reconcile durable bookings.
