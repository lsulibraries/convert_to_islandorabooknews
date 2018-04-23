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


def split_pdf_into_page_pdfs(pointer, source_root, output_root):
    filename = '{}.pdf'.format(pointer)
    if filename not in os.listdir(source_root):
        print('Exiting:  expected {} in folder {}'.format(filename, source_root))
        exit()
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    arguments = ['pdftk',
                 os.path.join(source_root, filename),
                 'burst',
                 'output',
                 os.path.join(dest_root, '%04d.pdf')
                 ]
    subprocess.call(arguments)
    os.remove(os.path.join(dest_root, 'doc_data.txt'))


def move_children_to_subfolders(all_page_tifs, filetype):
    for source_path in all_page_tifs:
        root, filename = os.path.split(source_path)
        prefix, extension = os.path.splitext(filename)
        # imagemagick-convert 0 indexes, while pdftk 1 indexes.  Magic Numbers to output with 1 index.
        if filetype == 'tif':
            magic_number = 1
        elif filetype == 'pdf':
            magic_number = 0
        prefix_plus_one = str(int(prefix) + magic_number)
        dest_path = os.path.join(root, prefix_plus_one)
        os.makedirs(dest_path, exist_ok=True)
        if filetype == 'tif':
            output_name = 'OBJ.tif'
        elif filetype == 'pdf':
            output_name = 'PDF.pdf'
        shutil.move(source_path, os.path.join(dest_path, output_name))


def find_page_files(output_root, filetype):
    all_child_files = []
    for parent_folder in os.listdir(output_root):
        parent_path = os.path.join(output_root, parent_folder)
        if not os.path.isdir(parent_path):
            continue
        for file in os.listdir(parent_path):
            child_filepath = os.path.join(parent_path, file)
            if not os.path.isfile(child_filepath):
                continue
            if file == 'PDF.pdf':
                continue
            if os.path.splitext(child_filepath)[1].replace('.', '') == filetype:
                all_child_files.append(child_filepath)
    return all_child_files


def copy_mods_files(pointer, source_root, output_root):
    source_filepath = os.path.join(source_root, '{}.xml'.format(pointer))
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)


def move_parent_pdfs_to_subfolders(pointer, source_root, output_root):
    source_filepath = os.path.join(source_root, '{}.pdf'.format(pointer))
    dest_root = os.path.join(output_root, pointer)
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'PDF.pdf')
    shutil.copy2(source_filepath, dest_filepath)


def convert_an_item(pointer, source_root, output_root):
    split_pdf_into_page_pdfs(pointer, source_root, output_root)
    all_page_pdfs = find_page_files(output_root, 'pdf')
    move_children_to_subfolders(all_page_pdfs, 'pdf')
    split_pdf_to_tiff(pointer, source_root, output_root)
    all_page_tifs = find_page_files(output_root, 'tif')
    move_children_to_subfolders(all_page_tifs, 'tif')
    copy_mods_files(pointer, source_root, output_root)
    move_parent_pdfs_to_subfolders(pointer, source_root, output_root)


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
