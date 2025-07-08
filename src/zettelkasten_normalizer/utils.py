"""
Utility functions for Zettelkasten note normalization.
"""

import os
import datetime
import platform
import unicodedata
import logging
import sys
from logging import Formatter
from logging.handlers import RotatingFileHandler


def setup_logger(log_dir):
    """setup logger"""
    if os.path.isdir(log_dir):
        # Put a slash at the end
        log_dir = os.path.join(log_dir, "")
    else:
        print("The specified root folder does not exist")
        print("Abort the process")
        print("You can see how to use it with the -h option")
        sys.exit()
    log_file_format = "%(asctime)s [%(levelname)s] %(message)s"
    log_console_format = "%(message)s"
    # main logger
    logger = logging.getLogger(__name__)
    # console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(Formatter(log_console_format))
    # logger.addHandler(console_handler)
    file_handler = RotatingFileHandler(
        "{}normalization_zettel.log".format(log_dir), maxBytes=1000000, backupCount=3
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(Formatter(log_file_format))

    # common config
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[console_handler, file_handler],
    )
    return logger


def get_file_name(file_path):
    """Retrieves a file name from the specified path. The format of the return value is as below:
    ('filename.ext', 'filename', '.ext')"""
    fullname = unicodedata.normalize("NFC", os.path.basename(file_path))
    name = os.path.splitext(fullname)[0]
    ext = os.path.splitext(fullname)[1]
    return (fullname, name, ext)


def get_dir_name(file_path):
    """Retrieves a folder name from the specified path. The format of the return value is as below:
    ('fullpath', 'basepath')"""
    fullpath = unicodedata.normalize("NFC", os.path.dirname(file_path))
    basepath = os.path.basename(fullpath)
    return (fullpath, basepath)


def format_date(unix_time):
    """format unix time to %Y-%m-%d %H:%M:%S"""
    date_value = datetime.datetime.fromtimestamp(unix_time)
    return date_value.strftime("%Y-%m-%d %H:%M:%S")


def format_uid_from_date(unix_time):
    """format unix time to yyyymmddhhmmss"""
    date_value = datetime.datetime.fromtimestamp(unix_time)
    return date_value.strftime("%Y%m%d%H%M%S")


def get_creation_date(file):
    """Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible."""
    if platform.system() == "Windows":
        return os.path.getctime(file)
    else:
        stat = os.stat(file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # On Linux, the file creation date is not available, so use the modification date
            return stat.st_mtime


def get_modification_date(unix_time):
    """try to get the date that a file was changed"""
    return os.path.getmtime(unix_time)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question"""
    # Acceptable responses
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    # set default Value
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    # check input process
    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').")