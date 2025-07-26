#!/usr/bin/env python3
"""
Enhanced JSON to Markdown converter for HOI4 strategy guides.
Automatically processes all JSON files in a directory.
"""

import json
import os
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_new_format_to_markdown(json_data: Dict[str, Any], checklist_filename: str = None) -> str:
    """Convert new structured JSON format to markdown."""
    logging.debug("Starting conversion of JSON to Markdown.")
    markdown_lines = []

    # Extract metadata
    meta = json_data.get("meta", {})
    logging.debug(f"Metadata extracted: {meta}")
    
    # Use title if available, otherwise construct from country/path
    if "title" in meta:
        title = f"{meta['title']}"
    else:
        country = meta.get("country", "Unknown Country")
        path = meta.get("path", "Unknown Path")
        patch = meta.get("patch", "Unknown")
        title = f"{country} {path} - {patch}"

    # Title and header
    markdown_lines.extend([
        f"**{title.upper()}**",
        ""
    ])
    
    # Add link to checklist if provided
    if checklist_filename:
        markdown_lines.extend([
            f"📋 **[View Checklist](../checklists/{checklist_filename})**",
            ""
        ])

    # Tier definitions
    if "tiers" in meta:
        tier_text = "*Tiers:* "
        tier_parts = []
        for tier, definition in meta["tiers"].items():
            tier_parts.append(f"**{tier} = {definition}**")
        tier_text += " • ".join(tier_parts)
        markdown_lines.append(tier_text)
        markdown_lines.append("")

    markdown_lines.extend(["---", ""])

    # Process sections
    sections = json_data.get("sections", [])
    logging.debug(f"Sections extracted: {sections}")

    for section in sections:
        section_id = section.get("id", "Unknown ID")
        section_name = section.get("name", "Unknown Section")
        markdown_lines.append(f"## {section_id}. {section_name}")
        markdown_lines.append("")

        # Handle special Air & Navy snapshot section
        if "air" in section and "navy" in section:
            # Air subsection
            markdown_lines.append("### Air Plan")
            markdown_lines.append("")
            air_header = "| " + " | ".join(section["air"]["columns"]) + " |"
            air_separator = "| " + " | ".join(["----"] * len(section["air"]["columns"])) + " |"
            markdown_lines.extend([air_header, air_separator])
            
            for row in section["air"]["rows"]:
                formatted_row = "| " + " | ".join(str(item) if item else "—" for item in row) + " |"
                markdown_lines.append(formatted_row)
            
            markdown_lines.append("")
            
            # Navy subsection
            markdown_lines.append("### Navy Plan")
            markdown_lines.append("")
            navy_header = "| " + " | ".join(section["navy"]["columns"]) + " |"
            navy_separator = "| " + " | ".join(["----"] * len(section["navy"]["columns"])) + " |"
            markdown_lines.extend([navy_header, navy_separator])
            
            for row in section["navy"]["rows"]:
                formatted_row = "| " + " | ".join(str(item) if item else "—" for item in row) + " |"
                markdown_lines.append(formatted_row)
            
            markdown_lines.append("")
        
        # Regular table if columns and rows are present
        elif "columns" in section and "rows" in section:
            header = "| " + " | ".join(section["columns"]) + " |"
            separator = "| " + " | ".join(["----"] * len(section["columns"])) + " |"
            markdown_lines.extend([header, separator])

            for row in section["rows"]:
                formatted_row = "| " + " | ".join(str(item) if item else "—" for item in row) + " |"
                markdown_lines.append(formatted_row)

            markdown_lines.append("")

        # Add notes below the table(s)
        if "notes" in section and section["notes"]:
            markdown_lines.append("### Notes")
            for note in section["notes"]:
                markdown_lines.append(f"- {note}")
            markdown_lines.append("")

    logging.debug("Finished conversion of JSON to Markdown.")
    return "\n".join(markdown_lines)

