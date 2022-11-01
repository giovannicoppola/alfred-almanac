# alfred-almanac

### Start your day with weather from [wttr.in](http://wttr.in/) and a daily almanac


![](images/alfred-almanac.gif)

<a href="https://github.com/giovannicoppola/alfred-almanac/releases/latest/">
<img alt="Downloads"
src="https://img.shields.io/github/downloads/giovannicoppola/alfred-almanac/total?color=purple&label=Downloads"><br/>
</a>

<!-- MarkdownTOC autolink="true" bracket="round" depth="3" autoanchor="true" -->

- [Setting up](#setting-up)
- [Basic Usage](#usage)
- [Known Issues](#known-issues)
- [Acknowledgments](#acknowledgments)
- [Changelog](#changelog)
- [Feedback](#feedback)

<!-- /MarkdownTOC -->


<a name="setting-up"></a>
# Setting up

### Needed

- Alfred with Powerpack license
- Python3 (howto install [here](https://www.freecodecamp.org/news/python-version-on-mac-update/))

### Setup

1. Download the most recent release of `alfred-almanac` from Github and double-click to install
2. _Optional:_ Click `Configure Workflow` in `alfred-almanac` preferences to change settings
3. _Optional:_ Setup a hotkey to launch alfred-almanac

<a name="usage"></a>
# Basic Usage
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


<a name="known-issues"></a>
# Known issues
- Not tested extensively for international locations

<a name="acknowledgments"></a>
# Acknowledgments
- [Igor Chubin](https://twitter.com/igor_chubin) for developing the amazing `wttr.in`
- [@vitorgalvao](https://github.com/vitorgalvao) for suggestions and great additions
- The [Alfred forum](https://www.alfredforum.com) community.

<a name="changelog"></a>
# Changelog

- 09-29-2022: version 1.3 added OneUpdater, quicklookurl preview, keyword configurable (thanks @vitorgalvao!)
- 08-07-2022: version 1.2 merging @vitorgalvao's changes to update Workflow Environment Variables to User Configuration
- 03-30-2022: version 1.1 (switched to `requests` package for web request handling)
- 03-22-2022: version 1.0

<a name="feedback"></a>
# Feedback

Feedback welcome! If you notice a bug, or have ideas for new features, please feel free to get in touch either here, or on the [Alfred](https://www.alfredforum.com) forum.

