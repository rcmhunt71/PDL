#!/usr/bin/env python

import os
import pprint

import PDL.configuration.cli.args as args
import PDL.logger.json_log as json_log
import PDL.logger.utils as utils
from PDL.configuration.cli.url_file import UrlFile
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.properties.app_cfg import AppConfig, AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.module_imports import import_module_class
from PDL.logger.logger import Logger as Logger
from PDL.reporting.summary import ReportingSummary

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'
DEFAULT_APP_CONFIG = None


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

    for key, value in logfile_info.items():
        if value == '' or value == 'None':
            logfile_info[key] = None
    log_name = utils.datestamp_filename(**logfile_info)
    return log_name


# --------------------------------------------------------------------
if __name__ == '__main__':

    # Instantiate the CLI Args parser
    cli = args.CLIArgs()

    # Get the configuration files (either via CLI or default value)
    app_cfg = AppConfig(cli.args.cfg or DEFAULT_APP_CONFIG)
    engine_cfg = AppConfig(cli.args.engine or DEFAULT_ENGINE_CONFIG)

    # Set log level (CLI overrides the config file)
    if cli.args.debug:
        log_level = 'debug'
    else:
        log_level = app_cfg.get(
            AppCfgFileSections.LOGGING,
            AppCfgFileSectionKeys.LOG_LEVEL.lower())

    # Setup the root logger for the app
    log_file = build_logfile_name(cfg_info=app_cfg)
    log_dir = os.path.sep.join(log_file.split(os.path.sep)[0:-1])
    utils.check_if_location_exists(location=log_dir, create_dir=True)

    log = Logger(filename=log_file,
                 default_level=Logger.STR_TO_VAL[log_level],
                 project=app_cfg.get(
                     AppCfgFileSections.PROJECT,
                     AppCfgFileSectionKeys.NAME),
                 set_root=True)

    # (DEBUG) Show defined loggers and log levels
    log.debug("Log File: {0}".format(log_file))
    for line in log.list_loggers().split('\n'):
        log.debug(line)

    # Actions for each specific sub-command

    # -----------------------------------------------------------------
    #                      DOWNLOAD
    # -----------------------------------------------------------------
    if cli.args.command == args.ArgSubmodules.DOWNLOAD:
        log.debug("Selected args.ArgSubmodules.DOWNLOAD")

        url_file = UrlFile()

        # Check for URLs
        raw_url_list = getattr(cli.args, args.ArgOptions.URLS)
        if not raw_url_list:
            log.debug("URL list from CLI is empty.")

            # Check for URL file
            url_file_name = getattr(cli.args, args.ArgOptions.FILE, None)
            if url_file_name is None:
                log.debug("No URL file was specified on the CLI.")
            else:
                url_file_name = os.path.abspath(url_file_name)
                raw_url_list = url_file.read_file(url_file_name)

        # Sanitize the URL list (missing spaces, duplicates, valid URLs)
        url_domains = app_cfg.get_list(
            AppCfgFileSections.PROJECT,
            AppCfgFileSectionKeys.URL_DOMAINS)

        url_list = ArgProcessing.process_url_list(raw_url_list, domains=url_domains)
        url_file.write_file(urls=url_list, create_dir=True,
                            location=app_cfg.get(
                                AppCfgFileSections.LOGGING,
                                AppCfgFileSectionKeys.URL_FILE_DIR))

        # Import the specified routines for processing the URLs
        Catalog = import_module_class(
            app_cfg.get(AppCfgFileSections.PROJECT,
                        AppCfgFileSectionKeys.CATALOG_PARSE))

        Contact = import_module_class(
            app_cfg.get(AppCfgFileSections.PROJECT,
                        AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

        log.info("URL LIST:\n{0}".format(
            ArgProcessing.list_urls(url_list=url_list)))

        image_data = list()
        for page_url in url_list:
            catalog = Catalog(page_url=page_url)
            catalog.get_image_info()
            if (catalog.image_info.image_url is not None and
                    catalog.image_info.image_url.lower().startswith(
                        ArgProcessing.PROTOCOL.lower())):
                image_data.append(catalog.image_info)

        # TODO: <CODE> Build all relevant data for locations (OS-agnostic)

        dl_dir = app_cfg.get(AppCfgFileSections.STORAGE,
                             AppCfgFileSectionKeys.LOCAL_DIR)

        utils.check_if_location_exists(dl_dir, create_dir=True)

        for index, image in enumerate(image_data):
            log.info("{index:>3}: {url}".format(
                index=index + 1, url=image.image_url))
            contact = Contact(
                image_url=image.image_url, dl_dir=dl_dir, image_info=image)
            contact.download_image()
            log.info('DL STATUS: {0}'.format(contact.status))

        # Log Results
        results = ReportingSummary(image_data)
        results.log_download_status_results_table()
        results.log_detailed_download_results_table()

        if cli.args.debug:
            for image in image_data:
                print(image.image_name)
                pprint.pprint(image.to_dict())

        jsonlog = json_log.JsonLog(image_obj_list=image_data, cfg_info=app_cfg, logfile_name=log_file)
        jsonlog.write_json()

        # TODO: Create JSON output file.

    # -----------------------------------------------------------------
    #                DUPLICATE MANAGEMENT
    # -----------------------------------------------------------------
    elif cli.args.command == args.ArgSubmodules.DUPLICATES:
        log.debug("Selected args.ArgSubmodules.DUPLICATES")

    # -----------------------------------------------------------------
    #                      DATABASE
    # -----------------------------------------------------------------
    elif cli.args.command == args.ArgSubmodules.DATABASE:
        log.debug("Selected args.ArgSubmodules.DATABASE")

    # -----------------------------------------------------------------
    #                      IMAGE INFO
    # -----------------------------------------------------------------
    elif cli.args.command == args.ArgSubmodules.INFO:
        log.debug("Selected args.ArgSubmodules.INFO")

    # -----------------------------------------------------------------
    #                UNRECOGNIZED SUB-COMMAND
    # -----------------------------------------------------------------
    else:
        # Should never get here, argparse should prevent it...
        raise args.UnrecognizedModule(cli.args.command)

    log.info("LOGGED TO: {logfile}".format(logfile=log_file))
