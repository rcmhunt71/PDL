"""

  Definitions for defining CLI Arguments

  NOTE: Argparse docs: https://docs.python.org/3/library/argparse.html

"""

import argparse
import pprint
from typing import List, Optional

from PDL.logger.logger import Logger as PDL_log

LOG = PDL_log()


class UnrecognizedModule(Exception):
    """

    Generic exception - defined for improved clarity

    """
    msg_fmt = "Unrecognized module: '{module}'"

    def __init__(self, module: str) -> None:
        self.message = self.msg_fmt.format(module=module)
        super(UnrecognizedModule, self).__init__()


class ArgSubmodules:
    """

    Defined submodules for the application

    """
    DATABASE = 'db'
    DOWNLOAD = 'dl'
    DUPLICATES = 'dups'
    GENERAL = 'general'
    INFO = 'info'
    STATS = 'stats'

    @classmethod
    def get_const_names(cls) -> List[str]:
        """
        Return a list of the names of the class-level constants

        :return: list of class-constant names

        """
        return [key for key, val in cls.__dict__.items()
                if not key.startswith('_') and key.upper() == key]

    @classmethod
    def get_const_values(cls) -> List[str]:
        """
        Return a list of the values of the class-level constants

        :return: list of class-constant values

        """
        return [val for key, val in cls.__dict__.items()
                if not key.startswith('_') and key.upper() == key]


class ArgOptions:
    """

    Defined constants for sub-options available via the CLI across all
    sub-modules.

    """
    AUTHOR = 'author'
    BUFFER = 'buffer'
    CFG = 'cfg'
    COMMAND = 'command'
    DIRECTORY = 'directory'
    DRY_RUN = 'dryrun'
    DEBUG = 'debug'
    DETAILS = 'details'
    ENGINE = 'engine'
    FILE = 'file'
    FILE_SPEC = 'filespec'
    FORCE_SCAN = 'force_scan'
    GENERAL = 'general'
    IGNORE_DUPS = 'ignore_dups'
    IMAGE = 'image'
    RECORDS = 'records'
    SUMMARY = 'summary'
    SYNC = 'sync'
    REMOVE_DUPS = 'remove_dups'
    URLS = 'urls'

    SHORTCUTS = {
        AUTHOR: "a",
        BUFFER: "b",
        CFG: "c",
        DEBUG: "d",
        DETAILS: "d",
        DIRECTORY: "d",
        DRY_RUN: "r",
        ENGINE: "e",
        FILE: "f",
        FILE_SPEC: "f",
        FORCE_SCAN: "s",
        IGNORE_DUPS: "i",
        RECORDS: "r",
        REMOVE_DUPS: "x",
        SUMMARY: "s",
        SYNC: "s",
    }


