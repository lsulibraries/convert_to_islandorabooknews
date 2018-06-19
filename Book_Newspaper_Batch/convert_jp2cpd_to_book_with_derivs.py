#! /usr/bin/env python3.6

import os
import sys
import shutil
import subprocess

from lxml import etree as ET

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
    update_structure_files(collection_sourcepath)
    rename_folders_move_files(collection_sourcepath, collection_outputpath)
    for book_name in sorted(books_needing_converting):
        book_outputpath = os.path.join(collection_outputpath, book_name)
        make_book_derivs.do_child_level(book_outputpath, fits_path)
        make_parent_tn(book_outputpath)
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


def rename_folders_move_files(collection_sourcepath, collection_outputpath):
    parent_orderedchildren_dict = parse_all_structure_files(collection_sourcepath)
    loop_through_parents(parent_orderedchildren_dict, collection_sourcepath, collection_outputpath)


def parse_all_structure_files(collection_sourcepath):
    parent_orderedchildren_dict = dict()
    for root, dirs, files in os.walk(collection_sourcepath):
        for file in files:
            if file == 'structure.xml':
                structure_filepath = os.path.join(root, file)
                parent, ordered_children = parse_structure_file(structure_filepath)
                parent_orderedchildren_dict[parent] = ordered_children
    return parent_orderedchildren_dict


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


def loop_through_parents(parent_orderedchildren_dict, collection_sourcepath, collection_outputpath):
    for parent_pointer, ordered_children_pointers in parent_orderedchildren_dict.items():
        copy_parent_mods(collection_sourcepath, collection_outputpath, parent_pointer)
        book_outputpath = os.path.join(collection_outputpath, parent_pointer)
        original_parent_dir = os.path.join(collection_sourcepath, parent_pointer)
        loop_through_children(ordered_children_pointers, original_parent_dir, book_outputpath)


def copy_parent_mods(collection_sourcepath, collection_outputpath, parent_pointer):
    original_parent_modspath = os.path.join(collection_sourcepath, parent_pointer, 'MODS.xml')
    book_outputpath = os.path.join(collection_outputpath, parent_pointer)
    book_modspath = os.path.join(book_outputpath, 'MODS.xml')
    os.makedirs(book_outputpath, exist_ok=True)
    shutil.copy2(original_parent_modspath, book_modspath)


def loop_through_children(ordered_children_pointers, original_parent_dir, book_outputpath):
    for num, child_pointer in enumerate(ordered_children_pointers):
        original_child_dir = os.path.join(original_parent_dir, child_pointer)
        page_outputpath = os.path.join(book_outputpath, "{0:0=4d}".format(num + 1))
        os.makedirs(page_outputpath, exist_ok=True)
        copy_child_mods(original_child_dir, page_outputpath)
        decompress_child_objs(original_child_dir, page_outputpath)


def copy_child_mods(original_child_dir, page_outputpath):
    original_mods_path = os.path.join(original_child_dir, 'MODS.xml')
    page_modspath = os.path.join(page_outputpath, 'MODS.xml')
    shutil.copy2(original_mods_path, page_modspath)


def decompress_child_objs(original_child_dir, page_outputpath):
    original_obj_path = os.path.join(original_child_dir, 'OBJ.jp2')
    page_objpath = os.path.join(page_outputpath, 'OBJ.tif')
    if not os.path.isfile(original_obj_path):
        print('no OBJ.jp2 file at {}'.format(original_obj_path))
    arguments = ['convert',
                 original_obj_path,
                 'TIFF64:/{}'.format(page_objpath),
                 ]
    subprocess.call(arguments)


def make_parent_tn(collection_outputpath):
    first_page_tn = os.path.join(collection_outputpath, '0001', 'TN.jpg')
    parent_tn = os.path.join(collection_outputpath, 'TN.jpg')
    shutil.copy2(first_page_tn, parent_tn)


if __name__ == '__main__':
    try:
        collection_sourcepath = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python convertJp2CpdToBook.py {{path_to_folder}}"')
        print('')
        exit()
    if '-cpd' in collection_sourcepath:
        main(collection_sourcepath)
    else:
        print('Expected "institution-namespace-cpd" folder name')
        print('No files processed')
        exit()
