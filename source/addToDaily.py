#!/usr/bin/env python3

## Append the almanac report to today's Obsidian daily note
# Friday, November 8, 2024

import os
import sys
import time

from config import OBSIDIAN_CREATE, OBSIDIAN_DAILY, VAULT_PATH

myAlmanacString = sys.argv[1] if len(sys.argv) > 1 else ""


def log(s, *args):
    if args:
        s = s % args
    print(s, file=sys.stderr)


def fetchDailyNoteName():
    return time.strftime(OBSIDIAN_DAILY or "%Y-%m-%d-%a", time.localtime())


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

    with open(daily_note_path, "a") as file:
        file.write(f"{myAlmanacString}")
    log(f"Appended almanac to {daily_note_path}")


if __name__ == "__main__":
    main()
