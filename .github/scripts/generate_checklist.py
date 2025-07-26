#!/usr/bin/env python3
"""
Simple checklist generator for HOI4 strategy guides.
Converts markdown tables into checklists while preserving structure.
"""

import re
import os
import glob

def process_guide_to_checklist(content: str, source_filename: str) -> str:
    """Convert a markdown guide to a checklist format."""
    
    # Extract title from first heading
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Strategy Guide"
    
    # Start building checklist
    checklist_lines = [
        f"# {title} - Interactive Checklist",
        "",
        f"> **Generated from [{source_filename}](../{source_filename})**",
        "> ",
        "> Tick each action as you complete it during gameplay.",
        ""
    ]
    
    # Split content by sections (## headers)
    sections = re.split(r'^##\s*(.+)$', content, flags=re.MULTILINE)
    
    # Process each section
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            section_title = sections[i].strip()
            section_content = sections[i + 1].strip()
            
            # Add section header
            checklist_lines.append(f"## {section_title}")
            checklist_lines.append("")
            
            # Handle complex sections specially
            if "factory" in section_title.lower() and "swap" in section_title.lower():
                checklist_lines.append("**Complex production timeline - see original guide for detailed factory allocations and equipment targets**")
                checklist_lines.append("")
                checklist_lines.append("- [ ] Follow production schedule from original guide")
                
                # Extract actual dates from the factory swap table
                factory_dates = extract_factory_dates(section_content)
                if factory_dates:
                    for date in factory_dates:
                        checklist_lines.append(f"- [ ] **{date}**: Check original guide for factory changes")
                else:
                    checklist_lines.append("- [ ] Monitor early game production priorities")
                    checklist_lines.append("- [ ] Adjust factory allocation based on timeline")
                    checklist_lines.append("- [ ] Balance military and civilian production")
                    checklist_lines.append("- [ ] Plan equipment transitions carefully")
                    checklist_lines.append("- [ ] Consider war timeline when scheduling changes")
                
                checklist_lines.append("")
                continue
            elif "equipment designs" in section_title.lower():
                checklist_lines.append("**Equipment designs with modules and chassis details - see original guide for full specifications**")
                checklist_lines.append("")
            elif "war" in section_title.lower() and "book" in section_title.lower():
                checklist_lines.append("**War strategies and detailed battle plans - consult original guide for tactics, timing, and unit compositions**")
                checklist_lines.append("")
            elif section_title.lower().startswith("9.") and ("air" in section_title.lower() or "navy" in section_title.lower()):
                checklist_lines.append("**Air/Navy deployment - check original guide for mission priorities, timing, and base assignments**")
                checklist_lines.append("")
            
            # Process tables in this section
            table_items = extract_table_items(section_content)
            
            # Process bullet points in this section
            bullet_items = extract_bullet_items(section_content)
            
            # Add all items
            all_items = table_items + bullet_items
            
            if all_items:
                for item in all_items:
                    checklist_lines.append(f"- [ ] {item}")
                checklist_lines.append("")
            else:
                # If no structured content, add a placeholder
                checklist_lines.append("- [ ] Review this section in original guide")
                checklist_lines.append("")
    
    # Add footer
    checklist_lines.extend([
        "---",
        "",
        "## Usage Tips",
        "",
        "- **Print this checklist** or keep it open in a second monitor/device",
        "- **Check off items** as you complete them in-game", 
        "- **Use Ctrl+F** to quickly find specific dates or actions",
        f"- **Refer back to the [source file](../{source_filename}) for detailed explanations**",
        "",
        f"*This checklist was auto-generated from {source_filename}.*"
    ])
    
    return '\n'.join(checklist_lines)

def extract_factory_dates(content: str) -> list:
    """Extract dates from factory swap tables for timeline reference."""
    dates = []
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        if '|' in line and not ('---' in line or line.startswith('|--')):
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) > 0 and cells[0] == '':
                cells = cells[1:]
            if len(cells) > 0 and cells[-1] == '':
                cells = cells[:-1]
            
            # Skip header rows
            if len(cells) >= 1:
                first_cell = cells[0].lower()
                if first_cell in ['date', 'start', 'phase', 'guns', 'art']:
                    continue
                
                # Look for date-like entries in first column
                if len(cells) >= 1:
                    date_cell = cells[0]
                    # Check if it looks like a date
                    if (any(month in date_cell.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) 
                        or any(word in date_cell.lower() for word in ['post', 'early', 'late', 'pre'])
                        or '→' in date_cell):
                        dates.append(date_cell)
    
    return dates

