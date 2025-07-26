#!/usr/bin/env python3
"""
Script to fix bad/special characters in JSON files.
Replaces Unicode special characters with standard ASCII equivalents.
"""

import json
import re
import sys
import os
from pathlib import Path


def fix_bad_characters(content):
    """
    Replace all problematic Unicode characters with standard ASCII equivalents.
    
    Args:
        content (str): The file content to clean
        
    Returns:
        str: Cleaned content with ASCII characters
    """
    # Define character replacements (excluding curly quotes to avoid issues)
    replacements = {
        # Dashes and arrows (main problem areas)
        '—': '-',  # Em dash
        '–': '-',  # En dash
        '−': '-',  # Minus sign
        '→': '-',  # Right arrow
        '⟶': '->',  # Long right arrow
        
        # Mathematical symbols
        '×': 'x',  # Multiplication sign
        '≥': '>=', # Greater than or equal
        '≤': '<=', # Less than or equal
        '≠': '!=', # Not equal
        '±': '+/-', # Plus-minus
        '∞': 'inf', # Infinity
        
        # Other problematic Unicode
        "’": "'", # Apostrophe (straight)

        # Other problematic Unicode
        '…': '...', # Horizontal ellipsis
        '°': 'deg', # Degree symbol
        '™': 'TM',  # Trademark
        '©': '(c)', # Copyright
        '®': '(R)', # Registered trademark
        '•': '*',   # Bullet point
        '‰': '%',   # Per mille (use % instead)
    }
    
    # Apply all replacements
    for bad_char, good_char in replacements.items():
        content = content.replace(bad_char, good_char)
    
    # Remove contentReference tags (from AI-generated content)
    content = re.sub(r' :contentReference\[oaicite:\d+\]\{index=\d+\}', '', content)
    
    return content


def validate_json(file_path):
    """
    Validate that a file contains valid JSON.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"JSON validation error: {e}")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False


def fix_json_file(file_path, backup=True):
    """
    Fix bad characters in a JSON file.
    
    Args:
        file_path (str): Path to the JSON file to fix
        backup (bool): Whether to create a backup before fixing
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"Error: File {file_path} does not exist")
        return False
    
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup if requested
        if backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"Backup created: {backup_path}")
        
        # Fix bad characters
        fixed_content = fix_bad_characters(original_content)
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Validate the result
        if validate_json(file_path):
            print(f"✅ Successfully fixed {file_path}")
            
            # Show what was changed
            if original_content != fixed_content:
                print("Fixed characters:")
                changes = []
                for bad_char, good_char in {
                    '—': '-', '–': '-', '−': '-', '→': '-', '⟶': '->',
                    '×': 'x', '≥': '>=', '≤': '<=', '≠': '!=', '±': '+/-',
                    '…': '...', '°': 'deg', '™': 'TM', '©': '(c)', '®': '(R)',
                    '•': '*', '‰': '%'
                }.items():
                    if bad_char in original_content:
                        count = original_content.count(bad_char)
                        changes.append(f"  {bad_char} → {good_char} ({count} occurrences)")
                
                if changes:
                    for change in changes:
                        print(change)
                else:
                    print("  No character replacements needed, but other fixes applied")
            else:
                print("  No changes needed - file was already clean")
            
            return True
        else:
            print(f"❌ Error: Fixed file is not valid JSON")
            # Restore from backup if validation fails
            if backup:
                with open(backup_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                print(f"Restored original file from backup")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False


def process_data_directory(data_dir: str, backup: bool = True):
    """
    Process all JSON files in the data directory.
    
    Args:
        data_dir (str): Path to the data directory
        backup (bool): Whether to create backups before fixing
        
    Returns:
        tuple: (success_count, total_count)
    """
    if not os.path.exists(data_dir):
        print(f"Data directory does not exist: {data_dir}")
        return 0, 0
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return 0, 0
    
    success_count = 0
    total_count = len(json_files)
    
    print(f"Processing {total_count} JSON file(s) in {data_dir}...")
    print("")
    
    for filename in json_files:
        file_path = os.path.join(data_dir, filename)
        if fix_json_file(file_path, backup=backup):
            success_count += 1
        print("")  # Add spacing between files
    
    return success_count, total_count


def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python fix_json_characters.py <json_file> [--no-backup]")
        print("       python fix_json_characters.py *.json [--no-backup]")
        print("       python fix_json_characters.py --data-dir [--no-backup]")
        print("")
        print("Examples:")
        print("  python fix_json_characters.py argentina_full.json")
        print("  python fix_json_characters.py *.json")
        print("  python fix_json_characters.py data.json --no-backup")
        print("  python fix_json_characters.py --data-dir")
        sys.exit(1)
    
    # Parse arguments
    files = []
    backup = True
    use_data_dir = False
    
    for arg in sys.argv[1:]:
        if arg == '--no-backup':
            backup = False
        elif arg == '--data-dir':
            use_data_dir = True
        elif arg.endswith('.json'):
            files.append(arg)
        else:
            # Try to expand glob patterns
            from glob import glob
            expanded = glob(arg)
            files.extend([f for f in expanded if f.endswith('.json')])
    
    # Handle data directory mode
    if use_data_dir:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(os.path.dirname(script_dir))
        data_dir = os.path.join(repo_root, "data")
        
        success_count, total_count = process_data_directory(data_dir, backup)
        
        # Summary
        print(f"Summary: {success_count}/{total_count} files processed successfully")
        
        if success_count < total_count:
            sys.exit(1)
        return
    
    if not files:
        print("No JSON files specified")
        sys.exit(1)
    
    # Process each file
    success_count = 0
    total_count = len(files)
    
    print(f"Processing {total_count} file(s)...")
    print("")
    
    for file_path in files:
        if fix_json_file(file_path, backup=backup):
            success_count += 1
        print("")  # Add spacing between files
    
    # Summary
    print(f"Summary: {success_count}/{total_count} files processed successfully")
    
    if success_count < total_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
