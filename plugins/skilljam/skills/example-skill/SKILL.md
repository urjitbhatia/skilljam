---
name: example-skill
description: A template skill demonstrating the SKILL.md format. Replace this with a real description of when Claude should use the skill — the model reads this text to decide when to invoke it, so be specific about the triggering task and keywords.
---

# Example Skill

This file is a template. Each skill lives in its own folder under `skills/`,
and the folder must contain a `SKILL.md` file. Once the plugin is installed,
this skill is invocable as `/skilljam:example-skill`.

## How to write a skill

1. **Frontmatter** (between the `---` lines) is required:
   - `name`: the skill's identifier (matches the folder name).
   - `description`: the single most important field. Claude uses it to decide
     when to invoke the skill automatically, so describe the task, the trigger
     conditions, and relevant keywords.
2. **Body**: the instructions Claude follows once the skill is invoked. Write
   it as direct guidance ("When asked to X, do Y").
3. **Arguments**: use the `$ARGUMENTS` placeholder to capture text the user
   passes after the skill name.

## Replace me

Delete this folder and add your own skills as `skills/<skill-name>/SKILL.md`.
Supporting files (scripts, references, templates) can live alongside `SKILL.md`
in the same folder.