class CLIArgs:
    """
    The class parses the CLI arguments to determine what user actions are required.
    Each "action set" is defined as a subparser, with the corresponding options.
    For each "action set", a set of rules can be defined to check the required
    switches were provided after parsing the routine.

    Parsers:
        Each basic set of operations is divided based on subparser.
            e.g. - downloading, inventory, dupchecks, etc.

        To determine which subparser was invoked:
            - check the value stored within parser.command
            - the parser.command is defined as part of the subparsers attribute.

    """
    PURPOSE = "Image Download Utility"
    FLAGS = {
        ArgSubmodules.GENERAL: [ArgOptions.DEBUG, ArgOptions.DRY_RUN],
        ArgSubmodules.DATABASE: [ArgOptions.RECORDS, ArgOptions.SYNC,
                                 ArgOptions.DETAILS],
        ArgSubmodules.DOWNLOAD: [],
        ArgSubmodules.DUPLICATES: [ArgOptions.REMOVE_DUPS],
        ArgSubmodules.INFO: [],
        ArgSubmodules.STATS: [],
    }

    def __init__(self, test_args_list: Optional[List[str]] = None) -> None:

        self.parser = argparse.ArgumentParser(description=self.PURPOSE)
        self.subparsers = self.parser.add_subparsers(dest=ArgOptions.COMMAND)

        self._define_standard_args()
        self._downloads()
        self._database()
        self._duplicates()
        self._image_info()
        self._stats_()

        self.args = self.parse_args(test_args_list)

    @staticmethod
    def get_module_names() -> List[str]:
        """
        Lists all of the submodules available as part of the application
        :return: List of strings (names of the submodules)

        """
        modules = ArgSubmodules.get_const_values()
        LOG.debug(f"Request for module names: {pprint.pformat(modules)}")
        return modules

    @staticmethod
    def get_shortcut(option: str) -> str:
        """
        Gets the single letter representation of the option
        :param option: Name of the option
        :return: character used on the CLI to represent the option.

        """
        if option in ArgOptions.SHORTCUTS.keys():
            return f"-{ArgOptions.SHORTCUTS[option]}"
        LOG.error(f'No shortcut registered for "{option}".')
        return ''

    def parse_args(self, test_args_list: Optional[List[str]] = None) -> argparse.Namespace:
        """
        Parses CLI, but allows injection of arguments for testing purposes
        :param test_args_list: List of args to test for.
        :return:

        """
        LOG.debug("Parsing command line args.")
        if test_args_list is not None:
            LOG.debug(
                f"Args passed in for testing:\n\t{test_args_list}")
        return (self.parser.parse_args() if test_args_list is None else
                self.parser.parse_args(test_args_list))

    def _define_standard_args(self) -> None:
        """
        Standard Args (not specific to any given action)
        :param self: Automatically provided.
        :return: None.
        """

        # GLOBAL DEBUG FLAG
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.DEBUG),
            f'--{ArgOptions.DEBUG}',
            help="Enable debug flag for logging and reporting",
            action='store_true')

        # DRY RUN
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.DRY_RUN),
            f'--{ArgOptions.DRY_RUN}',
            help="Enable flag for dry-run. See what happens without taking action",
            action='store_true')

        # USER/APP CFG FILE
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.CFG),
            f'--{ArgOptions.CFG}',
            help="Specify application configuration file")

        # ENGINE CFG FILE
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.ENGINE),
            f'--{ArgOptions.ENGINE}',
            help="Specify engine configuration file")

        # FORCE SCAN
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.FORCE_SCAN),
            f'--{ArgOptions.FORCE_SCAN}',
            help="Force inventory scan",
            action='store_true')

    def _downloads(self) -> None:
        """
        Args associated with downloading images
        :param self: Automatically provided.
        :return: None.
        """
        dl_args = self.subparsers.add_parser(
            ArgSubmodules.DOWNLOAD, help="Options for downloading images")

        # URLS TO PARSE AND DOWNLOAD
        dl_args.add_argument(
            ArgOptions.URLS, nargs=argparse.REMAINDER,
            help=("List of URLs to parse and download, should be last argument "
                  "on the CLI"),
            metavar="<URLS>"
        )

        # FILE TO READ URLS
        dl_args.add_argument(
            self.get_shortcut(ArgOptions.FILE),
            f'--{ArgOptions.FILE}',
            help="Download PLAY file from a previous execution",
            metavar="<DL_FILE>"
        )

        # READ URLS FROM OS COPY/PASTE BUFFER
        dl_args.add_argument(
            self.get_shortcut(ArgOptions.BUFFER),
            f'--{ArgOptions.BUFFER}',
            help="Read list from copy/paste buffer",
            action='store_true'
        )

        # ALLOW DUPLICATES URLS ALREADY IN THE INVENTORY
        dl_args.add_argument(
            self.get_shortcut(ArgOptions.IGNORE_DUPS),
            f'--{ArgOptions.IGNORE_DUPS}',
            help="Allow duplicate DLs (DL even if DL'd previously)",
            action='store_true'
        )

    def _database(self) -> None:
        """
        Args associated with database management
        :param self: Automatically provided.
        :return: None.
        """

        db_args = self.subparsers.add_parser(
            ArgSubmodules.DATABASE, help="Options for database management")

        # Either SYNC or QUERY, not both (at the same time).
        db_mutex = db_args.add_mutually_exclusive_group()

        # DATABASE SYNC
        db_mutex.add_argument(
            self.get_shortcut(ArgOptions.SYNC),
            f'--{ArgOptions.SYNC}',
            help="Scan inventory and update DB based on findings.",
            action="store_true"
        )

        # RECORDS
        db_mutex.add_argument(
            self.get_shortcut(ArgOptions.RECORDS),
            f'--{ArgOptions.RECORDS}',
            help="Display database summary.",
            action='store_true'
        )

        # FILESPEC
        db_args.add_argument(
            self.get_shortcut(ArgOptions.FILE_SPEC),
            f'--{ArgOptions.FILE_SPEC}',
            help=("File spec to list information about images, requires "
                  "--records option and can be combined with --details."),
            metavar="<FILE SPEC>"
        )

        # DETAILS
        db_args.add_argument(
            self.get_shortcut(ArgOptions.DETAILS),
            f'--{ArgOptions.DETAILS}',
            help=("Display detailed summary of database contents or details of "
                  "selected <filespec>."),
            action='store_true'
        )

    def _duplicates(self) -> None:
        """
        Args associated with managing duplicate images
        :param self: Automatically provided.
        :return: None.
        """
        dup_args = self.subparsers.add_parser(
            ArgSubmodules.DUPLICATES,
            help="Options for managing duplicate images")

        # REMOVE DUPLICATES
        dup_args.add_argument(
            self.get_shortcut(ArgOptions.REMOVE_DUPS),
            f'--{ArgOptions.REMOVE_DUPS}',
            help="Remove duplicate for duplicate images",
            action='store_true',
        )

    def _image_info(self) -> None:
        """
        Args associated with querying info about a specific image
        :param self: Automatically provided.
        :return: None.
        """
        image_info_args = self.subparsers.add_parser(
            ArgSubmodules.INFO,
            help="Options for querying info about a specific image")

        # IMAGE QUERY
        image_info_args.add_argument(
            ArgOptions.IMAGE,
            help="Image Name to query",
            metavar="<IMAGE_NAME>")

    def _stats_(self) -> None:
        """
        Args associated with collection stats
        :param self: Automatically provided
        :return: None
        """
        stats_args = self.subparsers.add_parser(
            ArgSubmodules.STATS,
            help="Options for querying statistics about overall collection")

        # OVERALL SUMMARY
        stats_args.add_argument(
            self.get_shortcut(ArgOptions.SUMMARY),
            f'--{ArgOptions.SUMMARY}',
            help="Show Summary Statistics",
            action='store_true')

        # Either AUTHOR or DIRECTORY, not both (at the same time).
        stats_mutex = stats_args.add_mutually_exclusive_group()

        # BY AUTHOR
        stats_mutex.add_argument(
            self.get_shortcut(ArgOptions.AUTHOR),
            f'--{ArgOptions.AUTHOR}',
            help="Show Statistics Based on Author",
            action='store_true')

        # BY DIRECTORY
        stats_mutex.add_argument(
            self.get_shortcut(ArgOptions.DIRECTORY),
            f'--{ArgOptions.DIRECTORY}',
            help="Show Statistics Based on Directory",
            action='store_true')

    def get_args_str(self) -> str:
        """
        Returns concatenated string of configured arguments
        (primary purpose is debugging)
        :return: String of args
        """
        args = ''
        for arg, val in sorted(vars(self.args).items()):
            args += f"\t{arg}: {val}\n"

        LOG.debug(f"Command Line Args:\n{args}")
        return args

    def get_opt_args_states(self) -> str:
        """
        Build string for CLI Args flag states. (For logging to file)
        :return: Multi-line string of flag states

        """
        msg = '\nGLOBAL FLAGS:\n'
        option_keys = [ArgSubmodules.GENERAL, self.args.command]
        for key in option_keys:
            LOG.debug(f"OPTION KEY: {key}")
            LOG.debug(f"OPTIONS: {self.FLAGS[key]}")
            if key != ArgSubmodules.GENERAL:
                msg += f"\nMODULE: {key}\n"
            for flag in self.FLAGS[key]:
                if hasattr(self.args, flag):
                    setting = "ENABLED" if getattr(self.args, flag) else "DISABLED"
                    LOG.debug(f"Flag: {flag} --> {setting}")
                    msg += f"--> {flag} {setting} <<--\n"
        return msg


def test_routine():
    """
    To stop pylint from whining... moved __main__ code into a routine to be
    called by __main__()

    :return: None

    """
    parser = CLIArgs()
    LOG.debug(parser.args)
    LOG.info(f"Modules: {parser.get_module_names()}")
    parser.get_args_str()


# Used for visual checks like the help screen and namespaces
# (e.g.- things not easily validated though automation)
if __name__ == '__main__':  # pragma: no cover
    test_routine()
