# Note normalization for Zettelkasten
Note normalization for Zettelkasten. Add Yaml Front Matter, add UIDs and rename files, replace Wikilink with Markdown link, etc.

## DEMO

## Features

- Automatically generate Yaml Front Matter from the note information and insert it into the header
- Move hashtags to Yaml Front Matter
- Rename the file to UID
- Move the Markdown file to the Zettelkasten's root folder
- Replace link (filename and folder)
- Change Wikilinks to Markdown links (with Relative Paths and Extensions)
- Support for Markdown files and images

## Requirements

- Python 3.9.1 or above

## Installation

Download or Git clone this repository

## Usage

Just run "normalization_zettel.py".
The first argument is the root folder of Zettelkasten.

```
python normalization_zettel.py /path/to/your/zettelkasten_root_folder
```

## Note

This program is mainly designed to fix my Zettelkasten, so if you use it, please test it beforehand to make sure it fits your Zettelkasten well.

You can check the results of the program execution in the "debug.log" file in the same folder.

It is recommended that you first copy all of your Zettelkasten and test run in the copied folder. Then check the file after the run and make sure the notes are modified as expected in copied folder.

It is strongly recommended to back up Zettelkasten using a mechanism such as git, even when running on production data. Not only should you be able to revert to the pre-run data, but you should also be able to see the differences for each file, like in Git diff, and repair them if necessary.

## Future works (TODO)

- Windows and Linux support
- Specify the file
- Toml and json Front Matter support

## Author

- [jMatsuzaki](https://jmatsuzaki.com/)
- [jMatsuzaki Inc.](https://jmatsuzaki.com/company)
- [@jmatsuzaki](https://twitter.com/jmatsuzaki)
