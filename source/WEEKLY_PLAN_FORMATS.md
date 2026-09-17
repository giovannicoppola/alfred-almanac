# Weekly Plan

When **Add weekly plan** is enabled, the workflow appends a link to this week's
plan *filename* (it does not create this week's file). On **Fridays** the output
also includes next week's link; that file is created if missing, and any
unchecked tasks (`- [ ]` at the start of a line) are copied from this week's
file into it.

This works with **any folder of Markdown (`.md`) files** — Obsidian, Logseq,
VS Code, Typora, plain text, etc. Set the **Notes folder** in the workflow
configuration to wherever your plan files live. The carried-over tasks use the
standard `- [ ]` checkbox syntax, which every Markdown editor understands.

## Link style

The **Weekly Plan Link Style** setting controls how the link is written:

| Style | Output | Renders as a link in |
|-------|--------|----------------------|
| `markdown` (default) | `[name](name.md)` | GitHub, VS Code, Typora, most editors |
| `wikilink` | `![[name]]` | Obsidian, Logseq (embed wikilink) |
| `plain` | `name` | (just the bare filename) |

## Filename formats

The `WEEKLY_PLAN_FORMAT` setting (a dropdown in the workflow configuration)
picks the filename pattern. If not set, it defaults to `format1`.

### format1 (Default)
**Example:** `Weekly plan (31) 2025-07-28 to 2025-08-01`
Original format with week number in parentheses and full ISO dates

### format2
**Example:** `Week 31 - July 28-August 1, 2025`
Readable format with full month names

### format3
**Example:** `W31 2025-07-28 to 2025-08-01`
Compact format with W prefix for week number

### format4
**Example:** `Weekly Plan Week 31 (Jul 28 - Aug 1)`
Professional format with abbreviated month names

### format5
**Example:** `2025 Week 31 (28-01 Jul-Aug)`
Year-first format with day numbers and abbreviated months

### format6
**Example:** `Week 31 - 07-28 to 08-01`
Compact format with MM-DD date format

## How to configure

1. Open Alfred Preferences → Workflows → select the Almanac workflow
2. Click the configuration button (`[x]` / gear icon)
3. Enable **Add weekly plan**, set your **Notes folder**, and pick a
   **Weekly Plan Format** and **Weekly Plan Link Style**
