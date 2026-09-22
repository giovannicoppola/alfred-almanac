# Alfred Almanac - Configuration Guide

Quick reference for configuring the alfred-almanac workflow.

## Workflow Variables

Access via: **Alfred Preferences → Workflows → alfred-almanac → Configure Workflow** (click the [x] icon in top right)

### Basic Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOCATION` | Text | _(empty)_ | Default weather location (city name or ZIP code) |
| `FORMATSTRING` | Text | `%C %c 🌡️%t (feels %f, %h) 🌬️%w %m` | Weather string format for **wttr.in only** ([wttr.in format codes](https://github.com/chubin/wttr.in#one-line-output)) |
| `SPECIAL_DAY` | Text | `03-14` | A special date to count days from and to (`MM-DD`) |
| `WEATHER_SOURCE` | Dropdown | `wttr` | Weather data source: `wttr` (wttr.in) or `openweather` (OpenWeather API) |
| `OPENWEATHER_KEY` | Text | _(empty)_ | API key for OpenWeather (required if using `openweather` source) |
| `TEMPERATURE_UNIT` | Dropdown | `fahrenheit` | Temperature unit: `fahrenheit` or `celsius` |

### Obsidian Integration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OBSIDIAN_VAULT` | Folder | _(empty)_ | Full path to your Obsidian vault |
| `OBSIDIAN_CHECK` | Checkbox | unchecked | Enable Obsidian daily note integration (Enter writes to the daily note instead of copying) |
| `DAILY_FORMAT` | Text | `%Y-%m-%d-%a` | Daily note filename format (Python strftime). Path is `{OBSIDIAN_VAULT}/{format}.md` |
| `OBSIDIAN_CREATE` | Checkbox | **checked** (this branch) | Create today's daily note if it is missing. Uncheck to skip instead |
| `OBSIDIAN_AGENDA` | Checkbox | unchecked | Fetch and append calendar agenda to the daily note (separate from `AGENDA` in the Alfred result) |
| `AGENDA` | Checkbox | unchecked | Append today's calendar events to the Alfred/almanac output |
| `CALENDAR_SOURCE` | Dropdown | `apple` | `apple` (Calendar.app) or `outlook` |
| `JOURNAL` | Checkbox | unchecked | Journal on-this-day links (scans `NOTES_FOLDER` for `journal`-tagged notes) |
| `LINEADAY` | Checkbox | unchecked | Enable line-a-day integration |
| `LINEADAYFILE` | File | _(empty)_ | Path to line-a-day file |
| `WEEKLY` | Checkbox | unchecked | Enable weekly plan integration |
| `WEEKLY_PLAN_FORMAT` | Dropdown | `format1` | Weekly plan filename format |
| `LINK_STYLE` | Dropdown | `markdown` | Weekly plan link style (`markdown` / `wikilink` / `plain`) |

### Calendar & One-on-One Integration

| Variable | Type | Default | Required | Description |
|----------|------|---------|----------|-------------|
| `PEOPLE_FOLDER` | Folder | _(empty)_ | **Yes** | Full path to folder containing person notes (e.g., `/path/to/vault/_People`) |
| `DISCUSS_SECTION` | Text | `# Active Items` | No | Section header in person notes containing discussion items |
| `ONE_ON_ONE_TAG` | Text | `one-on-one` | No | Frontmatter tag to identify person notes with regular one-on-ones |
| `GRAPH_CONFIG_DIR` | Env var | _(unset)_ | No | Directory holding Graph API `config.json` / `token_cache.json`. Not a Configure Workflow field. If unset, this branch currently uses a developer-specific fallback in `fetchAgenda.py` |

### Email Integration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EMAILSTROM_SCRIPT` | File | _(empty)_ | Path to emailstrom script for email summary in daily note |

---

## One-on-One Setup Checklist

### ✅ Step 1: Workflow Configuration
- [ ] Set `PEOPLE_FOLDER` to your people notes folder path
- [ ] (Optional) Customize `DISCUSS_SECTION` if you use a different header
- [ ] (Optional) Customize `ONE_ON_ONE_TAG` if you prefer a different tag

### ✅ Step 2: Person Notes Structure
Each person note should follow this structure:
```markdown
---
tags: [one-on-one]
---

# Projects
(Any projects you're working on together)

# Active Items
- [ ] Item to discuss in next meeting
- [ ] Another discussion topic
- [ ] Action item from last meeting

# Timeline
(Meeting history)
```

### ✅ Step 3: Tag Your People
Add `tags: [one-on-one]` to frontmatter for people you meet regularly.

**Supported tag formats:**
```yaml
# Array format (recommended)
tags: [one-on-one]
tags: [meetings, one-on-one, work]

# List format
tags:
  - one-on-one
  - meetings

# Inline format
tags: one-on-one, meetings
```

---

## Testing Your Setup

1. **Test path configuration:**
   - Make sure `PEOPLE_FOLDER` path is correct
   - Check that person note filenames match calendar attendee names

2. **Test tag detection:**
   - Verify frontmatter tags are properly formatted with `---` delimiters
   - Ensure the tag matches your `ONE_ON_ONE_TAG` setting (default: `one-on-one`)

3. **Test section extraction:**
   - Verify your section header exactly matches `DISCUSS_SECTION` (including `#` and spacing)
   - Default is `# Active Items` (one `#`, one space)

4. **Test name matching:**
   - Calendar shows "John Smith" → Create `John Smith.md` (exact match best)
   - Partial matches work: "John Smith" will match `J. Smith.md` or `John S.md`
   - Matching is case-insensitive

---

## Troubleshooting

### One-on-one items not appearing?

**Check these in order:**

1. **Path Issues:**
   - Verify `PEOPLE_FOLDER` path is absolute (starts with `/`)
   - Check folder exists: `ls -la "/your/path/to/_People"`

2. **Tag Issues:**
   - Open person note and verify frontmatter has opening/closing `---`
   - Tag is inside frontmatter block
   - Tag name matches `ONE_ON_ONE_TAG` exactly (default: `one-on-one`)

3. **Section Issues:**
   - Section header must match exactly: `# Active Items` by default
   - Check for exact spacing (one space after `#`)
   - Section must contain content (empty sections are skipped)

4. **Name Matching Issues:**
   - Check how attendee name appears in calendar
   - Try creating a note with the exact calendar name
   - Use Alfred's debugger to see matching attempts

5. **Meeting Detection:**
   - Feature matches Outlook events with **one or two** attendees
   - The attendee is matched to a tagged person note; the event is then headed `# Meeting with [[Person]]`

### Checking Alfred Debugger

1. Open Alfred Preferences → Workflows → alfred-almanac
2. Click the bug icon (🐛) in top right
3. Run the workflow and watch for error messages
4. Look for lines starting with `[ERROR]` or `[STDERR]`

---

## Default Behavior (No Configuration)

If you don't configure the one-on-one settings:
- **No error occurs** - the feature is simply disabled
- Calendar events still appear in daily agenda
- "To discuss" items are not fetched
- Set `PEOPLE_FOLDER` to enable the feature

---

## Version Requirements

- **Alfred 5** with Powerpack
- **Python 3** (bundled with macOS)
- **Obsidian** (for daily note integration)
- **Microsoft Outlook** (for calendar integration)
  - New Outlook: Uses Graph API
  - Legacy Outlook: Uses AppleScript
