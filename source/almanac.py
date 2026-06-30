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


from config import LOCATION, FORMATSTRING, SPECIAL_DAY, WEATHER_SOURCE, OPENWEATHER_KEY, TEMPERATURE_UNIT

FORMATSTRING = FORMATSTRING+"--%Z--" #adding local timezone
#FORMATSTRING = f'"{FORMATSTRING}"'  #enclosing in quotes


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)



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


def julian_day(date):
    """Convert date to Julian day number"""
    a = (14 - date.month) // 12
    y = date.year + 4800 - a
    m = date.month + 12 * a - 3
    return date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


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

myAlmanac,myIcon = almanac()

locations = mylocation.split(",")
for loc in locations:
    myOutput,myLocalTime, myTimeZone= get_weather_data(loc)
    myFinalString = myOutput + " " + myLocalTime + myAlmanac
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

