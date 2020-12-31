import sys, shutil, os, datetime, re, platform, logging, unicodedata
# setup logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Setting section ===
INBOX_DIR = ['Inbox', 'Draft', 'Pending'] # The files in this folder will have the YFM draft key set to true
EXCLUDE_DIR = set(['Backup', 'Template', 'tmp']) # Folders not to be processed (Hidden folders and files are not covered by default)
EXCLUDE_FILE = set(['tags']) # Files not to be processed (Hidden folders and files are not covered by default)
NOTE_EXT = ['.md', '.txt'] # Note file extension
IMG_EXT = ['.png', '.jpg', '.jpeg', '.svg', '.gif'] # image file extension
# YFM default settings
YFM = {
    "title": "", # It will be replaced by the file name
    "aliases": "[]",
    "date": "", # Replaced by the file creation date
    "update":"", # Replaced by the file modification date
    "tags": "[]", # If you have a hashtag, it will be generated automatically
    "draft": "false" # The following note will be true for the folder specified as INBOX_DIR
}

# === Enable function section ===
# Please set the function you want to use to True.
EXECUTION_FUNCTION_LIST = {
    "function_create_yfm": True, # If there is no Yaml FrontMatter at the beginning of the note, it will be generated
    "function_rename_notes": True, # Replace the file name of the note with the UID and replace the linked parts from other notes
    "function_rename_images": True, # Replace the file name of the image with the UID and replace the linked part from the other note
}

# === Start the process ===
def get_files(type):
    '''Retrieves a file of the specified type'''
    files = []
    # get all files
    for pathname, dirnames, filenames in os.walk(ROOT_PATH, topdown=True):
        # exclude dir and files
        dirnames[:] = list(filter(lambda d: not d in EXCLUDE_DIR, dirnames))
        filenames[:] = list(filter(lambda f: not f in EXCLUDE_FILE, filenames))
        dirnames[:] = list(filter(lambda d: not d[0] == '.', dirnames)) # Hidden directory beginning with "."
        filenames[:] = list(filter(lambda f: not f[0] == '.', filenames)) # Hidden files beginning with "."
        for filename in filenames:
            # Filtering files
            if type == 'note':
                if filename.endswith(tuple(NOTE_EXT)):
                    # append target notes to array
                    files.append(os.path.join(pathname,filename))
            if type == 'image':
                if filename.endswith(tuple(IMG_EXT)):
                    # append target notes to array
                    files.append(os.path.join(pathname,filename))
    return files

