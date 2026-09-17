#!/usr/bin/env python3
# encoding: utf-8
#
#
# Wednesday, July 21, 2021, 4:42 PM
#


from __future__ import unicode_literals

import os
import sys

LOCATION = os.path.expanduser(os.getenv('LOCATION', ''))
FORMATSTRING = os.path.expanduser(os.getenv('FORMATSTRING', ''))
SPECIAL_DAY = os.path.expanduser(os.getenv('SPECIAL_DAY', ''))
WEATHER_SOURCE = os.path.expanduser(os.getenv('WEATHER_SOURCE', 'wttr'))
OPENWEATHER_KEY = os.path.expanduser(os.getenv('OPENWEATHER_KEY', ''))
TEMPERATURE_UNIT = os.path.expanduser(os.getenv('TEMPERATURE_UNIT', 'fahrenheit'))
WEEKLY = os.path.expanduser(os.getenv('WEEKLY', ''))
NOTES_FOLDER = os.path.expanduser(os.getenv('NOTES_FOLDER', ''))
WEEKLY_PLAN_FORMAT = os.path.expanduser(os.getenv('WEEKLY_PLAN_FORMAT', 'format1'))
LINK_STYLE = os.path.expanduser(os.getenv('LINK_STYLE', 'markdown'))
AGENDA = os.path.expanduser(os.getenv('AGENDA', ''))
CALENDAR_SOURCE = os.path.expanduser(os.getenv('CALENDAR_SOURCE', 'apple'))
LINEADAY = os.path.expanduser(os.getenv('LINEADAY', ''))
LINEADAY_FILE = os.path.expanduser(os.getenv('LINEADAYFILE', ''))
JOURNAL = os.path.expanduser(os.getenv('JOURNAL', ''))

VAULT_PATH = os.path.expanduser(os.getenv('OBSIDIAN_VAULT', ''))
OBSIDIAN_CHECK = os.path.expanduser(os.getenv('OBSIDIAN_CHECK', ''))
OBSIDIAN_DAILY = os.path.expanduser(os.getenv('DAILY_FORMAT', '%Y-%m-%d-%a'))
OBSIDIAN_CREATE = os.path.expanduser(os.getenv('OBSIDIAN_CREATE', '1'))
OBSIDIAN_AGENDA = os.path.expanduser(os.getenv('OBSIDIAN_AGENDA', ''))
EMAILSTROM_SCRIPT = os.path.expanduser(os.getenv('EMAILSTROM_SCRIPT', ''))
PEOPLE_FOLDER = os.path.expanduser(os.getenv('PEOPLE_FOLDER', ''))
DISCUSS_SECTION = os.path.expanduser(os.getenv('DISCUSS_SECTION', '# Active Items'))
ONE_ON_ONE_TAG = os.path.expanduser(os.getenv('ONE_ON_ONE_TAG', 'one-on-one'))

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)
