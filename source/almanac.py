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
from urllib.parse import quote


from config import LOCATION, FORMATSTRING, SPECIAL_DAY, WEATHER_SOURCE, OPENWEATHER_KEY, TEMPERATURE_UNIT, WEEKLY, NOTES_FOLDER, WEEKLY_PLAN_FORMAT, LINK_STYLE, AGENDA, LINEADAY, LINEADAY_FILE, JOURNAL

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

    page_url = f"https://wttr.in/{location}"
    return (myWeatherString, myLocalTime, myTimeZone, page_url)


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


def openweather_page_url(location, city_id=None):
    """Shift-enter / quicklook URL for OpenWeather.

    `/city/{id}` is the real city page. `/city/{name}` 404s, so fall back
    to the search page when the API did not return an id.
    """
    if city_id:
        return f"https://openweathermap.org/city/{city_id}"
    return f"https://openweathermap.org/find?q={quote(location)}"


def get_weather_openweather(location):
    """Get weather data from OpenWeatherMap API"""
    location = location.strip()
    find_url = openweather_page_url(location)

    if not OPENWEATHER_KEY:
        return "OpenWeather API key not configured", "", "", find_url

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

        page_url = openweather_page_url(location, data.get("id"))
        return (weather_string, local_time_str, tz_string, page_url)

    except requests.exceptions.RequestException as e:
        log(f"Error fetching OpenWeather data: {e}")
        return f"Error fetching weather for {location}", "", "", find_url
    except KeyError as e:
        log(f"Error parsing OpenWeather data: {e}")
        return f"Error parsing weather data for {location}", "", "", find_url


def get_weather_data(location):
    """Get weather data from the configured source"""
    if WEATHER_SOURCE.lower() == 'openweather':
        return get_weather_openweather(location)
    else:
        return get_weather(location)


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


def format_plan_link(filename):
    """Render a link to a plan file according to the configured LINK_STYLE.

    wikilink -> ![[name]]   (Obsidian / Logseq embed)
    plain    -> name        (bare filename, no extension)
    markdown -> [name](name.md)   (standard Markdown, default)
    """
    style = LINK_STYLE.lower()
    if style == 'wikilink':
        return f"![[{filename}]]"
    elif style == 'plain':
        return filename
    else:
        return f"[{filename}]({filename}.md)"


def createWeeklyPlan():
    """Return the filename (no extension) of the current week's plan."""
    today = datetime.today()

    # Calculate the previous Monday
    previous_monday = today - timedelta(days=today.weekday())

    # Calculate the following Friday
    following_friday = previous_monday + timedelta(days=4)

    # Get the ISO calendar week number
    year_week = date2.date.today().isocalendar()[1]

    return get_weekly_plan_filename(today, previous_monday, following_friday, year_week)


def createNextWeeklyPlan(this_week_filename):
    """On Fridays, create next week's plan file and carry over unchecked
    tasks from this week. Returns next week's filename, or '' on other days."""
    today = datetime.today()

    # Only roll over on Friday (weekday() returns 4 for Friday)
    if today.weekday() != 4:
        return ""

    # Calculate next Monday and its following Friday
    next_monday = today + timedelta(days=(7 - today.weekday()))
    following_friday = next_monday + timedelta(days=4)
    year_week = next_monday.isocalendar()[1]

    next_week_filename = get_weekly_plan_filename(next_monday, next_monday, following_friday, year_week)

    file_path_next = f"{NOTES_FOLDER}/{next_week_filename}.md"
    file_path_this = f"{NOTES_FOLDER}/{this_week_filename}.md"
    carry_over_unchecked_tasks(file_path_this, file_path_next)

    return next_week_filename


def carry_over_unchecked_tasks(file_path_this, file_path_next):
    """Create next week's file if needed and append this week's unchecked
    tasks that are not already present, so a second Friday run does not
    duplicate them.
    """
    if not os.path.exists(file_path_next):
        with open(file_path_next, 'w') as dest:
            pass

    existing = set()
    with open(file_path_next, 'r') as dest:
        existing = {line.rstrip('\n') for line in dest}

    new_tasks = []
    if os.path.exists(file_path_this):
        with open(file_path_this, 'r') as src:
            for line in src:
                if not line.startswith('- [ ]'):
                    continue
                key = line.rstrip('\n')
                if key in existing:
                    continue
                new_tasks.append(line if line.endswith('\n') else line + '\n')
                existing.add(key)

    if new_tasks:
        with open(file_path_next, 'a') as tgt:
            tgt.writelines(new_tasks)


