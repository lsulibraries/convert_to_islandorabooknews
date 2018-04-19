#! /usr/bin/env python3.6

import os
import subprocess
import shutil
import sys

import make_book_derivs


def split_pdf_to_tiff(pointer, source_root, output_root):
    filename = '{}.pdf'.format(pointer)
    if filename not in os.listdir(source_root):
        print('Exiting:  expected {} in folder {}'.format(filename, source_root))
        exit()
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    arguments = ['convert',
                 '-density',
                 '300',
                 os.path.join(source_root, filename),
                 '-depth',
                 '8',
                 os.path.join(dest_root, '%04d.tif')
                 ]
    subprocess.call(arguments)


def move_images_to_subfolders(all_page_images):
    for source_path in all_page_images:
        root, filename = os.path.split(source_path)
        prefix, extension = os.path.splitext(filename)
        prefix_plus_one = str(int(prefix) + 1)
        dest_path = os.path.join(root, prefix_plus_one)
        os.makedirs(dest_path, exist_ok=True)
        shutil.move(source_path, os.path.join(dest_path, 'OBJ.tif'))


def find_all_images(output_root):
    all_output_images = []
    for parent_folder in os.listdir(output_root):
        parent_path = os.path.join(output_root, parent_folder)
        if not os.path.isdir(parent_path):
            continue
        for file in os.listdir(parent_path):
            child_filepath = os.path.join(parent_path, file)
            if not os.path.isfile(child_filepath):
                continue
            if os.path.splitext(child_filepath)[1] == '.tif':
                all_output_images.append(child_filepath)
    return all_output_images


def move_mods_files(pointer, source_root, output_root):
    source_filepath = os.path.join(source_root, '{}.xml'.format(pointer))
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)


def move_pdfs_to_subfolders(pointer, source_root, output_root):
    source_filepath = os.path.join(source_root, '{}.pdf'.format(pointer))
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'PDF.pdf')
    shutil.copy2(source_filepath, dest_filepath)


def convert_an_item(pointer, source_root, output_root):
    split_pdf_to_tiff(pointer, source_root, output_root)
    move_mods_files(pointer, source_root, output_root)
    all_page_images = find_all_images(output_root)
    move_images_to_subfolders(all_page_images)
    move_pdfs_to_subfolders(pointer, source_root, output_root)


def main(source_root):
    source_root = os.path.realpath(source_root)
    parent_root, source_folder = os.path.split(source_root)
    output_root = os.path.join(parent_root, '{}-to-book'.format(source_folder))
    os.makedirs(output_root, exist_ok=True)

    pointers = {os.path.splitext(i)[0] for i in os.listdir(source_root)}
    fits_path = make_book_derivs.find_fits_package()
    for pointer in pointers:
        convert_an_item(pointer, source_root, output_root)
        parent_root = os.path.join(output_root, pointer)
        make_book_derivs.do_child_level(parent_root, fits_path)


if __name__ == '__main__':
    try:
        source_root = sys.argv[1]
    except IndexError:
        print('\nChange to: "python3 convert_pdf_to_book_with_derivatives.py $path/to/source_pdf_folder"\n')
        quit()
    if '-pdf' in source_root:
        main(source_root)
    else:
        print('Expected "institution-namespace-pdf" folder name')
        print('No files processed')
        exit()