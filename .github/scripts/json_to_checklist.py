#!/usr/bin/env python3
"""
JSON to Checklist converter for HOI4 strategy guides.
Converts JSON strategy guides into actionable checklists.
"""

import json
import os
from typing import Dict, Any, List

def convert_section_to_checklist(section: Dict[str, Any], guide_filename: str = None) -> str:
    """Convert a single section to checklist format."""
    section_id = section.get("id", "")
    section_name = section.get("name", "Unknown Section")
    
    # Format section header
    if section_id != "":
        header = f"## {section_id}. {section_name}"
    else:
        header = f"## {section_name}"
    
    checklist_lines = [header, ""]
    
    # Special handling for Section 5 (Factory-swap ladder)
    if section_id == 5 or "factory-swap" in section_name.lower():
        # Add reference to main guide
        if guide_filename:
            checklist_lines.extend([
                f"*For full factory allocation details, see the [main strategy guide](../guides/{guide_filename}#5-factory-swap-ladder)*",
                ""
            ])
        else:
            checklist_lines.extend([
                "*For full factory allocation details, see the main strategy guide*",
                ""
            ])
        
        # Only show changes for Factory-swap ladder
        if "columns" in section and "rows" in section:
            columns = section["columns"]
            
            # Find specific columns we want
            date_col_idx = None
            take_give_idx = None
            dockyards_idx = None
            why_idx = None
            
            for i, col in enumerate(columns):
                if col.lower() in ["date"]:
                    date_col_idx = i
                elif "take_from_give_to" in col.lower():
                    take_give_idx = i
                elif "dockyards" in col.lower():
                    dockyards_idx = i
                elif col.lower() in ["why"]:
                    why_idx = i
            
            # Process each row showing only changes
            for row in section["rows"]:
                if not row:  # Skip empty rows
                    continue
                
                # Get date
                date_info = ""
                if date_col_idx is not None and date_col_idx < len(row):
                    date_value = row[date_col_idx]
                    if date_value and str(date_value).strip() != "-":
                        date_info = str(date_value)
                
                # Build action from specific columns only
                action_parts = []
                
                # Take from / Give to changes
                if take_give_idx is not None and take_give_idx < len(row):
                    take_give = row[take_give_idx]
                    if take_give and str(take_give).strip() not in ["-", "0", ""]:
                        action_parts.append(f"Factory Change: {take_give}")
                
                # Dockyards
                if dockyards_idx is not None and dockyards_idx < len(row):
                    dockyards = row[dockyards_idx]
                    if dockyards and str(dockyards).strip() != "-":
                        action_parts.append(f"Dockyards: {dockyards}")
                
                # Why
                if why_idx is not None and why_idx < len(row):
                    why = row[why_idx]
                    if why and str(why).strip() != "-":
                        action_parts.append(f"({why})")
                
                # Create checklist item only if there are meaningful changes
                if action_parts:
                    action_text = " - ".join(action_parts)
                    if date_info:
                        checklist_item = f"- [ ] **{date_info}**: {action_text}"
                    else:
                        checklist_item = f"- [ ] {action_text}"
                    checklist_lines.append(checklist_item)
        
        # Add notes if present
        if "notes" in section and section["notes"]:
            checklist_lines.extend(["", "### Notes"])
            for note in section["notes"]:
                checklist_lines.append(f"- {note}")
        
        return "\n".join(checklist_lines)
    
    # Handle Air & Navy snapshot special case
    elif "air" in section and "navy" in section:
        # Air subsection
        checklist_lines.extend(["### Air Plan", ""])
        air_columns = section["air"]["columns"]
        for row in section["air"]["rows"]:
            action_parts = []
            for i, value in enumerate(row):
                if value and str(value).strip() != "-":
                    action_parts.append(str(value))
            if action_parts:
                checklist_lines.append(f"- [ ] {' - '.join(action_parts)}")
        
        # Navy subsection
        checklist_lines.extend(["", "### Navy Plan", ""])
        navy_columns = section["navy"]["columns"]
        for row in section["navy"]["rows"]:
            action_parts = []
            for i, value in enumerate(row):
                if value and str(value).strip() != "-":
                    action_parts.append(str(value))
            if action_parts:
                checklist_lines.append(f"- [ ] {' - '.join(action_parts)}")
    
    # Handle regular sections with columns and rows
    elif "columns" in section and "rows" in section:
        columns = section["columns"]
        
        # Find the date/timing column
        date_col_idx = None
        for i, col in enumerate(columns):
            if col.lower() in ["date", "start", "start_end", "timing", "#"]:
                date_col_idx = i
                break
        
        # Process each row
        for row in section["rows"]:
            if not row:  # Skip empty rows
                continue
                
            # Get date/timing info
            date_info = ""
            if date_col_idx is not None and date_col_idx < len(row):
                date_value = row[date_col_idx]
                if date_value and str(date_value).strip() != "-":
                    date_info = str(date_value)
            
            # Build action details from other columns
            action_parts = []
            for i, value in enumerate(row):
                if i == date_col_idx:  # Skip date column
                    continue
                if value and str(value).strip() != "-" and str(value).strip() != "":
                    col_name = columns[i] if i < len(columns) else f"col_{i}"
                    
                    # Format special columns
                    if col_name.lower() in ["why", "reason"]:
                        action_parts.append(f"({value})")
                    elif col_name.lower() == "tier":
                        action_parts.append(f"[Tier {value}]")
                    else:
                        action_parts.append(str(value))
            
            # Create checklist item
            if action_parts:
                action_text = " - ".join(action_parts)
                if date_info:
                    checklist_item = f"- [ ] **{date_info}**: {action_text}"
                else:
                    checklist_item = f"- [ ] {action_text}"
                checklist_lines.append(checklist_item)
    
    # Add notes if present (for non-factory-swap sections)
    if section_id != 5 and "factory-swap" not in section_name.lower():
        if "notes" in section and section["notes"]:
            checklist_lines.extend(["", "### Notes"])
            for note in section["notes"]:
                checklist_lines.append(f"- {note}")
    
    return "\n".join(checklist_lines)

