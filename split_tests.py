#!/usr/bin/env python3
"""
Script to split the large test_discovery_system.py file into multiple smaller test files.
"""

import os
import re

def split_test_file(input_file, output_dir):
    """Split a large test file into multiple smaller test files."""
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract imports and common setup code
    imports_match = re.search(r'^(.*?)def test_', content, re.DOTALL)
    if imports_match:
        imports_and_setup = imports_match.group(1)
    else:
        imports_and_setup = ""
    
    # Find all test functions
    test_pattern = re.compile(r'def (test_[a-zA-Z0-9_]+).*?(?=def test_|\Z)', re.DOTALL)
    test_matches = list(test_pattern.finditer(content))
    
    print(f"Found {len(test_matches)} test functions.")
    
    # Group tests into files (approximately 5-10 tests per file)
    tests_per_file = 5
    num_files = (len(test_matches) + tests_per_file - 1) // tests_per_file
    
    for file_index in range(num_files):
        start_idx = file_index * tests_per_file
        end_idx = min((file_index + 1) * tests_per_file, len(test_matches))
        
        # Create file content with imports and tests
        file_content = imports_and_setup
        
        # Add test functions
        for i in range(start_idx, end_idx):
            match = test_matches[i]
            test_name = match.group(1)
            test_code = match.group(0)
            
            # Fix indentation in test code
            fixed_test_code = fix_test_indentation(test_code)
            file_content += fixed_test_code
        
        # Write to file
        output_file = os.path.join(output_dir, f"test_discovery_{file_index + 1}.py")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        print(f"Created {output_file} with {end_idx - start_idx} tests.")

def fix_test_indentation(test_code):
    """Fix indentation issues in a test function."""
    lines = test_code.split('\n')
    fixed_lines = []
    
    # Get the indentation of the function definition
    first_line = lines[0]
    function_indent = len(first_line) - len(first_line.lstrip())
    
    fixed_lines.append(lines[0])  # Add function definition line
    
    for i in range(1, len(lines)):
        line = lines[i]
        if not line.strip():
            fixed_lines.append(line)
            continue
        
        # Calculate leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        
        # Check if this is a new function definition
        if line.lstrip().startswith('def '):
            fixed_lines.append(line)
            continue
        
        # Fix indentation for lines in test methods
        if leading_spaces <= function_indent and line.strip() and not line.strip().startswith('#'):
            # This is likely a line that should be indented
            fixed_line = ' ' * (function_indent + 4) + line.lstrip()
        else:
            fixed_line = line
        
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)

if __name__ == "__main__":
    split_test_file('tests/test_discovery_system.py', 'tests/discovery') 