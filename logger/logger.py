import inspect
import logging
import os

# TODO: <DOC> Add README.md to directory


class Logger(object):

    DEFAULT_PROJECT = 'PDL'

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

    VAL_TO_STR = dict([(value, text) for text, value in STR_TO_VAL.items()])

    LOG_FORMAT = (r'[%(asctime)-15s][%(pid)s][%(levelname)-5s]'
                  r'[%(file_name)s:%(routine)s|%(linenum)d] - %(message)s')
    DATE_FORMAT = r'%m%d%y-%T'

    DEFAULT_STACK_DEPTH = 3
    ROOT_LOGGER = 'root'

    def __init__(
            self, filename=None, default_level=None, added_depth=0,
            project=None, set_root=False, test_name=None):

        self.filename = filename
        self.loglevel = default_level or self.DEFAULT_LOG_LEVEL
        self.depth = self.DEFAULT_STACK_DEPTH + int(added_depth)
        self.project = project or self.DEFAULT_PROJECT
        self.logger = None
        self.name = test_name
        self.root = set_root

        self._start_logger()

    def _start_logger(self):
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

        if self.name is None:
            self.name = (
                self._get_module_name() if __name__ != '__main__' else
                self.ROOT_LOGGER)

        if self.root:
            self.name = self.ROOT_LOGGER

        if self.filename is not None:
            self._add_console()

        root_log = logging.getLogger()
        if self.name != self.ROOT_LOGGER:
            self.logger = root_log.getChild(self.name)
        else:
            self.logger = root_log
            self.logger.setLevel(self.loglevel)

    def _add_console(self):
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

    def _get_module_name(self):
        """
        Gets stack information, determines package, and creates dotted path

        :return: string - dotted path lib
        """
        frame_info = inspect.stack()[self.depth]
        filename = os.path.abspath(frame_info[1]).split(
            '{0}{1}'.format(self.project, os.path.sep))[-1]

        return self._translate_to_dotted_lib_path(filename)

    def _log_level(self, level, msg, prefix=''):
        """
        Determine and use the proper logging level (abstracted to expose logging
        routines at class level; also reduces the dotted path when invoking in
        code.

        :param level: logging.LEVEL (or corresponding integer value)
        :param msg: message to log
        :param prefix: If preamble needs an additional internal prefix.

        :return: None
        """
        log_routine = getattr(self.logger, level.lower())
        log_routine(str(prefix) + str(msg), extra=self._method())

    def _list_loggers(self):
        """
        Lists all child loggers defined under the root logger, and effective
        logging levels
        :param: None
        :return: List of tuples (logger instance name, log_level (int))

        """
        logger_info = [self._get_logger_info('root')]

        for logger_name in sorted(logging.getLogger().manager.loggerDict.keys()):
            if logger_name != 'root':
                logger_info.append(self._get_logger_info(logger_name))
        return logger_info

    def list_loggers(self):
        """
        Lists all loggers (root + children) and their corresponding log level

        :return: str table representation of loggers, starting with root, and
        alphabetically listing children.

        """

        # Define table format
        border = "+{0}+{1}+\n".format('-' * 42, '-' * 12)
        table_row = "| {0:<40} | {1:^10} |\n"

        # Create Header
        table = "\n{0}".format(border)
        table += table_row.format("CHILD LOGGER", "LOG LEVEL")
        table += border

        # Populate Table
        for data in self._list_loggers():
            table += table_row.format(*data)

        # Close Table
        table += border

        return table

    def _get_logger_info(self, name):
        """
        Gets the effective log level for the given name
        :param name: Name of the logging facility/child
        :return: list (logger_name, logging_level)

        """
        child = logging.getLogger().getChild(name)
        return [name, self.VAL_TO_STR[child.getEffectiveLevel()].upper()]

    @staticmethod
    def _translate_to_dotted_lib_path(path):
        return str(path.split('.')[0]).replace(os.path.sep, ".")

    def _method(self):
        """
        Get calling frame's basic info
        + File name relative to project name
        + Calling linenum
        + Calling routine
        + Process pid

        :return: Dictionary of values listed above.

        """
        frame_info = inspect.stack()[self.depth]
        filename = os.path.abspath(frame_info[1]).split(
            '{0}{1}'.format(self.project, os.path.sep))[-1]

        return {'file_name': self._translate_to_dotted_lib_path(path=filename),
                'linenum': frame_info[2],
                'routine': frame_info[3],
                'pid': os.getpid()}

    def fatal(self, msg):
        self._log_level(level='FATAL', msg=msg)

    def error(self, msg):
        self._log_level(level='ERROR', msg=msg)

    def warn(self, msg):
        self._log_level(level='WARN', msg=msg)

    def info(self, msg):
        self._log_level(level='INFO', msg=msg)

    def debug(self, msg):
        self._log_level(level='DEBUG', msg=msg)

    def exception(self, msg):
        self._log_level(level='EXCEPTION', msg=msg)


# FOR VISUAL/MANUAL TESTING PURPOSES
if __name__ == '__main__':  # pragma: no cover

    def test_routine(logger, level, msg):
        test_log = getattr(logger, level.lower())
        test_log(msg)

    def test_logging():
        test_routine(log, 'info', 'TEST')
        test_routine(log, 'debug', 'TEST2')

    log = Logger(default_level=logging.DEBUG,
                 filename="logger_test.log",
                 set_root=True,
                 added_depth=1)
    test_logging()
