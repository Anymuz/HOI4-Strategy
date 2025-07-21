#!/usr/bin/env python3
"""
Generate interactive checklists for HOI4 strategy guides.
This script parses markdown files with a specific structure and creates
separate checklist files in the checklists/ folder.
"""

import re
import os
import glob
from typing import List, Dict, Tuple

def normalize_text(text: str) -> str:
    """Normalize text by replacing various Unicode spaces with regular spaces."""
    return re.sub(r'[\s\xa0\u202f\u2009\u200a]+', ' ', text).strip()

def extract_table_rows(content: str) -> List[Tuple[str, str, str, str]]:
    """Extract table rows with better Unicode handling."""
    rows = []
    lines = content.split('\n')
    
    for line in lines:
        if '|' in line and not line.strip().startswith('|--') and '---' not in line:
            # Split by | and clean up
            parts = [normalize_text(part) for part in line.split('|')]
            if len(parts) >= 3:  # Skip lines that don't have enough columns
                # Pad with empty strings if needed
                while len(parts) < 6:
                    parts.append("")
                
                col1, col2, col3, col4 = parts[1], parts[2], parts[3] if len(parts) > 3 else "", parts[4] if len(parts) > 4 else ""
                if col1 and col2 and 'Date' not in col1 and 'Finish date' not in col1 and 'Asset' not in col1:
                    rows.append((col1, col2, col3, col4))
    
    return rows

def extract_focus_timeline(content: str) -> List[str]:
    """Extract national focus timeline items."""
    items = []
    focus_section = re.search(r"## 1[\s\xa0]*[·•‑-][\s\xa0]*[Nn]ational[‑-]*focus[\s\xa0]*timeline(.+?)(?=## 2|$)", content, re.DOTALL | re.IGNORECASE)
    
    if focus_section:
        section_content = focus_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            date, focus = row[0], row[1]
            if date and focus:
                # Mark important focuses in bold
                if focus.startswith('**') or 'Universidad' in focus or 'Work with' in focus or 'Support Radical' in focus or 'Cut Ties' in focus or 'Old Enemy' in focus:
                    items.append(f"**{focus.strip('*')}** ({date})")
                else:
                    items.append(f"{focus} ({date})")
    
    return items

def extract_government_timeline(content: str) -> List[str]:
    """Extract government & law timeline items."""
    items = []
    gov_section = re.search(r"## 2[\s\xa0]*[·•‑-][\s\xa0]*[Gg]overnment[\s\xa0]*&[\s\xa0]*law[\s\xa0]*timeline(.+?)(?=## 3|$)", content, re.DOTALL | re.IGNORECASE)
    
    if gov_section:
        section_content = gov_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            date, action = row[0], row[1]
            if date and action and 'PP 150' not in action and 'Why' not in action:
                if "Chief of Army" in action or action.startswith('**'):
                    items.append(f"Appoint {action} ({date})")
                else:
                    items.append(f"Appoint {action} ({date})")
        
        # Extract trade rules
        trade_bullets = re.findall(r"^\*[\s\xa0\u202f]*(.+)$", section_content, re.MULTILINE)
        for bullet in trade_bullets:
            bullet = normalize_text(bullet)
            if 'Export Focus' in bullet:
                items.append("Keep **Export Focus** the whole run")
            elif 'rubber' in bullet:
                items.append("Import 8 rubber from British Malaya until Brazil's rubber is captured")
    
    return items

def extract_research_timeline(content: str) -> List[str]:
    """Extract research timeline items."""
    items = []
    research_section = re.search(r"## 3[\s\xa0]*[·•‑-][\s\xa0]*[Rr]esearch[\s\xa0]*timeline(.+?)(?=## 4|$)", content, re.DOTALL | re.IGNORECASE)
    
    if research_section:
        section_content = research_section.group(1)
        
        # Extract specific research items
        if "Basic Machine Tools" in section_content:
            items.append("Research Basic Machine Tools → Concentration I (Slot 1, 1936)")
        if "Electrical Eng" in section_content:
            items.append("Research Electrical Engineering → Radio (Slot 2, 1936)")
        if "Support Eq I" in section_content:
            items.append("Research Support Eq I → Engineers I (Slot 3, Oct 36)")
        if "Superior Firepower" in section_content:
            items.append("Research Superior Firepower (land doctrine)")
        if "Trade" in section_content and "Interdiction" in section_content:
            items.append("Research Trade-Interdiction (navy doctrine)")
        if "Mobile Strike" in section_content:
            items.append("Research Mobile Strike (tank doctrine)")
        
        items.append("Continue research as per table for 1937–1940")
    
    return items