def check_and_create_yfm(files):
    '''If there is no YFM, create one.'''
    logger.debug('====== Start Check YFM ======')
    logger.debug('the target is: ' + str(len(files)) + ' files\n')
    update_yfm_files = [] # if note have YFM
    create_yfm_files = [] # if note doesn't have YFM
    # check and classify files by exists YFM
    for i, file in enumerate(files):
        logger.debug('Checking YFM...')
        logger.debug("target: " + file)
        # create target file list
        with open(file) as f:
            # check for the exist of YFM
            lines = f.readline().rstrip('\n')
            if lines == '---':
                update_yfm_files.append(file)
                logger.debug("Have already YFM")
            else: 
                create_yfm_files.append(file)
                logger.debug("No YFM yet")
        logger.debug("check done! [" + str(i+1) + "/" + str(len(files)) + "]\n")
    logger.debug('====== Start Update YFM ======')
    logger.debug('the target is: ' + str(len(update_yfm_files)) + ' files\n')
    processing_file_cnt = 0 # Counting the number of files processed
    for i, update_yfm_file in enumerate(update_yfm_files):
        logger.debug("Updating YFM...")
        logger.debug("target: " + update_yfm_file)
        this_YFM = YFM
        check_YFM = {
            "title": False,
            "aliases": False,
            "date": False,
            "update": False,
            "tags": False,
            "draft": False
        }
        with open(update_yfm_file) as f:
            lines = f.readlines()
            yfm_separate = 0
            end_of_yfm = 0
            # Check the end of header and the item exists or not
            for i, line in enumerate(lines):
                if line == "---\n":
                    yfm_separate += 1
                if yfm_separate == 2: # 2nd separate is end of YFM
                    end_of_yfm = i
                    break
                for key in check_YFM:
                    if re.match("^" + key + ": ", line):
                        check_YFM[key] = True
            update_flg = False # Check to see if it has been processed
            # Adding an item
            for key in check_YFM:
                if check_YFM[key] == False:
                    # Check as processed
                    if not update_flg:
                        update_flg = True
                    if key == 'title':
                        this_YFM[key] = get_file_name(update_yfm_file)[1]
                    elif key == 'aliases':
                        this_YFM[key] = "[]"
                    elif key == 'date':
                        this_YFM[key] = format_date(get_creation_date(update_yfm_file))
                    elif key == 'update':
                        this_YFM[key] = format_date(get_modification_date(update_yfm_file))
                    elif key == 'tags':
                        this_YFM[key] = create_tag_line_from_lines(lines)
                    elif key == 'draft':
                        if get_dir_name(update_yfm_file)[1] in INBOX_DIR:
                            this_YFM[key] = "true"
                        else:
                            this_YFM[key] = "false"
                    # Add an element to the end of the header
                    lines.insert(end_of_yfm, key + ': ' + this_YFM[key] + '\n')
                    end_of_yfm += 1
            # writing header
            writing_lines_without_hashtags(update_yfm_file, lines)
            # Count the number of files processed.
            if update_flg:
                logger.debug("update YFM!")
                processing_file_cnt += 1
            else:
                logger.debug("There is no YFM to update")
        logger.debug("processing done! [" + str(i+1) + "/" + str(len(update_yfm_files)) + "]\n")
    logger.debug(str(processing_file_cnt) + ' files have been updated!\n')
    logger.debug('====== Start Add New YFM ======')
    logger.debug('the target is: ' + str(len(create_yfm_files)) + ' files\n')
    processing_file_cnt = 0 # Counting the number of files processed
    for i, create_yfm_file in enumerate(create_yfm_files):
        logger.debug("Creating YFM...")
        logger.debug("target: " + create_yfm_file)
        with open(create_yfm_file) as f:
            lines = f.readlines()
            tag_line = create_tag_line_from_lines(lines)
            logger.debug("insert YFM...")
            this_YFM = YFM
            this_YFM['title'] = get_file_name(create_yfm_file)[1]
            this_YFM['date'] = format_date(get_creation_date(create_yfm_file))
            this_YFM['update'] = format_date(get_modification_date(create_yfm_file))
            this_YFM['tags'] = tag_line
            if get_dir_name(create_yfm_file)[1] in INBOX_DIR:
                this_YFM['draft'] = "true"
            else:
                this_YFM['draft'] = "false"
            YFM_text = '---\n'\
                    'title: ' + this_YFM['title'] + '\n'\
                    'aliases: ' + this_YFM['aliases'] + '\n'\
                    'date: ' + this_YFM['date'] + '\n'\
                    'update: ' + this_YFM['update'] + '\n'\
                    'tags: ' + this_YFM['tags'] + '\n'\
                    'draft: ' + this_YFM['draft'] + '\n'\
                    '---\n\n'
            logger.debug(YFM_text)
            lines.insert(0, YFM_text)
            # writing header
            writing_lines_without_hashtags(create_yfm_file, lines)
            processing_file_cnt += 1 # Counting the number of files processed
        logger.debug("processing done! [" + str(i+1) + "/" + str(len(create_yfm_files)) + "]\n")
    logger.debug(str(processing_file_cnt) + 'files have been updated!\n')

def get_file_name(file_path):
    '''Retrieves a file name from the specified path. The format of the return value is as below:
        ('filename.ext', 'filename', '.ext')'''
    fullname = unicodedata.normalize("NFC", os.path.basename(file_path))
    name = os.path.splitext(fullname)[0]
    ext = os.path.splitext(fullname)[1]
    return (fullname, name, ext)

def get_dir_name(file_path):
    '''Retrieves a folder name from the specified path. The format of the return value is as below:
        ('fullpath', 'basepath')'''
    fullpath = unicodedata.normalize("NFC", os.path.dirname(file_path))
    basepath = os.path.basename(fullpath)
    return (fullpath, basepath)

def format_date(unix_time):
    '''format unix time to %Y-%m-%d %H:%M:%S'''
    date_value = datetime.datetime.fromtimestamp(unix_time)
    return date_value.strftime('%Y-%m-%d %H:%M:%S')

def format_uid_from_date(unix_time):
    '''format unix time to yyyymmddhhmmss'''
    date_value = datetime.datetime.fromtimestamp(unix_time)
    return date_value.strftime('%Y%m%d%H%M%S')

