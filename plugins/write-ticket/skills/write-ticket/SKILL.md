---
name: write-ticket
description: 'Write or update a well-structured Linear ticket (and create it via the Linear MCP). Turns a rough description, a bug report, or research notes into a scannable ticket: conventional [TYPE] scope — summary title, an at-a-glance header, an upfront ask, prior research, details, and follow-ups — using tables, lists, and bold instead of walls of text. Use when the user says /write-ticket, "write a ticket", "file a ticket", "create a Linear ticket", "turn this into a ticket", or "update ticket XYZ-123 with …", or when you have to create a Linear ticket as part of your workflow.'
when_to_use: 'Use when the user says /write-ticket, "write a ticket", "file a ticket", "create a Linear ticket", "create a ticket", "turn this into a ticket", "update ticket XYZ-123", or "draft a ticket" — or whenever creating a Linear ticket is part of the workflow.'
---

Write a Linear ticket that someone can **act on in 15 seconds of scanning** — not a wall
of prose they have to read twice. The whole point of this skill is readability: lead with
what matters, format everything into blocks, lists, and tables, and push history down.

There are two modes:
- **New ticket** — build the body, pick a home, create it.
- **Update** — surface the new actionable info at the top, demote the old to a timeline.

---

## Core principles (apply to everything below)

> **Rule of thumb — the glasses test.** Could someone who forgot their glasses still make out
> the *shape* of the document — where the groups are, what's a heading vs. a list vs. a table —
> without squinting? If the blurred page reads as one gray slab, it fails. Every section should
> have a distinct silhouette: a heading, then chunks separated by whitespace, then a clearly
> set-apart list/table/code block. Format for the blurred read first, the close read second.

1. **No walls of text.** Default to bullets, tables, and short bolded leads. If a paragraph
   is more than ~3 lines, it's probably a list. Use visual spacing - paragraphs are our friends,
   we can break text-walls with empty lines between paragraphs, between paragraphs and following
   lists etc. Visual chunking and readability are very important. Even within a paragraph, prefer
   conceptually grouped sentences, separated by new lines, code fences when needed.
   Sub-headings create visual space in dense paragraphs - paragraphs are dense not only visually but
   information wise as well. Both need spacing for readability. 
2. **Lead with the actionable thing.** Title → at-a-glance header → The Ask. A reader should
   know *what kind of work this is, how big, and what to do* before scrolling.
3. **Bold the subject of every bullet.** `**CoreDNS healthy** — ruled out as cause.` beats a
   bare sentence.
4. **Tables for anything with 2+ parallel facts** (options, affected services, repro matrix,
   versions across clusters).
5. **State confidence.** Mark things as `confirmed` / `suspected` / `unverified`. Don't
   present a guess as a fact.
