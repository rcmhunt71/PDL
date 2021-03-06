"""
    PURPOSE: Utility to combine multiple JSON files into a single JSON file (DL'd images only)
    ===========================================================================================
        * Find all <data>.json files
        * Read all records with dl_status == DOWNLOADED into a single dictionary
        * Write dictionary to file in JSON format
        * Verify data integrity
        * Delete <data>.json files
        * Verify all <data>.json files were deleted.
"""

import argparse
import configparser
import json
import os
import pprint
from typing import Dict, List

from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys)
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus
from PDL.engine.inventory.json.inventory import JsonInventory
from PDL.logger.logger import Logger
import PDL.logger.utils as utils


PURPOSE_CLI = "Consolidate JSON files into single file."
BASE_FILE_NAME = "CONSOLIDATED_"
EXTENSION = "json"

LOG = Logger()


def parse_cli() -> argparse.Namespace:
    """
    Define basic CLI arguments

    :return: Arguments parsed from CLI

    """
    parser = argparse.ArgumentParser(PURPOSE_CLI)
    parser.add_argument('cfg', help="PDL App config file to use")
    return parser.parse_args()


def build_json_log_location(cfg: configparser.ConfigParser) -> str:
    """
    Build the location of the JSON files from the configuration file.

    :param cfg: Instantiated ConfigParser (containing specified CFG file)

    :return: (str) Location of <data>.json files

    """
    # ======================
    # JSON LOGFILE LOCATION
    # ======================
    json_log_location = cfg.get(AppCfgFileSections.LOGGING,
                                AppCfgFileSectionKeys.JSON_FILE_DIR)
    json_drive = cfg.get(AppCfgFileSections.LOGGING,
                         AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
    if json_drive is not None:
        json_log_location = f"{json_drive.strip(':')}:{json_log_location}"

    # Verify directory exists
    LOG.info(f"Checking directory: {json_log_location}")
    if not utils.check_if_location_exists(location=json_log_location, create_dir=False):
        LOG.error(f"Unable to find source directory: {json_log_location}")
        exit()

    return json_log_location


def read_files(files: List[str]) -> Dict[str, ImageData]:
    """
    Read list of <data>.json files into a common dictionary. All keeps stats about
    how many records were found, and how many were dl_status == DOWNLOAD.

    :param files: list of absolute_path <data>.json files

    :return: dictionary of all json records for status==DOWNLOAD from all data files

    """
    data = dict()
    num_raw_recs = 0
    num_dl_recs = 0

    # Iterate through the files
    for json_file in files:

        # Read JSON contents and convert into python structure
        with open(json_file, "r") as source_json_file:
            lines = "\n".join(source_json_file.readlines())
        raw_data = json.loads(lines)
        num_raw_recs += len(raw_data.keys())

        LOG.info(f"Reading JSON File: {json_file}")

        # Filter out non-DOWNLOAD'ed records
        dl_images = get_downloads_only(raw_data)
        num_dl_recs += len(dl_images.keys())

        # Add entries to dictionary
        data.update(dl_images)

    LOG.info(f"RAW RECORDS: {num_raw_recs}  DOWNLOADED: {num_dl_recs}")
    LOG.debug(pprint.pformat(data))
    return data


def get_downloads_only(json_dict: Dict[str, ImageData]) -> Dict[str, ImageData]:
    """
    Filter out records from dictionary, where the record does not have dl_status == DOWNLOAD.

    :param json_dict: dictionary of JSON records

    :return: dictionary of JSON records where dl_status == DOWNLOAD

    """
    return {image: data for image, data in json_dict.items() if
            getattr(data, ImageData.DL_STATUS) == DownloadStatus.DOWNLOADED}


def determine_consolidate_file_name(files: List[str], target_dir: str) -> str:
    """
    Determine what that last index of the CONSOLIDATED json files are, and increment by 1.

    :param files: List of CONSOLIDATED_x.json files

    :param target_dir: Location to write next CONSOLIDATED_x+1.json

    :return: Absolute path/filename of next CONSOLIDATED_x.json file.

    """
    last_index = 0

    # Get all file names from list of files provided
    file_names = [x.split(os.path.sep)[-1] for x in files]

    # Keep only the consolidated files (starts with BASE_FILE_NAME)
    file_names = [x for x in file_names if x.startswith(BASE_FILE_NAME)]

    # If there are CONSOLIDATED_x.json files, get the index of the last file (CONSOLIDATE_X.json)
    if file_names:
        file_names = [x.split('.')[0] for x in file_names]
        last_index = sorted([int(x.split('_')[-1]) for x in file_names])[-1]
        LOG.info(f"Last Index Found: {last_index}")
    else:
        LOG.warn("CONSOLIDATED FILE NOT FOUND.")

    filename = f'{BASE_FILE_NAME}{last_index + 1}.{EXTENSION}'
    return os.path.abspath(os.path.sep.join([target_dir, filename]))


def write_json_file(filename: str, data: dict) -> None:
    """
    Write data to filename (in json format)

    :param filename: Absolute path/filename of JSON file to create.
    :param data: Data (dictionary) to write to file.

    :return: None
    """
    with open(filename, "w") as json_output_file:
        json_output_file.write(json.dumps(data))
    LOG.info(f"Wrote data to: {filename}")


def read_json_file(filename: str) -> dict:
    """
    Read data from filename (in json format)

    :param filename: Absolute path/filename of JSON file to read.

    :return: python data structure from JSON.loads()

    """
    data = dict()
    with open(filename, "r") as json_file:
        data.update(json.loads('\n'.join(json_file.readlines())))
    LOG.info(f"Read data from: {filename}")
    return data


def verify_records_match(original: dict, consolidated: dict) -> bool:
    """
    Verify dictionaries are identical (in key names only)

    :param original: Original/Master dictionary
    :param consolidated: New/Consolidated dictionary

    :return: (bool) Success = True, Errors = False

    """
    errors = False

    # Convert to sets to do easy comparison of keys
    orig = set(original.keys())
    consolid = set(consolidated.keys())

    # If the sets are not equal... something did not copy correctly.
    if orig != consolid:
        errors = True
        diff = orig - consolid

        LOG.error("*** Missing records!!!")
        for rec in diff:
            LOG.error(f"+ Did not find: {rec}")

    # Dictionaries match!
    else:
        LOG.info("VALIDATED: All records accounted for.")

    return not errors


def main_routine():
    """
    Primary routine:
       * Get list of non-consolidated JSON files based on info from config file
       * Read all JSON files into a common structure, and combine any identical items
       * Write data to file.
       * Verify all data in consolidated file matches the source files.
       * Delete source JSON files that were consolidated (and verify all files were deleted)

    :return: None

    """
    length = 80
    border = "=" * length

    # Parse CLI for specified config file
    cfg_name = parse_cli().cfg
    LOG.info(border)
    LOG.info(f"     USING CFG: {cfg_name}")
    LOG.info(border)

    # Determine the JSON log directory from the config file
    log_location = build_json_log_location(cfg=AppConfig(cfg_file=cfg_name))

    # Get a list of the JSON files in the 'log_location' directory
    LOG.info(border)
    LOG.info("    GET LISTING OF JSON FILES TO CONSOLIDATE.")
    LOG.info(border)
    inv = JsonInventory(dir_location=log_location)
    json_files = inv.get_json_files()

    # Find all files that DO NOT HAVE the consolidated base filename.
    # Put data from all matching files into a single dictionary.
    data_files = [x for x in json_files if not x.split(os.path.sep)[-1].startswith(BASE_FILE_NAME)]
    records = read_files(files=data_files)

    # Determine name and location of where CONSOLIDATED JSON file
    consolidated_log = determine_consolidate_file_name(files=json_files, target_dir=log_location)
    LOG.info(f"Consolidating to: {consolidated_log}")

    # Create the CONSOLIDATED JSON file
    write_json_file(data=records, filename=consolidated_log)

    # Verify CONSOLIDATED JSON file matches the original data
    LOG.info(border)
    LOG.info("    VERIFY CONTENTS MATCH ORIGINAL FILES")
    LOG.info(border)
    success = verify_records_match(
        original=read_files(files=data_files),
        consolidated=read_json_file(consolidated_log))

    # Verify all <data>.json files have been deleted
    if success:

        # Delete files
        LOG.info(border)
        LOG.info("    DELETING NON-CONSOLIDATED JSON FILES")
        LOG.info(border)
        for data_file in data_files:
            os.remove(data_file)
            LOG.info(f"Deleted {data_file}")

        # Get updated list of JSON files in the directory
        json_files = inv.get_json_files()
        data_files = [x for x in json_files if BASE_FILE_NAME not in x]

        # data_files should be empty (no <data>.JSON files)
        if data_files:
            LOG.error("JSON data files NOT deleted:")
            for data_file in data_files:
                LOG.error(f"+ {data_file}")
        else:
            LOG.info(border)
            LOG.info(f"    CONSOLIDATION SUCCESSFUL. {consolidated_log}")
            LOG.info(border)


if __name__ == '__main__':
    main_routine()
