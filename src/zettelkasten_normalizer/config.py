"""
Configuration settings for Zettelkasten note normalization.
"""

# Directory and file settings
INBOX_DIR = [
    "Inbox",
    "Draft", 
    "Pending",
]  # The files in this folder will have the YFM draft key set to true

EXCLUDE_DIR = {
    "Backup", 
    "Template", 
    "tmp", 
    "node_modules"
}  # Folders not to be processed (Hidden folders and files are not covered by default)

EXCLUDE_FILE = {
    "tags"
}  # Files not to be processed (Hidden folders and files are not covered by default)

# File extension settings
NOTE_EXT = [".md", ".txt"]  # Note file extension
IMG_EXT = [".png", ".jpg", ".jpeg", ".svg", ".gif"]  # image file extension

# YFM default settings
YFM = {
    "title": "",  # It will be replaced by the file name
    "aliases": "[]",
    "date": "",  # Replaced by the file creation date
    "update": "",  # Replaced by the file modification date
    "tags": "[]",  # If you have a hashtag, it will be generated automatically
    "draft": "false",  # The following note will be true for the folder specified as INBOX_DIR
}

# Function execution settings
EXECUTION_FUNCTION_LIST = {
    "function_create_yfm": True,  # If there is no Yaml FrontMatter at the beginning of the note, it will be generated
    "function_rename_notes": True,  # Replace the file name of the note with the UID and replace the linked parts from other notes
    "function_rename_images": True,  # Replace the file name of the image with the UID and replace the linked part from the other note
}