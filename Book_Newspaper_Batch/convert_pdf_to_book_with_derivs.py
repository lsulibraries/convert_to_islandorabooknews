#! /usr/bin/env python3.6

import os
import sys
import shutil
import subprocess
import multiprocessing

import make_book_derivs


FITS_PATH = make_book_derivs.find_fits_package()


def main(collection_sourcepath):
    collection_sourcepath = os.path.realpath(collection_sourcepath)
    collection_root, collection_name = os.path.split(collection_sourcepath)
    collection_outputpath = os.path.join(collection_root, '{}-to-book'.format(collection_name))
    os.makedirs(collection_outputpath, exist_ok=True)
    process_collection(collection_sourcepath, collection_outputpath)
    subprocess.call(['chmod', '-R', 'u+rwX,go+rX,go-w', collection_outputpath])


def process_collection(collection_sourcepath, collection_outputpath):
    book_names = {os.path.splitext(i)[0] for i in os.listdir(collection_sourcepath)}
    already_converted_books = {os.path.splitext(i)[0] for i in os.listdir(collection_outputpath)}
    books_needing_converting = book_names - already_converted_books
    print("collection total: {}\nto do: {},\ndone: {}\n".format(
        len(book_names), len(books_needing_converting), len(already_converted_books))
    )
    loop_through_books(
        collection_sourcepath,
        collection_outputpath,
        books_needing_converting
    )


def loop_through_books(collection_sourcepath, collection_outputpath, books_needing_converting):
    for book_name in sorted(books_needing_converting):
        convert_a_book(
            book_name,
            collection_sourcepath,
            collection_outputpath
        )


def convert_a_book(book_name, collection_sourcepath, collection_outputpath):
    split_pdf_into_page_pdfs(book_name, collection_sourcepath, collection_outputpath)
    all_page_pdfs = find_page_files(collection_outputpath, 'pdf')
    move_pages_to_subfolders(all_page_pdfs, 'pdf')
    prep_page(book_name, collection_outputpath)
    move_book_pdfs_to_subfolders(book_name, collection_sourcepath, collection_outputpath)
    book_outputpath = os.path.join(collection_outputpath, book_name)
    make_book_derivs.do_page_levels(book_outputpath, FITS_PATH)


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


def prep_page(book_name, collection_outputpath):
    book_outputpath = os.path.join(collection_outputpath, book_name)
    page_folders = [os.path.join(book_outputpath, i)
                    for i in os.listdir(book_outputpath)
                    if os.path.isdir(os.path.join(book_outputpath, i))
                    ]
    cpus = multiprocessing.cpu_count()
    with multiprocessing.Pool(cpus) as pool:
        pool.map(convert_page_pdf_to_tif, page_folders)
    copy_page_mods(book_name, collection_sourcepath, collection_outputpath)


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
    all_page_files = []
    for book_folder in os.listdir(collection_outputpath):
        book_path = os.path.join(collection_outputpath, book_folder)
        if not os.path.isdir(book_path):
            continue
        for file in os.listdir(book_path):
            page_filepath = os.path.join(book_path, file)
            if not os.path.isfile(page_filepath):
                continue
            if file == 'PDF.pdf':
                continue
            if os.path.splitext(page_filepath)[1].replace('.', '') == filetype:
                all_page_files.append(page_filepath)
    return all_page_files


def move_pages_to_subfolders(all_page_pdfs, filetype):
    for source_path in all_page_pdfs:
        root, filename = os.path.split(source_path)
        page_num, extension = os.path.splitext(filename)
        dest_path = os.path.join(root, page_num)
        os.makedirs(dest_path, exist_ok=True)
        shutil.move(source_path, os.path.join(dest_path, 'PDF.pdf'))


def copy_page_mods(book_name, collection_sourcepath, collection_outputpath):
    source_filepath = os.path.join(collection_sourcepath, '{}.xml'.format(book_name))
    dest_filepath = os.path.join(collection_outputpath, book_name, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)


def move_book_pdfs_to_subfolders(book_name, collection_sourcepath, collection_outputpath):
    source_filepath = os.path.join(collection_sourcepath, '{}.pdf'.format(book_name))
    book_outputpath = os.path.join(collection_outputpath, book_name)
    dest_filepath = os.path.join(book_outputpath, 'PDF.pdf')
    shutil.copy2(source_filepath, dest_filepath)


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