def convert_json_to_checklist(json_data: Dict[str, Any], guide_filename: str = None) -> str:
    """Convert JSON to checklist format."""
    checklist_lines = []
    
    # Extract metadata for title
    meta = json_data.get("meta", {})
    title = meta.get("title", "Strategy Guide Checklist")
    
    checklist_lines.extend([
        f"# {title} - Checklist",
        ""
    ])
    
    # Add link to guide if provided
    if guide_filename:
        checklist_lines.extend([
            f"📖 **[View Full Strategy Guide](../guides/{guide_filename})**",
            ""
        ])
    
    checklist_lines.extend([
        "Use this checklist to track your progress through the strategy guide.",
        "",
        "---",
        ""
    ])
    
    # Process all sections
    sections = json_data.get("sections", [])
    
    for i, section in enumerate(sections):
        section_checklist = convert_section_to_checklist(section, guide_filename)
        checklist_lines.append(section_checklist)
        
        # Add separator between sections (except for the last one)
        if i < len(sections) - 1:
            checklist_lines.extend(["", "---", ""])
    
    return "\n".join(checklist_lines)

def process_json_files_in_directory(data_dir: str, checklists_dir: str):
    """Process all JSON files from data directory and create checklists in checklists directory."""
    # Ensure checklists directory exists
    os.makedirs(checklists_dir, exist_ok=True)
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(data_dir, filename)
            
            # Create output paths
            base_name = os.path.splitext(filename)[0]
            guide_filename = f"{base_name}.md"
            checklist_filename = f"{base_name}-checklist.md"
            checklist_path = os.path.join(checklists_dir, checklist_filename)
            
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                
                checklist_content = convert_json_to_checklist(json_data, guide_filename)
                
                with open(checklist_path, "w", encoding="utf-8") as f:
                    f.write(checklist_content)
                
                print(f"✓ Generated checklist: {checklist_path}")
                
            except Exception as e:
                print(f"✗ Failed to process {filename}: {e}")

def main():
    """Main function to process JSON files from data directory to checklists directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(repo_root, "data")
    checklists_dir = os.path.join(repo_root, "checklists")
    
    print(f"Processing JSON files from: {data_dir}")
    print(f"Outputting checklists to: {checklists_dir}")
    
    if not os.path.exists(data_dir):
        print(f"Data directory does not exist: {data_dir}")
        return
    
    process_json_files_in_directory(data_dir, checklists_dir)

if __name__ == "__main__":
    main()
