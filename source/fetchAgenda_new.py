#!/usr/bin/python3 
# 
# Modified from fetchMeetingDetails to get agenda for a specific day
# Now gets events for Monday, August 18, 2025

"""
FETCH OUTLOOK MEETING DETAILS - DAILY VERSION
A script to use AppleScript to grab all meeting details for Monday, August 18, 2025
Returns a markdown formatted list of all events with participants and details

"""

import time
import json
import os
from config import log
from subprocess import Popen, PIPE, run

def fetch_today_agenda():
    """
    Fetch Monday's agenda from Outlook and return as markdown string
    """
    myTimeStart = round(time.time())

    # AppleScript to get events for Monday, August 18, 2025
    scpt = '''
    on run
        with timeout of (300) seconds
            set targetDate to date "Monday, August 18, 2025 12:00:00 AM"
            set dayStart to targetDate
            set dayEnd to targetDate + (24 * hours) - 1
            
            tell application "Microsoft Outlook"
                set finalList to ""
                set totalList to (get every calendar event whose start time is greater than or equal to dayStart and start time is less than dayEnd)
                
                repeat with CalEv in totalList
                    tell CalEv
                        set mySubject to (subject as text)
                        set eventStart to start time
                        set eventEnd to end time
                        set startTimeFormat to time string of eventStart
                        set endTimeFormat to time string of eventEnd
                        
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
                        
                        -- Get content/agenda
                        set eventContent to ""
                        try
                            set eventContent to content as text
                        end try
                        
                        -- Format the event data
                        set currEvent to (mySubject & "|||" & startTimeFormat & "|||" & endTimeFormat & "|||" & nameList & "|||" & eventLocation & "|||" & eventContent & "[][][]")
                        set finalList to (finalList & currEvent)
                    end tell
                end repeat
                
                return finalList
            end tell
        end timeout
    end run
    '''

    try:
        # Execute the AppleScript using subprocess
        p = Popen(['osascript', '-e', scpt], stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        stdout, stderr = p.communicate()
        
        log(f"Raw output: {stdout}")
        if stderr:
            log(f"Error output: {stderr}")
        
        # Parse the results
        events_data = []
        if stdout and stdout.strip():
            myResults = stdout.strip().split("[][][]")
            for currResult in myResults:
                if currResult.strip():
                    try:
                        parts = currResult.split("|||")
                        if len(parts) >= 6:
                            event = {
                                'subject': parts[0],
                                'startTime': parts[1],
                                'endTime': parts[2],
                                'attendees': parts[3],
                                'location': parts[4],
                                'agenda': parts[5]
                            }
                            events_data.append(event)
                    except Exception as e:
                        log(f"Error parsing event: {e}")
                        continue
        
        # Generate markdown output
        markdown_output = f"\n"
        
        if not events_data:
            markdown_output += "No meetings scheduled for Monday, August 18, 2025. Enjoy your free time! ☕️\n\n"
        else:
            for i, event in enumerate(events_data, 1):
                markdown_output += f"# {event['subject']}\n"
                markdown_output += f"**Time:** {event['startTime']} - {event['endTime']}\n"
                
                if event['location'] and event['location'].strip():
                    markdown_output += f"**Location:** {event['location']}\n"
                
                if event['attendees'] and event['attendees'].strip():
                    markdown_output += f"**Attendees:** {event['attendees']}\n"
                
                if event['agenda'] and event['agenda'].strip() and event['agenda'] != '&nbsp;':
                    # Clean up the agenda content
                    agenda_clean = event['agenda'].replace('&nbsp;', '').strip()
                    if agenda_clean:
                        if len(agenda_clean) > 200:
                            agenda_clean = agenda_clean[:200] + '...'
                        markdown_output += f"**Agenda:** {agenda_clean}\n"
                
                markdown_output += "\n"
        
        log(f"Generated markdown output with {len(events_data)} events")
        
        myTimeEnd = round(time.time())
        main_timeElapsed = round(myTimeEnd - myTimeStart)
        log(f"time elapsed: {main_timeElapsed}")
        
        return markdown_output
        
    except Exception as e:
        log(f"Error: {str(e)}")
        
        # Return error message as markdown
        error_output = f"\n## Monday's Meetings - Error\n\nFailed to fetch Monday's meetings: {str(e)}\n\n"
        
        return error_output


# If this script is run directly (for backwards compatibility with Alfred)
if __name__ == "__main__":
    agenda_markdown = fetch_today_agenda()
    
    # For Alfred compatibility, convert back to JSON format
    result_json = {"items": []}
    
    if "No meetings scheduled" in agenda_markdown:
        result_json["items"].append({
            "title": "No meetings Monday",
            "subtitle": "Enjoy your free time!",
            "arg": agenda_markdown,
            "icon": {
                "path": "coffee.png"
            }
        })
    else:
        result_json["items"].append({
            "title": "Monday's Schedule",
            "subtitle": "Meetings found",
            "arg": agenda_markdown
        })
    
    # Output the final JSON result for Alfred
    print(json.dumps(result_json))
