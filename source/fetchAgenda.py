#!/usr/bin/env python3

"""
Daily agenda for alfred-almanac.

Reads today's calendar events and returns a compact Markdown list, suitable
for appending to the almanac output (or an Obsidian daily note). The data
source is selected with the CALENDAR_SOURCE setting:

  apple    -> macOS Calendar.app (default; also surfaces iCloud / Google /
              Exchange accounts that are synced into Calendar), read via
              AppleScript.
  outlook  -> Microsoft Outlook. Tries the Graph API first (new Outlook),
              falling back to AppleScript (legacy Outlook) if Graph API
              credentials aren't configured or the request fails. For
              one-on-one meetings (exactly 1-2 attendees), also pulls
              "to discuss" items from a matching person note (see
              PEOPLE_FOLDER / ONE_ON_ONE_TAG / DISCUSS_SECTION).

Calendar.app scripting can be slow, so the agenda is opt-in (the "Add
today's agenda" checkbox in the workflow configuration); it is not run
unless enabled.
"""

import calendar
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import config

# Each Apple Calendar event is packed as "sortkey|||title|||start|||end|||location",
# events are joined by EVENT_SEP. sortkey is seconds-since-midnight so the
# events can be sorted chronologically regardless of locale time format.
FIELD_SEP = "|||"
EVENT_SEP = "[][][]"


# ---------------------------------------------------------------------------
# Apple Calendar (AppleScript)
# ---------------------------------------------------------------------------

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