def extract_construction_rail(content: str) -> List[str]:
    """Extract construction & rail items."""
    items = []
    construction_section = re.search(r"## 4[\s\xa0]*[·•‑-][\s\xa0]*[Cc]onstruction[\s\xa0]*&[\s\xa0]*rail(.+?)(?=## 5|$)", content, re.DOTALL | re.IGNORECASE)
    
    if construction_section:
        section_content = construction_section.group(1)
        
        # Extract bullet points
        bullets = re.findall(r"^\*[\s\xa0]*\*\*([^*]+)\*\*(.+)$", section_content, re.MULTILINE)
        for bullet in bullets:
            date_range = normalize_text(bullet[0])
            action = normalize_text(bullet[1])
            
            if "Jan 36" in date_range and "6 civs" in action:
                items.append(f"Build 6 civs in Buenos Aires & Córdoba ({date_range})")
            elif "25 Jun 36" in date_range:
                items.append("Upgrade Santa Cruz infra to 5 (25 Jun 36)")
            elif "military factories" in action:
                items.append(f"Build all new slots as military factories ({date_range})")
            elif "rail" in action:
                items.append(f"Build level-3 rail Buenos Aires → Santa Cruz → Porto Alegre ({date_range})")
    
    return items

def extract_factory_swap_ladder(content: str) -> List[str]:
    """Extract factory swap ladder items."""
    items = []
    factory_section = re.search(r"## 5[\s\xa0]*[·•‑-][\s\xa0]*[Ff]actory[‑-]*swap[\s\xa0]*ladder(.+?)(?=## 6|$)", content, re.DOTALL | re.IGNORECASE)
    
    if factory_section:
        section_content = factory_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            date, total_mils, new_lines, cut_lines = row[0], row[1], row[2], row[3]
            if date and total_mils and 'Date' not in date and 'Total mils' not in total_mils:
                item = f"**{date}** ({total_mils} mils): Add {new_lines}"
                if cut_lines and cut_lines not in ["—", "new mils", ""]:
                    item += f", Cut {cut_lines}"
                items.append(item)
    
    return items

def extract_division_templates(content: str) -> List[str]:
    """Extract division templates & recruit plan items."""
    items = []
    division_section = re.search(r"## 6[\s\xa0]*[·•‑-][\s\xa0]*[Dd]ivision[\s\xa0]*templates[\s\xa0]*&[\s\xa0]*recruit[\s\xa0]*plan(.+?)(?=## 7|$)", content, re.DOTALL | re.IGNORECASE)
    
    if division_section:
        section_content = division_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            date, action = row[0], row[1]
            if date and action and 'Date' not in date and 'Template action' not in action:
                items.append(f"{action} ({date})")
        
        # Extract support companies
        support_match = re.search(r"Support companies:\*\*(.+)", section_content)
        if support_match:
            items.append(f"Add support companies: {support_match.group(1).strip()}")
    
    return items

def extract_equipment_designs(content: str) -> List[str]:
    """Extract equipment design items."""
    items = []
    equipment_section = re.search(r"## 7[\s\xa0]*[·•‑-][\s\xa0]*[Ee]quipment[\s\xa0]*designs(.+?)(?=## 8|$)", content, re.DOTALL | re.IGNORECASE)
    
    if equipment_section:
        section_content = equipment_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            design_name = row[0]
            if design_name and 'Class' not in design_name:
                items.append(f"Design {design_name}")
    
    return items

def extract_air_navy_snapshot(content: str) -> List[str]:
    """Extract air & navy snapshot items."""
    items = []
    air_navy_section = re.search(r"## 8[\s\xa0]*[·•‑-][\s\xa0]*[Aa]ir[\s\xa0]*&[\s\xa0]*navy[\s\xa0]*snapshot(.+?)(?=## 9|$)", content, re.DOTALL | re.IGNORECASE)
    
    if air_navy_section:
        section_content = air_navy_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            asset, qty = row[0], row[1]
            if asset and qty and 'Asset' not in asset and 'Qty' not in qty:
                items.append(f"Build {qty} {asset}")
    
    return items

