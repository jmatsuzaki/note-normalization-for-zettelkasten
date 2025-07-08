"""
YAML Front Matter processing functions for Zettelkasten note normalization.
"""

import re
import logging
from .config import YFM, INBOX_DIR
from .utils import get_file_name, get_dir_name, format_date, get_creation_date, get_modification_date

# Get logger
logger = logging.getLogger(__name__)


def create_tag_line_from_lines(lines):
    """create tag line for YFM from hashtags"""
    logger.debug("checking tags...")
    tag_line = ""
    for line in lines:
        for tag in re.findall("(\s|^)\#([^\s|^\#]+)", line):
            if tag_line == "":
                tag_line += str(tag[1])
            else:
                tag_line += ", " + str(tag[1])
    tag_line = "[" + tag_line + "]"
    return tag_line


def writing_lines_without_hashtags(target, lines):
    """writing lines without hashtags"""
    with open(target, mode="w") as wf:
        logger.debug("writing file...")
        for i, line in enumerate(lines):
            # Delete the hashtag line
            if not re.match("^\#[^\#|^\s].+", line):
                wf.write(line)
    with open(target) as f:
        lines = f.readlines()
        while lines[-1] == "\n":
            lines.pop(-1)
        with open(target, mode="w") as wf:
            wf.writelines(lines)
    logger.debug("done!")


def check_and_create_yfm(files):
    """If there is no YFM, create one."""
    logger.info("====== Start Check YFM ======")
    logger.info("the target is: " + str(len(files)) + " files")
    update_yfm_files = []  # if note have YFM
    create_yfm_files = []  # if note doesn't have YFM
    
    # check and classify files by exists YFM
    for i, file in enumerate(files):
        logger.debug("Checking YFM...")
        logger.debug("target: " + file)
        # create target file list
        with open(file) as f:
            # check for the exist of YFM
            lines = f.readline().rstrip("\n")
            if lines == "---":
                update_yfm_files.append(file)
                logger.debug("Have already YFM")
            else:
                create_yfm_files.append(file)
                logger.debug("No YFM yet")
        logger.info("check done! [" + str(i + 1) + "/" + str(len(files)) + "]")
    
    # Update existing YFM files
    _update_existing_yfm(update_yfm_files)
    
    # Create new YFM for files without it
    _create_new_yfm(create_yfm_files)


def _update_existing_yfm(update_yfm_files):
    """Update existing YFM files"""
    logger.info("====== Start Update YFM ======")
    logger.info("the target is: " + str(len(update_yfm_files)) + " files")
    processing_file_cnt = 0  # Counting the number of files processed
    
    for j, update_yfm_file in enumerate(update_yfm_files):
        logger.debug("Updating YFM...")
        logger.info("target: " + update_yfm_file)
        this_YFM = YFM
        check_YFM = {
            "title": -1,
            "aliases": -1,
            "date": -1,
            "update": -1,
            "tags": -1,
            "draft": -1,
        }
        
        with open(update_yfm_file) as f:
            lines = f.readlines()
            yfm_separate = 0
            end_of_yfm = 0
            # Check the end of header and the item exists or not
            for i, line in enumerate(lines):
                if line == "---\n":
                    yfm_separate += 1
                if yfm_separate == 2:  # 2nd separate is end of YFM
                    end_of_yfm = i
                    break
                for key in check_YFM:
                    if re.match("^" + key + ":", line):
                        check_YFM[key] = i
            
            update_flg = False  # Check to see if it has been processed
            # Adding an item
            for key in check_YFM:
                if check_YFM[key] == -1:
                    # Check as processed
                    if not update_flg:
                        update_flg = True
                    if key == "title":
                        this_YFM[key] = get_file_name(update_yfm_file)[1]
                    elif key == "aliases":
                        this_YFM[key] = "[]"
                    elif key == "date":
                        this_YFM[key] = format_date(get_creation_date(update_yfm_file))
                    elif key == "update":
                        this_YFM[key] = format_date(
                            get_modification_date(update_yfm_file)
                        )
                    elif key == "tags":
                        this_YFM[key] = create_tag_line_from_lines(lines)
                    elif key == "draft":
                        if get_dir_name(update_yfm_file)[1] in INBOX_DIR:
                            this_YFM[key] = "true"
                        else:
                            this_YFM[key] = "false"
                    # Add an element to the end of the header
                    lines.insert(end_of_yfm, key + ": " + this_YFM[key] + "\n")
                    end_of_yfm += 1
            
            # updating an item
            if str(check_YFM["update"]).isdecimal():
                del lines[check_YFM["update"]]
                lines.insert(
                    check_YFM["update"],
                    "update: "
                    + format_date(get_modification_date(update_yfm_file))
                    + "\n",
                )
                update_flg = True
            
            # writing header
            writing_lines_without_hashtags(update_yfm_file, lines)
            # Count the number of files processed.
            if update_flg:
                logger.debug("update YFM!")
                processing_file_cnt += 1
            else:
                logger.debug("There is no YFM to update")
        
        logger.debug(
            "processing done! [" + str(j + 1) + "/" + str(len(update_yfm_files)) + "]"
        )
    
    logger.info(str(processing_file_cnt) + " files have been updated!")


def _create_new_yfm(create_yfm_files):
    """Create new YFM for files without it"""
    logger.info("====== Start Add New YFM ======")
    logger.info("the target is: " + str(len(create_yfm_files)) + " files")
    processing_file_cnt = 0  # Counting the number of files processed
    
    for i, create_yfm_file in enumerate(create_yfm_files):
        logger.debug("Creating YFM...")
        logger.info("target: " + create_yfm_file)
        
        with open(create_yfm_file) as f:
            lines = f.readlines()
            tag_line = create_tag_line_from_lines(lines)
            logger.debug("insert YFM...")
            this_YFM = YFM
            this_YFM["title"] = get_file_name(create_yfm_file)[1]
            this_YFM["date"] = format_date(get_creation_date(create_yfm_file))
            this_YFM["update"] = format_date(get_modification_date(create_yfm_file))
            this_YFM["tags"] = tag_line
            if get_dir_name(create_yfm_file)[1] in INBOX_DIR:
                this_YFM["draft"] = "true"
            else:
                this_YFM["draft"] = "false"
            
            YFM_text = (
                "---\n"
                "title: " + this_YFM["title"] + "\n"
                "aliases: " + this_YFM["aliases"] + "\n"
                "date: " + this_YFM["date"] + "\n"
                "update: " + this_YFM["update"] + "\n"
                "tags: " + this_YFM["tags"] + "\n"
                "draft: " + this_YFM["draft"] + "\n"
                "---\n\n"
            )
            logger.debug(YFM_text)
            lines.insert(0, YFM_text)
            # writing header
            writing_lines_without_hashtags(create_yfm_file, lines)
            processing_file_cnt += 1  # Counting the number of files processed
        
        logger.debug(
            "processing done! [" + str(i + 1) + "/" + str(len(create_yfm_files)) + "]"
        )
    
    logger.info(str(processing_file_cnt) + "files have been updated!")