6. **Link, don't paste.** PRs, dashboards, logs, related tickets → links. For URLs use
   `save_issue` body links, not `create_attachment` (that's for file uploads — see gotchas).
   Bare issue identifiers (`INFRA-2879`) auto-link in Linear — no explicit link needed for cross-refs.
7. **Special blocks almost always call for visual spacing** If adding a link to another linear ticket or
   a github issue for example, linear will most likely unfurl or decorate the links/special blocks. This is
   a good opportunity to insert vertical spacing with new lines, or using a sub-heading. 

### Linear editor formatting reference

Linear uses a **ProseMirror** editor, not vanilla CommonMark. The markdown you pass to
`save_issue` is converted to rich text on save. Full docs: <https://linear.app/docs/editor> —
follow the link if you need a directive not listed here.

| Element | Markdown to emit | Notes |
|---------|------------------|-------|
| Headings | `#` … `####` | Only h1–h4; `#####` won't render as a heading |
| Bold / italic / strike | `**b**` / `_i_` / `~~s~~` | |
| Inline code / code block | `` `code` `` / ```` ```lang ```` | |
| Bulleted / numbered list | `-` / `1.` | |
| Task list (checkboxes) | `- [ ]` / `- [x]` | renders as interactive checkboxes |
| Blockquote | `>` + space | |
| **Collapsible / toggle** | `+++ Title` … content … `+++` | **canonical form.** The `>>>`+space editor shortcut also works (Linear rewrites it to `+++`). **`<details>` does NOT** — renders as literal tags |
| Table | `\| a \| b \|` + `\|---\|---\|` | Linear may rewrite the separator to `\| -- \|` — harmless |
| Horizontal divider | `___` + space | |
| Mermaid diagram | ```` ```mermaid ```` | renders as a diagram |
| Issue / user / project mention | bare `INFRA-2879`, `@name` | **bare issue IDs auto-link** to a live mention — no markdown link needed |
| Date | `@Oct 1` | |

**Verified gotchas (round-tripped through the API):**
- **A list hugs the paragraph above it.** Linear renders a paragraph→list transition with a
  *tighter* gap than paragraph→paragraph, and markdown collapses any extra blank lines — so a
  blank line in source is necessary but not sufficient to make the list read as its own group.
  Give every list/table a **bold lead-in line ending in `:`** directly above it
  (`**Make termination unconditional:**`, `**Summary:**`, `**Repro:**`) so the eye sees a
  labeled, set-apart block. This is the fix when a list fails the glasses test.
- **Collapsibles:** emit `+++ Title … +++`, never `<details>`.
- **Don't bold across an inline-code boundary.** `**Why** \`foo\` **fails**` breaks the bold at
  the code span. Bold the lead *without* the code (`**Why foo fails:**`), or keep them separate.

---

## Title convention — `[TYPE] scope — summary`

```
[BUG] acme/storage-service — 416 on Range request for moov-atom videos
[FEAT] acme-cli — add `range` subcommand for partial artifact download
[INVESTIGATION] otel-gateway — 503s under load, one replica pinned
[INFRA] prod-cluster-1 — NAT gateway cost spike, missing S3 VPC endpoint
```

- **TYPE** (uppercase, in brackets) — one of:
  `BUG`, `FEAT`, `INVESTIGATION`, `RESEARCH`, `CHORE`, `INFRA`, `INCIDENT`, `SPIKE`.
- **scope** — the surface area: a service, repo, cluster, or subsystem. Keep it short and
  consistent with how the team already names things.
- **summary** — imperative or noun phrase, specific. Not "fix the bug" — say which bug.

---

## Body template

Fill this in. Drop any section that's genuinely empty rather than writing "N/A everywhere",
but **never** drop the header block or The Ask.

````markdown
```yaml
type:     bug
surface:  acme/storage-service
impact:   Range requests 416 on some videos
priority: high
observed: 2026-06-20 (prod-cluster-1, prod)
involves: [backend, infra]
links:    [PR #10978, INFRA-2891]
```

## The Ask

**One or two sentences: what needs to happen.** Then, if there are concrete steps:

- [ ] First deliverable
- [ ] Second deliverable

## Priors — what we already know

**Summary:** one-line state of current understanding.

| Fact | Status |
|------|--------|
| CoreDNS was healthy during the window | confirmed |
| Root cause is a dropped UDP packet | suspected |

+++ Technical detail
Deeper notes, stack traces, query output — inside a **Linear collapsible** so the ticket stays
scannable. The `+++ Title … +++` fence is the canonical form Linear stores; emit it directly.
+++

## Details

The full description — but still formatted. Repro steps as a numbered list, options as a
table, code/log snippets in fenced blocks. Break it up.

**Repro:**
1. …
2. …

## Follow-ups / sign-off

- **Out of scope here:** …
- **Likely follow-on work:** … (file as separate tickets if real)
- **Open questions:** …
````

### Header block fields

The fenced `yaml` block is **not** rendered as a table by Linear — it's a monospace code
block that reads like frontmatter. Keep keys aligned for scannability. Common keys:

| Key | Notes |
|-----|-------|
| `type` | matches the title TYPE, lowercase |
| `surface` | the scope from the title |
| `impact` | a *few words* on blast radius / why it matters |
| `priority` | urgent / high / medium / low — maps to Linear priority |
| `observed` | for bugs/incidents: when first seen, where (cluster/env) |
| `target` | for feat/chore: desired-by date or milestone, if any |
| `involves` | other teams or systems that need to be in the loop |
| `links` | PRs, related tickets, dashboards (also link them inline in the body) |

Only include keys that carry signal. A small feature might just have `type`, `surface`,
`impact`.

---

## Creating the ticket (Linear MCP)

1. **Build the body** per the template above.
2. **Pick a home — ask unless it's clear from context.** If the conversation already makes
   the team/project obvious (e.g. an infra investigation → Infrastructure / "Infra
   Intake"), state your choice and proceed. Otherwise:
   - `list_teams` and, if needed, `list_projects` for the chosen team.
   - Use **AskUserQuestion** to let the user pick team (and project) — offer the most likely
     option first, labeled `(Recommended)`.
3. **Set fields on `save_issue`:** `title`, `description` (the body), `teamId`, optionally
   `projectId`, `priority`, `labelIds`. Derive `priority` from the header block.
4. **Return the issue URL** and identifier (e.g. `INFRA-2912`) when done.

### Linear MCP gotchas (from hard-won experience)

- **`state` is team-scoped.** Setting a status like "In Progress" can silently migrate the
  issue to a *different team* if that status name resolves elsewhere. Set state via a value
  valid for the target team, or leave it as the team default on create.
- **URLs → `links` on `save_issue`**, not `create_attachment`. `create_attachment` /
  `create_attachment_from_upload` are for **file** uploads. To attach a PR or dashboard URL,
  put it in the body and/or use the issue's links.
- **Don't invent label/project IDs.** List them first; pass real IDs.

---

## Updating an existing ticket — keep a timeline

When new information arrives, the ticket must still answer "what do I do *now*?" at the top.
**Do not** append the new info to the bottom and leave stale conclusions on top.

Procedure:
1. **Fetch** current body (`get_issue`).
2. **Promote the new, actionable info** to the top: update **The Ask** and the header block
   (`impact`, `priority`, `status`) to reflect current reality.
3. **Demote the old content** into a reverse-chronological **Timeline / Investigation log**
   section near the bottom. Each entry is dated and bolded:

   ```markdown
   ## Timeline

   **2026-06-24 — Root cause found**
   Dropped UDP packet confirmed via … . Fix in PR #11042.

   **2026-06-20 — First observed**
   7 jobs hit transient DNS failures on staging-main. CoreDNS healthy.
   ```
4. **Correct, don't accumulate.** If a prior "suspected" line is now disproven, move it to
   the timeline and mark it struck/resolved — don't leave it asserted in Priors.
5. Save with `save_issue` (pass the issue `id`). Note in your reply what you promoted and
   what you moved down.

---

## Quick checklist before creating/updating

- [ ] Title is `[TYPE] scope — summary`, specific.
- [ ] Header block present, only signal-bearing keys.
- [ ] The Ask is at the top and is genuinely actionable.
- [ ] No paragraph longer than ~3 lines without a list/table breaking it up.
- [ ] Confidence marked on claims (confirmed/suspected/unverified).
- [ ] Links instead of pasted blobs; URLs via body/links not file-attachment.
- [ ] Team/project chosen (asked if unclear).
- [ ] (Update) New info on top, old demoted into the Timeline.
