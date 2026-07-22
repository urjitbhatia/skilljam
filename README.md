# skilljam

Publicly shared LLM skills, distributed as a [Claude Code](https://code.claude.com/docs/en/plugins)
plugin marketplace.

## Install

Add this repository as a marketplace, then install the plugin:

```shell
/plugin marketplace add urjitbhatia/skilljam
/plugin install skilljam@skilljam
/reload-plugins
```

Skills ship namespaced under the plugin, so they're invoked as
`/skilljam:<skill-name>`.

To pick up new skills after they're published, refresh the marketplace:

```shell
/plugin marketplace update skilljam
```

## Repository layout

```
.claude-plugin/
└── marketplace.json          # Marketplace catalog (what users add)
plugins/
└── skilljam/
    ├── .claude-plugin/
    │   └── plugin.json        # Plugin manifest
    ├── skills/
    │   └── <skill>/SKILL.md   # One folder per skill
    └── README.md
```

## Contributing a skill

Add a folder under `plugins/skilljam/skills/` containing a `SKILL.md` file.
See [`plugins/skilljam/README.md`](plugins/skilljam/README.md) for the format.

## License

[MIT](LICENSE)
