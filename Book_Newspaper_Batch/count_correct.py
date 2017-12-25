#!/usr/bin/env python3

import os

cpd_folder = '/home/francis/Desktop/lsuhsc-lsubk01-cpd'
book_folder = '/home/francis/Desktop/lsuhsc-lsubk01-cpd-Book-with-derivatives'


def parse_source_folder(path):
    parent_dirs_child_counts = dict()
    for root, dirs, files in os.walk(path):
        if len(dirs) and os.path.split(root)[1].isnumeric():
            parent_dirs_child_counts[os.path.split(root)[1]] = len(dirs)
    return parent_dirs_child_counts


cpd_counts = parse_source_folder(cpd_folder)
book_counts = parse_source_folder(book_folder)


print((cpd_counts.keys() - book_counts.keys()) or (book_counts.keys() - cpd_counts.keys()))

for k, v in cpd_counts.items():
    if book_counts[k] != v:
        print('Key: {} Cpd child counts: {} doesnt match book counts {}'.format(k, v, book_counts[k]))

# only finds if same parents in two folders, not useful
