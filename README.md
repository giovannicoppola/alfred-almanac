# alfred-almanac

### Start your day with weather and a daily almanac — plus optional weekly planning, a calendar agenda, and a journal lookback

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
- [Optional features](#optional-features)
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
	- `%f`  'feels like' temperature
	- `%h` humidity
	- 🌬️`%w` wind
	- `%m` moon phase
- Temperature can be shown in °F or °C (set **Temperature unit** in the configuration)
- The weather source can be switched from `wttr.in` to [OpenWeather](https://openweathermap.org) (set **Weather Info Source** and provide your own API key)

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

<h1 id="optional-features">Optional features</h1>

All of these are **off by default** and can be enabled in `Configure Workflow`. They append extra lines to the almanac output (which you can copy with ↩️ or view in large text with ⌃↩️).

### Weather source & units
- **Weather Info Source:** `wttr.in` (default, no setup) or **OpenWeather**. For OpenWeather, get a free API key at [openweathermap.org](https://openweathermap.org/api) and paste it into **Open Weather API Key**.
- **Temperature unit:** `°F` (default) or `°C`. Applies to both sources.

### Weekly plan + task carryover
Enable **Add weekly plan** to append a link to the current week's plan file. On **Fridays** it also creates next week's plan file and carries over any unchecked tasks (`- [ ]` lines) from this week.

- **Notes folder:** any folder of Markdown (`.md`) files where the plans live — works with Obsidian, Logseq, VS Code, plain text, etc.
- **Weekly Plan Format:** pick the filename pattern (e.g. `Weekly plan (31) 2025-07-28 to 2025-08-01`).
- **Weekly Plan Link Style:** how the link is written — standard Markdown `[name](name.md)` (default), Obsidian/Logseq wikilink `![[name]]`, or plain filename.

See [`source/WEEKLY_PLAN_FORMATS.md`](source/WEEKLY_PLAN_FORMATS.md) for the full list of formats.

### Daily agenda
Enable **Add today's agenda** to append today's calendar events (time, title, location), sorted chronologically.

- **Calendar source:** **Apple Calendar** (default — also covers iCloud/Google/Exchange accounts synced into Calendar) or **Microsoft Outlook**.
- On first use, macOS will ask for permission to control the chosen app. Reading Apple Calendar can be slow, which is why this feature is opt-in.

#### Outlook: Graph API + one-on-one meeting integration

When **Calendar source** is **Microsoft Outlook**, the agenda tries the **Graph API** first (works with new Outlook), and falls back to **AppleScript** (legacy Outlook) if it's unavailable. It returns all accepted events for today (including recurring/overlapping ones), skips cancelled/declined events, and cleans up meeting body text (Office file-icon links, Teams join boilerplate, inline image references).

For one-on-one meetings (exactly 2 attendees), it can also pull "to discuss" items from person notes and include them in the agenda:

1. Create a Microsoft Entra (Azure AD) app registration for Graph API access at [portal.azure.com](https://portal.azure.com), then create a `config.json` in `source/`:
   ```json
   {
     "client_id": "YOUR_CLIENT_ID",
     "tenant_id": "YOUR_TENANT_ID",
     "client_secret": "YOUR_CLIENT_SECRET",
     "scopes": ["Calendars.Read", "Mail.Read"]
   }
   ```
   On first run, a browser window opens for Microsoft login; subsequent runs use a cached token (`token_cache.json`, auto-generated next to `config.json`). Alternatively, set **`GRAPH_CONFIG_DIR`** to a directory holding both files, to share credentials across workflows.
2. Set **`PEOPLE_FOLDER`** to your Obsidian people-notes folder (e.g. `_People`) — this is the only setting required to enable one-on-one matching.
3. Tag the person notes you have regular one-on-ones with (`tags: [one-on-one]` in frontmatter — matches **`ONE_ON_ONE_TAG`**), and keep a section of items in each (default header `# Active Items` — matches **`DISCUSS_SECTION`**).

When a one-on-one is detected, the attendee name is matched (case-insensitive, partial match) to a file in `PEOPLE_FOLDER`; if that note carries the tag, its discussion items are inserted under the meeting as `**To Discuss with [[PersonName]]:**`.

Graph API packages (`msal`, `requests`, `jwt`, `cryptography`, `cffi`, `pycparser`, `certifi`, `urllib3`, `idna`, `charset_normalizer`) are bundled in `source/lib/`; update with `pip install --target=source/lib msal requests`.

See [`CONFIGURATION.md`](CONFIGURATION.md) for the full variable reference.

### Line-a-day lookback
Enable **Quote previous line-a-day items?** to append, for each past year, the journal entry closest to *this day* in that year (a "on this day" lookback). Point **line-a-day file** at a Markdown file whose entries look like `- **YYYY-MM-DD** ...`. Pairs nicely with the companion [alfred-line-a-day](https://github.com/giovannicoppola/alfred-line-a-day) workflow.


<h1 id="known-issues">Known issues</h1>
- Not tested extensively for international locations

<h1 id="acknowledgments">Acknowledgments </h1>
- [Igor Chubin](https://twitter.com/igor_chubin) for developing the amazing `wttr.in`
- [@vitorgalvao](https://github.com/vitorgalvao) for suggestions and great additions
- The [Alfred forum](https://www.alfredforum.com) community.

<h1 id="changelog">Changelog </h1>

- 2026-07-21: version 1.6.1, added an optional journal 'on this day' feature (index built on launch, cached in the workflow data folder)
- 06-30-2026: version 1.6 added optional features: OpenWeather source + °F/°C unit, weekly plan with Friday task carryover, daily agenda (Apple Calendar / Outlook — with Graph API and one-on-one meeting integration for Outlook), Obsidian Daily Notes integration, and line-a-day lookback
- 11-30-2022: version 1.5 removed OneUpdater (for Alfred Gallery)
- 11-01-2022: version 1.4 added timezones
- 09-29-2022: version 1.3 added OneUpdater, quicklookurl preview, keyword configurable (thanks @vitorgalvao!)
- 08-07-2022: version 1.2 merging @vitorgalvao's changes to update Workflow Environment Variables to User Configuration
- 03-30-2022: version 1.1 (switched to `requests` package for web request handling)
- 03-22-2022: version 1.0

<h1 id="feedback">Feedback</h1>
Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum.

