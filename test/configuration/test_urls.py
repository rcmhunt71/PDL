from PDL.configuration.urls import CliArgProcessing

from nose.tools import assert_equals, assert_not_equals, assert_true, assert_false


class TestUrlProcessing(object):

    # ===============================================================
    # -------   CliArgProcessing::reduce_url_list(url_list)   -------
    # ===============================================================

    UNIQUE_URL_LIST = [1, 2, 3, 4]

    def test_unique_list_with_no_dups(self):
        expected_unique_dups = 0
        results = CliArgProcessing.reduce_url_list(url_list=self.UNIQUE_URL_LIST)

        # Unique List
        assert_equals(len(self.UNIQUE_URL_LIST), len(results[CliArgProcessing.REDUCED_LIST]))

        # Total Duplicates
        assert_equals(len(results[CliArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups)

        # Unique Duplicates
        assert_equals(len(results[CliArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    def test_unique_list_with_single_dups(self):
        # Create a list of duplicate elements (unique * 2)
        dup_list = self.UNIQUE_URL_LIST[:]
        dup_list.extend(self.UNIQUE_URL_LIST)

        # Expected number of duplicates
        expected_unique_dups = len(self.UNIQUE_URL_LIST)
        results = CliArgProcessing.reduce_url_list(url_list=dup_list)

        # Unique List
        assert_equals(len(results[CliArgProcessing.REDUCED_LIST]), len(self.UNIQUE_URL_LIST))

        # Total Duplicates
        assert_equals(len(results[CliArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups)

        # Unique Duplicates
        assert_equals(len(results[CliArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    def test_unique_list_with_multiple_dups(self):
        # Create a list of duplicate elements (unique * 3)
        dup_list = self.UNIQUE_URL_LIST[:]
        dup_list.extend(self.UNIQUE_URL_LIST)
        dup_list.extend(self.UNIQUE_URL_LIST)

        # Expected number of duplicates
        expected_unique_dups = len(self.UNIQUE_URL_LIST)
        results = CliArgProcessing.reduce_url_list(url_list=dup_list)

        # Unique List
        assert_equals(len(results[CliArgProcessing.REDUCED_LIST]), len(self.UNIQUE_URL_LIST))

        # Total Duplicates (two of each unique value)
        assert_equals(len(results[CliArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups * 2)

        # Unique Duplicates
        assert_equals(len(results[CliArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    # ================================================================
    # ------- CliArgProcessing::validate_url(url, [delimiter]) -------
    # ================================================================

    VALID_DELIMITER = 'https://'
    VALID_URL_FORMAT = 'https://test.domain.dom/resource_1/resource_2/endpoint_{0}.jpg'
    VALID_URL = VALID_URL_FORMAT.format('')

    def test_validate_url_with_valid_url_lowercase(self):
        url = self.VALID_URL
        valid = CliArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_valid_url_uppercase(self):
        url = self.VALID_URL.upper()
        valid = CliArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_valid_url_mixed_case(self):
        url = self.VALID_URL.capitalize()
        valid = CliArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_delimiter_lowercase(self):
        url = self.VALID_URL
        delimiter = self.VALID_DELIMITER.lower()
        valid = CliArgProcessing.validate_url(url=url, delimiter=delimiter)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with a valid delimiter ({delim}).".format(
            url=url, delim=delimiter))

    def test_validate_url_with_delimiter_uppercase(self):
        url = self.VALID_URL
        delimiter = self.VALID_DELIMITER.upper()
        valid = CliArgProcessing.validate_url(url=url, delimiter=delimiter)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with valid delimiter ({delim}).".format(
            url=url, delim=delimiter))

    def test_validate_url_with_delimiter_mixed_case(self):
        url = self.VALID_URL
        delimiter = self.VALID_DELIMITER.capitalize()
        valid = CliArgProcessing.validate_url(url=url, delimiter=delimiter)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with valid delimiter ({delim}).".format(
            url=url, delim=delimiter))

    def test_validate_url_with_invalid_url(self):
        url = '.idea'
        valid = CliArgProcessing.validate_url(url=url)
        assert_false(valid, "Invalid URL ({url}) was marked as valid.".format(url=url))

    def test_validate_url_with_invalid_delimiter(self):
        url = self.VALID_URL
        delimiter = "\r\ninvalid"
        valid = CliArgProcessing.validate_url(url=url, delimiter=delimiter)
        assert_false(valid, "Valid URL ({url}) was marked as valid with invalid delimiter ({delim}).".format(
            url=url, delim=delimiter))

    def test_validate_url_with_delimiter_as_url(self):
        url = self.VALID_DELIMITER
        delimiter = self.VALID_DELIMITER
        valid = CliArgProcessing.validate_url(url=url, delimiter=delimiter)
        assert_false(valid, "Invalid URL ({url}) was marked as valid with valid delimiter ({delim}).".format(
            url=url, delim=delimiter))

    # ===================================================================
    # ------- CliArgProcessing::split_urls(url_list, [delimiter]) -------
    # ===================================================================

    def test_split_urls_all_elems_valid_urls(self):
        valid_split_url_list = [self.VALID_URL_FORMAT.format(id_) for id_ in range(1, 10)]
        updated_list = CliArgProcessing.split_urls(valid_split_url_list)
        assert_equals(len(valid_split_url_list), len(updated_list))

    def test_split_urls_list_concatenated_into_single_element(self):
        list_size = 10
        valid_split_url_list = [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(0, list_size)])]
        updated_list = CliArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size)

    def test_split_urls_list_concatenated_into_two_elements(self):
        list_size = 10
        valid_split_url_list = [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(0, list_size)])]
        valid_split_url_list.append(
            [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(list_size, list_size * 2)])])
        updated_list = CliArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size)

    def test_split_urls_with_concatenated_element(self):
        list_size = 10
        valid_split_url_list = [self.VALID_URL_FORMAT.format(id_) for id_ in range(1, 10)]

        valid_split_url_list.append(valid_split_url_list[-1] + valid_split_url_list[-2] + valid_split_url_list[-3])
        list_size += 2

        updated_list = CliArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size)
