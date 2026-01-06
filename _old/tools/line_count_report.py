#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Line Count Report Generator for Readloom Project
Generates a comprehensive report of all Python files and their line counts.

Usage:
    python line_count_report.py              # Normal tree view
    python line_count_report.py --sort       # Sort by line count (descending)
    python line_count_report.py --sort-asc   # Sort by line count (ascending)
"""

import os
import sys
from pathlib import Path
from collections import defaultdict
import fnmatch


def count_lines(file_path):
    """Count lines in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def get_relative_path(file_path, root_path):
    """Get relative path from root."""
    return os.path.relpath(file_path, root_path)


def load_gitignore_patterns(root_path):
    """Load patterns from .gitignore file."""
    gitignore_path = root_path / ".gitignore"
    patterns = []
    
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}")
    
    return patterns


def should_ignore(file_path, root_path, patterns):
    """Check if file should be ignored based on gitignore patterns."""
    relative_path = os.path.relpath(file_path, root_path)
    
    for pattern in patterns:
        # Handle directory patterns
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if relative_path.startswith(pattern):
                return True
        
        # Handle glob patterns
        if fnmatch.fnmatch(relative_path, pattern):
            return True
        
        # Handle patterns with wildcards
        if fnmatch.fnmatch(relative_path, f"*/{pattern}"):
            return True
        
        # Check if any parent directory matches
        for part in relative_path.split(os.sep):
            if fnmatch.fnmatch(part, pattern):
                return True
    
    return False


def print_tree(directory_structure, prefix="", is_last=True):
    """Print directory tree structure."""
    for i, (name, content) in enumerate(directory_structure.items()):
        is_last_item = i == len(directory_structure) - 1
        
        # Print current item
        connector = "└── " if is_last_item else "├── "
        print(f"{prefix}{connector}{name}")
        
        # Print children if it's a directory
        if isinstance(content, dict):
            extension = "    " if is_last_item else "│   "
            print_tree(content, prefix + extension, is_last_item)


def build_tree_structure(files_by_directory):
    """Build a tree structure from files by directory."""
    tree = {}
    
    for directory, files in sorted(files_by_directory.items()):
        if directory == "root":
            # Add root files directly
            for file_path, lines in sorted(files):
                file_name = os.path.basename(file_path)
                tree[f"{file_name} ({lines} lines)"] = None
        else:
            # Build nested structure
            parts = directory.split(os.sep)
            current = tree
            
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add files to this directory
            for file_path, lines in sorted(files):
                file_name = os.path.basename(file_path)
                current[f"{file_name} ({lines} lines)"] = None
    
    return tree


def print_tree_recursive(tree, prefix="", is_last=True):
    """Recursively print tree structure."""
    items = sorted(tree.items())
    for i, (name, content) in enumerate(items):
        is_last_item = i == len(items) - 1
        connector = "+-- " if is_last_item else "|-- "
        current_prefix = prefix
        
        print(f"{current_prefix}{connector}{name}")
        
        # If it's a directory (has content), print its children
        if isinstance(content, dict) and content:
            extension = "    " if is_last_item else "|   "
            print_tree_recursive(content, prefix + extension, is_last_item)


def generate_report(sort_mode=None):
    """Generate comprehensive line count report.
    
    Args:
        sort_mode: None for tree view, 'desc' for descending, 'asc' for ascending
    """
    root_path = Path(__file__).parent
    
    # Load gitignore patterns
    gitignore_patterns = load_gitignore_patterns(root_path)
    
    # Collect all Python files
    files_by_directory = defaultdict(list)
    all_files = []  # For sorting
    total_lines = 0
    total_files = 0
    
    print("=" * 120)
    print("READLOOM PROJECT - LINE COUNT REPORT")
    if sort_mode == 'desc':
        print("(Sorted by line count - DESCENDING)")
    elif sort_mode == 'asc':
        print("(Sorted by line count - ASCENDING)")
    print("=" * 120)
    print()
    
    # Walk through all directories
    for py_file in sorted(root_path.rglob("*.py")):
        # Skip files matching gitignore patterns
        if should_ignore(py_file, root_path, gitignore_patterns):
            continue
        
        lines = count_lines(py_file)
        relative_path = get_relative_path(py_file, root_path)
        
        # Get directory for grouping
        directory = os.path.dirname(relative_path)
        if not directory:
            directory = "root"
        
        files_by_directory[directory].append((relative_path, lines))
        all_files.append((relative_path, lines))
        total_lines += lines
        total_files += 1
    
    # Print based on sort mode
    if sort_mode:
        # Sorted view
        print("FILES SORTED BY LINE COUNT")
        print("=" * 120)
        print()
        
        # Sort files
        reverse = sort_mode == 'desc'
        sorted_files = sorted(all_files, key=lambda x: x[1], reverse=reverse)
        
        for file_path, lines in sorted_files:
            print(f"{file_path:<80} {lines:>8} lines")
    else:
        # Tree view
        print("PROJECT STRUCTURE")
        print("=" * 120)
        print()
        print("Readloom/")
        
        tree_structure = build_tree_structure(files_by_directory)
        print_tree_recursive(tree_structure)
    
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"Total Files: {total_files}")
    print(f"Total Lines: {total_lines}")
    print(f"Average Lines per File: {total_lines // total_files if total_files > 0 else 0}")
    print("=" * 120)
    
    # Print by component
    print()
    print("=" * 120)
    print("BY COMPONENT")
    print("=" * 120)
    
    backend_lines = sum(lines for dir_name, files in files_by_directory.items() 
                       for _, lines in files if dir_name.startswith("backend"))
    backend_files = sum(len(files) for dir_name, files in files_by_directory.items() 
                       if dir_name.startswith("backend"))
    
    frontend_lines = sum(lines for dir_name, files in files_by_directory.items() 
                        for _, lines in files if dir_name.startswith("frontend"))
    frontend_files = sum(len(files) for dir_name, files in files_by_directory.items() 
                        if dir_name.startswith("frontend"))
    
    other_lines = total_lines - backend_lines - frontend_lines
    other_files = total_files - backend_files - frontend_files
    
    print(f"Backend:  {backend_files:>3} files, {backend_lines:>6} lines (avg: {backend_lines // backend_files if backend_files > 0 else 0} lines/file)")
    print(f"Frontend: {frontend_files:>3} files, {frontend_lines:>6} lines (avg: {frontend_lines // frontend_files if frontend_files > 0 else 0} lines/file)")
    print(f"Other:    {other_files:>3} files, {other_lines:>6} lines (avg: {other_lines // other_files if other_files > 0 else 0} lines/file)")
    print("-" * 120)
    print(f"Total:    {total_files:>3} files, {total_lines:>6} lines (avg: {total_lines // total_files if total_files > 0 else 0} lines/file)")
    print("=" * 120)


if __name__ == "__main__":
    sort_mode = None
    
    # Parse command-line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == '--sort':
            sort_mode = 'desc'
        elif arg == '--sort-asc':
            sort_mode = 'asc'
        elif arg in ['--help', '-h']:
            print(__doc__)
            sys.exit(0)
    
    generate_report(sort_mode)
