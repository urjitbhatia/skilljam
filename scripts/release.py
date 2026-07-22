#!/usr/bin/env python3
"""Release a plugin by updating marketplace.json version to match plugin.json."""

import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from textual.app import App, ComposeResult
    from textual.screen import Screen
    from textual.widgets import DataTable, Footer, Header, Label, OptionList
    from textual.widgets.option_list import Option
except ImportError:
    print("Error: 'textual' library not found. Run: make setup")
    sys.exit(1)


def bump_version(version: str, bump_type: str) -> str:
    """Bump a semantic version string.

    Args:
        version: Version string like "1.2.3"
        bump_type: One of "major", "minor", "patch"

    Returns:
        Bumped version string
    """
    match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not match:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch = map(int, match.groups())

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")


def update_plugin_version(plugin_json_file: Path, new_version: str) -> None:
    """Update the version in a plugin.json file."""
    plugin_json = json.loads(plugin_json_file.read_text())
    plugin_json["version"] = new_version
    plugin_json_file.write_text(json.dumps(plugin_json, indent=2) + "\n")


def update_marketplace_version(
    marketplace_file: Path, plugin_name: str, new_version: str
) -> None:
    """Update the version for a plugin in marketplace.json."""
    marketplace = json.loads(marketplace_file.read_text())

    for plugin in marketplace["plugins"]:
        if plugin["name"] == plugin_name:
            plugin["version"] = new_version
            break

    marketplace_file.write_text(json.dumps(marketplace, indent=2) + "\n")


def get_git_staged_files(plugin_dir: Path) -> list[str]:
    """Get list of staged files in the plugin directory."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=plugin_dir.parent.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        plugin_rel_path = plugin_dir.relative_to(plugin_dir.parent.parent)
        staged_files = [
            f
            for f in result.stdout.strip().split("\n")
            if f and f.startswith(str(plugin_rel_path))
        ]
        return staged_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_git_unstaged_files(plugin_dir: Path) -> list[str]:
    """Get list of unstaged modified files in the plugin directory."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=plugin_dir.parent.parent,
            capture_output=True,
            text=True,
            check=True,
        )
        plugin_rel_path = plugin_dir.relative_to(plugin_dir.parent.parent)
        unstaged_files = [
            f
            for f in result.stdout.strip().split("\n")
            if f and f.startswith(str(plugin_rel_path))
        ]
        return unstaged_files
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_commits_since_version_change(plugin_dir: Path, plugin_json_file: Path) -> int:
    """Get number of commits to plugin since plugin.json version was last changed."""
    try:
        result = subprocess.run(
            [
                "git",
                "log",
                "-1",
                "--format=%H",
                str(plugin_json_file.relative_to(plugin_dir.parent.parent)),
            ],
            cwd=plugin_dir.parent.parent,
            capture_output=True,
            text=True,
            check=True,
        )

        last_version_commit = result.stdout.strip()
        if not last_version_commit:
            return 0

        plugin_rel_path = plugin_dir.relative_to(plugin_dir.parent.parent)
        result = subprocess.run(
            [
                "git",
                "log",
                "--oneline",
                f"{last_version_commit}..HEAD",
                "--",
                str(plugin_rel_path),
            ],
            cwd=plugin_dir.parent.parent,
            capture_output=True,
            text=True,
            check=True,
        )

        commits = [line for line in result.stdout.strip().split("\n") if line]
        return len(commits)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 0


def get_git_status_summary(plugin_dir: Path, plugin_json_file: Path) -> str:
    """Get a one-line summary of git status for the plugin."""
    staged_files = get_git_staged_files(plugin_dir)
    unstaged_files = get_git_unstaged_files(plugin_dir)
    commits_since_version = get_commits_since_version_change(
        plugin_dir, plugin_json_file
    )

    parts = []

    if unstaged_files:
        parts.append(f"📝 {len(unstaged_files)} modified")

    if staged_files:
        parts.append(f"✅ {len(staged_files)} staged")

    if commits_since_version > 0:
        parts.append(f"⚠️  {commits_since_version} commits since bump")

    if not parts:
        parts.append("✓ Clean")

    return " | ".join(parts)


