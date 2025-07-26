# HOI4 Strategy Guide Scripts

This directory contains the automation scripts that power the HOI4 Strategy Guide workflow, converting JSON strategy guides into readable Markdown guides and actionable checklists.

## Scripts Overview

### 1. `fix_json_characters.py`
**Purpose**: Cleans problematic Unicode characters from JSON files before processing.

**Features**:
- Converts em dashes (—), en dashes (–) to standard hyphens (-)
- Replaces special quotes with standard ASCII quotes
- Fixes mathematical symbols (×, ≥, ≤, etc.) with ASCII equivalents
- Removes AI-generated content references and other problematic text
- Creates backups before modification (optional)
- Validates JSON after cleaning

**Usage**:
```bash
# Process all JSON files in data directory
python fix_json_characters.py --data-dir

# Process specific file
python fix_json_characters.py argentina_full.json

# Process without creating backups
python fix_json_characters.py --data-dir --no-backup
```

### 2. `json_to_markdown.py`
**Purpose**: Converts JSON strategy guides into readable Markdown format.

**Features**:
- Extracts metadata (title, tiers, patch info)
- Converts structured tables into Markdown format
- Special handling for Air & Navy sections (split into subsections)
- Cross-links to corresponding checklists
- Tier-based organization and formatting
- Processes entire `/data` directory automatically

**Key Sections Handled**:
- Day-One Snapshots
- National Focus timelines
- Government/Laws/MIOs & Theorists
- Research timelines
- Construction schedules
- Factory-swap ladders
- Army grouping & commands
- Division templates & recruitment
- Equipment designs
- Air & Navy plans
- Garrisons & occupation laws
- Spy missions
- War playbooks
- Special projects

### 3. `json_to_checklist.py`
**Purpose**: Creates actionable checklists from JSON strategy guides.

**Features**:
- Generates interactive checkboxes for all actionable items
- Special handling for factory-swap sections with notes
- Cross-links back to full strategy guides
- Simplified formatting optimized for gameplay tracking
- Contextual grouping of related tasks
- Smart date and action extraction

**Special Handling**:
- **Factory-swap sections**: Notes placed below tables, simplified timeline
- **Complex tables**: Checkbox format with key information
- **Cross-referencing**: Links between guides and checklists

## Workflow Integration

These scripts work together in the automated GitHub Actions workflow:

1. **Character Cleaning**: `fix_json_characters.py` cleans all JSON files
2. **Guide Generation**: `json_to_markdown.py` creates readable strategy guides
3. **Checklist Creation**: `json_to_checklist.py` generates actionable checklists
4. **Auto-commit**: Results are automatically committed back to the repository

## Directory Structure

```
/data/                          # Input JSON files
├── argentina_full.json         # Strategy guide data
└── ...

/guides/                        # Generated Markdown guides
├── argentina_full.md           # Readable strategy guide
└── ...

/checklists/                    # Generated checklists
├── argentina_full-checklist.md # Actionable checklist
└── ...

/.github/
├── scripts/                    # Automation scripts
│   ├── fix_json_characters.py  # JSON cleaning
│   ├── json_to_markdown.py     # Guide generation
│   └── json_to_checklist.py    # Checklist creation
└── workflows/
    └── convert-json-guides.yml # GitHub Actions workflow
```

## JSON Format Requirements

Input JSON files should follow this structure:

```json
{
  "meta": {
    "title": "Strategy Guide Title",
    "tiers": {
      "1": "First Tier Description",
      "2": "Second Tier Description"
    },
    "patch": "1.17",
    "dlc": "All"
  },
  "sections": [
    {
      "id": 0,
      "name": "Section Name",
      "notes": ["Optional notes"],
      "columns": ["col1", "col2"],
      "rows": [["data1", "data2"]]
    }
  ]
}
```

### Special Section Types

- **Air & Navy sections**: Include both `air` and `navy` objects with separate tables
- **Factory-swap sections**: Include `notes` array for important timing information
- **Special Projects**: Include `used`, `project`, and project-specific columns

## Manual Usage

Run scripts individually for testing or manual processing:

```bash
# Clean JSON files
python .github/scripts/fix_json_characters.py --data-dir

# Generate guides
python .github/scripts/json_to_markdown.py

# Generate checklists  
python .github/scripts/json_to_checklist.py
```

## Automated Usage

The GitHub Actions workflow (`.github/workflows/convert-json-guides.yml`) automatically:

- Triggers on changes to `/data/*.json` files
- Runs all three scripts in sequence
- Commits generated files back to `/guides/` and `/checklists/`
- Can be manually triggered via GitHub Actions interface

## Output Examples

**Generated Guide** (`/guides/argentina_full.md`):
- Clean, readable Markdown with proper formatting
- Cross-linked to corresponding checklist
- Tier information and metadata
- Properly formatted tables and sections

**Generated Checklist** (`/checklists/argentina_full-checklist.md`):
- Interactive checkboxes for tracking progress
- Simplified, action-oriented format
- Cross-linked back to full strategy guide
- Optimized for in-game use

This system ensures consistency, reduces manual work, and maintains proper cross-referencing between all generated content.
