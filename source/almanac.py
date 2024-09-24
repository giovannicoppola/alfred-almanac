#!/usr/bin/env python3

## a script to get a one-liner from wttr
# Wednesday, July 21, 2021, 10:42 AM
# Tuesday, March 1, 2022, 8:51 AM new version without requests

#import requests
import json
import sys
import requests
from datetime import datetime, timedelta
import datetime as date2
import re, os, time


from config import LOCATION, FORMATSTRING, SPECIAL_DAY, WEEKLY

FORMATSTRING = FORMATSTRING+"--%Z--" #adding local timezone
#FORMATSTRING = f'"{FORMATSTRING}"'  #enclosing in quotes


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)

def createWeeklyPlan():
    # Get today's date
    today = datetime.today()
    
    # Calculate the previous Monday
    previous_monday = today - timedelta(days=today.weekday())
    
    # Calculate the following Friday
    following_friday = previous_monday + timedelta(days=4)
    
    # Format the dates as strings
    previous_monday_str = previous_monday.strftime('%Y-%m-%d')
    following_friday_str = following_friday.strftime('%Y-%m-%d')
    year_week = date2.date.today().isocalendar()[1]
    finalString = f"[[Weekly plan ({year_week}) {previous_monday_str} to {following_friday_str}]]" 
    return finalString


def get_weather(location):
    
    
    myURL= "http://wttr.in/"
    
    payload = {'format': FORMATSTRING}
    payload_j = {'format': "j1"}
    #paramsJ = "format=j1"
    location = location.strip()
    location=re.sub(" ", '+', location)
    
    resp = requests.get(f"http://wttr.in/{loc}", params=payload)
    log (f"----={resp.url}")
    myData = resp.text.strip()
    log (myData)
    
    #fetching also the JSON output for extra information
    resp_j = requests.get(f"http://wttr.in/{loc}", params=payload_j) 
    
    myResults =  (resp_j.json())
    myLocation = myResults['nearest_area'][0]['areaName'][0]['value'] #getting the location from the output
    
            
    # extracting timezone
    timeZonePattern="--(.*?)--"
    
    myTimeZone = re.search(timeZonePattern, myData).group(1)

    log (myTimeZone)
    myData=re.sub(timeZonePattern, '', myData)

    myWeatherString = myLocation + \
    " – " + myData.strip()
        
    #getting date and time in the corresponding timezone
    os.environ['TZ'] = myTimeZone
    time.tzset()
    myLocalTime=time.asctime()
    log (myLocalTime)


    return (myWeatherString,myLocalTime, myTimeZone)
    

def almanac ():
    today = datetime.now()
    todayStandard = today.strftime("%Y-%m-%d %a %-I:%M%p")
    todayMonth = today.month
    todayHour = today.hour

    todayQuarter =  (todayMonth-1)//3 + 1
    currentYear = today.year

    day_of_year = datetime.now().timetuple().tm_yday  # from https://stackoverflow.com/questions/620305/convert-year-month-day-to-day-of-year-in-python
    year_week = date2.date.today().isocalendar()[1]

    Yend = datetime(currentYear,12,31)
    days_to_Yend = Yend - today

    
    ## Special Day
    SD_month, SD_day = SPECIAL_DAY.split('-')
    currentSD = datetime(currentYear,int(SD_month),int(SD_day))
    dateDiff = currentSD - today
    
    if dateDiff.days>0:  #SD is in the future
        pastSD = datetime(currentYear-1,int(SD_month),int(SD_day))
        nextSD = currentSD
    else:
        pastSD = currentSD
        nextSD = datetime(currentYear+1,int(SD_month),int(SD_day))
        
    days_fromSD = (today - pastSD).days
    days_toSD = (nextSD - today).days

    myAlmanacString = "\nW"+str(year_week)+"Q"+str(todayQuarter)+" – "+ str(day_of_year) + " ➡️ " + str(days_to_Yend.days) + \
        " – " + str(days_fromSD) + " ❇️ " + str(days_toSD) 
    

    if todayHour > 12:
        myIcon = "icons/moon.png"
    else:
        myIcon = "icons/sun.png"
    return (myAlmanacString,myIcon)
        


result = {"items": []}
mylocation = LOCATION
if sys.argv[1] == '':
    mylocation = LOCATION
else:
    mylocation = sys.argv[1]

myAlmanac,myIcon= almanac()
if WEEKLY == '1':
    weeklyPlan = "\n" + createWeeklyPlan()
else:
    weeklyPlan = ""

locations = mylocation.split(",")
for loc in locations:
    myOutput,myLocalTime, myTimeZone= get_weather(loc)
    myFinalString = myOutput + " " + myLocalTime + myAlmanac + weeklyPlan 
    myTZstring = f"Current date/time: {myLocalTime} ({myTimeZone})"
    result["items"].append({
            "title": myFinalString,
            'subtitle': "↩️ copy to clipboard, ^↩️ large text, ⇧↩️ open in browser, ⌥ timezone",
                        
            "icon": {
                "path": myIcon
            },
            "mods": {
                "option": {
                    "valid": 'true',
                    "arg": myTZstring,
                    
                    "subtitle": myTZstring
                    
                }
            },
            'quicklookurl': f"https://wttr.in/{loc}",
            'arg': (myFinalString + ";;;" + f"http://wttr.in/{loc}")
                })    

print (json.dumps(result))

