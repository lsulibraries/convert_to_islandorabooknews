#! /usr/bin/env python3.6

import os
import sys
import shutil
import subprocess
import multiprocessing

from lxml import etree as ET

import make_book_derivs


FITS_PATH = make_book_derivs.find_fits_package()


def main(collection_sourcepath):
    collection_sourcepath = os.path.realpath(collection_sourcepath)
    collection_root, collection_name = os.path.split(collection_sourcepath)
    collection_outputpath = os.path.join(collection_root, '{}-to-book'.format(collection_name))
    os.makedirs(collection_outputpath, exist_ok=True)
    update_structure_files(collection_sourcepath)
    process_collection(collection_sourcepath, collection_outputpath)
    subprocess.call(['chmod', '-R', 'u+rwX,go+rX,go-w', collection_outputpath])


def update_structure_files(collection_sourcepath):
    for root, dirs, files in os.walk(collection_sourcepath):
        if 'structure.cpd' in files:
            parent = os.path.split(root)[-1]
            new_etree = ET.Element("islandora_compound_object", title=parent)
            old_etree = ET.parse("{}/structure.cpd".format(root))
            for i in old_etree.findall('.//pageptr'):
                new_etree.append(ET.Element('child', content='{}/{}'.format(parent, i.text)))
            with open('{}/structure.xml'.format(root), 'wb') as f:
                f.write(ET.tostring(new_etree, encoding="utf-8", xml_declaration=True, pretty_print=True))


def process_collection(collection_sourcepath, collection_outputpath):
    book_orderedpages_dict = parse_all_structure_files(collection_sourcepath)
    book_names = {os.path.splitext(i)[0] for i in os.listdir(collection_sourcepath)}
    already_converted_books = {os.path.splitext(i)[0] for i in os.listdir(collection_outputpath)}
    books_needing_converting = book_names - already_converted_books
    print("collection total: {}\nto do: {},\ndone: {}\n".format(
        len(book_names), len(books_needing_converting), len(already_converted_books))
    )
    loop_through_books(
        book_orderedpages_dict,
        collection_sourcepath,
        collection_outputpath,
        books_needing_converting
    )


def parse_all_structure_files(collection_sourcepath):
    book_orderedpages_dict = dict()
    for root, dirs, files in os.walk(collection_sourcepath):
        for file in files:
            if file == 'structure.xml':
                structure_filepath = os.path.join(root, file)
                book, ordered_pages = parse_structure_file(structure_filepath)
                book_orderedpages_dict[book] = ordered_pages
    return book_orderedpages_dict


def parse_structure_file(parent_structure_file):
    ordered_pointers = []
    structure_etree = ET.parse(parent_structure_file).getroot()
    parent = structure_etree.get('title')
    for i in structure_etree.iterchildren():
        try:
            repeated_parent, child = i.get('content').split('/')
        except ValueError:
            print('probably oldstyle structure file: {}'.format(parent_structure_file))
            break
        if repeated_parent != parent:
            print('unexpected multiple parents in one structure file')
            quit()
        ordered_pointers.append(child)
    return parent, ordered_pointers


def loop_through_books(book_orderedpages_dict, collection_sourcepath, collection_outputpath, books_needing_converting):
    for book_name, ordered_pages_pointers in sorted(book_orderedpages_dict.items()):
        if book_name not in books_needing_converting:
            continue
        convert_a_book(
            book_name,
            ordered_pages_pointers,
            collection_sourcepath,
            collection_outputpath
        )


def convert_a_book(book_name, ordered_pages_pointers, collection_sourcepath, collection_outputpath):
    copy_book_mods(collection_sourcepath, collection_outputpath, book_name)
    original_book_dir = os.path.join(collection_sourcepath, book_name)
    book_folder = os.path.join(collection_outputpath, book_name)
    loop_through_pages(ordered_pages_pointers, original_book_dir, book_folder)
    make_book_derivs.do_page_levels(book_folder)


def copy_book_mods(collection_sourcepath, collection_outputpath, book_name):
    original_book_modspath = os.path.join(collection_sourcepath, book_name, 'MODS.xml')
    book_folder = os.path.join(collection_outputpath, book_name)
    book_modspath = os.path.join(book_folder, 'MODS.xml')
    os.makedirs(book_folder, exist_ok=True)
    shutil.copy2(original_book_modspath, book_modspath)


def loop_through_pages(ordered_pages_pointers, original_book_dir, book_folder):
    cpus = multiprocessing.cpu_count()
    args = [
        (original_book_dir, page_pointer, book_folder, num)
        for num, page_pointer in enumerate(ordered_pages_pointers)
    ]
    with multiprocessing.Pool(cpus) as pool:
        pool.map(prep_page, args)


def prep_page(args):
    original_book_dir, page_pointer, book_folder, num = args
    original_page_dir = os.path.join(original_book_dir, page_pointer)
    page_outputpath = os.path.join(book_folder, "{0:0=4d}".format(num + 1))
    os.makedirs(page_outputpath, exist_ok=True)
    decompress_page_objs(original_page_dir, page_outputpath)
    copy_page_mods(original_page_dir, page_outputpath)


def decompress_page_objs(original_page_dir, page_outputpath):
    original_obj_path = os.path.join(original_page_dir, 'OBJ.jp2')
    page_objpath = os.path.join(page_outputpath, 'OBJ.tif')
    if not os.path.isfile(original_obj_path):
        print('no OBJ.jp2 file at {}'.format(original_obj_path))
    arguments = ['convert',
                 original_obj_path,
                 'TIFF64:/{}'.format(page_objpath),
                 ]
    subprocess.call(arguments)


def copy_page_mods(original_page_dir, page_outputpath):
    source_filepath = os.path.join(original_page_dir, 'MODS.xml')
    dest_filepath = os.path.join(page_outputpath, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)



if __name__ == '__main__':
    try:
        collection = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python convertJp2CpdToBook.py {{filename or foldername in "./source_data"}}"')
        print('')
        exit()
    if collection[-4:] in ('-cpd' or 'cpd/'):
        collection_sourcepath = os.path.join('/code/source_data', collection)
        main(collection_sourcepath)
    else:
        print(os.getcwd())
        print(f"looked for convert_to_islandorabooknews/source_data/{collection}")
        print('couldnt find the source data.  doublecheck the path')
        print('No files processed')
        exit()
