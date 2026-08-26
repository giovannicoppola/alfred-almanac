#!/usr/bin/env python3
"""
Identify people with one-on-one meetings from daily notes history.

Searches the last year of daily notes for "# Meeting with [[PersonName]]" entries
(from MDsuite ZM script) and adds the 'one-on-one' tag to those person notes.
"""

import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter


def find_daily_notes(vault_path, since_date):
    """Find all daily note files since a given date."""
    daily_notes = []

    for filename in os.listdir(vault_path):
        # Match YYYY-MM-DD format (with or without day suffix)
        match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        if match and filename.endswith('.md'):
            date_str = match.group(1)
            try:
                note_date = datetime.strptime(date_str, '%Y-%m-%d')
                if note_date >= since_date:
                    daily_notes.append(os.path.join(vault_path, filename))
            except ValueError:
                continue

    return sorted(daily_notes)


def extract_zm_meetings(note_path):
    """Extract person names from ZM script entries in a daily note.

    Looks for: # Meeting with [[PersonName]]
    """
    people = []

    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except (IOError, OSError):
        return people

    # Pattern: # Meeting with [[PersonName]]
    pattern = r'#\s+Meeting\s+with\s+\[\[([^\]]+)\]\]'
    matches = re.findall(pattern, content, re.IGNORECASE)

    return matches


def has_frontmatter_tag(note_path, tag):
    """Check if a person note already has a specific tag."""
    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, OSError):
        return False

    if not lines or lines[0].strip() != '---':
        return False

    # Find closing delimiter
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            frontmatter = lines[1:i]
            break
    else:
        return False

    # Check if tag exists
    tag = tag.lstrip('#')
    frontmatter_text = ' '.join(line.strip() for line in frontmatter)

    # Check various formats
    patterns = [
        rf'\btags:\s*\[.*\b{re.escape(tag)}\b.*\]',
        rf'\btags:\s+.*\b{re.escape(tag)}\b',
    ]

    for pattern in patterns:
        if re.search(pattern, frontmatter_text, re.IGNORECASE):
            return True

    # Check YAML list format
    in_tags = False
    for line in frontmatter:
        stripped = line.strip()
        if stripped.startswith('tags:'):
            in_tags = True
            rest = stripped[5:].strip()
            if rest and tag.lower() in rest.lower():
                return True
        elif in_tags:
            if stripped.startswith('-'):
                item = stripped[1:].strip()
                if item.lower() == tag.lower():
                    return True
            elif not stripped.startswith(' '):
                break

    return False


def add_frontmatter_tag(note_path, tag):
    """Add a tag to a person note's frontmatter."""
    tag = tag.lstrip('#')

    try:
        with open(note_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (IOError, OSError) as e:
        print(f"  ❌ Error reading {note_path}: {e}")
        return False

    # Check if frontmatter exists
    has_frontmatter = lines and lines[0].strip() == '---'

    if has_frontmatter:
        # Find closing delimiter
        closing_index = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                closing_index = i
                break

        if closing_index is None:
            print(f"  ⚠️  Malformed frontmatter in {note_path}")
            return False

        frontmatter = lines[1:closing_index]

        # Check if tags: exists
        tags_line_index = None
        for i, line in enumerate(frontmatter):
            if line.strip().startswith('tags:'):
                tags_line_index = i
                break

        if tags_line_index is not None:
            # Add to existing tags
            tags_line = frontmatter[tags_line_index].rstrip()

            # Check format
            if '[' in tags_line:
                # Array format: tags: [tag1, tag2]
                if tags_line.rstrip().endswith(']'):
                    new_line = tags_line[:-1] + f', {tag}]\n'
                else:
                    new_line = tags_line + f', {tag}]\n'
            else:
                # Could be tags: or tags: tag1
                rest = tags_line.split(':', 1)[1].strip()
                if rest:
                    # tags: tag1 -> tags: [tag1, newtag]
                    new_line = f'tags: [{rest}, {tag}]\n'
                else:
                    # tags: (empty) -> tags: [newtag]
                    new_line = f'tags: [{tag}]\n'

            frontmatter[tags_line_index] = new_line
        else:
            # No tags: line, add it
            frontmatter.insert(0, f'tags: [{tag}]\n')

        # Reconstruct file
        new_lines = ['---\n'] + frontmatter + ['---\n'] + lines[closing_index + 1:]

    else:
        # No frontmatter, create it
        new_lines = [
            '---\n',
            f'tags: [{tag}]\n',
            '---\n',
            '\n'
        ] + lines

    # Write back
    try:
        with open(note_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        return True
    except (IOError, OSError) as e:
        print(f"  ❌ Error writing {note_path}: {e}")
        return False


def main():
    vault_path = "/Users/giovanni.coppola/Library/CloudStorage/OneDrive-RegeneronPharmaceuticals,Inc/GiovanniNotes"
    people_folder = "/Users/giovanni.coppola/Library/CloudStorage/OneDrive-RegeneronPharmaceuticals,Inc/GiovanniNotes/_People"
    tag = "one-on-one"

    # Find daily notes from last year
    one_year_ago = datetime.now() - timedelta(days=365)
    print(f"📅 Searching daily notes since {one_year_ago.strftime('%Y-%m-%d')}...\n")

    daily_notes = find_daily_notes(vault_path, one_year_ago)
    print(f"Found {len(daily_notes)} daily notes\n")

    # Extract all people from ZM meetings
    all_people = []
    for note in daily_notes:
        people = extract_zm_meetings(note)
        all_people.extend(people)

    # Count occurrences
    people_counts = Counter(all_people)
    print(f"Found {len(people_counts)} unique people with ZM meetings:\n")

    for person, count in people_counts.most_common():
        print(f"  • {person}: {count} meeting(s)")

    print(f"\n{'='*60}\n")
    print(f"Adding '{tag}' tag to person notes...\n")

    # Process each person
    tagged_count = 0
    already_tagged = 0
    not_found = 0

    for person, count in sorted(people_counts.items()):
        # Find person note
        person_note = os.path.join(people_folder, f"{person}.md")

        if not os.path.isfile(person_note):
            print(f"⚠️  {person}: Note not found")
            not_found += 1
            continue

        # Check if already tagged
        if has_frontmatter_tag(person_note, tag):
            print(f"✓  {person}: Already has '{tag}' tag")
            already_tagged += 1
            continue

        # Add tag
        if add_frontmatter_tag(person_note, tag):
            print(f"✅ {person}: Added '{tag}' tag")
            tagged_count += 1
        else:
            print(f"❌ {person}: Failed to add tag")

    print(f"\n{'='*60}")
    print(f"\n📊 Summary:")
    print(f"  • Total people found: {len(people_counts)}")
    print(f"  • Tags added: {tagged_count}")
    print(f"  • Already tagged: {already_tagged}")
    print(f"  • Notes not found: {not_found}")
    print()


if __name__ == "__main__":
    main()
