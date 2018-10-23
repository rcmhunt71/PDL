import datetime


DEFAULT_EXTENSION = 'log'
DELIMITER = '_'


def datestamp_filename(prefix=None, suffix=None, extension=DEFAULT_EXTENSION):
    timestamp = datetime.datetime.now().strftime(r'%y%m%dT%H%M%S')
    filename = ''
    if prefix is not None:
        filename = "{prefix}{delim}".format(prefix=prefix, delim=DELIMITER)
    filename += timestamp
    if suffix is not None:
        filename = "{filename}{delim}{suffix}".format(
            filename=filename, suffix=suffix, delim=DELIMITER)
    filename += ".{ext}".format(ext=extension)
    return filename


if __name__ == '__main__':
    datestamp_filename(suffix="image_download")
