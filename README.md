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

<h1 id="known-issues">Known issues</h1>
- Not tested extensively for international locations

<h1 id="acknowledgments">Acknowledgments </h1>
- [Igor Chubin](https://twitter.com/igor_chubin) for developing the amazing `wttr.in`
- [@vitorgalvao](https://github.com/vitorgalvao) for suggestions and great additions
- The [Alfred forum](https://www.alfredforum.com) community.

<h1 id="changelog">Changelog </h1>

- version 1.6: integration with Obsidian Daily Notes, and Weekly plan files, integration with line-a-day workflow, added OpenWeather API support.
- 11-30-2022: version 1.5 removed OneUpdater (for Alfred Gallery)
- 11-01-2022: version 1.4 added timezones
- 09-29-2022: version 1.3 added OneUpdater, quicklookurl preview, keyword configurable (thanks @vitorgalvao!)
- 08-07-2022: version 1.2 merging @vitorgalvao's changes to update Workflow Environment Variables to User Configuration
- 03-30-2022: version 1.1 (switched to `requests` package for web request handling)
- 03-22-2022: version 1.0

<h1 id="feedback">Feedback</h1>
Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum.

# To add:
- support for OpenWeather API key (wttr.in is blocked in some corporate networks)
- support for Obsidian Daily Notes and Weekly Plan files
- support for line-a-day workflow
- support for Outlook calendar events
