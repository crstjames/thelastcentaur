#!/usr/bin/env python3
"""
Script to fix indentation issues in test_discovery_system.py
"""

import re

def fix_indentation(input_file, output_file):
    """Fix indentation issues in the test file."""
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split into lines
    lines = content.split('\n')
    
    # Track indentation state
    in_test_method = False
    method_indent = 0
    fixed_lines = []
    
    print("Fixing indentation...")
    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            fixed_lines.append(line)
            continue
        
        # Calculate leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        
        # Check if this is a test method definition
        if re.match(r'\s*def test_', line):
            in_test_method = True
            method_indent = leading_spaces
            fixed_lines.append(line)
            continue
        
        # Check if we're exiting a method (less indentation than method definition)
        if in_test_method and leading_spaces <= method_indent and not line.strip().startswith('#'):
            in_test_method = False
        
        # Fix indentation for lines in test methods
        if in_test_method:
            # Lines that should be indented more (like assertions after setup)
            if (re.search(r'assert', line) or 
                re.search(r'self\.assert', line) or 
                line.strip().startswith('#')):
                # Check if indentation is wrong (less than method + 4)
                if leading_spaces < method_indent + 8:
                    # Fix indentation to method + 8
                    line = ' ' * (method_indent + 8) + line.lstrip()
        
        fixed_lines.append(line)
    
    # Write fixed content
    print(f"Writing fixed content to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Done!")

if __name__ == "__main__":
    fix_indentation('tests/test_discovery_system.py', 'tests/test_discovery_system_fixed.py') 