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
import math


from config import LOCATION, FORMATSTRING, SPECIAL_DAY, WEEKLY, LINEADAY_FILE, LINEADAY, VAULT_PATH, WEATHER_SOURCE, OPENWEATHER_KEY, TEMPERATURE_UNIT, WEEKLY_PLAN_FORMAT
FORMATSTRING = FORMATSTRING+"--%Z--" #adding local timezone
#FORMATSTRING = f'"{FORMATSTRING}"'  #enclosing in quotes


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)

def get_weekly_plan_filename(today, previous_monday, following_friday, year_week):
    """Generate weekly plan filename based on the selected format"""
    
    # Format the dates as strings
    previous_monday_str = previous_monday.strftime('%Y-%m-%d')
    following_friday_str = following_friday.strftime('%Y-%m-%d')
    monday_short = previous_monday.strftime('%m-%d')
    friday_short = following_friday.strftime('%m-%d')
    monday_day = previous_monday.strftime('%d')
    friday_day = following_friday.strftime('%d')
    month_name = previous_monday.strftime('%B')
    month_short = previous_monday.strftime('%b')
    year = previous_monday.year
    
    format_type = WEEKLY_PLAN_FORMAT.lower()
    
    if format_type == 'format1':
        # Original format: Weekly plan (31) 2025-07-28 to 2025-08-01
        return f"Weekly plan ({year_week}) {previous_monday_str} to {following_friday_str}"
    elif format_type == 'format2':
        # Week 31 - July 28-August 1, 2025
        return f"Week {year_week} - {month_name} {monday_day}-{following_friday.strftime('%B')} {friday_day}, {year}"
    elif format_type == 'format3':
        # W31 2025-07-28 to 2025-08-01
        return f"W{year_week} {previous_monday_str} to {following_friday_str}"
    elif format_type == 'format4':
        # Weekly Plan Week 31 (Jul 28 - Aug 1)
        return f"Weekly Plan Week {year_week} ({month_short} {monday_day} - {following_friday.strftime('%b')} {friday_day})"
    elif format_type == 'format5':
        # 2025 Week 31 (28-01 Jul-Aug)
        return f"{year} Week {year_week} ({monday_day}-{friday_day} {month_short}-{following_friday.strftime('%b')})"
    elif format_type == 'format6':
        # Week 31 - 07-28 to 08-01
        return f"Week {year_week} - {monday_short} to {friday_short}"
    else:
        # Default to format1 if unknown format
        return f"Weekly plan ({year_week}) {previous_monday_str} to {following_friday_str}"

def createWeeklyPlan():
    # Get today's date
    today = datetime.today()
    
    # Calculate the previous Monday
    previous_monday = today - timedelta(days=today.weekday())
    
    # Calculate the following Friday
    following_friday = previous_monday + timedelta(days=4)
    
    # Get the ISO calendar week number
    year_week = date2.date.today().isocalendar()[1]
    
    # Generate filename based on selected format
    filename = get_weekly_plan_filename(today, previous_monday, following_friday, year_week)
    finalString = f"![[{filename}]]" 
    return finalString



def createNextWeeklyPlan(thisWeeksPlan):
    # Get today's date
    today = datetime.today()
    
    # Check if today is Friday (weekday() returns 4 for Friday)
    if today.weekday() == 4:
        # Calculate the next Monday
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        # Calculate the following Friday
        following_friday = next_monday + timedelta(days=4)
        
        # Get the ISO calendar week number for the next Monday
        year_week = next_monday.isocalendar()[1]
        
        # Generate filename based on selected format
        filename = get_weekly_plan_filename(next_monday, next_monday, following_friday, year_week)
        finalString = f"\n![[{filename}]]"

        FILE_PATH_NEXT = f"{VAULT_PATH}/{finalString[4:-2]}.md"
        FILE_PATH_THIS = f"{VAULT_PATH}/{thisWeeksPlan[4:-2]}.md"

        """Create a file if it does not exist."""
        if not os.path.exists(FILE_PATH_NEXT):
            with open(FILE_PATH_NEXT, 'w') as file:
                pass  # Just create the file

        """Append undone tasks from source_file to target_file."""
        undone_tasks = []
        
        # Read the source file and collect undone tasks
        with open(FILE_PATH_THIS, 'r') as src:
            for line in src:
                if line.startswith('- [ ]'):
                    undone_tasks.append(line)
        
        # Append the undone tasks to the target file
        with open(FILE_PATH_NEXT, 'a') as tgt:
            for task in undone_tasks:
                tgt.write(task)
        return finalString
    else:
        return ""

    
    
    
def get_weather(location):
    
    
    myURL= "http://wttr.in/"
    
    # Modify format string based on temperature unit preference
    format_string = FORMATSTRING
    if TEMPERATURE_UNIT.lower() == 'celsius':
        # Use metric units (Celsius)
        payload = {'format': format_string}
        payload_j = {'format': "j1"}
    else:
        # Default to Fahrenheit (imperial units)
        format_string = FORMATSTRING.replace('°C', '°F')
        # Add the 'u' parameter for imperial units (Fahrenheit)
        payload = {'format': format_string, 'u': ''}
        payload_j = {'format': "j1", 'u': ''}
    
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


