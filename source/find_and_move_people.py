#!/usr/bin/env python3
"""
Find person notes in vault root and move them to _People folder.
Then add the one-on-one tag to them.
"""

import os
import shutil
import re


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

    # List of missing people (excluding non-person entries)
    missing_people = [
        "Ann Ligocki",
        "Irina Marcovich",
        "Joshua Motelow",
        "Julie Horowitz",
        "Marisa Santella",
        "Michael Kessler",
        "Sarah Murphy",
        "Vassili Valayannopoulos",
    ]

    print(f"🔍 Searching for {len(missing_people)} missing person notes in vault root...\n")

    found_count = 0
    moved_count = 0
    tagged_count = 0
    not_found = []

    for person in missing_people:
        filename = f"{person}.md"
        source_path = os.path.join(vault_path, filename)
        dest_path = os.path.join(people_folder, filename)

        # Check if file exists in vault root
        if os.path.isfile(source_path):
            found_count += 1
            print(f"✓ Found: {person}")

            # Check if already in _People folder (shouldn't happen, but check anyway)
            if os.path.isfile(dest_path):
                print(f"  ⚠️  Already exists in _People folder, skipping move")
                # Still try to tag it
                if not has_frontmatter_tag(dest_path, tag):
                    if add_frontmatter_tag(dest_path, tag):
                        print(f"  ✅ Added '{tag}' tag")
                        tagged_count += 1
                else:
                    print(f"  ℹ️  Already has '{tag}' tag")
                continue

            # Move to _People folder
            try:
                shutil.move(source_path, dest_path)
                print(f"  📁 Moved to _People folder")
                moved_count += 1

                # Add tag
                if not has_frontmatter_tag(dest_path, tag):
                    if add_frontmatter_tag(dest_path, tag):
                        print(f"  ✅ Added '{tag}' tag")
                        tagged_count += 1
                else:
                    print(f"  ℹ️  Already has '{tag}' tag")

            except (IOError, OSError) as e:
                print(f"  ❌ Error moving file: {e}")

        else:
            not_found.append(person)

    print(f"\n{'='*60}")
    print(f"\n📊 Summary:")
    print(f"  • Found in vault root: {found_count}")
    print(f"  • Moved to _People: {moved_count}")
    print(f"  • Tags added: {tagged_count}")
    print(f"  • Still not found: {len(not_found)}")

    if not_found:
        print(f"\n⚠️  Still missing:")
        for person in not_found:
            print(f"     • {person}")

    print()


if __name__ == "__main__":
    main()
