import os
import re

from PDL.logger.utils import datestamp_filename, DEFAULT_EXTENSION, DELIMITER

from nose.tools import assert_equals, assert_is_not_none


# TODO: Add inline docstrings
class TestLogUtils(object):

    TIMESTAMP_FORMAT = r'[0-9]{6}T[0-9]{6}'
    EXPECTED_PREFIX = 'myPrefix'
    EXPECTED_SUFFIX = 'mySuffix'
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
                                      base_dir=log_path)

        self._validate_filename(filename=filename,
                                prefix=self.EXPECTED_PREFIX,
                                suffix=self.EXPECTED_SUFFIX,
                                extension=DEFAULT_EXTENSION,
                                log_dir=log_path)

    def _validate_filename(self,
                           filename, prefix=None, suffix=None,
                           extension=DEFAULT_EXTENSION,
                           log_dir=DEFAULT_LOG_DIR):

        debug_statement_format = ("FILENAME PARTS (split on {path_delim}, "
                                  "{delim} and fileext): {parts}")

        # Break apart filename based on path separator, delimiter and
        # file extension
        path_and_file = filename.split(os.path.sep)
        path_str = os.path.sep.join(path_and_file[:-1])

        filename_parts = path_and_file[-1].split(DELIMITER)
        filename_parts.extend(os.path.splitext(filename_parts.pop()))

        # Debug statement for failure assessment
        print(debug_statement_format.format(
            delim=DELIMITER, parts=filename_parts, path_delim=os.path.sep))

        # PATH
        print("LOG DIR STRING:  %s" % log_dir)
        print("PARSED PATH STR: %s" % path_str)
        assert_equals(log_dir, path_str)

        # VALIDATE PREFIX
        if filename_parts > 2 and prefix is not None:
            assert_equals(filename_parts[0], self.EXPECTED_PREFIX)
            filename_parts = filename_parts[1:]

        # VALIDATE SUFFIX
        if filename_parts > 2 and suffix is not None:
            assert_equals(filename_parts[-2], self.EXPECTED_SUFFIX)
            del filename_parts[-2]

        # Validate Timestamp
        assert_is_not_none(re.search(self.TIMESTAMP_FORMAT, filename))

        # Validate Extension
        assert_equals(filename_parts[-1], ".{0}".format(extension))
