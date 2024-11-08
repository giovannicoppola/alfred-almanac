#!/usr/bin/env python3

## adding to obsidian daily note
# Friday, November 8, 2024


#import requests
import json
import sys
import requests
from datetime import datetime, timedelta
import datetime as date2
import re, os, time


from config import VAULT_PATH, OBSIDIAN_DAILY

myAlmanacString = sys.argv[1]


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)



def fetchDailyNoteName():
    # Get today's date

    current_time = time.localtime()

    # Format today's date according to OBSIDIAN_DAILY
    myDailyNote = time.strftime(OBSIDIAN_DAILY, current_time)
    
    return myDailyNote

def main():
    myDailyNote = fetchDailyNoteName()
    with open(f"{VAULT_PATH}/{myDailyNote}.md", "a") as file:
        file.write(f"{myAlmanacString}")
        



# Run the main function
if __name__ == "__main__":
    main()