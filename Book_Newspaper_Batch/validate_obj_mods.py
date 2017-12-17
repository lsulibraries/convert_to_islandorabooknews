import os
import sys
from jpylyzer import jpylyzer
from PIL import Image


def sort_child_folders_by_contents(children_folders):
    this_dict = dict()
    for child_folder in children_folders:
        sorted_files = tuple(sorted(os.listdir(child_folder)))
        if this_dict.get(sorted_files):
            this_dict[sorted_files].append(child_folder)
        else:
            this_dict[sorted_files] = [child_folder, ]
    for k, v in this_dict.items():
        print(k, len(v))
    return this_dict


def fix_bad_characters(path):
    with open(path, 'r') as f:
        text = f.read().encode('utf-8')
    if b'\xc2\xa0' in text:
        text = text.replace(b'\xc2\xa0', b'\x20')
    with open(path, 'w') as f:
        f.write(text.decode('utf-8'))


def validate_text_file(path):
    with open(path, 'r') as f:
        text = f.read()
        for num, char in enumerate(text):
            if not char.replace('\b', '').replace('\n', '').replace('\t', '').strip().isprintable():
                return False
    return True


def validate_image(path):
    with Image.open(path) as im:
        if im.format not in ('JPEG2000', 'JPEG'):
            print(path, im.format)
            return False
        if im.format == 'JPEG2000':
            jpylyzed = jpylyzer.checkOneFile(path)
            if not jpylyzed.findtext('isValidJP2'):
                print(path, 'is not valid')
                return False
        if im.mode not in ('RGB', ):
            print(path, im.mode)
            return False
    with Image.open(path) as im:
        im.verify()
    return True


def validate_or_repair_or_complain_text_file(root):
    text_types = ['HOCR.html', 'MODS.xml', 'OCR.txt']
    for text_type in text_types:
        path = os.path.join(root, text_type)
        if not validate_text_file(path):
            fix_bad_characters(path)
            if not validate_text_file(path):
                print(path, 'is not a valid textfile')


def validate_or_complain_image_files(root):
    image_types = ['JP2.jp2', 'JPG.jpg', 'OBJ.jp2', 'TN.jpg']
    for image_type in image_types:
        path = os.path.join(root, image_type)
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

    children_folders = [root for root, dirs, files in os.walk(collection_path)
                        if os.path.split(os.path.split(root)[0])[1].isnumeric()]
    derivs_dict = sort_child_folders_by_contents(children_folders)
    for k, roots in derivs_dict.items():
        for root in roots:
            validate_or_repair_or_complain_text_file(root)
            validate_or_complain_image_files(root)
