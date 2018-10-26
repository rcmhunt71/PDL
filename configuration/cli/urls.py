import PDL.logger.logger as pdl_log

log = pdl_log.Logger()


class CliArgProcessing(object):

    REDUCED_LIST = 'reduced_list'
    TOTAL_DUP_LIST = 'total_dup_list'
    UNIQUE_DUP_LIST = 'unique_dup_list'
    DELIMITER = 'https://'

    @classmethod
    def process_url_list(cls, url_list):
        """
        Split any combined URLs, verify all URLs are valid, and remove any duplicates

        :param url_list: List of URLs to process

        :return: List of valid, unique URLs

        """
        # Split URLS that were concatenated
        split_urls = CliArgProcessing.split_urls(url_list)

        valid_urls = list()
        invalid_urls = list()

        # Make sure each url is valid
        for url in split_urls:
            if CliArgProcessing.validate_url(url):
                valid_urls.append(url)
            else:
                invalid_urls.append(url)
        log.debug("Number of VALID URLs on CLI: {0}".format(len(valid_urls)))
        log.debug("Number of INVALID URLs on CLI: {0}".format(len(invalid_urls)))
        for url in invalid_urls:
            log.debug("Invalid URL: {0}".format(url))

        # Remove duplicates
        url_dict = CliArgProcessing.reduce_url_list(valid_urls)

        return url_dict[cls.REDUCED_LIST]

    @classmethod
    def reduce_url_list(cls, url_list):
        """
        Remove any duplicates from the list.

        TODO: Log all duplicates found; currently only counts are reported.

        :return: dictionary of:
            * reduced_list: List of unique elements
            * total_dup_list: List of all duplicates
            * unique_dup_list: List of all unique duplicates

        """
        reduced_list = list(set(url_list))
        total_dups = [url for n, url in enumerate(url_list) if url in url_list[:n]]
        unique_dups = list(set(total_dups))

        log.debug("Number of URLs on CLI: {0}".format(len(url_list)))
        log.debug("Number of Unique URLs: {0}".format(len(reduced_list)))
        log.debug("Number of Duplicates:  {0}".format(len(total_dups)))
        log.debug("Number of Unique Duplicates:  {0}".format(len(unique_dups)))

        return {cls.REDUCED_LIST: reduced_list,
                cls.TOTAL_DUP_LIST: total_dups,
                cls.UNIQUE_DUP_LIST: unique_dups}

    @classmethod
    def split_urls(cls, url_list, delimiter=DELIMITER):
        """
        Check for URLs that are not space delimited from the CLI. If found,
        split the URL into two URLs and add to the list.
        :param url_list: List of URLs to process
        :param delimiter: Delimiter that indicates unique URLs, e.g. - space or comma

        :return: List of valid URLs

        """
        # Concatenate all entries into a space-delimited string
        url_concat = ' '.join(url_list)

        # Split on delimiter (Catches concatenated http entries)
        # Rejoin with space delimiter (concatenated entries are now separate)
        url_temp = ' {0}'.format(delimiter).join(url_concat.split(delimiter))
        if url_concat != url_temp:
            log.debug("Concatenated URL Found (Delimiter: {delim}) - Fixed".format(
                delim=delimiter))

        # Ignore '' urls, they are not valid, and the splitting generates a ''
        # at the front of each element in a split list.

        return [url for url in url_temp.split(' ') if url is not '' and
                CliArgProcessing.validate_url(url)]

    @classmethod
    def validate_url(cls, url, delimiter=DELIMITER):
        """
        Verify URL starts with delimited, and has additional URL info.

        TODO: Check for domain. <protocol>://<domain>/[[resources]..]

        :param url: URL
        :param delimiter: protocol prefix for URL

        :return: Boolean; True = Valid URL

        """
        valid = (url.lower().startswith(delimiter.lower()) and
                 url.lower() != delimiter.lower())

        log.debug("{status}: URL: {url}".format(
            status="VALID" if valid else "INVALID", url=url))

        return valid

    @classmethod
    def list_urls(cls, url_list):
        """
        Generate multi-line string of URLs in list
        :param url_list: List of URLs

        :return: multi-line string

        """
        url_list_string = ''
        for index, url in enumerate(url_list):
            url_list_string += "{counter}) {curr_url}\n".format(
                counter=index + 1, curr_url=url)
        return url_list_string