def extract_table_items(content: str) -> list:
    """Extract items from markdown tables - include more contextual information."""
    items = []
    
    # Find all table rows (lines with |)
    lines = content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        # Skip table header separators
        if '---' in line and '|' in line:
            continue
            
        # Process table data rows
        if '|' in line and not line.startswith('|--'):
            # Split by | and clean up
            cells = [cell.strip() for cell in line.split('|')]
            
            # Remove empty first/last cells from markdown table formatting
            if len(cells) > 0 and cells[0] == '':
                cells = cells[1:]
            if len(cells) > 0 and cells[-1] == '':
                cells = cells[:-1]
            
            # Skip obvious header rows
            if len(cells) >= 2:
                first_cell_lower = cells[0].lower()
                # More specific header detection
                if (first_cell_lower in ['#', 'date', 'start', 'slot', 'class', 'asset', 'phase', 'war', 'tier', 'group', 'item'] or
                    'start → end' in ' '.join(cells[:2]).lower()):
                    continue
            
            # Extract meaningful content from table rows
            if len(cells) >= 2:
                # Clean up cells
                clean_cells = []
                for cell in cells:
                    # Clean up but preserve important formatting
                    cleaned = cell.strip()
                    if cleaned and cleaned != '—' and cleaned != '-':
                        clean_cells.append(cleaned)
                
                if len(clean_cells) >= 2:
                    # Build contextual checklist items based on table type
                    
                    # Air/Navy plans: Phase | Wings/Composition | Missions | Bases | ...
                    if len(clean_cells) >= 3 and any(mission in ' '.join(clean_cells).lower() for mission in ['air sup', 'sup/cas', 'sup/nav', 'nav strike', 'shore bombard']):
                        phase_cell = clean_cells[0]
                        composition_cell = clean_cells[1]
                        mission_cell = clean_cells[2] if len(clean_cells) > 2 else ""
                        base_cell = clean_cells[3] if len(clean_cells) > 3 else ""
                        if mission_cell and base_cell:
                            items.append(f"**{phase_cell}**: Deploy {composition_cell} for {mission_cell} from {base_cell}")
                        elif mission_cell:
                            items.append(f"**{phase_cell}**: Deploy {composition_cell} for {mission_cell}")
                        else:
                            items.append(f"**{phase_cell}**: Deploy {composition_cell}")
                    
                    # Focus tables: # | Start→End | Days | Focus | ...
                    elif len(clean_cells) >= 4 and ('→' in clean_cells[1] or 
                        any(month in clean_cells[1].lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])):
                        date_cell = clean_cells[1]  # Start→End column
                        action_cell = clean_cells[3] if len(clean_cells) > 3 else clean_cells[2]  # Focus name
                        items.append(f"**{date_cell}**: {action_cell}")
                    
                    # Government/Laws tables: Date | PP | XP | Slot/Tab | Pick | ...
                    elif len(clean_cells) >= 5 and any(word in ' '.join(clean_cells).lower() for word in ['trade law', 'economy law', 'conscription', 'chief of', 'theorist', 'high command']):
                        date_cell = clean_cells[0]
                        pick_cell = clean_cells[4] if len(clean_cells) > 4 else clean_cells[3]
                        # Add context from slot/tab column if available
                        slot_context = clean_cells[3] if len(clean_cells) > 3 and clean_cells[3] not in pick_cell else ""
                        if slot_context and slot_context != pick_cell:
                            items.append(f"**{date_cell}**: {slot_context} → {pick_cell}")
                        else:
                            items.append(f"**{date_cell}**: {pick_cell}")
                    
                    # Construction tables: Start→End | Build Queue | State(s) | ...
                    elif len(clean_cells) >= 3 and any(word in ' '.join(clean_cells).lower() for word in ['civ', 'mil', 'infra', 'fort', 'aa']):
                        date_cell = clean_cells[0]
                        build_cell = clean_cells[1]
                        location_cell = clean_cells[2] if len(clean_cells) > 2 else ""
                        if location_cell:
                            items.append(f"**{date_cell}**: {build_cell} in {location_cell}")
                        else:
                            items.append(f"**{date_cell}**: {build_cell}")
                    
                    # Research tables: Start | Finish | Slot | Tech | ...
                    elif len(clean_cells) >= 4 and any(word in ' '.join(clean_cells).lower() for word in ['machine tools', 'construction', 'artillery', 'radio', 'engineers', 'tank', 'infantry']):
                        date_cell = clean_cells[0]
                        tech_cell = clean_cells[3] if len(clean_cells) > 3 else clean_cells[2]
                        slot_cell = clean_cells[2] if len(clean_cells) > 2 and clean_cells[2].isdigit() else ""
                        if slot_cell:
                            items.append(f"**{date_cell}**: (Slot {slot_cell}) {tech_cell}")
                        else:
                            items.append(f"**{date_cell}**: {tech_cell}")
                    
                    # Army grouping: Date | Group | Divs | Commander | ...
                    elif len(clean_cells) >= 4 and any(word in ' '.join(clean_cells).lower() for word in ['army group', 'corps', 'promote', 'gen.', 'fm']):
                        date_cell = clean_cells[0]
                        group_cell = clean_cells[1]
                        commander_cell = clean_cells[3] if len(clean_cells) > 3 else ""
                        if commander_cell:
                            items.append(f"**{date_cell}**: {group_cell} → {commander_cell}")
                        else:
                            items.append(f"**{date_cell}**: {group_cell}")
                    
                    # Division templates: Date | Action | Qty | Template | ...
                    elif len(clean_cells) >= 4 and any(word in ' '.join(clean_cells).lower() for word in ['train', 'convert', 'exercise', 'queue', 'create', 'add art', 'upgrade']):
                        date_cell = clean_cells[0]
                        action_cell = clean_cells[1]
                        template_cell = clean_cells[3] if len(clean_cells) > 3 else clean_cells[2]
                        qty_cell = clean_cells[2] if len(clean_cells) > 2 and (clean_cells[2].replace('×', '').replace('x', '').replace('~', '').strip().isdigit() or clean_cells[2] == '—') else ""
                        if qty_cell and template_cell and qty_cell != '—':
                            items.append(f"**{date_cell}**: {action_cell} {qty_cell} {template_cell}")
                        elif template_cell:
                            items.append(f"**{date_cell}**: {action_cell} {template_cell}")
                        else:
                            items.append(f"**{date_cell}**: {action_cell}")
                    
                    # Equipment designs: Date | Unit | Chassis | Modules | ...
                    elif len(clean_cells) >= 3 and any(word in ' '.join(clean_cells).lower() for word in ['tank', 'fighter', 'sub', 'cas', 'nav', 'mech']) and not any(mission in ' '.join(clean_cells).lower() for mission in ['air sup', 'sup/cas', 'sup/nav']):
                        date_cell = clean_cells[0]
                        unit_cell = clean_cells[1]
                        # Check if modules are in same row
                        if len(clean_cells) >= 4:
                            modules_cell = clean_cells[3] if len(clean_cells) > 3 else clean_cells[2]
                            items.append(f"**{date_cell}**: Design {unit_cell} - {modules_cell}")
                        else:
                            items.append(f"**{date_cell}**: Design {unit_cell} (see original guide for modules)")
                    
                    # Factory swap: Date | Guns | ART | ... - very complex, only match if many production columns
                    elif len(clean_cells) >= 6 and any(word in ' '.join(clean_cells).lower() for word in ['guns', 'trucks', 'suppeq', 'flame lt']) and not any(template_word in ' '.join(clean_cells).lower() for template_word in ['inf', 'mtn', 'template', 'train', 'convert']):
                        date_cell = clean_cells[0]
                        # Factory swap is too complex for checklist format
                        items.append(f"**{date_cell}**: Factory changes (see original guide for specific allocations)")
                    
                    # Navy plans: Group | Composition | Mission | Tier | ...
                    elif len(clean_cells) >= 3 and any(word in ' '.join(clean_cells).lower() for word in ['bb', 'ca', 'cl', 'dd', 'sub', 'fleet', 'surface', 'convoy', 'shore bombard']):
                        group_cell = clean_cells[0]
                        composition_cell = clean_cells[1]
                        mission_cell = clean_cells[2] if len(clean_cells) > 2 else ""
                        if mission_cell:
                            items.append(f"**{group_cell}**: {composition_cell} on {mission_cell}")
                        else:
                            items.append(f"**{group_cell}**: {composition_cell}")
                    
                    # Garrisons: Phase | When | Law | Template | ...
                    elif len(clean_cells) >= 4 and any(word in ' '.join(clean_cells).lower() for word in ['civilian oversight', 'local police', 'secret police', 'martial law']):
                        phase_cell = clean_cells[0]
                        when_cell = clean_cells[1]
                        law_cell = clean_cells[2]
                        template_cell = clean_cells[3] if len(clean_cells) > 3 else ""
                        if template_cell:
                            items.append(f"**{when_cell}** ({phase_cell}): Set {law_cell} with {template_cell}")
                        else:
                            items.append(f"**{when_cell}** ({phase_cell}): Set {law_cell}")
                    
                    # War playbook: War | Tier | Timing | Opening Move | ...
                    elif len(clean_cells) >= 2 and any(word in ' '.join(clean_cells).lower() for word in ['paraguay', 'uruguay', 'chile', 'brazil', 'falklands', 'usa']):
                        war_cell = clean_cells[0]
                        # War plans are complex - refer to original
                        items.append(f"**{war_cell}**: Execute war plan (see original guide for strategy details)")
                    
                    # Spy missions: Date | Action | ...
                    elif len(clean_cells) >= 2 and any(word in ' '.join(clean_cells).lower() for word in ['create', 'build', 'network', 'collaboration', 'integrate', 'root out']):
                        date_cell = clean_cells[0]
                        action_cell = clean_cells[1]
                        items.append(f"**{date_cell}**: {action_cell}")
                    
                    # Victory/Logistics targets: Item | Qty | ...
                    elif len(clean_cells) >= 2 and any(word in ' '.join(clean_cells).lower() for word in ['guns', 'artillery', 'tanks', 'fighters', 'convoys', 'greater argentina', 'malvinas']):
                        item_cell = clean_cells[0]
                        target_cell = clean_cells[1]
                        items.append(f"Target: {item_cell} → {target_cell}")
                    
                    # Generic fallback with more context
                    else:
                        # Look for date pattern
                        date_cell = None
                        action_cell = None
                        
                        for i, cell in enumerate(clean_cells[:3]):
                            if (any(month in cell.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) 
                                or '→' in cell or re.search(r'\d{1,2}', cell)):
                                date_cell = cell
                                # Get the most meaningful next cell(s)
                                remaining_cells = clean_cells[i+1:]
                                if len(remaining_cells) >= 2:
                                    action_cell = f"{remaining_cells[0]} → {remaining_cells[1]}"
                                elif len(remaining_cells) >= 1:
                                    action_cell = remaining_cells[0]
                                break
                        
                        if date_cell and action_cell:
                            items.append(f"**{date_cell}**: {action_cell}")
                        elif len(clean_cells) >= 2:
                            items.append(f"{clean_cells[0]} → {clean_cells[1]}")
    
    return items

