# coding: utf-8

# === Setting section ===
# ROOT_PATH = '/Users/jmatsuzaki/Dropbox/Knowledge/Zettelkasten' # set your Zettelkasten's absolute path
ROOT_PATH = '/Users/jmatsuzaki/Desktop/Ztest' # set your Zettelkasten's absolute path
INBOX_DIR = ['Inbox', 'Draft', 'Pending'] # The files in this folder will have the YFM draft key set to true
EXCLUDE_DIR = set(['Template', 'tmp']) # Folders not to be processed (Hidden folders and files are not covered by default)
EXCLUDE_FILE = set(['tags']) # Files not to be processed (Hidden folders and files are not covered by default)
NOTE_EXT = ['.md', '.txt'] # Note file extension
IMG_EXT = ['.png', '.jpg', '.jpeg', '.svg'] # image file extension
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
function_create_yfm = True # If there is no Yaml FrontMatter at the beginning of the note, it will be generated
function_rename_notes = True # Replace the file name of the note with the UID and replace the linked parts from other notes
function_rename_images = True # Replace the file name of the image with the UID and replace the linked part from the other note

# === Start the process ===
import shutil, os, datetime, re

def get_files(type):
    '''get all note files'''
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
    print('\n====== Start Check YFM ======')
    print('the target is: ' + str(len(files)) + ' files\n')
    update_yfm_files = [] # if note have YFM
    create_yfm_files = [] # if note doesn't have YFM
    # check and classify files by exists YFM
    for file in files:
        print('Checking YFM...')
        print("target: " + file)
        # create target file list
        with open(file) as f:
            # check for the exist of YFM
            lines = f.readline().rstrip('\n')
            if lines == '---':
                update_yfm_files.append(file)
                print("Have already YFM")
            else: 
                create_yfm_files.append(file)
                print("No YFM yet")
    print('\n====== Start Update YFM ======')
    print('the target is: ' + str(len(update_yfm_files)) + ' files\n')
    for update_yfm_file in update_yfm_files:
        print("Updating YFM...")
        print("target: " + update_yfm_file)
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
            dt = datetime.datetime
            # Adding an item
            for key in check_YFM:
                if check_YFM[key] == False:
                    if key == 'title':
                        this_YFM[key] = os.path.splitext(os.path.basename(create_yfm_file))[0]
                    elif key == 'aliases':
                        this_YFM[key] = "[]"
                    elif key == 'date':
                        date_value = datetime.datetime.fromtimestamp(os.stat(update_yfm_file).st_birthtime)
                        this_YFM[key] = date_value.strftime('%Y-%m-%d %H:%M:%S')
                    elif key == 'update':
                        update_value = datetime.datetime.fromtimestamp(os.path.getmtime(update_yfm_file))
                        this_YFM[key] = update_value.strftime('%Y-%m-%d %H:%M:%S')
                    elif key == 'tags':
                        this_YFM[key] = create_tag_line_from_lines(lines)
                    elif key == 'draft':
                        if os.path.basename(os.path.dirname(update_yfm_file)) in INBOX_DIR:
                            this_YFM[key] = "true"
                        else:
                            this_YFM[key] = "false"
                    # Add an element to the end of the header
                    lines.insert(end_of_yfm, key + ': ' + this_YFM[key] + '\n')
                    end_of_yfm += 1
            # writing header
            writing_lines_without_hashtags(update_yfm_file, lines)
    print('\n====== Start Add New YFM ======')
    print('the target is: ' + str(len(create_yfm_files)) + ' files\n')
    for create_yfm_file in create_yfm_files:
        print("Creating YFM...")
        print("target: " + create_yfm_file)
        with open(create_yfm_file) as f:
            lines = f.readlines()
            tag_line = create_tag_line_from_lines(lines)
            print("insert YFM...")
            dt = datetime.datetime
            date_value = datetime.datetime.fromtimestamp(os.stat(create_yfm_file).st_birthtime)
            update_value = datetime.datetime.fromtimestamp(os.path.getmtime(create_yfm_file))
            this_YFM = YFM
            this_YFM['title'] = os.path.splitext(os.path.basename(create_yfm_file))[0]
            this_YFM['date'] = date_value.strftime('%Y-%m-%d %H:%M:%S')
            this_YFM['update'] = update_value.strftime('%Y-%m-%d %H:%M:%S')
            this_YFM['tags'] = tag_line
            if os.path.basename(os.path.dirname(create_yfm_file)) in INBOX_DIR:
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
            print(YFM_text)
            lines.insert(0, YFM_text)
            # writing header
            writing_lines_without_hashtags(create_yfm_file, lines)

