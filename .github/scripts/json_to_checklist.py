#!/usr/bin/env python3
"""
JSON to Checklist converter for HOI4 strategy guides.
Converts JSON strategy guides into actionable checklists.
"""

import json
import os
from typing import Dict, Any, List

def convert_section_to_checklist(section_key: str, section_data: Dict[str, Any], guide_filename: str = None) -> str:
    """Convert a single section to checklist format."""
    # Format section header based on section key
    if section_key == "day_one_snapshot":
        header = "## 0. Day-One Snapshot"
    elif section_key == "national_focus_timeline":
        header = "## 1. National Focus Timeline"
    else:
        section_title = section_key.replace("_", " ").title()
        header = f"## {section_title}"
    
    checklist_lines = [header, ""]
    
    # Special handling for different section types
    if section_key == "day_one_snapshot":
        if "summary" in section_data:
            checklist_lines.extend([
                f"**Summary:** {section_data['summary']}",
                ""
            ])
        
        if "oob" in section_data:
            checklist_lines.extend([
                "**Starting Order of Battle:**",
                ""
            ])
            oob = section_data["oob"]
            for key, value in oob.items():
                formatted_key = key.replace("_", " ").title()
                checklist_lines.append(f"- [ ] {formatted_key}: {value}")
            checklist_lines.append("")
    
    elif section_key == "national_focus_timeline":
        checklist_lines.extend([
            "Track your focus progression:",
            ""
        ])
        
        if isinstance(section_data, list):
            for i, focus in enumerate(section_data, 1):
                focus_name = focus.get("focus", "Unknown Focus")
                start_date = focus.get("start", "—")
                tier = focus.get("tier", "—")
                why = focus.get("why", "")
                
                focus_line = f"- [ ] **{focus_name}** ({start_date}) [T{tier}]"
                if why:
                    focus_line += f" - {why}"
                checklist_lines.append(focus_line)
        checklist_lines.append("")
    
    else:
        # Generic section processing
        if isinstance(section_data, list):
            if section_data:
                first_item = section_data[0]
                if isinstance(first_item, dict):
                    # Create checklist from dict items
                    for item in section_data:
                        # Try to find a meaningful description
                        description_keys = ['pick', 'action', 'focus', 'item', 'name', 'tech', 'type']
                        description = None
                        for key in description_keys:
                            if key in item:
                                description = item[key]
                                break
                        
                        if not description:
                            description = str(item)
                        
                        # Add additional context if available
                        context_parts = []
                        if 'date' in item:
                            context_parts.append(f"({item['date']})")
                        if 'tier' in item:
                            context_parts.append(f"[T{item['tier']}]")
                        if 'why' in item:
                            context_parts.append(f"- {item['why']}")
                        
                        context = " ".join(context_parts)
                        checklist_lines.append(f"- [ ] {description} {context}")
                else:
                    # Simple list items
                    for item in section_data:
                        checklist_lines.append(f"- [ ] {item}")
            checklist_lines.append("")
        
        elif isinstance(section_data, dict):
            # Handle nested dictionary data
            for key, value in section_data.items():
                if isinstance(value, list):
                    sub_header = key.replace("_", " ").title()
                    checklist_lines.extend([f"### {sub_header}", ""])
                    for item in value:
                        if isinstance(item, dict):
                            # Try to create meaningful checklist items
                            item_desc = str(item)
                            if 'name' in item:
                                item_desc = item['name']
                            elif 'type' in item:
                                item_desc = item['type']
                            checklist_lines.append(f"- [ ] {item_desc}")
                        else:
                            checklist_lines.append(f"- [ ] {item}")
                    checklist_lines.append("")
                elif isinstance(value, dict):
                    sub_header = key.replace("_", " ").title()
                    checklist_lines.extend([f"### {sub_header}", ""])
                    for k, v in value.items():
                        formatted_key = k.replace("_", " ").title()
                        checklist_lines.append(f"- [ ] {formatted_key}: {v}")
                    checklist_lines.append("")
                else:
                    formatted_key = key.replace("_", " ").title()
                    checklist_lines.append(f"- [ ] {formatted_key}: {value}")
            if not any(isinstance(v, (list, dict)) for v in section_data.values()):
                checklist_lines.append("")
        
        else:
            # Simple value
            checklist_lines.extend([f"- [ ] {section_data}", ""])
    
    return "\n".join(checklist_lines)

def convert_json_to_checklist(json_data: Dict[str, Any], guide_filename: str = None) -> str:
    """Convert JSON to checklist format."""
    checklist_lines = []
    
    # Extract metadata for title
    meta = json_data.get("meta", {})
    country = meta.get("country", "Unknown Country")
    path = meta.get("path", "Strategy Guide")
    title = f"{country} {path}"
    
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
    
    # Process sections
    sections = json_data.get("sections", {})
    
    # Handle both old format (list) and new format (dict)
    if isinstance(sections, list):
        # Old format: sections is a list of section objects
        for i, section in enumerate(sections):
            section_id = section.get("id", str(i))
            section_checklist = convert_section_to_checklist(section_id, section, guide_filename)
            checklist_lines.append(section_checklist)
            
            # Add separator between sections (except for the last one)
            if i < len(sections) - 1:
                checklist_lines.extend(["", "---", ""])
    else:
        # New format: sections is a dict with section names as keys
        section_keys = list(sections.keys())
        for i, (section_key, section_data) in enumerate(sections.items()):
            section_checklist = convert_section_to_checklist(section_key, section_data, guide_filename)
            checklist_lines.append(section_checklist)
            
            # Add separator between sections (except for the last one)
            if i < len(section_keys) - 1:
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
