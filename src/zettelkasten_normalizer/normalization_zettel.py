#!/usr/bin/env python3
"""
Zettelkasten Note Normalization Tool

This tool normalizes Markdown notes for Zettelkasten systems by:
- Adding YAML front matter
- Renaming files with UIDs
- Converting WikiLinks to Markdown links

Author: jMatsuzaki
Repository: https://github.com/jmatsuzaki/note-normalization-for-zettelkasten
"""

import sys
import os
import argparse

# Import our modules
from .config import EXECUTION_FUNCTION_LIST
from .utils import setup_logger, query_yes_no
from .file_operations import get_files
from .yfm_processor import check_and_create_yfm
from .link_processor import rename_notes_with_links, rename_images_with_links


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="This program will normalize Markdown notes for Zettelkasten",
        epilog="This program will add Front Matter, add UIDs and rename files, replace Wikilink with Markdown link, etc.\nFurther details can be found in the repository. See below:\n\nhttps://github.com/jmatsuzaki/note-normalization-for-zettelkasten",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("root", help="Zettelkasten's root folder")
    parser.add_argument("-t", "--target", help="normalization target folder or file")
    parser.add_argument(
        "-y", "--yes", action="store_true", help="automatically answer yes to all questions"
    )
    parser.add_argument(
        "-f", "--format", choices=["yaml", "toml", "json"], default="yaml",
        help="Front matter format (default: yaml)"
    )
    parser.add_argument(
        "--skip-frontmatter", action="store_true",
        help="Skip front matter processing"
    )
    parser.add_argument(
        "--skip-rename-notes", action="store_true",
        help="Skip note renaming and link updating"
    )
    parser.add_argument(
        "--skip-rename-images", action="store_true",
        help="Skip image renaming and link updating"
    )
    return parser.parse_args()


def validate_paths(args):
    """Validate and set up paths"""
    # Validate root path
    if not os.path.isdir(args.root):
        print("The specified root folder does not exist")
        print("Abort the process")
        print("You can see how to use it with the -h option")
        sys.exit(1)
    
    root_path = args.root
    
    # Validate target path
    if args.target:
        if not os.path.exists(args.target):
            print("The specified target folder or file does not seem to exist.")
            print("Abort the process")
            sys.exit(1)
        target_path = args.target
    else:
        target_path = args.root
    
    return root_path, target_path


def confirm_execution(args, logger):
    """Confirm execution with user"""
    if args.yes:
        logger.info("--yes option has been specified, continue processing automatically")
        return True
    
    logger.info("Can I normalize these notes?")
    if not query_yes_no("Can I normalize these notes?"):
        logger.info("okay. Abort the process")
        return False
    
    logger.info("okay. Continue processing")
    return True


def get_execution_functions(args):
    """Get execution function settings based on command line arguments and config"""
    # Start with default config settings
    execution_functions = {
        "function_create_yfm": EXECUTION_FUNCTION_LIST["function_create_yfm"],
        "function_rename_notes": EXECUTION_FUNCTION_LIST["function_rename_notes"],
        "function_rename_images": EXECUTION_FUNCTION_LIST["function_rename_images"],
    }
    
    # Override with command line arguments if specified
    if args.skip_frontmatter:
        execution_functions["function_create_yfm"] = False
    if args.skip_rename_notes:
        execution_functions["function_rename_notes"] = False
    if args.skip_rename_images:
        execution_functions["function_rename_images"] = False
    
    return execution_functions


def show_function_status(logger, execution_functions, format_type="yaml"):
    """Show which functions are enabled"""
    function_desc = {
        "function_create_yfm": f"- {format_type.upper()} FrontMatter formatting\t\t\t......\t",
        "function_rename_notes": "- Rename the note to UID and update the link\t.......\t",
        "function_rename_images": "- Rename the image to UID and update the link\t.......\t",
    }
    on_off_text = ["ON", "OFF"]
    
    for key in execution_functions:
        status = on_off_text[0] if execution_functions[key] else on_off_text[1]
        logger.info(function_desc[key] + status)


def confirm_functions(args, logger):
    """Confirm function execution with user"""
    if args.yes:
        logger.info("--yes option has been specified, continue processing automatically")
        return True
    
    if not query_yes_no("\nAre you sure you want to perform the above functions?"):
        logger.info("okay. Abort the process")
        return False
    
    logger.info("okay. Continue processing")
    return True


def execute_normalization(target_path, root_path, logger, execution_functions, format_type="yaml"):
    """Execute the normalization process"""
    # Execute Front Matter processing
    if execution_functions["function_create_yfm"]:
        check_and_create_yfm(get_files(target_path, "note"), format_type)
    
    # Execute note renaming
    if execution_functions["function_rename_notes"]:
        rename_notes_with_links(get_files(target_path, "note"), root_path)
    
    # Execute image renaming
    if execution_functions["function_rename_images"]:
        rename_images_with_links(get_files(target_path, "image"), root_path)


def main():
    """Main execution function"""
    # Parse command line arguments
    args = parse_arguments()
    
    # Validate paths
    root_path, target_path = validate_paths(args)
    
    # Setup logger
    logger = setup_logger(root_path)
    
    # Welcome message
    logger.info("=================================================")
    logger.info("Welcome to Note normalization for Zettelkasten!")
    logger.info("=================================================")
    
    # Log paths
    logger.debug("Folder has been specified")
    logger.debug("The existence of the folder has been confirmed!")
    logger.info("Set the specified folder as the root folder of Zettelkasten and process all files under it")
    logger.info("Zettelkasten ROOT PATH is: " + root_path)
    logger.info("Normalize TARGET PATH is: " + target_path)
    
    # Get execution functions based on command line arguments
    execution_functions = get_execution_functions(args)
    
    # Confirm execution
    if not confirm_execution(args, logger):
        sys.exit(0)
    
    # Show function status
    logger.debug("Checking the process to be executed")
    show_function_status(logger, execution_functions, args.format)
    
    # Confirm functions
    if not confirm_functions(args, logger):
        sys.exit(0)
    
    # Execute normalization
    execute_normalization(target_path, root_path, logger, execution_functions, args.format)
    
    # Completion message
    logger.info("All processing is complete!")
    logger.info("The execution log was saved to a log file. please see /path/to/your/zettelkasten_root_folder/normalization_zettel.log files.")
    logger.info("=================================================")
    logger.info("Enjoy building your SECOND BRAIN!")
    logger.info("=================================================")


if __name__ == "__main__":
    main()