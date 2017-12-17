#! /usr/bin/env python3

import os
import sys
import subprocess


def make_JPG(path):
    input_path = os.path.join(path, 'OBJ.jp2')
    output_path = os.path.join(path, 'JPG.jpg')
    arguments = ['convert',
                 input_path,
                 output_path]
    subprocess.call(arguments)


def shrink_JPG(path):
    input_path = os.path.join(path, 'OBJ.jp2')
    output_path = os.path.join(path, 'JPG.jpg')
    arguments = ['convert',
                 '-quality',
                 '75',
                 '-resize',
                 '600 x 800',
                 input_path,
                 output_path]
    subprocess.call(arguments)


def make_TN(path):
    input_path = os.path.join(path, 'OBJ.jp2')
    output_path = os.path.join(path, 'TN.jpg')
    arguments = ['convert',
                 input_path,
                 '-quality',
                 '75',
                 '-resize',
                 '200 x 200',
                 '-colorspace',
                 'RGB',
                 output_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def make_PDF(path):
    input_path = os.path.join(path, 'JPG.jpg')
    output_path = os.path.join(path, 'PDF.pdf')
    short_output_path = os.path.join(path, 'PDF')
    arguments = ['tesseract',
                 input_path,
                 short_output_path,
                 'pdf']
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def make_OCR(path):
    input_path = os.path.join(path, 'JPG.jpg')
    output_path = os.path.join(path, 'OCR.txt')
    short_output_path = os.path.join(path, 'OCR')
    arguments = ['tesseract',
                 input_path,
                 short_output_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def make_HOCR(path):
    input_path = os.path.join(path, 'JPG.jpg')
    output_path = os.path.join(path, 'HOCR.html')
    short_output_path = os.path.join(path, 'HOCR')
    arguments = ['tesseract',
                 input_path,
                 short_output_path,
                 'hocr']
    if not os.path.isfile(output_path):
        subprocess.call(arguments)
        subprocess.call(['mv', os.path.join(path, 'HOCR.hocr'), os.path.join(path, 'HOCR.html')])


def make_JP2(path):
    input_path = os.path.join(path, 'OBJ.jp2')
    output_path = os.path.join(path, 'JP2.jp2')
    arguments = ['cp',
                 input_path,
                 output_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def find_fits():
    sysout = subprocess.getoutput('find / -name fits.sh')
    programs_list = [i for i in sysout.split('\n')]
    if not programs_list:
        print('fits.sh needs to be installed')
        exit()
    our_version = [i for i in programs_list if '0.8.5' in i]
    if not our_version:
        return programs_list[0]
    return our_version[0]


def make_fits(root, fits_path):
    input_path = os.path.join(root, 'OBJ.jp2')
    output_path = os.path.join(root, 'TECHMD.xml')
    # Islanodora has a try expect block here
    # with a ./fits.sh -i xxxxx -x -o xxxxx
    # fallback.
    arguments = [fits_path,
                 '-i',
                 input_path,
                 '-xc',
                 '-o',
                 output_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


# Note:  tesseract uses the jpg - so we make a full quality one first,
# then overwrite it with the correct medium size one at the end.

if __name__ == '__main__':
    try:
        collection_path = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python validate_derivs_output.py {{path_to_folder}}"')
        print('')
        exit()

fits_path = find_fits()
for root, dirs, files in sorted(os.walk(collection_path)):
    print(root)
    if os.path.split(os.path.split(root)[0])[1].isnumeric():
        make_JPG(root)
        make_TN(root)
        make_PDF(root)
        make_OCR(root)
        make_HOCR(root)
        make_JP2(root)
        make_fits(root, fits_path)
for root, dirs, files in sorted(os.walk(collection_path)):
    if os.path.split(root)[1].isnumeric():
        shrink_JPG(root)
