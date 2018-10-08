import inspect
import logging
import os


class Logger(object):

    LOG_FORMAT = r'[%(asctime)-15s] [%(levelname)-5s] [%(name)s] [%(file_name)s:%(routine)s:%(linenum)d] - %(message)s'
    DATE_FORMAT = r'%m%d%y-%T'

    DEFAULT_DEPTH = 3

    def __init__(self, filename=None, default_level=logging.INFO, added_depth=0):
        self.filename = filename
        self.loglevel = default_level
        self.depth = self.DEFAULT_DEPTH + int(added_depth)

        self.logger = None
        self._start_logger()

    def _start_logger(self):
        default_config = {
            'level': self.loglevel,
            'format': self.LOG_FORMAT,
            'datefmt': self.DATE_FORMAT,
        }

        if self.filename is not None:
            default_config['filename'] = self.filename

        logging.basicConfig(**default_config)

        name = __name__ if __name__ != '__main__' else 'root'
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.loglevel)

    def _log_level(self, level, msg, prefix=''):
        log_routine = getattr(self.logger, level.lower())
        log_routine(str(prefix) + str(msg), extra=self._method())

    def _method(self):
        frame_info = inspect.stack()[self.depth]

        return {'file_name': frame_info[1],
                'linenum': frame_info[2],
                'routine': frame_info[3]}

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


if __name__ == '__main__':

    def test_routine(logger, level, msg):
        testlog = getattr(logger, level.lower())
        testlog(msg)

    def wooba():
        test_routine(log, 'info', 'TEST')
        test_routine(log, 'debug', 'TEST2')

    log = Logger(default_level=logging.DEBUG, added_depth=1)
    wooba()