def extract_garrison_occupation(content: str) -> List[str]:
    """Extract garrison & occupation law items."""
    items = []
    garrison_section = re.search(r"## 9[\s\xa0]*[·•‑-][\s\xa0]*[Gg]arrison[\s\xa0]*&[\s\xa0]*occupation[\s\xa0]*laws(.+?)(?=## 10|$)", content, re.DOTALL | re.IGNORECASE)
    
    if garrison_section:
        section_content = garrison_section.group(1)
        
        # Extract specific law changes
        if "Military Governor" in section_content:
            items.append("Set **Military Governor** during wartime")
        if "Local Police Force" in section_content:
            items.append("Switch to **Local Police Force** when resistance <10%")
        if "Civilian Oversight" in section_content:
            items.append("Set **Civilian Oversight** (coast) post-Brazil (Jul 41)")
        
        # Extract armoured car building
        if "120 cars" in section_content:
            items.append("Build 120 Armoured Cars (Jan 41–Apr 41)")
    
    return items

def extract_spy_missions(content: str) -> List[str]:
    """Extract spy mission items."""
    items = []
    spy_section = re.search(r"## 10[\s\xa0]*[·•‑-][\s\xa0]*[Ss]py[\s\xa0]*missions(.+?)(?=## 11|$)", content, re.DOTALL | re.IGNORECASE)
    
    if spy_section:
        section_content = spy_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            date, task = row[0], row[1]
            if date and task and 'Date' not in date and 'Task' not in task:
                if "Break Brazil cipher" in task:
                    items.append(f"**{task}** ({date})")
                else:
                    items.append(f"{task} ({date})")
    
    return items

def extract_war_playbook(content: str) -> List[str]:
    """Extract war playbook items."""
    items = []
    war_section = re.search(r"## 11[\s\xa0]*[·•‑-][\s\xa0]*[Ww]ar[\s\xa0]*play[‑-]*book(.+?)(?=## 12|$)", content, re.DOTALL | re.IGNORECASE)
    
    if war_section:
        section_content = war_section.group(1)
        table_rows = extract_table_rows(section_content)
        
        for row in table_rows:
            war, strategy = row[0], row[1]
            if war and strategy and 'War' not in war and 'Opening move' not in strategy:
                items.append(f"**{war}**: {strategy}")
    
    return items

def extract_final_logistics(content: str) -> List[str]:
    """Extract final logistics check items."""
    items = []
    logistics_section = re.search(r"## 12[\s\xa0]*[·•‑-][\s\xa0]*[Ff]inal[\s\xa0]*logistics(.+?)(?=###|$)", content, re.DOTALL | re.IGNORECASE)
    
    if logistics_section:
        section_content = logistics_section.group(1)
        
        # Extract bullet points
        bullets = re.findall(r"^\*[\s\xa0]*\*\*([^*]+)\*\*(.+)$", section_content, re.MULTILINE)
        for bullet in bullets:
            category = normalize_text(bullet[0])
            details = normalize_text(bullet[1])
            
            if "Factories" in category:
                items.append(f"Verify {details} factories (civ + mil)")
            elif "Army" in category:
                army_parts = details.split(", ")
                for part in army_parts:
                    part = part.strip()
                    if "42‑w" in part or "42-w" in part:
                        items.append(f"Confirm {part} divisions")
                    elif "Mtn" in part:
                        items.append(f"Confirm {part} divisions") 
                    elif "Med spearheads" in part:
                        items.append(f"Confirm {part} spearheads")
            elif "Garrisons" in category:
                items.append(f"Check {details} garrisons on coast")
            elif "Stockpiles" in category:
                # Split stockpiles into separate items
                stockpile_parts = details.split(" • ")
                for part in stockpile_parts:
                    part = part.strip()
                    if "trains" in part:
                        items.append(f"Verify {part} in stockpile")
                    elif "trucks" in part:
                        items.append(f"Verify {part} in stockpile")
            elif "Compliance" in category:
                items.append(f"Check compliance levels: {details}")
    
    return items

