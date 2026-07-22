# skilljam plugin

A collection of publicly shared, general-purpose LLM skills, packaged as a
Claude Code plugin.

## Skills

_No skills yet — add one using the template below._

## Adding a skill

Copy [`skills/TEMPLATE.md`](skills/TEMPLATE.md) into a new folder as
`skills/<skill-name>/SKILL.md`:

```
skills/
├── TEMPLATE.md          # reference — not a live skill
└── my-skill/
    └── SKILL.md
```

Skills are namespaced by the plugin, so `skills/my-skill/` is invoked as
`/skilljam:my-skill`. The template documents every available frontmatter field;
see the [Claude Code skills docs](https://code.claude.com/docs/en/skills#frontmatter-reference)
for full details.
