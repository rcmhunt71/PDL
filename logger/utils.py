import datetime
import os

DEFAULT_EXTENSION = 'log'
DELIMITER = '_'


def datestamp_filename(prefix=None, suffix=None, extension=DEFAULT_EXTENSION,
                       base_dir='.'):

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

    filename = os.path.sep.join([base_dir, filename])

    return filename