def extract_bullet_items(content: str) -> list:
    """Extract items from bullet points and other non-table content."""
    items = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        # Skip table-related lines
        if '|' in line:
            continue
            
        # Extract meaningful bullet points
        if line.startswith('- ') or line.startswith('* '):
            bullet_text = line[2:].strip()
            if bullet_text and len(bullet_text) > 3:
                items.append(bullet_text)
        
        # Extract meaningful standalone lines that look like instructions
        elif (line and not line.startswith('#') and 
              len(line) > 10 and 
              not line.startswith('>')):
            # Look for instructional content
            if any(keyword in line.lower() for keyword in ['build', 'train', 'research', 'focus', 'recruit', 'convert', 'upgrade']):
                items.append(line)
    
    return items

def normalize_text(text):
    """Normalize unicode characters to ASCII."""
    # Replace common unicode characters
    replacements = {
        '–': '-',  # en-dash
        '—': '-',  # em-dash  
        ''': "'",  # left single quote
        ''': "'",  # right single quote
        '"': '"',  # left double quote
        '"': '"',  # right double quote
        '…': '...',  # ellipsis
        '×': 'x',   # multiplication sign
        '‑': '-',   # non-breaking hyphen
        '·': '.',   # middle dot
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

def main():
    """Main function to process files."""
    import sys
    
    # Get the workspace root (parent of .github)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(workspace_root)
    
    # Create checklists directory if it doesn't exist
    os.makedirs('checklists', exist_ok=True)
    
    # Process specific file if provided as argument
    if len(sys.argv) > 1:
        input_files = [sys.argv[1]]
    else:
        # Process all .md files except README.md
        input_files = [f for f in glob.glob('*.md') if f != 'README.md']
    
    for input_file in input_files:
        if os.path.exists(input_file):
            print(f"Processing {input_file}...")
            
            # Read the source file
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Normalize unicode characters
            content = normalize_text(content)
            
            # Convert to checklist
            checklist_content = process_guide_to_checklist(content, input_file)
            
            # Generate output filename
            base_name = os.path.splitext(input_file)[0]
            output_file = f"checklists/{base_name}-checklist.md"
            
            # Write the checklist
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(checklist_content)
            
            print(f"✓ Generated: {output_file}")
        else:
            print(f"✗ File not found: {input_file}")

if __name__ == "__main__":
    main()