class PluginSelectionScreen(Screen):
    """Screen for selecting a plugin to release."""

    CSS = """
    PluginSelectionScreen {
        padding: 1;
    }

    DataTable {
        height: 100%;
    }

    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self, plugins_data: list[dict]) -> None:
        super().__init__()
        self.plugins_data = plugins_data

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label(
            "Select a plugin to release (↑↓ to navigate, Enter to select)", id="title"
        )
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        """Set up the data table."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.zebra_stripes = True

        # Add columns
        table.add_column("Plugin Name", width=40)
        table.add_column("Marketplace Version", width=15)
        table.add_column("Sync", width=8)
        table.add_column("Plugin Version", width=15)
        table.add_column("Git Status", width=35)

        # Add rows
        for data in self.plugins_data:
            name = data["name"]
            local_version = data["current_version"]
            registered_version = data["registered_version"]
            git_status = data["git_status"]

            # Highlight out-of-sync versions
            if local_version == registered_version:
                sync_indicator = ""
                marketplace_ver = registered_version
                plugin_ver = local_version
            else:
                sync_indicator = "[yellow]→[/yellow]"
                marketplace_ver = f"[yellow]{registered_version}[/yellow]"
                plugin_ver = f"[yellow]{local_version}[/yellow]"

            table.add_row(
                name, marketplace_ver, sync_indicator, plugin_ver, git_status, key=name
            )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle plugin selection."""
        plugin_name = event.row_key.value
        plugin_data = next(d for d in self.plugins_data if d["name"] == plugin_name)
        self.app.push_screen(ActionSelectionScreen(plugin_data))


class ActionSelectionScreen(Screen):
    """Screen for selecting an action (uprev, release, or both)."""

    CSS = """
    ActionSelectionScreen {
        align: center middle;
    }

    OptionList {
        width: 80;
        height: auto;
    }

    #info {
        dock: top;
        height: 5;
        padding: 1;
    }
    """

    def __init__(self, plugin_data: dict) -> None:
        super().__init__()
        self.plugin_data = plugin_data

    def compose(self) -> ComposeResult:
        yield Header()

        info_text = (
            f"Plugin: {self.plugin_data['name']}\n"
            f"Version: {self.plugin_data['current_version']}\n"
            f"Git: {self.plugin_data['git_status']}"
        )
        yield Label(info_text, id="info")

        version_status = self.plugin_data["version_status"]

        options = [
            Option("📝 Uprev only - Bump version in plugin.json", id="uprev"),
            Option(
                f"🚀 Release only - Sync marketplace ({version_status})", id="release"
            ),
            Option(
                "⚡ Uprev and Release - Bump version and sync marketplace", id="both"
            ),
        ]

        yield OptionList(*options)
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle action selection."""
        action = event.option.id

        if action in ["uprev", "both"]:
            self.app.push_screen(BumpTypeScreen(self.plugin_data, action))
        else:
            # Release only - no bump needed
            self.perform_release(self.plugin_data["current_version"])

    def perform_release(self, version: str) -> None:
        """Perform the release with the given version."""
        root = Path(__file__).parent.parent
        marketplace_file = root / ".claude-plugin" / "marketplace.json"

        update_marketplace_version(marketplace_file, self.plugin_data["name"], version)

        self.app.push_screen(
            ResultScreen(
                f"✓ Plugin '{self.plugin_data['name']}' released at version {version}",
                success=True,
            )
        )


