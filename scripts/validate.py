#!/usr/bin/env python3
"""Validate the marketplace structure and all plugins."""

import json
import sys
from pathlib import Path


# ANSI color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def error(msg: str) -> None:
    print(f"{Colors.RED}✗ {msg}{Colors.RESET}")


def success(msg: str) -> None:
    print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")


def warn(msg: str) -> None:
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")


def validate_yaml_frontmatter(skill_path: Path) -> list[str]:
    """Validate SKILL.md has valid YAML frontmatter with description."""
    errors = []
    content = skill_path.read_text()

    if not content.startswith("---"):
        errors.append(f"{skill_path}: Missing YAML frontmatter (must start with ---)")
        return errors

    # Find the closing ---
    rest = content[3:]
    end_idx = rest.find("---")
    if end_idx == -1:
        errors.append(f"{skill_path}: Missing closing --- for frontmatter")
        return errors

    frontmatter = rest[:end_idx].strip()

    # Check for description (simple check, not full YAML parse)
    has_description = False
    for line in frontmatter.split("\n"):
        line = line.strip()
        if line.startswith("description:") and not line.startswith("#"):
            has_description = True
            # Multiline block scalars can break skill parsing; require single-line.
            if line in ("description: |", "description: >"):
                errors.append(
                    f"{skill_path}: Multiline description (| or >) can break parsing - "
                    f"use a single-line quoted string"
                )
            break

    if not has_description:
        errors.append(f"{skill_path}: Missing 'description' in frontmatter")

    return errors


def validate() -> bool:
    root = Path(__file__).parent.parent
    plugins_dir = root / "plugins"
    marketplace_file = root / ".claude-plugin" / "marketplace.json"

    errors = []
    warnings = []
    version_mismatches = []  # Track version mismatches separately for table display

    # Check marketplace.json exists and is valid
    if not marketplace_file.exists():
        error(".claude-plugin/marketplace.json not found")
        return False

    try:
        marketplace = json.loads(marketplace_file.read_text())
        success("marketplace.json is valid JSON")
    except json.JSONDecodeError as e:
        error(f"marketplace.json is invalid JSON: {e}")
        return False

    # Get registered plugins from marketplace.json
    registered_plugins = {p["name"]: p for p in marketplace.get("plugins", [])}

    # Get actual plugin directories
    actual_plugins = set()
    if plugins_dir.exists():
        for d in plugins_dir.iterdir():
            if d.is_dir() and d.name != ".gitkeep":
                actual_plugins.add(d.name)

    # Check each registered plugin exists and has required files
    for name, plugin_info in registered_plugins.items():
        plugin_dir = plugins_dir / name

        if not plugin_dir.exists():
            errors.append(
                f"Plugin '{name}' is registered but directory doesn't exist at "
                f"{plugin_info.get('source', 'unknown')}"
            )
            continue

        # Check plugin.json
        plugin_json = None
        plugin_json_file = plugin_dir / ".claude-plugin" / "plugin.json"
        if not plugin_json_file.exists():
            errors.append(f"Plugin '{name}': missing .claude-plugin/plugin.json")
        else:
            try:
                plugin_json = json.loads(plugin_json_file.read_text())
                success(f"{name}/plugin.json is valid")
            except json.JSONDecodeError as e:
                errors.append(f"Plugin '{name}': plugin.json is invalid JSON: {e}")

        # Check for at least one skill or agent
        skills_dir = plugin_dir / "skills"
        agents_dir = plugin_dir / "agents"

        has_skill = False
        has_agent = False

        if skills_dir.exists():
            for skill_dir in skills_dir.iterdir():
                if skill_dir.is_dir():
                    skill_md = skill_dir / "SKILL.md"
                    if skill_md.exists():
                        has_skill = True
                        errors.extend(validate_yaml_frontmatter(skill_md))

        # Agents are flat markdown files in agents/ (e.g. agents/reviewer.md).
        if agents_dir.exists():
            has_agent = any(
                f.is_file() and f.suffix == ".md" for f in agents_dir.iterdir()
            )

        if not has_skill and not has_agent:
            warnings.append(
                f"Plugin '{name}': no skill or agent found "
                f"(expected: skills/<skill-name>/SKILL.md or agents/<agent-name>.md)"
            )

        # Check that the published version and the local version match (when both exist).
        local_version = plugin_json.get("version") if plugin_json else None
        registered_version = plugin_info.get("version")
        if local_version and registered_version and local_version != registered_version:
            version_mismatches.append(
                {
                    "name": name,
                    "local": local_version,
                    "registered": registered_version,
                }
            )

    # Check for unregistered plugins
    unregistered = actual_plugins - set(registered_plugins.keys())
    for name in unregistered:
        warnings.append(
            f"Plugin '{name}' exists but is not registered in marketplace.json "
            f"(run: make register NAME={name})"
        )

    # Print version mismatches as a table
    if version_mismatches:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}Version Mismatches:{Colors.RESET}")
        print(
            f"{Colors.YELLOW}{'Plugin':<40} {'Local Version':<15} "
            f"{'Registered Version':<15}{Colors.RESET}"
        )
        print(f"{Colors.YELLOW}{'-' * 40} {'-' * 15} {'-' * 15}{Colors.RESET}")
        for mismatch in version_mismatches:
            print(
                f"{Colors.YELLOW}{mismatch['name']:<40} {mismatch['local']:<15} "
                f"{mismatch['registered']:<15}{Colors.RESET}"
            )
        print(
            f"\n{Colors.YELLOW}Hint: run 'make release' to sync marketplace.json "
            f"versions with plugin.json.{Colors.RESET}\n"
        )

    # Print warnings
    for w in warnings:
        warn(w)

    # Print errors
    for e in errors:
        error(e)

    print()
    total_warnings = len(warnings) + len(version_mismatches)
    if errors:
        print(
            f"{Colors.BOLD}{Colors.RED}Validation failed with "
            f"{len(errors)} error(s){Colors.RESET}"
        )
        return False
    elif total_warnings > 0:
        print(
            f"{Colors.BOLD}{Colors.YELLOW}Validation passed with "
            f"{total_warnings} warning(s){Colors.RESET}"
        )
        return True
    else:
        print(f"{Colors.BOLD}{Colors.GREEN}Validation passed!{Colors.RESET}")
        return True


if __name__ == "__main__":
    sys.exit(0 if validate() else 1)
