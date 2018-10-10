import inspect
import logging
import os


class Logger(object):

    LOG_FORMAT = (r'[%(asctime)-15s][%(levelname)-5s][%(uuid)s][%(name)s]'
                  r'[%(file_name)s:%(routine)s:%(linenum)d] - %(message)s')
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

    def _log_level(self, level, msg, prefix='', uuid=None):
        log_routine = getattr(self.logger, level.lower())
        log_routine(str(prefix) + str(msg), extra=self._method(uuid=uuid))

    def _method(self, uuid=None):
        frame_info = inspect.stack()[self.depth]

        uuid = uuid or 'UUID:not_set'

        return {'file_name': frame_info[1],
                'linenum': frame_info[2],
                'routine': frame_info[3],
                'uuid': uuid}

    def fatal(self, msg, uuid=None):
        self._log_level(level='FATAL', msg=msg, uuid=uuid)

    def error(self, msg, uuid=None):
        self._log_level(level='ERROR', msg=msg, uuid=uuid)

    def warn(self, msg, uuid=None):
        self._log_level(level='WARN', msg=msg, uuid=uuid)

    def info(self, msg, uuid=None):
        self._log_level(level='INFO', msg=msg, uuid=uuid)

    def debug(self, msg, uuid=None):
        self._log_level(level='DEBUG', msg=msg, uuid=uuid)


if __name__ == '__main__':

    import uuid

    def test_routine(logger, level, msg, uuid=None):
        testlog = getattr(logger, level.lower())
        testlog(msg, uuid=uuid)

    def wooba():
        test_routine(log, 'info', 'TEST', str(uuid.uuid4()).split('-')[-1])
        test_routine(log, 'debug', 'TEST2', str(uuid.uuid4()).split('-')[-1])

    log = Logger(default_level=logging.DEBUG, added_depth=1)
    wooba()