def convert_day_one_snapshot_to_markdown(snapshot: Dict[str, Any]) -> str:
    """Convert day one snapshot to markdown."""
    markdown_lines = ["## 0. Day-One Snapshot"]
    markdown_lines.append("")

    if "summary" in snapshot:
        markdown_lines.append(f"*{snapshot['summary']}*")
        markdown_lines.append("")

    if "oob" in snapshot:
        oob = snapshot["oob"]
        header = "| Type | Count | Notes |"
        separator = "| ---- | ---- | ---- |"
        markdown_lines.extend([header, separator])

        # Add OOB entries
        entries = [
            ("Divisions", oob.get("divisions", "—"), "Starting army"),
            ("Ships", oob.get("ships", "—"), "Starting navy"),
            ("Planes", oob.get("planes", "—"), "Starting air force"),
            ("Civilian Factories", oob.get("civ_factories", "—"), "Industrial base"),
            ("Military Factories", oob.get("mil_factories", "—"), "Production capacity"),
            ("Dockyards", oob.get("dockyards", "—"), "Naval production"),
            ("Research Slots", oob.get("research_slots", "—"), "Technology capacity")
        ]

        for entry_type, count, notes in entries:
            markdown_lines.append(format_table_row([entry_type, str(count), notes]))

    return "\n".join(markdown_lines)

def convert_focus_timeline_to_markdown(focuses: Dict[str, Any]) -> str:
    """Convert focus timeline to markdown table."""
    markdown_lines = ["## 1. National Focus Timeline"]
    markdown_lines.append("")

    # Create table header
    header = "| # | Start → End | Days | Focus | Tier | Prerequisites | Why |"
    separator = "| ---- | ---- | ---- | ---- | ---- | ---- | ---- |"
    markdown_lines.extend([header, separator])

    # Add each focus
    for i, focus in enumerate(focuses, 1):
        start = focus.get("start", "—")
        end = focus.get("end", "—")
        days = focus.get("days", "—")
        focus_name = focus.get("focus", "—")
        tier = focus.get("tier", "—")
        prereqs = focus.get("prereqs") or "—"
        why = focus.get("why", "—")

        # Format start → end
        start_end = f"{start} → {end}" if start != "—" and end != "—" else "—"

        row = [str(i), start_end, str(days), focus_name, str(tier), prereqs, why]
        markdown_lines.append(format_table_row(row))

    return "\n".join(markdown_lines)

def format_table_row(row: list) -> str:
    """Format a table row with proper spacing."""
    formatted_row = [str(item) if item else "—" for item in row]
    return "| " + " | ".join(formatted_row) + " |"

def process_json_files_in_directory(data_dir: str, guides_dir: str):
    """Process all JSON files from data directory and output to guides directory."""
    # Ensure guides directory exists
    os.makedirs(guides_dir, exist_ok=True)
    
    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            json_path = os.path.join(data_dir, filename)
            
            # Create output paths
            base_name = os.path.splitext(filename)[0]
            markdown_filename = f"{base_name}.md"
            checklist_filename = f"{base_name}-checklist.md"
            markdown_path = os.path.join(guides_dir, markdown_filename)

            try:
                logging.debug(f"Processing file: {json_path}")
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                markdown_content = convert_new_format_to_markdown(json_data, checklist_filename)

                with open(markdown_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                logging.info(f"✓ Generated: {markdown_path}")

            except Exception as e:
                logging.error(f"✗ Failed to process {filename}: {e}")

def main():
    """Main function to process JSON files from data directory to guides directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(repo_root, "data")
    guides_dir = os.path.join(repo_root, "guides")
    
    print(f"Processing JSON files from: {data_dir}")
    print(f"Outputting guides to: {guides_dir}")
    
    if not os.path.exists(data_dir):
        print(f"Data directory does not exist: {data_dir}")
        return
    
    process_json_files_in_directory(data_dir, guides_dir)

if __name__ == "__main__":
    main()