def _run_osascript(script):
    """Run an AppleScript and return stdout, or None on error."""
    process = subprocess.Popen(['osascript', '-e', script],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        config.log(f"Agenda AppleScript error: {stderr.strip()}")
        return None
    return stdout


def _parse_apple_events(raw):
    """Parse packed Calendar.app AppleScript output into a chronological list of events."""
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


def _format_apple_agenda(raw, weekday_name):
    """Render parsed Calendar.app events as a compact Markdown agenda."""
    events = _parse_apple_events(raw)
    if not events:
        return f"\U0001F4C5 No meetings today – enjoy your {weekday_name}! ☕️"
    lines = [f"\U0001F4C5 {weekday_name}'s agenda"]
    for e in events:
        line = f"• {e['start']}–{e['end']} – {e['title']}"
        if e['location']:
            line += f" @ {e['location']}"
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Outlook (Graph API + AppleScript fallback), with one-on-one "to discuss"
# ---------------------------------------------------------------------------

def _outlook_script_for_today(date_string):
    """AppleScript that reads today's events from Microsoft Outlook (legacy).
    Meetings with "Tentative" in the subject are skipped."""
    return f'''
    tell application "Microsoft Outlook"
        try
            set targetDate to date "{date_string}"
            set startOfDay to targetDate
            set endOfDay to targetDate + (24 * 60 * 60) - 1

            set finalList to ""

            set todayEvents to (get every calendar event whose start time ≥ startOfDay and start time ≤ endOfDay)

            repeat with CalEv in todayEvents
                try
                    tell CalEv
                        set mySubject to (subject as text)
                        set eventStart to start time
                        set eventEnd to end time
                        set startTimeFormat to time string of eventStart
                        set endTimeFormat to time string of eventEnd

                        set shouldSkip to false
                        try
                            if mySubject contains "Tentative" or mySubject contains "(Tentative)" then
                                set shouldSkip to true
                            end if
                        end try

                        if not shouldSkip then
                            set eventLocation to ""
                            try
                                set eventLocation to location as text
                            end try

                            set nameList to ""
                            try
                                set emailList to get every email address of every attendee
                                set ind to 0
                                repeat with theName in emailList
                                    set ind to (ind + 1)
                                    if ind = 1 then
                                        set nameList to name of theName
                                    else
                                        set nameList to nameList & ", " & name of theName
                                    end if
                                end repeat
                            end try

                            set eventAgenda to ""
                            try
                                set eventAgenda to plain text content as text
                            end try

                            set eventString to mySubject & "|||" & startTimeFormat & "|||" & endTimeFormat & "|||" & nameList & "|||" & eventLocation & "|||" & eventAgenda
                            set finalList to (eventString & "[][][]" & finalList)
                        end if
                    end tell
                end try
            end repeat

            return finalList
        end try
    end tell
    '''


def _fetch_via_outlook_applescript():
    """Fetch today's events via AppleScript (legacy Outlook). Returns list of event dicts."""
    today = datetime.now()
    date_string = today.strftime("%A, %B %-d, %Y") + " 12:00:00 AM"

    raw = _run_osascript(_outlook_script_for_today(date_string))
    if raw is None:
        return None

    events = []
    if raw.strip():
        for event_string in raw.strip().split(EVENT_SEP):
            if not event_string.strip():
                continue
            parts = event_string.split(FIELD_SEP)
            if len(parts) >= 6:
                events.append({
                    'title': parts[0].strip(),
                    'start_time': parts[1].strip(),
                    'end_time': parts[2].strip(),
                    'attendees': parts[3].strip(),
                    'location': parts[4].strip(),
                    'agenda': parts[5].strip(),
                })
    return events


def _fetch_via_graph():
    """Fetch today's events via Graph API. Returns list of event dicts or None on failure."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(script_dir, "lib")
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)
    # Point auth.py to shared config location if not already set
    if "GRAPH_CONFIG_DIR" not in os.environ:
        os.environ["GRAPH_CONFIG_DIR"] = os.path.join(
            os.getenv('HOME'),
            "Library/CloudStorage/OneDrive-RegeneronPharmaceuticals,Inc/MyScripts/myGitHubRepos/alfred-outlook/src"
        )

    try:
        from auth import get_token, GRAPH_ENDPOINT
        import requests
    except ImportError:
        return None

    try:
        token = get_token()
    except Exception:
        return None

    local_tz = datetime.now().astimezone().tzinfo
    today = datetime.now().date()
    start_dt = datetime.combine(today, datetime.min.time()).replace(tzinfo=local_tz)
    end_dt = datetime.combine(today, datetime.max.time()).replace(tzinfo=local_tz)
    start_utc = start_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    end_utc = end_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    response = requests.get(
        f"{GRAPH_ENDPOINT}/me/calendarView",
        headers={
            "Authorization": f"Bearer {token}",
            "Prefer": 'outlook.timezone="Eastern Standard Time", outlook.body-content-type="text"',
        },
        params={
            "startDateTime": start_utc,
            "endDateTime": end_utc,
            "$select": "subject,start,end,attendees,body,location,responseStatus,isCancelled",
            "$orderby": "start/dateTime",
            "$top": 100,
        },
    )
    if response.status_code != 200:
        config.log(f"Graph API error {response.status_code}")
        return None

    raw_events = response.json().get("value", [])

    # Filter: skip cancelled and declined events
    events = []
    for ev in raw_events:
        if ev.get("isCancelled"):
            continue
        response_status = ev.get("responseStatus", {}).get("response", "")
        if response_status == "declined":
            continue
        events.append(ev)

    # Format into the common event dict structure
    result = []
    for ev in events:
        start_str = ev["start"]["dateTime"]
        end_str = ev["end"]["dateTime"]
        # Handle extra fractional digits from Graph API
        start_str = re.sub(r'(\.\d{6})\d+', r'\1', start_str)
        end_str = re.sub(r'(\.\d{6})\d+', r'\1', end_str)
        dt_start = datetime.fromisoformat(start_str)
        dt_end = datetime.fromisoformat(end_str)

        attendees = ev.get("attendees", [])
        name_list = ", ".join(
            a.get("emailAddress", {}).get("name", a.get("emailAddress", {}).get("address", ""))
            for a in attendees
        )

        result.append({
            'title': ev.get("subject", "(no subject)"),
            'start_time': dt_start.strftime("%-I:%M:%S %p"),
            'end_time': dt_end.strftime("%-I:%M:%S %p"),
            'attendees': name_list,
            'location': ev.get("location", {}).get("displayName", ""),
            'agenda': ev.get("body", {}).get("content", ""),
        })

    return result


def _extract_section_from_file(file_path, section_header):
    """Extract content from a specific section in a markdown file.

    Extracts all content between the specified header and the next # header.

    Args:
        file_path: Path to the markdown file
        section_header: Header to extract (e.g., "# Active Items")

    Returns:
        List of lines in that section, or empty list if not found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, OSError):
        return []

    sections = {}
    current_section = "intro"
    current_content = []

    for line in lines:
        if re.match(r'^# +', line):
            sections[current_section] = current_content
            current_section = line.strip()
            current_content = []
        else:
            current_content.append(line.rstrip())

    sections[current_section] = current_content

    return sections.get(section_header, [])