def get_lunar_phase(julian_day):
    """Calculate lunar phase based on Julian day number"""
    # Moon phase calculation
    cycle = 29.53058868  # lunar cycle in days
    known_new_moon = 2451549.5  # Julian day of a known new moon (Jan 6, 2000)
    
    phase = ((julian_day - known_new_moon) % cycle) / cycle
    
    if phase < 0.0625 or phase >= 0.9375:
        return "🌑"  # New Moon
    elif phase < 0.1875:
        return "🌒"  # Waxing Crescent
    elif phase < 0.3125:
        return "🌓"  # First Quarter
    elif phase < 0.4375:
        return "🌔"  # Waxing Gibbous
    elif phase < 0.5625:
        return "🌕"  # Full Moon
    elif phase < 0.6875:
        return "🌖"  # Waning Gibbous
    elif phase < 0.8125:
        return "🌗"  # Last Quarter
    else:
        return "🌘"  # Waning Crescent


def julian_day(date):
    """Convert date to Julian day number"""
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    return date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def get_weather_openweather(location):
    """Get weather data from OpenWeatherMap API"""
    if not OPENWEATHER_KEY:
        return "OpenWeather API key not configured", "", ""
    
    location = location.strip()
    
    # Get current weather
    url = f"http://api.openweathermap.org/data/2.5/weather"
    
    # Set units based on temperature preference
    if TEMPERATURE_UNIT.lower() == 'celsius':
        units = 'metric'
    else:
        # Default to Fahrenheit (imperial units)
        units = 'imperial'
    
    params = {
        'q': location,
        'appid': OPENWEATHER_KEY,
        'units': units
    }
    
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract weather information
        city_name = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        description = data['weather'][0]['description'].title()
        
        # Format temperatures - API already returns in requested unit
        if TEMPERATURE_UNIT.lower() == 'celsius':
            temp_str = f"{round(temp)}°C"
            feels_like_str = f"{round(feels_like)}°C"
        else:
            # Default to Fahrenheit
            temp_str = f"{round(temp)}°F"
            feels_like_str = f"{round(feels_like)}°F"
        
        # Get timezone offset
        timezone_offset = data['timezone']
        
        # Calculate local time
        utc_time = datetime.utcnow()
        local_time = utc_time + timedelta(seconds=timezone_offset)
        local_time_str = local_time.strftime('%a %b %d %H:%M:%S %Y')
        
        # Get lunar phase
        jd = julian_day(local_time.date())
        lunar_phase = get_lunar_phase(jd)
        
        # Create timezone string (simplified)
        tz_hours = timezone_offset // 3600
        tz_sign = '+' if tz_hours >= 0 else '-'
        tz_string = f"UTC{tz_sign}{abs(tz_hours):02d}"
        
        # Format weather string similar to wttr.in
        weather_string = f"{city_name}, {country} – {description} {temp_str} (feels like {feels_like_str}) 💧{humidity}% {lunar_phase}"
        
        log(f"OpenWeather data: {weather_string}")
        
        return (weather_string, local_time_str, tz_string)
        
    except requests.exceptions.RequestException as e:
        log(f"Error fetching OpenWeather data: {e}")
        return f"Error fetching weather for {location}", "", ""
    except KeyError as e:
        log(f"Error parsing OpenWeather data: {e}")
        return f"Error parsing weather data for {location}", "", ""


def get_weather_data(location):
    """Get weather data from the configured source"""
    if WEATHER_SOURCE.lower() == 'openweather':
        return get_weather_openweather(location)
    else:
        return get_weather(location)




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
        nextWeeklyPlan = "\n" + createNextWeeklyPlan(weeklyPlan)
    else:
        weeklyPlan = ""
        nextWeeklyPlan = ""

    if LINEADAY == '1':
        previousLines = fetchLineADay(LINEADAY_FILE)
    else:
        previousLines = ""


    locations = mylocation.split(",")
    for loc in locations:
        myOutput,myLocalTime, myTimeZone= get_weather_data(loc)
        myFinalString = myOutput + " " + myLocalTime + myAlmanac + previousLines + weeklyPlan + nextWeeklyPlan
        myTZstring = f"Current date/time: {myLocalTime} ({myTimeZone})"
        
        # Set quicklook URL based on weather source
        if WEATHER_SOURCE.lower() == 'openweather':
            quicklook_url = f"https://openweathermap.org/city/{loc}"
            arg_url = f"https://openweathermap.org/city/{loc}"
        else:
            quicklook_url = f"https://wttr.in/{loc}"
            arg_url = f"http://wttr.in/{loc}"
        
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
                'quicklookurl': quicklook_url,
                'arg': (myFinalString + ";;;" + arg_url)
                    })    

    
    print (json.dumps(result))



# Run the main function
if __name__ == "__main__":
    main()