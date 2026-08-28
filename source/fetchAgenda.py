#!/usr/bin/env python3

"""
FETCH OUTLOOK MEETING DETAILS
Fetches today's calendar events and returns a markdown formatted list.

Tries Graph API first (new Outlook), falls back to AppleScript (legacy).
"""

import subprocess
import json
import sys
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
import config


def _extract_section_from_file(file_path, section_header):
    """Extract content from a specific section in a markdown file.

    Similar to MDsuite's fetchSection.py - extracts all content between
    the specified header and the next # header.

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
        # Check if line is a header (starts with # followed by space)
        if re.match(r'^# +', line):
            # Save previous section
            sections[current_section] = current_content
            # Start new section
            current_section = line.strip()
            current_content = []
        else:
            current_content.append(line.rstrip())

    # Save last section
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

    # Check if file starts with frontmatter delimiter
    if not lines or lines[0].strip() != '---':
        return False

    # Find the closing delimiter
    in_frontmatter = False
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            # End of frontmatter found
            frontmatter_lines = lines[1:i]
            break
    else:
        # No closing delimiter found
        return False

    # Search for the tag in frontmatter
    # Tags can be in format:
    #   tags: [tag1, tag2]
    #   tags: tag1, tag2
    #   tags:
    #     - tag1
    #     - tag2

    # Remove # if present in tag
    tag = tag.lstrip('#')

    # Check inline formats first (join all lines)
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

        # Check if we're entering a tags: section
        if line_stripped.startswith('tags:'):
            in_tags_list = True
            # Check if tag is on the same line: "tags: tag1"
            rest = line_stripped[5:].strip()
            if rest and not rest.startswith('['):
                # Single tag or comma-separated on same line
                if re.search(rf'\b{re.escape(tag)}\b', rest, re.IGNORECASE):
                    return True
            continue

        # If we're in tags list, check list items
        if in_tags_list:
            if line_stripped.startswith('-'):
                # List item under tags:
                item = line_stripped[1:].strip()
                if item.lower() == tag.lower():
                    return True
            elif not line_stripped.startswith(' ') and not line_stripped.startswith('-'):
                # New key, exit tags list
                in_tags_list = False

    return False


def _match_attendee_to_person_note(attendee_name, people_folder):
    """Match an attendee name to a person note file.

    Tries to find a markdown file in the people folder that matches the
    attendee name. Handles various name formats.

    Args:
        attendee_name: Name of the attendee from calendar
        people_folder: Path to the folder containing person notes

    Returns:
        Path to the matching person note, or None if not found
    """
    if not people_folder or not os.path.isdir(people_folder):
        return None

    # Clean up attendee name
    name_clean = attendee_name.strip()

    # Try exact match first (case-insensitive)
    for filename in os.listdir(people_folder):
        if not filename.endswith('.md'):
            continue

        file_stem = Path(filename).stem

        # Exact match
        if file_stem.lower() == name_clean.lower():
            return os.path.join(people_folder, filename)

    # Try partial match (attendee name is in filename or vice versa)
    name_parts = name_clean.lower().split()
    for filename in os.listdir(people_folder):
        if not filename.endswith('.md'):
            continue

        file_stem = Path(filename).stem.lower()

        # Check if all parts of attendee name are in filename
        if all(part in file_stem for part in name_parts):
            return os.path.join(people_folder, filename)

        # Check if filename is in attendee name
        file_parts = file_stem.split()
        if all(part in name_clean.lower() for part in file_parts):
            return os.path.join(people_folder, filename)

    return None


def _get_to_discuss_items(attendees_str):
    """Get 'to discuss' items for one-on-one meetings.

    If this is a one-to-one meeting (exactly 2 attendees) and the other
    person has a note with the one-on-one tag, extract their Active Items.

    Args:
        attendees_str: Comma-separated string of attendee names

    Returns:
        Formatted string with to-discuss items, or empty string
    """
    if not config.PEOPLE_FOLDER or not os.path.isdir(config.PEOPLE_FOLDER):
        return ""

    # Parse attendees
    attendees = [a.strip() for a in attendees_str.split(',') if a.strip()]

    # Check if it's a one-to-one
    # Graph API doesn't include organizer in attendees, so:
    # - 1 attendee = organizer + 1 other (one-on-one)
    # - 2 attendees = could be organizer explicitly listed + 1 other, or 3-person meeting
    # For safety, accept 1 or 2 attendees
    if len(attendees) == 0 or len(attendees) > 2:
        return ""

    # Try to match each attendee to a person note
    for attendee in attendees:
        person_file = _match_attendee_to_person_note(attendee, config.PEOPLE_FOLDER)

        if not person_file:
            continue

        # Check if this person has the one-on-one tag
        if not _has_frontmatter_tag(person_file, config.ONE_ON_ONE_TAG):
            continue

        # Extract the Active Items section
        items = _extract_section_from_file(person_file, config.DISCUSS_SECTION)

        if items:
            # Filter out empty lines
            items = [line for line in items if line.strip()]

            if items:
                # Format like MDsuite: "Meeting with [[PersonName]]" followed by items
                person_name = Path(person_file).stem
                result = f"**To Discuss with [[{person_name}]]:**\n"
                result += "\n".join(items)
                return result

    return ""


def _clean_body(body_text):
    """Clean up event body text: fix links, remove Teams boilerplate."""
    # Convert [​icon] filename<URL> to markdown [filename](URL)
    body_text = re.sub(
        r'\[\u200b\w+ icon\]\s*([^<\n]+)<(https?://[^>]+)>',
        r'[\1](\2)',
        body_text
    )
    # Convert [https://...icon.svg] filename<URL> to markdown [filename](URL)
    body_text = re.sub(
        r'\[https?://[^\]]+\]\s*([^<\n]+)<(https?://[^>]+)>',
        r'[\1](\2)',
        body_text
    )
    # Remove [cid:...] inline image references
    body_text = re.sub(r'\[cid:[^\]]+\]', '', body_text)
    # Remove Teams boilerplate (meeting join info, dial-in, etc.)
    lines = body_text.split("\n")
    filtered = []
    for line in lines:
        if "Microsoft Teams" in line and ("meeting" in line.lower() or "Need help" in line):
            break
        filtered.append(line)
    return "\n".join(filtered).rstrip()


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


def _fetch_via_applescript():
    """Fetch today's events via AppleScript (legacy Outlook). Returns list of event dicts."""
    today = datetime.now()
    day_name = today.strftime("%A")
    month_name = today.strftime("%B")
    day = today.day
    year = today.year

    date_string = f"{day_name}, {month_name} {day}, {year} 12:00:00 AM"

    apple_script = f'''
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

    process = subprocess.Popen(['osascript', '-e', apple_script],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        config.log(f"AppleScript error: {stderr}")
        return None

    events = []
    if stdout.strip():
        event_strings = stdout.strip().split('[][][]')
        for event_string in event_strings:
            if event_string.strip():
                parts = event_string.split('|||')
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


def fetch_today_agenda():
    """
    Fetch today's calendar events and format as markdown.
    Tries Graph API first, falls back to AppleScript.
    """
    today = datetime.now()
    day_name = today.strftime("%A")
    month_name = today.strftime("%B")
    day = today.day
    year = today.year

    # Try Graph API first
    events = _fetch_via_graph()
    if events is None:
        config.log("Graph API unavailable, falling back to AppleScript")
        events = _fetch_via_applescript()

    if not events:
        return f"No meetings scheduled for {day_name}, {month_name} {day}, {year}. Enjoy your free time! ☕️\n\n"

    markdown_output = ""
    for event in events:
        markdown_output += f"# {event['title']}\n"
        markdown_output += f"**Time:** {event['start_time']} - {event['end_time']}\n"
        if event['location']:
            markdown_output += f"**Location:** {event['location']}\n"
        if event['attendees']:
            markdown_output += f"**Attendees:** {event['attendees']}\n"

        # Check for one-on-one and add "to discuss" items
        if event['attendees']:
            to_discuss = _get_to_discuss_items(event['attendees'])
            if to_discuss:
                markdown_output += f"{to_discuss}\n"

        if event['agenda'] and len(event['agenda']) > 10:
            agenda_clean = _clean_body(event['agenda'])
            if agenda_clean:
                agenda_preview = agenda_clean[:500] + "..." if len(agenda_clean) > 500 else agenda_clean
                markdown_output += f"**Agenda:** {agenda_preview}\n"
        markdown_output += "\n"

    return markdown_output.strip()


def main():
    try:
        result = fetch_today_agenda()

        alfred_output = {
            "items": [
                {
                    "title": f"{datetime.now().strftime('%A')}'s Schedule",
                    "subtitle": "Meetings found",
                    "arg": result
                }
            ]
        }

        print(json.dumps(alfred_output))
        config.log(f"Generated markdown output with {result.count('# ')} events")

    except Exception as e:
        error_output = {
            "items": [
                {
                    "title": "Error fetching agenda",
                    "subtitle": str(e),
                    "arg": f"Error: {str(e)}"
                }
            ]
        }
        print(json.dumps(error_output))
        config.log(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()