def _has_frontmatter_tag(file_path, tag):
    """Check if a markdown file has a specific tag in its YAML frontmatter.

    Args:
        file_path: Path to the markdown file
        tag: Tag to look for (without #)

    Returns:
        True if the tag is found in frontmatter, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, OSError):
        return False

    if not lines or lines[0].strip() != '---':
        return False

    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter_lines = lines[1:i]
            break
    else:
        return False

    tag = tag.lstrip('#')

    frontmatter_text = ' '.join(line.strip() for line in frontmatter_lines)
    patterns = [
        rf'\btags:\s*\[.*\b{re.escape(tag)}\b.*\]',  # tags: [tag1, tag2]
        rf'\btags:\s+.*\b{re.escape(tag)}\b',         # tags: tag1, tag2
    ]

    for pattern in patterns:
        if re.search(pattern, frontmatter_text, re.IGNORECASE):
            return True

    # Check YAML list format (line by line)
    in_tags_list = False
    for line in frontmatter_lines:
        line_stripped = line.strip()

        if line_stripped.startswith('tags:'):
            in_tags_list = True
            rest = line_stripped[5:].strip()
            if rest and not rest.startswith('['):
                if re.search(rf'\b{re.escape(tag)}\b', rest, re.IGNORECASE):
                    return True
            continue

        if in_tags_list:
            if line_stripped.startswith('-'):
                item = line_stripped[1:].strip()
                if item.lower() == tag.lower():
                    return True
            elif not line_stripped.startswith(' ') and not line_stripped.startswith('-'):
                in_tags_list = False

    return False


def _match_attendee_to_person_note(attendee_name, people_folder):
    """Match an attendee name to a person note file.

    Args:
        attendee_name: Name of the attendee from calendar
        people_folder: Path to the folder containing person notes

    Returns:
        Path to the matching person note, or None if not found
    """
    if not people_folder or not os.path.isdir(people_folder):
        return None

    name_clean = attendee_name.strip()

    # Try exact match first (case-insensitive)
    for filename in os.listdir(people_folder):
        if not filename.endswith('.md'):
            continue

        file_stem = Path(filename).stem

        if file_stem.lower() == name_clean.lower():
            return os.path.join(people_folder, filename)

    # Try partial match (attendee name is in filename or vice versa)
    name_parts = name_clean.lower().split()
    for filename in os.listdir(people_folder):
        if not filename.endswith('.md'):
            continue

        file_stem = Path(filename).stem.lower()

        if all(part in file_stem for part in name_parts):
            return os.path.join(people_folder, filename)

        file_parts = file_stem.split()
        if all(part in name_clean.lower() for part in file_parts):
            return os.path.join(people_folder, filename)

    return None


def _get_to_discuss_items(attendees_str):
    """Get 'to discuss' items for one-on-one meetings.

    If this is a one-to-one meeting and the other person has a note with
    the one-on-one tag, extract their discussion items.

    Args:
        attendees_str: Comma-separated string of attendee names

    Returns:
        Formatted string with to-discuss items, or empty string
    """
    if not config.PEOPLE_FOLDER or not os.path.isdir(config.PEOPLE_FOLDER):
        return ""

    attendees = [a.strip() for a in attendees_str.split(',') if a.strip()]

    # Graph API doesn't include the organizer in attendees, so:
    # - 1 attendee = organizer + 1 other (one-on-one)
    # - 2 attendees = could be organizer explicitly listed + 1 other, or a 3-person meeting
    # For safety, accept 1 or 2 attendees.
    if len(attendees) == 0 or len(attendees) > 2:
        return ""

    for attendee in attendees:
        person_file = _match_attendee_to_person_note(attendee, config.PEOPLE_FOLDER)

        if not person_file:
            continue

        if not _has_frontmatter_tag(person_file, config.ONE_ON_ONE_TAG):
            continue

        items = _extract_section_from_file(person_file, config.DISCUSS_SECTION)

        if items:
            items = [line for line in items if line.strip()]

            if items:
                person_name = Path(person_file).stem
                result = f"**To Discuss with [[{person_name}]]:**\n"
                result += "\n".join(items)
                return result

    return ""


def _relative_delta(past_date, today):
    """Human-readable calendar delta between two dates, e.g. "1m 18d ago"."""
    years = today.year - past_date.year
    months = today.month - past_date.month
    days = today.day - past_date.day
    if days < 0:
        months -= 1
        prev_month = today.month - 1
        prev_year = today.year
        if prev_month == 0:
            prev_month = 12
            prev_year -= 1
        days += calendar.monthrange(prev_year, prev_month)[1]
    if months < 0:
        years -= 1
        months += 12
    total_months = years * 12 + months
    parts = []
    if total_months:
        parts.append(f"{total_months}m")
    parts.append(f"{days}d")
    return " ".join(parts) + " ago"


def _get_previous_meeting_block(attendees_str):
    """For a one-on-one meeting, find the most recent daily note that logged a
    "# Meeting with [[Person]]" entry and return a backlink to it plus the
    time the vault scan took.

    Returns a two-line string (previous-meeting backlink + grepTime), or "".
    """
    vault = config.VAULT_PATH
    if not vault or not os.path.isdir(vault):
        return ""

    attendees = [a.strip() for a in attendees_str.split(',') if a.strip()]
    if len(attendees) == 0 or len(attendees) > 2:
        return ""

    # Resolve each attendee to the person-note stem used in daily-note headers;
    # fall back to the raw attendee name when there's no matching note.
    candidates = []
    for attendee in attendees:
        person_file = _match_attendee_to_person_note(attendee, config.PEOPLE_FOLDER)
        candidates.append(Path(person_file).stem if person_file else attendee)

    start = time.perf_counter()
    today = datetime.now().date()

    dated_files = []
    for filename in os.listdir(vault):
        if not filename.endswith('.md'):
            continue
        m = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        if not m:
            continue
        try:
            note_date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        except ValueError:
            continue
        if note_date >= today:
            continue
        dated_files.append((note_date, filename))

    dated_files.sort(key=lambda x: x[0], reverse=True)

    found = None
    for note_date, filename in dated_files:
        try:
            with open(os.path.join(vault, filename), 'r', encoding='utf-8') as f:
                content = f.read()
        except (IOError, OSError):
            continue
        for person_name in candidates:
            pattern = rf'#\s+Meeting\s+with\s+\[\[{re.escape(person_name)}\]\]'
            if re.search(pattern, content, re.IGNORECASE):
                found = (note_date, Path(filename).stem, person_name)
                break
        if found:
            break

    elapsed = time.perf_counter() - start

    if not found:
        return ""

    note_date, stem, person_name = found
    rel = _relative_delta(note_date, today)
    line = f"Previous meeting ({rel}): [[{stem}#Meeting with {person_name}]]"
    return f"{line}\ngrepTime: {elapsed:.3f} sec"


def _clean_body(body_text):
    """Clean up event body text: fix links, remove Teams boilerplate."""
    body_text = re.sub(
        r'\[​\w+ icon\]\s*([^<\n]+)<(https?://[^>]+)>',
        r'[\1](\2)',
        body_text
    )
    body_text = re.sub(
        r'\[https?://[^\]]+\]\s*([^<\n]+)<(https?://[^>]+)>',
        r'[\1](\2)',
        body_text
    )
    body_text = re.sub(r'\[cid:[^\]]+\]', '', body_text)
    lines = body_text.split("\n")
    filtered = []
    for line in lines:
        if "Microsoft Teams" in line and ("meeting" in line.lower() or "Need help" in line):
            break
        filtered.append(line)
    return "\n".join(filtered).rstrip()


def _format_outlook_agenda(events, weekday_name):
    """Render Outlook events (Graph or AppleScript) as a Markdown agenda,
    including "to discuss" items for one-on-one meetings."""
    if not events:
        return f"\U0001F4C5 No meetings scheduled for {weekday_name}. Enjoy your free time! ☕️"

    markdown_output = ""
    for event in events:
        markdown_output += f"# {event['title']}\n"
        markdown_output += f"**Time:** {event['start_time']} - {event['end_time']}\n"
        if event['location']:
            markdown_output += f"**Location:** {event['location']}\n"
        if event['attendees']:
            markdown_output += f"**Attendees:** {event['attendees']}\n"

        if event['attendees']:
            to_discuss = _get_to_discuss_items(event['attendees'])
            if to_discuss:
                markdown_output += f"{to_discuss}\n"

            prev_meeting = _get_previous_meeting_block(event['attendees'])
            if prev_meeting:
                markdown_output += f"{prev_meeting}\n"

        if event['agenda'] and len(event['agenda']) > 10:
            agenda_clean = _clean_body(event['agenda'])
            if agenda_clean:
                agenda_preview = agenda_clean[:500] + "..." if len(agenda_clean) > 500 else agenda_clean
                markdown_output += f"**Agenda:** {agenda_preview}\n"
        markdown_output += "\n"

    return markdown_output.strip()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def fetch_today_agenda():
    """Return today's agenda as a Markdown string, using CALENDAR_SOURCE."""
    today = datetime.now()
    weekday_name = today.strftime("%A")
    source = config.CALENDAR_SOURCE.lower()
    try:
        if source == 'outlook':
            events = _fetch_via_graph()
            if events is None:
                config.log("Graph API unavailable, falling back to AppleScript")
                events = _fetch_via_outlook_applescript()
            if events is None:
                return "\U0001F4C5 Could not read your calendar (check Outlook automation permissions)."
            return _format_outlook_agenda(events, weekday_name)
        else:
            raw = _run_osascript(_apple_script_for_today())
            if raw is None:
                return "\U0001F4C5 Could not read your calendar (check Automation permissions)."
            return _format_apple_agenda(raw, weekday_name)
    except Exception as e:
        config.log(f"Error in fetch_today_agenda: {e}")
        return f"\U0001F4C5 Error fetching agenda: {e}"


if __name__ == "__main__":
    print(fetch_today_agenda())
