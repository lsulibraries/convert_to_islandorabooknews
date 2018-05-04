import os
import sys
import subprocess
import string

from jpylyzer import jpylyzer
from PIL import Image
from lxml import etree as ET


def find_mods_schema():
    sysout = subprocess.getoutput('find / -name mods-3-6.xsd')
    programs_list = [i for i in sysout.split('\n')]
    if not programs_list:
        print('mods-3-6.xsd needs to be downloaded')
        exit()
    return programs_list[0]


def sort_child_folders_by_contents(children_folders):
    this_dict = dict()
    for child_folder in children_folders:
        sorted_files = tuple(sorted(os.listdir(child_folder)))
        if this_dict.get(sorted_files):
            this_dict[sorted_files].append(child_folder)
        else:
            this_dict[sorted_files] = [child_folder, ]
    return this_dict


def fix_bad_characters(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read().encode('utf-8')
    printable_codepoints = set([i for i in range(5000) if chr(i).isprintable()])
    good_whitespace_codepoints = set([32, 9, 10, 11, 12, 13])
    acceptable_codepoints = printable_codepoints.union(good_whitespace_codepoints)
    new_text = bytearray([
        i for i in text
        if i in acceptable_codepoints])
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_text.decode('utf-8', 'ignore'))


def has_invalid_characters(path):
    invalid_characters = set()
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
        for num, char in enumerate(text):
            if char in ('\b', '\n', '\t', ' '):
                continue
            if not char.isprintable():
                invalid_characters.add(char)
    if invalid_characters:
        return invalid_characters
    return None


def validate_image(path):
    with Image.open(path) as im:
        if im.format not in ('JPEG2000', 'JPEG'):
            print(path, im.format, 'format')
            return False
        if im.format == 'JPEG2000':
            jpylyzed = jpylyzer.checkOneFile(path)
            if not jpylyzed.findtext('isValidJP2'):
                print(path, 'is not valid')
                return False
        if im.mode not in ('RGB', 'RGBA', 'L'):
            print(path, im.mode, 'mode')
            return False
    with Image.open(path) as im:
        im.verify()
    return True


def validate_mods(mods_filepath, MODS_SCHEMA):
    if not os.path.isfile(mods_filepath):
        return
    file_etree = ET.parse(mods_filepath)
    if not MODS_SCHEMA.validate(file_etree):
        print("{} post-xsl did not validate!!!!".format(mods_filepath))


def validate_or_repair_or_complain_text_file(root):
    text_types = ['HOCR.html', 'OCR.txt']
    for text_type in text_types:
        path = os.path.join(root, text_type)
        if not os.path.isfile(path):
            continue
        if has_invalid_characters(path):
            fix_bad_characters(path)
            remaining_invalid_chars = has_invalid_characters(path)
            if remaining_invalid_chars:
                print('{} has invalid characters: ordinals {}'.format(path, remaining_invalid_chars))


def validate_or_complain_image_files(root):
    image_types = ['JP2.jp2', 'JPG.jpg', 'OBJ.jp2', 'TN.jpg']
    for image_type in image_types:
        path = os.path.join(root, image_type)
        if not os.path.isfile(path):
            continue
        if not validate_image(path):
            print(path, 'is not a valid image')


if __name__ == '__main__':
    try:
        collection_path = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python validate_folder.py {{path_to_folder}}"')
        print('')
        exit()

    mods_schema_file = find_mods_schema()
    MODS_DEF = ET.parse(mods_schema_file)
    MODS_SCHEMA = ET.XMLSchema(MODS_DEF)

    children_folders = [root for root, dirs, files in os.walk(collection_path)
                        if os.path.split(os.path.split(root)[0])[1].isnumeric()]
    parent_and_child_folders = [root for root, dirs, files in os.walk(collection_path)
                                if os.path.split(root)[1].isnumeric()]
    derivs_dict = sort_child_folders_by_contents(children_folders)

    for k, v in derivs_dict.items():
        print(k, len(v))
        if len(k) < 8:
            print('ERROR:  These paths have less than 8 derivs per page')
            for path in v:
                print(path)
    for root in sorted(parent_and_child_folders):
        validate_or_repair_or_complain_text_file(root)
        validate_mods(os.path.join(root, 'MODS.xml'), MODS_SCHEMA)
        validate_or_complain_image_files(root)
