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


from config import LOCATION, FORMATSTRING, SPECIAL_DAY, WEEKLY, LINEADAY_FILE, LINEADAY

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
    finalString = f"![[Weekly plan ({year_week}) {previous_monday_str} to {following_friday_str}]]" 
    return finalString



def createNextWeeklyPlan():
    # Get today's date
    today = datetime.today()
    
    # Check if today is Friday (weekday() returns 4 for Friday)
    if today.weekday() == 4:
        # Calculate the next Monday
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        # Calculate the following Friday
        following_friday = next_monday + timedelta(days=4)
        
        # Format the dates as strings
        next_monday_str = next_monday.strftime('%Y-%m-%d')
        following_friday_str = following_friday.strftime('%Y-%m-%d')
        
        # Get the ISO calendar week number for the next Monday
        year_week = next_monday.isocalendar()[1]
        
        # Create the final string
        finalString = f"\n![[Weekly plan ({year_week}) {next_monday_str} to {following_friday_str}]]"
        
        return finalString
    else:
        return ""
    
    
    
def get_weather(location):
    
    
    myURL= "http://wttr.in/"
    
    payload = {'format': FORMATSTRING}
    payload_j = {'format': "j1"}
    #paramsJ = "format=j1"
    location = location.strip()
    location=re.sub(" ", '+', location)
    
    resp = requests.get(f"http://wttr.in/{location}", params=payload)
    log (f"----={resp.url}")
    myData = resp.text.strip()
    log (myData)
    
    #fetching also the JSON output for extra information
    resp_j = requests.get(f"http://wttr.in/{location}", params=payload_j) 
    
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




# Function to read the markdown file and extract lines
def read_markdown_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

# Function to extract dates and store the original lines
def extract_dates_and_lines(lines):
    date_lines = []
    for line in lines:
        if line.startswith('- **'):
            date_str = line.split('**')[1].split(' ')[0]
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_lines.append((date_obj, line.strip()))
    return date_lines

# Function to find the closest dates
def find_closest_dates(date_lines, target_date):
    return min(date_lines, key=lambda x: abs(x[0] - target_date))

def fetchLineADay(file_path):
    # Read the markdown file
    lines = read_markdown_file(file_path)

    # Extract dates and lines
    date_lines = extract_dates_and_lines(lines)

    # Calculate today's date
    today = datetime.now()

    # Determine the range of dates
    earliest_date = min(date_lines, key=lambda x: x[0])[0]  # Extract the date part from the tuple

    date_range_years = (today - earliest_date).days / 365.25

    # Calculate the number of complete years
    complete_years = int(date_range_years)
    # Initialize an empty string to accumulate results
    result_string = "\n\n📅 **One-line-a-days**\n"
    # Find the closest dates to each complete year ago
    for year in range(1, complete_years + 1):
        target_date = today - timedelta(days=365 * year)
        closestLine = find_closest_dates(date_lines, target_date)
        result_string += "\t" + closestLine[1] + "\n"  # Add the line part of the tuple to the result string

    return result_string
    





def almanac ():
    today = datetime.now()
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
        

def main():

    result = {"items": []}
    mylocation = LOCATION
    if sys.argv[1] == '':
        mylocation = LOCATION
    else:
        mylocation = sys.argv[1]

    myAlmanac,myIcon= almanac()
    if WEEKLY == '1':
        weeklyPlan = "\n" + createWeeklyPlan()
        nextWeeklyPlan = "\n" + createNextWeeklyPlan()
    else:
        weeklyPlan = ""
        nextWeeklyPlan = ""

    if LINEADAY == '1':
        previousLines = fetchLineADay(LINEADAY_FILE)
    else:
        previousLines = ""


    locations = mylocation.split(",")
    for loc in locations:
        myOutput,myLocalTime, myTimeZone= get_weather(loc)
        myFinalString = myOutput + " " + myLocalTime + myAlmanac + previousLines + weeklyPlan + nextWeeklyPlan
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



# Run the main function
if __name__ == "__main__":
    main()