from collections import OrderedDict
import configparser
import os

import PDL.configuration.cli.args as args
from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys, ProjectCfgFileSectionKeys, ProjectCfgFileSections)
from PDL.logger.json_log import JsonLog
from PDL.logger.logger import Logger as Logger
import PDL.logger.utils as utils


import prettytable

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'
DEFAULT_APP_CONFIG = None
PICKLE_EXT = ".dat"


log = Logger()

# TODO: Add docstrings and inline comments


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
