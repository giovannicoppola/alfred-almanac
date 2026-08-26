#!/usr/bin/python3

import os
from subprocess import run

# Test the current JXA script to see the exact error
scpt = '''
function run() {
    const now = new Date();
    
    // Get start of today (00:00:00)
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
    
    // Get end of today (23:59:59)
    const todayEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59);

    const Outlook = Application('Microsoft Outlook');
    
    // Get all events and filter manually for today
    const allEvents = Outlook.calendarEvents();
    
    return "Found " + allEvents.length + " total events";
}

const result = run();
result;
'''

# Save the JXA script to a temporary file
temp_script_path = "debug_simple.js"
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
