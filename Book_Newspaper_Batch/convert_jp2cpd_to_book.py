#! /usr/bin/env python3.6

# Only works if imagemagick + jp2 delegates are active on the linux machine

import os
import sys
import shutil

from lxml import etree as ET

import make_book_derivs


def update_structure_files(collection_folder):
    for root, dirs, files in os.walk(collection_folder):
        if 'structure.cpd' in files:
            parent = os.path.split(root)[-1]
            new_etree = ET.Element("islandora_compound_object", title=parent)
            old_etree = ET.parse("{}/structure.cpd".format(root))
            for i in old_etree.findall('.//pageptr'):
                new_etree.append(ET.Element('child', content='{}/{}'.format(parent, i.text)))
            with open('{}/structure.xml'.format(root), 'wb') as f:
                f.write(ET.tostring(new_etree, encoding="utf-8", xml_declaration=True, pretty_print=True))


def parse_structure_files(parent_structure_file):
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


def parse_all_structure_files(directory):
    parent_orderedchildren_dict = dict()
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'structure.xml':
                parent, ordered_children = parse_structure_files(os.path.join(root, file))
                parent_orderedchildren_dict[parent] = ordered_children
    return parent_orderedchildren_dict


def doublecheck_1obj_and_1mods(child_dir):
    for root, dirs, files in os.walk(child_dir):
        if files and len(files) != 2:
            print('expected 2 files in dir {}'.format(root))
            break
    else:
        return True


def move_parent_mods(source_dir, output_dir, parent_pointer):
    output_parent_dir = os.path.join(output_dir, parent_pointer)
    output_parent_modspath = os.path.join(output_parent_dir, 'MODS.xml')
    original_parent_modspath = os.path.join(source_dir, parent_pointer, 'MODS.xml')
    os.makedirs(output_parent_dir, exist_ok=True)
    shutil.copy2(original_parent_modspath, output_parent_modspath)


def move_child_mods(original_child_dir, converted_child_dir):
    original_mods_path = os.path.join(original_child_dir, 'MODS.xml')
    converted_mods_path = os.path.join(converted_child_dir, 'MODS.xml')
    shutil.copy2(original_mods_path, converted_mods_path)


def move_child_objs(original_child_dir, converted_child_dir):
    for file in os.listdir(original_child_dir):
        if 'OBJ' not in file:
            continue
        original_obj_path = os.path.join(original_child_dir, file)
        converted_obj_path = os.path.join(converted_child_dir, file)
        if not os.path.isfile(original_obj_path):
            print('not obj file at {}'.format(original_obj_path))
        shutil.copy2(original_obj_path, converted_obj_path)


def loop_through_children(ordered_children_pointers, original_parent_dir, converted_parent_dir):
    for num, child_pointer in enumerate(ordered_children_pointers):
        original_child_dir = os.path.join(original_parent_dir, child_pointer)
        converted_child_dir = os.path.join(converted_parent_dir, str(num + 1))
        os.makedirs(converted_child_dir, exist_ok=True)
        move_child_mods(original_child_dir, converted_child_dir)
        move_child_objs(original_child_dir, converted_child_dir)
        doublecheck_1obj_and_1mods(converted_child_dir)


def loop_through_parents(parent_orderedchildren_dict, source_dir, output_dir):
    for parent_pointer, ordered_children_pointers in parent_orderedchildren_dict.items():
        move_parent_mods(source_dir, output_dir, parent_pointer)
        converted_parent_dir = os.path.join(output_dir, parent_pointer)
        original_parent_dir = os.path.join(source_dir, parent_pointer)
        loop_through_children(ordered_children_pointers, original_parent_dir, converted_parent_dir)


def rename_folders_move_files(source_dir, output_dir):
    parent_orderedchildren_dict = parse_all_structure_files(source_dir)
    loop_through_parents(parent_orderedchildren_dict, source_dir, output_dir)


def find_all_jp2s(output_root):
    all_output_images = []
    for parent_folder in os.listdir(output_root):
        parent_path = os.path.join(output_root, parent_folder)
        if not os.path.isdir(parent_path):
            continue
        for file in os.listdir(parent_path):
            child_filepath = os.path.join(parent_path, file)
            if not os.path.isfile(child_filepath):
                continue
            if os.path.splitext(child_filepath)[1] == '.jp2':
                all_output_images.append(child_filepath)
    return all_output_images


def make_derivatives(source_root, output_root):
    pointers = {os.path.splitext(i)[0] for i in os.listdir(source_root)}
    fits_path = make_book_derivs.find_fits_package()
    for pointer in pointers:
        parent_root = os.path.join(output_root, pointer)
        make_book_derivs.do_child_level(parent_root, fits_path)


def main(source_root):
    source_root = os.path.realpath(source_root)
    parent_root, source_folder = os.path.split(source_root)
    output_root = os.path.join(parent_root, '{}-to-book'.format(source_folder))
    update_structure_files(source_root)
    rename_folders_move_files(source_root, output_root)
    make_derivatives(source_root, output_root)


if __name__ == '__main__':
    try:
        source_root = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python convertJp2CpdToBook.py {{path_to_folder}}"')
        print('')
        exit()
    if '-cpd' in source_root:
        main(source_root)
    else:
        print('Expected "institution-namespace-cpd" folder name')
        print('No files processed')
        exit()
