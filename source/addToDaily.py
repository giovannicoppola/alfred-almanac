#!/usr/bin/env python3

## adding to obsidian daily note
# Friday, November 8, 2024


#import requests
import sys
import time

from config import OBSIDIAN_AGENDA, OBSIDIAN_DAILY, VAULT_PATH
from fetchAgenda import fetch_today_agenda

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
    daily_note_path = f"{VAULT_PATH}/{myDailyNote}.md"
    
    # First, append the original content (one-line-a-day, weekly agenda, etc.)
    with open(daily_note_path, "a") as file:
        file.write(f"{myAlmanacString}")
    
    # Check if OBSIDIAN_AGENDA is set to "1" (checked in Alfred)
    if OBSIDIAN_AGENDA == "1":
        log("OBSIDIAN_AGENDA = '1'")
        try:
            # Fetch today's agenda
            agenda_markdown = fetch_today_agenda()
            
            # Append the agenda to the daily note with 2 blank lines before it
            with open(daily_note_path, "a") as file:
                file.write(f"\n\n{agenda_markdown}")
            
            log("Successfully appended today's agenda to daily note")
            
        except Exception as e:
            log(f"Error fetching or appending agenda: {str(e)}")
    else:
        log("OBSIDIAN_AGENDA <> '1', skipping agenda fetch")
        



# Run the main function
if __name__ == "__main__":
    main()
