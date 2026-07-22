# skilljam plugin

A collection of publicly shared, general-purpose LLM skills, packaged as a
Claude Code plugin.

## Skills

| Skill | Invoke as | Description |
| :---- | :-------- | :---------- |
| `example-skill` | `/skilljam:example-skill` | Template demonstrating the SKILL.md format (replace with real skills). |

## Adding a skill

Create a new folder under `skills/` containing a `SKILL.md` file:

```
skills/
└── my-skill/
    └── SKILL.md
```

Skills are namespaced by the plugin, so `skills/my-skill/` is invoked as
`/skilljam:my-skill`. See the [Claude Code skills docs](https://code.claude.com/docs/en/skills)
for authoring details.
