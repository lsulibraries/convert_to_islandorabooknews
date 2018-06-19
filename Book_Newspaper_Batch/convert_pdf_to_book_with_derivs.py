#! /usr/bin/env python3.6

import os
import sys
import shutil
import subprocess

import make_book_derivs


def main(collection_sourcepath):
    collection_sourcepath = os.path.realpath(collection_sourcepath)
    parent_root, collection_name = os.path.split(collection_sourcepath)
    collection_outputpath = os.path.join(parent_root, '{}-to-book'.format(collection_name))
    os.makedirs(collection_outputpath, exist_ok=True)
    book_names = {os.path.splitext(i)[0] for i in os.listdir(collection_sourcepath)}
    already_converted_books = {os.path.splitext(i)[0] for i in os.listdir(collection_outputpath)}
    books_needing_converting = book_names - already_converted_books
    fits_path = make_book_derivs.find_fits_package()
    for book_name in sorted(books_needing_converting):
        convert_an_item(book_name, collection_sourcepath, collection_outputpath)
        book_outputpath = os.path.join(collection_outputpath, book_name)
        make_book_derivs.do_child_level(book_outputpath, fits_path)
        make_parent_tn(book_outputpath)
    subprocess.call(['chmod', '-R', 'u+rwX,go+rX,go-w', collection_outputpath])


def convert_an_item(book_name, collection_sourcepath, collection_outputpath):
    split_pdf_into_page_pdfs(book_name, collection_sourcepath, collection_outputpath)
    all_page_pdfs = find_page_files(collection_outputpath, 'pdf')
    move_children_to_subfolders(all_page_pdfs, 'pdf')
    book_outputpath = os.path.join(collection_outputpath, book_name)
    page_folders = [os.path.join(book_outputpath, i)
                    for i in os.listdir(book_outputpath)
                    if os.path.isdir(os.path.join(book_outputpath, i))
                    ]
    for page_folder in sorted(page_folders):
        convert_page_pdf_to_tif(page_folder)
    copy_mods_files(book_name, collection_sourcepath, collection_outputpath)
    move_parent_pdfs_to_subfolders(book_name, collection_sourcepath, collection_outputpath)


def split_pdf_into_page_pdfs(book_name, collection_sourcepath, collection_outputpath):
    filename = '{}.pdf'.format(book_name)
    if filename not in os.listdir(collection_sourcepath):
        print('Exiting:  expected {} in folder {}'.format(filename, collection_sourcepath))
        exit()
    book_outputpath = os.path.join(collection_outputpath, book_name)
    os.makedirs(book_outputpath, exist_ok=True)
    arguments = ['pdftk',
                 os.path.join(collection_sourcepath, filename),
                 'burst',
                 'output',
                 os.path.join(book_outputpath, '%04d.pdf')
                 ]
    subprocess.call(arguments)
    os.remove(os.path.join(book_outputpath, 'doc_data.txt'))


def convert_page_pdf_to_tif(page_folder):
    arguments = ['convert',
                 '-density',
                 '300',
                 os.path.join(page_folder, 'PDF.pdf'),
                 '-depth',
                 '8',
                 '-flatten',
                 os.path.join(page_folder, 'OBJ.tif')
                 ]
    subprocess.call(arguments)


def find_page_files(collection_outputpath, filetype):
    all_child_files = []
    for parent_folder in os.listdir(collection_outputpath):
        parent_path = os.path.join(collection_outputpath, parent_folder)
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


def move_children_to_subfolders(all_page_tifs, filetype):
    for source_path in all_page_tifs:
        root, filename = os.path.split(source_path)
        prefix, extension = os.path.splitext(filename)
        dest_path = os.path.join(root, prefix)
        os.makedirs(dest_path, exist_ok=True)
        shutil.move(source_path, os.path.join(dest_path, 'PDF.pdf'))


def copy_mods_files(book_name, collection_sourcepath, collection_outputpath):
    source_filepath = os.path.join(collection_sourcepath, '{}.xml'.format(book_name))
    book_outputpath = os.path.join(collection_outputpath, book_name)
    os.makedirs(book_outputpath, exist_ok=True)
    dest_filepath = os.path.join(book_outputpath, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)


def move_parent_pdfs_to_subfolders(book_name, collection_sourcepath, collection_outputpath):
    source_filepath = os.path.join(collection_sourcepath, '{}.pdf'.format(book_name))
    book_outputpath = os.path.join(collection_outputpath, book_name)
    os.makedirs(book_outputpath, exist_ok=True)
    dest_filepath = os.path.join(book_outputpath, 'PDF.pdf')
    shutil.copy2(source_filepath, dest_filepath)


def make_parent_tn(collection_outputpath):
    first_page_tn = os.path.join(collection_outputpath, '0001', 'TN.jpg')
    parent_tn = os.path.join(collection_outputpath, 'TN.jpg')
    shutil.copy2(first_page_tn, parent_tn)


if __name__ == '__main__':
    try:
        collection_sourcepath = sys.argv[1]
    except IndexError:
        print('\nChange to: "python3 convert_pdf_to_book_with_derivatives.py $path/to/source_pdf_folder"\n')
        quit()
    if os.path.split(collection_sourcepath)[-1][-4:] == '-pdf':
        main(collection_sourcepath)
    else:
        print('Expected "institution-namespace-pdf" folder name')
        print('No files processed')
        exit()
