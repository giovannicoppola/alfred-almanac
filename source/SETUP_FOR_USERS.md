# One-on-One Meeting Integration - Setup Guide

## For End Users

The one-on-one meeting integration is **completely optional** and **automatically disabled** if not configured. The workflow will continue to work normally without it.

### Minimum Required Configuration

To enable the feature, users only need to set **ONE** workflow variable:

**`PEOPLE_FOLDER`** = Path to your Obsidian people notes folder

That's it! Everything else has sensible defaults.

### Quick Start (3 minutes)

1. **In Alfred Preferences:**
   - Open Workflows → alfred-almanac
   - Click **[x] Configure Workflow** (top right)
   - Set **PEOPLE_FOLDER** to your people folder path
   - Click **Save**

2. **Tag a few person notes:**
   ```yaml
   ---
   tags: [one-on-one]
   ---
   ```

3. **Add discussion items:**
   ```markdown
   # Active Items
   - [ ] Topic to discuss
   - [ ] Follow-up item
   ```

Done! The next time you have a one-on-one meeting, the items will appear.

### Optional Customization

Most users won't need to change these:

- **`DISCUSS_SECTION`** (default: `# Active Items`)
  - Only change if your notes use a different header like `## To Discuss` or `# Agenda`

- **`ONE_ON_ONE_TAG`** (default: `one-on-one`)
  - Only change if you prefer a different tag like `meetings` or `1on1`

### What Happens If Not Configured?

**Nothing breaks!** The feature simply doesn't activate:
- Calendar events still appear in daily agenda ✓
- Meeting times and attendees still show ✓
- "To discuss" items are not fetched (feature disabled)
- No errors or warnings

### Universal Design Features

✅ **Path-agnostic**: Works with any Obsidian vault structure
✅ **Tag-agnostic**: Users can customize tag names
✅ **Section-agnostic**: Users can customize section headers  
✅ **Name-matching**: Flexible matching handles various name formats
✅ **Format-agnostic**: Supports multiple frontmatter tag formats
✅ **Graceful fallback**: Missing notes or tags are silently skipped
✅ **No hardcoded paths**: Everything configured via workflow variables

### Supported Tag Formats

The workflow recognizes all standard YAML frontmatter tag formats:

```yaml
# Array (recommended)
tags: [one-on-one]
tags: [meetings, one-on-one, work]

# List
tags:
  - one-on-one
  - meetings

# Inline
tags: one-on-one, meetings
```

### Name Matching Examples

The workflow handles real-world naming variations:

| Calendar Name | Matches Note |
|---------------|--------------|
| "Sarah Johnson" | `Sarah Johnson.md` ✓ (exact) |
| "Sarah Johnson" | `Sarah J.md` ✓ (partial) |
| "Sarah Johnson" | `S. Johnson.md` ✓ (partial) |
| "sarah johnson" | `Sarah Johnson.md` ✓ (case-insensitive) |
| "Dr. Sarah Johnson" | `Sarah Johnson.md` ✓ (contains) |

### Troubleshooting

**Items not appearing?**

1. Check `PEOPLE_FOLDER` is set correctly
2. Verify person note has `tags: [one-on-one]` in frontmatter
3. Confirm section header matches exactly: `# Active Items`
4. Make sure meeting has exactly 2 attendees
5. Check person note filename matches calendar name

**Still not working?**

Open Alfred Debugger (bug icon 🐛) and run the workflow to see detailed logs.

### For Developers / Contributors

See `fetchAgenda.py` functions:
- `_get_to_discuss_items()` - Main integration logic
- `_match_attendee_to_person_note()` - Name matching
- `_has_frontmatter_tag()` - Tag detection
- `_extract_section_from_file()` - Section extraction

Configuration variables are read from `config.py`.
