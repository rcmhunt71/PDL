#!/usr/bin/env python

import os
from pprint import pformat

import PDL.configuration.cli.args as args
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.cli.url_file import UrlFile
from PDL.configuration.properties.app_cfg import AppConfig, AppCfgFileSections, AppCfgFileSectionKeys
from PDL.engine.module_imports import import_module_class
from PDL.logger.logger import Logger as Logger
import PDL.logger.utils as utils
from PDL.engine.images import status as image_consts

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
                               AppCfgFileSectionKeys.PREFIX, None),
        'suffix': cfg_info.get(AppCfgFileSections.LOGGING,
                               AppCfgFileSectionKeys.SUFFIX, None),
        'extension': cfg_info.get(AppCfgFileSections.LOGGING,
                                  AppCfgFileSectionKeys.EXTENSION, None),
        'drive_letter': cfg_info.get(AppCfgFileSections.LOGGING,
                                     AppCfgFileSectionKeys.LOG_DRIVE_LETTER,
                                     None),
        'directory': cfg_info.get(AppCfgFileSections.LOGGING,
                                  AppCfgFileSectionKeys.LOG_DIRECTORY, None)
    }

    for key, value in logfile_info.items():
        if value == '' or value == 'None':
            logfile_info[key] = None
    log_name = utils.datestamp_filename(**logfile_info)
    return log_name

# --------------------------------------------------------------------


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
        AppCfgFileSectionKeys.LOG_LEVEL.lower(),
        Logger.INFO)

# Setup the root logger for the app
log = Logger(filename=build_logfile_name(cfg_info=app_cfg),
             default_level=Logger.STR_TO_VAL[log_level],
             project=app_cfg.get(
                 AppCfgFileSections.PROJECT,
                 AppCfgFileSectionKeys.NAME, None),
             set_root=True)
log.debug(log.list_loggers())

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
                            AppCfgFileSectionKeys.URL_FILE_DIR, None))

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
        log.info("{index:>3}: {url}".format(index=index, url=image.image_url))
        contact = Contact(
            image_url=image.image_url, dl_dir=dl_dir, image_info=image)
        status = contact.download_image()
        log.info('DL STATUS: {0}'.format(status))

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
