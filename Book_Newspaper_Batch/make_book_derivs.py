#! /usr/bin/env python3.6

import os
import sys
import subprocess
import shutil
import multiprocessing


def make_JPG(path):
    input_path = os.path.join(path, 'OBJ.tif')
    output_path = os.path.join(path, 'JPG.jpg')
    arguments = ['convert',
                 '-quality',
                 '75',
                 '-resize',
                 '600 x 800',
                 input_path,
                 '-colorspace',
                 'RGB',
                 output_path]
    subprocess.call(arguments)


def make_TN(path):
    input_path = os.path.join(path, 'OBJ.tif')
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


def shrink_PDF(path):
    input_path = os.path.join(path, 'TN.jpg')
    short_output_path = os.path.join(path, 'PDF')
    arguments = ['tesseract',
                 input_path,
                 short_output_path,
                 'pdf']
    subprocess.call(arguments)


def extract_text(path):
    input_path = os.path.join(path, 'PDF.pdf')
    output_path = os.path.join(path, 'OCR.txt')
    arguments = ['pdf2txt',
                 '-o',
                 output_path,
                 input_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def make_PDF_if_not_one(path):
    input_path = os.path.join(path, 'OBJ.tif')
    output_path = os.path.join(path, 'PDF.pdf')
    arguments = ['convert',
                 input_path,
                 output_path]
    if not os.path.isfile(output_path):
        subprocess.call(arguments)


def make_OCR_from_tif(path):
    input_path = os.path.join(path, 'OBJ.tif')
    output_path = os.path.join(path, 'OCR')
    arguments = ['tesseract',
                 input_path,
                 output_path]
    subprocess.call(arguments)


def make_OCR(path):
    input_path = os.path.join(path, 'PDF.pdf')
    output_path = os.path.join(path, 'OCR.txt')
    arguments = ['pdftotext',
                 input_path,
                 output_path]
    subprocess.call(arguments)
    if os.path.getsize(output_path) < 10:
        make_OCR_from_tif(path)
        print(os.path.getsize(output_path))


def make_HOCR(path):
    input_path = os.path.join(path, 'OBJ.tif')
    short_output_path = os.path.join(path, 'HOCR')
    arguments = ['tesseract',
                 input_path,
                 short_output_path,
                 'hocr']
    subprocess.call(arguments)
    subprocess.call(['mv', os.path.join(path, 'HOCR.hocr'), os.path.join(path, 'HOCR.html')])


def find_fits_package():
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
    subprocess.call(arguments)


def make_JP2(folder):
    input_path = os.path.join(folder, 'OBJ.tif')
    output_path = os.path.join(folder, 'JP2.jp2')
    kakadu_arguments = ["kdu_compress",
                        "-i",
                        input_path,
                        "-o",
                        output_path,
                        "-rate",
                        "0.5",
                        "Clayers=1",
                        "Clevels=7",
                        "Cprecincts={256,256},{256,256},{256,256},{128,128},{128,128},{64,64},{64,64},{32,32},{16,16}",
                        "Corder=RPCL",
                        "ORGgen_plt=yes",
                        "ORGtparts=R",
                        "Cblk={32,32}",
                        "Cuse_sop=yes"]
    error_message = subprocess.call(kakadu_arguments)
    if error_message:
        imagemagick_arguments = ['convert',
                                 input_path,
                                 output_path]
        subprocess.call(imagemagick_arguments)


def replace_obj_with_jp2(folder):
    orig_obj_file = os.path.join(folder, 'OBJ.tif')
    jp2_file = os.path.join(folder, 'JP2.jp2')
    new_object_file = os.path.join(folder, 'OBJ.jp2')
    os.remove(orig_obj_file)
    shutil.copy2(jp2_file, new_object_file)


def make_book_level_thumbnail(page_folder):
    collection_outputpath, page_num = os.path.split(page_folder)
    if int(page_num) == 1:
        first_page_tn = os.path.join(collection_outputpath, '0001', 'TN.jpg')
        parent_tn = os.path.join(collection_outputpath, 'TN.jpg')
        shutil.copy2(first_page_tn, parent_tn)


def do_page_folder(folder, fits_path, results):
    print(folder)
    if not os.path.isfile(os.path.join(folder, 'OBJ.tif')):
        print('page already done {}'.format(folder))
        return
    make_HOCR(folder)
    make_JP2(folder)
    make_JPG(folder)
    make_TN(folder)
    make_PDF_if_not_one(folder)
    make_OCR(folder)

    replace_obj_with_jp2(folder)
    make_fits(folder, fits_path)
    shrink_PDF(folder)
    make_book_level_thumbnail(folder)


def do_child_levels(parent_root, fits_path):
    child_folders = [os.path.join(parent_root, i)
                     for i in os.listdir(parent_root)
                     if os.path.isdir(os.path.join(parent_root, i))]
    results = multiprocessing.Queue()
    jobs = [
        multiprocessing.Process(target=do_page_folder, args=(folder, fits_path, results))
        for folder in sorted(child_folders)
    ]
    for i in jobs:
        i.start()
    for i in jobs:
        i.join()


if __name__ == '__main__':
    try:
        collection_path = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python make_book_derivs.py {{ path_to_folder }}"')
        print('')
        exit()
    fits_path = find_fits_package()
    parent_folders = [os.path.join(collection_path, i)
                      for i in os.listdir(collection_path)
                      if os.path.isdir(os.path.join(collection_path, i))]
    for folder in sorted(parent_folders):
        do_child_levels(folder, fits_path)
