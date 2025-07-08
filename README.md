# Note normalization for Zettelkasten #

Note normalization for Zettelkasten. Add Yaml Front Matter, add UIDs and rename files, replace Wikilink with Markdown link, etc.

Normalizing notes reduces dependence on tools and increases the flexibility and independence of Zettelkasten notes. This is useful for transforming a knowledge notebook into a permanent notebook.

1. [Screenshots](#screenshots)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Note](#note)
8. [Development](#development)
9. [Future works (TODO)](#future-works-todo)
10. [Author](#author)
11. [Preview images](#preview-images)

## Screenshots ##

![Screenshots](img/readme_screenshots.png)

## Features ##

- Automatically generate Front Matter from the note information and insert it into the header
- Support for multiple front matter formats: **YAML**, **TOML**, and **JSON**
- Move hashtags to Front Matter
- Rename the file to UUID
- Move the Markdown file to the Zettelkasten's root folder
- Replace link (filename and folder)
- Change Wikilinks to Markdown links (with Relative Paths and Extensions)
- Support for Markdown files and images

## Project Structure ##

The project follows the standard Python `src` layout:

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

## Requirements ##

- Python 3.9.1 or above

## Installation ##

Download or clone this repository.

```bash
git clone https://github.com/jmatsuzaki/note-normalization-for-zettelkasten.git
cd note-normalization-for-zettelkasten
```

### Option 1: Direct Usage (Recommended)

No installation required. Just use the `run_normalization.py` script directly:

```bash
python run_normalization.py /path/to/your/zettelkasten_root_folder
```

### Option 2: Install as Package

If you want to install it as a package:

```bash
pip install -e .
```

After installation, you can use:

```bash
zettelkasten-normalizer /path/to/your/zettelkasten_root_folder
```

## Usage ##

### Basic Usage

```bash
python run_normalization.py /path/to/your/zettelkasten_root_folder
```

### Command Line Options

- **Positional arguments:**
  - `root`: Zettelkasten's root folder

- **Optional arguments:**
  - `-h, --help`: Show help message and exit
  - `-t TARGET, --target TARGET`: Normalization target folder or file
  - `-y, --yes`: Automatically answer yes to all questions
  - `-f FORMAT, --format FORMAT`: Front matter format (yaml, toml, json). Default: yaml

### Examples

```bash
# Process entire Zettelkasten (default YAML format)
python run_normalization.py ~/Documents/MyZettelkasten

# Process with TOML front matter
python run_normalization.py ~/Documents/MyZettelkasten -f toml

# Process with JSON front matter
python run_normalization.py ~/Documents/MyZettelkasten -f json

# Process specific file
python run_normalization.py ~/Documents/MyZettelkasten -t ~/Documents/MyZettelkasten/new-note.md

# Process without confirmation prompts
python run_normalization.py ~/Documents/MyZettelkasten -y
```

### Git Hook Integration

To automatically process changed files, add this to your pre-commit hook (`.git/hooks/pre-commit`):

```bash
#!/bin/bash
git diff --cached --name-status | grep -e "^M" -e "^A" | while read a b; do
  python /path/to/run_normalization.py /path/to/your/zettelkasten_root_folder -t "$b" -y
  git add "$b"
done
```

### Logging

The execution log is saved to `normalization_zettel.log` in the current directory.

## Note ##

This program is mainly designed to fix my Zettelkasten, so if you use it, please test it beforehand to make sure it fits your Zettelkasten well.

### Testing Recommendations

1. **Test on a Copy First**: Create a copy of your Zettelkasten and test the tool on the copy before running it on your actual data.

2. **Check Logs**: Review the execution results in `normalization_zettel.log`.

3. **Use Version Control**: It is strongly recommended to use Git or another version control system with your Zettelkasten. This allows you to:
   - Revert changes if needed
   - Review differences with `git diff`
   - Repair specific changes if necessary

### Configuration

You can modify the behavior by editing `src/zettelkasten_normalizer/config.py`:

- `FRONT_MATTER_FORMAT`: Default front matter format ("yaml", "toml", "json")
- `INBOX_DIR`: Folders where files get `draft: true` in front matter
- `EXCLUDE_DIR`: Folders to skip during processing
- `EXCLUDE_FILE`: Files to skip during processing
- `NOTE_EXT`: Supported note file extensions
- `IMG_EXT`: Supported image extensions

### Front Matter Formats

The tool supports three front matter formats:

**YAML (default)**
```yaml
---
title: Note Title
tags: [tag1, tag2]
draft: false
---
```

**TOML**
```toml
+++
title = "Note Title"
tags = ["tag1", "tag2"]
draft = false
+++
```

**JSON**
```json
{
  "title": "Note Title",
  "tags": ["tag1", "tag2"],
  "draft": false
}
```

## Development ##

### Running Tests

```bash
python -m pytest tests/
# or
python tests/test_normalization_zettel.py
```

### Development Installation

```bash
pip install -e ".[dev]"
```

This installs development dependencies including pytest, black, flake8, and mypy.

## Future works (TODO) ##

- Windows and Linux support
- Option to execute only certain functions
- TOML parsing optimization for older Python versions

## Author ##

- [jMatsuzaki](https://jmatsuzaki.com/)
- [jMatsuzaki Inc.](https://jmatsuzaki.com/company)
- [@jmatsuzaki](https://twitter.com/jmatsuzaki)

## Preview images ##

Preview images were taken using:

- [iTerm2](https://iterm2.com/) terminal emulator on macOS
- [onedark.vim](https://github.com/joshdick/onedark.vim) on [Neovim](https://github.com/neovim/neovim)
