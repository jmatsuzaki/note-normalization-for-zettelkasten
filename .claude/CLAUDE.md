# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**重要**: 日本語で回答してください。

## Overview

This is a modular Python tool for normalizing Markdown notes for Zettelkasten systems. The tool processes notes to add front matter (YAML, TOML, or JSON), rename files with UIDs, and convert WikiLinks to Markdown links.

### Project Structure

The codebase follows the standard Python `src` layout:

```
.
├── src/
│   └── zettelkasten_normalizer/
│       ├── __init__.py
│       ├── config.py                 # Configuration settings
│       ├── utils.py                  # Utility functions
│       ├── file_operations.py        # File discovery and validation
│       ├── frontmatter_parser.py     # Front matter parsing (YAML/TOML/JSON)
│       ├── yfm_processor.py          # Front Matter processing
│       ├── link_processor.py         # Link substitution and file renaming
│       └── normalization_zettel.py   # Main entry point
├── tests/
│   └── test_normalization_zettel.py  # Comprehensive test suite
├── run_normalization.py              # Command line entry point
└── setup.py                          # Package configuration
```

## Running the Tool

### Basic Usage

```bash
python run_normalization.py /path/to/your/zettelkasten_root_folder
```

### With Options

```bash
# Target specific folder/file
python run_normalization.py /path/to/root -t /path/to/target

# Use TOML front matter
python run_normalization.py /path/to/root -f toml

# Use JSON front matter
python run_normalization.py /path/to/root -f json

# Auto-answer yes to all prompts
python run_normalization.py /path/to/root -y

# Combine options
python run_normalization.py /path/to/root -t /path/to/target -f toml -y
```

### Git Hook Integration

For automated processing of changed files:

```bash
# In .git/hooks/pre-commit
git diff --cached --name-status | grep -e "^M" -e "^A" | while read a b; do
  python /path/to/run_normalization.py /path/to/zettelkasten_root -t "$b" -y
  git add "$b"
done
```

## Configuration

### Key Settings (lines 18-39 in normalization_zettel.py)

- `INBOX_DIR`: Folders where files get `draft: true` in YAML front matter
- `EXCLUDE_DIR`: Folders to skip during processing
- `EXCLUDE_FILE`: Files to skip during processing
- `NOTE_EXT`: Supported note file extensions (.md, .txt)
- `IMG_EXT`: Supported image extensions (.png, .jpg, .jpeg, .svg, .gif)

### Function Controls (lines 35-39)

- `function_create_yfm`: Add/update YAML front matter
- `function_rename_notes`: Rename notes to UUID and update links
- `function_rename_images`: Rename images to UUID and update links

## Architecture

### Core Functions

- `check_and_create_yfm()`: Creates/updates YAML front matter with title, date, tags, etc.
- `rename_notes_with_links()`: Renames note files to UUID format and updates all references
- `rename_images_with_links()`: Renames image files to UUID format and updates all references
- `substitute_wikilinks_to_markdown_links()`: Converts `[[wikilinks]]` to `[markdown](links)`

### File Processing Flow

1. Parse command line arguments for root path and options
2. Collect target files based on extensions and exclusion rules
3. Process YAML front matter (if enabled)
4. Rename notes to UUID and update links (if enabled)
5. Rename images to UUID and update links (if enabled)
6. Log all operations to `normalization_zettel.log`

### UUID Generation

- Uses UUID v4 (32-character hex without hyphens)
- Automatically checks for duplicates and regenerates if needed
- Markdown files move to root directory, images stay in place

## Requirements

- Python 3.9.1 or above
- Standard library only (no external dependencies)
- Designed for macOS (Windows/Linux support in TODO)

## Testing

This tool requires manual testing on a copy of your Zettelkasten before running on production data. No automated test suite is provided.

