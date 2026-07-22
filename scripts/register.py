#!/usr/bin/env python3
"""Register a plugin in marketplace.json."""

import argparse
import json
import sys
from pathlib import Path

# Metadata fields copied from a plugin's plugin.json into its marketplace entry.
CARRIED_FIELDS = ("author", "homepage", "repository", "license", "keywords", "category")


def register_plugin(name: str) -> bool:
    root = Path(__file__).parent.parent
    plugins_dir = root / "plugins"
    plugin_dir = plugins_dir / name
    marketplace_file = root / ".claude-plugin" / "marketplace.json"

    # Check plugin exists
    if not plugin_dir.exists():
        print(
            f"Error: Plugin '{name}' does not exist. Run 'make new-plugin NAME={name}' first."
        )
        return False

    # Load marketplace.json
    marketplace = json.loads(marketplace_file.read_text())
    plugins = marketplace.get("plugins", [])

    # Check if already registered
    for p in plugins:
        if p["name"] == name:
            print(f"Plugin '{name}' is already registered.")
            return True

    # Build the entry, pulling metadata from plugin.json when available.
    description = "TODO: Add description"
    version = "1.0.0"
    extras = {}
    plugin_json_path = plugin_dir / ".claude-plugin" / "plugin.json"
    if plugin_json_path.exists():
        try:
            plugin_data = json.loads(plugin_json_path.read_text())
            description = plugin_data.get("description", description)
            version = plugin_data.get("version", version)
            extras = {k: plugin_data[k] for k in CARRIED_FIELDS if k in plugin_data}
        except json.JSONDecodeError:
            pass

    entry = {
        "name": name,
        "source": f"./plugins/{name}",
        "description": description,
        "version": version,
        **extras,
    }
    plugins.append(entry)
    marketplace["plugins"] = plugins

    # Write back
    marketplace_file.write_text(json.dumps(marketplace, indent=2) + "\n")
    print(f"Registered '{name}' in marketplace.json")

    if description == "TODO: Add description":
        print(
            "Don't forget to update the description in marketplace.json and plugin.json"
        )

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Register a plugin in marketplace.json"
    )
    parser.add_argument("name", help="Plugin name to register")
    args = parser.parse_args()

    sys.exit(0 if register_plugin(args.name) else 1)


if __name__ == "__main__":
    main()
