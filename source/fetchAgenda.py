#!/usr/bin/env python3

"""
Daily agenda for alfred-almanac.

Reads today's calendar events and returns a compact Markdown list, suitable
for appending to the almanac output. The data source is selected with the
CALENDAR_SOURCE setting:

  apple    -> macOS Calendar.app (default; also surfaces iCloud / Google /
              Exchange accounts that are synced into Calendar)
  outlook  -> Microsoft Outlook desktop client

Both read the calendar through AppleScript. Calendar.app scripting can be
slow, so the agenda is opt-in (the "Add today's agenda" checkbox in the
workflow configuration); it is not run unless enabled.
"""

import subprocess
import sys
from datetime import datetime

from config import CALENDAR_SOURCE

# Each event is packed as "sortkey|||title|||start|||end|||location",
# events are joined by EVENT_SEP. sortkey is seconds-since-midnight so the
# events can be sorted chronologically regardless of locale time format.
FIELD_SEP = "|||"
EVENT_SEP = "[][][]"


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def _apple_script_for_today():
    """AppleScript that reads today's events from Calendar.app."""
    return '''
    set startDate to (current date)
    set hours of startDate to 0
    set minutes of startDate to 0
    set seconds of startDate to 0
    set endDate to startDate + (1 * days)
    set output to ""
    tell application "Calendar"
        repeat with cal in calendars
            set theEvents to (every event of cal whose start date ≥ startDate and start date < endDate)
            repeat with ev in theEvents
                set evTitle to summary of ev
                set evStart to start date of ev
                set evEnd to end date of ev
                set evLoc to ""
                try
                    set evLoc to location of ev
                end try
                set output to output & (time of evStart as text) & "|||" & evTitle & "|||" & (time string of evStart) & "|||" & (time string of evEnd) & "|||" & evLoc & "[][][]"
            end repeat
        end repeat
    end tell
    return output
    '''


def _outlook_script_for_today(date_string):
    """AppleScript that reads today's events from Microsoft Outlook.
    Meetings with "Tentative" in the subject are skipped."""
    return f'''
    tell application "Microsoft Outlook"
        set targetDate to date "{date_string}"
        set startOfDay to targetDate
        set endOfDay to targetDate + (24 * 60 * 60) - 1
        set output to ""
        set todayEvents to (get every calendar event whose start time ≥ startOfDay and start time ≤ endOfDay)
        repeat with CalEv in todayEvents
            try
                tell CalEv
                    set mySubject to (subject as text)
                    set shouldSkip to false
                    try
                        if mySubject contains "Tentative" then set shouldSkip to true
                    end try
                    if not shouldSkip then
                        set eventStart to start time
                        set eventEnd to end time
                        set evLoc to ""
                        try
                            set evLoc to location as text
                        end try
                        set output to output & (time of eventStart as text) & "|||" & mySubject & "|||" & (time string of eventStart) & "|||" & (time string of eventEnd) & "|||" & evLoc & "[][][]"
                    end if
                end tell
            end try
        end repeat
        return output
    end tell
    '''


def _run_osascript(script):
    """Run an AppleScript and return stdout, or None on error."""
    process = subprocess.Popen(['osascript', '-e', script],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        log(f"Agenda AppleScript error: {stderr.strip()}")
        return None
    return stdout


def _parse_events(raw):
    """Parse packed AppleScript output into a chronological list of events."""
    events = []
    if not raw or not raw.strip():
        return events
    for chunk in raw.strip().split(EVENT_SEP):
        if not chunk.strip():
            continue
        parts = chunk.split(FIELD_SEP)
        if len(parts) < 5:
            continue
        try:
            sort_key = int(parts[0].strip())
        except ValueError:
            sort_key = 0
        events.append({
            'sort': sort_key,
            'title': parts[1].strip(),
            'start': parts[2].strip(),
            'end': parts[3].strip(),
            'location': parts[4].strip(),
        })
    events.sort(key=lambda e: e['sort'])
    return events


def _format_agenda(raw, weekday_name):
    """Render parsed events as a compact Markdown agenda."""
    events = _parse_events(raw)
    if not events:
        return f"\U0001F4C5 No meetings today – enjoy your {weekday_name}! ☕️"
    lines = [f"\U0001F4C5 {weekday_name}'s agenda"]
    for e in events:
        line = f"• {e['start']}–{e['end']} – {e['title']}"
        if e['location']:
            line += f" @ {e['location']}"
        lines.append(line)
    return "\n".join(lines)


def fetch_today_agenda():
    """Return today's agenda as a compact Markdown string."""
    today = datetime.now()
    weekday_name = today.strftime("%A")
    source = CALENDAR_SOURCE.lower()
    try:
        if source == 'outlook':
            date_string = today.strftime("%A, %B %-d, %Y") + " 12:00:00 AM"
            raw = _run_osascript(_outlook_script_for_today(date_string))
        else:
            raw = _run_osascript(_apple_script_for_today())
        if raw is None:
            return "\U0001F4C5 Could not read your calendar (check Automation permissions)."
        return _format_agenda(raw, weekday_name)
    except Exception as e:
        log(f"Error in fetch_today_agenda: {e}")
        return f"\U0001F4C5 Error fetching agenda: {e}"


if __name__ == "__main__":
    print(fetch_today_agenda())
