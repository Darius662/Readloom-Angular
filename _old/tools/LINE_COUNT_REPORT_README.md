# Line Count Report Generator

A comprehensive Python utility for analyzing the codebase structure and line counts of the Readloom project.

## Overview

`line_count_report.py` generates detailed reports showing:
- **Project structure** as a hierarchical file tree
- **Line counts** for every Python file
- **Component breakdown** (Backend, Frontend, Other)
- **Summary statistics** (total files, lines, averages)
- **Sorting capabilities** to identify largest/smallest files

## Features

### 📊 Three View Modes

#### 1. **Tree View** (Default)
Displays the project structure as a hierarchical tree with line counts for each file.

```bash
python line_count_report.py
```

**Output:**
```
Readloom/
|-- Readloom.py (366 lines)
|-- backend/
|   |-- base/
|   |   |-- helpers.py (442 lines)
|   |   +-- logging.py (63 lines)
|   |-- features/
|   |   |-- calendar/
|   |   |   +-- calendar.py (348 lines)
...
```

#### 2. **Sorted View - Descending** (Largest First)
Lists all files sorted by line count from largest to smallest.

```bash
python line_count_report.py --sort
```

**Output:**
```
FILES SORTED BY LINE COUNT
========================================================================================================================

frontend\api.py                                                                      2292 lines
backend\features\ebook_files.py                                                       973 lines
backend\features\collection\collections.py                                            827 lines
...
```

#### 3. **Sorted View - Ascending** (Smallest First)
Lists all files sorted by line count from smallest to largest.

```bash
python line_count_report.py --sort-asc
```

**Output:**
```
FILES SORTED BY LINE COUNT
========================================================================================================================

backend\features\metadata_providers\anilist\__init__.py                                 6 lines
backend\migrations\__init__.py                                                          6 lines
backend\features\scrapers\__init__.py                                                   7 lines
...
```

## Usage

### Basic Commands

```bash
# Show tree view (default)
python line_count_report.py

# Sort by line count (descending - largest first)
python line_count_report.py --sort

# Sort by line count (ascending - smallest first)
python line_count_report.py --sort-asc

# Show help
python line_count_report.py --help
```

### Command-Line Arguments

| Argument | Description |
|----------|-------------|
| (none) | Display hierarchical tree view |
| `--sort` | Sort files by line count (descending) |
| `--sort-asc` | Sort files by line count (ascending) |
| `--help`, `-h` | Show help message |

## Features

### ✅ Gitignore Support
- Automatically reads `.gitignore` file
- Excludes all patterns listed in `.gitignore`
- Respects directory patterns (e.g., `data/`, `logs/`)
- Handles glob patterns (e.g., `*.db`, `__pycache__/`)
- Skips ignored files in all views

### ✅ Comprehensive Statistics
- **Total Files**: Count of all Python files
- **Total Lines**: Sum of all lines across files
- **Average Lines per File**: Mean lines per file
- **Component Breakdown**:
  - Backend: Files and lines in `backend/`
  - Frontend: Files and lines in `frontend/`
  - Other: Files and lines in other directories

### ✅ Flexible Output
- Tree view with proper indentation
- Sorted views for easy analysis
- Consistent formatting across all views
- Clear section headers and separators

## Output Example

```
========================================================================================================================
READLOOM PROJECT - LINE COUNT REPORT
========================================================================================================================

PROJECT STRUCTURE
========================================================================================================================

Readloom/
|-- Readloom.py (366 lines)
|-- backend/
|   |-- base/
|   |   |-- custom_exceptions.py (36 lines)
|   |   |-- definitions.py (99 lines)
|   |   |-- helpers.py (442 lines)
|   |   +-- logging.py (63 lines)
|-- frontend/
|   |-- api/
|   |   |-- authors/
|   |   |   |-- __init__.py (18 lines)
|   |   |   |-- crud.py (141 lines)
|   |   |   +-- routes.py (164 lines)
...

========================================================================================================================
SUMMARY
========================================================================================================================
Total Files: 309
Total Lines: 40724
Average Lines per File: 131
========================================================================================================================

========================================================================================================================
BY COMPONENT
========================================================================================================================
Backend:  145 files,  20129 lines (avg: 138 lines/file)
Frontend:  75 files,  12112 lines (avg: 161 lines/file)
Other:     89 files,   8483 lines (avg: 95 lines/file)
------------------------------------------------------------------------------------------------------------------------
Total:    309 files,  40724 lines (avg: 131 lines/file)
========================================================================================================================
```

## Use Cases

### 📈 Code Analysis
- Identify the largest files in the project
- Find files that might need refactoring
- Understand code distribution across components

### 🔍 Project Overview
- Get a quick overview of project structure
- See which directories contain the most code
- Understand the scale of the project

### 🎯 Performance Optimization
- Identify bottleneck files by size
- Find opportunities for modularization
- Track code growth over time

### 📊 Team Communication
- Share project statistics with team members
- Document codebase structure
- Identify areas for code review focus

## Technical Details

### Dependencies
- Python 3.7+
- Standard library only (no external dependencies)

### Supported Patterns
The script respects `.gitignore` patterns including:
- Directory patterns: `data/`, `logs/`
- File patterns: `*.db`, `*.log`
- Glob patterns: `__pycache__/`, `.venv/`
- Wildcard patterns: `*.py[cod]`

### Performance
- Scans entire project structure
- Counts lines for all Python files
- Generates report in seconds
- Minimal memory footprint

## Tips & Tricks

### Find Large Files
```bash
python line_count_report.py --sort
```
Shows the largest files first - great for identifying refactoring candidates.

### Find Small Files
```bash
python line_count_report.py --sort-asc
```
Shows the smallest files first - useful for understanding module structure.

### Analyze Specific Component
Use the tree view and look for specific directories:
```bash
python line_count_report.py | grep "backend/features"
```

### Export Results
```bash
python line_count_report.py > report.txt
python line_count_report.py --sort > sorted_report.txt
```

## Troubleshooting

### No Output
- Ensure you're in the Readloom project root directory
- Check that `.gitignore` file exists
- Verify Python 3.7+ is installed

### Missing Files
- Check `.gitignore` - files may be excluded
- Ensure files have `.py` extension
- Verify files are readable

### Encoding Issues
- Script handles UTF-8 encoding automatically
- Falls back gracefully on encoding errors

## Contributing

To improve this script:
1. Add new sorting options
2. Enhance gitignore pattern matching
3. Add filtering capabilities
4. Improve output formatting
5. Add export formats (JSON, CSV, etc.)

## License

Part of the Readloom project. See main project LICENSE for details.

## Related Files

- `.gitignore` - Patterns for files to exclude
- `Readloom.py` - Main application entry point
- `requirements.txt` - Project dependencies

---

**Last Updated**: November 11, 2025  
**Version**: 1.0  
**Maintained by**: Readloom Development Team
