from collections import OrderedDict
import configparser
import os

import PDL.configuration.cli.args as args
from PDL.configuration.properties.app_cfg import (
    AppConfig, AppCfgFileSections, AppCfgFileSectionKeys, ProjectCfgFileSectionKeys, ProjectCfgFileSections)
from PDL.logger.json_log import JsonLog
from PDL.logger.logger import Logger as Logger
import PDL.logger.utils as utils
from PDL.reporting.summary import ReportingSummary


import prettytable

DEFAULT_ENGINE_CONFIG = 'pdl.cfg'  # Default Engine config file name
DEFAULT_APP_CONFIG = None          # Default app config file name
PICKLE_EXT = ".dat"                # Default extension for pickled (binary) data files


log = Logger()

"""
This class is a container class, storing various information required 
by the application to operate:
  * Configuration objects (configparser-based)
  * Directories for writing information (logs, file/data stores, DLs)
  * URLs, data, inventory

The class will also build the various directories required by the application,
based on the information specified in the configuration files.

"""


class PdlConfig(object):
    def __init__(self) -> None:
        self.image_data = None
        self.inventory = None
        self.urls = None

        self.cli_args = args.CLIArgs().args
        self.app_cfg = AppConfig(self.cli_args.cfg or DEFAULT_APP_CONFIG)
        self.engine_cfg = AppConfig(self.cli_args.engine or DEFAULT_ENGINE_CONFIG)

        # Define the various directory paths and create the directories if needed
        self.dl_dir = self._build_image_download_dir()
        self.logfile_name = self._build_logfile_name()
        self.json_log_location = self._build_json_log_location()
        self.json_logfile = self._build_json_logfile_name()
        self.inv_pickle_file = self._build_pickle_filename()
        self.temp_storage_path = self._build_temp_storage()

        self._display_file_locations()

    def _build_image_download_dir(self) -> str:
        """
        Builds the image download directory, and create the directory if necessary.

        :return: (str) Absolute path to the DL directory

        """
        dl_dir = self.app_cfg.get(AppCfgFileSections.STORAGE,
                                  AppCfgFileSectionKeys.LOCAL_DIR)
        dl_drive = self.app_cfg.get(AppCfgFileSections.STORAGE,
                                    AppCfgFileSectionKeys.LOCAL_DRIVE_LETTER)

        if dl_drive not in [None, '']:
            dl_dir = f"{dl_drive.strip(':')}:{dl_dir}"

        dl_dir = os.path.abspath(dl_dir)
        utils.check_if_location_exists(location=dl_dir, create_dir=True)
        return dl_dir

    def _build_logfile_name(self) -> str:
        """
        Builds the logging directory, and create the directory if necessary.

        :return: (str) Absolute path to the logging directory

        """
        logfile_name = AppLogging.build_logfile_name(cfg_info=self.app_cfg)
        log_dir = os.path.abspath(os.path.sep.join(logfile_name.split(os.path.sep)[0:-1]))

        utils.check_if_location_exists(location=log_dir, create_dir=True)
        return logfile_name

    def _build_json_log_location(self) -> str:
        """
        Builds the JSON inventory logging directory, and create the directory if necessary.

        :return: (str) Absolute path to the JSON inventory logging directory

        """
        json_log_location = self.app_cfg.get(AppCfgFileSections.LOGGING,
                                             AppCfgFileSectionKeys.JSON_FILE_DIR)
        json_drive = self.app_cfg.get(AppCfgFileSections.LOGGING,
                                      AppCfgFileSectionKeys.LOG_DRIVE_LETTER)

        if json_drive not in [None, '']:
            json_log_location = f"{json_drive.strip(':')}:{json_log_location}"

        json_log_location = os.path.abspath(json_log_location)
        utils.check_if_location_exists(location=json_log_location, create_dir=True)
        return json_log_location

    def _build_json_logfile_name(self) -> str:
        """
        Builds the JSON inventory log file name.

        :return: (str) Absolute path to the JSON inventory file name.

        """
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
        filename = os.path.abspath(os.path.sep.join([self.json_log_location, filename]))
        return filename

    def _build_pickle_filename(self) -> str:
        """
        Builds the general inventory pickled (binary) data file.

        :return: (str) Absolute path to the pickled (binary) data file name.

        """
        pickle_location = self.json_log_location
        pickle_filename = "{0}{1}".format(
            self.engine_cfg.get(ProjectCfgFileSections.PYTHON_PROJECT,
                                ProjectCfgFileSectionKeys.NAME).upper(), PICKLE_EXT)

        pickle_filename = os.path.abspath(os.path.sep.join([pickle_location, pickle_filename]))
        utils.check_if_location_exists(location=pickle_location, create_dir=True)
        return pickle_filename

    def _build_temp_storage(self) -> str:
        """
        Builds the temp (local) file storage directory.

        :return: (str) Absolute path to the temp (local) file storage directory.

        """
        storage_location = self.app_cfg.get(
            AppCfgFileSections.STORAGE, AppCfgFileSectionKeys.TEMP_STORAGE_PATH)

        storage_drive = self.app_cfg.get(
            AppCfgFileSections.STORAGE, AppCfgFileSectionKeys.TEMP_STORAGE_DRIVE)

        if storage_drive not in [None, '']:
            storage_location = f"{storage_drive.strip(':')}:{storage_location}"

        storage_location = os.path.abspath(storage_location)
        utils.check_if_location_exists(location=storage_location, create_dir=True)
        return storage_location

    def _display_file_locations(self) -> None:
        """
        Lists/logs the locations of the various configured/generated directories.
        Used for reference and debugging.

        :return: None

        """

        # Build and configure the table
        table = prettytable.PrettyTable()
        table.field_names = ['File Type', 'Location']
        for col in table.field_names:
            table.align[col] = 'l'

        # Configure the table data (use Ordered Dict to maintain order in table,
        # based on importance of data)
        setup = OrderedDict([
            ('DL Directory', self.dl_dir),
            ('DL Log File', self.logfile_name),
            ('JSON Data File', self.json_logfile),
            ('Binary Inv File', self.inv_pickle_file),
            ('Temp Storage', self.temp_storage_path)])

        # Populate the table
        for name, data in setup.items():
            table.add_row([name, data])

        # Display results
        ReportingSummary.log_table(table.get_string(title="FILE INFORMATION"))


class AppLogging(object):
    """

    This class sets up the logging specific to the application.

    """

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
        """
        Sets up the root logger (format, location) and updates the existing the handlers

        :param app_cfg_obj: (PdlConfig): Contains the required location, etc., for the logger

        :return: Instantiated, updated root logger

        """
        # Set log level (CLI overrides the config file)
        # ---------------------------------------------
        # Get the config-file specified value
        log_level = app_cfg_obj.app_cfg.get(
            AppCfgFileSections.LOGGING,
            AppCfgFileSectionKeys.LOG_LEVEL.lower())

        if app_cfg_obj.cli_args.debug:
            log_level = 'debug'

        # Determine and store the log file name, create directory if needed.
        log_dir = os.path.abspath(os.path.sep.join(app_cfg_obj.logfile_name.split(os.path.sep)[0:-1]))
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
