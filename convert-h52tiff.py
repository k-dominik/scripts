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


def convert_single_file(
        in_file_name,
        out_path,
        format_string,
        dataset_key='exported_data',
        **kwargs):

    is_bigtiff = kwargs.get('is_bigtiff', True)
    try:
        current_file = h5py.File(in_file_name, 'r')
        dataset = current_file[dataset_key]

        if len(dataset.shape) != 3:
            raise ValueError("Data needs to have 3 dimensions: cyx!")

        if dataset.shape[0] > 20:
            raise ValueError("Will not convert data with more than 20 channels")

        logger.debug(f"{in_file_name} to {out_path}")
        file_only = os.path.split(in_file_name)[1]
        for slice_index, c_slice in enumerate(dataset):
            new_file_name = format_string.format(
                original_filename=file_only,
                exported_channel=slice_index
            )
            new_file_name = f"{new_file_name}.tiff"
            new_file_name = os.path.join(out_path, new_file_name)
            tiff = pytiff.Tiff(new_file_name, file_mode='w', bigtiff=is_bigtiff)
            tiff.write(c_slice)
            tiff.close()
    except (KeyError, ValueError) as e:
        logger.warning(f'encountered the following error in {in_file_name}', e)
    finally:
        current_file.close()


def main():
    options = parse_args()
    errors = []
    if not os.path.exists(options.in_file):
        errors.append(f'in-file {options.in_file} does not exist.')
    og_in = '{original_filename}' in options.naming_pattern
    if not og_in:
        errors.append(
            'Supplied pattern is invalid: {original_filename} not found')
    ec_in = '{exported_channel}' in options.naming_pattern
    if not ec_in:
        errors.append(
            'Supplied pattern is invalid: {exported_channel} not found')

    if errors:
        logger.warning("Exiting due to following erros:")
        logger.error("\n".join(f"\t{e}" for e in errors))
        sys.exit(1)

    output_folder = os.path.abspath(options.output_folder)

    if not os.path.exists(output_folder):
        logger.info(f"Creating output-folder at {output_folder}")
        os.makedirs(output_folder)

    file_list = []
    is_file = os.path.isfile(options.in_file)
    if is_file:
        file_list.append(os.path.abspath(options.in_file))
    else:
        file_list.extend(
            glob.glob(f'{options.in_file}/*.h5')
        )

    logger.info(f"About to convert {len(file_list)} files.")
    logger.debug("\n".join(f'\t{file}' for file in file_list))

    for file in file_list:
        convert_single_file(file, output_folder, options.naming_pattern)


if __name__ == '__main__':
    main()
