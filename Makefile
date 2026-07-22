.PHONY: help setup new-plugin register validate list release format-scripts

help:
	@echo "Usage:"
	@echo "  make new-plugin NAME=<name>   Create a new plugin scaffold"
	@echo "  make register NAME=<name>     Register plugin in marketplace.json"
	@echo "  make validate                 Validate marketplace structure"
	@echo "  make list                     List registered plugins"
	@echo "  make release                  Release a plugin (sync marketplace version)"
	@echo "  make setup                    Install dependencies for 'make release' (uv)"

setup:
	@echo "Installing dependencies with uv..."
	@uv sync

new-plugin:
ifndef NAME
	$(error NAME is required. Usage: make new-plugin NAME=my-plugin)
endif
	@python3 scripts/new_plugin.py $(NAME)

register:
ifndef NAME
	$(error NAME is required. Usage: make register NAME=my-plugin)
endif
	@python3 scripts/register.py $(NAME)

validate:
	@python3 scripts/validate.py

# 'release' is an interactive TUI and needs textual; run 'make setup' first.
release:
	@uv run python scripts/release.py

format-scripts:
	@uvx ruff format scripts/

list:
	@python3 -c "import json; \
data = json.load(open('.claude-plugin/marketplace.json')); \
plugins = data.get('plugins', []); \
print('Registered plugins:') if plugins else print('No plugins registered.'); \
[print(f'  - {p[\"name\"]}: {p.get(\"description\", \"No description\")}') for p in plugins]"
