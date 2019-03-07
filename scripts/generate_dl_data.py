#!/usr/bin/env python

"""
    Utility to generate test data for routines requiring JSON data or
    ImageData objects.

    Can be used as a module or as a stand-alone script.

"""

import argparse
import configparser
import json
import os
import pprint
from random import choice, choices, randint
from typing import Dict, List

from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys)
from PDL.engine.images.image_info import ImageData, ModStatus
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger
import PDL.logger.utils as utils

PURPOSE_CLI = ("Generate JSON data files for testing the parsing and "
               "cataloging routines.")

LOG = Logger()


def parse_cli() -> argparse.Namespace:
    """
    Define basic CLI arguments

    :return: Arguments parsed from CLI

    """
    parser = argparse.ArgumentParser(PURPOSE_CLI)
    parser.add_argument('cfg', help="PDL App config file to use.")
    parser.add_argument(
        'num_data_sets', help="Number of data sets to generate.")
    parser.add_argument(
        'max_records', help="Max number of records per data set.")
    parser.add_argument(
        '-d', '--debug', help="Enabled debug", action='store_true')
    return parser.parse_args()


def build_json_log_location(cfg: configparser.ConfigParser) -> str:
    """
    Build the location of the JSON files from the configuration file.

    :param cfg: Instantiated ConfigParser (containing specified CFG file)

    :return: (str) Location of <data>.json files

    """
    json_log_location = cfg.get(AppCfgFileSections.LOGGING,
                                AppCfgFileSectionKeys.JSON_FILE_DIR)
    json_drive = cfg.get(AppCfgFileSections.LOGGING,
                         AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
    if json_drive not in [None, '']:
        json_log_location = f"{json_drive.strip(':')}:{json_log_location}"

    # Verify directory exists
    LOG.info(f"Checking directory: {json_log_location}")
    if not utils.check_if_location_exists(
            location=json_log_location, create_dir=True):
        LOG.error(f"Unable to find source directory: {json_log_location}")
        exit()

    return json_log_location


def build_data_element(index: int) -> ImageData:
    """
    Builds artificial ImageData object based on index

    :param index: Value to identify the object in the data set

    :return: Instantiated ImageData Object

    """
    LOG.debug(f"Building dataset #:{index}")
    metadata = [f"category_{x}" for x in range(1, 7)]

    return ImageData.build_obj({
        'image_name': f"image_{index}",
        'description': f"Mock Image Data - {index}",
        'page_url': 'http://foo.com/page/{0:<16}'.format(
            str(index) * 8).strip(),
        'image_url': 'http://foo.com/image/{0:<16}'.format(
            str(index) * 8).strip(),
        'author': f"Picasso{index}",
        'filename': 'test_data_{0}.jpg'.format(index),
        'image_date': "01/{0:02d}/19".format(index % 31),
        'resolution': "1600x7{0:02d}".format(index),
        'downloaded_on': "08/{0:02d}/19".format(index % 30),
        'classification_metadata': sorted(list(set(choices(
            population=metadata, k=randint(0, len(metadata)))))),
        'download_duration': index,
        'locations': '/tmp/pdl/images',
        'dl_status': choice(DownloadStatus.get_statuses()),
        'mod_status': ModStatus.NEW,
        'error_info': None,
    })


def generate_data(num_data_sets: int, max_num_recs_per_file: int) -> \
        Dict[str, Dict[str, ImageData]]:
    """
    Builds dictionary of data_sets for each filename

    key: filename value: dict of data (key = image_name, value = ImageObj)

    :param num_data_sets: Number of data sets to define
    :param max_num_recs_per_file: Maximum number of data records to define
           per data set

    :return: Builds dictionary of data_sets for each filename, each with a
             random number of records from 1 to max_num_recs_per_file

    """
    filename_fmt = 'test_data_{0}.json'

    data_sets = dict()

    LOG.info(f"Generating {num_data_sets} data sets.")
    for number in range(num_data_sets):
        filename = filename_fmt.format(number + 1)
        data_sets[filename] = dict()

        num_records = randint(1, max_num_recs_per_file)
        LOG.info(f"Data set has {num_records} records.")

        for data_set in range(num_records):
            record = build_data_element(data_set)
            data_sets[filename][getattr(record, ImageData.FILENAME)] = record

    return data_sets


def execute(num_data_sets: int, max_records: int, cfg_file: str) -> List[str]:
    """

    Given the parameters, generate the requested data files in the specified directory.
    The number of records per data set is a random value between [1, max_records].
    The files will be generated in the log directory defined in the App cfg file provided.

    :param num_data_sets: Number of files to generate
    :param max_records: Max number of records per data set.
    :param cfg_file: PDL cfg file to use for generating data

    :return: List of files generated by routine.

    """
    # Get the JSON data/log directory
    config = AppConfig(cfg_file=cfg_file, test=False)
    json_dir = build_json_log_location(cfg=config)

    # Generate the data
    data = generate_data(
        num_data_sets=int(num_data_sets),
        max_num_recs_per_file=int(max_records))
    LOG.debug(pprint.pformat(data))

    # Determine the number of records generated
    actual_count = sum([len(x.keys()) for x in data.values()])
    max_count = int(num_data_sets) * int(max_records)
    LOG.info(f"Count: {actual_count} (MAX: {max_count})")

    # Write the dictionary to JSON files in the predetermined directory
    gen_files = []
    for filename, data in data.items():

        # Convert the ImageData objects to dictionaries (json-serializable)
        for data_id, data_obj in data.items():
            data[data_id] = data_obj.to_dict()

        # Build the full filespec for the current dataset
        filepath = os.path.sep.join([json_dir, filename])
        gen_files.append(filepath)

        # Write the data to file.
        with open(filepath, "w") as data_file:
            data_file.write(json.dumps(data))
        LOG.info(f"Wrote data to '{filepath}'.")

    LOG.info("Done")
    return gen_files


def main_test_routine():
    """
    Main test routine.
       * Get args from CLI
       * Setup Logging
       * Execute data generation

    :return:
    """
    args = parse_cli()

    log = Logger(set_root=True,
                 default_level=Logger.DEBUG if args.debug else Logger.INFO)

    log.debug("DEBUG enabled.")

    execute(num_data_sets=args.num_data_sets,
            max_records=args.max_records,
            cfg_file=args.cfg)


if __name__ == '__main__':
    main_test_routine()
