#!/usr/bin/python3

import json
import os
from subprocess import run

# Test script to debug calendar access
scpt = '''
function run() {
    try {
        const Outlook = Application('Microsoft Outlook');
        
        // Get all calendars
        const allCalendars = Outlook.calendars();
        const calendarInfo = [];
        
        for (const calendar of allCalendars) {
            try {
                calendarInfo.push({
                    name: calendar.name(),
                    eventCount: calendar.calendarEvents().length
                });
            } catch (e) {
                calendarInfo.push({
                    name: "Error accessing calendar",
                    error: e.toString()
                });
            }
        }
        
        return JSON.stringify({
            totalCalendars: allCalendars.length,
            calendars: calendarInfo
        });
        
    } catch (error) {
        return JSON.stringify({
            error: error.toString()
        });
    }
}

const result = run();
result;
'''

# Save the JXA script to a temporary file
temp_script_path = "debug_calendars.js"
with open(temp_script_path, "w") as file:
    file.write(scpt)

try:
    # Execute the JXA script using subprocess and capture both stdout and stderr
    result = run(["osascript", temp_script_path], capture_output=True, text=True)
    
    print("Return code:", result.returncode)
    print("STDOUT:", repr(result.stdout))
    print("STDERR:", repr(result.stderr))
    
    # Remove the temporary file
    os.remove(temp_script_path)
    
except Exception as e:
    print(f"Exception: {e}")
    # Clean up temp file if it exists
    if os.path.exists(temp_script_path):
        os.remove(temp_script_path)
