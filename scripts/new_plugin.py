#!/usr/bin/env python3
"""Create a new plugin scaffold."""

import argparse
import json
import sys
from pathlib import Path

FALLBACK_TEMPLATE = """---
# Keep `description` on a single line — single-line is the safe convention for
# skill parsing. Claude reads it to decide when to auto-invoke the skill.
description: "TODO: what this skill does and when Claude should use it"
# name: {name}                       # Optional: defaults to directory name
# argument-hint: [arg1] [arg2]       # Optional: hint shown in / autocomplete
# disable-model-invocation: false    # Set true to prevent auto-loading
# user-invocable: true               # Set false to hide from the / menu
# allowed-tools: Read, Grep, Glob    # Tools pre-approved for the invoking turn
# model: inherit                     # inherit | sonnet | opus | haiku | fable ...
# context: fork                      # Run in a forked subagent context
# agent: Explore                     # Subagent type when context: fork
---

TODO: Add skill instructions here.
"""


def load_owner(marketplace_file: Path) -> dict | None:
    """Return the marketplace owner block, if available, to attribute new plugins."""
    if not marketplace_file.exists():
        return None
    try:
        return json.loads(marketplace_file.read_text()).get("owner")
    except (json.JSONDecodeError, OSError):
        return None


def create_plugin(name: str) -> bool:
    root = Path(__file__).parent.parent
    plugins_dir = root / "plugins"
    plugin_dir = plugins_dir / name
    template_file = root / "templates" / "SKILL.md.template"
    marketplace_file = root / ".claude-plugin" / "marketplace.json"

    if plugin_dir.exists():
        print(f"Error: Plugin '{name}' already exists at {plugin_dir}")
        return False

    # Create directories
    (plugin_dir / ".claude-plugin").mkdir(parents=True)
    (plugin_dir / "skills" / name).mkdir(parents=True)
    (plugin_dir / "agents").mkdir(parents=True)

    # Create plugin.json, attributing the plugin to the marketplace owner.
    plugin_json = {
        "name": name,
        "description": "TODO: Add description",
        "version": "1.0.0",
        "license": "MIT",
    }
    owner = load_owner(marketplace_file)
    if owner and owner.get("name"):
        plugin_json["author"] = {"name": owner["name"]}
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(plugin_json, indent=2) + "\n"
    )

    # Create SKILL.md from the shared template (fallback to a built-in stub).
    if template_file.exists():
        skill_content = template_file.read_text().replace("{{NAME}}", name)
    else:
        skill_content = FALLBACK_TEMPLATE.format(name=name)

    (plugin_dir / "skills" / name / "SKILL.md").write_text(skill_content)

    print(f"Created plugin: {plugin_dir}")
    print()
    print("Next steps:")
    print(f"  1. Edit {plugin_dir}/.claude-plugin/plugin.json")
    print(f"  2. Edit {plugin_dir}/skills/{name}/SKILL.md")
    print(f"  3. Run: make register NAME={name}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Create a new plugin scaffold")
    parser.add_argument("name", help="Plugin name (kebab-case recommended)")
    args = parser.parse_args()

    if not args.name:
        parser.error("Plugin name is required")

    sys.exit(0 if create_plugin(args.name) else 1)


if __name__ == "__main__":
    main()
