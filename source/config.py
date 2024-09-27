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
WEEKLY = os.path.expanduser(os.getenv('WEEKLY', ''))

	
LINEADAY_FILE = os.path.expanduser(os.getenv('LINEADAYFILE', ''))
LINEADAY = os.path.expanduser(os.getenv('LINEADAY', ''))