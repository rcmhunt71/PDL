import argparse
import pprint

# Argparse docs: https://docs.python.org/3/library/argparse.html

from PDL.logger.logger import Logger as PDL_log

log = PDL_log()


class ArgSubmodules(object):
    """
    Defined submodules for the application
    """
    DOWNLOAD = 'dl'
    DUPLICATES = 'dups'
    INFO = 'info'
    DATABASE = 'db'

    @classmethod
    def _get_const_values(cls):
        return [val for key, val in cls.__dict__.items()
                if not key.startswith('_')]

    @classmethod
    def _get_const_names(cls):
        return [key for key, val in cls.__dict__.items()
                if not key.startswith('_')]


class ArgOptions(object):
    """
    Defined constants for sub-options available via the CLI across all
    sub-modules.
    """

    CFG = 'cfg'
    COMMAND = 'command'
    DRY_RUN = 'dryrun'
    DEBUG = 'debug'
    DETAILS = 'details'
    FILE = 'file'
    FILE_SPEC = 'filespec'
    IMAGE = 'image'
    RECORDS = 'records'
    SYNC = 'sync'
    REMOVE_DUPS = 'remove_dups'
    URLS = 'urls'

    SHORTCUTS = {
        CFG: "c",
        DEBUG: "d",
        DETAILS: "d",
        DRY_RUN: "r",
        FILE: "f",
        FILE_SPEC: "f",
        RECORDS: "r",
        REMOVE_DUPS: "x",
        SYNC: "s",
    }


class CLIArgs(object):
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
    FLAGS = ['debug']

    def __init__(self, test_args_list=None):
        self.parser = argparse.ArgumentParser(description=self.PURPOSE)
        self.subparsers = self.parser.add_subparsers(dest=ArgOptions.COMMAND)

        self._define_standard_args()
        self._downloads()
        self._database()
        self._duplicates()
        self._image_info()

        self.args = self.parse_args(test_args_list)

    @staticmethod
    def get_module_names():
        """
        Lists all of the submodules available as part of the application
        :return: List of strings (names of the submodules)

        """
        modules = ArgSubmodules._get_const_values()
        log.debug("Request for module names: {0}".format(
            pprint.pformat(modules)))
        return modules

    @staticmethod
    def get_shortcut(option):
        """
        Gets the single letter representation of the option
        :param option: Name of the option
        :return: character used on the CLI to represent the option.

        """
        if option in ArgOptions.SHORTCUTS.keys():
            return "-{0}".format(ArgOptions.SHORTCUTS[option])
        log.error('No shortcut registered for "{0}".'.format(option))
        return None

    def parse_args(self, test_args_list=None):
        """
        Parses CLI, but allows injection of arguments for testing purposes
        :param test_args_list:
        :return:

        """
        log.debug("Parsing command line args.")
        if test_args_list is not None:
            log.debug(
                "Args passed in for testing:\n\t{0}".format(test_args_list))
        return (self.parser.parse_args() if test_args_list is None else
                self.parser.parse_args(test_args_list))

    def _define_standard_args(self):
        """
        Standard Args (not specific to any given action)
        :param self: Automatically provided.
        :return: None.
        """

        # GLOBAL DEBUG FLAG
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.DEBUG),
            '--{0}'.format(ArgOptions.DEBUG),
            help="Enable debug flag for logging and reporting",
            action='store_true')

        # DRY RUN
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.DRY_RUN),
            '--{0}'.format(ArgOptions.DRY_RUN),
            help="Enable flag for dry-run. See what happens without taking action",
            action='store_true')

        # CFG FILE
        self.parser.add_argument(
            self.get_shortcut(ArgOptions.CFG),
            '-c', '--{0}'.format(ArgOptions.CFG),
            help="Specify configuration file")

    def _downloads(self):
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
            '--{0}'.format(ArgOptions.FILE),
            help="Download PLAY file from a previous execution",
            metavar="<DL_FILE>"
        )

    def _database(self):
        """
        Args associated with database management
        :param self: Automatically provided.
        :return: None.
        """

        db_args = self.subparsers.add_parser(
            ArgSubmodules.DATABASE, help="Options for database management")

        # Either SYNC or QUERY, not both (at the same time).
        mutex = db_args.add_mutually_exclusive_group()

        # DATABASE SYNC
        mutex.add_argument(
            self.get_shortcut(ArgOptions.SYNC),
            '--{0}'.format(ArgOptions.SYNC),
            help="Scan inventory and update DB based on findings.",
            action="store_true"
        )

        # RECORDS
        mutex.add_argument(
            self.get_shortcut(ArgOptions.RECORDS),
            '--{0}'.format(ArgOptions.RECORDS),
            help="Display database summary.",
            action='store_true'
        )

        # FILESPEC
        db_args.add_argument(
            self.get_shortcut(ArgOptions.FILE_SPEC),
            '--{0}'.format(ArgOptions.FILE_SPEC),
            help=("File spec to list information about images, requires "
                  "--records option and can be combined with --details."),
            metavar="<FILE SPEC>"
        )

        # DETAILS
        db_args.add_argument(
            self.get_shortcut(ArgOptions.DETAILS),
            '--{0}'.format(ArgOptions.DETAILS),
            help=("Display detailed summary of database contents or details of "
                  "selected <filespec>."),
            action='store_true'
        )

    def _duplicates(self):
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
            '--{0}'.format(ArgOptions.REMOVE_DUPS),
            help="Remove duplicate for duplicate images",
            action='store_true',
        )

    def _image_info(self):
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

    def get_args_str(self):
        """
        Returns concatenated string of configured arguments
        (primary purpose is debugging)
        :return: String of args
        """
        args = ''
        for arg, val in sorted(vars(self.args).items()):
            args += "\t{arg}: {value}\n".format(arg=arg, value=val)

        log.debug("Command Line Args:\n{args}".format(args=args))
        return args

    def get_opt_args_states(self):
        """
        Build string for CLI Args flag states. (For logging to file)
        :return: Multi-line string of flag states

        """
        msg = '\n'
        for flag in self.FLAGS:
            if getattr(self.args, flag):
                msg += "--> {0} ENABLED <<--\n".format(flag)
        return msg


# Used for visual checks like the help screen and namespaces
# (e.g.- things not easily validated though automation)
if __name__ == '__main__':
    filename = 'args.test.log'
    # log = PDL_log(filename=filename)
    parser = CLIArgs()
    log.debug(parser.args)
    log.info("Modules: {0}".format(parser.get_module_names()))
    parser.get_args_str()