def generate_checklist_file(original_filepath: str, items_dict: Dict[str, List[str]]) -> str:
    """Generate a complete checklist file."""
    base_name = os.path.splitext(os.path.basename(original_filepath))[0]
    
    # Extract title from the original file if possible
    try:
        with open(original_filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            if first_line.startswith('# '):
                title = first_line[2:].strip()
            else:
                title = base_name.replace('-', ' ').title()
    except:
        title = base_name.replace('-', ' ').title()
    
    checklist_content = f"""# {title} - Checklist

> **Interactive checklist for following the [{title}](../{original_filepath}) strategy guide.**
> 
> Tick each action as you complete it during gameplay.

"""
    
    section_order = [
        ("National Focus Timeline", "focus_timeline"),
        ("Government & Law Timeline", "government_timeline"),
        ("Research Timeline", "research_timeline"),
        ("Construction & Rail", "construction_rail"),
        ("Factory-Swap Ladder", "factory_swap"),
        ("Division Templates & Recruit Plan", "division_templates"),
        ("Equipment Designs", "equipment_designs"),
        ("Air & Navy Snapshot", "air_navy"),
        ("Garrison & Occupation Laws", "garrison_occupation"),
        ("Spy Missions", "spy_missions"),
        ("War Playbook", "war_playbook"),
        ("Final Logistics Check (May 41)", "final_logistics")
    ]
    
    for section_title, section_key in section_order:
        if section_key in items_dict and items_dict[section_key]:
            checklist_content += f"## {section_title}\n\n"
            for item in items_dict[section_key]:
                checklist_content += f"- [ ] {item}\n"
            checklist_content += "\n"
    
    checklist_content += """---

## Usage Tips

- **Print this checklist** or keep it open in a second monitor/device
- **Check off items** as you complete them in-game
- **Use Ctrl+F** to quickly find specific dates or actions
- **Refer back to the [main guide](../{}) for detailed explanations**

*This checklist was auto-generated from the strategy guide.*
""".format(original_filepath)
    
    return checklist_content

def process_guide_file(filepath: str) -> bool:
    """Process a single guide file and create/update checklist in checklists folder."""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    # Check if this is a strategy guide (has the expected structure)
    if not re.search(r"## 1[\s\xa0]*[·•‑-][\s\xa0]*[Nn]ational[‑-]*focus[\s\xa0]*timeline", content, re.IGNORECASE):
        print(f"Skipping {filepath} - not a strategy guide")
        return False
    
    # Extract items from each section
    items_dict = {
        "focus_timeline": extract_focus_timeline(content),
        "government_timeline": extract_government_timeline(content),
        "research_timeline": extract_research_timeline(content),
        "construction_rail": extract_construction_rail(content),
        "factory_swap": extract_factory_swap_ladder(content),
        "division_templates": extract_division_templates(content),
        "equipment_designs": extract_equipment_designs(content),
        "air_navy": extract_air_navy_snapshot(content),
        "garrison_occupation": extract_garrison_occupation(content),
        "spy_missions": extract_spy_missions(content),
        "war_playbook": extract_war_playbook(content),
        "final_logistics": extract_final_logistics(content)
    }
    
    # Generate checklist content
    checklist_content = generate_checklist_file(filepath, items_dict)
    
    # Create checklists directory if it doesn't exist
    os.makedirs('checklists', exist_ok=True)
    
    # Generate checklist filename
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    checklist_filepath = os.path.join('checklists', f"{base_name}-checklist.md")
    
    # Write checklist file
    try:
        with open(checklist_filepath, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        print(f"Created checklist: {checklist_filepath}")
        return True
    except Exception as e:
        print(f"Error writing {checklist_filepath}: {e}")
        return False

def main():
    """Main function to process all guide files."""
    # Find all markdown files except README.md and checklist files
    guide_files = []
    for pattern in ['*.md', '**/*.md']:
        guide_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out README and checklist files
    guide_files = [f for f in guide_files if not f.lower().endswith('readme.md') and 'checklist' not in f.lower()]
    
    if not guide_files:
        print("No guide files found.")
        return
    
    print(f"Found {len(guide_files)} potential guide files")
    
    updated_count = 0
    for filepath in guide_files:
        if process_guide_file(filepath):
            updated_count += 1
    
    print(f"Updated {updated_count} files")

if __name__ == "__main__":
    main()