def create_tag_line_from_lines(lines):
    '''create tag line for YFM from hashtags'''
    print('checking tags...')
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
        print("writing file...")
        for line in lines:
            # Delete the hashtag line
            if not re.match("^\#[^\#|^\s].+", line):
                wf.write(line)
        print("done!\n")

def rename_notes_with_links(files):
    '''Rename the all file names to UID and update wikilinks to Markdownlinks'''
    print('\n====== Start Rename Notes And Substitute Wikilinks ======')
    print('the target is: ' + str(len(files)) + ' files\n')
    for file in files: 
        print("target: " + file)
        if check_note_has_uid(file):
            print("It seems that this file already has a UID\n")
            continue
        else:
            new_file_path = get_new_filepath_with_uid(file)
            print("rename: " + new_file_path)
            # rename and move ROOT PATH
            new_file_path_result = shutil.move(file, new_file_path)
            print("rename done: " + new_file_path_result)
            # add UID to top of YFM
            with open(new_file_path_result) as f:
                lines = f.readlines()
                lines.insert(1, "uid: " + str(os.path.splitext(os.path.basename(new_file_path_result))[0]) + "\n")
                with open(new_file_path_result, mode='w') as wf:
                    wf.writelines(lines)
            substitute_wikilinks_to_markdown_links(file, new_file_path_result)

def rename_images_with_links(files):
    print('\n====== Start Rename Images And Substitute Wikilinks ======')
    print('the target is: ' + str(len(files)) + ' files\n')
    for file in files:
        print("target: " + file)
        if check_note_has_uid(file):
            print("It seems that this file already has a UID\n")
            continue
        else:
            # rename image
            new_file_path = get_new_filepath_with_uid(file)
            os.rename(file, new_file_path)
            print("rename: " + new_file_path)
            substitute_wikilinks_to_markdown_links(file, new_file_path)

def check_note_has_uid(file):
    file_title = os.path.splitext(os.path.basename(file))[0]
    return re.match('^\d{14}$', file_title)

def get_new_filepath_with_uid(file):
    '''get new filepath with uid'''
    # UID is yyyymmddhhmmss from create date
    uid = datetime.datetime.fromtimestamp(os.stat(file).st_birthtime)
    uid = int(uid.strftime('%Y%m%d%H%M%S'))
    ext = os.path.splitext(os.path.basename(file))[1]
    if ext == '.md':
        path = ROOT_PATH
    else:
        path = os.path.dirname(file)
    # Add 1 if the UID is duplicated
    while os.path.exists(build_filepath_by_uid(uid, ext, path)):
        uid += 1
    return build_filepath_by_uid(uid, ext, path)

def build_filepath_by_uid(uid, ext='.md', path=ROOT_PATH):
    return path + '/' + str(uid) + ext

def substitute_wikilinks_to_markdown_links(old_file_path, new_file_path):
    '''substitute wikilinks to markdown links'''
    # build file info
    old_file_title = os.path.splitext(os.path.basename(old_file_path))[0]
    old_file_ext = os.path.splitext(os.path.basename(old_file_path))[1]
    new_file_link = os.path.basename(new_file_path)
    print("substitute Wikilinks...")
    update_link_files = get_files('note')
    # check all notes links
    for update_link_file in update_link_files:
        with open(update_link_file, mode='r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Replace the target Wikilinks if any
                match = re.search('\[\[(' + old_file_title + '(' + old_file_ext + ')?'+ '(\s\|\s(.+))?)\]\]', line)
                if match:
                    print("match: " + old_file_path)
                    print("substitute: " + match.group(0))
                    # If Alias is set in the Link, use Alias as the Link Text
                    if match.group(4):
                        lines[i] = line.replace(match.group(0), '[' + match.group(4) + '](' + new_file_link + ')')
                    else:
                        lines[i] = line.replace(match.group(0), '[' + match.group(1) + '](' + new_file_link + ')')
                    print(lines[i])
            with open(update_link_file, mode='w') as wf:
                wf.writelines(lines)
    print("done!\n")

if __name__ == '__main__':
'''This is the main process to implement the enabled features'''
    if function_create_yfm:
        check_and_create_yfm(get_files('note'))

    if function_rename_notes:
        rename_notes_with_links(get_files('note'))

    if function_rename_images: 
        rename_images_with_links(get_files('image'))
