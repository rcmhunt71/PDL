import argparse
import pprint

# Argparse docs: https://docs.python.org/3/library/argparse.html

from PDL.logger.logger import Logger as PDL_log

log = PDL_log()


class ArgSubmodules(object):
    DOWNLOAD = 'dl'
    INVENTORY = 'inv'
    DUPLICATES = 'dups'
    INFO = 'info'

    @classmethod
    def _get_const_values(cls):
        return [val for key, val in cls.__dict__.items()
                if not key.startswith('_')]

    @classmethod
    def _get_const_names(cls):
        return [key for key, val in cls.__dict__.items()
                if not key.startswith('_')]


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
        self.subparsers = self.parser.add_subparsers(dest='command')

        self._define_standard_args()
        self._downloads()
        self._duplicates()
        self._inventory()
        self._image_info()

        self.args = self.parse_args(test_args_list)

    @staticmethod
    def get_module_names():
        modules = ArgSubmodules._get_const_values()
        log.debug("Request for module names: {0}".format(
            pprint.pformat(modules)))
        return modules

    def parse_args(self, test_args_list=None):
        """
        Parses CLI, but allows injection of arguments for testing purposes
        :param test_args_list:
        :return:
        """

        log.debug("Parsing command line args.")
        return (self.parser.parse_args() if test_args_list is None else
                self.parser.parse_args(test_args_list))

    def _define_standard_args(self):
        """
        Standard Args (not specific to any given action)
        :param self: Automatically provided.
        :return: None.
        """
        self.parser.add_argument(
            '-d', '--debug', help="Enable debug flag for logging and reporting",
            action='store_true')

        self.parser.add_argument(
            '-r', '--dryrun', help="Enable flag for dry-run. See what happens without taking action",
            action='store_true')

        self.parser.add_argument(
            '-c', '--cfg', help="Specify configuration file")

    def _downloads(self):
        """
        Args associated with downloading images
        :param self: Automatically provided.
        :return: None.
        """
        dl_args = self.subparsers.add_parser(
            ArgSubmodules.DOWNLOAD, help="Options for downloading images")

        dl_args.add_argument(
            'urls', nargs=argparse.REMAINDER, metavar="<URLS>",
            help=("List of URLs to parse and download, should be last argument "
                  "on the CLI")
        )

        dl_args.add_argument(
            '-f', '--file', metavar="<DL_FILE>",
            help="Download PLAY file from a previous execution"
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

        dup_args.add_argument(
            '-x', '--remove_dups', action='store_true',
            help="Remove duplicate for duplicate images"
        )

    def _inventory(self):
        """
        Args associated with querying the image inventory.
        :param self: Automatically provided.
        :return: None.
        """
        inv_args = self.subparsers.add_parser(
            ArgSubmodules.INVENTORY,
            help="Options for managing reporting inventory")

        inv_args.add_argument(
            'filespec', metavar="<FILE SPEC>",
            help="File spec to list information about images")

        inv_args.add_argument(
            '-d', '--detailed', action="store_true",
            help="Detailed summary of inventory file spec."
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

        image_info_args.add_argument(
            'image', metavar="<IMAGE_NAME>", help="Image Name to query")

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
    parser = CLIArgs()
    log.debug(parser.args)
    log.info("Modules: {0}".format(parser.get_module_names()))
    parser.get_args_str()

