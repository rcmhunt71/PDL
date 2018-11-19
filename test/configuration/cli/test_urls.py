from PDL.configuration.cli.urls import UrlArgProcessing

from nose.tools import assert_equals, assert_not_equals, assert_true, assert_false


class TestUrlProcessing(object):

    # ===============================================================
    # -------   CliArgProcessing::reduce_url_list(url_list)   -------
    # ===============================================================

    UNIQUE_URL_LIST = [1, 2, 3, 4]

    def test_unique_list_with_no_dups(self):
        expected_unique_dups = 0
        results = UrlArgProcessing.reduce_url_list(url_list=self.UNIQUE_URL_LIST)

        # Unique List
        assert_equals(len(self.UNIQUE_URL_LIST), len(results[UrlArgProcessing.REDUCED_LIST]))

        # Total Duplicates
        assert_equals(len(results[UrlArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups)

        # Unique Duplicates
        assert_equals(len(results[UrlArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    def test_unique_list_with_single_dups(self):
        # Create a list of duplicate elements (unique * 2)
        dup_list = self.UNIQUE_URL_LIST[:]
        dup_list.extend(self.UNIQUE_URL_LIST)

        # Expected number of duplicates
        expected_unique_dups = len(self.UNIQUE_URL_LIST)
        results = UrlArgProcessing.reduce_url_list(url_list=dup_list)

        # Unique List
        assert_equals(len(results[UrlArgProcessing.REDUCED_LIST]), len(self.UNIQUE_URL_LIST))

        # Total Duplicates
        assert_equals(len(results[UrlArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups)

        # Unique Duplicates
        assert_equals(len(results[UrlArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    def test_unique_list_with_multiple_dups(self):
        # Create a list of duplicate elements (unique * 3)
        dup_list = self.UNIQUE_URL_LIST[:]
        dup_list.extend(self.UNIQUE_URL_LIST)
        dup_list.extend(self.UNIQUE_URL_LIST)

        # Expected number of duplicates
        expected_unique_dups = len(self.UNIQUE_URL_LIST)
        results = UrlArgProcessing.reduce_url_list(url_list=dup_list)

        # Unique List
        assert_equals(len(results[UrlArgProcessing.REDUCED_LIST]), len(self.UNIQUE_URL_LIST))

        # Total Duplicates (two of each unique value)
        assert_equals(len(results[UrlArgProcessing.TOTAL_DUP_LIST]), expected_unique_dups * 2)

        # Unique Duplicates
        assert_equals(len(results[UrlArgProcessing.UNIQUE_DUP_LIST]), expected_unique_dups)

    def test_duplicate_counts_per_url(self):
        dup_list = self.UNIQUE_URL_LIST[:]
        dup_list.extend(self.UNIQUE_URL_LIST)
        dup_list.extend(self.UNIQUE_URL_LIST)

        expected_count_per_url = 3
        results = UrlArgProcessing.counts_of_each_dup(dup_list)
        for url, count in results.items():
            print("URL: {url} --> Count {count}".format(url=url, count=count))
            assert_equals(count, expected_count_per_url)

    # ================================================================
    # ------- CliArgProcessing::validate_url(url, [protocol]) -------
    # ================================================================

    VALID_PROTOCOL = 'https://'
    VALID_DOMAIN = 'test.domain.com'
    INVALID_DOMAIN = 'wooba.boom.python'
    VALID_URL_STR_FORMAT = ('{protocol}{domain}/resource_1/resource_2/'
                            'endpoint_{{0}}.jpg')

    VALID_URL_FORMAT = VALID_URL_STR_FORMAT.format(
        protocol=VALID_PROTOCOL, domain=VALID_DOMAIN)

    VALID_NON_DOMAIN_FORMAT = VALID_URL_STR_FORMAT.format(
        protocol=VALID_PROTOCOL, domain=INVALID_DOMAIN)

    VALID_URL = VALID_URL_FORMAT.format('1')
    VALID_URL_WITH_INVALID_DOMAIN = VALID_NON_DOMAIN_FORMAT.format('1')

    INVALID_URL = ".idea/not/valid"

    def test_validate_url_with_valid_url_lowercase(self):
        url = self.VALID_URL
        valid = UrlArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_valid_url_uppercase(self):
        url = self.VALID_URL.upper()
        valid = UrlArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_valid_url_mixed_case(self):
        url = self.VALID_URL.capitalize()
        valid = UrlArgProcessing.validate_url(url=url)
        assert_true(valid, "Valid URL ({url}) was marked as invalid.".format(url=url))

    def test_validate_url_with_protocol_lowercase(self):
        url = self.VALID_URL
        protocol = self.VALID_PROTOCOL.lower()
        valid = UrlArgProcessing.validate_url(url=url, protocol=protocol)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with a valid protocol ({delim}).".format(
            url=url, delim=protocol))

    def test_validate_url_with_protocol_uppercase(self):
        url = self.VALID_URL
        protocol = self.VALID_PROTOCOL.upper()
        valid = UrlArgProcessing.validate_url(url=url, protocol=protocol)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with valid protocol ({delim}).".format(
            url=url, delim=protocol))

    def test_validate_url_with_protocol_mixed_case(self):
        url = self.VALID_URL
        protocol = self.VALID_PROTOCOL.capitalize()
        valid = UrlArgProcessing.validate_url(url=url, protocol=protocol)
        assert_true(valid, "Valid URL ({url}) was marked as invalid with valid protocol ({delim}).".format(
            url=url, delim=protocol))

    def test_validate_url_with_invalid_url(self):
        url = self.INVALID_URL
        valid = UrlArgProcessing.validate_url(url=url)
        assert_false(valid, "Invalid URL ({url}) was marked as valid.".format(url=url))

    def test_validate_url_with_invalid_protocol(self):
        url = self.VALID_URL
        protocol = "\r\ninvalid"
        valid = UrlArgProcessing.validate_url(url=url, protocol=protocol)
        assert_false(valid, "Valid URL ({url}) was marked as valid with invalid protocol ({delim}).".format(
            url=url, delim=protocol))

    def test_validate_url_with_protocol_as_url(self):
        url = self.VALID_PROTOCOL
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(url=url, protocol=protocol)
        assert_false(valid, "Invalid URL ({url}) was marked as valid with valid protocol ({delim}).".format(
            url=url, delim=protocol))

    def test_validate_url_with_valid_domains(self):
        url = self.VALID_URL
        domain = self.VALID_DOMAIN
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain, self.INVALID_DOMAIN])
        assert_true(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_url_with_valid_domain_and_none_domain(self):
        url = self.VALID_URL
        domain = self.VALID_DOMAIN
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain, None])
        assert_true(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_url_with_valid_url_and_uppercase_domain(self):
        url = self.VALID_URL
        domain = self.VALID_DOMAIN.upper()
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain])
        assert_true(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_url_with_valid_url_and_capitalized_domain(self):
        url = self.VALID_URL
        domain = self.VALID_DOMAIN.capitalize()
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain])
        assert_true(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_url_with_valid_url_and_none_domain(self):
        url = self.VALID_URL
        domain = None
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain])
        assert_true(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_url_with_valid_url_and_invalid_domain(self):
        url = self.VALID_URL_WITH_INVALID_DOMAIN
        domain = self.VALID_DOMAIN
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain])
        assert_false(
            valid, ("Valid URL ({url}) was marked as invalid with valid "
                    "protocol ({delim}) and invalid domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_invalid_url_with_invalid_protocol_and_valid_domain(self):
        url = self.VALID_URL_WITH_INVALID_DOMAIN
        domain = self.VALID_DOMAIN
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain])
        assert_false(
            valid, ("Invalid URL ({url}) was marked as valid with invalid "
                    "protocol ({delim}) and valid domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    def test_validate_invalid_url_with_valid_protocol_and_valid_domain(self):
        url = self.INVALID_URL
        domain = self.VALID_DOMAIN
        protocol = self.VALID_PROTOCOL
        valid = UrlArgProcessing.validate_url(
            url=url, protocol=protocol, domains=[domain, self.INVALID_DOMAIN])
        assert_false(
            valid, ("Invalid URL ({url}) was marked as valid with valid "
                    "protocol ({delim}) and valid domain ({domain}).".format(
                url=url, delim=protocol, domain=domain)))

    # ===================================================================
    # ------- CliArgProcessing::split_urls(url_list, [protocol]) -------
    # ===================================================================

    def test_split_urls_all_elems_valid_urls(self):
        valid_split_url_list = [self.VALID_URL_FORMAT.format(id_) for id_ in range(1, 10)]
        updated_list = UrlArgProcessing.split_urls(valid_split_url_list)
        assert_equals(len(valid_split_url_list), len(updated_list))

    def test_split_urls_list_concatenated_into_single_element(self):
        list_size = 10
        valid_split_url_list = [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(0, list_size)])]
        updated_list = UrlArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size)

    def test_split_urls_list_concatenated_into_two_elements(self):
        list_size = 10
        valid_split_url_list = [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(0, list_size)])]
        valid_split_url_list.extend(
            [''.join([self.VALID_URL_FORMAT.format(id_) for id_ in range(list_size, list_size * 2)])])
        updated_list = UrlArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size * 2)

    def test_split_urls_with_concatenated_element(self):
        list_size = 10
        valid_split_url_list = [self.VALID_URL_FORMAT.format(id_) for id_ in range(1, 10)]

        valid_split_url_list.append(valid_split_url_list[-1] + valid_split_url_list[-2] + valid_split_url_list[-3])
        list_size += 2

        updated_list = UrlArgProcessing.split_urls(valid_split_url_list)
        assert_not_equals(len(valid_split_url_list), len(updated_list))
        assert_equals(len(updated_list), list_size)

    def test_list_urls_combines_urls_correctly(self):
        list_size = 100
        url_list = [self.VALID_URL_FORMAT.format(id_) for id_ in range(0, list_size)]

        url_str = UrlArgProcessing.list_urls(url_list=url_list)
        assert isinstance(url_str, str)

        url_count = len([line for line in url_str.split('\n') if line != ''])
        assert_equals(list_size, url_count)

    # ===============================================================
    # -------   CliArgProcessing::process_url_list(url_list)   -------
    # ===============================================================
    def test_all_valid_and_unique_urls_are_returned(self):
        num_urls = 10
        url_list = [self.VALID_URL_FORMAT.format(index) for index in range(0, num_urls)]
        processed_list = UrlArgProcessing.process_url_list(url_list)
        assert_equals(num_urls, len(processed_list))

    def test_concat_urls_only_valid_and_unique_urls_are_returned(self):
        num_urls = 10
        concat_urls = 3
        url_list = [self.VALID_URL_FORMAT.format(index) for index in range(0, num_urls)]
        concat = [self.VALID_URL_FORMAT.format(index) for index in range(100, 100 + concat_urls)]
        url_list.append(''.join(concat))

        processed_list = UrlArgProcessing.process_url_list(url_list)
        assert_equals(num_urls + concat_urls, len(processed_list))

    def test_duplicate_urls_only_valid_and_unique_urls_are_returned(self):
        num_urls = 10
        url_list = [self.VALID_URL_FORMAT.format(index) for index in range(0, num_urls)]
        url_list.extend(url_list)
        processed_list = UrlArgProcessing.process_url_list(url_list)
        assert_equals(num_urls, len(processed_list))

    def test_concat_and_dup_urls_only_valid_and_unique_urls_are_returned(self):
        num_urls = 10
        concat_urls = 3
        url_list = [self.VALID_URL_FORMAT.format(index) for index in range(0, num_urls)]
        url_list.extend(url_list)

        concat = [self.VALID_URL_FORMAT.format(index) for index in range(100, 100 + concat_urls)]

        url_list.append(''.join(concat))
        processed_list = UrlArgProcessing.process_url_list(url_list)
        assert_equals(num_urls + concat_urls, len(processed_list))

    def test_invalid_urls_are_removed(self):
        num_urls = 5
        url_list = [self.VALID_URL_FORMAT.format(index) for index in range(0, num_urls)]
        url_list.append(self.INVALID_URL)
        url_list.extend([self.VALID_URL_FORMAT.format(index) for index in range(10, 10 + num_urls)])
        processed_list = UrlArgProcessing.process_url_list(url_list)
        assert_equals(num_urls * 2, len(processed_list))

