from mock import patch
import os
import re

from PDL.logger.utils import (
    datestamp_filename, DEFAULT_EXTENSION, DELIMITER, check_if_location_exists)
from nose.tools import assert_equals, assert_is_not_none


class TestLogUtils(object):

    TIMESTAMP_FORMAT = r'[0-9]{6}T[0-9]{6}'
    EXPECTED_PREFIX = 'myPrefix'
    EXPECTED_SUFFIX = 'mySuffix'
    LOG_LEVEL = 'INFO'
    NON_DEFAULT_EXT = 'txt'
    DEFAULT_LOG_DIR = '.'

    def test_if_filename_is_timestamp(self):
        filename = datestamp_filename()
        self._validate_filename(filename=filename)

    def test_if_filename_has_non_default_extension(self):
        filename = datestamp_filename(extension=self.NON_DEFAULT_EXT)
        self._validate_filename(filename=filename,
                                extension=self.NON_DEFAULT_EXT)

    def test_if_filename_is_timestamp_with_prefix(self):
        filename = datestamp_filename(prefix=self.EXPECTED_PREFIX)
        self._validate_filename(filename=filename,
                                prefix=self.EXPECTED_PREFIX,
                                extension=DEFAULT_EXTENSION)

    def test_if_filename_is_timestamp_with_suffix(self):
        filename = datestamp_filename(suffix=self.EXPECTED_SUFFIX)
        self._validate_filename(filename=filename,
                                suffix=self.EXPECTED_SUFFIX,
                                extension=DEFAULT_EXTENSION)

    def test_if_filename_is_timestamp_with_prefix_and_suffix(self):
        filename = datestamp_filename(prefix=self.EXPECTED_PREFIX,
                                      suffix=self.EXPECTED_SUFFIX)

        self._validate_filename(filename=filename,
                                prefix=self.EXPECTED_PREFIX,
                                suffix=self.EXPECTED_SUFFIX,
                                extension=DEFAULT_EXTENSION)

    def test_if_filename_path_is_attached_correctly(self):

        log_path = "/this/is/a/test"

        filename = datestamp_filename(prefix=self.EXPECTED_PREFIX,
                                      suffix=self.EXPECTED_SUFFIX,
                                      directory=log_path)

        self._validate_filename(filename=filename,
                                prefix=self.EXPECTED_PREFIX,
                                suffix=self.EXPECTED_SUFFIX,
                                extension=DEFAULT_EXTENSION,
                                log_dir=log_path)

    def test_if_filename_path_is_attached_correctly_with_drive(self):
            drive_letter = "c"
            log_path = r"\this\is\a\test"

            # The drive letter validation is a windows-only test
            filename = datestamp_filename(prefix=self.EXPECTED_PREFIX,
                                          suffix=self.EXPECTED_SUFFIX,
                                          drive_letter=drive_letter,
                                          directory=log_path)

            print("FILENAME: %s" % filename)

            self._validate_filename(filename=filename,
                                    prefix=self.EXPECTED_PREFIX,
                                    suffix=self.EXPECTED_SUFFIX,
                                    extension=DEFAULT_EXTENSION,
                                    log_dir="{0}:{1}".format(
                                        drive_letter, log_path),
                                    is_windows=True)

    def _validate_filename(self,
                           filename: str, prefix: str = None, suffix: str = None, log_level: str = LOG_LEVEL,
                           extension: str = DEFAULT_EXTENSION, log_dir: str = DEFAULT_LOG_DIR,
                           is_windows: bool = False) -> None:
        """
        General routine to validate the entire filespec, based on the provided
        parameters.

        :param filename: (str) - filename
        :param prefix: (str) - custom prefix expected in filename
        :param suffix: (str) - custom suffix expected in filename
        :param log_level (str) - logging level expected in file
        :param extension: (str) - expected file extension
        :param log_dir: (str) - path of the filename
        :param is_windows: (bool) - Is this for windows (verify drive letter on
                               log_dir)

        :return: None. asserts interrupt routine, or return none

        """
        debug_statement_format = ("FILENAME PARTS (split on {path_delim}, "
                                  "{delim} and fileext): {parts}")

        # Break apart filename based on path separator, delimiter and
        # file extension

        # Split on OS separator, rebuild path without last arg (filename)
        path_and_file = filename.split(os.path.sep)
        path_str = os.path.sep.join(path_and_file[:-1])

        # Split filename based on the file name delimiter
        filename_parts = path_and_file[-1].split(DELIMITER)

        # Remove file extension from the filename parts
        filename_parts.extend(os.path.splitext(filename_parts.pop()))

        # Debug statement for failure assessment
        print(debug_statement_format.format(
            delim=DELIMITER, parts=filename_parts, path_delim=os.path.sep))

        # Path
        if not is_windows:
            log_dir = os.path.abspath(log_dir)
            path_str = os.path.abspath(path_str)

        print(f"LOG DIR STRING:  {log_dir}")
        print(f"PARSED PATH STR: {path_str}")
        assert_equals(log_dir, path_str)

        # Filename parts can consist of prefix, TIMESTAMP, suffix, LOG_LEVEL, EXTENSION
        # (CAPITALIZED = MANDATORY, lowercase = optional)

        # Validate extension
        assert_equals(filename_parts[-1], f".{extension}")
        del filename_parts[-1]

        # Validate log_level
        assert_equals(filename_parts[-1], self.LOG_LEVEL)
        del filename_parts[-1]

        # Validate suffix
        if len(filename_parts) > 2 and suffix is not None:
            assert_equals(filename_parts[-1], self.EXPECTED_SUFFIX)
            del filename_parts[-1]

        # Validate prefix
        if len(filename_parts) > 2 and prefix is not None:
            assert_equals(filename_parts[0], self.EXPECTED_PREFIX)

        # Validate Timestamp
        assert_is_not_none(re.search(self.TIMESTAMP_FORMAT, filename))

# ----------------------------------------------------------------
#       check_if_location_exists()
# ----------------------------------------------------------------

    def test_check_if_location_exists_but_does_not_exist_no_create(self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = False

        if os.path.exists(path):
            os.removedirs(path)

        result = check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is False
        assert os.path.exists(path) is False

    def test_check_if_location_exists_but_does_not_exist_create(self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = True

        if os.path.exists(path):
            os.removedirs(path)

        result = check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is True
        assert os.path.exists(path) is False

    def test_check_if_location_exists_and_does_exist(
            self):
        path_dirs = ['tmp', 'does', 'not', 'exist']
        path = os.path.sep.join(path_dirs)
        create_dir = True
        os.makedirs(path)

        result = check_if_location_exists(
            location=path, create_dir=create_dir)
        try:
            os.removedirs(path)
        except OSError:
            pass  # Found a directory that was not empty

        assert result is True
        assert os.path.exists(path) is False


class TestLogUtilsMocked(object):

    def test_check_if_location_exists_but_does_not_exist_cannot_create(self):

        with patch('PDL.logger.utils.os.makedirs', side_effect=Exception()) as make_dirs_mock:
            path_dirs = ['tmp', 'does', 'not', 'exist']
            path = os.path.sep.join(path_dirs)
            create_dir = True

            if os.path.exists(path):
                os.removedirs(path)

            result = check_if_location_exists(location=path, create_dir=create_dir)
            try:
                os.removedirs(path)
            except OSError:
                pass  # Found a directory that was not empty

            assert result is False
            assert make_dirs_mock.call_count == 1
            assert os.path.exists(path) is False
