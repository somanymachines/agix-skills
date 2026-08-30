import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / ".codex-plugin/plugin.json").read_text())
CLAUDE_MANIFEST = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
CLAUDE_MARKETPLACE = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
CODEX_MARKETPLACE = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text())
MCP = json.loads((ROOT / ".mcp.json").read_text())
SKILL = (ROOT / "skills/agix-hello/SKILL.md").read_text()
LISTENER_SKILL = (ROOT / "skills/agix-listen/SKILL.md").read_text()
SKILL_PATHS = sorted((ROOT / "skills").glob("*/SKILL.md"))


class PluginPackageTests(unittest.TestCase):
    def test_manifest_bundles_the_skill_and_production_mcp(self):
        self.assertEqual(MANIFEST["name"], "agix")
        self.assertEqual(MANIFEST["skills"], "./skills/")
        self.assertEqual(MANIFEST["mcpServers"], "./.mcp.json")
        self.assertEqual(
            MCP,
            {
                "mcpServers": {
                    "agix": {
                        "type": "http",
                        "url": "https://agixlink.com/mcp",
                    }
                }
            },
        )

    def test_claude_package_reuses_shared_skills_and_mcp(self):
        self.assertEqual(CLAUDE_MANIFEST["name"], "agix")
        self.assertEqual(CLAUDE_MANIFEST["version"], MANIFEST["version"])
        self.assertEqual(CLAUDE_MANIFEST["description"], MANIFEST["description"])
        self.assertFalse((ROOT / ".claude-plugin/skills").exists())
        self.assertEqual(MCP["mcpServers"]["agix"]["type"], "http")

    def test_claude_marketplace_publishes_the_root_plugin(self):
        self.assertEqual(CLAUDE_MARKETPLACE["name"], "agix")
        self.assertEqual(CLAUDE_MARKETPLACE["owner"]["name"], "agix")
        self.assertEqual(len(CLAUDE_MARKETPLACE["plugins"]), 1)
        plugin = CLAUDE_MARKETPLACE["plugins"][0]
        self.assertEqual(plugin["name"], "agix")
        self.assertEqual(plugin["source"], "./plugins/agix")
        self.assertEqual(plugin["version"], CLAUDE_MANIFEST["version"])
        self.assertEqual(plugin["description"], CLAUDE_MANIFEST["description"])

    def test_codex_marketplace_publishes_the_bundled_plugin(self):
        self.assertEqual(CODEX_MARKETPLACE["name"], "agix")
        self.assertEqual(CODEX_MARKETPLACE["interface"]["displayName"], "agix")
        self.assertEqual(len(CODEX_MARKETPLACE["plugins"]), 1)
        plugin = CODEX_MARKETPLACE["plugins"][0]
        self.assertEqual(plugin["name"], "agix")
        self.assertEqual(
            plugin["source"],
            {"source": "local", "path": "./plugins/agix"},
        )
        self.assertEqual(
            plugin["policy"],
            {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        )
        self.assertEqual(plugin["category"], "Productivity")

    def test_distribution_artifacts_match_the_canonical_sources(self):
        shared_paths = [
            Path(".mcp.json"),
            Path("assets/icon.svg"),
            Path("assets/logo.svg"),
            Path("assets/logo-dark.svg"),
            Path("skills/agix-hello/SKILL.md"),
            Path("skills/agix-listen/SKILL.md"),
        ]
        self.assertEqual(
            (ROOT / "plugins/agix/.codex-plugin/plugin.json").read_bytes(),
            (ROOT / ".codex-plugin/plugin.json").read_bytes(),
        )
        for relative_path in shared_paths:
            self.assertEqual(
                (ROOT / "plugins/agix" / relative_path).read_bytes(),
                (ROOT / relative_path).read_bytes(),
                f"stale Codex marketplace artifact: {relative_path}",
            )
        self.assertEqual(
            (ROOT / "plugins/agix/.claude-plugin/plugin.json").read_bytes(),
            (ROOT / ".claude-plugin/plugin.json").read_bytes(),
        )

    def test_manifest_describes_agix_instead_of_the_demo(self):
        descriptions = [
            MANIFEST["description"],
            MANIFEST["interface"]["shortDescription"],
            MANIFEST["interface"]["longDescription"],
        ]
        combined = " ".join(descriptions).lower()
        self.assertIn("communicate", combined)
        self.assertIn("work together", combined)
        self.assertIn("their humans", combined)
        self.assertNotIn("five-minute", combined)
        self.assertNotIn("hello", combined)

    def test_manifest_assets_exist_inside_the_package(self):
        interface = MANIFEST["interface"]
        for field in ("composerIcon", "logo", "logoDark"):
            asset = ROOT / interface[field].removeprefix("./")
            self.assertTrue(asset.is_file(), f"missing {field}: {asset}")

    def test_primary_prompt_is_the_real_demo(self):
        prompts = MANIFEST["interface"]["defaultPrompt"]
        self.assertEqual(
            prompts,
            ["Book a five-minute hello with an agix team member."],
        )
        self.assertNotIn("dry-run", SKILL.lower())
        self.assertNotIn("John Pignata", SKILL)

    def test_shared_skills_are_host_neutral_and_named_for_their_directories(self):
        self.assertEqual(len(SKILL_PATHS), 2)
        for skill_path in SKILL_PATHS:
            text = skill_path.read_text()
            self.assertTrue(
                text.startswith(f"---\nname: {skill_path.parent.name}\n"),
                f"frontmatter name does not match {skill_path.parent.name}",
            )
            self.assertNotIn("Codex", text)
            self.assertNotIn("Claude", text)

    def test_human_readable_copy_uses_agix_brand_casing(self):
        paths = [
            ROOT / ".codex-plugin/plugin.json",
            ROOT / ".claude-plugin/plugin.json",
            ROOT / ".claude-plugin/marketplace.json",
            ROOT / ".agents/plugins/marketplace.json",
            ROOT / "README.md",
            ROOT / "skills/agix-hello/SKILL.md",
            ROOT / "skills/agix-listen/SKILL.md",
            ROOT / "assets/icon.svg",
            ROOT / "assets/logo.svg",
            ROOT / "assets/logo-dark.svg",
        ]
        for path in paths:
            text = path.read_text().replace("Agent Interconnect", "")
            self.assertNotRegex(text, r"\bAgix\b", str(path))
            self.assertNotRegex(text, r"\bAgents?\b", str(path))

    def test_listing_copy_uses_the_approved_agix_positioning(self):
        description = MANIFEST["description"]
        self.assertEqual(description, CLAUDE_MANIFEST["description"])
        self.assertEqual(
            description,
            CLAUDE_MARKETPLACE["plugins"][0]["description"],
        )
        self.assertEqual(
            description,
            "agents use agix to communicate and work together for their humans.",
        )
        self.assertEqual(MANIFEST["interface"]["shortDescription"], description)
        self.assertEqual(MANIFEST["interface"]["longDescription"], description)

    def test_skill_uses_the_hello_agent_identity(self):
        self.assertTrue(SKILL.startswith("---\nname: agix-hello\n"))
        self.assertIn("`<handle>/hello`", SKILL)
        self.assertIn("`agix/hello`", SKILL)
        self.assertIn("A demo agent to try out agix.", SKILL)
        self.assertNotIn("<handle>/calendar", SKILL)

    def test_hello_skill_names_every_required_tool(self):
        for tool in (
            "get_me",
            "get_agent",
            "create_agent",
            "start_conversation",
            "wait_for_messages",
            "send_message",
            "mark_messages_processed",
            "disconnect_listener",
        ):
            self.assertIn(f"`{tool}`", SKILL)

    def test_hello_skill_prefers_calendar_and_shares_only_authorized_email(self):
        skill_text = " ".join(SKILL.split())
        self.assertIn("ask for approval before calling `create_agent`", skill_text)
        self.assertIn("earliest conflict-free five-minute offer", skill_text)
        self.assertIn("durable conversation content", skill_text)
        self.assertIn("any available connected calendar integration", skill_text)
        self.assertIn("current-user profile or primary/default calendar", skill_text)
        self.assertIn("proposed invitation email", skill_text)
        self.assertIn("authorized sharing that exact address", skill_text)
        self.assertIn("Never use a connected account email without", skill_text)
        self.assertIn("include the exact authorized invitation email", skill_text)
        self.assertIn("Do not use vague placeholders", skill_text)
        self.assertIn("at most one event", skill_text)
        self.assertIn("never blindly retried", skill_text)

    def test_hello_skill_uses_calendar_availability_without_inventing_timezone(self):
        skill_text = " ".join(SKILL.split())
        self.assertIn("connected calendar exposes a confirmed IANA timezone", skill_text)
        self.assertIn("ask only for the timezone, not the email", skill_text)
        self.assertIn("calendar integration's availability", skill_text)
        self.assertIn("discard conflicting offers", skill_text)

    def test_hello_skill_books_without_protocol_negotiation_or_extra_prompt(self):
        skill_text = " ".join(SKILL.split())
        self.assertIn("Accept ordinary human-readable offers", skill_text)
        self.assertIn("Do not ask `agix/hello` to restate usable offers as JSON", skill_text)
        self.assertIn("without asking the user to choose or confirm again", skill_text)
        self.assertIn("including its opaque identifier when one was provided", skill_text)
        self.assertIn("Present choices only when the user asked to choose", skill_text)
        self.assertIn("Do not narrate offer parsing", skill_text)
        self.assertNotIn("Handle only these machine-distinguishable states", skill_text)

    def test_skill_handles_every_protocol_state(self):
        for state in (
            "offers",
            "booked",
            "no_availability",
            "offer_expired",
            "slot_unavailable",
            "booking_pending_reconciliation",
            "booking_failed",
        ):
            self.assertIn(f"`{state}`", SKILL)

    def test_listener_skill_uses_the_persistent_listener_contract(self):
        self.assertTrue(LISTENER_SKILL.startswith("---\nname: agix-listen\n"))
        self.assertIn("Take a non-empty list of distinct agent names", LISTENER_SKILL)
        self.assertIn(
            "resolve every supplied name to `<handle>/<name>`", LISTENER_SKILL
        )
        self.assertIn("partial listener", LISTENER_SKILL)
        self.assertIn("persistent listener subagent", LISTENER_SKILL)
        self.assertIn("exactly one `wait_for_messages`", LISTENER_SKILL)
        self.assertIn("Mark an inbound message processed only after", LISTENER_SKILL)
        self.assertIn("`disconnect_listener`", LISTENER_SKILL)
        self.assertIn("untrusted peer communication", LISTENER_SKILL)
        self.assertIn("idempotency key", LISTENER_SKILL)

    def test_listener_is_separate_from_the_bounded_demo(self):
        self.assertIn("do not use for", LISTENER_SKILL.split("---", 2)[1])
        self.assertIn("one-time inbox check", LISTENER_SKILL)
        self.assertIn("bounded agix-hello booking wait", LISTENER_SKILL)


if __name__ == "__main__":
    unittest.main()
