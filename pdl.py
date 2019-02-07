#!/usr/bin/env python

from collections import OrderedDict
import configparser
import os
import pprint
import time

import PDL.configuration.cli.args as args
import PDL.logger.json_log as json_logger
import PDL.logger.utils as utils
from PDL.configuration.cli.url_file import UrlFile
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys, ProjectCfgFileSectionKeys, ProjectCfgFileSections)
from PDL.engine.images.image_info import ImageData
from PDL.engine.images.status import DownloadStatus as Status
from PDL.engine.module_imports import import_module_class
from PDL.engine.inventory.inventory_composite import Inventory
from PDL.logger.logger import Logger as Logger
from PDL.logger.json_log import JsonLog
from PDL.reporting.summary import ReportingSummary

import prettytable
import pyperclip

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'
DEFAULT_APP_CONFIG = None
PICKLE_EXT = ".dat"

# TODO: Add docstrings and inline comments

LOCAL_STORAGE = ""


class NoURLsProvided(Exception):
    pass

# TODO: Move logic into separate file


class PdlConfig(object):
    def __init__(self) -> None:
        self.cli_args = args.CLIArgs().args
        self.app_cfg = AppConfig(self.cli_args.cfg or DEFAULT_APP_CONFIG)
        self.engine_cfg = AppConfig(self.cli_args.engine or DEFAULT_ENGINE_CONFIG)

        # Define the download the directory and create the directory if needed
        self.dl_dir = self._build_image_download_dir()
        self.logfile_name = self._build_logfile_name()
        self.json_log_location = self._build_json_log_location()
        self.json_logfile = self._build_json_logfile_name()
        self.inv_pickle_file = self._build_pickle_filename()
        self.temp_storage_path = self._build_temp_storage()
        self.urls = None
        self.image_data = None
        self._display_file_locations()

        self.inventory = None

    def _build_image_download_dir(self) -> str:
        # =========================
        # IMAGE DOWNLOAD DIRECTORY
        # =========================
        dl_dir = self.app_cfg.get(AppCfgFileSections.STORAGE,
                                  AppCfgFileSectionKeys.LOCAL_DIR)
        dl_drive = self.app_cfg.get(AppCfgFileSections.STORAGE,
                                    AppCfgFileSectionKeys.LOCAL_DRIVE_LETTER)

        if dl_drive not in [None, '']:
            dl_dir = f"{dl_drive.strip(':')}:{dl_dir}"
        utils.check_if_location_exists(location=dl_dir, create_dir=True)
        return dl_dir

    def _build_logfile_name(self) -> str:
        # ================================
        # LOGFILE NAME
        # ================================
        logfile_name = AppLogging.build_logfile_name(cfg_info=self.app_cfg)
        log_dir = os.path.sep.join(logfile_name.split(os.path.sep)[0:-1])
        utils.check_if_location_exists(location=log_dir, create_dir=True)
        return logfile_name

    def _build_json_log_location(self) -> str:
        # ======================
        # JSON LOGFILE LOCATION
        # ======================
        json_log_location = self.app_cfg.get(AppCfgFileSections.LOGGING,
                                             AppCfgFileSectionKeys.JSON_FILE_DIR)
        json_drive = self.app_cfg.get(AppCfgFileSections.LOGGING,
                                      AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
        if json_drive not in [None, '']:
            json_log_location = f"{json_drive.strip(':')}:{json_log_location}"
        utils.check_if_location_exists(location=json_log_location, create_dir=True)
        return json_log_location

    def _build_json_logfile_name(self) -> str:
        # Get logging prefix and suffix
        add_ons = [self.app_cfg.get(AppCfgFileSections.LOGGING,
                                    AppCfgFileSectionKeys.PREFIX),
                   self.app_cfg.get(AppCfgFileSections.LOGGING,
                                    AppCfgFileSectionKeys.SUFFIX)]

        # Isolate the timestamp out of the logfile name.
        log_name = self.logfile_name.split(os.path.sep)[-1]
        timestamp = '-'.join(log_name.split('_')[0:-1])
        for update in add_ons:
            if update is not None:
                timestamp = timestamp.replace(update, '')

        # Build the file name
        filename = f"{timestamp}.{JsonLog.EXTENSION}"

        # Build the full file spec
        filename = os.path.sep.join([self.json_log_location, filename])
        return filename

    def _build_pickle_filename(self) -> str:
        # ==========================
        # INVENTORY PICKLE FILE
        # ==========================
        pickle_location = self.json_log_location
        pickle_filename = "{0}{1}".format(self.engine_cfg.get(ProjectCfgFileSections.PYTHON_PROJECT,
                                                              ProjectCfgFileSectionKeys.NAME).upper(), PICKLE_EXT)
        pickle_filename = os.path.sep.join([pickle_location, pickle_filename])
        utils.check_if_location_exists(location=pickle_location, create_dir=True)
        return pickle_filename

    def _build_temp_storage(self) -> str:
        # ======================
        # JSON LOGFILE LOCATION
        # ======================
        storage_location = self.app_cfg.get(
            AppCfgFileSections.STORAGE, AppCfgFileSectionKeys.TEMP_STORAGE_PATH)
        storage_drive = self.app_cfg.get(
            AppCfgFileSections.STORAGE, AppCfgFileSectionKeys.TEMP_STORAGE_DRIVE)
        if storage_drive not in [None, '']:
            storage_location = f"{storage_drive.strip(':')}:{storage_location}"
        utils.check_if_location_exists(location=storage_location, create_dir=True)
        return storage_location

    def _display_file_locations(self) -> None:
        table = prettytable.PrettyTable()
        table.field_names = ['File Type', 'Location']
        for col in table.field_names:
            table.align[col] = 'l'

        setup = OrderedDict([
            ('DL Directory', self.dl_dir),
            ('DL Log File', self.logfile_name),
            ('JSON Data File', self.json_logfile),
            ('Binary Inv File', self.inv_pickle_file),
            ('Temp Storage', self.temp_storage_path)])
        for name, data in setup.items():
            table.add_row([name, data])
        print(table.get_string(title="FILE INFORMATION"))


class AppLogging(object):

    @staticmethod
    def build_logfile_name(cfg_info: configparser.ConfigParser):
        """
        Builds the logfile name and path for each invocation of the application.
        The name is built based on information within the application configuration
        file. (cfg file, not the engine.cfg file)

        :param cfg_info: Absolute path to the configuration file

        :return: tuple((str) log file directory, (str) full filespec name of the log file).

        """
        logfile_info = {
            'prefix': cfg_info.get(AppCfgFileSections.LOGGING,
                                   AppCfgFileSectionKeys.PREFIX),
            'suffix': cfg_info.get(AppCfgFileSections.LOGGING,
                                   AppCfgFileSectionKeys.SUFFIX),
            'extension': cfg_info.get(AppCfgFileSections.LOGGING,
                                      AppCfgFileSectionKeys.EXTENSION),
            'drive_letter': cfg_info.get(AppCfgFileSections.LOGGING,
                                         AppCfgFileSectionKeys.LOG_DRIVE_LETTER),
            'directory': cfg_info.get(AppCfgFileSections.LOGGING,
                                      AppCfgFileSectionKeys.LOG_DIRECTORY),
            'log_level': cfg_info.get(AppCfgFileSections.LOGGING,
                                      AppCfgFileSectionKeys.LOG_LEVEL)
        }

        # Set defaults if not specified in the config file
        for key, value in logfile_info.items():
            if value == '' or value == 'None':
                logfile_info[key] = None

        return utils.datestamp_filename(**logfile_info)

    @classmethod
    def configure_logging(cls, app_cfg_obj: PdlConfig) -> Logger:
        # Set log level (CLI overrides the config file)
        log_level = app_cfg_obj.app_cfg.get(
            AppCfgFileSections.LOGGING,
            AppCfgFileSectionKeys.LOG_LEVEL.lower())

        if app_cfg_obj.cli_args.debug:
            log_level = 'debug'

        # Determine and store the log file name, create directory if needed.
        log_dir = os.path.sep.join(app_cfg_obj.logfile_name.split(os.path.sep)[0:-1])
        utils.check_if_location_exists(location=log_dir, create_dir=True)

        # Setup the root logger for the app
        logger = Logger(filename=app_cfg_obj.logfile_name,
                        default_level=Logger.STR_TO_VAL[log_level],
                        project=app_cfg_obj.app_cfg.get(
                            AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.NAME),
                        set_root=True)

        # Show defined loggers and log levels
        logger.debug(f"Log File: {app_cfg_obj.logfile_name}")
        for line in logger.list_loggers().split('\n'):
            logger.debug(line)

        return logger


def is_url(target_string: str) -> bool:
    """
    Verify target_string is a URL
    :param target_string: String to test
    :return: (Boolean) Is a URL? T/F
    """
    return target_string.lstrip().lower().startswith('http')


def read_from_buffer(read_delay: float = 0.25) -> list:
    """
    Read URLs from OS copy/paste buffer.
    :param read_delay: Amount of time between each polling of the buffer.
    :return: list of URLs

    """
    last_url = None
    url_list = list()
    log.info("Press CTRL-C to stop buffer scanning.")
    while True:
        try:
            # Read buffer
            buffer = pyperclip.paste().strip()

            # If URL and buffer does not match previous iteration...
            if is_url(buffer) and buffer != last_url:

                # If the URL is already in the buffer, don't duplicate it.
                if buffer in url_list:
                    log.info(f"The specified URL is already in the list ({buffer}).")
                    last_url = buffer
                    continue

                # Append the URL in the list and store the link in the last_buffer
                url_list.append(buffer.strip())
                last_url = buffer
                log.info(f"({len(url_list)}) Copied '{buffer}'")

            # Give user time to collect another url
            time.sleep(read_delay)

        except KeyboardInterrupt:
            # Control-C detected, break out of loop. Context manager will close file.
            break

    # Bye Felicia!
    log.debug(f"Done. {len(url_list)} URLs copied.")
    return url_list


def process_and_record_urls(cfg_obj: PdlConfig) -> list:
    url_file = UrlFile()

    # Check for URLs on the CLI
    raw_url_list = getattr(cfg_obj.cli_args, args.ArgOptions.URLS)

    # If no URLs are provided, check if URL file was specified
    if not raw_url_list:
        log.debug("URL list from CLI is empty.")

        # Check for URL file
        url_file_name = getattr(
            cfg_obj.cli_args, args.ArgOptions.FILE, None)

        if url_file_name is not None:
            url_file_name = os.path.abspath(url_file_name)
            raw_url_list = url_file.read_file(url_file_name)

        elif getattr(cfg_obj.cli_args, args.ArgOptions.BUFFER, False):
            raw_url_list = read_from_buffer()

        else:
            log.info(cfg_obj.cli_args)
            log.debug("No URL file was specified on the CLI, nor reading from buffer.")
            raise NoURLsProvided()

    # Determine the supported URL domains (to remove junk/unexpected URLs)
    url_domains = cfg_obj.app_cfg.get_list(
        AppCfgFileSections.PROJECT, AppCfgFileSectionKeys.URL_DOMAINS)

    # Sanitize the URL list (missing spaces, duplicates, valid and accepted URLs)
    cfg_obj.urls = ArgProcessing.process_url_list(raw_url_list, domains=url_domains)

    # Remove duplicates from the inventory (can be disabled via CLI)
    if not cfg_obj.cli_args.ignore_dups:
        cfg_obj.urls = remove_duplicate_urls_from_inv(cfg_obj)

    # Write the file of accepted/sanitized URLs to be processed
    url_file_dir = cfg_obj.app_cfg.get(AppCfgFileSections.LOGGING,
                                       AppCfgFileSectionKeys.URL_FILE_DIR)
    url_file_drive = cfg_obj.app_cfg.get(AppCfgFileSections.LOGGING,
                                         AppCfgFileSectionKeys.LOG_DRIVE_LETTER)
    if url_file_drive is not None:
        url_file_dir = f"{url_file_drive}:{url_file_dir}"
        log.debug(f"Updated URL File directory for drive letter: {url_file_dir}")

    if len(cfg_obj.urls) > 0:
        url_file.write_file(urls=cfg_obj.urls, create_dir=True, location=url_file_dir)
    else:
        log.info("No URLs for DL, no URL FILE created.")
    return cfg_obj.urls


def remove_duplicate_urls_from_inv(cfg_obj: PdlConfig) -> list:
    page_urls_in_inv = [getattr(image_obj, ImageData.PAGE_URL) for
                        image_obj in cfg_obj.inventory.inventory.values()]
    orig_urls = set(cfg_obj.urls.copy())

    cfg_obj.urls = [url for url in cfg_obj.urls if url not in page_urls_in_inv]
    new_urls = set(cfg_obj.urls.copy())
    duplicates = orig_urls - new_urls

    log.info("Removing URLs from existing inventory: Found {dups} duplicates.".format(
        dups=len(orig_urls)-len(new_urls)))
    log.info(f"URLs for downloading: {len(new_urls)}")

    for dup in duplicates:
        log.info(f"Duplicate: {dup}")

    return cfg_obj.urls


def download_images(cfg_obj: PdlConfig) -> None:
    # Process the urls and return the final list to download
    url_list = process_and_record_urls(cfg_obj=cfg_obj)

    # Import the specified libraries for processing the URLs, based on the config file
    Catalog = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.CATALOG_PARSE))

    Contact = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

    log.info(f"URL LIST:\n{ArgProcessing.list_urls(url_list=url_list)}")

    # Get the correct image URL from each catalog Page
    cfg_obj.image_data = list()
    image_errors = list()
    for index, page_url in enumerate(url_list):

        # Parse the primary image page for the image URL and metadata.
        catalog = Catalog(page_url=page_url)
        log.info(f"({index + 1}/{len(url_list)}) Retrieving URL: {page_url}")
        catalog.get_image_info()

        # If parsing was successful, store the image URL
        if (catalog.image_info.image_url is not None and
                catalog.image_info.image_url.lower().startswith(
                    ArgProcessing.PROTOCOL.lower())):
            cfg_obj.image_data.append(catalog.image_info)
        else:
            image_errors.append(catalog.image_info)

    downloaded_image_urls = cfg_obj.inventory.get_list_of_image_urls()
    downloaded_images = cfg_obj.inventory.get_list_of_images()
    log.debug(f"Have {len(downloaded_image_urls)} URLs in inventory.")

    # Download each image
    for index, image in enumerate(cfg_obj.image_data):
        log.info(f"{index + 1:>3}: {image.image_url}")
        contact = Contact(image_url=image.image_url, dl_dir=cfg_obj.dl_dir, image_info=image)
        if image.image_url not in downloaded_image_urls and image.image_name not in downloaded_images:
            status = contact.download_image()
        else:
            image_metadata = None
            if image.image_url in downloaded_image_urls:
                image_metadata = image.image_url
            elif image.image_name in downloaded_images:
                image_metadata = image.image_name
            log.info(f"Found image url that exists in metadata: {image_metadata}")
            status = Status.EXISTS
            contact.status = status
            contact.image_info.dl_status = status
        log.info(f'DL STATUS: {status}')

    # Add error_info to be included in results
    cfg_obj.image_data += image_errors

    # Log Results
    results = ReportingSummary(cfg_obj.image_data)
    results.log_download_status_results_table()
    results.log_detailed_download_results_table()

    # Log image metadata (DEBUG)
    if cfg_obj.cli_args.debug:
        for image in cfg_obj.image_data:
            log.debug(image.image_name)
            log.debug(pprint.pformat(image.to_dict()))

    # If images were downloaded, create the corresponding JSON file
    if cfg_obj.image_data:
        json_logger.JsonLog(
            image_obj_list=cfg_obj.image_data,
            log_filespec=cfg_obj.json_logfile).write_json()
    else:
        log.info("No images DL'd. No JSON file created.")

