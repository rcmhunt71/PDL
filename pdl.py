#!/usr/bin/env python

import os
from pprint import pformat

import PDL.configuration.cli.args as args
from PDL.configuration.cli.urls import UrlArgProcessing as ArgProcessing
from PDL.configuration.properties.app_cfg import AppConfig, AppCfgFileSections, AppCfgFileSectionKeys
import PDL.engine.module_imports as engine
from PDL.logger.logger import Logger as Logger
import PDL.logger.utils as log_utils
from PDL.engine.images import consts as image_consts

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
        'drive': cfg_info.get(AppCfgFileSections.LOGGING,
                              AppCfgFileSectionKeys.LOG_DRIVE_LETTER, None),
        'directory': cfg_info.get(AppCfgFileSections.LOGGING,
                                  AppCfgFileSectionKeys.LOG_DIRECTORY, None)
    }

    for key, value in logfile_info.items():
        if value == '' or value == 'None':
            logfile_info[key] = None
    log_name = log_utils.datestamp_filename(**logfile_info)
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

    # Check for URLs
    raw_url_list = getattr(cli.args, args.ArgOptions.URLS)
    if not raw_url_list:
        log.debug("URL list from CLI is empty.")

        # Check for URL file
        url_file = getattr(cli.args, args.ArgOptions.FILE, None)
        if url_file is None:
            log.debug("No URL file was specified on the CLI.")
        else:
            url_file = os.path.abspath(url_file)
            if os.path.exists(url_file):
                with open(url_file, "r") as FILE:
                    contents = FILE.readlines()
                raw_url_list = [url.strip() for url in contents if url != '']
            else:
                log.error("Unable to find URL file: '{0}'".format(url_file))

    # Sanitize the URL list (missing spaces, duplicates, valid URLs)
    url_domain = app_cfg.get(
        AppCfgFileSections.PROJECT,
        AppCfgFileSectionKeys.URL_DOMAIN)

    url_list = ArgProcessing.process_url_list(raw_url_list)

    # Import the specified routines for processing the URLs
    Catalog = engine.import_module_class(
        app_cfg.get(AppCfgFileSections.PROJECT,
                    AppCfgFileSectionKeys.CATALOG_PARSE))

    Contact = engine.import_module_class(
        app_cfg.get(AppCfgFileSections.PROJECT,
                    AppCfgFileSectionKeys.IMAGE_CONTACT_PARSE))

    # -----------------------------------------------
    # TESTING <<------ DELETE ME
    # -----------------------------------------------
    catalog = Catalog(page_url="foo.com")
    contact = Contact(page_url="foo.com/index.html")
    log.debug("CATALOG URL: %s" % catalog.page_url)
    log.debug("CONTACT URL: %s" % contact.page_url)
    log.debug("CONTACT URLS: %s" % contact.image_urls)
    # -----------------------------------------------

    log.info("URL LIST:\n{0}".format(pformat(url_list)))

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
