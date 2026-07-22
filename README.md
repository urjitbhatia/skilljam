# skilljam

Publicly shared LLM skills, distributed as a [Claude Code](https://code.claude.com/docs/en/plugins)
plugin marketplace. Each plugin bundles one or more skills and is installed
individually.

## Install

Add this repository as a marketplace, then install the plugins you want:

```shell
/plugin marketplace add urjitbhatia/skilljam
/plugin install <plugin-name>@skilljam
/reload-plugins
```

Browse what's available with `/plugin` after adding the marketplace. Skills are
namespaced by their plugin, so they're invoked as `/<plugin-name>:<skill-name>`.

To pick up new or updated plugins later:

```shell
/plugin marketplace update skilljam
```

## Repository layout

```
.claude-plugin/
└── marketplace.json          # Catalog of all plugins (what users add)
plugins/
└── <plugin-name>/
    ├── .claude-plugin/
    │   └── plugin.json        # Plugin manifest (name, version, metadata)
    └── skills/
        └── <skill>/SKILL.md   # One folder per skill
templates/
└── SKILL.md.template          # Starting point for new skills
scripts/                       # Authoring helpers (see below)
Makefile
```

## Authoring plugins

Helper scripts wrap the repetitive parts of adding a plugin. Run `make help`
for the full list.

```shell
make new-plugin NAME=my-plugin   # scaffold plugins/my-plugin/ from the template
# ...edit plugins/my-plugin/.claude-plugin/plugin.json and skills/my-plugin/SKILL.md...
make register NAME=my-plugin     # add it to marketplace.json (carries over metadata)
make validate                    # check structure, frontmatter, and version sync
make list                        # list registered plugins
make release                     # interactive TUI to bump versions / sync marketplace
```

Notes:

- `new-plugin`, `register`, `validate`, and `list` need only Python 3.10+ (stdlib).
- `release` is an interactive [Textual](https://textual.textualize.io/) TUI; run
  `make setup` once (installs dependencies with [uv](https://docs.astral.sh/uv/))
  before using it.
- Plugins are versioned in their `plugin.json`. `make validate` flags any plugin
  whose `plugin.json` version is out of sync with its `marketplace.json` entry,
  and `make release` reconciles them.
- See [`templates/SKILL.md.template`](templates/SKILL.md.template) for every
  available skill frontmatter field, and the
  [skills reference](https://code.claude.com/docs/en/skills#frontmatter-reference)
  for details.

## License

[MIT](LICENSE)