# Read a markdown file and return its lines (empty list if missing)
def read_markdown_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines


# Matches any YYYY-MM-DD date inside an entry
DATE_PATTERN = re.compile(r'\d{4}-\d{2}-\d{2}')


# Stamp the weekday onto the date: 2025-09-14 -> 2025-09-14-Sun
# But skip if weekday already follows the date in the original line
def add_weekday(line, date_str, date_obj):
    weekday = date_obj.strftime('%a')
    # Check if weekday already appears right after the date (e.g., "2024-09-18 Wed")
    if date_str + ' ' + weekday in line:
        return line  # Already present, don't add it
    return line.replace(date_str, date_str + '-' + weekday, 1)


# Extract (date, line) pairs from "- **...YYYY-MM-DD...** ..." entries
def extract_dates_and_lines(lines):
    date_lines = []
    for line in lines:
        if line.startswith('- **'):
            match = DATE_PATTERN.search(line)
            if not match:
                continue  # skip malformed entries
            date_str = match.group(0)
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                continue  # skip impossible dates (e.g. 2025-02-30)
            date_lines.append((date_obj, add_weekday(line.strip(), date_str, date_obj)))
    return date_lines


# Find the entry whose date is closest to target_date
def find_closest_dates(date_lines, target_date):
    return min(date_lines, key=lambda x: abs(x[0] - target_date))


def fetchLineADay(file_path):
    # Read the markdown file
    lines = read_markdown_file(file_path)

    # Extract dates and lines
    date_lines = extract_dates_and_lines(lines)

    # Nothing usable -> contribute nothing to the output
    if not date_lines:
        return ""

    # Calculate today's date
    today = datetime.now()

    # Determine the earliest entry to know how many years back we can go
    earliest_date = min(date_lines, key=lambda x: x[0])[0]
    date_range_years = (today - earliest_date).days / 365.25
    complete_years = int(date_range_years)

    # For each complete year ago, quote the entry closest to that day
    result_string = "\n\n📅 **One-line-a-days**\n"
    for year in range(1, complete_years + 1):
        target_date = today - timedelta(days=365 * year)
        closestLine = find_closest_dates(date_lines, target_date)
        result_string += "\t" + closestLine[1] + "\n"

    return result_string


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

# Optional "on this day" quotes from a line-a-day journal file
if LINEADAY == '1':
    previousLines = fetchLineADay(LINEADAY_FILE)
else:
    previousLines = ""

# Optional weekly plan + Friday task carryover
if WEEKLY == '1':
    this_week_filename = createWeeklyPlan()
    weeklyPlan = "\n" + format_plan_link(this_week_filename)
    next_week_filename = createNextWeeklyPlan(this_week_filename)
    nextWeeklyPlan = ("\n" + format_plan_link(next_week_filename)) if next_week_filename else ""
else:
    weeklyPlan = ""
    nextWeeklyPlan = ""

# Optional daily agenda from the calendar (opt-in; can be slow)
if AGENDA == '1':
    from fetchAgenda import fetch_today_agenda
    agendaString = "\n" + fetch_today_agenda()
else:
    agendaString = ""

# Optional "on this day" links from journal-tagged notes (opt-in).
# The index is (re)built on launch and stored in the Alfred workflow data folder,
# so it stays out of the repo and is never committed.
if JOURNAL == '1':
    from fetchJournal import ensure_database, get_journal_lines_for_today
    _db = ensure_database(NOTES_FOLDER)
    _journalLines = get_journal_lines_for_today(_db)
    journalString = ("\n\n📔 **On this day (journal)**\n" + "\n".join("\t" + l for l in _journalLines)) if _journalLines else ""
else:
    journalString = ""

locations = mylocation.split(",")
for loc in locations:
    myOutput, myLocalTime, myTimeZone, page_url = get_weather_data(loc)
    myFinalString = myOutput + " " + myLocalTime + myAlmanac + previousLines + weeklyPlan + nextWeeklyPlan + agendaString + journalString
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
            'quicklookurl': page_url,
            'arg': (myFinalString + ";;;" + page_url)
                })    

print (json.dumps(result))

