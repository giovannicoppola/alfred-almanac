#!/usr/bin/env python3
# encoding: utf-8
#
#
# Wednesday, July 21, 2021, 4:42 PM
#


from __future__ import unicode_literals
import os


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

	
