#!/usr/bin/env python

import os
import pprint

import PDL.configuration.cli.args as args
import PDL.logger.json_log as json_logger
import PDL.logger.utils as utils
from PDL.configuration.cli.url_file import UrlFile
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.properties.app_cfg import AppConfig, AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.module_imports import import_module_class
from PDL.logger.logger import Logger as Logger
from PDL.reporting.summary import ReportingSummary

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'
DEFAULT_APP_CONFIG = None


class NoURLsProvided(Exception):
    pass


class PdlConfig(object):
    def __init__(self):
        self.cli_args = args.CLIArgs().args
        self.app_cfg = AppConfig(self.cli_args.cfg or DEFAULT_APP_CONFIG)
        self.engine_cfg = AppConfig(self.cli_args.engine or DEFAULT_ENGINE_CONFIG)

        # Define the download the directory and create the directory if needed
        # TODO: <CODE> Build all relevant data for locations (OS-agnostic)
        self.dl_dir = self.app_cfg.get(AppCfgFileSections.STORAGE,
                                       AppCfgFileSectionKeys.LOCAL_DIR)

        utils.check_if_location_exists(self.dl_dir, create_dir=True)

        self.logfile_name = None
        self.json_log = None

        self.urls = None
        self.image_data = None


class AppLogging(object):

    @staticmethod
    def build_logfile_name(cfg_info):
        """
        Builds the logfile name and path for each invocation of the application.
        The name is built based on information within the application configuration
        file. (cfg file, not the engine.cfg file)

        :param cfg_info: Absolute path to the configuration file

        :return: (str) name of the log file.

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

        log_name = utils.datestamp_filename(**logfile_info)
        return log_name

    @classmethod
    def configure_logging(cls, app_cfg_obj):
        # Set log level (CLI overrides the config file)
        log_level = app_cfg_obj.app_cfg.get(
            AppCfgFileSections.LOGGING,
            AppCfgFileSectionKeys.LOG_LEVEL.lower())

        if app_cfg_obj.cli_args.debug:
            log_level = 'debug'

        # Determine and store the log file name, create directory if needed.
        log_file = cls.build_logfile_name(cfg_info=app_cfg_obj.app_cfg)
        app_cfg_obj.logfile_name = log_file
        log_dir = os.path.sep.join(log_file.split(os.path.sep)[0:-1])
        utils.check_if_location_exists(location=log_dir, create_dir=True)

        # Setup the root logger for the app
        logger = Logger(filename=log_file,
                        default_level=Logger.STR_TO_VAL[log_level],
                        project=app_cfg_obj.app_cfg.get(
                            AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.NAME),
                        set_root=True)

        # Show defined loggers and log levels
        logger.debug("Log File: {0}".format(log_file))
        for line in logger.list_loggers().split('\n'):
            logger.debug(line)

        return logger


def process_and_record_urls(cfg_obj):
    url_file = UrlFile()

    # Check for URLs on the CLI
    raw_url_list = getattr(cfg_obj.cli_args, args.ArgOptions.URLS)

    # If no URLs are provided, check if URL file was specified
    if not raw_url_list:
        log.debug("URL list from CLI is empty.")

        # Check for URL file
        url_file_name = getattr(cfg_obj.cli_args, args.ArgOptions.FILE, None)
        if url_file_name is None:
            log.debug("No URL file was specified on the CLI.")
            raise NoURLsProvided()

        url_file_name = os.path.abspath(url_file_name)
        raw_url_list = url_file.read_file(url_file_name)

    # Determine the supported URL domains (to remove junk/unexpected URLs)
    url_domains = cfg_obj.app_cfg.get_list(
        AppCfgFileSections.PROJECT, AppCfgFileSectionKeys.URL_DOMAINS)

    # Sanitize the URL list (missing spaces, duplicates, valid and accepted URLs)
    cfg_obj.urls = ArgProcessing.process_url_list(raw_url_list, domains=url_domains)

    # Write the file of accepted/sanitized URLs to be processed
    url_file.write_file(
        urls=cfg_obj.urls, create_dir=True,
        location=cfg_obj.app_cfg.get(AppCfgFileSections.LOGGING,
                                     AppCfgFileSectionKeys.URL_FILE_DIR))
    return cfg_obj.urls


def download_images(cfg_obj):
    # Process the urls and return the final list to download
    url_list = process_and_record_urls(cfg_obj=cfg_obj)

    # Import the specified libraries for processing the URLs, based on the config file
    Catalog = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.CATALOG_PARSE))

    Contact = import_module_class(
        cfg_obj.app_cfg.get(AppCfgFileSections.PROJECT,
                            AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

    log.info("URL LIST:\n{0}".format(ArgProcessing.list_urls(url_list=url_list)))

    # Get the correct image URL from each catalog Page
    cfg_obj.image_data = list()
    for page_url in url_list:

        # Parse the primary image page for the image URL and metadata.
        catalog = Catalog(page_url=page_url)
        catalog.get_image_info()

        # If parsing was successful, store the image URL
        if (catalog.image_info.image_url is not None and
                catalog.image_info.image_url.lower().startswith(
                    ArgProcessing.PROTOCOL.lower())):
            cfg_obj.image_data.append(catalog.image_info)

    # Download each image
    for index, image in enumerate(cfg_obj.image_data):
        log.info("{index:>3}: {url}".format(index=index + 1, url=image.image_url))
        contact = Contact(image_url=image.image_url, dl_dir=cfg_obj.dl_dir, image_info=image)
        status = contact.download_image()
        log.info('DL STATUS: {0}'.format(status))

    # Log Results
    results = ReportingSummary(cfg_obj.image_data)
    results.log_download_status_results_table()
    results.log_detailed_download_results_table()

    if cfg_obj.cli_args.debug:
        for image in cfg_obj.image_data:
            print(image.image_name)
            pprint.pprint(image.to_dict())

    json_logger.JsonLog(
        image_obj_list=cfg_obj.image_data,
        cfg_info=cfg_obj.app_cfg,
        logfile_name=cfg_obj.logfile_name).write_json()

# --------------------------------------------------------------------


if __name__ == '__main__':

    app_config = PdlConfig()
    log = AppLogging.configure_logging(app_cfg_obj=app_config)

    # -----------------------------------------------------------------
    #                      DOWNLOAD
    # -----------------------------------------------------------------
    if app_config.cli_args.command == args.ArgSubmodules.DOWNLOAD:
        log.debug("Selected args.ArgSubmodules.DOWNLOAD")
        download_images(cfg_obj=app_config)

    # -----------------------------------------------------------------
    #                DUPLICATE MANAGEMENT
    # -----------------------------------------------------------------
    elif app_config.cli_args.command == args.ArgSubmodules.DUPLICATES:
        log.debug("Selected args.ArgSubmodules.DUPLICATES")

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

    # -----------------------------------------------------------------
    #                UNRECOGNIZED SUB-COMMAND
    # -----------------------------------------------------------------
    else:
        # Should never get here, argparse should prevent it...
        raise args.UnrecognizedModule(app_config.cli_args.command)

    log.info("LOGGED TO: {logfile}".format(logfile=app_config.logfile_name))
