"""
Front Matter processing functions for Zettelkasten note normalization.
Supports YAML, TOML, and JSON formats.
"""

import re
import logging
from .config import YFM, INBOX_DIR, FRONT_MATTER_FORMAT
from .utils import get_file_name, get_dir_name, format_date, get_creation_date, get_modification_date
from .frontmatter_parser import FrontMatterParser, get_frontmatter_delimiters

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
    # Convert string to lines if necessary
    if isinstance(lines, str):
        lines = lines.split('\n')
    
    with open(target, mode="w", encoding='utf-8') as wf:
        logger.debug("writing file...")
        for i, line in enumerate(lines):
            # Add newline if missing (except for last line)
            if not line.endswith('\n') and i < len(lines) - 1:
                line += '\n'
            # Delete the hashtag line
            if not re.match("^\#[^\#|^\s].+", line):
                wf.write(line)
    
    # Clean up trailing newlines
    with open(target, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove excessive trailing newlines but keep at least one
    content = content.rstrip('\n') + '\n'
    
    with open(target, mode="w", encoding='utf-8') as wf:
        wf.write(content)
    logger.debug("done!")


def check_and_create_yfm(files, format_type=None):
    """If there is no Front Matter, create one."""
    if format_type is None:
        format_type = FRONT_MATTER_FORMAT
    
    logger.info("====== Start Check Front Matter ======")
    logger.info(f"Format: {format_type}")
    logger.info("the target is: " + str(len(files)) + " files")
    
    # Initialize parser
    try:
        parser = FrontMatterParser(format_type)
    except (ValueError, ImportError) as e:
        logger.error(f"Failed to initialize parser: {e}")
        return
    
    update_yfm_files = []  # if note have front matter
    create_yfm_files = []  # if note doesn't have front matter
    
    # check and classify files by exists front matter
    for i, file in enumerate(files):
        logger.debug("Checking Front Matter...")
        logger.debug("target: " + file)
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Detect front matter format
            detected_format = parser.detect_format(content)
            if detected_format:
                update_yfm_files.append(file)
                logger.debug(f"Have already Front Matter ({detected_format})")
            else:
                create_yfm_files.append(file)
                logger.debug("No Front Matter yet")
                
        except Exception as e:
            logger.error(f"Error reading file {file}: {e}")
            continue
            
        logger.info("check done! [" + str(i + 1) + "/" + str(len(files)) + "]")
    
    # Update existing front matter files
    _update_existing_yfm(update_yfm_files, parser)
    
    # Create new front matter for files without it
    _create_new_yfm(create_yfm_files, parser)


def _update_existing_yfm(update_yfm_files, parser):
    """Update existing Front Matter files"""
    logger.info("====== Start Update Front Matter ======")
    logger.info("the target is: " + str(len(update_yfm_files)) + " files")
    processing_file_cnt = 0  # Counting the number of files processed
    
    for j, update_yfm_file in enumerate(update_yfm_files):
        logger.debug("Updating Front Matter...")
        logger.info("target: " + update_yfm_file)
        
        try:
            with open(update_yfm_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse existing front matter
            metadata, body_content = parser.parse_frontmatter(content)
            if metadata is None:
                logger.debug("Failed to parse front matter, skipping")
                continue
            
            # Check for missing fields and update
            update_flg = False
            required_fields = {
                "title": get_file_name(update_yfm_file)[1],
                "aliases": "[]",
                "date": format_date(get_creation_date(update_yfm_file)),
                "update": format_date(get_modification_date(update_yfm_file)),
                "tags": create_tag_line_from_lines(content.split('\n')),
                "draft": "true" if get_dir_name(update_yfm_file)[1] in INBOX_DIR else "false"
            }
            
            # Add missing fields
            for key, default_value in required_fields.items():
                if key not in metadata:
                    metadata[key] = default_value
                    update_flg = True
                    logger.debug(f"Added missing field: {key}")
            
            # Always update the 'update' field
            if "update" in metadata:
                old_update = metadata["update"]
                new_update = format_date(get_modification_date(update_yfm_file))
                if old_update != new_update:
                    metadata["update"] = new_update
                    update_flg = True
                    logger.debug(f"Updated 'update' field: {old_update} -> {new_update}")
            
            if update_flg:
                # Regenerate content with updated metadata
                updated_content = parser.serialize_frontmatter(metadata, body_content)
                
                # Remove hashtag lines from body
                lines = updated_content.split('\n')
                writing_lines_without_hashtags(update_yfm_file, lines)
                
                processing_file_cnt += 1
                logger.debug("Updated Front Matter!")
            else:
                logger.debug("There is no Front Matter to update")
                
        except Exception as e:
            logger.error(f"Error updating front matter for {update_yfm_file}: {e}")
            continue
        
        logger.debug(
            "processing done! [" + str(j + 1) + "/" + str(len(update_yfm_files)) + "]"
        )
    
    logger.info(str(processing_file_cnt) + " files have been updated!")


def _create_new_yfm(create_yfm_files, parser):
    """Create new Front Matter for files without it"""
    logger.info("====== Start Add New Front Matter ======")
    logger.info("the target is: " + str(len(create_yfm_files)) + " files")
    processing_file_cnt = 0  # Counting the number of files processed
    
    for i, create_yfm_file in enumerate(create_yfm_files):
        logger.debug("Creating Front Matter...")
        logger.info("target: " + create_yfm_file)
        
        try:
            with open(create_yfm_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            tag_line = create_tag_line_from_lines(lines)
            
            logger.debug("insert Front Matter...")
            
            # Create metadata dictionary
            metadata = {
                "title": get_file_name(create_yfm_file)[1],
                "aliases": "[]",
                "date": format_date(get_creation_date(create_yfm_file)),
                "update": format_date(get_modification_date(create_yfm_file)),
                "tags": tag_line,
                "draft": "true" if get_dir_name(create_yfm_file)[1] in INBOX_DIR else "false"
            }
            
            # Serialize front matter with content
            updated_content = parser.serialize_frontmatter(metadata, content)
            
            # Remove hashtag lines from body
            lines = updated_content.split('\n')
            writing_lines_without_hashtags(create_yfm_file, lines)
            
            processing_file_cnt += 1  # Counting the number of files processed
            logger.debug(f"Created {parser.format_type.upper()} Front Matter")
            
        except Exception as e:
            logger.error(f"Error creating front matter for {create_yfm_file}: {e}")
            continue
        
        logger.debug(
            "processing done! [" + str(i + 1) + "/" + str(len(create_yfm_files)) + "]"
        )
    
    logger.info(str(processing_file_cnt) + " files have been updated!")