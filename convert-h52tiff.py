#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Small script to convert multi-channel .h5 files to multiple .tiff files

Axisorder is assumed to be `cyx`. The script will output one .tiff file per channel.
"""
import logging
import argparse
import os
import sys
import glob

import h5py
import pytiff

logger = logging.getLogger(f"{__file__}")
logging.basicConfig(
    filename=f'log_{__file__}.txt',
    level=logging.DEBUG,
    filemode='w')
logger.addHandler(logging.StreamHandler())


def parse_args():
    p = argparse.ArgumentParser(
        description=(
            'Small script to convert multi-channel .h5 files to multiple .tiff '
            'files\nNote that it is assumed that the axisorder is "cyx" and '
            'that the dataset-name of the multi-channel image is '
            '"exported_data" (ilastik default).'),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        'in_file',
        metavar='in-file',
        help=(
            'Single .h5 file or folder. In case a folder is given, all .h5 files '
            'inside this folder will be converted to .tiff stacks'
        )
    )
    p.add_argument(
        'output_folder',
        metavar='output-folder',
        help=('Output folder for generated .tiff files'),
    )
    p.add_argument(
        '-p', '--naming-pattern',
        help=(
            'Naming pattern for generated .tiff files. Must include '
            '{original_filename} and {exported_channel}. The .tiff file '
            'extension is added automatically.'
        ),
        default='{original_filename}_{exported_channel}'
    )
    p.add_argument(
        '--no-big-tiff',
        help=(
            'Per default it is attempted to write bigtiff files. '
            'Use this command line flag to write regular tiff files.'
        ),
        action='store_true'
    )

    args = p.parse_args()
    return args


def main():
    options = parse_args()



if __name__ == '__main__':
    main()
