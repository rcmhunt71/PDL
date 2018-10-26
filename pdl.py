#!/usr/bin/env python

from PDL.configuration.cli import args, urls
from PDL.configuration.properties.app_cfg import AppConfig, AppCfgFileSections, AppCfgFileSectionKeys
from PDL.logger.logger import Logger as Logger
import PDL.logger.utils as log_utils
from PDL.images import image_info, download_base, consts as image_consts

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'
DEFAULT_APP_CONFIG = None


def build_logfile_name(cfg_info):
    logfile_info = {
        'prefix': cfg_info.get(AppCfgFileSections.LOGGING,
                               AppCfgFileSectionKeys.PREFIX, None),
        'suffix': cfg_info.get(AppCfgFileSections.LOGGING,
                               AppCfgFileSectionKeys.SUFFIX, None),
        'extension': cfg_info.get(AppCfgFileSections.LOGGING,
                                  AppCfgFileSectionKeys.EXTENSION, None)
    }

    for key, value in logfile_info.items():
        if value == '' or value == 'None':
            logfile_info[key] = None
    log_name = log_utils.datestamp_filename(**logfile_info)
    return log_name


cli = args.CLIArgs()
app_cfg = AppConfig(cli.args.cfg or DEFAULT_APP_CONFIG)
engine_cfg = AppConfig(cli.args.engine or DEFAULT_ENGINE_CONFIG)

if cli.args.debug:
    log_level = 'debug'
else:
    log_level = app_cfg.get(
        AppCfgFileSections.LOGGING,
        AppCfgFileSectionKeys.LOG_LEVEL.lower(),
        Logger.INFO)


logfile_name = build_logfile_name(cfg_info=app_cfg)
log = Logger(filename=build_logfile_name(cfg_info=app_cfg),
             default_level=Logger.STR_TO_VAL[log_level],
             project=app_cfg.get(
                 AppCfgFileSections.PYTHON_PROJECT,
                 AppCfgFileSectionKeys.NAME, None),
             set_root=True)
log.debug(log.list_loggers())

if cli.args.command == args.ArgSubmodules.DOWNLOAD:
    log.debug("Selected args.ArgSubmodules.DOWNLOAD")
elif cli.args.command == args.ArgSubmodules.DUPLICATES:
    log.debug("Selected args.ArgSubmodules.DUPLICATES")
elif cli.args.command == args.ArgSubmodules.DATABASE:
    log.debug("Selected args.ArgSubmodules.DATABASE")
elif cli.args.command == args.ArgSubmodules.INFO:
    log.debug("Selected args.ArgSubmodules.INFO")
else:
    log.error("Unrecognized submodule!!")