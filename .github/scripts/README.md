# Checklist Generation Scripts

This directory contains scripts for automatically generating interactive checklists from HOI4 strategy guides.

## How it Works

The `generate_checklist.py` script:

1. **Scans** all `.md` files in the repository
2. **Parses** the structured content of HOI4 strategy guides
3. **Extracts** actionable items from each section:
   - National Focus Timeline
   - Government & Law Timeline
   - Research Timeline
   - Construction & Rail
   - Factory-Swap Ladder
   - Division Templates & Recruit Plan
   - Equipment Designs
   - Air & Navy Snapshot
   - Garrison & Occupation Laws
   - Spy Missions
   - War Playbook
   - Final Logistics Check

4. **Generates** a separate interactive checklist file in the `checklists/` folder
5. **Creates** standalone checklist files that link back to the main guide

## Manual Usage

You can run the script manually:

```bash
python .github/scripts/generate_checklist.py
```

## Automatic Usage

The GitHub Action (`.github/workflows/generate-checklist.yml`) automatically runs this script when:

- Any `.md` file is pushed to the repository
- A pull request modifies `.md` files
- Manually triggered via GitHub Actions

## Guide Format Requirements

For the script to work, your guides must follow this structure:

- Section headers: `## 1 · National‑focus timeline`
- Tables with dates and actions
- Bullet points with `**bold dates**` or actions
- Consistent formatting across guides

## Generated Checklist Format

The script creates separate checklist files in the `checklists/` folder with:
- **Standalone files**: `checklists/[guide-name]-checklist.md`
- **Interactive checkboxes**: `- [ ] **Work with the Nationalists** (04 Feb 36)`
- **Detailed actions**: `- [ ] **Oct 36** (7 mils): Add **Art I ×2** lines, Cut −1 Inf & −1 Support`
- **Links back to main guide** for detailed explanations
- **Usage tips** for gameplay tracking

## File Structure

```
your-repo/
├── fascist-argentina.md          # Main strategy guide
├── checklists/
│   └── fascist-argentina-checklist.md  # Auto-generated checklist
└── .github/
    ├── workflows/
    │   └── generate-checklist.yml      # GitHub Action
    └── scripts/
        └── generate_checklist.py       # Python script
```

## Example Output

When you add `new-guide.md`, the script automatically creates:
- `checklists/new-guide-checklist.md` 
- Links from main guide to checklist
- Interactive checkboxes for all actionable items
- Usage tips and navigation aids
