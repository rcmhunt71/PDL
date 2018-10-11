import inspect
import logging
import os


class Logger(object):

    DEFAULT_PROJECT = 'PDL'
    DEFAULT_LOG_LEVEL = logging.DEBUG

    LOG_FORMAT = (r'[%(asctime)-15s][%(levelname)-5s][%(pid)s]'
                  r'[%(file_name)s:%(routine)s:%(linenum)d] - %(message)s')
    DATE_FORMAT = r'%m%d%y-%T'

    DEFAULT_DEPTH = 3

    def __init__(
            self, filename=None, default_level=None, added_depth=0,
            project=None):

        self.filename = filename
        self.loglevel = default_level or self.DEFAULT_LOG_LEVEL
        self.depth = self.DEFAULT_DEPTH + int(added_depth)
        self.project = project or self.DEFAULT_PROJECT
        self.logger = None
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

        name = self._get_module_name() if __name__ != '__main__' else 'root'

        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.loglevel)

    def _get_module_name(self):
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


# FOR TESTING PURPOSES
if __name__ == '__main__':

    def test_routine(logger, level, msg):
        test_log = getattr(logger, level.lower())
        test_log(msg)

    def test_logging():
        test_routine(log, 'info', 'TEST')
        test_routine(log, 'debug', 'TEST2')

    log = Logger(default_level=logging.DEBUG, added_depth=1, filename="logger_test.log")
    test_logging()