class BumpTypeScreen(Screen):
    """Screen for selecting version bump type."""

    CSS = """
    BumpTypeScreen {
        align: center middle;
    }

    OptionList {
        width: 80;
        height: auto;
    }

    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        text-style: bold;
    }
    """

    def __init__(self, plugin_data: dict, action: str) -> None:
        super().__init__()
        self.plugin_data = plugin_data
        self.action = action

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Select version bump type", id="title")

        current = self.plugin_data["current_version"]

        options = [
            Option(
                f"🔴 Major - {current} → {bump_version(current, 'major')} "
                f"(breaking changes)",
                id="major",
            ),
            Option(
                f"🟡 Minor - {current} → {bump_version(current, 'minor')} "
                f"(new features)",
                id="minor",
            ),
            Option(
                f"🟢 Patch - {current} → {bump_version(current, 'patch')} (bug fixes)",
                id="patch",
            ),
        ]

        yield OptionList(*options)
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle bump type selection."""
        bump_type = event.option.id
        current_version = self.plugin_data["current_version"]
        new_version = bump_version(current_version, bump_type)

        root = Path(__file__).parent.parent
        plugin_dir = root / "plugins" / self.plugin_data["name"]
        plugin_json_file = plugin_dir / ".claude-plugin" / "plugin.json"
        marketplace_file = root / ".claude-plugin" / "marketplace.json"

        # Update plugin.json
        update_plugin_version(plugin_json_file, new_version)

        if self.action == "both":
            # Also update marketplace
            update_marketplace_version(
                marketplace_file, self.plugin_data["name"], new_version
            )
            message = (
                f"✓ Plugin '{self.plugin_data['name']}' bumped and released: "
                f"{current_version} → {new_version}"
            )
        else:
            # Just uprev
            message = (
                f"✓ Plugin '{self.plugin_data['name']}' version bumped to "
                f"{new_version}\nRun 'make release' again to sync marketplace.json"
            )

        self.app.push_screen(ResultScreen(message, success=True))


class ResultScreen(Screen):
    """Screen showing the result of the operation."""

    CSS = """
    ResultScreen {
        align: center middle;
    }

    #result {
        width: 80;
        height: auto;
        padding: 2;
        text-align: center;
    }

    .success {
        color: $success;
    }

    .error {
        color: $error;
    }
    """

    def __init__(self, message: str, success: bool = True) -> None:
        super().__init__()
        self.message = message
        self.success = success

    def compose(self) -> ComposeResult:
        yield Header()
        css_class = "success" if self.success else "error"
        yield Label(self.message, id="result", classes=css_class)
        yield Footer()

    def on_key(self, event) -> None:
        """Exit on any key press."""
        self.app.exit()


class ReleaseApp(App):
    """Textual app for plugin release management."""

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.root = Path(__file__).parent.parent

    def on_mount(self) -> None:
        """Load plugin data and show selection screen."""
        plugins_dir = self.root / "plugins"
        marketplace_file = self.root / ".claude-plugin" / "marketplace.json"

        if not marketplace_file.exists():
            self.exit(message="Error: .claude-plugin/marketplace.json not found")
            return

        try:
            marketplace = json.loads(marketplace_file.read_text())
        except json.JSONDecodeError as e:
            self.exit(message=f"Error: marketplace.json is invalid JSON: {e}")
            return

        registered_plugins = {p["name"]: p for p in marketplace.get("plugins", [])}

        if not registered_plugins:
            self.exit(message="Error: No plugins found in marketplace.json")
            return

        plugins_data = []
        for name, plugin_info in sorted(registered_plugins.items()):
            plugin_dir = plugins_dir / name
            plugin_json_file = plugin_dir / ".claude-plugin" / "plugin.json"

            if not plugin_json_file.exists():
                continue

            try:
                plugin_json = json.loads(plugin_json_file.read_text())
                local_version = plugin_json.get("version", "unknown")
                registered_version = plugin_info.get("version", "unknown")

                git_status = get_git_status_summary(plugin_dir, plugin_json_file)

                if local_version == registered_version:
                    version_info = f"✓ {local_version}"
                    version_status = "✓ synced"
                else:
                    version_info = f"⚠ {local_version} → {registered_version}"
                    version_status = f"{local_version} vs {registered_version}"

                plugins_data.append(
                    {
                        "name": name,
                        "current_version": local_version,
                        "registered_version": registered_version,
                        "version_info": version_info,
                        "version_status": version_status,
                        "git_status": git_status,
                    }
                )

            except json.JSONDecodeError:
                continue

        if not plugins_data:
            self.exit(message="Error: No valid plugins found to release")
            return

        self.push_screen(PluginSelectionScreen(plugins_data))


def release() -> bool:
    """Run the release TUI."""
    app = ReleaseApp()
    app.run()
    return True


if __name__ == "__main__":
    sys.exit(0 if release() else 1)
