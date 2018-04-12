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
                     300,
                     os.path.join(root, filename),
                     '-quality',
                     75,
                     '-colorspace',
                     'RGB',
                     "-define numrlvls=7",
                     "-define jp2:tilewidth=1024",
                     "-define jp2:tileheight=1024",
                     "-define jp2:rate=0.02348",
                     "-define jp2:prg=rpcl",
                     "-define jp2:mode=int",
                     "-define jp2:prcwidth=16383",
                     "-define jp2:prcheight=16383",
                     "-define jp2:cblkwidth=64",
                     "-define jp2:cblkheight=64",
                     "-define jp2:sop",
                     os.path.join(dest_root, '%03d.jp2'),
                     ])


def split_pdf_to_tiff(pdf_file, output_root,):
    root, filename = os.path.split(pdf_file)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    arguments = ['convert',
                 # '-size',
                 # '563x779',
                 '-density',
                 '300',
                 os.path.join(root, filename),
                 '-depth',
                 '8',
                 # '-resize',
                 # '24%',
                 # '-compress',
                 # 'jpeg',
                 os.path.join(dest_root, '%04d.tif')
                 ]
    subprocess.call(arguments)


def move_images_to_subfolders(filepath, output_filetype):
    root, filename = os.path.split(filepath)
    prefix, extension = os.path.splitext(filename)
    prefix_plus_one = str(int(prefix) + 1)
    dest_filepath = os.path.join(root, prefix_plus_one)
    print(filepath, dest_filepath)
    os.makedirs(dest_filepath, exist_ok=True)
    shutil.move(filepath, os.path.join(dest_filepath, 'OBJ.{}'.format(output_filetype)))


def move_mods_files(source_filepath, output_root):
    root, filename = os.path.split(source_filepath)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'MODS.xml')
    shutil.copy2(source_filepath, dest_filepath)


def find_all_images(output_root, output_filetype):
    all_output_images = []
    for parent_folder in os.listdir(output_root):
        parent_path = os.path.join(output_root, parent_folder)
        if not os.path.isdir(parent_path):
            continue
        for file in os.listdir(parent_path):
            child_filepath = os.path.join(parent_path, file)
            if not os.path.isfile(child_filepath):
                continue
            if os.path.splitext(child_filepath)[1] == '.{}'.format(output_filetype):
                all_output_images.append(child_filepath)
    return all_output_images


def move_pdfs_to_subfolders(source_filepath, output_root):
    root, filename = os.path.split(source_filepath)
    dest_root = os.path.join(output_root, os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    dest_filepath = os.path.join(dest_root, 'PDF.pdf')
    print(source_filepath, dest_filepath)
    shutil.copy2(source_filepath, dest_filepath)


if __name__ == '__main__':

    try:
        source_root, output_filetype = sys.argv[1], sys.argv[2]
    except IndexError:
        print('\nChange to: "python3 splitting_newspaper_pdf_into_images.py $path/to/source_pdf_folder {{tif or jp2}}"\n')
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
        if output_filetype == 'jp2':
            split_pdf_to_jp2s(filepath, output_root)
        elif output_filetype == 'tif':
            split_pdf_to_tiff(filepath, output_root)

    all_source_mods = [os.path.join(source_root, i)
                       for i in os.listdir(source_root)
                       if os.path.splitext(i)[1] == '.xml']
    for filepath in sorted(all_source_mods):
        move_mods_files(filepath, output_root)

    all_output_images = find_all_images(output_root, output_filetype)
    for filepath in sorted(all_output_images):
        move_images_to_subfolders(filepath, output_filetype)

    for filepath in sorted(all_source_pdfs):
        print(filepath)
        move_pdfs_to_subfolders(filepath, output_root)
