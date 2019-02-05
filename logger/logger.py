import inspect
import logging
import os

import prettytable


# TODO: <DOC> Add README.md to directory


class Logger(object):
    """
    Creates a logging facility that can be used by any module.
    Import the loggeer and instantiate in module:

    log = Logger()

    In the main application, instantiate the logger, but
    set `set_root` to True. This will reset all of the loggers to
    the correct level, and set the destination file. (Since they were
    instantiated when the module was loaded, additional updates
    are not applied.

    By setting `set_root` to True:
    * it removes and stores the handlers
    * updates the root logger with the desired level and target files
    * reapplies the handlers to the root, which will cause the handlers
        to adopt the updated root logger properties.

    """

    # Enables print statements for issues like double registration of loggers
    DEBUG_MODULE = False

    DEFAULT_PROJECT = 'PDL'

    # Quick macros for convenience
    INFO = logging.INFO
    WARN = logging.WARN
    FATAL = logging.FATAL
    DEBUG = logging.DEBUG
    ERROR = logging.ERROR

    DEFAULT_LOG_LEVEL = INFO

    STR_TO_VAL = {'fatal': FATAL,
                  'warn': WARN,
                  'error': ERROR,
                  'info': INFO,
                  'debug': DEBUG}

    # Reverse lookups: logging.LEVEL are integers, and this creates
    # a quick lookup: given a value, what is the corresponding string
    # e.g. = 40 --> INFO
    VAL_TO_STR = dict([(value, text) for text, value in STR_TO_VAL.items()])

    # Logging statement format
    LOG_FORMAT = (r'[%(asctime)-15s][%(pid)s][%(levelname)-5s]'
                  r'[%(file_name)s:%(routine)s|%(linenum)d] - %(message)s')
    DATE_FORMAT = r'%m%d%y-%T'

    # Depth: Actual stack level calling log (there are two additional levels
    # within the logging module that if referenced, would always be reported
    # as the calling routine = not helpful.)
    DEFAULT_STACK_DEPTH = 3
    ROOT_LOGGER = 'root'

    def __init__(
            self, filename: str = None, default_level: str = None, added_depth: int = 0,
            project: str = None, set_root : bool = False, test_name: str = None) -> None:
        """
        :param filename: Filename to write logs to...
        :param default_level: Default stack level (default = DEFAULT_STACK_DEPTH)
        :param added_depth: Added_depth - in case a different stack level is required
                   (not commonly used)
        :param project: Name of project
        :param set_root: Boolean (set root, see class description for information)
        :param test_name: Used for testing... allows setting of specific name
                    in log preamable for validation

        """
        self.filename = filename
        self.loglevel = default_level or self.DEFAULT_LOG_LEVEL
        self.depth = self.DEFAULT_STACK_DEPTH + int(added_depth)
        self.project = project or self.DEFAULT_PROJECT
        self.logger = None
        self.name = test_name
        self.root = set_root

        # Need to clear the existing loggers if building the root logger and then
        # re-add the handlers after updating the root logger config.
        # Reason: Updating the config with handlers attached is a 'no-op'
        if self.root:

            # Store (copy) the list of handlers associated with the root handler
            handlers = logging.root.handlers[:]

            # Remove the handlers from the root
            for handler in handlers:
                logging.root.removeHandler(handler)

            # Initialize the root handler
            self._start_logger()

            # Re-associate the handlers to the root handler
            for handler in handlers:
                logging.root.addHandler(handler)

        else:
            # Start the logger for the given module.
            self._start_logger()

    def _start_logger(self) -> None:
        """
        Define the logger for the current context.
          + Set the default logging level
          + Set the format
          + Set the filename, as needed.

        :return: None

        """
        default_config = {
            'level': self.loglevel,
            'format': self.LOG_FORMAT,
            'datefmt': self.DATE_FORMAT,
        }

        if self.filename is not None:
            default_config['filename'] = self.filename
        logging.basicConfig(**default_config)

        # Set the name if it is not defined
        if self.name is None:
            self.name = (
                self._get_module_name() if __name__ != '__main__' else
                self.ROOT_LOGGER)

        if self.root:
            self.name = self.ROOT_LOGGER

        # If no filename is specified, add the console as the logger
        if self.filename is not None:
            self._add_console()

        root_log = logging.getLogger()

        # Get the correct child logger
        if self.name != self.ROOT_LOGGER:
            if self.DEBUG_MODULE:
                print(f"Child Logger: {self.name}")
            self.logger = root_log.getChild(self.name)

        # Get the root logger
        else:
            if self.DEBUG_MODULE:
                print(f"Root: {self.name}")
            self.logger = root_log
            self.logger.setLevel(self.loglevel)

    def _add_console(self) -> None:
        """
        Enables a stream handler for logging to the console (STDOUT).
        This is used when a log file is specified, because all log output is
        directed to the file.

        :return: None
        """
        console = logging.StreamHandler()
        console.setLevel(self.loglevel)
        console.setFormatter(logging.Formatter(self.LOG_FORMAT))
        logging.getLogger(self.ROOT_LOGGER).addHandler(console)

    def _get_module_name(self) -> str:
        """
        Gets stack information, determines package, and creates dotted path

        :return: string - dotted path lib
        """
        frame_info = inspect.stack()[self.depth]
        filename = os.path.abspath(frame_info[1]).split(
            f'{self.project}{os.path.sep}')[-1]

        return self._translate_to_dotted_lib_path(filename)

    def _log_level(self, level: str, msg: str, prefix: str = '') -> None:
        """
        Determine and use the proper logging level (abstracted to expose logging
        routines at class level; also reduces the dotted path when invoking in
        code.

        :param level: logging.LEVEL
        :param msg: message to log
        :param prefix: If preamble needs an additional internal prefix.

        :return: None
        """
        log_routine = getattr(self.logger, level.lower())
        log_routine(str(prefix) + str(msg), extra=self._method())

    def _list_loggers(self) -> list:
        """
        Lists all child loggers defined under the root logger, and effective
        logging levels
        :param: None
        :return: List of tuples (logger instance name, log_level (int))

        """
        logger_info = [self._get_logger_info(self.ROOT_LOGGER)]

        for logger_name in sorted(logging.getLogger().manager.loggerDict.keys()):
            if logger_name != self.ROOT_LOGGER:
                logger_info.append(self._get_logger_info(logger_name))
        return logger_info

    def list_loggers(self) -> str:
        """
        Lists all loggers (root + children) and their corresponding log level

        :return: str table representation of loggers, starting with root, and
        alphabetically listing children.

        """
        child = "CHILD LOGGER"
        level = 'LOG LEVEL'

        # Define table format
        table = prettytable.PrettyTable()
        table.field_names = [child, level]
        table.align[child] = 'l'
        table.align[level] = 'c'

        # Populate Table
        for data in self._list_loggers():
            table.add_row(data)
        return table.get_string(title='Loggers')

    def _get_logger_info(self, name: str) -> list:
        """
        Gets the effective log level for the given name
        :param name: Name of the logging facility/child
        :return: list (logger_name, logging_level)

        """
        child = logging.getLogger().getChild(name)
        return [name, self.VAL_TO_STR[child.getEffectiveLevel()].upper()]

    @staticmethod
    def _translate_to_dotted_lib_path(path: str) -> str:
        """
        Create a python import path from a filesystem path by replacing the '/' (os.path.sep) with '.'
        :param path: path of module

        :return: (str) dotted module path

        """
        return str(path.split('.')[0]).replace(os.path.sep, ".")

    def _method(self) -> dict:
        """
        Get calling frame's basic info
        + File name relative to project name
        + Calling linenum
        + Calling routine
        + Process pid

        :return: Dictionary of values listed above.

        """
        frame_info = inspect.stack()[self.depth]
        filename = str(os.path.abspath(frame_info[1]).split(
            '{0}{1}'.format(self.project, os.path.sep))[-1])

        return {'file_name': self._translate_to_dotted_lib_path(path=filename),
                'linenum': frame_info[2],
                'routine': frame_info[3],
                'pid': os.getpid()}

    # Quick class level references to logger methods.
    # ------------------------------------------------------------------
    # ==> Simplification from obj.log.log_level() to obj.log_level()
    # ------------------------------------------------------------------

    def fatal(self, msg: str) -> None:
        self._log_level(level='FATAL', msg=msg)

    def error(self, msg: str) -> None:
        self._log_level(level='ERROR', msg=msg)

    def warn(self, msg: str) -> None:
        self._log_level(level='WARN', msg=msg)

    def info(self, msg: str) -> None:
        self._log_level(level='INFO', msg=msg)

    def debug(self, msg: str) -> None:
        self._log_level(level='DEBUG', msg=msg)

    def exception(self, msg: str) -> None:
        self._log_level(level='EXCEPTION', msg=msg)


# FOR VISUAL/MANUAL TESTING PURPOSES
#   - Need to be executed explicitly.
#   - pragma = not monitored by coverage tool

if __name__ == '__main__':  # pragma: no cover

    def test_routine(logger: logging.Logger, level: str, msg: str) -> None:
        test_log = getattr(logger, level.lower())
        test_log(msg)

    def test_logging() -> None:
        test_routine(log, 'info', 'TEST')
        test_routine(log, 'debug', 'TEST2')

    log = Logger(default_level=logging.DEBUG,
                 filename="logger_test.log",
                 set_root=True,
                 added_depth=1)
    test_logging()
