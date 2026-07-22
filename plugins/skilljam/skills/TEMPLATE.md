# Skill template

Copy this file into a new folder as `skills/<skill-name>/SKILL.md`, then fill it
in. Do not leave it named `TEMPLATE.md` — a bare `.md` file here does not
register as a skill; only `<skill-name>/SKILL.md` directories do.

In this plugin, skills are namespaced, so `skills/my-skill/SKILL.md` is invoked
as `/skilljam:my-skill`.

```markdown
---
# Keep `description` on a single line. Single-line is the safe convention; some
# YAML block-scalar styles ( | ) have tripped up parsing in the past.
description: "TODO: what this skill does AND when to use it — Claude reads this to auto-invoke"

# All fields below are optional. Uncomment what you need.

# name: my-skill              # Display name. Defaults to the directory name.
                              # In a plugin, this also sets the command's last
                              # segment: `name: fancy` -> /skilljam:fancy

# when_to_use: "..."          # Extra trigger phrases / example requests.
                              # Appended to description in the skill listing.

# argument-hint: [arg1] [arg2]   # Shown during / autocomplete
# arguments: [arg1, arg2]        # Named positional args for $arg1 / $arg2 in the body

# disable-model-invocation: false  # true = only the user can run it (never auto-loaded)
# user-invocable: true             # false = hide from the / menu (Claude-only knowledge)

# allowed-tools: Read, Grep, Glob  # Pre-approved tools for the invoking turn only
                                   # (grant clears on your next message)
# disallowed-tools: AskUserQuestion # Tools removed while this skill is active

# model: inherit              # inherit | sonnet | opus | haiku | fable ... (for this turn)
# effort: medium              # low | medium | high | xhigh | max

# paths: "src/**/*.ts"        # Auto-activate only when working on matching files

# context: fork               # Run the skill in a forked subagent context
# agent: Explore              # Subagent type to use when context: fork
---

TODO: Add skill instructions here. Write them as direct guidance
("When asked to X, do Y"). Use $ARGUMENTS to reference user input.
```

Supporting files (scripts, references, templates) can live alongside `SKILL.md`
in the same folder and be referenced via `${CLAUDE_SKILL_DIR}`.

See the [Claude Code skills docs](https://code.claude.com/docs/en/skills#frontmatter-reference)
for the full frontmatter reference.
