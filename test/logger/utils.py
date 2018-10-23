import os
import re

from PDL.logger.utils import datestamp_filename, DEFAULT_EXTENSION, DELIMITER

from nose.tools import assert_equals, assert_is_not_none


class TestLogUtils(object):

    TIMESTAMP_FORMAT = r'[0-9]{6}T[0-9]{6}'
    EXPECTED_PREFIX = 'myPrefix'
    EXPECTED_SUFFIX = 'mySuffix'
    NON_DEFAULT_EXT = 'txt'

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

    def _validate_filename(self,
                           filename, prefix=None, suffix=None,
                           extension=DEFAULT_EXTENSION):

        debug_statement_format = ("FILENAME PARTS (split on '{delim}' and "
                                  "fileext): {parts}")

        # Break apart filename based on delimiter and file extension
        filename_parts = filename.split(DELIMITER)
        filename_parts.extend(os.path.splitext(filename_parts.pop()))

        # Debug statement for failure assessment
        print(debug_statement_format.format(
            delim=DELIMITER, parts=filename_parts))

        # Validate Prefix
        if filename_parts > 2 and prefix is not None:
            assert_equals(filename_parts[0], self.EXPECTED_PREFIX)
            filename_parts = filename_parts[1:]

        # Validate Suffix
        if filename_parts > 2 and suffix is not None:
            assert_equals(filename_parts[-2], self.EXPECTED_SUFFIX)
            del filename_parts[-2]

        # Validate Timestamp
        assert_is_not_none(re.search(self.TIMESTAMP_FORMAT, filename))

        # Validate Extension
        assert_equals(filename_parts[-1], ".{0}".format(extension))

