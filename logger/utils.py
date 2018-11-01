import datetime
import os

import PDL.logger.logger as logger

DEFAULT_EXTENSION = 'log'
DELIMITER = '_'


log = logger.Logger()


def datestamp_filename(prefix=None, suffix=None, extension=DEFAULT_EXTENSION,
                       drive_letter=None, directory='.'):

    # TODO: Add docstring

    timestamp = datetime.datetime.now().strftime(r'%y%m%dT%H%M%S')
    filename = ''
    if prefix is not None:
        filename = "{prefix}{delim}".format(prefix=prefix, delim=DELIMITER)
    filename += timestamp
    if suffix is not None:
        filename = "{filename}{delim}{suffix}".format(
            filename=filename, suffix=suffix, delim=DELIMITER)
    filename += ".{ext}".format(ext=extension)

    log.debug("RAW LOG FILENAME: {0}".format(filename))

    if drive_letter is not None and drive_letter != '':
        directory = "{drive}:{directory}".format(
            drive=drive_letter, directory=directory)

    log.debug("DIRECTORY: {0}".format(directory))

    filename = os.path.sep.join([directory, filename])
    if drive_letter is None:
        filename = os.path.abspath(filename)

    log.debug("FINAL LOG FILENAME: {0}".format(filename))

    return filename
