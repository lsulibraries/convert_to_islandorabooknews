#! /usr/bin/env python3

import os
import subprocess
import shutil
import sys


def split_pdf_to_jp2s(pdf_file):
    root, filename = os.path.split(pdf_file)
    dest_root = os.path.join(root, 'Jp2BookConverted', os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    print(root, filename)
    subprocess.call(['convert',
                     '-density',
                     '300',
                     os.path.join(root, filename),
                     '-quality',
                     '75',
                     os.path.join(dest_root, '%03d.jp2'),
                     ])


def move_jp2s_to_subfolders(filepath):
    root, filename = os.path.split(filepath)
    prefix, extension = os.path.splitext(filename)
    prefix_plus_one = str(int(prefix) + 1)
    dest_filepath = os.path.join(root, prefix_plus_one)
    os.makedirs(dest_filepath)
    shutil.move(filepath, dest_filepath)
    shutil.move(os.path.join(dest_filepath, filename), os.path.join(dest_filepath, 'OBJ.jp2'))


def move_mods_files(mods_file):
    root, filename = os.path.split(mods_file)
    dest_root = os.path.join(root, 'Jp2BookConverted', os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    shutil.copy2(mods_file, os.path.join(dest_root, 'MODS.xml'))


def find_all_filetype(directory, filetype):
    all_this_type = [os.path.join(root, file)
                     for root, dirs, files in os.walk(directory)
                     for file in files
                     if os.path.splitext(file)[1] == filetype]
    return all_this_type


if __name__ == '__main__':

    try:
        source_dir = sys.argv[1]
    except IndexError:
        print('\nChange to: "python splitting_newspaper_pdf_into_jp2.py $path/to/source_pdf_folder"\n')
        quit()
    all_pdf_files = find_all_filetype(source_dir, '.pdf')
    all_mods_files = find_all_filetype(source_dir, '.xml')
    all_jp2_files = find_all_filetype(source_dir, '.jp2')

    for filepath in all_pdf_files:
        split_pdf_to_jp2s(filepath)

    for filepath in all_mods_files:
        move_mods_files(filepath)

    for filepath in all_jp2_files:
        move_jp2s_to_subfolders(filepath)
