#! /usr/bin/env python3

import os
import subprocess
import shutil


def split_pdf_to_tiff(pdf_file):
    root, filename = os.path.split(pdf_file)
    dest_root = os.path.join(root, 'sugarTestJp2Converted', os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    subprocess.call(['convert',
                     '-density',
                     '300',
                     os.path.join(root, filename),
                     '-depth',
                     '8',
                     '-compress',
                     'jpeg',
                     os.path.join(dest_root, '%03d.tif')
                     ])


def move_tifs_to_subfolders(filepath):
    root, filename = os.path.split(filepath)
    prefix, extension = os.path.splitext(filename)
    prefix_plus_one = str(int(prefix) + 1)
    dest_filepath = os.path.join(root, prefix_plus_one)
    os.makedirs(dest_filepath)
    shutil.move(filepath, dest_filepath)
    shutil.move(os.path.join(dest_filepath, filename), os.path.join(dest_filepath, 'OBJ.tif'))


def move_mods_files(mods_file):
    root, filename = os.path.split(mods_file)
    dest_root = os.path.join(root, 'sugarTestJp2Converted', os.path.splitext(filename)[0])
    os.makedirs(dest_root, exist_ok=True)
    shutil.copy2(mods_file, os.path.join(dest_root, 'MODS.xml'))


def find_all_filetype(directory, filetype):
    all_pdfs = [os.path.join(root, file)
                for root, dirs, files in os.walk(directory)
                for file in files
                if os.path.splitext(file)[1] == filetype]
    return all_pdfs


all_pdf_files = find_all_filetype('/home/docker/share/sugarbulletin_sample_pdf/', '.pdf')
all_mods_files = find_all_filetype('/home/docker/share/sugarbulletin_sample_pdf/', '.xml')


for filepath in all_pdf_files:
    split_pdf_to_tiff(filepath)


for filepath in all_mods_files:
    move_mods_files(filepath)


all_tiff_files = find_all_filetype('/home/docker/share/sugarbulletin_sample_pdf/', '.tif')


for filepath in all_tiff_files:
    move_tifs_to_subfolders(filepath)