def get_creation_date(file):
    '''Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.'''
    if platform.system() == 'Windows':
        return os.path.getctime(file)
    else:
        stat = os.stat(file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # On Linux, the file creation date is not available, so use the modification date
            return stat.st_mtime

def get_modification_date(unix_time):
    '''try to get the date that a file was changed'''
    return os.path.getmtime(unix_time)

def create_tag_line_from_lines(lines):
    '''create tag line for YFM from hashtags'''
    logger.debug('checking tags...')
    tag_line = ""
    for line in lines:
        for tag in re.findall('(\s|^)\#([^\s|^\#]+)', line):
            if tag_line == "":
                tag_line += str(tag[1])
            else:
                tag_line += ', ' + str(tag[1])
    tag_line = "[" + tag_line + "]"
    return tag_line

def writing_lines_without_hashtags(target, lines):
    '''writing lines without hashtags'''
    with open(target, mode='w') as wf:
        logger.debug("writing file...")
        for i, line in enumerate(lines):
            # Delete the hashtag line
            if not re.match("^\#[^\#|^\s].+", line):
                wf.write(line)
    with open(target) as f:
        lines = f.readlines()
        while lines[-1] == "\n":
            lines.pop(-1)
        with open(target, mode='w') as wf:
            wf.writelines(lines)
    logger.debug("done!")

def rename_notes_with_links(files):
    '''Rename the all file names to UID and update wikilinks to Markdownlinks'''
    logger.debug('====== Start Rename Notes And Substitute Wikilinks ======')
    logger.debug('the target is: ' + str(len(files)) + ' files\n')
    rename_file_cnt = 0 # Counting the number of files processed
    substitute_file_cnt = 0 # Number of files with links
    for i, file in enumerate(files): 
        logger.debug("target: " + file)
        if check_note_has_uid(file):
            logger.debug("It seems that this file already has a UID\n")
            continue
        else:
            new_file_path = get_new_filepath_with_uid(file)
            logger.debug("rename: " + new_file_path)
            # rename and move ROOT PATH
            new_file_path_result = shutil.move(file, new_file_path)
            logger.debug("rename done: " + new_file_path_result)
            rename_file_cnt += 1
            # add UID to top of YFM
            with open(new_file_path_result) as f:
                lines = f.readlines()
                lines.insert(1, "uid: " + get_file_name(new_file_path_result)[1] + "\n")
                with open(new_file_path_result, mode='w') as wf:
                    wf.writelines(lines)
            # Replace backlinks
            if substitute_wikilinks_to_markdown_links(file, new_file_path_result):
                substitute_file_cnt += 1
        logger.debug("processing done! [" + str(i+1) + "/" + str(len(files)) + "]\n")
    logger.debug(str(rename_file_cnt) + ' files have been renamed!\n')
    logger.debug(str(substitute_file_cnt) + 'linked files have been updated!\n')

def rename_images_with_links(files):
    logger.debug('====== Start Rename Images And Substitute Wikilinks ======')
    logger.debug('the target is: ' + str(len(files)) + ' files\n')
    rename_file_cnt = 0 # Counting the number of files processed
    substitute_file_cnt = 0 # Number of files with links
    for i, file in enumerate(files): 
        logger.debug("target: " + file)
        if check_note_has_uid(file):
            logger.debug("It seems that this file already has a UID\n")
            continue
        else:
            # rename image
            new_file_path = get_new_filepath_with_uid(file)
            os.rename(file, new_file_path)
            rename_file_cnt += 1
            logger.debug("rename: " + new_file_path)
            # Replace backlinks
            if substitute_wikilinks_to_markdown_links(file, new_file_path):
                substitute_file_cnt += 1
        logger.debug("processing done! [" + str(i+1) + "/" + str(len(files)) + "]\n")
    logger.debug(str(rename_file_cnt) + ' files have been renamed!')
    logger.debug(str(substitute_file_cnt) + ' linked files have been updated!\n')

def check_note_has_uid(file):
    file_title = get_file_name(file)[1]
    return re.match('^\d{14}$', file_title)

def get_new_filepath_with_uid(file):
    '''get new filepath with uid'''
    # UID is yyyymmddhhmmss from create date
    uid = int(format_uid_from_date(get_creation_date(file)))
    ext = get_file_name(file)[2]
    if ext == '.md':
        path = ROOT_PATH
    else:
        path = os.path.dirname(file)
    # Add 1 if the UID is duplicated
    while os.path.exists(build_filepath_by_uid(uid, path, ext)):
        uid += 1
    return build_filepath_by_uid(uid, path, ext)

def build_filepath_by_uid(uid, path, ext='.md'):
    return path + '/' + str(uid) + ext

def substitute_wikilinks_to_markdown_links(old_file_path, new_file_path):
    '''substitute wikilinks to markdown links'''
    # build file info
    old_file_names = get_file_name(old_file_path)
    new_file_link = get_file_name(new_file_path)[0]
    logger.debug("substitute Wikilinks...")
    update_link_files = get_files('note')
    check_substitute_flg = False # Whether it has been replaced or not
    # check all notes links
    logger.debug("checking " + str(len(update_link_files)) + " files...")
    substitute_file_cnt = 0 # For counting the number of replaced files
    substitute_line_cnt = 0
    for update_link_file in update_link_files:
        substitute_flg = False # For counting the number of replaced files
        with open(update_link_file, mode='r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Replace the target Wikilinks if any
                match = re.search('\[\[(' + old_file_names[1] + '(' + old_file_names[2] + ')?'+ '(\s\|\s(.+))?)\]\]', line)
                if match:
                    logger.debug("match: " + update_link_file)
                    logger.debug("substitute: " + match.group(0))
                    if not check_substitute_flg:
                        check_substitute_flg = True
                    if not substitute_flg:
                        substitute_flg = True
                    substitute_line_cnt += 1
                    # If Alias is set in the Link, use Alias as the Link Text
                    if match.group(4):
                        lines[i] = line.replace(match.group(0), '[' + match.group(4) + '](' + new_file_link + ')')
                    else:
                        lines[i] = line.replace(match.group(0), '[' + match.group(1) + '](' + new_file_link + ')')
                    logger.debug(lines[i])
            with open(update_link_file, mode='w') as wf:
                wf.writelines(lines)
            if substitute_flg:
                substitute_file_cnt += 1
    logger.debug(str(substitute_line_cnt) + " lines replaced!")
    logger.debug("The link that existed in file " + str(substitute_file_cnt) + " has been updated!")
    logger.debug("done!")
    return check_substitute_flg

def query_yes_no(question, default="yes"):
    """Ask a yes/no question"""
    # Acceptable responses
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
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
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

# === Main process ===
if __name__ == '__main__':
    '''This is the main process to implement the enabled features'''
    logger.debug('=================================================')
    logger.debug('Welcome to Note normalization for Zettelkasten!')
    logger.debug('=================================================\n')
    argv = sys.argv
    # Specify the target folder
    if len(argv) > 1:
        logger.debug('Arguments received')
        path = argv[1]
        if os.path.isdir(path):
            logger.debug('The existence of the folder has been confirmed!')
        else:
            logger.debug('The specified folder does not seem to exist.')
    else:
        logger.debug('no arguments. Target the current directory.')
        path = os.getcwd()
    logger.debug('Zettelkasten ROOT PATH is: ' + path)
    logger.debug('Can I normalize the notes in this folder?')
    # Confirmation to the user
    if query_yes_no(path):
        logger.debug('okay. Continue processing')
        ROOT_PATH = path
    else:
        logger.debug('okay. Abort the process')
        sys.exit()
    # Confirm the function to be performed
    logger.debug('Checking the process to be executed\n')
    function_desc = {
        'function_create_yfm': '- Yaml FrontMatter formatting\t\t\t......\t',
        'function_rename_notes': '- Rename the note to UID and update the link\t.......\t',
        'function_rename_images': '- Rename the image to UID and update the link\t.......\t'
    }
    on_off_text = ['ON', 'OFF']
    for key in EXECUTION_FUNCTION_LIST:
        if EXECUTION_FUNCTION_LIST[key]:
            logger.debug(function_desc[key] + on_off_text[0])
        else:
            logger.debug(function_desc[key] + on_off_text[1])
    if not query_yes_no('\nAre you sure you want to perform the above functions?'):
        logger.debug('okay. Abort the process')
        sys.exit()
    # Execute an enabled process
    if EXECUTION_FUNCTION_LIST["function_create_yfm"]:
        check_and_create_yfm(get_files('note'))
    if EXECUTION_FUNCTION_LIST["function_rename_notes"]:
        rename_notes_with_links(get_files('note'))
    if EXECUTION_FUNCTION_LIST["function_rename_images"]: 
        rename_images_with_links(get_files('image'))
    # finish!
    logger.debug('All processing is complete!')
    logger.debug('The execution log was saved to a log file. please see ./debug.log files.\n')
    logger.debug('Enjoy building your SECOND BRAIN!')
