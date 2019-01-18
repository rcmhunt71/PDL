#!/usr/bin/env python

import argparse
import json
import os
import pprint
from random import choice, choices, randint

from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys)
from PDL.engine.images.image_info import ImageData, ModStatus
from PDL.engine.images.status import DownloadStatus
from PDL.logger.logger import Logger
import PDL.logger.utils as utils

PURPOSE_CLI = "Generate JSON data files for parsing and cataloging."


# Don't instantiate logger if it is using the code as the primary script.
# Logic to load logger is in __main__ portion of the script.
if __name__ != '__main__':
    log = Logger()


"""
Utility to generate test data for routines requiring JSON data or
ImageData objects.

Can be used as a module or as a stand-alone script.

"""


def parse_cli():
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
        '-d', '--debug', help="Enabled debug",  action='store_true')
    return parser.parse_args()


def build_json_log_location(cfg):
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
        json_log_location = '{0}:{1}'.format(
            json_drive.strip(':'), json_log_location)

    # Verify directory exists
    log.info("Checking directory: {0}".format(json_log_location))
    if not utils.check_if_location_exists(
            location=json_log_location, create_dir=True):
        log.error("Unable to find source directory: {0}".format(
            json_log_location))
        exit()

    return json_log_location


def build_data_element(index):
    """
    Builds artificial ImageData object based on index

    :param index: Value to identify the object in the data set

    :return: Instantiated ImageData Object

    """
    log.debug("Building dataset #:{index}".format(index=index))
    metadata = ["category_{0}".format(x) for x in range(1, 7)]

    return ImageData.build_obj({
        'image_name': "image_{0}".format(index),
        'description': "Mock Image Data - {0}".format(index),
        'page_url': 'http://foo.com/page/{0:<16}'.format(
            str(index) * 8).strip(),
        'image_url': 'http://foo.com/image/{0:<16}'.format(
            str(index) * 8).strip(),
        'author': "Picasso{0}".format(index),
        'filename': 'test_data_{0}.jpg'.format(index),
        'image_date': "01/{0:02d}/19".format(index % 31),
        'resolution': "1600x7{0:02d}".format(index),
        'downloaded_on': "08/{0:02d}/19".format(index % 30),
        'classification_metadata': sorted(list(set(choices(
            population=metadata, k=randint(0, len(metadata)))))),
        'download_duration': index,
        'locations': '/tmp/pdl/images',
        'dl_status': choice(DownloadStatus.get_statuses_()),
        'mod_status': ModStatus.NEW,
        'error_info': None,
    })


def generate_data(num_data_sets, max_num_recs_per_file):
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

    log.info("Generating {0} data sets.".format(num_data_sets))
    for number in range(num_data_sets):
        filename = filename_fmt.format(number + 1)
        data_sets[filename] = dict()

        num_records = randint(1, max_num_recs_per_file)
        log.info("Data set has {0} records.".format(num_records))

        for data_set in range(num_records):
            record = build_data_element(data_set)
            data_sets[filename][getattr(record, ImageData.FILENAME)] = record

    return data_sets


def execute(num_data_sets, max_records, cfg_file):
    """

    Given the parameters, generate the requested data files in the specified directory. The number of
    records per data set is a random value between [1, max_records]. The files will be generated in the log
    directory defined in the App cfg file provided.

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
    log.debug(pprint.pformat(data))

    # Determine the number of records generated
    actual_count = sum([len(x.keys()) for x in data.values()])
    max_count = int(num_data_sets) * int(max_records)
    log.info("Count: {0} (MAX: {1})".format(actual_count, max_count))

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
        with open(filepath, "w") as DATA_FILE:
            DATA_FILE.write(json.dumps(data))
        log.info("Wrote data to '{filespec}'.".format(filespec=filepath))

    log.info("Done")
    return gen_files


if __name__ == '__main__':
    args = parse_cli()

    # TODO: Figure out what is causing adding second logger (duplicate logs)
    log = Logger(set_root=True,
                 default_level=Logger.DEBUG if args.debug else Logger.INFO)
    log.debug("DEBUG enabled.")

    data_files = execute(
        num_data_sets=args.num_data_sets,
        max_records=args.max_records,
        cfg_file=args.cfg
    )
