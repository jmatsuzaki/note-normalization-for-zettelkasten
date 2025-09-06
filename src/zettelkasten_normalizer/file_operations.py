"""
File operations for Zettelkasten note normalization.
"""

import os
import uuid
import re
import logging
from .config import EXCLUDE_DIR, EXCLUDE_FILE, NOTE_EXT, IMG_EXT
from .utils import get_file_name

# Get logger
logger = logging.getLogger(__name__)


def get_files(start_path, type):
    """Retrieves a file of the specified path and type"""
    files = []
    if os.path.isfile(start_path):
        if check_note_type(start_path, type):
            files.append(start_path)
    else:
        # get all files
        for pathname, dirnames, filenames in os.walk(start_path, topdown=True):
            # exclude dir and files
            dirnames[:] = list(filter(lambda d: not d in EXCLUDE_DIR, dirnames))
            filenames[:] = list(filter(lambda f: not f in EXCLUDE_FILE, filenames))
            dirnames[:] = list(
                filter(lambda d: not d[0] == ".", dirnames)
            )  # Hidden directory beginning with "."
            filenames[:] = list(
                filter(lambda f: not f[0] == ".", filenames)
            )  # Hidden files beginning with "."
            for filename in filenames:
                file_path = os.path.join(pathname, filename)
                if check_note_type(file_path, type):
                    # append target notes to array
                    files.append(file_path)
    return files


def check_note_type(file_path, type):
    """Check if the specified file has an extension of the specified type"""
    if type == "note":
        target_ext = tuple(NOTE_EXT)
    elif type == "image":
        target_ext = tuple(IMG_EXT)
    # Filtering files
    if file_path.endswith(target_ext):
        return True
    else:
        return False


def check_note_has_uid(file):
    """Check if a note file already has a UID as filename"""
    file_title = get_file_name(file)[1]
    return re.match("^[a-f0-9]{32}$", file_title)


def get_new_filepath_with_uid(file, root_path):
    """get new filepath with uid"""
    # UID is UUID v4 (32-digit hexadecimal without hyphens)
    uid = uuid.uuid4().hex
    ext = get_file_name(file)[2]
    # Target path to check for duplicate UID
    if ext == ".md":
        path = root_path
    else:
        path = os.path.dirname(file)
    # Generate new UUID if duplicated (very unlikely but possible)
    while os.path.exists(build_filepath_by_uid(uid, path, ext)):
        uid = uuid.uuid4().hex
    return build_filepath_by_uid(uid, path, ext)


def build_filepath_by_uid(uid, path, ext=".md"):
    """Build file path using UID"""
    return path + "/" + str(uid) + ext