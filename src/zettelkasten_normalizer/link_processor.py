"""
Link processing functions for Zettelkasten note normalization.
"""

import re
import os
import shutil
import logging
from .utils import get_file_name, read_file_cross_platform, write_file_cross_platform
from .file_operations import get_files, check_note_has_uid, get_new_filepath_with_uid
from .frontmatter_parser import FrontMatterParser

# Get logger
logger = logging.getLogger(__name__)


def substitute_wikilinks_to_markdown_links(old_file_path, new_file_path, root_path):
    """substitute wikilinks to markdown links"""
    # build file info
    old_file_names = get_file_name(old_file_path)
    new_file_link = get_file_name(new_file_path)[0]
    logger.debug("substitute Wikilinks...")
    update_link_files = get_files(root_path, "note")
    check_substitute_flg = False  # Whether it has been replaced or not
    # check all notes links
    logger.debug("checking " + str(len(update_link_files)) + " files...")
    substitute_file_cnt = 0  # For counting the number of replaced files
    substitute_line_cnt = 0
    
    for update_link_file in update_link_files:
        substitute_flg = False  # For counting the number of replaced files
        
        # Use cross-platform file reading
        content = read_file_cross_platform(update_link_file)
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
                # Replace the target Wikilinks if any
                match = re.search(
                    "\[\[("
                    + re.escape(old_file_names[1])
                    + "("
                    + re.escape(old_file_names[2])
                    + ")?"
                    + "(\s\|\s(.+))?)?\]\]",
                    line,
                )
                if match:
                    logger.debug("Wikilink match: " + update_link_file)
                    logger.debug("substitute: " + match.group(0))
                    if not check_substitute_flg:
                        check_substitute_flg = True
                    if not substitute_flg:
                        substitute_flg = True
                    substitute_line_cnt += 1
                    # If Alias is set in the Link, use Alias as the Link Text
                    if match.group(4):
                        lines[i] = line.replace(
                            match.group(0),
                            "[" + match.group(4) + "](" + new_file_link + ")",
                        )
                    else:
                        lines[i] = line.replace(
                            match.group(0),
                            "[" + match.group(1) + "](" + new_file_link + ")",
                        )
                    logger.debug(lines[i])
                
                # Replace the target Markdownlinks if any
                match = re.search(
                    "\[.+\]\(((?!http.*).*" + re.escape(old_file_names[0]) + ")\)", line
                )
                if match:
                    logger.debug("Markdown link match: " + update_link_file)
                    logger.debug("substitute: " + match.group(0))
                    if not check_substitute_flg:
                        check_substitute_flg = True
                    if not substitute_flg:
                        substitute_flg = True
                    substitute_line_cnt += 1
                    lines[i] = line.replace(match.group(1), new_file_link)
                    logger.debug(lines[i])
        
        # Write back the modified content using cross-platform function
        if substitute_flg:
            modified_content = '\n'.join(lines)
            write_file_cross_platform(update_link_file, modified_content)
            substitute_file_cnt += 1
    
    logger.debug(str(substitute_line_cnt) + " lines replaced!")
    logger.debug(
        "The link that existed in file "
        + str(substitute_file_cnt)
        + " has been updated!"
    )
    logger.debug("done!")
    return check_substitute_flg


def rename_notes_with_links(files, root_path):
    """Rename the all file names to UID and update wikilinks to Markdownlinks"""
    logger.info("====== Start Rename Notes And Substitute Wikilinks ======")
    logger.info("the target is: " + str(len(files)) + " files")
    rename_file_cnt = 0  # Counting the number of files processed
    substitute_file_cnt = 0  # Number of files with links
    
    for i, file in enumerate(files):
        logger.debug("target: " + file)
        if check_note_has_uid(file):
            logger.debug("It seems that this file already has a UID")
            continue
        else:
            new_file_path = get_new_filepath_with_uid(file, root_path)
            uid = get_file_name(new_file_path)[1]
            logger.debug("uid: " + uid)
            logger.debug("rename: " + new_file_path)
            # rename and move ROOT PATH
            new_file_path_result = shutil.move(file, new_file_path)
            logger.info("rename done: " + new_file_path_result)
            rename_file_cnt += 1
            # add or update UID in front matter
            logger.debug("Insert or update UID in Front Matter")
            content = read_file_cross_platform(new_file_path_result)
            
            # Detect front matter format and parse it
            parser = FrontMatterParser()
            detected_format = parser.detect_format(content)
            
            if detected_format:
                # Parse existing front matter
                metadata, body_content = parser.parse_frontmatter(content)
                if metadata is not None:
                    # Update or add the uid property
                    metadata['uid'] = uid
                    
                    # Use the detected format to serialize back
                    parser_with_format = FrontMatterParser(detected_format)
                    modified_content = parser_with_format.serialize_frontmatter(metadata, body_content)
                    write_file_cross_platform(new_file_path_result, modified_content)
                else:
                    # Failed to parse, fallback to simple insertion
                    logger.warning(f"Failed to parse frontmatter for {new_file_path_result}, using fallback method")
                    lines = content.split('\n')
                    lines.insert(1, "uid: " + uid)
                    modified_content = '\n'.join(lines)
                    write_file_cross_platform(new_file_path_result, modified_content)
            else:
                # No front matter detected, use original logic
                lines = content.split('\n')
                lines.insert(1, "uid: " + uid)
                modified_content = '\n'.join(lines)
                write_file_cross_platform(new_file_path_result, modified_content)
            # Replace backlinks
            if substitute_wikilinks_to_markdown_links(file, new_file_path_result, root_path):
                substitute_file_cnt += 1
        logger.debug("processing done! [" + str(i + 1) + "/" + str(len(files)) + "]")
    
    logger.info(str(rename_file_cnt) + " files have been renamed!")
    logger.info(str(substitute_file_cnt) + " linked files have been updated!")


def rename_images_with_links(files, root_path):
    """Rename image files to UID and update links"""
    logger.info("====== Start Rename Images And Substitute Wikilinks ======")
    logger.info("the target is: " + str(len(files)) + " files")
    rename_file_cnt = 0  # Counting the number of files processed
    substitute_file_cnt = 0  # Number of files with links
    
    for i, file in enumerate(files):
        logger.debug("target: " + file)
        if check_note_has_uid(file):
            logger.debug("It seems that this file already has a UID")
            continue
        else:
            # rename image
            new_file_path = get_new_filepath_with_uid(file, root_path)
            uid = get_file_name(new_file_path)[1]
            logger.debug("uid: " + uid)
            os.rename(file, new_file_path)
            rename_file_cnt += 1
            logger.info("rename done: " + new_file_path)
            # Replace backlinks
            if substitute_wikilinks_to_markdown_links(file, new_file_path, root_path):
                substitute_file_cnt += 1
        logger.debug("processing done! [" + str(i + 1) + "/" + str(len(files)) + "]")
    
    logger.info(str(rename_file_cnt) + " files have been renamed!")
    logger.info(str(substitute_file_cnt) + " linked files have been updated!")