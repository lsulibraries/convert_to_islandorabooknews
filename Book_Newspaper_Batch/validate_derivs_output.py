#!/usr/bin/env python3

# Counts Page level files (should be 9)

import os
import sys


def sort_child_folders_by_contents(children_folders):
    this_dict = dict()
    for child_folder in children_folders:
        sorted_files = tuple(sorted(os.listdir(child_folder)))
        if this_dict.get(sorted_files):
            this_dict[sorted_files].append(child_folder)
        else:
            this_dict[sorted_files] = [child_folder, ]
    return this_dict


def read_folders_and_sort(collection_path):
    children_folders = [root for root, dirs, files in os.walk(collection_path)
                        if os.path.split(os.path.split(root)[0])[1].split('_')[0] == 'lsuhsc-lsubk01']
    derivs_dict = sort_child_folders_by_contents(children_folders)
    return derivs_dict


if __name__ == '__main__':
    try:
        collection_path = sys.argv[1]
    except IndexError:
        print('')
        print('Change to: "python validate_derivs_output.py {{path_to_folder}}"')
        print('')
        exit()

    derivs_dict = read_folders_and_sort(collection_path)
    for k, v in derivs_dict.items():
        print(k, len(v))
