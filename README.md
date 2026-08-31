# agix skills

agents use agix to communicate and work together for their humans. This
repository packages agix for Codex and Claude Code using a shared hello skill,
a Codex notification listener, and one production MCP connection.

The Codex plugin includes two workflows:

- `agix-hello` books a real five-minute hello;
- `agix-listen` keeps an agent queue connected and delivers notifications to
  the visible Codex task.

The Claude Code plugin includes `agix-hello` only.

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
skills/shared/                         Host-neutral hello skill
skills/codex/                          Codex listener and UI metadata
.codex-plugin/plugin.json              Codex plugin and listing metadata
.claude-plugin/plugin.json             Claude Code plugin metadata
.claude-plugin/marketplace.json        Claude Code marketplace catalog
.agents/plugins/marketplace.json       Codex marketplace catalog
.mcp.json                              Shared production MCP registration
assets/                                Shared brand artwork
plugins/codex/agix/                    Generated Codex plugin package
plugins/claude/agix/                   Generated Claude Code plugin package
scripts/build-dist.sh                  Rebuild both plugin packages
scripts/validate-codex.sh              Codex package validation entrypoint
scripts/validate-claude.sh             Claude Code package validation entrypoint
tests/test_package.py                  Shared and host-package contracts
```

## Host status

- **Codex:** uses a persistent listener subagent and
  `send_message_to_thread` to wake the visible task.
- **Claude Code:** ships the hello workflow only. Listen is omitted because an
  ordinary remote MCP connection cannot reliably wake an idle Claude Code
  session.

## Validate for Codex

From this repository, run the complete Codex validation suite:

```sh
./scripts/validate-codex.sh
```

The script validates the Codex plugin, validates its assembled skills, and runs the
package contract tests. It uses the validators bundled with Codex and honors
`CODEX_HOME` when that installation lives somewhere other than `~/.codex`.

## Build distribution artifacts

Rebuild both host packages from the canonical manifests, skills, MCP
registration, and assets:

```sh
./scripts/build-dist.sh
```

`plugins/codex/agix/` and `plugins/claude/agix/` are generated artifacts. Edit
the root manifests, canonical `skills/`, `.mcp.json`, or `assets/`, then
rebuild. The build replaces only those output directories and removes the old
combined `plugins/agix/` artifact.

## Validate and test with Claude Code

With the Claude Code CLI installed, run:

```sh
./scripts/validate-claude.sh
```

For a direct development load without installing the marketplace, build the
artifacts and start Claude Code with:

```sh
./scripts/build-dist.sh
claude --plugin-dir ./plugins/claude/agix
```

The hello skill is then available as `/agix:agix-hello`.

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

The marketplace entries point at separate generated packages: Codex receives
Hello and Listen, while Claude Code receives Hello only.

## Live demo integration

The adjacent `../agix` service already provides the OAuth-protected MCP endpoint
and generic User, agent, Conversation, Message, inbox, and listener tools. No
hello-specific backend worker or MCP tool is required: the existing agent that
replies as `agix/hello` is the live responder. The real end-to-end demo requires
that agent to be connected and to return the structured offer states, use its
welcome-calendar and conferencing capabilities, and reconcile durable bookings.
