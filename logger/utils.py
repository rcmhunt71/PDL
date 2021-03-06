"""
   Generic routines for used for logging
   * Timestamp_filename building - used for naming logs and time-specific data files.
   * Check if location exists, if not, give chance to create it.
          (Used by logging when logging to file)
"""

import datetime
import glob
import os
from typing import Optional

import PDL.logger.logger as logger

DEFAULT_EXTENSION = 'log'      # Used for finding log files
DELIMITER = '_'                # Delimiter for file naming convention
TIMESTAMP = r'%y%m%dT%H%M%S'   # Timestamp: YYYYMMDDThhmmss

LOG = logger.Logger()


def datestamp_filename(prefix: Optional[str] = None, suffix: Optional[str] = None,
                       extension: str = DEFAULT_EXTENSION, drive_letter: Optional[str] = None,
                       directory: str = '.', timestamp_format: str = TIMESTAMP,
                       log_level: str = 'INFO') -> str:

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
    :param log_level: (str) - added to filename to indicate level of output.

    :return: (str) - Fully qualified absolute path to the log file.

    """

    filename = ''

    # Build timestamp string
    timestamp = datetime.datetime.now().strftime(timestamp_format)

    # Create prefix
    if prefix is not None:
        filename = f"{prefix}{DELIMITER}"

    # Add timestamp
    filename += timestamp

    # Add suffix
    if suffix is not None:
        filename = f"{filename}{DELIMITER}{suffix}"

    # Add extension
    filename += f"{DELIMITER}{log_level.upper()}.{extension}"

    LOG.debug(f"RAW LOG FILENAME: {filename}")

    # Build drive specification (if drive letter is provided)
    if drive_letter is not None and drive_letter != '':
        directory = f"{drive_letter}:{directory}"

    LOG.debug(f"DIRECTORY: {directory}")

    # Join the path and filename
    filename = os.path.sep.join([directory, filename])

    # Create absolute path using filespec
    if drive_letter is None:
        filename = os.path.abspath(filename)

    LOG.debug(f"FINAL LOG FILENAME: {filename}")

    return filename


def check_if_location_exists(location: str, create_dir: bool = False) -> bool:
    """
    If the save_url directory path does not exist... Create target
    directory & all intermediate directories if 'create_dir' is True

    :param location: (str) directory path
    :param create_dir: (bool) - Create path if it does not exist, DEFAULT=False

    :return: (bool) Does path exist (or was it created, if requested)

    """
    # If the path does not exist...
    if not os.path.exists(location):
        if create_dir:
            try:
                os.makedirs(location)

            # Unexpected exception
            except Exception as exc:
                result = False
                LOG.exception(exc)

            # Directories created
            else:
                result = True
                LOG.debug(f"Created URL save directory: '{location}'")

        # Path does not exist, but not asked to create it.
        else:
            result = False
            msg = (f"URL save file directory does not exist "
                   f"('{location}'), and was not configured "
                   f"to create dir.")
            LOG.error(msg)

    # Path exists
    else:
        result = True
        LOG.debug(f"URL save file directory exists ('{location}')")

    return result


def num_file_of_type(directory: str, file_type: str) -> int:
    """
    Provide the number of files of type "file_type" in "directory".

    :param directory: directory to check
    :param file_type: file extension to count

    :return: number of files of type "file_type"

    """
    count = 0

    # If path exists, count the number of files matching the file type.
    if os.path.exists(directory):
        files = glob.glob(os.path.sep.join([directory, f'*.{file_type}']), recursive=False)
        count = len(files)

    # Otherwise... sorry Houston, the mission is a no-go.
    else:
        LOG.warn(f"Directory '{directory}' does not exist. Unable to "
                 f"tally files of type '{file_type}'.")

    return count
