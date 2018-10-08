import logging


class Logger(object):

    LOG_FORMAT = r'%(asctime)s: %(name)s:%(module)s:%(funcName)s:%(lineno)d: %(levelname)s - %(message)s'
    DATE_FORMAT = r'%m%d%y-%T'

    def __init__(self, filename=None, default_level=logging.INFO):
        self.filename = filename
        self.loglevel = default_level

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

    def info(self, msg):
        self.logger.info(msg)


if __name__ == '__main__':
    log = Logger(default_level=logging.INFO)
    log.info('TEST')
