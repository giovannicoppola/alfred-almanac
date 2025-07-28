# Weekly Plan Format Options

The `WEEKLY_PLAN_FORMAT` environment variable is now available as a dropdown menu in the Alfred workflow configuration.

## Available Formats

### format1 (Default)
**Value:** `format1`  
**Example:** `Weekly plan (31) 2025-07-28 to 2025-08-01`  
**Description:** Original format with week number in parentheses and full ISO dates

### format2
**Value:** `format2`  
**Example:** `Week 31 - July 28-August 1, 2025`  
**Description:** Readable format with full month names

### format3
**Value:** `format3`  
**Example:** `W31 2025-07-28 to 2025-08-01`  
**Description:** Compact format with W prefix for week number

### format4
**Value:** `format4`  
**Example:** `Weekly Plan Week 31 (Jul 28 - Aug 1)`  
**Description:** Professional format with abbreviated month names

### format5
**Value:** `format5`  
**Example:** `2025 Week 31 (28-01 Jul-Aug)`  
**Description:** Year-first format with day numbers and abbreviated months

### format6
**Value:** `format6`  
**Example:** `Week 31 - 07-28 to 08-01`  
**Description:** Compact format with MM-DD date format

## How to Set the Format

The format can now be selected from a dropdown menu in the Alfred workflow configuration:

1. Open Alfred Preferences
2. Go to Workflows
3. Select your Almanac workflow
4. Click the configuration button (gear icon) or environment variables section
5. Find "Weekly Plan Format" in the dropdown list
6. Select your preferred format from the available options

The dropdown shows example formats to help you choose the right one for your needs. If not set, it defaults to `format1` (the original format).

## Configuration Integration

The weekly plan format is now fully integrated into the Alfred workflow's user interface:
- **Dropdown menu**: Easy selection from predefined options
- **Example previews**: Each option shows what the filename will look like
- **Default value**: Set to `format1` for backward compatibility
- **Description**: Helpful text explaining the purpose of the setting

The weekly plan filenames will automatically use your selected format for both current and next week planning features.
