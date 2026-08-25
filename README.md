# alfred-almanac

### Start your day with weather from [wttr.in](http://wttr.in/) and a daily almanac

![](images/alfred-almanac.gif)

<a href="https://github.com/giovannicoppola/alfred-almanac/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-almanac/total?color=purple&label=Downloads"><br/>
</a>
<a href="https://alfred.app/workflows/giovannicoppola/almanac/">
<img alt="Gallery Downloads"
src="https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Fgiovannicoppola%2Falfred-gallery-downloads%2Fmain%2Fdownloads.json&query=%24.almanac%5B0%5D.display&label=Gallery%20Downloads&color=blue&logo=alfred"><br/>
</a>

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Setting up](#setting-up)
- [Basic Usage](#basic-usage)
- [Known Issues](#known-issues)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)
- [Feedback](#feedback)

<!-- /MarkdownTOC -->

<h1 id="setting-up">Setting up</h1>

### Needed

- Alfred with Powerpack license
- Python3 (howto install [here](https://www.freecodecamp.org/news/python-version-on-mac-update/))

### Setup

1. Download the most recent release of `alfred-almanac` from Github and double-click to install
2. _Optional:_ Click `Configure Workflow` in `alfred-almanac` preferences to change settings
3. _Optional:_ Setup a hotkey to launch alfred-almanac

<h1 id="basic-usage">Basic Usage</h1>
![](images/complice-almanac.png)

- Launch `alfred-almanac` to retrieve weather and other almanac information from default locations ...
- ... or enter a location/ZIP code directly

- The default weather string from `wttr.in` will output:

  - `%C` weather condition text
  - `%c` weather condition
  - 🌡️`%t` actual temperature
  - `%f` 'feels like' temperature
  - `%h` humidity
  - 🌬️`%w` wind
  - `%m` moon phase

- The almanac section will output:

  - local date and time
  - current week of the year
  - current quarter
  - days from and to the end of the year
  - days from and to the special day

- Enter (↩️) will copy to the clipboard and past to the frontmost application
- Shift-enter (⇧↩️) will open the corresponding page on `wttr.in`
- CTRL-enter (⌃↩️) will show the almanac string in large font
- Option (⌥) will show the local date/time and timezone

## Outlook Calendar Integration

The almanac can fetch today's meeting agenda from Microsoft Outlook and append it to your Obsidian daily note.

### Setup

This feature requires a Microsoft Entra (Azure AD) app registration for Graph API access:

1. Create an app registration at [https://portal.azure.com](https://portal.azure.com) (or use an existing one)
2. Create a `config.json` file in the `source/` directory:
   ```json
   {
     "client_id": "YOUR_CLIENT_ID",
     "tenant_id": "YOUR_TENANT_ID",
     "client_secret": "YOUR_CLIENT_SECRET",
     "scopes": ["Calendars.Read", "Mail.Read"]
   }
   ```
3. Set the `OBSIDIAN_AGENDA` workflow variable to `1`
4. On first run, a browser window will open for Microsoft login. Subsequent runs use cached tokens (`token_cache.json`, auto-generated).

Alternatively, set the `GRAPH_CONFIG_DIR` workflow environment variable to point to a directory containing `config.json` and `token_cache.json` (e.g., to share credentials with other workflows).

### One-on-One Meeting Integration

For one-on-one meetings (exactly 2 attendees), the almanac can automatically fetch "to discuss" items from person notes and include them in the daily agenda.

#### Quick Setup (3 Steps)

**1. Configure Workflow Variables** (Alfred Preferences → Workflows → alfred-almanac → Configure Workflow):

Required:
- **`PEOPLE_FOLDER`**: Full path to your Obsidian people folder
  - Example: `/Users/yourname/Documents/Vault/_People`
  - Click the folder icon to browse and select

Optional (sensible defaults provided):
- **`DISCUSS_SECTION`**: Section header in person notes (default: `# Active Items`)
- **`ONE_ON_ONE_TAG`**: Frontmatter tag to identify notes (default: `one-on-one`)

**2. Tag Person Notes**

Add the tag to person notes for people you have regular one-on-ones with:
```yaml
---
tags: [one-on-one]
---
```

**3. Create Discussion Sections**

Maintain a section in those person notes with items to discuss:
```markdown
# Active Items
- [ ] Discuss project timeline
- [ ] Review Q4 goals
- [ ] Follow up on last week's action items
```

#### How It Works

When the almanac detects a one-on-one meeting (exactly 2 attendees), it will:
1. Match the attendee name to a file in your `PEOPLE_FOLDER` (case-insensitive, partial matching)
2. Check if that note has the `ONE_ON_ONE_TAG` in frontmatter
3. Extract all content from the `DISCUSS_SECTION` header
4. Insert the items in your daily note under the meeting header as: `**To Discuss with [[PersonName]]:**`

#### Name Matching

The workflow matches calendar attendee names to person note filenames flexibly:
- **Exact match**: "Julie Horowitz" → `Julie Horowitz.md`
- **Partial match**: "Julie Horowitz" → `Julie H.md` or `J. Horowitz.md`
- **Case-insensitive**: Works with any capitalization

Tip: Use the full name in your person note filename that matches how it appears in your calendar.

#### Example Output

In your daily note:
```markdown
# Weekly sync with Product Team
**Time:** 10:00:00 AM - 10:30:00 AM
**Attendees:** Julie Horowitz, Giovanni Coppola
**To Discuss with [[Julie Horowitz]]:**
- [ ] Discuss project timeline
- [ ] Review Q4 goals
- [ ] Follow up on last week's action items

**Agenda:** Product roadmap review...
```

### How it works

- Tries the **Graph API** first (works with new Outlook)
- Falls back to **AppleScript** if Graph API is unavailable (legacy Outlook)
- Returns all accepted events for today, including recurring and overlapping ones
- Skips cancelled and declined events
- Cleans up meeting body text:
  - Converts Office file icon links to proper markdown links
  - Removes Microsoft Teams join/dial-in boilerplate
  - Removes inline image references (`[cid:...]`)

### Dependencies

Graph API packages are bundled in `source/lib/`:
- `msal`, `requests`, `jwt` (PyJWT), `cryptography`, `cffi`, `pycparser`, `certifi`, `urllib3`, `idna`, `charset_normalizer`

Install/update with:
```bash
pip install --target=source/lib msal requests
```

<h1 id="known-issues">Known issues</h1>
- Not tested extensively for international locations

<h1 id="acknowledgments">Acknowledgments </h1>
- [Igor Chubin](https://twitter.com/igor_chubin) for developing the amazing `wttr.in`
- [@vitorgalvao](https://github.com/vitorgalvao) for suggestions and great additions
- The [Alfred forum](https://www.alfredforum.com) community.

<h1 id="changelog">Changelog </h1>

- version 1.8: One-on-one meeting integration - automatically fetch "to discuss" items from person notes and include them in daily agenda. Detects one-on-one meetings (2 attendees), matches attendee names to person notes, extracts discussion items from configurable sections. Supports flexible name matching and frontmatter tag filtering.
- version 1.7: Outlook calendar agenda via Graph API (new Outlook support), with AppleScript fallback. Meeting body cleanup (markdown links, Teams boilerplate removal).
- version 1.6: integration with Obsidian Daily Notes, and Weekly plan files, integration with line-a-day workflow, added OpenWeather API support.
- 11-30-2022: version 1.5 removed OneUpdater (for Alfred Gallery)
- 11-01-2022: version 1.4 added timezones
- 09-29-2022: version 1.3 added OneUpdater, quicklookurl preview, keyword configurable (thanks @vitorgalvao!)
- 08-07-2022: version 1.2 merging @vitorgalvao's changes to update Workflow Environment Variables to User Configuration
- 03-30-2022: version 1.1 (switched to `requests` package for web request handling)
- 03-22-2022: version 1.0

<h1 id="feedback">Feedback</h1>
Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum.

