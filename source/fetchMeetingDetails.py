 #!/usr/bin/python3 
# 
# Partly cloudy ⛅️  🌡️+44°F (feels +39°F, 51%) 🌬️↓12mph 🌕 Thu Mar  9 15:22:34 2023
# W10Q1 – 68 ➡️ 296 – 302 ❇️ 62

"""
FETCH OUTLOOK MEETING DETAILS
A script to use applescript to grab meeting details without focusing on the app or selecting the event (as I had in the previous versions)

"""

import time
import json
import os
from config import log
from subprocess import Popen, PIPE, run

myTimeStart = round(time.time())
TIMEINTERVAL = os.path.expanduser(os.getenv('TIME_INTERVAL'))



scpt = '''
    on run {minInterval}


with timeout of (2800 * minutes) seconds
	
	set now to current date
	set now5 to now + (minInterval * minutes) #will work for the current event until x min from the end, after which will work for the next event
	
	tell application "Microsoft Outlook"
		set the clipboard to ""
		
		-- Create and add items
		set theItems to {}
        set theTitles to ""
		set CalEvProperties to ""
        set totalList to (get every calendar event whose start time is less than or equal to now5 and end time is greater than now5)
        set totalNumber to the number of items in totalList
        
		set finalList to ""
        repeat with CalEv in (get every calendar event whose start time is less than or equal to now5 and end time is greater than now5)
			set the clipboard to ""
            
			tell CalEv
                
				# repeat until (the clipboard) contains ("Event" & id as text) & " info"
				# 	delay 0.1
				# end repeat
				
                
                
                set mySubject to (subject as text)
				set eventStart to start time
                set eventEnd to end time
                set startFormat to date string of eventStart
                set startTimeFormat to time string of eventStart
                set endTimeFormat to time string of eventEnd
                

                set emailList to ""
		        set nameList to ""
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
		
                
				#return {CalEvProperties, mySubject}
                set currEvent to (startFormat & " – " & startTimeFormat & "-" & endTimeFormat & "|||---|||" & mySubject & "|||---|||" & nameList & "|||---|||")
                set finalList to (currEvent & "[][][]" & finalList)

			end tell
			#delay 0.5
		end repeat
    
    return finalList


	end tell
end timeout

end run
'''


args = [TIMEINTERVAL]        
p = Popen(['osascript', '-'] + args, stdin=PIPE, stdout=PIPE, stderr=PIPE, universal_newlines=True)
stdout, stderr = p.communicate(scpt)
log (stdout)

myResults = stdout.split("[][][]")
myFinalString = ''
countR = 0
result = {"items": []}
lenResults = len(myResults)-1
if lenResults > 0:

    for currResult in myResults[:-1]:
        
        countR += 1 
        currResultL = currResult.split("|||---|||")
        myStartTime = currResultL[0]
        myTitle = currResultL[1]
        myAttendees = currResultL[2]
        myFinalString = f"{myTitle}\n{myStartTime}\n\t{myAttendees}\n\n"

        result["items"].append({
            "title": f"{myTitle}",
            "subtitle": f"{countR}/{lenResults} – {myStartTime}",
            "arg": f"# {myFinalString}"
                })
        log (myFinalString)
else:
   result["items"].append({
            "title": f"No events in this time interval",
            "subtitle": f"enjoy the break!",
            "arg": "",
            "icon": {   
        
                 "path": "coffee.png"
             }

                })


    

myTimeEnd = round(time.time())

main_timeElapsed = round (myTimeEnd - myTimeStart)
log (f"time elapsed: {main_timeElapsed}")


myTimeStartF = time.strftime('%Y-%m-%d-%a, %I:%M', time.localtime(myTimeStart))
myTimeEndF = time.strftime('%I:%M %p', time.localtime(myTimeEnd))


# Copy the string to the clipboard
#run('pbcopy', universal_newlines=True, input=myFinalString)


print (json.dumps(result))













 

