#!/usr/bin/env python3

## adding to obsidian daily note
# Friday, November 8, 2024


#import requests
import json
import os
import plistlib
import re
import subprocess
import sys
import time

from config import EMAILSTROM_SCRIPT, OBSIDIAN_AGENDA, OBSIDIAN_CREATE, OBSIDIAN_DAILY, VAULT_PATH
from fetchAgenda import fetch_today_agenda

myAlmanacString = sys.argv[1] if len(sys.argv) > 1 else ""


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)



def fetchDailyNoteName():
    return time.strftime(OBSIDIAN_DAILY or "%Y-%m-%d-%a", time.localtime())

def fetchEmailSummary():
    """Run the emailstrom script and return its summary title string.

    The script is an Alfred Script Filter living in the email-sweeper
    workflow, so it expects that workflow's variables (sprintDur,
    WatchFolder, alfred_workflow_bundleid). We reconstruct them from that
    workflow's info.plist defaults + prefs.plist overrides.
    """
    script_path = os.path.expanduser(EMAILSTROM_SCRIPT)
    if not script_path or not os.path.isfile(script_path):
        log("EMAILSTROM_SCRIPT not set or file missing, skipping email summary")
        return None

    script_dir = os.path.dirname(script_path)
    env = os.environ.copy()

    # Defaults from the email-sweeper workflow's user configuration
    info_path = os.path.join(script_dir, "info.plist")
    if os.path.isfile(info_path):
        with open(info_path, "rb") as f:
            info = plistlib.load(f)
        env["alfred_workflow_bundleid"] = info.get("bundleid", "")
        for item in info.get("userconfigurationconfig", []):
            var = item.get("variable")
            default = item.get("config", {}).get("default")
            if var and isinstance(default, str):
                env.setdefault(var, default)

    # Overrides the user actually saved
    prefs_path = os.path.join(script_dir, "prefs.plist")
    if os.path.isfile(prefs_path):
        with open(prefs_path, "rb") as f:
            prefs = plistlib.load(f)
        for key, value in prefs.items():
            if isinstance(value, str):
                env[key] = value

    try:
        result = subprocess.run(
            [script_path],
            capture_output=True,
            text=True,
            cwd=script_dir,
            env=env,
        )
    except Exception as e:
        log(f"Error running emailstrom script: {str(e)}")
        return None

    output = result.stdout.strip()
    if not output:
        log(f"emailstrom script returned no output (stderr: {result.stderr.strip()})")
        return None

    # The script emits Alfred JSON with trailing commas, which strict JSON
    # rejects; strip them before parsing.
    cleaned = re.sub(r",(\s*[}\]])", r"\1", output)
    try:
        data = json.loads(cleaned)
        item = data["items"][0]
        title = item["title"]
    except (ValueError, KeyError, IndexError) as e:
        log(f"Could not parse emailstrom output: {str(e)}")
        return None

    # Color the callout by email count: green < 50, orange 50-200, red > 200
    try:
        count = int(item.get("arg", 0))
    except (TypeError, ValueError):
        count = 0

    if count < 50:
        callout_type = "success"
    elif count <= 200:
        callout_type = "question"
    elif count <= 500:
        callout_type = "warning"
    else:
        callout_type = "danger"

    # Split at the mailbox emoji: email count on line 1, sprints on line 2
    if "📬" in title:
        first, second = title.split("📬", 1)
        return f"> [!{callout_type}] {first.strip()} 📬\n> {second.strip()}"
    return f"> [!{callout_type}] {title}"


def main():
    if not VAULT_PATH:
        log("OBSIDIAN_VAULT is not set, skipping daily note append")
        return

    daily_note_path = os.path.join(VAULT_PATH, f"{fetchDailyNoteName()}.md")
    if not os.path.isfile(daily_note_path):
        if OBSIDIAN_CREATE != "1":
            log(f"Daily note not found: {daily_note_path}")
            return
        parent = os.path.dirname(daily_note_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        log(f"Creating daily note: {daily_note_path}")

    # First, append the original content (one-line-a-day, weekly agenda, etc.)
    with open(daily_note_path, "a") as file:
        file.write(f"{myAlmanacString}")
    
    # Append the email summary if the emailstrom script is configured
    email_summary = fetchEmailSummary()
    if email_summary:
        with open(daily_note_path, "a") as file:
            file.write(f"\n\n{email_summary}")
        log("Successfully appended email summary to daily note")

    # Check if OBSIDIAN_AGENDA is set to "1" (checked in Alfred)
    if OBSIDIAN_AGENDA == "1":
        log("OBSIDIAN_AGENDA = '1'")
        try:
            # Fetch today's agenda
            agenda_markdown = fetch_today_agenda()

            # Append the agenda to the daily note with 2 blank lines before it
            with open(daily_note_path, "a") as file:
                file.write(f"\n\n{agenda_markdown}")

            log("Successfully appended today's agenda to daily note")

        except Exception as e:
            log(f"Error fetching or appending agenda: {str(e)}")
    else:
        log("OBSIDIAN_AGENDA <> '1', skipping agenda fetch")




# Run the main function
if __name__ == "__main__":
    main()