# --------------------------------------------------------------------


if __name__ == '__main__':

    app_config = PdlConfig()
    log = AppLogging.configure_logging(app_cfg_obj=app_config)

    # INVENTORY
    metadata = app_config.app_cfg.get_list(
        section=AppCfgFileSections.CLASSIFICATION,
        option=AppCfgFileSectionKeys.TYPES)

    app_config.inventory = Inventory(
        cfg=app_config, force_scan=getattr(app_config.cli_args, args.ArgOptions.FORCE_SCAN))

    # -----------------------------------------------------------------
    #                      DOWNLOAD
    # -----------------------------------------------------------------
    if app_config.cli_args.command == args.ArgSubmodules.DOWNLOAD:
        log.debug("Selected args.ArgSubmodules.DOWNLOAD")
        download_images(cfg_obj=app_config)
        # TODO: Get inventory, include as part of filtering for downloading images.

    # -----------------------------------------------------------------
    #                DUPLICATE MANAGEMENT
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.DUPLICATES:
        log.debug("Selected args.ArgSubmodules.DUPLICATES")
        app_config.inventory.fs_inventory_obj.list_duplicates()
        log.info(app_config.inventory.fs_inventory_obj.list_inventory())

    # -----------------------------------------------------------------
    #                      DATABASE
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.DATABASE:
        log.debug("Selected args.ArgSubmodules.DATABASE")

    # -----------------------------------------------------------------
    #                      IMAGE INFO
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.INFO:
        log.debug("Selected args.ArgSubmodules.INFO")
        image = getattr(app_config.cli_args, args.ArgOptions.IMAGE, None).lower()
        if image.lower().endswith('jpg'):
            image = image.split('.')[0]
        if image.lower() in app_config.inventory.inventory.keys():
            log.info(app_config.inventory.inventory[image])
        else:
            log.info(f"Image '{image}' not found.")

    # -----------------------------------------------------------------
    #                UNRECOGNIZED SUB-COMMAND
    # -----------------------------------------------------------------
    else:
        # Should never get here, argparse should prevent it...
        raise args.UnrecognizedModule(app_config.cli_args.command)

    log.info(f"LOGGED TO: {app_config.logfile_name}")
