import datetime
import os

import PDL.logger.logger as logger

DEFAULT_EXTENSION = 'log'
DELIMITER = '_'
TIMESTAMP = r'%y%m%dT%H%M%S'

log = logger.Logger()


def datestamp_filename(prefix=None, suffix=None, extension=DEFAULT_EXTENSION,
                       drive_letter=None, directory='.',
                       timestamp_format=TIMESTAMP):

    """
    Creates the full path and filename to the log file. Implemented to support
    both Windows and *nix style directory structures (Windows = drive letter)

    FORMAT: <prefix>_<timestamp>

    :param prefix: (str) - A custom prefix to add to the filename
    :param suffix: (str) - A custom suffix to add to the filename
    :param extension: (str) - Extension for the log file (default = .log)
    :param drive_letter: (char) - A character representing the drive letter
                                 (for windows only)
    :param directory: (str) - Directory path to log directory.
    :param timestamp_format: (str) - format of timestamp.
                      See datetime.strftime() formats for acceptable directives.

    :return: (str) - Fully qualified absolute path to the log file.

    """

    filename = ''

    # Build timestamp string
    timestamp = datetime.datetime.now().strftime(timestamp_format)

    # Create prefix
    if prefix is not None:
        filename = "{prefix}{delim}".format(prefix=prefix, delim=DELIMITER)

    filename += timestamp

    # Add suffix
    if suffix is not None:
        filename = "{filename}{delim}{suffix}".format(
            filename=filename, suffix=suffix, delim=DELIMITER)

    # Add extension
    filename += ".{ext}".format(ext=extension)

    log.debug("RAW LOG FILENAME: {0}".format(filename))

    # Build drive specification (if drive letter is provided)
    if drive_letter is not None and drive_letter != '':
        directory = "{drive}:{directory}".format(
            drive=drive_letter, directory=directory)

    log.debug("DIRECTORY: {0}".format(directory))

    # Join the path and filename
    filename = os.path.sep.join([directory, filename])

    # Create absolute path using filespec
    if drive_letter is None:
        filename = os.path.abspath(filename)

    log.debug("FINAL LOG FILENAME: {0}".format(filename))

    return filename
