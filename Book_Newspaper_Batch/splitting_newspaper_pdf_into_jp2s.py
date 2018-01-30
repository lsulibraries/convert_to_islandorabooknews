#! /usr/bin/env python3

import os
import subprocess
import shutil
import sys


def split_pdf_to_jp2s(pdf_file, output_root):
    root, filename = os.path.split(pdf_file)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    if os.path.isdir(dest_root):
        return
    os.makedirs(dest_root, exist_ok=True)
    subprocess.call(['convert',
                     '-density',
                     '300',
                     os.path.join(root, filename),
                     '-quality',
                     '75',
                     '-colorspace',
                     'RGB',
                     os.path.join(dest_root, '%03d.jp2'),
                     ])


def move_jp2s_to_subfolders(filepath):
    root, filename = os.path.split(filepath)
    prefix, extension = os.path.splitext(filename)
    prefix_plus_one = str(int(prefix) + 1)
    dest_filepath = os.path.join(root, prefix_plus_one)
    print(filepath, dest_filepath)
    os.makedirs(dest_filepath, exist_ok=True)
    shutil.move(filepath, os.path.join(dest_filepath, 'OBJ.jp2'))


def move_mods_files(source_filepath, output_root):
    root, filename = os.path.split(source_filepath)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'MODS.xml')
    print(source_filepath, dest_filepath)
    shutil.copy2(source_filepath, dest_filepath)


def find_all_jp2s(output_root):
    all_output_jp2s = []
    for parent_folder in os.listdir(output_root):
        parent_path = os.path.join(output_root, parent_folder)
        if not os.path.isdir(parent_path):
            continue
        for file in os.listdir(parent_path):
            child_filepath = os.path.join(parent_path, file)
            if not os.path.isfile(child_filepath):
                continue
            if os.path.splitext(child_filepath)[1] == '.jp2':
                all_output_jp2s.append(child_filepath)
    return all_output_jp2s


def move_pdfs_to_subfolders(source_filepath, output_root):
    root, filename = os.path.split(source_filepath)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'PDF.pdf')
    print(source_filepath, dest_filepath)
    shutil.copy2(source_filepath, dest_filepath)


if __name__ == '__main__':

    try:
        source_root = sys.argv[1]
    except IndexError:
        print('\nChange to: "python splitting_newspaper_pdf_into_jp2.py $path/to/source_pdf_folder"\n')
        quit()

    source_root = os.path.realpath(source_root)
    parent_root, source_folder = os.path.split(source_root)
    output_root = os.path.join(parent_root, '{}-to-book'.format(source_folder))
    os.makedirs(output_root, exist_ok=True)

    all_source_pdfs = [os.path.join(source_root, i)
                       for i in os.listdir(source_root)
                       if os.path.splitext(i)[1] == '.pdf']

    for filepath in sorted(all_source_pdfs):
        print(os.path.split(filepath))
        split_pdf_to_jp2s(filepath, output_root)

    all_source_mods = [os.path.join(source_root, i)
                       for i in os.listdir(source_root)
                       if os.path.splitext(i)[1] == '.xml']

    for filepath in sorted(all_source_mods):
        move_mods_files(filepath, output_root)

    all_output_jp2s = find_all_jp2s(output_root)
    print(len(all_output_jp2s))

    for filepath in sorted(all_output_jp2s):
        move_jp2s_to_subfolders(filepath)

    for filepath in sorted(all_source_pdfs):
        print(filepath)
        move_pdfs_to_subfolders(filepath, output_root)
