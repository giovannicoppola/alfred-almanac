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
WEEKLY = os.path.expanduser(os.getenv('WEEKLY', ''))

	
LINEADAY_FILE = os.path.expanduser(os.getenv('LINEADAYFILE', ''))
LINEADAY = os.path.expanduser(os.getenv('LINEADAY', ''))
VAULT_PATH = os.path.expanduser(os.getenv('OBSIDIAN_VAULT', ''))
OBSIDIAN_CHECK = os.path.expanduser(os.getenv('OBSIDIAN_CHECK', ''))
OBSIDIAN_DAILY = os.path.expanduser(os.getenv('DAILY_FORMAT', ''))
OBSIDIAN_AGENDA = os.path.expanduser(os.getenv('OBSIDIAN_AGENDA', ''))
WEATHER_SOURCE = os.path.expanduser(os.getenv('WEATHER_SOURCE', 'wttr'))
OPENWEATHER_KEY = os.path.expanduser(os.getenv('OPENWEATHER_KEY', ''))
TEMPERATURE_UNIT = os.path.expanduser(os.getenv('TEMPERATURE_UNIT', 'fahrenheit'))
WEEKLY_PLAN_FORMAT = os.path.expanduser(os.getenv('WEEKLY_PLAN_FORMAT', 'format1'))

def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)
