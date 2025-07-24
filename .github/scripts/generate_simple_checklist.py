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
    
    # Remove file extension and clean up title
    base_name = os.path.splitext(source_filename)[0].replace('_', ' ').replace('-', ' ')
    
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
                checklist_lines.append("- [ ] Review this section")
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

def extract_table_items(content: str) -> list:
    """Extract items from markdown tables."""
    items = []
    
    # Find all table rows (lines with |)
    lines = content.split('\n')
    in_table = False
    
    for line in lines:
        line = line.strip()
        
        # Skip table header separators
        if '---' in line and '|' in line:
            in_table = True
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
            
            # Skip header rows
            if any(word in ' '.join(cells).lower() for word in ['date', 'finish', 'slot', 'class', 'asset', 'phase', 'war']):
                if not any(char.isdigit() for char in ' '.join(cells)):
                    continue
            
            # Create item from meaningful cells
            if len(cells) >= 2:
                meaningful_cells = [cell for cell in cells if cell and len(cell) > 1]
                if meaningful_cells:
                    # Use date + action format if first cell looks like a date
                    first_cell = meaningful_cells[0]
                    if any(pattern in first_cell.lower() for pattern in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']) or re.search(r'\d{1,2}', first_cell):
                        # Date + action format
                        if len(meaningful_cells) >= 2:
                            items.append(f"**{first_cell}**: {meaningful_cells[1]}")
                        else:
                            items.append(first_cell)
                    else:
                        # Just combine first two meaningful cells
                        if len(meaningful_cells) >= 2:
                            items.append(f"{meaningful_cells[0]} → {meaningful_cells[1]}")
                        else:
                            items.append(meaningful_cells[0])
    
    return items

def extract_bullet_items(content: str) -> list:
    """Extract items from bullet points."""
    items = []
    
    # Find bullet points (lines starting with * or -)
    bullet_pattern = r'^\s*[\*\-]\s*(.+)$'
    
    for match in re.finditer(bullet_pattern, content, re.MULTILINE):
        bullet_text = match.group(1).strip()
        if bullet_text and len(bullet_text) > 3:  # Skip very short items
            # Remove any existing markdown formatting
            bullet_text = re.sub(r'\*\*(.*?)\*\*', r'\1', bullet_text)
            items.append(bullet_text)
    
    return items

def generate_checklist_for_file(input_file: str, output_dir: str = "checklists"):
    """Generate checklist for a single file."""
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        return False
    
    # Skip README files
    if 'readme' in os.path.basename(input_file).lower():
        print(f"Skipping README file: {input_file}")
        return False
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        source_filename = os.path.basename(input_file)
        checklist_content = process_guide_to_checklist(content, source_filename)
        
        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate output filename
        base_name = os.path.splitext(source_filename)[0]
        output_file = os.path.join(output_dir, f"{base_name}-checklist.md")
        
        # Write checklist
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(checklist_content)
        
        print(f"✓ Generated: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error processing {input_file}: {e}")
        return False

def process_all_guides(directory: str = "."):
    """Process all markdown files in directory."""
    
    md_files = glob.glob(os.path.join(directory, "*.md"))
    
    if not md_files:
        print("No .md files found in current directory")
        return
    
    print(f"Found {len(md_files)} markdown files")
    
    success_count = 0
    for md_file in md_files:
        if generate_checklist_for_file(md_file):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{len(md_files)} files processed successfully")

def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) == 1:
        # Process all files in current directory
        print("Processing all .md files in current directory...")
        process_all_guides()
    elif len(sys.argv) == 2:
        # Process single file
        input_file = sys.argv[1]
        generate_checklist_for_file(input_file)
    else:
        print("Usage:")
        print(f"  {sys.argv[0]}                    # Process all .md files")
        print(f"  {sys.argv[0]} <input.md>        # Process single file")

if __name__ == "__main__":
    main()
