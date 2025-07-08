# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**重要**: 日本語で回答してください。

## Overview

This is a Python tool for normalizing Markdown notes for Zettelkasten systems. The tool processes notes to add YAML front matter, rename files with UIDs, and convert WikiLinks to Markdown links.

## Running the Tool

### Basic Usage

```bash
python normalization_zettel.py /path/to/your/zettelkasten_root_folder
```

### With Options

```bash
# Target specific folder/file
python normalization_zettel.py /path/to/root -t /path/to/target

# Auto-answer yes to all prompts
python normalization_zettel.py /path/to/root -y

# Combine options
python normalization_zettel.py /path/to/root -t /path/to/target -y
```

### Git Hook Integration

For automated processing of changed files:

```bash
# In .git/hooks/pre-commit
git diff --cached --name-status | grep -e "^M" -e "^A" | while read a b; do
  python /path/to/normalization_zettel.py /path/to/zettelkasten_root -t "$b" -y
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

