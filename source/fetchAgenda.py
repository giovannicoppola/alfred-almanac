#!/usr/bin/env python3

"""
FETCH OUTLOOK MEETING DETAILS - APPLESCRIPT VERSION
A script to use AppleScript to grab all meeting details for today
Returns a markdown formatted list of all events with participants and details
Based on working template from fetchMeetingDetails.py

FILTERING: Skips meetings with "Tentative" or "(Tentative)" in the subject line.
This provides basic filtering for tentative meetings while maintaining compatibility.
More advanced response status filtering can be added later if needed.
"""

import subprocess
import json
import sys
import re
from datetime import datetime
import config


def fetch_today_agenda():
    """
    Use AppleScript to fetch today's calendar events from Outlook and format as markdown
    """
    try:
        # Get today's date for AppleScript
        today = datetime.now()
        day_name = today.strftime("%A")
        month_name = today.strftime("%B")
        day = today.day
        year = today.year
        
        # Format date string for AppleScript
        date_string = f"{day_name}, {month_name} {day}, {year} 12:00:00 AM"
        
        # AppleScript to get events for today
        apple_script = f'''
        tell application "Microsoft Outlook"
            try
                set targetDate to date "{date_string}"
                set startOfDay to targetDate
                set endOfDay to targetDate + (24 * 60 * 60) - 1
                
                set eventList to {{}}
                set finalList to ""
                
                -- Get all calendar events for today
                set todayEvents to (get every calendar event whose start time ≥ startOfDay and start time ≤ endOfDay)
                
                repeat with CalEv in todayEvents
                    try
                        tell CalEv
                            set mySubject to (subject as text)
                            set eventStart to start time
                            set eventEnd to end time
                            set startTimeFormat to time string of eventStart
                            set endTimeFormat to time string of eventEnd
                            
                            -- Simple filtering: skip if subject contains certain keywords that indicate tentative
                            set shouldSkip to false
                            try
                                if mySubject contains "Tentative" or mySubject contains "(Tentative)" then
                                    set shouldSkip to true
                                end if
                            end try
                            
                            if not shouldSkip then
                                -- Get location
                                set eventLocation to ""
                                try
                                    set eventLocation to location as text
                                end try
                                
                                -- Get attendees
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
                                
                                -- Get agenda/body
                                set eventAgenda to ""
                                try
                                    set eventAgenda to plain text content as text
                                end try
                                
                                -- Create event string
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
        
        # Execute the AppleScript
        process = subprocess.Popen(['osascript', '-e', apple_script], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE, 
                                   text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            config.log(f"AppleScript error: {stderr}")
            return "No agenda found - AppleScript error occurred"
        
        # Parse the events
        events = []
        if stdout.strip():
            # Split by events and clean up
            event_strings = stdout.strip().split('[][][]')
            
            for event_string in event_strings:
                if event_string.strip():
                    parts = event_string.split('|||')
                    if len(parts) >= 6:
                        title = parts[0].strip()
                        start_time = parts[1].strip()
                        end_time = parts[2].strip()
                        attendees = parts[3].strip()
                        location = parts[4].strip()
                        agenda = parts[5].strip()
                        
                        events.append({
                            'title': title,
                            'start_time': start_time,
                            'end_time': end_time,
                            'attendees': attendees,
                            'location': location,
                            'agenda': agenda
                        })
        
        # Generate markdown output
        if not events:
            markdown_output = f"No meetings scheduled for {day_name}, {month_name} {day}, {year}. Enjoy your free time! ☕️\n\n"
        else:
            markdown_output = ""
            for event in events:
                markdown_output += f"# {event['title']}\n"
                markdown_output += f"**Time:** {event['start_time']} - {event['end_time']}\n"
                if event['location']:
                    markdown_output += f"**Location:** {event['location']}\n"
                if event['attendees']:
                    markdown_output += f"**Attendees:** {event['attendees']}\n"
                if event['agenda'] and len(event['agenda']) > 10:  # Only show if substantial content
                    # Truncate very long agendas for readability
                    agenda_preview = event['agenda'][:500] + "..." if len(event['agenda']) > 500 else event['agenda']
                    markdown_output += f"**Agenda:** {agenda_preview}\n"
                markdown_output += "\n"
        
        return markdown_output.strip()
    except Exception as e:
        config.log(f"Error in fetch_today_agenda: {str(e)}")
        return f"Error fetching agenda: {str(e)}"


def main():
    try:
        result = fetch_today_agenda()
        
        # Format for Alfred - wrap in JSON structure
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
