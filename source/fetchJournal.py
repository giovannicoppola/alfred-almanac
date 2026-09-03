#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build and query a fast index of "journal" notes in an Obsidian vault.

Database format (JSON):
{
  "YYYY-MM-DD": "relative/path/to/note/without_extension",
  ...
}
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, List, Optional, Tuple


def log(s: str, *args) -> None:
    if args:
        s = s % args
    print(s, file=sys.stderr)


DATE_RE = re.compile(r"(?P<date>\d{4}[-._]\d{2}[-._]\d{2})")

# In-body journal entry header, e.g. "Monday July 9, 2018, 6:06 PM".
_WEEKDAY = r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
_MONTH = (
    r"(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)"
)
_ENTRY_HEADER_RE = re.compile(
    rf"(?mi)^#*\s*{_WEEKDAY},?\s+(?P<mon>{_MONTH})\s+(?P<day>\d{{1,2}}),\s+(?P<year>\d{{4}})"
)


def _read_frontmatter_and_body(file_path: str) -> Tuple[Optional[str], str]:
    """Return (YAML frontmatter text without --- lines, body text). ('', ...)
    frontmatter is None when the file has no frontmatter."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            first = f.readline()
            if not first.startswith("---"):
                return None, ""

            lines: List[str] = []
            for line in f:
                if line.startswith("---"):
                    break
                lines.append(line)
            return "".join(lines), f.read()
    except (OSError, UnicodeDecodeError):
        return None, ""


def _distinct_entry_dates(body: str) -> int:
    """Count distinct dated entry headers in the body. Used to detect
    'aggregate' notes (a single file holding several dated journal entries),
    which are de-prioritized so split-out single notes win a date collision."""
    dates = set()
    for m in _ENTRY_HEADER_RE.finditer(body):
        dates.add((m.group("mon").lower(), m.group("day"), m.group("year")))
    return len(dates)


def _frontmatter_has_journal_tag(frontmatter: str) -> bool:
    """
    Lightweight 'journal' tag detector supporting common Obsidian YAML patterns:
    - tags: [journal, foo]
    - tags:
      - journal
      - foo
    """
    # Normalize to simplify matching
    fm = frontmatter.lower()

    # Fast path: no tags field at all
    if "tags" not in fm:
        return False

    # Look for the 'tags:' block/line and see if 'journal' appears on that line or list items below it.
    # This is intentionally permissive but still scoped to the YAML section.
    if re.search(r"(?m)^\s*tags\s*:\s*\[.*\bjournal\b.*\]\s*$", fm):
        return True

    # Multi-line list under tags:
    # tags:
    #   - journal
    if re.search(r"(?ms)^\s*tags\s*:\s*\n(?:\s*-\s*.*\n)*\s*-\s*journal\b", fm):
        return True

    # Some people use "tag:" or embed "journal" in tags line without list brackets; be conservative:
    if re.search(r"(?m)^\s*tags\s*:\s*.*\bjournal\b", fm):
        return True

    return False


def _extract_date_key(file_path: str, frontmatter: Optional[str]) -> Optional[str]:
    """
    Determine the note's date key (YYYY-MM-DD).
    Preference order:
    1) YAML date-like fields ('date', 'created', 'day') if they start with YYYY-MM-DD
    2) First date-like token in filename (YYYY-MM-DD / YYYY.MM.DD / YYYY_MM_DD)
    """
    if frontmatter:
        # Support your vault's common pattern:
        # created: 2019-11-29T18:47:00
        # plus variants like:
        # date: "2019-11-29"
        # day: 2019-11-29 18:47
        m = re.search(
            r"(?mi)^\s*(date|created|day)\s*:\s*['\"]?(\d{4}-\d{2}-\d{2})",
            frontmatter,
        )
        if m:
            return m.group(2)

    base = os.path.basename(file_path)
    m2 = DATE_RE.search(base)
    if m2:
        return m2.group("date").replace(".", "-").replace("_", "-")

    return None


def _walk_markdown_files(vault_root: str) -> Iterable[str]:
    for root, dirs, files in os.walk(vault_root):
        # Skip common noisy folders
        dirs[:] = [d for d in dirs if d not in {".git", ".obsidian", ".trash", ".Trash"}]
        for name in files:
            if name.lower().endswith(".md"):
                yield os.path.join(root, name)


def _default_vault_root() -> str:
    # Prefer an explicit env override, then the almanac's configured notes folder.
    env = os.getenv("GIOVAULT_PATH") or os.getenv("GIOVAULT")
    if env:
        return os.path.expanduser(env)
    try:
        from config import NOTES_FOLDER  # type: ignore

        if NOTES_FOLDER:
            return os.path.expanduser(NOTES_FOLDER)
    except Exception:
        pass
    return os.path.expanduser("~/GioVault")


def _data_dir() -> str:
    """Alfred workflow data folder (outside the repo) — where the DB lives so it is
    never committed. Falls back to the script folder only if run outside Alfred."""
    d = os.getenv("alfred_workflow_data") or os.path.dirname(__file__)
    os.makedirs(d, exist_ok=True)
    return d


def _default_db_path() -> str:
    return os.path.join(_data_dir(), "journal_db.json")


def _default_report_path() -> str:
    return os.path.join(_data_dir(), "journal_db_report.md")


def ensure_database(vault_root: Optional[str] = None, db_path: Optional[str] = None,
                    max_age_hours: float = 12.0) -> str:
    """Build the journal DB on launch if it is missing or older than max_age_hours.
    Returns the DB path. Never raises — a build failure just leaves any existing DB."""
    if db_path is None:
        db_path = _default_db_path()
    db_path = os.path.abspath(os.path.expanduser(db_path))
    if vault_root is None:
        vault_root = _default_vault_root()

    fresh = False
    if os.path.exists(db_path):
        age_hours = (datetime.now().timestamp() - os.path.getmtime(db_path)) / 3600.0
        fresh = age_hours < max_age_hours
    if not fresh:
        try:
            db, _stats = build_database(vault_root)
            save_database(db, db_path)
        except Exception as e:
            log("Journal DB build on launch failed (%s): %s", vault_root, str(e))
    return db_path


@dataclass(frozen=True)
class BuildStats:
    vault_root: str
    scanned_markdown_files: int
    had_frontmatter: int
    tagged_journal: int
    missing_date_key: int
    duplicates: int
    indexed: int
    indexed_by_year: Dict[int, int]


def build_database(vault_root: str) -> Tuple[Dict[str, str], BuildStats]:
    """
    Build a date -> relative_path_without_ext index for notes tagged 'journal'.
    """
    vault_root = os.path.abspath(os.path.expanduser(vault_root))
    if not os.path.isdir(vault_root):
        raise FileNotFoundError(f"Vault root does not exist or is not a directory: {vault_root}")
    db: Dict[str, str] = {}
    # Track whether the file currently holding each date key is an "aggregate"
    # (multi-entry) note, so a single-entry note can take precedence.
    db_is_aggregate: Dict[str, bool] = {}
    duplicates: List[Tuple[str, str, str]] = []

    scanned_markdown_files = 0
    had_frontmatter = 0
    tagged_journal = 0
    missing_date_key = 0

    for file_path in _walk_markdown_files(vault_root):
        scanned_markdown_files += 1
        fm, body = _read_frontmatter_and_body(file_path)
        if not fm:
            continue
        had_frontmatter += 1
        if not _frontmatter_has_journal_tag(fm):
            continue
        tagged_journal += 1

        date_key = _extract_date_key(file_path, fm)
        if not date_key:
            missing_date_key += 1
            continue

        rel = os.path.relpath(file_path, vault_root)
        rel_no_ext = os.path.splitext(rel)[0].replace(os.sep, "/")
        is_aggregate = _distinct_entry_dates(body) >= 2

        if date_key in db and db[date_key] != rel_no_ext:
            duplicates.append((date_key, db[date_key], rel_no_ext))
            # Prefer a single-entry note over an aggregate on a date collision.
            if db_is_aggregate.get(date_key, False) and not is_aggregate:
                db[date_key] = rel_no_ext
                db_is_aggregate[date_key] = is_aggregate
            continue

        db[date_key] = rel_no_ext
        db_is_aggregate[date_key] = is_aggregate

    indexed_by_year: Dict[int, int] = {}
    for date_key in db.keys():
        try:
            y = int(date_key[0:4])
        except Exception:
            continue
        indexed_by_year[y] = indexed_by_year.get(y, 0) + 1

    stats = BuildStats(
        vault_root=vault_root,
        scanned_markdown_files=scanned_markdown_files,
        had_frontmatter=had_frontmatter,
        tagged_journal=tagged_journal,
        missing_date_key=missing_date_key,
        duplicates=len(duplicates),
        indexed=len(db),
        indexed_by_year=dict(sorted(indexed_by_year.items(), key=lambda kv: kv[0], reverse=True)),
    )

    if duplicates:
        log("Journal DB: %d duplicate date keys encountered (keeping first).", stats.duplicates)

    return db, stats


def save_database(db: Dict[str, str], out_path: str) -> None:
    out_path = os.path.abspath(os.path.expanduser(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_database(db_path: str) -> Dict[str, str]:
    db_path = os.path.abspath(os.path.expanduser(db_path))
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("Journal DB is not a JSON object.")
    # Normalize to str->str
    out: Dict[str, str] = {}
    for k, v in data.items():
        if isinstance(k, str) and isinstance(v, str):
            out[k] = v
    return out


@dataclass(frozen=True)
class JournalPick:
    year: int
    date_key: str
    rel_path_no_ext: str


def _safe_target_date_for_year(today: date, year: int) -> date:
    last_day = calendar.monthrange(year, today.month)[1]
    return date(year, today.month, min(today.day, last_day))


def pick_journals_for_month(today: date, db: Dict[str, str]) -> List[JournalPick]:
    """
    For each previous year, pick at most one journal entry:
    - must be within today's calendar month
    - closest to today's day within that month (ties -> earlier date)
    """
    candidates_by_year: Dict[int, List[Tuple[date, str, str]]] = {}

    for date_key, rel_path in db.items():
        try:
            d = datetime.strptime(date_key, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d.month != today.month:
            continue
        if d.year >= today.year:
            continue
        candidates_by_year.setdefault(d.year, []).append((d, date_key, rel_path))

    picks: List[JournalPick] = []
    for year, items in candidates_by_year.items():
        target = _safe_target_date_for_year(today, year)

        # Choose closest within the month; if tied, prefer earlier date.
        best = min(
            items,
            key=lambda t: (abs((t[0] - target).days), t[0]),
        )
        picks.append(JournalPick(year=year, date_key=best[1], rel_path_no_ext=best[2]))

    # Most recent years first
    picks.sort(key=lambda p: p.year, reverse=True)
    return picks


def format_journal_lines(picks: List[JournalPick]) -> List[str]:
    """
    Output lines in the requested format:
    - **year**: ![[completePath|notetitle]]
    """
    out: List[str] = []
    for p in picks:
        note_title = os.path.basename(p.rel_path_no_ext)
        out.append(f"- **{p.year}**: ![[{p.rel_path_no_ext}|{note_title}]]")
    return out


def get_journal_lines_for_today(db_path: Optional[str] = None, today: Optional[date] = None) -> List[str]:
    if today is None:
        today = datetime.now().date()
    if db_path is None:
        db_path = _default_db_path()
    try:
        db = load_database(db_path)
    except FileNotFoundError:
        log("Journal DB not found at %s (run fetchJournal.py -database first).", db_path)
        return []
    except Exception as e:
        log("Failed to load journal DB (%s): %s", db_path, str(e))
        return []

    picks = pick_journals_for_month(today, db)
    return format_journal_lines(picks)


def write_report(stats: BuildStats, out_path: str) -> None:
    out_path = os.path.abspath(os.path.expanduser(out_path))
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines: List[str] = []
    lines.append("# Journal database report")
    lines.append("")
    lines.append(f"- **Generated**: {generated_at}")
    lines.append(f"- **Vault root**: `{stats.vault_root}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Markdown files scanned**: {stats.scanned_markdown_files}")
    lines.append(f"- **Files with YAML frontmatter**: {stats.had_frontmatter}")
    lines.append(f"- **Files with `journal` tag in YAML**: {stats.tagged_journal}")
    lines.append(f"- **Journal files missing a date key**: {stats.missing_date_key}")
    lines.append(f"- **Duplicate date keys skipped**: {stats.duplicates}")
    lines.append(f"- **Indexed journal notes**: {stats.indexed}")
    lines.append("")
    lines.append("## Indexed notes by year")
    lines.append("")

    if stats.indexed_by_year:
        lines.append("| Year | Count |")
        lines.append("| ---: | ----: |")
        for year, count in stats.indexed_by_year.items():
            lines.append(f"| {year} | {count} |")
        lines.append("")
    else:
        lines.append("_No indexed notes._")
        lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-database",
        action="store_true",
        help="Create/update the journal JSON database",
    )
    parser.add_argument(
        "--vault",
        default=_default_vault_root(),
        help="Vault root to scan (defaults to GIOVAULT_PATH/GIOVAULT or OBSIDIAN_VAULT-derived)",
    )
    parser.add_argument(
        "--out",
        default=_default_db_path(),
        help="Where to write the JSON database (default: workflow folder)",
    )
    parser.add_argument(
        "--report",
        default=_default_report_path(),
        help="Where to write the Markdown build report (default: workflow folder)",
    )
    args = parser.parse_args()

    if args.database:
        vault_root = os.path.abspath(os.path.expanduser(args.vault))
        out_path = os.path.abspath(os.path.expanduser(args.out))
        report_path = os.path.abspath(os.path.expanduser(args.report))
        log("Building journal DB from: %s", vault_root)
        try:
            db, stats = build_database(vault_root)
            save_database(db, out_path)
            log("Wrote %d journal entries to: %s", len(db), out_path)
            write_report(stats, report_path)
            log("Wrote report to: %s", report_path)
            return
        except Exception as e:
            log("Failed to build journal DB: %s", str(e))
            raise SystemExit(2)

    # Default action: print today's journal lines using the DB.
    for line in get_journal_lines_for_today():
        print(line)


if __name__ == "__main__":
    main()

