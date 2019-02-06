from configparser import ConfigParser, NoSectionError, NoOptionError
import os
from typing import List

from PDL.logger.logger import Logger

log = Logger()


class AppCfgFileSections(object):
    """
    Sections available within the application configuration. Defined as
    constants to reduce typos, and if a value needs to change, it only needs to
    be changed here.

    Listed in alphabetical order.

    """
    DATABASE = 'database'
    LOGGING = 'logging'
    IMAGES = 'images'
    PROJECT = 'project'
    STORAGE = 'storage'
    CLASSIFICATION = 'classification'


class AppCfgFileSectionKeys(object):
    """
    Options available within the various sections. Defined as constants to
    reduce typos, and if a value needs to change, it only needs to be changed
    here.

    Chose not to map the options to the section, since there could duplicate
    option names across sections. (Unnecessary complication at this point.)

    Listed in alphabetical order.

    """
    CATALOG_PARSE = 'catalog_parse'
    SIMULTANEOUS_DLS = 'simultaneous_dls'
    EXTENSION = 'extension'
    IMAGE_CONTACT_PARSE = 'image_contact_parse'
    INVENTORY_FILENAME = 'inventory_filename'
    JSON_FILE_DIR = 'json_file_dir'
    LOCAL_DIR = 'local_dir'
    LOCAL_DRIVE_LETTER = 'local_drive_letter'
    LOG_DIRECTORY = 'log_directory'
    LOG_DRIVE_LETTER = 'log_drive_letter'
    LOG_LEVEL = 'log_level'
    NAME = 'name'
    PORT = 'port'
    PREFIX = 'prefix'
    STORAGE_DRIVE_LETTER = 'storage_drive_letter'
    STORAGE_DIR = 'storage_dir'
    TEMP_STORAGE_DRIVE = 'temp_storage_drive'
    TEMP_STORAGE_PATH = 'temp_storage_path'
    SUFFIX = 'suffix'
    TYPES = 'types'
    URL = 'url'
    URL_DOMAINS = 'url_domains'
    URL_FILE_DIR = 'url_file_dir'


class ProjectCfgFileSections(object):
    """
    Sections available within the project configuration. Defined as
    constants to reduce typos, and if a value needs to change, it only needs to
    be changed here.

    """
    PYTHON_PROJECT = 'python_project'


class ProjectCfgFileSectionKeys(object):
    """
    Options available within the various sections. Defined as constants to
    reduce typos, and if a value needs to change, it only needs to be changed
    here.

    """
    NAME = 'name'


class ConfigSectionDoesNotExist(Exception):
    """ Exception for non-existent config sections. """

    msg_fmt = "Section '{section}' is not defined in '{cfg_file}'"

    def __init__(self, section: str, cfg_file: str) -> None:
        self.message = self.msg_fmt.format(section=section, cfg_file=cfg_file)


class OptionDoesNotExist(Exception):
    """ Exception for non-existent option within a sections. """

    msg_fmt = ("Option '{option}' in section '{section}' "
               "is not defined in '{cfg_file}'")

    def __init__(self, section: str, option: str, cfg_file: str) -> None:
        self.message = self.msg_fmt.format(
            section=section, option=option, cfg_file=cfg_file)


class CannotCastValueToType(Exception):
    """
    Exception for trying to cast a value to type that cannot support the value.
    """

    msg_fmt = ("Option '{option}' in section '{section}' "
               "cannot be cast to '{type_}'in '{cfg_file}'")

    def __init__(self, section: str, option: str, cfg_file: str, type_: str) -> None:
        self.message = self.msg_fmt.format(
            section=section, option=option, cfg_file=cfg_file, type_=type_)


class CfgFileDoesNotExist(Exception):
    """ Exception for non-existent config file. """

    msg_fmt = "Config file '{cfg_file}' was not found or does not exist."

    def __init__(self, cfg_file: str) -> None:
        self.message = self.msg_fmt.format(cfg_file=cfg_file)


class AppConfig(ConfigParser):
    """
    Config Parser for the application, plus a few helper routines
    (primarily for debugging)

    """
    def __init__(self, cfg_file: str, test: bool = False) -> None:
        ConfigParser.__init__(self)
        self.cfg_file = cfg_file

        # This is not a test... this is for a live-fire exercise. The config
        # file needs to exist.
        if not test:

            # Check to see if config file exists. If so, read it, otherwise
            # throw an exception
            if self.cfg_file is not None:
                if os.path.exists(self.cfg_file):
                    log.debug(f'Reading: {self.cfg_file}')
                    self.config = self.read(self.cfg_file)
                else:
                    log.error(f'Unable to read cfg file: {self.cfg_file}')
                    raise CfgFileDoesNotExist(cfg_file=self.cfg_file)
            else:
                log.error(f"No config file was provided: '{str(cfg_file)}'.")
                raise CfgFileDoesNotExist(cfg_file=str(cfg_file))

        # For testing, read specified file, without checking for existence
        else:
            log.debug(f'Reading: {self.cfg_file}')
            self.config = self.read(self.cfg_file)

    def get_options(self, section: str) -> List[str]:
        """
        Get the list of options within a section, and log as debug (if log level
        enabled). If the section does not exist, throw an exception.

        :param section: (str) Config file section

        :return: (list) - List options for the specified section

        """
        if self.has_section(section=section):
            options = self.options(section)
            log.debug("Options for {section}:\n{option_list}".format(
                section=section, option_list=[f"\t{opt}\n" for opt in options]))
            return options

        raise ConfigSectionDoesNotExist(section=section, cfg_file=self.cfg_file)

    def _get_raw_option(self, section: str, option: str, api_name: str) -> str:
        """
        Designed to get raw option data and return it to the calling function,
        but will check if the section exists.

        :param section: (str) Section name
        :param option: (str) Option name under section
        :param api_name: (str) Parser API (get, set, etc.)

        :return: (str) Raw returned value from API

        """
        if self.has_section(section=section):
            if self.has_option(section=section, option=option):
                api = getattr(self, api_name)
                return api(section=section, option=option)
            raise NoOptionError(section, option)
        raise NoSectionError(section)

    def get_list(self, section: str, option: str, delimiter: str = ',') -> List[str]:
        """
        Gets delimited option value, splits into list, and returns list.

        e.g. option = 1,2,3,4 ==> [1, 2, 3, 4]

        :param section: (str) Section Name
        :param option: (str) Option Name
        :param delimiter: (str) Character(s) to split value

        :return: List of values based on splitting delimiter

        """
        api_name = 'get'
        list_str = self._get_raw_option(
            section=section, option=option, api_name=api_name)
        return [x.strip() for x in list_str.split(delimiter)]
