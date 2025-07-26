# HOI4 Strategy Guide Automation Workflow

## Overview

This repository now has an automated workflow to convert JSON strategy guides into both Markdown guides and actionable checklists with cross-linking between them.

## Directory Structure

```
/data/          # Input JSON files
/guides/        # Generated Markdown strategy guides
/checklists/    # Generated actionable checklists
/.github/
  /scripts/     # Conversion scripts
  /workflows/   # GitHub Actions automation
```

## How It Works

### 1. JSON Input
Place your HOI4 strategy guide JSON files in the `/data/` directory. The JSON should follow the established schema with:
- `meta` object containing title, tiers, patch, and DLC info
- `sections` array with structured guide content

### 2. Automated Conversion
When you commit changes to files in the `/data/` directory, GitHub Actions automatically:
- Cleans JSON files of problematic Unicode characters (em dashes, special quotes, etc.)
- Converts JSON files to readable Markdown guides in `/guides/`
- Creates actionable checklists in `/checklists/`
- Cross-links guides and checklists to each other
- Commits and pushes the generated files back to the repository

### 3. Manual Conversion
You can also run the scripts manually:

```bash
# Clean JSON files of bad characters
python .github/scripts/fix_json_characters.py --data-dir

# Generate Markdown guides
python .github/scripts/json_to_markdown.py

# Generate checklists
python .github/scripts/json_to_checklist.py
```

## Features

### Character Cleaning
- Automatically fixes problematic Unicode characters in JSON files
- Converts em dashes (—), en dashes (–) to standard hyphens (-)
- Replaces special quotes, mathematical symbols, and other Unicode with ASCII equivalents
- Ensures JSON files are properly formatted and parseable

### Cross-Linking
- Guides include a link to their corresponding checklist
- Checklists include a link back to the full strategy guide

### Special Handling
- **Air & Navy sections**: Automatically split into separate Air Plan and Navy Plan subsections
- **Factory-swap sections**: Special handling in checklists with notes below tables
- **Tier-based organization**: Color-coded tier system throughout

### File Naming
- Input: `filename.json` in `/data/`
- Output: `filename.md` in `/guides/` and `filename-checklist.md` in `/checklists/`

## Example Workflow

1. Create `my_strategy.json` in `/data/`
2. Commit and push changes
3. GitHub Actions automatically:
   - Cleans the JSON file of problematic Unicode characters
   - Generates `/guides/my_strategy.md` (full strategy guide)
   - Creates `/checklists/my_strategy-checklist.md` (actionable checklist)
   - Cross-links both files to each other
   - Commits and pushes all generated files back to the repository

## Scripts

- **fix_json_characters.py**: Cleans problematic Unicode characters from JSON files
- **json_to_markdown.py**: Converts JSON to readable Markdown guides
- **json_to_checklist.py**: Converts JSON to actionable checklists
- **convert-json-guides.yml**: GitHub Actions workflow for automation

This automated system ensures consistency, reduces manual work, and maintains proper cross-referencing between strategy guides and their checklists.
